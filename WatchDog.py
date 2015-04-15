import time
import os
import NMDA
import sqlite3

def get_last():
	try:
		cursor = conn_local.cursor()
		cursor.execute("SELECT max(start_date_time) FROM binTable")
		row = cursor.fetchone()
		last_data=row[0]
	except:
		lat_data=None

	if last_data==None:
		last_data='2000-01-01 00:00:00'
	else:
		last_data=str(last_data)
	return last_data


# First of all we give big priority to this process
os.nice(20)
args=NMDA.create_parser().parse_args()

conn_local 	= sqlite3.connect(args.database)
last_data	= get_last()
cont		= 0

wd = open("/dev/watchdog", "w+")
while True:
	wd.write("\n")
	wd.flush()
	time.sleep(20)
	cont+=1

	if cont >= 15:					#15*20secs=5mins
		cont		= 0
		curr_last	= get_last()
		if curr_last == last_data:
			time.sleep(120)			#This will reset the board
		last_data 	= curr_last
