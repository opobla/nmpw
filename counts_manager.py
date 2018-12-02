import datetime
#import numpy


class CountsManager:

    def __init__(self, database_adapter):
        self.name = 'CountsManager'
        self.database_adapter = database_adapter

    def save_counts(self, time_now, counts, sensors):
        time_entry = datetime.datetime.fromtimestamp(time_now).strftime('%Y-%m-%d %H:%M:%S')
        if self.database_adapter is None:
            print 'start_date_time:', time_entry, 'Counts:', counts, 'Sensors:', sensors
        else:
            sql = "INSERT INTO binTable (start_date_time, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, hv1, hv2, hv3, hv4, temp_1, temp_2, atmPressure) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            self.database_adapter.execute(sql, [time_entry] + counts + [sensors['hv1'], sensors['hv2'], sensors['hv3'],
                                                                        sensors['hv4'], sensors['temp_1'],
                                                                        sensors['temp_2'], sensors['atmPressure']])
            self.database_adapter.commit()

    @staticmethod
    def get_min(the_time):
        return the_time - the_time % 60

    def median_algorithm(self, counts):
        r = [float(x) / float(z) for x, z in zip(counts, self.channel_avg)
             if z > 0 and 0.3 < (float(x) / float(z)) < 10]
        tet = numpy.median(r)
        s0 = sum(self.channel_avg)
        summa = s0 * tet
        return summa
