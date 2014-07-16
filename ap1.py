import Adafruit_BBIO.GPIO as GPIO
import time


class ap1:
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
			print 'Tiempo:',time_a
			print 'Medida:','%.0f' % round(time_a/0.0003)
