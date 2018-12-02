import telnetlib
import re
from datetime import datetime, timedelta


class VaisalaDriver:

    def __init__(self, args):
        self.temperature_in_celsius = None
        self.pressure_in_hPa = None
        self.relative_humidity = None
        self.last_update = None
        self.vaisala_ip = args.vaisala_ip
        self.vaisala_port = args.vaisala_port

    def update_info(self):
        telnet_client = telnetlib.Telnet(self.vaisala_ip, self.vaisala_port)
        telnet_client.read_until(">".encode("ascii"))
        telnet_client.write("SEND".encode("ascii") + b"\r")
        telnet_client.read_until(b"\n")
        response = telnet_client.read_until(b"\n")
        self.pressure_in_hPa, self.temperature_in_celsius, self.relative_humidity = self.parse_response(response)
        self.last_update = datetime.now()
        return self.pressure_in_hPa, self.temperature_in_celsius, self.relative_humidity

    def get_pressure(self):
        if self.is_info_expired(): self.update_info()
        return self.pressure_in_hPa

    def get_temperature(self):
        if self.is_info_expired(): self.update_info()
        return self.temperature_in_celsius

    def get_relative_humidity(self):
        if self.is_info_expired(): self.update_info()
        return self.relative_humidity

    def parse_response(self, response):
        tokens = re.search("P= *([0-9.]+) *hPa[ \t]*T=[ \t]*([0-9.]+)[ \t]*'C[ \t]*RH=[ \t]*([0-9.]+)", response)
        self.pressure_in_hPa = float(tokens.group(1))
        self.temperature_in_celsius = float(tokens.group(2))
        self.relative_humidity = float(tokens.group(3))
        return self.pressure_in_hPa, self.temperature_in_celsius, self.relative_humidity

    def is_info_expired(self):
        return self.last_update is None or datetime.now() - self.last_update > timedelta(seconds=30)
