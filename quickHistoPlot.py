import sqlite3
import json
import matplotlib.pyplot as plt
import numpy as np

data_date='2014-07-05 15:20:00'
channel_toplot=1 #0..17
database_name='test.db'
sql="select * from EventsInfo10Mins where start_date_time='"+data_date+"';"

conn = sqlite3.connect(database_name, check_same_thread=False)
data_json='{0}'.format(conn.execute(sql).fetchone()[3+channel_toplot])

data=json.loads(data_json)
plt.bar(np.arange(128),data)
plt.ylabel('Eje Y')
plt.xlabel('0.2...........81.9            Data in usecs')
print data
plt.show()
