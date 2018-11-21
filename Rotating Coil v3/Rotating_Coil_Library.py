'''
Created on 17 de nov de 2017

@author: James Citadini
'''
#import numpy as np
import os
import sys
import time
import sqlite3
import pandas as pd
import traceback
# from io import StringIO


# Biblioteca de variaveis globais utilizadas
class RotatingCoil_Library(object):
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.abspath(__file__)) + '\\'
        self.settings_file = 'rc_settings.dat'
        self.load_settings()

        self.App = None
        self.flags = flags()
        self.comm = communication()
        self.aux_df()
        self.coil_settings = None
        self.ps_settings = None
        self.ps_settings_2 = None
        self.measurement_settings = None

        self.db_create_table()

    def db_create_table(self):
        """
        Creates measurements table if it doesn't exists in db file
        """
        _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        _cur = _con.cursor()
        _cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND "
                     "name='measurements';")
        if not len(_cur.fetchall()):
            _create_table = """CREATE TABLE "measurements" (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\
             `magnet_name` TEXT NOT NULL,
             `filename` TEXT NOT NULL,
             `date` TEXT NOT NULL,
             `hour` TEXT NOT NULL,
             `operator` TEXT NOT NULL,
             `software_version` TEXT NOT NULL,
             `bench` INTEGER NOT NULL,
             `temperature` REAL NOT NULL,
             `rotation_motor_speed` REAL NOT NULL,
             `rotation_motor_acceleration` REAL NOT NULL,
             `coil_rotation_direction` TEXT NOT NULL,
             `integrator_gain` INTEGER NOT NULL,
             `trigger_ref` INTEGER NOT NULL,
             `n_integration_points` INTEGER NOT NULL,
             `n_turns` INTEGER NOT NULL,
             `n_collections` INTEGER NOT NULL,
             `analisys_interval` TEXT NOT NULL,
             `main_current` REAL NOT NULL,
             `main_coil_current_avg` REAL NOT NULL,
             `main_coil_current_std` REAL NOT NULL,
             `ch_coil_current_avg` REAL NOT NULL,
             `ch_coil_current_std` REAL NOT NULL,
             `cv_coil_current_avg` REAL NOT NULL,
             `cv_coil_current_std` REAL NOT NULL,
             `qs_coil_current_avg` REAL NOT NULL,
             `qs_coil_current_std` REAL NOT NULL,
             `trim_coil_current_avg` REAL NOT NULL,
             `trim_coil_current_std` REAL NOT NULL,
             `main_coil_volt_avg` REAL NOT NULL,
             `main_coil_volt_std` REAL NOT NULL,
             `magnet_resistance_avg` REAL NOT NULL,
             `magnet_resistance_std` REAL NOT NULL,
             `accelerator_type` TEXT NOT NULL,
             `magnet_model` INTEGER NOT NULL,
             `magnet_family`    TEXT,
             `coil_name` TEXT NOT NULL,
             `coil_type` TEXT NOT NULL,
             `measurement_type` TEXT NOT NULL,
             `n_turns_normal` INTEGER NOT NULL,
             `radius1_normal` REAL NOT NULL,
             `radius2_normal` REAL NOT NULL,
             `n_turns_bucked` INTEGER NOT NULL,
             `radius1_bucked` REAL NOT NULL,
             `radius2_bucked` REAL NOT NULL,
             `coil_comments` TEXT NOT NULL,
             `comments` TEXT NOT NULL,
             `main_harmonic`    REAL,
             `normalization_radius` REAL NOT NULL,
             `angle` REAL NOT NULL,
             `magnetic_center_x` REAL NOT NULL,
             `magnetic_center_y` REAL NOT NULL,
             `temperature_magnet`    REAL,
             `temperature_water`    REAL,
             `read_data` TEXT NOT NULL,
             `raw_curve` TEXT NOT NULL)"""

            _create_sets_table = """CREATE TABLE `sets_of_measurements` (
             `id`    INTEGER NOT NULL,
             `magnet_name`    TEXT NOT NULL,
             `magnet_family`    TEXT,
             `date`    TEXT NOT NULL,
             `hour_0`    TEXT NOT NULL,
             `hour_f`    TEXT NOT NULL,
             `collection_type`    TEXT NOT NULL,
             `n_measurements`    INTEGER NOT NULL,
             `id_0`    INTEGER NOT NULL,
             `id_f`    INTEGER NOT NULL,
             `current_min`    REAL NOT NULL,
             `current_max`    REAL NOT NULL,
             `comments`    TEXT NOT NULL,
             PRIMARY KEY(`id`) )"""

            _create_failures_table = """CREATE TABLE `failures` (
             `id`    INTEGER NOT NULL,
             `magnet_name`    TEXT NOT NULL,
             `date`    TEXT NOT NULL,
             `hour`    TEXT NOT NULL,
             `type`    INTEGER NOT NULL,
             `description`    INTEGER NOT NULL,
             PRIMARY KEY(`id`) )"""

            _cur.execute(_create_table)
            _cur.execute(_create_sets_table)
            _cur.execute(_create_failures_table)

        _con.close()

    def db_save_measurement(self):
        """
        Saves measurement log into database; All values are in SI units
        """
        try:
            _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
            _cur = _con.cursor()

            _date_name = time.strftime("%y%m%d", time.localtime())
            _hour_name = time.strftime("%H%M%S", time.localtime())

            _disable_ps_interlock = self.get_value(self.data_settings,
                                                   'disable_ps_interlock', int)

            _magnet_model = self.get_value(self.measurement_settings,
                                           'magnet_model', int)
            if _magnet_model == 0:
                _magnet_type = 'X'
                _angle = 0
            elif _magnet_model in [1, 5, 6]:
                _magnet_type = 'D'
                _angle = self.App.myapp.averageAngle[0]
            elif _magnet_model == 2:
                _magnet_type = 'Q'
                _angle = self.App.myapp.averageAngle[1]
            elif _magnet_model == 3:
                _magnet_type = 'S'
                _angle = self.App.myapp.averageAngle[2]
            elif _magnet_model == 4:
                _magnet_type = 'K'
                _angle = self.App.myapp.averageAngle[1]

            _accelerator_type = self.get_value(self.measurement_settings,
                                               'accelerator_type', str)
            if _accelerator_type == 'Booster':
                _accelerator_name = 'BOB'
            elif _accelerator_type == 'Storage Ring':
                _accelerator_name = 'BOA'

            if _disable_ps_interlock:
                _main_current = 0
            else:
                _main_current = self.get_value(self.ps_settings,
                                               'Current Setpoint', float)
            _trim_coil_type = self.get_value(self.measurement_settings,
                                             'trim_coil_type', int)

            _magnet_name = self.get_value(self.measurement_settings,
                                          'name', str)
            _magnet_family = self.get_value(self.measurement_settings,
                                            'magnet_family')
            _filename = (_magnet_name + '_' + _magnet_type + '_' +
                         _accelerator_name + '_' +
                         str(_main_current).zfill(5) + 'A_' + _date_name +
                         '_' + _hour_name + '.dat')
            _date = time.strftime("%d/%m/%Y", time.localtime())
            _hour = time.strftime("%H:%M:%S", time.localtime())
            _operator = self.get_value(self.measurement_settings, 'operator',
                                       str)
            _software_version = self.get_value(self.measurement_settings,
                                               'software_version', str)
            _bench = self.get_value(self.data_settings, 'bench', int)
            _temperature = (
                self.get_value(self.measurement_settings, 'temperature',
                               float))
            _rotation_motor_speed = (
                self.get_value(self.data_settings, 'rotation_motor_speed',
                               float))
            _rotation_motor_acceleration = (
                self.get_value(self.data_settings,
                               'rotation_motor_acceleration', float))
            _coil_rotation_direction = (
                self.get_value(self.measurement_settings,
                               'coil_rotation_direction', str))
            _integrator_gain = (
                self.get_value(self.data_settings, 'integrator_gain', int))
            _trigger_ref = (
                self.get_value(self.coil_settings, 'trigger_ref', int))
            _n_integration_points = (
                self.get_value(self.data_settings, 'n_integration_points',
                               int))
            _n_turns = (
                self.get_value(self.data_settings, 'total_number_of_turns',
                               int))
            _n_collections = (
                self.get_value(self.measurement_settings, 'n_collections',
                               int))
            _analisys_interval = (
                self.get_value(self.measurement_settings, 'analisys_interval',
                               str))
            _main_coil_current_avg = 0
            _main_coil_current_std = 0
            _ch_coil_current_avg = 0
            _ch_coil_current_std = 0
            _cv_coil_current_avg = 0
            _cv_coil_current_std = 0
            _qs_coil_current_avg = 0
            _qs_coil_current_std = 0
            _trim_coil_current_avg = 0
            _trim_coil_current_std = 0
            _main_coil_volt_avg = 0
            _main_coil_volt_std = 0
            _magnet_resistance_avg = 0
            _magnet_resistance_std = 0
            if not _disable_ps_interlock:
                _main_coil_current_avg = (
                    self.get_value(self.aux_settings,
                                   'main_current_array').mean()[0])
                _main_coil_current_std = (
                    self.get_value(self.aux_settings,
                                   'main_current_array').std()[0])
                if _trim_coil_type == 0:
                    _trim_coil_current_avg = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').mean()[0])
                    _trim_coil_current_std = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').std()[0])
                elif _trim_coil_type == 1:
                    _ch_coil_current_avg = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').mean()[0])
                    _ch_coil_current_std = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').std()[0])
                elif _trim_coil_type == 2:
                    _cv_coil_current_avg = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').mean()[0])
                    _cv_coil_current_std = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').std()[0])
                elif _trim_coil_type == 3:
                    _qs_coil_current_avg = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').mean()[0])
                    _qs_coil_current_std = (
                        self.get_value(self.aux_settings,
                                       'secondary_current_array').std()[0])
                if self.App.myapp.ui.chb_voltage.isChecked():
                    _main_coil_volt_avg = (
                        self.get_value(self.aux_settings,
                                       'main_voltage_array').mean()[0])
                    _main_coil_volt_std = (
                        self.get_value(self.aux_settings,
                                       'main_voltage_array').std()[0])
                    _magnet_resistance_avg = (
                        _main_coil_volt_avg / _main_coil_current_avg)
                    _magnet_resistance_std = (
                        (1/_main_coil_current_avg) * (_main_coil_volt_std**2 + (_main_coil_volt_avg**2/_main_coil_current_avg**2) * _main_coil_current_std**2)**0.5)
            _coil_name = self.get_value(self.coil_settings, 'coil_name', str)
            _coil_type = self.get_value(self.coil_settings, 'coil_type', str)
            _measurement_type = (
                self.get_value(self.measurement_settings,
                               'measurement_type', str))
            _n_turns_normal = (
                self.get_value(self.coil_settings, 'n_turns_normal', int))
            _radius1_normal = (
                self.get_value(self.coil_settings, 'radius1_normal', float))
            _radius2_normal = (
                self.get_value(self.coil_settings, 'radius2_normal', float))
            _n_turns_bucked = (
                self.get_value(self.coil_settings, 'n_turns_bucked', int))
            _radius1_bucked = (
                self.get_value(self.coil_settings, 'radius1_bucked', float))
            _radius2_bucked = (
                self.get_value(self.coil_settings, 'radius2_bucked', float))
            _coil_comments = (
                self.get_value(self.coil_settings, 'comments', str))
            _comments = (
                self.get_value(self.measurement_settings, 'comments', str))
            _main_harmonic = self.App.myapp.main_harmonic()
            _norm_radius = (
                self.get_value(self.measurement_settings, 'norm_radius',
                               float))
            _angle = round(_angle, 9)
            # [um]
            _magnetic_center_x = (
                self.get_value(self.measurement_settings, 'magnetic_center_x',
                               float))
            # [um]
            _magnetic_center_y = (
                self.get_value(self.measurement_settings,
                               'magnetic_center_y', float))
            _temperature_magnet = getattr(self.App.myapp, 'temperature_magnet')
            _temperature_water = getattr(self.App.myapp, 'temperature_water')
            _read_data = self.get_read_data()
            _raw_curve = self.get_raw_curve()

            _db_values = (None, _magnet_name, _filename, _date, _hour,
                          _operator, _software_version, _bench,
                          _temperature, _rotation_motor_speed,
                          _rotation_motor_acceleration,
                          _coil_rotation_direction,
                          _integrator_gain, _trigger_ref,
                          _n_integration_points, _n_turns,
                          _n_collections, _analisys_interval,
                          _main_current, _main_coil_current_avg,
                          _main_coil_current_std,
                          _ch_coil_current_avg, _ch_coil_current_std,
                          _cv_coil_current_avg, _cv_coil_current_std,
                          _qs_coil_current_avg, _qs_coil_current_std,
                          _trim_coil_current_avg, _trim_coil_current_std,
                          _main_coil_volt_avg, _main_coil_volt_std,
                          _magnet_resistance_avg, _magnet_resistance_std,
                          _accelerator_type, _magnet_model, _magnet_family,
                          _coil_name, _coil_type, _measurement_type,
                          _n_turns_normal, _radius1_normal, _radius2_normal,
                          _n_turns_bucked, _radius1_bucked, _radius2_bucked,
                          _coil_comments, _comments, _main_harmonic,
                          _norm_radius, _angle,
                          _magnetic_center_x, _magnetic_center_y,
                          _temperature_magnet, _temperature_water,
                          _read_data, _raw_curve)

            _l = []
            [_l.append('?') for _ in range(len(_db_values))]
            _l = '(' + ','.join(_l) + ')'
            _cur.execute(('INSERT INTO measurements VALUES ' + _l), _db_values)
            _con.commit()
            _con.close()
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def db_load_measurement(self, _id=None):
        """
        Load measurement from database, returns selected measurements
        """
        _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        _cur = _con.cursor()
        #loads last measurement:
        if _id is None or _id is False:
            _cur.execute('SELECT * FROM measurements WHERE '
                         'id = (SELECT MAX(id) FROM measurements)')
        #loads measurement from id:
        else:
            _cur.execute('SELECT * FROM measurements WHERE id = ?', (_id,))
        _db_entry = _cur.fetchall()
        _con.close()
        return _db_entry

    def db_load_measurements(self, _id=None, magnet_name=None, filename=None,
                             date=None, hour=None, operator=None,
                             magnet_model=None, magnet_family=None,
                             coil_name=None, bench=None, software_version=None,
                             temperature=None, integrator_gain=None,
                             main_current=None, accelerator_type=None,
                             comments=None, trigger_ref=None, angle=None,
                             magnetic_center_x=None, magnetic_center_y=None):
        _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        _cur = _con.cursor()

        _and_flag = False
        _command = 'SELECT * FROM measurements WHERE '

        if _id is not None and _id is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(_id) == int or type(_id) == float:
                _command = _command + 'id = ' + str(_id) + ' '
            elif type(_id) == str:
                _command = _command + 'id ' + _id + ' '

        if magnet_name is not None and magnet_name is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'magnet_name = "' + magnet_name + '" '

        if magnet_family is not None and magnet_name is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'magnet_family = "' + magnet_family + '" '

        if filename is not None and filename is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'filename = "' + filename + '" '

        if date is not None and date is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'date = "' + date + '" '

        if hour is not None and hour is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'hour = "' + hour + '" '

        if operator is not None and operator is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'operator = "' + operator + '" '

        if magnet_model is not None and magnet_model is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'magnet_model = ' + str(magnet_model) + ' '

        if coil_name is not None and coil_name is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'coil_name = "' + coil_name + '" '

        if bench is not None and bench is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'bench = ' + str(bench) + ' '

        if software_version is not None and software_version is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = (_command + 'software_version = "' + software_version +
                        '" ')

        if accelerator_type is not None and accelerator_type is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = (_command + 'accelerator_type = "' + accelerator_type +
                        '" ')

        if comments is not None and comments is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'comments = "' + comments + '" '

        if temperature is not None and temperature is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(temperature) == int or type(temperature) == float:
                _command = _command + 'temperature = ' + str(temperature) + ' '
            elif type(temperature) == str:
                _command = _command + 'temperature ' + temperature + ' '

        if integrator_gain is not None and integrator_gain is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(integrator_gain) == int or type(integrator_gain) == float:
                _command = (_command + 'integrator_gain = ' +
                            str(integrator_gain) + ' ')
            elif type(integrator_gain) == str:
                _command = (_command + 'integrator_gain ' + integrator_gain +
                            ' ')

        if main_current is not None and main_current is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(main_current) == int or type(main_current) == float:
                _command = (_command + 'main_current = ' + str(main_current) +
                            ' ')
            elif type(main_current) == str:
                _command = _command + 'main_current ' + main_current + ' '

        if trigger_ref is not None and trigger_ref is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(trigger_ref) == int or type(trigger_ref) == float:
                _command = _command + 'trigger_ref = ' + str(trigger_ref) + ' '
            elif type(trigger_ref) == str:
                _command = _command + 'trigger_ref ' + angle + ' '

        if angle is not None and angle is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(angle) == int or type(angle) == float:
                _command = _command + 'angle = ' + str(angle) + ' '
            elif type(angle) == str:
                _command = _command + 'angle ' + angle + ' '

        if magnetic_center_x is not None and magnetic_center_x is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if any([isinstance(magnetic_center_x, int),
                    isinstance(magnetic_center_x, float)]):
                _command = (_command + 'magnetic_center_x = ' +
                            str(magnetic_center_x) + ' ')
            elif isinstance(magnetic_center_x, str):
                _command = (_command + 'magnetic_center_x ' +
                            magnetic_center_x + ' ')

        if magnetic_center_y is not None and magnetic_center_y is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if any([type(magnetic_center_y) == int,
                    type(magnetic_center_y) == float]):
                _command = (_command + 'magnetic_center_y = ' +
                            str(magnetic_center_y) + ' ')
            elif type(magnetic_center_y) == str:
                _command = (_command + 'magnetic_center_y ' +
                            magnetic_center_y + ' ')

        _cur.execute(_command)
        _db_entry = _cur.fetchall()
        _con.close()
        return _db_entry

    def db_load_sets_of_measurements(self, _id=None, magnet_name=None,
                                     magnet_family=None, date=None,
                                     hour_0=None, hour_f=None,
                                     collection_type=None, id_0=None,
                                     id_f=None, current_min=None,
                                     current_max=None, comments=None):
        _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        _cur = _con.cursor()

        _and_flag = False
        _command = 'SELECT * FROM sets_of_measurements WHERE '

        if _id is not None and _id is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(_id) == int or type(_id) == float:
                _command = _command + 'id = ' + str(_id) + ' '
            elif type(_id) == str:
                _command = _command + 'id ' + _id + ' '

        if magnet_name is not None and magnet_name is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'magnet_name = "' + magnet_name + '" '

        if magnet_family is not None and magnet_name is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'magnet_family = "' + magnet_family + '" '

        if date is not None and date is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'date = "' + date + '" '

        if hour_0 is not None and hour_0 is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'hour_0 = "' + hour_0 + '" '

        if hour_f is not None and hour_f is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'hour_f = "' + hour_f + '" '

        if collection_type is not None and collection_type is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = (_command + 'collection_type = "' + collection_type +
                        '" ')

        if id_0 is not None and id_0 is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(id_0) == int or type(id_0) == float:
                _command = _command + 'id_0 = ' + str(id_0) + ' '
            elif type(id_0) == str:
                _command = _command + 'id_0 ' + id_0 + ' '

        if id_f is not None and id_f is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(id_f) == int or type(id_f) == float:
                _command = _command + 'id_f = ' + str(id_f) + ' '
            elif type(id_f) == str:
                _command = _command + 'id_f ' + id_f + ' '

        if current_min is not None and current_min is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(current_min) == int or type(current_min) == float:
                _command = _command + 'current_min = ' + str(current_min) + ' '
            elif type(current_min) == str:
                _command = _command + 'current_min ' + current_min + ' '

        if current_max is not None and current_max is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(current_max) == int or type(current_max) == float:
                _command = _command + 'current_max = ' + str(current_max) + ' '
            elif type(current_max) == str:
                _command = _command + 'current_max ' + current_max + ' '

        if comments is not None and comments is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'comments = "' + comments + '" '

    def db_load_failures(self, _id=None, magnet_name=None, date=None,
                         hour=None, _type=None):
        _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        _cur = _con.cursor()

        _and_flag = False
        _command = 'SELECT * FROM sets_of_measurements WHERE '

        if _id is not None and _id is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(_id) == int or type(_id) == float:
                _command = _command + 'id = ' + str(_id) + ' '
            elif type(_id) == str:
                _command = _command + 'id ' + _id + ' '

        if magnet_name is not None and magnet_name is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'magnet_name = "' + magnet_name + '" '

        if date is not None and date is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'date = "' + date + '" '

        if hour is not None and hour is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            _command = _command + 'hour = "' + hour + '" '

        if _type is not None and _type is not False:
            if _and_flag:
                _command = _command + 'AND '
            _and_flag = True
            if type(_type) == int or type(_type) == float:
                _command = _command + 'type = ' + str(_type) + ' '
            elif type(_type) == str:
                _command = _command + 'type ' + _type + ' '

    def db_save_set(self, n_measurements, collection_type,
                    current_min, current_max):
        """
        Save data to sets_of_measurements table
        """
        try:
            _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
            _cur = _con.cursor()

            _magnet_name = self.get_value(self.measurement_settings, 'name',
                                          str)
            _magnet_family = self.get_value(self.measurement_settings,
                                            'magnet_family')
            _date = time.strftime("%d/%m/%Y", time.localtime())
            _n_measurements = n_measurements
            _cur.execute('SELECT id, hour FROM measurements WHERE '
                         'id = (SELECT MAX(id) FROM measurements)')
            _ans = _cur.fetchall()[0]
            _id_f = _ans[0]
            _hour_f = _ans[1]
            _id_0 = _id_f - (_n_measurements - 1)
            _cur.execute('SELECT hour FROM measurements WHERE id = ?',
                         (_id_0,))
            _hour_0 = _cur.fetchall()[0][0]
            _current_min = current_min
            _current_max = current_max
            _comments = self.get_value(self.measurement_settings, 'comments',
                                       str)

            if collection_type == 0:
                _collection_type = "Series of measurements"
            elif collection_type == 1:
                _collection_type = "Automatic power supply"
            elif collection_type == 2:
                _collection_type = "Automatic secondary power supply"

            _db_values = (None, _magnet_name, _magnet_family, _date, _hour_0,
                          _hour_f, _collection_type, _n_measurements, _id_0,
                          _id_f, _current_min, _current_max, _comments)

            _l = []
            [_l.append('?') for _ in range(len(_db_values))]
            _l = '(' + ','.join(_l) + ')'
            _cur.execute(('INSERT INTO sets_of_measurements VALUES ' + _l),
                         _db_values)
            _con.commit()
            _con.close()
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def db_save_failure(self, error_type):
        """
        Save data to failures table
        """
        try:
            _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
            _cur = _con.cursor()

            _magnet_name = self.get_value(self.measurement_settings, 'name',
                                          str)
            _date = time.strftime("%d/%m/%Y", time.localtime())
            _hour = time.strftime("%H:%M:%S", time.localtime())

            _type = error_type

            if _type == 0:
                _description = "Data not received from integrator"
            elif _type == 1:
                _description = "Main multipole standard deviation too high"
            elif _type == 2:
                _description = "Integrator tension over-range"
            elif _type == 3:
                _description = "Emergency during measurement"
            elif _type == 4:
                _description = "Could not save measurement to database"
            elif _type == 5:
                _description = "Could not save log file"
            elif _type == 6:
                _description = "Could not set the power supply current"
            elif _type == 7:
                _description = "No compressed air flux"

            _db_values = (None, _magnet_name, _date, _hour, _type,
                          _description)

            _l = []
            [_l.append('?') for _ in range(len(_db_values))]
            _l = '(' + ','.join(_l) + ')'
            _cur.execute(('INSERT INTO failures VALUES ' + _l), _db_values)
            _con.commit()
            _con.close()
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def get_read_data(self):
        """
        Retrieves read data from current measurement and returns as string
        (old log file format)
        """
        _n_rows = self.App.myapp.ui.tw_multipoles_table.rowCount()
        _magnet_type = self.get_value(self.measurement_settings,
                                      'magnet_model', int)
        # convert to mm
        _norm_radius = self.get_value(self.measurement_settings,
                                      'norm_radius', float)*1000
        if _magnet_type >= 4:
            _norm = 'Sn'
            if _magnet_type == 4:
                _magnet_type = 2
            elif _magnet_type == 5:
                _magnet_type = 1
        else:
            _norm = 'Nn'
        _str = ('n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\t'
                'std_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\t'
                'avg_angle(rad)  \tstd_angle(rad)  \tavg_Nn/' + _norm +
                'Magnet@' + str(_norm_radius) + "mm\tstd_Nn/" + _norm +
                "Magnet@" + str(_norm_radius) + "mm\tavg_Sn/" + _norm +
                "Magnet@" + str(_norm_radius) + "mm\tstd_Sn/" + _norm +
                "Magnet@" + str(_norm_radius) + "mm\n")

        for i in range(_n_rows):
            _str = _str + str('{0:<4d}'.format(i+1)) + '\t'
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.averageN.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.stdN.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.averageS.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.stdS.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.averageMod.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.stdMod.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.averageAngle.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.stdAngle.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.averageN_norm.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.stdN_norm.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.averageS_norm.values[i])) + '\t')
            _str = (_str + str('{0:^+18.6e}'.format(
                self.App.myapp.stdS_norm.values[i])) + '\n')

        return _str

    def load_read_data(self, _id=None):
        """
        Load read data from database entry id and returns as string
        (reads from last entry if id = None)
        """
        _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        _cur = _con.cursor()
        if _id is None or _id is False:
            _cur.execute('SELECT read_data FROM measurements WHERE '
                         'id = (SELECT MAX(id) FROM measurements)')
        else:
            _cur.execute('SELECT read_data FROM measurements WHERE id = ?',
                         (_id,))
        _read_data = _cur.fetchall()[0][0]
        _con.close()
        return _read_data

    def get_raw_curve(self):
        """
        Retrieves raw curve from current measurement and returns as string
        (old log file format)
        """
        _n_of_turns = self.get_value(self.data_settings,
                                     'total_number_of_turns', int)
        _n_integration_points = self.get_value(self.data_settings,
                                               'n_integration_points', int)
        _str = ''
        for i in range(_n_of_turns):
            _str = _str + '{:#^18}'.format(' Turn_' + str(i+1) + '')
        _str = _str + '\n' + self.App.myapp.df_rawcurves.to_csv(sep='\t',
                                                                header=False,
                                                                index=False)
        return _str

    def load_raw_curve(self, _id=None):
        """
        Load raw curve from database entry and returns as string
        (reads from last entry if id = None)
        """
        _con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        _cur = _con.cursor()
        if _id is None or _id is False:
            _cur.execute('SELECT raw_curve FROM measurements WHERE '
                         'id = (SELECT MAX(id) FROM measurements)')
        else:
            _cur.execute('SELECT raw_curve FROM measurements WHERE id = ?',
                         (_id,))
        _raw_curve = _cur.fetchall()[0][0]
        _con.close()
        return _raw_curve

    def save_log_file(self, _id=None, path=None):
        """
        Saves log file from database entry id (last entry if id = None),
        similar to old log file format
        """
        # loads last measurement
        _measurement_entry = self.db_load_measurement(_id)[0]
        #Configuration Data
        _id = _measurement_entry[0]
        _magnet_name = _measurement_entry[1]
        _filename = _measurement_entry[2]
        _date = _measurement_entry[3]
        _hour = _measurement_entry[4]
        _operator = _measurement_entry[5]
        _software_version = _measurement_entry[6]
        _bench = _measurement_entry[7]
        _temperature = _measurement_entry[8]
        _integrator_gain = _measurement_entry[12]
        _n_integration_points = _measurement_entry[14]
        _rotation_motor_speed = _measurement_entry[9]
        _rotation_motor_acceleration = _measurement_entry[10]
        _n_collections = _measurement_entry[16]
        _n_turns = _measurement_entry[15]
        _analisys_interval = _measurement_entry[17]
        _coil_rotation_direction = _measurement_entry[11]
        _main_coil_current_avg = _measurement_entry[19]
        _main_coil_current_std = _measurement_entry[20]
        _ch_coil_current_avg = _measurement_entry[21]
        _ch_coil_current_std = _measurement_entry[22]
        _cv_coil_current_avg = _measurement_entry[23]
        _cv_coil_current_std = _measurement_entry[24]
        _qs_coil_current_avg = _measurement_entry[25]
        _qs_coil_current_std = _measurement_entry[26]
        _trim_coil_current_avg = _measurement_entry[27]
        _trim_coil_current_std = _measurement_entry[28]
        _main_coil_volt_avg = _measurement_entry[29]
        _main_coil_volt_std = _measurement_entry[30]
        _magnet_resistance_avg = _measurement_entry[31]
        _magnet_resistance_std = _measurement_entry[32]
        #Rotating Coil Data
        _coil_name = _measurement_entry[36]
        _coil_type = _measurement_entry[37]
        _measurement_type = _measurement_entry[38]
        _trigger_ref = _measurement_entry[13]
        _n_turns_normal = _measurement_entry[39]
        _radius1_normal = _measurement_entry[40]
        _radius2_normal = _measurement_entry[41]
        _n_turns_bucked = _measurement_entry[42]
        _radius1_bucked = _measurement_entry[43]
        _radius2_bucked = _measurement_entry[44]
        #Comments
        _comments = _measurement_entry[46]
        #Reading data
        _read_data = _measurement_entry[54]
        _magnetic_center_x = _measurement_entry[50]
        _magnetic_center_y = _measurement_entry[51]
        #Raw data
        _raw_curve = _measurement_entry[55]

        if path is None or path is False:
            _dir = self.dir_path
        else:
            _dir = path

        try:
            with open((_dir+_filename), 'w') as f:
                f.write('########## EXCITATION CURVE'
                        ' - ROTATING COIL ##########')
                f.write('\n\n')
                f.write('### Configuration Data ###')
                f.write('\n')
                f.write('id                             \t' +
                        str(_id) + '\n')
                f.write('file                           \t' +
                        str(_filename) + '\n')
                f.write('date                           \t' +
                        str(_date) + '\n')
                f.write('hour                           \t' +
                        str(_hour) + '\n')
                f.write('operator                       \t' +
                        str(_operator) + '\n')
                f.write('software_version               \t' +
                        str(_software_version) + '\n')
                f.write('bench                          \t' +
                        str(_bench) + '\n')
                f.write('temperature(C)                 \t' +
                        str(_temperature) + '\n')
                f.write('integrator_gain                \t' +
                        str(_integrator_gain) + '\n')
                f.write('n_integration_points           \t' +
                        str(_n_integration_points) + '\n')
                f.write('velocity(rps)                  \t' +
                        str(_rotation_motor_speed) + '\n')
                f.write('acceleration(rps^2)            \t' +
                        str(_rotation_motor_acceleration) + '\n')
                f.write('n_collections                  \t' +
                        str(_n_collections) + '\n')
                f.write('n_turns                        \t' +
                        str(_n_turns) + '\n')
                f.write('analysis_interval              \t' +
                        str(_analisys_interval) + '\n')
                f.write('rotation                       \t' +
                        str(_coil_rotation_direction) + '\n')
                f.write('main_coil_current_avg(A)       \t' +
                        str('{0:+0.6e}'.format(_main_coil_current_avg)) + '\n')
                f.write('main_coil_current_std(A)       \t' +
                        str('{0:+0.6e}'.format(_main_coil_current_std)) + '\n')
                f.write('main_coil_volt_avg(V)          \t' +
                        str('{0:+0.6e}'.format(_main_coil_volt_avg)) + '\n')
                f.write('main_coil_volt_std(V)          \t' +
                        str('{0:+0.6e}'.format(_main_coil_volt_std)) + '\n')
                f.write('magnet_resistance_avg(ohm)     \t' +
                        str('{0:+0.6e}'.format(_magnet_resistance_avg)) + '\n')
                f.write('magnet_resistance_std(ohm)     \t' +
                        str('{0:+0.6e}'.format(_magnet_resistance_std)) + '\n')
                f.write('ch_coil_current_avg(A)       \t' +
                        str('{0:+0.6e}'.format(_ch_coil_current_avg)) + '\n')
                f.write('ch_coil_current_std(A)       \t' +
                        str('{0:+0.6e}'.format(_ch_coil_current_std)) + '\n')
                f.write('cv_coil_current_avg(A)       \t' +
                        str('{0:+0.6e}'.format(_cv_coil_current_avg)) + '\n')
                f.write('cv_coil_current_std(A)       \t' +
                        str('{0:+0.6e}'.format(_cv_coil_current_std)) + '\n')
                f.write('qs_coil_current_avg(A)       \t' +
                        str('{0:+0.6e}'.format(_qs_coil_current_avg)) + '\n')
                f.write('qs_coil_current_std(A)       \t' +
                        str('{0:+0.6e}'.format(_qs_coil_current_std)) + '\n')
                f.write('trim_coil_current_avg(A)   \t' +
                        str('{0:+0.6e}'.format(_trim_coil_current_avg)) + '\n')
                f.write('trim_coil_current_std(A)   \t' +
                        str('{0:+0.6e}'.format(_trim_coil_current_std)) + '\n')
                f.write('\n')
                f.write('### Rotating Coil Data ###')
                f.write('\n')
                f.write('rotating_coil_name             \t' +
                        str(_coil_name) + '\n')
                f.write('rotating_coil_type             \t' +
                        str(_coil_type) + '\n')
                # bucked ou n_bucked
                f.write('measurement_type               \t' +
                        str(_measurement_type) + '\n')
                f.write('pulse_start_collect            \t' +
                        str(_trigger_ref) + '\n')
                f.write('n_turns_main_coil              \t' +
                        str(_n_turns_normal) + '\n')
                f.write('main_coil_internal_radius(m)   \t' +
                        str(_radius1_normal) + '\n')
                f.write('main_coil_external_radius(m)   \t' +
                        str(_radius2_normal) + '\n')
                f.write('n_turns_bucked_coil            \t' +
                        str(_n_turns_bucked) + '\n')
                f.write('bucked_coil_internal_radius(m) \t' +
                        str(_radius1_bucked) + '\n')
                f.write('bucked_coil_external_radius(m) \t' +
                        str(_radius2_bucked) + '\n')
                f.write('\n')
                f.write('### Comments ###')
                f.write('\n')
                f.write('comments                       \t' +
                        str(_comments) + '\n')
                f.write('\n\n\n')
                f.write('##### Reading Data #####')
                f.write('\n\n')
                f.write(_read_data)
                f.write('\n')
                f.write('magnetic_center_x(um) \t' +
                        str(_magnetic_center_x) + '\n')
                f.write('magnetic_center_y(um) \t' +
                        str(_magnetic_center_y) + '\n')
                f.write('\n\n')
                f.write('##### Raw Data Stored(V.s) #####')
                f.write('\n\n')
                f.write(_raw_curve)
            return True
        except Exception:
            return False

    def load_settings(self):
        try:
            self.data_settings = None
            _file = self.dir_path + self.settings_file
            print(_file)
            self.data_settings = pd.read_csv(_file, comment='#',
                                             delimiter='\t',
                                             names=['datavars', 'datavalues'],
                                             dtype={'datavars': str},
                                             index_col='datavars')
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def save_settings(self):
        try:
            _file = self.dir_path + self.settings_file
            fname = open(_file, 'w')
            fname.write('# Rotating Coil Main Parameters\n')
            fname.write('# Insert the variable name and value separated by '
                        'tab.\n')
            fname.write('# Commented lines are ignored.\n\n')

            for i in range(len(self.data_settings)):
                fname.write(self.data_settings.index[i] + '\t' +
                            str(self.data_settings.iloc[i].get_values()[0]) +
                            '\n')
            fname.close()

            return True
        except Exception:
            return False

    def load_coil(self, filename):
        try:
            self.coil_settings = pd.read_csv(filename, comment='#',
                                             delimiter='\t',
                                             names=['datavars', 'datavalues'],
                                             dtype={'datavars': str},
                                             index_col='datavars')
            return True
        except Exception:
            return False

    def save_coil(self, filename):
        try:
            fname = open(filename, 'w')
            fname.write('# Coil Parameters\n')
            fname.write('# Insert the variable name and value separated by '
                        'tab.\n')
            fname.write('# Commented lines are ignored.\n\n')

            for i in range(len(self.coil_settings)):
                fname.write(self.coil_settings.index[i] + '\t' +
                            str(self.coil_settings.loc[
                                self.coil_settings.index[i]].get_values()[0]) +
                            '\n')
            fname.close()

            return True
        except Exception:
            return False

    def load_ps(self, filename, secondary=False):
        try:
            if not secondary:
                self.ps_settings = pd.read_csv(filename, comment='#',
                                               delimiter='\t',
                                               names=['datavars',
                                                      'datavalues'],
                                               dtype={'datavars': str},
                                               index_col='datavars')
                _df = self.ps_settings
            else:
                self.ps_settings_2 = pd.read_csv(filename, comment='#',
                                                 delimiter='\t',
                                                 names=['datavars',
                                                        'datavalues'],
                                                 dtype={'datavars': str},
                                                 index_col='datavars')
                _df = self.ps_settings_2
            _ps_type = self.get_value(_df, 'Power Supply Type', int)
            if _ps_type < 2:
                self.write_value(_df, 'Power Supply Type', 2)
            elif _ps_type > 6:
                self.write_value(_df, 'Power Supply Type', 6)
            return True
        except Exception:
            return False

    def save_ps(self, filename, secondary=False):
        try:
            fname = open(filename, 'w')
            fname.write('# Power Supply Parameters\n')
            fname.write('# Insert the variable name and value separated by '
                        'tab.\n')
            fname.write('# Commented lines are ignored.\n\n')

            if not secondary:
                _df = self.ps_settings
            else:
                _df = self.ps_settings_2
            for i in range(len(_df)):
                fname.write(_df.index[i] + '\t' +
                            str(_df.loc[_df.index[i]].get_values()[0]) + '\n')
            fname.close()
            return True
        except Exception:
            return False

    def measurement_df(self):
        # check if n_turns really is the total number of turns
        _n_turns = self.get_value(self.data_settings, 'total_number_of_turns',
                                  int)
        _i = (self.get_value(self.data_settings, 'remove_initial_turns', int) +
              1)
        _f = self.get_value(self.data_settings, 'remove_final_turns', int)
        try:
            if self.App.myapp.ui.chb_seriesofmeas.isChecked():
                _le_n_collections = int(
                    self.App.myapp.ui.le_n_collections.text())
            else:
                _le_n_collections = 1
        except ValueError:
            _le_n_collections = 1

        try:
            _analisys_interval = str(_i) + '-' + str(_n_turns - _f)
        except ValueError:
            _analisys_interval = '0'

        _comments = ''
        if self.get_value(self.data_settings, 'disable_alignment_interlock',
                          int):
            _comments = (_comments +
                         'Warning: Alignment interlock is disabled; '
                         'Ref_encoder_A = {0:0.6f}, Ref_encoder_B = {1:0.6f} .'
                         '\n'.format(self.get_value(self.aux_settings,
                                                    'ref_encoder_A', float),
                                     self.get_value(self.aux_settings,
                                                    'ref_encoder_B', float)))
        if self.get_value(self.data_settings, 'disable_ps_interlock', int):
            _comments = (_comments +
                         'Warning: Power supply interlock is disabled.\n')

        _magnet_family = (
            self.App.myapp.dialog.ui.cb_magnet_family.currentText())
        if _magnet_family == 'None':
            _magnet_family = None
        _datavars = ['name',
                     'operator',
                     'software_version',
                     'temperature',
                     'coil_rotation_direction',
                     'n_collections',
                     'analisys_interval',
                     'accelerator_type',
                     'magnet_model',
                     'magnet_family',
                     'measurement_type',
                     'comments',
                     'norm_radius',
                     'magnetic_center_x',
                     'magnetic_center_y',
                     'trim_coil_type']
        _datavalues = [
            self.App.myapp.dialog.ui.le_magnet_name.text().upper(),
            self.App.myapp.dialog.ui.cb_operator.currentText(),
            'v3.6',
            float(self.App.myapp.dialog.ui.le_temperature.text()),
            self.App.myapp.ui.cb_coil_rotation_direction.currentText(),
            _le_n_collections,
            _analisys_interval,
            self.App.myapp.ui.cb_accelerator_type.currentText(),
            self.App.myapp.dialog.ui.cb_magnet_model.currentIndex(),
            _magnet_family,
            'N_bucked',
            self.App.myapp.dialog.ui.te_meas_details.toPlainText() + _comments,
            # convert from mm to meter
            float(self.App.myapp.ui.le_norm_radius.text())/1000,
            0.,
            0.,
            -1]
        _df = pd.DataFrame({'datavars': _datavars,
                            'datavalues': _datavalues})
        self.measurement_settings = _df.set_index('datavars')

    def aux_df(self):
        _datavars = ['dclink_value',
                     'status_ps',
                     'status_ps_2',
                     'actual_current',
                     'actual_current_2',
                     'main_current_array',
                     'secondary_current_array',
                     'main_voltage_array',
                     'magnet_resistance_avg',
                     'magnet_resistance_std',
                     'ref_encoder_A',
                     'ref_encoder_B']
        _datavalues = [90,
                       0,
                       0,
                       0.,
                       0.,
                       pd.DataFrame([]),
                       pd.DataFrame([]),
                       pd.DataFrame([]),
                       0.,
                       0.,
                       0.,
                       0.]

        _df = pd.DataFrame({'datavars': _datavars,
                            'datavalues': _datavalues})
        self.aux_settings = _df.set_index('datavars')

    def coil_df(self):
        _datavars = ['coil_name',
                     'n_turns_normal',
                     'radius1_normal',
                     'radius2_normal',
                     'n_turns_bucked',
                     'radius1_bucked',
                     'radius2_bucked',
                     'trigger_ref',
                     'coil_type',
                     'comments']
        _datavalues = [self.App.myapp.ui.le_coil_name.text(),
                       self.App.myapp.ui.le_n_turns_normal.text(),
                       self.App.myapp.ui.le_radius1_normal.text(),
                       self.App.myapp.ui.le_radius2_normal.text(),
                       self.App.myapp.ui.le_n_turns_bucked.text(),
                       self.App.myapp.ui.le_radius1_bucked.text(),
                       self.App.myapp.ui.le_radius2_bucked.text(),
                       self.App.myapp.ui.le_trigger_ref.text(),
                       self.App.myapp.ui.cb_coil_type.currentText(),
                       self.App.myapp.ui.te_comments.toPlainText()]
        _df = pd.DataFrame({'datavars': _datavars,
                            'datavalues': _datavalues})
        self.coil_settings = _df.set_index('datavars')

    def ps_df(self, secondary=False):
        _datavars = ['Power Supply Name',
                     'Power Supply Type',
                     'Current Setpoint',
                     'Amplitude Step',
                     'Delay/Step',
                     'Sinusoidal Amplitude',
                     'Sinusoidal Offset',
                     'Sinusoidal Frequency',
                     'Sinusoidal N cycles',
                     'Sinusoidal Initial Phase',
                     'Sinusoidal Final Phase',
                     'Damped Sinusoidal Amplitude',
                     'Damped Sinusoidal Offset',
                     'Damped Sinusoidal Frequency',
                     'Damped Sinusoidal N cycles',
                     'Damped Sinusoidal Phase Shift',
                     'Damped Sinusoidal Final Phase',
                     'Damped Sinusoidal Damping',
                     'Damped Sinusoidal2 Amplitude',
                     'Damped Sinusoidal2 Offset',
                     'Damped Sinusoidal2 Frequency',
                     'Damped Sinusoidal2 N cycles',
                     'Damped Sinusoidal2 Phase Shift',
                     'Damped Sinusoidal2 Final Phase',
                     'Damped Sinusoidal2 Damping',
                     'Trapezoidal Offset',
                     'Trapezoidal Array',
                     'Maximum Current',
                     'Minimum Current',
                     'Automatic Setpoints',
                     'Kp',
                     'Ki',
                     'DCCT Head']
        _datavalues = ['',
                       3,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0.0,
                       0,
                       0.0,
                       0.0,
                       '',
                       0.0,
                       0.0,
                       '',
                       0.0,
                       0.0,
                       2]
        _df = pd.DataFrame({'datavars': _datavars,
                            'datavalues': _datavalues})
        if not secondary:
            self.ps_settings = _df.set_index('datavars')
        if secondary:
            self.ps_settings_2 = _df.set_index('datavars')

    def get_value(self, dataframe, index, value_type=None):
        """
        get value from dataframe, value_types: int,float,str,None
        (returns same type as in df)
        """
        if value_type == int:
            return int(dataframe.loc[index].astype(float).get_values()[0])
        if value_type == float:
            return dataframe.loc[index].astype(float).get_values()[0]
        if value_type == str:
            return dataframe.loc[index].astype(str).get_values()[0]
        else:
            return dataframe.loc[index].get_values()[0]

    def write_value(self, dataframe, index, value, numeric=False):
        """
        write values in dataframe
        """
        if numeric:
            try:
                float(value)
            except Exception:
                raise TypeError("'{0}' value ({1}) must be a number".format(
                    index, value))
                return
        dataframe.loc[index].values[0] = value


class flags(object):
    def __init__(self):
        self.coil_ref_flag = False
        self.devices_connected = False
        self.emergency = False
        self.stop_all = False


class communication(object):
    def __init__(self):
        # Connection Tab
        self.display = None
        self.parker = None
        self.fdi = None
        self.agilent34970a = None
        self.drs = None
