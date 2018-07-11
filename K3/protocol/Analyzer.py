from bitarray import bitarray
import pdb

class Analyzer:

    def __init__(self):
        self.lastStep=0
        self.lastChannel=bitarray(18)
        self.statusBuffer={}
        self.nsPerStep=20
        

    def process(self,step,channel):
        if (self.lastStep==0):
            self.lastStep=step
            self.lastChannel=channel
            return

        changes=(self.lastChannel ^ channel)
        lastChangeIndex=0
        for i in range(0,changes.count()):
            index=changes.index(True,lastChangeIndex)
            channelKey='ch%02d' % (18-index)
            if (channel[index]):
                status="ON"
                if not(channelKey in self.statusBuffer):
                    continue
                lastOff=self.statusBuffer[channelKey]['lastOff']
                self.statusBuffer[channelKey]['separation']=(step-lastOff)*self.nsPerStep

            else:
                status="OFF"
                if not(channelKey in self.statusBuffer):
                    self.statusBuffer[channelKey]={}
                    self.statusBuffer[channelKey]['lastOff']=step
                    continue

                self.statusBuffer[channelKey]['width']=(step-self.lastStep)*self.nsPerStep
                self.statusBuffer[channelKey]['lastOff']=step
                print channelKey, self.statusBuffer[channelKey]

            lastChangeIndex=lastChangeIndex+1

        self.lastStep=step
        self.lastChannel=channel
       
