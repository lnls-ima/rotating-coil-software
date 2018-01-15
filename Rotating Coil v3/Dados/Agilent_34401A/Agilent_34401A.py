# -*- coding: utf-8 -*-
"""
Created on 08/02/2013
Versão 1.0
@author: James Citadini
"""
# Importa bibliotecas
import serial
import time
import threading
# ******************************************

class SerialCom(threading.Thread):
    def __init__(self,porta):
        threading.Thread.__init__(self)
        self.porta = porta
        self.ser = serial.Serial(self.porta-1)
        self.start()

    def callback(self):
        self._stop()

    def run(self):
        self.Comandos()
        
    def Comandos(self):
        CR = '\r'

        self.LerVolt = ':READ?'
        self.Acesso = ':SYST:REM'
        self.Reset = '*RST'
        self.Limpar = '*CLS'
        # Conf 0.02, 0.2, 1, 10, 100 PLC
        self.ConfiguraVolt = ['CONF:VOLT:DC 10,0.001',\
                              'CONF:VOLT:DC 10,0.0001',\
                              'CONF:VOLT:DC 10,0.00003',\
                              'CONF:VOLT:DC 10,0.00001',\
                              'CONF:VOLT:DC 10,0.000003']

        self.Delays = {'0.02':25,\
                       '0.2':30,\
                       '1':60,\
                       '10':400,\
                       '100':3400}
        
    def Conectar(self):       
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = 0.01
        if not self.ser.isOpen():
            self.ser.open(
            
    def Desconectar(self):
        self.ser.close()
        
    def LimpaTxRx(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def Enviar(self,comando):
        self.LimpaTxRx()
        ajuste = comando + '\r\n'
        self.ser.write(ajuste.encode('utf-8'))

    def Ler(self,n):
        try:
            leitura = self.ser.read(n)
            leitura = leitura.decode('utf-8')
            leitura = leitura.replace('\r\n','')
        except:
            leitura = ''

        return leitura
