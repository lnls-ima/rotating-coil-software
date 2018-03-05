# -*- coding: utf-8 -*-
"""
Created on 11/01/2013
Update on 23/11/2017
Versão 1.0
@author: James Citadini
"""
# Importa bibliotecas
import serial
import time
# ******************************************

class SerialCom(object):
    def __init__(self,port):  
        self.ser = serial.Serial(port)
        self.commands()
        self.delay = 0.2
        
    def commands(self):

        #Library - Integrator
        self.PDISearchIndex      = 'IND'         #Habilita a procura de indice do integrador
        self.PDIStart            = 'RUN'         #Inicia coleta com o integrador
        self.PDIStop             = 'BRK'         #Para coleta com o integrador
        self.PDIReadStatus       = 'STB,'        #Le status do integrador binario
        self.PDIReadStatusHex    = 'STH,'        #Le status do integrador hexa
        self.PDIEnquire          = 'ENQ'         #Busca Resultados do integrador
        self.PDIChannel          = 'CHA,A'       #Escolha de Canal
        self.PDIGain             = 'SGA,A,'      #Configura ganho integrador
        self.PDIClearStatus      = 'CRV,A'       #Limpa Saturacao
        self.PDITriggerEncoder   = 'TRS,E,'      #Tipo de Trigger encoder incremental rotativo
        self.PDITriggerTimer     = 'TRS,T'       #Configura integrador por tempo sem trigger externo - Default
        self.PDITriggerExternal  = 'TRS,X'       #Configura integrador por trigger externo 
        self.PDITriggerSeqNeg    = 'TRI,-,'      #Sequencia Trigger -
        self.PDITriggerSeqPos    = 'TRI,+,'      #Sequencia Trigger +
        self.PDIStoreBlockEnd    = 'IMD,0'       #Configura Dados para serem armazenados em blocos
        self.PDIStoreBlockDuring = 'IMD,1'       #Configura Dados para serem armazenados e coletados        
        self.PDIStoreCum         = 'CUM,0'       #Configura Dados para serem armazenados
        self.PDIClearCounter     = 'ZCT'         #Zerar contador de pulsos
        self.PDIEndofData        = 'EOD'         #End of Data
        self.PDISincronize       = 'SYN,1'       #Sincroniza
        self.PDIOffsetOn         = 'ADJ,A,1'     #Offset on
        self.PDIOffsetOff        = 'ADJ,A,0'     #Offset off        
        self.PDIReadEncoder      = 'RCT'         #reading Pulso Encoder
        self.FDIResolution       = 'FCT,1E12'    #Set FDI Resolution
        self.PDIShortCircuitOn   = 'ISC,A,1'     #Short Circuit On
        self.PDIShortCircuitOff  = 'ISC,A,0'     #Short Circuit Off      
        
    def connect(self):
        self.ser.baudrate = 115200      ##9600
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = 0.01
        if not self.ser.isOpen():
            self.ser.open()
            
    def disconnect(self):
        self.ser.close()
        
    def flushTxRx(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def send(self,comando):
        self.flushTxRx()
        adjust = comando + '\r'
        self.ser.write(adjust.encode('utf-8'))

    def read(self,n):
        try:
            if n==0:
                reading = self.ser.readall()
            else:
                reading = self.ser.read(n)
            reading = reading.decode('utf-8')
            reading = reading.replace('\r\n','')
        except:
            reading = ''

        return reading

    def status(self,registrador):
        self.send(self.PDIReadStatus + registrador)
        time.sleep(0.1)
        reading = self.read(10)
        return reading

    def statusHex(self,registrador):
        self.send(self.PDIReadStatusHex + registrador)
        time.sleep(0.1)
        reading = self.read(10)
        return reading
    
    def read_encoder(self):
        try:
            self.flushTxRx()
            self.send(self.PDIReadEncoder)
            time.sleep(0.05)
            reading = self.read(50)
            return reading
        except:
            return ''
        
    def config_encoder(self,encoder_pulses):
        self.send(self.PDITriggerEncoder + str(encoder_pulses))

    def index_search(self, direction):
        if direction == 0:
            self.send(self.PDISearchIndex + str(',+'))
        else:
            self.send(self.PDISearchIndex + str(',-'))

    def config_measurement(self, encoder_pulses, gain, direction, trigger_ref, integration_points, n_of_turns):
        # stop all commands and measurements
        self.send(self.PDIStop)
        time.sleep(self.delay)
        
        self.config_encoder(int(encoder_pulses/4))
        
        # configure interval and direction
        interval = int(encoder_pulses / integration_points)
        if direction  == 0:
            self.send(self.PDITriggerSeqNeg + str(trigger_ref) + '/' + str(integration_points*n_of_turns) + ',' + str(interval))
        else:
            self.send(self.PDITriggerSeqPos + str(trigger_ref) + '/' + str(integration_points*n_of_turns) + ',' + str(interval))
        time.sleep(self.delay)
        
        #configure storage - flux values can be read during the measurement.
#         self.send(self.PDIStoreBlockDuring)
        
        # configure storage - flux values cannot be read during the measurement.
        self.send(self.PDIStoreBlockEnd)        
        time.sleep(self.delay)
 
        # Configure Integrated values are stored separately
        self.send(self.PDIStoreCum)
        time.sleep(self.delay)
 
        # Configure End of Data
        self.send(self.PDIEndofData)
        time.sleep(self.delay)
        
        # Stop all collects and ready integrator
        self.send(self.PDIGain + str(gain))
        time.sleep(self.delay)
        
         # integrator resolution 1e-12 - FDI
        self.send(self.FDIResolution)
        time.sleep(self.delay)

    def start_measurement(self):
        self.send(self.PDIStart)
        time.sleep(self.delay)
        
    def get_data(self):
        if (int(self.status('1')[-3]) == 1):
            self.send(self.PDIEnquire)
            time.sleep(self.delay)
            reading = self.read(0)  # read_all        
#             reading = self.read(10)
#             if reading != '':
# #             reading = reading.replace(' A','')
# #             reading = reading.replace(chr(26),'')
#                 return reading
#             else:
#                 return ''            
        else:
            reading = ''            
        
        return reading
        
