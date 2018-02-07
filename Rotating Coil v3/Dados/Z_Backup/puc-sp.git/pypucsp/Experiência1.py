#####Testando a versão PUC_2v6#####

import PUC_2v6
import sys
import time
import serial
import numpy as np
import math
import matplotlib.pyplot as plt

p=PUC_2v6.Serial_PUC()

print(str(p))
p.Conectar("COM4", 6e6, 8)

print('Estado:', p.P.sync.getState())
print ('D/As:', p.P.das)
print('A/Ds:', p.P.ads)


def EscritaDA():
    num = int(input('Entre com a valor a ser escrito no D/A: '))
    conta =0
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
    p.WriteDA(0)

##def gera_curva_senoidal(Amp,nPontos,offset=0):
### gera a curva em 4 bytes e complemento de 2
##    
##    # Número de pontos da flash DA
##    flashPoints = 32768
##    nCiclos = int((flashPoints-int(nPontos/4))/nPontos)
##    Amp = Amp/2
##
##    # gera a lista de pontos
##    w=(2*math.pi)/nPontos
##    periodo = list(map(lambda x: Amp*math.sin(w*x+3*math.pi/2)+offset,range(nPontos)))
##    listaPontos = periodo[int(3*nPontos/4):]
##    listaPontos = listaPontos + periodo * nCiclos
##
##    # completa o restante com 0
##    remaining = flashPoints - len(listaPontos)
##    fim = periodo[0]
##    if remaining > 0:
##        listaPontos = listaPontos + [fim]*remaining
##
##    # converte para complemento de 2 com 4 bytes
##    curva = p.ConverteCurva(listaPontos)
##
##    # calcula o checksum da curva gerada
##    checksum = p.CalculateGeneratedCsum(curva)
##    return curva, checksum, listaPontos
##
##def gera_curva_senoidal2(Amp,nPontos,offset=0):
### gera a curva em 4 bytes e complemento de 2
##    
##    # Número de pontos da flash DA
##    flashPoints = 32768
##    nCiclos = int(flashPoints/nPontos)
##    Amp = Amp/2
##
##    # gera a lista de pontos
##    w=(2*math.pi)/nPontos
##    periodo = list(map(lambda x: Amp*math.sin(w*x+3*math.pi/2)+offset,range(nPontos)))
##    listaPontos = periodo * nCiclos
##
##    # completa o restante com 0
##    remaining = flashPoints - len(listaPontos)
##    fim = periodo[0]
##    if remaining > 0:
##        listaPontos = listaPontos + [fim]*remaining
##
##    # converte para complemento de 2 com 4 bytes
##    curva = p.ConverteCurva(listaPontos)
##
##    # calcula o checksum da curva gerada
##    checksum = p.CalculateGeneratedCsum(curva)
##    return curva, checksum, listaPontos
##
##    
    


