import pymongo
import sys
from time import strftime
import datetime
import numpy as np

#Read from console.
data=sys.stdin.read()
ite=0

#Default Mongo server and database.
client= pymongo.MongoClient('mongodb://localhost:27017')
db=client['testDatab']
start_time=1388534400


#While there is elements...
while ite < len(data):
	#Initialize the histogram with zeros
	#data_entry=[[0 for x in xrange(32)] for x in xrange (18)]
	data_entry=[[0 for x in xrange(64)] for x in xrange (18)]
	#60 secs
	for z in range (0,60):
		#Poisson random...
		s=np.random.poisson(5)
		#-5 lecturas * 18 tubos
		for y in range(0,(s*18)-1):
			channel = ord(data[ite])&0b00011111

			#Storing events as separate entries
			#valueLow = ord(data[ite+1])&0b01111111        
			#valueHigh = (ord(data[ite+2])&0b00011111)<<7
			#value=valueLow+valueHigh

			#Storing 5bit histogran
			#valueHigh = (ord(data[ite+2])&0b00011111) 

			#Storing 6bit histogram
			valueLow = (ord(data[ite+1])&0b01000000)>>6        
			valueHigh = (ord(data[ite+2])&0b00011111)<<1
			valueHigh = valueHigh+valueLow

			level = (ord(data[ite+2])&0b00100000)>>5
			
			data_entry[channel-1][valueHigh] +=1

			ite +=3
			if not ite < len(data):
				break

		if not ite < len(data):
			break

	time_entry=datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
	
	#Create the new entry
	entry={'start_date_time': time_entry,
		'histogram': data_entry,
	}
	#Insert the new entry in the collection
	#db.testEntries32.insert(entry)
	db.testEntries64.insert(entry)
	#Increment the time by 1 min..
	start_time +=60



#print some text 
print 'everything went well'

