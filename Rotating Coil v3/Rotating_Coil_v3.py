#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import threading
import traceback
import numpy as np
import pandas as pd
import pyqtgraph as pg
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore

import FDI2056
import SerialDRS
import Agilent_34970A
import Parker_Drivers
import Display_Heidenhain
from Pop_up import Ui_Pop_Up
import Rotating_Coil_Library as Library
from Rotating_Coil_Interface_v3 import Ui_RotatingCoil_Interface

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_RotatingCoil_Interface()
        self.ui.setupUi(self)

        self.timer = QtCore.QTimer()
        self.signals()

        self.refresh_interface()

        self.ui.gb_start_supply.setEnabled(False)
        self.ui.gb_start_supply.setEnabled(False)

        self.sync = threading.Event()
        

    def signals(self):
        for i in range(1,self.ui.tabWidget.count()):
            self.ui.tabWidget.setTabEnabled(i,False)    #Lock main Tabs
        
        #tabWidget
        self.ui.tabWidget.currentChanged.connect(self.tabWidget)
        self.timer.timeout.connect(self.agilent_monitor)
        
        # Connection Tab
        self.ui.pb_connect_devices.clicked.connect(self.connect_devices)
        
        # Settings Tab
        self.ui.pb_save_config.clicked.connect(self.save_config)
        self.ui.pb_config.clicked.connect(self.config)
        self.ui.pb_emergency1.clicked.connect(lambda: self.stop(True)) 
        
        # Motors and Integrator Tab
        self.ui.pb_move_motor.clicked.connect(self.move_motor_manual)
        self.ui.pb_stop_motor.clicked.connect(self.stop_motor)
        self.ui.pb_encoder_reading.clicked.connect(self.encoder_reading)
        self.ui.pb_move_to_encoder_position.clicked.connect(self.move_to_encoder_position)
        self.ui.pb_set_gain.clicked.connect(self.set_gain)
        self.ui.pb_status_update.clicked.connect(self.status_update)
        self.ui.pb_get_coil_index_2.clicked.connect(self.get_coil_index)
        self.ui.pb_emergency2.clicked.connect(lambda: self.stop(True))
        
        # Coil Tab
        self.ui.pb_get_coil_index.clicked.connect(self.get_coil_index)
        self.ui.pb_config_coil.clicked.connect(self.configure_coil)
        self.ui.pb_load_coil.clicked.connect(self.load_coil)
        self.ui.pb_save_coil.clicked.connect(self.save_coil)
        self.ui.pb_emergency3.clicked.connect(lambda: self.stop(True))
        
        # Power Supply tab
        self.ui.pb_PS_button.clicked.connect(lambda: self.start_powersupply(False))
        self.ui.pb_refresh.clicked.connect(self.display_current)
        self.ui.pb_load_PS.clicked.connect(lambda: self.load_PowerSupply(False))
        self.ui.pb_save_PS.clicked.connect(lambda: self.save_PowerSupply(False))
        self.ui.pb_send.clicked.connect(lambda: self.send_setpoint(False))
        self.ui.pb_rows_auto.clicked.connect(lambda: self.add_rows(False))
        self.ui.pb_send_curve.clicked.connect(lambda: self.send_curve(False))
        self.ui.pb_config_pid.clicked.connect(self.config_pid)
        self.ui.pb_reset_inter.clicked.connect(lambda: self.reset_interlocks(False))
        self.ui.pb_cycle.clicked.connect(lambda: self.cycling_ps(False))
        self.ui.pb_config_ps.clicked.connect(lambda: self.configure_ps(False))
        self.ui.pb_clear_table.clicked.connect(lambda: self.clear_table(False))
        #Secondary Power Supply
        self.ui.pb_PS_button_2.clicked.connect(lambda: self.start_powersupply(True))
        self.ui.pb_load_PS_2.clicked.connect(lambda: self.load_PowerSupply(True))
        self.ui.pb_save_PS_2.clicked.connect(lambda: self.save_PowerSupply(True))
        self.ui.pb_send_2.clicked.connect(lambda: self.send_setpoint(True))
        self.ui.pb_rows_auto_2.clicked.connect(lambda: self.add_rows(True))
        self.ui.pb_send_curve_2.clicked.connect(lambda: self.send_curve(True))
        self.ui.pb_reset_inter_2.clicked.connect(lambda: self.reset_interlocks(True))
        self.ui.pb_cycle_2.clicked.connect(lambda: self.cycling_ps(True))
        self.ui.pb_clear_table_2.clicked.connect(lambda: self.clear_table(True))
        self.ui.pb_config_ps_2.clicked.connect(lambda: self.configure_ps(True))
        self.ui.pb_emergency4.clicked.connect(lambda: self.stop(True))
        
        # Measurements Tab
        self.ui.pb_start_meas.clicked.connect(self.popup_meas)
        self.ui.pb_stop.clicked.connect(lambda: self.stop(False))
        self.ui.pb_emergency5.clicked.connect(lambda: self.stop(True))
        
        # Results Tab
        self.ui.pb_save_data_results.clicked.connect(self.save_data_results)
        self.ui.pb_emergency6.clicked.connect(lambda: self.stop(True))
        
    def agilent_monitor(self):
        if Lib.get_value(Lib.data_settings, 'enable_Agilent34970A', int) and Lib.flags.devices_connected:
            _ans = Lib.comm.agilent34970a.read_temp_volt()
            self.ui.lcdNumber.display(_ans[0])
            self.ui.lcdNumber_4.display(_ans[1])
            self.ui.lcdNumber_5.display(_ans[2])
            QtWidgets.QApplication.processEvents()
        
    def tabWidget(self):
        if self.ui.tabWidget.currentIndex() == 5:
            self.timer.start(2000)
        else:
            self.timer.stop()
        
    def connect_devices(self):
        """
        connect devices and check status
        """
        self.ui.pb_connect_devices.setText('Processing...')
        if not Lib.flags.devices_connected:
            try:
                self.config_variables() 
                # connect digital power supply
                Lib.comm.drs = SerialDRS.SerialDRS_FBP()
                Lib.comm.drs.Connect(Lib.get_value(Lib.data_settings,'ps_port',str))
                if not Lib.comm.drs.ser.is_open:
                    QtWidgets.QMessageBox.warning(self,'Warning','Failed to connect to Power Supply.',QtWidgets.QMessageBox.Ok)
                    raise
                 
                #Turns off any power supply which might be enabled
                for i in range(1,7):
                    Lib.comm.drs.SetSlaveAdd(i)
                    try:
                        if Lib.comm.drs.Read_ps_OnOff() == 1:
                            Lib.comm.drs.TurnOff()
                    except:
                        continue
                    QtWidgets.QApplication.processEvents()

                # connect integrator
                Lib.comm.fdi = FDI2056.SerialCom(Lib.get_value(Lib.data_settings,'integrator_port',str))
                Lib.comm.fdi.connect()
                if len(Lib.comm.fdi.status('1')) < 8:
                    Lib.comm.drs.Disconnect()
                    Lib.comm.fdi.disconnect()
                    QtWidgets.QMessageBox.warning(self,'Warning','Failed to connect to the integrator.',QtWidgets.QMessageBox.Ok)
                    raise
                    
                # connect display
                Lib.comm.display = Display_Heidenhain.SerialCom(Lib.get_value(Lib.data_settings,'disp_port',str),'ND-780')
                Lib.comm.display.connect()

                # connect driver 
                Lib.comm.parker = Parker_Drivers.SerialCom(Lib.get_value(Lib.data_settings,'driver_port',str))
                Lib.comm.parker.connect()

                Lib.write_value(Lib.data_settings, 'agilent34970A_address', self.ui.sb_agilent34970A_address.value(),True)

                # connect agilent 34970a - multichannel
                if self.ui.chb_enable_Agilent34970A.isChecked() != 0:
                    Lib.comm.agilent34970a = Agilent_34970A.GPIB()
                    Lib.comm.agilent34970a.connect(Lib.get_value(Lib.data_settings,'agilent34970A_address',int))
                    Lib.comm.agilent34970a.config_temp_volt()
                    time.sleep(0.1)
                    Lib.comm.agilent34970a.read_val() #this line prevents crash on monitor tab
                    self.ui.lb_status_34970A.setText('Connected')
                                          
                QtWidgets.QMessageBox.information(self,'Information','Devices connected.',QtWidgets.QMessageBox.Ok)
                self.ui.pb_connect_devices.setText('Disconnect Devices')
                Lib.flags.devices_connected = True
                for i in range(1,7):
                    self.ui.tabWidget.setTabEnabled(i,True)            # Unlock main Tabs
            except:
                self.ui.pb_connect_devices.setText('Connect Devices')
                QtWidgets.QMessageBox.warning(self,'Warning','Failed to connect devices',QtWidgets.QMessageBox.Ok)
             
        else:
            try:
                # connect display
                Lib.comm.display.disconnect()
        
                # connect driver 
                Lib.comm.parker.disconnect()
        
                # connect integrator
                Lib.comm.fdi.disconnect()  

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
                self.ui.pb_connect_devices.setText('Disconnect Devices')
                QtWidgets.QMessageBox.warning(self,'Warning','Failed disconnecting devices',QtWidgets.QMessageBox.Ok)
                        
    def save_config(self):
        """
        save settings in external file
        """
        if self.config_variables():
            if Lib.save_settings():
                QtWidgets.QMessageBox.information(self,'Information','File saved successfully.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Warning','Failed to save settings',QtWidgets.QMessageBox.Ok)
                return
            
    def config(self):
        """
        config interface data into variables
        """
        if self.ui.chb_disable_alignment_interlock.isChecked():
            _ans = QtWidgets.QMessageBox.question(self,'Attention','Do you want to DISABLE alignment interlock?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
            if _ans == QtWidgets.QMessageBox.No:
                self.ui.chb_disable_alignment_interlock.setChecked(False)
                return
        if self.ui.chb_disable_ps_interlock.isChecked():
            _ans = QtWidgets.QMessageBox.question(self,'Attention','Do you want to DISABLE power supply interlock?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
            if _ans == QtWidgets.QMessageBox.No:
                self.ui.chb_disable_alignment_interlock.setChecked(False)
                return
        if not self.config_variables():
            QtWidgets.QMessageBox.warning(self,'Warning','Failed to configure settings;\nCheck if all the settings values are numbers.',QtWidgets.QMessageBox.Ok)
        QtWidgets.QMessageBox.information(self,'Information','Configuration completed successfully.',QtWidgets.QMessageBox.Ok)

    def start_powersupply(self, secondary=False):
        try:
            if not secondary:
                self.ui.pb_PS_button.setEnabled(False)
                self.ui.pb_PS_button.setText('Processing...')
                _df = Lib.ps_settings
                _status_ps = Lib.get_value(Lib.aux_settings, 'status_ps', int)
            else:
                self.ui.pb_PS_button_2.setEnabled(False)
                self.ui.pb_PS_button_2.setText('Processing...')
                _df = Lib.ps_settings_2
                _status_ps = Lib.get_value(Lib.aux_settings, 'status_ps_2', int)
            self.ui.tabWidget_2.setEnabled(False)
            QtWidgets.QApplication.processEvents()

            _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
            Lib.comm.drs.SetSlaveAdd(_ps_type)

            _safety_enabled = 1
            if Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int) and ((secondary == False and _status_ps == 0) or (secondary == True and _status_ps == 0)):
                _ret = QtWidgets.QMessageBox.question(self,'Attention','Do you want to turn on the Power Supply with Safety Control DISABLED?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
                if _ret == QtWidgets.QMessageBox.Yes:
                    _safety_enabled = 0
                else:
                    self.change_ps_button(secondary, True)
                    return

            if (secondary == False and _status_ps == 0) or (secondary == True and _status_ps == 0):         # Status PS is OFF                
                try:
                    Lib.comm.drs.Read_iLoad1()
                except:
                    traceback.print_exc(file=sys.stdout)
                    QtWidgets.QMessageBox.warning(self,'Warning','Could not read the digital current.',QtWidgets.QMessageBox.Ok)
                    self.change_ps_button(secondary, True)
                    return
                
                if _safety_enabled == 1:
                    _status_interlocks = Lib.comm.drs.Read_ps_SoftInterlocks()
                    if _status_interlocks != 0:
                        self.ui.pb_interlock.setChecked(True)
                        QtWidgets.QMessageBox.warning(self,'Warning','Soft Interlock activated!',QtWidgets.QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return
                    _status_interlocks = Lib.comm.drs.Read_ps_HardInterlocks()
                    if _status_interlocks != 0:
                        self.ui.pb_interlock.setChecked(True)  
                        QtWidgets.QMessageBox.warning(self,'Warning','Hard Interlock activated!',QtWidgets.QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return

                if _ps_type == 2:                               # PS 1000 A needs to turn dc link on
                    Lib.comm.drs.SetSlaveAdd(_ps_type-1)
                    # Turn ON PS DClink
                    try:
                        Lib.comm.drs.TurnOn()           # Turn ON the DC Link of the PS
                        time.sleep(0.1)
                        if Lib.comm.drs.Read_ps_OnOff() != 1:
                            QtWidgets.QMessageBox.warning(self,'Warning',"Power Supply Capacitor Bank did not initialize.",QtWidgets.QMessageBox.Ok)
                            self.change_ps_button(secondary, True)
                            return
                    except:
                        QtWidgets.QMessageBox.warning(self,'Warning',"Power Supply Capacitor Bank did not initialize.",QtWidgets.QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return
                    # Closing DC link Loop
                    try:
                        Lib.comm.drs.ClosedLoop()        # Closed Loop
                        time.sleep(0.1)
                        if Lib.comm.drs.Read_ps_OpenLoop() == 1:
                            QtWidgets.QMessageBox.warning(self,'Warning',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                            self.change_ps_button(secondary, True)
                            return
                    except:
                        QtWidgets.QMessageBox.warning(self,'Warning',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return
                    # Set ISlowRef for DC Link (Capacitor Bank)
                    _mode = 0
                    Lib.comm.drs.OpMode(_mode)                     # Operation mode selection for Slowref
                    _dclink_value = Lib.get_value(Lib.aux_settings, 'dclink_value', float) #30 V
                    Lib.comm.drs.SetISlowRef(_dclink_value)        # Set 30 V for Capacitor Bank (default value according to the ELP Group)
                    time.sleep(1)
                    _feedback_DCLink = round(Lib.comm.drs.Read_vOutMod1()/2 +\
                                            Lib.comm.drs.Read_vOutMod2()/2,3)                        
                    #Waiting few seconds until voltage stabilization before starting PS Current
                    _i = 100
                    while _feedback_DCLink < _dclink_value and _i > 0:
                        _feedback_DCLink = round(Lib.comm.drs.Read_vOutMod1()/2 +\
                                                Lib.comm.drs.Read_vOutMod2()/2,3)
                        QtWidgets.QApplication.processEvents()
                        time.sleep(0.5)
                        _i = _i-1                            
                    if _i == 0:
                        QtWidgets.QMessageBox.warning(self,'Warning',"DC link setpoint is not set.\nCheck configurations.",QtWidgets.QMessageBox.Ok)
                        Lib.comm.drs.TurnOff()
                        self.change_ps_button(secondary, True)
                        return
                #Turn on Power Supply
                Lib.comm.drs.SetSlaveAdd(_ps_type)  # Set power supply address
                if _ps_type < 4:
                    self.pid_setting()
                Lib.comm.drs.TurnOn()           
                time.sleep(0.1)
                if not Lib.comm.drs.Read_ps_OnOff():
                    Lib.comm.drs.SetSlaveAdd(_ps_type-1)
                    Lib.comm.drs.TurnOff()  #TurnOff PS DC Link
                    self.change_ps_button(secondary, True)
                    QtWidgets.QMessageBox.warning(self,'Warning','The Power Supply did not start.',QtWidgets.QMessageBox.Ok)
                    return
                # Closed Loop
                Lib.comm.drs.ClosedLoop()       
                time.sleep(0.1)
                if Lib.comm.drs.Read_ps_OpenLoop() == 1:
                    Lib.comm.drs.SetSlaveAdd(_ps_type-1)
                    Lib.comm.drs.TurnOff()  #TurnOff PS DC Link
                    self.change_ps_button(secondary, True)
                    QtWidgets.QMessageBox.warning(self,'Warning',"Power Supply circuit loop is not closed.",QtWidgets.QMessageBox.Ok)
                    return
                self.change_ps_button(secondary, False)
                if not secondary:
                    Lib.write_value(Lib.aux_settings, 'status_ps', 1)      # Status PS is ON
                    Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                    self.ui.le_status_loop.setText('Closed')
                    self.ui.lb_status_ps.setText('OK')
                    self.ui.tabWidget_2.setEnabled(True)
                    self.ui.tabWidget_3.setEnabled(True)
                    self.ui.pb_refresh.setEnabled(True)
                    self.ui.pb_send.setEnabled(True)
                    self.ui.pb_send_curve.setEnabled(True)
                else:
                    Lib.write_value(Lib.aux_settings, 'status_ps_2', 1)      # Status PS is ON
                    Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                    self.ui.le_status_loop_2.setText('Closed')
                    self.ui.pb_send_2.setEnabled(True)
                    self.ui.pb_send_curve_2.setEnabled(True)
                QtWidgets.QMessageBox.information(self,'Information','The Power Supply started successfully.',QtWidgets.QMessageBox.Ok)
            else: #Turn off power supply
                Lib.comm.drs.SetSlaveAdd(_ps_type)
                Lib.comm.drs.TurnOff()
                time.sleep(0.1)
                _status = Lib.comm.drs.Read_ps_OnOff()
                if _status:
                    QtWidgets.QMessageBox.warning(self,'Warning','Could not turn the power supply off. \nPlease, try again.',QtWidgets.QMessageBox.Ok)
                    self.change_ps_button(secondary, False)
                    return
                if _ps_type == 2: # Turn of dc link
                    Lib.comm.drs.SetSlaveAdd(_ps_type-1)
                    Lib.comm.drs.TurnOff()
                    time.sleep(0.1)
                    _status = Lib.comm.drs.Read_ps_OnOff()
                    if _status:
                        QtWidgets.QMessageBox.warning(self,'Warning',"Could not turn the power supply off. \nPlease, try again.",QtWidgets.QMessageBox.Ok)
                        self.change_ps_button(secondary, False)
                        return
                if not secondary:
                    Lib.write_value(Lib.aux_settings, 'status_ps', 0)      # Status PS is OFF
                    Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                    self.ui.lb_status_ps.setText('NOK')
                    self.ui.le_status_loop.setText('Open')
                    self.ui.pb_send.setEnabled(False)
                    self.ui.pb_cycle.setEnabled(False)
                    self.ui.pb_send_curve.setEnabled(False)
                else:
                    Lib.write_value(Lib.aux_settings, 'status_ps_2', 0)      # Status PS_2 is OFF
                    Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                    self.ui.le_status_loop_2.setText('Open')
                    self.ui.pb_send_2.setEnabled(False)
                    self.ui.pb_cycle_2.setEnabled(False)
                    self.ui.pb_send_curve_2.setEnabled(False)
                self.change_ps_button(secondary, True)
                QtWidgets.QMessageBox.information(self,'Information',"Power supply was turned off.",QtWidgets.QMessageBox.Ok)
        except:
            traceback.print_exc(file=sys.stdout)
            QtWidgets.QMessageBox.warning(self,'Warning','Failed to change the power supply state.',QtWidgets.QMessageBox.Ok)
            self.change_ps_button(secondary, False)
            return
        
    def change_ps_button(self, secondary=False, on=True):
        if not secondary:
            self.ui.pb_PS_button.setEnabled(True)
            if on:
                self.ui.pb_PS_button.setChecked(False)
                self.ui.pb_PS_button.setText('Turn ON')
            else:
                self.ui.pb_PS_button.setChecked(True)
                self.ui.pb_PS_button.setText('Turn OFF')
        else:
            self.ui.pb_PS_button_2.setEnabled(True)
            if on:
                self.ui.pb_PS_button_2.setChecked(False)
                self.ui.pb_PS_button_2.setText('Turn ON')
            else:
                self.ui.pb_PS_button_2.setChecked(True)
                self.ui.pb_PS_button_2.setText('Turn OFF')
        self.ui.tabWidget_2.setEnabled(True)
        QtWidgets.QApplication.processEvents()
        
    def config_pid(self):
        _ans = QtWidgets.QMessageBox.question(self, 'PID settings', 'Be aware that this will overwrite the current configurations.\nAre you sure you want to configure the PID parameters? ', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if _ans == QtWidgets.QMessageBox.Yes:
            _ans = self.pid_setting()
            if _ans:
                QtWidgets.QMessageBox.information(self,'Information','PID configured.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Fail','Power Supply PID configuration fault.',QtWidgets.QMessageBox.Ok)             
                
    def pid_setting(self):
        '''
        Set by software the PID configurations  
        '''
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
            traceback.print_exc(file=sys.stdout)
            return False
        try:
            _list_coeffs = np.zeros(16)
            _kp = Lib.get_value(Lib.ps_settings, 'Kp', float)
            _ki = Lib.get_value(Lib.ps_settings, 'Ki', float)
            _list_coeffs[0] = _kp
            _list_coeffs[1] = _ki
            Lib.comm.drs.Write_dp_Coeffs(_list_coeffs.tolist())       #Write kp and ki
            Lib.comm.drs.ConfigDPModule()                             #Configure kp and ki
        except:
            traceback.print_exc(file=sys.stdout)
            return False
        
        return True

    def display_current(self):
        _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
        Lib.comm.drs.SetSlaveAdd(_ps_type)
        try:
            _refresh_current = round(float(Lib.comm.drs.Read_iLoad1()),3)
            self.ui.lcd_PS_reading.display(_refresh_current)
            if self.ui.chb_dcct.isChecked() and self.ui.chb_enable_Agilent34970A.isChecked():
                self.ui.lcd_current_dcct.setEnabled(True)
                self.ui.label_161.setEnabled(True)
                self.ui.label_164.setEnabled(True)
                _current = round(self.dcct_convert(), 3)
                self.ui.lcd_current_dcct.display(_current)
                QtWidgets.QApplication.processEvents()
        except:
            QtWidgets.QMessageBox.warning(self,'Warning','Could not display Current.',QtWidgets.QMessageBox.Ok)
            return
    
    def current_setpoint(self, setpoint=0, secondary=False):
        self.ui.tabWidget_2.setEnabled(False)
        if not secondary:
            _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
            _df = Lib.ps_settings
        else:
            _ps_type = Lib.get_value(Lib.ps_settings_2, 'Power Supply Type', int)
            _df = Lib.ps_settings_2

        Lib.comm.drs.SetSlaveAdd(_ps_type)

        #verify current limits
        _setpoint = self.verify_current_limits(0, setpoint, secondary)
        if _setpoint == 'False':
            self.ui.tabWidget_2.setEnabled(True)
            return False
        Lib.write_value(_df,'Current Setpoint',_setpoint,True)

        #send setpoint and wait until current is set
        Lib.comm.drs.SetISlowRef(_setpoint)
        time.sleep(0.1)
        for i in range(30):
            _compare = round(float(Lib.comm.drs.Read_iLoad1()),3)
            if not secondary:
                self.display_current()
            if abs(_compare - _setpoint) <= 0.5:
                self.ui.tabWidget_2.setEnabled(True)
                return True
            QtWidgets.QApplication.processEvents()
            time.sleep(1)
        self.ui.tabWidget_2.setEnabled(True)
        return False
    
    def send_setpoint(self, secondary=False):
        if not secondary:
            _df = Lib.ps_settings
            self.config_ps()
        else:
            _df = Lib.ps_settings_2
            self.config_ps_2()
            
        _setpoint = Lib.get_value(_df,'Current Setpoint',float)
        _ans = self.current_setpoint(_setpoint, secondary)
        if _ans:
            QtWidgets.QMessageBox.information(self, 'Information', 'Current properly set.',QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Current was not properly set.\n',QtWidgets.QMessageBox.Ok)

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
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Incorrect value for maximum Supply Current.\nPlease, verify the value.',QtWidgets.QMessageBox.Ok)
            return 'False'
        try:
            _current_min = Lib.get_value(_df, 'Minimum Current', float)
        except:
            QtWidgets.QMessageBox.warning(self,'Warning','Incorrect value for minimum Supply Current.\nPlease, verify the value.',QtWidgets.QMessageBox.Ok)
            return 'False'
        
        if index == 0 or index == 1:
            if _current > _current_max:
                if (index == 0):
                    QtWidgets.QMessageBox.warning(self,'Warning','Value of current higher than the Supply Limit.',QtWidgets.QMessageBox.Ok)
                self.ui.dsb_current_setpoint.setValue(float(_current_max))
                _current = _current_max
   
            if _current < _current_min:
                if index == 0:
                    QtWidgets.QMessageBox.warning(self,'Warning','Current value lower than the Supply Limit.',QtWidgets.QMessageBox.Ok)
                self.ui.dsb_current_setpoint.setValue(float(_current_min))
                _current = _current_min
        elif index == 2:
            if ((_current)+offset) > _current_max:
                QtWidgets.QMessageBox.warning(self,'Warning','Check Peak to Peak Current and Offset values.\nValues out of source limit.',QtWidgets.QMessageBox.Ok)
                return 'False'
            
            if ((-_current)+offset) < _current_min:
                QtWidgets.QMessageBox.warning(self,'Warning','Check Peak to Peak Current and Offset values.\nValues out of source limit.',QtWidgets.QMessageBox.Ok)
                return 'False'
            
        return float(_current) 

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
            QtWidgets.QMessageBox.warning(self,'Warning','Fail to send curve.',QtWidgets.QMessageBox.Ok)
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
                
                
        #Generating curves
        try:
            try:
                _mode=3          #Operating mode
                Lib.comm.drs.OpMode(_mode)
                if Lib.comm.drs.Read_ps_OpMode()!=3:
                    QtWidgets.QMessageBox.warning(self,'Warning','Signal generator not configured correctly.',QtWidgets.QMessageBox.Ok)
                    return False
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Signal generator not configured correctly. Verify PS settings.',QtWidgets.QMessageBox.Ok)
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
                    QtWidgets.QMessageBox.warning(self,'Warning','Failed to send configuration to the controller.\nPlease, verify the parameters of the Power Supply.',QtWidgets.QMessageBox.Ok)
                    return
                
            if _curve_type == 1:        # Damped Sinusoidal                
                try:
                    _sigType=4
                    Lib.comm.drs.Write_sigGen_Freq(float(_freq))             
                    Lib.comm.drs.Write_sigGen_Amplitude(float(_amp))         
                    Lib.comm.drs.Write_sigGen_Offset(float(_offset))    
                except:
                    QtWidgets.QMessageBox.warning(self,'Warning','Failed to send configuration to the controller.\nPlease, verify the parameters of the Power Supply.',QtWidgets.QMessageBox.Ok)
                    return
    
                #Sending sigGenDamped
                try:
                    Lib.comm.drs.Write_sigGen_Aux(float(self.ui.le_damp_sin_Damping.text()))
                    Lib.comm.drs.ConfigSigGen(_sigType, _n_cycles, _phase_shift, _final_phase)
                except:
                    QtWidgets.QMessageBox.warning(self,'Warning.','Damped Sinusoidal fault.',QtWidgets.QMessageBox.Ok)
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
        
        if _ps_type == 2: # 1000A power supply, reset capacitor bank interlock
            Lib.comm.drs.SetSlaveAdd(_ps_type-1)
            Lib.comm.drs.ResetInterlocks()
            
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
            QtWidgets.QMessageBox.warning(self,'Warning','Interlocks not reseted.',QtWidgets.QMessageBox.Ok)
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
                _freq = Lib.get_value(_df,'Damped Sinusoidal Frequency', float)
                _n_cycles = Lib.get_value(_df,'Damped Sinusoidal N Cycles', float) 
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
            
            QtWidgets.QMessageBox.information(self,'Information','Cycle process completed successfully.',QtWidgets.QMessageBox.Ok)
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
            _mode = 0
            Lib.comm.drs.OpMode(_mode)  #returns to mode ISlowRef
        except:
            QtWidgets.QMessageBox.warning(self,'Warning','Cycling process not realized.',QtWidgets.QMessageBox.Ok)
            return       
    
    def move_motor_until_stops(self, address): # Ok
        """
        """
        Lib.flags.stop_all = False
        
        Lib.comm.parker.movemotor(address)

        while ( (Lib.comm.parker.ready(address) == False) and (Lib.flags.stop_all == False) ):
            Lib.comm.parker.flushTxRx()
            QtWidgets.QApplication.processEvents()

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

    def set_gain(self): # Ok
        """
        """
        Lib.flags.stop_all = False
        self.ui.pb_set_gain.setText('Processing...')
        self.ui.pb_set_gain.setEnabled(False)

        self.config_variables()

        _gain = Lib.get_value(Lib.data_settings, 'integrator_gain', str)
        Lib.comm.fdi.send(Lib.comm.fdi.PDIGain + _gain)
        time.sleep(0.2)

        Lib.comm.fdi.send(Lib.comm.fdi.PDIShortCircuitOn)
        time.sleep(0.2)

        Lib.comm.fdi.send(Lib.comm.fdi.PDIOffsetOn)

        while (int(Lib.comm.fdi.status('1')[-4]) != 1) and (Lib.flags.stop_all == False):
            QtWidgets.QApplication.processEvents()
            time.sleep(0.1)

        Lib.comm.fdi.send(Lib.comm.fdi.PDIOffsetOff)
        time.sleep(0.2)        
        Lib.comm.fdi.send(Lib.comm.fdi.PDIShortCircuitOff)
        
        # Setup integrator for first measurement
        self.configure_integrator(adj_offset=True)
        Lib.comm.fdi.start_measurement()
        self.move_motor_measurement(2)
        time.sleep(0.5)
        Lib.comm.fdi.get_data()
        

        self.ui.lb_status_integrator.setText('OK')
        self.ui.pb_set_gain.setText('Set Gain')
        self.ui.pb_set_gain.setEnabled(True)

        QtWidgets.QMessageBox.information(self,'Information','Gain set and offset adjusted.',QtWidgets.QMessageBox.Ok)

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
        
    def get_coil_index(self): # Ok
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
            filename = QtWidgets.QFileDialog.getOpenFileName(self,'Load Coil File' , Lib.dir_path + '\Config\Coils\\', 'Data files (*.dat);;Text files (*.txt)')
            if Lib.load_coil(filename[0]) == True:
                if self.refresh_coiltab():
                    QtWidgets.QMessageBox.information(self,'Information','Coil File loaded.',QtWidgets.QMessageBox.Ok)
                    #If OKAY
                    self.ui.lb_status_coil.setText('OK')                
            else:
                QtWidgets.QMessageBox.warning(self,'Warning','Failed to load Coil File.',QtWidgets.QMessageBox.Ok)
                self.ui.lb_status_coil.setText('NOK')
                 
        except:
            return
    
    def save_coil(self): # Ok
        """
        """
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self,'Save Coil File' , Lib.dir_path + '\Config\Coils\\', 'Data files (*.dat);;Text files (*.txt)')
            
            self.config_coil()

            if Lib.save_coil(filename[0]) == True:
                QtWidgets.QMessageBox.information(self,'Information','Coil File saved.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Warning','Failed to save Coil File.',QtWidgets.QMessageBox.Ok) 
        except:
            return
        
    def save_PowerSupply(self, secondary=False):
        """
        save settings of the Power Supply in external file
        """
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Power Supply File', Lib.dir_path + '\Config\Power Supplies\\', 'Data files (*.dat);;Text files (*.txt)')
            
            if not secondary:
                self.config_ps()
                _ans = Lib.save_ps(filename[0])
            else:
                self.config_ps_2()
                _ans = Lib.save_ps(filename[0], secondary=True)
            if _ans:
                QtWidgets.QMessageBox.information(self,'Information','Power Supply File saved.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Warning','Failed to save Power Supply File.',QtWidgets.QMessageBox.Ok) 
        except:
            return
        
    def load_PowerSupply(self, secondary=False):
        """
        load settings of the Power Supply in the interface
        """
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,'Load Power Supply File' , Lib.dir_path + '\Config\Power Supplies\\', 'Data files (*.dat);;Text files (*.txt)')
            if not secondary:
                _ans = Lib.load_ps(filename[0])
            else:
                _ans = Lib.load_ps(filename[0], secondary=True)
            if _ans == True:
                if not secondary:
                    self.refresh_ps_settings()
                    self.ui.gb_start_supply.setEnabled(True)
                else:
                    self.refresh_ps_settings_2()
                    self.ui.gb_start_supply_2.setEnabled(True)
                QtWidgets.QMessageBox.information(self,'Information','Power Supply File loaded.',QtWidgets.QMessageBox.Ok)
                self.ui.tabWidget_2.setEnabled(True)
                self.ui.tabWidget_3.setEnabled(True)
                self.ui.pb_refresh.setEnabled(True)
            else:
                QtWidgets.QMessageBox.warning(self,'Warning','Failed to load Power Supply File.',QtWidgets.QMessageBox.Ok) 
        except:
            traceback.print_exc(file=sys.stdout)
            QtWidgets.QMessageBox.warning(self,'Warning',"Could not load the power supply settings.\nCheck if the configuration file values are correct.",QtWidgets.QMessageBox.Ok)

    def start_meas(self):
        """ 
        """
        try:
            Lib.flags.stop_all = False
            Lib.flags.emergency = False
            self.ui.pb_start_meas.setEnabled(False)
            self.ui.le_n_collections.setEnabled(False)
            self.ui.tabWidget.setTabEnabled(5, False)
            self.ui.tabWidget_2.setEnabled(False)
            self.ui.chb_automatic_ps.setEnabled(False)
            QtWidgets.QApplication.processEvents()
            _save_flag = False

            if not Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int):
                _ans = self.config_ps()
                if not _ans:
                    raise

            self.ui.lb_meas_counter.setText('{0:04}'.format(0))
            QtWidgets.QApplication.processEvents()
            
            if self.ui.chb_seriesofmeas.isChecked():
                _n_collections = Lib.get_value(Lib.measurement_settings, 'n_collections', int)
            else:
                _n_collections = 1
            
            if self.ui.chb_automatic_ps.isChecked():
                if Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int):
                    _ans = QtWidgets.QMessageBox.question(self,'Automatic Power Supply','The power supply interlock is disabled.\nDo you want to continue this measurement with no guarantee that the power supply is working properly?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                    if _ans == QtWidgets.QMessageBox.No:
                        raise
                #load array
                if self.ui.rb_main_ps.isChecked():
                    _current_array = Lib.get_value(Lib.ps_settings, 'Automatic Setpoints')
                    _secondary = False
                else:
                    _current_array = Lib.get_value(Lib.ps_settings_2, 'Automatic Setpoints')
                    _secondary = True
                _current_array = np.asarray(_current_array.split(','), dtype=float)
                #set n_collections
                _n_collections = _current_array.shape[0]
                
            if _n_collections > 1: #Asks whether to save each measurement to file or not
                _ans = QtWidgets.QMessageBox.question(self,'Save logs','Do you want to save each measurement log to file?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if _ans == QtWidgets.QMessageBox.Yes:
                    _dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save Directory', Lib.dir_path).replace('/', '\\\\') + '\\\\'
                    _save_flag = True

            # data array
            self.data_array = np.array([])
            self.df_rawcurves = None   
            
            # configure integrator
            self.configure_integrator()
            
            # check system components
            self.collect_infocomponents()

            #Begin loop for n_collections
            for i in range(_n_collections):
                #change current if automatic adjust is enabled
                if self.ui.chb_automatic_ps.isChecked():
                    _ans = self.current_setpoint(_current_array[i], _secondary)
                    if not _ans:
                        Lib.db_save_failure(6)
                        QtWidgets.QMessageBox.warning(self, 'Warning', 'Current was not properly set.\n',QtWidgets.QMessageBox.Ok)
                        raise

                # measure and read data
                self.measure_and_read()

                # fft calculation
                self.fft_calculation()

                # multipoles calculation
                self.multipoles_calculation()

                # normalize multipoles 
                self.multipoles_normalization()             
                
                # displacement calculation
                self.displacement_calculation()   

                # plot results
                self.plot_raw_graph()
                self.plot_multipoles()

                # write table
                self.fill_multipole_table()

                # write database
                if not Lib.db_save_measurement():
                    Lib.db_save_failure(4)
                    raise

                # saves measurement to log file
                if _save_flag:
                    _ans = Lib.save_log_file(path=_dir)
                    if not _ans:
                        _ans = QtWidgets.QMessageBox.question(self,'Warning',"Failed to save log file.\nContinue measurements anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                        if _ans == QtWidgets.QMessageBox.No:
                            Lib.db_save_failure(5)
                            raise

                #checks standard deviation
                _ans = self.check_std()
                if not _ans:
                    Lib.db_save_failure(1)
                    _ans = QtWidgets.QMessageBox.question(self,'Warning',"Standard deviation too high.\nContinue measurement anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if _ans == QtWidgets.QMessageBox.No:
                        raise

                self.ui.lb_meas_counter.setText('{0:04}'.format(i+1))
                self.ui.tabWidget.setTabEnabled(7, True)
                QtWidgets.QApplication.processEvents()
                
                if Lib.flags.stop_all:
                    raise
            #End loop for n_collections

            #Saves data to set_of_collections table if a set of measurements was successfull
            if _n_collections > 1:
                if self.ui.chb_automatic_ps.isChecked():
                    if _secondary:
                        _type = 2
                    else:
                        _type = 1
                    _current_min = _current_array.min()
                    _current_max = _current_array.max()
                else:
                    _type = 0
                    _current_min = Lib.get_value(Lib.ps_settings, 'Current Setpoint', float)
                    _current_max = _current_min
                if not Lib.db_save_set(_n_collections, _type, _current_min, _current_max):
                    raise

            #Set current to zero after measurement
            if self.ui.chb_clear_current.isChecked():
                if self.ui.chb_automatic_ps.isChecked():
                    self.current_setpoint(0, _secondary)
                else:
                    self.current_setpoint(0, False)

            #Move coil to assembly position after measurement
            self.ui.le_encoder_setpoint.setText(Lib.get_value(Lib.coil_settings,'trigger_ref',str))
            self.move_to_encoder_position()

            if Lib.flags.stop_all == False:
                QtWidgets.QMessageBox.information(self,'Information','Measurement completed.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.information(self,'Information','Failure during measurement.',QtWidgets.QMessageBox.Ok) 

            self.ui.pb_start_meas.setEnabled(True)
            self.ui.le_n_collections.setEnabled(True)
            Lib.App.myapp.ui.tabWidget.setTabEnabled(5, True)
            self.ui.tabWidget_2.setEnabled(True)
            self.ui.chb_automatic_ps.setEnabled(True)
        except:
            if self.ui.chb_clear_current.isChecked():
                self.current_setpoint(0, False) #sets main current to zero
            QtWidgets.QMessageBox.warning(self,'Warning','Measurement failed.',QtWidgets.QMessageBox.Ok)
            self.ui.pb_start_meas.setEnabled(True)
            self.ui.le_n_collections.setEnabled(True)
            Lib.App.myapp.ui.tabWidget.setTabEnabled(5, True)
            self.ui.tabWidget_2.setEnabled(True)
            self.ui.chb_automatic_ps.setEnabled(True)

    def misalignment(self):
        '''
        Check misalignment with ND780 before measurement 
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
                    return False
                else:
                    return True
        except:
            return False
     
    def collect_infocomponents(self):
        '''
        Setup verification routines
        '''
        try:
            if not Lib.get_value(Lib.data_settings, 'disable_alignment_interlock', int):
                if self.misalignment():
                    pass
                else:
                    raise
        except:
            QtWidgets.QMessageBox.warning(self,'Warning','Stages alignment failed.',QtWidgets.QMessageBox.Ok)
            raise
        
        if not Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int):
            if not Lib.get_value(Lib.aux_settings,'status_ps',int):
                QtWidgets.QMessageBox.warning(self,'Warning','Power supply is not ready.',QtWidgets.QMessageBox.Ok)
                raise
            if self.ui.lb_status_ps.text() == 'NOK':
                QtWidgets.QMessageBox.warning(self,'Warning','Power supply is not ready.\nVerify power supply data.',QtWidgets.QMessageBox.Ok)
                raise 
        if self.ui.lb_status_coil.text() == 'NOK':
            QtWidgets.QMessageBox.warning(self,'Warning','Please, load the coil data.',QtWidgets.QMessageBox.Ok)
            raise 
        if self.ui.lb_status_integrator.text() == 'NOK':
            QtWidgets.QMessageBox.warning(self,'Warning','Please, configure the Integrator FDI 2056. \nClick "Set Gain" button.',QtWidgets.QMessageBox.Ok)
            raise

        _i = Lib.get_value(Lib.data_settings, 'remove_initial_turns', int)
        _f = Lib.get_value(Lib.data_settings, 'remove_final_turns', int)
        _n = Lib.get_value(Lib.data_settings, 'total_number_of_turns', int)
        if _i + _f >= _n:
            _ans = QtWidgets.QMessageBox.question(self, 'Discard turns error', 'Number of discarded turns is greater than the total number of turns.\nWould you like to continue the measurement discarding zero turns?', QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if _ans == QtWidgets.QMessageBox.No:
                raise

    def coil_position_correction(self):
        """
        Before start measurement, keep coil in ref trigger + half turn
        """
        self.config_coil()
        _velocity = Lib.get_value(Lib.data_settings,'rotation_motor_speed',int)
        _acceleration = Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',int)
        _trigger = Lib.get_value(Lib.coil_settings,'trigger_ref',int)
        _encoder_pulse = Lib.get_value(Lib.data_settings,'n_encoder_pulses',int) #360000
    
        _position = _trigger + (_encoder_pulse / 2)
        if _position > _encoder_pulse:
            _position = _position - _encoder_pulse
            
        _address_motor = Lib.get_value(Lib.data_settings,'rotation_motor_address',int)
        
        self.angular_position(_position,_address_motor,_velocity,_acceleration,_encoder_pulse)
        time.sleep(1)
        
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
            self.stdN_norm = 1/abs(self.averageS.values[n_ref-1]) * np.sqrt(self.stdN**2 + (self.stdS.values[n_ref-1]**2)*(self.averageN**2)/(self.averageS.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            self.averageS_norm = self.df_skew_multipoles_norm.mean(axis=1)
            self.stdS_norm = 1/abs(self.averageS.values[n_ref-1]) * np.sqrt(self.stdS**2 + (self.stdS.values[n_ref-1]**2)*(self.averageS**2)/(self.averageS.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            
        else: #Normal magnet normalization
            self.df_norm_multipoles_norm = self.df_norm_multipoles / self.df_norm_multipoles.iloc[n_ref-1,:]
            self.df_skew_multipoles_norm = self.df_skew_multipoles / self.df_norm_multipoles.iloc[n_ref-1,:]
            
            for i in range(len(self.df_norm_multipoles_norm.columns)):
                self.df_norm_multipoles_norm.iloc[:,i] = self.df_norm_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))
                self.df_skew_multipoles_norm.iloc[:,i] = self.df_skew_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))
            
            self.averageN_norm = self.df_norm_multipoles_norm.mean(axis=1)
            self.stdN_norm = 1/abs(self.averageN.values[n_ref-1]) * np.sqrt(self.stdN**2 + (self.stdN.values[n_ref-1]**2)*(self.averageN**2)/(self.averageN.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            self.averageS_norm = self.df_skew_multipoles_norm.mean(axis=1)
            self.stdS_norm = 1/abs(self.averageN.values[n_ref-1]) * np.sqrt(self.stdS**2 + (self.stdN.values[n_ref-1]**2)*(self.averageS**2)/(self.averageN.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
     
    def popup_meas(self):
        try:
            self.dialog = QtWidgets.QDialog()
            self.dialog.ui = Ui_Pop_Up()
            self.dialog.ui.setupUi(self.dialog)
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            
            try:
                Lib.measurement_settings != None
            except TypeError:
                self.dialog.ui.le_magnet_name.setText(Lib.get_value(Lib.measurement_settings, 'name', str))
                self.dialog.ui.cb_operator.setCurrentText(Lib.get_value(Lib.measurement_settings, 'operator', str))
                self.dialog.ui.cb_magnet_model.setCurrentIndex(Lib.get_value(Lib.measurement_settings, 'magnet_model', int))

            if Lib.get_value(Lib.aux_settings, 'status_ps_2', int):
                self.dialog.cb_trim_coil_type.setEnabled(True)
            self.dialog.ui.bB_ok_cancel.accepted.connect(self.ok_popup)
            self.dialog.ui.bB_ok_cancel.rejected.connect(self.cancel_popup)
            if Lib.get_value(Lib.data_settings, 'enable_Agilent34970A', int):
                _temp = Lib.comm.agilent34970a.read_temp_volt()[0]
                self.dialog.ui.le_temperature.setText(str(round(float(_temp),1)))
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
        _n_of_turns = self.df_rawcurves.shape[1]
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
                    anl = self.df_fft[i].real[n]
                    bnl = -self.df_fft[i].imag[n]
                    
                    an = (anl*np.sin(dtheta*n) + bnl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius2**n - _radius1**n)/n)*(np.cos(dtheta*n)-1)) 
                    bn = (bnl*np.sin(dtheta*n) - anl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius2**n - _radius1**n)/n)*(np.cos(dtheta*n)-1))        
                
                    self.df_norm_multipoles.iloc[n-1,i] = bn
                    self.df_skew_multipoles.iloc[n-1,i] = an
        
        #Tangential coil calculation:
        if _coil_type == 1:
            _radiusDelta = _radius1*np.pi/180
            for i in range(_n_of_turns):
                for n in range(1,_nmax+1):
                    anl = self.df_fft[i].real[n]
                    bnl = -self.df_fft[i].imag[n]
                    
                    an = n * (_radius2**(-n)) * ((anl)*(np.cos(n*dtheta)-1) - bnl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))
                    bn = n * (_radius2**(-n)) * ((bnl)*(np.cos(n*dtheta)-1) + anl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))
            
                    self.df_norm_multipoles.iloc[n-1,i] = bn 
                    self.df_skew_multipoles.iloc[n-1,i] = an

        self.averageN = self.df_norm_multipoles.mean(axis=1)
        self.stdN = self.df_norm_multipoles.std(axis=1)
        self.averageS = self.df_skew_multipoles.mean(axis=1)
        self.stdS = self.df_skew_multipoles.std(axis=1)
        self.averageMod = np.sqrt(self.averageN**2 + self.averageS**2)
        self.stdMod = np.sqrt(self.averageN**2*self.stdN**2 + self.averageS**2*self.stdS**2) / (self.averageMod) #error propagation
        if _magnet_model == 4: #Angle calculation for skew magnet
            self.averageAngle = (1/self.averageN.index) * np.arctan(self.averageN/self.averageS)
        else: #Angle calculation for normal magnet
            self.averageAngle = (1/self.averageN.index) * np.arctan(self.averageS/self.averageN)
        self.stdAngle = (1/self.averageN.index) * 1/(self.averageN**2 + self.averageS**2) * np.sqrt(self.averageS**2 * self.stdN**2 + self.averageN**2 * self.stdS**2) #error propagation is equal for normal and skew magnets

    def check_std(self):
        """
        Checks standard deviation magnitode and returns false if greater than maximum error
        """
        _n_ref = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)
        if _n_ref == 0:
            _max_error = 1
            _n_ref = _n_ref + 1 #checks dipole error
        elif _n_ref == 1:
            _max_error = 8e-6
        elif _n_ref == 2 or _n_ref == 4:
            _max_error = 8e-4
        elif _n_ref == 3:
            _max_error = 3.6e-2
        
        if self.stdN[_n_ref] > _max_error or self.stdS[_n_ref] > _max_error:
            return False
        return True

    def fft_calculation(self): # Ok
        """
        """
        _n_of_turns = self.df_rawcurves.shape[1]
        self.df_fft = pd.DataFrame()

        for i in range(_n_of_turns):
            _tmp = self.df_rawcurves[i].tolist()
            _tmpfft = np.fft.fft(_tmp) / (len(_tmp)/2)
            self.df_fft[i] = _tmpfft
            
    def displacement_calculation(self):
        _main_harmonic = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)

        if _main_harmonic > 1:
            if _main_harmonic == 4: #Skew quadrupole
                #Prepares skew magnet center calculation
                _main_harmonic = 2 #Quadrupole main harmonic is 2
                _main_multipole = self.averageS[_main_harmonic]
                _prev_multipole = self.averageS[_main_harmonic-1]
                _prev_perp_multipole = self.averageN[_main_harmonic-1]
                _dy_sign = -1
            else:
                #Prepares normal magnet center calculation
                _main_multipole = self.averageN[_main_harmonic]
                _prev_multipole = self.averageN[_main_harmonic-1]
                _prev_perp_multipole = self.averageS[_main_harmonic-1]
                _dy_sign = 1

            _dx = (1/(_main_harmonic-1))*(_prev_multipole/_main_multipole)
            _dy = (_dy_sign)*(1/(_main_harmonic-1))*(_prev_perp_multipole/_main_multipole)
            _dx_um = round(_dx*1e06, 3)
            _dy_um = round(_dy*1e06, 3)

            self.ui.le_magnetic_center_x.setText(str(_dx_um))
            self.ui.le_magnetic_center_y.setText(str(_dy_um))
            
            Lib.write_value(Lib.measurement_settings, 'magnetic_center_x', _dx_um, True)
            Lib.write_value(Lib.measurement_settings, 'magnetic_center_y', _dy_um, True)

        else:
            self.ui.le_magnetic_center_x.setText("")
            self.ui.le_magnetic_center_y.setText("")
            
    def configure_integrator(self, adj_offset=False): # Ok
        """
        """
        _n_of_turns = Lib.get_value(Lib.data_settings,'total_number_of_turns',int)

        _n_encoder_pulses = int(Lib.get_value(Lib.data_settings, 'n_encoder_pulses', float))
        _gain =  Lib.get_value(Lib.data_settings, 'integrator_gain', int)
        try:
            if Lib.get_value(Lib.measurement_settings, 'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()

        try:
            _trigger_ref = Lib.get_value(Lib.coil_settings, 'trigger_ref', int)
        except:
            if adj_offset:
                _trigger_ref = 0
            else:
                raise
        if _trigger_ref > int(_n_encoder_pulses-1):
            QtWidgets.QMessageBox.warning(self,'Warning',"Trigger ref greater than allowed.",QtWidgets.QMessageBox.Ok)
            return False
        
        _n_integration_points = Lib.get_value(Lib.data_settings, 'n_integration_points', int)

        if adj_offset:
            _n_of_turns = 1

        try:
            Lib.comm.fdi.config_measurement(_n_encoder_pulses, _direction, _trigger_ref, _n_integration_points, _n_of_turns)
            return True
        except:
            traceback.print_exc(file=sys.stdout)
            return False       

    def measure_and_read(self): # Ok
        """
        """
        _n_of_turns = Lib.get_value(Lib.data_settings, 'total_number_of_turns', int)
        _n_integration_points = Lib.get_value(Lib.data_settings, 'n_integration_points', int)
        _total_n_of_points = _n_integration_points * _n_of_turns

        #starts monitor thread
        self.sync.clear()
        _thread = threading.Thread(target=self.monitor_thread, name='Monitor Thread')
        _thread.start()

        if Lib.flags.stop_all == False:
            #corrects coil position
            self.coil_position_correction()

            # start measurement
            Lib.comm.fdi.start_measurement()

        #Enables monitor thread
        self.sync.set()
        
        if Lib.flags.stop_all == False:
            # move motor     
            self.move_motor_measurement(_n_of_turns+1)
        # start collecting data
        _status = int(Lib.comm.fdi.status('1')[-3])
        while (_status != 1) and (Lib.flags.stop_all == False):
            _status = int(Lib.comm.fdi.status('1')[-3])           
            QtWidgets.QApplication.processEvents()
        if Lib.flags.stop_all == False:
            _results = Lib.comm.fdi.get_data()
            self.data_array = np.fromstring(_results[:-1], dtype=np.float64, sep=' A')
            self.data_array = self.data_array * 1e-12
            
            try:
                _tmp = self.data_array.reshape(_n_of_turns,_n_integration_points).transpose()
            except:
                if int(Lib.comm.fdi.status('4')[-1]):
                    Lib.db_save_failure(2)
                    QtWidgets.QMessageBox.warning(self,'Warning',"Integrator tension over-range.\nPlease configure a lower gain.",QtWidgets.QMessageBox.Ok)
                else:
                    Lib.db_save_failure(0)
                raise
            #discart initial and final turns
            _i = Lib.get_value(Lib.data_settings, 'remove_initial_turns', int)
            _f = -Lib.get_value(Lib.data_settings, 'remove_final_turns', int)
            if not _f: #avoids error if _f == 0
                _f = None
            if _i + _f < _n_of_turns:
                _tmp = _tmp[:,_i:_f]
            self.df_rawcurves = pd.DataFrame(_tmp)
        
    def plot_raw_graph(self): # Ok
        """
        """
        self.ui.gv_rawcurves.plotItem.curves.clear()
        self.ui.gv_rawcurves.clear()
        self.ui.gv_rawcurves.plotItem.setLabel('left', "Amplitude", units="V.s")
        self.ui.gv_rawcurves.plotItem.setLabel('bottom', "Points")
        self.ui.gv_rawcurves.plotItem.showGrid(x=True, y=True, alpha=0.2)

        px = np.linspace(0, len(self.data_array)-1, len(self.data_array))
        self.ui.gv_rawcurves.plotItem.plot(px, self.data_array, pen=(255,0,0), symbol=None)

    def plot_multipoles(self):
        """
        """
        self.ui.gv_multipoles.clear()
        
        _px = np.linspace(1, 15, 15)
        
        _n = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)
        if _n == 4: #sextupolo skew
            _n = 2
        _n = _n - 1
        
        self.ui.gv_multipoles.plotItem.addLegend()
        _graph = pg.BarGraphItem(x=_px, height=self.averageN_norm.values, width=0.6, brush='r', name='Normal')
        _graph2 = pg.BarGraphItem(x=_px, height=self.averageS_norm.values, width=0.6, brush='b', name='Skew')
        
        self.ui.gv_multipoles.addItem(_graph)
        self.ui.gv_multipoles.addItem(_graph2)
        self.ui.gv_multipoles.plotItem.setLabel('left', 'Normalized Multipoles')
        self.ui.gv_multipoles.plotItem.setLabel('bottom', "Multipole number")
        self.ui.gv_multipoles.plotItem.showGrid(x=True, y=True, alpha=0.2)
        if _n > -1:
            _maxn = np.delete(abs(self.averageN_norm.values), _n).max()
            _maxs = np.delete(abs(self.averageS_norm.values), _n).max()
            _max = max(_maxn, _maxs)
            self.ui.gv_multipoles.plotItem.setYRange(-_max,_max)
        
    def save_data_results(self):
        """Save results to log file"""
        _dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save Directory', Lib.dir_path).replace('/', '\\\\') + '\\\\'
        _ans = Lib.save_log_file(path=_dir)
        if _ans:
            QtWidgets.QMessageBox.information(self,'Information',"Log file successfully saved.",QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self,'Warning',"Failed to save log file.",QtWidgets.QMessageBox.Ok)


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
        self.ui.cb_disp_port.setCurrentText(Lib.get_value(Lib.data_settings,'disp_port',str))
        self.ui.cb_driver_port.setCurrentText(Lib.get_value(Lib.data_settings,'driver_port',str))
        self.ui.cb_integrator_port.setCurrentText(Lib.get_value(Lib.data_settings,'integrator_port',str))
        self.ui.cb_ps_port.setCurrentText(Lib.get_value(Lib.data_settings,'ps_port',str))
 
        self.ui.chb_enable_Agilent34970A.setChecked(Lib.get_value(Lib.data_settings,'enable_Agilent34970A',int))
        self.ui.sb_agilent34970A_address.setValue(Lib.get_value(Lib.data_settings,'agilent34970A_address',int))
               
        # Settings Tab
        self.ui.le_total_number_of_turns.setText(Lib.get_value(Lib.data_settings,'total_number_of_turns',str))
        self.ui.le_remove_initial_turns.setText(Lib.get_value(Lib.data_settings,'remove_initial_turns',str))
        self.ui.le_remove_final_turns.setText(Lib.get_value(Lib.data_settings,'remove_final_turns',str))

        self.ui.le_rotation_motor_address.setText(Lib.get_value(Lib.data_settings,'rotation_motor_address',str))
        self.ui.le_rotation_motor_resolution.setText(Lib.get_value(Lib.data_settings,'rotation_motor_resolution',str))        
        self.ui.le_rotation_motor_speed.setText(Lib.get_value(Lib.data_settings,'rotation_motor_speed',str))
        self.ui.le_rotation_motor_acceleration.setText(Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',str))
        self.ui.le_rotation_motor_ratio.setText(Lib.get_value(Lib.data_settings,'rotation_motor_ratio',str))

        self.ui.le_n_encoder_pulses.setText(Lib.get_value(Lib.data_settings,'n_encoder_pulses',str))        
        
        self.ui.cb_integrator_gain.setCurrentText(str(Lib.get_value(Lib.data_settings,'integrator_gain',int)))
        self.ui.cb_n_integration_points.setCurrentText(str(Lib.get_value(Lib.data_settings,'n_integration_points',int)))
        
        self.ui.chb_disable_alignment_interlock.setChecked(Lib.get_value(Lib.data_settings,'disable_alignment_interlock',int))
        self.ui.chb_disable_ps_interlock.setChecked(Lib.get_value(Lib.data_settings,'disable_ps_interlock',int))
        
        self.ui.cb_bench.setCurrentIndex(Lib.get_value(Lib.data_settings,'bench',int) - 1)

        # Motor Tab
        self.ui.le_motor_vel.setText(Lib.get_value(Lib.data_settings,'rotation_motor_speed',str))
        self.ui.le_motor_ace.setText(Lib.get_value(Lib.data_settings,'rotation_motor_acceleration',str))
        self.ui.le_motor_turns.setText(str(1))        

        
    def config_variables(self): # Ok
        """
        Refresh variables with inteface values
        """
        try:
            # Connection Tab 
            Lib.write_value(Lib.data_settings,'disp_port',self.ui.cb_disp_port.currentText())
            Lib.write_value(Lib.data_settings,'driver_port',self.ui.cb_driver_port.currentText())
            Lib.write_value(Lib.data_settings,'integrator_port',self.ui.cb_integrator_port.currentText())
            Lib.write_value(Lib.data_settings,'ps_port',self.ui.cb_ps_port.currentText())

            Lib.write_value(Lib.data_settings,'enable_Agilent34970A', int(self.ui.chb_enable_Agilent34970A.isChecked()))
            Lib.write_value(Lib.data_settings,'agilent34970A_address',self.ui.sb_agilent34970A_address.value(),True)
                   
            # Settings Tab
            Lib.write_value(Lib.data_settings,'total_number_of_turns',self.ui.le_total_number_of_turns.text(),True)
            Lib.write_value(Lib.data_settings,'remove_initial_turns',self.ui.le_remove_initial_turns.text(),True)
            Lib.write_value(Lib.data_settings,'remove_final_turns',self.ui.le_remove_final_turns.text(),True)
    
            Lib.write_value(Lib.data_settings,'rotation_motor_address',self.ui.le_rotation_motor_address.text(),True)
            Lib.write_value(Lib.data_settings,'rotation_motor_resolution',self.ui.le_rotation_motor_resolution.text(),True)        
            Lib.write_value(Lib.data_settings,'rotation_motor_speed',self.ui.le_rotation_motor_speed.text(),True)
            Lib.write_value(Lib.data_settings,'rotation_motor_acceleration',self.ui.le_rotation_motor_acceleration.text(),True)
            Lib.write_value(Lib.data_settings,'rotation_motor_ratio',self.ui.le_rotation_motor_ratio.text(),True)
            
            Lib.write_value(Lib.data_settings,'n_encoder_pulses',self.ui.le_n_encoder_pulses.text(),True)  
    
            Lib.write_value(Lib.data_settings,'integrator_gain',int(self.ui.cb_integrator_gain.currentText()))
            Lib.write_value(Lib.data_settings,'n_integration_points',int(self.ui.cb_n_integration_points.currentText()))
    
            Lib.write_value(Lib.data_settings,'disable_alignment_interlock', int(self.ui.chb_disable_alignment_interlock.isChecked()))
            Lib.write_value(Lib.data_settings,'disable_ps_interlock', int(self.ui.chb_disable_ps_interlock.isChecked()))
            
            Lib.write_value(Lib.data_settings,'bench',self.ui.cb_bench.currentIndex() + 1)
            return True
        except:
            QtWidgets.QMessageBox.warning(self,'Warning',"Could not configure the settings.\nCheck if all the inputs are numbers.",QtWidgets.QMessageBox.Ok)
            return False
  
    def refresh_coiltab(self): # Ok     
        # Coil Tab
        try:
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
            return True
        except:
            QtWidgets.QMessageBox.warning(self,'Warning','Failed to load coil',QtWidgets.QMessageBox.Ok)
            return False

    def configure_coil(self):
        try:
            if Lib.coil_settings == None:
                Lib.coil_df()
        except TypeError:
            pass
        _ans = self.config_coil()
        if _ans:
            QtWidgets.QMessageBox.information(self,'Information',"Coil configurations completed successfully.",QtWidgets.QMessageBox.Ok)

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
            return True
        except:
            QtWidgets.QMessageBox.warning(self,'Warning',"Could not configure the coil settings.\nCheck if all the coil inputs are correct.",QtWidgets.QMessageBox.Ok)
            return False

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
        #Settings
        self.ui.le_maximum_current.setText(str(Lib.get_value(Lib.ps_settings,'Maximum Current',float)))
        self.ui.le_minimum_current.setText(str(Lib.get_value(Lib.ps_settings,'Minimum Current',float)))
        self.ui.sb_kp.setValue(Lib.get_value(Lib.ps_settings,'Kp',float))
        self.ui.sb_ki.setValue(Lib.get_value(Lib.ps_settings,'Ki',float))
        self.ui.dcct_select.setCurrentIndex(Lib.get_value(Lib.ps_settings,'DCCT Head', int))

    def configure_ps(self, secondary=False):
        if not secondary:
            try:
                if Lib.ps_settings == None:
                    Lib.ps_df(False)
            except TypeError:
                pass
            self.ui.gb_start_supply.setEnabled(True)
            _ans = self.config_ps()
        else:
            try:
                if Lib.ps_settings_2 == None:
                    Lib.ps_df(True)
            except TypeError:
                pass
            self.ui.gb_start_supply_2.setEnabled(True)
            _ans = self.config_ps_2()
        if _ans:
            QtWidgets.QMessageBox.information(self,'Information',"Configurations completed successfully.",QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self,'Warning',"Failed to configure power supply.\nCheck if all values are numbers.",QtWidgets.QMessageBox.Ok)

    def config_ps(self):
        """
        Write variables with interface values for new features
        """
        try:
            # Power Supply Tab
            Lib.write_value(Lib.ps_settings,'Power Supply Name',self.ui.le_PS_Name.text())
            Lib.write_value(Lib.ps_settings,'Power Supply Type', self.ui.cb_ps_type.currentIndex()+2,True)
            Lib.write_value(Lib.ps_settings,'Current Setpoint',self.ui.dsb_current_setpoint.value(),True)
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
            #Automatic setpoints
            _values = self.keep_auto_values(1)
            _values = ", ".join(str(x) for x in _values)          
            Lib.write_value(Lib.ps_settings,'Automatic Setpoints',str(_values),False)       
            #Settings
            Lib.write_value(Lib.ps_settings,'Maximum Current',self.ui.le_maximum_current.text(),True)
            Lib.write_value(Lib.ps_settings,'Minimum Current',self.ui.le_minimum_current.text(),True)
            Lib.write_value(Lib.ps_settings,'Kp',self.ui.sb_kp.text(),True)
            Lib.write_value(Lib.ps_settings,'Ki',self.ui.sb_ki.text(),True)
            Lib.write_value(Lib.ps_settings,'DCCT Head',self.ui.dcct_select.currentIndex(),True)
            return True
        except:
            QtWidgets.QMessageBox.warning(self,'Warning',"Could not configure the power supply settings.\nCheck if all the inputs are correct.",QtWidgets.QMessageBox.Ok)
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
            QtWidgets.QMessageBox.warning(self,'Warning',"Could not configure the secondary power supply settings.\nCheck if all the inputs are correct.",QtWidgets.QMessageBox.Ok)
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
                _auto_values = np.asarray(_auto.split(','), dtype=float)
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Could not get the automatic current values from interface.',QtWidgets.QMessageBox.Ok)
                return
            try:
                self.clear_table(secondary)
                for i in range(len(_auto_values)):
                    _tw.insertRow(i)   
                    self.set_table_item(_tw, i, 0, _auto_values[i])
                QtWidgets.QApplication.processEvents()
            except:
                QtWidgets.QMessageBox.warning(self,'Warning','Could not write the automatic current values on interface.',QtWidgets.QMessageBox.Ok)
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
            item.setText('{0:0.3e}'.format(val))
        else:
            item = QtWidgets.QTableWidgetItem()
            table.setItem(row, col, item)
            item.setText(str(val))

    def stop(self, emergency=True):
        """Function stops motor, integrador and power supplies in case of emergency
        """
        Lib.flags.stop_all = True
        #stops motor
        self.stop_motor()
        #stops integrator
        Lib.comm.fdi.send(Lib.comm.fdi.PDIStop)
            
        self.ui.pb_start_meas.setEnabled(True)
        self.ui.le_n_collections.setEnabled(True)
        self.ui.tabWidget.setTabEnabled(5, True)
        self.ui.chb_automatic_ps.setEnabled(True)
        QtWidgets.QApplication.processEvents()
        
        #Move coil to assembly position
        self.ui.le_encoder_setpoint.setText(Lib.get_value(Lib.coil_settings,'trigger_ref',str))
        self.move_to_encoder_position() #this clears stop_all flag
        Lib.flags.stop_all = True #setting stop_all again

        if emergency:
            Lib.flags.emergency = emergency
            
            try:
                if Lib.ps_settings_2 == None:
                    _secondary_flag = 0
            except TypeError:
                _secondary_flag = Lib.get_value(Lib.ps_settings_2, 'ps_status_2', int)            
            _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
            if _secondary_flag:
                _ps_type_2 = Lib.get_value(Lib.ps_settings_2, 'Power Supply Type', int)
            #Turn off main power supply
            Lib.comm.drs.SetSlaveAdd(_ps_type)
            Lib.comm.drs.OpMode(0)
            Lib.comm.drs.SetISlowRef(0)
            time.sleep(0.1)
            Lib.comm.drs.TurnOff()
            time.sleep(0.1)
            if Lib.comm.drs.Read_ps_OnOff() == 0:
                Lib.write_value(Lib.aux_settings, 'status_ps', 0)
                Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                self.ui.pb_PS_button.setChecked(False)
                self.ui.pb_PS_button.setText('Turn ON')
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
                time.sleep(0.1)
                if Lib.comm.drs.Read_ps_OnOff() == 0:
                    Lib.write_value(Lib.aux_settings, 'status_ps_2', 0)
                    Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                    self.ui.pb_PS_button_2.setChecked(False)
                    self.ui.pb_PS_button_2.setText('Turn ON')
                    QtWidgets.QApplication.processEvents()
                        
            QtWidgets.QMessageBox.warning(self,'Warning','Emergency situation. \nMotor and Integrator are stopped, power supply(ies) turned off.',QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.information(self,'Information','The measurement was stopped.',QtWidgets.QMessageBox.Ok)

    def dcct_convert(self):
        _voltage = Lib.comm.agilent34970a.read_temp_volt()[2]
        if _voltage =='':
            _current = 0
        else:
            if self.ui.dcct_select.currentIndex() == 0:   #For 40 A dcct head
                _current = (float(_voltage))*4
            if self.ui.dcct_select.currentIndex() == 1:   #For 160 A dcct head
                _current = (float(_voltage))*16
            if self.ui.dcct_select.currentIndex() == 2:   #For 320 A dcct head
                _current = (float(_voltage))*32
        return _current

    def monitor_thread(self):
        """Function to generate a thread which monitors power supply 
        currents and interlocks"""
        _n_turns = Lib.get_value(Lib.data_settings, 'total_number_of_turns', int)
        #check interlock if disable_ps_interlock not checked
        _disable_interlock = Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int)
        _interlock_flag = 0
        #clear main_current_array, secondary_current_array and main_voltage_array
        Lib.write_value(Lib.aux_settings, 'main_current_array', pd.DataFrame([]))
        Lib.write_value(Lib.aux_settings, 'secondary_current_array', pd.DataFrame([]))
        Lib.write_value(Lib.aux_settings, 'main_voltage_array', pd.DataFrame([]))
        
        try:
            if Lib.ps_settings_2 == None:
                _secondary_flag = 0
        except TypeError:
            _secondary_flag = Lib.get_value(Lib.ps_settings_2, 'ps_status_2', int)
        _voltage_flag = self.ui.chb_voltage.isChecked()
        _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
        _velocity = Lib.get_value(Lib.data_settings,'rotation_motor_speed', float)
        if _secondary_flag:
            _ps_type_2 = Lib.get_value(Lib.ps_settings_2, 'Power Supply Type', int)

        self.sync.wait() #waits for main loop to enable monitoring
        for i in range(_n_turns):
            _t = time.time()

            #monitor main coil current and interlocks
            Lib.comm.drs.SetSlaveAdd(_ps_type)
            if not _disable_interlock:
                _soft_interlock = Lib.comm.drs.Read_ps_SoftInterlocks()
                _hard_interlock = Lib.comm.drs.Read_ps_HardInterlocks()
#             _current = round(float(Lib.comm.drs.Read_iLoad1()),3)
            if Lib.get_value(Lib.data_settings, 'enable_Agilent34970A', int):
                _current = round(self.dcct_convert(),3)
            else:
                _current = round(float(Lib.comm.drs.Read_iLoad1()),3)
            _i = Lib.get_value(Lib.aux_settings, 'main_current_array')
            _i = _i.append([_current], ignore_index=True)
            Lib.write_value(Lib.aux_settings, 'main_current_array', _i)

            #monitor secondary coil current  and interlocks if exists
            if _secondary_flag:
                Lib.comm.drs.SetSlaveAdd(_ps_type_2)
                if not _disable_interlock:
                    _soft_interlock_2 = Lib.comm.drs.Read_ps_SoftInterlocks()
                    _hard_interlock_2 = Lib.comm.drs.Read_ps_HardInterlocks()
                _current_2 = round(float(Lib.comm.drs.Read_iLoad1()),3)
                _i_2 = Lib.get_value(Lib.aux_settings, 'secondary_current_array')
                _i_2 = _i_2.append([_current_2], ignore_index=True)
                Lib.write_value(Lib.aux_settings, 'secondary_current_array', _i_2)

            #monitor main coil voltage / magnet resistance (dcct)
            if _voltage_flag and Lib.get_value(Lib.data_settings, 'enable_Agilent34970A', int): #voltage read from 34970A multichannel
                _voltage = round(float(Lib.comm.agilent34970a.read_temp_volt()[1]),3)
                _v = Lib.get_value(Lib.aux_settings, 'main_voltage_array')
                _v = _v.append([_voltage], ignore_index=True)
                Lib.write_value(Lib.aux_settings, 'main_voltage_array', _v)

            #in case of interlock or emergency, cuts off power supply, stop motors, abort integrator, send warning
            if not _disable_interlock:
                _interlock = _soft_interlock + _hard_interlock
                _interlock_flag = _interlock  
                if _secondary_flag:
                    _interlock_2 = _soft_interlock_2 + _hard_interlock_2
                    _interlock_flag = _interlock_flag + _interlock_2
                    
            if _interlock_flag or Lib.flags.stop_all:
                if _interlock:
                    self.ui.pb_interlock.setChecked(True)
                    self.ui.pb_emergency1.click()
                if _secondary_flag:
                    if _interlock_2:
                        self.ui.pb_interlock_2.setChecked(True)
                        self.ui.pb_emergency1.click()
                QtWidgets.QApplication.processEvents()
                if Lib.flags.emergency:
                    Lib.db_save_failure(3)
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
