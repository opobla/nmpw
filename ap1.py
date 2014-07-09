import threading
from threading import Thread
import Adafruit_BBIO.GPIO as GPIO
import time


class ap1(threading.Thread):
	def __init__(self,end_condition,shared_pressure_data):
		threading.Thread.__init__(self)
		self.name='Ap1_Barometer'
		self.end_condition=end_condition
		self.shared_pressure_data=shared_pressure_data

	@staticmethod
	def ap1_init_strobe_reader():
		GPIO.setup("P8_9", GPIO.IN)

	@staticmethod
	def ap1_read_pressure_using_strobe():
		while True:
			GPIO.wait_for_edge("P8_9", GPIO.RISING)
			time_aux=time.time()
			GPIO.wait_for_edge("P8_9", GPIO.FALLING)
			time_a=time.time()-time_aux
			return '%.0f' % round(time_a/0.0003)


	def run(self):
		self.ap1_init_strobe_reader()
		while self.end_condition.is_set():
			self.shared_pressure_data=self.ap1_read_pressure_using_strobe()
			print self.shared_pressure_data
			#wake up at hh.mm.30
			time.sleep((60.0-time.time()%60.0)+30.0)
