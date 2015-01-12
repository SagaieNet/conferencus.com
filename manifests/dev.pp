# load base manifest
import "base.pp"

node default inherits base {
  exec { "create-dev-db":
    unless => "mysql -udev -pdev dev",
    command => "mysql -uroot -e \"create database dev DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci; grant all on dev.* to dev@localhost identified by 'dev';\"",
    require => Service["mysql"],
  }
}