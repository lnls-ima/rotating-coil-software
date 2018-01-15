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
from hashlib import md5

class Serial_PUC(object):
##    def __init__(self, port, baud, address, retries=3, debug=False):
##        puc.SerialPUC(port, baud, address, retries=3, debug=False)
##        self.DA = puc.DA(self.das)

    def Iniciar(self):
        self.Comandos()
        self.DA = self.P.das[0]
        self.AD = self.P.ads[0]
##        self.DigIn = self.P.digins[0]
##        self.DigOut = self.P.digouts[0]
##        self.SendCurve = self.P.sync.outCurve()
##        self.nPoints = self.P.puccurve.nPoints(syncCurves[1])
##        self.ExeCurve = self.P.sync()
##        self.StopCurve = self.P.sync()
##        self.ReadCurve = self.P.sync.inCurve()
     


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

    def Conectar(self, port, baud, address, retries=3, debug=False):
        self.P = pucsp.SerialPUC(port, baud, address, retries=3, debug=False)
        self.Iniciar()
        

    def Desconectar(self):
        self.P.PUC.disconnect()

   
## Funções de leitura   
         
    def ReadDA(self):
        return self.DA.read()

    def ReadDigOut(self):
        return self.DigiOut.read()

    def ReadAD(self):
        return self.AD.read()

    def ReadDigIn(self):
        return self.DigiIn.read()

## Funções de escrita

    def WriteDigBit(self):
        pass
    
    def WriteDig(self,value):
        pass

    def WriteDA(self, value):
        return self.DA.write(value)

## Funções da curva:

##    def SendCurve(self, syncCurves, nPoints):
##        self.SendCurve.write(syncCurves[1])
##        self.nPoints().setValue(nPts)
##          
##    def ExecuteCurve():
##        return self.ExeCurve.start()
##
##    def ReadStatusCurve():
##        pass
##
##    def StopCurve(self):
##        return self.StopCurve.stop()
##
##    def ReadCaptured(self):
##        pts = self.pucsp.sync.inCurve.read(nPoints, widePoint=False)
##        npts = len(pts)
##        try:
##            with open(path, 'w') as f:
##                for pt in pts:
##                    f.write("{:-02.3f}\n".format(pt))
