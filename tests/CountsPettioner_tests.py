import unittest
import mock
from mock import MagicMock
from mock import call
import sys
sys.path.append('.')
from CountsPettioner import CountsPettioner as CP

class CountsPettionerTestCase(unittest.TestCase):
	def test_Equality_aux(self):
		response=CP.aux(['hola','hello'])
		self.assertEqual(response, '["hola", "hello"]')

		response=CP.aux({'color':'red','fruits':['apple','pear','strawberry','banana'],'numbers':[1,2,3,4,5]})
		self.assertEqual(response, '{"color": "red", "numbers": [1, 2, 3, 4, 5], "fruits": ["apple", "pear", "strawberry", "banana"]}')

	def test_Equality_reset_to_0(self):
		aux=[234,432,[43243,4324,4234,[324,324,[3445]]]]
		CP.reset_to_0(aux)
		self.assertEqual(aux, [0, 0, [0, 0, 0, [0, 0, [0]]]])

	def test_Eqiality_copy_and_reset(self):
		aux1=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		aux2=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		response=CP.copy_and_reset(aux1,False)
		self.assertEqual(aux2, response)
		self.assertEqual(aux1,[[0,0],[3452,421],[43243,4324,4234,[324,324,[3445]]]])

		aux1=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		aux2=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		response=CP.copy_and_reset(aux1,True)
		self.assertEqual(aux2, response)
		self.assertEqual(aux1,[[0,0],[0,0],[0,0,0,[0,0,[0]]]])


	def test_OutPut_save_BinTable(self):
		#Instance of a CountsPettioner where everythong is None.
		database_adapter=None
		CP_instance=CP(None, None, None, None, None, database_adapter)
		with capture(CP_instance.save_BinTable,1405516380.0, [23,12,45,23,12,67], [1,2]) as output:
			self.assertEqual(output,'start_date_time: 2014-07-16 15:13:00 Counts: [23, 12, 45, 23, 12, 67] Sensors: [1, 2]\n')		


	def test_DatabaseCalls_save_BinTable(self):
		database=MagicMock()
		database.execute.return_value=True
		database.commit.return_value=True

		#Instance of a CountsPettioner where everythong is None except the database_adapter.
		CP_instance=CP(None, None, None, None, None, database)
		CP_instance.save_BinTable(1405516380.0,[4 for x in xrange(18)], {'hv1':-1,'hv2':-1,'hv3':-1,'temp_1':-1,'temp_2':-1,'atmPressure':-1}
)

		database.assert_has_calls([call.execute(mock.ANY), call.commit()], any_order=False)

	def test_OutPut_save_BinTableFromEvents(self):
		#Instance of a CountsPettioner where everythong is None.
		database_adapter=None
		CP_instance=CP(None, None, None, None, None, database_adapter)
		with capture(CP_instance.save_BinTableFromEvents,1405516380.0, [23,12,45,23,12,67], [1,2]) as output:
			self.assertEqual(output,'start_date_time: 2014-07-16 15:13:00 CountsFromEvents: [23, 12, 45, 23, 12, 67] Sensors: [1, 2]\n')		


	def test_DatabaseCalls_save_BinTableFromEvents(self):
		database=MagicMock()
		database.execute.return_value=True
		database.commit.return_value=True

		#Instance of a CountsPettioner where everythong is None except the database_adapter.
		CP_instance=CP(None, None, None, None, None, database)
		CP_instance.save_BinTableFromEvents(1405516380.0,[4 for x in xrange(18)], {'hv1':-1,'hv2':-1,'hv3':-1,'temp_1':-1,'temp_2':-1,'atmPressure':-1}
)

		database.assert_has_calls([call.execute(mock.ANY), call.commit()], any_order=False)



	def test_OutPut_save_EventsInfo(self):
		#Instance of a CountsPettioner where everythong is None.
		database_adapter=None
		CP_instance=CP(None, None, None, None, None, database_adapter)
		with capture(CP_instance.save_EventsInfo,1405516380.0,[None,'To_print_histo','To_print_Low','To_print_Overflows']) as output:
			self.assertEqual(output, '\nstart_date_time: 2014-07-16 15:04:00 \nhistograms: To_print_histo \nlowlevels: To_print_Low \noverflows: To_print_Overflows\n')
		

	def test_DatabaseCalls_save_EventsInfo(self):
		database=MagicMock()
		database.execute.return_value=True
		database.commit.return_value=True
	
		#Instance of a CountsPettioner where everythong is None except the database_adapter.
		CP_instance=CP(None, None, None, None, None, database)
		CP_instance.save_EventsInfo(1405516380.0,[None,[[4 for x in xrange(128)] for x in xrange(18)],[4 for x in xrange(18)],[0 for x in xrange(18)]])

		database.assert_has_calls([call.execute(mock.ANY), call.commit()], any_order=False)

	def test_Equality_get_min(self):
		response=CP.get_min(1405524513.631769)
		self.assertEqual(response,1405524480.0)

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


	def test_request_get_Counts_EventsInfo(self):
		counts_condition=MagicMock()
		counts_condition.acquire.return_value=True
		counts_condition.wait.return_value=True
		counts_condition.release.return_value=True
		shared_counts_data=[1,2,3,4,5]
		shared_events_data='HiThere'
		# the mock for the port and the counts_condition is the same. This way we can assert the call_order.
		port=counts_condition
		port.write.return_value=True
		
		CP_instance=CP(port, None, counts_condition, shared_counts_data, shared_events_data, None)
		CP_instance.copy_and_reset=MagicMock(return_value='Hi')

		responce=CP_instance.request_get_Counts_EventsInfo(123.0)


		# This is the flow that our thread must follow in order to correctly receive the data.
		# First of all we acquire the condition in order to ensure the atomic execution of the the rest of the code. We can see that the last instruction releases the condition.
		# Once the atomicity is ensured, we proceed with the data acquisition. For the purpose we first write into the port requesting the counts and then we must wait until the counts are delivered by the Reader thread.
		counts_condition.assert_has_calls([call.acquire(),call.write('\x11'),call.wait(),call.release()],any_order=False)
		
		self.assertEqual(responce['Counts'],shared_counts_data)
		#Remember this must equal to the ouput from the copy_and_reset method which is mocked to retyrn 'Hi'. The next assertion will be: Has the copy_and_reset function been called with the value of the shared_events_data.
		self.assertEqual(responce['EventsInfo'],'Hi')
		CP_instance.copy_and_reset.assert_called_with(shared_events_data,False)

		



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
