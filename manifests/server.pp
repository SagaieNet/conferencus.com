# load base manifest
import "base.pp"

node default inherits base {
  package {"sendmail":
      ensure => installed,
  }

  package {"supervisor":
      ensure => installed,
  }
  service { "supervisor":
    ensure => running,
    enable => true,
    require => Package['supervisor'],
  }

  file { "/etc/supervisor/conf.d/website.conf":
    ensure => present,
    source => "/var/www/manifests/resources/supervisor_website.conf",
    require => [Package['supervisor'],File['/etc/uwsgi.xml']],
    notify => Service["supervisor"]
  }

  file { "/etc/supervisor/conf.d/processor.conf":
    ensure => present,
    source => "/var/www/manifests/resources/supervisor_processor.conf",
    require => [Package['rabbitmq-server'],Exec['website-dependencies']],
    notify => Service["supervisor"]
  }

  package {"nginx":
      ensure => installed,
  }
  service { "nginx":
    ensure => running,
    enable => true,
    require => Package['nginx'],
  }

  file { "/etc/nginx/sites-enabled/default":
      require => Package["nginx"],
      ensure  => absent,
      notify  => Service["nginx"]
  }

  file { "/etc/nginx/sites-enabled/example.conf":
    ensure => present,
    source => "/var/www/manifests/resources/website.conf",
    require => [Package['nginx'],File['/etc/supervisor/conf.d/website.conf']],
    notify => Service["nginx"]
  }

  package { "uwsgi":
    ensure => present,
    provider => "pip"
  }

  file { "/etc/uwsgi.xml":
    ensure => present,
    source => "/var/www/manifests/resources/uwsgi.xml",
    require => Package['uwsgi'],
    notify => Service["supervisor"]
  }
}
