import Adafruit_BBIO.GPIO as GPIO
import logging
import argparse
import ConfigParser
import time
import threading
from time import strftime
from datetime import datetime
import serial
#import pymongo
import sqlite3
import signal
import sys

from Reader import Reader
from CountsPettioner import CountsPettioner
from SensorsManager import SensorsManager

def create_parser():
	#Create the parser

	config = ConfigParser.SafeConfigParser()
	try:
    		config.read(['/server/nmpw/.nmpw.conf'])
    		basics = dict(config.items("Basics"))
		sensors = dict(config.items("Sensors"))
		defaults = dict(basics.items() + sensors.items())
	
	except:
		print 'Probably the .nmpw.conf file is not configured. The nmpw.conf.example is an example file of how to config the .nmpw.conf file'
		logging.info('Probably the .nmpw.conf file is not configured. The nmpw.conf.example is an example file of how to config the .nmpw.conf file')
		print 'Exiting'
		logging.info('Exiting')
		sys.exit(0)

	# Simple cast
	for key in defaults:
		if defaults[key]=='None':
			defaults[key]=None

	parser = argparse.ArgumentParser(description="Launch the python module for the new pulse width core for the neutron monitors.")
	parser.set_defaults(**defaults)
	parser.add_argument('-sp','--serial_port_control', help='The port that will be used to read the data.')
	parser.add_argument('-db','--database', help='The database where the data will be stored, by default the data will be printed on the shell.')
	parser.add_argument('-sps','--serial_port_sensors', help='The port the sensors will use to deliver their data')
	parser.add_argument('-bm','--barometer_type', choices=['ap1', 'bm35'],help='The barometer used for the pressure measurement')
	parser.add_argument('-hv','--hvps_type', choices=['digital','analog'],help='Analog or Digital high voltage power suplly')

	return parser


def init_port(args_port, args_baudrate):
	if args_port != None:
		port=serial.Serial(port=args_port, baudrate=args_baudrate)
		port.flush()
		return port
	return None

def init_database(args_database):
	conn=None
	if args_database!='shell':
		conn = sqlite3.connect(args_database, check_same_thread=False)
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
					 'hv4' int(11) DEFAULT NULL,\
					 'temp_1' int(11) DEFAULT NULL,\
					 'temp_2' int(11) DEFAULT NULL,\
					 'atmPressure' int(11) DEFAULT NULL,\
					 PRIMARY KEY ('start_date_time')\
		)")

		conn.execute("CREATE TABLE IF NOT EXISTS 'binTableFromEvents' (\
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
					 'hv4' int(11) DEFAULT NULL,\
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
	# Finaly return the database connection
	return conn


def init_resources(args):
	# Initialize the Serial Port
	port=init_port(args.serial_port_control, args_baudrate=921600)

	# Initialize the Serial Port for the barometer if one is needed.
	#  TODO Pass the sps baudrate as parameter or leave it as it is now
	port_sensors=init_port(args.serial_port_sensors, args_baudrate=921600) #  TODO change the baudrate

	# Initialize the Database connection
	conn=init_database(args.database)

	return port, port_sensors, conn

def init_threads(port, args, port_sensors, conn):
	# Initialize all threads
	end_condition=threading.Event()
	end_condition.set()

	counts_condition=threading.Lock()
	counts_condition.acquire()
	shared_counts_data=[]
	shared_events_data=[]
	shared_sensors_data=[]

	sensors_manager=SensorsManager('Sensor Manager', bar_type=args.barometer_type, hvps_type=args.hvps_type, port_control=port, port_data=port_sensors)

	reader=Reader(port, end_condition, counts_condition, shared_counts_data, shared_events_data)
	counts=CountsPettioner(port,end_condition, counts_condition, shared_counts_data, shared_events_data, conn, sensors_manager)
	
	return reader, counts
	
def start_threads(reader, counts):
	reader.start()
	counts.start()

def end_threads(reader, counts):
	reader.join()
	counts._Thread__stop()

def release_resources(port, port_sensors, conn):
	port.close()
	if port_sensors != None:
		port_sensors.close()
	if conn!=None:
		conn.close()


if __name__=='__main__':
	# Init the P9_42. First we active the Reset signal for 0.5 secs
	GPIO.setup('P9_42', GPIO.OUT)
	GPIO.output("P9_42", GPIO.LOW)
	#time.sleep(0.5)
	GPIO.output("P9_42", GPIO.HIGH)

	# Init the loogger and log we are starting the program
	logging.basicConfig(filename='/server/logs/nmpw.log', level=logging.DEBUG, format="%(asctime)s   %(message)s")
	logging.info('.........................')
	logging.info('.........................')
	logging.info('Started')

	args=create_parser().parse_args()
	port, port_sensors, conn = init_resources(args)

	reader, counts= init_threads(port, args, port_sensors, conn)
	start_threads(reader, counts)
	
	#For now this allows us to stop the threads relising the resources
	def signal_handler(signal, frame):
		logging.info('End requested')
		print 'Bye Bye'
		reader.end_condition.clear()
	signal.signal(signal.SIGINT,signal_handler)

	while reader.end_condition.is_set():
		time.sleep(100000000000)

	end_threads(reader, counts)
	release_resources(port, port_sensors, conn)

	logging.info('Correctly ended. bye')
