import time
import threading
from time import strftime
from threading import Thread
import datetime
import json
#import sqlite3
import copy

class CountsPettioner(threading.Thread):
	def __init__(self, port, end_condition, counts_condition, shared_counts_data, shared_events_data, database_adapter):
		threading.Thread.__init__(self)
		self.name='CountsPettioner'
		self.port=port
		self.end_condition=end_condition
		self.counts_condition=counts_condition
		self.shared_counts_data=shared_counts_data
		self.shared_events_data=shared_events_data
	
		self.database_adapter=database_adapter

	@staticmethod
	def aux (array_to_json):
		b=json.dumps(array_to_json)
		return b 

	#return a copy of the argument and resets he argument
	@staticmethod
	def copy_and_reset(data, bool_all):
		events_data=copy.deepcopy(data)
		if bool_all:
			CountsPettioner.reset_to_0(data)
		else:
			CountsPettioner.reset_to_0(data[0]) #  TODO change to data['CountsFromEvents']
		return events_data

	
	@staticmethod
	def reset_to_0(the_array):
    		for i, e in enumerate(the_array):
        		if isinstance(e, list):
            			CountsPettioner.reset_to_0(e)
        		else:
            			the_array[i] = 0
			

	def save_BinTable(self, now_min, binTable, sensors):
		time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
		if self.database_adapter==None:
			print 'start_date_time:', time_entry, 'Counts:', binTable, 'Sensors:', sensors
		else:
			sql="INSERT INTO binTable (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, hv1, hv2, hv3, temp_1, temp_2, atmPressure) values ('"+time_entry+"', "+`binTable[0]`+", "+`binTable[1]`+", "+`binTable[2]`+", "+`binTable[3]`+", "+`binTable[4]`+", "+`binTable[5]`+", "+`binTable[6]`+", "+`binTable[7]`+", "+`binTable[8]`+", "+`binTable[9]`+", "+`binTable[10]`+", "+`binTable[11]`+", "+`binTable[12]`+", "+`binTable[13]`+", "+`binTable[14]`+", "+`binTable[15]`+", "+`binTable[16]`+", "+`binTable[17]`+", "+`sensors['hv1']`+", "+`sensors['hv2']`+", "+`sensors['hv3']`+", "+`sensors['temp_1']`+", "+`sensors['temp_2']`+", "+`sensors['atmPressure']`+")"
			self.database_adapter.execute(sql)
			self.database_adapter.commit()


	def save_BinTableFromEvents(self, now_min, binTableFromEvents, sensors):
		time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
		if self.database_adapter==None:
			print 'start_date_time:', time_entry, 'CountsFromEvents:', binTableFromEvents, 'Sensors:', sensors
		else:
			sql="INSERT INTO binTableFromEvents (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, hv1, hv2, hv3, temp_1, temp_2, atmPressure) values ('"+time_entry+"', "+`binTableFromEvents[0]`+", "+`binTableFromEvents[1]`+", "+`binTableFromEvents[2]`+", "+`binTableFromEvents[3]`+", "+`binTableFromEvents[4]`+", "+`binTableFromEvents[5]`+", "+`binTableFromEvents[6]`+", "+`binTableFromEvents[7]`+", "+`binTableFromEvents[8]`+", "+`binTableFromEvents[9]`+", "+`binTableFromEvents[10]`+", "+`binTableFromEvents[11]`+", "+`binTableFromEvents[12]`+", "+`binTableFromEvents[13]`+", "+`binTableFromEvents[14]`+", "+`binTableFromEvents[15]`+", "+`binTableFromEvents[16]`+", "+`binTableFromEvents[17]`+", "+`sensors['hv1']`+", "+`sensors['hv2']`+", "+`sensors['hv3']`+", "+`sensors['temp_1']`+", "+`sensors['temp_2']`+", "+`sensors['atmPressure']`+")"
			self.database_adapter.execute(sql)
			self.database_adapter.commit()
			

	def save_EventsInfo(self, now_min, events_data):
		time_entry=datetime.datetime.fromtimestamp(now_min-540).strftime('%Y-%m-%d %H:%M:%S')
		if self.database_adapter==None:
			print '\nstart_date_time:',time_entry,'\nhistograms:',events_data[1],'\nlowlevels:',events_data[2],'\noverflows:',events_data[3]
		else:
			sql="insert into EventsInfo10Mins (start_date_time, overflows, lowLevels, ch01Histo, ch02Histo, ch03Histo, ch04Histo, ch05Histo, ch06Histo, ch07Histo, ch08Histo, ch09Histo, ch10Histo, ch11Histo, ch12Histo, ch13Histo, ch14Histo, ch15Histo, ch16Histo, ch17Histo, ch18Histo) values ('"+time_entry+"', '"+self.aux(events_data[3])+"', '"+self.aux(events_data[2])+"', '"+self.aux(events_data[1][0])+"', '"+self.aux(events_data[1][1])+"', '"+self.aux(events_data[1][2])+"', '"+self.aux(events_data[1][3])+"', '"+self.aux(events_data[1][4])+"', '"+self.aux(events_data[1][5])+"', '"+self.aux(events_data[1][6])+"', '"+self.aux(events_data[1][7])+"', '"+self.aux(events_data[1][8])+"', '"+self.aux(events_data[1][9])+"', '"+self.aux(events_data[1][10])+"', '"+self.aux(events_data[1][11])+"', '"+self.aux(events_data[1][12])+"', '"+self.aux(events_data[1][13])+"', '"+self.aux(events_data[1][14])+"', '"+self.aux(events_data[1][15])+"', '"+self.aux(events_data[1][16])+"', '"+self.aux(events_data[1][17])+"')"
			self.database_adapter.execute(sql)
			self.database_adapter.commit()

	def save_data(self, now_min, data, sensors_data):
		self.save_BinTable(now_min,data['Counts'],sensors_data)
		self.save_BinTableFromEvents(now_min,data['EventsInfo'][0],sensors_data)
		if now_min%600==540:
			self.save_EventsInfo(now_min,data['EventsInfo'])


	@staticmethod
	def get_min(the_time):
		return the_time-the_time%60


	def request_get_Counts_EventsInfo(self,now_min):
		#acquire--release blocks executes atomicly.
		self.counts_condition.acquire()
		events_data=self.copy_and_reset(self.shared_events_data, now_min%600==540)
		#Ask the FPGA for the counts data
		self.port.write('\x11') #0x11
		#wait release the lock and wait for a notification.
		self.counts_condition.wait()

		#  TODO make a method that copy the shared data and test it. The slice trick is weird..
		binTable=self.shared_counts_data[:]	
		self.counts_condition.release()
		return {'Counts':binTable,'EventsInfo':events_data}

	def run(self):
		now_min=None
		while self.end_condition.is_set():
			now=time.time()
			if now_min==None:
				now_min=self.get_min(now)
			else:
				if now_min+60 < now:   
					data=self.request_get_Counts_EventsInfo(now_min)
					#  TODO Pressure and HV sensors information.....
					sensors_data={'hv1':-1,'hv2':-1,'hv3':-1,'temp_1':-1,'temp_2':-1,'atmPressure':-1}
					
					self.save_data(now_min, data, sensors_data)

					now_min=self.get_min(now)
				else:
					raise AssertionError('The thread have woken up earlier')
			time.sleep(60.0-time.time()%60)

