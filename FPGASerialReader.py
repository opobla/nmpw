import time
import sys
import threading
from time import strftime
import datetime
import operator
import logging
from bitarray import bitarray

class FPGASerialReader(threading.Thread):
	def __init__(self, port, queue):
		threading.Thread.__init__(self)
		self.name='Reader'
		self.port=port
		self.queue=queue

	def run(self):
		while True:
			aux= self.port.inWaiting()
			if aux==0:
				aux=1
			if aux >= 2000:
				logging.info(self.name+': inWaiting()= '+`aux`)

			next=self.port.read(aux)
			if not next:
				break
			for data in next:
				#sys.stdout.write(data)
				self.queue.put(ord(data))
