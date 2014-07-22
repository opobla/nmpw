import time
import threading
from time import strftime
import datetime
import operator

class Reader(threading.Thread):
	def __init__(self, port, end_condition, counts_condition, shared_counts_data, shared_events_data):
		threading.Thread.__init__(self)
		self.name='Reader'
		self.port=port
		self.end_condition=end_condition
		self.counts_condition=counts_condition
		self.shared_counts_data=shared_counts_data
		self.shared_events_data=shared_events_data

		self.status='bytex'
		self.histo_data=[[0 for x in xrange(128)] for x in xrange(18)]
		self.events_min=[0 for x in xrange(18)]
		self.low_events=[0 for x in xrange(18)]
		self.overflows=[0 for x in xrange(18)]

		self.shared_counts_data[:]=[0 for x in xrange(18)]
		self.shared_events_data[:]=[[0 for x in xrange(18)],[[0 for x in xrange(128)] for x in xrange(18)],[0 for x in xrange(18)],[0 for x in xrange(18)]]
		
	def run(self):
		channel_counts=None
		while self.end_condition.is_set():
			next=self.port.read(1)
			if not next:
				break
	
			#------------------Overflows
			if ((ord(next[0]) & 0b11000000)== 0b00000000):
				self.status='Ovbyte1'
				if channel_counts!=None:
					channel_counts=None
					#  TODO Something went wrong reading the Counts
				overflow=[0 for x in xrange(18)]
				overflow[0:6]=[int(x) for x in '{0:06b}'.format(ord(next[0]) & 0b00111111)[::-1]]
				continue

			if self.status=='Ovbyte1' and ((ord(next[0]) & 0b10000000) == 0b10000000):
				self.status='Ovbyte2'
				overflow[6:13]=[int(x) for x in '{0:07b}'.format(ord(next[0]) & 0b01111111)[::-1]]
				continue

			if self.status=='Ovbyte2' and ((ord(next[0]) & 0b10000000) == 0b10000000):
				self.status='bytex'
				overflow[13:]=[int(x) for x in '{0:05b}'.format(ord(next[0]) & 0b00011111)[::-1]]
				overflow_general=(ord(next[0]) & 0b00100000) >> 5
				overflow_almost_full=(ord(next[0]) & 0b01000000) >> 6
	
				print 'Yo man overflow: ',overflow
				self.shared_events_data[3][:]=map(operator.add, self.shared_events_data[3],overflow)
				#  TODO Decide what to do with the overflow_general and almost_full data...
				continue
		
			#----------------Pulse Widths
    			if ((ord(next[0]) & 0b11100000) == 0b01000000):
        			self.status="byte1"
				if channel_counts!=None:
					channel_counts=None
					#  TODO Something went wrong reading the Counts
        			channel=ord(next[0]) & 0b00011111
        			continue

    			if  self.status=="byte1" and ((ord(next[0]) & 0b10000000) == 0b10000000):
        			self.status="byte2"
        			count06=ord(next[0]) & 0b01111111
        			continue

    			if self.status=="byte2" and ((ord(next[0]) & 0b10000000) == 0b10000000):
        			self.status="bytex"
        			count711=ord(next[0]) & 0b00011111
        			pulse_type=(ord(next[0]) & 0b00100000) >> 5
        			pulse_width_ticks=count06 + (count711 << 7)

				if pulse_type==0:
					#self.low_events[channel] +=1
					self.shared_events_data[2][channel] +=1
				if pulse_type==1:
					#self.histo_data[channel][pulse_width_ticks>>5] +=1
					self.shared_events_data[1][channel][pulse_width_ticks>>5] +=1
					#self.events_min[channel] +=1
					self.shared_events_data[0][channel] +=1
				

        			print datetime.datetime.now().time(),"Ch:",channel,"Pulse type:",pulse_type," Pulse width:",pulse_width_ticks,\
                			float(pulse_width_ticks) / 50.0,"useg"
        			continue


			#----------------Counts
			if ((ord(next[0]) & 0b11100000) == 0b01100000):
				self.status='Contbyte3'
				print 'Counts transmision started...'
				if channel_counts!=None:
					print '' #This is here just to make compilation possible
					#  TODO Somethong went wrong reading the Counts
				channel_counts=0
				counts_val=0
				counts_values=[0 for x in xrange(18)]
				continue

			if self.status=='Contbyte3' and ((ord(next[0]) & 0b10000000) == 0b10000000):
				self.status='Contbyte1'
				counts_val=ord(next[0]) & 0b01111111
				continue

			if self.status=='Contbyte1' and ((ord(next[0]) & 0b10000000) == 0b10000000):
				self.status='Contbyte2'
				counts_val=counts_val+((ord(next[0]) & 0b01111111) << 7)
				continue

			if self.status=='Contbyte2' and ((ord(next[0]) & 0b10000000) == 0b10000000):
				self.status='Contbyte3'
				counts_val=counts_val+((ord(next[0]) & 0b00000011) << 14)
				counts_values[channel_counts]=counts_val
				if channel_counts==17:
					self.shared_counts_data[:]=counts_values[:]
					self.counts_condition.release()

					channel_counts=None
					self.status='bytex'
				else:
					channel_counts +=1
				continue



			#--------Error, we have received something that wasnt expected
			if channel_counts!=None:
				print ''#this is here just to make compilation posible 
				#  TODO Somethong went wrong reading the Counts
			self.status='bytex'
			#  TODO maybe restart all the varibles {channel_counts}
			#  TODO keep acounts of unexpected reads
			print 'Unexpected reading'




