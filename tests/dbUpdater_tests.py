import unittest
from mock import MagicMock
import sys
sys.path.append('.')
import dbUpdater
import sqlite3
import MySQLdb

class dbUpdaterTestCase(unittest.TestCase):
	def test_all_in_one(self):
		# Init the config
		dbUpConf={'name':'Lolz the name', 'local':{'name':'/server/trash/test.db'}, 'remote':{'host':'localhost', 'user':'hristo', 'pass':'pass', 'database':'nmdadb_tests'}}

		# Create the sqlite database and push some data to binTable.....
		conn = sqlite3.connect(dbUpConf['local']['name'], check_same_thread=False)
		conn.execute("drop table binTable;")
		conn.execute("CREATE TABLE IF NOT EXISTS 'binTable' (\
			 'start_date_time' datetime NOT NULL,\
			 'ch01' int(11) DEFAULT NULL,\
			 'ch02' int(11) DEFAULT NULL,\
			 'ch03' int(11) DEFAULT NULL,\
			 'ch04' int(11) DEFAULT NULL,\
			 'ch05' int(11) DEFAULT NULL,\
			 'ch06' int(11) DEFAULT NULL,\
			 'ch07' int(11) DEFAULT NULL,\
			 'ch08' int(11) DEFAULT NULL,\
			 'ch09' int(11) DEFAULT NULL,\
			 'ch10' int(11) DEFAULT NULL,\
			 'ch11' int(11) DEFAULT NULL,\
			 'ch12' int(11) DEFAULT NULL,\
			 'ch13' int(11) DEFAULT NULL,\
			 'ch14' int(11) DEFAULT NULL,\
			 'ch15' int(11) DEFAULT NULL,\
			 'ch16' int(11) DEFAULT NULL,\
			 'ch17' int(11) DEFAULT NULL,\
			 'ch18' int(11) DEFAULT NULL,\
			 'hv1' int(11) DEFAULT NULL,\
			 'hv2' int(11) DEFAULT NULL,\
			 'hv3' int(11) DEFAULT NULL,\
			 'hv4' int(11) DEFAULT NULL,\
			 'temp_1' int(11) DEFAULT NULL,\
			 'temp_2' int(11) DEFAULT NULL,\
			 'atmPressure' int(11) DEFAULT NULL,\
			 PRIMARY KEY ('start_date_time')\
		)")

		some_data=[]
		some_data.append(( '2014-01-01 00:00:00', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 1, 2, 3, 4, 1, 2, 999 ))
		some_data.append(( '2014-01-01 00:01:00', 5, 5, 5, 5, 5, 5, 5, 5, 5, 55, 55, 55, 55, 55, 55, 55, 55, 55, 6, 6, 6, 6, 7, 7, 555 ))
		some_data.append(( '2014-01-01 00:02:00', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 1, 2, 3, 4, 1, 2, 999 ))
		some_data.append(( '2014-01-01 00:04:00', 5, 5, 5, 5, 5, 5, 5, 5, 5, 55, 55, 55, 55, 55, 55, 55, 55, 55, 6, 6, 6, 6, 7, 7, 555 ))

		conn.executemany("INSERT INTO binTable (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, hv1, hv2, hv3, hv4, temp_1, temp_2, atmPressure) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", some_data)
		conn.commit()

		# Create the remote mysql database.....
		remote=dbUpConf['remote']
		conn_remote = MySQLdb.connect(	host= 	remote['host'], # your host, usually localhost
						user= 	remote['user'], # your username
						passwd= remote['pass']) # your password

		cur = conn_remote.cursor()
		cur.execute('CREATE DATABASE IF NOT EXISTS '+ remote['database'] +';')
		cur.execute('use '+ remote['database'] +';')

		cur.execute("CREATE TABLE IF NOT EXISTS binTable (\
				 start_date_time datetime NOT NULL,\
				 ch01 int(11) DEFAULT NULL,\
				 ch02 int(11) DEFAULT NULL,\
				 ch03 int(11) DEFAULT NULL,\
				 ch04 int(11) DEFAULT NULL,\
				 ch05 int(11) DEFAULT NULL,\
				 ch06 int(11) DEFAULT NULL,\
				 ch07 int(11) DEFAULT NULL,\
				 ch08 int(11) DEFAULT NULL,\
				 ch09 int(11) DEFAULT NULL,\
				 ch10 int(11) DEFAULT NULL,\
				 ch11 int(11) DEFAULT NULL,\
				 ch12 int(11) DEFAULT NULL,\
				 ch13 int(11) DEFAULT NULL,\
				 ch14 int(11) DEFAULT NULL,\
				 ch15 int(11) DEFAULT NULL,\
				 ch16 int(11) DEFAULT NULL,\
				 ch17 int(11) DEFAULT NULL,\
				 ch18 int(11) DEFAULT NULL,\
				 hv1 int(11) DEFAULT NULL,\
				 hv2 int(11) DEFAULT NULL,\
				 hv3 int(11) DEFAULT NULL,\
				 hv4 int(11) DEFAULT NULL,\
				 temp_1 int(11) DEFAULT NULL,\
				 temp_2 int(11) DEFAULT NULL,\
				 atmPressure int(11) DEFAULT NULL,\
				 PRIMARY KEY (start_date_time)\
		)")


		# Once created the two databases we call the dbUpdater
		the_dbUpdater=dbUpdater.dbUpdater(dbUpConf)
		the_dbUpdater.start()
		the_dbUpdater.join()

		# The two databases should have the same content. The next step is to check.

		cur.execute("select * from binTable;")
		count=0
		for row in cur:
			the_row=(str(row[0]), row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25])

			self.assertEqual(the_row,some_data[count])
			count+=1



		#  TODO insert some more data into the local database, then call again the dbUpdater and finally chech.




		# Finally drop the remote database
		cur.execute("drop database "+remote['database']+";")
