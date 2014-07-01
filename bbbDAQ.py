import argparse
import time
import threading
from time import strftime
import datetime
import serial
import pymongo


class Contadores(threading.Thread):
	def __init__(self, port, end_condition):
		threading.Thread.__init__(self)
		self.name='Contadores'
		self.port=port
		self.end_condition=end_condition

	def run(self):
		now_min=None
		while self.end_condition.is_set():
			now=time.time()
			if now_min==None:
				now_min=now-now%60
			else:
				if now_min+60 < now:
					#  TODO write in the port requesting the counts....
					print 'Contadores wake up time: ',now
					now_min=now-now%60

			#Instead of having the thread sleeping for 60 secs we have it taking short cat naps every sec. This way the thread is more responsive when trying to close it...
			time.sleep(min(1.0,60-time.time()%60))

class Reader(threading.Thread):
	def __init__(self, port, end_condition, histo_collection_adapter):
		threading.Thread.__init__(self)
		self.name='Reader'
		self.port=port
		self.end_condition=end_condition
		self.histo_collection_adapter=histo_collection_adapter

		self.status='bytex'
		self.histo_data=[[0 for x in xrange(128)] for x in xrange(18)]
		self.events_min=[0 for x in xrange(18)]
		self.low_events=[0 for x in xrange(18)]
		self.overflows=[0 for x in xrange(18)]
	def run(self):
		now_min=None
		now_ten_min=None
		while self.end_condition.is_set():
			next=self.port.read(1)
			if not next:
				break

			if ((ord(next[0]) & 0b11000000) == 0b00000000):
        			self.status="bytex"
        			print 'OVERFLOW'
				#  TODO Read 2 more bytes and update the self.overflow
				#  TODO Add more states to handle correctly overflows data.
        			continue

    			if ((ord(next[0]) & 0b11100000) == 0b01000000):
        			self.status="byte1"
        			channel=ord(next[0]) & 0b00011111
        			continue

    			if  self.status=="byte1" and ((ord(next[0]) & 0b10000000) == 0b10000000):
        			self.status="byte2"
        			count06=ord(next[0]) & 0b01111111
        			continue

    			if self.status=="byte2" and ((ord(next[0]) & 0b10000000) == 0b10000000):
        			self.status="byte3"
        			count711=ord(next[0]) & 0b00011111
        			pulse_type=(ord(next[0]) & 0b00100000) >> 5
        			pulse_width_ticks=count06 + (count711 << 7)

				now=time.time()
				
				#  TODO Do we want events per minute. With overflows evets can be lost. Its more reliable to use the data generated from the FPGA?
				#Events per minute
        			if now_min==None:
            				now_min=now-now%60
        			else:
            				if now_min+60 < now:
						#  TODO Decide if we want low level pulses every min or 10mins
						time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
						entry={	'start_date_time':time_entry,
							'binTable_incompleto':self.events_min,
						}
						if True: #  TODO
							print entry
						else:
							print ''#this is here just to make compilation posible 
							#  TODO Safe to mongodb

						#Clear the saved data
						self.events_min=[0 for x in xrange(18)]

						#Update the interval
            					now_min=now-now%60
				
				#Histograms every ten minutes
				if now_ten_min==None:
            				now_ten_min=now-now%600
        			else:
            				if now_ten_min+600 < now:
						#  TODO Decide if we want low level pulses every min or 10mins
						time_entry=datetime.datetime.fromtimestamp(now_ten_min).strftime('%Y-%m-%d %H:%M:%S')
						#Considerar secuencia de eventos
						#Minuto Nuevo >> Overflow >> Overflow >> Correct data
						#Tendriamos dos overflow que no pertenecen al minuto..
						#Es algo con lo que podemos vivir?
						entry={	'start_date:time':time_entry,
							'histogram':self.histo_data,
							'low_levels':self.low_events,
							'overflows':self.overflows,	
						}
						if self.histo_collection_adapter==None:
							print entry
						else:
							self.histo_collection_adapter.insert(entry)

						#Clear the saved data
						self.histo_data=[[0 for x in xrange(128)] for x in xrange(18)]
						self.low_events=[0 for x in xrange(18)]
						self.overflows=[0 for x in xrange(18)]

						#Update the interval
            					now_ten_min=now-now%600

				if pulse_type==0:
					self.low_events[channel] +=1
				if pulse_type==1:
					self.histo_data[channel][pulse_width_ticks>>5] +=1
					self.events_min[channel] +=1
				

        			print datetime.datetime.now().time(),"Ch:",channel,"Pulse type:",pulse_type," Pulse width:",pulse_width_ticks,\
                			float(pulse_width_ticks) / 50.0,"useg"
        			continue



if __name__=='__main__':
	#Create the parser
	parser = argparse.ArgumentParser(description="Launch the python module for the new pulse width core for the neutron monitors.")
	parser.add_argument('-sp','--serialPort',type=str, required=True, help='The port that will be used to read the data.')
	parser.add_argument('-db','--database',type=str,default='shell',help='The database where the data will be stored, by default the data will be printed on the shell.')
	parser.add_argument('-c','--collection',type=str,default='shell',help='The name of the collection which will store the data, by default the data will be printed on the shell.')

	#Parse the arguments
	args=parser.parse_args()

	#Initialize the Serial Port
	port=serial.Serial(port=args.serialPort,baudrate=921600)
	port.flush()
	port.flushInput()

	#Initialize the Database connection
	histo_collection_adapter=None
	if args.database!='shell' and  args.collection!='shell':
		client=pymongo.MongoClient('mongodb://localhost:27017') #  TODO Set as configurable argument?
		histo_collection_adapter=client[args.database][args.collection]	
		# TODO histo_collection_adapter.ensureIndex({start_date_time : 1})  #always or do it manually??????????

	#Initialize all threads
	end_condition=threading.Event()
	end_condition.set()
	reader=Reader(port, end_condition, histo_collection_adapter)
	contadores=Contadores(port,end_condition)
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
	contadores.join()
	port.close()

