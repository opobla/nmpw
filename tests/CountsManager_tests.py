import unittest
import mock
from mock import MagicMock
from mock import call
import sys
sys.path.append('.')
from CountsManager import CountsManager as CM

class CountsManagerTestCase(unittest.TestCase):

	def test_Constructor(self):
		myCM=CM('port', 'counts_condition', 'shared_counts', 'shared_countsFromEvents', 'shared_events', 'database_adapter', 'sensors_manager', 'dbUpConf', 'channel_avg', 'pressureConf', 'efficiencyConf')
		self.assertEqual(myCM.name,'CountsManager','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.port,'port','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.counts_condition, 'counts_condition','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.shared_counts, 'shared_counts','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.shared_countsFromEvents, 'shared_countsFromEvents','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.shared_events, 'shared_events','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.database_adapter, 'database_adapter','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.sensors_manager, 'sensors_manager','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.dbUpConf, 'dbUpConf','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.channel_avg, 'channel_avg','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.pressureConf, 'pressureConf','CountsPettioner Constructor behaving incorrectly')
		self.assertEqual(myCM.efficiencyConf, 'efficiencyConf','CountsPettioner Constructor behaving incorrectly')

	def test_Equality_aux(self):
		response=CM.aux(['hola','hello'])
		self.assertEqual(response, '["hola", "hello"]')

		response=CM.aux({'color':'red','fruits':['apple','pear','strawberry','banana'],'numbers':[1,2,3,4,5]})
		self.assertEqual(response, '{"color": "red", "numbers": [1, 2, 3, 4, 5], "fruits": ["apple", "pear", "strawberry", "banana"]}')

	def test_Equality_reset_to_0(self):
		aux=[234,432,[43243,4324,4234,[324,324,[3445]]]]
		CM.reset_to_0(aux)
		self.assertEqual(aux, [0, 0, [0, 0, 0, [0, 0, [0]]]])

	def test_Eqiality_copy_and_reset(self):
		aux1=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		aux2=[[345,321],[3452,421],[43243,4324,4234,[324,324,[3445]]]]
		response=CM.copy_and_reset(aux1)
		self.assertEqual(aux2, response)
		self.assertEqual(aux1,[[0,0],[0,0],[0,0,0,[0,0,[0]]]])

	def test_Equality_get_min(self):
		response=CM.get_min(1405524513.631769)
		self.assertEqual(response,1405524480.0)

		response=CM.get_min(123.3)
		self.assertEqual(response,120.0)

	def test_calc_globals(self):
		myCM=CM('port', 'counts_condition', 'shared_counts', 'shared_countsFromEvents', 'shared_events', 'database_adapter', 'sensors_manager', 'dbUpConf',\
 				[255, 290, 0, 295, 0, 0, 289, 291, 252, 254, 293, 299, 298, 328, 299, 302, 302, 272], \
					{'average':932, 'beta':0.0067}, {'beta':1.0})

		counts0=[242, 239, 0, 276, 0, 0, 279, 251, 242, 236, 293, 319, 270, 323, 290, 258, 268, 276]
		counts1=[223, 305, 0, 284, 0, 0, 288, 268, 289, 240, 283, 284, 279, 304, 302, 316, 317, 250]
		counts2=[239, 300, 0, 256, 0, 0, 322, 287, 246, 235, 306, 328, 311, 324, 268, 308, 347, 255]
		counts3=[241, 321, 0, 284, 0, 0, 306, 295, 297, 241, 288, 282, 277, 274, 290, 279, 302, 262]
		counts4=[265, 296, 0, 324, 0, 0, 374, 297, 293, 291, 292, 256, 318, 363, 298, 306, 301, 317]

		counts0=[228, 234, 93, 262, 0, 0, 240, 260, 238, 210, 238, 261, 240, 0, 261, 257, 244, 257]
		counts1=[217, 283, 102, 256, 0, 0, 246, 242, 179, 229, 281, 258, 274, 0, 305, 274, 278, 271]

		pressure0=93891
		pressure1=93890 
		pressure2=93890
		pressure3=93890
		pressure4=93889 

		globals0=(round(68.3167, 2)	, round(70.1333, 2) , round(70.1333, 2))
		globals1=(round(69.3, 2)	, round(71.1333, 2) , round(71.1333, 2)) 
		globals2=(round(71.1, 2)	, round(72.9833, 2) , round(72.9833, 2))
		globals3=(round(69.3333, 2)	, round(71.1667, 2) , round(71.1667, 2))
		globals4=(round(74.8, 2)	, round(76.7833, 2) , round(76.7833, 2)) 

		return0=myCM.calc_globals(counts0, {'atmPressure':pressure0})
		return1=myCM.calc_globals(counts1, {'atmPressure':pressure1}) 
		return2=myCM.calc_globals(counts2, {'atmPressure':pressure2}) 
		return3=myCM.calc_globals(counts3, {'atmPressure':pressure3}) 
		return4=myCM.calc_globals(counts4, {'atmPressure':pressure4}) 

		return0=(round(return0[0], 3), round(return0[1], 2), round(return0[2], 2))
		return1=(round(return1[0], 3), round(return1[1], 2), round(return1[2], 2))
		return2=(round(return2[0], 2), round(return2[1], 2), round(return2[2], 2))
		return3=(round(return3[0], 2), round(return3[1], 2), round(return3[2], 2))
		return4=(round(return4[0], 2), round(return4[1], 2), round(return4[2], 2))

		print "\n", return0
		print return1

		#self.assertEqual(return0, globals0)
	
	
	"""
	def test_request_get_Counts_EventsInfo(self):
		counts_condition=MagicMock()
		counts_condition.acquire.return_value=True
		shared_counts_data=[1,2,3,4,5]
		shared_events_data='HiThere'
		# the mock for the port and the counts_condition is the same. This way we can assert the call_order.
		port=counts_condition
		port.write.return_value=True
		
		CP_instance=CP(port, None, counts_condition, shared_counts_data, shared_events_data, None, None, None)
		CP_instance.copy_and_reset=MagicMock(return_value='Hi')

		responce=CP_instance.request_get_Counts_EventsInfo(123.0)


		# This is the flow that our thread must follow in order to correctly receive the data.
		# First of all we acquire the condition in order to ensure the atomic execution of the the rest of the code. We can see that the last instruction releases the condition.
		# Once the atomicity is ensured, we proceed with the data acquisition. For the purpose we first write into the port requesting the counts and then we must wait until the counts are delivered by the Reader thread.
		counts_condition.assert_has_calls([call.write('\x11'),call.acquire()],any_order=False)
		
		self.assertEqual(responce['Counts'],shared_counts_data)
		#Remember this must equal to the ouput from the copy_and_reset method which is mocked to retyrn 'Hi'. The next assertion will be: Has the copy_and_reset function been called with the value of the shared_events_data.
		self.assertEqual(responce['EventsInfo'],'Hi')
		CP_instance.copy_and_reset.assert_called_with(shared_events_data,False)


	def test_run_loop(self):
		# Mock the time
		time=MagicMock()
		time.sleep.return_value=True		
		time.time.side_effect=ReturnSequence([40.7,40.9,68.7,68.8],0.0)

		# Mock the end condition
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True,True],False)

		# Make the CountsPettioner use the mocked time.
		sys.modules['time'] = time
		import CountsPettioner
		reload(CountsPettioner)  

		# Create CountsPettioner and mock the methods called inside the run loop
		CP_instance=CP(None, end_condition, None, None, None, None, None, None)
		aux=MagicMock()
		aux.request_get_Counts_EventsInfo.return_value='Potato'
		aux.save_data.return_value=True
		aux.read_sensors.return_value='Potato2'
		CP_instance.request_get_Counts_EventsInfo=aux.request_get_Counts_EventsInfo
		CP_instance.save_data=aux.save_data
		CP_instance.read_sensors=aux.read_sensors
	
		CP_instance.run()
		
		end_condition.is_set.assert_called_with()
		time.sleep.assert_has_calls([call(60.0-40.9),call(120.0-68.8)])
		aux.assert_has_calls([call.request_get_Counts_EventsInfo(0.0),call.save_data(0.0, 'Potato', 'Potato2')], any_order=False)


	def test_run_loop_error(self):
		# Mock the time
		time=MagicMock()
		time.sleep.return_value=True		
		time.time.side_effect=ReturnSequence([40.7,40.9,59.7,59.8],0.0)

		#Mock the logging
		logging=MagicMock()
		logging.info.return_value=True

		# Mock the end condition
		end_condition=MagicMock()
		end_condition.is_set.side_effect=ReturnSequence([True,True],False)

		# Make the CountsPettioner use the mocked time.
		sys.modules['time'] = time
		import CountsPettioner
		reload(CountsPettioner)  

		# Make the CountsPettioner use the mocked logging
		sys.modules['logging'] = logging
		import CountsPettioner
		reload(CountsPettioner)


		# Create CountsPettioner and mock the methods called inside the run loop
		CP_instance=CP(None, end_condition, None, None, None, None, None, None)

		aux=MagicMock()
		aux.request_get_Counts_EventsInfo.return_value='Potato'
		aux.save_data.return_value=True
		aux.read_sensors.return_value='Potato2'
		CP_instance.request_get_Counts_EventsInfo=aux.request_get_Counts_EventsInfo
		CP_instance.save_data=aux.save_data
		CP_instance.read_sensors=aux.read_sensors
	
		CP_instance.run()
		# the CountsPettioner thread should wake up once every minute. With this test we assert if an error is correctly logged when the thread wakes up twice in the same minute
		logging.info.assert_called_with(mock.ANY)

	def test_Calls_read_sensors(self):
		#Mock the sensors_manager
		sensors_manager=MagicMock()
		sensors_manager.read_pressure.return_value=11
		sensors_manager.read_hvps.return_value=22, 33, 44 ,55
		sensors_manager.read_temp.return_value=66, 77

		CP_instance=CP(None, None, None, None, None, None, sensors_manager, None)
		returned_value=CP_instance.read_sensors()
		
		sensors_manager.read_pressure.assert_called_with()
		sensors_manager.read_hvps.assert_called_with()
		sensors_manager.read_temp.assert_called_with()

		self.assertEqual(returned_value, {'atmPressure': 11, 'hv1':22, 'hv2':33, 'hv3':44, 'hv4':55, 'temp_1':66, 'temp_2':77})
		
		

	def test_Calls_dbUpdater(self):
		#Mock the dbUpdater
		dbUpdater=MagicMock()
		#dbUpdater.__init__.return_value=True
		dbUpdater.start.return_value=True

		# Make the CountsPettioner use the mocked dbUpdater
		sys.modules['dbUpdater'] = dbUpdater
		import CountsPettioner
		reload(CountsPettioner)

		CP_instance=CP(None, None, None, None, None, None, None, 'Something not None')
		CP_instance.update_remote()
	"""




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

    def __call__(self):
        if 0  < len(self.return_sequence):
            	return self.return_sequence.pop(0)
	else:
		return self.expired
