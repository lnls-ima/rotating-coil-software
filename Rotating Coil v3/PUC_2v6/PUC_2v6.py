#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 23/07/2014
Versão 2.6
@author: Lucas Igor
Python 3.2.3 32 bits
"""
#Importa bibliotecas
import time, sys, math
import pucsp
import bsmp
import hashlib


class SerialCom(object):

    def __init__(self,PUCaddr):
        self.PUCaddress = int(PUCaddr)

    def Iniciar(self):
        self.Comandos()
        self.DA = self.P.das[0]
        self.AD = self.P.ads[0]
        self.DigIn = self.P.digins[0]
        self.DigOut = self.P.digouts[0]

        
    def Comandos(self):
        # Constantes de comando de protocolo da PUC
        #(Protocolo de controle de baixo nível 0v7)
        self.QUERY_STATUS                    = 0x00
        self.STATUS                          = 0x01
        self.QUERY_VARS_LIST                 = 0x02
        self.VARS_LIST                       = 0x03
        self.QUERY_GROUPS_LIST               = 0x04
        self.GROUPS_LIST                     = 0x05
        self.QUERY_GROUP                     = 0x06
        self.GROUP                           = 0x07
        self.QUERY_CURVES_LIST               = 0x08
        self.CURVES_LIST                     = 0x09
        self.QUERY_CHECKSUM                  = 0x0A
        self.CHECKSUM                        = 0x0B
        # Comados de leitura
        self.READ_VAR                        = 0x10
        self.VAR_READING                     = 0x11
        self.READ_GROUP                      = 0x12
        self.GROUP_READING                   = 0x13
        # Comandos de escrita
        self.WRITE_VAR                       = 0x20
        self.WRITE_GROUP                     = 0x22
        # Mainupulação de grupos
        self.CREATE_GROUP                    = 0x30
        self.GROUP_CREATED                   = 0x31
        self.REMOVE_ALL_GROUPS               = 0x32
        #Transferências de curvas
        self.CURVE_TRANSMIT                  = 0x40
        self.CURVE_BLOCK                     = 0x41
        self.CURVE_RECALC_CSUM               = 0x42
        #Comandos de erro
        self.OK                              = 0xE0
        self.ERR_MALFORMED_MESSAGE           = 0xE1
        self.ERR_OP_NOT_SUPPORTED            = 0xE2
        self.ERR_INVALID_ID                  = 0xE3
        self.ERR_INVALID_VALUE               = 0xE4
        self.ERR_INVALID_PAYLOAD_SIZE        = 0xE5
        self.ERR_READ_ONLY                   = 0xE6
        self.ERR_INSUFFICIENT_MEMORY         = 0xE7
        self.ERR_INTERNAL                    = 0xE8

    def Var_type(self):
        self.CONFIG_SYNC     = 0x85
        self.DIGIN           = 0x01
        self.ADC             = 0x03
        self.DIGOUT          = 0x81
        self.DAC             = 0x83

    def Conectar(self, port, baud=6e6, tout=2.0, retries=3, debug=False):
        try:
            port = 'COM'+str(port)
            self.P = pucsp.SerialPUC(port, baud, self.PUCaddress, retries=3, debug=False)
            self.Iniciar()
            return True
        except:
            return False
   
    def Desconectar(self):
        self.P.disconnect()
        
    def reset(self):
        self.P.pucReset.execute()
   
## Funções de leitura   
         
    def ReadDA(self):
        return self.DA.read()

    def ReadDigOut(self):
        return self.DigOut.read()

    def ReadAD(self):
        return self.AD.read()

    def ReadDigIn(self):
        return self.DigIn.read()

## Funções de escrita

    def WriteDigBit(self,port, value):
        # Escreve em um bit digital
        # Lê a saída atual
        outnow = self.ReadDigOut()
        if port == 0:
            if value == 0:
                outnew = 0b11111110 & outnow
            else:
                outnew = 0b00000001 | outnow
        elif port == 1:
            if value == 0:
                outnew = 0b11111101 & outnow
            else:
                outnew = 0b00000010 | outnow
        elif port == 2:
            if value == 0:
                outnew = 0b11111011 & outnow
            else:
                outnew = 0b00000100 | outnow
        elif port == 3:
            if value == 0:
                outnew = 0b11110111 & outnow
            else:
                outnew = 0b00001000 | outnow
        elif port == 4:
            if value == 0:
                outnew = 0b11101111 & outnow
            else:
                outnew = 0b00010000 | outnow
        elif port == 5:
            if value == 0:
                outnew = 0b11011111 & outnow
            else:
                outnew = 0b00100000 | outnow
        elif port == 6:
            if value == 0:
                outnew = 0b10111111 & outnow
            else:
                outnew = 0b01000000 | outnow
        elif port == 7:
            if value == 0:
                outnew = 0b01111111 & outnow
            else:
                outnew = 0b10000000 | outnow
        else:
            return False
        self.DigOut.write(outnew)
        return True

    def WriteDig(self,value):
        # Escreve na Saída Digital
        return self.DigOut.write(value)

    def WriteDA(self, value):
        return self.DA.write(value)

## Funções da curva:

    def CreateChecksum(self,pts,bits=True):
        try:
            pktCSum = self.P.sync.outCurve.doCSum(pts, bool(bits))
            return pktCSum
        except:
            return False
        
    def SendCurve(self, pts, widePoint=True, force=True):       # widePoint=False; Os pontos tem 16 bits (2 bytes).
        self.P.sync.outCurve.write(pts, widePoint, force)       # widePoint=True; Os pontos tem 18 bits (4 bytes).
                                                                # force=True; A curva é enviada mesmo já havendo curva idêntica na memória.
        return self.P.sync.outCurve.recalcCSum()                                                            

    def ExecuteCurve(self, points=None, CLK_IN_EXT=1, CLK_OUT=1, Flash=1, RAM=1, Dout_bit=0, Loop=0, Precision=1, divisor=14, pfim=0, Bit_pfim=0): ## CLK int0/ext1
        if not points:                                                                                                                             ## Precision = 1(True), 18 bits 
            return                                                                                                                                 ## Precision = 0(False), 16 bits

        if points > self.P.Syconfig.MAX_WPOINTS and Precision == 1:
            return False
        
        if points >= 65536:
            points = 65536            
            byte1=byte2=0
        else:
            byte1 = points>>8              
            byte2 = points & 0xFF

        if divisor >= 65535:
            divisor = 65535
        else:
            div1 = divisor>>8
            div2 = divisor & 0xFF

        # Configuration of first byte (first)
        if RAM == 1:
            first = 0x80
        else:
            first = 0x00
        if Flash == 1:
            first = first | 0x40
        if Precision == 1:
            first = first | 0x20
        if CLK_IN_EXT == 1:
            first = first | 0x08
            divisor = 0

        # Configuration of sixth byte (sixth)
        sixth = 0
        if CLK_OUT == 1:
            sixth = 0x80            
        if pfim == 1:
            sixth = sixth | 0x08
        Dout_bit = Dout_bit<<4
        sixth = sixth | Dout_bit
        sixth = sixth | Bit_pfim

        if Dout_bit or Bit_pfim > 0x07:
            return False 

        conf = [first, byte1, byte2, div1, div2, sixth]
##        print(conf)
        self.P.sync.config.write(conf)

        if self.P.sync.getState()[0] == "STOPPED":
           self.P.sync.start()
           
           return

    def parseState(self, data):
        states = ("STOPPED", "RUNNING", "PAUSED")
        stateString = states[(data[0] & 0xC0) >> 6]
        index = (data[1] << 16) | (data[2] << 8) | data[3]
        return (stateString, index)

    def getState(self):
        DYN_VARS = 3
        vars = self.P.bsmp.queryVarsList()
        syncVars = vars[1:DYN_VARS]
        self.state = syncVars[0]
        data = self.state.read()
        return self.parseState(data)

    def ReadStatusCurve(self):
        return self.P.sync.getState()

    def StepCurve(self):
        return self.P.sync.step()

    def PauseCurve(self):
        return self.P.sync.pause()

    def StopCurve(self):
        return self.P.sync.stop()

    def ReadCaptured(self, nPoints, widePoint=True):
        try:
            pts = self.P.sync.inCurve.read(nPoints, widePoint=True)
##            npts = len(pts)
##            with open(path, 'w') as f:
##                for pt in npts:
##                    f.write("{:-02.3f}\n".format(pt))
##            return True
            return pts                    
        except:
            return False       
    
    def ReadFirstPoint(self):
        return self.P.sync.inCurve.read(1, widePoint=True)

    def CalculateGeneratedCsum(self):
        return self.P.sync.inCurve.cSum()

    def UpdateChecksumsCurves(self):
        return self.P.sync.inCurve.curve()

##    def CalculateGeneratedCsum(self,data):
##        return hashlib.md5(bytearray(data)).hexdigest()

    def UpdateChecksumsCurves(self, curves = []):
        # Lê o Checksum da curva DA da PUC
        # Flash DA
        return self.P.sync.outCurve.recalcCSum()

    def CalculateGeneratedCsum(self, pts, bits = False):
        return self.P.sync.outCurve.doCSum(pts, bits)

        







        

    

    
    
    

        
