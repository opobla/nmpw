import unittest
import mock
from mock import MagicMock
from mock import call
import sys
sys.path.append('.')
import validate_arguments

class args(object):
	pass

class validate_argumentsTestCase(unittest.TestCase):
	def setUp(self):
		#mock the logging
		logging=MagicMock()
		logging.info.return_value=True

		# make the countspettioner use the mocked logging
		sys.modules['logging'] = logging
		import validate_arguments
		reload(validate_arguments)


	def test_minimal_valid_arguments(self):
		args.serial_port_control='/dev/ttyO2'
		args.database='/server/data/test.db'
		args.serial_port_sensors=None
		args.barometer_type=None
		args.hvps_type=None
		args.analog_hvps_corr=None
		args.db_updater_enabled=None
		args.local_db=None
		args.remote_db_host=None
		args.remote_db_user=None
		args.remote_db_pass=None
		args.remote_db_db=None

		try:
			validate_arguments.validate_arguments(args)
		except:
			self.fail('validate_arguments() raised unexpected error')

	def test_all_missing_arguments(self):
		args.serial_port_control=None
		args.database=None
		args.serial_port_sensors=None
		args.barometer_type=None
		args.hvps_type=None
		args.analog_hvps_corr=None
		args.db_updater_enabled=None
		args.local_db=None
		args.remote_db_host=None
		args.remote_db_user=None
		args.remote_db_pass=None
		args.remote_db_db=None
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

	def test_missing_database_argument(self):
		args.serial_port_control='/dev/ttyO2'
		args.database=None
		args.serial_port_sensors='/dev/ttyO1'
		args.barometer_type='bm35'
		args.hvps_type='analog'
		args.analog_hvps_corr=1.0
		args.db_updater_enabled=None
		args.local_db=None
		args.remote_db_host=None
		args.remote_db_user=None
		args.remote_db_pass=None
		args.remote_db_db=None
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

	def test_invalid_conf_bm35_arguments(self):
		args.serial_port_control='/dev/ttyO2'
		args.database='/server/data/test.db'
		args.serial_port_sensors=None
		args.barometer_type='bm35'
		args.hvps_type='analog'
		args.analog_hvps_corr=1.0
		args.db_updater_enabled=None
		args.local_db=None
		args.remote_db_host=None
		args.remote_db_user=None
		args.remote_db_pass=None
		args.remote_db_db=None
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

	def test_invalid_barometer_type_arguments(self):
		args.serial_port_control='/dev/ttyO2'
		args.database='/server/data/test.db'
		args.serial_port_sensors=None
		args.barometer_type='Hi There'
		args.hvps_type='analog'
		args.analog_hvps_corr=1.0
		args.db_updater_enabled=None
		args.local_db=None
		args.remote_db_host=None
		args.remote_db_user=None
		args.remote_db_pass=None
		args.remote_db_db=None
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

	def test_invalid_hvps_type_arguments(self):
		args.serial_port_control='/dev/ttyO2'
		args.database='/server/data/test.db'
		args.serial_port_sensors='/dev/ttyO1'
		args.barometer_type='bm35'
		args.hvps_type='Hi There'
		args.analog_hvps_corr=1.0
		args.db_updater_enabled=None
		args.local_db=None
		args.remote_db_host=None
		args.remote_db_user=None
		args.remote_db_pass=None
		args.remote_db_db=None
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

	def test_invalid_conf_dbUpdater_arguments(self):
		args.serial_port_control='/dev/ttyO2'
		args.database='/server/data/test.db'
		args.serial_port_sensors=None
		args.barometer_type=None
		args.hvps_type=None
		args.analog_hvps_corr=None

		args.db_updater_enabled=True
		args.local_db=None
		args.remote_db_host='localhost'
		args.remote_db_user='hristo'
		args.remote_db_pass='pass'
		args.remote_db_db='nmdadb'
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)


		args.db_updater_enabled=True
		args.local_db='/server/data/test.db'
		args.remote_db_host=None
		args.remote_db_user='hristo'
		args.remote_db_pass='pass'
		args.remote_db_db='nmdadb'
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

		args.db_updater_enabled=True
		args.local_db='/server/data/test.db'
		args.remote_db_host='localhost'
		args.remote_db_user=None
		args.remote_db_pass='pass'
		args.remote_db_db='nmdadb'
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

		args.db_updater_enabled=True
		args.local_db='/server/data/test.db'
		args.remote_db_host='localhost'
		args.remote_db_user='hristo'
		args.remote_db_pass=None
		args.remote_db_db='nmdadb'
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

		args.db_updater_enabled=True
		args.local_db='/server/data/test.db'
		args.remote_db_host='localhost'
		args.remote_db_user='hristo'
		args.remote_db_pass='pass'
		args.remote_db_db=None
		self.assertRaises(AttributeError, validate_arguments.validate_arguments, args)

	def test_dbUpdater_valid_arguments(self):
		args.serial_port_control='/dev/ttyO2'
		args.database='/server/data/test.db'
		args.serial_port_sensors=None
		args.barometer_type=None
		args.hvps_type=None
		args.analog_hvps_corr=None
		args.db_updater_enabled=True
		args.local_db='/server/data/test.db'
		args.remote_db_host='localhost'
		args.remote_db_user='hristo'
		args.remote_db_pass='pass'
		args.remote_db_db='nmdadb'

		try:
			validate_arguments.validate_arguments(args)
		except:
			self.fail('validate_arguments() raised unexpected error')

