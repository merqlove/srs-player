# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.vm.provider "virtualbox" do |vb|
  #   vb.memory = "1024"
    vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
    vb.customize ['modifyvm', :id, '--natdnsproxy1', 'on']
  end

  config.vm.define "player" do |player|
    player.vm.box = "ubuntu/trusty64"
    player.vm.network 'private_network', ip: "192.168.10.11"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook       = "provision/site.yml"
    ansible.sudo           = true
    ansible.tags           = ENV['TAGS']
    ansible.raw_arguments  = ENV['ANSIBLE_ARGS']
    ansible.groups         = {
      streamer: ['default'],
      development: ['default']
    }
    ansible.extra_vars     = {
      user: 'vagrant'
    }
  end
end
