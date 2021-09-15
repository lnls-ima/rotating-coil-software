# -*- coding: utf-8 -*-
"""
Created on 11/01/2013
Update on 23/11/2017
Versao 1.0
@author: James Citadini
@coauthor: Vitor Soares
"""
# Importa bibliotecas
import serial
import time
import visa
# ******************************************


class SerialCom(object):
    def __init__(self, port):
        self.ser = serial.Serial(port)
        self.commands()
        self.delay = 0.2

    def commands(self):

        #Library - Integrator
        #Habilita a procura de indice do integrador
        self.PDISearchIndex = 'IND'
        #Inicia coleta com o integrador
        self.PDIStart = 'RUN'
        #Para coleta com o integrador
        self.PDIStop = 'BRK'
        #Le status do integrador binario
        self.PDIReadStatus = 'STB,'
        #Le status do integrador hexa
        self.PDIReadStatusHex = 'STH,'
        #Busca Resultados do integrador
        self.PDIEnquire = 'ENQ'
        #Escolha de Canal
        self.PDIChannel = 'CHA,A'
        #Configura ganho integrador
        self.PDIGain = 'SGA,A,'
        #Limpa Saturacao
        self.PDIClearStatus = 'CRV,A'
        #Tipo de Trigger encoder incremental rotativo
        self.PDITriggerEncoder = 'TRS,E,'
        #Configura integrador por tempo sem trigger externo - Default
        self.PDITriggerTimer = 'TRS,T'
        #Configura integrador por trigger externo
        self.PDITriggerExternal = 'TRS,X'
        #Sequencia Trigger -
        self.PDITriggerSeqNeg = 'TRI,-,'
        #Sequencia Trigger +
        self.PDITriggerSeqPos = 'TRI,+,'
        #Configura Dados para serem armazenados em blocos
        self.PDIStoreBlockEnd = 'IMD,0'
        #Configura Dados para serem armazenados e coletados
        self.PDIStoreBlockDuring = 'IMD,1'
        #Configura Dados para serem armazenados
        self.PDIStoreCum = 'CUM,0'
        #Zerar contador de pulsos
        self.PDIClearCounter = 'ZCT'
        #End of Data
        self.PDIEndofData = 'EOD'
        # Sincroniza
        self.PDISincronize = 'SYN,1'
        # Offset on
        self.PDIOffsetOn = 'ADJ,A,1'
        # Offset off
        self.PDIOffsetOff = 'ADJ,A,0'
        # reading Pulso Encoder
        self.PDIReadEncoder = 'RCT'
        # Set FDI Resolution
        self.FDIResolution = 'FCT,1E12'
        # Short Circuit On
        self.PDIShortCircuitOn = 'ISC,A,1'
        # Short Circuit Off
        self.PDIShortCircuitOff = 'ISC,A,0'

    def connect(self):
        # 9600
        self.ser.baudrate = 115200
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

    def send(self, comando):
        self.flushTxRx()
        adjust = comando + '\r'
        self.ser.write(adjust.encode('utf-8'))

    def read(self, n):
        try:
            if n == 0:
                reading = self.ser.readall()
            else:
                reading = self.ser.read(n)
            reading = reading.decode('utf-8')
            reading = reading.replace('\r\n', '')
        except:
            reading = ''

        return reading

    def status(self, registrador):
        self.send(self.PDIReadStatus + registrador)
        time.sleep(0.1)
        reading = self.read(10)
        return reading

    def statusHex(self, registrador):
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

    def config_encoder(self, encoder_pulses):
        self.send(self.PDITriggerEncoder + str(encoder_pulses))

    def index_search(self, direction):
        if direction == 0:
            self.send(self.PDISearchIndex + str(',+'))
        else:
            self.send(self.PDISearchIndex + str(',-'))

    def config_measurement(self, encoder_pulses, direction, trigger_ref,
                           integration_points, n_of_turns):
        # stop all commands and measurements
        self.send(self.PDIStop)
        time.sleep(self.delay)

        self.config_encoder(int(encoder_pulses/4))

        # configure interval and direction
        interval = int(encoder_pulses / integration_points)
        if direction == 0:
            self.send(self.PDITriggerSeqNeg + str(trigger_ref) + '/' +
                      str(integration_points*n_of_turns) + ',' + str(interval))
        else:
            self.send(self.PDITriggerSeqPos + str(trigger_ref) + '/' +
                      str(integration_points*n_of_turns) + ',' + str(interval))
        time.sleep(self.delay)

        #configure storage - flux values can be read during the measurement.
#         self.send(self.PDIStoreBlockDuring)

        # configure storage - flux values cannot be read during the measurement
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
            # read_all
            reading = self.read(0)
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
        # le posicao do encoder
        self.FDIReadEncoder = "CONTR:ENC:POS?"
        # configura encoder
        self.FDIConfigEncoder = "CONTR:ENC:CONF 'DIFF,/A:/B:IND,ROT:"
        # retorna comprimento do buffer de fluxo
        self.FDIDataCount = "DATA:COUN?"
        # configura encoder como fonte de trigger_ref
        self.FDIArmEncoder = "ARM:SOUR ENC"
        # configura trigger_ref
        self.FDIArmRef = "ARM:ENC "
        # configura integrais parciais (integra somente entre triggers)
        self.FDICalcFlux = "CALC:FLUX 0"
        # disable timestamp
        self.FDIDisableTime = "FORM:TIMESTAMP:ENABLE 0"
        # lê buffer de fluxo
        self.FDIFetchArray = "FETC:ARR? "
        # Short circuit on
        self.FDIShortCircuitOn = "INP:COUP GND"
        # Short circuit off
        self.FDIShortCircuitOff = "INP:COUP DC"
        # configure gain
        self.FDIGain = "INP:GAIN "
        # saves current configuration in hd
        self.FDIStoreConfig = "MEM:STOR"
        # deletes current configuration in hd
        self.FDIDelConfig = "MEM:DEL"
        # same as FetchArray but sends ABORt;INIT before fetching the array
        self.FDIReadArray = "READ:ARR? "
        # calibrates offset and slope for all gains
        self.FDICalibrate = "SENS:CORR:ALL"
        # configures encoder as trigger source
        self.FDITriggerSource = "TRIG:SOUR ENC"
        # configures number of triggers to complete a measurement
        self.FDITriggerCount = "TRIG:COUN "
        # number of enconder pulses to generate a trigger
        self.FDITriggerECount = "TRIG:ECO "
        # configures trigger direction as FORward or BACKward
        self.FDITriggerDir = "TRIG:ENC "
        # returns system errors until all errors are read
        self.FDIError = "SYST:ERR?"
        # aborts ongoing commands
        self.FDIStop = "ABORT"
        # starts measurement
        self.FDIStart = "INIT"
        # resets to default configurations
        self.FDIReset = "*RST"
        # returns identification and firmware version
        self.FDIIdn = "*IDN?"
        #Status registers:
        # clears status registers
        self.FDIClearStatus = "*CLS"
        # enable bits in Status Byte
        self.FDIStatusEn = "*SRE "
        # read Status Byte
        self.FDIStatus = "*STB?"
        # enable bits in Standard Event Status Register
        self.FDIEventEn = "*ESE "
        # read Standard Event Status Register
        self.FDIEvent = "*ESR?"
        # enable bits in OPERation Status
        self.FDIOperEn = "STAT:OPER:ENAB "
        # read OPERation Status
        self.FDIOper = "STAT:OPER?"
        # enable bits in QUEStionable Status
        self.FDIQuesEn = "STAT:QUES:ENAB "
        # read QUEStionable Status
        self.FDIQues = "STAT:QUES?"
        # set operation complete bit
        self.FDIOpc = "*OPC"

    def connect(self, bench=1):
        try:
            _bench1 = 'TCPIP0::FDI2056-0004::inst0::INSTR'
            _bench2 = 'TCPIP0::FDI2056-0005::inst0::INSTR'
            if bench == 1:
                _name = _bench1
            else:
                _name = _bench2
            self.inst = self.rm.open_resource(_name)
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

    def send(self, command):
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

    def config_measurement(self, encoder_pulses, gain, direction, trigger_ref,
                           integration_points, n_of_turns):
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
        self.send(self.FDIDisableTime)

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
