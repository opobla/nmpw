import Adafruit_BBIO.GPIO as GPIO
import logging
import argparse
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
#from ap1 import ap1

def create_parser():
	#Create the parser
	parser = argparse.ArgumentParser(description="Launch the python module for the new pulse width core for the neutron monitors.")
	parser.add_argument('-sp','--serialPort',type=str, required=True, help='The port that will be used to read the data.')
	parser.add_argument('-db','--database',type=str,default='shell',help='The database where the data will be stored, by default the data will be printed on the shell.')
	parser.add_argument('-bm','--barometer',type=str,default=None,choices=['ap1', 'bm35'],help='The barometer used for the pressure measurement')
	parser.add_argument('-spb','--serialPortBar',type=str,default=None,help='The port the barometer will use to to deliver the data')

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
	port=init_port(args.serialPort, args_baudrate=921600)

	# Initialize the Serial Port for the barometer if one is needed.
	#  TODO Pass the spb baudrate as parameter or leave it as it is now
	port_bar=init_port(args.serialPortBar, args_baudrate=921600) #  TODO change the baudrate

	# Initialize the Database connection
	conn=init_database(args.database)

	return port, port_bar, conn

def init_threads(port, args_barometer, port_bar, conn):
	# Initialize all threads
	end_condition=threading.Event()
	end_condition.set()

	counts_condition=threading.Lock()
	counts_condition.acquire()
	shared_counts_data=[]
	shared_events_data=[]
	shared_pressure_data=None

	reader=Reader(port, end_condition, counts_condition, shared_counts_data, shared_events_data)
	counts=CountsPettioner(port,end_condition, counts_condition, shared_counts_data, shared_events_data, conn)
	barometer=None
	if args_barometer != None:
		# TODO init the barometer thread
		barometer='just to test'

	return reader, counts, barometer
	
def start_threads(reader, counts, barometer):
	reader.start()
	counts.start()
	if barometer != None:
		barometer.start()

def end_threads(reader, counts, barometer):
	reader.join()
	counts._Thread__stop()
	if barometer != None:
		barometer._Thread__stop()

def release_resources(port, port_bar, conn):
	port.close()
	if port_bar != None:
		port_bar.close()
	if conn!=None:
		conn.close()


if __name__=='__main__':
	# Init the P8_42
	GPIO.setup('P9_42', GPIO.OUT)
	GPIO.output("P9_42", GPIO.HIGH)

	logging.basicConfig(filename='nmwp.log', level=logging.DEBUG, format="%(asctime)s   %(message)s")
	logging.info('.........................')
	logging.info('.........................')
	logging.info('Started')

	args=create_parser().parse_args()
	port, port_bar, conn = init_resources(args)

	reader, counts, barometer= init_threads(port, args.barometer, port_bar, conn)
	start_threads(reader, counts, barometer)
	
	#For now this allows us to stop the threads relising the resources
	def signal_handler(signal, frame):
		logging.info('End requested')
		print 'Bye Bye'
		reader.end_condition.clear()
	signal.signal(signal.SIGINT,signal_handler)

	while reader.end_condition.is_set():
		time.sleep(100000000000)

	end_threads(reader, counts, barometer)
	release_resources(port, port_bar, conn)

	logging.info('Correctly ended. bye')
	
def init_barometer(barometer_arg, end_condition, shared_pressure_data, port_arg):
	return {
        	'ap1': init_ap1(end_condition, shared_pressure_data),
        	'bm35': {'barometer':None,'port':None},  #  TODO
		None:{},
        }[barometer_arg]  # The dafault value to return
	
def init_ap1(end_condition, shared_pressure_data):
	ap1_bar=None#ap1(end_conditio, shared_pressure_data)
	return {'barometer':ap1_bar}

def init_bm35(end_conditio, shared_pressure_data, port_arg):
	#  TODO init the port that will read the data
	#  TODO init the thread itself and return it
	#  return {'barometer':bm35_bar, 'port': the_press_port}	
	print '' # just to make compilation posible
