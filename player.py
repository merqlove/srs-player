#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import subprocess as sp
import signal
import uuid
from random import randint

import redis
import time
import logging
import atexit
import psutil
import threading
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, jsonify, send_from_directory
from werkzeug.contrib.fixers import ProxyFix

FLASK_ENV = os.getenv('FLASK_ENV', 'develop')
FFMPEG_BIN = os.getenv('FFMPEG_BIN', "/usr/local/bin/ffmpeg")
DOMAIN = os.getenv('STREAM', "192.168.10.11")
RTMP_DOMAIN = os.getenv('RTMP_DOMAIN', "127.0.0.1")
CHANNEL = os.getenv('CHANNEL', "live")
SRS_PORT = os.getenv('SRS_PORT', "8080")
PROTO = os.getenv('PROTO', 'rtmp://')
SCRIPT_DIR = os.getcwd()
FILE_DIR = os.getenv('FILE_DIR', 'mp3')
# PLAYLIST = os.getenv('PLAYLIST', '/vagrant/mp3/%s.mp3' % randint(1, 4))
LOG_FILE = 'player.log'
ERROR_LOG_FILE = 'player.error.log'
CODEC = 'libmp3lame'
BITRATE = '256k'
RATE = '44100'
CHANNELS = '2'
SEEK = '00:00:00'
# In seconds
ACTIVE_STREAM = 30

r = redis.StrictRedis(host='localhost', port=6379, db=0)
app = Flask(__name__)


def is_develop():
    return FLASK_ENV == 'develop'


if not is_develop():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)


def state_loop(interval):
    manage_states()
    try:
        threading.Timer(interval, state_loop, [interval]).start()
    except TypeError:
        pass


def file_path():
    return '%s/%s/%s.mp3' % (SCRIPT_DIR, FILE_DIR, randint(1, 4))


def stream_path(stream_id):
    return "%s%s/%s/%s" % (PROTO, RTMP_DOMAIN, CHANNEL, stream_id)


def is_process_running(pid):
    try:
        proc = psutil.Process(int(pid))
        status = proc.status()
        return status != psutil.STATUS_ZOMBIE
    except (OSError, psutil.NoSuchProcess):
        return False


def run(stream_id=None, playlist=None, retry=False):
    if stream_id and not retry:
        pipe = find(stream_id)
        if pipe and is_process_running(pipe['pid']):
            return stream_id

    if stream_id and not retry:
        stream_id = uuid.uuid4()

    if not playlist:
        playlist = file_path()

    command = [FFMPEG_BIN,
               '-re',
               '-ss', SEEK,
               '-i', playlist,
               '-vn',
               '-acodec', CODEC,
               '-b:a', BITRATE,
               '-ac', CHANNELS,
               '-ar', RATE,
               '-f', 'flv',
               stream_path(stream_id)
               ]

    log_file = open(LOG_FILE, 'w+')
    error_log_file = open(ERROR_LOG_FILE, 'w+')
    pipe = sp.Popen(command, stdout=log_file, stderr=error_log_file, preexec_fn=os.setsid)
    r.hmset('stream:pid:%s' % stream_id, {'pid': pipe.pid, 'stream_id': stream_id, 'playlist': playlist})
    return stream_id


def find(stream_id):
    return r.hgetall('stream:pid:%s' % stream_id)


def stop(stream_id):
    try:
        pipe = find(stream_id)
        if pipe and is_process_running(pipe['pid']):
            r.delete('stream:pid:%s' % stream_id)
            os.killpg(os.getpgid(int(pipe['pid'])), signal.SIGTERM)
    except redis.ResponseError:
        pass


def push_state(stream_id):
    pipe = find(stream_id)
    if not pipe:
        return False

    r.set('stream:state:%s' % stream_id, time.time())
    return True


def check_state(stream_id):
    stamp = r.get('stream:state:%s' % stream_id)
    if not stamp:
        return False
    if (time.time() - float(stamp)) < ACTIVE_STREAM:
        return True
    else:
        return False


def restart_pipe(key):
    try:
        pipe = r.hgetall(key)
        if pipe and not is_process_running(pipe['pid']):
            stop(pipe['stream_id'])
            # run(pipe['stream_id'], pipe['playlist'], True)
            # Make it Random
            run(pipe['stream_id'], None, True)
    except redis.ResponseError:
        pass


def manage_states():
    for key in r.scan_iter('stream:pid*'):
        prefix, uid = key.split('stream:pid:')
        if not check_state(uid):
            stop(uid)
        else:
            restart_pipe(key)


# ASSETS

if is_develop():
    @app.route('/vendor/js/<path:path>')
    def send_vendor_js(path):
        return send_from_directory('public/vendor/js', path)


    @app.route('/js/<path:path>')
    def send_js(path):
        return send_from_directory('public/js', path)


    @app.route('/css/<path:path>')
    def send_css(path):
        return send_from_directory('public/css', path)


    @app.route('/images/<path:path>')
    def send_images(path):
        return send_from_directory('public/images', path)


# APP

@app.route('/')
def static_page():
    return render_template('index.html', server={'domain': DOMAIN, 'channel': CHANNEL, 'port': SRS_PORT, 'stream_id': None})


# API

@app.route('/play/<string:stream_id>', methods=['GET'])
def play_stream(stream_id):
    stream_id = run(stream_id)
    return jsonify(status=True, stream_id=stream_id)


@app.route('/stop/<string:stream_id>', methods=['GET'])
def stop_stream(stream_id):
    stop(stream_id)
    return jsonify(status=True)


@app.route('/state/<string:stream_id>', methods=['POST'])
def write_state(stream_id):
    state = push_state(stream_id)
    return jsonify(status=True, stream_state=state)


def stop_streams():
    for key in r.scan_iter('stream:pid*'):
        prefix, uid = key.split('stream:pid:')
        stop(uid)


# Management Sheduler, check for unused streams & restart needed.
state_loop(5)

# Drop all streams at exit.
atexit.register(stop_streams)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler(ERROR_LOG_FILE, maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.run(threaded=True)
