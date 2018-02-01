# -*- coding: utf-8 -*-
"""
Created on 04/10/2013
Update on 23/11/2017
Versão 1.0
@author: James Citadini
"""
# Import
import time
import visa

# ******************************************
# GPIB
class GPIB(object):
    def __init__(self):
        self.commands()

    def commands(self):
        self.ReadVolt = ':READ?'
        self.Reset = '*RST'
        self.Clean = '*CLS'
        self.ConfigVolt = ':CONF:VOLT:DC AUTO'
        
    def connect(self,address):
        try:
            aux = 'GPIB0::'+str(address)+'::INSTR'
            rm = visa.ResourceManager()
            self.inst = rm.open_resource(aux.encode('utf-8'))
            self.inst.timeout = 5
            return True
        except:
            return False

    def send(self,command):
        try:
            self.inst.write(command)
            return True
        except:
            return False

    def read(self):
        try:
            reading = self.inst.read()
        except:
            reading = ''
        return reading

    def config(self):
        try:
            self.send(self.Clean)
            self.send(self.Reset)
            self.send(self.ConfigVolt)
            return True
        except:
            return False

    def collect(self):
        try:
            self.send(self.ReadVolt)
            time.sleep(0.4)
            dado = self.read()
            return dado
        except:
            dado = ''
            return dado
        
