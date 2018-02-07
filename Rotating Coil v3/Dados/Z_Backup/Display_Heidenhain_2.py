# -*- coding: utf-8 -*-
"""
Created on 01/07/2013
Versão 2.0
@author: James Citadini
"""
# Importa bibliotecas
import time
import serial
import threading
# ****************************************** ND 780

class SerialCom(object):
    def __init__(self,porta):
        self.porta = porta
        self.ser = serial.Serial(self.porta-1)
        self.Comandos()

    def Comandos(self):
        try:
             #Constantes de comandos da Régua Digital
            self.Converte_metros_mm   = 1000 #

            self.Zero0      = '\x1bT0000\r' # {Tecla 0}
            self.Um1        = '\x1bT0001\r' # {Tecla 1}
            self.Dois2      = '\x1bT0002\r' # {Tecla 2}
            self.Tres3      = '\x1bT0003\r' # {Tecla 3}
            self.Quatro4    = '\x1bT0004\r' # {Tecla 4}
            self.Cinco5     = '\x1bT0005\r' # {Tecla 5}
            self.Seis6      = '\x1bT0006\r' # {Tecla 6}
            self.Sete7      = '\x1bT0007\r' # {Tecla 7}
            self.Oito8      = '\x1bT0008\r' # {Tecla 8}
            self.Nove9      = '\x1bT0009\r' # {Tecla 9}
            self.CL         = '\x1bT0100\r' # {Tecla CL}
            self.Menos      = '\x1bT0101\r' # {Tecla -}
            self.Ponto      = '\x1bT0102\r' # {Tecla .}
            self.Ent        = '\x1bT0104\r' # {Tecla Ent}
            self.Eixo12     = '\x1bT0107\r' # {Tecla 1/2}
            self.EixoX      = '\x1bT0109\r' # {Tecla X}
            self.EixoY      = '\x1bT0110\r' # {Tecla Y}
            self.EixoZ      = '\x1bT0111\r' # {Tecla Z}
            self.Spec       = '\x1bT0129\r' # {Tecla Spec Fct}
            self.Rpn        = '\x1bT0142\r' # {Tecla R+/-}

            self.CEZero0    = '\x1bT1000\r' # {Tecla CE+0}
            self.CEUm1      = '\x1bT1001\r' # {Tecla CE+1}
            self.CEDois2    = '\x1bT1002\r' # {Tecla CE+2}
            self.CETres3    = '\x1bT1003\r' # {Tecla CE+3}
            self.CEQuatro4  = '\x1bT1004\r' # {Tecla CE+4}
            self.CECinco5   = '\x1bT1005\r' # {Tecla CE+5}
            self.CESeis6    = '\x1bT1006\r' # {Tecla CE+6}
            self.CESete7    = '\x1bT1007\r' # {Tecla CE+7}
            self.CEOito8    = '\x1bT1008\r' # {Tecla CE+8}
            self.CENove9    = '\x1bT1009\r' # {Tecla CE+9}

            self.Modelo     = '\x1bA0000\r' # {Output of model designation}
            self.Segm       = '\x1bA0100\r' # {Output of 14-segment display}
            self.Valor      = '\x1bA0200\r' # {Output of current value}
            self.Error      = '\x1bA0301\r' # {Output of error text}
            self.Soft       = '\x1bA0400\r' # {Output of software number}
            self.Ind        = '\x1bA0900\r' # {Output of indicators}

            self.ResetRegua = '\x1bS0000\r' # {Counter RESET}
            self.Lock       = '\x1bS0001\r' # {Lock keyboard}
            self.Unlock     = '\x1bS0002\r' # {Unlock keyboard}

            # Variável de leitura
            self.DisplayPos = (0,0,0)
            self.X = 0
            self.Y = 0
            self.Z = 0
            self.Volume = 0
            return True
        except:
            return False

    def Conectar(self):
        try:
            self.ser.baudrate = 9600
            self.ser.bytesize = serial.SEVENBITS
            self.ser.stopbits = serial.STOPBITS_TWO
            self.ser.parity = serial.PARITY_EVEN
            self.ser.timeout = 0.3
            if not self.ser.isOpen():
                self.ser.open()
            return True
        except:
            return False

    def Desconectar(self):
        try:
            self.ser.close()
            return True
        except:
            return False

    def LimpaTxRx(self):
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            return True
        except:
            return False

    def EscreveValorDisplay(self,Eixo,Valor):
        try:
            # Converte para string
            aux = str(abs(Valor))
            nchar = len(aux)

            self.LimpaTxRx()
            self.ser.write(self.CL.encode('utf-8'))
            time.sleep(0.1)

            if Eixo == 0:
                self.ser.write(self.EixoX.encode('utf-8'))
            elif Eixo == 1:
                self.ser.write(self.EixoY.encode('utf-8'))
            elif Eixo == 2:
                self.ser.write(self.EixoZ.encode('utf-8'))

            time.sleep(0.2)

            # Identifica e escreve
            for i in range(nchar):
                self.LimpaTxRx()
                tmp = aux[i]
                if (tmp == '0'):
                    ajuste = self.Zero0
                elif (tmp == '1'):
                    ajuste = self.Um1
                elif (tmp == '2'):
                    ajuste = self.Dois2
                elif (tmp == '3'):
                    ajuste = self.Tres3
                elif (tmp == '4'):
                    ajuste = self.Quatro4
                elif (tmp == '5'):
                    ajuste = self.Cinco5
                elif (tmp == '6'):
                    ajuste = self.Seis6
                elif (tmp == '7'):
                    ajuste = self.Sete7
                elif (tmp == '8'):
                    ajuste = self.Oito8
                elif (tmp == '9'):
                    ajuste = self.Nove9
                elif (tmp == '.'):
                    ajuste = self.Ponto
                self.ser.write(ajuste.encode('utf-8'))
                time.sleep(0.2)

            if Valor < 0:
                self.ser.write(self.Menos.encode('utf-8'))
                time.sleep(0.2)

            # Enter
            self.ser.write(self.Ent.encode('utf-8'))
            return True
        except:
            return False

    def LerDisplay(self):
        try:
            ajuste = self.Valor
            self.LimpaTxRx()
            self.ser.write(ajuste.encode('utf-8'))
            time.sleep(0.1)
            leitura = self.ser.read(60)
            
            leitura = leitura.decode('utf-8')
            aux1 = leitura[leitura.find('X=')+2:leitura.find(' R\r\n')]
            aux1 = aux1.replace(' ','')

            leitura = leitura[leitura.find('R\r\n')+3:]
            aux2 = leitura[leitura.find('Y=')+2:leitura.find(' R\r\n')]
            aux2 = aux2.replace(' ','')

            leitura = leitura[leitura.find('R\r\n')+3:]
            aux3 = leitura[leitura.find('Z=')+2:leitura.find(' R\r\n')]
            aux3 = aux3.replace(' ','')
        
            self.X = float(aux1)/1000
            self.Y = float(aux2)/1000
            self.Z = float(aux3)/1000
                    
            #Converte para float
            self.DisplayPos = [self.X,self.Y,self.Z]
            self.Volume = self.X * self.Y * self.Z
            return True
        except:
            return False

    def Reset_SetRef_Display(self):
        try:
            # Envia comando de reset
            self.LimpaTxRx()
            self.ser.write(self.ResetRegua.encode('utf-8'))

            # Aguarda 3 segundos o processo de reset to display
            time.sleep(4)

            # Envia enter para buscar referência
            self.LimpaTxRx()
            self.ser.write(self.Ent.encode('utf-8'))
            return True
        except:
            return False
