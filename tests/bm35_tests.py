import unittest
from mock import MagicMock
import sys
sys.path.append('.')
import bm35

class bm35TestCase(unittest.TestCase):
	def test_Equality_compute_crc(self):
		response=bm35.bm35_compute_crc('AAA')
		self.assertEqual(response,'AAA195')
		
		response=bm35.bm35_compute_crc('HiThere')
		self.assertEqual(response,'HiThere681')

		response=bm35.bm35_compute_crc('aaa')
		self.assertNotEqual(response,'aaa195')

	def test_Equality_parse_pressure_answer(self):
		response=bm35.bm35_parse_pressure_answer('M99D08.02.1999,11:40,96502,96555,0785')
		self.assertEqual(response,{'date':'1999-02-08 11:40:00','meanPressure':96502,'instantPressure':96555})

		response=bm35.bm35_parse_pressure_answer('M99D17.07.2014,12:47,85661,11555,0768')
		self.assertEqual(response,{'date':'2014-07-17 12:47:00','meanPressure':85661,'instantPressure':11555})

	def test_Errors_parse_pressure_answer(self):
		self.assertRaisesRegexp(ValueError,'Invalid answer to parse', bm35.bm35_parse_pressure_answer, 'A incorrect string, just to test')
		
		self.assertRaisesRegexp(ValueError,'Answers crc is invalid', bm35.bm35_parse_pressure_answer, 'M99D17.07.2014,12:47,85661,11555,0444')


	def test_Writting_request_pressure_reading(self):
		import serial
		mock_port=serial.Serial()
		mock_port.write=MagicMock(return_value='Hi')
		bm35.bm35_request_pressure_reading(mock_port)

		mock_port.write.assert_called_with(bm35.bm35_compute_crc('A00Q1')+'\r\n')

	def test_Writting_request_1min_reading_period(self):
		import serial
		mock_port=serial.Serial()
		mock_port.write=MagicMock(return_value='Hi')
		bm35.bm35_request_1min_reading_period(mock_port)

		mock_port.write.assert_called_with(bm35.bm35_compute_crc('A00I10')+'\r\n')


