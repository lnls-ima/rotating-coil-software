#####Testando a versão PUC_2v6#####

import PUC_2v6
import sys
import time
import serial
import numpy as np
import math
import matplotlib.pyplot as plt

p=PUC_2v6.SerialCom(8)

print(p.Conectar(7))
print('Estado:', p.P.sync.getState())
print ('D/As:', p.P.das)
print('A/Ds:', p.P.ads)
       

def EscritaDA():
    num = int(input('Entre com a valor a ser escrito no D/A: '))
    if num > 10:
        mum = 10
    elif num < 1:
        num = 1
    conta = 0
    print('*Entre com a  opção que deseja para a iteração*')
    option = int(input('1 = p.DA.write ; 2 = p.WriteDA: '))
    if option == 1:
        print('----------------------------------------------------------')
        if num != 0:
            for i in range(num):
                conta = conta + 1
                time.sleep(1.5)
                p.DA.write(i)
                leituraAD = p.AD.read()
                leituraDA = p.DA.read()
                print(str(conta)+' Write D/A:', leituraDA, ' |  Read A/D: ', leituraAD)
        else:
            print('Invalid Number')
            return 
    else:
        print('----------------------------------------------------------')
        if num != 0:
            for i in range (num):
                conta = conta + 1
                time.sleep(1.5)
                p.WriteDA(i)
                leituraAD = p.ReadAD()
                leituraDA = p.ReadDA()
                print(str(conta)+' Write D/A:', leituraDA, ' |  Read A/D: ', leituraAD)
        else:
            print('Invalid Number')
            return

def Rampa_AD_DA(fim,inicio=''):

    if inicio == '':
        inicio = round(p.ReadDA(),2)
    if inicio > 10: inicio = 10
    elif inicio < -10: inicio = -10
    if fim > 10: fim = 10
    elif fim < -10: fim = -10

    step = 0.1
    tempo = 0.25
    print(inicio, fim)
    
    if fim > inicio:
        faixa = np.arange(inicio+step,fim+step,step)
    else:
        faixa = np.arange(fim+step,inicio+step,step)
        faixa = faixa[::-1]
    faixa[-1] = fim
    print(faixa)
    for i in faixa:
        print(i)
        time.sleep(tempo)
        p.WriteDA(i)
##    p.WriteDA(0)

#Gerando a forma senoidal para a curva:
def norm(c):
    return [max(min(p, 10.0),-10.0) for p in c]

def genSinusoid(phase=0, off=0):

    # Data
    nPoints = int(input('Nº of points: '))
    if nPoints > 65536:
        nPoints = 65536
        print('Points adjusted to 65536')
    divisor = int(input('Divisor: '))
    Vpp = float(input('Vpp: '))
    freq = float(input('Signal freq (Hz): '))
    IN = int(input('Entrada: '))
    OUT = int(input('Saída: '))
    Precision = int(input('Precisão: 1 = 18bits ou 0 = 16bits: '))
    if nPoints > 32768 and Precision == 1:
        print('Precision selected invalid')
        return False
    clk = int(input('Fonte de clock: 0: Interno ou 1: Externo: '))
            
    # Create Sinusoidal Signal
    realFreq = 60e3/(1+divisor)
    A = Vpp/2.0
    Phi = phase*math.radians(phase)
    w = 2*math.pi*freq/realFreq
    f = lambda x: off+A*math.sin(w*x+Phi)
    pts = norm([f(x) for x in range(nPoints)])

    # completa o restante com 0 (CheckSum)
##    if Precision == 0:
##        remaining = 65536 - pts
##    else:
##        remaining = 32768 - pts
##    if remaining > 0:
##        fim = pts[0]
##        pts = pts + [fim]*remaining
    
    pktCSum = p.CreateChecksum(pts,bool(Precision))

    #Envia os pontos para a PUC
    ck=p.SendCurve(pts, bool(Precision))   
    print('Pontos enviados para PUC')
    print ('CheckSum calculado: ',pktCSum)
    print ('CheckSum recebido:  ',ck)
    
    #Cria arquivo .txt de saída
    NomeArq = str('Teste de saída senoidal')       
    f=open(NomeArq+'.txt','w') 
    for i in range(len(pts)):
        data = str(pts[i])+'\n'
        f.write(data)        
    f.close()
    return True

def Executar(points, CLK_IN_EXT, CLK_OUT, Flash, RAM, Dout_bit, Loop, Precision, divisor, pfim, Bit_pfim):
    print('Executando')    
    p.ExecuteCurve(points, CLK_IN_EXT, CLK_OUT, Flash, RAM, Dout_bit, Loop, Precision, divisor, pfim, Bit_pfim)

def Monitorar_Curva():
    a=0
    while a==0:
        j=p.ReadDigOut()
        if j>0:
            a=1
    print('Finalizado')

def Pausar():
    p.PauseCurve()

def Parar():
    p.StopCurve()


   
   
