##import Display_Heidenhain as Disp
##import Controle_GPIB
##import PUC_2v5
##x=Controle_GPIB.Controle()

##dev = Disp.SerialCom(4)
##
##dev.Conectar()

import numpy
import matplotlib.pyplot as plt


f = open('pontos_integrador_1.txt','r')
ponto_int = f.read().strip()
f.close()
ponto_int = ponto_int.split('\n')

##for i in range(len(ponto_int)):
##    ponto_int[i] = float(ponto_int[i])
##ponto_int = numpy.array(ponto_int)

ponto_int = numpy.array(ponto_int)
ponto_int = ponto_int.astype(float)

##resp=[]
##resp.append(abs(ponto_int.max()));resp.append(abs(ponto_int.min()))
##resp=numpy.array(resp)
##valor = resp.max()
##for i in range(len(ponto_int)):
##    ponto_int[i]=ponto_int[i]/valor


y = numpy.linspace(0,len(ponto_int)*20,len(ponto_int))

for i in range(len(y)):
    y[i] = y[i]/1000

plt.plot(y,ponto_int)
##plt.show()


f = open('pontos_puc_1.txt','r')
ponto_puc = f.read().strip()
f.close()
ponto_puc = ponto_puc.split('\n')

ponto_puc = numpy.array(ponto_puc)
ponto_puc = ponto_puc.astype(float)

for i in range(len(ponto_puc)):
    ponto_puc[i]=(ponto_puc[i])
##
##resp=[]
##resp.append(abs(ponto_puc.max()));resp.append(abs(ponto_puc.min()))
##resp=numpy.array(resp)
##valor = resp.max()
##for i in range(len(ponto_puc)):
##    ponto_puc[i]=ponto_puc[i]/valor


y = numpy.linspace(0,len(ponto_puc),len(ponto_puc))

for i in range(len(y)):
    y[i] = y[i]/4000
##    y[i] = y[i]/9000

plt.plot(y,ponto_puc)

plt.show()
