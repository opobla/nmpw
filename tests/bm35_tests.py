import unittest
from mock import MagicMock
import sys
sys.path.append('.')
import BM35Driver

class bm35TestCase(unittest.TestCase):
	def setUp(self):
		reload(BM35Driver)

	def test_Equality_compute_crc(self):
		response=BM35Driver.bm35_compute_crc('AAA')
		self.assertEqual(response,'AAA195')
		
		response=BM35Driver.bm35_compute_crc('HiThere')
		self.assertEqual(response,'HiThere681')

		response=BM35Driver.bm35_compute_crc('aaa')
		self.assertNotEqual(response,'aaa195')

	def test_Equality_parse_pressure_answer(self):
		response=BM35Driver.bm35_parse_pressure_answer('M99D08.02.1999,11:40,96502,96555,0785\r\n')
		self.assertEqual(response,{'date':'1999-02-08 11:40:00','meanPressure':96502,'instantPressure':96555})

		response=BM35Driver.bm35_parse_pressure_answer('M99D17.07.2014,12:47,85661,11555,0768\r\n')
		self.assertEqual(response,{'date':'2014-07-17 12:47:00','meanPressure':85661,'instantPressure':11555})

	def test_Errors_parse_pressure_answer(self):
		#Mock the logging
		logging=MagicMock()
		logging.info.return_value=True
		sys.modules['logging'] = logging
		import BM35Driver
		reload(BM35Driver)

		response=BM35Driver.bm35_parse_pressure_answer('M99D08.02.1999,11:40,96502,96555,0785')
		self.assertEqual(response,{'date':-1,'meanPressure':-1,'instantPressure':-1})
		logging.info.assert_called_with('Bm35: Invalid answer to parse. Bad format')

		response=BM35Driver.bm35_parse_pressure_answer('M99D17.07.2014,12:47,85661,11555,0111\r\n')
		self.assertEqual(response,{'date':-1,'meanPressure':-1,'instantPressure':-1})
		logging.info.assert_called_with('Bm35: Invalid answer to parse. Wrong CRC')

	def test_Writting_request_pressure_reading(self):
		import serial
		mock_port=serial.Serial()
		mock_port.write=MagicMock(return_value='Hi')
		BM35Driver.bm35_request_pressure_reading(mock_port)

		mock_port.write.assert_called_with(BM35Driver.bm35_compute_crc('A00Q1')+'\r\n')

	def test_Writting_request_1min_reading_period(self):
		import serial
		mock_port=serial.Serial()
		mock_port.write=MagicMock(return_value='Hi')
		BM35Driver.bm35_request_1min_reading_period(mock_port)

		mock_port.write.assert_called_with(BM35Driver.bm35_compute_crc('A00I10')+'\r\n')
