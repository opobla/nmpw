import unittest
import mock
from mock import MagicMock
import sys
sys.path.append('.')
from CountsPettioner import CountsPettioner as CP

class CountsPettionerTestCase(unittest.TestCase):
	def test_Equality_aux(self):
		response=CP.aux(['hola','hello'])
		self.assertEqual(response, '["hola", "hello"]', 'Incorrect json dump')

		response=CP.aux({'color':'red','fruits':['apple','pear','strawberry','banana'],'numbers':[1,2,3,4,5]})
		self.assertEqual(response, '{"color": "red", "numbers": [1, 2, 3, 4, 5], "fruits": ["apple", "pear", "strawberry", "banana"]}', 'Incorrect json dump')

	def test_Equality_reset_to_0(self):
		aux=[234,432,[43243,4324,4234,[324,324,[3445]]]]
		CP.reset_to_0(aux)
		self.assertEqual(aux, [0, 0, [0, 0, 0, [0, 0, [0]]]], 'Incorrest reset to 0')

	def test_Eqiality_copy_and_reset(self):
		aux1=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		aux2=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		response=CP.copy_and_reset(aux1,False)
		self.assertEqual(aux2, response, 'Incorrect copy in copy and reset')
		self.assertEqual(aux1,[[0,0],[3452,421],[43243,4324,4234,[324,324,[3445]]]])

		aux1=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		aux2=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		response=CP.copy_and_reset(aux1,True)
		self.assertEqual(aux2, response, 'Incorrect copy in copy and reset')
		self.assertEqual(aux1,[[0,0],[0,0],[0,0,0,[0,0,[0]]]])


	def test_OutPut_save_BinTable(self):
		#Instance of a CountsPettioner where everythong is None.
		database_adapter=None
		CP_instance=CP(None, None, None, None, None, database_adapter)
		with capture(CP_instance.save_BinTable,1405516380.0, [23,12,45,23,12,67]) as output:
			self.assertEqual(output,'start_date_time: 2014-07-16 15:13:00 Counts: [23, 12, 45, 23, 12, 67]\n','Nah man')		


	def test_DatabaseCalls_save_BinTable(self):
		database=MagicMock()
		database.execute=MagicMock(return_value=True)
		database.commit=MagicMock(return_value=True)

		#Instance of a CountsPettioner where everythong is None except the database_adapter.
		CP_instance=CP(None, None, None, None, None, database)
		CP_instance.save_BinTable(1405516380.0,[4 for x in xrange(18)])

		database.execute.assert_called_with(mock.ANY)
		database.commit.assert_called_with()

	def test_OutPut_save_EventsInfo(self):
		#Instance of a CountsPettioner where everythong is None.
		database_adapter=None
		CP_instance=CP(None, None, None, None, None, database_adapter)
		with capture(CP_instance.save_EventsInfo,1405516380.0,[None,'To_print_histo','To_print_Low','To_print_Overflows']) as output:
			self.assertEqual(output, 'start_date_time: 2014-07-16 15:04:00 \nhistograms: To_print_histo \nlowlevels: To_print_Low \noverflows: To_print_Overflows\n')
		

	def test_DatabaseCalls_save_EventsInfo(self):
		database=MagicMock()
		database.execute=MagicMock(return_value=True)
		database.commit=MagicMock(return_value=True)
	
		#Instance of a CountsPettioner where everythong is None except the database_adapter.
		CP_instance=CP(None, None, None, None, None, database)
		CP_instance.save_EventsInfo(1405516380.0,[None,[[4 for x in xrange(128)] for x in xrange(18)],[4 for x in xrange(18)],[0 for x in xrange(18)]])

		database.execute.assert_called_with(mock.ANY)
		database.commit.assert_called_with()

	def test_Equality_get_min(self):
		response=CP.get_min(1405524513.631769)
		self.assertEqual(response,1405524480.0,'Minute calculated uncorrectly')

		response=CP.get_min(123.3)
		self.assertEqual(response,120.0)

	def test_Constructor(self):
		myCP=CP('Hi','There',{'some_numbers':[1,2,3,4,]},4,5,6)
		self.assertEqual(myCP.name,'CountsPettioner','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCP.port,'Hi','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCP.end_condition,'There','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCP.counts_condition,{'some_numbers':[1,2,3,4]},'CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCP.shared_counts_data,4,'CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCP.shared_events_data,5,'CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCP.database_adapter,6,'CountsPettioner Constructor behaving incorrectly')


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
