# -*- coding: utf-8 -*-
"""
Created on 01/07/2013
Update on 23/11/2017
Versão 4.0
@author: James Citadini
"""
# Importa bibliotecas
import time
import visa
# *******************************************

class GPIB(object):
    def __init__(self):
        self.commands()

    def commands(self):
        self.Acesso = 'SYSTEM:REMOTE'
        self.Liberar = 'SYSTEM:LOCAl'
        self.ConfTipo = 'APPLY:PULSE'
        self.Impedancia = 'OUTPut:LOAD INFinity'
        self.SaidaOff = 'OUTPUT OFF'
        self.SaidaOn = 'OUTPUT ON'
        self.SetPeriodo = 'PULSE:PERIOD '
        self.SetLargura = 'PULSE:WIDTH 1e-6'
        self.SetNivelBaixo = 'VOLTAGE:LOW 0'
        self.SetNivelAlto = 'VOLTAGE:HIGH 5'
        self.SetOffset = 'VOLTAGE:OFFSET 2.5'
        self.SetPulseTransition = 'PULSE:TRANSITION 5e-9'            
 
    def connect(self,address):
        try:
            aux = 'GPIB0::'+str(address)+'::INSTR'
            rm = visa.ResourceManager()
            self.inst = rm.open_resource(aux.encode('utf-8'))
            self.inst.timeout = 1
            return True
        except:
            return False
         
    def disconnect(self):
        try:
            self.inst.close()
            return True
        except:
            return False
           
    def send(self,comando):
        try:
            self.inst.write(comando)
            return True
        except:
            return False

    def read(self):
        try:
            tmp = self.inst.read_raw()
            leitura = tmp.split(',')
        except:
            leitura = ''

        return leitura

    def config(self,PeriodoPulso):
        try:
            # Configuração do voltímetro Agilent 33220A
            self.send('SYSTEM:REMOTE')
            self.send('APPLY:PULSE')
            self.send('OUTPut:LOAD INFinity')
            self.send('OUTPUT OFF')
            self.send('PULSE:PERIOD '+ str(PeriodoPulso))
            self.send('PULSE:WIDTH 1e-6')
            self.send('VOLTAGE:LOW 0')
            self.send('VOLTAGE:HIGH 5')
            self.send('VOLTAGE:OFFSET 2.5')
            self.send('PULSE:TRANSITION 5e-9')
            time.sleep(1)
            return True
        except:
            return False

    
