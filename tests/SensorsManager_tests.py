import unittest
import mock
from mock import MagicMock
from mock import call
import sys
sys.path.append('.')

ap1=MagicMock()
sys.modules['AP1Driver'] = ap1
analogHVPS=MagicMock()
sys.modules['HVPSDriver']=analogHVPS

import SensorsManager

class SensorsManagerTestCase(unittest.TestCase):
	def setUp(self):
		reload(SensorsManager)
		
	def test_Constructor(self):
		#Tests the correct order of constructors parameters.
		aux=MagicMock()
		aux.validate_attributes.return_value=True
		aux.init_resources.return_value=True

		SensorsManager.SensorsManager.validate_attributes=aux.validate_attributes
		SensorsManager.SensorsManager.init_resources=aux.init_resources

		SM_instance=SensorsManager.SensorsManager('one', 'two', 'three', 'four', 'five')
		
		self.assertEqual(SM_instance.name, 'one')
		self.assertEqual(SM_instance.bar_type, 'two')
		self.assertEqual(SM_instance.hvps_type, 'three')
		self.assertEqual(SM_instance.port_control, 'four')
		self.assertEqual(SM_instance.port_data, 'five')

	def test_init_resources(self):
		# Validate we setup a timeout for the data port when data port is present
		SM_instance=MagicMock(spec=SensorsManager.SensorsManager)	
		SM_instance.bar_type='hi'
		SM_instance.hvps_type='there'
		SM_instance.port_control=None
		SM_instance.port_data=MagicMock()
		SM_instance.port_data.timeout=0.0
		SensorsManager.SensorsManager.init_resources(SM_instance)
		self.assertNotEqual(SM_instance.port_data.timeout, 0.0)

		# Validate we call ap1.init
		ap1.ap1_init_strobe_reader.return_value=True
		SM_instance.bar_type='ap1'
		SM_instance.hvps_type='there'
		SM_instance.port_control=None
		SM_instance.port_data=None
		SensorsManager.SensorsManager.init_resources(SM_instance)
		ap1.ap1_init_strobe_reader.assert_called_with()

		# Validate we call analogHVPS.init
		analogHVPS.analogHVPS_init.return_value=True
		SM_instance.bar_type='hi'
		SM_instance.hvps_type='analog'
		SM_instance.port_control=None
		SM_instance.port_data=None
		SensorsManager.SensorsManager.init_resources(SM_instance)
		analogHVPS.analogHVPS_init.assert_called_with()

	def test_read_pressure(self):
		# Returned value when no barometer is specified
		SM_instance=SensorsManager.SensorsManager('The_name', None, None, None, None)	
		read_pressure=SM_instance.read_pressure()
		self.assertEqual(read_pressure, -1)

		# Returned value when bm35 barometer is specified
		time=MagicMock()
		time.sleep.return_value=True
		sys.modules['time'] = time
		reload(SensorsManager)

		port_control=MagicMock()
		port_control.write.return_value=True
		port_data=MagicMock()
		port_data.flush.return_value=True
		port_data.readline.return_value='M99D17.07.2014,12:47,85661,11555,0768\r\n'

		SM_instance=SensorsManager.SensorsManager('The_name', 'bm35', None, port_control, port_data)
		read_pressure=SM_instance.read_pressure()
		self.assertEqual(read_pressure, 85661)

		# Returned value when ap1 barometer is specified
		ap1=MagicMock()
		ap1.ap1_read_pressure_using_strobe.return_value=88888	
		sys.modules['AP1Driver']=ap1
		reload(SensorsManager)

		SM_instance=SensorsManager.SensorsManager('The_name', 'ap1', None, None, None)
		read_pressure=SM_instance.read_pressure()
		self.assertEqual(read_pressure, 88888)
		
	def test_read_hvps(self):
		# Resturned value when no hvps is specified
		SM_instance=SensorsManager.SensorsManager('The_name', None, None, None, None)
		read_hvps1, read_hvps2, read_hvps3, read_hvps4=SM_instance.read_hvps()
		self.assertEqual(read_hvps1, -1)
		self.assertEqual(read_hvps2, -1)
		self.assertEqual(read_hvps3, -1)
		self.assertEqual(read_hvps4, -1)
