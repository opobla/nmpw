def validate_arguments(args):
	# Arguments always needed
	if args.serial_port_control==None:
		end('A control serial port is needed')
	if args.database==None:
		end('A database is needed')

	# Valid bar_type 
	if not(args.barometer_type==None or args.barometer_type=='ap1' or args.barometer_type=='bm35'):
		end('Invalid barometer type')

	# Valid hvps_type
	if not(args.hvps_type==None or args.hvps_type=='digital' or args.hvps_type=='analog'):
		end('Invalid hvps_type')

	# The needed port are present
	if (args.hvps_type=='digital' or args.barometer_type=='bm35') and (args.serial_port_control==None or args.serial_port_sensors==None):
		end('In order to read data from a digital hvps we need two ports, one for control and one for data')

	#  TODO dbupdater arguemnts.....


def end(error_msg):
	pass
	raise AttributeError(error_msg)
