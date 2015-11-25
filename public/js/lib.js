function diplay_hide(start) {
  if ($(start).css('display') == 'none') {
    $(start).animate({
      height: 'show'
    }, 400);
  } else {
    $(start).animate({
      height: 'hide'
    }, 400);
  }
}

// Stream state in cookies

function _pushState(id, seconds) {
  if (seconds) {
    var date = new Date();
    date.setTime(date.getTime() + (seconds * 1000));
    var expires = "; expires=" + date.toGMTString();
  } else var expires = "";
  document.cookie = 'stream_state' + "=" + id + expires + "; path=/";
}

function _readState() {
  var nameEQ = 'stream_state' + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function _eraseState() {
  _pushState("", -1);
}

$(document).ready(function() {
  var startButton = $('a.start_batton'),
      _player = jwplayer('player_id'),
      isStateChecking = false;

    function playerStop(){
        _player.stop();
    }

    function playerPlay(){
        _player.play(true);
    }

  function playerSetup(stream_id) {
      var conf = {
        autostart: false,
        width: 1,
        height: 1,
//        androidhls: true,
        playlist: [{
          sources: [
           {
            file: 'rtmp://' + DOMAIN + '/' + CHANNEL + '/' + stream_id
          },
           {
            file: 'http://' + DOMAIN + ':' + PORT + '/' + CHANNEL + '/' + stream_id + '.mp3'
          },
//{
//            file: 'http://' + DOMAIN + ':' + PORT + '/' + CHANNEL + '/' + stream_id + '.m3u8'
//          },

          ]
        }],
        primary: 'html5'
      };
      _player.setup(conf);
  }

  // State pusher

  function updateState(cb) {
    (function pusher() {
      var state = _readState(),
          lateState = false;
      if (state) {
        isStateChecking = true;
        $.post('/state/' + state, {}, 'json').done(function(data) {
          if (data.stream_state) {
            _pushState(state, 1000);
            if (!startButton.hasClass('start_batton_click')) {
              startButton.click();
            }
          } else {
            if (startButton.hasClass('start_batton_click')) {
              startButton.click();
            } else {
                playerStop();
            }
            _eraseState();
            lateState = true;
            isStateChecking = false;
          }
        });
        if(!lateState)
            setTimeout(pusher, 5 * 1000);
      } else {
        isStateChecking = false;
        if (typeof cb == 'function') {
          cb(state);
        }
      }
    })();
  }

  playerSetup(_readState() || STREAM);

  // Init check

  (function checkState() {
    if (_readState()) {
      setTimeout(function(){
        updateState();
      }, 500);
    }
  })();

  $('a.start_batton').click(function() {
    var $this = $(this);
    $this.toggleClass('start_batton_click wow slideInLeft animated');
    $('.cd-3d-nav-container').removeClass('cd-3d_asd');

    if ($this.hasClass('start_batton_click')) {
      var initialState = _readState();
      $.getJSON('/play/' + initialState)
        .done(function(data) {
          playerSetup(data.stream_id);
          _pushState(data.stream_id, 1000);
          playerPlay();
          if (initialState != data.stream_id && !isStateChecking) {
            updateState(function() {
              console.log('Push Finished');
            });
          }
        })
    } else {
      var state = _readState();
      playerStop();
      _eraseState();
      $.getJSON('/stop/' + state);
    }
  });

  $('.qaz').click(function() {
    $('#st-pusher').toggleClass('st-pusher_dop');
    $('#foot').toggleClass('dn');
    $('.cd-3d-nav-container').toggleClass('cd-3d_asd');
  });

  $('a.menu_close').click(function() {
    $('#st-container').toggleClass('st-menu-open');
    $('#st-pusher').toggleClass('st-pusher_dop');
    $('#foot').toggleClass('dn');
    $('.cd-3d-nav-container').toggleClass('cd-3d_asd');
  });
});



function diplay_vip(first) {
  if ($(first).css('display') == 'none') {
    $(first).animate({
      height: 'show'
    }, 400);
    $(second).animate({
      height: 'hide'
    }, 400);
    $(tree).animate({
      height: 'hide'
    }, 400);
  } else {
    $(first).animate({
      height: 'hide'
    }, 400);
  }
}

function diplay_show_vs(tree) {
  if ($(tree).css('display') == 'none') {
    $(tree).animate({
      height: 'show'
    }, 400);
    $(first).animate({
      height: 'hide'
    }, 400);
    $(second).animate({
      height: 'hide'
    }, 400);
  } else {
    $(tree).animate({
      height: 'hide'
    }, 400);
  }
}

function diplay_sor(second) {
  if ($(second).css('display') == 'none') {
    $(second).animate({
      height: 'show'
    }, 400);
    $(first).animate({
      height: 'hide'
    }, 400);
    $(tree).animate({
      height: 'hide'
    }, 400);
  } else {
    $(second).animate({
      height: 'hide'
    }, 400);
  }
}

function diplay_show(left) {
  if ($(left).css('display') == 'none') {
    $(left).animate({
      width: 'show'
    }, 400);
  } else {
    $(left).animate({
      width: 'hide'
    }, 400);
  }
}



$(function() {
  $('.scroll-pane').before(
    $('<div class="width-marker" />')
  );
  $('.scroll-pane').jScrollPane();
  $('#reinit-link').bind(
    'click',
    function() {
      // Using this form rather than the API simply because
      // it is easier to apply the same action to multiple
      // scrollpanes this way - they should be equivalent
      $('.scroll-pane').jScrollPane();
      return false;
    }
  );
});
