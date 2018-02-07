# -*- coding: utf-8 -*-

# Importa bibliotecas
import Agilent_33220A
import Agilent_34401A
import threading
import ctypes
import numpy
import time
import sys


# ******************************************


class Biblioteca(object):
    def __init__(self):
        self.Gerador = 0
        self.Gerador_Status = 0
        self.Gerador_Config = 0
        self.Multimetro = 0
        self.Multimetro_Status = 0
        self.Multimetro_Config = 0
        self.dados = 0
        
        

lib = Biblioteca()
lib.Gerador = Agilent_33220A.GPIB()
lib.Multimetro = Agilent_34401A.GPIB()



class Controle(object):
    def __init__(self):
        try:
            self.Comandos()            
        except:
            return None

    def Comandos(self):
        pass

    def Conectar_Multimetro(self,endereco=18):
        try:
            lib.Multimetro_Status = lib.Multimetro.Conectar(endereco)
            time.sleep(1)
            return lib.Multimetro_Status
        except:
            return False

    def Conectar_Gerador(self,endereco=19):
        try:
            lib.Gerador_Status = lib.Gerador.Conectar(endereco)
            time.sleep(1)
            return lib.Gerador_Status
        except:
            return False

    def Saida_Gerador(self,status):
        if lib.Gerador_Status == True:
            if status == 1:
                lib.Gerador.Enviar('OUTPUT ON')
                return True
            else:
                lib.Gerador.Enviar('OUTPUT OFF')
                return True
        else:
            return False

    def Config_Gerador_DC(self):
        if lib.Gerador_Status == True:
            try:
                # Configuração do voltímetro Agilent 33220A
                lib.Gerador.Enviar('SYSTEM:REMOTE')
                lib.Gerador.Enviar('OUTPUT OFF')
                lib.Gerador.Enviar('OUTPut:LOAD INFinity')
                lib.Gerador.Enviar('APPLY:DC')
                lib.Gerador.Enviar('OUTPUT OFF')
                lib.Gerador.Enviar('VOLT:OFFS 10')
                lib.Gerador.Enviar('VOLT:RANG:AUTO OFF')
                lib.Gerador.Enviar('VOLT:OFFS 0')            
                return True
            except:
                return False
        else:
            return False

    def DC_Saida(self,tensao):
        if lib.Gerador_Status == True:
            try:
                lib.Gerador.Enviar('OUTPUT ON')
                lib.Gerador.Enviar('VOLT:OFFS '+str(tensao)+'')
                return True
            except:
                return False
        else:
            return False

    def Config_Gerador_Ciclagem(self,Frequencia):
        if lib.Gerador_Status == True:
            pontos=self.Pontos()
            pontos=str(pontos)
            dados=pontos[1:-1]
            try:
                # Configuração do gerador Agilent 33220A
                lib.Gerador.Enviar('SYSTEM:REMOTE')
                lib.Gerador.Enviar('OUTPUT OFF')
                lib.Gerador.Enviar('APPLY:DC 0,0,0')
                lib.Gerador.Enviar('OUTPut:LOAD INFinity')
                lib.Gerador.Enviar('OUTPUT ON')
                lib.Gerador.Enviar('DATA VOLATILE, ' + str(dados))
                lib.Gerador.Enviar('FUNC:USER VOLATILE')
                lib.Gerador.Enviar('APPLY:USER ' + str(Frequencia) + ', 20, 0')
                return True
            except:
                return False
        else:
            return False

    def Config_Gerador_Ciclagem_Quadrupolo(self,Frequencia,pontos):
        if lib.Gerador_Status == True:
            pontos=str(pontos)
            dados=pontos[1:-1]
            try:
                # Configuração do gerador Agilent 33220A
                lib.Gerador.Enviar('SYSTEM:REMOTE')
                lib.Gerador.Enviar('OUTPUT OFF')
                lib.Gerador.Enviar('APPLY:DC 0,0,0')
                lib.Gerador.Enviar('OUTPut:LOAD INFinity')
                lib.Gerador.Enviar('OUTPUT ON')
                lib.Gerador.Enviar('DATA VOLATILE, ' + str(dados))
                lib.Gerador.Enviar('FUNC:USER VOLATILE')
                lib.Gerador.Enviar('APPLY:USER ' + str(Frequencia) + ', 20, 0')
                return True
            except:
                return False
        else:
            return False

    def Pontos(self,Freq=.5):
        pontofinal=0
        total=25000
        pontos=numpy.zeros(total)
        dados = list(map(lambda x: (x*0.0032),range(total)))
        for i in range(len(dados)):
            pontos[i]=round((numpy.sin(2*numpy.pi*Freq*dados[i]))*(numpy.exp(-(dados[i]/12))),3)

        pontofinal=pontos.tolist()
        return pontofinal

    def Config_Multimetro(self):
        if lib.Multimetro_Status == True:
            try:
                lib.Multimetro.Config()
                return True
            except:
                return False
        else:
            return False

    def Coleta_Multimetro(self):
        if lib.Multimetro_Status == True:
            try:
                date=lib.Multimetro.Coleta()
                return date
            except:
                return False
        else:
            return False
    
cont = Controle()


def start():
    cont.Conectar_Gerador()
    cont.Conectar_Multimetro()

