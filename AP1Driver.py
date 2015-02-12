import Adafruit_BBIO.GPIO as GPIO
import time

def ap1_init_strobe_reader():
	GPIO.setup("P8_10", GPIO.IN)

def ap1_read_pressure_using_strobe():
	GPIO.wait_for_edge("P8_10", GPIO.RISING)
	time_aux=time.time()
	GPIO.wait_for_edge("P8_10", GPIO.FALLING)
	time_a=time.time()-time_aux
	return '%.0f' % round(time_a/0.0003)

