# -*- coding: utf-8 -*-
"""
Created on 28/08/2012
Upgraded on 22/11/2017
Versão 2.0
@author: James Citadini
Comments : code does not check adjusts
"""
# Importa bibliotecas
import serial
import time
# ******************************************

class SerialCom(object):
    def __init__(self, port):
        self.ser = serial.Serial(port)
        self.commands()
        
    def commands(self):
        self.move  = 'G' # {Command to move motor}
        self.stop  = 'S' # {Command to stop motor}
        self.dist   = 'D' # {Command to set distance}
        self.speed    = 'V' # {motor speed}
        self.acce    = 'A' # {motor acceleration}
        self.status = 'CR' # {motor status}
        self.continuousmode = 'MC' # {motor mode continuous}
        self.manualmode = 'MN' # {motor mode manual}
        self.direction = 'H' # {motor direction}
        self.EOC_Off = 'LD3' # {disable end of course}
        self.EOC_On = 'LD0' # {enable end of course}
        self.kill = 'K' # {emergency stop}
        self.setresolution = 'MR' # {set motor resolution}
        self.istatus = 'IS' # {read input status}
        
    def connect(self,baudrate=9600,timeout=0.01):
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = timeout
        
        if not self.ser.isOpen():
            self.ser.open()
    
    def disconnect(self):
        self.ser.close()
    
    def flushTxRx(self):
        self.ser.flushInput()
        self.ser.flushOutput()
    
    def conf_mode(self,driver_add, mode, direction):
        self.flushTxRx()
        # Adjust manual (0) or continuous mode (1)
        if (mode == 0):
            adjust = str(driver_add) + self.manualmode + '\r'
        else:
            adjust = str(driver_add) + self.continuousmode + '\r'

        self.ser.write(adjust.encode('utf-8'))

        # Adjust clockwise (0) or counterclockwise direction (1)
        if (direction == 0):
            adjust = str(driver_add) + self.direction + '+\r'
        else:
            adjust = str(driver_add) + self.direction + '-\r'

        self.ser.write(adjust.encode('utf-8'))
            
    def conf_motor(self, driver_add, resolution, speed, acceleration, steps, direction, mode = 0):
        self.flushTxRx()

        # set resolution
        adjust = str(driver_add) + self.setresolution + str(resolution) + '\r'
        self.ser.write(adjust.encode('utf-8'))

        # Enable end of course
        adjust = str(driver_add) + self.EOC_On + '\r'
        self.ser.write(adjust.encode('utf-8'))

        # Configure Driver
        if mode == 0:
            adjust = str(driver_add) + self.manualmode + '\r'
        else:
            adjust = str(driver_add) + self.continuousmode + '\r'            
        self.ser.write(adjust.encode('utf-8'))
        
        adjust = str(driver_add) + self.speed + str(speed) + '\r'
        self.ser.write(adjust.encode('utf-8'))
        
        adjust = str(driver_add) + self.acce + str(acceleration) + '\r'
        self.ser.write(adjust.encode('utf-8'))

        adjust = str(driver_add) + self.dist + str(steps) + '\r'
        self.ser.write(adjust.encode('utf-8'))

        # Adjust clockwise (0) or counterclockwise direction (1)
        if (direction == 0):
            adjust = str(driver_add) + self.direction + '+\r'
        else:
            adjust = str(driver_add) + self.direction + '-\r'
        self.ser.write(adjust.encode('utf-8'))            

    def stopmotor(self,driver_add):
        self.flushTxRx()
        # Para o motor
        adjust = str(driver_add) + self.stop + '\r'
        self.ser.write(adjust.encode('utf-8'))

    def movemotor(self,driver_add):
        self.flushTxRx()
        # Mover o motor n passos
        adjust = str(driver_add) + self.move + '\r'
        self.ser.write(adjust.encode('utf-8'))

    def ready(self,driver_add):
        self.flushTxRx()
        adjust = str(driver_add) + self.status + '\r'
        self.ser.write(adjust.encode('utf-8'))
        time.sleep(0.01)
        result = str(self.ser.read(100).decode('utf-8'))
        if (result.find('\r\r') >= 0):
            return True
        else:
            return False
        
    def limits(self,driver_add):
        self.flushTxRx()
        _adjust = str(driver_add) + self.istatus + '\r'
        self.ser.write(_adjust.encode('utf-8'))
        time.sleep(0.25)
        _result = self.ser.read_until('\r').decode('utf-8')
        if _result[10:12] == '11':
            return True
        else:
            return False

    def kill(self):
        self.flushTxRx()
        adjust = self.kill + '\r'
        self.ser.write(adjust.encode('utf-8'))

    def setresolution(self,driver_add,resolution):
        self.flushTxRx()
        adjust = str(driver_add) + self.setresolution + str(int(resolution)) + '\r'
        self.ser.write(adjust.encode('utf-8'))

    def test_motor(self):
        for i in range(1,9,1):
            self.conf_mode(i,0,0)
            self.conf_motor(i,1,1,50000)
            self.movemotor(i)
            print(i)
            time.sleep(5)
        
