nmpw
====
    # TODO        
    Update DBUpdater   CALM_ori 

***Python software for the new pulse width core for neutron monitors***


**Init_config**: These steps will allow us to configure your system so as to initialize correctly our data acquisition when the system is started. These allows the system to correctly recover from unexpected situations like power loss. The idea behind all this is to establish internet connection, synchronize the system time, and then run the data acquisition software.

        Create the next folder tree
             /
             |---- server
                   |---- nmpw    #Data Acquisition software, this repository
                   |---- data    #Our data
                   |---- logs    #Logs which give us information about the state of our system


        Configure the config file.
            Edit/Create /server/nmpw/.NMDA.conf
            Or you can copy the exmaple file:
                cp /server/nmpw/NMDA.conf.exmaple /server/nmpw/.NMDA.conf


        Install ntp if not installed
            root@beaglebone:~# opkg install ntp 

        Edit /etc/ntp.conf
            add line : server pool.ntp.org
            add lines:
                `# Using local hardware clock as fallback
                `# Disable this when using ntpd -q -g -x as ntpdate or it will sync to itself
                `# server 127.127.1.0 
                `# fudge 127.127.1.0 stratum 14
        
        Edit /lib/systemd/system/ntpdate.service
            change line:
                ExecStart=/usr/bin/ntpdate-sync silent  <-->  ExecStart=/usr/bin/ntpd -q -g -x

        Edit/Create /lib/systemd/system/nmpwDataAcquisition.service
            Content should be:
        	    [Unit]
        	    Description=NMPW Data Acquisition Service
        	    After=ntpdate.service

        	    [Service]
        	    ExecStart=/usr/bin/python /server/nmpw/NMDA.py

        	    [Install]
        	    WantedBy=multi-user.target

        Edit/Create /lib/systemd/system/myWatchDog.service
            Content should be:
        	    [Unit]
        	    Description=WatchDog

        	    [Service]
        	    ExecStart=/usr/bin/python /server/nmpw/WatchDog.py

        	    [Install]
        	    WantedBy=multi-user.target

        Enable ntp services
            root@beaglebone:~# systemctl enable ntpdate.service
            root@beaglebone:~# systemctl enable ntpd.service
            root@beaglebone:~# systemctl enable nmpwDataAcquisition
            root@beaglebone:~# systemctl enable myWatchDog

	`#  TODO configure and enable systemctl service which starts the software which copies our database  


**Beaglebone Black config**:

        Enable UART2, UART1 
            edit /media/BEAGLEBONE/uEnv.txt
                should look like this:   optargs=quiet drm.debug=7 capemgr.enable_partno=BB-UART2,BB-UART1 


**Install**: Software modules need for the data acquisition.

        pip
            root@beaglebone:~# opkg update && opkg install python-pip python-setuptools python-smbus	
        Before trying to install anything using pip you must have the internal clock of the BBB updated
            root@beaglebone:~# ntpdate -b -s -u pool.ntp.org
        Adafruit_BBIO
            root@beaglebone:~# pip install Adafruit_BBIO
        pyserial
            root@beaglebone:~# pip install pyserial
        sqlite3
            root@beaglebone:~# pip install db-sqlite3
	`#  TODO install MySQL-python
	
**MicroSD**: Configuration a uSD needs.

	The BeagleBone Black will look for the uEnv.txt file in the uSD. So we need to have one that looks like this.
		mmcdev=1
		bootpart=1:2
		mmcroot=/dev/mmcblk1p2 ro
		optargs=quiet drm.debug=7 capemgr.enable_partno=BB-UART2,BB-UART1 

	The next thigh we must set up is the mount point for the uSD. Edit the file /etc/fstab adding the following line. Create the directory /media/microSD if not present.
		/dev/mmcblk0p1       /media/microSD	  auto	     defaults		   0  0

