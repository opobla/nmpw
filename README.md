nmpw
====

Python software for the new pulse width core for neutron monitors

Init_config:
	-->opkg install ntp 
	-->Edit /etc/ntp.conf
		-->add line : server pool.ntp.org
		-->add in /etc/default/ntpdate
			NTPSERVERS="pool.ntp.org"

	-->Enable UART2. edit /media/BEAGLEBONE/uEnv.txt
		-->should look like this:   optargs=quiet drm.debug=7 capemgr.enable_partno=BB-UART2 



Install:
	-->pip:
		opkg update && opkg install python-pip python-setuptools python-smbus	
	-->Before trying to install anything using pip you must have the internal clock of the BBB updated
		ntpdate -b -s -u pool.ntp.org
	-->Adafruit_BBIO
		pip install Adafruit_BBIO
	-->pyserial
		pip install pyserial
	-->sqlite3
		pip install db-sqlite3
