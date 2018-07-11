#!/bin/bash

[ -d ../logs ] || mkdir -p ../logs
[ -d ../data ] || mkdir -p ../data

apt-get install python-MySQLdb ntp

if [ ! -x /usr/sbin/ntpdate ] 
then
	echo "Error: ntpdate must be installed in your system and be in the PATH"
	exit -1;
fi

ntpdate -b -s -u pool.ntp.org

apt-get install python-pip python-setuptools python-smbus sqlite3
pip install Adafruit_BBIO
pip install pyserial
pip install db-sqlite3
