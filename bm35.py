import re


class bm35:
	# Returns the command with correspondient check sum
	@staticmethod
	def bm35_compute_crc(command):
		the_sum=0;
		for x in range(0,len(command)):
			the_sum +=ord(command[x])
		check_sum=the_sum%1000
		return command+`check_sum`

	@staticmethod
	def bm35_parse_pressure_answer(answer):
		re_answer=re.compile('^M[0-9][0-9]D[0-9][0-9].[0-9][0-9].[0-9][0-9][0-9][0-9],[0-9][0-9]:[0-9][0-9],[0-9]+,[0-9]+,[0-9][0-9][0-9][0-9]$')
		if not(re_answer.match(answer)):
			raise ValueError("Invalid answer to parse")
		if bm35.bm35_compute_crc(answer[:-3]) != answer:
			raise ValueError("Answers crc is invalid")

		m=re.compile('[, || D || M || .]')
		splited=m.split(answer)
		the_date=splited[4]+'-'+splited[3]+'-'+splited[2]+' '+splited[5]+':00'
		return {'date':the_date,
			'meanPressure':int(splited[6]),
			'instantPressure':int(splited[7])}

	@staticmethod
	def bm35_request_1min_reading_period(port):
		command='A00I10'
		full_command=bm35.bm35_compute_crc(command)
		full_command +='\r\n'
		#  TODO not sure......
		port.write(full_command)

	@staticmethod
	def bm35_request_pressure_reading(port):
		command='A00Q1'
		full_command=bm35.bm35_compute_crc(command)
		full_command +='\r\n'
		#  TODO not sure......
		port.write(full_command)

