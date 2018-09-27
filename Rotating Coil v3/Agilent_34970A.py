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
        self.Read_Val = ':READ?'
        self.Remote = ':SYST:REM'
        self.Local = ':SYST:LOC'
        self.Reset = '*RST'
        self.Clear = '*CLS'
        # acrescentar no final o channel que deseja scanear
        # exemplo: 'ROUT:SCAN (@101)'
        self.SCAN = ':ROUT:SCAN'
        # acrescentar no final o channel que deseja APENAS monitorar no
        # display, exemplo: 'ROUT:MON:CHAN (@102)'
        self.MON = ':ROUT:MON:CHAN '
        self.MON_STATE = ':ROUT:MON:STATE ON'
        self.ConfgVolt = ':CONF:VOLT:DC'
        self.CON = ':CONF'
        self.Volt = ':VOLT'
        self.DC = ':DC'
        self.Conf_Temp = ':CONF:TEMP FRTD,85,'
        self.Conf_Volt = ':CONF:VOLT:DC'
        self.ConfiguraVolt = [':ROUT:SCAN ',
                              ':CONF:VOLT:DC',
                              ':CONF:TEMP FRTD,85,',
                              ':ROUT:MON:STATE ON']

    def connect(self, address):
        try:
            aux = 'GPIB0::'+str(address)+'::INSTR'
            rm = visa.ResourceManager()
            self.inst = rm.open_resource(aux.encode('utf-8'))
            self.inst.timeout = 5
            return True
        except:
            return False

    def disconnect(self):
        try:
            self.inst.close()
            return True
        except:
            return False

    def send(self, command):
        try:
            self.inst.write(command)
            return True
        except:
            return False

    def read(self):
        try:
            _ans = self.inst.read()
        except:
            _ans = ''

        return _ans

    def config(self):
        try:
            self.send(self.Clear)
            self.send(self.Reset)
            self.send(self.ConfiguraVolt)
            return True
        except:
            return False

    def config_temp_volt(self):
        try:
            self.send(self.Clear)
            self.send(self.Reset)
            _cmd = ':CONF:TEMP FRTD,85, (@101:103); VOLT:DC (@104:105);'
            self.send(_cmd)
            time.sleep(0.3)
            _cmd = ':ROUT:SCAN (@101:105)'
            self.send(_cmd)
            return True
        except:
            return False

    def read_temp_volt(self, wait=0.5):
        self.send(':READ?')
        time.sleep(wait)
        _ans = self.inst.read('\n').split(',')
        for i in range(len(_ans)):
            _ans[i] = float(_ans[i])
        return _ans

    def config_temp(self, channel=101):
        try:
            self.send(self.Clear)
            self.send(self.Reset)
            _cmd = (self.Conf_Temp + ' (@' + str(channel) + '); ' +
                    self.SCAN + ' (@' + str(channel) + ')')
            self.send(_cmd)
            return True
        except:
            return False

#     def config_volt(self, channels=[105,106]):
#         try:
#             self.send(self.Clear)
#             self.send(self.Reset)
#             _cmd = self.Conf_Temp + ' (@'
#             _cmd2 = ''
#             for i in channels:
#                 _cmd_2 = _cmd_2 + str(i) + ', '
#             _cmd = _cmd + _cmd_2 + ')'
#             self.send(_cmd)
#             self.send(self.SCAN + ' (@' + _cmd_2 + ')')
#             return True
#         except:
#             return False
    def config_volt(self, channel=105):
        try:
            self.send(self.Clear)
            self.send(self.Reset)
            _cmd = (self.Conf_Volt + ' (@' + str(channel) + '); ' +
                    self.SCAN + ' (@' + str(channel) + ')')
            self.send(_cmd)
            return True
        except:
            return False

    def collect(self):
        try:
            self.send(self.Read_Val)
            _data = self.read()
            return _data
        except:
            _data = ''
            return _data

    def read_val(self):
        self.send(self.Read_Val)
        time.sleep(0.85)
        _ans = self.read()
        return _ans

    def scan(self, channel):
        try:
            string = str(channel)
            value = self.SCAN + '(@10'+string+')'
            self.send(value)
            return True
        except:
            return False

    def monitor(self, channel):
        try:
            string = str(channel)
            value = self.MON + '(@10'+string+')'
            self.send(value)
            return True
        except:
            return False
