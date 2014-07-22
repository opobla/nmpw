import unittest
import mock
from mock import MagicMock
from mock import call

from Reader import Reader

class ReaderTestCase(unittest.TestCase):

	def test_Constructor(self):
		shared_counts=[]
		shared_events=[]
		reader=Reader('port', 'end', 'counts_condition', shared_counts, shared_events)
		self.assertEqual(reader.name, 'Reader')
		self.assertEqual(reader.port, 'port')
		self.assertEqual(reader.end_condition, 'end')
		self.assertEqual(reader.counts_condition, 'counts_condition')
		self.assertEqual(reader.shared_counts_data, [0 for x in xrange(18)])
		self.assertEqual(reader.shared_events_data, [[0 for x in xrange(18)],[[0 for x in xrange(128)] for x in xrange(18)],[0 for x in xrange(18)],[0 for x in xrange(18)]])
		self.assertEqual(reader.status, 'bytex')

	# With this test we assert that the run method ends when the end_condition is unset
	def test_end_condition(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([],False)
		
		reader=Reader(None, end_condition, None, [], [])
		reader.run()
		
	# With this test we assert that we read byte by byte and that the execution stops when a None value is read from the port
	def test_read_one_byte(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([], True)
		
		port=MagicMock()
		port.read.return_value=None		

		reader=Reader(port , end_condition, None, [], [])
		reader.run()

		port.read.assert_called_with(1)
	
	# OverFlow on all the channels
	def test_overflow_read(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x3F'],['\xFF'],['\xFF']],['\x00'])	

		reader=Reader(port , end_condition, None, [], [])
		reader.run()

		self.assertEqual(reader.shared_events_data[3],[1 for x in xrange(18)])

	# Initial states bytex. Reading a 11xxxxxx byte is something unexpected 
	def test_unexpected_reding(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\xFF']],['\x00'])	

		reader=Reader(port , end_condition, None, [], [])

		with capture(reader.run) as output:
			self.assertEqual(output, 'Unexpected reading\n')


	# High level pulse. Pulse.width < 0.2useg. Channel=3
	def test_high_level_pulse(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x43'],['\x80'],['\xA0']],['\x00'])	

		reader=Reader(port , end_condition, None, [], [])
		reader.run()

		self.assertEqual(reader.shared_events_data[0][3],1)
		self.assertEqual(reader.shared_events_data[1][3][0],1)

		# Lets run it again
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False) 
		port.read.side_effect=ReturnSequence([['\x43'],['\x80'],['\xA0']],['\x00'])
		reader.run() 
		
		self.assertEqual(reader.shared_events_data[0][3],2)
		self.assertEqual(reader.shared_events_data[1][3][0],2) 
		
		# And again with different pulse width, channel.
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False) 
		port.read.side_effect=ReturnSequence([['\x4A'],['\x80'],['\xA8']],['\x00'])
		reader.run() 
		
		self.assertEqual(reader.shared_events_data[0][10],1)
		# do not forget we are using 7 bits build the histogram, although the FPGA returns 12
		self.assertEqual(reader.shared_events_data[1][10][32],1) 


	def test_low_level_pulse(self):
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True, True, True], False)
		
		port=MagicMock()
		port.read.side_effect=ReturnSequence([['\x45'],['\x80'],['\x80']],['\x00'])	

		reader=Reader(port , end_condition, None, [], [])
		reader.run()

		self.assertEqual(reader.shared_events_data[2][5], 1)

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

		reader=Reader(port , end_condition, counts_condition, [], [])
		reader.run()
	
		self.assertEqual(reader.shared_counts_data, [10 for x in xrange(18)])
		counts_condition.assert_has_calls([call.release()],any_order=False)
		


import sys
from cStringIO import StringIO
from contextlib import contextmanager

@contextmanager
def capture(command, *args, **kwargs):
  out, sys.stdout = sys.stdout, StringIO()
  command(*args, **kwargs)
  sys.stdout.seek(0)
  yield sys.stdout.read()
  sys.stdout = out




class ReturnSequence(object):
    def __init__(self, return_sequence, expired):
        self.return_sequence = return_sequence
	self.expired = expired

    def __call__(self, *args):
        if 0  < len(self.return_sequence):
            	return self.return_sequence.pop(0)
	else:
		return self.expired
