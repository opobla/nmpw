from bitarray import bitarray

class Decoder:

    def __init__(self,analyzer):
        self.channel=bitarray(18)
        self.status='Ovbyte0'
        self.analyzer=analyzer

    def process(self, next):
        if self.status=='Ovbyte0' and  ((next & 0b11100000)==0b01100000):
            self.status='Ovbyte1'
            self.channel=bitarray(18)
            self.channel[13:18]=bitarray('{0:05b}'.format((next & 0b00011111)))
            return
        if self.status=='Ovbyte1' and ((next & 0b10000000) == 0b10000000):
            self.status='Ovbyte2'
            self.channel[6:13]=bitarray('{0:07b}'.format((next & 0b01111111))) 
            return
        if self.status=='Ovbyte2' and ((next & 0b11000000) == 0b10000000):
            self.status='Ovbyte3'
            self.channel[0:6]=bitarray('{0:06b}'.format((next & 0b00111111)))
            return
        if self.status=='Ovbyte3' and ((next & 0b10000000) == 0b10000000):
            self.status='Ovbyte4'
            self.step=next & 0b01111111 
            self.step_state=1
            return

        if self.status=='Ovbyte4' and ((next & 0b10000000) == 0b10000000):
            self.step=self.step + ((next & 0b01111111) << (7*self.step_state))
            self.step_state=self.step_state+1
            if (self.step_state==6):
                self.status='Ovbyte0'
                #print str(self.step*10) + "-" + self.channel.to01()
                self.analyzer.process(self.step,self.channel)
                return
        return

        raise NameError('Invalid sequence ' + str(next) + " while in "
                +self.status )
