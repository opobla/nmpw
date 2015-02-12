import Adafruit_BBIO.ADC as ADC

def analogHVPS_init():
	ADC.setup()

def analogHVPS_read(corr):
	# Read returns values between 0.0 and 1.0. In volatage those two values correspond to 0.0V and 1.8V. Multiplying by 1800 the read value we convert it to millivolts

	# I hate this........
	# There is a bug in BBIO.ADC and values must be read twice in order to obtain the correct value. 
	#  TODO keep track if this bug.   https://learn.adafruit.com/setting-up-io-python-library-on-beaglebone-black/adc
	hvps1=((ADC.read("P9_39")*1800.0) /2.7*10.02) *corr
	hvps1=((ADC.read("P9_39")*1800.0) /2.7*10.02) *corr

	hvps2=((ADC.read("P9_40")*1800.0) /2.7*10.02) *corr
	hvps2=((ADC.read("P9_40")*1800.0) /2.7*10.02) *corr

	hvps3=((ADC.read("P9_37")*1800.0) /2.7*10.02) *corr
	hvps3=((ADC.read("P9_37")*1800.0) /2.7*10.02) *corr

	hvps4=((ADC.read("P9_38")*1800.0) /2.7*10.02) *corr
	hvps4=((ADC.read("P9_38")*1800.0) /2.7*10.02) *corr
	#  TODO Maybe convert the millivolts to something more meaningfull to us and return that value
	return round(hvps1), round(hvps2), round(hvps3), round(hvps4)


