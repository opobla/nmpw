import sys
import numpy as np
from random import randrange

s=np.random.poisson(300);
level='1'
#secs*mins*hours*days
for z in range (0,60*60*24*2):
	#300 lecturas / 60 secs = 5
	s=np.random.poisson(5);
	#~5 lecturas * 18 tubos..
	for y in range(0,(s*18)-1):
		#Random uniform distribution 1-18=>Quitar 0b para quedarnos solo con el valor en binario=>Rellenar con 0.....
		channel="{0:b}".format(randrange(18)+1).zfill(5)

		channel=randrange(18)+1
		byte1=64+channel 

		randNorm=-1
		while randNorm >= 2**12 or randNorm < 0:
			#2^11 porque tenemos 12 bits.. Media=2048, Std=500
			randNorm=np.random.normal(2**11,500);
		#Redondear=>Pasar a entero=>Pasar a binario, el formato es 0bxxVALUExx=>Quitar Ob para quedrnos solo con el valor en binario=>Rellenar con 0....
		valueBin="{0:b}".format(int(round(randNorm))).zfill(12)

		byte2=0b10000000|int(valueBin[5:],2)

		byte3=0b10100000|int(valueBin[:5],2)

		sys.stdout.write(bytearray([byte1,byte2,byte3]))
