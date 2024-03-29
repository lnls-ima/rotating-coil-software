#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import traceback
import numpy as np
import pandas as pd
import pyqtgraph as pg
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QMessageBox as _QMessageBox,
    QProgressDialog as _QProgressDialog)

import FDI2056
from pydrs import SerialDRS
import Agilent_34970A
import Agilent_34401A
import Parker_Drivers
import Display_Heidenhain
from Pop_up import Ui_Pop_Up
import Rotating_Coil_Library as Library
from Rotating_Coil_Interface import Ui_RotatingCoil_Interface

from imautils.devices import Agilent34401ALib as multimeter
from matplotlib.figure import Figure as _Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as _FigureCanvas,
    NavigationToolbar2QT as _Toolbar)


class PlotDialog(QtWidgets.QDialog):
    """Matplotlib plot dialog."""

    def __init__(self, parent=None):
        """Add figure canvas to layout."""
        super().__init__(parent)

        self.figure = _Figure()
        self.canvas = _FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(self.canvas)
        self.toolbar = _Toolbar(self.canvas, self)
        _layout.addWidget(self.toolbar)
        self.setLayout(_layout)

    def updatePlot(self):
        """Update plot."""
        self.canvas.draw()

    def show(self):
        """Show dialog."""
        self.updatePlot()
        super().show()


class ApplicationWindow(QtWidgets.QMainWindow):
    """Rotating Coil Software user interface."""
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_RotatingCoil_Interface()
        self.ui.setupUi(self)

        self.timer = QtCore.QTimer()
        self.signals()

        #power supply current slope, [F1000A, F225A, F10A] [A/s]
        self.slope = [50, 90, 1000]

        self.refresh_interface()

        self.plot_dialog = PlotDialog()

        self.sync = threading.Event()

    def signals(self):
        """Connects UI signals and functions."""
        for i in range(1, self.ui.tabWidget.count()):
            # Lock main Tabs
            self.ui.tabWidget.setTabEnabled(i, False)

        # tabWidget
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
        self.ui.pb_move_to_encoder_position.clicked.connect(
            self.move_to_encoder_position)
        self.ui.pb_config_integrator.clicked.connect(self.config_integrator)
        self.ui.pb_status_update.clicked.connect(self.status_update)
        self.ui.pb_emergency2.clicked.connect(lambda: self.stop(True))

        # Coil Tab
        self.ui.pb_config_coil.clicked.connect(self.configure_coil)
        self.ui.pb_load_coil.clicked.connect(self.load_coil)
        self.ui.pb_save_coil.clicked.connect(self.save_coil)
        self.ui.pb_emergency3.clicked.connect(lambda: self.stop(True))

        # Power Supply tab
        self.ui.pb_ps_button.clicked.connect(
            lambda: self.start_powersupply(False))
        self.ui.pb_refresh.clicked.connect(lambda: self.display_current(False))
        self.ui.pb_load_ps.clicked.connect(
            lambda: self.load_PowerSupply(False))
        self.ui.pb_save_ps.clicked.connect(
            lambda: self.save_PowerSupply(False))
        self.ui.pb_send.clicked.connect(lambda: self.send_setpoint(False))
        self.ui.pb_add_row.clicked.connect(
            lambda: self.add_row(self.ui.tw_currents))
        self.ui.pb_remove_row.clicked.connect(
            lambda: self.remove_row(self.ui.tw_currents))
        self.ui.pb_clear_table.clicked.connect(
            lambda: self.clear_table(self.ui.tw_currents))
        self.ui.pb_add_row_3.clicked.connect(
            lambda: self.add_row(self.ui.tw_trapezoidal))
        self.ui.pb_remove_row_3.clicked.connect(
            lambda: self.remove_row(self.ui.tw_trapezoidal))
        self.ui.pb_clear_table_3.clicked.connect(
            lambda: self.clear_table(self.ui.tw_trapezoidal))
        self.ui.pb_send_curve.clicked.connect(lambda: self.send_curve(False))
        self.ui.pb_config_pid.clicked.connect(self.config_pid)
        self.ui.pb_reset_inter.clicked.connect(
            lambda: self.reset_interlocks(False))
        self.ui.pb_list_interlocks.clicked.connect(
            lambda: self.list_interlocks(False))
        self.ui.pb_cycle.clicked.connect(lambda: self.cycling_ps(False))
        self.ui.pb_config_ps.clicked.connect(lambda: self.configure_ps(False))
        self.ui.pb_plot.clicked.connect(lambda: self.plot(False))
        #Secondary Power Supply
        self.ui.pb_ps_button_2.clicked.connect(
            lambda: self.start_powersupply(True))
        self.ui.pb_refresh_2.clicked.connect(
            lambda: self.display_current(True))
        self.ui.pb_load_ps_2.clicked.connect(
            lambda: self.load_PowerSupply(True))
        self.ui.pb_save_ps_2.clicked.connect(
            lambda: self.save_PowerSupply(True))
        self.ui.pb_send_2.clicked.connect(lambda: self.send_setpoint(True))
        self.ui.pb_add_row_2.clicked.connect(
            lambda: self.add_row(self.ui.tw_currents_2))
        self.ui.pb_remove_row_2.clicked.connect(
            lambda: self.remove_row(self.ui.tw_currents_2))
        self.ui.pb_clear_table_2.clicked.connect(
            lambda: self.clear_table(self.ui.tw_currents_2))
        self.ui.pb_add_row_4.clicked.connect(
            lambda: self.add_row(self.ui.tw_trapezoidal_2))
        self.ui.pb_remove_row_4.clicked.connect(
            lambda: self.remove_row(self.ui.tw_trapezoidal_2))
        self.ui.pb_clear_table_4.clicked.connect(
            lambda: self.clear_table(self.ui.tw_trapezoidal_2))
        self.ui.pb_reset_inter_2.clicked.connect(
            lambda: self.reset_interlocks(True))
        self.ui.pb_list_interlocks_2.clicked.connect(
            lambda: self.list_interlocks(True))
        self.ui.pb_send_curve_2.clicked.connect(lambda: self.send_curve(True))
        self.ui.pb_cycle_2.clicked.connect(lambda: self.cycling_ps(True))
        self.ui.pb_plot_2.clicked.connect(lambda: self.plot(True))
        self.ui.pb_send_curve_3.clicked.connect(lambda: self.send_curve(True))
        self.ui.pb_cycle_3.clicked.connect(lambda: self.cycling_ps(True))
        self.ui.pb_plot_3.clicked.connect(lambda: self.plot(True))
        self.ui.pb_send_curve_4.clicked.connect(lambda: self.send_curve(True))
        self.ui.pb_cycle_4.clicked.connect(lambda: self.cycling_ps(True))
        self.ui.pb_plot_4.clicked.connect(lambda: self.plot(True))
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
        """Reads agilent multichannel and prints it's values on monitor tab."""
        if all([Lib.get_value(Lib.data_settings, 'enable_Agilent34970A', int),
                Lib.flags.devices_connected]):
            try:
                _ans = Lib.comm.agilent34970a.read_temp_volt()
                self.ui.lcdNumber.display(_ans[0])
                self.ui.lcdNumber_2.display(_ans[1])
                self.ui.lcdNumber_3.display(_ans[2])
                self.ui.lcdNumber_4.display(_ans[3])
                self.ui.lcdNumber_5.display(_ans[4])
                QtWidgets.QApplication.processEvents()
            except Exception:
                traceback.print_exc(file=sys.stdout)

    def tabWidget(self):
        """Checks if current tab is Monitor tab to start the monitor timer."""
        if self.ui.tabWidget.currentIndex() == 5:
            self.timer.start(2000)
        else:
            self.timer.stop()

    def connect_devices(self):
        """Connect devices and check status."""
        self.ui.pb_connect_devices.setText('Processing...')
        QtWidgets.QApplication.processEvents()
        if not Lib.flags.devices_connected:
            try:
                _con_prg_dialog = _QProgressDialog('Connecting', None, 0, 5,
                                                   self)
                _con_prg_dialog.setWindowTitle('Connection')
                _con_prg_dialog.show()
                QtWidgets.QApplication.processEvents()
                self.config_variables()

                # connect digital power supply
                Lib.comm.drs1 = SerialDRS()
                _ps_port = Lib.get_value(Lib.data_settings, 'ps_port', str)
                Lib.comm.drs1.Connect(_ps_port)
                if not Lib.comm.drs1.ser.is_open:
                    _con_prg_dialog.destroy()
                    _QMessageBox.warning(self, 'Warning', 'Failed to '
                                         'connect to Power Supply.',
                                         _QMessageBox.Ok)
                    raise Exception

                _ps_port_2 = Lib.get_value(Lib.data_settings, 'ps_port_2', str)
                if _ps_port_2 != 'None':
                    if _ps_port_2 == _ps_port:
                        Lib.comm.drs2 = Lib.comm.drs1
                    else:
                        _con_prg_dialog.destroy()
                        Lib.comm.drs2 = SerialDRS()
                        Lib.comm.drs2.Connect(Lib.get_value(Lib.data_settings,
                                                        'ps_port_2', str))
                        if not Lib.comm.drs2.ser.is_open:
                            _QMessageBox.warning(self, 'Warning', 'Failed to '
                                                 'connect to Power Supply.',
                                                 _QMessageBox.Ok)
                            raise Exception
                else:
                    Lib.comm.drs2 = None
                _con_prg_dialog.setValue(1)
                QtWidgets.QApplication.processEvents()

                # connect integrator
                Lib.comm.fdi = FDI2056.EthernetCom()
                _bench = Lib.get_value(Lib.data_settings, 'bench', int)
                _ans = Lib.comm.fdi.connect(_bench)
                if not _ans:
                    _ans = Lib.comm.fdi.connect(_bench)
                    if not _ans:
                        _con_prg_dialog.destroy()
                        Lib.comm.drs1.Disconnect()
                        if _ps_port_2 != 'None':
                            Lib.comm.drs2.Disconnect()
                        Lib.comm.fdi.disconnect()
                        _QMessageBox.warning(self, 'Warning', 'Failed'
                                             ' to connect to the integrator.',
                                             _QMessageBox.Ok)
                        raise Exception
                _con_prg_dialog.setValue(2)
                QtWidgets.QApplication.processEvents()

                # connect display
                Lib.comm.display = Display_Heidenhain.SerialCom(
                    Lib.get_value(Lib.data_settings, 'disp_port', str),
                    'ND-780')
                Lib.comm.display.connect()
                _con_prg_dialog.setValue(3)
                QtWidgets.QApplication.processEvents()

                # connect driver
                Lib.comm.parker = Parker_Drivers.SerialCom(
                    Lib.get_value(Lib.data_settings, 'driver_port', str))
                Lib.comm.parker.connect()

                Lib.write_value(Lib.data_settings, 'agilent34970A_address',
                                self.ui.sb_agilent34970A_address.value(), True)
                _con_prg_dialog.setValue(4)
                QtWidgets.QApplication.processEvents()

                # connect agilent 34970a - multichannel
                if self.ui.chb_enable_Agilent34970A.isChecked() != 0:
                    Lib.comm.agilent34970a = Agilent_34970A.GPIB()
                    _ans = Lib.comm.agilent34970a.connect(
                        Lib.get_value(Lib.data_settings,
                                      'agilent34970A_address', int))
                    if not _ans:
                        _con_prg_dialog.destroy()
                        Lib.comm.display.disconnect()
                        Lib.comm.drs1.Disconnect()
                        if _ps_port_2 != 'None':
                            Lib.comm.drs2.Disconnect()
                        Lib.comm.fdi.disconnect()
                        Lib.comm.parker.disconnect()
                        _QMessageBox.warning(self, 'Warning', 'Failed'
                                             ' to connect to Agilent 34970A.',
                                             _QMessageBox.Ok)
                        raise Exception
                    Lib.comm.agilent34970a.config_temp_volt()
                    time.sleep(0.1)
                    # this line prevents crash on monitor tab
                    Lib.comm.agilent34970a.read_val()
                    self.ui.lb_status_34970A.setText('Connected')
                
                
                #adding agilent 34401A multimeter
                if self.ui.chb_enable_Agilent34401A.isChecked() != 0:
                    #Lib.comm.agilent34401A = Agilent_34401A.GPIB()
                    Lib.comm.agilent34401A = multimeter.Agilent34401AGPIB()

#                     _ans2 = Lib.comm.agilent34401A.connect(
#                         Lib.get_value(Lib.data_settings,
#                                       'agilent34401A_address', int))
                    _ans2 = Lib.comm.agilent34401A.connect(
                        Lib.get_value(Lib.data_settings,
                                      'agilent34401A_address', int), board=1)
                    if not _ans2:
                        _con_prg_dialog.destroy()
                        Lib.comm.display.disconnect()
                        Lib.comm.drs1.Disconnect()
                        if _ps_port_2 != 'None':
                            Lib.comm.drs2.Disconnect()
                        Lib.comm.fdi.disconnect()
                        Lib.comm.parker.disconnect()
                        _QMessageBox.warning(self, 'Warning', 'Failed'
                                             ' to connect to Agilent 34401A.',
                                             _QMessageBox.Ok)
                        raise Exception
                    Lib.comm.agilent34401A.config()
                    time.sleep(0.1)
                    self.ui.lb_status_34401A.setText('Connected')
                    
                _con_prg_dialog.setValue(5)
                QtWidgets.QApplication.processEvents()
                _con_prg_dialog.destroy()
                _QMessageBox.information(self, 'Information',
                                         'Devices connected.',
                                         _QMessageBox.Ok)
                self.ui.pb_connect_devices.setText('Disconnect Devices')
                Lib.flags.devices_connected = True
                for i in range(1, 7):
                    # Unlock main Tabs
                    self.ui.tabWidget.setTabEnabled(i, True)
            except Exception:
                traceback.print_exc(file=sys.stdout)
                self.ui.pb_connect_devices.setText('Connect Devices')
                _QMessageBox.warning(self, 'Warning',
                                     'Failed to connect devices',
                                     _QMessageBox.Ok)

        else:
            try:
                # disconnect display
                if Lib.comm.display is not None:
                    Lib.comm.display.disconnect()

                # disconnect driver
                if Lib.comm.parker is not None:
                    Lib.comm.parker.disconnect()

                # disconnect integrator
                if Lib.comm.fdi is not None:
                    Lib.comm.fdi.disconnect()

                # disconnect agilent 34970a - Multichannel
                if self.ui.lb_status_34970A.text() == 'Connected':
                    Lib.comm.agilent34970a.disconnect()
                    self.ui.lb_status_34970A.setText('Disconnected')
                    
                 # disconnect agilent 34401A - Multimeter
                if self.ui.lb_status_34401A.text() == 'Connected':
                    Lib.comm.agilent34401A.disconnect()
                    self.ui.lb_status_34401A.setText('Disconnected')

                # disconnect digital power supply
                if Lib.comm.drs1 is not None:
                    Lib.comm.drs1.Disconnect()
                if Lib.comm.drs2 is not None:
                    Lib.comm.drs2.Disconnect()

                _QMessageBox.information(self, 'Information',
                                         'Devices disconnected.',
                                         _QMessageBox.Ok)
                self.ui.pb_connect_devices.setText('Connect Devices')
                Lib.flags.devices_connected = False
                for i in range(1, 7):
                    # Lock main Tabs
                    self.ui.tabWidget.setTabEnabled(i, False)
            except Exception:
                traceback.print_exc(file=sys.stdout)
                self.ui.pb_connect_devices.setText('Disconnect Devices')
                _QMessageBox.warning(self, 'Warning',
                                     'Failed disconnecting devices',
                                     _QMessageBox.Ok)

    def save_config(self):
        """Save settings in external file."""
        if self.config_variables():
            if Lib.save_settings():
                _QMessageBox.information(self, 'Information',
                                         'File saved successfully.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Failed to save settings',
                                     _QMessageBox.Ok)
                return

    def config(self):
        """Configure interface data into program variables."""
        if self.ui.chb_disable_alignment_interlock.isChecked():
            _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                         'DISABLE alignment interlock?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                self.ui.chb_disable_alignment_interlock.setChecked(False)
                return
        if self.ui.chb_disable_ps_interlock.isChecked():
            _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                         'DISABLE power supply interlock?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                self.ui.chb_disable_alignment_interlock.setChecked(False)
                return
        if not self.config_variables():
            _QMessageBox.warning(self, 'Warning', 'Failed to configure '
                                 'settings.\nCheck if all the settings values '
                                 'are numbers.',
                                 _QMessageBox.Ok)
        _QMessageBox.information(self, 'Information',
                                 'Configuration completed successfully.',
                                 _QMessageBox.Ok)

    def set_address(self, address, secondary):
        """Sets power supply address.

        Args:
            address (int): power supply new address.
        Returns:
            True in case of success.
            False otherwise."""

        if not secondary:
            Lib.comm.drs = Lib.comm.drs1
        else:
            Lib.comm.drs = Lib.comm.drs2

        if Lib.comm.drs.ser.is_open:
            if address == 2: # F1000 capacitor bank address
                address = 1 # F1000 controller address
            elif address == 1:
                address = 2
            Lib.comm.drs.SetSlaveAdd(address)
            return True
        else:
            _QMessageBox.warning(self, 'Warning',
                                 'Power Supply serial port is closed.',
                                 _QMessageBox.Ok)
            return False

    def set_op_mode(self, mode=0):
        """Sets power supply operation mode.

        Args:
            mode (int): 0 for SlowRef, 1 for SigGen.
        Returns:
            True in case of success.
            False otherwise."""
        if mode:
            _mode = 'Cycle'
        else:
            _mode = 'SlowRef'
        Lib.comm.drs.select_op_mode(_mode)
        time.sleep(0.1)
        if Lib.comm.drs.read_ps_opmode() == _mode:
            return True
        return False

    def start_powersupply(self, secondary=False):
        """Turns power supply on and off."""
        try:
            if not secondary:
                self.ui.pb_ps_button.setEnabled(False)
                self.ui.pb_ps_button.setText('Processing...')
                _df = Lib.ps_settings
                _status_ps = Lib.get_value(Lib.aux_settings, 'status_ps', int)
            else:
                self.ui.pb_ps_button_2.setEnabled(False)
                self.ui.pb_ps_button_2.setText('Processing...')
                _df = Lib.ps_settings_2
                _status_ps = Lib.get_value(Lib.aux_settings, 'status_ps_2',
                                           int)
            self.ui.tabWidget_2.setEnabled(False)
            QtWidgets.QApplication.processEvents()

            _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
            if not self.set_address(_ps_type, secondary):
                if _status_ps:
                    self.change_ps_button(secondary, False)
                else:
                    self.change_ps_button(secondary, True)
                return

            _safety_enabled = 1
            if all([Lib.get_value(Lib.data_settings, 'disable_ps_interlock',
                                  int),
                    ((secondary is False and _status_ps == 0) or
                    (secondary is True and _status_ps == 0))]):
                _ret = _QMessageBox.question(self, 'Attention',
                                             'Do you want to turn on the Power'
                                             ' Supply with Safety Control'
                                             'DISABLED?',
                                             _QMessageBox.Yes |
                                             _QMessageBox.No,
                                             _QMessageBox.No)
                if _ret == _QMessageBox.Yes:
                    _safety_enabled = 0
                else:
                    self.change_ps_button(secondary, True)
                    return

            # Status PS is OFF
            if not _status_ps:
                try:
                    Lib.comm.drs.read_iload1()
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    _QMessageBox.warning(self, 'Warning',
                                         'Could not read the current.',
                                         _QMessageBox.Ok)
                    self.change_ps_button(secondary, True)
                    return

                if _safety_enabled == 1:
                    _status_interlocks = Lib.comm.drs.read_ps_softinterlocks()
                    if _status_interlocks != 0:
                        self.ui.pb_interlock.setChecked(True)
                        _QMessageBox.warning(self, 'Warning',
                                             'Soft Interlock activated!',
                                             _QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return
                    _status_interlocks = Lib.comm.drs.read_ps_hardinterlocks()
                    if _status_interlocks != 0:
                        self.ui.pb_interlock.setChecked(True)
                        _QMessageBox.warning(self, 'Warning',
                                             'Hard Interlock activated!',
                                             _QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return

                # PS 1000 A needs to turn dc link on
                if _ps_type == 2:
                    Lib.comm.drs.SetSlaveAdd(_ps_type)
                    # Turn ON PS DClink
                    try:
                        # Turn ON the DC Link of the PS
                        Lib.comm.drs.turn_on()
                        time.sleep(1)
                        if Lib.comm.drs.read_ps_onoff() != 1:
                            _QMessageBox.warning(self, 'Warning',
                                                 'Power Supply Capacitor Bank '
                                                 'did not initialize.',
                                                 _QMessageBox.Ok)
                            self.change_ps_button(secondary, True)
                            return
                    except Exception:
                        _QMessageBox.warning(self, 'Warning',
                                             'Power Supply Capacitor Bank '
                                             'did not initialize.',
                                             _QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return
                    # Closing DC link Loop
                    try:
                        Lib.comm.drs.closed_loop()        # Closed Loop
                        time.sleep(1)
                        if Lib.comm.drs.read_ps_openloop() == 1:
                            _QMessageBox.warning(self, 'Warning',
                                                 'Power Supply circuit loop is'
                                                 ' not closed.',
                                                 _QMessageBox.Ok)
                            self.change_ps_button(secondary, True)
                            return
                    except Exception:
                        _QMessageBox.warning(self, 'Warning', 'Power Supply '
                                             'circuit loop is not closed.',
                                             _QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return
                    # Set ISlowRef for DC Link (Capacitor Bank)
                    # Operation mode selection for Slowref
                    if not self.set_op_mode(0):
                        _QMessageBox.warning(self, 'Warning', 'Could not set '
                                             'the slowRef operation mode.',
                                             _QMessageBox.Ok)
                        self.change_ps_button(secondary, True)
                        return
                    # 90 V
                    _dclink_value = Lib.get_value(Lib.aux_settings,
                                                  'dclink_value', float)
                    # Set 90 V for Capacitor Bank (default value according to
                    # the ELP Group)
                    Lib.comm.drs.set_slowref(_dclink_value)
                    time.sleep(1)
                    _feedback_DCLink = Lib.comm.drs.read_vdclink()
                    # Waiting few seconds until voltage stabilization before
                    # starting PS Current
                    _i = 100
                    while _feedback_DCLink < _dclink_value and _i > 0:
                        _feedback_DCLink = Lib.comm.drs.read_vdclink()
                        QtWidgets.QApplication.processEvents()
                        time.sleep(0.5)
                        _i = _i - 1
                    if _i == 0:
                        _QMessageBox.warning(self, 'Warning', 'DC link '
                                             'setpoint is not set.\nCheck '
                                             'configurations.',
                                             _QMessageBox.Ok)
                        Lib.comm.drs.turn_off()
                        self.change_ps_button(secondary, True)
                        return
                #Turn on Power Supply
                Lib.comm.drs.SetSlaveAdd(_ps_type - 1)  # Set ps address
                self.pid_setting(secondary)
                Lib.comm.drs.turn_on()
                time.sleep(1)
                if not Lib.comm.drs.read_ps_onoff():
                    if _ps_type == 2:
                        Lib.comm.drs.SetSlaveAdd(_ps_type)
                    # turn_off PS DC Link
                    Lib.comm.drs.turn_off()
                    self.change_ps_button(secondary, True)
                    _QMessageBox.warning(self, 'Warning',
                                         'The Power Supply did not start.',
                                         _QMessageBox.Ok)
                    return
                # Closed Loop
                Lib.comm.drs.closed_loop()
                time.sleep(0.1)
                if _ps_type == 2:
                    time.sleep(0.9)
                if Lib.comm.drs.read_ps_openloop() == 1:
                    Lib.comm.drs.SetSlaveAdd(_ps_type)
                    # turn_off PS DC Link
                    Lib.comm.drs.turn_off()
                    self.change_ps_button(secondary, True)
                    _QMessageBox.warning(self, 'Warning', 'Power Supply '
                                         'circuit loop is not closed.',
                                         _QMessageBox.Ok)
                    return
                self.change_ps_button(secondary, False)
                if not secondary:
                    # Status PS is ON
                    Lib.write_value(Lib.aux_settings, 'status_ps', 1)
                    Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                    self.ui.le_status_loop.setText('Closed')
                    self.ui.lb_status_ps.setText('OK')
                    self.ui.tabWidget_2.setEnabled(True)
                    self.ui.tabWidget_3.setEnabled(True)
                    self.ui.pb_refresh.setEnabled(True)
                    self.ui.pb_send.setEnabled(True)
                    self.ui.pb_send_curve.setEnabled(True)
                else:
                    # Status PS is ON
                    Lib.write_value(Lib.aux_settings, 'status_ps_2', 1)
                    Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                    self.ui.le_status_loop_2.setText('Closed')
                    self.ui.pb_send_2.setEnabled(True)
                    self.ui.pb_send_curve_2.setEnabled(True)
                    self.ui.pb_send_curve_3.setEnabled(True)
                    self.ui.pb_send_curve_4.setEnabled(True)
                    self.ui.pb_refresh_2.setEnabled(True)
                self.display_current(secondary)
                _QMessageBox.information(self, 'Information', 'The Power '
                                         'Supply started successfully.',
                                         _QMessageBox.Ok)
            # Turn off power supply
            else:
                if _ps_type == 2:
                    Lib.comm.drs.SetSlaveAdd(_ps_type - 1)
                else:
                    Lib.comm.drs.SetSlaveAdd(_ps_type)
                Lib.comm.drs.turn_off()
                time.sleep(1)
                _status = Lib.comm.drs.read_ps_onoff()
                if _status:
                    _QMessageBox.warning(self, 'Warning', 'Could not turn the'
                                         ' power supply off.\nPlease, try '
                                         'again.',
                                         _QMessageBox.Ok)
                    self.change_ps_button(secondary, False)
                    return
                # Turn of dc link
                if _ps_type == 2:
                    Lib.comm.drs.SetSlaveAdd(_ps_type)
                    Lib.comm.drs.turn_off()
                    time.sleep(0.1)
                    if _ps_type == 2:
                        time.sleep(0.9)
                    _status = Lib.comm.drs.read_ps_onoff()
                    if _status:
                        _QMessageBox.warning(self, 'Warning', 'Could not turn'
                                             ' the power supply off.\n'
                                             'Please, try again.',
                                             _QMessageBox.Ok)
                        self.change_ps_button(secondary, False)
                        return
                if not secondary:
                    # Status PS is OFF
                    Lib.write_value(Lib.aux_settings, 'status_ps', 0)
                    Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                    self.ui.lb_status_ps.setText('NOK')
                    self.ui.le_status_loop.setText('Open')
                    self.ui.pb_send.setEnabled(False)
                    self.ui.pb_cycle.setEnabled(False)
                    self.ui.pb_send_curve.setEnabled(False)
                else:
                    # Status PS_2 is OFF
                    Lib.write_value(Lib.aux_settings, 'status_ps_2', 0)
                    Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                    self.ui.le_status_loop_2.setText('Open')
                    self.ui.pb_send_2.setEnabled(False)
                    self.ui.pb_cycle_2.setEnabled(False)
                    self.ui.pb_send_curve_2.setEnabled(False)
                self.change_ps_button(secondary, True)
                _QMessageBox.information(self, 'Information',
                                         'Power supply was turned off.',
                                         _QMessageBox.Ok)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            _QMessageBox.warning(self, 'Warning',
                                 'Failed to change the power supply state.',
                                 _QMessageBox.Ok)
            self.change_ps_button(secondary, False)
            return

    def change_ps_button(self, secondary=False, is_off=True):
        """Changes UI widgets state when turning power supply on/off."""
        if not secondary:
            self.ui.pb_ps_button.setEnabled(True)
            if is_off:
                self.ui.pb_ps_button.setChecked(False)
                self.ui.pb_ps_button.setText('Turn ON')
            else:
                self.ui.pb_ps_button.setChecked(True)
                self.ui.pb_ps_button.setText('Turn OFF')
        else:
            self.ui.pb_ps_button_2.setEnabled(True)
            if is_off:
                self.ui.pb_ps_button_2.setChecked(False)
                self.ui.pb_ps_button_2.setText('Turn ON')
            else:
                self.ui.pb_ps_button_2.setChecked(True)
                self.ui.pb_ps_button_2.setText('Turn OFF')
        self.ui.tabWidget_2.setEnabled(True)
        QtWidgets.QApplication.processEvents()

    def config_pid(self):
        """Configures power supply PID parameters from UI."""
        _ans = _QMessageBox.question(self, 'PID settings', 'Be aware that this'
                                     ' will overwrite the current '
                                     'configurations.\nAre you sure you want '
                                     'to configure the PID parameters?',
                                     _QMessageBox.Yes |
                                     _QMessageBox.No)
        if _ans == _QMessageBox.Yes:
            _ans = self.pid_setting(False)
            if _ans:
                _QMessageBox.information(self, 'Information',
                                         'PID configured.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Power Supply PID configuration fault.',
                                     _QMessageBox.Ok)

    def pid_setting(self, secondary=False):
        """Configures power supply PID parameters."""
        try:
            if not secondary:
                _kp = float(self.ui.sb_kp.text())
                _ki = float(self.ui.sb_ki.text())
                Lib.write_value(Lib.ps_settings, 'Kp', self.ui.sb_kp.text(),
                                True)
                Lib.write_value(Lib.ps_settings, 'Ki', self.ui.sb_ki.text(),
                                True)
                _df = Lib.ps_settings
            else:
                _df = Lib.ps_settings_2

            _kp = Lib.get_value(_df, 'Kp', float)
            _ki = Lib.get_value(_df, 'Ki', float)
            _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
            if not self.set_address(_ps_type, secondary):
                return

            if _ps_type == 3:
                _umin = 0
            else:
                _umin = -0.90

            if _ps_type in [2, 3, 4]:
                _dsp_id = 0
            elif _ps_type == 5:
                _dsp_id = 1
            elif _ps_type == 6:
                _dsp_id = 2
            elif _ps_type == 7:
                _dsp_id = 3

            Lib.comm.drs.set_dsp_coeffs(3, _dsp_id, [_kp, _ki, 0.90, _umin])
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False
        return True

    def display_current(self, secondary=False):
        """Displays power supply current on Power Supply tab."""
        if not secondary:
            _df = Lib.ps_settings
            _cb = self.ui.cb_ps_type
            _le_ps_type_cfg = self.ui.le_ps_type_cfg
            _lcd = self.ui.lcd_ps_reading
            _idx = 2
        else:
            _df = Lib.ps_settings_2
            _cb = self.ui.cb_ps_type_2
            _le_ps_type_cfg = self.ui.le_ps_type_cfg_2
            _lcd = self.ui.lcd_ps_reading_2
            _idx = 4
        if _df is None:
            _QMessageBox.warning(self, 'Warning',
                                 'Please configure the power supply.',
                                 _QMessageBox.Ok)
            return
        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        _ps_type_cfg = _cb.itemText(_ps_type - _idx)
        _le_ps_type_cfg.setText(_ps_type_cfg)
        QtWidgets.QApplication.processEvents()
        if not self.set_address(_ps_type, secondary):
            return
        try:
            _refresh_current = round(float(Lib.comm.drs.read_iload1()), 3)
            _lcd.display(_refresh_current)
            if all([not secondary,
                    self.ui.chb_dcct.isChecked(),
                    self.ui.chb_enable_Agilent34970A.isChecked()]):
                self.ui.lcd_current_dcct.setEnabled(True)
                self.ui.label_161.setEnabled(True)
                self.ui.label_164.setEnabled(True)
                if self.ui.chb_enable_Agilent34401A.isChecked():
                    _agilent_reading = Lib.comm.agilent34401A.read()
                    _current = round(self.dcct_convert(_agilent_reading, True),
                                      3)
                else:
                    _agilent_reading = Lib.comm.agilent34970a.read_temp_volt()
                    _current = round(self.dcct_convert(_agilent_reading, False),
                                     3)
                #_current = round(self.dcct_convert(_agilent_reading), 3)
                self.ui.lcd_current_dcct.display(_current)
            QtWidgets.QApplication.processEvents()
        except Exception:
            traceback.print_exc(file=sys.stdout)
            _QMessageBox.warning(self, 'Warning',
                                 'Could not display the current.',
                                 _QMessageBox.Ok)
            return

    def current_setpoint(self, setpoint=0, secondary=False):
        """Changes power supply current setpoint."""
        self.ui.tabWidget_2.setEnabled(False)
        if not secondary:
            _df = Lib.ps_settings
            _slewrate = self.ui.dsb_current_slewrate.value()
        else:
            _df = Lib.ps_settings_2
            _slewrate = self.ui.dsb_current_slewrate_2.value()

        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        if not self.set_address(_ps_type, secondary):
            return False

        #send slew rate
        if _ps_type < 4:
            if self.slew_rate(_slewrate, _ps_type):
                Lib.write_value(_df, 'Current Slew Rate', _slewrate, True)

        #verify current limits
        _setpoint = setpoint
        if not self.verify_current_limits(setpoint, 0, False, secondary):
            self.ui.tabWidget_2.setEnabled(True)
            return False

        #PS offset adjustment with curve calibration by linear regression
        if _ps_type == 3:
            _adjusted_setpoint = (_setpoint-0.0264)/1.0003
            Lib.comm.drs.set_slowref(_adjusted_setpoint)
        else:
            #send setpoint and wait until current is adjusted
            Lib.comm.drs.set_slowref(_setpoint)

        time.sleep(0.1)
        for _ in range(30):
            _compare = round(float(Lib.comm.drs.read_iload1()), 3)
            self.display_current(secondary)
            if abs(_compare - _setpoint) <= 0.5:
                Lib.write_value(_df, 'Current Setpoint', _setpoint, True)
                self.ui.tabWidget_2.setEnabled(True)
                return True
            QtWidgets.QApplication.processEvents()
            time.sleep(1)
        self.ui.tabWidget_2.setEnabled(True)
        return False

    def slew_rate(self, slew_rate, ps_type):
        """Changes power supply slew rate [A/s].

        Args:
            slew_rate: power supply slew rate;
            ps_type: power supply type.

        Returns:
            True if successful, False otherwise."""
        try:
            # power supply current slopes, [F1000A, F225A, F10A] [A/s]
            _slope_limits = [50, 90, 1000]
            if ps_type == 2:
                _limit = _slope_limits[0]
            if ps_type == 3:
                _limit = _slope_limits[1]
            if ps_type > 3:
                _QMessageBox.warning(self, 'Warning',
                                     "You can't modify F10's slew rate.",
                                     _QMessageBox.Ok)
                return False

            if not (0 < slew_rate <= _limit):
                _QMessageBox.warning(self, 'Warning',
                                     'Could not set the slew rate for it is'
                                     'out of bounds.\nUpper limits: 50 A/s, '
                                     '90 A/s and 1000 A/s for F1000, F225 and '
                                     'F10 respectively.',
                                     _QMessageBox.Ok)
                return False

            Lib.comm.drs.set_dsp_coeffs(1, 0, [slew_rate])
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            _QMessageBox.warning(self, 'Warning',
                                 'Could not set the slew rate properly.',
                                 _QMessageBox.Ok)
            return False

    def send_setpoint(self, secondary=False):
        """Changes power supply current setpoint from UI."""
        try:
            if not secondary:
                _setpoint = self.ui.dsb_current_setpoint.value()
            else:
                _setpoint = self.ui.dsb_current_setpoint_2.value()

            _ans = self.current_setpoint(_setpoint, secondary)

            if _ans:
                _QMessageBox.information(self, 'Information',
                                         'Current properly set.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Current was not properly set.',
                                     _QMessageBox.Ok)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def verify_current_limits(self, current, offset=0, chk_offset=False,
                              secondary=False):
        """Check the limits of the current values set.

        Args:
            current (float): current value in [A] to be verified.
            offset (float, optional): offset value in [A]; default 0.
            check_offset (bool, optional): flag to check current value plus
                offset; default False.
            secondary (bool, optional): flag indicating to check
                primary/secondary power supply
        Return:
            True if current is within the limits, False otherwise.
        """
        _current = float(current)
        _offset = float(offset)
        if not secondary:
            _df = Lib.ps_settings
        else:
            _df = Lib.ps_settings_2

        try:
            _current_max = Lib.get_value(_df, 'Maximum Current', float)
        except Exception:
            _QMessageBox.warning(self, 'Warning',
                                 'Invalid Maximum Current value.',
                                 _QMessageBox.Ok)
            return False
        try:
            _current_min = Lib.get_value(_df, 'Minimum Current', float)
        except Exception:
            _QMessageBox.warning(self, 'Warning',
                                 'Invalid Minimum Current value.',
                                 _QMessageBox.Ok)
            return False

        if not chk_offset:
            if _current > _current_max:
                _QMessageBox.warning(self, 'Warning',
                                     'Current value is too high.',
                                     _QMessageBox.Ok)
                self.ui.dsb_current_setpoint.setValue(float(_current_max))
                _current = _current_max
                return False
            if _current < _current_min:
                _QMessageBox.warning(self, 'Warning',
                                     'Current value is too low',
                                     _QMessageBox.Ok)
                self.ui.dsb_current_setpoint.setValue(float(_current_min))
                _current = _current_min
                return False
        else:
            if any([(_current + _offset) > _current_max,
                    (-1 * _current + _offset) < _current_min]):
                _QMessageBox.warning(self, 'Warning', 'Peak-to-peak '
                                     'current values out of bounds.',
                                     _QMessageBox.Ok)
                return False

        return True

    def send_curve(self, secondary=False):
        """Configures power supply curve generator from UI."""
        self.ui.tabWidget_2.setEnabled(False)
        if self.curve_gen(secondary) is True:
            self.ui.tabWidget_2.setEnabled(True)
            if not secondary:
                self.ui.pb_cycle.setEnabled(True)
            else:
                _curve_type = int(self.ui.tabWidget_5.currentIndex())
                if _curve_type == 2:
                    self.ui.pb_cycle_2.setEnabled(True)
                elif _curve_type == 3:
                    self.ui.pb_cycle_3.setEnabled(True)
                elif _curve_type == 4:
                    self.ui.pb_cycle_4.setEnabled(True)
            QtWidgets.QApplication.processEvents()
            _QMessageBox.information(self, 'Information',
                                     'Curve sent successfully.',
                                     _QMessageBox.Ok)
        else:
            _QMessageBox.warning(self, 'Warning', 'Failed to send curve.',
                                 _QMessageBox.Ok)
            self.ui.tabWidget_2.setEnabled(True)
            QtWidgets.QApplication.processEvents()
            return False

    def curve_gen(self, secondary=False):
        """Configures power supply curve generator."""
        if not secondary:
            if not self.config_ps():
                return False
            _curve_type = int(self.ui.tabWidget_3.currentIndex())
            _df = Lib.ps_settings
        else:
            if not self.config_ps_2():
                return False
            _curve_type = int(self.ui.tabWidget_5.currentIndex()) - 1
            _df = Lib.ps_settings_2

        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        if not self.set_address(_ps_type, secondary):
            return False

        # Sinusoidal
        if _curve_type == 0:
            try:
                _offset = Lib.get_value(_df, 'Sinusoidal Offset', float)
                if not self.verify_current_limits(0, _offset):
                    self.ui.le_Sinusoidal_Offset.setText('0')
                    Lib.write_value(_df, 'Sinusoidal Offset', 0)
                    return False
                self.ui.le_Sinusoidal_Offset.setText(str(_offset))
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Offset parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _amp = Lib.get_value(_df, 'Sinusoidal Amplitude', float)
                if not self.verify_current_limits(abs(_amp), _offset, True):
                    self.ui.le_Sinusoidal_Amplitude.setText('0')
                    Lib.write_value(_df, 'Sinusoidal Amplitude', 0)
                    return False
                self.ui.le_Sinusoidal_Amplitude.setText(str(_amp))
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Amplitude parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _freq = Lib.get_value(_df, 'Sinusoidal Frequency', float)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Frequency parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _n_cycles = Lib.get_value(_df, 'Sinusoidal N Cycles', int)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     '#cycles parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _phase_shift = Lib.get_value(_df, 'Sinusoidal Initial Phase',
                                             float)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Phase parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _final_phase = Lib.get_value(_df, 'Sinusoidal Final Phase',
                                             float)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Final phase parameter of the curve.',
                                     _QMessageBox.Ok)

        # Damped Sinusoidal (can be primary or secondary ps)
        if _curve_type in [1, 2]:
            if _curve_type == 1:
                _sin = 'Sinusoidal'
            else:
                _sin = 'Sinusoidal2'
            try:
                _offset = Lib.get_value(_df, 'Damped '+_sin+' Offset', float)
                if not self.verify_current_limits(0, _offset, False,
                                                  secondary):
                    Lib.write_value(_df, 'Damped '+_sin+' Offset', 0)
                    if not secondary:
                        self.ui.le_damp_sin_Offset.setText('0')
                    else:
                        self.ui.le_damp_sin_Offset_2.setText('0')
                    return False
                if not secondary:
                    self.ui.le_damp_sin_Offset.setText(str(_offset))
                else:
                    self.ui.le_damp_sin_Offset_2.setText(str(_offset))
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Offset parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _amp = Lib.get_value(_df, 'Damped '+_sin+' Amplitude', float)
                if not self.verify_current_limits(abs(_amp), _offset, True,
                                                  secondary):
                    Lib.write_value(_df, 'Damped '+_sin+' Amplitude', 0)
                    if not secondary:
                        self.ui.le_damp_sin_Ampl.setText('0')
                    else:
                        self.ui.le_damp_sin_Ampl_2.setText('0')
                    return False
                if not secondary:
                    self.ui.le_damp_sin_Ampl.setText(str(_amp))
                else:
                    self.ui.le_damp_sin_Ampl_2.setText(str(_amp))
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Amplitude parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _freq = Lib.get_value(_df, 'Damped '+_sin+' Frequency',
                                      float)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Frequency parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _n_cycles = Lib.get_value(_df, 'Damped '+_sin+' N Cycles',
                                          int)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     '#cycles parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _phase_shift = Lib.get_value(_df, 'Damped '+_sin+' Phase '
                                             'Shift', float)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Phase parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _final_phase = Lib.get_value(_df, 'Damped '+_sin+' Final '
                                             'Phase', float)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Final Phase parameter of the curve.',
                                     _QMessageBox.Ok)
            try:
                _damping = Lib.get_value(_df, 'Damped '+_sin+' Damping',
                                         float)
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please, verify the '
                                     'Damping time parameter of the curve.',
                                     _QMessageBox.Ok)

        #Generating curves
        try:
            if _curve_type < 3:
                try:
                    # Sinusoidal
                    if _curve_type == 0:
                        _sigtype = 0
                        _damping = 0
                    elif _curve_type in [1, 2]:
                        # Damped Sinusoidal
                        if _curve_type == 1:
                            _sigtype = 1
                        # Damped Sinusoidal^2
                        else:
                            _sigtype = 3
                    # Sending curves to PS Controller
                    Lib.comm.drs.cfg_siggen(_sigtype, _n_cycles, _freq,
                                            _amp, _offset, _phase_shift,
                                            _final_phase, _damping, 0)
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    _QMessageBox.warning(self, 'Warning', 'Failed to send '
                                         'configuration to the controller.\n'
                                         'Please, verify the parameters of the'
                                         ' Power Supply.',
                                         _QMessageBox.Ok)
                    return False
            return True
        except Exception:
            return False

    def reset_interlocks(self, secondary=False):
        """Resets power supply interlocks."""
        if not secondary:
            _df = Lib.ps_settings
        else:
            _df = Lib.ps_settings_2
        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        if not self.set_address(_ps_type, secondary):
            return
        _interlock = 0

        # 1000A power supply, reset capacitor bank interlock
        if _ps_type == 2:
            Lib.comm.drs.SetSlaveAdd(_ps_type)
            Lib.comm.drs.reset_interlocks()
            time.sleep(0.1)
            _interlock = _interlock + (Lib.comm.drs.read_ps_hardinterlocks() +
                                       Lib.comm.drs.read_ps_softinterlocks())

        Lib.comm.drs.SetSlaveAdd(_ps_type - 1)

        try:
            Lib.comm.drs.reset_interlocks()
            time.sleep(0.1)
            _interlock = _interlock + (Lib.comm.drs.read_ps_hardinterlocks() +
                                       Lib.comm.drs.read_ps_softinterlocks())
            if not secondary:
                if self.ui.pb_interlock.isChecked() and not _interlock:
                    self.ui.pb_interlock.setChecked(False)
            else:
                if self.ui.pb_interlock_2.isChecked() and not _interlock:
                    self.ui.pb_interlock_2.setChecked(False)
            if not _interlock:
                _QMessageBox.information(self, 'Information',
                                         'Interlocks reseted.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Interlocks could not be reseted.',
                                     _QMessageBox.Ok)
        except Exception:
            _QMessageBox.warning(self, 'Warning',
                                 'Interlocks could not be reseted.',
                                 _QMessageBox.Ok)
            return

    def list_interlocks(self, secondary=False):
        try:
            if not secondary:
                _df = Lib.ps_settings
            else:
                _df = Lib.ps_settings_2
            _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
            _msg = 'Power Supply active interlocks:\n\n'
            _lsoft = []
            _lhard = []

            if _ps_type == 2:
                # F1000, reads dclink and ps
                _msg = _msg + 'DCLink:\n'
                if not self.set_address(_ps_type - 1, secondary):
                    return
                _interlock = Lib.comm.drs.read_ps_softinterlocks()
                _lsoft = Lib.comm.drs.interlock_decoder(_interlock, _ps_type,
                                                        False)
                _interlock = Lib.comm.drs.read_ps_hardinterlocks()
                _lhard = Lib.comm.drs.interlock_decoder(_interlock, _ps_type,
                                                        True)
                _msg = _msg + 'Software Interlocks:\n'
                if not len(_lsoft):
                    _msg = _msg + '    None\n'
                else:
                    for _i in _lsoft:
                        _msg = _msg + '    - ' + _i + '\n'
                _msg = _msg + 'Hardware Interlocks:\n'
                if not len(_lhard):
                    _msg = _msg + '    None\n'
                else:
                    for _i in _lhard:
                        _msg = _msg + '    - ' + _i + '\n'
                _msg = _msg + '\nPower Supply:\n'
                _lsoft = []
                _lhard = []

            else:
                if not self.set_address(_ps_type, secondary):
                    return
                _interlock = Lib.comm.drs.read_ps_softinterlocks()
                _lsoft = Lib.comm.drs.interlock_decoder(_interlock, _ps_type,
                                                        False)
                _interlock = Lib.comm.drs.read_ps_hardinterlocks()
                _lhard = Lib.comm.drs.interlock_decoder(_interlock, _ps_type,
                                                        True)
            _msg = _msg + 'Soft Interlocks:\n'
            if not len(_lsoft):
                _msg = _msg + '    None\n'
            else:
                for _i in _lsoft:
                    _msg = _msg + '    - ' + _i + '\n'
            _msg = _msg + 'Hard Interlocks:\n'
            if not len(_lhard):
                _msg = _msg + '    None\n'
            else:
                for _i in _lhard:
                    _msg = _msg + '    - ' + _i + '\n'

            _QMessageBox.warning(self, 'Active Interlocks', _msg,
                                 _QMessageBox.Ok)
            QtWidgets.QApplication.processEvents()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def cycling_ps(self, secondary=False):
        """Cycles power supply curve generator."""
        if not secondary:
            _curve_type = int(self.ui.tabWidget_3.currentIndex())
            _df = Lib.ps_settings
            _pb = self.ui.pb_cycle
            self.ui.pb_load_ps.setEnabled(False)
            self.ui.pb_refresh.setEnabled(False)
        else:
            _curve_type = int(self.ui.tabWidget_5.currentIndex()) - 1
            _df = Lib.ps_settings_2
            if _curve_type == 1:
                _pb = self.ui.pb_cycle_2
            if _curve_type == 2:
                _pb = self.ui.pb_cycle_3
            if _curve_type == 3:
                _pb = self.ui.pb_cycle_4
        _pb.setText('Wait...')
        self.ui.tabWidget_2.setEnabled(False)
        self.ui.pb_start_meas.setEnabled(False)
        QtWidgets.QApplication.processEvents()

        _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
        if not self.set_address(_ps_type, secondary):
            return

        try:
            if _curve_type < 3:
                if not self.set_op_mode(1):
                    _QMessageBox.warning(self, 'Warning', 'Could not set '
                                         'the sigGen operation mode.\n'
                                         'Please check if it is turned on.',
                                         _QMessageBox.Ok)
                    raise Exception('Power supply is not in sigGen mode.')
            if _curve_type == 0:
                _freq = Lib.get_value(_df, 'Sinusoidal Frequency', float)
                _n_cycles = Lib.get_value(_df, 'Sinusoidal N Cycles', float)
                _offset = Lib.get_value(_df, 'Sinusoidal Offset', float)
            elif _curve_type == 1:
                _freq = Lib.get_value(_df, 'Damped Sinusoidal Frequency',
                                      float)
                _n_cycles = Lib.get_value(_df, 'Damped Sinusoidal N Cycles',
                                          float)
                _offset = Lib.get_value(_df, 'Damped Sinusoidal Offset', float)
            elif _curve_type == 2:
                _freq = Lib.get_value(_df, 'Damped Sinusoidal2 Frequency',
                                      float)
                _n_cycles = Lib.get_value(_df, 'Damped Sinusoidal2 N Cycles',
                                          float)
                _offset = Lib.get_value(_df, 'Damped Sinusoidal2 Offset',
                                        float)
            if _curve_type == 3:
                _offset = Lib.get_value(_df, 'Trapezoidal Offset', float)
                if not self.trapezoidal_cycle():
                    raise Exception('Failure during trapezoidal cycle.')
            else:
                Lib.comm.drs.enable_siggen()
                _t0 = time.monotonic()
                _deadline = _t0 + (1/_freq*_n_cycles)
                _prg_dialog = _QProgressDialog('Cycling Power Supply...',
                                               'Abort', _t0,
                                               _deadline + 0.3, self)
                _prg_dialog.setWindowTitle('SigGen')
                _prg_dialog.show()
                _abort_flag = False
                _t = time.monotonic()
                while _t < _deadline:
                    if _prg_dialog.wasCanceled():
                        _ans = _QMessageBox.question(self, 'Abort Cycling',
                                                     'Do you really want to '
                                                     'abort the cycle '
                                                     'process?',
                                                     (_QMessageBox.No |
                                                      _QMessageBox.Yes))
                        if _ans == _QMessageBox.Yes:
                            _abort_flag = True
                            break
                    _prg_dialog.setValue(_t)
                    QtWidgets.QApplication.processEvents()
                    time.sleep(0.01)
                    _t = time.monotonic()
                _prg_dialog.destroy()
                QtWidgets.QApplication.processEvents()
                time.sleep(0.1)
                Lib.comm.drs.disable_siggen()
                # returns to mode ISlowRef
                if not self.set_op_mode(0):
                    _QMessageBox.warning(self, 'Warning', 'Could not set '
                                         'the slowRef operation mode.',
                                         _QMessageBox.Ok)
                #Lib.comm.drs.set_slowref(_offset)
                Lib.comm.drs.set_slowref(0)
            Lib.write_value(_df, 'Current Setpoint', _offset, True)
            if _abort_flag:
                _QMessageBox.warning(self, 'Warning', 'The cycle process was '
                                     'aborted.', _QMessageBox.Ok)
            else:
                _QMessageBox.information(self, 'Information', 'Cycle process '
                                         'completed successfully.',
                                         _QMessageBox.Ok)
            self.display_current(secondary)
            self.ui.tabWidget_2.setEnabled(True)
            _pb.setText('Cycle')
            _pb.setEnabled(False)
            if not secondary:
                self.ui.pb_load_ps.setEnabled(True)
                self.ui.pb_refresh.setEnabled(True)
            self.ui.pb_start_meas.setEnabled(True)
            QtWidgets.QApplication.processEvents()
        except Exception:
            traceback.print_exc(file=sys.stdout)
            self.ui.tabWidget_2.setEnabled(True)
            _pb.setText('Cycle')
            _pb.setEnabled(False)
            if not secondary:
                self.ui.pb_load_ps.setEnabled(True)
                self.ui.pb_refresh.setEnabled(True)
            self.ui.pb_start_meas.setEnabled(True)
            QtWidgets.QApplication.processEvents()
            _QMessageBox.warning(self, 'Warning',
                                 'Cycling process was not performed properly.',
                                 _QMessageBox.Ok)
            return

    def trapezoidal_cycle(self, secondary=False):
        try:
            if not secondary:
                _df = Lib.ps_settings
            else:
                _df = Lib.ps_settings_2

            _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
            _offset = Lib.get_value(_df, 'Trapezoidal Offset', float)
            _array = Lib.get_value(_df, 'Trapezoidal Array')
            _array = np.fromstring(_array, sep=',')
            _array = _array.reshape(int(_array.shape[0]/2), 2)

            if not self.set_address(_ps_type, secondary):
                return False

            if _ps_type in [2, 3]:
                _slope = self.slope[_ps_type - 2]
            else:
                _slope = self.slope[-1]
            for i in range(len(_array)):
                if not self.verify_current_limits(_array[i, 0] + _offset):
                    return False

            Lib.comm.drs.set_slowref(_offset)
            for i in range(len(_array)):
                _i0 = _offset
                _i = _array[i, 0] + _offset
                _t = _array[i, 1]
                _t_border = abs(_i - _i0) / _slope
                Lib.comm.drs.set_slowref(_i)
                _deadline = time.monotonic() + _t_border + _t
                while time.monotonic() < _deadline:
                    QtWidgets.QApplication.processEvents()
                    time.sleep(0.01)
                Lib.comm.drs.set_slowref(_offset)
                _deadline = time.monotonic() + _t_border + _t
                while time.monotonic() < _deadline:
                    QtWidgets.QApplication.processEvents()
                    time.sleep(0.01)
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def plot(self, secondary=False):
        try:
            if not secondary:
                _tab_idx = self.ui.tabWidget_3.currentIndex()
                _df = Lib.ps_settings
            else:
                _tab_idx = self.ui.tabWidget_5.currentIndex() - 1
                _df = Lib.ps_settings_2
            # plot sinusoidal
            if _tab_idx == 0:
                a = float(self.ui.le_Sinusoidal_Amplitude.text())
                offset = float(self.ui.le_Sinusoidal_Offset.text())
                f = float(self.ui.le_Sinusoidal_Frequency.text())
                ncycles = int(self.ui.le_Sinusoidal_n_cycles.text())
                theta = float(self.ui.le_Initial_Phase.text())
                if any([a == 0, f == 0, ncycles == 0]):
                    _QMessageBox.warning(self, 'Warning',
                                         'Please check the parameters.',
                                         _QMessageBox.Ok)
                    return
                sen = lambda t: (a*np.sin(2*np.pi*f*t + theta/360*2*np.pi) +
                                 offset)
            # plot damped sinusoidal
            elif _tab_idx == 1:
                if not secondary:
                    a = float(self.ui.le_damp_sin_Ampl.text())
                    offset = float(self.ui.le_damp_sin_Offset.text())
                    f = float(self.ui.le_damp_sin_Freq.text())
                    ncycles = int(self.ui.le_damp_sin_nCycles.text())
                    theta = float(self.ui.le_damp_sin_phaseShift.text())
                    tau = float(self.ui.le_damp_sin_Damping.text())
                if secondary:
                    a = float(self.ui.le_damp_sin_Ampl_2.text())
                    offset = float(self.ui.le_damp_sin_Offset_2.text())
                    f = float(self.ui.le_damp_sin_Freq_2.text())
                    ncycles = int(self.ui.le_damp_sin_nCycles_2.text())
                    theta = float(self.ui.le_damp_sin_phaseShift_2.text())
                    tau = float(self.ui.le_damp_sin_Damping_2.text())
                if any([a == 0, f == 0, ncycles == 0, tau == 0]):
                    _QMessageBox.warning(self, 'Warning',
                                         'Please check the parameters.',
                                         _QMessageBox.Ok)
                    return
                sen = lambda t: (a*np.sin(2*np.pi*f*t + theta/360*2*np.pi) *
                                 np.exp(-t/tau) + offset)
            # plot damped sinusoidal^2
            elif _tab_idx == 2:
                if not secondary:
                    a = float(self.ui.le_damp_sin2_Ampl.text())
                    offset = float(self.ui.le_damp_sin2_Offset.text())
                    f = float(self.ui.le_damp_sin2_Freq.text())
                    ncycles = int(self.ui.le_damp_sin2_nCycles.text())
                    theta = float(self.ui.le_damp_sin2_phaseShift.text())
                    tau = float(self.ui.le_damp_sin2_Damping.text())
                if secondary:
                    a = float(self.ui.le_damp_sin2_Ampl_2.text())
                    offset = float(self.ui.le_damp_sin2_Offset_2.text())
                    f = float(self.ui.le_damp_sin2_Freq_2.text())
                    ncycles = int(self.ui.le_damp_sin2_nCycles_2.text())
                    theta = float(self.ui.le_damp_sin2_phaseShift_2.text())
                    tau = float(self.ui.le_damp_sin2_Damping_2.text())
                if any([a == 0, f == 0, ncycles == 0, tau == 0]):
                    _QMessageBox.warning(self, 'Warning',
                                         'Please check the parameters.',
                                         _QMessageBox.Ok)
                    return
                sen = lambda t: (a*np.sin(2*np.pi*f*t + theta/360*2*np.pi)*
                                 np.sin(2*np.pi*f*t + theta/360*2*np.pi)*
                                 np.exp(-t/tau) + offset)
            fig = self.plot_dialog.figure
            ax = self.plot_dialog.ax
            ax.clear()
            # plot trapezoidal
            if _tab_idx == 3:
                if _df is None:
                    _QMessageBox.warning(self, 'Warning',
                                         'Please configure the power supply.',
                                         _QMessageBox.Ok)
                    return
                _ps_type = Lib.get_value(_df, 'Power Supply Type', int)
                if _ps_type in [2, 3]:
                    _slope = self.slope[_ps_type - 2]
                else:
                    _slope = self.slope[2]
                if not secondary:
                    _offset = float(self.ui.le_trapezoidal_offset.text())
                    _array = self.table_to_array(self.ui.tw_trapezoidal)
                else:
                    _offset = float(self.ui.le_trapezoidal_offset_2.text())
                    _array = self.table_to_array(self.ui.tw_trapezoidal_2)
                _t0 = 0
                for i in range(len(_array)):
                    _i0 = _offset
                    _i = _array[i, 0] + _offset
                    _t = _array[i, 1]
                    _t_border = abs(_i - _i0) / _slope
                    ax.plot([_t0, _t0+_t_border], [_offset, _i], 'b-')
                    ax.plot([_t0+_t_border, _t0+_t_border+_t], [_i, _i], 'b-')
                    ax.plot([_t0+_t_border+_t, _t0+2*_t_border+_t],
                            [_i, _offset], 'b-')
                    ax.plot([_t0+2*_t_border+_t, _t0+2*(_t_border+_t)],
                            [_offset, _offset], 'b-')
                    _t0 = _t0+2*(_t_border+_t)
            else:
                x = np.linspace(0, ncycles/f, ncycles*20)
                y = sen(x)
                ax.plot(x, y)
            ax.set_xlabel('Time (s)', size=20)
            ax.set_ylabel('Current (I)', size=20)
            ax.grid('on', alpha=0.3)
            fig.tight_layout()
            self.plot_dialog.show()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def move_motor_until_stops(self, address, period):
        """Moves motor until it stops. The period plus 5 seconds is the
        timeout value.

        Args:
            address (int): driver address;
            period (float): time interval needed to complete the movement.

        Returns:
            True if successful, False otherwise."""
        Lib.flags.stop_all = False
        _stop_flag = False
        Lib.comm.parker.movemotor(address)
        time.sleep(0.05)
        _tf = time.monotonic() + period + 5
        while ((_stop_flag is False) and (Lib.flags.stop_all is False)):
            Lib.comm.parker.flushTxRx()
            if Lib.comm.parker.ready(address):
                _stop_flag = Lib.comm.parker.ready(address)
            QtWidgets.QApplication.processEvents()
            if time.monotonic() > _tf:
                break
            time.sleep(0.01)
        return _stop_flag

    def move_motor_manual(self):
        """Moves motor according to UI Motor tab configurations."""
        _address = Lib.get_value(Lib.data_settings, 'rotation_motor_address',
                                 int)
        _ratio = Lib.get_value(Lib.data_settings, 'rotation_motor_ratio',
                               float)

        _resolution = Lib.get_value(Lib.data_settings,
                                    'rotation_motor_resolution', int)
        _vel = float(self.ui.le_motor_vel.text()) * _ratio
        _acce = float(self.ui.le_motor_ace.text()) * _ratio
        _nturns = float(self.ui.le_motor_turns.text()) * _ratio
        _period = _nturns / _vel

        _direction = self.ui.cb_driver_direction.currentIndex()
        _steps = abs(int(_nturns * Lib.get_value(Lib.data_settings,
                                                 'rotation_motor_resolution',
                                                 float)))

        # mode
        if self.ui.cb_driver_mode.currentIndex() == 0:
            _mode = 0
        else:
            _mode = 1

        Lib.comm.parker.conf_motor(_address, _resolution, _vel, _acce, _steps,
                                   _direction, _mode)

        self.move_motor_until_stops(_address, _period)

    def stop_motor(self):
        """Stops motor."""
        Lib.flags.stop_all = True
        _address = Lib.get_value(Lib.data_settings, 'rotation_motor_address',
                                 int)
        Lib.comm.parker.stopmotor(_address)

    def encoder_reading(self):
        """Read encoder from integrator and update UI value"""
        _val = Lib.comm.fdi.read_encoder()
        self.ui.le_encoder_reading.setText(_val)

    def pulses_to_go(self):
        """Computes number of pulses to the desired encoder position."""
        self.encoder_reading()
        _encoder_current = int(self.ui.le_encoder_reading.text())
        _encoder_setpoint = int(self.ui.le_encoder_setpoint.text())
        _pulses_to_go = _encoder_setpoint - _encoder_current

        return _pulses_to_go

    def move_to_encoder_position(self):
        """Moves motor to the configured encoder position."""
        Lib.flags.stop_all = False

        _address = Lib.get_value(Lib.data_settings, 'rotation_motor_address',
                                 int)
        _ratio = Lib.get_value(Lib.data_settings, 'rotation_motor_ratio',
                               float)

        _resolution = Lib.get_value(Lib.data_settings,
                                    'rotation_motor_resolution', int)
        _vel = float(self.ui.le_motor_vel.text()) * _ratio
        _acce = float(self.ui.le_motor_ace.text()) * _ratio

        #Direction
        try:
            if Lib.get_value(Lib.measurement_settings,
                             'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except Exception:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()

        # _encoder_pulse = 360000
        _encoder_pulse = Lib.get_value(Lib.data_settings, 'n_encoder_pulses',
                                       int)

        _pulses = self.pulses_to_go()
        if _pulses > 0 and _direction == 0:
            _pulses = _encoder_pulse - _pulses
        elif _pulses < 0 and _direction == 1:
            _pulses = _encoder_pulse - _pulses
        _steps = abs(int(_pulses *
                         Lib.get_value(Lib.data_settings,
                                       'rotation_motor_resolution', int) /
                         Lib.get_value(Lib.data_settings,
                                       'n_encoder_pulses', int) * _ratio))
        _nturns = _steps / Lib.get_value(Lib.data_settings,
                                         'rotation_motor_resolution', int)
        _period = _nturns / _vel

        Lib.comm.parker.conf_motor(_address, _resolution, _vel, _acce, _steps,
                                   _direction, 0)
        self.move_motor_until_stops(_address, _period)

        self.encoder_reading()

    def config_integrator(self):
        """Configures integrator."""
        self.config_variables()
        _n_encoder_pulses = int(Lib.get_value(Lib.data_settings,
                                              'n_encoder_pulses', float))
        Lib.comm.fdi.config_encoder(int(_n_encoder_pulses/4))
        # finds encoder index
        self.move_motor_measurement(1)
        self.ui.lb_status_integrator.setText('OK')
        _QMessageBox.information(self, 'Information', 'Integrator configured.',
                                 _QMessageBox.Ok)

    def status_update(self):
        """Updates integrator status on UI."""
        try:
            self.ui.label_status_1.setText(Lib.comm.fdi.status(0))
            self.ui.label_status_2.setText(Lib.comm.fdi.status(1))
            self.ui.label_status_3.setText(Lib.comm.fdi.status(2))
            self.ui.label_status_4.setText(Lib.comm.fdi.status(3))
        except Exception:
            pass

    def move_motor_measurement(self, turns):
        """Moves motor according to measurement configurations."""
        _address = Lib.get_value(Lib.data_settings, 'rotation_motor_address',
                                 int)
        _ratio = Lib.get_value(Lib.data_settings, 'rotation_motor_ratio',
                               float)

        _resolution = Lib.get_value(Lib.data_settings,
                                    'rotation_motor_resolution', int)
        _vel = Lib.get_value(Lib.data_settings, 'rotation_motor_speed',
                             float) * _ratio
        _acce = Lib.get_value(Lib.data_settings, 'rotation_motor_acceleration',
                              float) * _ratio
        _nturns = turns * _ratio
        _period = _nturns / _vel

        try:
            if Lib.get_value(Lib.measurement_settings,
                             'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except Exception:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()

        _steps = abs(int(_nturns * Lib.get_value(Lib.data_settings,
                                                 'rotation_motor_resolution',
                                                 float)))

        _mode = 0

        Lib.comm.parker.conf_motor(_address, _resolution, _vel, _acce, _steps,
                                   _direction, _mode)

        self.move_motor_until_stops(_address, _period)

    def load_coil(self):
        """Loads coil configuration from file."""
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,
                                                             'Load Coil File',
                                                             Lib.dir_path +
                                                             '\Config\Coils\\',
                                                             'Data files '
                                                             '(*.dat);;Text '
                                                             'files (*.txt)')
            if Lib.load_coil(filename[0]) is True:
                if self.refresh_coiltab():
                    _QMessageBox.information(self, 'Information',
                                             'Coil File loaded.',
                                             _QMessageBox.Ok)
                    #If OK
                    self.ui.lb_status_coil.setText('OK')
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Failed to load Coil File.',
                                     _QMessageBox.Ok)
                self.ui.lb_status_coil.setText('NOK')

        except Exception:
            return

    def save_coil(self):
        """Saves coil configuration file."""
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self,
                                                             'Save Coil File',
                                                             Lib.dir_path +
                                                             '\Config\Coils\\',
                                                             'Data files '
                                                             '(*.dat);;Text '
                                                             'files (*.txt)')

            self.config_coil()

            if Lib.save_coil(filename[0]) is True:
                _QMessageBox.information(self, 'Information',
                                         'Coil File saved.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Failed to save Coil File.',
                                     _QMessageBox.Ok)
        except Exception:
            return

    def save_PowerSupply(self, secondary=False):
        """Saves Power Supply configuration file."""
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Power'
                                                             ' Supply File',
                                                             Lib.dir_path +
                                                             '\Config\Power '
                                                             'Supplies\\',
                                                             'Data files '
                                                             '(*.dat);;Text '
                                                             'files (*.txt)')

            if not secondary:
                self.config_ps()
                _ans = Lib.save_ps(filename[0])
            else:
                self.config_ps_2()
                _ans = Lib.save_ps(filename[0], secondary=True)
            if _ans:
                _QMessageBox.information(self, 'Information',
                                         'Power Supply File saved.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Failed to save Power Supply File.',
                                     _QMessageBox.Ok)
        except Exception:
            return

    def load_PowerSupply(self, secondary=False):
        """Loads Power Supply configuration from file."""
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,
                                                             'Load Power '
                                                             'Supply File',
                                                             Lib.dir_path +
                                                             '\Config\Power '
                                                             'Supplies\\',
                                                             'Data files '
                                                             '(*.dat);;Text '
                                                             'files (*.txt)')
            if not secondary:
                _ans = Lib.load_ps(filename[0])
            else:
                _ans = Lib.load_ps(filename[0], secondary=True)
            if _ans is True:
                if not secondary:
                    self.refresh_ps_settings()
                    self.ui.gb_start_supply.setEnabled(True)
                    self.ui.pb_ps_button.setEnabled(True)
                    self.ui.le_status_loop.setEnabled(True)
                    self.ui.label_32.setEnabled(True)
                    self.ui.pb_refresh.setEnabled(True)
                else:
                    self.refresh_ps_settings_2()
                    self.ui.gb_start_supply_2.setEnabled(True)
                    self.ui.pb_ps_button_2.setEnabled(True)
                    self.ui.le_status_loop_2.setEnabled(True)
                    self.ui.label_37.setEnabled(True)
                    self.ui.pb_refresh_2.setEnabled(True)
                self.ui.tabWidget_2.setEnabled(True)
                self.ui.tabWidget_3.setEnabled(True)
                _QMessageBox.information(self, 'Information',
                                         'Power Supply File loaded.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Failed to load Power Supply File.',
                                     _QMessageBox.Ok)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            _QMessageBox.warning(self, 'Warning', 'Could not load the power '
                                 'supply settings.\nCheck if the configuration'
                                 ' file values are correct.',
                                 _QMessageBox.Ok)

    def start_meas(self):
        """Starts a measurement."""
        try:
            Lib.flags.stop_all = False
            Lib.flags.emergency = False
            self.ui.pb_start_meas.setEnabled(False)
            self.ui.le_n_collections.setEnabled(False)
            self.ui.tabWidget.setTabEnabled(5, False)
            self.ui.tabWidget_2.setEnabled(False)
            self.ui.chb_automatic_ps.setEnabled(False)
            self.ui.pb_refresh.setEnabled(False)
            self.ui.groupBox_5.setEnabled(False)
            QtWidgets.QApplication.processEvents()
            _save_flag = False

            self.ui.lb_meas_counter.setText('{0:04}'.format(0))
            QtWidgets.QApplication.processEvents()

            if self.ui.chb_seriesofmeas.isChecked():
                _n_collections = Lib.get_value(Lib.measurement_settings,
                                               'n_collections', int)
            else:
                _n_collections = 1

            if self.ui.chb_automatic_ps.isChecked():
                if Lib.get_value(Lib.data_settings, 'disable_ps_interlock',
                                 int):
                    _ans = _QMessageBox.question(self,
                                                 'Automatic Power Supply',
                                                 'The power supply interlock '
                                                 'is disabled.\nDo you want to'
                                                 ' continue this measurement '
                                                 'with no guarantee that the '
                                                 'power supply is working '
                                                 'properly?',
                                                 _QMessageBox.Yes |
                                                 _QMessageBox.No,
                                                 _QMessageBox.No)
                    if _ans == _QMessageBox.No:
                        raise Exception
                #load array
                if self.ui.rb_main_ps.isChecked():
                    _current_array = Lib.get_value(Lib.ps_settings,
                                                   'Automatic Setpoints')
                    _secondary = False
                else:
                    if Lib.ps_settings_2 is None:
                        _QMessageBox.warning(self, 'Warning',
                                             'Please configure the secondary '
                                             'power supply.',
                                             _QMessageBox.Ok)
                        raise Exception
                    _current_array = Lib.get_value(Lib.ps_settings_2,
                                                   'Automatic Setpoints')
                    _secondary = True
                _current_array = np.asarray(_current_array.split(', '),
                                            dtype=float)
                #set n_collections
                _n_collections = _current_array.shape[0]

            # Asks whether to save each measurement to file or not
            if _n_collections > 1:
                _ans = _QMessageBox.question(self, 'Save logs', 'Do you want '
                                             'to save each measurement log '
                                             'to file?',
                                             _QMessageBox.Yes |
                                             _QMessageBox.No)
                if _ans == _QMessageBox.Yes:
                    _dir = QtWidgets.QFileDialog.getExistingDirectory(
                        self, 'Save Directory', Lib.dir_path)
                    _dir = _dir.replace('/', '\\\\') + '\\\\'
                    _save_flag = True

            # data array
            self.data_array = np.array([])
            self.df_rawcurves = None

            # configure integrator
            if not self.configure_integrator():
                _QMessageBox.warning(self, 'Warning',
                                     'Could not configure the integrator.',
                                     _QMessageBox.Ok)
                raise Exception

            # check system components
            self.collect_infocomponents()

            #Begin loop for n_collections
            for i in range(_n_collections):
                #change current if automatic adjust is enabled
                if self.ui.chb_automatic_ps.isChecked():
                    _ans = self.current_setpoint(_current_array[i], _secondary)
                    #*Change suggested by James*: Increase time sleep to wait
                    #Power Supply stabilization
                    time.sleep(4)
                    if not _ans:
                        Lib.db_save_failure(6)
                        _QMessageBox.warning(self, 'Warning',
                                             'Current was not properly set.',
                                             _QMessageBox.Ok)
                        raise Exception

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
                    raise Exception

                # saves measurement to log file
                if _save_flag:
                    _ans = Lib.save_log_file(path=_dir)
                    if not _ans:
                        _ans = _QMessageBox.question(self, 'Warning',
                                                     'Failed to save log file.'
                                                     '\nContinue measurements '
                                                     'anyway?',
                                                     _QMessageBox.Yes |
                                                     _QMessageBox.No)
                        if _ans == _QMessageBox.No:
                            Lib.db_save_failure(5)
                            raise Exception

                #checks standard deviation
                _ans = self.check_std()
                if not _ans:
                    Lib.db_save_failure(1)
                    _ans = _QMessageBox.question(self, 'Warning',
                                                 'Standard deviation '
                                                 'too high.\nContinue'
                                                 ' measurement anyway?',
                                                 _QMessageBox.Yes |
                                                 _QMessageBox.No)
                    if _ans == _QMessageBox.No:
                        raise Exception

                self.ui.lb_meas_counter.setText('{0:04}'.format(i+1))
                self.ui.tabWidget.setTabEnabled(7, True)
                QtWidgets.QApplication.processEvents()

                if Lib.flags.stop_all:
                    raise Exception
            #End loop for n_collections

            #Saves data to set_of_collections table if a set of measurements
            # was successfull
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
                    _current_min = Lib.get_value(Lib.ps_settings,
                                                 'Current Setpoint', float)
                    _current_max = _current_min
                if not Lib.db_save_set(_n_collections, _type, _current_min,
                                       _current_max):
                    raise Exception

            #Set current to zero after measurement
            if self.ui.chb_clear_current.isChecked():
                if self.ui.chb_automatic_ps.isChecked():
                    self.current_setpoint(0, _secondary)
                else:
                    self.current_setpoint(0, False)

            #Move coil to assembly position after measurement
            self.ui.le_encoder_setpoint.setText(Lib.get_value(
                Lib.coil_settings, 'trigger_ref', str))
            self.move_to_encoder_position()

            if Lib.flags.stop_all is False:
                _QMessageBox.information(self, 'Information',
                                         'Measurement completed.',
                                         _QMessageBox.Ok)
            else:
                _QMessageBox.information(self, 'Information', 'Failure during '
                                         'measurement.',
                                         _QMessageBox.Ok)

            self.ui.pb_start_meas.setEnabled(True)
            self.ui.le_n_collections.setEnabled(True)
            Lib.App.myapp.ui.tabWidget.setTabEnabled(5, True)
            self.ui.groupBox_5.setEnabled(True)
            self.ui.tabWidget_2.setEnabled(True)
            self.ui.chb_automatic_ps.setEnabled(True)
            self.ui.pb_refresh.setEnabled(True)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            if self.ui.chb_clear_current.isChecked():
                # sets main current to zero
                self.current_setpoint(0, False)
            _QMessageBox.warning(self, 'Warning', 'Measurement failed.',
                                 _QMessageBox.Ok)
            self.ui.pb_start_meas.setEnabled(True)
            self.ui.le_n_collections.setEnabled(True)
            Lib.App.myapp.ui.tabWidget.setTabEnabled(5, True)
            self.ui.groupBox_5.setEnabled(True)
            self.ui.tabWidget_2.setEnabled(True)
            self.ui.chb_automatic_ps.setEnabled(True)
            self.ui.pb_refresh.setEnabled(True)

    def misalignment(self):
        """Check misalignment with ND780 before measurement."""
        try:
            Lib.comm.display.readdisplay_ND780()
            time.sleep(0.3)
            _disp_pos = Lib.comm.display.DisplayPos
            Lib.write_value(Lib.aux_settings, 'ref_encoder_A', _disp_pos[0],
                            True)
            Lib.write_value(Lib.aux_settings, 'ref_encoder_B', _disp_pos[1],
                            True)
            if Lib.get_value(Lib.data_settings, 'disable_alignment_interlock',
                             int):
                return True
            else:
                if any([abs(Lib.get_value(Lib.aux_settings, 'ref_encoder_A',
                                          float)) > 0.005,
                        abs(Lib.get_value(Lib.aux_settings, 'ref_encoder_B',
                                          float)) > 0.005]):
                    return False
                else:
                    return True
        except Exception:
            return False

    def collect_infocomponents(self):
        """Setup verification routines before measurement."""
        _address = Lib.get_value(Lib.data_settings, 'rotation_motor_address',
                                 int)
        try:
            if not Lib.get_value(Lib.data_settings,
                                 'disable_alignment_interlock', int):
                if self.misalignment():
                    pass
                else:
                    raise Exception
            else:
                _ans = _QMessageBox.question(self, 'Attention', 'Do you want '
                                             'start measurement with '
                                             'alignment interlock disabled?',
                                             _QMessageBox.Yes |
                                             _QMessageBox.No,
                                             _QMessageBox.No)
                if _ans == _QMessageBox.No:
                    self.ui.chb_disable_alignment_interlock.setChecked(False)
                    self.config_variables()
                    raise Exception
        except Exception:
            _QMessageBox.warning(self, 'Warning', 'Stages alignment failed.',
                                 _QMessageBox.Ok)
            raise Exception

        if not Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int):
            if not Lib.get_value(Lib.aux_settings, 'status_ps', int):
                _QMessageBox.warning(self, 'Warning',
                                     'Power supply is not ready.',
                                     _QMessageBox.Ok)
                raise Exception
            if self.ui.lb_status_ps.text() == 'NOK':
                _QMessageBox.warning(self, 'Warning', 'Power supply is not '
                                     'ready.\nVerify power supply data.',
                                     _QMessageBox.Ok)
                raise Exception
        else:
            pass  # AQUI
            # _ans = _QMessageBox.question(self, 'Attention', 'Do you want start'
            #                              ' measurement with power supply '
            #                              'interlock disabled?',
            #                              _QMessageBox.Yes |
            #                              _QMessageBox.No,
            #                              _QMessageBox.No)
            # if _ans == _QMessageBox.No:
            #     self.ui.chb_disable_ps_interlock.setChecked(False)
            #     self.config_variables()
            #     raise Exception
        if self.ui.lb_status_coil.text() == 'NOK':
            _QMessageBox.warning(self, 'Warning',
                                 'Please, load the coil data.',
                                 _QMessageBox.Ok)
            raise Exception
        if self.ui.lb_status_integrator.text() == 'NOK':
            _QMessageBox.warning(self, 'Warning',
                                 'Please, configure the Integrator FDI 2056.\n'
                                 'Press "Configure Integrator" button.',
                                 _QMessageBox.Ok)
            raise Exception

        _i = Lib.get_value(Lib.data_settings, 'remove_initial_turns', int)
        _f = Lib.get_value(Lib.data_settings, 'remove_final_turns', int)
        _n = Lib.get_value(Lib.data_settings, 'total_number_of_turns', int)
        if _i + _f >= _n:
            _ans = _QMessageBox.question(self, 'Discard turns error',
                                         'Number of discarded turns is greater'
                                         ' than the total number of turns.\n'
                                         'Would you like to continue the '
                                         'measurement anyway?',
                                         _QMessageBox.No |
                                         _QMessageBox.Yes,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                raise Exception

        if Lib.comm.parker.limits(_address):
            _QMessageBox.warning(self, 'Warning', 'No compressed air flux.',
                                 _QMessageBox.Ok)
            Lib.db_save_failure(7)
            raise Exception

    def coil_position_correction(self):
        """Before start measurement, keep coil in ref trigger + half turn."""
        self.config_coil()
        _velocity = Lib.get_value(Lib.data_settings, 'rotation_motor_speed',
                                  int)
        _acceleration = Lib.get_value(Lib.data_settings,
                                      'rotation_motor_acceleration', int)
        _trigger = Lib.get_value(Lib.coil_settings, 'trigger_ref', int)
        # 360000
        _encoder_pulse = Lib.get_value(Lib.data_settings, 'n_encoder_pulses',
                                       int)
        _address_motor = Lib.get_value(Lib.data_settings,
                                       'rotation_motor_address', int)
        _rotation_motor_resolution = Lib.get_value(Lib.data_settings,
                                                   'rotation_motor_resolution',
                                                   int)
        _encoder_pos = int(Lib.comm.fdi.read_encoder())
        #Direction
        try:
            if Lib.get_value(Lib.measurement_settings,
                             'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except Exception:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()

        _position = _trigger + (_encoder_pulse / 2)
        if _position > _encoder_pulse:
            _position = _position - _encoder_pulse

        _shift = _position - _encoder_pos
        if _shift > 0 and _direction == 0:
            _shift = _encoder_pulse - _shift
        elif _shift < 0 and _direction == 1:
            _shift = _encoder_pulse - _shift

        # /10000
        _steps = int(_rotation_motor_resolution*abs(_shift)/_encoder_pulse)
        _nturns = _steps / Lib.get_value(Lib.data_settings,
                                         'rotation_motor_resolution', int)
        _period = _nturns / _velocity

        Lib.comm.parker.conf_motor(_address_motor, _rotation_motor_resolution,
                                   _velocity, _acceleration, _steps,
                                   _direction, mode=0)
        self.move_motor_until_stops(_address_motor, _period)

    def multipoles_normalization(self):
        """Normalizes multipoles."""
        _magnet_model = Lib.get_value(Lib.measurement_settings, 'magnet_model',
                                      int)

        r_ref = Lib.get_value(Lib.measurement_settings, 'norm_radius', float)
        n_ref = _magnet_model
        i_ref = self.df_norm_multipoles.index.values

        # Skew magnet normalization
        if _magnet_model in [4, 5]:
            # skew quadrupole
            if _magnet_model == 4:
                n_ref = 2
            # skew dipole (CV)
            elif _magnet_model == 5:
                n_ref = 1
            self.df_norm_multipoles_norm = (
                self.df_norm_multipoles /
                self.df_skew_multipoles.iloc[n_ref-1, :])
            self.df_skew_multipoles_norm = (
                self.df_skew_multipoles /
                self.df_skew_multipoles.iloc[n_ref-1, :])

            for i in range(len(self.df_norm_multipoles_norm.columns)):
                self.df_norm_multipoles_norm.iloc[:, i] = (
                    self.df_norm_multipoles_norm.iloc[:, i] *
                    (r_ref**(i_ref-n_ref)))
                self.df_skew_multipoles_norm.iloc[:, i] = (
                    self.df_skew_multipoles_norm.iloc[:, i] *
                    (r_ref**(i_ref-n_ref)))

            self.averageN_norm = self.df_norm_multipoles_norm.mean(axis=1)
            self.stdN_norm = 1/abs(self.averageS.values[n_ref-1]) * np.sqrt(self.stdN**2 + (self.stdS.values[n_ref-1]**2)*(self.averageN**2)/(self.averageS.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            self.averageS_norm = self.df_skew_multipoles_norm.mean(axis=1)
            self.stdS_norm = 1/abs(self.averageS.values[n_ref-1]) * np.sqrt(self.stdS**2 + (self.stdS.values[n_ref-1]**2)*(self.averageS**2)/(self.averageS.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))

        # Normal magnet normalization
        else:
            # considers normal dipole normalizing "no model" or "CH" magnet
            if n_ref in [0, 6]:
                n_ref = 1
            self.df_norm_multipoles_norm = (
                self.df_norm_multipoles /
                self.df_norm_multipoles.iloc[n_ref-1, :])
            self.df_skew_multipoles_norm = (
                self.df_skew_multipoles /
                self.df_norm_multipoles.iloc[n_ref-1, :])

            for i in range(len(self.df_norm_multipoles_norm.columns)):
                self.df_norm_multipoles_norm.iloc[:,i] = self.df_norm_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))
                self.df_skew_multipoles_norm.iloc[:,i] = self.df_skew_multipoles_norm.iloc[:,i] * (r_ref**(i_ref-n_ref))

            self.averageN_norm = self.df_norm_multipoles_norm.mean(axis=1)
            self.stdN_norm = 1/abs(self.averageN.values[n_ref-1]) * np.sqrt(self.stdN**2 + (self.stdN.values[n_ref-1]**2)*(self.averageN**2)/(self.averageN.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))
            self.averageS_norm = self.df_skew_multipoles_norm.mean(axis=1)
            self.stdS_norm = 1/abs(self.averageN.values[n_ref-1]) * np.sqrt(self.stdS**2 + (self.stdN.values[n_ref-1]**2)*(self.averageS**2)/(self.averageN.values[n_ref-1]**2)) * (r_ref**(i_ref-n_ref))

    def popup_meas(self):
        """Opens measurement configuration popup."""
        try:
            self.dialog = QtWidgets.QDialog()
            self.dialog.ui = Ui_Pop_Up()
            self.dialog.ui.setupUi(self.dialog)
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)

            if Lib.measurement_settings is not None:
                self.dialog.ui.le_magnet_name.setText(
                    Lib.get_value(Lib.measurement_settings, 'name', str))
                self.dialog.ui.cb_operator.setCurrentText(
                    Lib.get_value(Lib.measurement_settings, 'operator', str))
                self.dialog.ui.cb_magnet_model.setCurrentIndex(
                    Lib.get_value(Lib.measurement_settings, 'magnet_model',
                                  int))
                _magnet_name = Lib.get_value(Lib.measurement_settings, 'name',
                                             str)
                _magnet_family = Lib.get_value(Lib.measurement_settings,
                                               'magnet_family', str)
                if 'Q20' in _magnet_name or 'S15' in _magnet_name:
                    self.family_enable()
                if _magnet_family is None:
                    self.dialog.ui.cb_magnet_family.setCurrentText('None')
                else:
                    self.dialog.ui.cb_magnet_family.setCurrentText(
                        _magnet_family)
                _trim_type = Lib.get_value(Lib.measurement_settings,
                                           'trim_coil_type', int)
                if _trim_type >= 0:
                    self.dialog.ui.cb_trim_coil_type.setCurrentIndex(
                        _trim_type)

            if Lib.get_value(Lib.aux_settings, 'status_ps_2', int):
                self.dialog.ui.cb_trim_coil_type.setEnabled(True)
            self.dialog.ui.bB_ok_cancel.accepted.connect(self.ok_popup)
            self.dialog.ui.bB_ok_cancel.rejected.connect(self.cancel_popup)
            self.dialog.ui.le_magnet_name.textChanged.connect(
                self.family_enable)
            if Lib.get_value(Lib.data_settings, 'enable_Agilent34970A', int):
                _agilent_reading = Lib.comm.agilent34970a.read_temp_volt()
                _temp = _agilent_reading[0]
                setattr(self, 'temperature_magnet', _agilent_reading[1])
                setattr(self, 'temperature_water', _agilent_reading[2])
                self.dialog.ui.le_temperature.setText(str(round(float(_temp),
                                                                2)))
            self.dialog.exec_()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def ok_popup(self):
        """Configures software with popup settings."""
        try:
            Lib.measurement_df()
        except Exception:
            _QMessageBox.warning(self, 'Warning', 'Please check if all '
                                 'the inputs are properly set.',
                                 _QMessageBox.Ok)
            return
        if Lib.get_value(Lib.aux_settings, 'status_ps_2', int):
            _trim_type = self.dialog.ui.cb_trim_coil_type.currentIndex()
        else:
            _trim_type = -1
        Lib.write_value(Lib.measurement_settings, 'trim_coil_type', _trim_type)
        self.dialog.done(1)
        self.start_meas()

    def cancel_popup(self):
        """Deletes popup."""
        self.dialog.deleteLater()

    def family_enable(self):
        """Checks whether to enable magnet family combobox."""
        _magnet_name = self.dialog.ui.le_magnet_name.text().upper()
        _count = self.dialog.ui.cb_magnet_family.count()
        _l = ['Q20', 'S15']
        _ans = [item in _magnet_name for item in _l]
        if any(_ans):
            if _ans[0]:
                _family_list = ['1', '2/3', '4', '5']
                _c = 5
            elif _ans[1]:
                _family_list = ['1', '2']
                _c = 3
            self.dialog.ui.cb_magnet_family.setEnabled(True)
            if _count == _c:
                pass
            elif _count > 1:
                while _count > 1:
                    self.dialog.ui.cb_magnet_family.removeItem(1)
                    _count = _count - 1
                for _item in _family_list:
                    self.dialog.ui.cb_magnet_family.addItem(_item)
        else:
            self.dialog.ui.cb_magnet_family.setEnabled(False)
            self.dialog.ui.cb_magnet_family.setCurrentText('None')

    def multipoles_calculation(self):
        """Computes magnet multipoles."""
        _nmax = 15
        _n_of_turns = self.df_rawcurves.shape[1]
        _n_integration_points = Lib.get_value(Lib.data_settings,
                                              'n_integration_points', int)

        _coil_type = Lib.get_value(Lib.coil_settings, 'coil_type', str)
        if _coil_type == 'Radial':
            _coil_type = 0
        else:
            _coil_type = 1
        _n_coil_turns = Lib.get_value(Lib.coil_settings, 'n_turns_normal', int)
        _radius1 = Lib.get_value(Lib.coil_settings, 'radius1_normal', float)
        _radius2 = Lib.get_value(Lib.coil_settings, 'radius2_normal', float)
        _magnet_model = Lib.get_value(Lib.measurement_settings, 'magnet_model',
                                      int)

        self.df_norm_multipoles = pd.DataFrame(index=range(1, _nmax+1),
                                               columns=range(_n_of_turns))
        self.df_skew_multipoles = pd.DataFrame(index=range(1, _nmax+1),
                                               columns=range(_n_of_turns))

        dtheta = 2*np.pi/_n_integration_points

        #Radial coil calculation:
        if _coil_type == 0:
            for i in range(_n_of_turns):
                for n in range(1, _nmax+1):
                    anl = self.df_fft[i].real[n]
                    bnl = -self.df_fft[i].imag[n]

                    an = (anl*np.sin(dtheta*n) + bnl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius2**n - _radius1**n)/n)*(np.cos(dtheta*n)-1)) 
                    bn = (bnl*np.sin(dtheta*n) - anl*(np.cos(dtheta*n)-1)) / (2*(_n_coil_turns*(_radius2**n - _radius1**n)/n)*(np.cos(dtheta*n)-1))        

                    self.df_norm_multipoles.iloc[n-1, i] = bn
                    self.df_skew_multipoles.iloc[n-1, i] = an

        #Tangential coil calculation:
        if _coil_type == 1:
            _radiusDelta = _radius1*np.pi/180
            for i in range(_n_of_turns):
                for n in range(1, _nmax+1):
                    anl = self.df_fft[i].real[n]
                    bnl = -self.df_fft[i].imag[n]

                    an = n * (_radius2**(-n)) * ((anl)*(np.cos(n*dtheta)-1) - bnl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))
                    bn = n * (_radius2**(-n)) * ((bnl)*(np.cos(n*dtheta)-1) + anl*np.sin(n*dtheta)) / (4*_n_coil_turns*(np.cos(n*dtheta)-1)*np.sin(_radiusDelta*n/2))

                    self.df_norm_multipoles.iloc[n-1, i] = bn
                    self.df_skew_multipoles.iloc[n-1, i] = an

        self.averageN = self.df_norm_multipoles.mean(axis=1)
        self.stdN = self.df_norm_multipoles.std(axis=1)
        self.averageS = self.df_skew_multipoles.mean(axis=1)
        self.stdS = self.df_skew_multipoles.std(axis=1)
        self.averageMod = np.sqrt(self.averageN**2 + self.averageS**2)
        # error propagation
        self.stdMod = np.sqrt(self.averageN**2*self.stdN**2 + self.averageS**2*self.stdS**2) / (self.averageMod)
        # Angle calculation for skew magnet
        if _magnet_model in [4, 5]:
            self.averageAngle = (1/self.averageN.index) * np.arctan(self.averageN/self.averageS)
        # Angle calculation for normal magnet
        else:
            self.averageAngle = (1/self.averageN.index) * np.arctan(self.averageS/self.averageN)
        self.stdAngle = (1/self.averageN.index) * 1/(self.averageN**2 + self.averageS**2) * np.sqrt(self.averageS**2 * self.stdN**2 + self.averageN**2 * self.stdS**2) #error propagation is equal for normal and skew magnets

    def main_harmonic(self):
        """Returns main harmonic from least measurement or NAN if no
        measurement was found."""
        if Lib.measurement_settings is not None:
            _n_ref = Lib.get_value(Lib.measurement_settings, 'magnet_model',
                                   int)
            if _n_ref in [1, 2, 3]:
                return self.averageN[_n_ref]
            elif _n_ref in [0, 6]:
                return self.averageN[1]
            elif _n_ref == 4:
                return self.averageS[2]
            elif _n_ref == 5:
                return self.averageS[1]
        return np.nan

    def check_std(self):
        """Checks standard deviation magnitude and returns false if it's
        greater than the maximum error."""
        _n_ref = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)
        if _n_ref == 0:
            _max_error = 1
            # checks dipole error
            _n_ref = _n_ref + 1
        elif _n_ref in [1, 5, 6]:
            _n_ref = 1
            _max_error = 8e-6
        elif _n_ref in [2, 4]:
            _n_ref = 2
            _max_error = 8e-4
        elif _n_ref == 3:
            _max_error = 3.6e-2

        if self.stdN[_n_ref] > _max_error or self.stdS[_n_ref] > _max_error:
            return False
        return True

    def fft_calculation(self):
        """Computes FFT from integrator data."""
        _n_of_turns = self.df_rawcurves.shape[1]
        self.df_fft = pd.DataFrame()

        try:
            shiftx = self.ui.le_shift_x.text()
            lpos = self.ui.le_longitudinal_pos.text()
            timestamp = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())

            filename = '{0:s}_LPos_{1:s}_HShift_{2:s}.txt'.format(
                timestamp, lpos, shiftx)
            filepath = os.path.join(Lib.dir_path, filename)

            to_file = []
            
            #Add scaling factor for Raw Data:
            _scale_fct = float(self.ui.sb_rescaling.text())
            self.df_rawcurves = self.df_rawcurves*(1-(_scale_fct/100))
                        
            for i in range(_n_of_turns):
                _tmp = self.df_rawcurves[i].tolist()
                _tmpfft = np.fft.fft(_tmp) / (len(_tmp)/2)
                self.df_fft[i] = _tmpfft
                to_file.append(_tmpfft)

            #np.savetxt(filepath, np.transpose(np.array(to_file)))
            #print("FFT coefficients saved to file: ", filepath)

            # Para ler o arquivo:
            # a = np.loadtxt(filepath, dtype=str)
            # c = np.array([[
            #    np.complex(v.replace('+-', '-')) for v in l] for l in a])

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def displacement_calculation(self):
        """Computes magnetic center displacement."""
        _main_harmonic = Lib.get_value(Lib.measurement_settings,
                                       'magnet_model', int)

        if 1 < _main_harmonic < 5:
            # Skew quadrupole
            if _main_harmonic >= 4:
                # Prepares skew magnet center calculation
                if _main_harmonic == 4:
                    # Skew quadrupole
                    _main_harmonic = 2
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

            _dx = -1*(1/(_main_harmonic-1))*(_prev_multipole/_main_multipole)
            _dy = (-1*(_dy_sign)*(1/(_main_harmonic-1)) *
                   (_prev_perp_multipole/_main_multipole))
            _dx_um = round(_dx*1e06, 3)
            _dy_um = round(_dy*1e06, 3)

            self.ui.le_magnetic_center_x.setText(str(_dx_um))
            self.ui.le_magnetic_center_y.setText(str(_dy_um))

            Lib.write_value(Lib.measurement_settings, 'magnetic_center_x',
                            _dx_um, True)
            Lib.write_value(Lib.measurement_settings, 'magnetic_center_y',
                            _dy_um, True)

        else:
            self.ui.le_magnetic_center_x.setText("")
            self.ui.le_magnetic_center_y.setText("")

    def configure_integrator(self, adj_offset=False):
        """Configures integrator."""
        _n_of_turns = Lib.get_value(Lib.data_settings,
                                    'total_number_of_turns', int)

        _n_encoder_pulses = int(Lib.get_value(Lib.data_settings,
                                              'n_encoder_pulses', float))
        _gain = Lib.get_value(Lib.data_settings, 'integrator_gain', int)
        try:
            if Lib.get_value(Lib.measurement_settings,
                             'coil_rotation_direction', str) == 'Clockwise':
                _direction = 0
            else:
                _direction = 1
        except Exception:
            _direction = self.ui.cb_coil_rotation_direction.currentIndex()

        try:
            _trigger_ref = Lib.get_value(Lib.coil_settings, 'trigger_ref', int)
        except Exception:
            if adj_offset:
                _trigger_ref = 0
            else:
                raise Exception
        if _trigger_ref > int(_n_encoder_pulses-1):
            _QMessageBox.warning(self, 'Warning',
                                 'Trigger ref greater than allowed.',
                                 _QMessageBox.Ok)
            return False

        _n_integration_points = Lib.get_value(Lib.data_settings,
                                              'n_integration_points', int)

        if adj_offset:
            _n_of_turns = 1

        try:
            Lib.comm.fdi.config_measurement(_n_encoder_pulses, _gain,
                                            _direction, _trigger_ref,
                                            _n_integration_points, _n_of_turns)
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def measure_and_read(self):
        """Measurement routine."""
        _address = Lib.get_value(Lib.data_settings, 'rotation_motor_address',
                                 int)
        _n_of_turns = Lib.get_value(Lib.data_settings, 'total_number_of_turns',
                                    int)
        _n_integration_points = Lib.get_value(Lib.data_settings,
                                              'n_integration_points', int)
        _total_n_of_points = _n_integration_points * _n_of_turns
        _ps_interlock = Lib.get_value(Lib.data_settings,
                                      'disable_ps_interlock', int)
        _ratio = Lib.get_value(Lib.data_settings, 'rotation_motor_ratio',
                               float)
        _vel = Lib.get_value(Lib.data_settings, 'rotation_motor_speed',
                             float) * _ratio
        # time limit is ~twice the time the measurement should take
        _time_limit = 2*(_n_of_turns+1)*_vel

        if not _ps_interlock:
            #starts monitor thread
            self.sync.clear()
            _thread = threading.Thread(target=self.monitor_thread,
                                       name='Monitor Thread')
            _thread.start()

        if Lib.flags.stop_all is False:
            #corrects coil position
            self.coil_position_correction()
            # start measurement
            Lib.comm.fdi.start_measurement()

        if not _ps_interlock:
            #Enables monitor thread
            self.sync.set()

        if Lib.flags.stop_all is False:
            # move motor
            self.move_motor_measurement(_n_of_turns+1+1)

        _time0 = time.time()
        # start collecting data
        _count = Lib.comm.fdi.get_data_count()
        while (_count != _total_n_of_points) and (Lib.flags.stop_all is False):
            _count = Lib.comm.fdi.get_data_count()
            if (time.time() - _time0) > _time_limit:
                if Lib.comm.parker.limits(_address):
                    Lib.db_save_failure(7)
                    _QMessageBox.warning(self, 'Warning', 'Air flux stopped '
                                         'during measurement.',
                                         _QMessageBox.Ok)
                    raise Exception
                else:
                    Lib.db_save_failure(0)
                    _QMessageBox.warning(self, 'Warning', 'Timeout while '
                                         'waiting for integrator data.',
                                         _QMessageBox.Ok)
                    raise Exception
            QtWidgets.QApplication.processEvents()
        if Lib.flags.stop_all is False:
            _results = Lib.comm.fdi.get_data()
            _results = _results.strip('\n').split(',')
            for i in range(len(_results)):
                try:
                    _results[i] = float(_results[i].strip(' WB'))
                except Exception:
                    if 'NAN' in _results[i]:
                        Lib.db_save_failure(2)
                        _QMessageBox.warning(self, 'Warning',
                                             'Integrator tension over-range.\n'
                                             'Please configure a lower gain.',
                                             _QMessageBox.Ok)
                    raise Exception
            self.data_array = np.array(_results, dtype=np.float64)
            try:
                _tmp = self.data_array.reshape(
                    _n_of_turns, _n_integration_points).transpose()
            except Exception:
                raise Exception
            #discard initial and final turns
            _i = Lib.get_value(Lib.data_settings, 'remove_initial_turns', int)
            _f = -Lib.get_value(Lib.data_settings, 'remove_final_turns', int)
            # avoids error if _f == 0
            if not _f:
                _f = None
            if _i + _f < _n_of_turns:
                _tmp = _tmp[:, _i:_f]
            # correction depending on rotation direction
            _direction = Lib.get_value(
                Lib.measurement_settings, 'coil_rotation_direction',
                str) == 'CounterClockwise'
            if not _direction:
                self.df_rawcurves = pd.DataFrame(_tmp)
            else:
                self.df_rawcurves = pd.DataFrame(_tmp[::-1] * -1)

    def plot_raw_graph(self):
        """Plot integrator raw data graph."""
        self.ui.gv_rawcurves.plotItem.curves.clear()
        self.ui.gv_rawcurves.clear()
        self.ui.gv_rawcurves.plotItem.setLabel('left', "Amplitude",
                                               units="V.s")
        self.ui.gv_rawcurves.plotItem.setLabel('bottom', "Points")
        self.ui.gv_rawcurves.plotItem.showGrid(x=True, y=True, alpha=0.2)

        px = np.linspace(0, len(self.data_array)-1, len(self.data_array))
        self.ui.gv_rawcurves.plotItem.plot(px, self.data_array,
                                           pen=(255, 0, 0), symbol=None)

    def plot_multipoles(self):
        """Plot multipoles bar graph."""
        self.ui.gv_multipoles.clear()

        _px = np.linspace(1, 15, 15)

        _n = Lib.get_value(Lib.measurement_settings, 'magnet_model', int)
        # skew quadrupole
        if _n == 4:
            _n = 2
        # corrector dipole
        elif _n in [5, 6]:
            _n = 1
        _n = _n - 1

        self.ui.gv_multipoles.plotItem.addLegend()
        _graph = pg.BarGraphItem(x=_px, height=self.averageN_norm.values,
                                 width=0.6, brush='r', name='Normal')
        _graph2 = pg.BarGraphItem(x=_px, height=self.averageS_norm.values,
                                  width=0.6, brush='b', name='Skew')

        self.ui.gv_multipoles.addItem(_graph)
        self.ui.gv_multipoles.addItem(_graph2)
        self.ui.gv_multipoles.plotItem.setLabel('left',
                                                'Normalized Multipoles')
        self.ui.gv_multipoles.plotItem.setLabel('bottom', "Multipole number")
        self.ui.gv_multipoles.plotItem.showGrid(x=True, y=True, alpha=0.2)
        if _n > -1:
            _maxn = np.delete(abs(self.averageN_norm.values), _n).max()
            _maxs = np.delete(abs(self.averageS_norm.values), _n).max()
            _max = max(_maxn, _maxs)
            self.ui.gv_multipoles.plotItem.setYRange(-_max, _max)

    def save_data_results(self):
        """Save results to log file"""
        _dir = (
            QtWidgets.QFileDialog.getExistingDirectory(
                self, 'Save Directory', Lib.dir_path).replace('/', '\\\\') +
            '\\\\')
        _ans = Lib.save_log_file(path=_dir)
        if _ans:
            _QMessageBox.information(self, 'Information',
                                     'Log file successfully saved.',
                                     _QMessageBox.Ok)
        else:
            _QMessageBox.warning(self, 'Warning', 'Failed to save log file.',
                                 _QMessageBox.Ok)

    def refresh_interface(self):
        """Refresh inteface with defaults settings."""
        #list ports and fill comboboxes
        _l = serial.tools.list_ports.comports()
        self.ports = []

        _s = ''
        _k = str
        if 'COM' in _l[0][0]:
            _s = 'COM'
            _k = int

        for key in _l:
            self.ports.append(key.device.strip(_s))
        self.ports.sort(key=_k)
        self.ports = [_s + key for key in self.ports]

        for _ in range(self.ui.cb_disp_port.count()):
            self.ui.cb_disp_port.removeItem(0)
            self.ui.cb_driver_port.removeItem(0)
            self.ui.cb_ps_port.removeItem(0)
            self.ui.cb_ps_port_2.removeItem(0)
        self.ui.cb_disp_port.addItems(self.ports)
        self.ui.cb_driver_port.addItems(self.ports)
        self.ui.cb_ps_port.addItems(self.ports)
        self.ui.cb_ps_port_2.addItems(['None'] + self.ports)

        # Connection Tab
        self.ui.cb_disp_port.setCurrentText(Lib.get_value(Lib.data_settings,
                                                          'disp_port', str))
        self.ui.cb_driver_port.setCurrentText(
            Lib.get_value(Lib.data_settings, 'driver_port', str))
        self.ui.cb_ps_port.setCurrentText(
            Lib.get_value(Lib.data_settings, 'ps_port', str))

        self.ui.chb_enable_Agilent34970A.setChecked(
            Lib.get_value(Lib.data_settings, 'enable_Agilent34970A', int))
        self.ui.sb_agilent34970A_address.setValue(
            Lib.get_value(Lib.data_settings, 'agilent34970A_address', int))
        
        #Add Agilent 34401A
        self.ui.chb_enable_Agilent34401A.setChecked(
            Lib.get_value(Lib.data_settings, 'enable_Agilent34401A', int))
        self.ui.sb_agilent34401A_address.setValue(
            Lib.get_value(Lib.data_settings, 'agilent34401A_address', int))

        # Settings Tab
        self.ui.le_total_number_of_turns.setText(
            Lib.get_value(Lib.data_settings, 'total_number_of_turns', str))
        self.ui.le_remove_initial_turns.setText(
            Lib.get_value(Lib.data_settings, 'remove_initial_turns', str))
        self.ui.le_remove_final_turns.setText(
            Lib.get_value(Lib.data_settings, 'remove_final_turns', str))

        self.ui.le_rotation_motor_address.setText(
            Lib.get_value(Lib.data_settings, 'rotation_motor_address', str))
        self.ui.le_rotation_motor_resolution.setText(
            Lib.get_value(Lib.data_settings, 'rotation_motor_resolution', str))
        self.ui.le_rotation_motor_speed.setText(
            Lib.get_value(Lib.data_settings, 'rotation_motor_speed', str))
        self.ui.le_rotation_motor_acceleration.setText(
            Lib.get_value(Lib.data_settings, 'rotation_motor_acceleration',
                          str))
        self.ui.le_rotation_motor_ratio.setText(
            Lib.get_value(Lib.data_settings, 'rotation_motor_ratio', str))

        self.ui.le_n_encoder_pulses.setText(
            Lib.get_value(Lib.data_settings, 'n_encoder_pulses', str))

        self.ui.cb_integrator_gain.setCurrentText(
            str(Lib.get_value(Lib.data_settings, 'integrator_gain', int)))
        self.ui.cb_n_integration_points.setCurrentText(
            str(Lib.get_value(Lib.data_settings, 'n_integration_points', int)))

        self.ui.chb_disable_alignment_interlock.setChecked(
            Lib.get_value(Lib.data_settings, 'disable_alignment_interlock',
                          int))
        self.ui.chb_disable_ps_interlock.setChecked(
            Lib.get_value(Lib.data_settings, 'disable_ps_interlock', int))

        self.ui.cb_bench.setCurrentIndex(
            Lib.get_value(Lib.data_settings, 'bench', int) - 1)

        # Motor Tab
        self.ui.le_motor_vel.setText(
            Lib.get_value(Lib.data_settings, 'rotation_motor_speed', str))
        self.ui.le_motor_ace.setText(
            Lib.get_value(Lib.data_settings, 'rotation_motor_acceleration',
                          str))
        self.ui.le_motor_turns.setText(str(1))

    def config_variables(self):
        """Refresh variables with inteface values."""
        try:
            # Connection Tab
            Lib.write_value(Lib.data_settings, 'disp_port',
                            self.ui.cb_disp_port.currentText())
            Lib.write_value(Lib.data_settings, 'driver_port',
                            self.ui.cb_driver_port.currentText())
            Lib.write_value(Lib.data_settings, 'ps_port',
                            self.ui.cb_ps_port.currentText())
            Lib.write_value(Lib.data_settings, 'ps_port_2',
                            self.ui.cb_ps_port_2.currentText())

            Lib.write_value(Lib.data_settings, 'enable_Agilent34970A',
                            int(self.ui.chb_enable_Agilent34970A.isChecked()))
            Lib.write_value(Lib.data_settings, 'agilent34970A_address',
                            self.ui.sb_agilent34970A_address.value(), True)
            #Add 34401A Multimeter
            Lib.write_value(Lib.data_settings, 'enable_Agilent34401A',
                            int(self.ui.chb_enable_Agilent34401A.isChecked()))
            Lib.write_value(Lib.data_settings, 'agilent34401A_address',
                            self.ui.sb_agilent34401A_address.value(), True)

            # Settings Tab
            Lib.write_value(Lib.data_settings, 'total_number_of_turns',
                            self.ui.le_total_number_of_turns.text(), True)
            Lib.write_value(Lib.data_settings, 'remove_initial_turns',
                            self.ui.le_remove_initial_turns.text(), True)
            Lib.write_value(Lib.data_settings, 'remove_final_turns',
                            self.ui.le_remove_final_turns.text(), True)

            Lib.write_value(Lib.data_settings, 'rotation_motor_address',
                            self.ui.le_rotation_motor_address.text(), True)
            Lib.write_value(Lib.data_settings, 'rotation_motor_resolution',
                            self.ui.le_rotation_motor_resolution.text(), True)
            Lib.write_value(Lib.data_settings, 'rotation_motor_speed',
                            self.ui.le_rotation_motor_speed.text(), True)
            Lib.write_value(Lib.data_settings, 'rotation_motor_acceleration',
                            self.ui.le_rotation_motor_acceleration.text(),
                            True)
            Lib.write_value(Lib.data_settings, 'rotation_motor_ratio',
                            self.ui.le_rotation_motor_ratio.text(), True)

            Lib.write_value(Lib.data_settings, 'n_encoder_pulses',
                            self.ui.le_n_encoder_pulses.text(), True)

            Lib.write_value(Lib.data_settings, 'integrator_gain',
                            int(self.ui.cb_integrator_gain.currentText()))
            Lib.write_value(Lib.data_settings, 'n_integration_points',
                            int(self.ui.cb_n_integration_points.currentText()))
            
#             Lib.write_value(Lib.data_settings, 'raw_data_scaling_factor',
#                             float(self.ui.sb_rescaling.value()), True) #Add

            Lib.write_value(
                Lib.data_settings, 'disable_alignment_interlock',
                int(self.ui.chb_disable_alignment_interlock.isChecked()))
            Lib.write_value(
                Lib.data_settings, 'disable_ps_interlock',
                int(self.ui.chb_disable_ps_interlock.isChecked()))

            Lib.write_value(Lib.data_settings, 'bench',
                            self.ui.cb_bench.currentIndex() + 1)
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            _QMessageBox.warning(self, 'Warning',
                                 'Could not configure the settings.\n'
                                 'Check if all the inputs are numbers.',
                                 _QMessageBox.Ok)
            return False

    def refresh_coiltab(self):
        """Refresh coil tab with current configurations."""
        # Coil Tab
        try:
            self.ui.le_coil_name.setText(
                Lib.get_value(Lib.coil_settings, 'coil_name', str))
            self.ui.le_n_turns_normal.setText(
                Lib.get_value(Lib.coil_settings, 'n_turns_normal', str))
            self.ui.le_radius1_normal.setText(
                Lib.get_value(Lib.coil_settings, 'radius1_normal', str))
            self.ui.le_radius2_normal.setText(
                Lib.get_value(Lib.coil_settings, 'radius2_normal', str))
            self.ui.le_n_turns_bucked.setText(
                Lib.get_value(Lib.coil_settings, 'n_turns_bucked', str))
            self.ui.le_radius1_bucked.setText(
                Lib.get_value(Lib.coil_settings, 'radius1_bucked', str))
            self.ui.le_radius2_bucked.setText(
                Lib.get_value(Lib.coil_settings, 'radius2_bucked', str))
            self.ui.le_trigger_ref.setText(
                str(Lib.get_value(Lib.coil_settings, 'trigger_ref', int)))

            if Lib.get_value(Lib.coil_settings, 'coil_type') == 'Radial':
                self.ui.cb_coil_type.setCurrentIndex(0)
            else:
                self.ui.cb_coil_type.setCurrentIndex(1)

            self.ui.te_comments.setPlainText(
                Lib.get_value(Lib.coil_settings, 'comments', str))
            return True
        except Exception:
            _QMessageBox.warning(self, 'Warning', 'Failed to load coil',
                                 _QMessageBox.Ok)
            return False

    def configure_coil(self):
        """Configures coil."""
        if Lib.coil_settings is None:
            try:
                Lib.coil_df()
            except Exception:
                _QMessageBox.warning(self, 'Warning', 'Please check if all '
                                     'the inputs are properly set.',
                                     _QMessageBox.Ok)
                return
        _ans = self.config_coil()
        if _ans:
            _QMessageBox.information(self, 'Information', 'Coil configurations'
                                     ' completed successfully.',
                                     _QMessageBox.Ok)

    def config_coil(self):
        """Configures coil with UI settings."""
        try:
            # Coil Tab
            Lib.write_value(Lib.coil_settings, 'coil_name',
                            self.ui.le_coil_name.text())
            Lib.write_value(Lib.coil_settings, 'n_turns_normal',
                            self.ui.le_n_turns_normal.text(), True)
            Lib.write_value(Lib.coil_settings, 'radius1_normal',
                            self.ui.le_radius1_normal.text(), True)
            Lib.write_value(Lib.coil_settings, 'radius2_normal',
                            self.ui.le_radius2_normal.text(), True)
            Lib.write_value(Lib.coil_settings, 'n_turns_bucked',
                            self.ui.le_n_turns_bucked.text(), True)
            Lib.write_value(Lib.coil_settings, 'radius1_bucked',
                            self.ui.le_radius1_bucked.text(), True)
            Lib.write_value(Lib.coil_settings, 'radius2_bucked',
                            self.ui.le_radius2_bucked.text(), True)
            Lib.write_value(Lib.coil_settings, 'trigger_ref',
                            self.ui.le_trigger_ref.text(), True)
            Lib.write_value(Lib.coil_settings, 'coil_type',
                            self.ui.cb_coil_type.currentText())
            Lib.write_value(Lib.coil_settings, 'comments',
                            self.ui.te_comments.toPlainText())
            return True
        except Exception:
            _QMessageBox.warning(self, 'Warning',
                                 'Could not configure the coil settings.\n'
                                 'Check if all the coil inputs are correct.',
                                 _QMessageBox.Ok)
            return False

    def refresh_ps_settings(self):
        """Configures Power Supply with UI settings."""
        #Power Supply Tab
        #Configuration
        self.ui.cb_ps_type.setCurrentIndex(
            Lib.get_value(Lib.ps_settings, 'Power Supply Type', int) - 2)
        self.ui.le_ps_name.setText(
            Lib.get_value(Lib.ps_settings, 'Power Supply Name', str))
        #Slew Rate Adjustment
        self.ui.dsb_current_slewrate.setValue(
            Lib.get_value(Lib.ps_settings, 'Current Slew Rate', float))
        #Current Adjustment
        self.ui.dsb_current_setpoint.setValue(
            Lib.get_value(Lib.ps_settings, 'Current Setpoint', float))
        _array = Lib.get_value(Lib.ps_settings, 'Automatic Setpoints')
        _array = np.fromstring(_array, sep=',')
        self.array_to_table(_array, self.ui.tw_currents)
        #Demagnetization Curves
        #Sinusoidal
        self.ui.le_Sinusoidal_Amplitude.setText(
            str(Lib.get_value(Lib.ps_settings, 'Sinusoidal Amplitude', float)))
        self.ui.le_Sinusoidal_Offset.setText(
            str(Lib.get_value(Lib.ps_settings, 'Sinusoidal Offset', float)))
        self.ui.le_Sinusoidal_Frequency.setText(
            str(Lib.get_value(Lib.ps_settings, 'Sinusoidal Frequency', float)))
        self.ui.le_Sinusoidal_n_cycles.setText(
            str(Lib.get_value(Lib.ps_settings, 'Sinusoidal N Cycles', int)))
        self.ui.le_Initial_Phase.setText(
            str(Lib.get_value(Lib.ps_settings, 'Sinusoidal Initial Phase',
                              float)))
        self.ui.le_Final_Phase.setText(
            str(Lib.get_value(Lib.ps_settings, 'Sinusoidal Final Phase',
                              float)))
        #Damped Sinusoidal
        self.ui.le_damp_sin_Ampl.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal Amplitude',
                              float)))
        self.ui.le_damp_sin_Offset.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal Offset',
                              float)))
        self.ui.le_damp_sin_Freq.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal Frequency',
                              float)))
        self.ui.le_damp_sin_nCycles.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal N Cycles',
                              int)))
        self.ui.le_damp_sin_phaseShift.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal Phase Shift',
                              float)))
        self.ui.le_damp_sin_finalPhase.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal Final Phase',
                              float)))
        self.ui.le_damp_sin_Damping.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal Damping',
                              float)))
        #Damped Sinusoidal^2
        self.ui.le_damp_sin2_Ampl.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal2 Amplitude',
                              float)))
        self.ui.le_damp_sin2_Offset.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal2 Offset',
                              float)))
        self.ui.le_damp_sin2_Freq.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal2 Frequency',
                              float)))
        self.ui.le_damp_sin2_nCycles.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal2 N Cycles',
                              int)))
        self.ui.le_damp_sin2_phaseShift.setText(
            str(Lib.get_value(Lib.ps_settings,
                              'Damped Sinusoidal2 Phase Shift', float)))
        self.ui.le_damp_sin2_finalPhase.setText(
            str(Lib.get_value(Lib.ps_settings,
                              'Damped Sinusoidal2 Final Phase', float)))
        self.ui.le_damp_sin2_Damping.setText(
            str(Lib.get_value(Lib.ps_settings, 'Damped Sinusoidal2 Damping',
                              float)))
        #Trapezoidal
        self.ui.le_trapezoidal_offset.setText(
            str(Lib.get_value(Lib.ps_settings, 'Trapezoidal Offset', float)))
        _array = Lib.get_value(Lib.ps_settings, 'Trapezoidal Array')
        if _array is not np.nan:
            _array = np.fromstring(_array, sep=',')
            _array = _array.reshape(int(_array.shape[0]/2), 2)
            self.array_to_table(_array, self.ui.tw_trapezoidal)
        #Settings
        self.ui.le_maximum_current.setText(
            str(Lib.get_value(Lib.ps_settings, 'Maximum Current', float)))
        self.ui.le_minimum_current.setText(
            str(Lib.get_value(Lib.ps_settings, 'Minimum Current', float)))
        self.ui.sb_kp.setValue(Lib.get_value(Lib.ps_settings, 'Kp', float))
        self.ui.sb_ki.setValue(Lib.get_value(Lib.ps_settings, 'Ki', float))
        self.ui.dcct_select.setCurrentIndex(
            Lib.get_value(Lib.ps_settings, 'DCCT Head', int))

    def configure_ps(self, secondary=False):
        """Configures power supply."""
        if not secondary:
            if Lib.ps_settings is None:
                try:
                    Lib.ps_df(False)
                except Exception:
                    _QMessageBox.warning(self, 'Warning', 'Please check if all'
                                         ' the inputs are properly set.',
                                         _QMessageBox.Ok)
            self.ui.gb_start_supply.setEnabled(True)
            self.ui.pb_ps_button.setEnabled(True)
            self.ui.le_status_loop.setEnabled(True)
            self.ui.label_32.setEnabled(True)
            _ans = self.config_ps()
        else:
            if Lib.ps_settings_2 is None:
                try:
                    Lib.ps_df(True)
                except Exception:
                    _QMessageBox.warning(self, 'Warning', 'Please check if all'
                                         ' the inputs are properly set.',
                                         _QMessageBox.Ok)
            self.ui.gb_start_supply_2.setEnabled(True)
            self.ui.pb_ps_button_2.setEnabled(True)
            self.ui.le_status_loop_2.setEnabled(True)
            self.ui.label_37.setEnabled(True)
            _ans = self.config_ps_2()
        if _ans:
            _QMessageBox.information(self, 'Information',
                                     'Configuration completed successfully.',
                                     _QMessageBox.Ok)
        else:
            _QMessageBox.warning(self, 'Warning',
                                 'Failed to configure power supply.\n'
                                 'Check if all values are numbers.',
                                 _QMessageBox.Ok)

    def config_ps(self):
        """Configures UI with current Power Supply settings."""
        try:
            # Power Supply Tab
            Lib.write_value(Lib.ps_settings, 'Power Supply Name',
                            self.ui.le_ps_name.text())
            Lib.write_value(Lib.ps_settings, 'Power Supply Type',
                            self.ui.cb_ps_type.currentIndex()+2, True)
            Lib.write_value(Lib.ps_settings, 'Current Setpoint',
                            self.ui.dsb_current_setpoint.value(), True)
            Lib.write_value(Lib.ps_settings, 'Current Slew Rate',
                            self.ui.dsb_current_slewrate.value(), True)
            Lib.write_value(Lib.ps_settings, 'Sinusoidal Amplitude',
                            self.ui.le_Sinusoidal_Amplitude.text(), True)
            Lib.write_value(Lib.ps_settings, 'Sinusoidal Offset',
                            self.ui.le_Sinusoidal_Offset.text(), True)
            Lib.write_value(Lib.ps_settings, 'Sinusoidal Frequency',
                            self.ui.le_Sinusoidal_Frequency.text(), True)
            Lib.write_value(Lib.ps_settings, 'Sinusoidal N Cycles',
                            self.ui.le_Sinusoidal_n_cycles.text(), True)
            Lib.write_value(Lib.ps_settings, 'Sinusoidal Initial Phase',
                            self.ui.le_Initial_Phase.text(), True)
            Lib.write_value(Lib.ps_settings, 'Sinusoidal Final Phase',
                            self.ui.le_Final_Phase.text(), True)
            #Damped Sinusoidal
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal Amplitude',
                            self.ui.le_damp_sin_Ampl.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal Offset',
                            self.ui.le_damp_sin_Offset.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal Frequency',
                            self.ui.le_damp_sin_Freq.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal N Cycles',
                            self.ui.le_damp_sin_nCycles.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal Phase Shift',
                            self.ui.le_damp_sin_phaseShift.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal Final Phase',
                            self.ui.le_damp_sin_finalPhase.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal Damping',
                            self.ui.le_damp_sin_Damping.text(), True)
            #Damped Sinusoidal^2
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal2 Amplitude',
                            self.ui.le_damp_sin2_Ampl.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal2 Offset',
                            self.ui.le_damp_sin2_Offset.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal2 Frequency',
                            self.ui.le_damp_sin2_Freq.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal2 N Cycles',
                            self.ui.le_damp_sin2_nCycles.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal2 Phase Shift',
                            self.ui.le_damp_sin2_phaseShift.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal2 Final Phase',
                            self.ui.le_damp_sin2_finalPhase.text(), True)
            Lib.write_value(Lib.ps_settings, 'Damped Sinusoidal2 Damping',
                            self.ui.le_damp_sin2_Damping.text(), True)
            #Trapezoidal
            Lib.write_value(Lib.ps_settings, 'Trapezoidal Offset',
                            self.ui.le_trapezoidal_offset.text(), True)
            _values = str(self.table_to_array(self.ui.tw_trapezoidal).tolist())
            _values = _values.replace('[', '').replace(']', '')
            Lib.write_value(Lib.ps_settings, 'Trapezoidal Array',
                            str(_values), False)
            #Automatic setpoints
            _values = self.table_to_array(self.ui.tw_currents)
            _values = ", ".join(str(x) for x in _values)
            Lib.write_value(Lib.ps_settings, 'Automatic Setpoints',
                            str(_values), False)
            #Settings
            Lib.write_value(Lib.ps_settings, 'Maximum Current',
                            self.ui.le_maximum_current.text(), True)
            Lib.write_value(Lib.ps_settings, 'Minimum Current',
                            self.ui.le_minimum_current.text(), True)
            Lib.write_value(Lib.ps_settings, 'Kp', self.ui.sb_kp.text(), True)
            Lib.write_value(Lib.ps_settings, 'Ki', self.ui.sb_ki.text(), True)
            Lib.write_value(Lib.ps_settings, 'DCCT Head',
                            self.ui.dcct_select.currentIndex(), True)
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            _QMessageBox.warning(self, 'Warning', 'Could not configure the '
                                 'power supply settings.\nCheck if all the '
                                 'inputs are correct.',
                                 _QMessageBox.Ok)
            return False

    def refresh_ps_settings_2(self):
        """Configures secondary Power Supply with UI settings."""
        #Power Supply Tab
        #Configuration
        self.ui.cb_ps_type_2.setCurrentIndex(
            Lib.get_value(Lib.ps_settings_2, 'Power Supply Type', int)-4)
        self.ui.le_ps_name_2.setText(
            Lib.get_value(Lib.ps_settings_2, 'Power Supply Name', str))
        #Slew Rate Adjustment
        self.ui.dsb_current_slewrate_2.setValue(
            Lib.get_value(Lib.ps_settings_2, 'Current Slew Rate', float))
        #Current Adjustment
        self.ui.dsb_current_setpoint_2.setValue(
            Lib.get_value(Lib.ps_settings_2, 'Current Setpoint', float))
        _array = Lib.get_value(Lib.ps_settings_2, 'Automatic Setpoints')
        _array = np.fromstring(_array, sep=',')
        self.array_to_table(_array, self.ui.tw_currents_2)
        #Demagnetization Curves
        #Damped Sinusoidal
        self.ui.le_damp_sin_Ampl_2.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Damped Sinusoidal Amplitude',
                              float)))
        self.ui.le_damp_sin_Offset_2.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Damped Sinusoidal Offset',
                              float)))
        self.ui.le_damp_sin_Freq_2.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Damped Sinusoidal Frequency',
                              float)))
        self.ui.le_damp_sin_nCycles_2.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Damped Sinusoidal N Cycles',
                              int)))
        self.ui.le_damp_sin_phaseShift_2.setText(
            str(Lib.get_value(Lib.ps_settings_2,
                              'Damped Sinusoidal Phase Shift', float)))
        self.ui.le_damp_sin_finalPhase_2.setText(
            str(Lib.get_value(Lib.ps_settings_2,
                              'Damped Sinusoidal Final Phase', float)))
        self.ui.le_damp_sin_Damping_2.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Damped Sinusoidal Damping',
                              float)))
        #Damped Sinusoidal^2
        self.ui.le_damp_sin2_Ampl.setText(
            str(Lib.get_value(Lib.ps_settings_2,
                              'Damped Sinusoidal2 Amplitude', float)))
        self.ui.le_damp_sin2_Offset.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Damped Sinusoidal2 Offset',
                              float)))
        self.ui.le_damp_sin2_Freq.setText(
            str(Lib.get_value(Lib.ps_settings_2,
                              'Damped Sinusoidal2 Frequency', float)))
        self.ui.le_damp_sin2_nCycles.setText(
            str(Lib.get_value(Lib.ps_settings_2,
                              'Damped Sinusoidal2 N Cycles', int)))
        self.ui.le_damp_sin2_phaseShift.setText(
            str(Lib.get_value(Lib.ps_settings_2,
                              'Damped Sinusoidal2 Phase Shift', float)))
        self.ui.le_damp_sin2_finalPhase.setText(
            str(Lib.get_value(Lib.ps_settings_2,
                              'Damped Sinusoidal2 Final Phase', float)))
        self.ui.le_damp_sin2_Damping.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Damped Sinusoidal2 Damping',
                              float)))
        #Trapezoidal
        self.ui.le_trapezoidal_offset.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Trapezoidal Offset', float)))
        _array = Lib.get_value(Lib.ps_settings_2, 'Trapezoidal Array')
        if _array is not np.nan:
            _array = np.fromstring(_array, sep=',')
            _array = _array.reshape(int(_array.shape[0]/2), 2)
            self.array_to_table(_array, self.ui.tw_trapezoidal_2)
        #Settings
        self.ui.le_maximum_current_2.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Maximum Current', float)))
        self.ui.le_minimum_current_2.setText(
            str(Lib.get_value(Lib.ps_settings_2, 'Minimum Current', float)))

    def config_ps_2(self):
        """Configures UI with current secondary Power Supply settings."""
        try:
            # Power Supply Tab
            Lib.write_value(Lib.ps_settings_2, 'Power Supply Name',
                            self.ui.le_ps_name_2.text())
            Lib.write_value(Lib.ps_settings_2, 'Power Supply Type',
                            self.ui.cb_ps_type_2.currentIndex()+4, True)
            Lib.write_value(Lib.ps_settings_2, 'Current Setpoint',
                            self.ui.dsb_current_setpoint_2.value(), True)
            Lib.write_value(Lib.ps_settings_2, 'Current Slew Rate',
                            self.ui.dsb_current_slewrate_2.value(), True)
            #Damped Sinusoidal
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal Amplitude',
                            self.ui.le_damp_sin_Ampl_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal Offset',
                            self.ui.le_damp_sin_Offset_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal Frequency',
                            self.ui.le_damp_sin_Freq_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal N Cycles',
                            self.ui.le_damp_sin_nCycles_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal Phase Shift',
                            self.ui.le_damp_sin_phaseShift_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal Final Phase',
                            self.ui.le_damp_sin_finalPhase_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal Damping',
                            self.ui.le_damp_sin_Damping_2.text(), True)
            #Damped Sinusoidal^2
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal2 Amplitude',
                            self.ui.le_damp_sin2_Ampl_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal2 Offset',
                            self.ui.le_damp_sin2_Offset_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal2 Frequency',
                            self.ui.le_damp_sin2_Freq_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal2 N Cycles',
                            self.ui.le_damp_sin2_nCycles_2.text(), True)
            Lib.write_value(Lib.ps_settings_2,
                            'Damped Sinusoidal2 Phase Shift',
                            self.ui.le_damp_sin2_phaseShift_2.text(), True)
            Lib.write_value(Lib.ps_settings_2,
                            'Damped Sinusoidal2 Final Phase',
                            self.ui.le_damp_sin2_finalPhase_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Damped Sinusoidal2 Damping',
                            self.ui.le_damp_sin2_Damping_2.text(), True)
            #Trapezoidal
            Lib.write_value(Lib.ps_settings_2, 'Trapezoidal Offset', True)
            _values = str(
                self.table_to_array(self.ui.tw_trapezoidal_2).tolist())
            _values = _values.replace('[', '').replace(']', '')
            Lib.write_value(Lib.ps_settings_2, 'Trapezoidal Array',
                            str(_values), False)
            #Automatic setpoints
            _values = self.table_to_array(self.ui.tw_currents_2)
            _values = ", ".join(str(x) for x in _values)
            Lib.write_value(Lib.ps_settings_2, 'Automatic Setpoints',
                            str(_values), False)
            #Settings
            Lib.write_value(Lib.ps_settings_2, 'Maximum Current',
                            self.ui.le_maximum_current_2.text(), True)
            Lib.write_value(Lib.ps_settings_2, 'Minimum Current',
                            self.ui.le_minimum_current_2.text(), True)
            return True
        except Exception:
            _QMessageBox.warning(self, 'Warning', 'Could not configure the '
                                 'secondary power supply settings.\n'
                                 'Check if all the inputs are correct.',
                                 _QMessageBox.Ok)
            return False

    def table_to_array(self, tw):
        """Returns tw_currents tableWidget values in a numpy array."""
        _tw = tw
        _ncells = _tw.rowCount()
        _current_array = []
        _time_flag = False
        if _tw in [self.ui.tw_trapezoidal, self.ui.tw_trapezoidal_2]:
            _time_flag = True
            _time_array = []
        try:
            if _ncells > 0:
                for i in range(_ncells):
                    _tw.setCurrentCell(i, 0)
                    if _tw.currentItem() is not None:
                        _current_array.append(float(_tw.currentItem().text()))
                    if _time_flag:
                        _tw.setCurrentCell(i, 1)
                        if _tw.currentItem() is not None:
                            _time_array.append(float(
                                _tw.currentItem().text()))
            if not _time_flag:
                return np.array(_current_array)
            else:
                return np.array([_current_array, _time_array]).transpose()
        except Exception:
            traceback.print_exc(file=sys.stdout)
            raise Exception('table_to_array() error.')
#             _QMessageBox.warning(self, 'Warning',
#                                  'Could not convert table to array.\n'
#                                  'Check if all inputs are numbers.',
#                                  _QMessageBox.Ok)
            return np.array([])

    def array_to_table(self, array, tw):
        """Inserts array values into tw_currents tableWidget."""
        _tw = tw
        _ncells = _tw.rowCount()
        _array = array
        _time_flag = False
        if _tw in [self.ui.tw_trapezoidal, self.ui.tw_trapezoidal_2]:
            _time_flag = True
        if _ncells > 0:
            self.clear_table(_tw)
        try:
            for i in range(len(_array)):
                _tw.insertRow(i)
                _item = QtWidgets.QTableWidgetItem()
                if not _time_flag:
                    _tw.setItem(i, 0, _item)
                    _item.setText(str(_array[i]))
                else:
                    _item2 = QtWidgets.QTableWidgetItem()
                    _tw.setItem(i, 0, _item)
                    _item.setText(str(_array[i, 0]))
                    time.sleep(0.1)
                    _tw.setItem(i, 1, _item2)
                    _item2.setText(str(_array[i, 1]))
                QtWidgets.QApplication.processEvents()
                time.sleep(0.01)
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            _QMessageBox.warning(self, 'Warning',
                                 'Could not insert array values into table.',
                                 _QMessageBox.Ok)
            return False

    def add_row(self, tw):
        _tw = tw
        _idx = _tw.rowCount()
        _tw.insertRow(_idx)

    def remove_row(self, tw):
        """Removes selected row from tw_currents tableWidget."""
        _tw = tw
        _idx = _tw.currentRow()
        _tw.removeRow(_idx)

    def clear_table(self, tw):
        """Clears currents from tableWidget."""
        _tw = tw
        _tw.clearContents()
        _ncells = _tw.rowCount()
        while _ncells >= 0:
            _tw.removeRow(_ncells)
            _ncells = _ncells - 1
        QtWidgets.QApplication.processEvents()

    def fill_multipole_table(self):
        """Fills multiples tableWidget."""

        n_rows = self.ui.tw_multipoles_table.rowCount()

        for i in range(n_rows):
            self.set_table_item(self.ui.tw_multipoles_table, i, 0,
                                self.averageN.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 1,
                                self.stdN.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 2,
                                self.averageS.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 3,
                                self.stdS.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 4,
                                self.averageMod.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 5,
                                self.stdMod.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 6,
                                self.averageAngle.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 7,
                                self.stdAngle.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 8,
                                self.averageN_norm.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 9,
                                self.stdN_norm.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 10,
                                self.averageS_norm.values[i])
            self.set_table_item(self.ui.tw_multipoles_table, i, 11,
                                self.stdS_norm.values[i])

    def set_table_item(self, table, row, col, val):
        """Sets a tableWidget cell value."""
        if table.objectName() == 'tw_multipoles_table':
            item = QtWidgets.QTableWidgetItem()
            table.setItem(row, col, item)
            item.setText('{0:0.3e}'.format(val))
        else:
            item = QtWidgets.QTableWidgetItem()
            table.setItem(row, col, item)
            item.setText(str(val))

    def stop(self, emergency=True):
        """Stops motor, integrador and power supplies in case of emergency."""
        Lib.flags.stop_all = True
        # stops motor
        self.stop_motor()
        # stops integrator
        Lib.comm.fdi.send(Lib.comm.fdi.FDIStop)

        self.ui.pb_start_meas.setEnabled(True)
        self.ui.le_n_collections.setEnabled(True)
        self.ui.tabWidget.setTabEnabled(5, True)
        self.ui.chb_automatic_ps.setEnabled(True)
        QtWidgets.QApplication.processEvents()

        # Move coil to assembly position
        self.ui.le_encoder_setpoint.setText(Lib.get_value(Lib.coil_settings,
                                                          'trigger_ref', str))
        # this clears stop_all flag
        self.move_to_encoder_position()
        # setting stop_all again
        Lib.flags.stop_all = True

        if emergency:
            Lib.flags.emergency = emergency

            if Lib.ps_settings_2 is None:
                _secondary_flag = 0
            else:
                _secondary_flag = Lib.get_value(Lib.aux_settings,
                                                'status_ps_2', int)
            _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
            if _secondary_flag:
                _ps_type_2 = Lib.get_value(Lib.ps_settings_2,
                                           'Power Supply Type', int)
            #Turn off main power supply
            if not self.set_address(_ps_type, False):
                return
            if not self.set_op_mode(0):
                _QMessageBox.warning(self, 'Warning', 'Could not set '
                                     'the slowRef operation mode.',
                                     _QMessageBox.Ok)
                return
            Lib.comm.drs.set_slowref(0)
            #wait down current according ps slew rate
            _slewrate = self.ui.dsb_current_slewrate.value()
            _t = Lib.get_value(Lib.ps_settings, 'Current Setpoint',
                               int) / _slewrate
            time.sleep(_t)
            Lib.comm.drs.turn_off()
            time.sleep(0.1)
            if _ps_type == 2:
                time.sleep(0.9)
            if Lib.comm.drs.read_ps_onoff() == 0:
                Lib.write_value(Lib.aux_settings, 'status_ps', 0)
                Lib.write_value(Lib.aux_settings, 'actual_current', 0)
                self.ui.pb_ps_button.setChecked(False)
                self.ui.pb_ps_button.setText('Turn ON')
                self.ui.lb_status_ps.setText('NOK')
                QtWidgets.QApplication.processEvents()
            time.sleep(.1)
            #Turn off secondary power supply
            if _secondary_flag:
                if not self.set_address(_ps_type_2, True):
                    return
                if not self.set_op_mode(0):
                    _QMessageBox.warning(self, 'Warning', 'Could not set '
                                         'the slowRef operation mode.',
                                         _QMessageBox.Ok)
                    return
                Lib.comm.drs.set_slowref(0)
                time.sleep(0.1)
                Lib.comm.drs.turn_off()
                time.sleep(0.1)
                if _ps_type == 2:
                    time.sleep(0.9)
                if Lib.comm.drs.read_ps_onoff() == 0:
                    Lib.write_value(Lib.aux_settings, 'status_ps_2', 0)
                    Lib.write_value(Lib.aux_settings, 'actual_current_2', 0)
                    self.ui.pb_ps_button_2.setChecked(False)
                    self.ui.pb_ps_button_2.setText('Turn ON')
                    QtWidgets.QApplication.processEvents()

            _QMessageBox.warning(self, 'Warning', 'Emergency situation.\n'
                                 'Motor and Integrator are stopped and the '
                                 'power supply(ies) turned off.',
                                 _QMessageBox.Ok)
        else:
            _QMessageBox.information(self, 'Information',
                                     'The measurement was stopped.',
                                     _QMessageBox.Ok)

    def dcct_convert(self, reading, DMM=False):
        """Converts dcct voltage to current."""
        _agilent_reading = reading
        if not DMM:
            if Lib.measurement_settings is not None:
                Lib.write_value(Lib.measurement_settings, 'temperature',
                                _agilent_reading[0])
                setattr(self, 'temperature_magnet', _agilent_reading[1])
                setattr(self, 'temperature_water', _agilent_reading[2])
            _voltage = _agilent_reading[4]
        
        if (Lib.get_value(Lib.data_settings, 'enable_Agilent34401A', 
                          int)) and (DMM==True):
            _voltage = Lib.comm.agilent34401A.read()
        else:
            _voltage = _agilent_reading[4]
        
        if _voltage == '':
            _current = 0
        else:
            # For 40 A dcct head
            if self.ui.dcct_select.currentIndex() == 0:
                _current = (float(_voltage))*4
            # For 160 A dcct head
            if self.ui.dcct_select.currentIndex() == 1:
                _current = (float(_voltage))*16
            # For 320 A dcct head
            if self.ui.dcct_select.currentIndex() == 2:
                _current = (float(_voltage))*32
            # For 1000 A dcct head
            if self.ui.dcct_select.currentIndex() == 3:
                if _voltage == 'NoneType':
                    Lib.comm.agilent34401A.connect(15,1)
                    Lib.comm.agilent34401A.config()
                    _current = 0
                else:
                    _current = (float(_voltage))*100
                    
        return _current

    def monitor_thread(self):
        """Function to generate a thread which monitors power supply
        currents and interlocks"""
        _n_turns = Lib.get_value(Lib.data_settings, 'total_number_of_turns',
                                 int)
        #check interlock if disable_ps_interlock not checked
        _disable_interlock = Lib.get_value(Lib.data_settings,
                                           'disable_ps_interlock', int)
        _interlock_flag = 0
        # clear arrays
        Lib.write_value(Lib.aux_settings, 'main_current_array',
                        pd.DataFrame([]))
        Lib.write_value(Lib.aux_settings, 'secondary_current_array',
                        pd.DataFrame([]))
        Lib.write_value(Lib.aux_settings, 'main_voltage_array',
                        pd.DataFrame([]))

        if Lib.ps_settings_2 is None:
            _secondary_flag = 0
        else:
            _secondary_flag = Lib.get_value(Lib.aux_settings, 'status_ps_2',
                                            int)
        _dcct_flag = self.ui.chb_dcct.isChecked()
        _voltage_flag = self.ui.chb_voltage.isChecked()
        _ps_type = Lib.get_value(Lib.ps_settings, 'Power Supply Type', int)
        _velocity = Lib.get_value(Lib.data_settings, 'rotation_motor_speed',
                                  float)
        if _secondary_flag:
            _ps_type_2 = Lib.get_value(Lib.ps_settings_2, 'Power Supply Type',
                                       int)

        # waits for main loop to enable monitoring
        self.sync.wait()
        for _ in range(_n_turns):
            _t = time.time()

            #monitor main coil current and interlocks
            if not self.set_address(_ps_type, False):
                return
            if not _disable_interlock:
                #_soft_interlock = Lib.comm.drs.read_ps_softinterlocks()  
                _soft_interlock = 0 #BYPASS
                #_hard_interlock = Lib.comm.drs.read_ps_hardinterlocks()
                _hard_interlock = 0 #BYPASS
#             _current = round(float(Lib.comm.drs.read_iload1()),3)
            if (Lib.get_value(Lib.data_settings,'enable_Agilent34401A',
                              int)) and (Lib.get_value(Lib.data_settings,
                                                       'enable_Agilent34970A',
                              int)) and (_dcct_flag):
                _agilent_reading = Lib.comm.agilent34401A.read()
                _current = round(self.dcct_convert(_agilent_reading, True), 3)
                #print('DMM: ', _current)
                
            elif (Lib.get_value(Lib.data_settings, 'enable_Agilent34970A',
                                 int)) and (Lib.get_value(Lib.data_settings,
                                                          'enable_Agilent34401A',
                              int) != 1) and (_dcct_flag):
#             if all([Lib.get_value(Lib.data_settings, 'enable_Agilent34970A',
#                                   int),
#                     _dcct_flag]):
                _agilent_reading = Lib.comm.agilent34970a.read_temp_volt()
                _current = round(self.dcct_convert(_agilent_reading, False), 3)
                #print('Multichannel: ', _current)
            else:
                _current = round(float(Lib.comm.drs.read_iload1()), 3)
            _i = Lib.get_value(Lib.aux_settings, 'main_current_array')
            _i = _i.append([_current], ignore_index=True)
            Lib.write_value(Lib.aux_settings, 'main_current_array', _i)

            #monitor secondary coil current  and interlocks if exists
            if _secondary_flag:
                if not self.set_address(_ps_type_2, True):
                    return
                if not _disable_interlock:
                    _soft_interlock_2 = Lib.comm.drs2.read_ps_softinterlocks()
                    _hard_interlock_2 = Lib.comm.drs2.read_ps_hardinterlocks()
                _current_2 = round(float(Lib.comm.drs2.read_iload1()), 3)
                _i_2 = Lib.get_value(Lib.aux_settings,
                                     'secondary_current_array')
                _i_2 = _i_2.append([_current_2], ignore_index=True)
                Lib.write_value(Lib.aux_settings, 'secondary_current_array',
                                _i_2)

            # monitor main coil voltage / magnet resistance (dcct)
            # voltage read from 34970A multichannel
            if _voltage_flag and Lib.get_value(Lib.data_settings,
                                               'enable_Agilent34970A', int):
                if _dcct_flag:
                    _voltage = round(float(_agilent_reading[3]), 3)
                else:
                    _voltage = round(
                        float(Lib.comm.agilent34970a.read_temp_volt()[3]), 3)
                _v = Lib.get_value(Lib.aux_settings, 'main_voltage_array')
                _v = _v.append([_voltage], ignore_index=True)
                Lib.write_value(Lib.aux_settings, 'main_voltage_array', _v)

            # in case of interlock or emergency, cuts off power supply,
            # stop motors, abort integrator, send warning
            if not _disable_interlock:
                _interlock = _soft_interlock + _hard_interlock
                _interlock_flag = _interlock
                if _secondary_flag:
                    _interlock_2 = _soft_interlock_2 + _hard_interlock_2
                    _interlock_flag = _interlock_flag + _interlock_2
            
#             print('Interlock F1000: ', _interlock, '| Interlock F10: ',
#                   _interlock_2)
#             print('F1K soft int: ', _soft_interlock, '| F1K hard int: ',
#                   _hard_interlock)
#             print('Stop all flag: ', Lib.flags.stop_all)
#             print('\n')

            if _interlock_flag or Lib.flags.stop_all:
                if _interlock:
                    self.ui.pb_interlock.setChecked(True)
                    self.ui.pb_emergency1.click()
                    print('Emergência acionado 1')
                    #Read interlocks DC/DC
                    print(Lib.comm.drs1.read_vars_fac_2p4s_dcdc())
                    #Change SlaveAdd for read interlocks AC/DC
                    Lib.comm.drs1.SetSlaveAdd(2) 
                    time.sleep(0.2)
                    print(Lib.comm.drs1.read_vars_fac_2p4s_acdc())
                    time.sleep(0.2)
                    Lib.comm.drs1.SetSlaveAdd(1) # volta para saída DC/DC
                    #Read interlocks from fbp
                    print(Lib.comm.drs2.read_vars_fbp())
                if _secondary_flag:
                    if _interlock_2:
                        self.ui.pb_interlock_2.setChecked(True)
                        self.ui.pb_emergency1.click()
                        print('Emergência acionado 2')
                QtWidgets.QApplication.processEvents()
                if Lib.flags.emergency:
                    Lib.db_save_failure(3)
                Lib.flags.stop_all = True
                return
            _t = (1/_velocity - 0.01) - (time.time()-_t)
            if _t > 0:
                time.sleep(_t)
#==============================================================================
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
#==============================================================================


class main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.myapp = ApplicationWindow()
        self.myapp.show()
        sys.exit(self.app.exec_())


# if __name__ == 'builtins':
if __name__ == '__main__':
    print(__name__ + ' ok')
    Lib = Library.RotatingCoil_Library()
    Lib.App = main()
else:
    print(__name__ + ' fail')
