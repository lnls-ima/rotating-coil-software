# -*- coding: utf-8 -*-
"""
Created on 28/08/2012
Modified on 22/11/2017
Versão 1.0
@author: James Citadini
"""
# Importa bibliotecas
import time
import serial
# ******************************************

class SerialCom(object):
    def __init__(self,port,model='ND-760'):
        self.port = 'COM' + str(port)
        self.model = model
        self.ser = serial.Serial(self.port)
        self.commands()

    def commands(self):
        self.Converte_metros_mm   = 1000 #

        self.Zero0      = '\x1bT0000\r' # {Tecla 0}
        self.One1       = '\x1bT0001\r' # {Tecla 1}
        self.Two2       = '\x1bT0002\r' # {Tecla 2}
        self.Three3     = '\x1bT0003\r' # {Tecla 3}
        self.Four4      = '\x1bT0004\r' # {Tecla 4}
        self.Five5      = '\x1bT0005\r' # {Tecla 5}
        self.Six6       = '\x1bT0006\r' # {Tecla 6}
        self.Seven7     = '\x1bT0007\r' # {Tecla 7}
        self.Eight8     = '\x1bT0008\r' # {Tecla 8}
        self.Nine9      = '\x1bT0009\r' # {Tecla 9}
        self.CL         = '\x1bT0100\r' # {Tecla CL}
        self.Minus      = '\x1bT0101\r' # {Tecla -}
        self.Point      = '\x1bT0102\r' # {Tecla .}
        self.Ent        = '\x1bT0104\r' # {Tecla Ent}
        self.Axis12     = '\x1bT0107\r' # {Tecla 1/2}
        self.AxisX      = '\x1bT0109\r' # {Tecla X}
        self.AxisY      = '\x1bT0110\r' # {Tecla Y}
        self.AxisZ      = '\x1bT0111\r' # {Tecla Z}
        self.Spec       = '\x1bT0129\r' # {Tecla Spec Fct}
        self.Rpn        = '\x1bT0142\r' # {Tecla R+/-}

        self.CEZero0    = '\x1bT1000\r' # {Tecla CE+0}
        self.CEOne1     = '\x1bT1001\r' # {Tecla CE+1}
        self.CETwo2     = '\x1bT1002\r' # {Tecla CE+2}
        self.CEThree3   = '\x1bT1003\r' # {Tecla CE+3}
        self.CEFour4    = '\x1bT1004\r' # {Tecla CE+4}
        self.CEFive5    = '\x1bT1005\r' # {Tecla CE+5}
        self.CESix6     = '\x1bT1006\r' # {Tecla CE+6}
        self.CESeven7   = '\x1bT1007\r' # {Tecla CE+7}
        self.CEEight8   = '\x1bT1008\r' # {Tecla CE+8}
        self.CENine9    = '\x1bT1009\r' # {Tecla CE+9}

        self.Out_Model  = '\x1bA0000\r' # {Output of model designation}
        self.Segm       = '\x1bA0100\r' # {Output of 14-segment display}
        self.Value      = '\x1bA0200\r' # {Output of current value}
        self.Error      = '\x1bA0301\r' # {Output of error text}
        self.Soft       = '\x1bA0400\r' # {Output of software number}
        self.Ind        = '\x1bA0900\r' # {Output of indicators}

        self.Resetcounter = '\x1bS0000\r' # {Counter RESET}
        self.Lock       = '\x1bS0001\r' # {Lock keyboard}
        self.Unlock     = '\x1bS0002\r' # {Unlock keyboard}

        # Variável de reading
        self.DisplayPos = (0,0,0)
#         self.X = 0
#         self.Y = 0
#         self.Z = 0
#         self.Volume = 0

    def connect(self,baudrate=9600,timeout=0.5):
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.SEVENBITS
        self.ser.stopbits = serial.STOPBITS_TWO
        self.ser.parity = serial.PARITY_EVEN
        self.ser.timeout = timeout
        if not self.ser.isOpen():
            self.ser.open()

    def disconnect(self):
        self.ser.close()

    def fushTxRx(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def write_display_value(self,axis,value):
        # Converte para string
        aux = str(abs(value))
        nchar = len(aux)

        self.fushTxRx()
        time.sleep(0.2)
        self.ser.write(self.CL.encode('utf-8'))
        time.sleep(0.2)

        if axis == 0:
            self.ser.write(self.AxisX.encode('utf-8'))
        elif axis == 1:
            self.ser.write(self.AxisY.encode('utf-8'))
        elif axis == 2:
            self.ser.write(self.AxisZ.encode('utf-8'))

        time.sleep(0.2)

        # Identifica e escreve
        for i in range(nchar):
            self.fushTxRx()
            tmp = aux[i]
            if (tmp == '0'):
                adjust = self.Zero0
            elif (tmp == '1'):
                adjust = self.One1
            elif (tmp == '2'):
                adjust = self.Two2
            elif (tmp == '3'):
                adjust = self.Three3
            elif (tmp == '4'):
                adjust = self.Four4
            elif (tmp == '5'):
                adjust = self.Five5
            elif (tmp == '6'):
                adjust = self.Six6
            elif (tmp == '7'):
                adjust = self.Seven7
            elif (tmp == '8'):
                adjust = self.Eight8
            elif (tmp == '9'):
                adjust = self.Nine9
            elif (tmp == '.'):
                adjust = self.Point
            self.ser.write(adjust.encode('utf-8'))
            time.sleep(0.2)

        if value < 0:
            self.ser.write(self.Minus.encode('utf-8'))
            time.sleep(0.2)

        # Enter
        self.ser.write(self.Ent.encode('utf-8'))

    def send_key(self,key):
        try:
            self.ser.write(key.encode('utf-8'))
            time.sleep(0.1)
            reading = self.ser.read(60)
            return reading
        except:
            return False

    def readdisplay(self):
        if self.model == 'ND-760':
            self.readdisplay_ND760()
        else:
            self.readdisplay_ND780()            
            
    def readdisplay_ND760(self):
        try:
            adjust = self.Value
            self.fushTxRx()
            self.ser.write(adjust.encode('utf-8'))
            time.sleep(0.1)
            reading = str(self.ser.read(40))

            #Converte para string e limpa lixo
            reading = self.cleanstring(reading)

            #Converte para float
            p1 = reading.find('rn')
            reading1 = float(reading[p1-10:p1])/1000
            reading = reading[p1+1:]

            p2 = reading.find('rn')
            reading2 = float(reading[p2-10:p2])/1000
            reading = reading[p2+1:]

            p3 = reading.find('rn')
            reading3 = float(reading[p3-10:p3])/1000
        except:
            reading1 = 0
            reading2 = 0
            reading3 = 0

        self.DisplayPos = (reading1,reading2,reading3)
        
    def readdisplay_ND780(self):
        try:
            adjust = self.Value
            self.fushTxRx()
            self.ser.write(adjust.encode('utf-8'))
            time.sleep(0.1)
            reading = self.ser.read(60)
            
            reading = reading.decode('utf-8')
            aux1 = reading[reading.find('A=')+2:reading.find(' R\r\n')]
            aux1 = aux1.replace(' ','')

            reading = reading[reading.find('R\r\n')+3:]
            aux2 = reading[reading.find('B=')+2:reading.find(' R\r\n')]
            aux2 = aux2.replace(' ','')

            self.X = float(aux1)
            self.Y = float(aux2)
                    
            #Converte para float
            self.DisplayPos = [self.X,self.Y]

            return True
        except:
            return False

    def cleanstring(self,reading):
        reading = reading.replace('\'','')
        reading = reading.replace('\\x82','')
        reading = reading.replace('\\x8d','')
        reading = reading.replace('\\','')
        reading = reading.replace('xb','')
        reading = reading.replace('b','')
        return reading

    def reset_setref(self):
        # Envia comando de reset
        self.fushTxRx()
        time.sleep(0.2)
        self.ser.write(self.Resetcounter.encode('utf-8'))

        # Aguarda 4 segundos o processo de reset to display
        time.sleep(4)

        # Envia enter para buscar referência
        self.fushTxRx()
        time.sleep(0.2)
        self.ser.write(self.Ent.encode('utf-8'))
        time.sleep(0.2)