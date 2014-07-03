import time
import threading
from time import strftime
from threading import Thread
import datetime

class CountsPettioner(threading.Thread):
	def __init__(self, port, end_condition, counts_condition, shared_counts_data, shared_events_data, counts_min_adapter, histo_collection_adapter):
		threading.Thread.__init__(self)
		self.name='Contadores'
		self.port=port
		self.end_condition=end_condition
		self.counts_condition=counts_condition
		self.shared_counts_data=shared_counts_data
		self.shared_events_data=shared_events_data
		self.counts_min_adapter=counts_min_adapter
		self.histograms_adapter=histo_collection_adapter

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
					entry_counts={	'start_date_time':time_entry,
						'binTable':binTable,
					}
					entry_countsFromEvents={'start_date_time':time_entry,
								'binTableEvents':events_data[0],
					}
					if self.counts_min_adapter==None:
						print entry_counts
					else:
						self.counts_min_adapter.insert(entry_counts)

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
						if self.histograms_adapter==None:
							print entry_histogram
						else:
							self.histogram_adapter.insert(entry_histogram) 

					now_min=now-now%60
				else:
					print 'The thread have woke up earlier, this shouldnt happend and this code is just to check... '

			time.sleep(60.0-time.time()%60)
