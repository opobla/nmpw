import Queue
import thread
import struct
from K3.protocol.Decoder import Decoder
from K3.protocol.Analyzer import Analyzer

q=Queue.Queue()

def reader(queue):
    with open("out.raw", "rb") as f:
        dataString = f.read()
   
    for data in dataString:
        byte=struct.unpack('B',data)[0]
        queue.put(byte)

def decoder(queue):
    deco=Decoder(Analyzer())
    while not queue.empty():
        byte=queue.get()
        deco.process(byte)

reader(q)
decoder(q)

