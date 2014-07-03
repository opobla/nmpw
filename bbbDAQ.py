import argparse
import time
import threading
from time import strftime
import datetime
import serial
import pymongo

from Reader import Reader
from CountsPettioner import CountsPettioner


if __name__=='__main__':
	#Create the parser
	parser = argparse.ArgumentParser(description="Launch the python module for the new pulse width core for the neutron monitors.")
	parser.add_argument('-sp','--serialPort',type=str, required=True, help='The port that will be used to read the data.')
	parser.add_argument('-db','--database',type=str,default='shell',help='The database where the data will be stored, by default the data will be printed on the shell.')
	parser.add_argument('-ch','--collectionHistograms',type=str,default='shell',help='The name of the collection which will store the data, by default the data will be printed on the shell.')
	parser.add_argument('-cc','--collectionCounts',type=str,default='shell',help='The name of the collection which will store the data, by default the data will be printed on the shell.')

	#Parse the arguments
	args=parser.parse_args()

	#Initialize the Serial Port
	port=serial.Serial(port=args.serialPort,baudrate=921600)
	port.flush()
	port.flushInput()

	#Initialize the Database connection
	histo_collection_adapter=None
	counts_min_adapter=None
	if args.database!='shell' and  args.collectionHistograms!='shell':
		client=pymongo.MongoClient('mongodb://localhost:27017') #  TODO Set as configurable argument?
		histo_collection_adapter=client[args.database][args.collectionHistograms]	
	if args.database!='shell' and  args.collectionCounts!='shell':
		client=pymongo.MongoClient('mongodb://localhost:27017') #  TODO Set as configurable argument?
		counts_min_adapter=client[args.database][args.collectionCounts]	
		# TODO histo_collection_adapter.ensureIndex({start_date_time : 1})  #always or do it manually??????????
		# TODO counts_min_adapter.ensureIndex({start_date_time : 1})  #always or do it manually??????????

	#Initialize all threads
	end_condition=threading.Event()
	end_condition.set()

	counts_condition=threading.Condition()
	shared_counts_data=[]
	shared_events_data=[]

	reader=Reader(port, end_condition, counts_condition, shared_counts_data, shared_events_data)
	contadores=CountsPettioner(port,end_condition, counts_condition, shared_counts_data, shared_events_data, counts_min_adapter, histo_collection_adapter)
	reader.start()
	contadores.start()

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

	reader.join()
	contadores._Thread__stop()
	port.close()
