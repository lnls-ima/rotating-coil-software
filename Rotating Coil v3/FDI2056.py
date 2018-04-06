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
import visa
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

    def config_measurement(self, encoder_pulses, direction, trigger_ref, integration_points, n_of_turns):
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

class EthernetCom():
    def __init__(self):
        self.rm = visa.ResourceManager()
        self._commands()

    def _commands(self):
        self.FDIReadEncoder     = "CONTR:ENC:POS?" #lê posição do encoder
        self.FDIConfigEncoder   = "CONTR:ENC:CONF 'DIFF,/A:/B:IND,ROT:" #configura encoder
        self.FDIDataCount       = "DATA:COUN?" #retorna comprimento do buffer de fluxo
        self.FDIArmEncoder      = "ARM:SOUR ENC" #configura encoder como fonte de trigger_ref
        self.FDIArmRef          = "ARM:ENC " #configura trigger_ref
        self.FDICalcFlux        = "CALC:FLUX 0" #configura integrais parciais (integra somente entre um trigger e outro)
        self.FDIFetchArray      = "FETC:ARR? " #lê buffer de fluxo
        self.FDIShortCircuitOn  = "INP:COUP GND" #Short circuit on
        self.FDIShortCircuitOff = "INP:COUP DC" #Short circuit off
        self.FDIGain            = "INP:GAIN " #configure gain
        self.FDIStoreConfig     = "MEM:STOR" #saves current configuration in hd
        self.FDIDelConfig       = "MEM:DEL" #deletes current configuration in hd
        self.FDIReadArray       = "READ:ARR? " #same as FetchArray but sends ABORt;INIT before fetching the array
        self.FDICalibrate       = "SENS:CORR:ALL" #calibrates offset and slope for all gains
        self.FDITriggerSource   = "TRIG:SOUR ENC" #configures encoder as trigger source
        self.FDITriggerCount    = "TRIG:COUN " #configures number of triggers to complete a measurement
        self.FDITriggerECount   = "TRIG:ECO " #number of enconder pulses to generate a trigger
        self.FDITriggerDir      = "TRIG:ENC " #configures trigger direction as FORward or BACKward
        self.FDIError           = "SYST:ERR?" #returns system errors until all errors are read
        self.FDIStop            = "ABORT" #aborts ongoing commands
        self.FDIStart           = "INIT" #starts measurement
        self.FDIReset           = "*RST" #resets to default configurations
        self.FDIIdn             = "*IDN?" #returns identification and firmware version
        #Status registers:
        self.FDIClearStatus     = "*CLS" #clears status registers
        self.FDIStatusEn        = "*SRE " #enable bits in Status Byte
        self.FDIStatus          = "*STB?" #read Status Byte
        self.FDIEventEn         = "*ESE " #enable bits in Standard Event Status Register
        self.FDIEvent           = "*ESR?" #read Standard Event Status Register
        self.FDIOperEn          = "STAT:OPER:ENAB " #enable bits in OPERation Status
        self.FDIOper            = "STAT:OPER?" #read OPERation Status
        self.FDIQuesEn          = "STAT:QUES:ENAB " #enable bits in QUEStionable Status
        self.FDIQues            = "STAT:QUES?" #read QUEStionable Status
        self.FDIOpc             = "*OPC" #set operation complete bit

    def connect(self, bench=1):
        try:
            _bench1 = 'TCPIP0::FDI2056-0004::inst0::INSTR'
            _bench2 = 'TCPIP0::FDI2056-0005::inst0::INSTR'
            if bench == 1:
                _name = _bench1
            else:
                _name = _bench2
            self.inst = self.rm.open_resource(_name.encode('utf-8'))
            self.status_config()
            self.send(self.FDIShortCircuitOff)
            return True
        except:
            return False

    def disconnect(self):
        try:
            self.inst.close()
            return True
        except:
            return False

    def send(self,command):
        try:
            self.inst.write(command + '\n')
            return True
        except:
            return False

    def read(self):
        try:
            _ans = self.inst.read()
        except:
            _ans = ''
        return _ans

    def read_encoder(self):
        try:
            self.send(self.FDIReadEncoder)
            _ans = self.read().strip('\n')
            return _ans
        except:
            return ''

    def config_encoder(self, encoder_pulses):
        self.send(self.FDIConfigEncoder + str(encoder_pulses) + "'")
        self.send(self.FDIArmEncoder)
        self.send(self.FDITriggerSource)

    def config_measurement(self, encoder_pulses, gain, direction, trigger_ref, integration_points, n_of_turns):
        _trig_count = str(integration_points*n_of_turns)
        _trig_interval = str(round(encoder_pulses/integration_points))

        self.config_encoder(int(encoder_pulses/4))
        self.send(self.FDIGain + str(gain))
        self.send(self.FDIArmRef+str(trigger_ref))
        if direction == 0:
            self.send(self.FDITriggerDir + 'BACK')
        else:
            self.send(self.FDITriggerDir + 'FOR')
        self.send(self.FDITriggerCount + _trig_count)
        self.send(self.FDITriggerECount + _trig_interval)
        self.send(self.FDICalcFlux)

    def start_measurement(self):
        self.send(self.FDIStop + ';' + self.FDIStart)

    def calibrate(self):
        self.send(self.FDIShortCircuitOn)
        self.send(self.FDICalibrate)
        self.send(self.FDIShortCircuitOff)

    def get_data(self):
        _ans = str(self.get_data_count())
        self.send(self.FDIFetchArray + _ans + ', 12')
        _ans = self.read()
        return _ans

    def get_data_count(self):
        self.send(self.FDIDataCount)
        _ans = int(self.read().strip('\n'))
        return _ans

    def status(self, reg=0):
        if reg == 0:
            self.send(self.FDIStatus)
        elif reg == 1:
            self.send(self.FDIEvent)
        elif reg == 2:
            self.send(self.FDIOper)
        elif reg == 3:
            self.send(self.FDIQues)
        _ans = self.read()
        _ans = bin(int(_ans.strip('\n')))[2:]
        return _ans

    def status_config(self):
        self.send(self.FDIClearStatus)
        self.send(self.FDIStatusEn + '255')
        self.send(self.FDIEventEn + '255')
        self.send(self.FDIOperEn + '65535')
        self.send(self.FDIQuesEn + '65535')
