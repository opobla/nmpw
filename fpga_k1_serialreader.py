import struct


class FpgaK1SerialReader:
    def __init__(self, port):
        """

        :type port: serial.Serial
        """
        self.name = 'Reader'
        self.port = port

    def get_samples(self):
        return self.send_read_samples_command()

    def send_read_samples_command(self):
        self.port.write(bytearray([1]))
        raw_values = self.port.read(36)
        self.port.flush()
        values = [struct.unpack(">H", raw_values[s:s + 2])[0] for s in range(0, 35, 2)]
        values.reverse()
        return values

    @staticmethod
    def print_values(values):
        channel = 1
        for value in values:
            print "Channel {0: >2}: {1: >5} counts".format(channel, value)
            channel = channel + 1
        pass
