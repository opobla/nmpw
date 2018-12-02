# coding=utf-8
import AP1Driver
import BM35Driver
import HVPSDriver
import time
import vaisala_driver
from dummy_driver import DummyDriver


class SensorsManager:
    def __init__(self, args):
        self.name = "Sensors manager"
        self.bar_type = args.barometer_type

        #TODO: rehacer todo esto para el resto de barómetros
        self.port_data = None
        self.hvps_type = None

        self.init_resources(args)

    def init_resources(self, args):
        # Set a timeout for the data port
        if self.port_data != None:
            # 1.5 secs should be enough time
            self.port_data.timeout = 1.5

        # Init the context for ap1
        if self.bar_type == 'ap1':
            AP1Driver.ap1_init_strobe_reader()

        # Init the context for analog barometers
        if self.hvps_type == 'analog':
            HVPSDriver.analogHVPS_init()

        if self.bar_type == 'bm35':
            BM35Driver.bm35_request_1min_reading_period(self.port_data)

        if self.bar_type == 'vaisala':
            self.pressure_adapter = vaisala_driver.VaisalaDriver(args)
        
        if self.bar_type is None:
            self.pressure_adapter = DummyDriver()


    def read_pressure(self):
        if self.bar_type == None:
            return -1
        if self.bar_type == 'bm35':
            self.port_control.write('\x00')
            time.sleep(0.5)
            self.port_data.flush()
            BM35Driver.bm35_request_pressure_reading(self.port_data)
            pressure_raw = self.port_data.readline()
            pressure = BM35Driver.bm35_parse_pressure_answer(pressure_raw)
            return pressure['meanPressure']
        if self.bar_type == 'ap1':
            pressure = AP1Driver.ap1_read_pressure_using_strobe()
            return pressure
        if self.bar_type == 'vaisala':
            pass

    def read_hvps(self):
        if self.hvps_type == None:
            return -1, -1, -1, -1
        if self.hvps_type == 'digital':
            self.port_control.write('\x01')
            time.sleep(0.5)
            self.port_data.flush()
            # TODO request the data from the sensor
            hvps1_raw = self.port_data.readline()
            hvps1 = hvps1_raw  # TODO parse the raw value

            self.port_control.write('\x02')
            time.sleep(0.5)
            self.port_data.flush()
            # TODO request the data from the sensor
            hvps2_raw = self.port_data.readline()
            hvps2 = hvps2_raw  # TODO parse the raw value

            self.port_control.write('\x03')
            time.sleep(0.5)
            self.port_data.flush()
            # TODO request the data from the sensor
            hvps3_raw = self.port_data.readline()
            hvps3 = hvps3_raw  # TODO parse the raw value

            # We can only read three digital hvps, so we return a -1 for the fourth one.
            return hvps1, hvps2, hvps3, -1
        if self.hvps_type == 'analog':
            return HVPSDriver.analogHVPS_read(self.analog_hvps_corr)

    def read_temp(self):
        return -1, -1

    def get_temperature(self):
        return self.pressure_adapter.get_temperature()

    def get_pressure(self):
        return self.pressure_adapter.get_pressure()

    def get_relative_humidity(self):
        return self.pressure_adapter.get_relative_humidity()
