import unittest
import mock
from mock import MagicMock
from mock import call
import sys

from FPGASerialReader import FPGASerialReader

class ReaderTestCase(unittest.TestCase):

	def test_Constructor(self):
		shared_counts=[]
		shared_countsFromEvents=[]
		shared_events=[]
		reader=FPGASerialReader('port', 'end', 'counts_condition', shared_counts, shared_countsFromEvents, shared_events)
		self.assertEqual(reader.name, 				'Reader')
		self.assertEqual(reader.port, 				'port')
		self.assertEqual(reader.end_condition, 			'end')
		self.assertEqual(reader.counts_condition, 		'counts_condition')
		self.assertEqual(reader.shared_counts, 			[0 for x in xrange(18)])
		self.assertEqual(reader.shared_countsFromEvents, 	[0 for x in xrange(18)])
		self.assertEqual(reader.shared_events,	 		[[[0 for x in xrange(128)] for x in xrange(18)],[0 for x in xrange(18)],[0 for x in xrange(18)]])
		self.assertEqual(reader.status, 			'bytex')

	# With this test we assert that the run method ends when the end_condition is unset
	def test_end_condition(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([],False)
		
		reader=FPGASerialReader(None, end_condition, None, [], [], [])
		reader.run()
		
	# With this test we assert that we the number of bytes that are available and when there is no available bytes we read one byte, which blocks us until a byte is received.
	def test_read_one_byte(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([], True)
		
		port=MagicMock()
		port.read.return_value=None		
		port.inWaiting.return_value='Potato'

		reader=FPGASerialReader(port , end_condition, None, [], [], [])
		reader.run()

		port.read.assert_called_with('Potato')

		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([], True)
		
		port=MagicMock()
		port.read.return_value=None		
		port.inWaiting.return_value=0

		reader=FPGASerialReader(port , end_condition, None, [], [], [])
		reader.run()

		port.read.assert_called_with(1)

	# OverFlow on all the channels
	def test_overflow_read(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x3F'],['\xFF'],['\xFF']],['\x00'])	

		reader=FPGASerialReader(port , end_condition, None, [], [], [])
		reader.run()

		self.assertEqual(reader.shared_events[2],[1 for x in xrange(18)])

	# Initial states bytex. Reading a 11xxxxxx byte is something unexpected 
	def test_unexpected_reding(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\xFF']],['\x00'])	
		
		logging=MagicMock()
		logging.info.return_value=True
		sys.modules['logging']=logging
		import FPGASerialReader
		reload(FPGASerialReader)

		reader=FPGASerialReader.FPGASerialReader(port , end_condition, None, [], [], [])
		reader.run()
		logging.info.assert_called_with(mock.ANY)


	# High level pulse. Pulse.width < 0.2useg. Channel=3
	def test_high_level_pulse(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x43'],['\x80'],['\xA0']],['\x00'])	

		reader=FPGASerialReader(port , end_condition, None, [], [], [])
		reader.run()

		self.assertEqual(reader.shared_countsFromEvents[3],1)
		self.assertEqual(reader.shared_events[0][3][0],1)

		# Lets run it again
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False) 
		port.read.side_effect=ReturnSequence([['\x43'],['\x80'],['\xA0']],['\x00'])
		reader.run() 
		
		self.assertEqual(reader.shared_countsFromEvents[3],2)
		self.assertEqual(reader.shared_events[0][3][0],2) 
		
		# And again with different pulse width, channel.
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False) 
		port.read.side_effect=ReturnSequence([['\x4A'],['\x80'],['\xA8']],['\x00'])
		reader.run() 
		
		self.assertEqual(reader.shared_countsFromEvents[10],1)
		# do not forget we are using 7 bits build the histogram, although the FPGA returns 12
		self.assertEqual(reader.shared_events[0][10][32],1) 


	def test_low_level_pulse(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x45'],['\x80'],['\x80']],['\x00'])	

		reader=FPGASerialReader(port , end_condition, None, [], [], [])
		reader.run()

		self.assertEqual(reader.shared_events[1][5], 1)

	# For this test we will mock the port to return a sequence of 55 bytes which will represent sertant amount of channel counts. Once executed the Reader we will assert on the shared_counts_data.
	def tests_counts(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True]*55, False)
		
		port=MagicMock()
		counts_seq=[['\x60']]
		counts_seq.extend([['\x8A'], ['\x80'], ['\x80']]*18)
		port.read.side_effect=ReturnSequence(counts_seq, ['\x00'])

		counts_condition=MagicMock()
                counts_condition.acquire.return_value=True
                counts_condition.notify.return_value=True
                counts_condition.release.return_value=True

		reader=FPGASerialReader(port , end_condition, counts_condition, [], [], [])
		reader.run()
	
		self.assertEqual(reader.shared_counts, [10 for x in xrange(18)])
		counts_condition.assert_has_calls([call.release()],any_order=False)
		


class ReturnSequence(object):
    def __init__(self, return_sequence, expired):
        self.return_sequence = return_sequence
	self.expired = expired

    def __call__(self, *args):
        if 0  < len(self.return_sequence):
            	return self.return_sequence.pop(0)
	else:
		return self.expired
