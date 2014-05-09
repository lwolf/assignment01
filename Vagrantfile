# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "base"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.hostname = "dev"
  config.ssh.private_key_path="~/.vagrant.d/insecure_private_key"

  config.vm.provision "ansible" do |ansible|
    ansible.inventory_path = "deploy/hosts"
    ansible.playbook = "deploy/playbook.yml"
    ansible.verbose = "extra"
    ansible.limit = 'all'
  end

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

end
