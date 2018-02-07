import numpy
import matplotlib.pyplot as plt


def teste(Tipo_Equacao,Amp,freq,total_ciclo,P_Final=0,fase=0):
    Pontos_Puc = 32768

    if P_Final != 0 or fase != 0:
        Divisor_Puc = int((60e3)/((Pontos_Puc*freq)/(total_ciclo+1)))
    else:
        Divisor_Puc = int((60e3)/((Pontos_Puc*freq)/total_ciclo))

    print(Divisor_Puc)
    Phi = numpy.radians(fase)
    offset = 0
    Amp = Amp/2
    freq_puc = 60e3/(Divisor_Puc+1)
    w = (2*numpy.pi*freq/freq_puc)       


    if Tipo_Equacao == 0:  ## Equacao Ciclagem senoidal com defasagem
        f = lambda y: Amp*numpy.sin(w*y+Phi)+offset
        pontos = [max(min(p, 10.0),-10.0) for p in ([f(y) for y in range(Pontos_Puc)])]

    if Tipo_Equacao == 1:
        pontos=numpy.zeros(Pontos_Puc)
        dados = list(map(lambda x: (x/freq_puc),range(Pontos_Puc)))
        for i in range(len(dados)):
            pontos[i] = ((Amp*numpy.sin(w*freq_puc*dados[i]))*(numpy.exp(-((dados[i])/12))))
        pontos=pontos.tolist()

    if P_Final != 0 or fase != 0:
        Ciclos_Puc = (Pontos_Puc/(Pontos_Puc/((60e3/(Divisor_Puc+1))/freq))) * (total_ciclo + 1)
        ponto_ciclo = Ciclos_Puc/(total_ciclo+1)
        ponto_final = (ponto_ciclo*(abs(P_Final-fase)))/360
        Ciclos_Puc = (Ciclos_Puc + ponto_final)-ponto_ciclo
        Ciclos_Puc = int(round(Ciclos_Puc,0))
    else:
        Ciclos_Puc = (Pontos_Puc/(Pontos_Puc/((60e3/(Divisor_Puc+1))/freq))) * total_ciclo
        Ciclos_Puc = int(round(Ciclos_Puc,0))

    print(Ciclos_Puc)
    pontos = pontos[:Ciclos_Puc]
    plt.plot(pontos)
    plt.show()
    
