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

		# TODO conn_remote last_from_remote="select start_date_time from bintable order by start_date_time desc limit 1
		# TODO conn local  to_apdate="select * from binTable where start_date_time > "+ last_from_remote +" limit 50
		# TODO conn remote  Update with to_update

		print 'Nice'

