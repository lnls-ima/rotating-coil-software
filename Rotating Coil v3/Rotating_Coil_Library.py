'''
Created on 17 de nov de 2017

@author: James Citadini
'''
#import numpy as np
import os
import time
import sqlite3
import pandas as pd
from io import StringIO


# Biblioteca de variaveis globais utilizadas
class RotatingCoil_Library(object):
    def __init__(self):
#         self.dir_path = 'F:\\Arq-James\\5 - Projetos\\1 - Desenvolvimento de Software\\Rotating Coil v3\\'
        self.dir_path = os.path.dirname(os.path.abspath(__file__)) + '\\'
        self.settings_file = 'rc_settings.dat'
        self.load_settings()
        
        self.App = None
        self.flags = flags()
        self.vars = interface_vars()
        self.comm = communication()
        
        self.con = sqlite3.connect(self.dir_path + 'measurements_data.db')
        self.cur = self.con.cursor()
        self.db_create_table()
        
    def db_create_table(self):
        """
        Creates measurements table if it doesn't exists in db file
        """
        self.cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='measurements';""")
        if not len(self.cur.fetchall()):
            _create_table = """CREATE TABLE "measurements" ( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\
             `name` TEXT NOT NULL,\
             `filename` TEXT NOT NULL,\
             `date` TEXT NOT NULL,\
             `hour` TEXT NOT NULL,\
             `operator` TEXT NOT NULL,\
             `software_version` TEXT NOT NULL,\
             `temperature` REAL NOT NULL,\
             `rotation_motor_speed` REAL NOT NULL,\
             `rotation_motor_acceleration` REAL NOT NULL,\
             `driver_direction` TEXT NOT NULL,\
             `integrator_gain` INTEGER NOT NULL,\
             `trigger_ref` INTEGER NOT NULL,\
             `n_integration_points` INTEGER NOT NULL,\
             `n_turns` INTEGER NOT NULL,\
             `n_collections` INTEGER NOT NULL,\
             `analisys_interval` INTEGER NOT NULL,\
             `main_current` REAL NOT NULL,\
             `main_coil_current_avg` REAL NOT NULL,\
             `main_coil_current_std` REAL NOT NULL,\
             `ch_coil_current_avg` REAL NOT NULL,\
             `ch_coil_current_std` REAL NOT NULL,\
             `cv_coil_current_avg` REAL NOT NULL,\
             `cv_coil_current_std` REAL NOT NULL,\
             `qs_coil_current_avg` REAL NOT NULL,\
             `qs_coil_current_std` REAL NOT NULL,\
             `trim_coil_current_avg` REAL NOT NULL,\
             `trim_coil_current_std` REAL NOT NULL,\
             `main_coil_volt_avg` REAL NOT NULL,\
             `main_coil_volt_std` REAL NOT NULL,\
             `magnet_resistance_avg` REAL NOT NULL,\
             `magnet_resistance_std` REAL NOT NULL,\
             `bench` INTEGER NOT NULL,\
             `accelerator_type` TEXT NOT NULL,\
             `magnet_model` TEXT NOT NULL,\
             `coil_name` TEXT NOT NULL,\
             `coil_type` TEXT NOT NULL,\
             `measurement_type` TEXT NOT NULL,\
             `n_turns_normal` INTEGER NOT NULL,\
             `radius1_normal` REAL NOT NULL,\
             `radius2_normal` REAL NOT NULL,\
             `n_turns_bucked` INTEGER NOT NULL,\
             `radius1_bucked` REAL NOT NULL,\
             `radius2_bucked` REAL NOT NULL,\
             `coil_comments` TEXT NOT NULL,\
             `comments` TEXT NOT NULL,\
             `normalization_radius` REAL NOT NULL,\
             `magnetic_center_x` REAL NOT NULL,\
             `magnetic_center_y` REAL NOT NULL,\
             `read_data` TEXT NOT NULL,\
             `raw_curve` TEXT NOT NULL )"""
            self.cur.execute(_create_table)
    
    def db_save_measurement(self):
        """
        Saves measurement log into database
        """
        _name = str(self.App.myapp.ui.le_magnet_name.text())
        _name = _name.upper()
        #pass _arquivo as parameter
#         _arquivo = QtWidgets.QFileDialog.getSaveFileName(self.App.myapp, 'Save File - Coleta Manual', _nome,'Data files')
        
        _date_name = time.strftime("%y%m%d", time.localtime())
        _hour_name = time.strftime("%H%M%S", time.localtime())
        
        _magnet_type = self.App.myapp.ui.cb_magnet_model.currentIndex()
        if _magnet_type == 0:
            _magnet_type = 'X'
        elif _magnet_type == 1:
            _magnet_type = 'D'
        elif _magnet_type == 2:
            _magnet_type = 'Q'
        elif _magnet_type == 3:
            _magnet_type = 'S'
        elif _magnet_type == 4:
            _magnet_type = 'K'
            
            
#         _accelerator_type = self.App.myapp.ui.cb_accelerator_type.currentIndex()
#         
#         if _accelerator_type == 0: #Booster
#             _accelerator_type = 'BOB'
#         elif _accelerator_type == 1: #Storage Ring
#             _accelerator_type = 'BOA'
        
#         _name = self.App.myapp.ui.le_magnet_name.text().upper()
#         _filename = _name + '_' + _magnet_type + '_' + _accelerator_type + '_' + str(Corrente_Principal).zfill(5) + 'A_' + _date_name + '_' + _hour_name + '.dat'
        _date = time.strftime("%d/%m/%Y", time.localtime())
        _hour = time.strftime("%H:%M:%S", time.localtime())
#         _operator = self.App.myapp.ui.cb_operator.text()
        _software_version = 'v3'
#         _temperature = float(self.App.myapp.ui.le_temperature.text()) #Automatic Reading?
#         _rotation_motor_speed = self.get_value(self.data_settings, 'rotation_motor_speed', float)
#         _rotation_motor_acceleration = self.get_value(self.data_settings, 'rotation_motor_acceleration', float)
#         _driver_direction = self.App.myapp.ui.cb_driver_direction.text()
#         _integrator_gain = self.get_value(self.data_settings, 'integrator_gain', int)    
#         _trigger_ref = self.get_value(self.coil_settings, 'trigger_ref', int)
#         _n_integration_points = self.get_value(self.data_settings, 'n_integration_points', int)
#         _n_turns = self.get_value(self.data_settings, 'total_number_of_turns', int) #check if n_turns really is the total number of turns
#         _n_collections = int(self.App.myapp.ui.le_n_series.text())
#         _analisys_interval = self.App.myapp.ui.le_remove_initial_turns.text() + '-' + str(_n_turns - int(self.App.myapp.ui.le_remove_final_turns.text())) #check!!
# #         `main_current[A]` ??????????
# #         `main_coil_current_avg[A]` ?????????
# #         `main_coil_current_std[A]` ?????????
# #         `ch_coil_current_avg[A]` REAL,\ ????????
# #         `ch_coil_current_std[A]` REAL,\ ????????
# #         `cv_coil_current_avg[A]` REAL,\ ????????
# #         `cv_coil_current_std[A]` REAL,\ ????????
# #         `qs_coil_current_avg[A]` REAL,\ ????????
# #         `qs_coil_current_std[A]` REAL,\ ????????
# #         `trim_coil_current_avg[A]` REAL,\ ???????
# #         `trim_coil_current_std[A]` REAL,\ ???????
# #         `main_coil_volt_avg[V]` REAL,\ ???????
# #         `main_coil_volt_std[V]` REAL,\ ???????
# #         `magnet_resistance_avg[ohm]` REAL,\ ???????
# #         `magnet_resistance_std[ohm]` REAL,\ ???????
#         _bench = self.App.myapp.ui.cb_bench.currentIndex()
#         _accelerator_type = self.App.myapp.ui.cb_accelerator_type.text()
#         _magnet_model = self.App.myapp.ui.cb_magnet_model.currentIndex()
#         _coil_name = self.get_value(self.coil_settings, 'coil_name', str)
#         _coil_type = self.get_value(self.coil_settings, 'coil_type', str)
        _measurement_type = 'N_Bucked' #Not necessary to implement bucked mode for now
#         _n_turns_normal = self.get_value(self.coil_settings, 'n_turns_normal', int)
#         _radius1_normal = self.get_value(self.coil_settings, 'radius1_normal', float)
#         _radius2_normal = self.get_value(self.coil_settings, 'radius2_normal', float)
#         _n_turns_bucked = self.get_value(self.coil_settings, 'n_turns_bucked', int)
#         _radius1_bucked = self.get_value(self.coil_settings, 'radius1_bucked', float)
#         _radius2_bucked = self.get_value(self.coil_settings, 'radius2_bucked', float)
#         _coil_comments = self.get_value(self.coil_settings, 'comments', str)
#         _comments = self.App.myapp.ui.le_meas_details.text()
#         _norm_radius = float(self.App.myapp.ui.le_norm_radius.text())
#         _magnetic_center_x = self.App.myapp.ui.le_magnetic_center_x.text()
#         _magnetic_center_y = self.App.myapp.ui.le_magnetic_center_y.text()
#         _read_data = self.get_read_data()
#         _raw_curve = self.get_raw_curve()
#         
#         _db_values = (None, _name, _filename, _date, _hour, _operator, _software_version, _temperature, _rotation_motor_speed,\
#                       _rotation_motor_acceleration, _driver_direction, _integrator_gain, _trigger_ref,\
#                       _n_integration_points, _n_turns, _n_collections, _analisys_interval,\
# #                       _main_current, _main_coil_currente_avg, main_coil_current_std,\
# #                       _ch_coil_current_avg, _ch_coil_current_std,\
# #                       _cv_coil_current_avg, _cv_coil_current_std,\
# #                       _qs_coil_current_avg, _qs_coil_current_std,\
# #                       _trim_coil_current_avg, _trim_coil_current_std,\
# #                       _main_coil_volt_avg, _main_coil_volt_std,\
# #                       _magnet_resistance_avg, _magnet_resistance_std,\
#                       _bench, _accelerator_type, _magnet_model, _coil_name, _coil_type, _measurement_type,\
#                       _n_turns_normal, _radius1_normal,\
#                       _radius2_normal, _n_turns_bucked, _radius1_bucked, _radius2_bucked,\
#                       _coil_comments, _comments, _norm_radius, _magnetic_center_x, _magnetic_center_y, _read_data, _raw_curve
#                     )
                    
        _db_test_values = (None,0,0,_date,_hour,0,_software_version,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

        self.cur.execute("INSERT INTO measurements VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", _db_test_values)
        self.con.commit()
        
    def db_load_measurement(self, idn=None):
        """
        Load measurement from database, returns selected measurements
        """
        #loads last measurement:
        if idn == None:
            self.cur.execute('SELECT * FROM measurements WHERE id = (SELECT MAX(id) FROM measurements)')
        #loads measurement from id:
        else:
            self.cur.execute('SELECT * FROM measurements WHERE id = ?', (idn,))
        #loads measurement from name:
#         _name = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE name=?)', (_name,))
        #loads measurement from filename:
#         _filename = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE filename=?)', (_filename,))
        #loads measurement from date:
#         _date = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE date=?', (_date,))
        #loads measurement from operator:
#         _operator = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE operator=?', (_operator,))
        #loads measurement from magnet_model:
#         _magnet_model = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE magnet_model=?', (_magnet_model))
        #loads measurement from coil_name:
#         _coil_name = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE coil_name=?', (_coil_name,))
        #loads measurement from bench:
#         _bench = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE bench=?', (_bench,))
        #loads measurement from software_version:
#         _software_version = ''
#         Lib.cur.execute('SELECT * FROM measurements WHERE software_version=?', (_bench,))
        return self.cur.fetchall()
    
    def get_read_data(self):
        """
        TEST!!!
        Retrieves read data from current measurement and returns as string (old log file format)
        """
        _n_rows = self.App.myapp.ui.tw_multipoles_table.rowCount()
        _magnet_type = self.App.myapp.ui.cb_magnet_model.currentIndex()
        _norm_radius = self.App.myapp.ui.le_norm_radius.text()
        _str = "n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\tstd_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\tavg_angle(rad)  \tstd_angle(rad)  \tavg_Nn/NnMagnet@"+ _norm_radius +"mm\tstd_Nn/NnMagnet@"+ _norm_radius+"mm\tavg_Sn/NnMagnet@" + _norm_radius + "mm\tstd_Sn/NnMagnet@r_ref\n"

        for i in range(_n_rows):
            _str = _str + str('{0:<4d}'.format(i)) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.averageN.values[i])) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.stdN.values[i])) + '\t'      
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.averageS.values[i])) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.stdS.values[i])) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.averageMod.values[i])) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.stdMod.values[i])) + '\t'
            if i == _magnet_type or _magnet_type == 0:
                _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.averageAngle.values[i])) + '\t'
                _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.stdAngle.values[i])) + '\t'
            else:
                _str = _str + str('{0:^+18.6e}'.format(0.0)) + '\t'
                _str = _str + str('{0:^+18.6e}'.format(0.0)) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.averageN_norm.values[i])) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.stdN_norm.values[i])) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.averageS_norm.values[i])) + '\t'
            _str = _str + str('{0:^+18.6e}'.format(self.App.myapp.stdS_norm.values[i])) + '\n'
            
        return _str

    def load_read_data(self, idn=None):
        """
        TEST!!!
        Load read data from database entry idn and returns as string (reads from last entry if idn = None)
        """
        if idn == None:
            self.cur.execute('SELECT read_data FROM measurements WHERE id = (SELECT MAX(id) FROM measurements)')
        else:
            self.cur.execute('SELECT read_data FROM measurements WHERE id = ?', (idn,))
        _read_data = self.cur.fetchall()[0][0]
#         _read_data = StringIO(_read_data)
#         return pd.read_csv(_read_data, sep='\t')
        return _read_data
        
    def get_raw_curve(self):
        """
        TEST!!!
        Retrieves raw curve from current measurement and returns as string (old log file format)
        """
        _n_of_turns = self.get_value(self.data_settings,'total_number_of_turns',int)
        _n_integration_points = int(self.App.myapp.ui.cb_n_integration_points.currentText())
        _str = ''
        for i in range(_n_of_turns):
            _str = _str + '{:#^18}'.format(' Turn_' + str(i+1) + '')
        _str = _str + '\n' + self.App.myapp.df_rawcurves.to_csv(sep='\t')
        return _str

    def load_raw_curve(self, idn=None):
        """
        TEST!!!
        Load raw curve from database entry and returns as string (reads from last entry if idn = None)
        """
        if idn == None:
            self.cur.execute('SELECT raw_curve FROM measurements WHERE id = (SELECT MAX(id) FROM measurements)')
        else:
            self.cur.execute('SELECT raw_curve FROM measurements WHERE id = ?', (idn,))
        _raw_curve = self.cur.fetchall()[0][0]
#         _raw_curve = StringIO(_raw_curve)
#         return pd.read_csv(_raw_curve,  comment = '#', delimiter = '\t')
        return _raw_curve
    
    def save_log_file(self, idn=None):
        """
        TEST!!!
        Saves log file from database entry idn (last entry if idn = None), similar to old log file format
        """
        
        _measurement_entry = self.db_load_measurement(idn)[0] #loads last measurement
        #Configuration Data
        _id = _measurement_entry[0]
        _name = _measurement_entry[1]
        _filename = _measurement_entry[2]
        _date = _measurement_entry[3]
        _hour = _measurement_entry[4]
        _operator = _measurement_entry[5]
        _software_version = _measurement_entry[6]
        _bench = _measurement_entry[32]
        _temperature = _measurement_entry[7]
        _integrator_gain = _measurement_entry[11]
        _n_integration_points = _measurement_entry[13]
        _rotation_motor_speed = _measurement_entry[8]
        _rotation_motor_acceleration = _measurement_entry[9]
        _n_collections = _measurement_entry[15]
        _n_turns = _measurement_entry[14]
        _analisys_interval = _measurement_entry[16]
        _driver_direction = _measurement_entry[10]
        _main_coil_current_avg = _measurement_entry[18]
        _main_coil_current_std = _measurement_entry[19]
        _ch_coil_current_avg = _measurement_entry[20]
        _ch_coil_current_std = _measurement_entry[21]
        _cv_coil_current_avg = _measurement_entry[22]
        _cv_coil_current_std = _measurement_entry[23]
        _qs_coil_current_avg = _measurement_entry[24]
        _qs_coil_current_std = _measurement_entry[25]
        _trim_coil_current_avg = _measurement_entry[26]
        _trim_coil_current_std = _measurement_entry[27]
        _main_coil_volt_avg = _measurement_entry[28]
        _main_coil_volt_std = _measurement_entry[29]
        _magnet_resistance_avg = _measurement_entry[30]
        _magnet_resistance_std = _measurement_entry[31]         
        #Rotating Coil Data
        _coil_name = _measurement_entry[35]
        _coil_type = _measurement_entry[36]
        _measurement_type = _measurement_entry[37]
        _trigger_ref = _measurement_entry[12]
        _n_turns_normal = _measurement_entry[38]
        _radius1_normal = _measurement_entry[39]
        _radius2_normal = _measurement_entry[40]
        _n_turns_bucked = _measurement_entry[41]
        _radius1_bucked = _measurement_entry[42]
        _radius2_bucked = _measurement_entry[43]         
        #Comments
        _comments = _measurement_entry[45]         
        #Reading data
        _read_data = _measurement_entry[49]
        _magnetic_center_x = _measurement_entry[47]
        _magnetic_center_y = _measurement_entry[48]         
        #Raw data
        _raw_curve = _measurement_entry[50]
        
        with open(_filename, 'w') as f:
            f.write('########## EXCITATION CURVE - ROTATING COIL ##########')
            f.write('\n\n')
            f.write('### Configuration Data ###')
            f.write('\n')
            f.write('id                             \t' + str(_id) + '\n')
            f.write('file                           \t' + str(_filename) + '\n')
            f.write('date                           \t' + str(_date) + '\n')
            f.write('hour                           \t' + str(_hour) + '\n')
            f.write('operator                       \t' + str(_operator) + '\n')
            f.write('software_version               \t' + str(_software_version) + '\n')
            f.write('bench                          \t' + str(_bench) + '\n')
            f.write('temperature(ºC)                \t' + str(_temperature) + '\n')
            f.write('integrator_gain                \t' + str(_integrator_gain) + '\n')
            f.write('n_integration_points           \t' + str(_n_integration_points) + '\n')
            f.write('velocity(rps)                  \t' + str(_rotation_motor_speed) + '\n')
            f.write('acceleration(rps^2)            \t' + str(_rotation_motor_acceleration) + '\n')
            f.write('n_collections                  \t' + str(_n_collections) + '\n')
            f.write('n_turns                        \t' + str(_n_turns) + '\n') 
            f.write('analysis_interval              \t' + str(_analisys_interval) + '\n')
            f.write('rotation                       \t' + str(_driver_direction) + '\n')
            f.write('main_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(_main_coil_current_avg)) + '\n')
            f.write('main_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(_main_coil_current_std)) + '\n')
            f.write('main_coil_volt_avg(V)          \t' + str('{0:+0.6e}'.format(_main_coil_volt_avg)) + '\n')
            f.write('main_coil_volt_std(V)          \t' + str('{0:+0.6e}'.format(_main_coil_volt_std)) + '\n')
            f.write('magnet_resistance_avg(ohm)     \t' + str('{0:+0.6e}'.format(_magnet_resistance_avg)) + '\n')
            f.write('magnet_resistance_std(ohm)     \t' + str('{0:+0.6e}'.format(_magnet_resistance_std)) + '\n')
            f.write('ch_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(_ch_coil_current_avg)) + '\n')
            f.write('ch_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(_ch_coil_current_std)) + '\n')
            f.write('cv_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(_cv_coil_current_avg)) + '\n')
            f.write('cv_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(_cv_coil_current_std)) + '\n')
            f.write('qs_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(_qs_coil_current_avg)) + '\n')
            f.write('qs_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(_qs_coil_current_std)) + '\n')                                              
            f.write('trim_coil_current_avg(A)   \t' + str('{0:+0.6e}'.format(_trim_coil_current_avg)) + '\n')
            f.write('trim_coil_current_std(A)   \t' + str('{0:+0.6e}'.format(_trim_coil_current_std)) + '\n')
            f.write('\n')
            f.write('### Rotating Coil Data ###')
            f.write('\n')
            f.write('rotating_coil_name             \t' + str(_coil_name) + '\n')
            f.write('rotating_coil_type             \t' + str(_coil_type) + '\n')
            f.write('measurement_type               \t' + str(_measurement_type) + '\n') ## bucked ou n_bucked
            f.write('pulse_start_collect            \t' + str(_trigger_ref) + '\n')
            f.write('n_turns_main_coil              \t' + str(_n_turns_normal) + '\n')
            f.write('main_coil_internal_radius(m)   \t' + str(_radius1_normal) + '\n')
            f.write('main_coil_external_radius(m)   \t' + str(_radius2_normal) + '\n')
            f.write('n_turns_bucked_coil            \t' + str(_n_turns_bucked) + '\n')
            f.write('bucked_coil_internal_radius(m) \t' + str(_radius1_bucked) + '\n')
            f.write('bucked_coil_external_radius(m) \t' + str(_radius2_bucked) + '\n')
            f.write('\n')
            f.write('### Comments ###')
            f.write('\n')
            f.write('comments                       \t' + str(_comments) + '\n')
            f.write('\n\n\n') 
            f.write('##### Reading Data #####')
            f.write('\n\n')
            f.write(_read_data)
            f.write('\n')
            f.write('magnetic_center_x(um) \t' + str(_magnetic_center_x) + '\n')
            f.write('magnetic_center_y(um) \t' + str(_magnetic_center_y) + '\n')
            f.write('\n\n')
            f.write('##### Raw Data Stored(V.s) [1e-12] #####')
            f.write('\n\n')
            f.write(_raw_curve)
            
            #SAVE TURN ANGLES!!!
#                         if self.ui.Salvar_Angulo_Volta.isChecked():
#                 f.write('\n\n\n')   ### Angulo por Volta.
#                 f.write('.........Turn Angle:.........\n\n')
#                 for i in range(0,len(lib.pontos),1):
#                     f.write(str(lib.AngulosVoltas[TipoIma][i]) + '\n') 
        
    def load_settings(self):
        try:
            self.data_settings = None
            _file = self.dir_path + self.settings_file
            self.data_settings = pd.read_csv(_file, comment = '#', delimiter = '\t',names=['datavars','datavalues'], dtype={'datavars':str}, index_col='datavars')
            return True
        except:
            return False

    def save_settings(self):
        try:
            _file = self.dir_path + self.settings_file
            fname = open(_file,'w')
            fname.write('# Rotating Coil Main Parameters\n')
            fname.write('# Insert the variable name and value separated by tab.\n')
            fname.write('# Commented lines are ignored.\n\n')
            
            for i in range(len(self.data_settings)):
                fname.write(self.data_settings.index[i] + '\t' + str(self.data_settings.iloc[i].get_values()[0]) +'\n')
            fname.close()
            
            return True
        except:
            return False

    def load_coil(self,filename):
        try:
            self.coil_settings = None
            self.coil_settings = pd.read_csv(filename, comment = '#', delimiter = '\t',names=['datavars','datavalues'], dtype={'datavars':str}, index_col='datavars')
            return True
        except:
            return False

    def save_coil(self,filename):
        try:
            fname = open(filename,'w')
            fname.write('# Coil Parameters\n')
            fname.write('# Insert the variable name and value separated by tab.\n')
            fname.write('# Commented lines are ignored.\n\n')
            
            for i in range(len(self.coil_settings)):
                fname.write(self.coil_settings.index[i] + '\t' + str(self.coil_settings.loc[self.coil_settings.index[i]].get_values()[0]) +'\n')
            fname.close()
            
            return True
        except:
            return False
        
        
    def load_PS(self,filename):
        try:
            self.PS_settings = None
            self.PS_settings = pd.read_csv(filename, comment = '#', delimiter = '\t',names=['datavars','datavalues'], dtype={'datavars':str}, index_col='datavars')
            return True
        except:
            return False        
            
        
    def save_PS(self,filename):
        try:
            fname = open(filename, 'w')
            fname.write('# Power Supply Parameters\n')
            fname.write('# Insert the variable name and value separated by tab.\n')
            fname.write('# Commented lines are ignored.\n\n')
            
            for i in range(len(self.PS_settings)):
                fname.write(self.PS_settings.index[i] + '\t' + str(self.PS_settings.loc[self.PS_settings.index[i]].get_values()[0]) +'\n')
            fname.close()
            return True
        except:
            return False
        
    def get_value(self,dataframe,index,value_type=None):
        """
        get value from dataframe, value_types: int,float,str,None(returns same type as in df)
        """
        if value_type == int:
            return int(dataframe.loc[index].astype(float).get_values()[0])
        if value_type == float:
            return dataframe.loc[index].astype(float).get_values()[0]
        if value_type == str:
            return dataframe.loc[index].astype(str).get_values()[0]
        else:
            return dataframe.loc[index].get_values()[0]

    def write_value(self,dataframe,index,value):
        """
        write values in dataframe
        """
        dataframe.loc[index].values[0] = value

class flags(object):
    def __init__(self):
        self.coil_ref_flag = False
        self.stop_all = False        

class communication(object):
    def __init__(self):
        # Connection Tab 
        self.display = None
        self.parker = None
        self.fdi = None    
        self.agilent33220a = None
        self.agilent34401a = None
        self.agilent34970a = None
        self.drs = None       
    
class interface_vars(object):
    def __init__(self):
        # Connection Tab 
        self.display_type = None
        self.disp_port = None
        self.driver_port = None
        self.integrator_port = None
        self.ps_type = None
        self.ps_port = None
        self.ps_address = None
        
        self.enable_Agilent33220A = None
        self.agilent33220A_address = None
                
        self.enable_Agilent34401A = None
        self.agilent34401A_address = None

        self.enable_Agilent34970A = None
        self.agilent34970A_address = None
        
        # Settings Tab
        self.total_number_of_turns = None
        self.remove_initial_turns = None
        self.remove_final_turns = None
        
        self.ref_encoder_A = None
        self.ref_encoder_B = None

        self.rotation_motor_address = None
        self.rotation_motor_resolution = None        
        self.rotation_motor_speed = None
        self.rotation_motor_acceleration = None
        self.rotation_motor_ratio = None

        self.poscoil_assembly = None
        self.n_encoder_pulses = None
        
        self.cb_integrator_gain = None
        self.cb_n_integration_points = None
               
        self.save_turn_angles = None
        self.disable_aligment_interlock = None
        self.disable_ps_interlock = None
        
        # Motors Tab
        self.driver_address = None
        self.driver_mode = None
        self.driver_direction = None
        self.motor_vel = None
        self.motor_ace = None
        self.motor_turns = None
        
        # Coil Tab
        self.coil_name = None
        self.n_turns_normal = None
        self.radius1_normal = None
        self.radius2_normal = None
        self.n_turns_bucked = None
        self.radius1_bucked = None
        self.radius2_bucked = None
        self.coil_type = None
        self.te_comments = None
        
        # Integrator Tab
        self.integrator_gain = None
        self.integration_points = None
        self.lcd_encoder_reading = None
        self.encoder_setpoint = None        
        self.label_status_1 = None
        self.label_status_2 = None
        self.label_status_3 = None
        self.label_status_4 = None
        self.label_status_5 = None
        self.label_status_6 = None
        self.label_status_7 = None
        
        self.norm_radius = None
        self.coil_rotation_direction = None
        
        # Power Supply Tab
        self.Status_PS = 0      #0 = OFF ; 1 = ON
        self.PS_cicle = 0
        self.Actual_current = 0
        
        #General 
        self.stop_all = 0
        
    
#     def communication(self):
#         self.display = 0            # Display Heidenhain
#         self.motor = 0              # Driver do motor
#         self.integrador = 0         # Integrador
#         self.controle_fonte = 0     #ACRESCENTADO# Seleciona o controle via PUC ou Digital  
#         self.StatusIntegrador = []
#         self.Janela = 0
#         self.endereco = 2
#         self.endereco_pararmotor = 0
#         self.tipo_display = 0
#         self.stop = 0
#         self.Ref_Bobina = 0
#         self.posicao = [0,0]
#         self.kill = 0
#         self.pontos = []
#         self.pontos_recebidos = []
#         self.parartudo = 0
#         self.media = 0
#         self.F = 0
#         self.ganho = 0
#         self.pontos_integracao = 0
#         self.pulsos_encoder = 0
#         self.pulsos_trigger = 0
#         self.voltas_offset = 0
#         self.volta_filtro = 0
#         
#         self.SJN = np.zeros(21)
#         self.SKN = np.zeros(21)
#         self.SNn = np.zeros(21)
#         self.SNn2 = np.zeros(21)
#         self.SSJN2 = np.zeros(21)
#         self.SSKN2 = np.zeros(21)
#         self.SdbdXN = np.zeros(21)
#         self.SdbdXN2 = np.zeros(21)
#         self.Nn = np.zeros(21)
#         self.Sn = np.zeros(21)
#         self.Nnl = np.zeros(21)
#         self.Snl = np.zeros(21)
#         self.sDesv = np.zeros(21)
#         self.sDesvNn = np.zeros(21)
#         self.sDesvSn = np.zeros(21)
#         self.sDesvNnl = np.zeros(21)
#         self.sDesvSnl = np.zeros(21)
#         self.Angulo = np.zeros(21)
#         self.Desv_angulo = np.zeros(21)
#         self.SMod = np.zeros(21)
#         self.AngulosVoltas = []
#         self.procura_indice_flag = 1
#         self.velocidade = 0
#         self.acaleracao = 0
#         self.sentido = 0
#         self.ima_bobina = 0             ## ACRESCENTADO ##
#         self.raio_referencia = 0        ## ACRESCENTADO ##
#         self.passos_volta = 500000
#         self.alpha = 0
#         self.Tipo_Bobina = 0
#         self.Bucked = 0
#         self.PUC = 0
#         self.PUC_Conectada = 0          ## 0 = Desconectada   1 = Conectada
#         self.Modelo_PUC = 0
#         self.Ciclos_Puc = 0
#         self.Divisor_Puc = 0
#         self.LeituraCorrente = 0
#         self.LeituraCorrente_Secundaria = 0     #ACRESCENTADO#
#         self.Leitura_Tensao = 0                 #ACRESCENTADO#
#         self.Leitura_tensao_e_corrente = 0      #ACRESCENTADO#
#         self.Status_Fonte = 0           ## 0 = Desligada   1 = Ligada
#         self.Fonte_Calibrada = [0,0]    ## [Entrada,Saida] 0 = N Calibrada  1 = Calibrada
#         self.Fonte_Pronta = 0           ## 0 = N Pronta    1 = Pronta
#         self.Fonte_Ciclagem = 0         ## 0 = N Ciclando  1 = Ciclando
#         self.Analise_Freq = 0           ## 0 = Parada      1 = Realizando
#         self.Corrente_Atual = 0
#         self.Ponto_Inicial_Curva = 0
#         self.Dados_Curva = []
#         self.reta_escrita = []
#         self.reta_leitura = []
#         self.FileName = 0
#         self.Motor_Posicao = 0
#         self.GPIB = 0
#         self.Multimetro = 0
#         self.Digital = 0               #ACRESCENTADO#  Seleciona a fonte digital
#         self.Digital_Conectada = 0     #ACRESCENTADO#  Retorna se a fonte está conectada: 0 = Desconectada   1 = Conectada  
#         
#     def constants(self):
#         self.numero_de_abas = 10                                # Numero de abas da janela grafica
#         self.ganhos = [1, 2, 5, 10, 20, 50, 100]                # Ganhos disponiveis para o integrador
# ##        self.p_integracao = [16, 32, 64, 128, 256, 512]         # Numero de pontos de integracao disponiveis encoder 2**n
#         self.p_integracao = [90, 100, 120, 144, 250, 500]       # Numero de pontos de integracao disponiveis
#         self.passos_mmA = 25000                                 # Numero de passos por mm
#         self.passos_mmB = 25000                                 # Numero de passos por mm
#         self.passos_mmC = 50000
#         self.motorA_endereco = 3                                # Endereco do motor A
#         self.motorB_endereco = 4                                # Endereco do motor B
#         self.motorC_endereco = 2
#         self.avancoA = 0
#         self.avancoB = 0
#         self.avancoC = 0
#         self.zeroA = 0
#         self.zeroB = 0
#         self.pos_ang = 0
#         self.pos_long = 0
#         self.pos_ver = 0
#         self.pos_trac = 0
#         self.premont_A = 0
#         self.premont_B = 0
#         self.final_A = 0
#         self.final_B = 0
#         self.Clock_Puc = 4000                                   #Clock interno da PUC
#         self.Pontos_Puc = 32768                                 #Número de pontos da Memória PUC