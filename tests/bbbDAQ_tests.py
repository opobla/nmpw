import unittest
import mock
from mock import MagicMock
from mock import call
import sys
import bbbDAQ

class bbbDAQTestCase(unittest.TestCase):

	#  TODO tests for the barrometers inicialization

	def test_create_parser(self):
		# Assert Equality
		parser=bbbDAQ.create_parser()
		args=parser.parse_args('-sp /dev/ttyUSB0'.split(' '))
		self.assertEqual(args.serialPort, '/dev/ttyUSB0')
		self.assertEqual(args.database, 'shell')
		self.assertEqual(args.barometer, None)
		self.assertEqual(args.serialPortBar, None)

		parser=bbbDAQ.create_parser()
		args=parser.parse_args('-sp /dev/ttyUSB4 -db test.db'.split(' '))
		self.assertEqual(args.serialPort, '/dev/ttyUSB4')
		self.assertEqual(args.database, 'test.db')
		self.assertEqual(args.barometer, None)
		self.assertEqual(args.serialPortBar, None)

		parser=bbbDAQ.create_parser()
		args=parser.parse_args('-sp /dev/ttyUSB4 -db test.db -bm bm35 -spb 4027'.split(' '))
		self.assertEqual(args.serialPort, '/dev/ttyUSB4')
		self.assertEqual(args.database, 'test.db')
		self.assertEqual(args.barometer, 'bm35')
		self.assertEqual(args.serialPortBar, '4027')


		# Assert execution is aborted when bad arguments are passed
		parser=bbbDAQ.create_parser()
		self.assertRaises(SystemExit, parser.parse_args,''.split(' '))
		
		parser=bbbDAQ.create_parser()
		self.assertRaises(SystemExit, parser.parse_args,'-rs hola'.split(' '))

		# Invalid barometer
		parser=bbbDAQ.create_parser()
		self.assertRaises(SystemExit, parser.parse_args,'-sp 4028 -bm hola'.split(' '))


	def test_init_port(self):
		# Mock the serial module
		serial=MagicMock()
		port=MagicMock()
		port.flush.return_value=True
		serial.Serial.return_value=port

		#Make the bbbDAQ use the mocked serial module
		sys.modules['serial'] = serial
		import bbbDAQ
		reload (bbbDAQ)

		created_port=bbbDAQ.init_port('/dev/ttyUSB3', args_baudrate=921600)
		self.assertEqual(created_port, port)
		serial.Serial.assert_called_with(port='/dev/ttyUSB3', baudrate=921600)

		created_port=bbbDAQ.init_port(None, args_baudrate=921600)
		self.assertEqual(created_port, None)

	def test_init_database(self):
		# Mock the sqlite3 and database_connection object. Make the sqlite3.connect return the mocked connection
		sqlite3=MagicMock()
		conn=MagicMock()
		conn.execute.return_value=True
		sqlite3.connect.return_value=conn

		#Make the bbbDAQ use the mocked sqlite3
		sys.modules['sqlite3'] = sqlite3
		import bbbDAQ
		reload (bbbDAQ)

		# Assert a connection is not created when we want to log the info to the console. 
		created_conn=bbbDAQ.init_database('shell')
		self.assertEqual(created_conn, None)

		# Asserts when we want to save the adquired info to a database
		created_conn=bbbDAQ.init_database('test.db')
		self.assertEqual(created_conn, conn)
		sqlite3.connect.assert_called_with('test.db', check_same_thread=False)
		conn.assert_has_calls([call.execute(mock.ANY)]*3)

	def test_init_resources(self):
		mock_bbbDAQ=MagicMock()
		args=MagicMock(serialPort='2068', serialPortBar=None, database='hi')
		mock_bbbDAQ.init_port.return_value='The serial Port'
		mock_bbbDAQ.init_database.return_value='The database'

		bbbDAQ.init_port=mock_bbbDAQ.init_port
		bbbDAQ.init_database=mock_bbbDAQ.init_database
		
		my_port, my_port_bar, my_conn = bbbDAQ.init_resources(args)
		
		mock_bbbDAQ.assert_has_calls([call.init_port(args.serialPort, args_baudrate=921600), call.init_port(args.serialPortBar, args_baudrate=921600), call.init_database(args.database)], any_order=True)
		
	def test_init_threads(self):
		import threading
		reader, counts, barometer=bbbDAQ.init_threads('Hi', None,'There', 'Bye')
		self.assertIsInstance(reader, threading.Thread)
		self.assertIsInstance(counts, threading.Thread)
		self.assertEqual(barometer,None)

		
		reader, counts, barometer=bbbDAQ.init_threads('Hi', 'bm35','There', 'Bye')
		self.assertIsInstance(reader, threading.Thread)
		self.assertIsInstance(counts, threading.Thread)
		#self.assertIsInstance(barometer, threading.Thread)
		self.assertEqual(barometer,'just to test')

	def test_start_threads(self):
		reader=MagicMock()
		reader.start.return_value=True
		counts=MagicMock()
		counts.start.return_value=True
		barometer=None

		bbbDAQ.start_threads(reader, counts, barometer)
		reader.start.assert_called_with()
		counts.start.assert_called_with()
		# If barometer.start is called exception will be raised. We expect it will not be called because barometer == None

		barometer=MagicMock()
		barometer.start.return_value=True
		bbbDAQ.start_threads(reader, counts, barometer)
		reader.start.assert_called_with()
		counts.start.assert_called_with()
		barometer.start.assert_called_with()		


	def test_end_threads(self):
		reader=MagicMock()
		reader.join.return_value=True
		counts=MagicMock()
		counts._Thread__stop.return_value=True
		barometer=None

		bbbDAQ.end_threads(reader, counts, barometer)
		reader.join.assert_called_with()
		counts._Thread__stop.assert_called_with()
		# If barometer._Thread__stop is called exception will be raised. We expect it will not be called because barometer == None

		barometer=MagicMock()
		barometer._Thread__stop.return_value=True
		bbbDAQ.end_threads(reader, counts, barometer)
		reader.join.assert_called_with()
		counts._Thread__stop.assert_called_with()
		barometer._Thread__stop.assert_called_with()		


	def test_release_resources(self):
		port=MagicMock()
		port.close.return_value=True
		port_bar=None
		conn=None
		
		bbbDAQ.release_resources(port, port_bar, conn)
		port.close.assert_called_with()
		# If port_bar.close is called exception will be raised. We expect it will not be called because port_bar == None
		# Same for conn

		port=MagicMock()
		port.close.return_value=True
		port_bar=MagicMock()
		port_bar.close.return_valuer=True
		conn=MagicMock()
		conn.close.return_value=True
		
		bbbDAQ.release_resources(port, port_bar, conn)
		port.close.assert_called_with()
		port_bar.close.assert_called_with()
		conn.close.assert_called_with()
	




