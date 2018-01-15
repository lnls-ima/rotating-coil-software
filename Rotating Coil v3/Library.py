'''
Created on 17 de nov de 2017

@author: James Citadini
'''
import time

import numpy as np

import Display_Heidenhain
import Parker_Drivers
import FDI2056
import PUC_2v5
# import PUC_2v6              ## Nova PUC.
import SerialDRS            ## Biblioteca Fonte Digital
import Controle_GPIB
import Controle_GPIB_2      ## Para comunicação SERIAL do multímetro 34401A

# Biblioteca de variaveis globais utilizadas
class RotatingCoil_Library(object):
    def __init__(self):
        self.interface = None
    
    def interface_vars(self):
        pass
    
    def communication(self):
        self.display = 0            # Display Heidenhain
        self.motor = 0              # Driver do motor
        self.integrador = 0         # Integrador
        self.controle_fonte = 0     #ACRESCENTADO# Seleciona o controle via PUC ou Digital  
        self.StatusIntegrador = []
        self.Janela = 0
        self.endereco = 2
        self.endereco_pararmotor = 0
        self.tipo_display = 0
        self.stop = 0
        self.Ref_Bobina = 0
        self.posicao = [0,0]
        self.kill = 0
        self.pontos = []
        self.pontos_recebidos = []
        self.parartudo = 0
        self.media = 0
        self.F = 0
        self.ganho = 0
        self.pontos_integracao = 0
        self.pulsos_encoder = 0
        self.pulsos_trigger = 0
        self.voltas_offset = 0
        self.volta_filtro = 0
        
        self.SJN = np.zeros(21)
        self.SKN = np.zeros(21)
        self.SNn = np.zeros(21)
        self.SNn2 = np.zeros(21)
        self.SSJN2 = np.zeros(21)
        self.SSKN2 = np.zeros(21)
        self.SdbdXN = np.zeros(21)
        self.SdbdXN2 = np.zeros(21)
        self.Nn = np.zeros(21)
        self.Sn = np.zeros(21)
        self.Nnl = np.zeros(21)
        self.Snl = np.zeros(21)
        self.sDesv = np.zeros(21)
        self.sDesvNn = np.zeros(21)
        self.sDesvSn = np.zeros(21)
        self.sDesvNnl = np.zeros(21)
        self.sDesvSnl = np.zeros(21)
        self.Angulo = np.zeros(21)
        self.Desv_angulo = np.zeros(21)
        self.SMod = np.zeros(21)
        self.AngulosVoltas = []
        self.procura_indice_flag = 1
        self.velocidade = 0
        self.acaleracao = 0
        self.sentido = 0
        self.ima_bobina = 0             ## ACRESCENTADO ##
        self.raio_referencia = 0        ## ACRESCENTADO ##
        self.passos_volta = 500000
        self.alpha = 0
        self.Tipo_Bobina = 0
        self.Bucked = 0
        self.PUC = 0
        self.PUC_Conectada = 0          ## 0 = Desconectada   1 = Conectada
        self.Modelo_PUC = 0
        self.Ciclos_Puc = 0
        self.Divisor_Puc = 0
        self.LeituraCorrente = 0
        self.LeituraCorrente_Secundaria = 0     #ACRESCENTADO#
        self.Leitura_Tensao = 0                 #ACRESCENTADO#
        self.Leitura_tensao_e_corrente = 0      #ACRESCENTADO#
        self.Status_Fonte = 0           ## 0 = Desligada   1 = Ligada
        self.Fonte_Calibrada = [0,0]    ## [Entrada,Saida] 0 = N Calibrada  1 = Calibrada
        self.Fonte_Pronta = 0           ## 0 = N Pronta    1 = Pronta
        self.Fonte_Ciclagem = 0         ## 0 = N Ciclando  1 = Ciclando
        self.Analise_Freq = 0           ## 0 = Parada      1 = Realizando
        self.Corrente_Atual = 0
        self.Ponto_Inicial_Curva = 0
        self.Dados_Curva = []
        self.reta_escrita = []
        self.reta_leitura = []
        self.FileName = 0
        self.Motor_Posicao = 0
        self.GPIB = 0
        self.Multimetro = 0
        self.Digital = 0               #ACRESCENTADO#  Seleciona a fonte digital
        self.Digital_Conectada = 0     #ACRESCENTADO#  Retorna se a fonte está conectada: 0 = Desconectada   1 = Conectada  
        
    def constants(self):
        self.numero_de_abas = 10                                # Numero de abas da janela grafica
        self.ganhos = [1, 2, 5, 10, 20, 50, 100]                # Ganhos disponiveis para o integrador
##        self.p_integracao = [16, 32, 64, 128, 256, 512]         # Numero de pontos de integracao disponiveis encoder 2**n
        self.p_integracao = [90, 100, 120, 144, 250, 500]       # Numero de pontos de integracao disponiveis
        self.passos_mmA = 25000                                 # Numero de passos por mm
        self.passos_mmB = 25000                                 # Numero de passos por mm
        self.passos_mmC = 50000
        self.motorA_endereco = 3                                # Endereco do motor A
        self.motorB_endereco = 4                                # Endereco do motor B
        self.motorC_endereco = 2
        self.avancoA = 0
        self.avancoB = 0
        self.avancoC = 0
        self.zeroA = 0
        self.zeroB = 0
        self.pos_ang = 0
        self.pos_long = 0
        self.pos_ver = 0
        self.pos_trac = 0
        self.premont_A = 0
        self.premont_B = 0
        self.final_A = 0
        self.final_B = 0
        self.Clock_Puc = 4000                                   #Clock interno da PUC
        self.Pontos_Puc = 32768                                 #Número de pontos da Memória PUC