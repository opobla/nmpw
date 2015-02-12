import time
import os

# First of all we give big priority to this process
os.nice(20)
wd = open("/dev/watchdog", "w+")
while 1:
	wd.write("\n")
	wd.flush()
	time.sleep(20)
