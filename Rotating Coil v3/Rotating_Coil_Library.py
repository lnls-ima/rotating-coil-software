'''
Created on 17 de nov de 2017

@author: James Citadini
'''
#import numpy as np
import os
import pandas as pd


# import PUC_2v5
# # import PUC_2v6              ## Nova PUC.

# import Controle_GPIB
# import Controle_GPIB_2      ## Para comunicação SERIAL do multímetro 34401A

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
        
    def get_value(self,dataframe,index,type=None):
        """
        get value from dataframe
        """
        if type == int:
            return int(dataframe.loc[index].astype(float).get_values()[0])
        if type == float:
            return dataframe.loc[index].astype(float).get_values()[0]
        if type == str:
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
        self.PUC_type = None
        self.PUC_port = None
        self.PUC_address = None
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