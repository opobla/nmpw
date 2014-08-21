import sqlite3
import MySQLdb
import threading
from threading import Thread

class dbUpdater(threading.Thread):
	def __init__(self, dbUpConf):
		threading.Thread.__init__(self)
		self.name='dbUpdater'
		self.local=dbUpConf['local']
		self.remote=dbUpConf['remote']

	def run(self):
		conn_local = sqlite3.connect(self.local['name'])
		conn_remote = MySQLdb.connect(	host= 	self.remote['host'], # your host, usually localhost
				 		user= 	self.remote['user'], # your username
						passwd= self.remote['pass'], # your password
						db= 	self.remote['database']) # name of the data base


		cur_rem = conn_remote.cursor()
		cur_rem.execute("SELECT max(start_date_time) FROM binTable")
		row = cur_rem.fetchone()
		last_data_remote=row[0]

		print last_data_remote
		if last_data_remote==None:
			last_data_remote='2000-01-01 00:00:00'
		else:
			last_data_remote=str(last_data_remote)

		cur_loc = conn_local.cursor()    
		cur_loc.execute("SELECT * FROM binTable where start_date_time > '"+ last_data_remote +"' limit 60*12")

		rows = []
		while True:	      
			row = cur_loc.fetchone()
			if row == None:
				break
			rows.append((str(row[0]),row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25]))
		
		cur_rem.executemany("INSERT INTO binTable (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, hv1, hv2, hv3, hv4, temp_1, temp_2, atmPressure) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
