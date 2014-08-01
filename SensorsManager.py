from ap1 import ap1
from bm35 import bm35

class SensorsManager:
	def __init__(self, name, bar_type=None, hvps_type=None, port_control=None, port_data=None):
		self.name=name
		self.bar_type=bar_type
		self.hvps_type=hvps_type
		self.port_control=port_control
		self.port_data=port_data
		if self.port_data!=None:
			# 1.5 secs should be enough time
			self.port_data.timeout=1.5 

		# Valid bar_type
		if not(bar_type==None or bar_type=='ap1' or bar_type=='bm35'):
			raise AttributeError('Invalid bar_type')

		# The needed port are present
		if self.name=='bm35' and (self.port_control==None or self.port_data==None):
			raise AttributeError('In order to read data from a bm35 barometer we need two ports, one for control and one for data')
 
 		# Init the context for ap1
		if self.name=='ap1':
			ap1.ap1_init_strobe_reader()

		#  TODO add the hvps_type validation and all that is needed


	def read_pressure(self):
		if self.bar_type==None:
			return -1
		if self.bar_type=='bm35':
			self.port_control.write('\x00')
			time.sleep(0.5)
			self.port_data.flush()
			bm35.bm35_request_pressure_reading(self.port_data)
			pressure_raw=self.port_data.readline()
			pressure=bm35.bm35_parse_pressure_answer(pressure_raw[:-2])
			return pressure
		if self.bar_type=='ap1':
			pressure=ap1.ap1_read_pressure_using_strobe()
			return pressure

	def read_hvps(self):
		if self.hvps_type==None:
			return -1, -1, -1
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

			return hvps1, hvps2, hvps3
		if self.hvps_type=='analog':
			#  TODO Do it
			return -1


	def read_temp(self):
		return -1, -1
