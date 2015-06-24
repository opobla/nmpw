from bitarray import bitarray

class Analyzer:

    def __init__(self):
        self.lastStep=0
        self.lastChannel=bitarray(18)
        self.statusBuffer={}
        

    def process(self,step,channel):
        if (self.lastStep==0):
            self.lastStep=step
            self.lastChannel=channel
            return

        changes=(self.lastChannel ^ channel)
        lastChangeIndex=0
        for i in range(0,changes.count()):
            index=changes.index(True,lastChangeIndex)
            if (channel[index]):
                status="ON"
                self.statusBuffer={ 'ch%02d' % (18-index):\
                        { 'separation': step-self.lastStep}}
            else:
                if not('ch%02d' % (18-index) in self.statusBuffer):
                    return

                status="OFF"
                self.statusBuffer['ch%02d' % (18-index)]['width']=step-self.lastStep
                print 'ch%02d' % (18-index), self.statusBuffer['ch%02d' % (18-index)]


            lastChangeIndex=lastChangeIndex+1

        print str(self.lastStep) + "-" + str(step) + "\t" +\
            "DeltaT=" + str(step-self.lastStep) + "\t" +\
            self.lastChannel.to01() + "-" + channel.to01() + "\t" \
            "Xor=" + changes.to01()

        self.lastStep=step
        self.lastChannel=channel
       
