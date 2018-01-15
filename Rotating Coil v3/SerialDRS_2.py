#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 26/04/2016
Versão 1.0
@author: Ricieri (ELP)
Python 3.4.4
"""

import struct
import serial
import time
import traceback
import sys
import numpy as np

from datetime import datetime

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
======================================================================
                    Listas de Entidades BSMP
        A posição da entidade na lista corresponde ao seu ID BSMP
======================================================================
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

ListVar = ['iLoad1','iLoad2','iMod1','iMod2','iMod3','iMod4','vLoad',
           'vDCMod1','vDCMod2','vDCMod3','vDCMod4','vOutMod1','vOutMod2',
           'vOutMod3','vOutMod4','temp1','temp2','temp3','temp4','ps_OnOff',
           'ps_OpMode','ps_Remote','ps_OpenLoop','ps_SoftInterlocks',
           'ps_HardInterlocks','iRef','wfm_Ref_Gain','wfmRef_Offset','sigGen_Enable','sigGen_Type',
           'sigGen_Ncycles','sigGenPhaseStart','sigGen_PhaseEnd','sigGen_Freq',
           'sigGen_Amplitude','sigGen_Offset','sigGen_Aux','dp_ID','dp_Class','dp_Coeffs']
ListCurv = ['wfmRef_Curve','sigGen_SweepAmp','samplesBuffer']
ListFunc = ['TurnOn','TurnOff','OpenLoop','ClosedLoop','OpMode','RemoteInterface',
            'SetISlowRef','ConfigWfmRef','ConfigSigGen', 'EnableSigGen',
            'DisableSigGen','ConfigDPModule','WfmRefUpdate','ResetInterlocks']

class SerialDRS_FBP(object):

    def __init__(self):
        self.ser=serial.Serial()

        self.MasterAdd              = '\x00'
        self.SlaveAdd               = '\x01'
        self.BCastAdd               = '\xFF'
        self.ComWriteVar            = '\x20'
        self.WriteFloatSizePayload  = '\x00\x05'
        self.WriteDoubleSizePayload = '\x00\x03'
        self.ComReadVar             = '\x10\x00\x01'
        self.ComSendWfmRef          = '\x41'
        self.ComFunction            = '\x50'
        
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                    Funções Internas da Classe
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Converte float para hexadecimal
    def float_to_hex(self, value):
        hex_value = struct.pack('f', value)
        return hex_value.decode('ISO-8859-1')
    
    # Converte double para hexadecimal
    def double_to_hex(self,value):
        hex_value = struct.pack('H',value)
        return hex_value.decode('ISO-8859-1')

    # Converte indice para hexadecimal
    def index_to_hex(self,value):
        hex_value = struct.pack('B',value)
        return hex_value.decode('ISO-8859-1')

    # Converte payload_size para hexadecimal
    def size_to_hex(self,value):
        hex_value = struct.pack('>H',value)
        return hex_value.decode('ISO-8859-1')

    # Função Checksum    
    def checksum(self, packet):
        b=bytearray(packet.encode('ISO-8859-1'))
        csum =(256-sum(b))%256
        hcsum = struct.pack('B',csum)
        send_msg = packet + hcsum.decode(encoding='ISO-8859-1')
        return send_msg

    # Função de leitura de variável 
    def read_var(self,var_id):
        send_msg = self.checksum(self.SlaveAdd+self.ComReadVar+var_id)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        
    #BSMP Error Table
    def check_reply(self, val):
        try:
            if '\xe0' in val:
                return 'OK'
            elif '\x51' in val:
                return 'OK'
            elif '\xe1' in val:
                return 'Mensagem Mal Formada'
            elif '\xe2' in val:
                return 'Operacao Nao Suportada'
            elif '\xe3' in val:
                return 'ID Invalido'
            elif '\xe4' in val:
                return 'Valor Invalido'
            elif '\xe5' in val:
                return 'Tamanho da Carga Invalido'
            elif '\xe6' in val:
                return 'Somente Leitura'
            elif '\xe7' in val:
                return 'Memória Insuficiente'
            elif '\xe8' in val:
                return 'Recurso Ocupado'
            else:
                return 'Erro Nao Identificado'
        except TypeError:
            val = chr(val)
            if '\xe0' in val:
                return 'OK'
            elif '\x51' in val:
                return 'OK'
            elif '\xe1' in val:
                return 'Mensagem Mal Formada'
            elif '\xe2' in val:
                return 'Operacao Nao Suportada'
            elif '\xe3' in val:
                return 'ID Invalido'
            elif '\xe4' in val:
                return 'Valor Invalido'
            elif '\xe5' in val:
                return 'Tamanho da Carga Invalido'
            elif '\xe6' in val:
                return 'Somente Leitura'
            elif '\xe7' in val:
                return 'Memória Insuficiente'
            elif '\xe8' in val:
                return 'Recurso Ocupado'
            else:
                return 'Erro Nao Identificado'
            
        
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Chamada de Entidades Funções BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def TurnOn(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('TurnOn'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def TurnOff(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('TurnOff'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)
    
    def OpenLoop(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('OpenLoop'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)
    
    def ClosedLoop(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ClosedLoop'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6) 

    def OpMode(self,op_mode):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_opmode
        hex_opmode   = self.double_to_hex(op_mode)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('OpMode'))+hex_opmode
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)
    
    def RemoteInterface(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('RemoteInterface'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SetISlowRef(self,setpoint):
        payload_size   = self.size_to_hex(1+4) #Payload: ID + iSlowRef
        hex_setpoint   = self.float_to_hex(setpoint)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('SetISlowRef'))+hex_setpoint
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigWfmRef(self,gain,offset):
        payload_size = self.size_to_hex(1+4+4) #Payload: ID + gain + offset
        hex_gain     = self.float_to_hex(gain)
        hex_offset   = self.float_to_hex(offset)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigWfmRef'))+hex_gain+hex_offset
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigSigGen(self,sigType,nCycles,phaseStart,phaseEnd):
        payload_size   = self.size_to_hex(1+2+2+4+4) #Payload: ID + type + nCycles + phaseStart + phaseEnd
        hex_sigType    = self.double_to_hex(sigType)
        hex_nCycles    = self.double_to_hex(nCycles)
        hex_phaseStart = self.float_to_hex(phaseStart)
        hex_phaseEnd   = self.float_to_hex(phaseEnd)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigSigGen'))+hex_sigType+hex_nCycles+hex_phaseStart+hex_phaseEnd
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def EnableSigGen(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('EnableSigGen'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def DisableSigGen(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('DisableSigGen'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigDPModule(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigDPModule'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def WfmRefUpdate(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('WfmRefUpdate'))
        send_msg     = self.checksum(self.BCastAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))

    def ResetInterlocks(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ResetInterlocks'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Leitura de Valores das Variáveis BSMP
    O retorno do método são os valores double/float da respectiva variavel
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def Read_iLoad1(self):
        self.read_var(self.index_to_hex(ListVar.index('iLoad1')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]
    
    def Read_iLoad2(self):
        self.read_var(self.index_to_hex(ListVar.index('iLoad2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]
    
    def Read_iMod1(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod1')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iMod2(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iMod3(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod3')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]
    
    def Read_iMod4(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod4')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]    

    def Read_vDCMod1(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod1')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]    

    def Read_vDCMod2(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]
    
    def Read_vDCMod3(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod3')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3] 

    def Read_vDCMod4(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod4')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp1(self):
        self.read_var(self.index_to_hex(ListVar.index('temp1')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp2(self):
        self.read_var(self.index_to_hex(ListVar.index('temp2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp3(self):
        self.read_var(self.index_to_hex(ListVar.index('temp3')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp4(self):
        self.read_var(self.index_to_hex(ListVar.index('temp4')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_ps_OnOff(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_OnOff')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_OpMode(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_OpMode')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_Remote(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_Remote')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_OpenLoop(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_OpenLoop')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_SoftInterlocks(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_SoftInterlocks')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHLB',reply_msg)
        return val[3]

    def Read_ps_HardInterlocks(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_HardInterlocks')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHLB',reply_msg)
        return val[3]

    def Read_iRef(self):
        self.read_var(self.index_to_hex(ListVar.index('iRef')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]
    
    def Read_wfmRef_Gain(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_Gain')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]
    
    def Read_wfmRef_Offset(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_Offset')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]     

    def Read_sigGen_Enable(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Enable')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_sigGen_Type(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Type')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_sigGen_Ncycles(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Ncycles')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_sigGen_PhaseStart(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_PhaseStart')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_PhaseEnd(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_PhaseEnd')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Freq(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Freq')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Amplitude(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Amplitude')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Offset(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Offset')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Aux(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Aux')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_dp_ID(self):
        self.read_var(self.index_to_hex(ListVar.index('dp_ID')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_dp_Class(self):
        self.read_var(self.index_to_hex(ListVar.index('dp_Class')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_dp_Coeffs(self):
        self.read_var(self.index_to_hex(ListVar.index('dp_Coeffs')))
        reply_msg = self.ser.read(69)
        val = struct.unpack('BBHffffffffffffffffB',reply_msg)
        return [val[3],val[4],val[5],val[6],val[7],val[8],val[9],val[10],val[11],val[12],val[13],val[14],val[15],val[16],val[17],val[18]]

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Escrita de Valores das Variáveis BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def Write_sigGen_Freq(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Freq'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_sigGen_Amplitude(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Amplitude'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_sigGen_Offset(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Offset'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_sigGen_Aux(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Aux'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_dp_ID(self,double_value):
        hex_double   = self.float_to_hex(double_value)
        send_packet  = self.ComWriteVar+self.WriteDoubleSizePayload+self.index_to_hex(ListVar.index('dp_ID'))+hex_double
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_dp_Class(self,double_value):
        hex_double   = self.float_to_hex(double_value)
        send_packet  = self.ComWriteVar+self.WriteDoubleSizePayload+self.index_to_hex(ListVar.index('dp_Class'))+hex_double
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_dp_Coeffs(self,list_float):
        hex_float_list = []
        for float_value in list_float:
            hex_float = self.float_to_hex(float(float_value))
            hex_float_list.append(hex_float)
        str_float_list = ''.join(hex_float_list)
        payload_size = self.size_to_hex(1+64) #Payload: ID + 16floats
        send_packet  = self.ComWriteVar+payload_size+self.index_to_hex(ListVar.index('dp_Coeffs'))+str_float_list
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                     Métodos de Escrita de Curvas BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def Send_wfmRef_Curve(self,block_idx,data):
        block_hex = struct.pack('>H',block_idx).decode('ISO-8859-1')
        val   = []
        for k in range(0,len(data)):
            val.append(self.float_to_hex(float(data[k])))
        payload_size = struct.pack('>H', (len(val)*4)+3).decode('ISO-8859-1')
        curva_hex     = ''.join(val)
        send_packet   = self.ComSendWfmRef+payload_size+self.index_to_hex(ListCurv.index('wfmRef_Curve'))+block_hex+curva_hex 
        send_msg      = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(7)

    
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                            Funções Serial
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
    def Connect(self,port,baud=115200):
        try:
            self.ser = serial.Serial(port,baud,timeout=1) #port format should be 'COM'+number
            return True
        except:
            return False

    def Disconnect(self):
        if (self.ser.isOpen()):
            try:
                self.ser.close()
                return True
            except:
                return False

    def SetSlaveAdd(self,address):
        self.SlaveAdd = struct.pack('B',address).decode('ISO-8859-1')
    


class Std_Alone():
    def __init__(self, classe_drs):
        self.fonte = classe_drs
        self.LeituraCorrente = 0
        self.Status_Fonte = 0
        self.fonte_ciclando = 0
        self.curva_configurada = -1
        #self.port = port
        
##    def Conectar(self):
##        """Conecta porta serial da fonte."""
##        try: #Conecta fonte
##            self.fonte.Connect(self.port, 115200)
##            self.fonte.SetSlaveAdd(2)
##            self.fonte.SetISlowRef(0)
##            self.Corrente_Fonte()
##            while self.LeituraCorrente > 1:
##                self.Corrente_Fonte()
##                time.sleep(0.2)
##            recv_hex = self.fonte.TurnOff().decode('ISO-8859-1')
##            self.fonte.SetSlaveAdd(1)
##            if self.fonte.Read_ps_OnOff(): #Desliga fonte
##                try:
##                    recv_hex = self.fonte.TurnOff().decode('ISO-8859-1')     
##                    if 'OK' in self.fonte.check_reply(recv_hex[1]):
##                        self.Status_Fonte = 0
##                except:
##                    traceback.print_exc()
##                    self.fonte.Disconnect()
##            #Checa interlock na fonte:
##            if self.checa_interlock():
##                print('Erro: Fonte em interlock.')
##                return False
##            return True
##        except:
##            traceback.print_exc()
##            self.fonte.Disconnect()
##            print('Erro: Porta serial da fonte ocupada ou inexistente.')
##            return False
##    
##    def Desconectar(self):
##        """Desconecta porta serial da fonte"""
##        try:
##            self.fonte.Disconnect()
##            return True
##        except:
##            traceback.print_exc()
##            print('Erro: Comunicação serial da fonte inexistente.')
##            return False
    
    def On_Off(self):
        """Liga/Desliga fonte"""
        if self.Status_Fonte == 0:
            try: #Carrega banco de capacitores:
                self.fonte.SetSlaveAdd(1)
                self.limpa_interlock()
                if self.checa_interlock():
                    self.Status_Fonte = 0
                    self.ui.groupBox_5.setEnabled(False)
                    print('Erro: Fonte em interlock.')
                    return False
                recv_hex = self.fonte.TurnOn().decode('ISO-8859-1')                
                if not 'OK' in self.fonte.check_reply(recv_hex[1]):
                    self.Status_Fonte = 0
                    self.ui.groupBox_5.setEnabled(False)
                    print('Erro: Não foi possível comunicar com a fonte. (1)')
                    return False
                time.sleep(1.1)
                recv_hex = self.fonte.ClosedLoop().decode('ISO-8859-1')
                if not 'OK' in self.fonte.check_reply(recv_hex[1]):
                    self.Status_Fonte = 0
                    self.ui.groupBox_5.setEnabled(False)
                    print('Erro: Não foi possível configurar fonte com malha fechada.')
                    return False
                if not self.fonte.Read_ps_OpenLoop():
                    recv_hex = self.fonte.SetISlowRef(90).decode('ISO-8859-1') #Seta tensão no banco para 90V
                    if 'OK' in self.fonte.check_reply(recv_hex[1]):
                        for i in range(30): #espera 15s para subir tensão dos capacitores
                            time.sleep(0.5)
                    else:
                        raise RuntimeError
                else:
                    raise RuntimeError
            except:
                traceback.print_exc()
                self.Status_Fonte = 0
                print('Erro: Não foi possível carregar banco de capacitores.')
                return False
            try: #Liga Módulo de Corrente:
                self.fonte.SetSlaveAdd(2)
                self.limpa_interlock()
                if self.checa_interlock():
                    print('Erro: Fonte em interlock.')
                    return False
                recv_hex = self.fonte.TurnOn().decode('ISO-8859-1')     
                if not 'OK' in self.fonte.check_reply(recv_hex[1]):
                    self.Janela.ui.status_fonte.setText('Sem conexao')
                    print('Erro: Não foi possível comunicar com a fonte. (2)')
                    return False
                if self.fonte.Read_ps_OpenLoop(): #Configura malha fechada
                    time.sleep(0.2)
                    recv_hex = self.fonte.ClosedLoop().decode('ISO-8859-1')
                    if not 'OK' in self.fonte.check_reply(recv_hex[1]):
                        print('Erro: Não foi possível configurar fonte com malha fechada.')
                        return False
                if not self.fonte.Read_ps_OpenLoop():
                    time.sleep(0.2)
                    recv_hex = self.fonte.OpMode(0)
                    if not 'OK' in self.fonte.check_reply(recv_hex[1]):
                        print('Erro: Não foi possível configurar fonte em modo SlowRef.')
                        return False
                    time.sleep(0.2)
                    recv_hex = self.fonte.SetISlowRef(0).decode('ISO-8859-1')
                    interlock = self.checa_interlock()
                    if 'OK' in self.fonte.check_reply(recv_hex[1]) and not interlock:
                        self.Corrente_Fonte()
                        self.Status_Fonte = 1
                    else:
                        self.Status_Fonte = 0
                        print('Erro, Não foi possível comunicar com a fonte. (3)')
                        return False
            except:
                traceback.print_exc()
                self.Status_Fonte = 0
                print('Atenção: Sem conexão com a fonte.1')
                return False
        else:
            #Desliga Módulo de Corrente
            self.fonte.SetSlaveAdd(2)
            status = self.fonte.Read_ps_OnOff()
            if status == 1:
                recv_hex = self.fonte.SetISlowRef(0).decode('ISO-8859-1')
                self.Corrente_Fonte()
                while self.LeituraCorrente > 1:
                    self.Corrente_Fonte()
                    time.sleep(0.5)
                self.Corrente_Atual = 0
                recv_hex = self.fonte.TurnOff().decode('ISO-8859-1') # Desliga saída da fonte
                if not 'OK' in self.fonte.check_reply(recv_hex[1]):
                    self.Status_Fonte = 1
                    print('Erro: Fonte não desligou, checar comunicação.')
                    return False
            elif status != 0:
                self.Status_Fonte = 1
                print('Erro: Fonte não recebeu o comando.')
                return False
            #Desliga Banco de Capacitores
            self.fonte.SetSlaveAdd(1)
            status = self.fonte.Read_ps_OnOff()
            time.sleep(0.2)
            if status == 1:
                recv_hex = self.fonte.TurnOff().decode('ISO-8859-1') # Desliga saída da fonte
                if not 'OK' in self.fonte.check_reply(recv_hex[1]):
                    self.Status_Fonte = 1
                    print('Erro: Banco de capacitores não desligou, checar comunicação.')
                    return False
                self.Status_Fonte = 0
            elif status != 0:
                self.Status_Fonte = 1
                print('Erro: Fonte não recebeu o comando.')
                return False
       
    def Corrente_Fonte(self):
        """Retorna leitura de corrente."""
        try:
            time.sleep(.1)
            self.LeituraCorrente = round(self.fonte.Read_iLoad1(),3)
            self.soft_interlock = self.fonte.Read_ps_SoftInterlocks()
            self.hard_interlock = self.fonte.Read_ps_HardInterlocks()
            return self.LeituraCorrente
        except:
            if self.Status_Fonte == 1:
                print('Atenção: Verificar Dados da Fonte.')
            return False
    
    def checa_interlock(self):
        """Checa interlock e retorna em caso de software ou hardware interlock"""
        time.sleep(0.2)
        self.soft_interlock = self.fonte.Read_ps_SoftInterlocks()
        time.sleep(0.2)
        self.hard_interlock = self.fonte.Read_ps_HardInterlocks()
        return self.soft_interlock + self.hard_interlock
        
    def limpa_interlock(self):
        """Limpa interlocks."""
        try:
            time.sleep(0.2)
            recv_hex = self.fonte.ResetInterlocks().decode('ISO-8859-1')
            if 'OK' in self.fonte.check_reply(recv_hex[1]):
                self.checa_interlock()
            else:
                raise
        except:
            traceback.print_exc()
            print('Atenção.','Sem conexão com a fonte.2')
            
    
    def configura_senoidal_am(self, freq=2, amp=150, offset=0, ctempo=5, ciclos=150):
        """Configura ciclagem senoidal amortecida.
        
        Args:
            freq (int):  frequência da ciclagem [Hz]
            amp (float): amplitude da ciclagem [A]
            offset (float): offset da ciclagem [A]
            ctempo (float): constante de tempo do amortecimento [s] 
        """
        try:
            sigType=4
            mode=3
            self.fonte.OpMode(mode)
            if (self.fonte.Read_ps_OpMode() != 3):
                print('Atenção: Gerador de sinais da fonte não configurado corretamente. Verifique configuração.')
                return False
        except:
            traceback.print_exc(file=sys.stdout)
            print('Atenção: Verifique configuração da fonte.')
            return
        
        try:
            self.fonte.Write_sigGen_Freq(freq)             #Enviando Frequencia
            self.fonte.Write_sigGen_Amplitude(amp)         #Enviando Amplitude
            self.fonte.Write_sigGen_Offset(offset)         #Enviando Offset
        except:
            traceback.print_exc(file=sys.stdout)
            print('Atenção: Verifique valores de configuração enviados para fonte.')
            return

        #Enviando o sigGenAmortecido
        try:
            self.fonte.Write_sigGen_Aux(ctempo)
            recv_hex = self.fonte.ConfigSigGen(sigType, ciclos, 0, 0)
            if 'OK' in self.fonte.check_reply(recv_hex[1]):
                self.curva_configurada = 1
                return True
        except:
            traceback.print_exc(file=sys.stdout)
            print('Atenção: Falha no envio da curva senoidal amortecida.')
            return False
        
    def configura_triangular_am(self, ganho=100, offset=0):
        """Configura ciclagem triangular amortecida.
        Curva padrão vai de zero até 1 A.
        
        Args:
            ganho (float): ganho para curva senoidal. Valor pode ser considerado máximo de corrente em [A].
            offset (float): offset da curva [A].
        """
        recv_hex = self.fonte.Send_wfmRef_Curve(0, Pontos_Triangular()) #Número do bloco e pontos da curva
        if 'OK' in self.fonte.check_reply(recv_hex[1]):
            self.curva_configurada = 2
        else:
            print('Atenção: Falha no envio da curva triangular amortecida.')
            return False
        recv_hex = self.fonte.ConfigWfmRef(ganho, offset)
        if not 'OK' in self.fonte.check_reply(recv_hex[1]):
            print('Atenção: Falha na configuração da curva triangular amortecida.')
            return False
        return True
        
    def ciclar_senoidal(self):
        """Realiza ciclagem senoidal amortecida."""
        op_mode = self.fonte.Read_ps_OpMode()
        ciclos = self.fonte.Read_sigGen_Ncycles()
        freq = self.fonte.Read_sigGen_Freq()
        if self.curva_configurada == 1 and op_mode == 3:
            self.fonte_ciclando = 1
            recv_hex = self.fonte.EnableSigGen().decode('ISO-8859-1')
            if 'OK' in self.fonte.check_reply(recv_hex[1]):         
                if not (self.fonte.Read_sigGen_Enable()):
                    self.fonte_ciclando = 0
                    print('Atenção: Não foi possível ligar gerador de função.')
                    return False
            else:
                self.fonte_ciclando = 0
                print('Atenção: Não foi possível ligar gerador de função.')
                return False
            time.sleep(ciclos/freq + 0.5) #espera final da ciclagem
        recv_hex = self.fonte.DisableSigGen().decode('ISO-8859-1')
        if 'OK' in self.fonte.check_reply(recv_hex[1]):         
            if (self.fonte.Read_sigGen_Enable()):
                self.fonte_ciclando = 0
                print('Atenção: Não foi possível desligar gerador de função.')
        else:
            self.fonte_ciclando = 0
            print('Atenção: Configurar curva senoidal amortecida.')
            return False
        
        #Zera corrente após ciclagem
        recv_hex = self.fonte.OpMode(0).decode('ISO-8859-1')
        if not 'OK' in self.fonte.check_reply(recv_hex[1]):
            self.Fonte_Ciclagem = 0
            print('Atenção: A fonte não está configurada no modo DC.')
            return False
        recv_hex = self.fonte.SetISlowRef(0).decode('ISO-8859-1')
        if not 'OK' in self.fonte.check_reply(recv_hex[1]):
            self.fonte_ciclando = 0
            print('Atenção: Não foi possível zerar corrente após ciclagem.')
            return False
        return True

    def ciclar_triangular(self):
        """Realiza ciclagem triangular amortecida."""
        op_mode = self.fonte.Read_ps_OpMode()
        ciclos = self.fonte.Read_sigGen_Ncycles()
        if self.curva_configurada == 2 and op_mode == 2:
            self.fonte_ciclando = 1
            for i in range(ciclos):
                tempo = time.time()
                try:
                    self.fonte.WfmRefUpdate()
                except:
                    self.fonte_ciclando = 0
                    print('Atenção: Não foi possível enviar pulso de sincronismo.')
                    return False
                try:
                    time.sleep(0.5 - (time.time()-tempo))
                except ValueError:
                    pass
                
        #Zera corrente após ciclagem
        recv_hex = self.fonte.OpMode(0).decode('ISO-8859-1')
        if not 'OK' in self.fonte.check_reply(recv_hex[1]):
            self.fonte_ciclando = 0
            print('Atenção: A fonte não está configurada no modo DC.')
            return False
        recv_hex = self.fonte.SetISlowRef(0).decode('ISO-8859-1')
        if not 'OK' in self.fonte.check_reply(recv_hex[1]):
            self.fonte_ciclando = 0
            print('Atenção: Não foi possível zerar corrente após ciclagem.')
            return False
        return True
    
    def setar_DC(self, corrente = 0):
        """Configura corrente DC.
        Args:
            corrente (float): corrente em [A]"""
        recv_hex = self.fonte.OpMode(0).decode('ISO-8859-1')
        if not 'OK' in self.fonte.check_reply(recv_hex[1]):
            self.fonte_ciclando = 0
            print('Atenção: A fonte não está configurada no modo DC.')
            return False
        recv_hex = self.fonte.SetISlowRef(corrente).decode('ISO-8859-1')
        if not 'OK' in self.fonte.check_reply(recv_hex[1]):
            self.fonte_ciclando = 0
            print('Atenção: Não foi possível enviar corrente para fonte.')
            return False
        while (self.LeituraCorrente < (corrente -0.5)):
            self.Corrente_Fonte()
            time.sleep(0.5)
        return True
           
def Pontos_Triangular():
    #Curve Polynomials
    p0 = np.poly1d([0.0003392857, 0.0007142857, 0, 0])
    p1 = np.poly1d([0, 0, 0.4357142857, 3])
    p2 = np.poly1d([-0.0001607143, -0.0060714286, 0.4357142857, 125])
    p3 = np.poly1d([0.0004821429, -0.0346428571, 0, 130])
    p4 = np.poly1d([0, 0, -0.8071428571, 120])
    p5 = np.poly1d([-0.0002678571, 0.0282142857, -0.8071428571, 7])
    t0 = np.array([0, 20, 300, 320, 340, 480, 500])
    n_points = 2048
    dt = t0[-1]/n_points
    current = np.array([])
    time = np.array([])
    for i in range(n_points):
        t = i*dt
        time = np.append(time, t)
        if t < t0[1]:
            current = np.append(current, p0(t)/130)
        elif t0[1] <= t < t0[2]:
            current = np.append(current, p1(t-t0[1])/130)
        elif t0[2] <= t < t0[3]:
            current = np.append(current, p2(t-t0[2])/130)
        elif t0[3] <= t < t0[4]:
            current = np.append(current, p3(t-t0[3])/130)
        elif t0[4] <= t < t0[5]:
            current = np.append(current, p4(t-t0[4])/130)
        elif t0[5] <= t:
            current = np.append(current, p5(t-t0[5])/130)
    return current
