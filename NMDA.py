import Adafruit_BBIO.UART as UART
import Adafruit_BBIO.GPIO as GPIO
import logging
import argparse
import ConfigParser
import time
import threading
from time import strftime
from datetime import datetime
import serial
import sqlite3
import MySQLdb
import signal
import sys

from FPGASerialReader import FPGASerialReader
from CountsManager import CountsManager
from SensorsManager import SensorsManager
#from validate_arguments import validate_arguments

def create_parser():
	#Create the parser

	config = ConfigParser.SafeConfigParser()
	try:
    		config.read(['/server/nmda/.NMDA.conf'])
    		basics 		= dict(config.items("Basics"))
		sensors 	= dict(config.items("Sensors"))
		dbUpdater 	= dict(config.items("dbUpdater"))
		pressure	= dict(config.items("Pressure"))
		efficiency	= dict(config.items("Efficiency"))
		defaults 	= dict(basics.items() + sensors.items() + dbUpdater.items()+ pressure.items()+efficiency.items())
	
	except:
		print 'Probably the .NMDA.conf file is not configured. The NMDA.conf.example is an example file of how to config the .NMDA.conf file'
		logging.info('Probably the .NMDA.conf file is not configured. The NMDA.conf.example is an example file of how to config the .NMDA.conf file')
		print 'Exiting'
		logging.info('Exiting')
		sys.exit(0)

	# Simple cast
	for key in defaults:
		if defaults[key]=='None':
			defaults[key]=None
		if defaults[key]=='True':
			defaults[key]=True
		if defaults[key]=='False':
			defaults[key]=False
		if key == 'channel_avg':
			defaults[key]=[int(i) for i in defaults[key].split(',')]

	parser = argparse.ArgumentParser(description="Launch the python module for the new pulse width core for the neutron monitors.")
	parser.set_defaults(**defaults)
	parser.add_argument('-sp',  '--serial_port_control', help='The port that will be used to read the data.')
	parser.add_argument('-db',  '--database', help='The database where the data will be stored, by default the data will be printed on the shell.')
	parser.add_argument('-sps', '--serial_port_sensors', help='The port the sensors will use to deliver their data.')
	parser.add_argument('-bm',  '--barometer_type', choices=['ap1', 'bm35'],help='The barometer used for the pressure measurement.')
	parser.add_argument('-hv',  '--hvps_type', choices=['digital','analog'],help='Analog or Digital high voltage power suplly.')
	parser.add_argument('-ahvc','--analog_hvps_corr', type=float, help='Correction coefficient for the analog hvps.')

	parser.add_argument('-dbU', '--db_updater_enabled', help='Enables or disables the remote databese updater(DBUpdater).')
	parser.add_argument('-ldb', '--local_db', help='The database the DBUpdater uses to read values from.')
	parser.add_argument('-rh',  '--remote_db_host', help='The host where the remote dabase is.')
	parser.add_argument('-ru',  '--remote_db_user', help='Username for the remote database host.')
	parser.add_argument('-rp',  '--remote_db_pass', help='Password for the remote database host.')
	parser.add_argument('-rdb', '--remote_db_db',   help='The name of the remote database.')

	parser.add_argument('-apr', '--avg_pressure',   help='Average atmospheric pressure for the station.')


	return parser

def validate_arguments(args):
	# Arguments always needed
	if args.serial_port_control==None:
		end('A control serial port is needed')
	if args.database==None:
		end('A database is needed')

	# Valid bar_type 
	if not(args.barometer_type==None or args.barometer_type=='ap1' or args.barometer_type=='bm35'):
		end('Invalid barometer type')

	# Valid hvps_type
	if not(args.hvps_type==None or args.hvps_type=='digital' or args.hvps_type=='analog'):
		end('Invalid hvps_type')

	# The needed port are present
	if (args.hvps_type=='digital' or args.barometer_type=='bm35') and (args.serial_port_control==None or args.serial_port_sensors==None):
		end('In order to read data from a digital hvps we need two ports, one for control and one for data')

	if args.db_updater_enabled==True:
		if args.local_db==None or args.local_db!=args.database:
			end('Incorrect local_db')
		if args.remote_db_host==None:
			end('If db_updater is enabled a remote_db_host must be set')
		if args.remote_db_user==None or args.remote_db_pass==None:
			end('A user and pass must be given for the remote database')
		if args.remote_db_db==None:
			end('The remote database name must be specified')

def end(error_msg):
	logging.info('Argument validator: '+error_msg)
	logging.info('Exiting')
	raise AttributeError(error_msg)




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

		conn.execute("CREATE TABLE IF NOT EXISTS 'CALM_ori'(\
					'start_date_time' datetime NOT NULL,\
					'length_time_interval_s' int(5) NOT NULL,\
					'measured_uncorrected' float unsigned DEFAULT NULL,\
					'measured_corr_for_efficiency' float unsigned DEFAULT NULL,\
					'measured_corr_for_pressure' float unsigned DEFAULT NULL,\
					'measured_pressure_mbar' float DEFAULT NULL,\
					PRIMARY KEY ('start_date_time')\
		)")
	# Finaly return the database connection
	return conn

def init_remote_database(dbUpConf):
	remote=dbUpConf['remote']
	conn_remote = MySQLdb.connect(	host= 	remote['host'], # your host, usually localhost
					user= 	remote['user'], # your username
					passwd= remote['pass']) # your password

	cur = conn_remote.cursor()
	cur.execute('CREATE DATABASE IF NOT EXISTS '+ remote['database'] +';')
	cur.execute('use '+ remote['database'] +';')

	cur.execute("CREATE TABLE IF NOT EXISTS binTable (\
				 start_date_time datetime NOT NULL,\
				 ch01 int(11) DEFAULT NULL,\
				 ch02 int(11) DEFAULT NULL,\
				 ch03 int(11) DEFAULT NULL,\
				 ch04 int(11) DEFAULT NULL,\
				 ch05 int(11) DEFAULT NULL,\
				 ch06 int(11) DEFAULT NULL,\
				 ch07 int(11) DEFAULT NULL,\
				 ch08 int(11) DEFAULT NULL,\
				 ch09 int(11) DEFAULT NULL,\
				 ch10 int(11) DEFAULT NULL,\
				 ch11 int(11) DEFAULT NULL,\
				 ch12 int(11) DEFAULT NULL,\
				 ch13 int(11) DEFAULT NULL,\
				 ch14 int(11) DEFAULT NULL,\
				 ch15 int(11) DEFAULT NULL,\
				 ch16 int(11) DEFAULT NULL,\
				 ch17 int(11) DEFAULT NULL,\
				 ch18 int(11) DEFAULT NULL,\
				 hv1 int(11) DEFAULT NULL,\
				 hv2 int(11) DEFAULT NULL,\
				 hv3 int(11) DEFAULT NULL,\
				 hv4 int(11) DEFAULT NULL,\
				 temp_1 int(11) DEFAULT NULL,\
				 temp_2 int(11) DEFAULT NULL,\
				 atmPressure int(11) DEFAULT NULL,\
				 PRIMARY KEY (start_date_time)\
	)")

	cur.execute("CREATE TABLE IF NOT EXISTS binTableFromEvents (\
				 start_date_time datetime NOT NULL,\
				 ch01 int(11) DEFAULT NULL,\
				 ch02 int(11) DEFAULT NULL,\
				 ch03 int(11) DEFAULT NULL,\
				 ch04 int(11) DEFAULT NULL,\
				 ch05 int(11) DEFAULT NULL,\
				 ch06 int(11) DEFAULT NULL,\
				 ch07 int(11) DEFAULT NULL,\
				 ch08 int(11) DEFAULT NULL,\
				 ch09 int(11) DEFAULT NULL,\
				 ch10 int(11) DEFAULT NULL,\
				 ch11 int(11) DEFAULT NULL,\
				 ch12 int(11) DEFAULT NULL,\
				 ch13 int(11) DEFAULT NULL,\
				 ch14 int(11) DEFAULT NULL,\
				 ch15 int(11) DEFAULT NULL,\
				 ch16 int(11) DEFAULT NULL,\
				 ch17 int(11) DEFAULT NULL,\
				 ch18 int(11) DEFAULT NULL,\
				 hv1 int(11) DEFAULT NULL,\
				 hv2 int(11) DEFAULT NULL,\
				 hv3 int(11) DEFAULT NULL,\
				 hv4 int(11) DEFAULT NULL,\
				 temp_1 int(11) DEFAULT NULL,\
				 temp_2 int(11) DEFAULT NULL,\
				 atmPressure int(11) DEFAULT NULL,\
				 PRIMARY KEY (start_date_time)\
	)")

	cur.execute("CREATE TABLE IF NOT EXISTS EventsInfo10Mins(\
				start_date_time datetime NOT NULL,\
				overflows TEXT DEFAULT NULL,\
				lowLevels TEXT DEFAULT NULL,\
				ch01Histo TEXT DEFAULT NULL,\
				ch02Histo TEXT DEFAULT NULL,\
				ch03Histo TEXT DEFAULT NULL,\
				ch04Histo TEXT DEFAULT NULL,\
				ch05Histo TEXT DEFAULT NULL,\
				ch06Histo TEXT DEFAULT NULL,\
				ch07Histo TEXT DEFAULT NULL,\
				ch08Histo TEXT DEFAULT NULL,\
				ch09Histo TEXT DEFAULT NULL,\
				ch10Histo TEXT DEFAULT NULL,\
				ch11Histo TEXT DEFAULT NULL,\
				ch12Histo TEXT DEFAULT NULL,\
				ch13Histo TEXT DEFAULT NULL,\
				ch14Histo TEXT DEFAULT NULL,\
				ch15Histo TEXT DEFAULT NULL,\
				ch16Histo TEXT DEFAULT NULL,\
				ch17Histo TEXT DEFAULT NULL,\
				ch18Histo TEXT DEFAULT NULL,\
				PRIMARY KEY (start_date_time)\
	)")



def init_resources(args):
	UART.setup("UART1")
	UART.setup("UART2")
	# Initialize the Serial Port
	port=init_port(args.serial_port_control, args_baudrate=921600)

	# Initialize the Serial Port for the barometer if one is needed.
	#  TODO Pass the sps baudrate as parameter or leave it as it is now
	port_sensors=init_port(args.serial_port_sensors, args_baudrate=2400) #  TODO change the baudrate

	# Initialize the Database connection
	conn=init_database(args.database)

	# Initialize the Sensors Manager
	sensors_manager=SensorsManager('Sensor Manager', bar_type=args.barometer_type, hvps_type=args.hvps_type, port_control=port, port_data=port_sensors, analog_hvps_corr=args.analog_hvps_corr)

	return port, port_sensors, conn, sensors_manager

def init_threads(port, args, port_sensors, conn, sensors_manager):
	# Initialize all threads
	counts_condition=threading.Lock()
	counts_condition.acquire()
	shared_counts		=[]
	shared_countsFromEvents	=[]
	shared_events		=[]

	dbUpConf=None
	if args.db_updater_enabled==True:
		dbUpConf={'local':{'name':args.local_db}, 'remote':{'host':args.remote_db_host, 'user':args.remote_db_user, 'pass':args.remote_db_pass, 'database': args.remote_db_db}}
		#  TODO Discuss this try catch block
		try:
			init_remote_database(dbUpConf)
		except:
			print 'Could not correctly init the remote database, but  the data acquisition software will continue as expected. The software will anyway try to write the data to the remote database every minute.'
			logging.info('Could not correctly init the remote database, but  the data acquisition software will continue as expected. The software will anyway try to write the data to the remote database every minute.')
	pressureConf 	= {'average':float(args.avg_pressure), 'beta':float(args.beta_pressure)}
	efficiencyConf	= {'beta':float(args.beta_efficiency)}
	
	reader=FPGASerialReader(port, counts_condition, shared_counts, shared_countsFromEvents, shared_events)
	counts=CountsManager(port, counts_condition, shared_counts, shared_countsFromEvents, shared_events, conn, sensors_manager, dbUpConf, args.channel_avg, pressureConf, efficiencyConf)
	
	return reader, counts
	
def start_threads(reader, counts):
	reader.start()
	counts.start()

def end_threads(reader, counts):
	reader._Thread__stop()
	counts._Thread__stop()

def release_resources(port, port_sensors, conn):
	port.close()
	if port_sensors != None:
		port_sensors.close()
	if conn!=None:
		conn.close()


if __name__=='__main__':
	# Init the loogger and log we are starting the program
	logging.basicConfig(filename='/server/logs/NMDA.log', level=logging.DEBUG, format="%(asctime)s   %(message)s")
	logging.info('                         ')
	logging.info('                         ')
	logging.info('Started')

	# Init the P9_42. First we active the Reset signal for 0.5 secs
	GPIO.setup('P9_42', GPIO.OUT)
	GPIO.output("P9_42", GPIO.LOW)
	time.sleep(0.5)
	GPIO.output("P9_42", GPIO.HIGH)
	
	args=create_parser().parse_args()
	print args
	validate_arguments(args)

	port, port_sensors, conn, sensors_manager= init_resources(args)

	reader, counts= init_threads(port, args, port_sensors, conn, sensors_manager)
	start_threads(reader, counts)
	
	end_condition=threading.Event()
	end_condition.set()
	def signal_handler(signal, frame):
		logging.info('End requested')
		print 'Bye Bye'
		end_condition.clear()
	signal.signal(signal.SIGINT,signal_handler)
	while end_condition.is_set():
		time.sleep(100000000000)

	end_threads(reader, counts)
	release_resources(port, port_sensors, conn)
	logging.info('Correctly ended. bye')
