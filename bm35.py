import re
import logging

# Returns the command with correspondient check sum
def bm35_compute_crc(command):
	the_sum=0;
	for x in range(0,len(command)):
		the_sum +=ord(command[x])
	check_sum=the_sum%1000
	return command+`check_sum`

def bm35_parse_pressure_answer(answer):
	answer=answer[:-2]
	re_answer=re.compile('^M[0-9][0-9]D[0-9][0-9].[0-9][0-9].[0-9][0-9][0-9][0-9],[0-9][0-9]:[0-9][0-9],[0-9]+,[0-9]+,[0-9][0-9][0-9][0-9]$')
	if not(re_answer.match(answer)):
		logging.info('Bm35: Invalid answer to parse. Bad format')
		return {'date':-1,
			'meanPressure':-1,
			'instantPressure':-1}
	if bm35_compute_crc(answer[:-3]) != answer:
		logging.info('Bm35: Invalid answer to parse. Wrong CRC')
		return {'date':-1,
			'meanPressure':-1,
			'instantPressure':-1}

	m=re.compile('[, || D || M || .]')
	splited=m.split(answer)
	the_date=splited[4]+'-'+splited[3]+'-'+splited[2]+' '+splited[5]+':00'
	return {'date':the_date,
		'meanPressure':int(splited[6]),
		'instantPressure':int(splited[7])}

def bm35_request_1min_reading_period(port):
	command='A00I10'
	full_command=bm35_compute_crc(command)
	full_command +='\r\n'
	port.write(full_command)

def bm35_request_pressure_reading(port):
	command='A00Q1'
	full_command=bm35_compute_crc(command)
	full_command +='\r\n'
	port.write(full_command)

