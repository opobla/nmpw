import time
import threading
from time import strftime
import datetime
import operator
import logging

class FPGASerialReader(threading.Thread):
	def __init__(self, port, counts_condition, shared_counts, shared_countsFromEvents, shared_events):
		threading.Thread.__init__(self)
		self.name='Reader'
		self.port=port
		self.counts_condition=counts_condition
		self.shared_counts=shared_counts
		self.shared_countsFromEvents=shared_countsFromEvents
		self.shared_events=shared_events

		self.status='bytex'
		self.shared_counts[:]			=[0 for x in xrange(18)]
		self.shared_countsFromEvents[:]		=[0 for x in xrange(18)]
		self.shared_events[:]			=[[[0 for x in xrange(128)] for x in xrange(18)],[0 for x in xrange(18)],[0 for x in xrange(18)]]

		self.channel_counts=None

		self.overflow=None

		self.channel=None
		self.count06=None
		self.count711=None
		self.pulse_type=None

		self.counts_val=None
		self.counts_values=None

	def process(self, next):
		#------------------Overflows
		if ((ord(next[0]) & 0b11000000)== 0b00000000):
			self.status='Ovbyte1'
			if self.channel_counts!=None:
				self.channel_counts=None
				logging.info(self.name+': Error:Error while reading the counts.')
			self.overflow=[0 for x in xrange(18)]
			self.overflow[0:6]=[int(x) for x in '{0:06b}'.format(ord(next[0]) & 0b00111111)[::-1]]
			return

		if self.status=='Ovbyte1' and ((ord(next[0]) & 0b10000000) == 0b10000000):
			self.status='Ovbyte2'
			self.overflow[6:13]=[int(x) for x in '{0:07b}'.format(ord(next[0]) & 0b01111111)[::-1]]
			return

		if self.status=='Ovbyte2' and ((ord(next[0]) & 0b10000000) == 0b10000000):
			self.status='bytex'
			self.overflow[13:]=[int(x) for x in '{0:05b}'.format(ord(next[0]) & 0b00011111)[::-1]]
			overflow_general=(ord(next[0]) & 0b00100000) >> 5
			overflow_almost_full=(ord(next[0]) & 0b01000000) >> 6

			self.shared_events[2][:]=map(operator.add, self.shared_events[2],self.overflow)
			#  TODO Decide what to do with the overflow_general and almost_full data...
			return
	
		#----------------Pulse Widths
		if ((ord(next[0]) & 0b11100000) == 0b01000000):
			self.status="byte1"
			if self.channel_counts!=None:
				self.channel_counts=None
				logging.info(self.name+': Error:Error while reading the counts.')
			self.channel=ord(next[0]) & 0b00011111
			return

		if  self.status=="byte1" and ((ord(next[0]) & 0b10000000) == 0b10000000):
			self.status="byte2"
			self.count06=ord(next[0]) & 0b01111111
			return

		if self.status=="byte2" and ((ord(next[0]) & 0b10000000) == 0b10000000):
			self.status="bytex"
			self.count711=ord(next[0]) & 0b00011111
			self.pulse_type=(ord(next[0]) & 0b00100000) >> 5
			pulse_width_ticks=self.count06 + (self.count711 << 7)

			if self.pulse_type==0:
				self.shared_events[1][self.channel] +=1
			if self.pulse_type==1:
				self.shared_events[0][self.channel][pulse_width_ticks>>5] +=1
				self.shared_countsFromEvents[self.channel] +=1
			return

		#----------------Counts
		if ((ord(next[0]) & 0b11100000) == 0b01100000):
			self.status='Contbyte3'
			if self.channel_counts!=None:
				logging.info(self.name+': Error:Error while reading the counts.')
			self.channel_counts=0
			self.counts_val=0
			self.counts_values=[0 for x in xrange(18)]
			return

		if self.status=='Contbyte3' and ((ord(next[0]) & 0b10000000) == 0b10000000):
			self.status='Contbyte1'
			self.counts_val=ord(next[0]) & 0b01111111
			return

		if self.status=='Contbyte1' and ((ord(next[0]) & 0b10000000) == 0b10000000):
			self.status='Contbyte2'
			self.counts_val=self.counts_val+((ord(next[0]) & 0b01111111) << 7)
			return

		if self.status=='Contbyte2' and ((ord(next[0]) & 0b10000000) == 0b10000000):
			self.status='Contbyte3'
			self.counts_val=self.counts_val+((ord(next[0]) & 0b00000011) << 14)
			self.counts_values[self.channel_counts]=self.counts_val
			if self.channel_counts==17:
				self.shared_counts[:]=self.counts_values[:]
				self.counts_condition.release()

				self.channel_counts=None
				self.status='bytex'
			else:
				self.channel_counts +=1
			return



		#--------Error, we have received something that wasnt expected
		if self.channel_counts!=None:
			logging.info(self.name+': Error:Error while reading the counts.')
		self.status='bytex'
		#  TODO maybe restart all the varibles {self.channel_counts}
		#  TODO keep acounts of unexpected reads
		logging.info(self.name+':  Error:Unexpected reading')



	def run(self):
		while True:
			aux= self.port.inWaiting()
			if aux==0:
				aux=1
			if aux >= 2000:
				logging.info(self.name+': inWaiting()= '+`aux`)

			next=self.port.read(aux)
			if not next:
				break
			for data in next:
				self.process(data)
