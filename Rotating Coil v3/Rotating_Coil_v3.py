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
        
        self.ui.gb_start_supply.setEnabled(False)
        self.ui.gb_start_supply.setEnabled(False)

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
#         self.ui.chb_disable_alignment_interlock
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
        self.ui.pb_PS_button.clicked.connect(lambda: self.start_powersupply(False)) #Ok
        self.ui.pb_refresh.clicked.connect(self.display_current) #Ok
        self.ui.pb_load_PS.clicked.connect(lambda: self.load_PowerSupply(False)) #Ok
        self.ui.pb_save_PS.clicked.connect(lambda: self.save_PowerSupply(False))
        self.ui.pb_send.clicked.connect(lambda: self.linear_manual_ramp(False)) #Ok
        self.ui.pb_rows_auto.clicked.connect(lambda: self.add_rows(False)) #Ok
        self.ui.pb_send_curve.clicked.connect(lambda: self.send_curve(False)) #Ok
        self.ui.pb_config_PID.clicked.connect(self.pid_setting) #Ok
        self.ui.pb_reset_inter.clicked.connect(lambda: self.reset_interlocks(False))
        self.ui.pb_cycle.clicked.connect(lambda: self.cycling_ps(False))
        self.ui.pb_config_ps.clicked.connect(lambda: self.configure_ps(False))
        self.ui.pb_clear_table.clicked.connect(lambda: self.clear_table(False))
        #Secondary Power Supply
        self.ui.pb_PS_button_2.clicked.connect(lambda: self.start_powersupply(True))
        self.ui.pb_load_PS_2.clicked.connect(lambda: self.load_PowerSupply(True))
        self.ui.pb_save_PS_2.clicked.connect(lambda: self.save_PowerSupply(True))
        self.ui.pb_send_2.clicked.connect(lambda: self.linear_manual_ramp(True))
        self.ui.pb_rows_auto_2.clicked.connect(lambda: self.add_rows(True))
        self.ui.pb_send_curve_2.clicked.connect(lambda: self.send_curve(True))
        self.ui.pb_reset_inter_2.clicked.connect(lambda: self.reset_interlocks(True))
        self.ui.pb_cycle_2.clicked.connect(lambda: self.cycling_ps(True))
        self.ui.pb_clear_table_2.clicked.connect(lambda: self.clear_table(True))
        self.ui.pb_config_ps_2.clicked.connect(lambda: self.configure_ps(True))
        self.ui.pb_emergency4.clicked.connect(self.emergency)
        
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
        self.ui.pb_emergency5.clicked.connect(self.emergency)
        
        # Results Tab
        self.ui.pb_save_data_results.clicked.connect(self.save_data_results)
        self.ui.pb_emergency6.clicked.connect(self.emergency)
        
    def connect_devices(self):
        """
        connect devices and check status
        """
        if not Lib.flags.devices_connected:
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
                
                Lib.write_value(Lib.data_settings, 'agilent33220A_address', self.ui.sb_agilent33220A_address.value(),True)
                Lib.write_value(Lib.data_settings, 'agilent34401A_address', self.ui.sb_agilent34401A_address.value(),True)
                Lib.write_value(Lib.data_settings, 'agilent34970A_address', self.ui.sb_agilent34970A_address.value(),True)
                
                # connect agilent 33220a - function generator
                if self.ui.chb_enable_Agilent33220A.checkState() != 0:
                    Lib.comm.agilent33220a = Agilent_33220A.GPIB()
                    Lib.comm.agilent33220a.connect(Lib.get_value(Lib.data_settings,'agilent33220A_address',int))
                    self.ui.lb_status_33220A.setText('Connected')        
        
                # connect agilent 34401a - voltmeter
                if self.ui.chb_enable_Agilent34401A.checkState() != 0:
                    Lib.comm.agilent34401a = Agilent_34401A.GPIB()
                    Lib.comm.agilent34401a.connect(Lib.get_value(Lib.data_settings,'agilent34401A_address',int))        
                    self.ui.lb_status_34401A.setText('Connected')        
        
                # connect agilent 34970a - multichannel
                if self.ui.chb_enable_Agilent34970A.checkState() != 0:
                    Lib.comm.agilent34970a = Agilent_34970A.GPIB()
                    Lib.comm.agilent34970a.connect(Lib.get_value(Lib.data_settings,'agilent34970A_address',int))
                    self.ui.lb_status_34970A.setText('Connected')
                     
                # connect digital power supply
                Lib.comm.drs = SerialDRS.SerialDRS_FBP()
                Lib.comm.drs.Connect(Lib.get_value(Lib.data_settings,'ps_port',str))
                
                QtWidgets.QMessageBox.information(self,'Information','Devices connected.',QtWidgets.QMessageBox.Ok)
                self.ui.pb_connect_devices.setText('Disconnect Devices')
                Lib.flags.devices_connected = True
                for i in range(1,7):
                    self.ui.tabWidget.setTabEnabled(i,True)            # Unlock main Tabs
            except:
                QtWidgets.QMessageBox.warning(self,'Attention','Fail to connect devices',QtWidgets.QMessageBox.Ok)
             
        else:
            try:
                # connect display
                Lib.comm.display.disconnect()
        
                # connect driver 
                Lib.comm.parker.disconnect()
        
                # connect integrator
                Lib.comm.fdi.disconnect()
                
                # connect agilent 33220a - function generator
                if self.ui.lb_status_33220A.text() == 'Connected':
                    Lib.comm.agilent33220a.disconnect()
                    self.ui.lb_status_33220A.setText('Disconnected')        
        
                # connect agilent 34401a - voltmeter
                if self.ui.lb_status_34401A.text() == 'Connected':
                    Lib.comm.agilent34401a.disconnect()       
                    self.ui.lb_status_34401A.setText('Disconnected')        
        
                # connect agilent 34970a - multichannel
                if self.ui.lb_status_34970A.text() == 'Connected':
                    Lib.comm.agilent34970a.disconnect()
                    self.ui.lb_status_34970A.setText('Disconnected')
                     
                # connect digital power supply
                Lib.comm.drs.Disconnect()
                
                QtWidgets.QMessageBox.information(self,'Information','Devices disconnected.',QtWidgets.QMessageBox.Ok)
                self.ui.pb_connect_devices.setText('Connect Devices')
                Lib.flags.devices_connected = False
                for i in range(1,7):
                    self.ui.tabWidget.setTabEnabled(i,False)            # Lock main Tabs
            except:
                QtWidgets.QMessageBox.warning(self,'Attention','Fail to disconnect devices',QtWidgets.QMessageBox.Ok)
                        
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

    def start_powersupply(self, secondary=False):
        if not secondary:
            _df = Lib.ps_settings
            _status_ps = Lib.get_value(Lib.aux_settings, 'status_ps', int)
        else:
            _df = Lib.ps_settings_2
            _status_ps = Lib.get_value(Lib.aux_settings, 'status_ps_2', int)
            
        try:
            _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
            Lib.comm.drs.SetSlaveAdd(_ps_type)
                        
            if not secondary:
                if self.ui.pb_PS_button.isChecked():
                    self.ui.pb_PS_button.setText('Power ON')    
                else:
                    self.ui.pb_PS_button.setChecked(False)
                    self.ui.pb_PS_button.setText('Power OFF')
            else:
                if self.ui.pb_PS_button_2.isChecked():
                    self.ui.pb_PS_button_2.setText('Power ON')    
                else:
                    self.ui.pb_PS_button_2.setChecked(False)
                    self.ui.pb_PS_button_2.setText('Power OFF')

            _safety_enabled = 1
            if Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int) and ((secondary == False and _status_ps == 0) or (secondary == True and _status_ps == 0)):
                _ret = QtWidgets.QMessageBox.question(self,'Attention','Do you want to turn on the Power Supply with Safety Control DISABLED?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
                if _ret == QtWidgets.QMessageBox.Yes:
                    _safety_enabled = 0
                else:
                    return
            if (secondary == False and _status_ps == 0) or (secondary == True and _status_ps == 0):         # Status PS is OFF                
                try:
                    Lib.comm.drs.Read_iLoad1()
                except:
                    traceback.print_exc(file=sys.stdout)
                    QtWidgets.QMessageBox.warning(self,'Warning','Impossible to read the digital current.',QtWidgets.QMessageBox.Ok)
                    if not secondary:
                        self.ui.pb_PS_button.setChecked(False)
                        self.ui.pb_PS_button.setText('Power OFF')
                    else:
                        self.ui.pb_PS_button_2.setChecked(False)
                        self.ui.pb_PS_button_2.setText('Power OFF')
                    return
                if _safety_enabled == 1:
                    _status_interlocks = Lib.comm.drs.Read_ps_SoftInterlocks()
                    time.sleep(0.25)
                    if _status_interlocks != 0:  
                        QtWidgets.QMessageBox.critical(self,'Attention','Soft Interlock activated!',QtWidgets.QMessageBox.Ok)
                        return
                    _status_interlocks = Lib.comm.drs.Read_ps_HardInterlocks()
                    time.sleep(0.25)
                    if _status_interlocks != 0:  
                        QtWidgets.QMessageBox.critical(self,'Attention','Hard Interlock activated!',QtWidgets.QMessageBox.Ok)
                        return
                    
                    if _ps_type > 2:                    # PS 225 A or 10 A
                        Lib.comm.drs.TurnOn()           # Turn ON the Digital Power Supply
                        time.sleep(0.5)
                        if Lib.comm.drs.Read_ps_OnOff() == 1:
                            if not secondary:
                                Lib.write_value(Lib.aux_settings, 'status_ps', 1)      # Status PS is ON
                                Lib.write_value(Lib.aux_settings, 'actual_current', 0)
#                                 self.ui.tabWidget_2.setEnabled(True)
#                                 self.ui.tabWidget_3.setEnabled(True)
                            else:
                                Lib.write_value(Lib.aux_settings, 'status_ps_2', 1)      # Status PS is ON
                                Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                            QtWidgets.QMessageBox.information(self,'Information','The Power Supply started successfully.',QtWidgets.QMessageBox.Ok)                           
                        else:
                            QtWidgets.QMessageBox.critical(self,'Attention','The Power Supply did not started.',QtWidgets.QMessageBox.Ok)
                            return
                        
                        # Closed Loop
                        Lib.comm.drs.ClosedLoop()       
                        time.sleep(0.5)
                        if Lib.comm.drs.Read_ps_OpenLoop() == 1:
                            QtWidgets.QMessageBox.warning(self,'Attention',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                            return
                        if not secondary:
                            self.ui.le_status_loop.setText('Closed')
    #                         self.ui.sb_ps_dclink.setEnabled(False)
                            self.ui.pb_refresh.setEnabled(True)
                            self.ui.lb_status_ps.setText('OK')
                        else:
                            self.ui.le_status_loop_2.setText('Closed')
                        QtWidgets.QApplication.processEvents()
                    else:                               # PS 1000 A (always primary)
                        Lib.comm.drs.SetSlaveAdd(_ps_type-1)
                        time.sleep(.1)
                        # Turn ON PS DClink
                        try:
                            Lib.comm.drs.TurnOn()           # Turn ON the DC Link of the PS
                            time.sleep(.5)
                            if Lib.comm.drs.Read_ps_OnOff() != 1:
                                QtWidgets.QMessageBox.information(self,'Information',"Power Supply Capacitor Bank did not initialize.",QtWidgets.QMessageBox.Ok)
                                return
                        except:
                            QtWidgets.QMessageBox.critical(self,'Attention',"Power Supply Capacitor Bank did not initialize.",QtWidgets.QMessageBox.Ok)
                            return
                        
                        # Closing DC link Loop
                        try:
                            Lib.comm.drs.ClosedLoop()        # Closed Loop
                            time.sleep(.5)
                            if Lib.comm.drs.Read_ps_OpenLoop() == 1:
                                QtWidgets.QMessageBox.warning(self,'Attention',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                                return
                        except:
                            QtWidgets.QMessageBox.warning(self,'Attention',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                            return
                        
                        # Set ISlowRef for DC Link (Capacitor Bank)
                        _mode = 0
                        Lib.comm.drs.OpMode(_mode)                     # Operation mode selection for Slowref
                        _dclink_value = Lib.get_value(Lib.aux_settings, 'dclink_value', float) #30 
                        Lib.comm.drs.SetISlowRef(_dclink_value)        # Set 30 V for Capacitor Bank (default value according to the ELP Group)
                        time.sleep(.3)
                        _feedback_DCLink = round(Lib.comm.drs.Read_vDCMod1()/2 +\
                                                Lib.comm.drs.Read_vDCMod2()/2,3)
                        
                        #Waiting few seconds before starting PS Current
                        _i = 100
                        while _feedback_DCLink < _dclink_value and _i > 0:
                            _feedback_DCLink = round(Lib.comm.drs.Read_vDCMod1()/2 +\
                                                    Lib.comm.drs.Read_vDCMod2()/2,3)
                            QtWidgets.QApplication.processEvents()
                            time.sleep(0.5)
                            self.ui.tabWidget_2.setEnabled(False)
                            self.ui.pb_PS_button.setEnabled(False)
                            self.ui.pb_PS_button.setText('Starting...')
                            _i = _i-1
                            
                        if _i == 0:
                            QtWidgets.QMessageBox.warning(self,'Attention',"Setpoint DC link is not set.\nCheck configurations.",QtWidgets.QMessageBox.Ok)
                            self.ui.pb_PS_button.setChecked(False)
                            self.ui.pb_PS_button.setEnabled(True)
                            self.ui.pb_PS_button.setText('Power OFF')
                            return
                        
                        #Turn on PS Current
                        Lib.comm.drs.SetSlaveAdd(_ps_type)  # Set 1000A supply address
                        Lib.comm.drs.TurnOn()           
                        time.sleep(0.5)
                        if Lib.comm.drs.Read_ps_OnOff() == 1:
                            Lib.write_value(Lib.aux_settings, 'status_ps', 1)      # Status PS is ON
                            Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                            self.ui.tabWidget_2.setEnabled(True)
                            self.ui.tabWidget_3.setEnabled(True)
                            QtWidgets.QMessageBox.information(self,'Information','The Power Supply started successfully.',QtWidgets.QMessageBox.Ok)
                        else:
                            QtWidgets.QMessageBox.critical(self,'Attention','The Power Supply did not start.',QtWidgets.QMessageBox.Ok)
                            return
                        
                        # Closed Loop
                        Lib.comm.drs.ClosedLoop()       
                        time.sleep(0.5)
                        if Lib.comm.drs.Read_ps_OpenLoop() == 1:
                            QtWidgets.QMessageBox.warning(self,'Attention',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                            return
                        self.ui.pb_PS_button.setText('Power On')
                        self.ui.le_status_loop.setText('Closed')
                        self.ui.pb_refresh.setEnabled(True)
                        #if everything goes well#:
                        self.ui.lb_status_ps.setText('OK')
                        QtWidgets.QApplication.processEvents()
            else:
                if not secondary:
                    Lib.comm.drs.SetSlaveAdd(_ps_type)
                    if not self.ui.pb_PS_button.isChecked():
                        self.ui.pb_PS_button.setText('Power Off')
                        self.ui.lb_status_ps.setText('NOK')
                else:
                    Lib.comm.drs.SetSlaveAdd(_ps_type)
                    if not self.ui.pb_PS_button_2.isChecked():
                        self.ui.pb_PS_button_2.setText('Power Off')
                _status = Lib.comm.drs.Read_ps_OnOff()
                if _status == 1:
                    Lib.comm.drs.TurnOff()                    # Turn OFF the Power Supply
                    if not secondary:
                        Lib.write_value(Lib.aux_settings, 'status_ps', 0)      # Status PS is OFF
                        Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                        self.ui.tabWidget_2.setEnabled(False)
                        self.ui.le_status_loop.setText('Open')
                    else:
                        Lib.write_value(Lib.aux_settings, 'status_ps_2', 0)      # Status PS_2 is OFF
                        Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                        self.ui.le_status_loop_2.setText('Open')
                else:
                    Lib.comm.drs.TurnOff()
                    QtWidgets.QMessageBox.critical(self,'Attention','Digital Source did not receive the command.',QtWidgets.QMessageBox.Ok)
                    return
        except:
            traceback.print_exc(file=sys.stdout)
            QtWidgets.QMessageBox.critical(self,'Fail','Power Supply start failed.',QtWidgets.QMessageBox.Ok)
            return
    
    def pid_setting(self):
        '''
        Set by software the PID configurations  
        '''
        _ans = QtWidgets.QMessageBox.question(self, 'PID settings', 'Be aware that this will overwrite the current configurations.\nAre you sure you want to configure the PID parameters? ', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if _ans == QtWidgets.QMessageBox.Yes:
            Lib.write_value(Lib.ps_settings,'Kp',self.ui.sb_kp.text(),True)
            Lib.write_value(Lib.ps_settings,'Ki',self.ui.sb_ki.text(),True)
            _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
            Lib.comm.drs.SetSlaveAdd(_ps_type)
            _id_mode = 0
            _elp_PI_dawu = 3
            try:
                Lib.comm.drs.Write_dp_ID(_id_mode)           #Write ID module from controller
                Lib.comm.drs.Write_dp_Class(_elp_PI_dawu)    #Write DP Class for setting PI 
            except:
                QtWidgets.QMessageBox.critical(self,'Fail','Power Supply PID configuration fault.',QtWidgets.QMessageBox.Ok)
                traceback.print_exc(file=sys.stdout)
                return
            try:
                _list_coeffs = np.zeros(16)
                _kp = Lib.get_value(Lib.ps_settings, 'Kp', float)
                _ki = Lib.get_value(Lib.ps_settings, 'Ki', float)
                _list_coeffs[0] = _kp
                _list_coeffs[1] = _ki
                Lib.comm.drs.Write_dp_Coeffs(_list_coeffs.tolist())       #Write kp and ki
                Lib.comm.drs.ConfigDPModule()                             #Configure kp and ki
                QtWidgets.QMessageBox.information(self,'Success','PID configured.',QtWidgets.QMessageBox.Ok)
    
            except:
                QtWidgets.QMessageBox.critical(self,'Fail','Power Supply write PID fault.\nTry again.',QtWidgets.QMessageBox.Ok)
                traceback.print_exc(file=sys.stdout)
                return
        else:
            return
            
    def dcct_convert(self):
        _reading_34401 = Lib.comm.agilent34401a.collect()
        if _reading_34401 =='':
            self.read_curr = 0
        else:
            if self.ui.dcct_select.currentIndex() == 0:   #For 40 A dcct head
                self.read_curr = (float(_reading_34401))*4
            if self.ui.dcct_select.currentIndex() == 1:   #For 160 A dcct head
                self.read_curr = (float(_reading_34401))*16
            if self.ui.dcct_select.currentIndex() == 2:   #For 320 A dcct head
                self.read_curr = (float(_reading_34401))*32
        return self.read_curr
        
    def display_current(self):
        _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
        Lib.comm.drs.SetSlaveAdd(_ps_type)
        try:
            time.sleep(0.3)
            _refresh_current = round(float(Lib.comm.drs.Read_iLoad1()),3)
            self.ui.lcd_PS_reading.display(_refresh_current)
            if ((self.ui.chb_dcct.isChecked() == True) and (self.ui.chb_enable_Agilent34401A.checkState() != 0)):
                #time.sleep(.1)
                self.ui.lcd_current_dcct.setEnabled(True)
                self.ui.label_161.setEnabled(True)
                self.ui.label_164.setEnabled(True)
                _current = round(self.dcct_convert(), 3)
                self.ui.lcd_current_dcct.display(_current)
                QtWidgets.QApplication.processEvents()
        except:
            QtWidgets.QMessageBox.warning(self,'Fail','Impossible display Current.',QtWidgets.QMessageBox.Ok)
            return
    
    def linear_ramp(self,final,actual,step,timer):
        _mode = 0                    # OpMode ISlowRef
        Lib.comm.drs.OpMode(_mode)
        try:
            _delta = abs(final - actual)
            _step = round(_delta/step)
            if _step < 1:
                _step = 1
            _values = np.linspace(actual, final, _step+1)
            
            for i in _values:
                if (Lib.flags.stop_all == 0):
                    time.sleep(timer)
                    Lib.comm.drs.SetISlowRef(i)
                else:
                    Lib.comm.drs.SetISlowRef(0)
                    time.sleep(0.1)
                    return False
            
            #Comparison between reading and sending value
            time.sleep(0.1)
            _compare = round(float(Lib.comm.drs.Read_iLoad1()),3)
            if final != 0 and (abs(_compare-final) <= abs(final/100)):
                self.display_current() 
                return True
            elif final == 0 and (abs(_compare)<=0.2):
                return True
            else:
                return False        
        except:
            #traceback.print_exc(file=sys.stdout)
            try:
                if ((final>actual) and ((final-actual)<step)) or ((final<actual) and ((actual-final)<step)):
                    Lib.comm.drs.SetISlowRef(final)
                    self.display_current()
                    return True
            except:
                return False
    
    def verify_current_limits(self, index, current, offset=0, secondary=False):
        '''
        Check the conditions of the Current values sets
        If there's an error, returns string 'False' in order to
        avoid confusion when returning the 0.0 value.
        '''
        _current = float(current)
        if not secondary:
            _df = Lib.ps_settings
        else:
            _df = Lib.ps_settings_2
            
        try:
            _current_max = Lib.get_value(_df, 'Maximum Current', float)
        except:
            QtWidgets.QMessageBox.warning(self, 'Attention', 'Incorrect value for maximum Supply Current.\nPlease, verify the value.',QtWidgets.QMessageBox.Ok)
            return 'False'
        try:
            _current_min = Lib.get_value(_df, 'Minimum Current', float)
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Incorrect value for minimum Supply Current.\nPlease, verify the value.',QtWidgets.QMessageBox.Ok)
            return 'False'
        
        if index == 0 or index == 1:
            if _current > _current_max:
                if (index == 0):
                    QtWidgets.QMessageBox.warning(self,'Attention','Value of current higher than the Supply Limit.',QtWidgets.QMessageBox.Ok)
                _current = _current_max
            if _current < _current_min:
                if index == 0:
                    QtWidgets.QMessageBox.warning(self,'Attention','Current value lower than the Supply Limit.',QtWidgets.QMessageBox.Ok)
                _current = _current_min
        elif index == 2:
            if ((_current/2)+offset) > _current_max:
                QtWidgets.QMessageBox.warning(self,'Attention','Check Peak to Peak Current and Offset values.\nValues out of source limit.',QtWidgets.QMessageBox.Ok)
                return 'False'
            
            if ((-_current/2)+offset) < _current_min:
                QtWidgets.QMessageBox.warning(self,'Attention','Check Peak to Peak Current and Offset values.\nValues out of source limit.',QtWidgets.QMessageBox.Ok)
                return 'False'
            
        return float(_current) 
              
    def linear_manual_ramp(self, secondary=False):
        if not secondary:
            self.config_ps()
            _df = Lib.ps_settings
        else:
            self.config_ps_2()
            _df = Lib.ps_settings_2            
        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        Lib.comm.drs.SetSlaveAdd(_ps_type)
        
        _actual = round(float(Lib.comm.drs.Read_iLoad1()),3)
        try:
            if not secondary:
                _df = Lib.ps_settings
            else:
                _df = Lib.ps_settings_2
            _current_setpoint = Lib.get_value(_df,'Current Setpoint',float)
            _final_value = self.verify_current_limits(0, _current_setpoint,secondary)
            if _final_value == 'False':
                return
            Lib.write_value(_df,'Current Setpoint',_final_value,True)
            if not secondary:
                self.ui.dsb_current_setpoint.setValue(float(_final_value))
                Lib.write_value(Lib.aux_settings,'actual_current', Lib.get_value(_df,'Current Setpoint',float))
            else:
                self.ui.dsb_current_setpoint_2.setValue(float(_final_value))
                Lib.write_value(Lib.aux_settings,'actual_current_2', Lib.get_value(_df,'Current Setpoint',float))
            _step = Lib.get_value(_df,'Amplitude Step',float)
            _time = Lib.get_value(_df,'Delay/Step',float)
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Invalid values or not numeric.',QtWidgets.QMessageBox.Ok)
            Lib.write_value(_df,'Current Setpoint', 0)
            if not secondary:
                self.ui.dsb_current_setpoint.setValue(float(0))
            else:
                self.ui.dsb_current_setpoint_2.setValue(float(0))
            Lib.write_value(_df,'Current Setpoint',0.0)
            #return
        if not secondary:
            self.ui.tabWidget_2.setEnabled(False)           #Disabled tabWidget until complete load current
            QtWidgets.QApplication.processEvents()
        else:
            self.ui.tabWidget_5.setEnabled(False)
            QtWidgets.QApplication.processEvents()
            
        _ramp = self.linear_ramp(_final_value, _actual, _step, _time)
    
        if _ramp == True:
            QtWidgets.QMessageBox.information(self,'Information','Select current successfully.',QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.critical(self,'Attention','Fail! \nVerify the Power Supply current values.',QtWidgets.QMessageBox.Ok)
        
        if not secondary:
            self.ui.tabWidget_2.setEnabled(True)
            QtWidgets.QApplication.processEvents()
        else:
            self.ui.tabWidget_5.setEnabled(True)
            QtWidgets.QApplication.processEvents()
        
    def linear_automatic_ramp(self, data_current, secondary=False):
        if not secondary:
            _df = Lib.ps_settings
        else:
            _df = Lib.ps_settings_2            
        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        Lib.comm.drs.SetSlaveAdd(_ps_type)
        
        try:
            _step = Lib.get_value(_df,'Amplitude Step',float)
            _time = Lib.get_value(_df,'Delay/Stepself',float)            
        except:
            QtWidgets.QMessageBox.critical(self,'Attention','Invalid step or time values.',QtWidgets.QMessageBox.Ok)
            return
        for i in range (len(data_current)):
            if abs(data_current[i]-data_current[i-1]) > _step:
                _actual_current = round(float(Lib.comm.drs.Read_iLoad1()),3)
                self.linear_ramp(data_current[i], _actual_current, _step, _time)
            else:
                Lib.comm.drs.SetISlowRef(data_current[i])
                       
        QtWidgets.QMessageBox.information(self,'Information','Automatic collect process done.',QtWidgets.QMessageBox.Ok)    
                            
    def send_curve(self, secondary=False):
        if not secondary:
            self.ui.tabWidget_2.setEnabled(False)
        if self.curve_gen(secondary) == True:
            QtWidgets.QMessageBox.information(self,'Information','Sending Curve Successfully.',QtWidgets.QMessageBox.Ok)
            if not secondary:
                self.ui.tabWidget_2.setEnabled(True)
                self.ui.pb_cycle.setEnabled(True)
            else:
                self.ui.pb_cycle_2.setEnabled(True)
            QtWidgets.QApplication.processEvents()
        else:
            QtWidgets.QMessageBox.critical(self,'Warning','Fail to Sending Curve.',QtWidgets.QMessageBox.Ok)
            if not secondary:
                self.ui.tabWidget_2.setEnabled(True)
            QtWidgets.QApplication.processEvents()
            return False
    
    def curve_gen(self, secondary=False):
        if not secondary:
            self.config_ps()
            _curve_type = int(self.ui.tabWidget_3.currentIndex())
            _df = Lib.ps_settings
        else:
            self.config_ps_2()
            _curve_type = 1 #Only curve available on secondary ps is damped sinusoidal
            _df = Lib.ps_settings_2
            
        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        Lib.comm.drs.SetSlaveAdd(_ps_type)
                                      
        if _curve_type == 0:    # Sinusoidal
            #For Offset
            try:
                _offset = Lib.get_value(_df, 'Sinusoidal Offset', float)
                _offset = self.verify_current_limits(0, _offset)
                if _offset == 'False':
                    self.ui.le_Sinusoidal_Offset.setText('0')
                    Lib.write_value(_df, 'Sinusoidal Offset', 0)
                    return False
                self.ui.le_Sinusoidal_Offset.setText(str(_offset))
                Lib.write_value(_df, 'Sinusoidal Offset', _offset, True)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Offset parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Amplitude
            try:
                _amp = Lib.get_value(_df, 'Sinusoidal Amplitude', float)
                _amp = self.verify_current_limits(2,abs(_amp),_offset)
                if _amp == 'False':
                    self.ui.le_Sinusoidal_Amplitude.setText('0')
                    Lib.write_value(_df, 'Sinusoidal Amplitude', 0)
                    return False
                self.ui.le_Sinusoidal_Amplitude.setText(str(_amp))
                Lib.write_value(_df, 'Sinusoidal Amplitude', _amp, True)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Amplitude parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Frequency
            try:
                _freq = Lib.get_value(_df, 'Sinusoidal Frequency', float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Frequency parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For N-cycles
            try:
                _n_cycles = Lib.get_value(_df, 'Sinusoidal N Cycles', int)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the #cycles parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Phase shift
            try:
                _phase_shift = Lib.get_value(_df, 'Sinusoidal Initial Phase', float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Final phase
            try:
                _final_phase = Lib.get_value(_df, 'Sinusoidal Final Phase', float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Final phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            
        if _curve_type == 1:    # Damped Sinusoidal (can be primary or secondary ps)
            #For Offset
            try:
                _offset = Lib.get_value(_df, 'Damped Sinusoidal Offset', float)
                _offset = self.verify_current_limits(0, _offset)
                if _offset == 'False':
                    Lib.write_value(_df, 'Damped Sinusoidal Offset', 0)
                    if not secondary:
                        self.ui.le_damp_sin_Offset.setText('0')
                    else:
                        self.ui.le_damp_sin_Offset_2.setText('0')
                    return False
                Lib.write_value(_df, 'Damped Sinusoidal Offset', _offset, True)
                if not secondary:
                    self.ui.le_damp_sin_Offset.setText(str(_offset))
                else:
                    self.ui.le_damp_sin_Offset_2.setText(str(_offset))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Offset parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Amplitude
            try:
                _amp = Lib.get_value(_df, 'Damped Sinusoidal Amplitude', float)
                _amp = self.verify_current_limits(2,abs(_amp),_offset)
                if _amp == 'False':
                    Lib.write_value(_df, 'Damped Sinusoidal Amplitude', 0)
                    if not secondary:
                        self.ui.le_damp_sin_Ampl.setText('0')
                    else:
                        self.ui.le_damp_sin_Ampl_2.setText('0')
                    return False
                Lib.write_value(_df, 'Damped Sinusoidal Amplitude', _amp, True)
                if not secondary:
                    self.ui.le_damp_sin_Ampl.setText(str(_amp))
                else:
                    self.ui.le_damp_sin_Ampl_2.setText(str(_amp))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Amplitude parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Frequency
            try:
                _freq = Lib.get_value(_df, 'Damped Sinusoidal Frequency', float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Frequency parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For N-cycles
            try:
                _n_cycles = Lib.get_value(_df, 'Damped Sinusoidal N Cycles', int)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the #cycles parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Phase shift
            try:
                _phase_shift = Lib.get_value(_df, 'Damped Sinusoidal Phase Shift', float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Final phase
            try:
                _final_phase = Lib.get_value(_df, 'Damped Sinusoidal Final Phase', float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Final Phase parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Damping
            try:
                _damping = Lib.get_value(_df, 'Damped Sinusoidal Damping', float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Damping time parameter of the curve.',QtWidgets.QMessageBox.Ok)
                
        if _curve_type == 2:                # Arbitrary Curve
            #For Amplitude
            try:
                _amp = self.verify_current_limits(2,abs(float(self.ui.le_arbitrary_amplitude.text())),_offset)
                if _amp == 'False':
                    self.ui.le_arbitrary_amplitude.setText('0')
                    return False
                self.ui.le_arbitrary_amplitude.setText(str(_amp))
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Amplitude parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For Frequency
            try:
                _freq = float(self.ui.le_arbitrary_frequency.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the Frequency parameter of the curve.',QtWidgets.QMessageBox.Ok)
            #For N-cycles
            try:
                _n_cycles = int(self.ui.le_arbitrary_nCycles.text())
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Please, verify the #cycles parameter of the curve.',QtWidgets.QMessageBox.Ok)
                
        #Generating curves
        try:
            try:
                _mode=3          #Operating mode
                Lib.comm.drs.OpMode(_mode)
                if Lib.comm.drs.Read_ps_OpMode()!=3:
                    QtWidgets.QMessageBox.warning(self,'Attention','Signal generator not configured correctly.',QtWidgets.QMessageBox.Ok)
                    return False
            except:
                QtWidgets.QMessageBox.warning(self,'Attention','Signal generator not configured correctly. Verify PS settings.',QtWidgets.QMessageBox.Ok)
                return
                            
            if _curve_type == 0:        # Sinusoidal
                try:
                    _sigType=0
                    Lib.comm.drs.Write_sigGen_Freq(float(_freq))        #send Frequency
                    Lib.comm.drs.Write_sigGen_Amplitude(float(_amp))    #send Amplitude
                    Lib.comm.drs.Write_sigGen_Offset(float(_offset))    #send Offset
                    #Sending curves to PS Controller
                    Lib.comm.drs.ConfigSigGen(_sigType, _n_cycles, _phase_shift, _final_phase)
                except:
                    traceback.print_exc(file=sys.stdout)
                    QtWidgets.QMessageBox.warning(self,'Attention','Fail to send config to Controller.\nPlease, verify the parameters of the Power Supply.',QtWidgets.QMessageBox.Ok)
                    return
                
            if _curve_type == 1:        # Damped Sinusoidal                
                try:
                    _sigType=4
                    Lib.comm.drs.Write_sigGen_Freq(float(_freq))             
                    Lib.comm.drs.Write_sigGen_Amplitude(float(_amp))         
                    Lib.comm.drs.Write_sigGen_Offset(float(_offset))    
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention','Please, verify the parameters of the Power Supply.',QtWidgets.QMessageBox.Ok)
                    return
    
                #Sending sigGenDamped
                try:
                    Lib.comm.drs.Write_sigGen_Aux(float(self.ui.le_damp_sin_Damping.text()))
                    Lib.comm.drs.ConfigSigGen(_sigType, _n_cycles, _phase_shift, _final_phase)
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention.','Damped Sinusoidal fault.',QtWidgets.QMessageBox.Ok)
                    traceback.print_exc(file=sys.stdout)
                    return False
            
            return True
        except:
            return False
        
    def reset_interlocks(self, secondary=False):
        if not secondary:
            _df = Lib.ps_settings
        else:
            _df = Lib.ps_settings_2
        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        Lib.comm.drs.SetSlaveAdd(_ps_type)
        
        try:
            Lib.comm.drs.ResetInterlocks()
            if not secondary:
                if self.ui.pb_interlock.isChecked():
                    self.ui.pb_interlock.setChecked(False)
            else:
                if self.ui.pb_interlock_2.isChecked():
                    self.ui.pb_interlock_2.setChecked(False)
            QtWidgets.QMessageBox.information(self,'Information','Interlocks reseted.',QtWidgets.QMessageBox.Ok)
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Interlocks not reseted.',QtWidgets.QMessageBox.Ok)
            return

    def cycling_ps(self, secondary=False):
        if not secondary:
            _curve_type = int(self.ui.tabWidget_3.currentIndex())
            _df = Lib.ps_settings
        else:
            _curve_type = 1 #Only curve available on secondary ps is damped sinusoidal
            _df = Lib.ps_settings_2

        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        Lib.comm.drs.SetSlaveAdd(_ps_type)

        try:
            if _curve_type == 0:
                Lib.comm.drs.EnableSigGen()
                _freq = Lib.get_value(_df, 'Sinusoidal Frequency', float)
                _n_cycles = Lib.get_value(_df, 'Sinusoidal N Cycles', float)
            if _curve_type == 1:
                Lib.comm.drs.EnableSigGen()
                _freq = Lib.get_value('Damped Sinusoidal Frequency', float)
                _n_cycles = Lib.get_value('Damped Sinusoidal N Cycles', float) 
                time.sleep(.2)
            _deadline = time.monotonic() + (1/_freq*_n_cycles)
            while time.monotonic() < _deadline:
                if not secondary:
                    self.ui.tabWidget_2.setEnabled(False)
                    self.ui.pb_load_PS.setEnabled(False)
                    self.ui.pb_refresh.setEnabled(False)
                else:
                    self.ui.pb_load_PS_2.setEnabled(False)
                self.ui.pb_start_meas.setEnabled(False)
                QtWidgets.QApplication.processEvents()
            
            QtWidgets.QMessageBox.information(self,'Information','Successful cycle process.',QtWidgets.QMessageBox.Ok)
            Lib.comm.drs.DisableSigGen()
            if not secondary:
                self.ui.tabWidget_2.setEnabled(True)
                self.ui.pb_load_PS.setEnabled(True)
                self.ui.pb_refresh.setEnabled(True)
            else:
                self.ui.pb_load_PS_2.setEnabled(True)
            self.ui.pb_start_meas.setEnabled(True)
            QtWidgets.QApplication.processEvents()
            
            if _curve_type == 2:
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
        _address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        _ratio = Lib.get_value(Lib.data_settings,'rotation_motor_ratio',float)

        _resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)        
        _vel = float(self.ui.le_motor_vel.text()) * _ratio
        _acce = float(self.ui.le_motor_ace.text()) * _ratio
        _nturns = float(self.ui.le_motor_turns.text()) * _ratio

        _direction = self.ui.cb_driver_direction.currentIndex()
        _steps = abs(int(_nturns * Lib.get_value(Lib.data_settings,'rotation_motor_resolution',float)))

        # mode
        if self.ui.cb_driver_mode.currentIndex() == 0:
            _mode = 0
        else:
            _mode = 1

        Lib.comm.parker.conf_motor(_address, _resolution, _vel, _acce, _steps, _direction, _mode)

        self.move_motor_until_stops(_address)

    def stop_motor(self): # Ok
        """
        """
        Lib.flags.stop_all = True        
        _address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        Lib.comm.parker.stopmotor(_address)

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

        _address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        _ratio = Lib.get_value(Lib.data_settings,'rotation_motor_ratio',float)

        _resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)
        _vel = float(self.ui.le_motor_vel.text()) * _ratio
        _acce = float(self.ui.le_motor_ace.text()) * _ratio

        _pulses = self.pulses_to_go()
        _steps =  abs(int( _pulses * Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int) / Lib.get_value(Lib.data_settings,'n_encoder_pulses',int) * _ratio))

        if _pulses >= 0:
            _direction = 0
        else:
            _direction = 1

        Lib.comm.parker.conf_motor(_address, _resolution, _vel, _acce, _steps, _direction, 0)
        self.move_motor_until_stops(_address)

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
        _address = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        _ratio = Lib.get_value(Lib.data_settings,'rotation_motor_ratio',float)

        _resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)
        _vel = Lib.get_value(Lib.data_settings,'rotation_motor_speed',float) * _ratio
        _acce = Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',float) * _ratio
#         nturns = float(self.ui.le_motor_turns.text()) * _ratio
        _nturns = turns * _ratio        

        try:
            if Lib.get_value(Lib.measurement_settings, 'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()
        _steps = abs(int(_nturns * Lib.get_value(Lib.data_settings,'rotation_motor_resolution',float)))

        _mode = 0

        Lib.comm.parker.conf_motor(_address, _resolution, _vel, _acce, _steps, _direction, _mode)
        
        self.move_motor_until_stops(_address)
        
    def get_coil_ref(self): # Ok
        """
        """
        Lib.flags.stop_all = False

        _res = QtWidgets.QMessageBox.warning(self,'Search Index','Continue to search for coil index?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if _res == QtWidgets.QMessageBox.Yes:
            # configure integrator encoder
            _n_encoder_pulses = int(Lib.get_value(Lib.data_settings,'n_encoder_pulses',float)/4)
            Lib.comm.fdi.config_encoder(_n_encoder_pulses)

            # Send command to find integrator reference
            try:
                if Lib.get_value(Lib.measurement_settings, 'coil_rotation_direction', str) == 'Clockwise':
                    _direction = 0
                else:
                    _direction = 1
            except:
                _direction = self.ui.cb_coil_rotation_direction.currentIndex()
            Lib.comm.fdi.index_search(_direction)

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
                #If OKAY
                self.ui.lb_status_coil.setText('OK')                
            else:
                QtWidgets.QMessageBox.warning(self,'Attention','Fail to load Coil File.',QtWidgets.QMessageBox.Ok)
                self.ui.lb_status_coil.setText('NOK')
                 
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
        
    def save_PowerSupply(self, secondary=False):
        """
        save settings of the Power Supply in external file
        """
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Power Supply File', Lib.dir_path, 'Data files (*.dat);;Text files (*.txt)')
            
            if not secondary:
                self.config_ps()
                _ans = Lib.save_ps(filename[0])
            else:
                self.config_ps_2()
                _ans = Lib.save_ps(filename[0], secondary=True)
            if _ans:
                QtWidgets.QMessageBox.warning(self,'Information','Power Supply File saved.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Information','Fail to save Power Supply File.',QtWidgets.QMessageBox.Ok) 
        except:
            return
        
    def load_PowerSupply(self, secondary=False):
        """
        load settings of the Power Supply in the interface
        """
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,'Load Power Supply File' , Lib.dir_path, 'Data files (*.dat);;Text files (*.txt)')
            if not secondary:
                _ans = Lib.load_ps(filename[0])
            else:
                _ans = Lib.load_ps(filename[0], secondary=True)
            if _ans == True:
                if not secondary:
                    self.refresh_ps_settings()
                    self.ui.gb_start_supply.setEnabled(True)
                    self.ui.pb_send.setEnabled(True)
                    self.ui.pb_send_curve.setEnabled(True)
                else:
                    self.refresh_ps_settings_2()
                    self.ui.gb_start_supply_2.setEnabled(True)
                    self.ui.pb_send_2.setEnabled(True)
                    self.ui.pb_send_curve_2.setEnabled(True)
                QtWidgets.QMessageBox.information(self,'Information','Power Supply File loaded.',QtWidgets.QMessageBox.Ok)
                self.ui.tabWidget_2.setEnabled(True)
                self.ui.tabWidget_3.setEnabled(True)
                self.ui.pb_refresh.setEnabled(True)
            else:
                QtWidgets.QMessageBox.information(self,'Information','Fail to load Power Supply File.',QtWidgets.QMessageBox.Ok) 
        except:
            traceback.print_exc(file=sys.stdout)
            QtWidgets.QMessageBox.warning(self,'Warning',"Couldn't load the power supply settings.\nCheck if the configuration file values are correct.",QtWidgets.QMessageBox.Ok)

    def start_meas(self):
        """ 
        """
        self.ui.pb_start_meas.setEnabled(False)
        Lib.flags.stop_all = False        
        
        # data array
        self.data_array = np.array([])
        self.df_rawcurves = None   
        
        # configure integrator
        if self.configure_integrator():
            self.ui.lb_status_integrator.setText('OK')
        else:
            self.ui.lb_status_integrator.setText('NOK')
            return
            
        # check components
#         self.collect_infocomponents()
        
        # routine Collect
        self.collect_routine()
        
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
        try:
            Lib.comm.display.readdisplay_ND780()
            time.sleep(0.3)
            _disp_pos = Lib.comm.display.DisplayPos
            Lib.write_value(Lib.aux_settings, 'ref_encoder_A', _disp_pos[0], True)
            Lib.write_value(Lib.aux_settings, 'ref_encoder_B', _disp_pos[1], True)
            if Lib.get_value(Lib.data_settings, 'disable_alignment_interlock', int):
                return True
            else:
                if (abs(Lib.get_value(Lib.aux_settings, 'ref_encoder_A', float))>0.005) or (abs(Lib.get_value(Lib.aux_settings, 'ref_encoder_B', float))>0.005):
                    QtWidgets.QMessageBox.warning(self, 'Attention', 'Fix the transversal encoders', QtWidgets.QMessageBox.Ok)
                    return False
                else:
                    return True
        except:
            QtWidgets.QMessageBox.warning(self, 'Attention', 'Impossible to read Display ND 780', QtWidgets.QMessageBox.Ok)
            return False
     
    def collect_infocomponents(self):
        '''
        Currents and setup verification routines
        '''
        _collect_type = 0  #single Collect
        try:
            if self.misalignment():
                pass
            else:
                return False
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','Stages alignment.',QtWidgets.QMessageBox.Ok)
            
            #IMPLEMENT==========================================================
            # _interlocks = self.check_interlocks()
            # if _interlocks == False:
            #     return False       
            #===================================================================
        
#             if (Lib.vars.Status_PS != 1): #and (Lib.vars.PS_ready == 0):
#                 QtWidgets.QMessageBox.warning(self,'Attention','Power supply is not ready.\nVerify PS data.',QtWidgets.QMessageBox.Ok)
#                 return False
        if self.ui.lb_status_ps.text() == 'NOK':
            QtWidgets.QMessageBox.warning(self,'Attention','Power supply is not ready.\nVerify PS data.',QtWidgets.QMessageBox.Ok)
            return False
        if self.ui.lb_status_coil.text() == 'NOK':
            QtWidgets.QMessageBox.warning(self,'Attention','Please, load the coil data.',QtWidgets.QMessageBox.Ok)
            return False
        if self.ui.lb_status_integrator.text() == 'NOK':
            QtWidgets.QMessageBox.warning(self,'Attention','Please, configure the Integrator FDI 2056.',QtWidgets.QMessageBox.Ok)
            return False
            
        if self.ui.chb_automatic_ps.isChecked():
            _collect_type = 2  #Automatic collect
            
        if self.ui.chb_seriesofmeas.isChecked():
            _collect_type = 1  #Successive collect  
        
        return _collect_type
            
    def collect_routine(self):
        """
        Currents adjustments and setup verification routines
        """
        _collect_type = self.collect_infocomponents()
        self.max_gain_check()
        self.ui.lb_meas_counter.setText('0')
        QtWidgets.QApplication.processEvents()
        try:
            if _collect_type == 0:               #Collect routine of the manual current for single collect
                self.coil_position_correction()
#                 _verify = Collect_Data()         #IMPLEMENT!! - Check the maximum standard deviation
#                 if _verify == False:
#                     QtWidgets.QMessageBox.warning(self, "Attention","High Standard deviation. Process done. \nCheck parameters and equipments",QtWidgets.QMessageBox.Ok)
#                     ret = QtWidgets.QMessageBox.question(self,'Standard Deviation','Show data with high Standard Deviation?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.Yes)
#                     if ret == QtWidgets.QMessageBox.Yes:
#                         self.ui.pb_start_meas.setEnabled(True)
# #                         self.multipoles_table()        # Call multipoles table
#                         self.ui.lb_meas_counter.setText('1')
#                         QtWidgets.QApplication.processEvents()
#                         return
#                     else:
#                         self.ui.pb_start_meas.setEnabled(True)
#                         QtWidgets.QApplication.processEvents()
#                         return
                #self.multipoles_calculation()            # Call multipoles calculation
                self.ui.lb_meas_counter.setText('1')
                QtWidgets.QApplication.processEvents()
    
            if _collect_type == 1: #Collect routine for the manual current with successive collects
                try:
                    _number_col = Lib.get_value(Lib.measurement_settings,'n_collections',int)
                    if _number_col <= 1:
                        QtWidgets.QMessageBox.warning(self,'Attention',' Number of collects must be greater than 1.\nTry again.',QtWidgets.QMessageBox.Ok)
                        
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention','Not integer number of successive collects.\nTry again.',QtWidgets.QMessageBox.Ok)
                    return
                ret = QtWidgets.QMessageBox.question(self,'Automatic collect','Do you want to automatically collect ' + str(_number_col) + ' measurements of the same current?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return
                self.ui.pb_start_meas.setEnabled(False)
                self.ui.le_n_collections.setEnabled(False)
                for i in range(0,_number_col,1):
                    self.coil_position_correction()
#                     _verify = Collect_Data(_number_col)  #IMPLEMENT
#                     if _verify == False:
#                         QtWidgets.QMessageBox.warning(self,'Warning','Measurement Process Interrupted. High Standard Deviation.',QtWidgets.QMessageBox.Ok)
#                         ret = QtWidgets.QMessageBox.question(self,'Standard Deviation','High Standard Deviation. \nDo you want to save this measurement?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.Yes)
#                         if ret == QtWidgets.QMessageBox.Yes:
#                             pass
#                         else:
#                             ret = QtWidgets.QMessageBox.question(self,'Standard Deviation','Do you want to continue with the process?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.Yes)
#                             if ret == QtWidgets.QMessageBox.Yes:
#                                 continue
#                             else:
#                                 self.ui.pb_start_meas.setEnabled(True)
#                                 self.ui.le_n_collections.setEnabled(True)
#                                 QtWidgets.QApplication.processEvents()
#                                 return
                    time.sleep(1)
                    #self.Salvar_Coletas(1,(i+1),dados_corrente)
                    self.ui.lb_meas_counter.setText(str(i+1))
                    QtWidgets.QApplication.processEvents()  
                
                QtWidgets.QMessageBox.information(self,'Information','Automatic Collect Process Completed.',QtWidgets.QMessageBox.Ok)
                self.ui.pb_start_meas.setEnabled(True)
                self.ui.le_n_collections.setEnabled(True)
                
            if _collect_type == 2:                              #Collect routine with automatic current
                try:
                    _current_data = self.keep_auto_values(1)    #Storage the current values from automatic settings
                            
                    for i in range(len(_current_data)):
                            _current_data[i]=self.verify_current_limits(1,_current_data[i])
                            if _current_data[i] == 'False':
                                return
                except:
                    QtWidgets.QMessageBox.warning(self,'Attention','Verify automatic settings values.\nTry again.',QtWidgets.QMessageBox.Ok)
                    return
                ret = QtWidgets.QMessageBox.question(self,'Automatic Settings','Do you want initialize the automatic collect ' + str(len(_current_data)) + ' different measurements?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return            
                
                self.ui.pb_start_meas.setEnabled(False)
                self.linear_automatic_ramp(_current_data)
                self.ui.pb_start_meas.setEnabled(True)
        except:
            QtWidgets.QMessageBox.warning(self,'Attention','collect routine fault',QtWidgets.QMessageBox.Ok)
            return        
            
    def coil_position_correction(self):
        """
        Before start measurement, keep coil in ref trigger + half turn
        """
        _velocity = Lib.get_value(Lib.data_settings,'rotation_motor_speed',int)
        _acceleration = Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',int)
        _trigger = Lib.get_value(Lib.coil_settings,'trigger_ref',int)
        _encoder_pulse = Lib.get_value(Lib.data_settings,'n_encoder_pulses',int)
    
        _position = _trigger + (_encoder_pulse / 2)
        if _position > _encoder_pulse:
            _position = _position - _encoder_pulse
            
        _address_motor = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        
        self.angular_position(_position,_address_motor,_velocity,_acceleration,_encoder_pulse)
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
        _rotation_motor_resolution = Lib.get_value(Lib.data_settings,'rotation_motor_resolution',int)
        
        #Direction
        try:
            if Lib.get_value(Lib.measurement_settings, 'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()        

        _steps = int(_rotation_motor_resolution*abs(shift)/pulse_encoder)  #/10000
        Lib.comm.parker.conf_motor(address_motor,_rotation_motor_resolution,velocity,acceleration,_steps,_direction,mode=0)
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
            if Lib.get_value(Lib.aux_settings, 'status_ps_2', int):
                self.dialog.cb_trim_coil_type.setEnabled(True)
            self.dialog.ui.bB_ok_cancel.accepted.connect(self.ok_popup)
            self.dialog.ui.bB_ok_cancel.rejected.connect(self.cancel_popup)        
            self.dialog.exec_()
        except:
            traceback.print_exc(file=sys.stdout)
        
    def ok_popup(self):
        Lib.measurement_df()
        if Lib.get_value(Lib.aux_settings, 'status_ps_2', int):
            Lib.write_value(Lib.measurement_settings, 'trim_coil_type', self.dialog.cb_trim_coil_type.currentIndex())
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
            
            Lib.write_value(Lib.measurement_settings, 'magnetic_center_x', _dx, True)
            Lib.write_value(Lib.measurement_settings, 'magnetic_center_y', _dy, True)

        else:
            self.ui.le_magnetic_center_x.setText("")
            self.ui.le_magnetic_center_y.setText("")

    def configure_integrator(self): # Ok
        """
        """
        _n_of_turns = Lib.get_value(Lib.data_settings,'total_number_of_turns',int)

        _n_encoder_pulses = int(Lib.get_value(Lib.data_settings, 'n_encoder_pulses', float)/4)
        _gain =  Lib.get_value(Lib.data_settings, 'integrator_gain', int)
        try:
            if Lib.get_value(Lib.measurement_settings, 'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()
        _trigger_ref = Lib.get_value(Lib.coil_settings, 'trigger_ref', int)
        _n_integration_points = Lib.get_value(Lib.data_settings, 'n_integration_points', int)
        _total_n_of_points = _n_integration_points * _n_of_turns
        
        try:
            Lib.comm.fdi.config_measurement(_n_encoder_pulses, _gain, _direction, _trigger_ref, _n_integration_points, _n_of_turns)
            return True
        except:
            return False       

    def measure_and_read(self): # Ok
        """
        """
        #if it is a series of measurements, starts monitor thread
        if self.ui.chb_seriesofmeas.isChecked():
            _thread = threading.Thread(target=self.monitor_thread, name='Monitor Thread')
            _thread.start()
        
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
        _dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save Directory', Lib.dir_path).replace('/', '\\\\') + '\\\\'
        Lib.save_log_file(path=_dir)

    def stop_meas(self): # Ok
        self.stop_motor()

    def refresh_interface(self):
        """
        """
        self.refresh_connection_settings_tab()
                
#     def check_parameters(self,_func):
#         '''
#         Check if all data entry in Dataframes are valid
#         '''
# #         _df_settings = Lib.data_settings
# #         _df_PS = Lib.PS_settings
#         #_var = ''
#         _flag = 0
#         #_df_meas = Lib.measurement_settings
#         
#         if _func == 1: _df = Lib.data_settings
#         if _func == 2: _df = Lib.PS_settings
#         
#         # Checking if all data entry are valid -> PS Settings
#         #_len_PS_df = _df_PS.datavalues.__len__()
#         for i in range (1,_df.datavalues.__len__()):
#             if not _df.get_values()[14].astype(float).item().is_integer():
#                 _flag += 1
 
#             
#             try:
#                 if _df.get_values()[i].astype(float).item() == float:
#                     pass
#             except:
#                 try:
#                     _var = _df.get_values()[i][0].split(',')
#                     _var = np.asarray(_var, dtype=float64)
#                 except:
#                     try:
#                         if _df.get_values()[i].astype(str).item() == str:
#                         
#                     _flag += 1
#             
#         print('Ok')
#         print(_flag)
                    
                #return False
            #_df_PS.get_values()[i]    
    
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
        self.ui.chb_disable_alignment_interlock.setChecked(Lib.get_value(Lib.data_settings,'disable_alignment_interlock',int))
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
        try:
            # Connection Tab 
            Lib.write_value(Lib.data_settings,'display_type',self.ui.cb_display_type.currentIndex(),True)
            Lib.write_value(Lib.data_settings,'disp_port',self.ui.cb_disp_port.currentText())
            Lib.write_value(Lib.data_settings,'driver_port',self.ui.cb_driver_port.currentText())
            Lib.write_value(Lib.data_settings,'integrator_port',self.ui.cb_integrator_port.currentText())
            Lib.write_value(Lib.data_settings,'ps_port',self.ui.cb_ps_port.currentText())
    
            Lib.write_value(Lib.data_settings,'enable_Agilent33220A',self.ui.chb_enable_Agilent33220A.checkState())
            Lib.write_value(Lib.data_settings,'agilent33220A_address',self.ui.sb_agilent33220A_address.value(),True)
    
            Lib.write_value(Lib.data_settings,'enable_Agilent34401A',self.ui.chb_enable_Agilent34401A.checkState())
            Lib.write_value(Lib.data_settings,'agilent34401A_address',self.ui.sb_agilent34401A_address.value(),True)
    
            Lib.write_value(Lib.data_settings,'enable_Agilent34970A',self.ui.chb_enable_Agilent34970A.checkState())
            Lib.write_value(Lib.data_settings,'agilent34970A_address',self.ui.sb_agilent34970A_address.value(),True)
                   
            # Settings Tab
            Lib.write_value(Lib.data_settings,'total_number_of_turns',self.ui.le_total_number_of_turns.text(),True)
            Lib.write_value(Lib.data_settings,'remove_initial_turns',self.ui.le_remove_initial_turns.text(),True)
            Lib.write_value(Lib.data_settings,'remove_final_turns',self.ui.le_remove_final_turns.text(),True)
            
            Lib.write_value(Lib.data_settings,'ref_encoder_A',self.ui.le_ref_encoder_A.text(),True)
            Lib.write_value(Lib.data_settings,'ref_encoder_B',self.ui.le_ref_encoder_B.text(),True)
    
            Lib.write_value(Lib.data_settings,'rotation_motor_address',self.ui.le_rotation_motor_address.text(),True)
            Lib.write_value(Lib.data_settings,'rotation_motor_resolution',self.ui.le_rotation_motor_resolution.text(),True)        
            Lib.write_value(Lib.data_settings,'rotation_motor_speed',self.ui.le_rotation_motor_speed.text(),True)
            Lib.write_value(Lib.data_settings,'rotation_motor_acceleration',self.ui.le_rotation_motor_acceleration.text(),True)
            Lib.write_value(Lib.data_settings,'rotation_motor_ratio',self.ui.le_rotation_motor_ratio.text(),True)
            
            Lib.write_value(Lib.data_settings,'poscoil_assembly',self.ui.le_poscoil_assembly.text(),True)
            Lib.write_value(Lib.data_settings,'n_encoder_pulses',self.ui.le_n_encoder_pulses.text(),True)  
    
            Lib.write_value(Lib.data_settings,'integrator_gain',int(self.ui.cb_integrator_gain.currentText()))
            Lib.write_value(Lib.data_settings,'n_integration_points',int(self.ui.cb_n_integration_points.currentText()))
    
            Lib.write_value(Lib.data_settings,'save_turn_angles',self.ui.chb_save_turn_angles.checkState())
            Lib.write_value(Lib.data_settings,'disable_alignment_interlock',self.ui.chb_disable_alignment_interlock.checkState())
            Lib.write_value(Lib.data_settings,'disable_ps_interlock',self.ui.chb_disable_ps_interlock.checkState())
            
            Lib.write_value(Lib.data_settings,'bench',self.ui.cb_bench.currentIndex())
        except:
            QtWidgets.QMessageBox.warning(self,'Warning',"Couldn't configure the settings.\nCheck if all the inputs are numbers.",QtWidgets.QMessageBox.Ok)
  
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
        try:
            # Coil Tab
            Lib.write_value(Lib.coil_settings,'coil_name',self.ui.le_coil_name.text())
            Lib.write_value(Lib.coil_settings,'n_turns_normal',self.ui.le_n_turns_normal.text(),True)
            Lib.write_value(Lib.coil_settings,'radius1_normal',self.ui.le_radius1_normal.text(),True)
            Lib.write_value(Lib.coil_settings,'radius2_normal',self.ui.le_radius2_normal.text(),True)
            Lib.write_value(Lib.coil_settings,'n_turns_bucked',self.ui.le_n_turns_bucked.text(),True)        
            Lib.write_value(Lib.coil_settings,'radius1_bucked',self.ui.le_radius1_bucked.text(),True)
            Lib.write_value(Lib.coil_settings,'radius2_bucked',self.ui.le_radius2_bucked.text(),True)
            Lib.write_value(Lib.coil_settings,'trigger_ref',self.ui.le_trigger_ref.text(),True)
            Lib.write_value(Lib.coil_settings,'coil_type',self.ui.cb_coil_type.currentText())
            Lib.write_value(Lib.coil_settings,'comments',self.ui.te_comments.toPlainText())
        except:
            QtWidgets.QMessageBox.warning(self,'Warning',"Couldn't configure the coil settings.\nCheck if all the coil inputs are correct.",QtWidgets.QMessageBox.Ok)
        
    def refresh_ps_settings(self):
        """
        When connected "Load Power Supply", refresh interface with values of the database 
        """
        #Power Supply Tab
        #Configuration
        self.ui.cb_ps_type.setCurrentIndex(Lib.get_value(Lib.ps_settings,'Power Supply Type',int)-2)
        self.ui.le_PS_Name.setText(Lib.get_value(Lib.ps_settings,'Power Supply Name',str))
        #Current Adjustment
        self.ui.dsb_current_setpoint.setValue(Lib.get_value(Lib.ps_settings,'Current Setpoint',float))
        self.ui.dsb_Amplitude_Linear.setValue(Lib.get_value(Lib.ps_settings,'Amplitude Step',float))
        self.ui.dsb_Time_Linear.setValue(Lib.get_value(Lib.ps_settings,'Delay/Step',float))
        self.keep_auto_values()
        #Demagnetization Curves
        #Sinusoidal
        self.ui.le_Sinusoidal_Amplitude.setText(str(Lib.get_value(Lib.ps_settings,'Sinusoidal Amplitude',float)))
        self.ui.le_Sinusoidal_Offset.setText(str(Lib.get_value(Lib.ps_settings,'Sinusoidal Offset',float)))
        self.ui.le_Sinusoidal_Frequency.setText(str(Lib.get_value(Lib.ps_settings,'Sinusoidal Frequency',float)))
        self.ui.le_Sinusoidal_n_cycles.setText(str(Lib.get_value(Lib.ps_settings,'Sinusoidal N Cycles',int)))
        self.ui.le_Initial_Phase.setText(str(Lib.get_value(Lib.ps_settings,'Sinusoidal Initial Phase',float)))
        self.ui.le_Final_Phase.setText(str(Lib.get_value(Lib.ps_settings,'Sinusoidal Final Phase',float)))
        #Damped Sinusoidal
        self.ui.le_damp_sin_Ampl.setText(str(Lib.get_value(Lib.ps_settings,'Damped Sinusoidal Amplitude',float)))
        self.ui.le_damp_sin_Offset.setText(str(Lib.get_value(Lib.ps_settings,'Damped Sinusoidal Offset',float)))
        self.ui.le_damp_sin_Freq.setText(str(Lib.get_value(Lib.ps_settings,'Damped Sinusoidal Frequency',float)))
        self.ui.le_damp_sin_nCycles.setText(str(Lib.get_value(Lib.ps_settings,'Damped Sinusoidal N Cycles',int)))
        self.ui.le_damp_sin_phaseShift.setText(str(Lib.get_value(Lib.ps_settings,'Damped Sinusoidal Phase Shift',float)))
        self.ui.le_damp_sin_finalPhase.setText(str(Lib.get_value(Lib.ps_settings,'Damped Sinusoidal Final Phase',float)))
        self.ui.le_damp_sin_Damping.setText(str(Lib.get_value(Lib.ps_settings,'Damped Sinusoidal Damping',float)))
        #Arbitrary Curve
        self.ui.le_arbitrary_amplitude.setText(str(Lib.get_value(Lib.ps_settings,'Arbitrary Amplitude',float)))
        self.ui.le_arbitrary_frequency.setText(str(Lib.get_value(Lib.ps_settings,'Arbitrary Frequency',float)))
        self.ui.le_arbitrary_nCycles.setText(str(Lib.get_value(Lib.ps_settings,'Arbitrary N Cycles',int)))
        self.ui.le_arbitrary_file.setText(str(Lib.get_value(Lib.ps_settings,'Arbitrary File',str)))
        #Settings
        self.ui.le_maximum_current.setText(str(Lib.get_value(Lib.ps_settings,'Maximum Current',float)))
        self.ui.le_minimum_current.setText(str(Lib.get_value(Lib.ps_settings,'Minimum Current',float)))
        self.ui.sb_kp.setValue(Lib.get_value(Lib.ps_settings,'Kp',float))
        self.ui.sb_ki.setValue(Lib.get_value(Lib.ps_settings,'Ki',float))

    def configure_ps(self, secondary=False):
        if not secondary:
            if Lib.ps_settings == None:
                Lib.ps_df(False)
                self.ui.gb_start_supply.setEnabled(True)
                self.ui.pb_send.setEnabled(True)
                self.ui.pb_send_curve.setEnabled(True)
            _ans = self.config_ps()
        else:
            if Lib.ps_settings_2 == None:
                Lib.ps_df(True)
                self.ui.gb_start_supply_2.setEnabled(True)
                self.ui.pb_send_2.setEnabled(True)
                self.ui.pb_send_curve_2.setEnabled(True)
            _ans = self.config_ps_2()
        if _ans:
            QtWidgets.QMessageBox.warning(self,'Warning',"Configurations are now set on the Data Frame.",QtWidgets.QMessageBox.Ok)
    
    def config_ps(self):
        """
        Write variables with interface values for new features
        """
        try:
            # Power Supply Tab
            Lib.write_value(Lib.ps_settings,'Power Supply Name',self.ui.le_PS_Name.text())
            Lib.write_value(Lib.ps_settings,'Power Supply Type', self.ui.cb_ps_type.currentIndex()+2,True)
            Lib.write_value(Lib.ps_settings,'Current Setpoint',self.ui.dsb_current_setpoint.value(),True)
            Lib.write_value(Lib.ps_settings,'Amplitude Step',self.ui.dsb_Amplitude_Linear.value(),True)
            Lib.write_value(Lib.ps_settings,'Delay/Step',self.ui.dsb_Time_Linear.value(),True)
            Lib.write_value(Lib.ps_settings,'Sinusoidal Amplitude',self.ui.le_Sinusoidal_Amplitude.text(),True)
            Lib.write_value(Lib.ps_settings,'Sinusoidal Offset',self.ui.le_Sinusoidal_Offset.text(),True)
            Lib.write_value(Lib.ps_settings,'Sinusoidal Frequency',self.ui.le_Sinusoidal_Frequency.text(),True)
            Lib.write_value(Lib.ps_settings,'Sinusoidal N Cycles',self.ui.le_Sinusoidal_n_cycles.text(),True)
            Lib.write_value(Lib.ps_settings,'Sinusoidal Initial Phase',self.ui.le_Initial_Phase.text(),True)
            Lib.write_value(Lib.ps_settings,'Sinusoidal Final Phase', self.ui.le_Final_Phase.text(),True)
            #Damped Sinusoidal
            Lib.write_value(Lib.ps_settings,'Damped Sinusoidal Amplitude',self.ui.le_damp_sin_Ampl.text(),True)
            Lib.write_value(Lib.ps_settings,'Damped Sinusoidal Offset',self.ui.le_damp_sin_Offset.text(),True)
            Lib.write_value(Lib.ps_settings,'Damped Sinusoidal Frequency',self.ui.le_damp_sin_Freq.text(),True)
            Lib.write_value(Lib.ps_settings,'Damped Sinusoidal N Cycles',self.ui.le_damp_sin_nCycles.text(),True)
            Lib.write_value(Lib.ps_settings,'Damped Sinusoidal Phase Shift',self.ui.le_damp_sin_phaseShift.text(),True)
            Lib.write_value(Lib.ps_settings,'Damped Sinusoidal Final Phase',self.ui.le_damp_sin_finalPhase.text(),True)
            Lib.write_value(Lib.ps_settings,'Damped Sinusoidal Damping',self.ui.le_damp_sin_Damping.text(),True)
            #Arbitrary Curve
            Lib.write_value(Lib.ps_settings,'Arbitrary Amplitude',self.ui.le_arbitrary_amplitude.text(),True)
            Lib.write_value(Lib.ps_settings,'Arbitrary Frequency',self.ui.le_arbitrary_frequency.text(),True)
            Lib.write_value(Lib.ps_settings,'Arbitrary N Cycles',self.ui.le_arbitrary_nCycles.text(),True)
            Lib.write_value(Lib.ps_settings,'Arbitrary File',self.le_arbitrary_file.text())
            #Automatic setpoints
            _values = self.keep_auto_values(1)
            _values = " ".join(str(x) for x in _values)          
            Lib.write_value(Lib.ps_settings,'Automatic Setpoints',_values,True) # Need revision       
            #Settings
            Lib.write_value(Lib.ps_settings,'Maximum Current',self.ui.le_maximum_current.text(),True)
            Lib.write_value(Lib.ps_settings,'Minimum Current',self.ui.le_minimum_current.text(),True)
            Lib.write_value(Lib.ps_settings,'Kp',self.ui.sb_kp.text(),True)
            Lib.write_value(Lib.ps_settings,'Ki',self.ui.sb_ki.text(),True)
            return True
        except:
            QtWidgets.QMessageBox.warning(self,'Warning',"Couldn't configure the power supply settings.\nCheck if all the inputs are correct.",QtWidgets.QMessageBox.Ok)
            return False

    def refresh_ps_settings_2(self):
        """
        When connected "Load Power Supply", refresh interface with values of the database 
        """
        #Power Supply Tab
        #Configuration
        self.ui.cb_ps_type_2.setCurrentIndex(Lib.get_value(Lib.ps_settings_2,'Power Supply Type',int)-4)
        self.ui.le_PS_Name_2.setText(Lib.get_value(Lib.ps_settings_2,'Power Supply Name',str))
        #Current Adjustment
        self.ui.dsb_current_setpoint_2.setValue(Lib.get_value(Lib.ps_settings_2,'Current Setpoint',float))
        self.ui.dsb_Amplitude_Linear_2.setValue(Lib.get_value(Lib.ps_settings_2,'Amplitude Step',float))
        self.ui.dsb_Time_Linear_2.setValue(Lib.get_value(Lib.ps_settings_2,'Delay/Step',float))
        self.keep_auto_values(secondary=True)
        #Demagnetization Curves
        #Damped Sinusoidal
        self.ui.le_damp_sin_Ampl_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Damped Sinusoidal Amplitude',float)))
        self.ui.le_damp_sin_Offset_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Damped Sinusoidal Offset',float)))
        self.ui.le_damp_sin_Freq_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Damped Sinusoidal Frequency',float)))
        self.ui.le_damp_sin_nCycles_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Damped Sinusoidal N Cycles',int)))
        self.ui.le_damp_sin_phaseShift_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Damped Sinusoidal Phase Shift',float)))
        self.ui.le_damp_sin_finalPhase_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Damped Sinusoidal Final Phase',float)))
        self.ui.le_damp_sin_Damping_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Damped Sinusoidal Damping',float)))
        #Settings
        self.ui.le_maximum_current_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Maximum Current',float)))
        self.ui.le_minimum_current_2.setText(str(Lib.get_value(Lib.ps_settings_2,'Minimum Current',float)))
        
    def config_ps_2(self):
        """
        Write variables with interface values for new features
        """
        try:
            # Power Supply Tab
            Lib.write_value(Lib.ps_settings_2,'Power Supply Name',self.ui.le_PS_Name_2.text())
            Lib.write_value(Lib.ps_settings_2,'Power Supply Type', self.ui.cb_ps_type_2.currentIndex()+4,True)
            Lib.write_value(Lib.ps_settings_2,'Current Setpoint',self.ui.dsb_current_setpoint_2.value(),True)
            Lib.write_value(Lib.ps_settings_2,'Amplitude Step',self.ui.dsb_Amplitude_Linear_2.value(),True)
            Lib.write_value(Lib.ps_settings_2,'Delay/Step',self.ui.dsb_Time_Linear_2.value(),True)
            #Damped Sinusoidal
            Lib.write_value(Lib.ps_settings_2,'Damped Sinusoidal Amplitude',self.ui.le_damp_sin_Ampl_2.text(),True)
            Lib.write_value(Lib.ps_settings_2,'Damped Sinusoidal Offset',self.ui.le_damp_sin_Offset_2.text(),True)
            Lib.write_value(Lib.ps_settings_2,'Damped Sinusoidal Frequency',self.ui.le_damp_sin_Freq_2.text(),True)
            Lib.write_value(Lib.ps_settings_2,'Damped Sinusoidal N Cycles',self.ui.le_damp_sin_nCycles_2.text(),True)
            Lib.write_value(Lib.ps_settings_2,'Damped Sinusoidal Phase Shift',self.ui.le_damp_sin_phaseShift_2.text(),True)
            Lib.write_value(Lib.ps_settings_2,'Damped Sinusoidal Final Phase',self.ui.le_damp_sin_finalPhase_2.text(),True)
            Lib.write_value(Lib.ps_settings_2,'Damped Sinusoidal Damping',self.ui.le_damp_sin_Damping_2.text(),True)
            #Automatic setpoints
            #Lib.write_value(Lib.ps_settings,'Automatic Setpoints',self.ui.le_Auto_Set.text()) # Need revision
            #Settings
            Lib.write_value(Lib.ps_settings_2,'Maximum Current',self.ui.le_maximum_current_2.text(),True)
            Lib.write_value(Lib.ps_settings_2,'Minimum Current',self.ui.le_minimum_current_2.text(),True)
            return True
        except:
            QtWidgets.QMessageBox.warning(self,'Warning',"Couldn't configure the secondary power supply settings.\nCheck if all the inputs are correct.",QtWidgets.QMessageBox.Ok)
            return False

    def keep_auto_values(self, mode=0, secondary=False):
        if mode == 0:
            try:
                if not secondary:
                    _auto = Lib.get_value(Lib.ps_settings,'Automatic Setpoints')
                    _tw = self.ui.tw_auto_set
                else:
                    _auto = Lib.get_value(Lib.ps_settings_2,'Automatic Setpoints')
                    _tw = self.ui.tw_auto_set_2
                _dataset_list=''.join(_auto)
                _dataset_array = []
                for item in _dataset_list.split(','):
                    _dataset_array.append(item)
                _auto_values = np.asarray(_dataset_array, dtype='float')
            except:
                QtWidgets.QMessageBox.warning(self,'Fail','Impossible to get automatic values.',QtWidgets.QMessageBox.Ok)
                return
            try:           
                for i in range(len(_auto_values)):
                    _tw.insertRow(i)   
                    self.set_table_item(_tw, i, 0, _auto_values[i])
                QtWidgets.QApplication.processEvents()
            except:
                QtWidgets.QMessageBox.warning(self,'Fail','Impossible to set in table the automatic values for Current.',QtWidgets.QMessageBox.Ok)
                return
            QtWidgets.QApplication.processEvents()
        else:               # Return table values in array
            if not secondary:
                _tw = self.ui.tw_auto_set
            else:
                _tw = self.ui.tw_auto_set_2
            _ncells = _tw.rowCount()
            _auto_array = []
            for i in range(_ncells):
                _tw.setCurrentCell(i,0)
                if _tw.currentItem() != None:
                    _auto_array.append(float(_tw.currentItem().text()))
                else:
                    pass
            return _auto_array
        
    
    def add_rows(self, secondary=False):
        if not secondary:
            _rowPosition = self.ui.tw_auto_set.rowCount()
            self.ui.tw_auto_set.insertRow(_rowPosition)
        else:
            _rowPosition = self.ui.tw_auto_set_2.rowCount()
            self.ui.tw_auto_set_2.insertRow(_rowPosition)
        
    def clear_table(self, secondary=False):
        if not secondary:
            _tw = self.ui.tw_auto_set
        else:
            _tw = self.ui.tw_auto_set_2
        _tw.clearContents()
        _ncells = _tw.rowCount()
        while _ncells >= 0:
            _tw.removeRow(_ncells)
            _ncells = _ncells - 1
        QtWidgets.QApplication.processEvents()

    def DataCollect_reading(self):
        """
        Receives the data collected by the Integrator
        """
        pass
#         if self.ui.chb_dcct.isChecked():
#             self.Reading_current = reading_curr_multimeter()
#             self.Reading_multichannel = reading_curr_multichannel()
#             self.Reading_Secundary_Curr = reading_secundary_curr()
            
            
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

    def emergency(self):
        """Function stops motor, integrador and power supplies in case of emergency
        """
        Lib.flags.stop_all = True
        if Lib.ps_settings_2 == None:
            _secondary_flag = 0
        else:
            _secondary_flag = Lib.get_value(Lib.ps_settings_2, 'ps_status_2', int)            
        _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
        if _secondary_flag:
            _ps_type_2 = Lib.get_value(Lib.ps_settings_2, 'Power Supply Type', int)
            
        #stops motor
        self.stop_motor()
        #stops integrator
        Lib.comm.fdi.send(Lib.comm.fdi.PDIStop)
        
        #Turn off main power supply
        Lib.comm.drs.SetSlaveAdd(_ps_type)
        Lib.comm.drs.OpMode(0)
        Lib.comm.drs.SetISlowRef(0)
        time.sleep(0.1)
        Lib.comm.drs.TurnOff()
        if Lib.comm.drs.Read_ps_OnOff() == 0:
            Lib.write_value(Lib.aux_settings, 'status_ps', 0)
            Lib.write_value(Lib.aux_settings, 'actual_current', 0)
            self.ui.pb_PS_button.setChecked(False)
            self.ui.pb_PS_button.setText('Power Off')
            self.ui.lb_status_ps.setText('NOK')
            QtWidgets.QApplication.processEvents()
        time.sleep(.1)
        #Turn off secondary power supply
        if _secondary_flag:
            Lib.comm.drs.SetSlaveAdd(_ps_type_2)
            Lib.comm.drs.OpMode(0)
            Lib.comm.drs.SetISlowRef(0)
            time.sleep(0.1)
            Lib.comm.drs.TurnOff()
            if Lib.comm.drs.Read_ps_OnOff() == 0:
                Lib.write_value(Lib.aux_settings, 'status_ps_2', 0)
                Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                self.ui.pb_PS_button_2.setChecked(False)
                self.ui.pb_PS_button_2.setText('Power Off')
                QtWidgets.QApplication.processEvents()
#         print('Passei pelo warning')
        QtWidgets.QMessageBox.critical(self,'Warning','Emergency situation. \nMotor and Integrator are stopped, power supply(ies) turned off.',QtWidgets.QMessageBox.Ok)

    def monitor_thread(self):
        """Function to generate a thread which monitors power supply 
        currents and interlocks"""
        #check interlock if disable_ps_interlock not checked
        _disable_interlock = Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int)
        if Lib.ps_settings_2 == None:
            _secondary_flag = 0
        else:
            _secondary_flag = Lib.get_value(Lib.ps_settings_2, 'ps_status_2', int)
        _voltage_flag = self.ui.chb_voltage.isChecked()
        _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
        _velocity = Lib.get_value(Lib.data_settings,'rotation_motor_speed', float)
        if _secondary_flag:
            _ps_type_2 = Lib.get_value(Lib.ps_settings_2, 'Power Supply Type', int)
        _n_collections = Lib.get_value(Lib.measurement_df, 'n_collections', int)
        for i in range(_n_collections):
            _t = time.time()
            
            #monitor main coil current and interlocks
            Lib.comm.drs.SetSlaveAdd(_ps_type)
            if not _disable_interlock:
                _soft_interlock = Lib.comm.drs.Read_ps_SoftInterlocks()
    #             time.sleep(0.1)
                _hard_interlock = Lib.comm.drs.Read_ps_HardInterlocks()
    #             time.sleep(0.1)
            _current = round(float(Lib.comm.drs.Read_iLoad1()),3)
            _i = Lib.get_value(Lib.aux_settings, 'main_current_array')
            _i = _i.append([_current], ignore_index=True)
            Lib.write_value(Lib.aux_settings, 'main_current_array', _i)        
            
            #monitor secondary coil current  and interlocks if exists
            if _secondary_flag:
                Lib.comm.drs.SetSlaveAdd(_ps_type_2)
                if not _disable_interlock:
                    _soft_interlock_2 = Lib.comm.drs.Read_ps_SoftInterlocks()
    #                 time.sleep(0.1)
                    _hard_interlock_2 = Lib.comm.drs.Read_ps_HardInterlocks()
    #                 time.sleep(0.1)
                _current_2 = round(float(Lib.comm.drs.Read_iLoad1()),3)
                _i_2 = Lib.get_value(Lib.aux_settings, 'secondary_current_array')
                _i_2 = _i_2.append([_current_2], ignore_index=True)
                Lib.write_value(Lib.aux_settings, 'secondary_current_array', _i_2)
              
            #monitor main coil voltage / magnet resistance (dcct)
            if _voltage_flag: #voltage read from 34401A multimeter
                _voltage = Lib.comm.agilent34401a.collect().split(',')
                if len(_voltage) >= 1:
                    _voltage = float(_voltage[-1])
                else:
                    _voltage = 0.
                _v = Lib.get_value(Lib.aux_settings, 'main_voltage_array')
                _v = _v.append([_voltage], ignore_index=True)
                Lib.write_value(Lib.aux_settings, 'main_voltage_array', _v)
                #calc magnet resistence
                _i_avg = _i.mean[0]
                _i_std = _i.std[0]
                _v_avg = _v.mean[0]
                _v_std = _v.std[0]
                _r = _v_avg / _i_avg
                _r_std = (1/_i_avg) * np.sqrt(_v_std**2 + (_v_avg**2/_i_avg**2) * _i_std**2)
                Lib.write_value(Lib.aux_settings, 'magnet_resistance_avg', _r)
                Lib.write_value(Lib.aux_settings, 'magnet_resistance_std', _r_std)
            
            #in case of interlock or emergency, cuts off power supply, stop motors, abort integrator, send warning
            _interlock = _soft_interlock + _hard_interlock
            _interlock_flag = _interlock  
            if _secondary_flag:
                _interlock_2 = _soft_interlock_2 + _hard_interlock_2
                _interlock_flag = _interlock_flag + _interlock_2
            if _interlock_flag or Lib.flags.stop_all:
                if _interlock:
                    self.ui.pb_interlock.setChecked(True)
                if _secondary_flag:
                    if _interlock_2:
                        self.ui.pb_interlock_2.setChecked(True)
                QtWidgets.QApplication.processEvents()
                self.ui.pb_emergency1.click()
                Lib.flags.stop_all = True
                return
            _t = (1/_velocity - 0.01) - (time.time()-_t)
            if _t > 0: 
                time.sleep(_t)
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
        
