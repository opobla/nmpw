import argparse
import time
import threading
from time import strftime
import datetime
import serial
#import pymongo
import sqlite3

from Reader import Reader
from CountsPettioner import CountsPettioner
from ap1 import ap1


if __name__=='__main__':
	#Create the parser
	parser = argparse.ArgumentParser(description="Launch the python module for the new pulse width core for the neutron monitors.")
	parser.add_argument('-sp','--serialPort',type=str, required=True, help='The port that will be used to read the data.')
	parser.add_argument('-db','--database',type=str,default='shell',help='The database where the data will be stored, by default the data will be printed on the shell.')
	parser.add_argument('-bm','--barometer',type=str,default=None,help='The barometer used for the pressure measurement')
	parser.add_argument('-spb','--serialPortBar',type=str,default=None,help='The port the barometer will use to to deliver the data')
	#parser.add_argument('-ch','--collectionHistograms',type=str,default='shell',help='The name of the collection which will store the data, by default the data will be printed on the shell.')
	#parser.add_argument('-cc','--collectionCounts',type=str,default='shell',help='The name of the collection which will store the data, by default the data will be printed on the shell.')

	#Parse the arguments
	args=parser.parse_args()

	#Initialize the Serial Port
	port=serial.Serial(port=args.serialPort,baudrate=921600)
	port.flush()
	port.flushInput()

	#Initialize the Database connection
	conn=None
	if args.database!='shell':
		conn = sqlite3.connect(args.database, check_same_thread=False)
		conn.execute("CREATE TABLE IF NOT EXISTS 'binTable' (\
					'start_date_time' datetime NOT NULL,\
					 'ch01' int(11) DEFAULT NULL,\
					 'ch02' int(11) DEFAULT NULL,\
					 'ch03' int(11) DEFAULT NULL,\
					 'ch04' int(11) DEFAULT NULL,\
					 'ch05' int(11) DEFAULT NULL,\
					 'ch06' int(11) DEFAULT NULL,\
					 'ch07' int(11) DEFAULT NULL,\
					 'ch08' int(11) DEFAULT NULL,\
					 'ch09' int(11) DEFAULT NULL,\
					 'ch10' int(11) DEFAULT NULL,\
					 'ch11' int(11) DEFAULT NULL,\
					 'ch12' int(11) DEFAULT NULL,\
					 'ch13' int(11) DEFAULT NULL,\
					 'ch14' int(11) DEFAULT NULL,\
					 'ch15' int(11) DEFAULT NULL,\
					 'ch16' int(11) DEFAULT NULL,\
					 'ch17' int(11) DEFAULT NULL,\
					 'ch18' int(11) DEFAULT NULL,\
					 'hv1' int(11) DEFAULT NULL,\
					 'hv2' int(11) DEFAULT NULL,\
					 'hv3' int(11) DEFAULT NULL,\
					 'temp_1' int(11) DEFAULT NULL,\
					 'temp_2' int(11) DEFAULT NULL,\
					 'atmPressure' int(11) DEFAULT NULL,\
					 PRIMARY KEY ('start_date_time')\
		)")

		conn.execute("CREATE TABLE IF NOT EXISTS 'EventsInfo10Mins'(\
					'start_date_time' datetime NOT NULL,\
					'overflows' TEXT DEFAULT NULL,\
					'lowLevels' TEXT DEFAULT NULL,\
					'ch01Histo' TEXT DEFAULT NULL,\
					'ch02Histo' TEXT DEFAULT NULL,\
					'ch03Histo' TEXT DEFAULT NULL,\
					'ch04Histo' TEXT DEFAULT NULL,\
					'ch05Histo' TEXT DEFAULT NULL,\
					'ch06Histo' TEXT DEFAULT NULL,\
					'ch07Histo' TEXT DEFAULT NULL,\
					'ch08Histo' TEXT DEFAULT NULL,\
					'ch09Histo' TEXT DEFAULT NULL,\
					'ch10Histo' TEXT DEFAULT NULL,\
					'ch11Histo' TEXT DEFAULT NULL,\
					'ch12Histo' TEXT DEFAULT NULL,\
					'ch13Histo' TEXT DEFAULT NULL,\
					'ch14Histo' TEXT DEFAULT NULL,\
					'ch15Histo' TEXT DEFAULT NULL,\
					'ch16Histo' TEXT DEFAULT NULL,\
					'ch17Histo' TEXT DEFAULT NULL,\
					'ch18Histo' TEXT DEFAULT NULL,\
					PRIMARY KEY ('start_date_time')\
		)")

	#Initialize all threads
	end_condition=threading.Event()
	end_condition.set()

	counts_condition=threading.Condition()
	shared_counts_data=[]
	shared_events_data=[]
	shared_pressure_data=None
	

	reader=Reader(port, end_condition, counts_condition, shared_counts_data, shared_events_data)
	contadores=CountsPettioner(port,end_condition, counts_condition, shared_counts_data, shared_events_data, conn)
	barometer=init_barometer(args.barometer, end_condition, shared_pressure_data, args.serialPortBar)
		
	reader.start()
	contadores.start()
	if barometer!=None:
		barometer['barometer'].start()

	import signal
	import sys

	#It looks like the KeyboardInterrupt exception is fired twice!!!!!!!!!!!!!!!!!!!!!!! 
	#For now this allows us to stop the threads relising the resources
	def signal_handler(signal, frame):
		print 'Bye Bye'
		end_condition.clear()
	signal.signal(signal.SIGINT,signal_handler)

	while end_condition.is_set():
		time.sleep(100000000000)

	conn.close()
	reader.join()
	contadores._Thread__stop()
	if barometer!=None:
		barometer['barometer']._Thread__stop()
	port.close()
	if 'port' in barometer:
		barometer['port'].close()

@staticmethod
def init_barometer(barometer_arg, end_condition, shared_pressure_data, port_arg):
	return {
        	'ap1': init_ap1(end_condition, shared_pressure_data),
        	'bm35': None,  #  TODO
        }.get(barometer_arg, None)  # The dafault value to return
	
@staticmethod
def init_ap1(end_condition, shared_pressure_data):
	ap1_bar=ap1(end_conditio, shared_pressure_data)
	return {'barometer':ap_1}

@staticmethod
def init_bm35(end_conditio, shared_pressure_data, port_arg):
	#  TODO init the port that will read the data
	#  TODO init the thread itself and return it
	#  return {'barometer':bm35_bar, 'port': the_press_port}	
	print '' # just to make compilation posible
