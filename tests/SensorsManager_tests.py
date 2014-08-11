import unittest
import mock
from mock import MagicMock
from mock import call
import sys
sys.path.append('.')

ap1=MagicMock()
sys.modules['ap1'] = ap1
analogHVPS=MagicMock()
sys.modules['analogHVPS']=analogHVPS

import SensorsManager

class SensorsManagerTestCase(unittest.TestCase):
	def setUp(self):
		reload(SensorsManager)
		
	def test_Constructor(self):
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
		
		aux.assert_has_calls([call.validate_attributes(), call.init_resources()], any_order=False)
	
	def test_validate_attributes(self):
		aux=MagicMock()
		aux.init_resources.return_value=True
		SensorsManager.SensorsManager.init_resources=aux.init_resources

		# A valis set of attributes, we expect no error will be raised
		SM_instance=SensorsManager.SensorsManager('The_mane', 'bm35', 'digital', 'Something not null', 'Something not null')

		# Another set of valud attributes
		SM_instance=SensorsManager.SensorsManager('The_name', 'ap1', 'analog', None, None)

		# Another set of valud attributes
		SM_instance=SensorsManager.SensorsManager('The_name', 'ap1', 'digital', 'Something not null', 'Something not null')

		# Invalid sets of data. Error should be raised
		SM_instance=MagicMock(spec=SensorsManager.SensorsManager)	
		SM_instance.bar_type='hi'
		SM_instance.hvps_type='there'
		SM_instance.port_control=None
		SM_instance.port_data=None
		self.assertRaises(AttributeError, SensorsManager.SensorsManager.validate_attributes, SM_instance)

		SM_instance.bar_type='bm35'
		SM_instance.hvps_type='there'
		SM_instance.port_control=None
		SM_instance.port_data=None
		self.assertRaises(AttributeError, SensorsManager.SensorsManager.validate_attributes, SM_instance)

		SM_instance.bar_type='bm35'
		SM_instance.hvps_type='analog'
		SM_instance.port_control=None
		SM_instance.port_data=None
		self.assertRaises(AttributeError, SensorsManager.SensorsManager.validate_attributes, SM_instance)

		SM_instance.bar_type='ap1'
		SM_instance.hvps_type='digital'
		SM_instance.port_control=None
		SM_instance.port_data=None
		self.assertRaises(AttributeError, SensorsManager.SensorsManager.validate_attributes, SM_instance)


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
