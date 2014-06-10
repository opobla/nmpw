import sys

#Read from console.
data=sys.stdin.read()

for i in range(0,len(data)-1,3):
	#me quedo con los 5 primeros bits..
	channel = ord(data[i])&0b00011111

	valueLow = ord(data[i+1])&0b01111111
	valueHigh = (ord(data[i+2])&0b00011111)<<7
	value=valueLow+valueHigh

	level = (ord(data[i+2])&0b00100000)>>5

	print 'channel: ',channel,' value: ',value,' level: ',level
