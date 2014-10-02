import ap1
import bm35
import analogHVPS
import time

class SensorsManager:
	def __init__(self, name, bar_type=None, hvps_type=None, port_control=None, port_data=None, analog_hvps_corr=None):
		self.name=name
		self.bar_type=bar_type
		self.hvps_type=hvps_type
		self.port_control=port_control
		self.port_data=port_data
		self.analog_hvps_corr=analog_hvps_corr
		
		self.validate_attributes()
		self.init_resources()

			
	def validate_attributes(self):
		# Valid bar_type
		if not(self.bar_type==None or self.bar_type=='ap1' or self.bar_type=='bm35'):
			raise AttributeError('Invalid bar_type')

		# Valid hvps_type
		if not(self.hvps_type==None or self.hvps_type=='digital' or self.hvps_type=='analog'):
			raise AttributeError('Invalid hvps_type')

		# The needed port are present
		if (self.hvps_type=='digital' or self.bar_type=='bm35') and (self.port_control==None or self.port_data==None):
			raise AttributeError('In order to read data from a digital hvps we need two ports, one for control and one for data')

	
	def init_resources(self):
		# Set a timeout for the data port
		if self.port_data!=None:
			# 1.5 secs should be enough time
			self.port_data.timeout=1.5 

	 	# Init the context for ap1
		if self.bar_type=='ap1':
			ap1.ap1_init_strobe_reader()

		# Init the context for analog barometers
		if self.hvps_type=='analog':
			analogHVPS.analogHVPS_init()

		if self.bar_type=='bm35':
			bm35.bm35_request_1min_reading_period(self.port_data)




	def read_pressure(self):
		if self.bar_type==None:
			return -1
		if self.bar_type=='bm35':
			self.port_control.write('\x00')
			time.sleep(0.5)
			self.port_data.flush()
			bm35.bm35_request_pressure_reading(self.port_data)
			pressure_raw=self.port_data.readline()
			pressure=bm35.bm35_parse_pressure_answer(pressure_raw)
			return pressure['meanPressure']
		if self.bar_type=='ap1':
			pressure=ap1.ap1_read_pressure_using_strobe()
			return pressure

	def read_hvps(self):
		if self.hvps_type==None:
			return -1, -1, -1, -1
		if self.hvps_type=='digital':
			self.port_control.write('\x01')
			time.sleep(0.5)
			self.port_data.flush()
			# TODO request the data from the sensor
			hvps1_raw=self.port_data.readline()
			hvps1=hvps1_raw #  TODO parse the raw value
			
			self.port_control.write('\x02')
			time.sleep(0.5)
			self.port_data.flush()
			# TODO request the data from the sensor
			hvps2_raw=self.port_data.readline()
			hvps2=hvps2_raw #  TODO parse the raw value

			self.port_control.write('\x03')
			time.sleep(0.5)
			self.port_data.flush()
			# TODO request the data from the sensor
			hvps3_raw=self.port_data.readline()
			hvps3=hvps3_raw #  TODO parse the raw value

			# We can only read three digital hvps, so we return a -1 for the fourth one.
			return hvps1, hvps2, hvps3, -1
		if self.hvps_type=='analog':
			return analogHVPS.analogHVPS_read(self.analog_hvps_corr)


	def read_temp(self):
		return -1, -1
