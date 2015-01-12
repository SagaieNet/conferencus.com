Vagrant::Config.run do |config|
  config.vm.box = "quantal"
  config.vm.box_url = "http://cloud-images.ubuntu.com/quantal/current/quantal-server-cloudimg-vagrant-amd64-disk1.box"

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "manifests"
    puppet.manifest_file  = "dev.pp"
  end

  config.vm.network :hostonly, "33.33.33.10"

  config.vm.share_folder "www", "/var/www", "./", :nfs => true

  config.vm.customize ["modifyvm", :id, "--memory", 1024]
end