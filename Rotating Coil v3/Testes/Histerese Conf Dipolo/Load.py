import numpy as np
import os
from os import listdir
import time
import matplotlib

correntes = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,\
             65,60,55,50,45,40,35,30,25,20,15,10,5,0,\
             -5,-10,-15,-20,-25,-30,-35,-40,-45,-50,-55,-60,-65,-70,\
             -65,-60,-55,-50,-45,-40,-35,-30,-25,-20,-15,-10,-5,0]

##diretorio = 'D:\\ARQ\\Work_at_LNLS\\Ima\\WEG - Sirius\\Histerese Conf Dipolo\\'

diretorio = 'C:\\Users\\labimas\\Desktop\\Bobina Girante\\Alterados\\bobinona\\Testes\\Histerese Conf Dipolo\\01_medida\\'
             

lista = listdir(diretorio)

for i in range(len(lista)):
	lista[i] = diretorio + lista[i]
	
lista.sort(key=lambda x:os.path.getmtime(x))

data = np.array([])

for i in range(len(lista)):
  f = open(lista[i])
  for j in range(40):
    f.readline()

  tmp = f.readline() # Harm 1 - Ignora
  tmp = f.readline() # Harm 2
  tmp = f.readline() # Harm 3

  tmp = tmp.split('   \t  ')

  data = np.append(data,'{0:0.1f}\t{1:0.8e}\t{2:0.8e}\t{3:0.8e}\t{4:0.8e}'.format(correntes[i],float(tmp[1]),float(tmp[2]),float(tmp[3]),float(tmp[4])))
