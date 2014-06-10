import sys
import numpy as np
from random import randrange

s=np.random.poisson(300);
level='1'
for y in range(0,(s-1)*18): # ~300 lecturas x18 canales x60min x24hours x1day
	channel=bin(randrange(18)+1)[2:].zfill(5) #Random uniform distribution 1-18=>Quitar 0b para quedarnos solo con el valor en binario=>Rellenar con 0.....

	channel=randrange(18)+1
	byte1=64+channel 
	
	randNorm=np.random.normal(2**11,500); #2^11 porque tenemos 12 bits.. Media=2048, Std=500 		
	valueBin=bin(int(round(randNorm)))[2:].zfill(12) #Redondear=>Pasar a entero=>Pasar a binario, el formato es 0bxxVALUExx=>Quitar Ob para quedrnos solo con el valor en binario=>Rellenar con 0....

	byte2=128+int(valueBin[5:],2)

	byte3=128+32+int(valueBin[:5],2)

	sys.stdout.write(bytearray([byte1,byte2,byte3]))
