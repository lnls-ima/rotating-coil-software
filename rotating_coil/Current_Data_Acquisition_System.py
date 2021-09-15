'''
Created on 24 de ago de 2020

@author: labimas
'''
import sys
import time
import numpy as np
import traceback
import Agilent_34970A
import pydrs

from imautils.devices import Agilent34401ALib as multimeter

class Measurement_routine(object):
    def __init__(self):
        self.pydrs = pydrs.SerialDRS()
        self.agilent = Agilent_34970A.GPIB()
        self.multi34401 = multimeter.Agilent34401AGPIB()

    def ps_model(self):
        #self.ps_modelo = self.pydrs.get_ps_name().split('1000')[0]
        self.ps_modelo = 'F1000A'

    def connect_devices(self, addr_source='COM25', addr_channel=18):
        '''Connect both devices, COM25, 18'''
        try:
            self.agilent.connect(addr_channel)
            self.multi34401.connect(15, board=1)
            self.pydrs.Connect(addr_source)
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def start_ps_f1000(self):
        try:
            _drs = self.pydrs
            _drs.SetSlaveAdd(2)     # Input stage AC/DC
            print('Mudando endereço AC/DC: {}'.format(_drs.GetSlaveAdd()))
            _drs.turn_on()
            print('Ligando estágio de entrada (AC/DC): {}'.format(
                _drs.read_ps_onoff()))
            time.sleep(1)
            _drs.closed_loop()
            print('Verificando loop aberto: {}'.format(
                _drs.read_ps_openloop()))
            time.sleep(1)
            _dclink_value = 90
            _drs.set_slowref(_dclink_value)    # Set 90V bank

            _i = 100
            _feedback_DCLink = _drs.read_vdclink()
            while _feedback_DCLink < _dclink_value and _i > 0:
                _feedback_DCLink = _drs.read_vdclink()
                print('Setting DClink: {}'.format(round(float(_feedback_DCLink),
                                                        3)))
                time.sleep(0.5)
                _i = _i - 1
            print('DClink final: {}'.format(round(float(_feedback_DCLink),
                                                  3)))
            #Change to power stage
            _drs.SetSlaveAdd(1)     # Output stage DC/DC
            print('Mudando endereço DC/DC: {}'.format(_drs.GetSlaveAdd()))
            time.sleep(1)
            _drs.turn_on()
            print('Ligando estágio de saída (DC/DC): {}'.format(
                _drs.read_ps_onoff()))
            time.sleep(1)
            _drs.closed_loop()
            print('Verificando loop aberto: {}'.format(
                _drs.read_ps_openloop()))
            time.sleep(1)
            print('\n')
            print('Fonte ligada!')
            print(_drs.read_ps_status())

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def disconnect_devices(self):
        '''Disconnect both devices'''
        try:
            self.agilent.disconnect()
            self.pydrs.Disconnect()
            self.multi34401.disconnect()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def config_volt_meas(self):
        '''Configure volt reading to Agilent 34970A/34401A'''
        self.agilent.config_volt()
        self.multi34401.config()

    def read_dcct_volt(self):
        '''Ready to read dcct measurement'''
        _coleta_dcct = self.agilent.read_temp_volt()
        _coleta_dcct = float(_coleta_dcct[0])*32
        return _coleta_dcct

    def read_current_power_supply(self):
        _coleta_ps = self.pydrs.read_iload1()
        return _coleta_ps

    def read_agilent34401A(self):
        _coleta_34401A = self.multi34401.read()
        return _coleta_34401A*100

    def set_current(self, setpoint):
        try:
            if setpoint > 150:
                setpoint = 150
            self.pydrs.set_slowref(setpoint)
            time.sleep(0.1)
            for _ in range(30):
                _compare = round(float(self.pydrs.read_iload1()), 3)
                if abs(_compare - setpoint) <= 0.5:
                    return True
                time.sleep(1)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False
        
    def datetime(self):
        timestamp = time.strftime("%y-%m-%d_%H:%M:%S", time.localtime())
        return timestamp

    def start_meas(self, setpoint, timer=100):
        try:
            if isinstance(setpoint, (float, int)):
                if self.set_current(setpoint):
                    time.sleep(4)       # Wait until stability current

                    #PS name
                    self.ps_model()

                    #Arrays
                    self.array_ps = np.array([])
                    self.array_dcct = np.array([])
                    self.array_34401A = np.array([])

                    #Creating external log file
                    file = open("log_"+str(self.ps_modelo)+"@"+str(setpoint)+"A.txt",
                                "w")
                    file.write("## SAIDA DE LEITURA DAS CORRENTES ##")
                    file.write('\n')
                    file.write('Time:        \t'+'F1000A:        \t' +
                               '34970A DCCT(320A):        \t' + '34401A DCCT (1000A):' + '\n')

                    while timer > 0:
                        _time = self.datetime()
                        _val_1 = self.read_current_power_supply()
                        self.array_ps = np.append(self.array_ps, float(_val_1))
                        #print('FAC1K1: %0.6f' % _val_1)
                        _val_2 = self.read_dcct_volt()
                        self.array_dcct = np.append(self.array_dcct, float(_val_2))
                        print('34970A: %0.6f' % _val_2)
                        _val_3 = self.read_agilent34401A()
                        self.array_34401A = np.append(self.array_34401A, float(_val_3))
                        print('34401A: %0.6f' % _val_3)
                        time.sleep(1)
                        timer -= 1
                        file.write(str(_time) + '\t' +
                                   str('{0:+0.6e}'.format(_val_1)) + '\t' +
                                   str('{0:+0.6e}'.format(_val_2)) + '\t' +
                                   str('{0:+0.6e}'.format(_val_3)) + '\n')
                    file.close()
                else:
                    print('Falha no ajuste do setpoint')
                    traceback.print_exc(file=sys.stdout)
            else:
                print('Input Error. Please, enter with a valid number.')
                return False
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False


if __name__ == '__main__':
    a = Measurement_routine()
