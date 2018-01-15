# -*- coding: utf-8 -*-
"""
Created on 04/10/2013
Update on 23/11/2017
Versão 2.0
@author: James Citadini
"""
# Importa bibliotecas
import time
import visa

# ******************************************
# Comunicacao GPIB
class GPIB(object):
    def __init__(self):
        self.commands()
        
    def commands(self):
        self.LerVolt =              ':READ?'
        self.Acesso =               ':SYST:REM'
        self.Liberar =              ':SYST:LOC'
        self.Reset =                '*RST'
        self.Limpar =               '*CLS'
        self.SCAN =                 ':ROUT:SCAN '        # acrescentar no final o canal que deseja scanear, exemplo: 'ROUT:SCAN (@101)'
        self.MON =                  ':ROUT:MON:CHAN '    # acrescentar no final o canal que deseja APENAS monitorar no display, exemplo: 'ROUT:MON:CHAN (@102)'
        self.MON_STATE =            ':ROUT:MON:STATE ON'
        self.ConfgVolt =            ':CONF:VOLT:DC'
        self.CON =                  ':CONF'
        self.Volt =                 ':VOLT'
        self.DC =                   ':DC'

##        self.ConfiguraVolt = [':ROUT:SCAN (@101)',\
##                              ':CONF:TEMP TC,K,(@101)',\
##                              'ROUT:MON:STATE ON']
        
    def connect(self,address):
        try:
            aux = 'GPIB0::'+str(address)+'::INSTR'
            rm = visa.ResourceManager()
            self.inst = rm.open_resource(aux.encode('utf-8'))
            self.inst.timeout = 1
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
            leitura = self.inst.read()
        except:
            leitura = ''

        return leitura

    def config(self):
        try:
            self.send(self.Limpar)
            self.send(self.Reset)
            self.send(self.ConfiguraVolt)
            return True
        except:
            return False

    def collect(self):
        try:
            self.send(self.LerVolt)
            dado = self.read()
            return dado
        except:
            dado = ''
            return dado

    def read_temp(self):
        self.send(self.LerVolt)
        time.sleep(.5)
        resp = self.read(15)
        return resp
       
    def scan(self,canal):               
        try:
            string = str(canal)
            value = self.SCAN + '(@10'+string+')'
            self.send(value)
            return True
        except:
            return False

    def monitor(self, canal):
        try:
            string = str(canal)
            value = self.MON + '(@10'+string+')'
            self.send(value)
            return True
        except:
            return False

    
