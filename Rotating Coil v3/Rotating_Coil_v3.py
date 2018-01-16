#!/usr/bin/python
# -*- coding: utf-8 -*-

# Remainders:

# sys.path.append(str(sys.path[0])+str('\\PUC_2v6')) ## Nome da pasta com biblioteca da PUC

import time
import threading
import numpy as np
import pandas as pd
import serial.tools.list_ports
# import ctypes
# import matplotlib.pyplot as plt

#import traceback
import sys
from PyQt5 import QtWidgets#,QtCore, QtGui

from Rotating_Coil_Interface_v3 import Ui_RotatingCoil_Interface
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
#         for i in range(1,self.ui.tabWidget.count()):
#             self.ui.tabWidget.setTabEnabled(i,False)
        
        # Connection Tab 
#         self.ui.cb_display_type
#         self.ui.cb_disp_port
#         self.ui.cb_driver_port
#         self.ui.cb_integrator_port
#         self.ui.cb_ps_type
#         self.ui.cb_PUC_type
#         self.ui.cb_PUC_port
#         self.ui.sb_PUC_address
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

        # Measurements Tab
        self.ui.le_magnet_name
        self.ui.le_temperature
        self.ui.chb_seriesofmeas
        self.ui.le_n_series
        self.ui.chb_automatic_ps
        self.ui.cb_magnet_model
        self.ui.le_norm_radius
        self.ui.cb_coil_rotation_direction
        self.ui.lb_status_ps
        self.ui.lb_status_coil
        self.ui.lb_status_integrator
        self.ui.lb_meas_counter
        self.ui.le_meas_details
        self.ui.pb_start_meas.clicked.connect(self.start_meas)
        self.ui.pb_stop_meas.clicked.connect(self.stop_meas)
        
    def connect_devices(self):
        """
        connect devices and check status
        """
        try:
            # connect display
            Lib.comm.display = Display_Heidenhain.SerialCom(int(Lib.get_value(Lib.data_settings,'disp_port')),'ND-780')
            Lib.comm.display.connect()
    
            # connect driver 
            Lib.comm.parker = Parker_Drivers.SerialCom(int(Lib.get_value(Lib.data_settings,'driver_port')))
            Lib.comm.parker.connect()
    
            # connect integrator
            Lib.comm.fdi = FDI2056.SerialCom(int(Lib.get_value(Lib.data_settings,'integrator_port')))
            Lib.comm.fdi.connect()
            
            # connect agilent 33220a - function generator
            if self.ui.chb_enable_Agilent33220A.checkState() != 0:        
                Lib.comm.agilent33220a = Agilent_33220A.GPIB()
                Lib.comm.agilent33220a.connect(int(Lib.get_value(Lib.data_settings,'enable_Agilent33220A')))        
    
            # connect agilent 34401a - voltmeter
            if self.ui.chb_enable_Agilent34401A.checkState() != 0:        
                Lib.comm.agilent34401a = Agilent_34401A.GPIB()
                Lib.comm.agilent34401a.connect(int(Lib.get_value(Lib.data_settings,'enable_Agilent34401A')))        
    
            # connect agilent 34970a - multichannel
            if self.ui.chb_enable_Agilent34970A.checkState() != 0:        
                Lib.comm.agilent34970a = Agilent_34970A.GPIB()
                Lib.comm.agilent34970a.connect(int(Lib.get_value(Lib.data_settings,'enable_Agilent34970A')))
                
            # connect digital power supply
            Lib.comm.drs = SerialDRS.SerialDRS_FBP()
            Lib.comm.drs.Connect(int(Lib.get_value(Lib.data_settings,'ps_port')))
            
            QtWidgets.QMessageBox.warning(self,'Information','Devices connected.',QtWidgets.QMessageBox.Ok)            
        except:
            #traceback.print_exc(file=sys.stdout)
            QtWidgets.QMessageBox.warning(self,'Information','Fail to connect devices',QtWidgets.QMessageBox.Ok) 
            
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
        address = int(Lib.get_value(Lib.data_settings,'rotation_motor_address'))
        _ratio = float(Lib.get_value(Lib.data_settings,'rotation_motor_ratio'))

        resolution = int(Lib.get_value(Lib.data_settings,'rotation_motor_resolution'))        
        vel = float(self.ui.le_motor_vel.text()) * _ratio
        acce = float(self.ui.le_motor_ace.text()) * _ratio
        nturns = float(self.ui.le_motor_turns.text()) * _ratio
        
        direction = self.ui.cb_driver_direction.currentIndex()
        steps = abs(int(nturns * float(Lib.get_value(Lib.data_settings,'rotation_motor_resolution'))))
        
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
        address = int(Lib.get_value(Lib.data_settings,'rotation_motor_address'))
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
        
        address = int(Lib.get_value(Lib.data_settings,'rotation_motor_address'))
        _ratio = float(Lib.get_value(Lib.data_settings,'rotation_motor_ratio'))
        
        resolution = int(Lib.get_value(Lib.data_settings,'rotation_motor_resolution'))
        vel = float(self.ui.le_motor_vel.text()) * _ratio
        acce = float(self.ui.le_motor_ace.text()) * _ratio
        
        _pulses = self.pulses_to_go()
        steps =  abs(int( _pulses * int(Lib.get_value(Lib.data_settings,'rotation_motor_resolution')) / int(Lib.get_value(Lib.data_settings,'n_encoder_pulses')) * _ratio))

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
        address = int(Lib.get_value(Lib.data_settings,'rotation_motor_address'))
        _ratio = float(Lib.get_value(Lib.data_settings,'rotation_motor_ratio'))
        
        resolution = int(Lib.get_value(Lib.data_settings,'rotation_motor_resolution'))
        vel = float(Lib.get_value(Lib.data_settings,'rotation_motor_speed')) * _ratio
        acce = float(Lib.get_value(Lib.data_settings,'rotation_motor_acceleration')) * _ratio
#         nturns = float(self.ui.le_motor_turns.text()) * _ratio
        nturns = turns * _ratio        
        
        direction = self.ui.cb_coil_rotation_direction.currentIndex()
        steps = abs(int(nturns * float(Lib.get_value(Lib.data_settings,'rotation_motor_resolution'))))
        
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
            _n_encoder_pulses = int(float(Lib.get_value(Lib.data_settings,'n_encoder_pulses'))/4)
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
                QtWidgets.QMessageBox.warning(self,'Information','Coil File loaded.',QtWidgets.QMessageBox.Ok)
                
            else:
                QtWidgets.QMessageBox.warning(self,'Information','Fail to load Coil File.',QtWidgets.QMessageBox.Ok) 
        except:
            return
    
    def save_coil(self): # Ok
        """
        """
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self,'Save Coil File' , Lib.dir_path, 'Data files (*.dat);;Text files (*.txt)')
            
            self.config_coil()

            if Lib.save_coil(filename[0]) == True:
                QtWidgets.QMessageBox.warning(self,'Information','Coil File saved.',QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.warning(self,'Information','Fail to save Coil File.',QtWidgets.QMessageBox.Ok) 
        except:
            return

    def start_meas(self):
        """ 
        """
        Lib.flags.stop_all = False
        
        # data array
        self.data_array = np.array([])
        self.df_rawcurves = None   
        
        # check components
        
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

        if Lib.flags.stop_all == False:
            QtWidgets.QMessageBox.warning(self,'Information','Measurement completed.',QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self,'Information','Failure during measurement.',QtWidgets.QMessageBox.Ok) 
    
    def multipoles_normalization(self): # Ok
        """
        """
        r_ref = float(self.ui.le_norm_radius.text())/1000 # convert meters
        n_ref = self.ui.cb_magnet_model.currentIndex()
        i_ref = self.df_norm_multipoles.index.values
        
        self.df_norm_multipoles_norm = self.df_norm_multipoles / self.df_norm_multipoles.iloc[n_ref-1,:]
        self.df_skew_multipoles_norm = self.df_skew_multipoles / self.df_norm_multipoles.iloc[n_ref-1,:]        
        
        for i in range(len(self.df_norm_multipoles_norm.columns)):
            self.df_norm_multipoles_norm.iloc[:,i] = self.df_norm_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))
            self.df_skew_multipoles_norm.iloc[:,i] = self.df_skew_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))            
                 
    def multipoles_calculation(self): # Ok
        """
        """
        _nmax = 15
        _n_of_turns = int(Lib.get_value(Lib.data_settings,'total_number_of_turns'))
        _n_integration_points = int(self.ui.cb_n_integration_points.currentText())
                
        _n_coil_turns = int(Lib.get_value(Lib.coil_settings,'n_turns_normal'))
        _radius1 = float(Lib.get_value(Lib.coil_settings,'radius1_normal'))
        _radius2 = float(Lib.get_value(Lib.coil_settings,'radius2_normal'))

        self.df_norm_multipoles = pd.DataFrame(index=range(1,_nmax+1), columns=range(_n_of_turns))
        self.df_skew_multipoles = pd.DataFrame(index=range(1,_nmax+1), columns=range(_n_of_turns))        
        
        dtheta = 2*np.pi/_n_integration_points
        for i in range(_n_of_turns):
            for n in range(1,_nmax+1):
                anl = self.df_fft[i].imag[n]
                bnl = -self.df_fft[i].real[n]
                
                an = (anl*np.sin(dtheta*n) + bnl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius1**n - _radius2**n)/n)*(np.cos(dtheta*n)-1)) 
                bn = (bnl*np.sin(dtheta*n) - anl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius1**n - _radius2**n)/n)*(np.cos(dtheta*n)-1))        
            
                self.df_norm_multipoles.iloc[n-1,i] = an
                self.df_skew_multipoles.iloc[n-1,i] = bn
                        
    def fft_calculation(self): # Ok
        """
        """
        _n_of_turns = int(Lib.get_value(Lib.data_settings,'total_number_of_turns'))
        self.df_fft = pd.DataFrame()
        
        for i in range(_n_of_turns):
            _tmp = self.df_rawcurves[i].tolist()
            _tmpfft = -np.fft.fft(_tmp) / (len(_tmp)/2)
            self.df_fft[i] = _tmpfft

    def configure_integrator(self): # Ok
        """
        """
        _n_of_turns = int(Lib.get_value(Lib.data_settings,'total_number_of_turns'))
        
        _n_encoder_pulses = int(float(Lib.get_value(Lib.data_settings,'n_encoder_pulses'))/4)
        _gain = self.ui.cb_integrator_gain.currentText()
        _direction = self.ui.cb_coil_rotation_direction.currentIndex()
        _trigger_ref = int(Lib.get_value(Lib.coil_settings,'trigger_ref'))
        _n_integration_points = int(self.ui.cb_n_integration_points.currentText())
        _total_n_of_points = _n_integration_points * _n_of_turns
        
        Lib.comm.fdi.config_measurement(_n_encoder_pulses, _gain, _direction, _trigger_ref, _n_integration_points, _n_of_turns)       

    def measure_and_read(self): # Ok
        """
        """
        # start measurement
        Lib.comm.fdi.start_measurement()
        
        _n_of_turns = int(Lib.get_value(Lib.data_settings,'total_number_of_turns'))
        _n_integration_points = int(self.ui.cb_n_integration_points.currentText())
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
        l = serial.tools.list_ports.comports()
        self.ports = []
        for i in l:
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
        #self.ui.cb_display_type.setCurrentIndex(int(Lib.get_value(Lib.data_settings,'display_type')))
        self.ui.cb_display_type.setCurrentIndex(Lib.get_value(Lib.data_settings,'display_type',int))

        self.ui.cb_disp_port.setCurrentText(Lib.get_value(Lib.data_settings,'disp_port',str))
        self.ui.cb_driver_port.setCurrentText(Lib.get_value(Lib.data_settings,'driver_port',str))
        self.ui.cb_integrator_port.setCurrentText(Lib.get_value(Lib.data_settings,'integrator_port',str))
        self.ui.cb_ps_type.setCurrentIndex(Lib.get_value(Lib.data_settings,'ps_type',int))
        self.ui.cb_ps_port.setCurrentText(Lib.get_value(Lib.data_settings,'ps_port',str))
        #self.ui.sb_ps_address.setValue(int(Lib.get_value(Lib.data_settings,'ps_address')))
         
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
        
        self.ui.cb_integrator_gain.setCurrentIndex(Lib.get_value(Lib.data_settings,'integrator_gain',int))
        self.ui.cb_n_integration_points.setCurrentIndex(Lib.get_value(Lib.data_settings,'n_integration_points',int))
        
        self.ui.chb_save_turn_angles.setChecked(Lib.get_value(Lib.data_settings,'save_turn_angles',int))
        self.ui.chb_disable_aligment_interlock.setChecked(Lib.get_value(Lib.data_settings,'disable_aligment_interlock',int))
        self.ui.chb_disable_ps_interlock.setChecked(Lib.get_value(Lib.data_settings,'disable_ps_interlock',int))

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
        Lib.write_value(Lib.data_settings,'disp_port',self.ui.cb_disp_port.currentIndex())
        Lib.write_value(Lib.data_settings,'driver_port',self.ui.cb_driver_port.currentIndex())
        Lib.write_value(Lib.data_settings,'integrator_port',self.ui.cb_integrator_port.currentIndex())
        Lib.write_value(Lib.data_settings,'ps_type',self.ui.cb_ps_type.currentIndex())
        Lib.write_value(Lib.data_settings,'ps_port',self.ui.cb_ps_port.currentIndex())
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

        Lib.write_value(Lib.data_settings,'integrator_gain',self.ui.cb_integrator_gain.currentIndex())
        Lib.write_value(Lib.data_settings,'n_integration_points',self.ui.cb_n_integration_points.currentIndex())

        Lib.write_value(Lib.data_settings,'save_turn_angles',self.ui.chb_save_turn_angles.checkState())
        Lib.write_value(Lib.data_settings,'disable_aligment_interlock',self.ui.chb_disable_aligment_interlock.checkState())
        Lib.write_value(Lib.data_settings,'disable_ps_interlock',self.ui.chb_disable_ps_interlock.checkState())
  
    def refresh_coiltab(self): # Ok     
        # Coil Tab
        self.ui.le_coil_name.setText(str((Lib.get_value(Lib.coil_settings,'coil_name'))))
        self.ui.le_n_turns_normal.setText(str((Lib.get_value(Lib.coil_settings,'n_turns_normal'))))
        self.ui.le_radius1_normal.setText(str((Lib.get_value(Lib.coil_settings,'radius1_normal'))))
        self.ui.le_radius2_normal.setText(str((Lib.get_value(Lib.coil_settings,'radius2_normal'))))
        self.ui.le_n_turns_bucked.setText(str((Lib.get_value(Lib.coil_settings,'n_turns_bucked'))))
        self.ui.le_radius1_bucked.setText(str((Lib.get_value(Lib.coil_settings,'radius1_bucked'))))
        self.ui.le_radius2_bucked.setText(str((Lib.get_value(Lib.coil_settings,'radius2_bucked'))))
        self.ui.le_trigger_ref.setText(str(int(Lib.get_value(Lib.coil_settings,'trigger_ref'))))
        
        if Lib.get_value(Lib.coil_settings,'coil_type') == 'Radial':
            self.ui.cb_coil_type.setCurrentIndex(0)
        else:
            self.ui.cb_coil_type.setCurrentIndex(1)            

        self.ui.te_comments.setPlainText(str((Lib.get_value(Lib.coil_settings,'comments'))))
        
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

    def fill_multipole_table(self): # Ok
        """
        """
        n_rows = self.ui.tw_multipoles_table.rowCount()
        
        _averageN = self.df_norm_multipoles.mean(axis=1)
        _stdN = self.df_norm_multipoles.std(axis=1)
        _averageS = self.df_skew_multipoles.mean(axis=1)
        _stdS = self.df_skew_multipoles.std(axis=1)  
        _averageMod = np.sqrt(_averageN**2 + _averageS**2)
        _stdMod = np.sqrt(_stdS**2 + _stdS**2)
        _averageAngle = (1/_averageN.index) * np.arctan(_averageN/_averageS)
        _stdAngle =  (1/_averageN.index) * np.arctan(_stdN/_stdS)

        _averageN_norm = self.df_norm_multipoles_norm.mean(axis=1)
        _averageS_norm = self.df_skew_multipoles_norm.mean(axis=1)

        for i in range(n_rows):
            self.set_table_item(self.ui.tw_multipoles_table,i, 0, _averageN.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 1, _stdN.values[i])            
            self.set_table_item(self.ui.tw_multipoles_table,i, 2, _averageS.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 3, _stdS.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 4, _averageMod.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 5, _stdMod.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 6, _averageAngle.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 7, _stdAngle.values[i])            
            self.set_table_item(self.ui.tw_multipoles_table,i, 8, _averageN_norm.values[i])
            self.set_table_item(self.ui.tw_multipoles_table,i, 9, _averageS_norm.values[i])            

    def set_table_item(self,table,row,col,val): # Ok
        """
        """
        item = QtWidgets.QTableWidgetItem()
        table.setItem(row, col, item)
        item.setText('{0:0.6e}'.format(val))
        
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
        
