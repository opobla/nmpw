import time
import threading
from time import strftime
from threading import Thread
import datetime
import json
#import sqlite3

class CountsPettioner(threading.Thread):
	def __init__(self, port, end_condition, counts_condition, shared_counts_data, shared_events_data, database_adapter):
		threading.Thread.__init__(self)
		self.name='Contadores'
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
	
	def run(self):
		now_min=None
		while self.end_condition.is_set():
			now=time.time()
			if now_min==None:
				now_min=now-now%60
			else:
				if now_min+60 < now:   
						#acquire--release blocks executes atomicly.
					self.counts_condition.acquire()

					#Get Events data
					events_data=[self.shared_events_data[0][:],[x[:] for x in self.shared_events_data[1]],self.shared_events_data[2][:],self.shared_events_data[3][:]]
					self.shared_events_data[0][:]=[0 for x in xrange(18)]
					if now_min%600==0:
						self.shared_events_data[:]=[[0 for x in xrange(18)],[[0 for x in xrange(128)] for x in xrange(18)],[0 for x in xrange(18)],[0 for x in xrange(18)]]
					#Ask the FPGA for the counts data
					self.port.write(chr(17)) #0x11
						#wait release the lock and wait for a notification.
					self.counts_condition.wait()
					binTable=self.shared_counts_data[:]	
					self.counts_condition.release()

					#  TODO Pressure and HV sensors information.....

					time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
					entry_countsFromEvents={'start_date_time':time_entry,
								'binTableEvents':events_data[0],
					}
					if self.database_adapter==None:
						print entry_counts
					else:
						sql="INSERT INTO binTable (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18) values ('"+time_entry+"', "+`binTable[0]`+", "+`binTable[1]`+", "+`binTable[2]`+", "+`binTable[3]`+", "+`binTable[4]`+", "+`binTable[5]`+", "+`binTable[6]`+", "+`binTable[7]`+", "+`binTable[8]`+", "+`binTable[9]`+", "+`binTable[10]`+", "+`binTable[11]`+", "+`binTable[12]`+", "+`binTable[13]`+", "+`binTable[14]`+", "+`binTable[15]`+", "+`binTable[16]`+", "+`binTable[17]`+")"
						self.database_adapter.execute(sql)
						self.database_adapter.commit()
						
					#By default print the countsFromEvents 
					#  TODO decide if we want to save them
					print entry_countsFromEvents

					if now_min%600==540:
						time_entry=datetime.datetime.fromtimestamp(now_min-540).strftime('%Y-%m-%d %H:%M:%S')
						entry_histogram={	'start_date_time':time_entry,
									'histogram':events_data[1],
									'lowlevels':events_data[2],
									'overflows':events_data[3],
						}
						if self.database_adapter==None:
							print entry_histogram
						else:
							sql="insert into EventsInfo10Mins (start_date_time, overflows, lowLevels, ch01Histo, ch02Histo, ch03Histo, ch04Histo, ch05Histo, ch06Histo, ch07Histo, ch08Histo, ch09Histo, ch10Histo, ch11Histo, ch12Histo, ch13Histo, ch14Histo, ch15Histo, ch16Histo, ch17Histo, ch18Histo) values ('"+time_entry+"', '"+self.aux(events_data[3])+"', '"+self.aux(events_data[2])+"', '"+self.aux(events_data[1][0])+"', '"+self.aux(events_data[1][1])+"', '"+self.aux(events_data[1][2])+"', '"+self.aux(events_data[1][3])+"', '"+self.aux(events_data[1][4])+"', '"+self.aux(events_data[1][5])+"', '"+self.aux(events_data[1][6])+"', '"+self.aux(events_data[1][7])+"', '"+self.aux(events_data[1][8])+"', '"+self.aux(events_data[1][9])+"', '"+self.aux(events_data[1][10])+"', '"+self.aux(events_data[1][11])+"', '"+self.aux(events_data[1][12])+"', '"+self.aux(events_data[1][13])+"', '"+self.aux(events_data[1][14])+"', '"+self.aux(events_data[1][15])+"', '"+self.aux(events_data[1][16])+"', '"+self.aux(events_data[1][17])+"')"
							self.database_adapter.execute(sql)
							self.database_adapter.commit()

					now_min=now-now%60
				else:
					print 'The thread have woke up earlier, this shouldnt happend and this code is just to check... '

			time.sleep(60.0-time.time()%60)

