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
		reader=FPGASerialReader('port', 'counts_condition', shared_counts, shared_countsFromEvents, shared_events)
		self.assertEqual(reader.name, 				'Reader')
		self.assertEqual(reader.port, 				'port')
		self.assertEqual(reader.counts_condition, 		'counts_condition')
		self.assertEqual(reader.shared_counts, 			[0 for x in xrange(18)])
		self.assertEqual(reader.shared_countsFromEvents, 	[0 for x in xrange(18)])
		self.assertEqual(reader.shared_events,	 		[[[0 for x in xrange(128)] for x in xrange(18)],[0 for x in xrange(18)],[0 for x in xrange(18)]])
		self.assertEqual(reader.status, 			'bytex')

	# Assert that the read function is called with the value returned by inWaiting. If that value is 0 the function must be called with 1.
	def test_read_one_byte(self):
		port=MagicMock()
		port.read.return_value=None		
		port.inWaiting.return_value='Potato'
		reader=FPGASerialReader(port, None, [], [], [])
		reader.run()
		port.read.assert_called_with('Potato')

		port=MagicMock()
		port.read.return_value=None		
		port.inWaiting.return_value=0
		reader=FPGASerialReader(port, None, [], [], [])
		reader.run()
		port.read.assert_called_with(1)

	# Assert a log message is generated when something inexpected is read.
	def test_unexpected_reding(self):
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\xFF']],None)	
		
		logging=MagicMock()
		logging.info.return_value=True
		sys.modules['logging']=logging
		import FPGASerialReader
		reload(FPGASerialReader)

		reader=FPGASerialReader.FPGASerialReader(port, None, [], [], [])
		reader.run()
		logging.info.assert_called_with(mock.ANY)

	# Test the Reception if overflow message.
	def test_overflow_read(self):
		port=MagicMock()
		port.inWaiting.side_effect=ReturnSequence([],[1])
		port.read.side_effect=ReturnSequence([['\x3F', '\xFF', '\xFF']],None)	
		reader=FPGASerialReader(port, None, [], [], [])
		reader.run()

		self.assertEqual(reader.shared_events[2],[1 for x in xrange(18)])

	# Test the Reception of pulse width message. Pulse.level=High  Pulse.width < 0.2useg  Channel=3(starting to count from 0)
	def test_high_level_pulse(self):
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x43'],['\x80'],['\xA0']],None)	

		reader=FPGASerialReader(port, None, [], [], [])
		reader.run()
		self.assertEqual(reader.shared_countsFromEvents[3],1)
		self.assertEqual(reader.shared_events[0][3][0],1)

		# Lets run it again
		port.read.side_effect=ReturnSequence([['\x43'],['\x80'],['\xA0']],None)
		reader.run() 
		self.assertEqual(reader.shared_countsFromEvents[3],2)
		self.assertEqual(reader.shared_events[0][3][0],2) 
		
		# And again with different pulse width and channel.
		port.read.side_effect=ReturnSequence([['\x4A'],['\x80'],['\xA8']],None)
		reader.run() 
		self.assertEqual(reader.shared_countsFromEvents[10],1)
		# do not forget we are using 7 bits to build the histogram, although the FPGA returns 12 the 5 LSB bits are discarted
		self.assertEqual(reader.shared_events[0][10][32],1) 

	# Test the Reception of pulse width message. Pulse.level=Low  Channel=5(starting to count from 0)
	def test_low_level_pulse(self):
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x45'],['\x80'],['\x80']],None)	

		reader=FPGASerialReader(port, None, [], [], [])
		reader.run()

		self.assertEqual(reader.shared_events[1][5], 1)

	# Test the Reception of counts message. 
	def tests_counts(self):
		port=MagicMock()
		counts_seq=[['\x60']]
		counts_seq.extend([['\x8A'], ['\x80'], ['\x80']]*18)
		port.read.side_effect=ReturnSequence(counts_seq, None)

		counts_condition=MagicMock()
                counts_condition.release.return_value=True

		reader=FPGASerialReader(port, counts_condition, [], [], [])
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
