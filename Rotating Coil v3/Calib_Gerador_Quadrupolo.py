import numpy
import time
import Agilent_34401A_Serial as Multimetro
import Agilent_33220A as Gerador


mult = Multimetro.SerialCom(15)
mult.Conectar()
gerad = Gerador.GPIB()
gerad.Conectar(19)


def Config_Gerador_DC():
    try:
        # Configuração do gerador Agilent 33220A
        gerad.Enviar('SYSTEM:REMOTE')
        gerad.Enviar('OUTPUT OFF')
        gerad.Enviar('OUTPut:LOAD INFinity')
        gerad.Enviar('APPLY:DC')
        gerad.Enviar('OUTPUT OFF')
        gerad.Enviar('VOLT:OFFS 10')
        gerad.Enviar('VOLT:RANG:AUTO OFF')
        gerad.Enviar('VOLT:OFFS 0')
        gerad.Enviar('OUTPUT ON')
        return True
    except:
        return False

def DC_Saida(tensao):
    try:
        gerad.Enviar('OUTPUT ON')
        gerad.Enviar('VOLT:OFFS '+str(tensao)+'')
        return True
    except:
        return False

def Ler():
    resp = mult.Ler_Volt()
    return resp

def Calibrar():
    ## DCCT 150A - 10V.
####    dados = []
    repeticao = 3
    f_saida = 15
    Max = 8
    Min = (-Max)
    Config_Gerador_DC()
    DC_Saida(0)
    rampa_descida = numpy.arange(Min,0,.5/f_saida)
    rampa_descida = rampa_descida[::-1]
    
####    rampa = rampa.tolist()
####    rampa.append(-8)
####    rampa = numpy.asarray(rampa)
    
    for i in range(len(rampa_descida)):
        DC_Saida(rampa_descida[i])
        time.sleep(.25)
        
    rampa_reta = numpy.arange(Min,(Max + 0.5/f_saida),.5/f_saida)
    dados = numpy.zeros(len(rampa_reta)*repeticao).reshape(len(rampa_reta),repeticao)
    
    for j in range(repeticao):
        print(j)
        for i in range(len(rampa_reta)):
            DC_Saida(rampa_reta[i])
            time.sleep(.5)
####            dados.append(Ler())
            dados[i][j]=Ler()
            time.sleep(.5)
        if j == repeticao-1:
            rampa_descida = numpy.arange(0,(Max + 0.5/f_saida),.5/f_saida)
            rampa_descida = rampa_descida[::-1]
        else:
            rampa_descida = numpy.arange(Min,(Max + 0.5/f_saida),.5/f_saida)
            rampa_descida = rampa_descida[::-1]
        for i in range(len(rampa_descida)):
            DC_Saida(rampa_descida[i])
            time.sleep(.25)
        time.sleep(1)
        

    media_dados = numpy.mean(dados,axis=1)
    reta = numpy.polyfit(rampa_reta,media_dados,10)
    reta = reta.tolist()
    reta.reverse()
    reta = numpy.asarray(reta)
    
####    print(reta)
    return(reta)

def Salvar(dados):
    arquivo = ('Dados_Reta_Gerador.dat')
    f = open(arquivo,'w')
    f.write(str(dados))
    f.close()
    print('Processo Finalizado...')
##    print('')
























        
    
