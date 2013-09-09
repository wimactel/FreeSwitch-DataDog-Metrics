#!/bin/sh
#Make appropriate directories
mkdir /usr/share/python-daemon
mkdir /var/log/python-daemon
mkdir /var/run/python-daemon

#move the init script
cp fsmetrics /etc/init.d/

#copy all other files to home directory
cp * /usr/share/python-daemon/
