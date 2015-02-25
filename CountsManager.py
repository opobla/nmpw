import time
import threading
from time import strftime
from threading import Thread
import datetime
import json
import copy
import logging
import numpy
import MySQLdb
import math

from DBUpdater import DBUpdater

class CountsManager(threading.Thread):
	def __init__(self, port, end_condition, counts_condition, shared_counts, shared_countsFromEvents, shared_events, database_adapter, sensors_manager, dbUpConf, channel_avg, pressureConf, efficiencyConf):
		threading.Thread.__init__(self)
		self.name			='CountsManager'
		self.port			=port
		self.end_condition		=end_condition
		self.counts_condition		=counts_condition
		self.shared_counts		=shared_counts
		self.shared_countsFromEvents	=shared_countsFromEvents
		self.shared_events		=shared_events
		self.database_adapter		=database_adapter
		self.sensors_manager		=sensors_manager
		self.dbUpConf			=dbUpConf
		self.channel_avg		=channel_avg
		self.pressureConf		=pressureConf
		self.efficiencyConf		=efficiencyConf
		
	@staticmethod
	def aux (array_to_json):
		b=json.dumps(array_to_json)
		return b 

	#return a copy of the argument and resets he argument
	@staticmethod
	def copy_and_reset(data):
		the_copy=copy.deepcopy(data)
		CountsManager.reset_to_0(data)
		return the_copy

	
	@staticmethod
	def reset_to_0(the_array):
    		for i, e in enumerate(the_array):
        		if isinstance(e, list):
            			CountsManager.reset_to_0(e)
        		else:
            			the_array[i] = 0
			

	def save_counts(self, now_min, counts, sensors):
		# TODO you left it here......
		time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
		if self.database_adapter==None:
			print 'start_date_time:', time_entry, 'Counts:', binTable, 'Sensors:', sensors
		else:
			sql="INSERT INTO binTable (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, hv1, hv2, hv3, hv4, temp_1, temp_2, atmPressure) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			self.database_adapter.execute(sql, [time_entry]+ counts +[sensors['hv1'], sensors['hv2'], sensors['hv3'], sensors['hv4'], sensors['temp_1'], sensors['temp_2'], sensors['atmPressure']])
			self.database_adapter.commit()


	def save_countsFromEvents(self, now_min, countsFromEvents, sensors):
		time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
		if self.database_adapter==None:
			print 'start_date_time:', time_entry, 'CountsFromEvents:', binTableFromEvents, 'Sensors:', sensors
		else:
			sql="INSERT INTO binTableFromEvents (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, hv1, hv2, hv3, hv4, temp_1, temp_2, atmPressure) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			self.database_adapter.execute(sql, [time_entry]+ countsFromEvents +[sensors['hv1'], sensors['hv2'], sensors['hv3'], sensors['hv4'], sensors['temp_1'], sensors['temp_2'], sensors['atmPressure']])
			self.database_adapter.commit()
			

	def save_events(self, now_min, events):
		time_entry=datetime.datetime.fromtimestamp(now_min-540).strftime('%Y-%m-%d %H:%M:%S')
		if self.database_adapter==None:
			print '\nstart_date_time:',time_entry,'\nhistograms:',events_data[1],'\nlowlevels:',events_data[2],'\noverflows:',events_data[3]
		else:
			sql="insert into EventsInfo10Mins (start_date_time, overflows, lowLevels, ch01Histo, ch02Histo, ch03Histo, ch04Histo, ch05Histo, ch06Histo, ch07Histo, ch08Histo, ch09Histo, ch10Histo, ch11Histo, ch12Histo, ch13Histo, ch14Histo, ch15Histo, ch16Histo, ch17Histo, ch18Histo) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			self.database_adapter.execute(sql, [time_entry, self.aux(events[2]), self.aux(events[1])] + [self.aux(x) for x in events[0]])
			self.database_adapter.commit()


	def save_globals(self, now_min, uncorrected, corr_pressure, corr_efficiency, sensors):
		time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
		if self.database_adapter==None:
			print '\nstart_date_time:',time_entry,'\nuncorrected', uncorrected,'\ncorr_pressure:',corr_pressure,'\ncorr_efficiency:',corr_efficiency
		else:
			sql="insert into CALM_ori (start_date_time, length_time_interval_s, measured_uncorrected, measured_corr_for_efficiency, measured_corr_for_pressure, measured_pressure_mbar) values (?, ?, ?, ?, ?, ?)"
			self.database_adapter.execute(sql, [time_entry, 60, uncorrected, corr_efficiency, corr_pressure, sensors['atmPressure']])
			self.database_adapter.commit()

	@staticmethod
	def get_min(the_time):
		return the_time-the_time%60


	def getData(self,now_min):
		#Ask the FPGA for the counts data
		self.port.write('\x11') #0x11
		countsFromEvents=self.copy_and_reset(self.shared_countsFromEvents)
		events = []
		if now_min%600==540:
			events=self.copy_and_reset(self.shared_events)
		self.counts_condition.acquire()
		#  TODO make a method that copy the shared data and test it. The slice trick is weird..
		counts=self.shared_counts[:]	
		return counts, countsFromEvents, events

	def read_sensors(self):
		sensors_data={}
		sensors_data['atmPressure']=self.sensors_manager.read_pressure()
		sensors_data['hv1'], sensors_data['hv2'], sensors_data['hv3'], sensors_data['hv4']=self.sensors_manager.read_hvps()
		sensors_data['temp_1'], sensors_data['temp_2']=self.sensors_manager.read_temp()
		return sensors_data

	def update_remote(self):
		if self.dbUpConf!=None:
			the_dbUpdater=DBUpdater(self.dbUpConf)
			the_dbUpdater.start()

	def calc_globals(self, counts, sensors_data):
		uncorrected_min   	= self.medianAlgorithm(counts)
		uncorrected_sec  	= uncorrected_min/60.0
		corr_pressure_sec 	= uncorrected_sec * math.exp(self.pressureConf['beta'] * ((sensors_data['atmPressure']/100.0)-self.pressureConf['average']))
		corr_efficiency_sec	= self.efficiencyConf['beta'] * corr_pressure_sec
		return uncorrected_sec, corr_pressure_sec, corr_efficiency_sec

	def medianAlgorithm(self, counts):
		r= [float(x)/float(z) for x,z in zip (counts, self.channel_avg) 
				if z>0 and (float(x)/float(z))>0.3 and (float(x)/float(z))< 10] 
		tet = numpy.median(r)
		s0 = sum(self.channel_avg)
		summa = s0*tet
		return summa

	def run(self):
		now_min=None
		while self.end_condition.is_set():
			now=time.time()
			if now_min==None:
				now_min=self.get_min(now)
				sensors_data=self.read_sensors()

			else:
				if now_min+60 < now:   
					counts, countsFromEvents, events		=self.getData(now_min)
					uncorrected, corr_pressure, corr_efficiency 	=self.calc_globals(counts, sensors_data)
					print uncorrected, corr_pressure, "		--->", now_min

					self.save_counts(now_min, counts, sensors_data)
					self.save_countsFromEvents(now_min, countsFromEvents, sensors_data)
					if now_min%600==540:
						self.save_events(now_min, events)
					self.save_globals(now_min, uncorrected, corr_pressure, corr_efficiency, sensors_data)

					self.update_remote()
					sensors_data=self.read_sensors()
					## TODO Remove. The workaround of not having a barometer
					conn_remote = MySQLdb.connect(	host	= self.dbUpConf['remote']['host'], # your host, usually localhost
				 					user	= self.dbUpConf['remote']['user'], # your username
									passwd	= self.dbUpConf['remote']['pass'], # your password
									db	= 'nmdadb') # name of the data base
					remote_cursor = conn_remote.cursor()
					remote_cursor.execute("SELECT atmPressure FROM binTable ORDER BY start_date_time DESC LIMIT 1")
					sensors_data['atmPressure'] = remote_cursor.fetchone()[0]
					## TODO Remove. The workaround of not having a barometer
					now_min=self.get_min(now)
				else:
					logging.info(self.name+': The thread have woken up earlier')
			time.sleep(60.0-time.time()%60)

