#!/usr/bin/python
# -*- coding: utf-8 -*-

# Remainders:

# sys.path.append(str(sys.path[0])+str('\\PUC_2v6')) ## Nome da pasta com biblioteca da PUC

import time
import threading
import numpy as np
import pandas as pd
import traceback
import serial.tools.list_ports
# import ctypes
# import matplotlib.pyplot as plt

# import traceback
import sys
from PyQt5 import QtWidgets,QtCore #QtWidgets

from Rotating_Coil_Interface_v3 import Ui_RotatingCoil_Interface
from Pop_up import Ui_Pop_Up
import Rotating_Coil_Library as Library
import Display_Heidenhain
import Parker_Drivers
import FDI2056
import Agilent_33220A
import Agilent_34401A
import Agilent_34970A
import SerialDRS

import pyqtgraph as pg

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_RotatingCoil_Interface()
        self.ui.setupUi(self)
        
        self.signals()

        self.refresh_interface()

    def signals(self):
        for i in range(1,self.ui.tabWidget.count()):
            self.ui.tabWidget.setTabEnabled(i,False)    #Lock main Tabs
        
        # Connection Tab 
#         self.ui.cb_display_type
#         self.ui.cb_disp_port
#         self.ui.cb_driver_port
#         self.ui.cb_integrator_port
#         self.ui.cb_ps_type
#         self.ui.cb_ps_port
#         self.ui.sb_ps_address
#         
#         self.ui.chb_enable_Agilent33220A
#         self.ui.sb_agilent33220A_address
#         self.ui.lb_status_33220A
#         
#         self.ui.chb_enable_Agilent34401A
#         self.ui.sb_agilent34401A_address
#         self.ui.lb_status_34401A
# 
#         self.ui.chb_enable_Agilent34970A
#         self.ui.sb_agilent34970A_address
#         self.ui.lb_status_34970A
        
        self.ui.pb_connect_devices.clicked.connect(self.connect_devices) # Ok
        
        # Settings Tab
#         self.ui.le_total_number_of_turns
#         self.ui.le_remove_initial_turns
#         self.ui.le_remove_final_turns
#         
#         self.ui.le_ref_encoder_A
#         self.ui.le_ref_encoder_B
#         
#         self.ui.le_rotation_motor_address
#         self.ui.le_rotation_motor_resolution        
#         self.ui.le_rotation_motor_speed
#         self.ui.le_rotation_motor_acceleration
#         self.ui.le_rotation_motor_ratio
#         
#         self.ui.le_poscoil_assembly
#         self.ui.le_n_encoder_pulses
#         
#         self.ui.cb_integrator_gain
#         self.ui.cb_n_integration_points
#         
#         self.ui.chb_save_turn_angles
#         self.ui.chb_disable_aligment_interlock
#         self.ui.chb_disable_ps_interlock
        self.ui.pb_save_config.clicked.connect(self.save_config) # Ok
        self.ui.pb_config.clicked.connect(self.config) # Ok
        self.ui.pb_emergency1.clicked.connect(self.emergency) 
        
        # Motors and Integrator Tab
#         self.ui.cb_driver_mode
#         self.ui.cb_driver_direction
#         self.ui.le_motor_vel
#         self.ui.le_motor_ace
#         self.ui.le_motor_turns
        self.ui.pb_move_motor.clicked.connect(self.move_motor_manual) # Ok
        self.ui.pb_stop_motor.clicked.connect(self.stop_motor) # Ok

#         self.ui.le_encoder_reading
        self.ui.pb_encoder_reading.clicked.connect(self.encoder_reading) # Ok
        
#         self.ui.le_encoder_setpoint
        self.ui.pb_move_to_encoder_position.clicked.connect(self.move_to_encoder_position) # Ok

        self.ui.pb_adjust_offset.clicked.connect(self.adjust_offset) # Ok
        
#         self.ui.label_status_1
#         self.ui.label_status_2
#         self.ui.label_status_3
#         self.ui.label_status_4
#         self.ui.label_status_5
#         self.ui.label_status_6
#         self.ui.label_status_7
        self.ui.pb_status_update.clicked.connect(self.status_update) # Ok
                
        self.ui.pb_emergency2.clicked.connect(self.emergency)
        
        # Coil Tab
#         self.ui.le_coil_name
#         self.ui.le_n_turns_normal
#         self.ui.le_radius1_normal 
#         self.ui.le_radius2_normal
#         self.ui.le_n_turns_bucked
#         self.ui.le_radius1_bucked
#         self.ui.le_radius2_bucked
#         self.ui.cb_coil_type
#         self.ui.te_comments
#         self.ui.le_trigger_ref
        self.ui.pb_get_coil_ref.clicked.connect(self.get_coil_ref) # Ok
        self.ui.pb_load_coil.clicked.connect(self.load_coil) # Ok
        self.ui.pb_save_coil.clicked.connect(self.save_coil) # Ok
        self.ui.pb_emergency3.clicked.connect(self.emergency)
        
        # Power Supply tab
        self.ui.pb_PS_button.clicked.connect(self.start_powersupply) #Ok
        self.ui.pb_refresh.clicked.connect(self.display_current) #Ok
        self.ui.pb_load_PS.clicked.connect(self.load_PowerSupply) #Ok
        self.ui.pb_save_PS.clicked.connect(self.save_PowerSupply)
        self.ui.pb_send.clicked.connect(self.linear_manual_ramp) #Ok
        self.ui.sb_ps_address.valueChanged.connect(self.update_seraddress)
        self.ui.pb_rows_auto.clicked.connect(self.add_rows) #Ok
        self.ui.pb_send_curve.clicked.connect(self.send_curve) #Ok
        self.ui.pb_config_PID.clicked.connect(self.pid_Setting) #Ok
        self.ui.pb_reset_inter.clicked.connect(self.reset_interlocks)
        self.ui.pb_cicle.clicked.connect(self.cycling_PS)

        # Measurements Tab
#         self.ui.chb_seriesofmeas
#         self.ui.le_n_series
#         self.ui.chb_automatic_ps
#         
#         self.ui.le_norm_radius
#         self.ui.cb_coil_rotation_direction
#         self.ui.lb_status_ps
#         self.ui.lb_status_coil
#         self.ui.lb_status_integrator
#         self.ui.lb_meas_counter
        self.ui.pb_start_meas.clicked.connect(self.popup_meas)
        self.ui.pb_stop_meas.clicked.connect(self.stop_meas)
        
        # Results Tab
        self.ui.pb_save_data_results.clicked.connect(self.save_data_results)
        
    def connect_devices(self):
        """
        connect devices and check status
        """
        try:
            # connect display
            Lib.comm.display = Display_Heidenhain.SerialCom(Lib.get_value(Lib.data_settings,'disp_port',str),'ND-780')
            Lib.comm.display.connect()
    
            # connect driver 
            Lib.comm.parker = Parker_Drivers.SerialCom(Lib.get_value(Lib.data_settings,'driver_port',str))
            Lib.comm.parker.connect()
    
            # connect integrator
            Lib.comm.fdi = FDI2056.SerialCom(Lib.get_value(Lib.data_settings,'integrator_port',str))
            Lib.comm.fdi.connect()
            
            # connect agilent 33220a - function generator
            if self.ui.chb_enable_Agilent33220A.checkState() != 0:
                self.ui.sb_agilent33220A_address.setEnabled(True)        
                Lib.comm.agilent33220a = Agilent_33220A.GPIB()
                Lib.comm.agilent33220a.connect(Lib.get_value(Lib.data_settings,'enable_Agilent33220A',int))
                self.ui.lb_status_33220A.setText('Connected')        
    
            # connect agilent 34401a - voltmeter
            if self.ui.chb_enable_Agilent34401A.checkState() != 0:
                self.ui.sb_agilent34401A_address.setEnabled(True)        
                Lib.comm.agilent34401a = Agilent_34401A.GPIB()
                Lib.comm.agilent34401a.connect(Lib.get_value(Lib.data_settings,'enable_Agilent34401A',int))        
                self.ui.lb_status_34401A.setText('Connected')        
    
            # connect agilent 34970a - multichannel
            if self.ui.chb_enable_Agilent34970A.checkState() != 0:
                self.ui.sb_agilent34970A_address.setEnabled(True)                        
                Lib.comm.agilent34970a = Agilent_34970A.GPIB()
                Lib.comm.agilent34970a.connect(Lib.get_value(Lib.data_settings,'enable_Agilent34970A',int))
                self.ui.lb_status_34970A.setText('Connected')
                 
            # connect digital power supply
            Lib.comm.drs = SerialDRS.SerialDRS_FBP()
            Lib.comm.drs.Connect(Lib.get_value(Lib.data_settings,'ps_port',str))
            
            QtWidgets.QMessageBox.information(self,'Information','Devices connected.',QtWidgets.QMessageBox.Ok)
            self.ui.pb_connect_devices.setText('Devices connected')
            for i in range(1,7):
                self.ui.tabWidget.setTabEnabled(i,True)            # Unlock main Tabs
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Fail to connect devices',QtWidgets.QMessageBox.Ok)
                        
    def save_config(self): # Ok
        """
        save settings in external file
        """
        self.config_variables()
        Lib.save_settings()

    def config(self): # Ok
        """
        config interface data into variables
        """
        self.config_variables()
    
    def emergency(self):
        """
        """
        pass
        
    def emergency_powersupply(self):
        """
        Stop PS in emergency case
        """
        if Lib.vars.Status_PS == 1:
            if Lib.vars.PS_cicle == 1:
                Lib.comm.drs.TurnOff()
                time.sleep(.1)
            Lib.comm.drs.OpMode(0)
            Lib.comm.drs.SetISlowRef(0)
            Lib.comm.drs.TurnOff()           # Turn off PS output
            its_worked = Lib.comm.drs.Read_ps_OnOff()
            if its_worked == 0:
                QtWidgets.QMessageBox.critical(self,'Warning','Emergency situation. \nPower Supply turned off.',QtWidgets.QMessageBox.Ok)                 
            time.sleep(.1)
        Lib.vars.Status_Fonte = 0
        Lib.vars.PS_cicle = 0
        
    def update_seraddress(self):
        Lib.comm.drs.SetSlaveAdd(self.ui.sb_ps_address.value())
    
    def start_powersupply(self):
        try:
            Addr_PS = int(self.ui.sb_ps_address.text())
            Lib.comm.drs.SetSlaveAdd(Addr_PS)
                        
            if self.ui.pb_PS_button.isChecked():
                self.ui.pb_PS_button.setText('Power ON')    
            else:
                #self.ui.pb_PS_button.setChecked(False)
                self.ui.pb_PS_button.setText('Power OFF')
            
            Safety_enabled = 1
            if (self.ui.chb_disable_ps_interlock.isChecked()) and (Lib.vars.Status_PS == 0):
                ret = QtWidgets.QMessageBox.question(self,'Attention','Do you want to turn on the Power Supply with Safety Control DISABLED?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.Yes:
                    Safety_enabled = 0
                else:
                    return
            if Lib.vars.Status_PS == 0:         # Status PS is OFF                
                try:
                    Lib.comm.drs.Read_iLoad1()
                except:
                    QtWidgets.QMessageBox.warning(self,'Warning','Impossible to read the digital current.',QtWidgets.QMessageBox.Ok)
                    return
                if Safety_enabled == 1:
                    status_interlocks = Lib.comm.drs.Read_ps_SoftInterlocks()
                    time.sleep(0.25)
                    if status_interlocks != 0:  
                        QtWidgets.QMessageBox.critical(self,'Attention','Soft Interlock activated!',QtWidgets.QMessageBox.Ok)
                        return
                    status_interlocks = Lib.comm.drs.Read_ps_HardInterlocks()
                    time.sleep(0.25)
                    if status_interlocks != 0:  
                        QtWidgets.QMessageBox.critical(self,'Attention','Hard Interlock activated!',QtWidgets.QMessageBox.Ok)
                        return
                    PSType = self.check_PS_type()
                    if PSType == 1:                     # PS 225 A
                        Lib.comm.drs.TurnOn()           # Turn ON the Digital Power Supply
                        time.sleep(0.5)
                        its_worked = Lib.comm.drs.Read_ps_OnOff()
                        if its_worked == 1:
                            Lib.vars.Status_PS = 1      # Status PS is ON
                            Lib.vars.Actual_current = 0
                            self.ui.tabWidget_2.setEnabled(True)
                            self.ui.tabWidget_3.setEnabled(True)
                            QtWidgets.QMessageBox.information(self,'Information','The Power Supply has started successfully.',QtWidgets.QMessageBox.Ok)
                            #return
                        else:
                            QtWidgets.QMessageBox.critical(self,'Attention','The Power Supply did not started.',QtWidgets.QMessageBox.Ok)
                            return
                        
                        # Closed Loop
                        Lib.comm.drs.ClosedLoop()       
                        time.sleep(0.5)
                        if (Lib.comm.drs.Read_ps_OpenLoop() == 1):
                            QtWidgets.QMessageBox.warning(self,'Attention',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                            #return
                        self.ui.le_status_fonte.setText('Closed')
                        self.ui.sb_ps_dclink.setEnabled(False)
                        self.ui.pb_refresh.setEnabled(True)
                        QtWidgets.QApplication.processEvents()
                    else:                               # PS 1000 A
                        addr_dclink = 1
                        Lib.comm.drs.SetSlaveAdd(addr_dclink)
                        time.sleep(.1)
                        # Turn ON PS DClink
                        try:
                            Lib.comm.drs.TurnOn()           # Turn ON the DC Link of the PS
                            time.sleep(.5)
                            its_worked = Lib.comm.drs.Read_ps_OnOff()
                            if (its_worked == 1):
                                QtWidgets.QMessageBox.information(self,'Information',"Power Supply Capacitor Bank turned on.",QtWidgets.QMessageBox.Ok)
                        except:
                            QtWidgets.QMessageBox.critical(self,'Attention',"Power Supply Capacitor Bank did not initialized",QtWidgets.QMessageBox.Ok)
                            return
                        
                        # Closing PS Loop
                        try:
                            Lib.comm.drs.ClosedLoop()        # Closed Loop
                            time.sleep(.5)
                            if (Lib.comm.drs.Read_ps_OpenLoop() == 1):
                                QtWidgets.QMessageBox.warning(self,'Attention',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                                return
                            else:
                                QtWidgets.QMessageBox.information(self,'Information',"Power Supply circuit loop is closed.",QtWidgets.QMessageBox.Ok)
                                return
                            self.ui.le_status_fonte.setText('Power On')
                        except:
                            QtWidgets.QMessageBox.warning(self,'Attention',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                            return
                        
                        # Set ISlowRef for DC Link (Capacitor Bank)
                        time.sleep(.2)
                        mode = 0
                        Lib.comm.drs.OpMode(mode)                     # Operation mode selection for Slowref
                        dclink_value = int(self.ui.sb_ps_dclink.text())
                        Lib.comm.drs.SetISlowRef(dclink_value)        # Set 30 V for Capacitor Bank (default value according to the ELP Group)
                        feedback_DCLink = float(Lib.comm.drs.Read_vDCMod1)
                        if feedback_DCLink == 0:
                            QtWidgets.QMessageBox.warning(self,'Attention',"Setpoint DC link is not set.",QtWidgets.QMessageBox.Ok)
                            return
                        QtWidgets.QApplication.processEvents()
            else:
                if not self.ui.pb_PS_button.isChecked():
                    self.ui.pb_PS_button.setText('Power Off')
                status = Lib.comm.drs.Read_ps_OnOff()
                if status == 1:
                    Lib.vars.Status_PS = 0              
                    Lib.vars.Actual_current = 0
                    Lib.comm.drs.TurnOff()                    # Turn OFF the Power Supply
                    self.ui.tabWidget_2.setEnabled(False)
                    self.ui.le_status_fonte.setText('Open')
                else:
                    Lib.comm.drs.TurnOff()
                    QtWidgets.QMessageBox.critical(self,'Attention','Digital Source did not receive the command.',QtWidgets.QMessageBox.Ok)
                    return
        except:
            QtWidgets.QMessageBox.critical(self,'Fail','Power Supply start failed.',QtWidgets.QMessageBox.Ok)
            return
            
    def check_PS_type(self):
        if self.ui.le_PS_type.text() == '225':
            PS_type = 1
        else:
            PS_type = 2
        return PS_type
    
    def pid_Setting(self):
        '''
        Set by software the PID configurations  
        '''
        addr_PS = int(self.ui.sb_ps_address.text())
        Lib.comm.drs.SetSlaveAdd(addr_PS)
        ID_mode = 0
        ELP_PI_dawu = 3
        try:
            Lib.comm.drs.Write_dp_ID(ID_mode)           #Write ID module from controller
            Lib.comm.drs.Write_dp_Class(ELP_PI_dawu)    #Write DP Class for setting PI 
        except:
            QtWidgets.QMessageBox.critical(self,'Fail','Power Supply PID configuration fault.',QtWidgets.QMessageBox.Ok)
            traceback.print_exc(file=sys.stdout)
            return
        try:
            list_coeffs = np.zeros(16)
            kp, ki = float(self.ui.sb_kp.text()), float(self.ui.sb_ki.text())
            list_coeffs[0] = kp
            list_coeffs[1] = ki
            Lib.comm.drs.Write_dp_Coeffs(list_coeffs.tolist())        #Write kp and ki
            Lib.comm.drs.ConfigDPModule()                             #Configure kp and ki
            QtWidgets.QMessageBox.information(self,'Success','PID configured.',QtWidgets.QMessageBox.Ok)

        except:
            QtWidgets.QMessageBox.critical(self,'Fail','Power Supply write PID fault. n/Try again.',QtWidgets.QMessageBox.Ok)
            traceback.print_exc(file=sys.stdout)
            return
            
    def dcct_convert(self):
        reading_34401 = Lib.comm.agilent34401a.collect()
        if reading_34401 =='':
            self.read_curr = 0
        else:
            if self.ui.dcct_select.currentIndex() == 0:   #For 40 A dcct head
                self.read_curr = (float(reading_34401))*4
            if self.ui.dcct_select.currentIndex() == 1:   #For 160 A dcct head
                self.read_curr = (float(reading_34401))*16
            if self.ui.dcct_select.currentIndex() == 2:   #For 320 A dcct head
                self.read_curr = (float(reading_34401))*32
        return self.read_curr
        
    def display_current(self):
        try:
            time.sleep(0.3)
            refresh_current = round(float(Lib.comm.drs.Read_iLoad1()),3)
            self.ui.lcd_PS_reading.display(refresh_current)
            if ((self.ui.chb_dcct.isChecked() == True) and (self.ui.chb_enable_Agilent34401A.checkState() != 0)):
                #time.sleep(.1)
                self.ui.lcd_current_dcct.setEnabled(True)
                self.ui.label_161.setEnabled(True)
                self.ui.label_164.setEnabled(True)
                corrente4 = round(self.dcct_convert(), 3)
                self.ui.lcd_current_dcct.display(corrente4)
                QtWidgets.QApplication.processEvents()
    
        except:
            QtWidgets.QMessageBox.warning(self,'Fail','Impossible display Current.',QtWidgets.QMessageBox.Ok)
            return
    
    def linear_ramp(self,final,actual,step,timer):
        mode = 0                    # OpMode ISlowRef
        Lib.comm.drs.OpMode(mode)
        #faixa = np.array([])
        try:
            delta = abs(final - actual)
            faixa = np.linspace(actual, final, round(delta/step)+1)
                                
            #===================================================================
            # if final > actual:
            #     faixa = np.arange(actual+step,final,step)
            # else:
            #     faixa = np.arange(final,actual,step)
            #     faixa = faixa[::-1]
            # faixa[-1] = final
            #===================================================================
            
            for i in faixa:
                if (Lib.vars.stop_all == 0):
                    #time = 0.1
                    time.sleep(timer)
                    Lib.comm.drs.SetISlowRef(i)
                else:
                    Lib.comm.drs.SetISlowRef(0)
                    time.sleep(0.1)
                    return False
            self.display_current()
            return True
        except:
            traceback.print_exc(file=sys.stdout)
            try:
                if ((final>actual) and ((final-actual)<step)) or ((final<actual) and ((actual-final)<step)):
                    Lib.comm.drs.SetISlowRef(final)
                    self.display_current()
                    return True
            except:
                return False
    
    def verify_current_limits(self, index, current, offset=0):
        '''
        Check the conditions of the Current values sets
        '''
        current = float(current)
        try:
            current_max = float(self.ui.le_maximum_current.text())
        except:
            QtWidgets.QMessageBox.warning(self, 'Attention', 'Incorrect value for maximum Supply Current.\nPlease, verify the value.',QtWidgets.QMessageBox.Ok)
            current = 'False'
            return (current)
        try:
            current_min = float(self.ui.le_minimum_current.text())
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Incorrect value for minimum Supply Current.\nPlease, verify the value.',QtWidgets.QMessageBox.Ok)
            current = 'False'
            return (current)
        
        if (index == 0) or (index == 1):
            if (current)>(current_max):
                if (index == 0):
                    QtWidgets.QMessageBox.warning(self,'Attention','Value of current higher than the Supply Limit.',QtWidgets.QMessageBox.Ok)
                current = current_max
            if (current)<(current_min):
                if (index == 0):
                    QtWidgets.QMessageBox.warning(self,'Attention','Current value lower than the Supply Limit.',QtWidgets.QMessageBox.Ok)
                current = current_min
        if (index == 2):
            if ((current/2)+offset) > (current_max):
                QtWidgets.QMessageBox.warning(self,'Attention','Check Peak to Peak Current and Offset values.\nValues out of source limit.',QtWidgets.QMessageBox.Ok)
                current = 'False'
                return (current)
            
            if ((-current/2)+offset) < (current_min):
                QtWidgets.QMessageBox.warning(self,'Attention','Check Peak to Peak Current and Offset values.\nValues out of source limit.',QtWidgets.QMessageBox.Ok)
                current = 'False'
                return (current)
            
        return(float(current)) 
              
    def linear_manual_ramp(self):
        actual = round(float(Lib.comm.drs.Read_iLoad1()),3)
        try:
            final_value = self.verify_current_limits(0, self.ui.dsb_current_setpoint.value())
            if final_value == 'False':
                return
            self.ui.dsb_current_setpoint.setValue(float(final_value))
            Lib.vars.Actual_current = self.ui.dsb_current_setpoint.value()
            step = self.ui.dsb_current_setpoint.value()
            time = self.ui.dsb_Time_Linear.value()
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Invalid values or not numeric.',QtWidgets.QMessageBox.Ok)
            self.ui.dsb_current_setpoint.setValue(float(0))
            #return
        self.ui.tabWidget_2.setEnabled(False)           #Disabled tabWidget until complete load current
        QtWidgets.QApplication.processEvents()
        
        ramp = self.linear_ramp(final_value, actual, step, time)
        
        if ramp == True:
            QtWidgets.QMessageBox.information(self,'Information','Select current successfully.',QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.critical(self,'Attention','Fail! \nVerify the Power Supply current values.',QtWidgets.QMessageBox.Ok)
        self.ui.tabWidget_2.setEnabled(True)
        QtWidgets.QApplication.processEvents()
        
    def linear_automatic_ramp(self, data_current, data_seletion_currents):
        try:
            step = self.ui.dsb_Amplitude_Linear.value()
            time = self.ui.dsb_Time_Linear.value()
        except:
            QtWidgets.QMessageBox.critical(self,'Attention','Invalid step or time values.',QtWidgets.QMessageBox.Ok)
            return
        for i in range (len(data_current)):
            if data_seletion_currents[i] == 'Y' or data_seletion_currents[i] == 'y' or data_seletion_currents[i] == 'S' or data_seletion_currents[i] == 's':
                actual_current = round(float(Lib.comm.drs.Read_iLoad1()),3)
                self.linear_ramp(data_current[i], actual_current, step, time)
                time.sleep(.2)
            else:
                if abs(data_current[i]-data_current[i-1])> step:
                    actual_current = round(float(Lib.comm.drs.Read_iLoad1()),3)
                    self.linear_ramp(data_current[i], actual_current, step, time)
                else:
                    Lib.comm.drs.SetISlowRef(data_current[i])
                       
        QtWidgets.QMessageBox.information(self,'Information','Automatic collect process done.',QtWidgets.QMessageBox.Ok)    
                            
    def send_curve(self):
        self.ui.tabWidget_2.setEnabled(False)
        if self.curve_gen() == True:
            QtWidgets.QMessageBox.information(self,'Information','Sending Curve Successfully.',QtWidgets.QMessageBox.Ok)
            self.ui.tabWidget_2.setEnabled(True)
            self.ui.pb_cicle.setEnabled(True)
            QtWidgets.QApplication.processEvents()
        else:
            QtWidgets.QMessageBox.critical(self,'Warning','Fail to Sending Curve.',QtWidgets.QMessageBox.Ok)
            self.ui.tabWidget_2.setEnabled(True)
            QtWidgets.QApplication.processEvents()
            return False
    
    def curve_gen(self):
        self.Curve_Type = int(self.ui.tabWidget_3.currentIndex())
                                            
        if self.Curve_Type == 0:    # Sinusoidal
            #For Offset
            try:
                self.offset = self.verify_current_limits(0, float(self.ui.le_Sinusoidal_Offset.text()))
                if (self.offset == 'False'):
                    self.ui.le_Sinusoidal_Offset.setText('0')
                    return False
                self.ui.le_Sinusoidal_Offset.setText(str(self.offset))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Offset parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Amplitude
            try:
                self.Amp = self.verify_current_limits(2,abs(float(self.ui.le_Sinusoidal_Amplitude.text())),self.offset)
                if self.Amp == 'False':
                    self.ui.le_Sinusoidal_Amplitude.setText('0')
                    return False
                self.ui.le_Sinusoidal_Amplitude.setText(str(self.Amp))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Amplitude parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Frequency
            try:
                self.freq = float(self.ui.le_Sinusoidal_Frequency.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Frequency parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For N-Cicles
            try:
                self.n_cicles = int(self.ui.le_Sinusoidal_n_cicles.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the #Cicles parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Phase shift
            try:
                self.phase_shift = float(self.ui.le_Initial_Phase.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Final phase
            try:
                self.Final_Phase = float(self.ui.le_Final_Phase.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Final phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            
        if self.Curve_Type == 1:    # Cushioned Sinusoidal
            #For Offset
            try:
                self.offset = self.verify_current_limits(0, float(self.ui.le_cush_sin_Offset.text()))
                if (self.offset == 'False'):
                    self.ui.le_cush_sin_Offset.setText('0')
                    return False
                self.ui.le_cush_sin_Offset.setText(str(self.offset))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Offset parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Amplitude
            try:
                self.Amp = self.verify_current_limits(2,abs(float(self.ui.le_cush_sin_Ampl.text())),self.offset)
                if self.Amp == 'False':
                    self.ui.le_cush_sin_Ampl.setText('0')
                    return False
                self.ui.le_cush_sin_Ampl.setText(str(self.Amp))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Amplitude parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Frequency
            try:
                self.freq = float(self.ui.le_cush_sin_Freq.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Frequency parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For N-Cicles
            try:
                self.n_cicles = int(self.ui.le_cush_sin_nCicles.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the #Cicles parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Phase shift
            try:
                self.phase_shift = float(self.ui.le_cush_sin_phaseShift.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Final phase
            try:
                self.Final_Phase = float(self.ui.le_cush_sin_finalPhase.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Final Phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Damping
            try:
                self.Damping = float(self.ui.le_cush_sin_Damping.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Damping time parameter of the curve.',QtWidgets.QMessageBox.Ok)
                
        if self.Curve_Type == 2:        # Triangular softened
            #For Offset
            try:
                self.offset = self.verify_current_limits(0, float(self.ui.le_softened_Offset.text()))
                if (self.offset == 'False'):
                    self.ui.le_softened_Offset.setText('0')
                    return False
                self.ui.le_softened_Offset.setText(str(self.offset))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Offset parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Amplitude
            try:
                self.Amp = self.verify_current_limits(2,abs(float(self.ui.le_softened_Ampl.text())),self.offset)
                if self.Amp == 'False':
                    self.ui.le_softened_Ampl.setText('0')
                    return False
                self.ui.le_softened_Ampl.setText(str(self.Amp))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Amplitude parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Frequency
            try:
                self.freq = float(self.ui.le_softened_Freq.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Frequency parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For N-Cicles
            try:
                self.n_cicles = int(self.ui.le_softened_nCicles.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the #Cicles parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Phase shift
            try:
                self.phase_shift = float(self.ui.le_softened_phaseShift.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Final phase
            try:
                self.Final_Phase = float(self.ui.le_softened_finalPhase.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Final phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
        
        if self.Curve_Type == 3:        # Arbitrary Curve
            #For Amplitude
            try:
                self.Amp = self.verify_current_limits(2,abs(float(self.ui.le_amplitude_arbitrary.text())),self.offset)
                if self.Amp == 'False':
                    self.ui.le_amplitude_arbitrary.setText('0')
                    return False
                self.ui.le_amplitude_arbitrary.setText(str(self.Amp))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Amplitude parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Frequency
            try:
                self.freq = float(self.ui.le_frequency_arbitrary.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Frequency parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For N-Cicles
            try:
                self.n_cicles = int(self.ui.le_nCicles_arbitrary.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the #Cicles parameter of the curve.',QtWidgets.QMessageBox.Ok)
                
        #Generating curves
        try:
            if self.Curve_Type == 0:        # Sinusoidal
                try:
                    sigType=0
                    mode=3          #Operating mode
                    Lib.comm.drs.OpMode(mode)
                    if Lib.comm.drs.Read_ps_OpMode()!=3:
                        QtWidgets.QMessageBox.warning(self,'Attention','Signal generator not configured correctly.',QtWidgets.QMessageBox.Ok)
                        return False
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention','Signal generator not configured correctly. Verify PS settings.',QtWidgets.QMessageBox.Ok)
                    return
                
                try:
                    Lib.comm.drs.Write_sigGen_Freq(float(self.freq))        #send Frequency
                    Lib.comm.drs.Write_sigGen_Amplitude(float(self.Amp))    #send Amplitude
                    Lib.comm.drs.Write_sigGen_Offset(float(self.offset))    #send Offset
                    #Sending curves to PS Controller
                    Lib.comm.drs.ConfigSigGen(sigType, self.n_cicles, self.phase_shift, self.Final_Phase)
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention','Fail to send config to Controller.\nPlease, verify the parameters of the Power Supply.',QtWidgets.QMessageBox.Ok)
                    return
                
            if self.Curve_Type == 1:        # Cushioned Sinusoidal
                try:
                    sigType=4
                    mode=3
                    Lib.comm.drs.OpMode(mode)
                    if (Lib.comm.drs.Read_ps_OpMode() != 3):
                        QtWidgets.QMessageBox.warning(self,'Attention','Signal generator not configured correctly.',QtWidgets.QMessageBox.Ok)
                        return False
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention','Signal generator not configured correctly. Verify PS settings.',QtWidgets.QMessageBox.Ok)
                    return
                
                try:
                    Lib.comm.drs.Write_sigGen_Freq(float(self.freq))             
                    Lib.comm.drs.Write_sigGen_Amplitude(float(self.Amp))         
                    Lib.comm.drs.Write_sigGen_Offset(float(self.offset))    
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention','Please, verify the parameters of the Power Supply.',QtWidgets.QMessageBox.Ok)
                    return
    
                #Sending sigGenAmortecido
                try:
                    Lib.comm.drs.Write_sigGen_Aux(float(self.ui.le_cush_sin_Damping.text()))
                    Lib.comm.drs.ConfigSigGen(sigType, self.n_cicles, self.phase_shift, self.Final_Phase)
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention.','Cushioned Sinusoidal fault.',QtWidgets.QMessageBox.Ok)
                    traceback.print_exc(file=sys.stdout)
                    return False
            
            return True
        except:
            return False
        
    def reset_interlocks(self):
        try:
            Lib.comm.drs.ResetInterlocks()
            if self.ui.pb_Hard_interlock.isChecked(): self.ui.pb_Hard_interlock.setChecked(False)
            if self.ui.pb_Soft_interlock.isChecked(): self.ui.pb_Soft_interlock.setChecked(False)
            QtWidgets.QMessageBox.information(self,'Information','Interlocks reseted.',QtWidgets.QMessageBox.Ok)
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Interlocks not reseted.',QtWidgets.QMessageBox.Ok)
            return
            
    def plot_curves(self):
        pass
    
    def cycling_PS(self):
        try:
            if self.Curve_Type == 0: Lib.comm.drs.EnableSigGen()
            if self.Curve_Type == 1:
                Lib.comm.drs.EnableSigGen()
                time.sleep(.2)
            deadline = time.monotonic() + (1/float(self.ui.le_cush_sin_Freq.text())*float(self.ui.le_cush_sin_nCicles.text()))
            while time.monotonic() < deadline:
                self.ui.tabWidget_2.setEnabled(False)
                self.ui.pb_start_meas.setEnabled(False)
                self.ui.pb_load_PS.setEnabled(False)
                self.ui.pb_refresh.setEnabled(False)
                QtWidgets.QApplication.processEvents()
            
            QtWidgets.QMessageBox.information(self,'Information','Successful cycle process.',QtWidgets.QMessageBox.Ok)
            Lib.comm.drs.DisableSigGen()
            self.ui.tabWidget_2.setEnabled(True)
            self.ui.pb_start_meas.setEnabled(True)
            self.ui.pb_load_PS.setEnabled(True)
            self.ui.pb_refresh.setEnabled(True)
            QtWidgets.QApplication.processEvents()
            
            if self.Curve_Type == 2:
                pass
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Cycling process not realized.',QtWidgets.QMessageBox.Ok)
            return       
    
    
    def move_motor_until_stops(self, address): # Ok
        """
        """
        Lib.flags.stop_all = False
        
        Lib.comm.parker.movemotor(address)

        while ( (Lib.comm.parker.ready(address) == False) and (Lib.flags.stop_all == False) ):
            Lib.comm.parker.flushTxRx()
            QtWidgets.QApplication.processEvents()
        
        Lib.flags.stop_all = False        
    
    def move_motor_manual(self): # Ok
        """
        """
        address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        _ratio = Lib.get_value(Lib.data_settings,'rotation_motor_ratio',float)

        resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)        
        vel = float(self.ui.le_motor_vel.text()) * _ratio
        acce = float(self.ui.le_motor_ace.text()) * _ratio
        nturns = float(self.ui.le_motor_turns.text()) * _ratio
        
        direction = self.ui.cb_driver_direction.currentIndex()
        steps = abs(int(nturns * Lib.get_value(Lib.data_settings,'rotation_motor_resolution',float)))
        
        # mode
        if self.ui.cb_driver_mode.currentIndex() == 0:
            _mode = 0
        else:
            _mode = 1

        Lib.comm.parker.conf_motor(address, resolution, vel, acce, steps, direction, _mode)
        
        self.move_motor_until_stops(address)

    def stop_motor(self): # Ok
        """
        """
        Lib.flags.stop_all = True        
        address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        Lib.comm.parker.stopmotor(address)
        
    def encoder_reading(self): # Ok
        """
        read encoder from integrator and update interface value
        """
        _val = Lib.comm.fdi.read_encoder()
        self.ui.le_encoder_reading.setText(_val)

    def pulses_to_go(self): # Ok
        """ """
        self.encoder_reading()
        _encoder_current = int(self.ui.le_encoder_reading.text())
        _encoder_setpoint = int(self.ui.le_encoder_setpoint.text())
        _pulses_to_go = _encoder_current - _encoder_setpoint 
        
        return _pulses_to_go
        
    def move_to_encoder_position(self): # Ok / implement automatic search in closed loop
        """
        """
        Lib.flags.stop_all = False
        
        address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        _ratio = Lib.get_value(Lib.data_settings,'rotation_motor_ratio',float)
        
        resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)
        vel = float(self.ui.le_motor_vel.text()) * _ratio
        acce = float(self.ui.le_motor_ace.text()) * _ratio
        
        _pulses = self.pulses_to_go()
        steps =  abs(int( _pulses * Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int) / Lib.get_value(Lib.data_settings,'n_encoder_pulses',int) * _ratio))

        if _pulses >= 0:
            direction = 0
        else:
            direction = 1

        Lib.comm.parker.conf_motor(address, resolution, vel, acce, steps, direction, 0)
        self.move_motor_until_stops(address)
             
        self.encoder_reading()  
        
    def adjust_offset(self): # Ok
        """
        """
        Lib.flags.stop_all = False
        
        Lib.comm.fdi.send(Lib.comm.fdi.PDIShortCircuitOn)
        time.sleep(0.5)
        
        Lib.comm.fdi.send(Lib.comm.fdi.PDIOffsetOn)
        
        while (int(Lib.comm.fdi.status('1')[-4]) != 1) and (Lib.flags.stop_all == False):
            QtWidgets.QApplication.processEvents()

        Lib.comm.fdi.send(Lib.comm.fdi.PDIOffsetOff)
        time.sleep(0.5)        
        Lib.comm.fdi.send(Lib.comm.fdi.PDIShortCircuitOff)

        QtWidgets.QMessageBox.information(self,'Information','Offset Integrator adjusted.',QtWidgets.QMessageBox.Ok)

    def status_update(self): # Ok
        """
        """
        try:
            self.ui.label_status_1.setText(Lib.comm.fdi.status('1'))
            self.ui.label_status_2.setText(Lib.comm.fdi.status('2'))
            self.ui.label_status_3.setText(Lib.comm.fdi.status('3'))
            self.ui.label_status_4.setText(Lib.comm.fdi.status('4'))
            self.ui.label_status_5.setText(Lib.comm.fdi.status('5'))
            self.ui.label_status_6.setText(Lib.comm.fdi.status('6'))
            self.ui.label_status_7.setText(Lib.comm.fdi.status('7'))
        except:
            pass
   
    def move_motor_measurement(self, turns): # Ok
        """ """
        address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        _ratio = Lib.get_value(Lib.data_settings,'rotation_motor_ratio',float)
        
        resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)
        vel = Lib.get_value(Lib.data_settings,'rotation_motor_speed',float) * _ratio
        acce = Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',float) * _ratio
#         nturns = float(self.ui.le_motor_turns.text()) * _ratio
        nturns = turns * _ratio        
        
        direction = self.ui.cb_coil_rotation_direction.currentIndex()
        steps = abs(int(nturns * Lib.get_value(Lib.data_settings,'rotation_motor_resolution',float)))
        
        _mode = 0
    
        Lib.comm.parker.conf_motor(address, resolution, vel, acce, steps, direction, _mode)
        
        self.move_motor_until_stops(address)
        
    def get_coil_ref(self): # Ok
        """
        """
        Lib.flags.stop_all = False
        
        _res = QtWidgets.QMessageBox.warning(self,'Search Index','Continue to search for coil index?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if _res == QtWidgets.QMessageBox.Yes:
            # configure integrator encoder
            _n_encoder_pulses = int(Lib.get_value(Lib.data_settings,'n_encoder_pulses',float)/4)
            Lib.comm.fdi.config_encoder(_n_encoder_pulses)
           
            # Send command to find integrator reference]
            direction = self.ui.cb_coil_rotation_direction.currentIndex()
            Lib.comm.fdi.index_search(direction)
            
            # Move Motor - 1 turn
            self.move_motor_measurement(turns=1)
            
            while (int(Lib.comm.fdi.status('1')[-1]) != 1) and (Lib.flags.stop_all == False):
                QtWidgets.QApplication.processEvents()
            
            Lib.flags.coil_ref_flag = True
            QtWidgets.QMessageBox.warning(self,'Search Index','Coil index search is done.',QtWidgets.QMessageBox.Ok)
        else:
            Lib.flags.coil_ref_flag = False
            QtWidgets.QMessageBox.warning(self,'Search Index','Coil index search is canceled',QtWidgets.QMessageBox.Ok)
            
    def load_coil(self): # Ok
        """
        """
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,'Load Coil File' , Lib.dir_path, 'Data files (*.dat);;Text files (*.txt)')
            if Lib.load_coil(filename[0]) == True:
                self.refresh_coiltab()
                QtWidgets.QMessageBox.information(self,'Information','Coil File loaded.',QtWidgets.QMessageBox.Ok)
                
            else:
                QtWidgets.QMessageBox.warning(self,'Attention','Fail to load Coil File.',QtWidgets.QMessageBox.Ok) 
        except:
            return
    
    def save_coil(self): # Ok
        """
        """
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self,'Save Coil File' , Lib.dir_path, 'Data files (*.dat);;Text files (*.txt)')
            
            self.config_coil()

            if Lib.save_coil(filename[0]) == True:
                QtWidgets.QMessageBox.information(self,'Information','Coil File saved.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Attention','Fail to save Coil File.',QtWidgets.QMessageBox.Ok) 
        except:
            return
        
    def save_PowerSupply(self):
        """
        save settings of the Power Supply in external file
        """
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Power Supply File', Lib.dir_path, 'Data files (*.dat);;Text files (*.txt)')
            
            self.config_PS()
            if Lib.save_PS(filename[0]) == True:
                QtWidgets.QMessageBox.warning(self,'Information','Power Supply File saved.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Information','Fail to save Power Supply File.',QtWidgets.QMessageBox.Ok) 
        except:
            return
        
    def load_PowerSupply(self):
        """
        load settings of the Power Supply in the interface
        """
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,'Load Power Supply File' , Lib.dir_path, 'Data files (*.dat);;Text files (*.txt)')
            if Lib.load_PS(filename[0]) == True:
                self.refresh_PS_settings()
                QtWidgets.QMessageBox.information(self,'Information','Power Supply File loaded.',QtWidgets.QMessageBox.Ok)
                #self.ui.tabWidget_2.setEnabled(True)
                #self.ui.tabWidget_3.setEnabled(True)
                self.ui.pb_refresh.setEnabled(True)
                self.ui.groupBox_StartFonte.setEnabled(True)     #Enable Start PS
            else:
                QtWidgets.QMessageBox.information(self,'Information','Fail to load Power Supply File.',QtWidgets.QMessageBox.Ok) 
        except:
            traceback.print_exc(file=sys.stdout)
            return
        
    def start_meas(self):
        """ 
        """
        self.ui.pb_start_meas.setEnabled(False)
        Lib.flags.stop_all = False        
        
        # data array
        self.data_array = np.array([])
        self.df_rawcurves = None   
        
        # check components
#         self.collect_infocomponents()
        
        # configure integrator
        self.configure_integrator()
        
        # measure and read data
        self.measure_and_read()
        
        # fft calculation
        self.fft_calculation()
        
        # multipoles calculation
        self.multipoles_calculation()
        
        # normalize multipoles 
        self.multipoles_normalization()
        
        # plot results
        self.plot_raw_graph()
        self.plot_multipoles()
        
        # write table
        self.fill_multipole_table()        
        
        # write database
        Lib.db_save_measurement()

        if Lib.flags.stop_all == False:
            QtWidgets.QMessageBox.warning(self,'Information','Measurement completed.',QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self,'Information','Failure during measurement.',QtWidgets.QMessageBox.Ok) 
    
        self.ui.pb_start_meas.setEnabled(True)
        self.ui.tabWidget.setTabEnabled(7, True)
        
    def max_gain_check(self):
        if (self.ui.cb_integrator_gain.currentText() != '100'):
            info = QtWidgets.QMessageBox.question(self,'Configuration.','Do you want to set up Integrator Max Gain?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.Yes)
            if info == QtWidgets.QMessageBox.Yes:
                self.ui.cb_integrator_gain.setCurrentIndex(6)
                QtWidgets.QApplication.processEvents()
                
    def misalignment(self):
        '''
        Check misalignment before measurement with ND780
        '''
        #try:
        Lib.comm.display.readdisplay_ND780()
        time.sleep(0.3)
        _Disp_pos = Lib.comm.display.DisplayPos
        print(_Disp_pos)
        Lib.vars.ref_encoder_A = _Disp_pos[0] 
        Lib.vars.ref_encoder_B = _Disp_pos[1]
        if self.ui.chb_disable_aligment_interlock.isChecked():
            return True
        else:
            if (abs(Lib.vars.ref_encoder_A)>0.005) or (abs(Lib.vars.ref_encoder_B)>0.005):
                QtWidgets.QMessageBox.warning(self, 'Attention', 'Fix the transversal motors', QtWidgets.QMessageBox.Ok)
                return False
            else:
                return True
        #=======================================================================
        # except:
        #     QtWidgets.QMessageBox.warning(self, 'Attention', 'Impossible to read Display ND 780', QtWidgets.QMessageBox.Ok)
        #     return False
        #=======================================================================
     
    def collect_infocomponents(self):
        '''
        Currents and setup verification routines
        '''
        try:
            _misalignment = self.misalignment()
            print(_misalignment)
            if _misalignment == False:
                return False
            
            #IMPLEMENT==========================================================
            # _interlocks = self.check_interlocks()
            # if _interlocks == False:
            #     return False       
            #===================================================================
    #         except:
    #             QtWidgets.QMessageBox.warning(self,'Attention','Stages alignment or interlocks activated.',QtWidgets.QMessageBox.Ok)
             
    #         if (Lib.vars.Status_PS == 1): #and (Lib.vars.PS_ready == 0):
    #             QtWidgets.QMessageBox.warning(self,'Attention','Power supply is not ready./nVerify PS data.',QtWidgets.QMessageBox.Ok)
    #             return False
    #         if self.ui.lb_status_ps.text() == 'NOK':
    #             QtWidgets.QMessageBox.warning(self,'Attention','Power supply is not ready./nVerify PS data.',QtWidgets.QMessageBox.Ok)
    #             return False
            if self.ui.lb_status_coil.text() == 'NOK':
                QtWidgets.QMessageBox.warning(self,'Attention','Please, load the coil data.',QtWidgets.QMessageBox.Ok)
                return False
            if self.ui.lb_status_integrator.text() == 'NOK':
                QtWidgets.QMessageBox.warning(self,'Attention','Please, configure the Integrator FDI 2056.',QtWidgets.QMessageBox.Ok)
                return False
                
            if (self.ui.tabWidget.isTabEnabled(4) == True) and (self.ui.chb_automatic_ps.isChecked()):
                _collect_type = 2  #Automatic collect
            elif self.ui.chb_seriesofmeas.isChecked():
                _collect_type = 1 # Sussesive collect  
            else:
                _collect_type = 0
            
            self.collect_routine(_collect_type)
        except:
            traceback.print_exc(file=sys.stdout)
            
    def collect_routine(self,collect_type):
        """
        Currents and setup verification routines
        """
        self.max_gain_check()
        self.configure_integrator()
        self.ui.lb_meas_counter.setText('0')
        QtWidgets.QApplication.processEvents()
        try:
            if collect_type == 0:
                self.coil_position_correction()
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','collect routine fault',QtWidgets.QMessageBox.Ok)
            return        
            
    def coil_position_correction(self):
        """
        Befere start meas, keep coil in ref trigger + half turn
        """
        try:
            velocity = int(self.ui.le_rotation_motor_speed.text())
        except ValueError:
            velocity = Lib.get_value(Lib.data_settings,'rotation_motor_speed',int)
        try:
            acceleration = int(self.ui.le_rotation_motor_acceleration.text())
        except ValueError:
            acceleration = Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',int)
        try:
            _trigger = int(self.ui.le_trigger_ref.text())
        except ValueError:
            _trigger = Lib.get_value(Lib.coil_settings,'trigger_ref',int)
            
        try:
            _encoder_pulse = int(self.ui.le_n_encoder_pulses.text())
        except ValueError:
            _encoder_pulse = Lib.get_value(Lib.data_settings,'n_encoder_pulses',int)
    
        _position = _trigger + (_encoder_pulse / 2)
        if _position > _encoder_pulse:
            _position = _position - _encoder_pulse
            
        _address_motor = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        
        self.angular_position(_position,_address_motor,velocity,acceleration,_encoder_pulse)
        time.sleep(2)
        
    def angular_position(self,position,address_motor,velocity,acceleration,pulse_encoder):
        Lib.comm.fdi.flushTxRx()
        Lib.comm.fdi.send(Lib.comm.fdi.PDIReadEncoder)
        time.sleep(0.1)
        _valor =  Lib.comm.fdi.ser.readall().strip()
        _valor = str(_valor).strip('b').strip("'")
        _valor = int(_valor)
        shift = position -_valor
        if shift < 0:
            way = 0
        else:
            way = 1
        #Rotation resolution
        rotation_motor_resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)
        
        #Direction
        clockwise_index = self.ui.cb_coil_rotation_direction.currentIndex()        
        
        _steps = int(rotation_motor_resolution*abs(shift)/pulse_encoder)  #/10000
        Lib.comm.parker.conf_motor(address_motor,rotation_motor_resolution,velocity,acceleration,_steps,clockwise_index,mode=0)
        Lib.comm.parker.conf_mode(address_motor,0,way)
        Lib.comm.parker.movemotor(address_motor)
        
        
    def multipoles_normalization(self): # Ok
        """
        """
        _magnet_model = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)
        
        r_ref = Lib.get_value(Lib.measurement_settings, 'norm_radius', float)
        n_ref = _magnet_model
        i_ref = self.df_norm_multipoles.index.values
        
        if _magnet_model == 4: #Skew magnet normalization
            n_ref = 2 #The only skew magnet is a quadrupole
            self.df_norm_multipoles_norm = self.df_norm_multipoles / self.df_skew_multipoles.iloc[n_ref-1,:]
            self.df_skew_multipoles_norm = self.df_skew_multipoles / self.df_skew_multipoles.iloc[n_ref-1,:]        
             
            for i in range(len(self.df_norm_multipoles_norm.columns)):
                self.df_norm_multipoles_norm.iloc[:,i] = self.df_norm_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))
                self.df_skew_multipoles_norm.iloc[:,i] = self.df_skew_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))            
             
            self.averageN_norm = self.df_norm_multipoles_norm.mean(axis=1)
            self.stdN_norm = 1/(self.averageS.values[n_ref-1]) * np.sqrt(self.stdN**2 + (self.stdS**2)*(self.averageN**2)/(self.averageS.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            self.averageS_norm = self.df_skew_multipoles_norm.mean(axis=1)
            self.stdS_norm = 1/(self.averageS.values[n_ref-1]) * np.sqrt(self.stdS**2 + (self.stdN**2)*(self.averageS**2)/(self.averageS.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            
        else: #Normal magnet normalization
            self.df_norm_multipoles_norm = self.df_norm_multipoles / self.df_norm_multipoles.iloc[n_ref-1,:]
            self.df_skew_multipoles_norm = self.df_skew_multipoles / self.df_norm_multipoles.iloc[n_ref-1,:]        
            
            for i in range(len(self.df_norm_multipoles_norm.columns)):
                self.df_norm_multipoles_norm.iloc[:,i] = self.df_norm_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))
                self.df_skew_multipoles_norm.iloc[:,i] = self.df_skew_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))            
            
            self.averageN_norm = self.df_norm_multipoles_norm.mean(axis=1)
            self.stdN_norm = 1/(self.averageN.values[n_ref-1]) * np.sqrt(self.stdN**2 + (self.stdS**2)*(self.averageN**2)/(self.averageN.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            self.averageS_norm = self.df_skew_multipoles_norm.mean(axis=1)
            self.stdS_norm = 1/(self.averageN.values[n_ref-1]) * np.sqrt(self.stdS**2 + (self.stdN**2)*(self.averageS**2)/(self.averageN.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
     
    def popup_meas(self):
        try:
            self.dialog = QtWidgets.QDialog()
            self.dialog.ui = Ui_Pop_Up()
            self.dialog.ui.setupUi(self.dialog)
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            #=======================================================================
            # self.dialog.ui.le_magnet_name
            # self.dialog.ui.le_temperature
            # self.dialog.ui.cb_magnet_model
            # self.dialog.ui.le_meas_details
            # self.dialog.ui.cb_operator
            # self.dialog.ui.le_date
            #=======================================================================
            
            self.dialog.ui.bB_ok_cancel.accepted.connect(self.ok_popup)
            self.dialog.ui.bB_ok_cancel.rejected.connect(self.cancel_popup)        
            self.dialog.exec_()
        except:
            traceback.print_exc(file=sys.stdout)
        
    def ok_popup(self):
        Lib.measurement_df()
        self.dialog.done(1)
        self.start_meas()
    
    def cancel_popup(self):
        self.dialog.deleteLater()
                        
    def multipoles_calculation(self): # Ok
        """
        """
        _nmax = 15
        _n_of_turns = Lib.get_value(Lib.data_settings,'total_number_of_turns',int)
        _n_integration_points = Lib.get_value(Lib.data_settings,'n_integration_points',int)
                
        _coil_type = Lib.get_value(Lib.coil_settings,'coil_type', str)
        if _coil_type == 'Radial':
            _coil_type = 0
        else:
            _coil_type = 1
        _n_coil_turns = Lib.get_value(Lib.coil_settings,'n_turns_normal',int)
        _radius1 = Lib.get_value(Lib.coil_settings,'radius1_normal',float)
        _radius2 = Lib.get_value(Lib.coil_settings,'radius2_normal',float)
        _magnet_model = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)

        self.df_norm_multipoles = pd.DataFrame(index=range(1,_nmax+1), columns=range(_n_of_turns))
        self.df_skew_multipoles = pd.DataFrame(index=range(1,_nmax+1), columns=range(_n_of_turns))        
        
        dtheta = 2*np.pi/_n_integration_points

        #Radial coil calculation:
        if _coil_type == 0:
            for i in range(_n_of_turns):
                for n in range(1,_nmax+1):
                    anl = self.df_fft[i].imag[n]
                    bnl = -self.df_fft[i].real[n]
                    
                    an = (anl*np.sin(dtheta*n) + bnl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius1**n - _radius2**n)/n)*(np.cos(dtheta*n)-1)) 
                    bn = (bnl*np.sin(dtheta*n) - anl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius1**n - _radius2**n)/n)*(np.cos(dtheta*n)-1))        
                
                    self.df_norm_multipoles.iloc[n-1,i] = an 
                    self.df_skew_multipoles.iloc[n-1,i] = bn 
        
        #Tangential coil calculation:
        if _coil_type == 1:
            _radiusDelta = _radius1*np.pi/180
            for i in range(_n_of_turns):
                for n in range(1,_nmax+1):
                    anl = self.df_fft[i].imag[n]
                    bnl = -self.df_fft[i].real[n]
                    
                    an = n * (_radius2**(-n)) * ((-anl)*(np.cos(n*dtheta)-1) - bnl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))
                    bn = n * (_radius2**(-n)) * ((-bnl)*(np.cos(n*dtheta)-1) + anl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))  
                
                    self.df_norm_multipoles.iloc[n-1,i] = an 
                    self.df_skew_multipoles.iloc[n-1,i] = bn 
                    
                    #Older version comparison:
                    #raioDelta = _radiusDelta = _radius1*np.pi/180
                    #r2 = _radius2
                    #An = lib.F[i][n].real = -bnl
                    #Bn = -lib.F[i][n].imag = -anl
                    #Sn = bn = n*Jn = n * (_radius2**(-n)) * ((-bnl)*(np.cos(n*dtheta)-1) + anl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))
                    #Nn = an = n*Kn = n * (_radius2**(-n)) * ((-anl)*(np.cos(n*dtheta)-1) - bnl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))
            
        self.averageN = self.df_norm_multipoles.mean(axis=1)
        self.stdN = self.df_norm_multipoles.std(axis=1)
        self.averageS = self.df_skew_multipoles.mean(axis=1)
        self.stdS = self.df_skew_multipoles.std(axis=1)
        self.averageMod = np.sqrt(self.averageN**2 + self.averageS**2)
        self.stdMod = np.sqrt(self.averageN**2*self.stdN**2 + self.averageS**2*self.stdS**2) / (self.averageMod) #error propagation
        if _magnet_model == 4: #Angle calculation for skew magnet
            self.averageAngle = (1/self.averageN.index) * np.arctan(self.averageS/self.averageN)
            self.stdAngle = (1/self.averageN.index) * 1/(self.averageN + self.averageS**2) * np.sqrt(self.stdS**2 + self.stdN**2*self.averageS**2/self.averageN**2) #error propagation
        else: #Angle calculation for normal magnet
            self.averageAngle = (1/self.averageN.index) * np.arctan(self.averageN/self.averageS)
            self.stdAngle = (1/self.averageN.index) * 1/(self.averageS + self.averageN**2) * np.sqrt(self.stdN**2 + self.stdS**2*self.averageN**2/self.averageS**2) #error propagation

    def fft_calculation(self): # Ok
        """
        """
        _n_of_turns = Lib.get_value(Lib.data_settings,'total_number_of_turns',int)
        self.df_fft = pd.DataFrame()

        for i in range(_n_of_turns):
            _tmp = self.df_rawcurves[i].tolist()
            _tmpfft = -np.fft.fft(_tmp) / (len(_tmp)/2)
            self.df_fft[i] = _tmpfft
            
    def displacement_calculation(self):
        _main_harmonic = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)

        if _main_harmonic > 1:
            if _main_harmonic == 4: #Skew quadrupole
                #Prepares skew magnet center calculation
                _main_harmonic = 2 #Quadrupole main harmonic is 2
                _main_multipole = self.averageS[_main_harmonic-1]
                _prev_multipole = self.averageS[_main_harmonic-2]
                _prev_perp_multipole = self.averageN[_main_harmonic-2]
                _dy_sign = 1
            else:
                #Prepares normal magnet center calculation
                _main_multipole = self.averageN[_main_harmonic-1]
                _prev_multipole = self.averageN[_main_harmonic-2]
                _prev_perp_multipole = self.averageS[_main_harmonic-2]
                _dy_sign = -1

            _dx = (1/(_main_harmonic-1))*(_prev_multipole/_main_multipole)
            _dy = (_dy_sign)*(1/(_main_harmonic-1))*(_prev_perp_multipole/_main_multipole)
            _dx_um = _dx*1e06
            _dy_um = _dy*1e06

            self.ui.le_magnetic_center_x.setText(str(_dx_um))
            self.ui.le_magnetic_center_y.setText(str(_dy_um))
            
            Lib.write_value(Lib.measurement_settings, 'magnetic_center_x', _dx)
            Lib.write_value(Lib.measurement_settings, 'magnetic_center_y', _dy)

        else:
            self.ui.le_magnetic_center_x.setText("")
            self.ui.le_magnetic_center_y.setText("")

    def configure_integrator(self): # Ok
        """
        """
        _n_of_turns = Lib.get_value(Lib.data_settings,'total_number_of_turns',int)

        _n_encoder_pulses = int(Lib.get_value(Lib.data_settings, 'n_encoder_pulses', float)/4)
        _gain =  Lib.get_value(Lib.data_settings, 'integrator_gain', int)
        _direction = self.ui.cb_coil_rotation_direction.currentIndex()
        _trigger_ref = Lib.get_value(Lib.coil_settings, 'trigger_ref', int)
        _n_integration_points = Lib.get_value(Lib.data_settings, 'n_integration_points', int)
        _total_n_of_points = _n_integration_points * _n_of_turns
        
        Lib.comm.fdi.config_measurement(_n_encoder_pulses, _gain, _direction, _trigger_ref, _n_integration_points, _n_of_turns)       

    def measure_and_read(self): # Ok
        """
        """
        # start measurement
        Lib.comm.fdi.start_measurement()
        
        _n_of_turns = Lib.get_value(Lib.data_settings, 'total_number_of_turns', int)
        _n_integration_points = Lib.get_value(Lib.data_settings, 'n_integration_points', int)
        _total_n_of_points = _n_integration_points * _n_of_turns

        # move motor                  
        self.move_motor_measurement(_n_of_turns)
        # start collecting data
        _status = int(Lib.comm.fdi.status('1')[-3])
        while (_status != 1) and (Lib.flags.stop_all == False):
            _status = int(Lib.comm.fdi.status('1')[-3])            
            QtWidgets.QApplication.processEvents()
        if Lib.flags.stop_all == False:       
            _results = Lib.comm.fdi.get_data()
            self.data_array = np.fromstring(_results[:-1], dtype=np.float64, sep=' A')
            self.data_array = self.data_array * 1e-12
            
            _tmp = self.data_array.reshape(_n_integration_points,_n_of_turns)
            self.df_rawcurves = pd.DataFrame(_tmp)  
        
    def plot_raw_graph(self): # Ok
        """
        """
        self.ui.gv_rawcurves.plotItem.curves.clear()
        self.ui.gv_rawcurves.clear()

        px = np.linspace(0, len(self.data_array)-1, len(self.data_array))
        self.ui.gv_rawcurves.plotItem.plot(px, self.data_array, pen=(255,0,0), symbol=None)

    def plot_multipoles(self):
        """
        """
        self.ui.gv_multipoles.clear()
        
        px = np.linspace(1, 15, 15)
        
        _graph = pg.BarGraphItem(x=px, height=self.df_norm_multipoles_norm.iloc[:,0].values, width=0.6, brush='r')
        _graph2 = pg.BarGraphItem(x=px, height=self.df_skew_multipoles_norm.iloc[:,0].values, width=0.6, brush='b')
        
        self.ui.gv_multipoles.addItem(_graph)
        self.ui.gv_multipoles.addItem(_graph2)
        
    def save_data_results(self):
        """Save results to log file"""
        Lib.save_log_file()
        
    def stop_meas(self): # Ok
        self.stop_motor()
           
    def refresh_interface(self):
        """
        """
        self.refresh_connection_settings_tab()
    
    def refresh_connection_settings_tab(self): # Ok
        """
        Refresh inteface with defaults settings
        """
        #list ports and fill comboboxes
        _l = serial.tools.list_ports.comports()
        self.ports = []
        for i in _l:
            self.ports.append(i.device)    
        self.ports.sort()
        
        for i in range(self.ui.cb_disp_port.count()):
            self.ui.cb_disp_port.removeItem(0)
        self.ui.cb_disp_port.addItems(self.ports)
        
        for i in range(self.ui.cb_driver_port.count()):
            self.ui.cb_driver_port.removeItem(0)
        self.ui.cb_driver_port.addItems(self.ports)
        
        for i in range(self.ui.cb_integrator_port.count()):
            self.ui.cb_integrator_port.removeItem(0)
        self.ui.cb_integrator_port.addItems(self.ports)
        
        for i in range(self.ui.cb_ps_port.count()):
            self.ui.cb_ps_port.removeItem(0)
        self.ui.cb_ps_port.addItems(self.ports)
        
        # Connection Tab 
        self.ui.cb_display_type.setCurrentIndex(Lib.get_value(Lib.data_settings,'display_type',int))
        self.ui.cb_disp_port.setCurrentText(Lib.get_value(Lib.data_settings,'disp_port',str))
        self.ui.cb_driver_port.setCurrentText(Lib.get_value(Lib.data_settings,'driver_port',str))
        self.ui.cb_integrator_port.setCurrentText(Lib.get_value(Lib.data_settings,'integrator_port',str))
        self.ui.cb_ps_port.setCurrentText(Lib.get_value(Lib.data_settings,'ps_port',str))
        #self.ui.sb_ps_address.setValue(Lib.get_value(Lib.data_settings,'ps_address',int))
         
        self.ui.chb_enable_Agilent33220A.setChecked(Lib.get_value(Lib.data_settings,'enable_Agilent33220A',int))
        self.ui.sb_agilent33220A_address.setValue(Lib.get_value(Lib.data_settings,'agilent33220A_address',int))
         
        self.ui.chb_enable_Agilent34401A.setChecked(Lib.get_value(Lib.data_settings,'enable_Agilent34401A',int))
        self.ui.sb_agilent34401A_address.setValue(Lib.get_value(Lib.data_settings,'agilent34401A_address',int))
 
        self.ui.chb_enable_Agilent34970A.setChecked(Lib.get_value(Lib.data_settings,'enable_Agilent34970A',int))
        self.ui.sb_agilent34970A_address.setValue(Lib.get_value(Lib.data_settings,'agilent34970A_address',int))
               
        # Settings Tab
        self.ui.le_total_number_of_turns.setText(Lib.get_value(Lib.data_settings,'total_number_of_turns',str))
        self.ui.le_remove_initial_turns.setText(Lib.get_value(Lib.data_settings,'remove_initial_turns',str))
        self.ui.le_remove_final_turns.setText(Lib.get_value(Lib.data_settings,'remove_final_turns',str))
        
        self.ui.le_ref_encoder_A.setText(Lib.get_value(Lib.data_settings,'ref_encoder_A',str))
        self.ui.le_ref_encoder_B.setText(Lib.get_value(Lib.data_settings,'ref_encoder_B',str))
        
        self.ui.le_rotation_motor_address.setText(Lib.get_value(Lib.data_settings,'rotation_motor_address',str))
        self.ui.le_rotation_motor_resolution.setText(Lib.get_value(Lib.data_settings,'rotation_motor_resolution',str))        
        self.ui.le_rotation_motor_speed.setText(Lib.get_value(Lib.data_settings,'rotation_motor_speed',str))
        self.ui.le_rotation_motor_acceleration.setText(Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',str))
        self.ui.le_rotation_motor_ratio.setText(Lib.get_value(Lib.data_settings,'rotation_motor_ratio',str))

        self.ui.le_poscoil_assembly.setText(Lib.get_value(Lib.data_settings,'poscoil_assembly',str))
        self.ui.le_n_encoder_pulses.setText(Lib.get_value(Lib.data_settings,'n_encoder_pulses',str))        
        
        self.ui.cb_integrator_gain.setCurrentText(str(Lib.get_value(Lib.data_settings,'integrator_gain',int)))
        self.ui.cb_n_integration_points.setCurrentText(str(Lib.get_value(Lib.data_settings,'n_integration_points',int)))
        
        self.ui.chb_save_turn_angles.setChecked(Lib.get_value(Lib.data_settings,'save_turn_angles',int))
        self.ui.chb_disable_aligment_interlock.setChecked(Lib.get_value(Lib.data_settings,'disable_aligment_interlock',int))
        self.ui.chb_disable_ps_interlock.setChecked(Lib.get_value(Lib.data_settings,'disable_ps_interlock',int))
        
        self.ui.cb_bench.setCurrentIndex(Lib.get_value(Lib.data_settings,'bench',int))

        # Motor Tab
        self.ui.le_motor_vel.setText(Lib.get_value(Lib.data_settings,'rotation_motor_speed',str))
        self.ui.le_motor_ace.setText(Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',str))
        self.ui.le_motor_turns.setText(str(1))        

        self.ui.le_encoder_setpoint.setText(Lib.get_value(Lib.data_settings,'poscoil_assembly',str))
        
    def config_variables(self): # Ok
        """
        Refresh variables with inteface values
        """
        # Connection Tab 
        Lib.write_value(Lib.data_settings,'display_type',self.ui.cb_display_type.currentIndex())
        Lib.write_value(Lib.data_settings,'disp_port',self.ui.cb_disp_port.currentText())
        Lib.write_value(Lib.data_settings,'driver_port',self.ui.cb_driver_port.currentText())
        Lib.write_value(Lib.data_settings,'integrator_port',self.ui.cb_integrator_port.currentText())
        Lib.write_value(Lib.data_settings,'ps_port',self.ui.cb_ps_port.currentText())
        Lib.write_value(Lib.data_settings,'ps_address',self.ui.sb_ps_address.value())

        Lib.write_value(Lib.data_settings,'enable_Agilent33220A',self.ui.chb_enable_Agilent33220A.checkState())
        Lib.write_value(Lib.data_settings,'agilent33220A_address',self.ui.sb_agilent33220A_address.value())

        Lib.write_value(Lib.data_settings,'enable_Agilent34401A',self.ui.chb_enable_Agilent34401A.checkState())
        Lib.write_value(Lib.data_settings,'agilent34401A_address',self.ui.sb_agilent34401A_address.value())

        Lib.write_value(Lib.data_settings,'enable_Agilent34970A',self.ui.chb_enable_Agilent34970A.checkState())
        Lib.write_value(Lib.data_settings,'agilent34970A_address',self.ui.sb_agilent34970A_address.value())
               
        # Settings Tab
        Lib.write_value(Lib.data_settings,'total_number_of_turns',self.ui.le_total_number_of_turns.text())
        Lib.write_value(Lib.data_settings,'remove_initial_turns',self.ui.le_remove_initial_turns.text())
        Lib.write_value(Lib.data_settings,'remove_final_turns',self.ui.le_remove_final_turns.text())
        
        Lib.write_value(Lib.data_settings,'ref_encoder_A',self.ui.le_ref_encoder_A.text())
        Lib.write_value(Lib.data_settings,'ref_encoder_B',self.ui.le_ref_encoder_B.text())

        Lib.write_value(Lib.data_settings,'rotation_motor_address',self.ui.le_rotation_motor_address.text())
        Lib.write_value(Lib.data_settings,'rotation_motor_resolution',self.ui.le_rotation_motor_resolution.text())        
        Lib.write_value(Lib.data_settings,'rotation_motor_speed',self.ui.le_rotation_motor_speed.text())
        Lib.write_value(Lib.data_settings,'rotation_motor_acceleration',self.ui.le_rotation_motor_acceleration.text())
        Lib.write_value(Lib.data_settings,'rotation_motor_ratio',self.ui.le_rotation_motor_ratio.text())
        
        Lib.write_value(Lib.data_settings,'poscoil_assembly',self.ui.le_poscoil_assembly.text())
        Lib.write_value(Lib.data_settings,'n_encoder_pulses',self.ui.le_n_encoder_pulses.text())        

        Lib.write_value(Lib.data_settings,'integrator_gain',int(self.ui.cb_integrator_gain.currentText()))
        Lib.write_value(Lib.data_settings,'n_integration_points',int(self.ui.cb_n_integration_points.currentText()))

        Lib.write_value(Lib.data_settings,'save_turn_angles',self.ui.chb_save_turn_angles.checkState())
        Lib.write_value(Lib.data_settings,'disable_aligment_interlock',self.ui.chb_disable_aligment_interlock.checkState())
        Lib.write_value(Lib.data_settings,'disable_ps_interlock',self.ui.chb_disable_ps_interlock.checkState())
        
        Lib.write_value(Lib.data_settings,'bench',self.ui.cb_bench.currentIndex())
  
    def refresh_coiltab(self): # Ok     
        # Coil Tab
        self.ui.le_coil_name.setText(Lib.get_value(Lib.coil_settings,'coil_name',str))
        self.ui.le_n_turns_normal.setText(Lib.get_value(Lib.coil_settings,'n_turns_normal',str))
        self.ui.le_radius1_normal.setText(Lib.get_value(Lib.coil_settings,'radius1_normal',str))
        self.ui.le_radius2_normal.setText(Lib.get_value(Lib.coil_settings,'radius2_normal',str))
        self.ui.le_n_turns_bucked.setText(Lib.get_value(Lib.coil_settings,'n_turns_bucked',str))
        self.ui.le_radius1_bucked.setText(Lib.get_value(Lib.coil_settings,'radius1_bucked',str))
        self.ui.le_radius2_bucked.setText(Lib.get_value(Lib.coil_settings,'radius2_bucked',str))
        self.ui.le_trigger_ref.setText(str(Lib.get_value(Lib.coil_settings,'trigger_ref',int)))
        
        if Lib.get_value(Lib.coil_settings,'coil_type') == 'Radial':
            self.ui.cb_coil_type.setCurrentIndex(0)
        else:
            self.ui.cb_coil_type.setCurrentIndex(1)            

        self.ui.te_comments.setPlainText(Lib.get_value(Lib.coil_settings,'comments',str))
        
    def config_coil(self): # Ok
        """
        Refresh variables with inteface values
        """
        # Coil Tab
        Lib.write_value(Lib.coil_settings,'coil_name',self.ui.le_coil_name.text())
        Lib.write_value(Lib.coil_settings,'n_turns_normal',self.ui.le_n_turns_normal.text())
        Lib.write_value(Lib.coil_settings,'radius1_normal',self.ui.le_radius1_normal.text())
        Lib.write_value(Lib.coil_settings,'radius2_normal',self.ui.le_radius2_normal.text())
        Lib.write_value(Lib.coil_settings,'n_turns_bucked',self.ui.le_n_turns_bucked.text())        
        Lib.write_value(Lib.coil_settings,'radius1_bucked',self.ui.le_radius1_bucked.text())
        Lib.write_value(Lib.coil_settings,'radius2_bucked',self.ui.le_radius2_bucked.text())
        Lib.write_value(Lib.coil_settings,'trigger_ref',self.ui.le_trigger_ref.text())
        Lib.write_value(Lib.coil_settings,'coil_type',self.ui.cb_coil_type.currentText())
        Lib.write_value(Lib.coil_settings,'comments',self.ui.te_comments.toPlainText())
        
    def refresh_PS_settings(self):
        """
        When connected "Load Power Supply", refresh interface with values of the database 
        """
        #Power Supply Tab
        #Configuration
        self.ui.le_PS_type.setText(Lib.get_value(Lib.PS_settings,'Power Supply Type',str))
        self.ui.le_PS_Name.setText(Lib.get_value(Lib.PS_settings,'Power Supply Name',str))
        #Current Adjustment
        self.ui.dsb_current_setpoint.setValue(Lib.get_value(Lib.PS_settings,'Current Setpoint',float))
        self.ui.dsb_Amplitude_Linear.setValue(Lib.get_value(Lib.PS_settings,'Amplitude Step',float))
        self.ui.dsb_Time_Linear.setValue(Lib.get_value(Lib.PS_settings,'Delay/Step',float))
        self.keep_auto_values()
        #Demagnetization Curves
        #Sinusoidal
        self.ui.le_Sinusoidal_Amplitude.setText(Lib.get_value(Lib.PS_settings,'Sinusoidal Amplitude (App)',str))
        self.ui.le_Sinusoidal_Offset.setText(Lib.get_value(Lib.PS_settings,'Sinusoidal Offset',str))
        self.ui.le_Sinusoidal_Frequency.setText(Lib.get_value(Lib.PS_settings,'Sinusoidal Frequency',str))
        self.ui.le_Sinusoidal_n_cicles.setText(Lib.get_value(Lib.PS_settings,'Sinusoidal N Cicles',str))
        self.ui.le_Initial_Phase.setText(Lib.get_value(Lib.PS_settings,'Sinusoidal Initial Phase',str))
        self.ui.le_Final_Phase.setText(Lib.get_value(Lib.PS_settings,'Sinusoidal Final Phase',str))
        #Cushioned Sinusoidal
        self.ui.le_cush_sin_Ampl.setText(Lib.get_value(Lib.PS_settings,'Cushioned Sinusoidal Amplitude',str))
        self.ui.le_cush_sin_Offset.setText(Lib.get_value(Lib.PS_settings,'Cushioned Sinusoidal Offset',str))
        self.ui.le_cush_sin_Freq.setText(Lib.get_value(Lib.PS_settings,'Cushioned Sinusoidal Frequency',str))
        self.ui.le_cush_sin_nCicles.setText(Lib.get_value(Lib.PS_settings,'Cushioned Sinusoidal N Cicles',str))
        self.ui.le_cush_sin_phaseShift.setText(Lib.get_value(Lib.PS_settings,'Cushioned Sinusoidal Phase Shift',str))
        self.ui.le_cush_sin_finalPhase.setText(Lib.get_value(Lib.PS_settings,'Cushioned Sinusoidal Final Phase',str))
        self.ui.le_cush_sin_Damping.setText(Lib.get_value(Lib.PS_settings,'Cushioned Sinusoidal Damping',str))
        #Triangular Softened
        self.ui.le_softened_Ampl.setText(Lib.get_value(Lib.PS_settings,'Triangular Softened Amplitude',str))
        self.ui.le_softened_Offset.setText(Lib.get_value(Lib.PS_settings,'Triangular Softened Offset',str))
        self.ui.le_softened_Freq.setText(Lib.get_value(Lib.PS_settings,'Triangular Softened Frequency',str))
        self.ui.le_softened_nCicles.setText(Lib.get_value(Lib.PS_settings,'Triangular Softened N Cicles',str))
        self.ui.le_softened_phaseShift.setText(Lib.get_value(Lib.PS_settings,'Triangular Softened Phase Shift',str))
        self.ui.le_softened_finalPhase.setText(Lib.get_value(Lib.PS_settings,'Triangular Softened Phase',str))
        #Settings
        self.ui.le_maximum_current.setText(Lib.get_value(Lib.PS_settings,'Maximum Current',str))
        self.ui.le_minimum_current.setText(Lib.get_value(Lib.PS_settings,'Minimum Current',str))
        self.ui.sb_kp.setValue(Lib.get_value(Lib.PS_settings,'Kp',float))
        self.ui.sb_ki.setValue(Lib.get_value(Lib.PS_settings,'Ki',float))
        
        
    def config_PS(self):
        """
        Write variables with interface values for new features
        """
        # Power Supply Tab
        Lib.write_value(Lib.PS_settings,'Power Supply Name',self.ui.le_PS_Name.text())
        Lib.write_value(Lib.PS_settings,'Power Supply Type', self.ui.le_PS_type.text())
        Lib.write_value(Lib.PS_settings,'Current Setpoint',self.ui.dsb_current_setpoint.text())
        Lib.write_value(Lib.PS_settings,'Amplitude Step',self.ui.dsb_Amplitude_Linear.text())
        Lib.write_value(Lib.PS_settings,'Delay/Step',self.ui.dsb_Time_Linear.text())
        Lib.write_value(Lib.PS_settings,'Sinusoidal Amplitude (App)',self.ui.le_Sinusoidal_Amplitude.text())
        Lib.write_value(Lib.PS_settings,'Sinusoidal Offset',self.ui.le_Sinusoidal_Offset.text())
        Lib.write_value(Lib.PS_settings,'Sinusoidal Frequency',self.ui.le_Sinusoidal_Frequency.text())
        Lib.write_value(Lib.PS_settings,'Sinusoidal N Cicles',self.ui.le_Sinusoidal_n_cicles.text())
        Lib.write_value(Lib.PS_settings,'Sinusoidal Initial Phase',self.ui.le_Initial_Phase.text())
        Lib.write_value(Lib.PS_settings,'Sinusoidal Final Phase', self.ui.le_Final_Phase.text())
        #Cushioned Sinusoidal
        Lib.write_value(Lib.PS_settings,'Cushioned Sinusoidal Amplitude',self.ui.le_cush_sin_Ampl.text())
        Lib.write_value(Lib.PS_settings,'Cushioned Sinusoidal Offset',self.ui.le_cush_sin_Offset.text())
        Lib.write_value(Lib.PS_settings,'Cushioned Sinusoidal Frequency',self.ui.le_cush_sin_Freq.text())
        Lib.write_value(Lib.PS_settings,'Cushioned Sinusoidal N Cicles',self.ui.le_cush_sin_nCicles.text())
        Lib.write_value(Lib.PS_settings,'Cushioned Sinusoidal Phase Shift',self.ui.le_cush_sin_phaseShift.text())
        Lib.write_value(Lib.PS_settings,'Cushioned Sinusoidal Final Phase',self.ui.le_cush_sin_finalPhase.text())
        Lib.write_value(Lib.PS_settings,'Cushioned Sinusoidal Damping',self.ui.le_cush_sin_Damping.text())
        #Triangular Softened
        Lib.write_value(Lib.PS_settings,'Triangular Softened Amplitude',self.ui.le_softened_Ampl.text())
        Lib.write_value(Lib.PS_settings,'Triangular Softened Offset',self.ui.le_softened_Offset.text())
        Lib.write_value(Lib.PS_settings,'Triangular Softened Frequency',self.ui.le_softened_Freq.text())
        Lib.write_value(Lib.PS_settings,'Triangular Softened N Cicles',self.ui.le_softened_nCicles.text())
        Lib.write_value(Lib.PS_settings,'Triangular Softened Phase Shift',self.ui.le_softened_phaseShift.text())
        Lib.write_value(Lib.PS_settings,'Triangular Softened Phase',self.ui.le_softened_finalPhase.text())
        #Automatic setpoints
        #Lib.write_value(Lib.PS_settings,'Automatic Setpoints',self.ui.le_Auto_Set.text()) # Need revision
        #Settings
        Lib.write_value(Lib.PS_settings,'Maximum Current',self.ui.le_maximum_current.text())
        Lib.write_value(Lib.PS_settings,'Minimum Current',self.ui.le_minimum_current.text())
        Lib.write_value(Lib.PS_settings,'Kp',self.ui.sb_kp.text())
        Lib.write_value(Lib.PS_settings,'Ki',self.ui.sb_ki.text())      
        
    def keep_auto_values(self):
        try:
            auto = Lib.get_value(Lib.PS_settings,'Automatic Setpoints')
            dataset_list=''.join(auto)
            dataset_array = []
            for item in dataset_list.split(','):
                dataset_array.append(item)
            self.auto_values = np.asarray(dataset_array, dtype='float')
        except:
            QtWidgets.QMessageBox.warning(self,'Fail','Impossible to get automatic values.',QtWidgets.QMessageBox.Ok)
            return
        try:           
            for i in range(len(self.auto_values)):
                self.set_table_item(self.ui.tw_auto_set, i, 0, self.auto_values[i])
        except:
            QtWidgets.QMessageBox.warning(self,'Fail','Impossible to set in table the automatic values for Current.',QtWidgets.QMessageBox.Ok)
            return
        QtWidgets.QApplication.processEvents()
        
    
    def add_rows(self):
        rowPosition = self.ui.tw_auto_set.rowCount()-2
        self.ui.tw_auto_set.insertRow(rowPosition)
        
        
    def fill_multipole_table(self): # Ok
        """
        """
        
        n_rows = self.ui.tw_multipoles_table.rowCount()

        for i in range(n_rows):
            self.set_table_item(self.ui.tw_multipoles_table,i, 0, self.averageN.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 1, self.stdN.values[i])            
            self.set_table_item(self.ui.tw_multipoles_table,i, 2, self.averageS.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 3, self.stdS.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 4, self.averageMod.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 5, self.stdMod.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 6, self.averageAngle.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 7, self.stdAngle.values[i])            
            self.set_table_item(self.ui.tw_multipoles_table,i, 8, self.averageN_norm.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 9, self.stdN_norm.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 10, self.averageS_norm.values[i])    
            self.set_table_item(self.ui.tw_multipoles_table,i, 11, self.stdS_norm.values[i])            

    def set_table_item(self,table,row,col,val): # Ok
        """
        """
        if table.objectName() == 'tw_multipoles_table':
            item = QtWidgets.QTableWidgetItem()
            table.setItem(row, col, item)
            item.setText('{0:0.6e}'.format(val))
        else:
            item = QtWidgets.QTableWidgetItem()
            table.setItem(row, col, item)
            item.setText(str(val))
        
         
#===============================================================================
# class main(object):
#     def __init__(self):
#         self.app = QtWidgets.QApplication(sys.argv)
#         self.myapp = ApplicationWindow()
#         self.myapp.show()
#         sys.exit(self.app.exec_())
#       
# if __name__ == "__main__":
#     Lib = Library.RotatingCoil_Library()
#     Lib.App = main()
#===============================================================================
     
class main(threading.Thread): # Ok
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
      
    def run(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.myapp = ApplicationWindow()
        self.myapp.show()
        sys.exit(self.app.exec_())
    
if __name__ == '__main__':
#if __name__ == 'builtins':
    print(__name__ + ' ok' )
    Lib = Library.RotatingCoil_Library()
    Lib.App = main()
else:
    print(__name__ + ' fail' )


        # move motor - Thread
#         _n_of_turns = int(self.ui.le_total_number_of_turns.text())
#         self.thread_motor = threading.Thread(target=self.move_motor_measurement, args=(_n_of_turns,))
#         self.thread_motor.setDaemon(True)
#         self.thread_motor.start()
        
