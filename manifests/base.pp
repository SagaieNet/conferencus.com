node base {
  # this makes puppet and vagrant shut up about the puppet group
  group { "puppet":
    ensure => "present",
  }

  # Set default paths
  Exec { path => '/usr/bin:/bin:/usr/sbin:/sbin' }

  # make sure the packages are up to date before beginning
  exec { "apt-get update":
    command => "apt-get update"
  }

  # because puppet command are not run sequentially, ensure that packages are
  # up to date before installing before installing packages, services, files, etc.
  Package { require => Exec["apt-get update"] }
  File { require => Exec["apt-get update"] }

  package { "npm":
    ensure => present,
  }

  # slimerjs setup
  $slimerjsRequirements = ["libc6", "libstdc++6", "libgcc1", "firefox", "xvfb"]
  package { $slimerjsRequirements: ensure => "installed" }

  # download slimerjs
  exec { "download-slimerjs":
      command => "wget http://download.slimerjs.org/v0.9/0.9.1/slimerjs-0.9.1-linux-x86_64.tar.bz2 && test -d '/home/vagrant/tools' || mkdir -p /home/vagrant/tools && mv -f slimerjs-0.9.1-linux-x86_64.tar.bz2 /home/vagrant/tools/slimerjs.tar.bz2 && tar -xf /home/vagrant/tools/slimerjs.tar.bz2 -C /home/vagrant/tools && ln -s /home/vagrant/tools/slimerjs-0.9.1/slimerjs /usr/bin/slimerjs",
      creates => "/usr/bin/slimerjs",
      require => Package[$slimerjsRequirements]
  }

  package {
      "build-essential": ensure => installed;
      "python": ensure => installed;
      "python-dev": ensure => installed;
      "python-pip": ensure => installed;
      "python-virtualenv": ensure => installed;
  }

  exec { "website-virtualenv":
    command => "virtualenv venv --distribute",
    cwd => "/var/www/website",
    creates => "/var/www/website/venv/bin/activate",
    require => Package["python-virtualenv"],
  }

  exec { "website-dependencies":
    command => "/var/www/website/venv/bin/pip install -r requirements.txt",
    cwd => "/var/www/website",
    require => Exec["website-virtualenv"],
    logoutput => "on_failure",
  }

  package { "rabbitmq-server":
    ensure => present,
  }

  $image = ["libtiff4-dev", "libjpeg8-dev", "libjpeg-dev", "zlib1g-dev", "libfreetype6-dev", "liblcms2-dev", "libwebp-dev", "tcl8.5-dev", "tk8.5-dev", "python-tk"]
  package { $image: ensure => "installed" }

  package { "mysql-server": ensure => installed }

  service { "mysql":
    enable => true,
    ensure => running,
    require => Package["mysql-server"],
  }

  # provides pdfinfo
  package { "poppler-utils": ensure => installed }
}