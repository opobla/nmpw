import time
import threading
from time import strftime
from threading import Thread
import datetime

class CountsPettioner(threading.Thread):
	def __init__(self, port, end_condition, counts_condition, shared_counts_data, counts_min_adapter):
		threading.Thread.__init__(self)
		self.name='Contadores'
		self.port=port
		self.end_condition=end_condition
		self.counts_condition=counts_condition
		self.shared_counts_data=shared_counts_data
		self.counts_min_adapter=counts_min_adapter

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
					self.port.write(chr(17)) #0x11
						#wait release the lock and wait for a notification.
					self.counts_condition.wait()
					binTable=self.shared_counts_data[:]	
					self.counts_condition.release()

					#  TODO Pressure and HV sensors information.....

					time_entry=datetime.datetime.fromtimestamp(now_min).strftime('%Y-%m-%d %H:%M:%S')
					entry={	'start_date_time':time_entry,
						'binTable':binTable,
					}
					if self.counts_min_adapter==None:
						print entry
					else:
						self.counts_min_adapter.insert(entry)

					now_min=now-now%60
				else:
					print 'The thread have woke up earlier, this shouldnt happend and this code is just to check... '

			time.sleep(60.0-time.time()%60)
