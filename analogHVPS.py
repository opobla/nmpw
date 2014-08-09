import Adafruit_BBIO.ADC as ADC

def analogHVPS_init():
	ADC.setup()

def analogHVPS_read():
	#Read returns values between 0.0 and 1.0. In volatage those two values correspond to 0.0V and 1.8V. Multiplying by 1800 the read value we convert it to millivolts
	hvps1=ADC.read("P9_39")*1800
	hvps2=ADC.read("P9_40")*1800
	hvps3=ADC.read("P9_37")*1800
	hvps4=ADC.read("P9_36")*1800
	#  TODO Maybe convert the millivolts to something more meaningfull to us and return that value
	return hvps1, hvps2, hvp3, hvp4


