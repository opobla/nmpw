import time
import threading
from time import strftime
from threading import Thread

class CountsPettioner(threading.Thread):
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
					#  TODO wait for the Reader to read the data
					#  TODO write the data into the database
					print 'CountsPettioner wake up time: ',now
					now_min=now-now%60
				else:
					print 'The thread have woke up earlier, this shouldnt happend and this code is just to check... '

			time.sleep(60.0-time.time()%60)
