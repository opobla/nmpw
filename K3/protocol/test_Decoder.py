import unittest
import mock

from bitarray import bitarray
from K3.protocol import Analyzer
from K3.protocol.Decoder import Decoder

class TestDecoder(unittest.TestCase):

    @mock.patch('K3.protocol.Analyzer')
    def test_step1(self,analyzer):
        sequence=[0x60,0x80,0x80,0xFF,0x81,0x80,0x80,0x80,0x80]
        self.assertEqual(len(sequence),9)

        deco=Decoder(analyzer)
        for byte in sequence:
            deco.process(byte)

        analyzer.process.assert_called_with(255,bitarray('000000000000000000'));

    @mock.patch('K3.protocol.Analyzer')
    def test_step2(self,analyzer):
        sequence=[0x60,0x80,0x80,0xFF,0x83,0x80,0x80,0x80,0x80]
        self.assertEqual(len(sequence),9)

        deco=Decoder(analyzer)
        for byte in sequence:
            deco.process(byte)

        analyzer.process.assert_called_with(511,bitarray('000000000000000000'));

    @mock.patch('K3.protocol.Analyzer')
    def test_step3(self,analyzer):
        sequence=[0x60,0x80,0x80,0xFF,0xA3,0xC4,0x88,0xF1,0x8F]
        self.assertEqual(len(sequence),9)

        deco=Decoder(analyzer)
        for byte in sequence:
            deco.process(byte)

        analyzer.process.assert_called_with(545747177983,bitarray('000000000000000000'));

    @mock.patch('K3.protocol.Analyzer')
    def test_seq1(self,analyzer):
        sequence=[0x75,0xAA,0x95,0x8A,0x80,0x80,0x80,0x80,0x80]
        self.assertEqual(len(sequence),9)

        deco=Decoder(analyzer)
        for byte in sequence:
            deco.process(byte)

        analyzer.process.assert_called_with(10,bitarray('010101010101010101'));

    @mock.patch('K3.protocol.Analyzer')
    def test_seq2(self,analyzer):
        sequence=[0x7F,0xFF,0xBF,0xFF,0xFF,0xFF,0xFF,0xFF,0x8F]
        self.assertEqual(len(sequence),9)

        deco=Decoder(analyzer)
        for byte in sequence:
            deco.process(byte)

        analyzer.process.assert_called_with(549755813887,bitarray('111111111111111111'));

    @mock.patch('K3.protocol.Analyzer')
    def test_outOfSync(self,analyzer):
        sequence=[0x64,0x80,0x80,0xE3,0xAE,0xC8,0x8B,0x80,0x80]
        self.assertEqual(len(sequence),9)

        deco=Decoder(analyzer)

        self.assertRaises(NameError,deco.process(sequence[0]));

