import time
import threading
from time import strftime


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
					print 'Contadores wake up time: ',now
					now_min=now-now%60

			#Instead of having the thread sleeping for 60 secs we have it taking short cat naps every sec. This way the thread is more responsive when trying to close it...
			time.sleep(min(1.0,60-time.time()%60))
			#  TODO Sleep 60 secs and kill this thread when exiting

