#!/usr/bin/python
# -*- coding: utf-8 -*-

# Lembretes: 

# Bobina girante v2.0

import sys
sys.path.append(str(sys.path[0])+str('\\PUC_2v6')) ## Nome da pasta com biblioteca da PUC
import time
import threading
import numpy
import pandas as pd
import ctypes
import matplotlib.pyplot as plt
import Display_Heidenhain
import Parker_Drivers
import FDI2056
import PUC_2v5
import PUC_2v6              ## Nova PUC.
import SerialDRS            ## Biblioteca Fonte Digital
import Controle_GPIB
import Controle_GPIB_2      ## Para comunicação SERIAL do multímetro 34401A
from PyQt4 import QtCore, QtGui
from interface1 import Ui_InterfaceBobina
import traceback



# ____________________________________________
# Biblioteca de variaveis globais utilizadas
class lib(object):
    def __init__(self):
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
        self.SJN = numpy.zeros(21)
        self.SKN = numpy.zeros(21)
        self.SNn = numpy.zeros(21)
        self.SNn2 = numpy.zeros(21)
        self.SSJN2 = numpy.zeros(21)
        self.SSKN2 = numpy.zeros(21)
        self.SdbdXN = numpy.zeros(21)
        self.SdbdXN2 = numpy.zeros(21)
        self.Nn = numpy.zeros(21)
        self.Sn = numpy.zeros(21)
        self.Nnl = numpy.zeros(21)
        self.Snl = numpy.zeros(21)
        self.sDesv = numpy.zeros(21)
        self.sDesvNn = numpy.zeros(21)
        self.sDesvSn = numpy.zeros(21)
        self.sDesvNnl = numpy.zeros(21)
        self.sDesvSnl = numpy.zeros(21)
        self.Angulo = numpy.zeros(21)
        self.Desv_angulo = numpy.zeros(21)
        self.SMod = numpy.zeros(21)
        self.AngulosVoltas = []
        self.procura_indice_flag = 1
        self.velocidade = 0
        self.acaleracao = 0
        self.sentido = 0
        self.ima_bobina = 0             ## ACRESCENTADO ##
        self.raio_referencia = 0        ## ACRESCENTADO ##
        self.passos_volta = 50000
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
        
        
lib = lib()
lib.GPIB = Controle_GPIB_2.Controle()  #Modificado para a biblioteca Controle_GPIB_2 para a comunicação Serial do multímetro 34401A da Bancada 2.

# ____________________________________________



# ____________________________________________
# Biblioteca de constantes utilizadas
class constantes(object):
    def __init__(self):
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

const = constantes()
# ____________________________________________



# ____________________________________________
# Definicao de todas as funcionalidades do programa ordenadas por abas
class JanelaGrafica(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(JanelaGrafica,self).__init__(parent)
        self.ui = Ui_InterfaceBobina()
        self.ui.setupUi(self)
        self.sinais()

    def sinais(self):
        for i in range(1,const.numero_de_abas):
            self.ui.tabWidget.setTabEnabled(i,False)
        self.ui.conectar.clicked.connect(self.CONECTAR)
        self.ui.zerar.clicked.connect(self.ZERAR)
        self.ui.ligar.clicked.connect(self.LIGARMOTOR)             
        self.ui.EndDriver_2.activated.connect(self.Texto_Combobox)
        self.ui.Zerar_Offset.clicked.connect(self.ZERAROFFSET)
        self.ui.Parar_1.clicked.connect(self.PARARMOTORES)
        self.ui.Parar_2.clicked.connect(self.PARARMOTORES)
        self.ui.Parar_3.clicked.connect(self.PARARMOTORES_1)
        self.ui.configurar_integrador.clicked.connect(self.Start_Config)
        self.ui.ler_encoder.clicked.connect(self.LERENCODER)
        self.ui.MoverA.clicked.connect(self.MOVER_A)
        self.ui.MoverB.clicked.connect(self.MOVER_B)
        self.ui.Mover_2.clicked.connect(self.MOVER2)
        self.ui.Emergencia_1.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_2.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_3.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_4.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_5.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_6.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_7.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_8.clicked.connect(self.EMERGENCIA)
        self.ui.Emergencia_9.clicked.connect(self.EMERGENCIA)
        self.ui.Ref.clicked.connect(self.ENCONTRA_REF)
        self.ui.bobinadesmontada.toggled.connect(self.BOBINADESMONTADA)
        self.ui.ProcuraIndice.clicked.connect(self.ProcuraIndiceEncoder)
        self.ui.coletar.clicked.connect(self.COLETA_INTEGRADOR)
        self.ui.salvar_harmonico.clicked.connect(self.Salvar_Coletas)
        self.ui.posicionar.clicked.connect(self.POSICIONAR)
        self.ui.salvar_config.clicked.connect(self.SALVAR_DEFAULT)
        self.ui.ConfGeral.clicked.connect(self.CONFGERAL)
        self.ui.salvar_config_2.clicked.connect(self.SALVAR_DEFAULT)
        self.ui.Ciclar.clicked.connect(self.Ciclagem)
        self.ui.Plota.clicked.connect(self.Plotar_Curva)
        self.ui.EnviaCurva.clicked.connect(self.Enviar_Curva)
        self.ui.tipo_bobina.activated.connect(self.Selecao_Tipo_Bobina)
        self.ui.sentido_2.activated.connect(self.Selecao_Sentido_Giro)
        self.ui.ima_bobina.activated.connect(self.Selecao_ima_bobina)       ## ACRESCENTADO
        self.ui.BobinaL.clicked.connect(self.CARREGABOBINA)
        self.ui.BobinaS.clicked.connect(self.SALVABOBINA)
        self.ui.Referenciar_Bobina.clicked.connect(self.Referenciar_Bobina)
        self.ui.montar.clicked.connect(self.MONTAR)
        self.ui.desmontar.clicked.connect(self.DESMONTAR)
        self.ui.ligar_fonte.clicked.connect(self.Start_Fonte)
        self.ui.Corrente_Atual.clicked.connect(self.Corrente_Fonte)
        self.ui.Enviar_Linear.clicked.connect(self.Rampa_Corrente_Manual)
        self.ui.Carregar_Config_Fonte.clicked.connect(self.Carregar_Fonte)
        self.ui.Salvar_Config_Fonte.clicked.connect(self.Salvar_Fonte)
        self.ui.Hab_Selecao.toggled.connect(self.Selecao)
        self.ui.Calibrar_Fonte.clicked.connect(self.Calibrar_Fonte)
        self.ui.Analise_Frequencia.clicked.connect(self.Analise_Frequencia)
        self.ui.Chk_Auto.toggled.connect(self.Hab_Auto)
        self.ui.C_Sucessivas.toggled.connect(self.Coleta_Suc_Manual)
        self.ui.posicaoA.setText('0')
        self.ui.posicaoB.setText('0')
        self.ui.velocidade_2.setText('3')
        self.ui.velocidade_2.editingFinished.connect(self.velocidade_2_Change)
        self.ui.groupBox_6.setEnabled(False)
        self.ui.velocidade.setText('1')
        self.ui.aceleracao.setText('1')
        self.ui.voltas.setText('1')
        self.ui.status.setText('Pronto')
        self.ui.Ciclagem_Corretora.clicked.connect(self.Ciclagem_Corretora)
        self.ui.Hab_Corretora.toggled.connect(self.Selecao)
        self.ui.Hab_Curva_Quadrupolo.toggled.connect(self.Selecao)
        self.ui.Ciclar_Curva_Quadrupolo.clicked.connect(self.Curva_Quadrupolo)
        self.ui.ckBox_GPIB_1.toggled.connect(self.Habilitar_GPIB)
        self.ui.ckBox_GPIB_2.toggled.connect(self.Habilitar_GPIB)
        self.ui.ckBox_GPIB_3.toggled.connect(self.Habilitar_GPIB)
        self.ui.checkCH_1.toggled.connect(self.Habilitar_Multicanal)
        self.ui.checkCH_2.toggled.connect(self.Habilitar_Multicanal)
        self.ui.checkCH_3.toggled.connect(self.Habilitar_Multicanal)
        self.ui.checkCH_4.toggled.connect(self.Habilitar_Multicanal)
        self.ui.checkCH_5.toggled.connect(self.Habilitar_Multicanal)
        self.ui.checkCH_6.toggled.connect(self.Habilitar_Multicanal)
        self.ui.checkCH_7.toggled.connect(self.Habilitar_Multicanal)
        self.ui.bt_conf_MultiCh.clicked.connect(self.Conf_Multicanal)
        self.ui.bt_read_MultiCh.clicked.connect(self.start_timer)
        self.ui.bt_stop_MultiCh.clicked.connect(self.stop_timer)
        self.ui.check_aux.toggled.connect(self.Habilitar_trim)
        
        
        self.ui.conectar_GPIB.clicked.connect(self.Conectar_GPIB)
        self.ui.Atualizar_Status.clicked.connect(self.Status_Display_Integrador)
        self.ui.label_173.setVisible(False)                     #ACRESCENTADO - Apenas para indicar a unidade da Amplitude (Ap) na fonte digital, Aba "Senoidal"#
        self.ui.label_174.setVisible(False)                     #ACRESCENTADO- Apenas para indicar a unidade da Amplitude (Ap) na fonte digital, Aba "Senoidal Amortecida"#      
        self.load_default()

    def load_default(self):
        try:
            f = open('default_settings2.dat','r')
        except:
##            QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Arquivo de inicialização inexistente.',QtGui.QMessageBox.Ok)
            print('Aviso: Arquivo de inicialização inexistente.')
            return
        config = f.read().split('\n\n')
        f.close()
        for i in range(len(config)):
            config[i]=config[i].split('\n')
            for j in range(len(config[i])):
                config[i][j]=config[i][j].split('\t')
        self.ui.Tipo_Display.setCurrentIndex(int(config[1][0][1]))
        self.ui.Porta.setCurrentIndex(int(config[1][1][1])-1)    #Porta Display
        self.ui.Porta_2.setCurrentIndex(int(config[1][2][1])-1)  #Porta Driver
        self.ui.Porta_3.setCurrentIndex(int(config[1][3][1])-1)  #Porta Integrador
        self.ui.Porta_5.setCurrentIndex(int(config[1][4][1])-1)  #Seleciona Fonte
        self.ui.Tipo_PUC.setCurrentIndex(int(config[1][5][1]))
        self.ui.Porta_4.setCurrentIndex(int(config[1][6][1])-1)
        self.ui.Enderac_PUC.setValue(int(config[1][7][1]))
        self.ui.Porta_6.setCurrentIndex(int(config[1][8][1])-1)  #Porta Digital
        self.ui.Enderac_Digi.setValue(int(config[1][9][1]))      #Endereço Digital
        self.ui.EndDriver.setCurrentIndex(int(config[2][0][1])-1)
        lib.endereco = config[2][0][1]
        self.ui.ganho.setCurrentIndex(int(config[2][1][1]))
        self.ui.pontos_integracao.setCurrentIndex(int(config[2][2][1]))
        self.ui.pulsos_encoder.setText(config[2][3][1])
        self.ui.velocidade_int.setText(config[2][4][1])
        self.ui.aceleracao_int.setText(config[2][5][1])
        self.ui.voltas_offset.setText(config[2][6][1])
        self.ui.filtro_voltas.setText(config[2][7][1])
        lib.passos_volta = int(config[2][8][1])
        self.ui.EndDriver_A.setCurrentIndex(int(config[4][0][1])-1)
        self.ui.EndDriver_B.setCurrentIndex(int(config[4][1][1])-1)
        self.ui.EndDriver_C.setCurrentIndex(int(config[4][2][1])-1)
        self.ui.sentido_A.setCurrentIndex(int(config[4][3][1]))
        self.ui.sentido_B.setCurrentIndex(int(config[4][4][1]))
        self.ui.sentido_C.setCurrentIndex(int(config[4][5][1]))
        self.ui.descarte_inicial.setText(config[4][6][1])
        self.ui.descarte_final.setText(config[4][7][1])
        self.ui.indice_A.setText(config[4][8][1])
        self.ui.indice_B.setText(config[4][9][1])
        self.ui.premont_A.setText(config[4][10][1])
        self.ui.premont_B.setText(config[4][11][1])
        self.ui.final_A.setText(config[4][12][1])
        self.ui.final_B.setText(config[4][13][1])
        self.ui.pos_ang.setText(config[4][14][1])
        self.ui.pos_long.setText(config[4][15][1])
        self.ui.pos_ver.setText(config[4][16][1])
        self.ui.pos_trac.setText(config[4][17][1])
        self.ui.Enderac_Gerador.setValue(int(config[4][18][1]))
        self.ui.Enderac_Multimetro.setValue(int(config[4][19][1]))
        self.CONFGERAL()

    ########### ABA 1: Conexao ###########

    def CONECTAR(self):        
        if (self.ui.conectar.text() == 'Conectar'):

            lib.stop = 0
            try:
                if self.ui.Tipo_Display.currentIndex() == 0:
                    lib.display = Display_Heidenhain.SerialCom_ND760(self.ui.Porta.currentIndex() + 1)
                    lib.tipo_display = 0
                else:
                    lib.display = Display_Heidenhain.SerialCom_ND780(self.ui.Porta.currentIndex() + 1)
                    lib.tipo_display = 1
                lib.display.Conectar()
            except:
                QtGui.QMessageBox.critical(self,'Erro.','Porta serial ocupada ou inexistente.',QtGui.QMessageBox.Ok)
                return
            try:                                            #ACRESCENTADO#
                if self.ui.Porta_5.currentIndex() == 0:
                    self.ui.groupBox_35.setEnabled(True)
                    self.ui.lcd_Corrente_Digital.setEnabled(False)
                    self.ui.label_171.setEnabled(False)
                    self.ui.label_170.setEnabled(False)
                    self.ui.tipo_fonte.setText('PUC')
                    lib.controle_fonte = 0  #PUC
                else:
##                    self.ui.groupBox_35.setEnabled(False)
                    self.ui.groupBox_37.setEnabled(True)
                    self.ui.lcd_Corrente.setEnabled(False)
                    self.ui.label_97.setEnabled(False)
                    self.ui.label_163.setEnabled(False)
                    self.ui.tipo_fonte.setText('Digital')
                    lib.controle_fonte = 1  #Digital
            except:
                QtGui.QMessageBox.critical(self,'Erro.','Porta serial ocupada ou inexistente.',QtGui.QMessageBox.Ok)
                return
            try:
                lib.motor = Parker_Drivers.SerialCom(self.ui.Porta_2.currentIndex() + 1)
                lib.motor.Conectar()
            except:
                QtGui.QMessageBox.critical(self,'Erro.','Porta serial ocupada ou inexistente.',QtGui.QMessageBox.Ok)
                lib.display.Desconectar()
                return
            try:
                lib.integrador = FDI2056.SerialCom(self.ui.Porta_3.currentIndex() + 1)
                lib.integrador.Conectar()
            except:
                QtGui.QMessageBox.critical(self,'Erro.','Porta serial ocupada ou inexistente.',QtGui.QMessageBox.Ok)
                lib.display.Desconectar()
                lib.motor.Desconectar()
                return
            try:
                if lib.controle_fonte == 0:                     # Se a combobox estiver selecionada para a PUC, ou seja, lib.controle_fonte = 0   #ACRESCENTADO#
                    try:
                        Address = int(self.ui.Enderac_PUC.text())
                        lib.Modelo_PUC = int(self.ui.Tipo_PUC.currentIndex())
                        if (lib.Modelo_PUC == 0):
                            lib.PUC = PUC_2v5.SerialCom(Address)
                            time.sleep(.1)
                            for i in range(0,7):## Abas curvas nao estao prontas
                                self.ui.tabWidget_3.setTabEnabled(i,False)
                            ## Funções nao prontas
                            self.ui.label_93.setEnabled(False)
                            self.ui.label_115.setEnabled(False)
                            self.ui.label_121.setEnabled(False)
                            self.ui.label_118.setEnabled(False)
                            self.ui.Defasagem_Senoidal.setEnabled(False)
                            self.ui.Posicao_Final_Senoidal.setEnabled(False)
                            
                        else:
                            lib.PUC = PUC_2v6.SerialCom(Address)
                            time.sleep(.1)
                            for i in range(0,7):
                                self.ui.tabWidget_3.setTabEnabled(i,True)
                            self.ui.label_93.setEnabled(True)
                            self.ui.label_115.setEnabled(True)
                            self.ui.label_121.setEnabled(True)
                            self.ui.label_118.setEnabled(True)
                            self.ui.Defasagem_Senoidal.setEnabled(True)
                            self.ui.Posicao_Final_Senoidal.setEnabled(True)
                            for i in range(3,7): ## Abas curvas nao estao prontas
                                self.ui.tabWidget_3.setTabEnabled(i,False)
                            
                            
                        status = lib.PUC.Conectar(self.ui.Porta_4.currentIndex() + 1)
                        if (status == False):
                            lib.PUC_Conectada = 0
                            QtGui.QMessageBox.critical(self,'Erro.','Porta serial ocupada/inexistente ou\nPUC não Conectada.',QtGui.QMessageBox.Ok)
                            self.ui.Chk_Auto.setEnabled(False)
                            for i in range(1,const.numero_de_abas-1):
                                self.ui.tabWidget.setTabEnabled(i,True)
                            self.ui.tabWidget.setTabEnabled(3,False)
                            self.ui.conectar.setText('Desconectar')
                            self.ui.Tipo_Display.setEnabled(False)
                            self.ui.Porta.setEnabled(False)
                            self.ui.Porta_2.setEnabled(False)
                            self.ui.Porta_3.setEnabled(False)
                            return
                    except:
                        lib.PUC_Conectada = 0
                        return
                else:                                #ACRESCENTADO# Se a combobox estiver selecionada para Digital, ou seja, lib.controle_fonte = 1   
                    try:
                        Address = int(self.ui.Enderac_Digi.text())  # Endereço digital por Default será sempre 1
                        lib.Digital = SerialDRS.SerialDRS_FBP()
                        lib.Digital.SetSlaveAdd(Address)
                        time.sleep(.1)
                        for i in range(0,7):
                            self.ui.tabWidget_3.setTabEnabled(i,True)
                        self.ui.label_93.setEnabled(True)
                        self.ui.label_115.setEnabled(True)
                        self.ui.label_121.setEnabled(True)
                        self.ui.label_118.setEnabled(True)
                        self.ui.Defasagem_Senoidal.setEnabled(True)
                        self.ui.Posicao_Final_Senoidal.setEnabled(True)
                        for i in range(2,7): ## Abas curvas nao estão prontas -- para fonte digital, aba Tringular Suavizada não operante.
                            self.ui.tabWidget_3.setTabEnabled(i,False)

                        status = lib.Digital.Connect('COM'+str(self.ui.Porta_6.currentIndex() + 1))

                        if (status == False):
                            lib.Digital_Conectada = 0
                            QtGui.QMessageBox.critical(self,'Erro.','Porta serial ocupada/inexistente ou\nFonte Digital não Conectada.',QtGui.QMessageBox.Ok)
                            self.ui.Chk_Auto.setEnabled(False)
                            for i in range(1,const.numero_de_abas-1):
                                self.ui.tabWidget.setTabEnabled(i,True)
                            self.ui.tabWidget.setTabEnabled(3,False)
                            self.ui.conectar.setText('Desconectar')
                            self.ui.Tipo_Display.setEnabled(False)
                            self.ui.Porta.setEnabled(False)
                            self.ui.Porta_2.setEnabled(False)
                            self.ui.Porta_3.setEnabled(False)
                    except:
                        lib.Digital_Conectada = 0
                        return                    
            except:
                QtGui.QMessageBox.critical(self,'Erro.','Porta serial ocupada ou inexistente.',QtGui.QMessageBox.Ok)
                return

            for i in range(1,const.numero_de_abas-1):
                self.ui.tabWidget.setTabEnabled(i,True)
            
            self.ui.conectar.setText('Desconectar')
            self.ui.Tipo_Display.setEnabled(False)
            self.ui.Porta.setEnabled(False)
            self.ui.Porta_2.setEnabled(False)
            self.ui.Porta_3.setEnabled(False)
            self.ui.Porta_4.setEnabled(False)
            self.ui.Porta_5.setEnabled(False)
            self.ui.Porta_6.setEnabled(False)
            self.ui.Enderac_PUC.setEnabled(False)
            self.ui.Enderac_Digi.setEnabled(False)
            self.ui.Tipo_PUC.setEnabled(False)
            if lib.controle_fonte == 0:
                lib.PUC_Conectada = 1
            else:
                lib.Digital_Conectada = 1
                        
        else:
            lib.stop = 1
            lib.display.Desconectar()
            lib.motor.Desconectar()
            lib.integrador.Desconectar()

            try:
                if lib.controle_fonte == 0:  #PUC
                    if lib.PUC_Conectada == 1:
                        lib.PUC.Desconectar()
                    lib.PUC_Conectada = 0
                else:                        #Digital
                    if lib.Digital_Conectada == 1:
                        lib.Digital.Disconnect()
                    lib.Digital_Conectada = 0
            except:
                QtGui.QMessageBox.critical(self,'Erro.','Erro ao Desconectar a fonte de alimentação. \nVerificar Equipamento.',QtGui.QMessageBox.Ok)
            
            for i in range(1,const.numero_de_abas):
                self.ui.tabWidget.setTabEnabled(i,False)
            self.ui.Tipo_Display.setEnabled(True)
            self.ui.Porta.setEnabled(True)
            self.ui.Porta_2.setEnabled(True)
            self.ui.Porta_3.setEnabled(True)
            self.ui.Porta_4.setEnabled(True)
            self.ui.Porta_5.setEnabled(True)
            self.ui.Porta_6.setEnabled(True)
            self.ui.groupBox_35.setEnabled(True)
            self.ui.Enderac_PUC.setEnabled(True)
            self.ui.Enderac_Digi.setEnabled(True)
            self.ui.Tipo_PUC.setEnabled(True)
            self.ui.conectar.setText('Conectar')

            
    ########### ABA 2: Configuracoes Gerais ###########

    def CONFGERAL(self):
        const.motorA_endereco = self.ui.EndDriver_A.currentIndex() + 1
        const.motorB_endereco = self.ui.EndDriver_B.currentIndex() + 1
        const.motorC_endereco = self.ui.EndDriver_C.currentIndex() + 1
        const.avancoA = self.ui.sentido_A.currentIndex()
        const.avancoB = self.ui.sentido_B.currentIndex()
        const.avancoC = self.ui.sentido_C.currentIndex()
        const.zeroA = float(self.ui.indice_A.text())
        const.zeroB = float(self.ui.indice_B.text())
        const.pos_ang = int(self.ui.pos_ang.text())
        const.pos_long = float(self.ui.pos_long.text())
        const.pos_ver = int(self.ui.pos_ver.text())
        const.pos_trac = float(self.ui.pos_trac.text())
        const.premont_A = float(self.ui.premont_A.text())
        const.premont_B = float(self.ui.premont_B.text())
        const.final_A = float(self.ui.final_A.text())
        const.final_B = float(self.ui.final_B.text())
        Controle_Status()
    

    ########### ABA 3: Mesas Transversais ###########

    def velocidade_2_Change(self):
        try:
            aux = float(self.ui.velocidade_2.text())
            if aux > 5:
                QtGui.QMessageBox.warning(self,'Atenção.','Velocidade muito alta.',QtGui.QMessageBox.Ok)
                self.ui.velocidade_2.setText('5')
            if aux < 0:
                QtGui.QMessageBox.warning(self,'Atenção.','Velocidade muito baixa.',QtGui.QMessageBox.Ok)
                self.ui.velocidade_2.setText('1')
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Valor não Numérico.',QtGui.QMessageBox.Ok)
            self.ui.velocidade_2.setText('3')

    def BOBINADESMONTADA(self):
        if self.ui.bobinadesmontada.isChecked():
            self.ui.groupBox_6.setEnabled(True)
            self.ui.groupBox_4.setEnabled(False)
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique se a bobina está desmontada.',QtGui.QMessageBox.Ok)
        else:
            self.ui.groupBox_6.setEnabled(False)
            self.ui.groupBox_4.setEnabled(True)

    def ENCONTRA_REF(self):
        ret = QtGui.QMessageBox.question(self,'Referência.','Deseja Referenciar o Sistema?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.ui.zerar.setEnabled(False)
            if lib.tipo_display == 0:
                EncontraRef_ND760()
            else:
                EncontraRef_ND780()
        else:
            return

    def MOVER_A(self):
        lib.endereco_pararmotor = const.motorA_endereco
        try:
            posicaoA = float(self.ui.posicaoA.text())
        except:
            QtGui.QMessageBox.critical(self,'Atenção.','Valor não é um número.',QtGui.QMessageBox.Ok)
            return
        self.ui.groupBox_6.setEnabled(False)
        self.ui.zerar.setEnabled(False)
        self.ui.bobinadesmontada.setEnabled(False)
        self.Mover_Motor_A(posicaoA,float(self.ui.velocidade_2.text()))

    def Mover_Motor_A(self,posicaoA,velocidade):
        lib.display.LerDisplay()
        lib.posicao = lib.display.DisplayPos
        posicaoB = float(lib.posicao[1])
        motortransversal(posicaoA, posicaoB, velocidade)
        return True

    def MOVER_B(self):
        lib.endereco_pararmotor = const.motorB_endereco
        try:
            posicaoB = float(self.ui.posicaoB.text())
        except:
            QtGui.QMessageBox.critical(self,'Atenção.','Valor não é um número.',QtGui.QMessageBox.Ok)
            return
        self.ui.groupBox_6.setEnabled(False)
        self.ui.zerar.setEnabled(False)
        self.ui.bobinadesmontada.setEnabled(False)
        self.Mover_Motor_B(posicaoB,float(self.ui.velocidade_2.text()))

    def Mover_Motor_B(self,posicaoB,velocidade):
        lib.display.LerDisplay()
        lib.posicao = lib.display.DisplayPos
        posicaoA = float(lib.posicao[0])
        motortransversal(posicaoA, posicaoB, velocidade)
        return True

    def MOVER2(self):
        try:
            posicao = float(self.ui.posicao_bobina_montada.text())
        except:
            QtGui.QMessageBox.critical(self,'Atenção.','Valor não é um número.',QtGui.QMessageBox.Ok)
            return
        self.ui.groupBox_4.setEnabled(False)
        self.ui.zerar.setEnabled(False)
        self.ui.bobinadesmontada.setEnabled(False)
        if posicao > 2:
            posicao = 2
            self.ui.posicao_bobina_montada.setText('2')
        elif posicao < -2:
            posicao = -2
            self.ui.posicao_bobina_montada.setText('-2')
        motortransversal(posicao, posicao)
        
    def KILL(self):
        lib.parartudo = 1
        time.sleep(0.5)
        lib.motor.Kill()
        self.Emergencia_Fonte()
        time.sleep(3)
        lib.parartudo = 0
    
    def ZERAR(self):
        lib.stop = 1
        time.sleep(1)
        lib.display.EscreveValorDisplay(0, 0)
        lib.display.EscreveValorDisplay(1, 0)
        lib.stop = 0
##        self.xyx = eixos()


    ########### ABA 4: Fonte  ###############
    
    def Valor_Equacao(self,index,Corrente,Fator_Fonte):
        y=0
        if lib.Fonte_Calibrada == [1,1]:
            if index==0:
                valores = lib.reta_escrita
            if index==1:
                valores = lib.reta_leitura
            if index==2:
                valores = [-1.60584813e-02,9.98204281e-01,-1.53421346e-05,-9.11799793e-06,1.48242302e-07,1.65268906e-07,-1.04523929e-08,-5.03470866e-09,3.77777061e-10,5.43734086e-11,-4.30811742e-12]
            for i in range(len(valores)):
                y = y + (float(valores[i])*(Corrente**i))

        if lib.Fonte_Calibrada == [1,0]:
            if index==0:
                y = Corrente/Fator_Fonte
            if index==1:
                valores = lib.reta_leitura
                for i in range(len(valores)):
                    y = y + (float(valores[i])*(Corrente**i))

        if lib.Fonte_Calibrada == [0,1]:
            if index==0:
                valores = lib.reta_escrita
                for i in range(len(valores)):
                    y = y + (float(valores[i])*(Corrente**i))
            if index==1:
                y = Corrente*Fator_Fonte
        
        if lib.Fonte_Calibrada == [0,0]:
            if index==0:
                y = Corrente/Fator_Fonte
            if index==1:
                y = Corrente*Fator_Fonte
        return y

    

    def Start_Fonte(self):
        if lib.controle_fonte == 0:  #ACRESCENTADO# Selecionado para PUC
            Seguranca_Habilitada = 1
            if (self.ui.Desab_Seg_Fonte.isChecked()) and (lib.Status_Fonte == 0):
                ret = QtGui.QMessageBox.question(self,'Atenção.','Deseja Ligar a Fonte com o Controle de Segurança DESATIVADO?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.Yes:
                    Seguranca_Habilitada = 0
                else:
                    return
            
            if (lib.Status_Fonte == 0):
                try:
                    corrente = round(lib.PUC.ReadAD(),3)
                except:
                    QtGui.QMessageBox.warning(self,'Atenção.','Impossível ler corrente PUC.',QtGui.QMessageBox.Ok)
                    return
                if corrente != 0:
                    ramp = self.Rampa(0,corrente,1,.1)
                    if ramp == False:
                        QtGui.QMessageBox.critical(lib.Janela,'Atenção.','Corrente PUC não zerada.\nImpossível ligar a fonte.',QtGui.QMessageBox.Ok)
                        return
                if Seguranca_Habilitada == 1:                
                    status = lib.PUC.ReadDigIn()
                    time.sleep(0.25)
                    if dec_bin(status,6) == 1:
                        QtGui.QMessageBox.critical(self,'Atenção.','Interlock Externo da Fonte Acionado.',QtGui.QMessageBox.Ok)
                        return
                    if dec_bin(status,5) == 1:
                        QtGui.QMessageBox.critical(self,'Atenção.','Interlock Interno da Fonte Acionado.',QtGui.QMessageBox.Ok)
                        return
    ##                status = lib.PUC.WriteDigBit(0,1)
                    status = lib.PUC.WriteDigBit(1,1)
                    if status == True:
                        time.sleep(0.5)
                        status = lib.PUC.ReadDigIn()
                        time.sleep(0.25)
                        if dec_bin(status,7) == 1:                    
                            lib.Status_Fonte = 1                                ##
                            lib.Corrente_Atual = 0                              ##
                            self.ui.Carregar_Config_Fonte.setEnabled(True)      ##
                            self.ui.groupBox_5.setEnabled(True)                 ##
                        else:
    ##                        status = lib.PUC.WriteDigBit(0,1)
                            status = lib.PUC.WriteDigBit(1,1)
                            time.sleep(0.5)
                            status = lib.PUC.ReadDigIn()
                            time.sleep(0.25)
                            if dec_bin(status,7) == 1:                        
                                lib.Status_Fonte = 1
                                lib.Corrente_Atual = 0
                                self.ui.Carregar_Config_Fonte.setEnabled(True)
                                self.ui.groupBox_5.setEnabled(True)
                            else:
                                QtGui.QMessageBox.critical(self,'Atenção.','Fonte Não Ligou.',QtGui.QMessageBox.Ok)
    ##                            status = lib.PUC.WriteDigBit(0,0)
                                status = lib.PUC.WriteDigBit(1,0)
                                return
                    else:
                        QtGui.QMessageBox.critical(self,'Atenção.','PUC Não recebeu o comando.',QtGui.QMessageBox.Ok)
                        return
                else:
    ##                status = lib.PUC.WriteDigBit(0,1)
                    status = lib.PUC.WriteDigBit(1,1)
                    time.sleep(0.5)
                    lib.Status_Fonte = 1
                    lib.Corrente_Atual = 0
                    self.ui.groupBox_5.setEnabled(True) 
            else:
    ##            status = lib.PUC.WriteDigBit(0,0)
                status = lib.PUC.WriteDigBit(1,0)
                if status == True:                
                    lib.Status_Fonte = 0
                    lib.Corrente_Atual = 0
                    lib.PUC.WriteDA(0)
                    self.ui.groupBox_5.setEnabled(False)
                    if self.ui.Nome_Fonte.text() == '':
                        self.ui.Corrente_Atual.setEnabled(False)
                else:
                    QtGui.QMessageBox.critical(self,'Atenção.','PUC Não recebeu o comando.',QtGui.QMessageBox.Ok)
                    return

        else:                           #ACRESCENTADO# Se estiver selecionado para Fonte Digital
            Seguranca_Habilitada = 1
            if (self.ui.Desab_Seg_Fonte.isChecked()) and (lib.Status_Fonte == 0):
                ret = QtGui.QMessageBox.question(self,'Atenção.','Deseja Ligar a Fonte com o Controle de Segurança DESATIVADO?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.Yes:
                    Seguranca_Habilitada = 0
                else:
                    return

            if (lib.Status_Fonte == 0):
                try:
                    corrente = round(lib.Digital.Read_iLoad1(),3)
                except:
                    QtGui.QMessageBox.warning(self,'Atenção.','Impossível ler corrente Digital.',QtGui.QMessageBox.Ok)
                    return
                if corrente != 0:
                    ramp = self.Rampa(0,corrente,1,.1)
                    if ramp == False:
                        QtGui.QMessageBox.critical(lib.Janela,'Atenção.','Corrente da fonte digital não zerada.\nImpossível ligar a fonte.',QtGui.QMessageBox.Ok)
                        return
                if Seguranca_Habilitada == 1:                
                    status = lib.Digital.Read_ps_SoftInterlocks()
                    time.sleep(0.25)
                    if status != 0:  
                        QtGui.QMessageBox.critical(self,'Atenção.','Soft Interlock da Fonte Acionado.',QtGui.QMessageBox.Ok)
                        return
                    status2 = lib.Digital.Read_ps_HardInterlocks()
                    time.sleep(0.25)
                    if status2 != 0:  
                        QtGui.QMessageBox.critical(self,'Atenção.','Hard Interlock da Fonte Acionado.',QtGui.QMessageBox.Ok)
                        return
                    lib.Digital.TurnOn()                    # Liga saída da fonte
                    time.sleep(0.5)
                    status = lib.Digital.Read_ps_OnOff()
                    if status == 1:
                        lib.Status_Fonte = 1
                        lib.Corrente_Atual = 0
                        self.ui.Carregar_Config_Fonte.setEnabled(True)
                        self.ui.groupBox_5.setEnabled(True)
                    else:
                        QtGui.QMessageBox.critical(self,'Atenção.','Fonte Não Ligou.',QtGui.QMessageBox.Ok)
                        status = lib.Digital.Read_ps_OnOff()
                        return
                    lib.Digital.ClosedLoop()                # Fecha a malha
                    time.sleep(0.5)
                    if (lib.Digital.Read_ps_OpenLoop() == 1):
                        QtGui.QMessageBox.critical(self,'Atenção.','Malha do circuito da fonte não está fechada.',QtGui.QMessageBox.Ok)
                        return
            else:
                status = lib.Digital.Read_ps_OnOff()
                if status == 1:
                    lib.Status_Fonte = 0
                    lib.Corrente_Atual = 0
                    lib.Digital.TurnOff()                    # Desliga saída da fonte
                    self.ui.groupBox_5.setEnabled(False)
                    if self.ui.Nome_Fonte.text() == '':
                        self.ui.Corrente_Atual.setEnabled(False)
                else:
                    QtGui.QMessageBox.critical(self,'Atenção.','Fonte Digital não recebeu o comando.',QtGui.QMessageBox.Ok)
                    return                        

    def Emergencia_Fonte(self):
        if lib.controle_fonte == 0:  #ACRESCENTADO# Selecionado para PUC
            if lib.Status_Fonte == 1:
                if lib.Fonte_Ciclagem == 1:
                    lib.PUC.StopCurve()
                    time.sleep(.1)
                lib.PUC.WriteDA(0)
                time.sleep(.1)
                for i in range(8):
                    lib.PUC.WriteDigBit(i,0)
            lib.Status_Fonte = 0
            lib.Fonte_Ciclagem = 0
        else:                       #ACRESCENTADO# Selecionado para Digital
            if lib.Status_Fonte == 1:
                if lib.Fonte_Ciclagem == 1:
                    lib.Digital.TurnOff()
                    time.sleep(.1)
                lib.Digital.OpMode(0)
                lib.Digital.SetISlowRef(0)
                lib.Digital.TurnOff()           # Desliga saída da fonte
                time.sleep(.1)
            lib.Status_Fonte = 0
            lib.Fonte_Ciclagem = 0
           
    
    def Salvar_Fonte(self):
        try:
            nome = str(self.ui.Nome_Fonte.text())
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Nome da Fonte Inválido.',QtGui.QMessageBox.Ok)
            return
        try:
            arquivo = QtGui.QFileDialog.getSaveFileName(self, 'Save File - Dados Fonte', nome,'Data files (*.dat);;Text files (*.txt)')
        except:
            return
        try:
            C_Linear = str(float(self.ui.Corrente_Linear.text()))
            Amp_Linear = str(float(self.ui.Amplitude_Linear.text()))
            T_Linear = str(float(self.ui.Tempo_Linear.text()))
            corrente_arbitraria = self.Converter_Corrente_Arbitraria(self.ui.Corrente_Arbitraria_PUC.toPlainText(),0)
            Amp_Sen = str(float(self.ui.Amplitude_Senoidal.text()))
            Off_Sen = str(float(self.ui.Offset_Senoidal.text()))
            D_Sen = str(float(self.ui.Defasagem_Senoidal.text()))
            P_F_Sen = str(float(self.ui.Posicao_Final_Senoidal.text()))
            Freq_Sen = str(float(self.ui.Frequencia_Senoidal.text()))
            Ciclo_Sen = str(int(self.ui.N_Ciclos_Senoidal.text()))
            Amp_Amort = str(float(self.ui.Amplitude_Senoidal_Amortecida.text()))
            Off_Amort = str(float(self.ui.Offset_Senoidal_Amortecida.text()))
            D_Amort = str(float(self.ui.Defasagem_Senoidal_Amortecida.text()))
            P_F_Amort = str(float(self.ui.Posicao_Final_Senoidal_Amortecida.text()))
            Freq_Amort = str(float(self.ui.Frequencia_Senoidal_Amortecida.text()))
            Ciclo_Amort = str(int(self.ui.N_Ciclos_Senoidal_Amortecida.text()))
            Tau_Amort = str(float(self.ui.Amortecimento_Senoidal.text()))
            F_Ent = str(float(self.ui.Fator_Entrada.text()))
            F_Saida = str(float(self.ui.Fator_Saida.text()))
            C_Max = str(float(self.ui.Corrente_Maxima_Fonte.text()))
            C_Min = str(float(self.ui.Corrente_Minima_Fonte.text()))
            DCCT = str(float(self.ui.Corrente_DCCT.text()))
            I0_calib = str(float(self.ui.Corr_Calib_Inicial.text()))
            Imax_calib = str(float(self.ui.Corr_Calib_Final.text()))
            N_calib = str(float(self.ui.Corr_Calib_Passo.text()))
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Valor não Numérico.',QtGui.QMessageBox.Ok)
            return
        try:    
            f = open(arquivo, 'w')
        except:
            return
        f.write('1\n')
        f.write('Nome da Fonte:\t' + nome + '\n')
        f.write('Corrente Linear:\t' + C_Linear +'\n')
        f.write('Amplitude Linear:\t' + Amp_Linear + '\n')
        f.write('Tempo Linear:\t' + T_Linear + '\n')
        f.write('Amplitude Senoidal:\t' + Amp_Sen + '\n')
        f.write('Offset Senoidal:\t' + Off_Sen + '\n')
        f.write('Defasagem Senoidal:\t' + D_Sen + '\n')
        f.write('Posicao Final Senoidal:\t' + P_F_Sen + '\n')
        f.write('Frequencia Senoidal:\t' + Freq_Sen + '\n')
        f.write('N Ciclos Senoidal:\t' + Ciclo_Sen + '\n')
        f.write('Amplitude Senoidal Amortecida:\t' + Amp_Amort + '\n')
        f.write('Offset Senoidal Amortecida:\t' + Off_Amort + '\n')
        f.write('Defasagem Senoidal Amortecida:\t' + D_Amort + '\n')
        f.write('Posicao Final Senoidal Amortecida:\t' + P_F_Amort + '\n')
        f.write('Frequencia Senoidal Amortecida:\t' + Freq_Amort + '\n')
        f.write('N Ciclos Senoidal Amortecida:\t' + Ciclo_Amort + '\n')
        f.write('Amortecimento:\t' + Tau_Amort + '\n')
        f.write('Fator Entrada:\t' + F_Ent + '\n')
        f.write('Fator Saida:\t' + F_Saida + '\n')
        f.write('Corrente Máxima da Fonte:\t' + C_Max + '\n')
        f.write('Corrente Mínima da Fonte:\t' + C_Min + '\n')
        f.write('Corrente Maxima DCCT:\t' + DCCT + '\n')
        f.write('Corrente Inicial Calibracao:\t' + I0_calib + '\n')
        f.write('Corrente Maxima Calibracao:\t' + Imax_calib + '\n')
        f.write('Pontos Calibracao:\t' + N_calib + '\n')
        try:
            f.write('Reta correcao escrita:\t' + str(lib.reta_escrita.tolist()) + '\n')
        except:
            f.write('Reta correcao escrita:\t' + str(lib.reta_escrita) + '\n')
        try:
            f.write('Reta correcao leitura:\t' + str(lib.reta_leitura.tolist()) + '\n')
        except:
            f.write('Reta correcao leitura:\t' + str(lib.reta_leitura) + '\n')
        f.write('Corrente Arbitraria Auto:\t' + str(corrente_arbitraria))
        f.close()
        

    def Carregar_Fonte(self):
        try:
            arquivo = QtGui.QFileDialog.getOpenFileName(self, 'Carregar Arquivo Fonte', '.','Data files (*.dat);;Text files (*.txt)')
            f = open(arquivo, 'r')
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Arquivo não foi Aberto.',QtGui.QMessageBox.Ok)
            return
        leitura = f.read().strip()
        f.close()
        dados = leitura.split('\n')
        leitura = dados
        if leitura[0] == '1':
            leitura.pop(0)
        else:
            QtGui.QMessageBox.warning(self,'Atenção.','Arquivo Incorreto.',QtGui.QMessageBox.Ok)
            return
        for i in range(len(leitura)):
            c = leitura[i].split('\t')
            dados[i] = c[1]
            
        try:
            self.ui.tabWidget_2.setEnabled(True)
            self.ui.Nome_Fonte.setText(dados[0])
            self.ui.Corrente_Linear.setText(dados[1])
            self.ui.Amplitude_Linear.setText(dados[2])
            self.ui.Tempo_Linear.setText(dados[3])
            self.ui.Amplitude_Senoidal.setText(dados[4])
            self.ui.Offset_Senoidal.setText(dados[5])
            self.ui.Defasagem_Senoidal.setText(dados[6])
            self.ui.Posicao_Final_Senoidal.setText(dados[7])
            self.ui.Frequencia_Senoidal.setText(dados[8])
            self.ui.N_Ciclos_Senoidal.setText(dados[9])
            self.ui.Amplitude_Senoidal_Amortecida.setText(dados[10])
            self.ui.Offset_Senoidal_Amortecida.setText(dados[11])
            self.ui.Defasagem_Senoidal_Amortecida.setText(dados[12])
            self.ui.Posicao_Final_Senoidal_Amortecida.setText(dados[13])
            self.ui.Frequencia_Senoidal_Amortecida.setText(dados[14])
            self.ui.N_Ciclos_Senoidal_Amortecida.setText(dados[15])
            self.ui.Amortecimento_Senoidal.setText(dados[16])
            self.ui.Fator_Entrada.setText(dados[17])
            self.ui.Fator_Saida.setText(dados[18])
            self.ui.Corrente_Maxima_Fonte.setText(dados[19])
            self.ui.Corrente_Minima_Fonte.setText(dados[20])
            self.ui.Corrente_DCCT.setText(dados[21])
            self.ui.Corr_Calib_Inicial.setText(dados[22])
            self.ui.Corr_Calib_Final.setText(dados[23])
            self.ui.Corr_Calib_Passo.setText(dados[24])
##            self.celulas = numpy.array([])
##            self.colunas = numpy.array([])
##            self.indice = numpy.arange(0,7)
##            for i in range (7):
##                for j in range (1,3):
##                    self.cell = self.ui.tabela_config.setCurrentCell(i,j)
##                    self.celltext = self.ui.tabela_config.currentItem().text()
##                    self.celulas = numpy.append(self.celulas,self.celltext)
##                self.createarray = numpy.asarray(self.celulas, dtype='float')
##            reshape = self.createarray.reshape((7,2))
##            print(reshape[0,1])
##            print(reshape[3,1])
##            print(reshape)
            try:
                lib.reta_escrita = (self.Recuperar_Valor(1,dados[25]))
                lib.Fonte_Calibrada[1] = 1
            except:
                lib.Fonte_Calibrada[1] = 0
                pass
            try:
                lib.reta_leitura = (self.Recuperar_Valor(1,dados[26]))
                lib.Fonte_Calibrada[0] = 1
            except:
                lib.Fonte_Calibrada[0] = 0
                pass
            try:
                self.ui.Corrente_Arbitraria_PUC.setPlainText(self.Recuperar_Valor(0,dados[27]))
            except:
                pass
            self.ui.Corrente_Atual.setEnabled(True)
            lib.Fonte_Pronta = 1
            self.ui.Chk_Auto.setEnabled(True)
            self.ui.tabWidget_3.setEnabled(True)            #ACRESCENTADO#
            self.ui.groupBox_40.setEnabled(True)            #groupbox da bobina trim ACRESCENTADO#
            QtGui.QApplication.processEvents()
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Dados da Fonte Incompletos.',QtGui.QMessageBox.Ok)
            return

    def Habilitar_trim(self):                               #ACRESCENTADO#
        if lib.controle_fonte == 1:
            if self.ui.check_aux.isChecked():
                self.ui.check_TrimCoil.setEnabled(True)
                self.ui.check_chCoil.setEnabled(True)
                self.ui.check_cvCoil.setEnabled(True)
                self.ui.check_qsCoil.setEnabled(True)
            else:
                self.ui.check_TrimCoil.setEnabled(False)
                self.ui.check_chCoil.setEnabled(False)
                self.ui.check_cvCoil.setEnabled(False)
                self.ui.check_qsCoil.setEnabled(False)
        else:
            QtGui.QMessageBox.warning(self,'Atenção.','A fonte deve ser digital para realização da leitura das correntes auxiliares.',QtGui.QMessageBox.Ok)
            return


        ########### ABA 4.1: Curva Linear ###########
    def Verificar_Limite_Corrente(self,index,Corrente,offset=0): ## index = 0 (Manual_C/msg)  index = 1 (Auto_S/msg) index = 2 (Ciclagem)
        Corrente = float(Corrente)
        try:
            Corrente_Maxima = float(self.ui.Corrente_Maxima_Fonte.text())
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Valor Incorreto para Corrente Maxima da Fonte.\n                    Verifique o Valor.',QtGui.QMessageBox.Ok)
            Corrente = 'False'
            return (Corrente)
        try:
            Corrente_Minima = float(self.ui.Corrente_Minima_Fonte.text())
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Valor Incorreto para Corrente Minima da Fonte.\n                    Verifique o Valor.',QtGui.QMessageBox.Ok)
            Corrente = 'False'
            return (Corrente)
        
        if (index == 0) or (index == 1):
            if (Corrente)>(Corrente_Maxima):
                if (index == 0):
                    QtGui.QMessageBox.warning(self,'Atenção.','Valor de Corrente Superior ao Limite da Fonte.',QtGui.QMessageBox.Ok)
                Corrente = Corrente_Maxima
            if (Corrente)<(Corrente_Minima):
                if (index == 0):
                    QtGui.QMessageBox.warning(self,'Atenção.','Valor de Corrente Inferior ao Limite da Fonte.',QtGui.QMessageBox.Ok)
                Corrente = Corrente_Minima
        if (index == 2):
            if ((Corrente/2)+offset) > (Corrente_Maxima):
                QtGui.QMessageBox.warning(self,'Atenção.','Verificar valores da Corrente de Pico a Pico e Offset.\nValores fora do Limite da Fonte.',QtGui.QMessageBox.Ok)
                Corrente = 'False'
                return (Corrente)
            
            if ((-Corrente/2)+offset) < (Corrente_Minima):
                QtGui.QMessageBox.warning(self,'Atenção.','Verificar valores da Corrente de Pico a Pico e Offset.\nValores fora do Limite da Fonte.',QtGui.QMessageBox.Ok)
                Corrente = 'False'
                return (Corrente)
            
        return(float(Corrente))
    
    def Corrente_Fonte(self):
        try:
            if lib.controle_fonte == 0:             #ACRESCENTADO# Seleciona a PUC
                if self.ui.cb_PUC.isChecked():      #ACRESCENTADO# Check box PUC
                    time.sleep(.1)
                    corrente = round(self.Valor_Equacao(1,lib.PUC.ReadAD(),float(self.ui.Fator_Entrada.text())),3)
                    self.ui.lcd_Corrente.display(corrente)
    ##                QtGui.QApplication.processEvents()
                    self.ui.lcd_Corrente.setEnabled(True)
                    self.ui.label_163.setEnabled(True)
                    self.ui.label_97.setEnabled(True)
                else:
                    self.ui.lcd_Corrente.setEnabled(False)
                    self.ui.label_163.setEnabled(False)
                    self.ui.label_97.setEnabled(False)
                if self.ui.cb_DCCT.isChecked():
                    time.sleep(.1)
                    if self.ui.label_multimetro.text()!='Conectado':
                        QtGui.QMessageBox.warning(self,'Atenção.','Para ler corrente no DCCT conectar Multimetro GPIB.\nTente Novamente.',QtGui.QMessageBox.Ok)
                        return
                    self.ui.lcd_Corrente_DCCT.setEnabled(True)
                    self.ui.label_161.setEnabled(True)
                    self.ui.label_164.setEnabled(True)
                    corrente2 = round(self.ConverteDCCT(), 3)
                    self.ui.lcd_Corrente_DCCT.display(corrente2)
                    QtGui.QApplication.processEvents()
                else:
                    self.ui.lcd_Corrente_DCCT.setEnabled(False)
                    self.ui.label_161.setEnabled(False)
                    self.ui.label_164.setEnabled(False)
            else:                                   #ACRESCENTADO# Seleciona a Fonte Digital
                time.sleep(.1)
                self.ui.lcd_Corrente.setEnabled(False)
                self.ui.label_163.setEnabled(False)
                self.ui.label_97.setEnabled(False)
                self.ui.cb_PUC.setEnabled(False)
                corrente3 = round(float(lib.Digital.Read_iLoad1()), 3)
                self.ui.lcd_Corrente_Digital.display(corrente3)
                if self.ui.cb_DCCT.isChecked():
                    time.sleep(.1)
                    if self.ui.label_multimetro.text()!='Conectado':
                        QtGui.QMessageBox.warning(self,'Atenção.','Para ler corrente no DCCT conectar Multimetro GPIB.\nTente Novamente.',QtGui.QMessageBox.Ok)
                        return
                    self.ui.lcd_Corrente_DCCT.setEnabled(True)
                    self.ui.label_161.setEnabled(True)
                    self.ui.label_164.setEnabled(True)
                    corrente4 = round(self.ConverteDCCT(), 3)           # Para a fonte digital de 225 A 
                    self.ui.lcd_Corrente_DCCT.display(corrente4)
                    QtGui.QApplication.processEvents()
                
                QtGui.QApplication.processEvents()
                
        except:
            if lib.Status_Fonte == 1:
                QtGui.QMessageBox.warning(self,'Atenção.','Verificar Dados da Fonte.',QtGui.QMessageBox.Ok)
            return

    def ConverteDCCT(self):                     #ACRESCENTADO# 
        self.variavel = lib.GPIB.Coleta_Multimetro()
        if self.ui.DCCT_select.currentIndex() == 0:   #Para cabeça de 40A
            self.num = (float(self.variavel))*4
        if self.ui.DCCT_select.currentIndex() == 1:   #Para cabeça de 160A
            self.num = (float(self.variavel))*16
        if self.ui.DCCT_select.currentIndex() == 2:   #Para cabeça de 320A
            self.num = (float(self.variavel))*32            
        return self.num

    def Converte_DCCT_MultiCanal(self):         #ACRESCENTADO#
        self.variavel = lib.GPIB.Coleta_Multicanal()
        if self.ui.DCCT_select.currentIndex() == 0:   #Para cabeça de 40A
            self.num = (float(self.variavel))*4
        if self.ui.DCCT_select.currentIndex() == 1:   #Para cabeça de 160A
            self.num = (float(self.variavel))*16
        if self.ui.DCCT_select.currentIndex() == 2:   #Para cabeça de 320A
            self.num = (float(self.variavel))*32            
        return self.num
    

    def Rampa(self,final,atual,passo,tempo):
        status_final = []
        if lib.controle_fonte == 0:             #ACRESCENTADO# Seleciona a PUC
            try:
                if final > atual:
                    faixa = numpy.arange(atual+passo,final,passo)
                else:
                    faixa = numpy.arange(final,atual,passo)
                    faixa = faixa[::-1]
                faixa[-1] = final
                for i in faixa:
                    if (lib.parartudo == 0):
                        time.sleep(tempo)
                        lib.PUC.WriteDA(i)
                    else:
                        lib.PUC.WriteDA(0)
                        time.sleep(0.1)
                        return False
                self.Corrente_Fonte()
                return True

    ######
    ##            f_saida = float(self.ui.Fator_Saida.text())
    ##            if final == self.Valor_Equacao(0,0,f_saida):
    ##                self.Corrente_Fonte()
    ##                return True
    ##            else:
    ##                for i in range(3):
    ##                    status_final.append(lib.PUC.ReadAD())
    ##                    time.sleep(.1)
    ##                avg_status_final = numpy.mean(status_final)
    ####                print(final)
    ####                print(avg_status_final)
    ##                if (abs((avg_status_final - final)/final))<(0.1):
    ##                    self.Corrente_Fonte()
    ##                    return True
    ##                else:
    ##                    QtGui.QMessageBox.warning(self,'Atenção.','Corrente Final Não Atingida.',QtGui.QMessageBox.Ok)
    ##                    return False
    ######
            
            except:
                try:
                    if ((final>atual) and ((final-atual)<passo)) or ((final<atual) and ((atual-final)<passo)):
                        lib.PUC.WriteDA(final)
                        self.Corrente_Fonte()
                        return True

                    
    ##                    f_saida = float(self.ui.Fator_Saida.text())
    ##                    if final == self.Valor_Equacao(0,0,f_saida):
    ##                        self.Corrente_Fonte()
    ##                        return True
    ##                    else:
    ##                        for i in range(3):
    ##                            status_final.append(lib.PUC.ReadAD())
    ##                            time.sleep(.1)
    ##                        avg_status_final = numpy.mean(status_final)
    ####                        print(final)
    ####                        print(avg_status_final)
    ##                        if (abs((avg_status_final - final)/final))<(0.1):
    ##                            self.Corrente_Fonte()
    ##                            return True
    ##                        else:
    ##                            QtGui.QMessageBox.warning(self,'Atenção.','Corrente Final Não Atingida.',QtGui.QMessageBox.Ok)
    ##                            return False

                    
                except:
                    return False
        else:                               #ACRESCENTADO# Seleciona a Fonte Digital.  
            mode = 0            
            lib.Digital.OpMode(mode) #Seleciona o mode = 0 (Operação Slowref)
            try:
                if final > atual:
                    faixa = numpy.arange(atual+passo,final,passo)
                else:
                    faixa = numpy.arange(final,atual,passo)
                    faixa = faixa[::-1]
                faixa[-1] = final
                for i in faixa:
                    if (lib.parartudo == 0):
                        time.sleep(tempo)
                        lib.Digital.SetISlowRef(i)  
                    else:
                        lib.Digital.SetISlowRef(0)
                        time.sleep(0.1)
                        return False
                self.Corrente_Fonte()
                return True
            except:
                try:
                    if ((final>atual) and ((final-atual)<passo)) or ((final<atual) and ((atual-final)<passo)):
                        lib.Digital.SetISlowRef(final)
                        self.Corrente_Fonte()
                        return True
                except:
                    return False
        
    def Rampa_Corrente_Manual(self):
##        atual = round(lib.PUC.ReadDA(),3)
        if lib.controle_fonte == 0:                 #ACRESCENTADO# Seleciona a PUC
            atual = round(lib.PUC.ReadAD(),3)
            try:
                f_saida = float(self.ui.Fator_Saida.text())
                final = self.Verificar_Limite_Corrente(0,float(self.ui.Corrente_Linear.text()))
                if (final == 'False'):
                    return
                self.ui.Corrente_Linear.setText(str(final))
                final = self.Valor_Equacao(0,final,f_saida)
                lib.Corrente_Atual = float(self.ui.Corrente_Linear.text())
                passo = (float(self.ui.Amplitude_Linear.text()))/f_saida
                tempo = float(self.ui.Tempo_Linear.text())
    ##            if final > 10:
    ##                final = atual
    ##                QtGui.QMessageBox.warning(self,'Atenção.','Valor fora dos Limites da Fonte.',QtGui.QMessageBox.Ok)
    ##            elif final < -10:
    ##                final = atual
    ##                QtGui.QMessageBox.warning(self,'Atenção.','Valor fora dos Limites da Fonte.',QtGui.QMessageBox.Ok)
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Valor Incorretos ou não Numérico.',QtGui.QMessageBox.Ok)
                return
            
            self.ui.tabWidget_2.setEnabled(False)
    ##        self.ui.coletar.setEnabled(False)
    ##        self.ui.Carregar_Config_Fonte.setEnabled(False)
    ##        self.ui.Corrente_Atual.setEnabled(False)
    ##        lib.Fonte_Pronta = 0
            QtGui.QApplication.processEvents()

    ##        Rampa_Corrente(final,atual,passo,tempo)
            ramp = self.Rampa(final,atual,passo,tempo)
            
            if ramp == True:
                QtGui.QMessageBox.information(lib.Janela,'Aviso.','Corrente atingida com Sucesso.',QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.critical(self,'Atenção.','Falha! Verifique Valores da Fonte.',QtGui.QMessageBox.Ok)
            self.ui.tabWidget_2.setEnabled(True)
            QtGui.QApplication.processEvents()

        else:                                       #ACRESCENTADO# Seleciona a Fonte Digital.
            atual = round(float(lib.Digital.Read_iLoad1()),3)
            try:
                f_saida = float(self.ui.Fator_Saida.text())
                final = self.Verificar_Limite_Corrente(0,float(self.ui.Corrente_Linear.text()))
                if (final == 'False'):
                    return
                self.ui.Corrente_Linear.setText(str(final))
##                final = self.Valor_Equacao(0,final,f_saida)
                lib.Corrente_Atual = float(self.ui.Corrente_Linear.text())
                passo = (float(self.ui.Amplitude_Linear.text()))/f_saida
                tempo = float(self.ui.Tempo_Linear.text())
    ##            if final > 10:
    ##                final = atual
    ##                QtGui.QMessageBox.warning(self,'Atenção.','Valor fora dos Limites da Fonte.',QtGui.QMessageBox.Ok)
    ##            elif final < -10:
    ##                final = atual
    ##                QtGui.QMessageBox.warning(self,'Atenção.','Valor fora dos Limites da Fonte.',QtGui.QMessageBox.Ok)
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Valor Incorretos ou não Numérico.',QtGui.QMessageBox.Ok)
                return
            
            self.ui.tabWidget_2.setEnabled(False)
    ##        self.ui.coletar.setEnabled(False)
    ##        self.ui.Carregar_Config_Fonte.setEnabled(False)
    ##        self.ui.Corrente_Atual.setEnabled(False)
    ##        lib.Fonte_Pronta = 0
            QtGui.QApplication.processEvents()

    ##        Rampa_Corrente(final,atual,passo,tempo)
            ramp = self.Rampa(final,atual,passo,tempo)
            
            if ramp == True:
                QtGui.QMessageBox.information(lib.Janela,'Aviso.','Corrente atingida com Sucesso.',QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.critical(self,'Atenção.','Falha! Verifique Valores da Fonte.',QtGui.QMessageBox.Ok)
            self.ui.tabWidget_2.setEnabled(True)
            QtGui.QApplication.processEvents()
            

    def Rampa_Corrente_Automatico(self,dados_corrente,dados_selecao_correntes):
        if lib.controle_fonte == 0:                 #ACRESCENTADO# Seleciona a PUC
            try:
                f_saida = float(self.ui.Fator_Saida.text())
                passo = float(self.ui.Amplitude_Linear.text())/f_saida
                tempo = float(self.ui.Tempo_Linear.text())
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Valor não Numérico.',QtGui.QMessageBox.Ok)
                return
            for i in range(len(dados_corrente)):
                dados_corrente[i] = self.Valor_Equacao(0,dados_corrente[i],f_saida)
            for i in range(len(dados_corrente)):
                if dados_selecao_correntes[i] == 'Y' or dados_selecao_correntes[i] == 'y' or dados_selecao_correntes[i] == 'S' or dados_selecao_correntes[i] == 's':
                    corrente_atual = round(lib.PUC.ReadAD(),3)
                    self.Rampa(dados_corrente[i],corrente_atual,passo,tempo)
                    time.sleep(.2)
                    self.Correcao_Posicao()
                    Verificar = ColetaDados(len(dados_corrente))
                    if Verificar == False:
                        QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Processo de Medição Interrompido. Desvio Padrão Elevado.',QtGui.QMessageBox.Ok)
                        ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Desvio Padrão Elevado.\nDeseja Salvar a Medida?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                        if ret == QtGui.QMessageBox.Yes:
                            pass
                        else:
                            ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Deseja continuar o Processo de Medição?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                            if ret == QtGui.QMessageBox.Yes:
                                continue
                            else:
                                self.ui.groupBox_2.setEnabled(True)
                                self.ui.coletar.setEnabled(True)
                                QtGui.QApplication.processEvents()
                                return
                    time.sleep(.1)
                    self.Salvar_Coletas(1,i+1,(self.Valor_Equacao(1,dados_corrente[i],f_saida)))
                    self.ui.label_138.setText(str(i+1))
                    QtGui.QApplication.processEvents()
                else:
                    if abs(dados_corrente[i]-dados_corrente[i-1]) > passo:
                        corrente_atual = round(lib.PUC.ReadAD(),3)
                        self.Rampa(dados_corrente[i],corrente_atual,passo,tempo)
                    else:
                        lib.PUC.WriteDA(dados_corrente[i])
    ##                    time.sleep(.02) ## Delay entre pontos para conservar a fonte.
      
            QtGui.QMessageBox.information(lib.Janela,'Atenção.','Processo de Coleta Automática Concluído.',QtGui.QMessageBox.Ok)

        else:                                           #ACRESCENTADO# Seleciona a Fonte Digital.
            try:
                f_saida = float(self.ui.Fator_Saida.text())
                passo = float(self.ui.Amplitude_Linear.text())/f_saida
                tempo = float(self.ui.Tempo_Linear.text())
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Valor não Numérico.',QtGui.QMessageBox.Ok)
                return
##            for i in range(len(dados_corrente)):
##                dados_corrente[i] = self.Valor_Equacao(0,dados_corrente[i],f_saida)
            for i in range(len(dados_corrente)):
                if dados_selecao_correntes[i] == 'Y' or dados_selecao_correntes[i] == 'y' or dados_selecao_correntes[i] == 'S' or dados_selecao_correntes[i] == 's':
                    corrente_atual = round(float(lib.Digital.Read_iLoad1()),3)
                    self.Rampa(dados_corrente[i],corrente_atual,passo,tempo)
                    time.sleep(.2)
                    self.Correcao_Posicao()
                    Verificar = ColetaDados(len(dados_corrente))
                    if Verificar == False:
                        QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Processo de Medição Interrompido. Desvio Padrão Elevado.',QtGui.QMessageBox.Ok)
                        ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Desvio Padrão Elevado.\nDeseja Salvar a Medida?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                        if ret == QtGui.QMessageBox.Yes:
                            pass
                        else:
                            ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Deseja continuar o Processo de Medição?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                            if ret == QtGui.QMessageBox.Yes:
                                continue
                            else:
                                lib.Janela.ui.groupBox_2.setEnabled(True)
                                lib.Janela.ui.coletar.setEnabled(True)
                                QtGui.QApplication.processEvents()
                                return
                    time.sleep(.1)
                    self.Salvar_Coletas(1,i+1,(self.Valor_Equacao(1,dados_corrente[i],f_saida)))
                    self.ui.label_138.setText(str(i+1))
                    QtGui.QApplication.processEvents()
                else:
                    if abs(dados_corrente[i]-dados_corrente[i-1]) > passo:
                        corrente_atual = round(float(lib.Digital.Read_iLoad1()),3)
                        self.Rampa(dados_corrente[i],corrente_atual,passo,tempo)
                    else:
                        lib.Digital.SetISlowRef(dados_corrente[i])
    ##                    time.sleep(.02) ## Delay entre pontos para conservar a fonte.
      
            QtGui.QMessageBox.information(lib.Janela,'Atenção.','Processo de Coleta Automática Concluído.',QtGui.QMessageBox.Ok)
         
    def Hab_Auto(self):
        if self.ui.Chk_Auto.isChecked():
            self.ui.Hab_Corretora.setEnabled(False)
            self.ui.C_Sucessivas.setEnabled(False)
        else:
            self.ui.Hab_Corretora.setEnabled(True)
            self.ui.C_Sucessivas.setEnabled(True)

            
        ########### ABA 4.2: Curva  ###########
    def Verificar_Dados_Curva(self,index): ## index=0 Escreve vetor de dados    index=1 compara dados
        Tipo_Curva = int(self.ui.tabWidget_3.currentIndex())
        if index == 0:
            lib.Dados_Curva=[]
            try:
                if Tipo_Curva == 0:         #Senoidal
                        lib.Dados_Curva.append(self.ui.Offset_Senoidal.text())
                        lib.Dados_Curva.append(self.ui.Amplitude_Senoidal.text())
                        lib.Dados_Curva.append(self.ui.Frequencia_Senoidal.text())
                        lib.Dados_Curva.append(self.ui.Defasagem_Senoidal.text())
                        lib.Dados_Curva.append(self.ui.N_Ciclos_Senoidal.text())
                        lib.Dados_Curva.append(self.ui.Posicao_Final_Senoidal.text())
                                        
                if Tipo_Curva == 1:         #Senoidal Amortecida
                    lib.Dados_Curva.append(self.ui.Offset_Senoidal_Amortecida.text())
                    lib.Dados_Curva.append(self.ui.Amplitude_Senoidal_Amortecida.text())
                    lib.Dados_Curva.append(self.ui.Frequencia_Senoidal_Amortecida.text())
                    lib.Dados_Curva.append(self.ui.Defasagem_Senoidal_Amortecida.text())
                    lib.Dados_Curva.append(self.ui.N_Ciclos_Senoidal_Amortecida.text())
                    lib.Dados_Curva.append(self.ui.Posicao_Final_Senoidal_Amortecida.text())
                    lib.Dados_Curva.append(self.ui.Amortecimento_Senoidal.text())

##                if Tipo_Curva == 2:         #ACRESCENTADO triangular suavizada
##                    ordem = numpy.array([])
##                    for i in range (7):
##                        cell1 = self.ui.tabela_config.setCurrentCell(i,2)
##                        valor = self.ui.tabela_config.currentItem().text()
##                        ordem = numpy.append(ordem, valor)
##                        amplitude = max(ordem)
##                    lib.Dados_Curva.append(amplitude)                       #Amplitude = lib.Dados_Curva[0]
##                    cell = self.ui.tabela_config.setCurrentCell(6,1)        
##                    periodo = self.ui.tabela_config.currentItem().text()
##                    lib.Dados_Curva.append(float(1/periodo*10E-03))         #Frequência = lib.Dados_Curva[1]                    
##                    lib.Dados_Curva.append(self.ui.Ciclos_Curva_2.text())   #Número de ciclos = lib.Dados_Curva[2]
##                    
                lib.Dados_Curva.append(self.ui.Fator_Entrada.text())
                lib.Dados_Curva.append(self.ui.Fator_Saida.text())
                lib.Dados_Curva.append(self.ui.Corrente_Maxima_Fonte.text())
                lib.Dados_Curva.append(self.ui.Corrente_Minima_Fonte.text())
                return True
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Dados Incorretos.',QtGui.QMessageBox.Ok)
                return False
            
        if index == 1:
            try:
                if Tipo_Curva == 0:         #Senoidal
                    if lib.Dados_Curva[0] == self.ui.Offset_Senoidal.text():
                        if lib.Dados_Curva[1] == self.ui.Amplitude_Senoidal.text():
                            if lib.Dados_Curva[2] == self.ui.Frequencia_Senoidal.text():
                                if lib.Dados_Curva[3] == self.ui.Defasagem_Senoidal.text():
                                    if lib.Dados_Curva[4] == self.ui.N_Ciclos_Senoidal.text():
                                        if lib.Dados_Curva[5] == self.ui.Posicao_Final_Senoidal.text():
                                            if lib.Dados_Curva[6] == self.ui.Fator_Entrada.text():
                                                if lib.Dados_Curva[7] == self.ui.Fator_Saida.text():
                                                    if lib.Dados_Curva[8] == self.ui.Corrente_Maxima_Fonte.text():
                                                        if lib.Dados_Curva[9] == self.ui.Corrente_Minima_Fonte.text():
                                                            return True
                    return False
                if Tipo_Curva == 1:         #Senoidal Amortecida
                    if lib.Dados_Curva[0] == self.ui.Offset_Senoidal_Amortecida.text():
                        if lib.Dados_Curva[1] == self.ui.Amplitude_Senoidal_Amortecida.text():
                            if lib.Dados_Curva[2] == self.ui.Frequencia_Senoidal_Amortecida.text():
                                if lib.Dados_Curva[3] == self.ui.Defasagem_Senoidal_Amortecida.text():
                                    if lib.Dados_Curva[4] == self.ui.N_Ciclos_Senoidal_Amortecida.text():
                                        if lib.Dados_Curva[5] == self.ui.Posicao_Final_Senoidal_Amortecida.text():
                                            if lib.Dados_Curva[6] == self.ui.Amortecimento_Senoidal.text():
                                                if lib.Dados_Curva[7] == self.ui.Fator_Entrada.text():
                                                    if lib.Dados_Curva[8] == self.ui.Fator_Saida.text():
                                                        if lib.Dados_Curva[9] == self.ui.Corrente_Maxima_Fonte.text():
                                                            if lib.Dados_Curva[10] == self.ui.Corrente_Minima_Fonte.text():
                                                                return True
                    return False
##                if Tipo_Curva == 2:         #Triangular suavizada
##                    if lib.Dados_Curva[0] == self.ui.Offset_Senoidal_Amortecida.text():
##                        if lib.Dados_Curva[1] == self.ui.Amplitude_Senoidal_Amortecida.text():
##                            if lib.Dados_Curva[2] == self.ui.Frequencia_Senoidal_Amortecida.text():
##                                if lib.Dados_Curva[3] == self.ui.Defasagem_Senoidal_Amortecida.text():
##                                    if lib.Dados_Curva[4] == self.ui.N_Ciclos_Senoidal_Amortecida.text():
##                                        if lib.Dados_Curva[5] == self.ui.Posicao_Final_Senoidal_Amortecida.text():
##                                            if lib.Dados_Curva[6] == self.ui.Amortecimento_Senoidal.text():
##                                                if lib.Dados_Curva[7] == self.ui.Fator_Entrada.text():
##                                                    if lib.Dados_Curva[8] == self.ui.Fator_Saida.text():
##                                                        if lib.Dados_Curva[9] == self.ui.Corrente_Maxima_Fonte.text():
##                                                            if lib.Dados_Curva[10] == self.ui.Corrente_Minima_Fonte.text():
##                                                                return True
##                    return False
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Dados Incorretos.',QtGui.QMessageBox.Ok)
                return False
        

    def Plotar_Curva(self):
        if lib.controle_fonte == 0:                 #ACRESCENTADO# Seleciona a PUC
            try:
                f_saida = float(self.ui.Fator_Saida.text())
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Valor não Numérico.',QtGui.QMessageBox.Ok)
                return
            if (lib.Modelo_PUC == 0):
                try:
                    curva, checksum, pontos, ciclos, freq = self.Gerar_Curva()
                except:
                    return
                ciclos = int((ciclos * const.Clock_Puc)/freq)
            else:
                try:
                    pontos, checksum, ciclos, freq = self.Gerar_Curva()
                    
                except:
                    
                    traceback.print_exc(file=sys.stdout)
                    return
                
            for i in range(len(pontos)):
                pontos[i]=pontos[i]*f_saida
            pontos = pontos[:ciclos]
    ##        print(pontos[0:100])
            plt.plot(pontos)
            plt.show()

        else:                                       #ACRESCENTADO# Seleciona a fonte digital
            try:
                f_saida = float(self.ui.Fator_Saida.text())
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Valor não Numérico.',QtGui.QMessageBox.Ok)
                return
            
            pontos = lib.Digital.Recv_wfmRef_Curve(0,pontos)  #Recebe os pontos float da curva
            print(pontos[:20], 'Plotar')
##            for i in range(len(pontos)):
##                pontos[i]=pontos[i]*f_saida
##            pontos = pontos[:int(self.ui.Ciclos_Curva_2.text())]
    ##        print(pontos[0:100])
            plt.plot(pontos)
            plt.show()
            

    def Enviar_Curva(self):
        resp = self.Verificar_Dados_Curva(0)
        if resp == False:
            return
        self.ui.tabWidget_2.setEnabled(False)
        QtGui.QApplication.processEvents()

        if lib.controle_fonte == 0:                 #ACRESCENTADO# Seleciona a PUC         
            if (lib.Modelo_PUC == 0):
                try:
                    curva, checksum, pontos, ciclos, freq = self.Gerar_Curva()
                except:
                    self.ui.tabWidget_2.setEnabled(True)
                    return
                check = lib.PUC.SendCurve(curva)
            else:
                try:
                    pontos, checksum, ciclos, freq = self.Gerar_Curva()
                except:
                    self.ui.tabWidget_2.setEnabled(True)
                    return
                check = lib.PUC.SendCurve(pontos,True)
                
            self.ui.tabWidget_2.setEnabled(True)
            QtGui.QApplication.processEvents()
            if check == checksum:
                QtGui.QMessageBox.warning(self,'Atenção.','Envio da Curva com Sucesso.',QtGui.QMessageBox.Ok)
                self.ui.Ciclar.setEnabled(True)
                self.ui.Analise_Frequencia.setEnabled(True)
                return True
            else:
                QtGui.QMessageBox.warning(self,'Atenção.','Falha no envio da Curva.',QtGui.QMessageBox.Ok)
                return False

        else:                                       #ACRESCENTADO# Seleciona a fonte digital
            if (self.Gerar_Curva() == True):
                QtGui.QMessageBox.warning(self,'Atenção.','Envio da Curva com Sucesso.',QtGui.QMessageBox.Ok)
                self.ui.tabWidget_2.setEnabled(True)
                self.ui.Ciclar.setEnabled(True)
                self.ui.Analise_Frequencia.setEnabled(True)
                QtGui.QApplication.processEvents()
            else:
                QtGui.QMessageBox.warning(self,'Atenção.','Falha no envio da Curva.',QtGui.QMessageBox.Ok)
                self.ui.tabWidget_2.setEnabled(True)
                QtGui.QApplication.processEvents()
                return False
                

    def Gerar_Curva(self):
        
        Tipo_Curva = int(self.ui.tabWidget_3.currentIndex())
        
        try:
            f_saida = float(self.ui.Fator_Saida.text())
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro de Fator de Saída na Configuração.',QtGui.QMessageBox.Ok)
            return False 
               
        try:                                    #Definindo Offset
            if Tipo_Curva == 0:
                self.offset = self.Verificar_Limite_Corrente(0,float(self.ui.Offset_Senoidal.text()))
                if (self.offset == 'False'):
                    self.ui.Offset_Senoidal.setText('0')
                    return False
                self.ui.Offset_Senoidal.setText(str(self.offset))
            if Tipo_Curva == 1:
                self.offset = self.Verificar_Limite_Corrente(0,float(self.ui.Offset_Senoidal_Amortecida.text()))
                if (self.offset == 'False'):
                    self.ui.Offset_Senoidal_Amortecida.setText('0')
                    return False
                self.ui.Offset_Senoidal_Amortecida.setText(str(self.offset))
            if Tipo_Curva == 2:
                self.offset = 0                     #ACRESCENTADO#
                
            if Tipo_Curva == 6:
                self.offset = 0
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro do Offset da Curva.',QtGui.QMessageBox.Ok)
            return False
                
        try:                                    #Definindo Amplitude
            if lib.controle_fonte == 0:         #ACRESCENTADO# Seleciona a PUC
                if Tipo_Curva == 0:               
                    Amp = self.Verificar_Limite_Corrente(2,abs(float(self.ui.Amplitude_Senoidal.text())),self.offset)
                    if (Amp == 'False'):
                        self.ui.Amplitude_Senoidal.setText('0')
                        return False
                    self.ui.Amplitude_Senoidal.setText(str(Amp))
                if Tipo_Curva == 1:               
                    Amp = self.Verificar_Limite_Corrente(2,abs(float(self.ui.Amplitude_Senoidal_Amortecida.text())),self.offset)
                    if (Amp == 'False'):
                        self.ui.Amplitude_Senoidal_Amortecida.setText('0')
                        return False
                    self.ui.Amplitude_Senoidal_Amortecida.setText(str(Amp))
                if Tipo_Curva == 6:
                    Amp = self.Verificar_Limite_Corrente(2,abs(float(self.ui.Amplitude_Curva_Arbitraria.text())),self.offset)
                    if (Amp == 'False'):
                        self.ui.Amplitude_Curva_Arbitraria.setText('0')
                        return False
                    self.ui.Amplitude_Curva_Arbitraria.setText(str(Amp))

            else:                                #ACRESCENTADO# Seleciona a fonte digital
                self.ui.label_92.setVisible(False)
                self.ui.label_91.setVisible(False)
                self.ui.label_173.setVisible(True)
                self.ui.label_173.setEnabled(True)
                self.ui.label_174.setVisible(True)
                self.ui.label_174.setEnabled(True)
                if Tipo_Curva == 0:               
                    Amp = self.Verificar_Limite_Corrente(2,abs(float(self.ui.Amplitude_Senoidal.text())),self.offset)
                    if (Amp == 'False'):
                        self.ui.Amplitude_Senoidal.setText('0')
                        return False
                    self.ui.Amplitude_Senoidal.setText(str(Amp))
                if Tipo_Curva == 1:               
                    Amp = self.Verificar_Limite_Corrente(2,abs(float(self.ui.Amplitude_Senoidal_Amortecida.text())),self.offset)
                    if (Amp == 'False'):
                        self.ui.Amplitude_Senoidal_Amortecida.setText('0')
                        return False
                    self.ui.Amplitude_Senoidal_Amortecida.setText(str(Amp))
##                if Tipo_Curva == 2:
##                    Amp = self.Verificar_Limite_Corrente(2,abs(float(self.ui.Amplitude_Triangular_Suavizada.text())),self.offset)
##                    if (Amp == 'False'):
##                        self.ui.Amplitude_Curva_Arbitraria.setText('0')
##                        return False
##                    self.ui.Amplitude_Triangular_Suavizada.setText(str(Amp))
                if Tipo_Curva == 6:
                    Amp = self.Verificar_Limite_Corrente(2,abs(float(self.ui.Amplitude_Curva_Arbitraria.text())),self.offset)
                    if (Amp == 'False'):
                        self.ui.Amplitude_Curva_Arbitraria.setText('0')
                        return False
                    self.ui.Amplitude_Curva_Arbitraria.setText(str(Amp))                
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro da Amplitude de pico da Curva.',QtGui.QMessageBox.Ok)
            return False

        try:                                     #Definindo Frequência
            if Tipo_Curva == 0:
                freq = float(self.ui.Frequencia_Senoidal.text())
            if Tipo_Curva == 1:
                freq = float(self.ui.Frequencia_Senoidal_Amortecida.text())
            if Tipo_Curva == 6:
                freq = float(self.ui.Frequencia_Curva_Arbitraria.text())
            if Tipo_Curva == 2:
                self.cell = self.ui.tabela_config.setCurrentCell(6,1)
                self.celltext = self.ui.tabela_config.currentItem().text()
                self.calc = (1/(float(self.celltext)/1000))                         # Cálculo da frequência
                self.addtext = self.ui.frequencia_triangular_suavizada.setText(str(self.calc))
                freq = float(self.ui.frequencia_triangular_suavizada.text())        #ACRESCENTADO#
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro da Frequencia da Curva.',QtGui.QMessageBox.Ok)
            return False
        
        try:                                     #Definindo Número de ciclos
            if Tipo_Curva == 0:
                total_ciclo = int(self.ui.N_Ciclos_Senoidal.text())
            if Tipo_Curva == 1:
                total_ciclo = int(self.ui.N_Ciclos_Senoidal_Amortecida.text())
            if Tipo_Curva == 6:
                total_ciclo = int(self.ui.N_Ciclos_Curva_Arbitraria.text())
            if Tipo_Curva == 2:
                total_ciclo = int(self.ui.Ciclos_Curva_2.text())        #ACRESCENTADO#
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro do Nº. Ciclos da Curva.',QtGui.QMessageBox.Ok)
            return False

        try:                                     #Definindo Defasagem senoidal
            if Tipo_Curva == 0:
                phase = float(self.ui.Defasagem_Senoidal.text())
            if Tipo_Curva == 1:
                phase = float(self.ui.Defasagem_Senoidal_Amortecida.text())
            if Tipo_Curva == 6:
                phase = 0
            if Tipo_Curva == 2:                                         #ACRESCENTADO#
                phase = 0                                               
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro da Defasagem da Curva.',QtGui.QMessageBox.Ok)
            return False

        try:                                     #Definindo Posição Final
            if Tipo_Curva == 0:
                P_Final = abs(float(self.ui.Posicao_Final_Senoidal.text()))
            if Tipo_Curva == 1:
                P_Final = abs(float(self.ui.Posicao_Final_Senoidal_Amortecida.text()))
            if Tipo_Curva == 2:
                P_Final = 0                                             #ACRESCENTADO# 
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro da Posição Final da Curva.',QtGui.QMessageBox.Ok)
            return False

        try:                                     #Definindo constante de amortecimento TAU
            if Tipo_Curva ==0: TAU=0
            if Tipo_Curva == 1:
                TAU = float(self.ui.Amortecimento_Senoidal.text())
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro do Amortecimento da Curva.',QtGui.QMessageBox.Ok)
            return False

        if Tipo_Curva == 0 or Tipo_Curva == 1: 
            self.offset = self.Valor_Equacao(0,float(self.offset),f_saida)
            Amp = self.Valor_Equacao(0,float(Amp),f_saida)
            Phi = numpy.radians(phase)

        if lib.controle_fonte == 0:         #ACRESCENTADO# Seleciona a PUC
            if (lib.Modelo_PUC == 0):
                Amp = Amp/2
                ciclos = int((const.Pontos_Puc/const.Clock_Puc)*freq )
                w = (2*numpy.pi*freq)/const.Clock_Puc
                pontos = list(map(lambda x: Amp*numpy.sin((w*x))+self.offset,range(const.Pontos_Puc)))  # gera a lista de pontos (EQUAÇÃO)
                lib.Ciclos_Puc = int((ciclos * const.Clock_Puc)/freq)
                curva = lib.PUC.ConverteCurva(pontos)   # converte para complemento de 2 com 4 bytes
                checksum = lib.PUC.CalculateGeneratedCsum(curva)     # calcula o checksum da curva gerada
                return curva, checksum, pontos, ciclos, freq
            else:
            ############# Curvas - Equacoes #############
                if P_Final != 0 or phase != 0:
                    x_ciclos = total_ciclo + 1
                else:
                    x_ciclos = total_ciclo
                    
                i = 0
                while i==0:
                    lib.Divisor_Puc = int((60e3)/((const.Pontos_Puc*freq)/(x_ciclos)))  #Cálculo do divisor
                    
                    
                    if Tipo_Curva == 0:  ## Equacao Ciclagem senoidal com defasagem
                        Amp = Amp/2
                        freq_puc = 60e3/(lib.Divisor_Puc+1)
                        w = (2*numpy.pi*freq/freq_puc)
                        f = lambda y: Amp*numpy.sin((w*y)+Phi)+self.offset     ## Funcao
                        pontos = [max(min(p, 10.0),-10.0) for p in ([f(y) for y in range(const.Pontos_Puc)])]
                        ciclos_total = (const.Pontos_Puc/(freq_puc/freq))
                        lib.Ciclos_Puc = int((const.Pontos_Puc/ciclos_total)*total_ciclo)+1
                            
                        
                    if Tipo_Curva == 1: ## Equacao Ciclagem senoidal com defasagem e amortecimento
                        Amp = Amp/2
                        freq_puc = 60e3/(lib.Divisor_Puc+1)
                        w = (2*numpy.pi*freq)
                        f = lambda y: (Amp*numpy.sin((w*(y/freq_puc))+Phi)*(numpy.exp(-((y/freq_puc)/(TAU)))))+self.offset
                        pontos = [max(min(p, 10.0),-10.0) for p in ([f(y) for y in range(const.Pontos_Puc)])]
                        ciclos_total = (const.Pontos_Puc/(freq_puc/freq))
                        lib.Ciclos_Puc = int((const.Pontos_Puc/ciclos_total)*total_ciclo)+1


                    if Tipo_Curva == 2: ## Equação Ciclagem triangular suavizada        #ACRESCENTADO#
                        lib.Divisor_Puc = int((60e3)/((const.Pontos_Puc*freq)/(15)))  #Cálculo do divisor
                        freq_puc = 60e3/(lib.Divisor_Puc+1)
                        self.celulas = numpy.array([])
                        self.colunas = numpy.array([])
                        self.indice = numpy.arange(0,7)
                        for i in range (7):
                            for j in range (1,3):
                                self.cell = self.ui.tabela_config.setCurrentCell(i,j)
                                self.celltext = self.ui.tabela_config.currentItem().text()
                                self.celulas = numpy.append(self.celulas,self.celltext)
                            self.createarray = numpy.asarray(self.celulas, dtype='float')
                        reshape = self.createarray.reshape((7,2))
                        self.DataTable = pd.DataFrame(reshape, index =self.indice,columns=['Tn[ms]','In[A]'])
                                    
                        # Cálculo do Delta I e Delta T
                        self.timeTn = self.DataTable.iloc[:,0]
                        self.currIn = self.DataTable.iloc[:,1]
                        deltaT = numpy.array([])
                        deltaI = numpy.array([])
                        for i in range (6):
                            DeltaT = self.timeTn[i+1]- self.timeTn[i]
                            deltaT = numpy.append(deltaT,DeltaT)
                            DeltaI = self.currIn[i+1]- self.currIn[i]
                            deltaI = numpy.append(deltaI,DeltaI)

                        # Cálculo dos coeficientes a0 até a3
                        # a0:
                        self.a0 = self.currIn[:6]
                        # a1:
                        self.a1 = pd.Series([0,deltaI[1]/deltaT[1],deltaI[1]/deltaT[1],0,deltaI[4]/deltaT[4],deltaI[4]/deltaT[4]], index=numpy.arange(0,6))
                        # a2:
                        self.a2 = pd.Series([(3*deltaI[0]/deltaT[0]-self.a1[1])/deltaT[0],0,(3*deltaI[2]-2*self.a1[2]*deltaT[2])/deltaT[2]**2,3/deltaT[3]*(deltaI[3]/deltaT[3]-self.a1[4]/3),0,(3*deltaI[5]-2*self.a1[5]*deltaT[5])/deltaT[5]**2], index=numpy.arange(0,6))
                        # a3:
                        self.a3 = pd.Series([(self.a1[1]-2*self.a2[0]*deltaT[0])/(3*deltaT[0]**2),0,-(self.a1[2]+2*self.a2[2]*deltaT[2])/(3*deltaT[2]**2),(self.a1[4]-2*self.a2[3]*deltaT[3])/(3*deltaT[3]**2),0,-(self.a1[5]+2*self.a2[5]*deltaT[5])/(3*deltaT[5]**2)],index=numpy.arange(0,6))
                        #t0
                        self.t0 = self.timeTn

                        # Parâmetros
                        N_pontos = 2048
                        dt_ms = self.timeTn[6]/N_pontos

                        # Início da equação I(t)
                        equation = numpy.array([])
                        x = 0
                        temp_ms = numpy.array([])
                        temp_ms =0
                        n_vezes = numpy.array([])
                        n_vezes = 0
                        for n in range (int(const.Pontos_Puc/(freq_puc/freq))):
                            equation = numpy.array([])                
                            for i in range (N_pontos):
                                x = x + dt_ms
                                temp_ms = numpy.append(temp_ms, x)     # Fórmula do tempo t(ms)                 
                                if temp_ms[i] < 20:       # Região 1
                                    a0 = self.a0[0]
                                    a1 = self.a1[0]
                                    a2 = self.a2[0]
                                    a3 = self.a3[0]
                                    t0 = self.t0[0]
                                    self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                    equation = numpy.append(equation, self.f_t)
                    
                                if 20 < temp_ms[i] < 300:   # Região 2
                                    a0 = self.a0[1]
                                    a1 = self.a1[1]
                                    a2 = self.a2[1]
                                    a3 = self.a3[1]
                                    t0 = self.t0[1]
                                    self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                    equation = numpy.append(equation, self.f_t)

                                if 300 < temp_ms[i] < 320:  # Região 3
                                    a0 = self.a0[2]
                                    a1 = self.a1[2]
                                    a2 = self.a2[2]
                                    a3 = self.a3[2]
                                    t0 = self.t0[2]
                                    self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                    equation = numpy.append(equation, self.f_t)

                                if 320 < temp_ms[i] < 340:  # Região 4
                                    a0 = self.a0[3]
                                    a1 = self.a1[3]
                                    a2 = self.a2[3]
                                    a3 = self.a3[3]
                                    t0 = self.t0[3]
                                    self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                    equation = numpy.append(equation, self.f_t)

                                if 340 < temp_ms[i] < 480:  # Região 5
                                    a0 = self.a0[4]
                                    a1 = self.a1[4]
                                    a2 = self.a2[4]
                                    a3 = self.a3[4]
                                    t0 = self.t0[4]
                                    self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                    equation = numpy.append(equation, self.f_t)

                                if 480 < temp_ms[i] < 500:  # Região 6
                                    a0 = self.a0[5]
                                    a1 = self.a1[5]
                                    a2 = self.a2[5]
                                    a3 = self.a3[5]
                                    t0 = self.t0[5]
                                    self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                    equation = numpy.append(equation, self.f_t)
                            n_vezes = numpy.append(n_vezes,equation)
                            
                        
                        lista_pts = n_vezes.tolist()                # A lista de pontos de corrente para serem enviados à PUC
                        lista2 = lista_pts[1:]
                        pontos = [max(min(p, 10.0),-10.0) for p in ([lista2[y]/float(self.ui.Fator_Saida.text()) for y in range(total_ciclo*N_pontos)])]
                        remaining = const.Pontos_Puc - len(pontos)
                        if remaining > 0:                           # Completa com zeros o checksum se os pontos forem menores que 32768
                            fim = pontos[0]
                            pontos = pontos + [fim]*remaining
                        ciclos_total = (const.Pontos_Puc/(freq_puc/freq)) # Tenho os 32768 pontos divididos pela frequência da PUC e pela frequência desejada (2Hz).
                        lib.Ciclos_Puc = int((const.Pontos_Puc/ciclos_total)*total_ciclo)+1
                         
                    
    ##                if Tipo_Curva == 6: ## Curva de ciclagem arbitraria do arquivo
    ##                    pontos = []
    ##                    for j in range(total_ciclo):
    ##                        for k in range(len(dados)):
    ##                            pontos.append(dados[k])
    ##                    pontos = numpy.asarray(pontos)
    ##
    ##                    for j in range(len(pontos)): 
    ##                        pontos[j] = pontos[j] * Amp   #converte array para corrente
    ##                        pontos[j] = self.Valor_Equacao(0,float(pontos[j]),f_saida)    #converte array para valores reais puc
    ##                    lib.Ciclos_Puc = (len(pontos))
    ##                    
    ##                    if (lib.Ciclos_Puc) < (const.Pontos_Puc):
    ##                        pontos = pontos.tolist()
    ##                        for j in range((const.Pontos_Puc)-(lib.Ciclos_Puc)):
    ##                            pontos.append(0)
    ##                    pontos = numpy.asarray(pontos)
                                            
        
                    if Tipo_Curva == 0 or Tipo_Curva == 1 or Tipo_Curva == 2:       #ACRESCENTADO Tipo_Curva == 2#
                        if (P_Final != 0 or phase != 0) and (P_Final != phase):
                            if P_Final > phase:
                                ponto_final = P_Final - phase
                            else:
                                ponto_final = 360 - (phase - P_Final)                            
                            ponto_final = int(((lib.Ciclos_Puc/total_ciclo)/360)*ponto_final)+1
                            lib.Ciclos_Puc = lib.Ciclos_Puc + ponto_final

                    if lib.Ciclos_Puc>const.Pontos_Puc:
                        x_ciclos+=1
                    else:
                        i=1
                        
            ###################################################
                    
            ######## Teste ponto de partida curva ciclagem ########
                    if Tipo_Curva == 0 or Tipo_Curva == 1:# or Tipo_Curva == 2:       #ACRESCENTADO Tipo_Curva == 2#
                        ponto_inicial = int((const.Pontos_Puc/total_ciclo)/8)
                    if Tipo_Curva ==2:
                        ponto_inicial = int((ciclos_total)/8)
                        lib.Ponto_Inicial_Curva = pontos[ponto_inicial]
        ##                    if self.offset>=0:
        ##                        lib.Ponto_Inicial_Curva = (Amp/2)-self.offset
        ##                    else:
        ##                        lib.Ponto_Inicial_Curva = (Amp/2)+self.offset
        ##                    for i in range (len(pontos)):
        ##                        if pontos[i]<(lib.Ponto_Inicial_Curva):
        ##                            pontos[i]=(lib.Ponto_Inicial_Curva)
        ##                        else:
        ##                            break
             #######################################################
                        
                checksum = lib.PUC.CreateChecksum(pontos)
                
                if checksum == False:
                    QtGui.QMessageBox.warning(self,'Atenção.','Falha nos Pontos.',QtGui.QMessageBox.Ok)
                    return False
                return pontos, checksum, lib.Ciclos_Puc, freq

        else:                           #ACRESCENTADO# seleciona a fonte digital
            try:
                if Tipo_Curva == 0:     # Ciclagem senoidal com defasagem
                
                    try:
                        sigType=0
                        mode=3
                        lib.Digital.OpMode(mode)
                        if (lib.Digital.Read_ps_OpMode() != 3):
                            QtGui.QMessageBox.warning(self,'Atenção','Gerador de sinais da fonte não configurado corretamente. Verifique configuração.',QtGui.QMessageBox.Ok)
                            return False
                    except:
                        QtGui.QMessageBox.warning(self,'Atenção','Verifique configuração da fonte.',QtGui.QMessageBox.Ok)
                        return
                            
                    try:
                        lib.Digital.Write_sigGen_Freq(float(freq))             #Enviando Frequencia
                        lib.Digital.Write_sigGen_Amplitude(float(Amp))         #Enviando Amplitude
                        lib.Digital.Write_sigGen_Offset(float(self.offset))    #Enviando Offset 
                    except:
                        QtGui.QMessageBox.warning(self,'Atenção.','Verifique valores de configuração da fonte.',QtGui.QMessageBox.Ok)
                        return

                    #Enviando o sigGenAmortecido
                    lib.Digital.ConfigSigGen(sigType, total_ciclo, phase, P_Final)

                if Tipo_Curva == 1:  ## Ciclagem senoidal amortecida com defasagem e amortecimento
                    
                    try:
                        sigType=4
                        mode=3
                        lib.Digital.OpMode(mode)
                        if (lib.Digital.Read_ps_OpMode() != 3):
                            QtGui.QMessageBox.warning(self,'Atenção','Gerador de sinais da fonte não configurado corretamente. Verifique configuração.',QtGui.QMessageBox.Ok)
                            return False
                    except:
                        QtGui.QMessageBox.warning(self,'Atenção','Verifique configuração da fonte.',QtGui.QMessageBox.Ok)
                        return
                    
                    try:
                        lib.Digital.Write_sigGen_Freq(float(freq))             #Enviando Frequencia
                        lib.Digital.Write_sigGen_Amplitude(float(Amp))         #Enviando Amplitude
                        lib.Digital.Write_sigGen_Offset(float(self.offset))    #Enviando Offset
                    except:
                        QtGui.QMessageBox.warning(self,'Atenção.','Verifique valores de configuração enviados para fonte.',QtGui.QMessageBox.Ok)
                        return

                    #Enviando o sigGenAmortecido
                    try:
                        lib.Digital.Write_sigGen_Aux(float(self.ui.Amortecimento_Senoidal.text()))
                        lib.Digital.ConfigSigGen(sigType, total_ciclo, phase, P_Final)
                    except:
                        QtGui.QMessageBox.warning(self,'Atenção.','Falha na curva senoidal amortecida.',QtGui.QMessageBox.Ok)
                        return False

                if Tipo_Curva == 2:  ## Triangular suavizada
                    self.celulas = numpy.array([])
                    self.colunas = numpy.array([])
                    self.indice = numpy.arange(0,7)
                    for i in range (7):
                        for j in range (1,3):
                            self.cell = self.ui.tabela_config.setCurrentCell(i,j)
                            self.celltext = self.ui.tabela_config.currentItem().text()
                            self.celulas = numpy.append(self.celulas,self.celltext)
                        self.createarray = numpy.asarray(self.celulas, dtype='float')
                    reshape = self.createarray.reshape((7,2))
                    self.DataTable = pd.DataFrame(reshape, index =self.indice,columns=['Tn[ms]','In[A]'])
                                
                    # Cálculo do Delta I e Delta T
                    self.timeTn = self.DataTable.iloc[:,0]
                    self.currIn = self.DataTable.iloc[:,1]
                    deltaT = numpy.array([])
                    deltaI = numpy.array([])
                    for i in range (6):
                        DeltaT = self.timeTn[i+1]- self.timeTn[i]
                        deltaT = numpy.append(deltaT,DeltaT)
                        DeltaI = self.currIn[i+1]- self.currIn[i]
                        deltaI = numpy.append(deltaI,DeltaI)

                    # Cálculo dos coeficientes a0 até a3
                    # a0:
                    self.a0 = self.currIn[:6]
                    # a1:
                    self.a1 = pd.Series([0,deltaI[1]/deltaT[1],deltaI[1]/deltaT[1],0,deltaI[4]/deltaT[4],deltaI[4]/deltaT[4]], index=numpy.arange(0,6))
                    # a2:
                    self.a2 = pd.Series([(3*deltaI[0]/deltaT[0]-self.a1[1])/deltaT[0],0,(3*deltaI[2]-2*self.a1[2]*deltaT[2])/deltaT[2]**2,3/deltaT[3]*(deltaI[3]/deltaT[3]-self.a1[4]/3),0,(3*deltaI[5]-2*self.a1[5]*deltaT[5])/deltaT[5]**2], index=numpy.arange(0,6))
                    # a3:
                    self.a3 = pd.Series([(self.a1[1]-2*self.a2[0]*deltaT[0])/(3*deltaT[0]**2),0,-(self.a1[2]+2*self.a2[2]*deltaT[2])/(3*deltaT[2]**2),(self.a1[4]-2*self.a2[3]*deltaT[3])/(3*deltaT[3]**2),0,-(self.a1[5]+2*self.a2[5]*deltaT[5])/(3*deltaT[5]**2)],index=numpy.arange(0,6))
                    #t0
                    self.t0 = self.timeTn

                    # Parâmetros
                    N_pontos = 2048
                    dt_ms = self.timeTn[6]/N_pontos

                    # Início da equação I(t)
                    equation = numpy.array([])
                    x = 0
                    temp_ms = numpy.array([])
                    temp_ms =0
                    n_vezes = numpy.array([])
                    n_vezes = 0
                    for n in range (int(total_ciclo)):
                        equation = numpy.array([])                
                        for i in range (N_pontos):
                            x = x + dt_ms
                            temp_ms = numpy.append(temp_ms, x)     # Fórmula do tempo t(ms)                 
                            if temp_ms[i] < self.timeTn[1]:       # Região 1
                                a0 = self.a0[0]
                                a1 = self.a1[0]
                                a2 = self.a2[0]
                                a3 = self.a3[0]
                                t0 = self.t0[0]
                                self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                equation = numpy.append(equation, self.f_t)
                
                            if self.timeTn[1] < temp_ms[i] < self.timeTn[2]:   # Região 2
                                a0 = self.a0[1]
                                a1 = self.a1[1]
                                a2 = self.a2[1]
                                a3 = self.a3[1]
                                t0 = self.t0[1]
                                self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                equation = numpy.append(equation, self.f_t)

                            if self.timeTn[2] < temp_ms[i] < self.timeTn[3]:  # Região 3
                                a0 = self.a0[2]
                                a1 = self.a1[2]
                                a2 = self.a2[2]
                                a3 = self.a3[2]
                                t0 = self.t0[2]
                                self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                equation = numpy.append(equation, self.f_t)

                            if self.timeTn[3] < temp_ms[i] < self.timeTn[4]:  # Região 4
                                a0 = self.a0[3]
                                a1 = self.a1[3]
                                a2 = self.a2[3]
                                a3 = self.a3[3]
                                t0 = self.t0[3]
                                self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                equation = numpy.append(equation, self.f_t)

                            if self.timeTn[4] < temp_ms[i] < self.timeTn[5]:  # Região 5
                                a0 = self.a0[4]
                                a1 = self.a1[4]
                                a2 = self.a2[4]
                                a3 = self.a3[4]
                                t0 = self.t0[4]
                                self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                equation = numpy.append(equation, self.f_t)

                            if self.timeTn[5] < temp_ms[i] < self.timeTn[6]:  # Região 6
                                a0 = self.a0[5]
                                a1 = self.a1[5]
                                a2 = self.a2[5]
                                a3 = self.a3[5]
                                t0 = self.t0[5]
                                self.f_t = a0+a1*(temp_ms[i]-t0)+a2*(temp_ms[i]-t0)**2+a3*(temp_ms[i]-t0)**3
                                equation = numpy.append(equation, self.f_t)
                        n_vezes = numpy.append(n_vezes,equation)
                          
                    lista_pts = n_vezes.tolist()                # A lista de pontos de corrente para serem enviados à PUC
                    lista2 = lista_pts[1:]
                    pontos = [max(min(p, 10.0),-10.0) for p in ([lista2[y]/float(self.ui.Fator_Saida.text()) for y in range(total_ciclo*N_pontos)])]
                    print(pontos[:10], 'Gerar')
##                    remaining = 32768 - len(pontos)
##                    if remaining > 0:                           # Completa com zeros o checksum se os pontos forem menores que 32768
##                        fim = pontos[0]
##                        pontos = pontos + [fim]*remaining

                    self.Digital.Send_wfmRef_Curve(0, pontos)   #Número do bloco e pontos da curva
                    self.Digital.ConfigWfmRef(0,0)              #Ganho =1 e Offset = 0

                return True
            except:
                return False
            

    def Curva_Quadrupolo(self):
        pontos=[]
##        if self.ui.Corrente_Arbitraria_PUC.isEnabled():
        try:
            f_saida = float(self.ui.Fator_Saida.text())
            Corrente_Maxima = float(self.ui.Corrente_Maxima_Fonte.text())
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verifique Valor do Parâmetro de Fator de Saída na Configuração.',QtGui.QMessageBox.Ok)
            return False
        try:
            dados_corrente = self.Converter_Corrente_Arbitraria(self.ui.Corrente_Arbitraria_PUC.toPlainText(),0) ###
            for i in range(len(dados_corrente)):
                dados_corrente[i]=self.Verificar_Limite_Corrente(1,dados_corrente[i])                
                if (dados_corrente[i] == 'False'):
                    return
            self.ui.Corrente_Arbitraria_PUC.setPlainText(self.Recuperar_Valor(0,str(dados_corrente)))
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Verificar Valores de Corrente Automático.\nTente Novamente.',QtGui.QMessageBox.Ok)
            return

        for i in range(len(dados_corrente)):
            dados_corrente[i] = dados_corrente[i]/f_saida

        for i in range(len(dados_corrente)):
            dados_corrente[i]=self.Valor_Equacao(2,(dados_corrente[i]),f_saida)
        
        for i in range(len(dados_corrente)):
            dados_corrente[i] = dados_corrente[i]/10

### Preparacao dos dados
        for j in range(int((len(dados_corrente))/2)):
            pontos.append(0)
        for j in range(int(str(self.ui.Ciclos_Curva_Quadrupolo.text()))):
            for k in range(len(dados_corrente)):
##                pontos.append(round((dados_corrente[k]/Corrente_Maxima),6))
                pontos.append(round((dados_corrente[k]),6))
        for j in range(int((len(dados_corrente))/2)):
            pontos.append(0)
            
        tempo_ciclagem = .5 * (int(str(self.ui.Ciclos_Curva_Quadrupolo.text()))+1)
        resp=lib.GPIB.Config_Gerador_Ciclagem_Quadrupolo(1/tempo_ciclagem,pontos)
        
        if resp==True:
            time.sleep(tempo_ciclagem + (int(str(self.ui.Ciclos_Curva_Quadrupolo.text())))/24)
            lib.GPIB.Saida_Gerador(0)
            QtGui.QMessageBox.information(self,'Aviso.','Ciclagem Concluida com sucesso.',QtGui.QMessageBox.Ok)
        else:
            lib.GPIB.Saida_Gerador(0)
            QtGui.QMessageBox.information(self,'Aviso.','Falha na Ciclagem.',QtGui.QMessageBox.Ok)            

        
    def Ciclagem(self,index=0):
        resp = self.Verificar_Dados_Curva(1)
        if resp == False:
            self.ui.Ciclar.setEnabled(False)
            QtGui.QMessageBox.warning(self,'Atenção.','Dados Diferentes. Reenviar Curva de Ciclagem.',QtGui.QMessageBox.Ok)
            return
        Tipo_Curva = int(self.ui.tabWidget_3.currentIndex())
        if lib.controle_fonte == 0:                 #ACRESCENTADO# Seleciona a PUC
            try:
    ##            atual = round(lib.PUC.ReadDA(),3)
                atual = round(lib.PUC.ReadAD(),3)
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','A controladora da fonte não está respondendo.',QtGui.QMessageBox.Ok)
                return
            try:
                f_saida = float(self.ui.Fator_Saida.text())
                passo = (float(self.ui.Amplitude_Linear.text()))/f_saida
                tempo = float(self.ui.Tempo_Linear.text())
                freq = float(self.ui.Frequencia_Senoidal.text())
                ciclo_final = int(self.ui.N_Ciclos_Senoidal.text())

                if Tipo_Curva == 0:
                    final = self.Valor_Equacao(0,float(self.ui.Offset_Senoidal.text()),f_saida)
                if Tipo_Curva == 1:
                    final = lib.Ponto_Inicial_Curva
                if Tipo_Curva == 2:                 #ACRESCENTADO#
                    final = lib.Ponto_Inicial_Curva
                if Tipo_Curva == 6:
                    final = 0       
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Dados Incorretos.',QtGui.QMessageBox.Ok)
                return
            
            self.ui.tabWidget_2.setEnabled(False)
            self.ui.coletar.setEnabled(False)
            self.ui.Carregar_Config_Fonte.setEnabled(False)
            self.ui.Corrente_Atual.setEnabled(False)
            QtGui.QApplication.processEvents()
            
            ### Cálculo Ciclos ### 
            ciclos = int((const.Pontos_Puc/const.Clock_Puc)*freq)
            rep_int = int(ciclo_final/ciclos)
            rep_float = (ciclo_final/ciclos)-int(ciclo_final/ciclos)
            delay = int("%.0f"%(ciclos*(1/freq)))                           ### "%.0f"% () ## aproximacao casa decimal (0,1,2..)casas
            n_ciclos = int(ciclos * rep_float)
            ponto_final = (int((lib.Ciclos_Puc/ciclos)*n_ciclos)+((lib.Ciclos_Puc*3)/(ciclos*4)-(75)))
            ####################
            
            lib.Fonte_Pronta = 0
            proc_ciclagem = Ciclagem_Fonte(final,atual,passo,tempo,rep_int,delay,n_ciclos,ponto_final,freq,index)
            proc_ciclagem.run()

        else:                           #ACRESCENTADO# Seleciona a Digital
            try:
                if Tipo_Curva == 0:
                    lib.Digital.EnableSigGen()
                if Tipo_Curva == 1:
                    lib.Digital.EnableSigGen()
                    time.sleep(.2)
                    while (abs(float(lib.Digital.Read_iLoad1())) > 5e-04):
                        self.ui.tabWidget_2.setEnabled(False) 
                        self.ui.coletar.setEnabled(False)
                        self.ui.Carregar_Config_Fonte.setEnabled(False)
                        self.ui.Corrente_Atual.setEnabled(False)
                        QtGui.QApplication.processEvents()
                   
                    QtGui.QMessageBox.information(self,'Ciclagem.','Processo de Ciclagem Concluído com Sucesso.',QtGui.QMessageBox.Ok)
                    lib.Digital.DisableSigGen()
                    self.ui.tabWidget_2.setEnabled(True)
                    self.ui.coletar.setEnabled(True)
                    self.ui.Carregar_Config_Fonte.setEnabled(True)
                    self.ui.Corrente_Atual.setEnabled(True)
                    QtGui.QApplication.processEvents()

                if Tipo_Curva == 2:
                    self.Digital.WfmRefUpdate()
                    
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Saída do gerador de sinais não ligada.',QtGui.QMessageBox.Ok)
                return
        
    def Calibrar_Fonte(self):
        Pontos_Desejados = 6
        ret = QtGui.QMessageBox.question(self,'Calibração da Fonte.','Deseja Iniciar o Processo de Calibração da Fonte?\nProcesso pode levar alguns minutos.',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        if self.ui.label_multimetro.text()!='Conectado':
            QtGui.QMessageBox.warning(self,'Atenção.','Conectar Multimetro GPIB.\nTente Novamente.',QtGui.QMessageBox.Ok)
            return
        
        QtGui.QApplication.processEvents()

        try:
            f_saida = float(self.ui.Fator_Saida.text())
            Fator_Corrente_DCCT = float(self.ui.Corrente_DCCT.text())/10
            Corrente_Inicial = self.Verificar_Limite_Corrente(0,float(self.ui.Corr_Calib_Inicial.text()))
            if (Corrente_Inicial == 'False'):
                return
            self.ui.Corr_Calib_Inicial.setText(str(Corrente_Inicial))
            Corrente_Inicial = Corrente_Inicial/f_saida
            Corrente_Final = self.Verificar_Limite_Corrente(0,float(self.ui.Corr_Calib_Final.text()))
            if (Corrente_Final == 'False'):
                return
            self.ui.Corr_Calib_Final.setText(str(Corrente_Final))
            Corrente_Final = Corrente_Final/f_saida
            N_Pontos = int(float(self.ui.Corr_Calib_Passo.text()))
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Dados Incorretos.',QtGui.QMessageBox.Ok)
            return
        
        if Corrente_Final < Corrente_Inicial:
            QtGui.QMessageBox.warning(self,'Atenção.','Corrente Final Deve ser Maior que Corrente Inicial.',QtGui.QMessageBox.Ok)
            return
        if N_Pontos <= 1:
            QtGui.QMessageBox.warning(self,'Atenção.','Número de Pontos deve ser Maior que 1.',QtGui.QMessageBox.Ok)
            return
        if N_Pontos >= Pontos_Desejados:
            Pontos_Reta = Pontos_Desejados
        else:
            Pontos_Reta = N_Pontos

        if lib.controle_fonte == 0:             #ACRESCENTADO# Se estiver selecionado para a PUC
            lib.Fonte_Calibrada = [0,0]
            self.ui.groupBox_5.setEnabled(False)
            QtGui.QApplication.processEvents()
            
            self.Rampa(0,lib.PUC.ReadAD(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text()))) ## Zerar corrente fonte
            Correntes_Calibracao = numpy.arange(Corrente_Inicial,Corrente_Final,(Corrente_Final-Corrente_Inicial)/N_Pontos).tolist()
            if Correntes_Calibracao[len(Correntes_Calibracao)-1] < Corrente_Final:
                Correntes_Calibracao.append(Corrente_Final)
            Correntes_Calibracao = numpy.asarray(Correntes_Calibracao)
            Repeticao = 3       ## Valor de repeticao da rotina de calibracao
            V_DA = numpy.zeros(len(Correntes_Calibracao)*Repeticao).reshape(len(Correntes_Calibracao),Repeticao)
            V_AD = numpy.zeros(len(Correntes_Calibracao)*Repeticao).reshape(len(Correntes_Calibracao),Repeticao)
            V_DCCT = numpy.zeros(len(Correntes_Calibracao)*Repeticao).reshape(len(Correntes_Calibracao),Repeticao)
            for j in range(Repeticao):
                for i in range(len(Correntes_Calibracao)):
                    self.Rampa(Correntes_Calibracao[i],lib.PUC.ReadAD(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text())))
                    time.sleep(2)
                    V_DA[i][j] = lib.PUC.ReadDA()                         ## ler referencia tensao da corrente enviada
                    V_DCCT[i][j] = lib.GPIB.Coleta_Multimetro()           ## ler referencia tensao da corrente DCCT
                time.sleep(2)
            self.Rampa(0,lib.PUC.ReadAD(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text()))) ## Zerar corrente fonte
            M_V_DA=numpy.mean(V_DA,axis=1)
            M_V_DCCT=numpy.mean(V_DCCT,axis=1)
            fator_correcao = ((M_V_DA)*((Correntes_Calibracao*f_saida)/Fator_Corrente_DCCT))/(M_V_DCCT)
            lib.reta_escrita = numpy.polyfit((Correntes_Calibracao*f_saida),fator_correcao,Pontos_Reta)
            lib.reta_escrita = lib.reta_escrita.tolist()
            lib.reta_escrita.reverse()
            lib.reta_escrita = numpy.asarray(lib.reta_escrita)
            lib.Fonte_Calibrada = [0,1]
             
            for j in range(Repeticao):
                for i in range(len(Correntes_Calibracao)):
                    self.Rampa(self.Valor_Equacao(0,Correntes_Calibracao[i]*f_saida,f_saida),lib.PUC.ReadAD(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text())))
                    time.sleep(2)
                    V_AD[i][j] = lib.PUC.ReadAD()                         ## ler referencia tensao da corrente da fonte
                    V_DCCT[i][j] = lib.GPIB.Coleta_Multimetro()           ## ler referencia tensao da corrente DCCT
                time.sleep(2)
            self.Rampa(0,lib.PUC.ReadAD(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text()))) ## Zerar corrente fonte
            M_V_AD=numpy.mean(V_AD,axis=1)
            M_V_DCCT=numpy.mean(V_DCCT,axis=1)

            lib.reta_leitura = numpy.polyfit(M_V_AD,(M_V_DCCT * Fator_Corrente_DCCT),Pontos_Reta)
            lib.reta_leitura = lib.reta_leitura.tolist()
            lib.reta_leitura.reverse()
            lib.reta_leitura = numpy.asarray(lib.reta_leitura)
            
            QtGui.QMessageBox.information(lib.Janela,'Aviso.','Processo de Calibração Concluído com Sucesso.',QtGui.QMessageBox.Ok)
            self.ui.groupBox_5.setEnabled(True)
            lib.Fonte_Calibrada = [1,1]
            QtGui.QApplication.processEvents()

        else:                                   #ACRESCENTADA# Se estiver selecionada para a fonte Digital
            lib.Fonte_Calibrada = [0,0]
            self.ui.groupBox_5.setEnabled(False)
            QtGui.QApplication.processEvents()
            
            self.Rampa(0,lib.Digital.Read_iLoad1(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text()))) ## Zerar corrente fonte
            Correntes_Calibracao = numpy.arange(Corrente_Inicial,Corrente_Final,(Corrente_Final-Corrente_Inicial)/N_Pontos).tolist()
            if Correntes_Calibracao[len(Correntes_Calibracao)-1] < Corrente_Final:
                Correntes_Calibracao.append(Corrente_Final)
            Correntes_Calibracao = numpy.asarray(Correntes_Calibracao)
            Repeticao = 3       ## Valor de repeticao da rotina de calibracao
            V_DA = numpy.zeros(len(Correntes_Calibracao)*Repeticao).reshape(len(Correntes_Calibracao),Repeticao)
            V_AD = numpy.zeros(len(Correntes_Calibracao)*Repeticao).reshape(len(Correntes_Calibracao),Repeticao)
            V_DCCT = numpy.zeros(len(Correntes_Calibracao)*Repeticao).reshape(len(Correntes_Calibracao),Repeticao)
            for j in range(Repeticao):
                for i in range(len(Correntes_Calibracao)):
                    self.Rampa(Correntes_Calibracao[i],lib.Digital.Read_iRef(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text())))
                    time.sleep(2)
                    V_DA[i][j] = lib.Digital.Read_iRef()                  ## ler referencia tensao da corrente enviada (Testar comando Read_iLoad2()
                    V_DCCT[i][j] = lib.GPIB.Coleta_Multimetro()           ## ler referencia tensao da corrente DCCT
                time.sleep(2)
            self.Rampa(0,lib.Digital.Read_iLoad1(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text()))) ## Zerar corrente fonte
            M_V_DA=numpy.mean(V_DA,axis=1)
            M_V_DCCT=numpy.mean(V_DCCT,axis=1)
            fator_correcao = ((M_V_DA)*((Correntes_Calibracao*f_saida)/Fator_Corrente_DCCT))/(M_V_DCCT)
            lib.reta_escrita = numpy.polyfit((Correntes_Calibracao*f_saida),fator_correcao,Pontos_Reta)
            lib.reta_escrita = lib.reta_escrita.tolist()
            lib.reta_escrita.reverse()
            lib.reta_escrita = numpy.asarray(lib.reta_escrita)
            lib.Fonte_Calibrada = [0,1]
             
            for j in range(Repeticao):
                for i in range(len(Correntes_Calibracao)):
                    self.Rampa(self.Valor_Equacao(0,Correntes_Calibracao[i]*f_saida,f_saida),lib.Digital.Read_iLoad1(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text())))
                    time.sleep(2)
                    V_AD[i][j] = lib.Digital.Read_iLoad1()                ## ler referencia tensao da corrente da fonte
                    V_DCCT[i][j] = lib.GPIB.Coleta_Multimetro()           ## ler referencia tensao da corrente DCCT
                time.sleep(2)
            self.Rampa(0,lib.Digital.Read_iLoad1(),((float(self.ui.Amplitude_Linear.text()))/f_saida),(float(self.ui.Tempo_Linear.text()))) ## Zerar corrente fonte
            M_V_AD=numpy.mean(V_AD,axis=1)
            M_V_DCCT=numpy.mean(V_DCCT,axis=1)

            lib.reta_leitura = numpy.polyfit(M_V_AD,(M_V_DCCT * Fator_Corrente_DCCT),Pontos_Reta)
            lib.reta_leitura = lib.reta_leitura.tolist()
            lib.reta_leitura.reverse()
            lib.reta_leitura = numpy.asarray(lib.reta_leitura)
            
            QtGui.QMessageBox.information(lib.Janela,'Aviso.','Processo de Calibração Concluído com Sucesso.',QtGui.QMessageBox.Ok)
            self.ui.groupBox_5.setEnabled(True)
            lib.Fonte_Calibrada = [1,1]
            QtGui.QApplication.processEvents()


    def Analise_Frequencia(self):
        lib.Analise_Freq = 1
        dt=20
        ret = QtGui.QMessageBox.question(self,'Analise em Frequência.','Deseja Iniciar o Processo de Analise em Frequência?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
##        if lib.procura_indice_flag == 1:
##            QtGui.QMessageBox.information(lib.Janela,'Aviso.','Referenciar Integrador Primeiro.',QtGui.QMessageBox.Ok) ## Verifica sistema referenciado
##            return
        
        lib.integrador.Enviar('ISC,A,1')    ## Fechar rele de coleta de dados
        lib.integrador.Enviar('IMD,0')      ## Configura Sequencia de descarregamento de dados apos parada.
        lib.integrador.Enviar(lib.integrador.PDITriggerTimer)   ## Configura integrador para trigger interno.
        lib.integrador.Enviar('TRI,,0/*,'+str(dt))   ## Enviar configuracao sequencia infinita com intervalo de 20 pontos
        lib.integrador.Enviar('ISC,A,0')    ## Abrir rele de coleta de dados
        self.Ciclagem(1)
        while lib.Fonte_Ciclagem == 0:
            QtGui.QApplication.processEvents()
        lib.integrador.Enviar(lib.integrador.PDIIniciaColeta)   ## Iniciar coleta de dados
        while lib.Fonte_Ciclagem == 1:
            QtGui.QApplication.processEvents()
        lib.integrador.Enviar(lib.integrador.PDIParaColeta)   ## Para coleta de dados

        valor = ''
        status = -1
        lib.integrador.LimpaTxRx()
        lib.integrador.Enviar('ENQ')
        time.sleep(0.1)
        while (status == -1):
            tmp = lib.integrador.ser.readall()
            tmp = tmp.decode('utf-8')
            valor = valor + tmp
            status = tmp.find('\x1a')
            time.sleep(0.5)

        valor = valor.strip(' A\r\n\x1a')
        pontos_integrador = valor.split(' A\r\n')
        lib.integrador.Enviar('ISC,A,1')
        
##        self.CONFIGURARINTEGRADOR(1)  ## Retorna configuracao do integrador para encoder
        
        for i in range(len(pontos_integrador)):
            try:
                pontos_integrador[i] = (int(pontos_integrador[i])*(10**(-8)))
            except:
                QtGui.QMessageBox.information(lib.Janela,'Aviso.','Falha no recebimento de Dados.\n    Repita o processo.',QtGui.QMessageBox.Ok)
                return
            
        pontos_integrador = numpy.array(pontos_integrador)
        #############################################################################
        resp=[] ## Transforma curva pontos integrador para valor unitario
        resp.append(abs(pontos_integrador.max()));resp.append(abs(pontos_integrador.min()))
        resp=numpy.array(resp)
        valor = resp.max()
        for i in range(len(pontos_integrador)):
            pontos_integrador[i] = pontos_integrador[i]/valor
        #############################################################################
            
        eixo_x = numpy.linspace(0,len(pontos_integrador)*dt,len(pontos_integrador))
        for i in range(len(eixo_x)):
            eixo_x[i] = eixo_x[i]/1000 ## Transformar eixo x de pontos para segundos. Dividido frequencia clock interno integrador
        plt.plot(eixo_x,pontos_integrador)
##        plt.show()
  
        if lib.Modelo_PUC == 0:
            pontos_PUC = lib.PUC.ReadCaptured()
            pontos_PUC = pontos_PUC[:-(len(pontos_PUC)-lib.Ciclos_Puc)]
            pontos_PUC = numpy.array(pontos_PUC)
            for i in range(len(pontos_PUC)):
                pontos_PUC[i] = (self.Valor_Equacao(1,pontos_PUC[i],float(self.ui.Fator_Entrada.text()))) - (self.Valor_Equacao(1,self.offset,float(self.ui.Fator_Entrada.text())))
##                pontos_PUC[i] = self.Valor_Equacao(1,pontos_PUC[i],float(self.ui.Fator_Entrada.text())) ##
                ## Retira o valor do offset da curva da corrente
        #############################################################################
##            valor_medio = (abs(pontos_PUC.max()) + abs(pontos_PUC.min()))/2 ##
##            for i in range(len(pontos_PUC)): ##
##                pontos_PUC[i] = pontos_PUC[i] - valor_medio ##

            resp=[] ## Transforma curva pontos puc para valor unitario
            resp.append(abs(pontos_PUC.max()));resp.append(abs(pontos_PUC.min()))
            resp=numpy.array(resp)
            valor = resp.max()
            for i in range(len(pontos_PUC)):
                pontos_PUC[i] = pontos_PUC[i]/valor
        #############################################################################

            eixo_x = numpy.linspace(0,len(pontos_PUC),len(pontos_PUC))
            for i in range(len(eixo_x)):
                eixo_x[i] = eixo_x[i]/4000 ## Transformar eixo x de pontos para segundos. Dividido frequencia clock interno integrador
            plt.plot(eixo_x,pontos_PUC)
            
        else:
            pontos_PUC = lib.PUC.ReadCaptured(lib.Ciclos_Puc)
            pontos_PUC = numpy.array(pontos_PUC)
            for i in range(len(pontos_PUC)):
                pontos_PUC[i] = (self.Valor_Equacao(1,pontos_PUC[i],float(self.ui.Fator_Entrada.text()))) - (self.Valor_Equacao(1,self.offset,float(self.ui.Fator_Entrada.text())))
                ## Retira o valor do offset da curva da corrente
        #############################################################################
            resp=[] ## Transforma curva pontos puc para valor unitario
            resp.append(abs(pontos_PUC.max()));resp.append(abs(pontos_PUC.min()))
            resp=numpy.array(resp)
            valor = resp.max()
            for i in range(len(pontos_PUC)):
                pontos_PUC[i] = pontos_PUC[i]/valor
        #############################################################################

            eixo_x = numpy.linspace(0,len(pontos_PUC),len(pontos_PUC))
            for i in range(len(eixo_x)):
                eixo_x[i] = eixo_x[i]/(6e4/(lib.Divisor_Puc+1)) ## Transformar eixo x de pontos para segundos. Dividido frequencia clock interno integrador
            plt.plot(eixo_x,pontos_PUC)
            
        index='x'
        f = open('pontos_integrador_'+str(index)+'.txt','w')
        for i in range(len(pontos_integrador)):
            f.write(str(pontos_integrador[i]))
            f.write('\n')
        f.close()
        f = open('pontos_puc_'+str(index)+'.txt','w')
        for i in range(len(pontos_PUC)):
            f.write(str(pontos_PUC[i]))
            f.write('\n')
        f.close()
        
        lib.Analise_Freq = 0
        plt.show()

    
    ########### ABA 5: GPIB ###########

    def Habilitar_GPIB(self):
        if self.ui.ckBox_GPIB_1.isChecked():
            self.ui.label_55.setEnabled(True)
            self.ui.Enderac_Gerador.setEnabled(True)
        else:
            self.ui.label_55.setEnabled(False)
            self.ui.Enderac_Gerador.setEnabled(False)

        if self.ui.ckBox_GPIB_2.isChecked():
            self.ui.label_56.setEnabled(True)
            self.ui.Enderac_Multimetro.setEnabled(True)
        else:
            self.ui.label_56.setEnabled(False)
            self.ui.Enderac_Multimetro.setEnabled(False)

        if self.ui.ckBox_GPIB_3.isChecked():
            self.ui.label_186.setEnabled(True)
            self.ui.Enderac_Multicanal.setEnabled(True)
        else:
            self.ui.label_186.setEnabled(False)
            self.ui.Enderac_Multicanal.setEnabled(False)

    def Conectar_GPIB(self):
        if self.ui.ckBox_GPIB_1.isChecked():
            status = lib.GPIB.Conectar_Gerador(int(self.ui.Enderac_Gerador.text()))
            if status == True:
                self.ui.label_gerador.setText('Conectado')
                self.ui.groupBox_32.setEnabled(True)
                self.ui.Hab_Curva_Quadrupolo.setEnabled(True)
            else:
                self.ui.label_gerador.setText('Falha')

        if self.ui.ckBox_GPIB_2.isChecked():                    #ACRESCENTADO# Função para comunicação da bancada 2. !!SERIAL E NÃO GPIB!!
            status = lib.GPIB.Conectar_Multimetro_Serial(int(self.ui.Enderac_Multimetro.text()))
            if status == True:
                self.ui.label_multimetro.setText('Conectado')
            else:
                self.ui.label_multimetro.setText('Falha')

        if self.ui.ckBox_GPIB_3.isChecked():                    #ACRESCENTADO# Função para comunicação da bancada 2. !!SERIAL E NÃO GPIB!!
            status = lib.GPIB.Conectar_Multicanal(int(self.ui.Enderac_Multicanal.text()))
            if status == True:
                self.ui.label_multicanal.setText('Conectado')
                self.ui.groupBox_39.setEnabled(True)
            else:
                self.ui.label_multicanal.setText('Falha')

##        if self.ui.ckBox_GPIB_2.isChecked():                  #ORIGINAL#
##            status = lib.GPIB.Conectar_Multimetro(int(self.ui.Enderac_Multimetro.text()))
##            if status == True:
##                self.ui.label_multimetro.setText('Conectado')
##            else:
##                self.ui.label_multimetro.setText('Falha')

    def Habilitar_Multicanal(self):
        self.ch = []
        if self.ui.checkCH_1.isChecked():
            self.ui.groupBox_41.setEnabled(True)
            self.ch.append('101')
        else:
            self.ui.groupBox_41.setEnabled(False)
            
        if self.ui.checkCH_2.isChecked():
            self.ui.groupBox_42.setEnabled(True)
            self.ch.append('102')
        else:
            self.ui.groupBox_42.setEnabled(False)
            
        if self.ui.checkCH_3.isChecked():
            self.ui.groupBox_43.setEnabled(True)
            self.ch.append('103')
        else:
            self.ui.groupBox_43.setEnabled(False)
            
        if self.ui.checkCH_4.isChecked():
            self.ui.groupBox_44.setEnabled(True)
            self.ch.append('104')
        else:
            self.ui.groupBox_44.setEnabled(False)
            
        if self.ui.checkCH_5.isChecked():
            self.ui.groupBox_45.setEnabled(True)
            self.ch.append('105')
        else:
            self.ui.groupBox_45.setEnabled(False)
            
        if self.ui.checkCH_6.isChecked():
            self.ui.groupBox_46.setEnabled(True)
            self.ch.append('106')
        else:
            self.ui.groupBox_46.setEnabled(False)
            
        if self.ui.checkCH_7.isChecked():
            self.ui.groupBox_47.setEnabled(True)
            self.ch.append('107')
        else:
            self.ui.groupBox_47.setEnabled(False)

    def Conf_Multicanal(self):
        self.ui.bt_read_MultiCh.setEnabled(True)
        self.ui.bt_stop_MultiCh.setEnabled(True)

        if self.ui.dc_volts_1.isChecked():
            valor = (", ".join(self.ch))        # Retira os square brackets da lista
            lib.GPIB.Config_Multicanal_volt(valor)

        if self.ui.temp_1.isChecked():
            valor = (", ".join(self.ch))        # Retira os square brackets da lista
            lib.GPIB.Config_Multicanal_temp(valor)

    def start_timer(self):
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.Multicanal)
        self.current_timer.setSingleShot(False)
        self.current_timer.start(10000)

    def stop_timer(self):
        try:
            self.current_timer.stop()
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Selecione pelo menos 1 canal.',QtGui.QMessageBox.Ok)
            return
                                     
    def Multicanal(self):
        try:
            value = lib.GPIB.Coleta_Multicanal()
            vetor = value.split(',')
            for i in range(len(vetor)):
                valor = round(float(vetor[i]),3)
                if self.ch[i] == '101':
                    self.ui.Canal_1.display(valor)
                elif self.ch[i] == '102':
                    self.ui.Canal_2.display(valor)
                elif self.ch[i] == '103':
                    self.ui.Canal_3.display(valor)
                elif self.ch[i] == '104':
                    self.ui.Canal_4.display(valor)
                elif self.ch[i] == '105':
                    self.ui.Canal_5.display(valor)
                elif self.ch[i] == '106':
                    self.ui.Canal_6.display(valor)
                elif self.ch[i] == '107':
                    self.ui.Canal_7.display(valor)
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Leitura interrompida',QtGui.QMessageBox.Ok)
            return

    ########### ABA 6: Motores ###########

    def LIGARMOTOR(self):
        endereco = int(self.ui.EndDriver_2.currentIndex() + 1)
        lib.endereco_pararmotor = endereco
        velocidade = float(self.ui.velocidade.text())
        if velocidade > 5:
            velocidade = 5
            self.ui.velocidade.setText('5')
        aceleracao = float(self.ui.aceleracao.text())
        if aceleracao > 5:
            aceleracao = 5
            self.ui.aceleracao.setText('5')
        voltas = float(self.ui.voltas.text())
        sentido = self.ui.sentido.currentIndex()
        modo = self.ui.modo.currentIndex()
        self.Motor_Manual(endereco, velocidade, aceleracao, voltas, sentido, modo)

    def Motor_Manual(self,endereco, velocidade, aceleracao, voltas, sentido, modo):
##    Endereco(1-Giro;2-Mesa longitudinal) sentido(0-Horario;1-Antihorario) modo(0-manual;1-continuo)
        voltas = int(voltas * lib.passos_volta)
        lib.motor.SetResolucao(endereco,lib.passos_volta)
        lib.motor.ConfMotor(endereco,velocidade,aceleracao,voltas)
        lib.motor.ConfModo(endereco,modo,sentido)
        if lib.motor.ready(endereco):
            lib.motor.MoverMotor(endereco)
            
    def PARARMOTORES(self):
            lib.parartudo = 1
            lib.motor.PararMotor(int(lib.endereco_pararmotor))
            time.sleep(2)
            lib.parartudo = 0
        
    def PARARMOTORES_1(self):
            lib.parartudo = 1
            lib.motor.PararMotor(int(lib.endereco_pararmotor))
            time.sleep(2)
            lib.parartudo = 0
            self.ui.Nome_Ima.setEnabled(True)
            self.ui.observacao.setEnabled(True)
            self.ui.coletar.setEnabled(True)
            self.ui.groupBox_2.setEnabled(True)

    def Texto_Combobox(self):
        if self.ui.EndDriver_2.currentIndex() == 0:
            self.ui.sentido.setItemText(0, "Horário")
            self.ui.sentido.setItemText(1, "Anti-horário")
        if self.ui.EndDriver_2.currentIndex() == 1:
            self.ui.sentido.setItemText(0, "Soltar")
            self.ui.sentido.setItemText(1, "Tracionar")
        

    ########### ABA 7: Bobina ###########

    def Selecao_Tipo_Bobina(self):
        lib.Tipo_Bobina = int(self.ui.tipo_bobina.currentIndex())   ## Tipo = 0 (Radial); Tipo = 1 (Tangencial)

    def Selecao_Sentido_Giro(self):
        lib.sentido = int(self.ui.sentido_2.currentIndex())

    def Selecao_ima_bobina(self):                                   ##ACRESCENTADO## Tipo = 0 (Booster); Tipo = 1 (Anel)
        lib.ima_bobina = int(self.ui.ima_bobina.currentIndex())


    def CARREGABOBINA(self):
        try:
            arquivo = QtGui.QFileDialog.getOpenFileName(self, 'Carregar Arquivo Bobina', '.','Data files (*.dat);;Text files (*.txt)')
            f = open(arquivo, 'r')
        except:
            return
        leitura = f.read().strip()
        f.close()
        dados = leitura.split('\n')
        leitura = dados
        if leitura[0] == '2':
            leitura.pop(0)
        else:
            QtGui.QMessageBox.warning(self,'Atenção.','Arquivo Incorreto.',QtGui.QMessageBox.Ok)
            return
        
        for i in range(len(leitura)):
            c = leitura[i].split('\t')
            dados[i] = c[1]
            
        try:
            self.ui.BobinaNome.setText(dados[0])            
            self.ui.nespiras.setText(dados[1])
            self.ui.raio1.setText(dados[2])
            self.ui.raio2.setText(dados[3])
            self.ui.nespirasb.setText(dados[4])
            self.ui.raio1b.setText(dados[5])
            self.ui.raio2b.setText(dados[6])
            self.ui.pulsos_trigger.setText(dados[7])
            self.ui.sentido_2.setCurrentIndex(int(dados[8]))
            lib.sentido = int(dados[8])
            self.ui.tipo_bobina.setCurrentIndex(int(dados[9]))
            lib.Tipo_Bobina = int(dados[9]) ## Tipo = 0 (Radial) Tipo = 1 (Tangencial)
            lib.ima_bobina = int(dados[10]) #ACRESCENTADO#
            self.ui.observacao_bobina.setPlainText(str(dados[11]))
            self.ui.label_136.setText('OK')
            self.ui.Referenciar_Bobina.setEnabled(True)
            QtGui.QApplication.processEvents()
        except:
            QtGui.QMessageBox.warning(self,'Atenção.','Dados da Bobina Incompletos.',QtGui.QMessageBox.Ok)
            return

    def SALVABOBINA(self):
        try:
            nome = str(self.ui.BobinaNome.text())
        except:
            return
        if nome == '':
            return
        try:
            arquivo = QtGui.QFileDialog.getSaveFileName(self, 'Save File - Dados Bobina', nome,'Data files (*.dat);;Text files (*.txt)')
        except:
            return
        
        Ne = str(self.ui.nespiras.text())
        Neb = str(self.ui.nespirasb.text())
        r1 = str(self.ui.raio1.text())
        r2 = str(self.ui.raio2.text())
        r1b = str(self.ui.raio1b.text())
        r2b = str(self.ui.raio2b.text())
        lib.sentido = int(self.ui.sentido_2.currentIndex())
        bobina = str(self.ui.tipo_bobina.currentIndex())
        lib.Tipo_Bobina = int(bobina)   ## Tipo = 0 (Radial) Tipo = 1 (Tangencial)
        pulsos_trigger = str(self.ui.pulsos_trigger.text())
        lib.ima_bobina = int(self.ui.ima_bobina.currentIndex())     #ACRESCENTADO#
        obs = str(self.ui.observacao_bobina.toPlainText())
        obs = obs.strip()
        obs = obs.replace('\n',' ')
        obs = obs.replace('\t',' ')

        try:
            f = open(arquivo, 'w')
        except:
            return

        f.write('2\n')
        f.write('Nome da bobina:\t' + nome + '\n')
        f.write('Numero espiras Normal:\t' + Ne + '\n')
        f.write('Normal Raio 1:\t' + r1 + '\n')
        f.write('Normal Raio 2:\t' + r2 + '\n')
        f.write('Numero de espiras Bucked:\t' + Neb + '\n')
        f.write('Bucked Raio 1:\t' + r1b + '\n')
        f.write('Bucked Raio 2:\t' + r2b + '\n')
        f.write('Pulso Trigger:\t' + pulsos_trigger + '\n')
        f.write('Sentido Giro:\t' + str(lib.sentido) + '\n')
        f.write('Tipo Bobina:\t' + bobina + '\n')
        f.write('R_ref normalizacao:\t' + str(lib.ima_bobina) + '\n')    #ACRESCENTADO#
        f.write('Observação:\t' + obs)
        f.close()

    def MONTAR(self):
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Rotina de montagem da bobina será inicializada.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        if lib.procura_indice_flag == 1:
            QtGui.QMessageBox.critical(self,'Montar Bobina.','Encoder Angular está sem referência.',QtGui.QMessageBox.Ok)
            return
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Enviar Mesa Longitudinal para Referência.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            lib.motor.MoverMotorFimdeCursoNeg(const.motorC_endereco,1,5)        
            while not lib.motor.ready(const.motorC_endereco) and lib.parartudo == 0:
                time.sleep(0.5)
        else:
            return
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Enviar Mesa A para Posição Livre.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_A(const.final_A,5)
        else:
            return
        while lib.Motor_Posicao == 0:
            time.sleep(.5)
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Enviar Mesa B para Posição Livre.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_B(const.final_B,5)
        else:
            return
        while lib.Motor_Posicao == 0:
            time.sleep(.5)
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Posicionar o Giro da Bobina.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.posicao_angular(const.pos_ang, 1)
        else:
            return     
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Posicionar a Bobina Dentro do Ima.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Enviar Mesa A para Posição de Pré Montagem.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_A(const.premont_A,5)
        else:
            return    
        while lib.Motor_Posicao == 0:
            time.sleep(.5)          
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Enviar Mesa A para Posição Zero.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_A(0,1)
        else:
            return
        while lib.Motor_Posicao == 0:
            time.sleep(.5)
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Enviar Mesa B para Posição de Pré Montagem.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_B(const.premont_B,5)
        else:
            return
        while lib.Motor_Posicao == 0:
            time.sleep(.5)
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Ligar o conector na Bobina.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Enviar Mesa B para Posição Zero.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_B(0,1)
        else:
            return
        while lib.Motor_Posicao == 0:
            time.sleep(.5)
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Realizar a pré-tração da Bobina.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            lib.motor.ConfMotor(const.motorC_endereco,1,5,int(const.pos_long*const.passos_mmC))
            lib.motor.ConfModo(const.motorC_endereco,0,const.avancoC)
            lib.motor.MoverMotor(const.motorC_endereco)            
            while not lib.motor.ready(const.motorC_endereco) and lib.parartudo == 0:
                time.sleep(0.5)
        else:
            return
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Travar a Bobina Manualmente.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        ret = QtGui.QMessageBox.question(self,'Montar Bobina.','Finalizar a tração da Bobina.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            lib.motor.ConfMotor(const.motorC_endereco,1,5,int((const.pos_trac - const.pos_long)*const.passos_mmC))
            lib.motor.ConfModo(const.motorC_endereco,0,const.avancoC)
            lib.motor.MoverMotor(const.motorC_endereco)
            while not lib.motor.ready(const.motorC_endereco) and lib.parartudo == 0:
                time.sleep(0.5)
        else:
            return
        QtGui.QMessageBox.critical(self,'Montar Bobina.','Processo de montagem da Bobina Finalizado.',QtGui.QMessageBox.Ok)        
       
    def DESMONTAR(self):
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Rotina de desmontagem da bobina será inicializada.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        if lib.procura_indice_flag == 1:
            QtGui.QMessageBox.critical(self,'Desmontar Bobina.','Encoder Angular está sem referência.',QtGui.QMessageBox.Ok)
            return
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Posicionar o Giro da Bobina.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.posicao_angular(const.pos_ang, 1)
        else:
            return
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Destravar a Bobina Manualmente.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Retirar a tração da Bobina.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            lib.motor.ConfMotor(const.motorC_endereco,1,5,int((const.pos_trac)*const.passos_mmC))
            lib.motor.ConfModo(const.motorC_endereco,0,const.avancoC^1)
            lib.motor.MoverMotor(const.motorC_endereco)
            while not lib.motor.ready(const.motorC_endereco) and lib.parartudo == 0:
                time.sleep(0.5)
        else:
            return
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Enviar Mesa B para Posição de Pré Desmontagem.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_B(const.premont_B,1)
        else:
            return    
        while lib.Motor_Posicao == 0:
            time.sleep(.5)
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Desligar o conector na Bobina.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Enviar Mesa B para Posição Final.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_B(const.final_B,5)
        else:
            return    
        while lib.Motor_Posicao == 0:
            time.sleep(.5)  
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Enviar Mesa A para Posição de Pré Desmontagem.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_A(const.premont_A,1)
        else:
            return    
        while lib.Motor_Posicao == 0:
            time.sleep(.5)         
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Enviar Mesa A para Posição Final.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.Mover_Motor_A(const.final_A,5)
        else:
            return    
        while lib.Motor_Posicao == 0:
            time.sleep(.5)
        ret = QtGui.QMessageBox.question(self,'Desmontar Bobina.','Retirar a Bobina de Dentro do Ima.\nDeseja continuar?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        QtGui.QMessageBox.critical(self,'Desmontar Bobina.','Processo de desmontagem da Bobina Finalizado.',QtGui.QMessageBox.Ok)

    def Referenciar_Bobina(self):
        ret = QtGui.QMessageBox.question(self,'Referenciar Bobina.','Deseja Referenciar a Bobina Girante?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return
        if self.ui.configurar_integrador.text() == 'Referenciar':
            QtGui.QMessageBox.critical(self,'Referenciar Bobina.','Configurar/Referenciar Integrador Primeiro.',QtGui.QMessageBox.Ok)
            return
        repeticao = 3
        lib.Ref_Bobina = 1
        Pulsos_encoder = (int(self.ui.pulsos_encoder.text()) * 4)
        Resolucao_encoder = Pulsos_encoder/(2*numpy.pi)
        trigger_inicial = self.ui.pulsos_trigger.text()
        self.ui.pulsos_trigger.setText('0')
        self.ui.TipoIma.setCurrentIndex(1)
        self.ui.Nome_Ima.setText('Referenciando Bobina: ' + str(self.ui.BobinaNome.text()))
        refinar=0
        
        while refinar < (repeticao+1):    
            angulo_ref=numpy.zeros(int(repeticao))
            Nn_ref=numpy.zeros(int(repeticao))
            Sn_ref=numpy.zeros(int(repeticao))
            
            if refinar>0:
                self.ui.pulsos_trigger.setText(str(int(Pulso_final)))
            for i in range(repeticao):
                status = self.COLETA_INTEGRADOR()
                if status == False:
                    self.ui.pulsos_trigger.setText(str(trigger_inicial))
                    return
                QtGui.QApplication.processEvents()
                angulo_ref[i] = lib.Angulo[1]
                Nn_ref[i] = lib.Nn[1]
                Sn_ref[i] = lib.Sn[1]

            angulo_final = numpy.mean(angulo_ref,axis=0)
            Nn_final = numpy.mean(Nn_ref,axis=0)
            Sn_final = numpy.mean(Sn_ref,axis=0)
            Pulsos = int(round((Pulsos_encoder * angulo_final)/(2*numpy.pi),0))
            
            if refinar==0:
                if Nn_final>=0:
                    if Sn_final>=0:
                        Pulso_final = int(abs(Pulsos)) ## Certo
                    else:
                        Pulso_final = int(Pulsos_encoder - abs(Pulsos)) ## Certo
                else:
                    if Sn_final>=0:
                        Pulso_final = int((Pulsos_encoder/2) - abs(Pulsos)) ## Certo
                    else:
                        Pulso_final = int((Pulsos_encoder/2) + abs(Pulsos)) ## Certo
            else:
                if abs(angulo_final)>(5e-5):
                    Pulso_final = int(Pulso_final + Pulsos) ## Certo
                else:
                    break
                
            refinar+=1

        if refinar==(repeticao+1):
            QtGui.QMessageBox.critical(self,'Referenciar Bobina.','Bobina Não Referenciada.\nVerificar sistema manualmente.',QtGui.QMessageBox.Ok)
            lib.Ref_Bobina = 0
            return
        
        lib.Ref_Bobina = 0
        self.SALVABOBINA()
        QtGui.QMessageBox.information(self,'Referenciar Bobina.','Bobina Referenciada com Sucesso.',QtGui.QMessageBox.Ok)
        self.ui.Nome_Ima.setText('')
        
    ########### ABA 8: Integrador ###########

    def SALVAR_DEFAULT(self):
        port1 = str(self.ui.Porta.currentIndex()+1)
        port2 = str(self.ui.Porta_2.currentIndex()+1)
        port3 = str(self.ui.Porta_3.currentIndex()+1)
        port4 = str(self.ui.Porta_4.currentIndex()+1)
        enderec = str(self.ui.Enderac_PUC.text())
        ganho = str(self.ui.ganho.currentIndex())
        pontos_integracao = str(self.ui.pontos_integracao.currentIndex())
        pulsos_encoder = self.ui.pulsos_encoder.text()
        velocidade = self.ui.velocidade_int.text()
        aceleracao = self.ui.aceleracao_int.text()
        voltas_offset = self.ui.voltas_offset.text()
        volta_filtro = self.ui.filtro_voltas.text()
        descarte_inicial = self.ui.descarte_inicial.text()
        descarte_final = self.ui.descarte_final.text()
        N = self.ui.nespiras.text()
        raio1 = self.ui.raio1.text()
        raio2 = self.ui.raio2.text()
        gpib_gerador = str(self.ui.Enderac_Gerador.text())
        gpib_multimetro = str(self.ui.Enderac_Multimetro.text())
        f = open('default_settings.dat','w')
        f.write('0\n')
        f.write('Configurações da bobina girante\n\n')
        f.write('Tipo Display\t'+ str(lib.tipo_display) + '\n')
        f.write('Porta Display\t' + port1 + '\n')
        f.write('Porta Driver\t' + port2 + '\n')
        f.write('Porta Integrador\t' + port3 + '\n')
        f.write('Tipo PUC\t' + str(lib.Modelo_PUC) + '\n')
        f.write('Porta PUC\t' + port4 + '\n')
        f.write('Enderecamento PUC\t' + enderec + '\n\n')
        f.write('Endereco Driver\t' + str(lib.endereco) + '\n')
        f.write('Ganho\t' + ganho + '\n')
        f.write('Pontos Integracao\t' + pontos_integracao + '\n')
        f.write('Pulsos Encoder\t' + pulsos_encoder + '\n')
        f.write('Velocidade Medida\t' + velocidade + '\n')
        f.write('Aceleracao Medida\t' + aceleracao + '\n')
        f.write('Voltas offset\t' + voltas_offset + '\n')
        f.write('Volta filtro\t' + volta_filtro + '\n')
        f.write('Passos Motor\t' + str(lib.passos_volta) + '\n\n')
        f.write('\n\nEndereco Driver A\t' + str(const.motorA_endereco) + '\n')
        f.write('Endereco Driver B\t' + str(const.motorB_endereco) + '\n')
        f.write('Endereco Driver C\t' + str(const.motorC_endereco) + '\n')
        f.write('Avanco do motor A\t' + str(const.avancoA) + '\n')
        f.write('Avanco do motor B\t' + str(const.avancoB) + '\n')
        f.write('Avanco do motor C\t' + str(const.avancoC) + '\n')
        f.write('Descarte voltas iniciais\t' + str(descarte_inicial) + '\n')
        f.write('Descarte voltas finais\t' + str(descarte_final) + '\n')
        f.write('Posicao de indice A\t' + str(const.zeroA) + '\n')
        f.write('Posicao de indice B\t' + str(const.zeroB) + '\n')
        f.write('Posicao de Premontagem A\t' + str(const.premont_A) + '\n')
        f.write('Posicao de Premontagem B\t' + str(const.premont_B) + '\n')
        f.write('Posicao de Final A\t' + str(const.final_A) + '\n')
        f.write('Posicao de Final B\t' + str(const.final_B) + '\n')        
        f.write('Posicao angular montagem\t' + str(const.pos_ang) + '\n')
        f.write('Posicao longitudinal montagem\t' + str(const.pos_long) + '\n')
        f.write('Posicao vertical\t' + str(const.pos_ver) + '\n')
        f.write('Posicao tracao\t' + str(const.pos_trac)+ '\n')
        f.write('Endereço GPIB Gerador\t' + str(gpib_gerador)+ '\n')
        f.write('Endereço GPIB Multimetro\t' + str(gpib_multimetro))
        f.close()
                
    def POSICIONAR(self):
        try:
            posicao = int(self.ui.posicao_angular.text())
        except:
            return
        if posicao > (lib.pulsos_encoder - 1):
            posicao = (lib.pulsos_encoder - 1)
            self.ui.posicao_angular.setText(str((lib.pulsos_encoder - 1)))
        if posicao < 0:
            posicao = 0
            self.ui.posicao_angular.setText('0')
        self.posicao_angular(posicao, lib.endereco,(1/1),(1/1))

    def posicao_angular(self, posicao, endereco, velocidade=1, aceleracao=1):
        tempoespera = 0.1
        lib.integrador.LimpaTxRx()
        lib.integrador.Enviar(lib.integrador.PDILerEncoder)
        time.sleep(tempoespera)
        valor = lib.integrador.ser.readall().strip()
        valor = str(valor).strip('b').strip("'")
        valor = int(valor)
        erro = posicao - valor
        if erro < 0:
            sentido = 0
        else:
            sentido = 1
        passos = int(lib.passos_volta*abs(erro)/lib.pulsos_encoder)  #/10000
        lib.motor.ConfMotor(endereco,velocidade,aceleracao,passos)
        lib.motor.ConfModo(endereco,0,sentido)
        lib.motor.MoverMotor(endereco)

    def Correcao_Posicao(self):
        posicao = lib.pulsos_trigger + (lib.pulsos_encoder / 2)
        if posicao > lib.pulsos_encoder:
            posicao = posicao - lib.pulsos_encoder
        self.posicao_angular(posicao, lib.endereco,(1/1),(1/1))
        time.sleep(2)

    def EMERGENCIA(self):
        self.KILL()
        lib.Janela.ui.coletar.setEnabled(True)
        lib.Janela.ui.groupBox_2.setEnabled(True)

            
    def Tabela(self):
##        self.ui.tabela.clear()
        TipoIma = lib.Janela.ui.TipoIma.currentIndex()
        if len(lib.F[0])>16:
            nmax = 16
        else:
            nmax = 8
        for i in range(1,nmax,1):
            self.set_item(i-1,0,str(lib.Nn[i]))
            self.set_item(i-1,1,str(lib.sDesvNn[i]))
            self.set_item(i-1,2,str(lib.Sn[i]))
            self.set_item(i-1,3,str(lib.sDesvSn[i]))
            self.set_item(i-1,4,str(lib.SMod[i]))
            self.set_item(i-1,5,str(lib.sDesv[i]))
            if i == TipoIma or TipoIma == 0:
                self.set_item(i-1,6,str(lib.Angulo[i]))
            else:
                self.set_item(i-1,6,str('0.00'))
            self.set_item(i-1,7,str(lib.Desv_angulo[i]))
            self.set_item(i-1,8,str(lib.Nnl[i]))
            self.set_item(i-1,9,str(lib.Snl[i]))

        self.deslocamento()

    def set_item(self,lin,col,Text):
        item = QtGui.QTableWidgetItem()
        self.ui.tabela.setItem(lin, col, item)
        item.setText(Text)

    def deslocamento(self):
        ordens = numpy.array([])
        posicao = int(lib.Janela.ui.TipoIma.currentIndex())
        for i in range(posicao):
            self.ui.tabela.setCurrentCell(i,0) 
            v_Nn = self.ui.tabela.currentItem().text() #valores Nn
            self.ui.tabela.setCurrentCell(i,2)             
            v_Sn = self.ui.tabela.currentItem().text() #valores Sn
            ordens = numpy.append(ordens, float(v_Nn))
            ordens = numpy.append(ordens, float(v_Sn))
        if posicao == 2:
            calc_X = ordens[0]/ordens[2]/1e-06              #cálculo deslocamento X => (Dipolo Nn / Quadrupolo Nn)
            calc_Y = ordens[1]/ordens[2]/1e-06              #cálculo deslocamento Y => (Dipolo Sn / Quadrupolo Nn)
        elif posicao == 3:
            calc_X = ordens[2]/(2*ordens[4])/1e-06              #cálculo deslocamento X => (Quadrupolo Nn / (2*Sextupolo Nn))
            calc_Y = ordens[3]/(2*ordens[4])/1e-06              #cálculo deslocamento Y => (Quadrupolo Sn / (2*Sextupolo Nn))
            
        self.ui.desl_X.setText(str(calc_X))
        self.ui.desl_Y.setText(str(calc_Y))
    
    def ProcuraIndiceEncoder(self):
        tempoespera = 0.1
        lib.integrador.Enviar(lib.integrador.PDIZerarContador)
        time.sleep(tempoespera)
        lib.integrador.Enviar(lib.integrador.PDIProcuraIndice)
        time.sleep(tempoespera)
        lib.motor.SetResolucao(lib.endereco,lib.passos_volta)
        lib.motor.ConfMotor(lib.endereco,1,1,lib.passos_volta*3)
        lib.motor.ConfModo(lib.endereco,0,lib.sentido)
        lib.motor.MoverMotor(lib.endereco)
        while not lib.motor.ready(lib.endereco) and not lib.parartudo:
            continue
##        lib.motor.ConfModo(lib.endereco,0,1)
##        lib.motor.MoverMotor(lib.endereco)
##        while not lib.motor.ready(lib.endereco) and not lib.parartudo:
##            continue
##        lib.motor.ConfModo(lib.endereco,0,0)
##        lib.motor.MoverMotor(lib.endereco)
##        while not lib.motor.ready(lib.endereco) and not lib.parartudo:
##            continue
        if not lib.parartudo:
            lib.integrador.LimpaTxRx()
            lib.integrador.Enviar(lib.integrador.PDILerEncoder)
            time.sleep(tempoespera)
            valor = lib.integrador.ser.readall().strip()
            valor = str(valor).strip('b').strip("'")
            valor = int(valor)
            passos = int(lib.passos_volta*valor/lib.pulsos_encoder)  #/10000
            lib.motor.ConfMotor(lib.endereco,1,1,passos)
            lib.motor.ConfModo(lib.endereco,0,0)
            lib.motor.MoverMotor(lib.endereco)
            
    def Start_Config(self):
        bit = 0
        lib.integrador.Enviar('ISC,A,1')
        self.CONFIGURARINTEGRADOR(bit)
        
    def CONFIGURARINTEGRADOR(self,bit):
        lib.ganho = self.ui.ganho.currentIndex()
        lib.ganho = const.ganhos[lib.ganho]
        pontos_integracao = self.ui.pontos_integracao.currentIndex()
        lib.pontos_integracao = const.p_integracao[pontos_integracao]
        lib.endereco = self.ui.EndDriver.currentIndex()+1
        try:
            lib.velocidade = float(self.ui.velocidade_int.text())
            lib.aceleracao = float(self.ui.aceleracao_int.text())
        except:
            QtGui.QMessageBox.critical(self,'Erro.','Não foi possível converter os valores de velocidade e aceleração.',QtGui.QMessageBox.Ok)
            return        
        try:
            lib.pulsos_encoder = (int(self.ui.pulsos_encoder.text())) * 4
            lib.voltas_offset = int(self.ui.voltas_offset.text()) + int(self.ui.descarte_inicial.text()) + int(self.ui.descarte_final.text()) + 1  # n voltas descarte_inicial_final aceleracao; 1 filtro de erro transmissão de dados
        except:
            QtGui.QMessageBox.critical(self,'Erro.','Parâmetros de configuração do integrador devem ser números inteiros.',QtGui.QMessageBox.Ok)
            return
        try:
            lib.pulsos_trigger = int(self.ui.pulsos_trigger.text())
        except:
            QtGui.QMessageBox.critical(self,'Erro.','Carregar Parâmetros da Bobina.',QtGui.QMessageBox.Ok)
            return
        if lib.velocidade > 2.5:
            QtGui.QMessageBox.warning(self,'Atenção.','Velocidade muito alta.',QtGui.QMessageBox.Ok)
            lib.velocidade = 2.5
            self.ui.velocidade_int.setText('2.5')
        if lib.aceleracao > 10:
            QtGui.QMessageBox.warning(self,'Atenção.','Aceleracao muito alta.',QtGui.QMessageBox.Ok)
            lib.aceleracao = 10
            self.ui.aceleracao_int.setText('10')
        if lib.pulsos_trigger > int(lib.pulsos_encoder-1):
            QtGui.QMessageBox.critical(self,'Atenção.','Pulso de Início Maior que permitido.\nTente novamente.',QtGui.QMessageBox.Ok)
            return
        lib.sentido = int(lib.Janela.ui.sentido_2.currentIndex())
        self.ui.label_69.setText('Máx: ' + str(int(lib.pulsos_encoder-1)))

        if lib.procura_indice_flag == 0:
            if lib.sentido == 0:
                lib.integrador.Configurar_Integrador('-',lib.ganho, lib.pontos_integracao, lib.pulsos_encoder, lib.pulsos_trigger, lib.voltas_offset)
            elif lib.sentido == 1:
                lib.integrador.Configurar_Integrador('+',lib.ganho, lib.pontos_integracao, lib.pulsos_encoder, lib.pulsos_trigger, lib.voltas_offset)

        if lib.procura_indice_flag == 1:           
##            self.Motor_Manual(lib.endereco, lib.velocidade, lib.aceleracao, 10, lib.sentido, 0)   #Voltas de acomodamento
            if lib.sentido == 0:
                lib.integrador.Configurar_Integrador('-',lib.ganho, lib.pontos_integracao, lib.pulsos_encoder, lib.pulsos_trigger, lib.voltas_offset)
            elif lib.sentido == 1:
                lib.integrador.Configurar_Integrador('+',lib.ganho, lib.pontos_integracao, lib.pulsos_encoder, lib.pulsos_trigger, lib.voltas_offset)
            time.sleep(1)
            self.ProcuraIndiceEncoder()
            lib.procura_indice_flag = 0
            self.ui.configurar_integrador.setText('Configurar')
            self.ui.posicionar.setEnabled(True)
##            self.ui.Zerar_Offset.setEnabled(True)
            self.ui.label_137.setText('OK')
            QtGui.QApplication.processEvents()
            
        if self.ui.TipoIma.currentIndex() == 0:
            self.ui.filtro_voltas.setEnabled(False)
        else:
            self.ui.filtro_voltas.setEnabled(True)
        if bit == 0:
            QtGui.QMessageBox.information(self,'Aviso.','Integrador configurado com sucesso.',QtGui.QMessageBox.Ok)

    def LERENCODER(self):
        lib.integrador.LimpaTxRx()
        lib.integrador.Enviar(lib.integrador.PDILerEncoder)
        time.sleep(0.05)
        valor = lib.integrador.ser.readall().strip()
        valor = str(valor).strip('b').strip("'")
        valor = int(valor)
        self.ui.lcdNumber.display(valor)

    def ZERAROFFSET(self):
        voltas = 12
        self.Motor_Manual(lib.endereco, lib.velocidade, lib.aceleracao, voltas, lib.sentido, 0)
        time.sleep(1/lib.aceleracao)
        lib.integrador.Enviar('ISC,A,0')
        lib.integrador.Enviar(lib.integrador.PDICurtoCircuito)
        time.sleep(voltas/lib.velocidade)
        lib.integrador.Enviar('ISC,A,1')
        QtGui.QMessageBox.information(self,'Aviso.','Off-set Integrador Zerado com sucesso.',QtGui.QMessageBox.Ok)

    def Status_Integrador(self,status,bit): ## status[1..7]   bit[0..7] [8:byte]
        try:
            status = str(int(status))
            bit = int(bit+1)
        except:
            QtGui.QMessageBox.information(self,'Aviso.','Dados Incorretos.',QtGui.QMessageBox.Ok)
            return
        dados = lib.integrador.Status(status)
        if bit==9:
            bitstatus = int(dados)
        else:
            bitstatus = int(dados[-bit])
        return bitstatus

    def Status_Display_Integrador(self):
        x=[0,0,0,0,0,0,0,0]
        for i in range(1,8,1):
            x[i] = self.Status_Integrador(i,8)
##            time.sleep(.1)
        self.ui.label_status_1.setText(str(x[1]).zfill(8))
        self.ui.label_status_2.setText(str(x[2]).zfill(8))
        self.ui.label_status_3.setText(str(x[3]).zfill(8))
        self.ui.label_status_4.setText(str(x[4]).zfill(8))
        self.ui.label_status_5.setText(str(x[5]).zfill(8))
        self.ui.label_status_6.setText(str(x[6]).zfill(8))
        self.ui.label_status_7.setText(str(x[7]).zfill(8))
        



     ########### ABA 9: Coletas ###########
    def Verificar_Ganho_Maximo(self):
        if (self.ui.ganho.currentIndex() != 6):
            ret = QtGui.QMessageBox.question(self,'Configuração.','Deseja Configurar Ganho Maximo do Integrador?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
            if ret == QtGui.QMessageBox.Yes:
                self.ui.ganho.setCurrentIndex(6)
                QtGui.QApplication.processEvents()
                

    def Desalinhamento(self):
        lib.display.LerDisplay()
        lib.posicao = lib.display.DisplayPos
        if self.ui.Desab_Desalinhamento.isChecked():
            return True
        else:
            if abs(lib.posicao[0])>0.005 or abs(lib.posicao[1])>0.005: #### 0.005
                QtGui.QMessageBox.information(self,'Aviso.','Corrigir Motores Transversais.',QtGui.QMessageBox.Ok)
                return False
            else:
                return True
            
        

########################## Corretoras ###############################

    def Ciclagem_Corretora(self):
        tempo_ciclagem=80 ##segundos
        self.ui.Ciclagem_Corretora.setEnabled(False)
        self.ui.coletar.setEnabled(False)
        QtGui.QApplication.processEvents()  #Atualizar tela
        lib.GPIB.Conectar_Gerador(19)
        resp=lib.GPIB.Config_Gerador_Ciclagem(1/tempo_ciclagem)
        if resp==True:
            time.sleep(tempo_ciclagem-1)
            lib.GPIB.Saida_Gerador(0)
            QtGui.QMessageBox.information(self,'Aviso.','Ciclagem Concluida com sucesso.',QtGui.QMessageBox.Ok)
        else:
            lib.GPIB.Saida_Gerador(0)
            QtGui.QMessageBox.information(self,'Aviso.','Falha na Ciclagem.',QtGui.QMessageBox.Ok)            
        self.ui.Ciclagem_Corretora.setEnabled(True)
        self.ui.coletar.setEnabled(True)

    def Selecao(self):
        if self.ui.Hab_Corretora.isChecked():
            self.ui.Ciclagem_Corretora.setEnabled(True)
            self.ui.Corrente_Arbitraria_GPIB.setEnabled(True)
            self.ui.C_Sucessivas.setEnabled(False)
            self.ui.Chk_Auto.setEnabled(False)
        else:
            self.ui.Ciclagem_Corretora.setEnabled(False)
            self.ui.Corrente_Arbitraria_GPIB.setEnabled(False)
            self.ui.C_Sucessivas.setEnabled(True)
            if (lib.PUC_Conectada == 1):
                self.ui.Chk_Auto.setEnabled(True)
                
        if self.ui.Hab_Curva_Quadrupolo.isChecked():
            self.ui.Ciclar_Curva_Quadrupolo.setEnabled(True)
            self.ui.Ciclos_Curva_Quadrupolo.setEnabled(True)
            self.ui.groupBox_33.setEnabled(True)
        else:
            self.ui.Ciclar_Curva_Quadrupolo.setEnabled(False)
            self.ui.Ciclos_Curva_Quadrupolo.setEnabled(False)
            self.ui.groupBox_33.setEnabled(False)

        if self.ui.Hab_Selecao.isChecked():
            self.ui.Selecao_Corrente_Arbitraria_PUC.setEnabled(True)
        else:
            self.ui.Selecao_Corrente_Arbitraria_PUC.setEnabled(False)        

    def Rampa_Corretora(self,final,atual,passo,tempo):
        try:
            if final > atual:
                faixa = numpy.arange(atual+passo,final,passo)
            else:
                faixa = numpy.arange(final,atual,passo)
                faixa = faixa[::-1]
            faixa[-1] = final
            for i in faixa:
                if (lib.parartudo == 0):
                    time.sleep(tempo)
                    resp = lib.GPIB.DC_Saida(i)
                    if resp == False:
                        return False
                else:
                    lib.GPIB.DC_Saida(0)
                    time.sleep(0.1)
                    return False
            return True
        except:
            try:
                if ((final>atual) and ((final-atual)<passo)) or ((final<atual) and ((atual-final)<passo)):
                    resp = lib.GPIB.DC_Saida(final)
                    if resp == False:
                        return False
                    return True
            except:
                return False
            


########################## Corretoras ###############################


            
                
    def Coleta_Suc_Manual(self):
        if self.ui.C_Sucessivas.isChecked():
            self.ui.N_Coletas_Manual.setEnabled(True)
            self.ui.label_22.setEnabled(True)
            self.ui.Chk_Auto.setEnabled(False)
            self.ui.Hab_Corretora.setEnabled(False)
        else:
            self.ui.N_Coletas_Manual.setEnabled(False)
            self.ui.label_22.setEnabled(False)
            self.ui.Hab_Corretora.setEnabled(True)
            if (lib.PUC_Conectada == 1):
                self.ui.Chk_Auto.setEnabled(True)           

    def COLETA_INTEGRADOR(self):
        lib.endereco_pararmotor = lib.endereco
        tipo_coleta = 0
        desalinhado = self.Desalinhamento()
        if desalinhado == False:
            return False
        if (lib.PUC_Conectada == 1) and ((lib.Fonte_Pronta == 0) or (lib.Fonte_Calibrada != [1,1])):
            QtGui.QMessageBox.warning(self,'Atenção.','Fonte Não esta Pronta. Verifique dados da fonte.\nTente Novamente.',QtGui.QMessageBox.Ok)
            return False
        if self.ui.label_136.text() == 'NOK':
            QtGui.QMessageBox.warning(self,'Atenção.','Carregue dados da bobina.\nTente Novamente.',QtGui.QMessageBox.Ok)
            return False
        if self.ui.label_137.text() == 'NOK':
            QtGui.QMessageBox.warning(self,'Atenção.','Configurar Integrador.\nTente Novamente.',QtGui.QMessageBox.Ok)
            return False
        if self.ui.Nome_Ima.text() == '':
            QtGui.QMessageBox.warning(self,'Atenção.','Informe o Nome do Ima.\nTente Novamente.',QtGui.QMessageBox.Ok)
            return False
        if self.ui.tempLine.text() == '':                           #ACRESCENTADO#
            QtGui.QMessageBox.warning(self,'Atenção.','Informe a temperatura do ímã.\nTente Novamente.',QtGui.QMessageBox.Ok)
            return False
        
        if (self.ui.tabWidget.isTabEnabled(3) == True) and (self.ui.Chk_Auto.isChecked()):
            tipo_coleta = 2
        if (self.ui.C_Sucessivas.isChecked()):
            tipo_coleta = 1
        if self.ui.Hab_Corretora.isChecked():
            tipo_coleta = 3

        if lib.Ref_Bobina == 1:
            tipo_coleta = 0

        if tipo_coleta == 0:
            self.ui.coletar.setEnabled(False)
            
        nome = str(self.ui.Nome_Ima.text())
        nome = nome.upper()
        self.Verificar_Ganho_Maximo()
        self.CONFIGURARINTEGRADOR(1)
        self.ui.label_138.setText('0')
        QtGui.QApplication.processEvents()
        
        if tipo_coleta == 0: #Rotina de Coleta de corrente manual para coleta unica
            self.ui.groupBox_2.setEnabled(False)
            self.Correcao_Posicao()
            Verificar = ColetaDados(1)
            if Verificar == False:
                QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Desvio Padrão Elevado. Processo Finalizado.\nVerifique parametros e equipamentos.',QtGui.QMessageBox.Ok)
                ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Mostrar Dados com Desvio Padrão Elevado?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                if ret == QtGui.QMessageBox.Yes:
                    lib.Janela.ui.coletar.setEnabled(True)
                    lib.Janela.ui.tabWidget.setTabEnabled(9,True)
##                    lib.Janela.ui.tabWidget.setCurrentIndex(9)
                    lib.Janela.ui.tabela.setEnabled(True)
                    lib.Janela.ui.salvar_harmonico.setEnabled(True)
                    lib.Janela.ui.Emergencia_9.setEnabled(True)
                    self.Tabela()
                    self.ui.label_138.setText('1')
##                    x = numpy.linspace(0,1,len(lib.media))
##                    lib.Janela.PlotFunc1(x,lib.media)
                    QtGui.QApplication.processEvents()
                    return
##                    pass
                else:
                    lib.Janela.ui.groupBox_2.setEnabled(True)
                    lib.Janela.ui.coletar.setEnabled(True)
                    QtGui.QApplication.processEvents()
                    return
            self.Tabela()
            self.ui.label_138.setText('1')
            QtGui.QApplication.processEvents()

        if tipo_coleta == 1: #Rotina de Coleta de corrente manual com coletas Sucessivas
            try:
                Rep = int(self.ui.N_Coletas_Manual.text())
                if Rep <= 1:
                    QtGui.QMessageBox.warning(self,'Atenção.','Número de Coletas deve ser Maior que 1.\nTente Novamente.',QtGui.QMessageBox.Ok)
                    return
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Número de Coletas Sucessivas Não Inteiro.\nTente Novamente.',QtGui.QMessageBox.Ok)
                return
            ret = QtGui.QMessageBox.question(self,'Coleta Automatica.','Deseja Coletar Automaticamente ' + str(Rep) + ' Medidas na mesma Corrente?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
            lib.FileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File - Coleta Automática Corrente Manual', nome,'Data files')
            self.ui.groupBox_2.setEnabled(False)
            self.ui.coletar.setEnabled(False)
            self.ui.Nome_Ima.setEnabled(False)
            self.ui.observacao.setEnabled(False)
            self.ui.N_Coletas_Manual.setEnabled(False)
            self.ui.tempLine.setEnabled(False)
            if (lib.Janela.ui.tabWidget.isTabEnabled(3) == True):
                dados_corrente = float(lib.Corrente_Atual)
            else:
                dados_corrente = 0
            for i in range(0,Rep,1):
                self.Correcao_Posicao()
                Verificar = ColetaDados(Rep)
                if Verificar == False:
                    QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Processo de Medição Interrompido. Desvio Padrão Elevado.',QtGui.QMessageBox.Ok)
                    ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Desvio Padrão Elevado.\nDeseja Salvar a Medida?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                    if ret == QtGui.QMessageBox.Yes:
                        pass
                    else:
                        ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Deseja continuar o Processo de Medição?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                        if ret == QtGui.QMessageBox.Yes:
                            continue
                        else:
                            lib.Janela.ui.groupBox_2.setEnabled(True)
                            lib.Janela.ui.coletar.setEnabled(True)
                            self.ui.Nome_Ima.setEnabled(True)
                            self.ui.observacao.setEnabled(True)
                            self.ui.N_Coletas_Manual.setEnabled(True)
                            self.ui.tempLine.setEnabled(True)
                            QtGui.QApplication.processEvents()
                            return
                time.sleep(1)
                self.Salvar_Coletas(1,(i+1),dados_corrente)
                self.ui.label_138.setText(str(i+1))
                QtGui.QApplication.processEvents()  #Atualizar tela
            QtGui.QMessageBox.information(lib.Janela,'Atenção.','Processo de Coleta Automática Concluído.',QtGui.QMessageBox.Ok)
            self.ui.coletar.setEnabled(True)
            self.ui.Nome_Ima.setEnabled(True)
            self.ui.observacao.setEnabled(True)
            self.ui.N_Coletas_Manual.setEnabled(True)
            self.ui.tempLine.setEnabled(True)
            self.ui.groupBox_2.setEnabled(True)
            
        if tipo_coleta == 2:  #Rotina de Coleta com corrente em automatico
            try:
                dados_corrente = self.Converter_Corrente_Arbitraria(self.ui.Corrente_Arbitraria_PUC.toPlainText(),0) ### Armazena os valores de corrente inseridos no campo correntes (A) (QPlainTexyEdit).
                if (self.ui.Hab_Selecao.isChecked()):
                    dados_selecao_correntes = self.Converter_Corrente_Arbitraria(self.ui.Selecao_Corrente_Arbitraria_PUC.toPlainText(),2) ###
                    if (len(dados_corrente)) != (len(dados_selecao_correntes)):
                        QtGui.QMessageBox.warning(self,'Atenção.','Quantidade de Dados entre Correntes Automáticas e Seleção de Medida são DIFERENTES.\nTente Novamente.',QtGui.QMessageBox.Ok)
                        return
                else:
                    vetor_selecao = []
                    for i in range(len(dados_corrente)):
                        vetor_selecao.append('Y')
                    dados_selecao_correntes = vetor_selecao
                        
                for i in range(len(dados_corrente)):
                        dados_corrente[i]=self.Verificar_Limite_Corrente(1,dados_corrente[i])
                        if (dados_corrente[i] == 'False'):
                            return
                self.ui.Corrente_Arbitraria_PUC.setPlainText(self.Recuperar_Valor(0,str(dados_corrente)))
            except:
                QtGui.QMessageBox.warning(self,'Atenção.','Verificar Valores de Corrente Automático.\nTente Novamente.',QtGui.QMessageBox.Ok)
                return
            ret = QtGui.QMessageBox.question(self,'Coleta Automatica.','Deseja Coletar Automaticamente ' + str(len(dados_corrente)) + ' Medidas em Diferentes Correntes?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return            
            lib.FileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File - Coleta Automática Corrente Automática', nome,'Data files')
            self.ui.groupBox_2.setEnabled(False)
            self.ui.coletar.setEnabled(False)
            self.ui.Nome_Ima.setEnabled(False)
            self.ui.tempLine.setEnabled(False)
            self.ui.observacao.setEnabled(False)
            self.Rampa_Corrente_Automatico(dados_corrente,dados_selecao_correntes)
            self.ui.groupBox_2.setEnabled(True)
            self.ui.coletar.setEnabled(True)
            self.ui.tempLine.setEnabled(True)
            self.ui.observacao.setEnabled(True)
            self.ui.Nome_Ima.setEnabled(True)

        if tipo_coleta == 3: #Rotina de Coleta para Corretoras, correntes estipuladas na caixa de dados
            if self.ui.label_multimetro.text()!='Conectado' or self.ui.label_gerador.text()!='Conectado': ## com multimetro e gerador
##            if self.ui.label_gerador.text()!='Conectado':  ## com gerador
                QtGui.QMessageBox.warning(self,'Atenção.','Verificar Configurações GPIB.\nTente Novamente.',QtGui.QMessageBox.Ok)
                return
            lib.GPIB.Config_Gerador_DC()
            dados_corrente = self.Converter_Corrente_Arbitraria(self.ui.Corrente_Arbitraria_GPIB.toPlainText(),1)
            if dados_corrente == False:
                return
            
            if len(dados_corrente)>1:
                lib.FileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File - Coleta Automática Corrente GPIB', nome,'Data files')
                self.ui.groupBox_2.setEnabled(False)
                self.ui.Nome_Ima.setEnabled(False)
                self.ui.observacao.setEnabled(False)
                self.ui.tempLine.setEnabled(False)
            self.ui.coletar.setEnabled(False)
            
            for i in range(len(dados_corrente)):
                final = dados_corrente[i]
                atual = float(lib.GPIB.Coleta_Multimetro())
                time.sleep(.2)
                envio_corrente = self.Rampa_Corretora(final,atual,0.1,0.35)
                
                if envio_corrente == False:
                    QtGui.QMessageBox.warning(self,'Atenção.','Falha no Envio da Corrente.\nTente Novamente.',QtGui.QMessageBox.Ok)
                    lib.GPIB.Saida_Gerador(0)
                    return
                time.sleep(2)
                self.Correcao_Posicao()
                Verificar = ColetaDados(len(dados_corrente))
                if Verificar == False:
                    QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Processo de Medição Interrompido. Desvio Padrão Elevado.',QtGui.QMessageBox.Ok)
                    ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Desvio Padrão Elevado.\nDeseja Salvar a Medida?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                    if ret == QtGui.QMessageBox.Yes:
                        pass
                    else:
                        ret = QtGui.QMessageBox.question(self,'Desvio Padrão.','Deseja continuar o Processo de Medição?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
                        if ret == QtGui.QMessageBox.Yes:
                            continue
                        else:
                            lib.Janela.ui.groupBox_2.setEnabled(True)
                            lib.Janela.ui.coletar.setEnabled(True)
                            self.ui.observacao.setEnabled(True)
                            self.ui.Nome_Ima.setEnabled(True)
                            self.ui.tempLine.setEnabled(True)
                            QtGui.QApplication.processEvents()
                            return
                time.sleep(1)
                if len(dados_corrente)>1:
                    self.Salvar_Coletas(1,(i+1),dados_corrente[i])
                self.ui.label_138.setText(str(i+1))
                QtGui.QApplication.processEvents()  #Atualizar tela

            lib.GPIB.Saida_Gerador(0)
            if len(dados_corrente)>1 :
                QtGui.QMessageBox.information(lib.Janela,'Atenção.','Processo de Coleta Automática Concluído.',QtGui.QMessageBox.Ok)
            self.ui.groupBox_2.setEnabled(True)
            self.ui.coletar.setEnabled(True)
            self.ui.observacao.setEnabled(True)
            self.ui.Nome_Ima.setEnabled(True)
            self.ui.tempLine.setEnabled(True)


    ########### ABA 10: Resultados ###########

    def Salvar_Coletas(self,Auto=0,Coleta=1,corrente=0):
        
        if Auto == 0:
            nome = str(self.ui.Nome_Ima.text())
            nome = nome.upper()
            arquivo = QtGui.QFileDialog.getSaveFileName(self, 'Save File - Coleta Manual', nome,'Data files')
            if (lib.Janela.ui.tabWidget.isTabEnabled(3) == True):
                Corrente_Principal = int(round(float(lib.Corrente_Atual),0))
            else:
                Corrente_Principal = 0
            self.SALVAR_DADOS_FINAIS(arquivo,Coleta,Corrente_Principal)
##                arquivo_salvar = QtGui.QFileDialog.getSaveFileName(self, 'Save File - Coleta Manual', nome)
##                arquivo = arquivo_salvar + '_FAC.dat'
##                self.SALVAR_HARMONICO_FAC(arquivo,Coleta)
##                arquivo = arquivo_salvar + '_IMA.dat'
##                self.SALVAR_HARMONICO_IMA(arquivo,Coleta)
        else:
            arquivo = lib.FileName
            self.SALVAR_DADOS_FINAIS(arquivo,Coleta,corrente)
##                arquivo_salvar = lib.FileName + '_Medida_' + str(Coleta)
##                arquivo = arquivo_salvar + '_FAC.dat'
##                self.SALVAR_HARMONICO_FAC(arquivo,Coleta)
##                arquivo = arquivo_salvar + '_IMA.dat'
##                self.SALVAR_HARMONICO_IMA(arquivo,Coleta)


##    def SALVAR_DADOS_FINAIS(self,arquivo,Coleta,Corrente_Principal):
##            ## Variaveis
##            iNumeroColetas = len(lib.F)
##            TipoIma = lib.Janela.ui.TipoIma.currentIndex()
##            if TipoIma == 0:
##                bob_excit = 'X'
##            if TipoIma == 1:
##                bob_excit = 'D'
##            if TipoIma == 2:
##                bob_excit = 'Q'
##            if TipoIma == 3:
##                bob_excit = 'S'
##            if TipoIma == 4:
##                bob_excit = 'K'
##
##            imabobina = lib.Janela.ui.ima_bobina.currentIndex()     #ACRESCENTADO#
##            if imabobina == 0: # Booster
##                sigla = 'BOB'
##            if imabobina == 1: #Anel
##                sigla = 'BOA'
##
##            dado_corrente = int(round(Corrente_Principal,0))
##            Corrente_Principal = str('{0:+d}'.format(dado_corrente))
##            
##            nome_bobina = str(self.ui.BobinaNome.text())
##            Ne = str(self.ui.nespiras.text())
##            Neb = str(self.ui.nespirasb.text())
##            r1 = str(self.ui.raio1.text())
##            r2 = str(self.ui.raio2.text())
##            r1b = str(self.ui.raio1b.text())
##            r2b = str(self.ui.raio2b.text())
##            pulsos_trigger = str(self.ui.pulsos_trigger.text())
##            volta_descarte_inicial = int(self.ui.descarte_inicial.text())
##            volta_descarte_final = int(self.ui.descarte_final.text())
##            temperature = self.ui.tempLine.text()                  #ACRESCENTADO#
##
##            if lib.sentido == 0:
##                sentido = 'Horario'
##            if lib.sentido == 1:
##                sentido = 'Antihorario'
##            
##            if lib.Tipo_Bobina == 0:    ## Tipo = 0 (Radial) Tipo = 1 (Tangencial)
##                bobina = 'Bobina Radial'
##            if lib.Tipo_Bobina == 1:
##                bobina = 'Bobina Tangencial'
##            
##            if lib.Bucked:
##                tipo_medicao = 'Bucked'
##            else:
##                tipo_medicao = 'N_Bucked'
##                
##            Corrente_2 = 0
##            
##            obs = str(self.ui.observacao.toPlainText())
##            obs = obs.strip()
##            obs = obs.replace('\n',' ')
##            obs = obs.replace('\t',' ')    
##
##            data = time.strftime("%d/%m/%Y", time.localtime())
##            data_nome = time.strftime("%y%m%d", time.localtime())
##            hora = time.strftime("%H:%M:%S", time.localtime())
##            hora_nome = time.strftime("%H%M%S", time.localtime())
####            arquivo = QtGui.QFileDialog.getSaveFileName(self, 'Save File', nome,'Data files (*.dat);;Text files (*.txt)')
##            arquivo = str(arquivo) + '_' + str(bob_excit) + '_' + str(sigla) + '_' + str(Corrente_Principal).zfill(5) + 'A_' + str(data_nome) + '_' + str(hora_nome) + '.dat'
##                        
##            try:
##                f = open(arquivo,'w')
##                arquivo_nome = arquivo.replace('/','\\')
##            except:
##                return
##
##            # Novo Cabecalho depois da reuniao IMA/FAC
##            f.write('########## CURVA DE EXCITACAO - BOBINA GIRANTE ##########')
##            f.write('\n\n')
##            f.write('### Dados de Configuração ###')
##            f.write('\n')
##            f.write('arquivo                        \t' + str(arquivo_nome) + '\n')
##            f.write('data                           \t' + str(data) + '\n')
##            f.write('hora                           \t' + str(hora) + '\n')
##            f.write('temperatura_ima(C)             \t' + str(temperature) + '\n')
##            f.write('ganho_integrador               \t' + str(lib.ganho) + '\n')
##            f.write('nr_pontos_integracao           \t' + str(lib.pontos_integracao) + '\n')
##            f.write('velocidade(rps)                \t' + str(lib.velocidade) + '\n')
##            f.write('aceleracao(rps^2)              \t' + str(lib.aceleracao) + '\n')
##            f.write('nr_coletas                     \t' + str(Coleta) + '\n')
##            f.write('nr_voltas                      \t' + str(len(lib.pontos)) + '\n')   ## str(lib.voltas_offset + 2) + '\n')
##            f.write('intervalo_analise              \t' + str(volta_descarte_inicial) + '-' + str(((lib.voltas_offset+1)-(volta_descarte_final))) + '\n')
##            f.write('sentido_de_rotacao             \t' + str(sentido) + '\n')
##            f.write('corrente_alim_principal_avg(A) \t' + str('{0:+0.6e}'.format(numpy.mean(lib.LeituraCorrente.saida))) + '\n')
##            f.write('corrente_alim_principal_std(A) \t' + str('{0:+0.6e}'.format(numpy.std(lib.LeituraCorrente.saida))) + '\n')
##            if lib.Janela.ui.check_aux.isChecked():             #ACRESCENTADO#
##                f.write('corrente_alim_secundaria_avg(A)\t' + str('{0:+0.6e}'.format(numpy.mean(lib.LeituraCorrente_Secundaria.saida))) + '\n')
##                f.write('corrente_alim_secundaria_std(A)\t' + str('{0:+0.6e}'.format(numpy.std(lib.LeituraCorrente_Secundaria.saida))) + '\n')
##            else:                                               
##                f.write('corrente_alim_secundaria_avg(A)\t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
##                f.write('corrente_alim_secundaria_std(A)\t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
##            f.write('\n')
##            f.write('### Dados da Bobina Girante ###')
##            f.write('\n')
##            f.write('nome_bobina_girante            \t' + str(nome_bobina) + '\n')
##            f.write('tipo_bobina_girante            \t' + str(bobina) + '\n')
##            f.write('tipo_medicao                   \t' + str(tipo_medicao) + '\n') ## bucked ou n_bucked
##            f.write('pulso_start_coleta             \t' + str(pulsos_trigger) + '\n')
##            f.write('n_espiras_bobina_principal     \t' + str(Ne) + '\n')
##            f.write('raio_interno_bobina_princip(m) \t' + str(r1) + '\n')
##            f.write('raio_externo_bobina_princip(m) \t' + str(r2) + '\n')
##            f.write('n_espiras_bobina_bucked        \t' + str(Neb) + '\n')
##            f.write('raio_interno_bobina_bucked(m)  \t' + str(r1b) + '\n')
##            f.write('raio_externo_bobina_bucked(m)  \t' + str(r2b) + '\n')
##            f.write('\n')
##            f.write('### Observações ###')
##            f.write('\n')
##            f.write('observacoes                    \t' + str(obs) + '\n')
##            f.write('\n\n\n')
##
##            f.write('##### Dados de Leitura #####')
##            f.write('\n\n')
####            f.write("n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\tstd_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\tavg_angulo(rad)  \tstd_angulo(rad)  \tavg_L.Nn'(T/m^n-2)\tstd_L.Nn'(T/m^n-2)\tavg_L.Sn'(T/m^n-2)\tstd_L.Sn'(T/m^n-2)\n")
####            f.write("n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\tstd_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\tavg_angulo(rad)  \tstd_angulo(rad)  \tavg_Nn/NnIma@17.5mm\tstd_Nn/NnIma@17.5mm\tavg_Sn/NnIma@17.5mm\tstd_Sn/NnIma@17.5mm\n")
##            f.write("n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\tstd_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\tavg_angulo(rad)  \tstd_angulo(rad)  \tavg_Nn/NnIma@"+str((lib.raio_referencia)*1000)+"mm"+"\tstd_Nn/NnIma@"+str((lib.raio_referencia)*1000)+"mm"+"\tavg_Sn/NnIma@"+str((lib.raio_referencia)*1000)+"mm"+"\tstd_Sn/NnIma@"+str((lib.raio_referencia)*1000)+"mm"+"\n")
##            
##            
##            if len(lib.F[0])>16:
##                Nfinal = 16
##            else:
##                Nfinal = 8
##                
##            if iNumeroColetas >= 1:
##                for i in range(1,Nfinal,1):
##                    f.write(str('{0:<4d}'.format(i)) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(lib.Nn[i])) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvNn[i]))) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(lib.Sn[i])) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvSn[i]))) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(lib.SMod[i])) + '\t')    
##                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesv[i]))) + '\t')
##                    if i == TipoIma or TipoIma == 0:
##                        f.write(str('{0:^+18.6e}'.format(lib.Angulo[i])) + '\t')
##                    else:
##                        f.write(str('{0:^+18.6e}'.format(0.0)) + '\t')
##                    if i == TipoIma or TipoIma == 0:
##                        f.write(str('{0:^+18.6e}'.format(lib.Desv_angulo[i])) + '\t')
##                    else:
##                        f.write(str('{0:^+18.6e}'.format(0.0)) + '\t')    
##                    f.write(str('{0:^+18.6e}'.format(lib.Nnl[i])) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvNnl[i]))) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(lib.Snl[i])) + '\t')
##                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvSnl[i]))) + '\n')
##
##            f.write('\n\n')
##            f.write('##### Dados Brutos Armazenados(V.s) [1e-12] #####')
##            f.write('\n\n')
##
##            for i in range(len(lib.pontos)):
##                f.write('{:#^18}'.format(' Volta_' + str(i+1) + ''))
##                f.write('\t')
##            f.write('\n')
##
##            for i in range(len(lib.pontos[0])):
##                for j in range(len(lib.pontos)):
##                    f.write('{0:^+18.10e}'.format(lib.pontos[j][i]) + '\t')
##                f.write('\n')
##
##            if self.ui.Salvar_Angulo_Volta.isChecked():
##                f.write('\n\n\n')   ### Angulo por Volta.
##                f.write('.........Angulo Volta:.........\n\n')
##                for i in range(0,len(lib.pontos),1):
##                    f.write(str(lib.AngulosVoltas[TipoIma][i]) + '\n')
##
##            f.close()

    '''
    After FAC/IMA meeting (11/17/2016), some changes in formatting and presentation of the
    results header of excitation curve.
    Changes:
    - Language from Portuguese to English;
    - Date and Time format and position in File name;
    '''

    def SALVAR_DADOS_FINAIS(self,arquivo,Coleta,Corrente_Principal):
            ## Variable
            iNumeroColetas = len(lib.F)
            TipoIma = lib.Janela.ui.TipoIma.currentIndex()
            if TipoIma == 0:
                bob_excit = 'X'
            if TipoIma == 1:
                bob_excit = 'D'
            if TipoIma == 2:
                bob_excit = 'Q'
            if TipoIma == 3:
                bob_excit = 'S'
            if TipoIma == 4:
                bob_excit = 'K'

            imabobina = lib.Janela.ui.ima_bobina.currentIndex()     #ACRESCENTADO#
            if imabobina == 0: # Booster
                sigla = 'BOB'
            if imabobina == 1: #Anel
                sigla = 'BOA'

            dado_corrente = int(round(Corrente_Principal,0))
            Corrente_Principal = str('{0:+d}'.format(dado_corrente))
            
            nome_bobina = str(self.ui.BobinaNome.text())
            Ne = str(self.ui.nespiras.text())
            Neb = str(self.ui.nespirasb.text())
            r1 = str(self.ui.raio1.text())
            r2 = str(self.ui.raio2.text())
            r1b = str(self.ui.raio1b.text())
            r2b = str(self.ui.raio2b.text())
            pulsos_trigger = str(self.ui.pulsos_trigger.text())
            volta_descarte_inicial = int(self.ui.descarte_inicial.text())
            volta_descarte_final = int(self.ui.descarte_final.text())
            temperature = self.ui.tempLine.text()                  #ACRESCENTADO#
            TipoIma = lib.Janela.ui.TipoIma.currentIndex()

            if lib.sentido == 0:
                sentido = 'Clockwise'
            if lib.sentido == 1:
                sentido = 'Counterclockwise'
            
            if lib.Tipo_Bobina == 0:    ## Type = 0 (Radial) Type = 1 (Tangencial)
                bobina = 'Radial Coil'
            if lib.Tipo_Bobina == 1:
                bobina = 'Tangential Coil'
            
            if lib.Bucked:
                tipo_medicao = 'Bucked'
            else:
                tipo_medicao = 'N_Bucked'
                
            Corrente_2 = 0
            
            obs = str(self.ui.observacao.toPlainText())
            obs = obs.strip()
            obs = obs.replace('\n',' ')
            obs = obs.replace('\t',' ')    

            data = time.strftime("%d/%m/%Y", time.localtime())
            data_nome = time.strftime("%y%m%d", time.localtime())
##            data_nome = time.strftime("%Y-%m-%d", time.localtime())
            hora = time.strftime("%H:%M:%S", time.localtime())
            hora_nome = time.strftime("%H%M%S", time.localtime())
##            hora_nome = time.strftime("%H-%M-%S", time.localtime())
##            arquivo = QtGui.QFileDialog.getSaveFileName(self, 'Save File', nome,'Data files (*.dat);;Text files (*.txt)')
            arquivo = str(arquivo) + '_' + str(bob_excit) + '_' + str(sigla) + '_' + str(Corrente_Principal).zfill(5) + 'A_' + str(data_nome) + '_' + str(hora_nome) + '.dat'

            
##            arquivo = str(arquivo)+ '_' +str(data_nome) + '_' + str(hora_nome) + '_' + str(bob_excit) + '_' + str(sigla) + '_' + str(Corrente_Principal).zfill(5) + 'A_' + '.dat'

##            arquivo = str(arquivo)+ '_' + str(hora_nome) + '_' + str(bob_excit) + '_' + str(Corrente_Principal).zfill(5) + 'A_' + '.dat'
##            print(arquivo)
                        
            try:
                f = open(arquivo,'w')
                arquivo_nome = arquivo.replace('/','\\')
            except:
                return

            # New header after IMA/FAC meeting - english version (11/17/2016)
            f.write('########## EXCITATION CURVE - ROTATING COIL ##########')
            f.write('\n\n')
            f.write('### Configuration Data ###')
            f.write('\n')
            f.write('file                           \t' + str(arquivo_nome) + '\n')
            f.write('date                           \t' + str(data) + '\n')
            f.write('hour                           \t' + str(hora) + '\n')
            f.write('temperature(ºC)                \t' + str(temperature) + '\n')
            f.write('integrator_gain                \t' + str(lib.ganho) + '\n')
            f.write('nr_integration_points          \t' + str(lib.pontos_integracao) + '\n')
            f.write('velocity(rps)                  \t' + str(lib.velocidade) + '\n')
            f.write('acceleration(rps^2)            \t' + str(lib.aceleracao) + '\n')
            f.write('nr_collections                 \t' + str(Coleta) + '\n')
            f.write('nr_turns                       \t' + str(len(lib.pontos)) + '\n')   ## str(lib.voltas_offset + 2) + '\n')
            f.write('analysis_interval              \t' + str(volta_descarte_inicial) + '-' + str(((lib.voltas_offset+1)-(volta_descarte_final))) + '\n')
            f.write('rotation                       \t' + str(sentido) + '\n')
            f.write('main_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(lib.LeituraCorrente.saida))) + '\n')
            f.write('main_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(lib.LeituraCorrente.saida))) + '\n')

            if imabobina == 1 and lib.Janela.ui.check_aux.isChecked() and TipoIma == 3:             #PARA SEXTYPOLO DO ANEL S15#
                if lib.Janela.ui.check_chCoil.isChecked():              #CH Coil
                    f.write('ch_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(lib.LeituraCorrente_Secundaria.saida))) + '\n')
                    f.write('ch_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(lib.LeituraCorrente_Secundaria.saida))) + '\n')
                    f.write('cv_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                    f.write('cv_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
                    f.write('qs_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                    f.write('qs_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')

                if lib.Janela.ui.check_cvCoil.isChecked():              #CV Coil
                    f.write('ch_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                    f.write('ch_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
                    f.write('cv_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(lib.LeituraCorrente_Secundaria.saida))) + '\n')
                    f.write('cv_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(lib.LeituraCorrente_Secundaria.saida))) + '\n')
                    f.write('qs_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                    f.write('qs_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')

                if lib.Janela.ui.check_qsCoil.isChecked():              #QS Coil
                    f.write('ch_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                    f.write('ch_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
                    f.write('cv_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                    f.write('cv_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
                    f.write('qs_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(lib.LeituraCorrente_Secundaria.saida))) + '\n')
                    f.write('qs_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(lib.LeituraCorrente_Secundaria.saida))) + '\n')
            elif imabobina == 1 and TipoIma == 3:
                f.write('ch_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                f.write('ch_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
                f.write('cv_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                f.write('cv_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
                f.write('qs_coil_current_avg(A)       \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                f.write('qs_coil_current_std(A)       \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
                           
            elif imabobina == 1 and lib.Janela.ui.check_aux.isChecked() and TipoIma == 2:             #PARA QUADRUPOLO DO ANEL Q14, Q20, Q30#
                f.write('trim_coil_current_avg(A)   \t' + str('{0:+0.6e}'.format(numpy.mean(lib.LeituraCorrente_Secundaria.saida))) + '\n')
                f.write('trim_coil_current_std(A)   \t' + str('{0:+0.6e}'.format(numpy.std(lib.LeituraCorrente_Secundaria.saida))) + '\n')
            else:                                               
                f.write('trim_coil_current_avg(A)   \t' + str('{0:+0.6e}'.format(numpy.mean(Corrente_2))) + '\n')
                f.write('trim_coil_current_std(A)   \t' + str('{0:+0.6e}'.format(numpy.std(Corrente_2))) + '\n')
            f.write('\n')
            f.write('### Rotating Coil Data ###')
            f.write('\n')
            f.write('rotating_coil_name             \t' + str(nome_bobina) + '\n')
            f.write('rotating_coil_type             \t' + str(bobina) + '\n')
            f.write('measurement_type               \t' + str(tipo_medicao) + '\n') ## bucked ou n_bucked
            f.write('pulse_start_collect            \t' + str(pulsos_trigger) + '\n')
            f.write('n_turns_main_coil              \t' + str(Ne) + '\n')
            f.write('main_coil_internal_radius(m)   \t' + str(r1) + '\n')
            f.write('main_coil_external_radius(m)   \t' + str(r2) + '\n')
            f.write('n_turns_bucked_coil            \t' + str(Neb) + '\n')
            f.write('bucked_coil_internal_radius(m) \t' + str(r1b) + '\n')
            f.write('bucked_coil_external_radius(m) \t' + str(r2b) + '\n')
            f.write('\n')
            f.write('### Comments ###')
            f.write('\n')
            f.write('comments                       \t' + str(obs) + '\n')
            f.write('\n\n\n')

            f.write('##### Reading Data #####')
            f.write('\n\n')
##            f.write("n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\tstd_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\tavg_angulo(rad)  \tstd_angulo(rad)  \tavg_L.Nn'(T/m^n-2)\tstd_L.Nn'(T/m^n-2)\tavg_L.Sn'(T/m^n-2)\tstd_L.Sn'(T/m^n-2)\n")
##            f.write("n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\tstd_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\tavg_angulo(rad)  \tstd_angulo(rad)  \tavg_Nn/NnIma@17.5mm\tstd_Nn/NnIma@17.5mm\tavg_Sn/NnIma@17.5mm\tstd_Sn/NnIma@17.5mm\n")
            f.write("n\tavg_L.Nn(T/m^n-2)\tstd_L.Nn(T/m^n-2)\tavg_L.Sn(T/m^n-2)\tstd_L.Sn(T/m^n-2)\tavg_L.Bn(T/m^n-2)\tstd_L.Bn(T/m^n-2)\tavg_angle(rad)  \tstd_angle(rad)  \tavg_Nn/NnMagnet@"+str((lib.raio_referencia)*1000)+"mm"+"\tstd_Nn/NnMagnet@"+str((lib.raio_referencia)*1000)+"mm"+"\tavg_Sn/NnMagnet@"+str((lib.raio_referencia)*1000)+"mm"+"\tstd_Sn/NnMagnet@"+str((lib.raio_referencia)*1000)+"mm"+"\n")
            
            
            if len(lib.F[0])>16:
                Nfinal = 16
            else:
                Nfinal = 8
                
            if iNumeroColetas >= 1:
                for i in range(1,Nfinal,1):
                    f.write(str('{0:<4d}'.format(i)) + '\t')
                    f.write(str('{0:^+18.6e}'.format(lib.Nn[i])) + '\t')
                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvNn[i]))) + '\t')
                    f.write(str('{0:^+18.6e}'.format(lib.Sn[i])) + '\t')
                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvSn[i]))) + '\t')
                    f.write(str('{0:^+18.6e}'.format(lib.SMod[i])) + '\t')    
                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesv[i]))) + '\t')
                    if i == TipoIma or TipoIma == 0:
                        f.write(str('{0:^+18.6e}'.format(lib.Angulo[i])) + '\t')
                    else:
                        f.write(str('{0:^+18.6e}'.format(0.0)) + '\t')
                    if i == TipoIma or TipoIma == 0:
                        f.write(str('{0:^+18.6e}'.format(lib.Desv_angulo[i])) + '\t')
                    else:
                        f.write(str('{0:^+18.6e}'.format(0.0)) + '\t')    
                    f.write(str('{0:^+18.6e}'.format(lib.Nnl[i])) + '\t')
                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvNnl[i]))) + '\t')
                    f.write(str('{0:^+18.6e}'.format(lib.Snl[i])) + '\t')
                    f.write(str('{0:^+18.6e}'.format(abs(lib.sDesvSnl[i]))) + '\n')

            f.write('\n\n')
            f.write('##### Raw Data Stored(V.s) [1e-12] #####')
            f.write('\n\n')

            for i in range(len(lib.pontos)):
                f.write('{:#^18}'.format(' Turn_' + str(i+1) + ''))
                f.write('\t')
            f.write('\n')

            for i in range(len(lib.pontos[0])):
                for j in range(len(lib.pontos)):
                    f.write('{0:^+18.10e}'.format(lib.pontos[j][i]) + '\t')
                f.write('\n')

            if self.ui.Salvar_Angulo_Volta.isChecked():
                f.write('\n\n\n')   ### Angulo por Volta.
                f.write('.........Turn Angle:.........\n\n')
                for i in range(0,len(lib.pontos),1):
                    f.write(str(lib.AngulosVoltas[TipoIma][i]) + '\n')

            f.close()        

            
    def SALVAR_HARMONICO_FAC(self,arquivo,Coleta):
            data = time.strftime("%d/%m/%Y", time.localtime())
            hora = time.strftime("%H:%M:%S", time.localtime())
            arquivo_nome = arquivo.replace('/','\\')
##            arquivo = QtGui.QFileDialog.getSaveFileName(self, 'Save File', nome,'Data files (*.dat);;Text files (*.txt)')

            try:
                f = open(arquivo,'w')
            except:
                return

            iNumeroColetas = len(lib.F)
            TipoIma = lib.Janela.ui.TipoIma.currentIndex()
            nome_bobina = str(self.ui.BobinaNome.text())
            obs = str(self.ui.observacao.toPlainText())
            obs = obs.strip()
            obs = obs.replace('\n',' ')
            obs = obs.replace('\t',' ')            

            # Cabecalho do arquivo - Sugestão FAC(Ximenes)
            f.write('### CURVA DE EXCITACAO - BOBINA GIRANTE: ' + str(nome_bobina) + ' ###\n')
            f.write('\n')
            f.write('### Dados de Configuração ###\n')
            f.write('\n')
            f.write('arquivo                      ' + str(arquivo_nome) + '\n')
            f.write('data                         ' + str(data) + '\n')
            f.write('hora                         ' + str(hora) + '\n')
            f.write('temperatura(C)               ' + str(0) + '\n')
            f.write('ganho                        ' + str(lib.ganho) + '\n')
            f.write('nr_pontos_integracao         ' + str(lib.pontos_integracao) + '\n')
            f.write('velocidade(rps)              ' + str(lib.velocidade) + '\n')
            f.write('aceleracao(rps^2)            ' + str(lib.aceleracao) + '\n')
            f.write('nr_coletas                   ' + str(Coleta) + '\n')
            f.write('nr_voltas                    ' + str(lib.voltas_offset + 2) + '\n')
            f.write('intervalo_analise            ' + str(2) + '-' + str(lib.voltas_offset + 1) + '\n')
            f.write('sentido_de_rotacao           ' + str(lib.sentido) + '\n')
            f.write('corrente_alimentacao_avg(A)  ' + str('{0:0.5e}'.format(numpy.mean(lib.LeituraCorrente.saida))) + '\n')
            f.write('corrente_alimentacao_std(A)  ' + str('{0:0.5e}'.format(numpy.std(lib.LeituraCorrente.saida))) + '\n')
            f.write('observacoes                  ' + str(obs) + '\n')
            f.write('\n\n\n')
            
            f.write('### Dados de Leitura ###\n')
            f.write('\n')
            f.write("n   avg_L.Nn(T/m^n-2)   avg_L.Sn(T/m^n-2)   avg_L.Bn(T/m^n-2)   std_L.Nn(T/m^n-2)   std_L.Sn(T/m^n-2)   std_L.Bn(T/m^n-2)   avg_angulo(rad)     avg_L.Nn'(T/m^n-2)  avg_L.Sn'(T/m^n-2)\n") 
       
            
            if len(lib.F[0])>16:
                Nfinal = 16
            else:
                Nfinal = 8
                
            if iNumeroColetas >= 1:
                for i in range(1,Nfinal,1):
                    f.write('{0:<4d}'.format(i))
                    f.write('{0:<+20.5e}'.format(lib.Nn[i]))
                    f.write('{0:<+20.5e}'.format(lib.Sn[i]))
                    f.write('{0:<+20.5e}'.format(lib.SMod[i]))
                    f.write('{0:<+20.5e}'.format(abs(lib.sDesvNn[i])))
                    f.write('{0:<+20.5e}'.format(abs(lib.sDesvSn[i])))
                    f.write('{0:<+20.5e}'.format(abs(lib.sDesv[i])))
                
                    if i == TipoIma or TipoIma == 0:
                        f.write('{0:<+20.5e}'.format(lib.Angulo[i]))
                    else:
                        f.write('{0:<+20.5e}'.format(0.0))
                    f.write('{0:<+20.5e}'.format(lib.Nnl[i]))
                    f.write('{0:<+20.5e}'.format(lib.Snl[i]))
                    f.write('\n')
            
            f.write('\n\n\n')
            f.write('### Dados Armazenados ###\n')
            f.write('\n')
            for i in range(len(lib.pontos[0])):
                for j in range(len(lib.pontos)):
                    f.write('{0:<+17.8e}'.format(lib.pontos[j][i]))
                f.write('\n')            
            f.close()

    def SALVAR_HARMONICO_IMA(self,arquivo,Coleta):
            data = time.strftime("%d/%m/%Y", time.localtime())
            hora = time.strftime("%H:%M:%S", time.localtime())
            arquivo_nome = arquivo.replace('/','\\')
##            arquivo = QtGui.QFileDialog.getSaveFileName(self, 'Save File', nome,'Data files (*.dat);;Text files (*.txt)')

            try:
                f = open(arquivo,'w')
            except:
                return

            iNumeroColetas = len(lib.F)
            TipoIma = lib.Janela.ui.TipoIma.currentIndex()
            nome_bobina = str(self.ui.BobinaNome.text())
            obs = str(self.ui.observacao.toPlainText())
            obs = obs.strip()
            obs = obs.replace('\n',' ')
            obs = obs.replace('\t',' ')
                        
            # Cabecalho do arquivo (Original)
            f.write('\nCurva de Excitação - Bobina Girante: ' + str(nome_bobina) + '\n\n')
            f.write('.........Dados de Configuração.........\n')
            f.write('Arquivo................: ' + str(arquivo_nome) + '\n')
            f.write('Data...................: ' + str(data) + '\n')
            f.write('Hora...................: ' + str(hora) + '\n')
            f.write('Temperatura(C).........: ' + str(0) + '\n')
            f.write('Ganho..................: ' + str(lib.ganho) + '\n')
            f.write('N. Pontos Integração...: ' + str(lib.pontos_integracao) + '\n')
            f.write('Velocidade.............: ' + str(lib.velocidade) + '\n')
            f.write('Aceleracao.............: ' + str(lib.aceleracao) + '\n')
            f.write('N. de Coletas..........: ' + str(Coleta) + '\n')
            f.write('N. de Voltas...........: ' + str(lib.voltas_offset + 2) + '\n')
            f.write('Intervalo de Análise...: ' + str(2) + '-' + str(lib.voltas_offset + 1) + '\n')
            f.write('Sentido de rotação.....: ' + str(lib.sentido) + '\n')
##            f.write('Deslocamento em Y(mm)..: ' + str(lib.deslY) + '\n')
            f.write('Corrente Alimentação(A): ' + str('{0:0.5e}'.format(numpy.mean(lib.LeituraCorrente.saida))) + ' Erro(S): ' + str('{0:0.5e}'.format(numpy.std(lib.LeituraCorrente.saida))) + '\n')
            f.write('Observações............: ' + str(obs) + '\n\n\n\n\n')
            
            f.write('.........Dados de Leitura.........\n')
            f.write("N\tL.Nn     \tL.Sn     \tL.Bn(T/m^n-2)\tEr_Nn(T/m^n-2)\tEr_Sn(T/m^n-2)\tErro(T/m^n-2)\tÂngulo(rad)\tL.Nn'   \tL.Sn'\n\n")
            
            if len(lib.F[0])>16:
                Nfinal = 16
            else:
                Nfinal = 8
                
            if iNumeroColetas >= 1:
                for i in range(1,Nfinal,1):
                    f.write(str(i) + '\t')
                    f.write(str('{0:0.5e}'.format(lib.Nn[i])) + '\t')
                    f.write(str('{0:0.5e}'.format(lib.Sn[i])) + '\t')
                    f.write(str('{0:0.5e}'.format(lib.SMod[i])) + '\t')
                    f.write(str('{0:0.5e}'.format(abs(lib.sDesvNn[i]))) + '\t')
                    f.write(str('{0:0.5e}'.format(abs(lib.sDesvSn[i]))) + '\t')
                    f.write(str('{0:0.5e}'.format(abs(lib.sDesv[i]))) + '\t')
                    if i == TipoIma or TipoIma == 0:
                        f.write(str('{0:0.5e}'.format(lib.Angulo[i])) + '\t')
                    else:
                        f.write(str('      000.00') + '\t')                       
                    f.write(str('{0:0.5e}'.format(lib.Nnl[i])) + '\t')
                    f.write(str('{0:0.5e}'.format(lib.Snl[i])) + '\n')
            
            f.write('\n\n\n')
            f.write('.........Dados Armazenados:.........\n\n')
##            f.write('Brutos  \t\tMédios\n\n')                 #Cabeçalho de Dados Brutos e Dados Médios
            f.write('Brutos\n\n')                               #Cabeçalho de Dados Brutos

            for i in range(len(lib.pontos)):
                for j in range(len(lib.pontos[i])):
##                    if i == 0:
##                        f.write(str(lib.pontos[i][j]) + ' \t\t' + str(lib.media[j]) + '\n')       #Rotina para salvar dados brutos e médios
##                    else:
                        f.write(str(lib.pontos[i][j]) + '\n')
                f.write('\n')

            f.write('\n\n\n')
            f.write('.........Angulo Volta:.........\n\n')
            for i in range(0,len(lib.pontos),1):
                f.write(str(lib.AngulosVoltas[TipoIma][i]) + '\n')
            
            f.close()
##        else:
##            QtGui.QMessageBox.critical(self,'Erro.','Dados inexistentas.',QtGui.QMessageBox.Ok)

            


    def PlotFunc1(self,x,y):
        self.ui.widget.canvas.ax1.clear()
        self.ui.widget.canvas.ax1.plot(x,y)
        self.ui.widget.canvas.ax1.set_xlabel('Volta')
        self.ui.widget.canvas.ax1.set_ylabel('Amplitude (V.s)')
        self.ui.widget.canvas.fig.tight_layout()
        self.ui.widget.canvas.draw()

    def PlotFunc2(self,x,y):
        self.ui.widget.canvas.ax2.clear()
        self.ui.widget.canvas.ax2.plot(x,y)
##        self.ui.widget.canvas.ax.set_xlabel('Frequência')
##        self.ui.widget.canvas.ax.set_ylabel('Amplitude')
        self.ui.widget.canvas.draw()

    def PlotFunc3(self,x,y):
        self.ui.widget.canvas.ax2.clear()
        for i in range(len(y)):
            if i % 2 == 0:
                self.ui.widget.canvas.ax2.plot(x[i*lib.pontos_integracao:(i+1)*lib.pontos_integracao],y[i],'b')
            else:
                self.ui.widget.canvas.ax2.plot(x[i*lib.pontos_integracao:(i+1)*lib.pontos_integracao],y[i],'r')
        self.ui.widget.canvas.ax2.set_xlabel('Voltas')
        self.ui.widget.canvas.ax2.set_ylabel('Amplitude (V.s)')
        self.ui.widget.canvas.fig.tight_layout()
        self.ui.widget.canvas.draw()

    def Converter_Corrente_Arbitraria(self,Campo,index):
        x= str(Campo)
        x=x.strip('\n')
        x=x.replace("\n",";").split(";")
        for i in range(len(x)):
            try:
                if index == 2:
                    x[i] = str(x[i])
                else:
                    x[i]=float(x[i])
            except:
                if index == 0:
                    QtGui.QMessageBox.warning(self,'Atenção.','Dados da Corrente da Fonte Não Numéricos ou existência de espaço.\n Utilizar ponto para decimal.',QtGui.QMessageBox.Ok)
                if index == 1:
                    QtGui.QMessageBox.warning(self,'Atenção.','Dados da Corrente GPIB Não Numéricos ou existência de espaço.\n Utilizar ponto para decimal.',QtGui.QMessageBox.Ok)
                if index == 2:
                    QtGui.QMessageBox.warning(self,'Atenção.','Dados da Seleção de Correntes Incorretos.\n Utilizar [Y/N].',QtGui.QMessageBox.Ok)
                return False
        return x

    def Recuperar_Valor(self,index,dados):
        x = dados.strip('[')
        x = x.strip(']')
        if index == 0:
            x = x.split(', ')
            for i in range(len(x)):
                if i== 0:
                    Valor = str(x[i])
                else:
                    Valor = Valor + ('\n'+str(x[i]))
        if index == 1:
            x = x.split(', ')
            for i in range(len(x)):
                x[i]=float(x[i])
            x = numpy.asarray(x)
            Valor = x
        return Valor


def dec_bin(Num,bit):
    valor = bin(Num)
    valor = list(valor)
    valor.pop(0)
    valor.pop(0)
    final=['0']
    if (len(valor))<8:
        for i in range(len(valor),8,1):
            valor = final + valor
    for i in range(0,8,1):
        valor[i] = int(valor[i])
    valor = valor[::-1]
    return valor[bit]


def ColetaDados(Repeticao):
    coleta = False
    i=0
    while coleta == False and lib.parartudo == 0:
        if i==3:
            return False
        lib.pontos_recebidos = ColetaDados_Leitura(Repeticao)
        if not lib.pontos_recebidos == [] and not lib.parartudo:
            coleta = ColetaDados_Calculos(Repeticao)
        if coleta == True:
            return True
        else:
            i+=1        
    
# Recebe os dados coletados pelo Integrador
def ColetaDados_Leitura(Repeticao):
    if lib.Janela.ui.Hab_Corretora.isChecked() or lib.Janela.ui.cb_DCCT.isChecked():                
        lib.LeituraCorrente = leitura_corrente_multimetro(lib.voltas_offset,lib.velocidade)
        if lib.controle_fonte == 1 and lib.Janela.ui.check_aux.isChecked():
            lib.LeituraCorrente_Secundaria = leitura_corrente_sec_mult(lib.voltas_offset,lib.velocidade)        #ACRESCENTADO#

        if lib.controle_fonte == 1 and lib.Janela.ui.check_aux.isChecked() and lib.Janela.ui.check_TrimCoil.isChecked():
            lib.LeituraCorrente_Secundaria = leitura_corrente_sec_Multicanal(lib.voltas_offset,lib.velocidade)        #ACRESCENTADO#
    else:
        lib.LeituraCorrente = leitura_corrente_puc(lib.voltas_offset,lib.velocidade)
##        lib.LeituraCorrente_Secundaria = leitura_corrente_puc(lib.voltas_offset,lib.velocidade)
        
    lib.integrador.Enviar('ISC,A,0')
    lib.integrador.Enviar(lib.integrador.PDIIniciaColeta)               # inicia a coleta de dados
    voltas = lib.voltas_offset + 2                                      
    lib.motor.SetResolucao(lib.endereco,lib.passos_volta)
    lib.motor.ConfMotor(lib.endereco,lib.velocidade,lib.aceleracao,lib.passos_volta*voltas)
##    sentido = lib.Janela.ui.sentido_2.currentIndex()
##    if sentido == 0:
##        lib.sentido = 'Horario'
##    else:
##        lib.sentido = 'Antihorario'
    lib.motor.ConfModo(lib.endereco,0,lib.sentido)
    lib.motor.MoverMotor(lib.endereco)
    while (not lib.motor.ready(lib.endereco)) and lib.parartudo == 0:
        QtGui.QApplication.processEvents()
    
    bitstatus = 0
    while (bitstatus != 1) and lib.parartudo == 0:
        QtGui.QApplication.processEvents()
        status = lib.integrador.Status('1')
        try:
            bitstatus = int(status[-3])
        except:
            pass
    statusintegrador = lib.Janela.Status_Integrador(4,0)
    
    valor = ''
    status = -1
    lib.integrador.LimpaTxRx()
    time.sleep(0.1)
    lib.integrador.Enviar('ENQ')
    time.sleep(0.2)
    while (status == -1) and not lib.parartudo:
        QtGui.QApplication.processEvents()
        tmp = lib.integrador.ser.readall()
        tmp = tmp.decode('utf-8')
        valor = valor + tmp
        status = tmp.find('\x1a')
    
    valor = valor.strip(' A\r\n\x1a')
    pontos = valor.split(' A\r\n')
    lib.integrador.Enviar('ISC,A,1')
    try:
        for i in range(len(pontos)):
            pontos[i] = int(pontos[i])
    except:
        if statusintegrador == 0:
            Historico_Falhas(0)
        else:
            Historico_Falhas(2)     ## Troca automatica do ganho para over-range na leitura.
            index = int(lib.Janela.ui.ganho.currentIndex())
            index-=1
            if index < 0:
                QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Valor Superior ao Menor Ganho.\nVerifique parametros e equipamentos.',QtGui.QMessageBox.Ok)
                return
            else:
                lib.Janela.ui.ganho.setCurrentIndex(index)
                QtGui.QApplication.processEvents()
                lib.Janela.CONFIGURARINTEGRADOR(1)
                time.sleep(1)                
        return ColetaDados_Leitura(Repeticao)
        
    if lib.parartudo == 1:
        lib.Janela.ui.groupBox_2.setEnabled(True)
        lib.Janela.ui.coletar.setEnabled(True)
    return pontos


def ColetaDados_Calculos(Repeticao):
    ### Variaveis Principais
    pontos = lib.pontos_recebidos
    lib.Bucked = lib.Janela.ui.Bucked.isChecked()
    Ne = int(lib.Janela.ui.nespiras.text())
    Neb = int(lib.Janela.ui.nespirasb.text())
    r1 = float(lib.Janela.ui.raio1.text())
    r2 = float(lib.Janela.ui.raio2.text())
    r1b = float(lib.Janela.ui.raio1b.text())
    r2b = float(lib.Janela.ui.raio2b.text())
    TipoIma = lib.Janela.ui.TipoIma.currentIndex()
    volta_filtro = int(lib.Janela.ui.filtro_voltas.text())
    aux = []
    
    ### Organiza dados para cálculos
    for i in range(int(lib.voltas_offset)):
        aux.append(pontos[i*lib.pontos_integracao:(i+1)*lib.pontos_integracao])
        if lib.parartudo == 1:
            lib.Janela.ui.groupBox_2.setEnabled(True)
            lib.Janela.ui.coletar.setEnabled(True)

############ Filtro Voltas Iniciais e Finais ############
    for i in range(int(lib.Janela.ui.descarte_inicial.text())):
        aux.pop(0)  ### despreza voltas de aceleração
    for i in range(int(lib.Janela.ui.descarte_final.text())):
        aux.pop(len(aux)-1) ### despreza voltas de desaceleração
        
#########################################################
    
    lib.pontos = aux
    dados = numpy.array(aux)*10**(-12)  ##Converte dados.

############### Filtro Erro de Transmissão ###############
    volta_total = len(dados)
    filtro = len(dados)-1
    while (volta_total > filtro):
        
        try:
            dados_std = numpy.std(dados,axis=0) # redefines std values
        except:
            file = open('Erro_Filtro_Transmissao.dat','w')  ##### salvar dados com erro.
            for i in range(len(dados)):
                for j in range(len(dados[0])):
                    file.write('{0:^+18.10e}'.format(dados[i][j]) + '\n')
                file.write('\n')
            file.close()                                    #####
            return
        
        locsj = numpy.argmax(dados_std) # searches for max std
        avg_std = numpy.mean(dados_std) #average of rms values
        locsi = numpy.argmax(abs(numpy.mean(dados[::,locsj])-dados[::,locsj])) #searches in which column is the max values
        dados = numpy.delete(dados,locsi,0) #deletes the data set with max std
        lib.pontos = numpy.delete(lib.pontos,locsi,0)
        volta_total = volta_total-1
############### Filtro Erro de Transmissão ###############


##### Dados finais apos filtro de erro de leitura #####
    fourier = numpy.zeros(len(dados)).tolist()
    for i in range(len(dados)):
        fourier[i] = (numpy.fft.fft(dados[i]))/(len(dados[i])/2)
    lib.F = numpy.array(fourier)                              # F contem as transformadas de fourier de cada volta
#######################################################

    if len(lib.F[0])>16:
        nmax = 21
    else:
        nmax = 9

################################################ CALCULO MULTIPOLOS BOBINA RADIAL #######################################################################################
    if lib.Tipo_Bobina == 0: ## Tipo = 0 (Radial) Tipo = 1 (Tangencial)
        
    ##### Filtro de leituras pela maior variacao em relaçao a media do angulo #####
        AnguloVolta = []
        iNumeroColetas = len(lib.F)
        dtheta = 2*numpy.pi/(len(lib.F[0]))
        if TipoIma != 0:
            volta_total = len(lib.F)
            while volta_total > volta_filtro:
                AnguloVolta = numpy.zeros(len(lib.F))
                for i in range(len(lib.F)):
                    n = TipoIma
                    if lib.Bucked:
                        R = Ne*(r2**n-r1**n)-Neb*(r2b**n-r1b**n)
                    else:
                        R = Ne*(r2**n-r1**n)

                    An = lib.F[i][n].real
                    Bn = -lib.F[i][n].imag
                    Jn = (An*numpy.sin(n*dtheta)+Bn*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))
                    Kn = (Bn*numpy.sin(n*dtheta)-An*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))

                    AnguloVolta[i] = (1/TipoIma)*numpy.arctan(Jn/Kn)
                   
                maior = numpy.argmax(abs(numpy.mean(AnguloVolta) - AnguloVolta),0)
                AnguloVolta = numpy.delete(AnguloVolta,maior,0)
                lib.F = numpy.delete(lib.F,maior,0)
                dados = numpy.delete(dados,maior,0)
                lib.pontos = numpy.delete(lib.pontos,maior,0)
                volta_total-=1
    ###############################################################################
                
        iNumeroColetas = len(lib.F)
        dtheta = 2*numpy.pi/(len(lib.F[0]))
        lib.AngulosVoltas = numpy.zeros(len(lib.F)*21).reshape(21,len(lib.F))
        lib.SJN = numpy.zeros(21)
        lib.SKN = numpy.zeros(21)
        lib.SNn = numpy.zeros(21)
        lib.SNn2 = numpy.zeros(21)
        lib.SSJN2 = numpy.zeros(21)
        lib.SSKN2 = numpy.zeros(21)
        lib.SdbdXN = numpy.zeros(21)
        lib.SdbdXN2 = numpy.zeros(21)
        for i in range(len(lib.F)):
            for n in range(1,nmax,1):
                if lib.Bucked and n==TipoIma:
                    n+=1
                    continue
                if lib.Bucked:
                    R = Ne*(r2**n-r1**n)-Neb*(r2b**n-r1b**n)
                else:
                    R = Ne*(r2**n-r1**n)
                An = lib.F[i][n].real
                Bn = -lib.F[i][n].imag
                Jn = (An*numpy.sin(n*dtheta)+Bn*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))
                Kn = (Bn*numpy.sin(n*dtheta)-An*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))
                dbdXN = n*(Jn**2+Kn**2)**(1/2)
                lib.SJN[n] = lib.SJN[n] + Jn
                lib.SKN[n] = lib.SKN[n] + Kn
                lib.SSJN2[n] = lib.SSJN2[n] + Jn**2
                lib.SSKN2[n] = lib.SSKN2[n] + Kn**2
                lib.SdbdXN[n] = lib.SdbdXN[n] + dbdXN
                lib.SdbdXN2[n] = lib.SdbdXN2[n] + dbdXN**2
                lib.AngulosVoltas[n][i] = (1/n)*numpy.arctan(Jn/Kn)

        lib.Angulo = numpy.mean(lib.AngulosVoltas,axis=1)   
        lib.Desv_angulo = numpy.std(lib.AngulosVoltas,axis=1)

    ##### Calculo Desvio Padrao das Medidas #####
        lib.sDesv = numpy.zeros(21)
        lib.sDesvSn = numpy.zeros(21)
        lib.sDesvNn = numpy.zeros(21)
        lib.Nn = numpy.zeros(21)
        lib.Sn = numpy.zeros(21)
        lib.SMod = numpy.zeros(21)
        for i in range(1,nmax,1):
            try:
                lib.sDesvSn[i] = ((((i**2)*lib.SSJN2[i]) - (i*lib.SJN[i])**2/iNumeroColetas)/(iNumeroColetas-1))**(1/2)
                lib.sDesvNn[i] = ((((i**2)*lib.SSKN2[i]) - (i*lib.SKN[i])**2/iNumeroColetas)/(iNumeroColetas-1))**(1/2)
                lib.sDesv[i] = (((lib.SdbdXN2[i] - lib.SdbdXN[i]**2/iNumeroColetas)/(iNumeroColetas-1))**(1/2))
            except:
                lib.sDesv[i] = 0
                lib.sDesvSn[i] = 0
                lib.sDesvNn[i] = 0 
            
            lib.Nn[i] = (lib.SKN[i]/iNumeroColetas)*i
            lib.Sn[i] = (lib.SJN[i]/iNumeroColetas)*i
            lib.SMod[i] = ((lib.Nn[i]**2)+(lib.Sn[i]**2))**0.5              #Modulo dos valores finais de Nn e Sn

######### Calculo da Correçao dos Multipolos para o Angulo do Tipo de Ima #####
##        lib.Nnl = numpy.zeros(21)
##        lib.Snl = numpy.zeros(21)
##        for i in range(1,nmax,1):
##            if TipoIma == 0:
##                lib.Nnl[i] = lib.Nn[i]
##                lib.Snl[i] = lib.Sn[i]
##                lib.sDesvNnl[i] = lib.sDesvNn[i]
##                lib.sDesvSnl[i] = lib.sDesvSn[i]
##            else:
##                lib.Nnl[i] = lib.Nn[i]*numpy.cos(i*lib.Angulo[TipoIma])+lib.Sn[i]*numpy.sin(i*lib.Angulo[TipoIma])
##                lib.Snl[i] = lib.Sn[i]*numpy.cos(i*lib.Angulo[TipoIma])-lib.Nn[i]*numpy.sin(i*lib.Angulo[TipoIma])
##                lib.sDesvNnl[i] = lib.sDesvNn[i]*numpy.cos(i*lib.Angulo[TipoIma])+lib.sDesvSn[i]*numpy.sin(i*lib.Angulo[TipoIma])
##                lib.sDesvSnl[i] = lib.sDesvSn[i]*numpy.cos(i*lib.Angulo[TipoIma])-lib.sDesvNn[i]*numpy.sin(i*lib.Angulo[TipoIma])
###############################################################################

##########################################################################################################################################################################

    elif lib.Tipo_Bobina == 1: ## Tipo = 0 (Radial) Tipo = 1 (Tangencial)
        
    ##### Filtro de leituras pela maior variacao em relaçao a media do angulo #####
        AnguloVolta = []
        iNumeroColetas = len(lib.F)
        dtheta = 2*numpy.pi/(len(lib.F[0]))
        if TipoIma != 0:
            volta_total = len(lib.F)
            while volta_total > volta_filtro:
                AnguloVolta = numpy.zeros(len(lib.F))
                for i in range(len(lib.F)):
                    n = TipoIma
                    raioDelta = r1*numpy.pi/180
                    if lib.Bucked:
                        pass
                        #R = Ne*(r2**n-r1**n)-Neb*(r2b**n-r1b**n)
                        #R = Ne*(r2**n-r1**n)-Neb*(r2b**n-r1b**n)
                    else:
                        pass
                        #R = Ne*(r2**n-r1**n)

                    An = lib.F[i][n].real
                    Bn = -lib.F[i][n].imag
                    
                    #Jn = (An*numpy.sin(n*dtheta)+Bn*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))
                    #Kn = (Bn*numpy.sin(n*dtheta)-An*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))

                    Jn = ( (r2**(-n))*( An*(numpy.cos(n*dtheta)-1) - Bn*numpy.sin(n*dtheta) ) )/ ( 4*Ne*(numpy.cos(n*dtheta)-1)*numpy.sin(raioDelta*n/2) )
                    Kn = ( (r2**(-n))*( Bn*(numpy.cos(n*dtheta)-1) + An*numpy.sin(n*dtheta) ) )/ ( 4*Ne*(numpy.cos(n*dtheta)-1)*numpy.sin(raioDelta*n/2) )

                    AnguloVolta[i] = (1/TipoIma)*numpy.arctan(Jn/Kn)
                   
                maior = numpy.argmax(abs(numpy.mean(AnguloVolta) - AnguloVolta),0)
                AnguloVolta = numpy.delete(AnguloVolta,maior,0)
                lib.F = numpy.delete(lib.F,maior,0)
                dados = numpy.delete(dados,maior,0)
                lib.pontos = numpy.delete(lib.pontos,maior,0)
                volta_total-=1
    ###############################################################################
                
        iNumeroColetas = len(lib.F)
        dtheta = 2*numpy.pi/(len(lib.F[0]))
        lib.AngulosVoltas = numpy.zeros(len(lib.F)*21).reshape(21,len(lib.F))
        lib.SJN = numpy.zeros(21)
        lib.SKN = numpy.zeros(21)
        lib.SNn = numpy.zeros(21)
        lib.SNn2 = numpy.zeros(21)
        lib.SSJN2 = numpy.zeros(21)
        lib.SSKN2 = numpy.zeros(21)
        lib.SdbdXN = numpy.zeros(21)
        lib.SdbdXN2 = numpy.zeros(21)
        for i in range(len(lib.F)):
            for n in range(1,nmax,1):
                raioDelta = r1*numpy.pi/180
                if lib.Bucked and n==TipoIma:
                    n+=1
                    continue
                if lib.Bucked:
                    pass
                    #R = Ne*(r2**n-r1**n)-Neb*(r2b**n-r1b**n)
                else:
                    pass
                    #R = Ne*(r2**n-r1**n)

                An = lib.F[i][n].real
                Bn = -lib.F[i][n].imag

                #Jn = (An*numpy.sin(n*dtheta)+Bn*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))
                #Kn = (Bn*numpy.sin(n*dtheta)-An*(numpy.cos(n*dtheta)-1))/(2*R*(numpy.cos(n*dtheta)-1))

                Jn = ( (r2**(-n))*( An*(numpy.cos(n*dtheta)-1) - Bn*numpy.sin(n*dtheta) ) )/ ( 4*Ne*(numpy.cos(n*dtheta)-1)*numpy.sin(raioDelta*n/2) )
                Kn = ( (r2**(-n))*( Bn*(numpy.cos(n*dtheta)-1) + An*numpy.sin(n*dtheta) ) )/ ( 4*Ne*(numpy.cos(n*dtheta)-1)*numpy.sin(raioDelta*n/2) )

                dbdXN = n*(Jn**2+Kn**2)**(1/2)
                lib.SJN[n] = lib.SJN[n] + Jn
                lib.SKN[n] = lib.SKN[n] + Kn
                lib.SSJN2[n] = lib.SSJN2[n] + Jn**2
                lib.SSKN2[n] = lib.SSKN2[n] + Kn**2
                lib.SdbdXN[n] = lib.SdbdXN[n] + dbdXN
                lib.SdbdXN2[n] = lib.SdbdXN2[n] + dbdXN**2
                lib.AngulosVoltas[n][i] = (1/n)*numpy.arctan(Jn/Kn)

        lib.Angulo = numpy.mean(lib.AngulosVoltas,axis=1)   
        lib.Desv_angulo = numpy.std(lib.AngulosVoltas,axis=1)

    ##### Calculo Desvio Padrao das Medidas #####
        lib.sDesv = numpy.zeros(21)
        lib.sDesvSn = numpy.zeros(21)
        lib.sDesvNn = numpy.zeros(21)
        lib.Nn = numpy.zeros(21)
        lib.Sn = numpy.zeros(21)
        lib.SMod = numpy.zeros(21)
        for i in range(1,nmax,1):
            try:
                lib.sDesvSn[i] = (((((i**2)*lib.SSJN2[i]) - (i*lib.SJN[i])**2/iNumeroColetas)/(iNumeroColetas-1))**(1/2))/(iNumeroColetas**(1/2))
                lib.sDesvNn[i] = (((((i**2)*lib.SSKN2[i]) - (i*lib.SKN[i])**2/iNumeroColetas)/(iNumeroColetas-1))**(1/2))/(iNumeroColetas**(1/2))
                lib.sDesv[i] = (((lib.SdbdXN2[i] - lib.SdbdXN[i]**2/iNumeroColetas)/(iNumeroColetas-1))**(1/2))/(iNumeroColetas**(1/2))
            except:
                lib.sDesv[i] = 0
                lib.sDesvSn[i] = 0
                lib.sDesvNn[i] = 0 
            
            lib.Nn[i] = (lib.SKN[i]/iNumeroColetas)*i
            lib.Sn[i] = (lib.SJN[i]/iNumeroColetas)*i
            lib.SMod[i] = ((lib.Nn[i]**2)+(lib.Sn[i]**2))**0.5              #Modulo dos valores finais de Nn e Sn

######### Calculo da Correçao dos Multipolos para o Angulo do Tipo de Ima #####
##        lib.Nnl = numpy.zeros(21)
##        lib.Snl = numpy.zeros(21)
##        for i in range(1,nmax,1):
##            if TipoIma == 0:
##                lib.Nnl[i] = lib.Nn[i]
##                lib.Snl[i] = lib.Sn[i]
##                lib.sDesvNnl[i] = lib.sDesvNn[i]
##                lib.sDesvSnl[i] = lib.sDesvSn[i]
##            else:
##                lib.Nnl[i] = lib.Nn[i]*numpy.cos(i*lib.Angulo[TipoIma])+lib.Sn[i]*numpy.sin(i*lib.Angulo[TipoIma])
##                lib.Snl[i] = lib.Sn[i]*numpy.cos(i*lib.Angulo[TipoIma])-lib.Nn[i]*numpy.sin(i*lib.Angulo[TipoIma])
##                lib.sDesvNnl[i] = lib.sDesvNn[i]*numpy.cos(i*lib.Angulo[TipoIma])+lib.sDesvSn[i]*numpy.sin(i*lib.Angulo[TipoIma])
##                lib.sDesvSnl[i] = lib.sDesvSn[i]*numpy.cos(i*lib.Angulo[TipoIma])-lib.sDesvNn[i]*numpy.sin(i*lib.Angulo[TipoIma])
###############################################################################

##########################################################################################################################################################################


##### Cálculo da Normalização dos Multipolos @ 0.0175 ou @ 0.012 para Tipo de Ima #####
    lib.Nnl = numpy.zeros(21)
    lib.Snl = numpy.zeros(21)

    if lib.ima_bobina == 0:     ## ACRESCENTADO - Selecionado o Booster ##
        r_ref = 0.0175
    else:
        r_ref = 0.012           ## ACRESCENTADO - Selecionado o Anel ##

##    r_ref = 0.0175 if lib.ima_bobina == 0 else 0.012    ## (apenas teste)
        
    lib.raio_referencia = r_ref
        
    for i in range(1,nmax,1):
        if TipoIma == 0:
            lib.Nnl[i] = lib.Nn[i]
            lib.Snl[i] = lib.Sn[i]
            lib.sDesvNnl[i] = 0
            lib.sDesvSnl[i] = 0
        else:
            lib.Nnl[i] = (lib.Nn[i] * ((r_ref)**(i-1)))/(lib.Nn[TipoIma] * ((r_ref)**(TipoIma-1)))
            lib.Snl[i] = (lib.Sn[i] * ((r_ref)**(i-1)))/(lib.Nn[TipoIma] * ((r_ref)**(TipoIma-1)))
            lib.sDesvNnl[i] = (lib.sDesvNn[i] * ((r_ref)**(i-1)))/(lib.Nn[TipoIma] * ((r_ref)**(TipoIma-1)))
            lib.sDesvSnl[i] = (lib.sDesvSn[i] * ((r_ref)**(i-1)))/(lib.Nn[TipoIma] * ((r_ref)**(TipoIma-1)))
        
############################################################################
            

##### Filtro do Erro desvio padrão ##### (##Erro Relativo desv/medida = 10e-4##) 
    if TipoIma == 0:
        max_erro = 1
    if TipoIma == 1:
        max_erro = 8e-6     ## original 8e-7
    if TipoIma == 2:
        max_erro = 8e-4     ## original 8e-5
    if TipoIma == 3:
        #max_erro = 8e-3     ## original 8e-3
        # Alterado por James Citadini em 18-01-2017.
        #Erro especificado de 0.05% para os 360.2 T/m
        #Assim, 3.6e-2 é 5 vezes melhor do que o necessário na especificação.
        max_erro = 3.6e-2     ## original 8e-5 

    if lib.sDesv[TipoIma]>max_erro or lib.sDesvSn[TipoIma]>max_erro or lib.sDesvNn[TipoIma]>max_erro:
        Historico_Falhas(1)
        return False
    else:                                                                                                
##### Plota os graficos na aba de resultados e habilita botoes de coleta #####
        if Repeticao == 1:
            lib.media = numpy.mean(dados, axis =0)
            x = numpy.linspace(0,1,len(lib.media))
            x2 = numpy.linspace(0,1,(len(dados[0])*len(dados)+10))  ## substituido pontos por dados
            lib.Janela.PlotFunc1(x,lib.media)
            lib.Janela.PlotFunc3(x2,dados)
            lib.Janela.ui.tabWidget.setTabEnabled(const.numero_de_abas-1,True)
            lib.Janela.ui.groupBox_2.setEnabled(True)
            lib.Janela.ui.coletar.setEnabled(True)
            if lib.Ref_Bobina == 0:
                QtGui.QMessageBox.warning(lib.Janela,'Aviso.','Dados transferidos com sucesso.',QtGui.QMessageBox.Ok)

        QtGui.QApplication.processEvents()
        return True

def Historico_Falhas(Index):
    data = time.strftime("%d/%m/%Y", time.localtime())
    hora = time.strftime("%H:%M:%S", time.localtime())
    Nome = str(lib.Janela.ui.Nome_Ima.text())
    Medida = 1+int(str(lib.Janela.ui.label_138.text()))
    f = open('Historico_Falhas.dat','a')

    if Index == 0:
        f.write(str(data) + ' ' + str(hora) + ': Falha no recebimento dos dados (' + str(Nome) + '_' + str(Medida) + ').\n')
    if Index == 1:
        f.write(str(data) + ' ' + str(hora) + ': Desvio Padrao elevado (' + str(Nome) + '_' + str(Medida) + ').\n')
    if Index == 2:
        f.write(str(data) + ' ' + str(hora) + ': Over-Range no Ganho de Tensão (' + str(Nome) + '_' + str(Medida) + ').\n')

    f.close

def Salvar_Arquivo(Dados):  ## Salvar arquivo de dados ##
    file = open('Arquivo.dat','w')  
    for i in range(len(Dados)):
##        for j in range(len(dados[0])):
##            file.write('{0:^+18.10e}'.format(dados[i][j]) + '\n')
##        file.write('{0:^+18.10e}'.format(Dados[i]) + '\n')
        file.write(str(Dados[i]) + '\n')
##        file.write('\n')
    file.close()            ## Salvar arquivo de dados ##



################################################################# INICIO THREADING #################################################################


########## Encontrar referencia dos motores transversais Display ND 760 ##########
class EncontraRef_ND760(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()
    def callback(self):
        self._stop()
    def run(self):
        lib.Janela.ui.status.setText('Movendo')
        lib.Janela.ui.groupBox_6.setEnabled(False)
        lib.motor.MoverMotorFimdeCursoNeg(const.motorA_endereco,3,5)
        lib.motor.MoverMotorFimdeCursoNeg(const.motorB_endereco,3,5)
        while (not lib.motor.ready(const.motorA_endereco) or not lib.motor.ready(const.motorB_endereco)) and lib.parartudo == 0:
            QtGui.QApplication.processEvents()
        if lib.parartudo == 0:
            lib.stop = 1
            time.sleep(0.5)
            lib.display.Reset_SetRef_Display()
            lib.stop = 0
            lib.motor.MoverMotorFimdeCursoPos(const.motorA_endereco,3,5)
            lib.motor.MoverMotorFimdeCursoPos(const.motorB_endereco,3,5)
            time.sleep(8.5)
            lib.motor.PararMotor(const.motorA_endereco)
            lib.motor.PararMotor(const.motorB_endereco)
            time.sleep(1)
            lib.Janela.Mover_Motor_A(0,1)
            time.sleep(.2)
            while (lib.Motor_Posicao == 0) and lib.parartudo == 0:
                lib.Janela.ui.groupBox_6.setEnabled(False)
                lib.Janela.ui.zerar.setEnabled(False)
                QtGui.QApplication.processEvents()
            lib.Janela.Mover_Motor_B(0,1)
            time.sleep(.2)
            while (lib.Motor_Posicao == 0) and lib.parartudo == 0:
                lib.Janela.ui.groupBox_6.setEnabled(False)
                lib.Janela.ui.zerar.setEnabled(False)
                QtGui.QApplication.processEvents()
        lib.Janela.ui.groupBox_6.setEnabled(True)
        lib.Janela.ui.zerar.setEnabled(True)
        lib.Janela.ui.status.setText('Pronto')
#########################################################################################################


########## Encontrar referencia dos motores transversais Display ND 780 ##########
class EncontraRef_ND780(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()
    def callback(self):
        self._stop()
    def run(self):
        lib.Janela.ui.status.setText('Movendo')
        lib.Janela.ui.groupBox_6.setEnabled(False)
        lib.motor.MoverMotorFimdeCursoNeg(const.motorA_endereco,3,5)
        lib.motor.MoverMotorFimdeCursoNeg(const.motorB_endereco,3,5)
        while (not lib.motor.ready(const.motorA_endereco) or not lib.motor.ready(const.motorB_endereco)) and lib.parartudo == 0:
            QtGui.QApplication.processEvents()
        if lib.parartudo == 0:
            lib.stop = 1
            time.sleep(0.5)
            lib.display.Reset_SetRef_Display()
            time.sleep(7)
            lib.stop = 0
            lib.display.Enviar_Tecla(lib.display.Ent)
            lib.motor.MoverMotorFimdeCursoPos(const.motorA_endereco,3,5)
            lib.motor.MoverMotorFimdeCursoPos(const.motorB_endereco,3,5)
            time.sleep(10)
            lib.motor.PararMotor(const.motorA_endereco)
            lib.motor.PararMotor(const.motorB_endereco)
            time.sleep(1)
            lib.Janela.Mover_Motor_A(0,2)
            time.sleep(.2)
            while (lib.Motor_Posicao == 0) and lib.parartudo == 0:
                lib.Janela.ui.groupBox_6.setEnabled(False)
                lib.Janela.ui.zerar.setEnabled(False)
                QtGui.QApplication.processEvents()
            lib.Janela.Mover_Motor_B(0,2)
            time.sleep(.2)
            while (lib.Motor_Posicao == 0) and lib.parartudo == 0:
                lib.Janela.ui.groupBox_6.setEnabled(False)
                lib.Janela.ui.zerar.setEnabled(False)
                QtGui.QApplication.processEvents()
        lib.Janela.ui.groupBox_6.setEnabled(True)
        lib.Janela.ui.zerar.setEnabled(True)
        lib.Janela.ui.status.setText('Pronto')
#########################################################################################################


########### Mover os motores transversais para a posicao desejada ###########
class motortransversal(threading.Thread):
    def __init__(self, posicaoA, posicaoB, velocidade = 0.2):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.posicaoA = posicaoA
        self.posicaoB = posicaoB
        self.velocidade = velocidade
        self.start()
    def callback(self):
        self._stop()
    def run(self):
        lib.Motor_Posicao = 0
        lib.Janela.ui.status.setText('Movendo')
        if self.velocidade >= 1:
            aceleracao = 5
        else:
            aceleracao = 0.2
        lib.display.LerDisplay()      
        posicao = lib.display.DisplayPos
        erroX = self.posicaoA-float(posicao[0])
        passosX = int(const.passos_mmA*abs(erroX))
        erroY = self.posicaoB-float(posicao[1])
        passosY = int(const.passos_mmB*abs(erroY))        
        while (passosX > const.passos_mmA/250 or passosY > const.passos_mmB/250) and lib.parartudo == 0: #### divisao por 500.
            if(erroX > 0):
                sentidoA = const.avancoA^1
            else:
                sentidoA = const.avancoA
            if(erroY > 0):
                sentidoB = const.avancoA^1
            else:
                sentidoB = const.avancoB
            lib.motor.ConfMotor(const.motorA_endereco,self.velocidade,aceleracao,passosX)
            lib.motor.ConfModo(const.motorA_endereco,0,sentidoA)
            lib.motor.ConfMotor(const.motorB_endereco,self.velocidade,aceleracao,passosY)
            lib.motor.ConfModo(const.motorB_endereco,0,sentidoB)
            if lib.motor.ready(const.motorA_endereco) and lib.motor.ready(const.motorB_endereco) and lib.parartudo == 0:
                lib.motor.MoverMotor(const.motorA_endereco)
                lib.motor.MoverMotor(const.motorB_endereco)
            while (not lib.motor.ready(const.motorA_endereco) or not lib.motor.ready(const.motorB_endereco)) and lib.parartudo == 0:
                QtGui.QApplication.processEvents()
            time.sleep(1)
            lib.display.LerDisplay()
            posicao = lib.display.DisplayPos
            erroX = self.posicaoA-float(posicao[0])
            passosX = int(const.passos_mmA*abs(erroX))
            erroY = self.posicaoB-float(posicao[1])
            passosY = int(const.passos_mmB*abs(erroY))
        if lib.Janela.ui.bobinadesmontada.isChecked():
            lib.Janela.ui.groupBox_6.setEnabled(True)
        else:
            lib.Janela.ui.groupBox_4.setEnabled(True)
        lib.Janela.ui.zerar.setEnabled(True)
        lib.Janela.ui.bobinadesmontada.setEnabled(True)
        lib.Janela.ui.status.setText('Pronto')
        QtGui.QApplication.processEvents()
        lib.Motor_Posicao = 1
#################################################################################################     


#################### Leitura Corrente Puc/Digital #############################
class leitura_corrente_puc(threading.Thread):
    def __init__(self, nVoltas, velocidade):
        threading.Thread.__init__(self)
        self.nVoltas = int(nVoltas)
        self.velocidade = float(velocidade)
        self.start()
    def run(self):
        if lib.controle_fonte == 0:              #ACRESCENTADO# Selecionado a PUC 
            saida = []
    ##        if (lib.Janela.ui.tabWidget.isTabEnabled(3) == True):
            if (lib.PUC_Conectada == 1) and (lib.Status_Fonte == 1):
                fator = float(lib.Janela.ui.Fator_Entrada.text())
                for i in range(self.nVoltas):
                    saida.append(float(lib.Janela.Valor_Equacao(1,lib.PUC.ReadAD(),fator)))
                    time.sleep((1/self.velocidade)-.1)
            else:
                for i in range(self.nVoltas):
                    saida.append(0)
            self.saida = saida
        else:                                   #ACRESCENTADO# Selecionado a Digital
            saida = []
    ##        if (lib.Janela.ui.tabWidget.isTabEnabled(3) == True):
            if (lib.Digital_Conectada == 1) and (lib.Status_Fonte == 1):
                fator = float(lib.Janela.ui.Fator_Entrada.text())
                for i in range(self.nVoltas):
                    saida.append(float(lib.Janela.Valor_Equacao(1,lib.Digital.Read_iLoad1(),fator)))
                    time.sleep((1/self.velocidade)-.1)
            else:
                for i in range(self.nVoltas):
                    saida.append(0)
            self.saida = saida
######################################################################


#################### Leitura Corrente Multimetro #############################
class leitura_corrente_multimetro(threading.Thread):
    def __init__(self, nVoltas, velocidade):
        threading.Thread.__init__(self)
        self.nVoltas = int(nVoltas)
        self.velocidade = float(velocidade)
        self.start()
    def run(self):
        if lib.controle_fonte == 0:              #ACRESCENTADO# Puc 
            saida = []
            for i in range(self.nVoltas):
                saida.append(lib.Janela.ConverteDCCT())
                time.sleep((1/self.velocidade)-0.01)
            self.saida = saida
        else:                                   #ACRESCENTADO# Digital 
            saida = []
            for i in range(self.nVoltas):
##                saida.append(lib.Janela.ConverteDCCT2())  # Original
                saida.append(lib.Janela.ConverteDCCT())     
                time.sleep((1/self.velocidade)-0.01)
            self.saida = saida
            

#################### Leitura Corrente Secundária Fonte Digital 10A ############################# ACRESCENTADO
class leitura_corrente_sec_mult(threading.Thread):
    def __init__(self, nVoltas, velocidade):
        threading.Thread.__init__(self)
        self.nVoltas = int(nVoltas)
        self.velocidade = float(velocidade)
        self.start()
    def run(self):
        saida = []
        for i in range(self.nVoltas):
            saida.append(lib.Digital.Read_iLoad1())
            time.sleep((1/self.velocidade)-0.01)
        self.saida = saida

#################### Leitura Corrente Secundária Fonte Digital 10A (Multicanal) ###################
class leitura_corrente_sec_Multicanal(threading.Thread):
    def __init__(self, nVoltas, velocidade):
        threading.Thread.__init__(self)
        self.nVoltas = int(nVoltas)
        self.velocidade = float(velocidade)
        self.start()
    def run(self):
        saida = []
        for i in range(self.nVoltas):
            saida.append(lib.Janela.Converte_DCCT_MultiCanal())
            time.sleep((1/self.velocidade)-0.01)
        self.saida = saida


################################ Ciclagem da Fonte ######################################
# Modificado por James Citadini em 22/02/2016: Tratamento na curva de ciclagem.
# A alteração transforma a classe em objeto.
#class Ciclagem_Fonte(threading.Thread):
class Ciclagem_Fonte(object):
    def __init__(self,final,atual,passo,tempo,rep_int,delay,n_ciclos,ponto_final,freq,index):
        #threading.Thread.__init__(self)
        self.final = float(final)
        self.atual = float(atual)
        self.passo = float(passo)
        self.tempo = float(tempo)
        self.ponto_final = int(ponto_final)
        self.rep_int = int(rep_int)
        self.delay = int(delay)
        self.n_ciclos = int(n_ciclos)
        self.freq = float(freq)
        self.index = int(index)        
        #self.start()
    #def callback(self):
    #    self._stop()
    def run(self):
        if lib.controle_fonte == 0:         #ACRESCENTADO#
            try:
                Tipo_Curva = int(lib.Janela.ui.tabWidget_3.currentIndex())
                if Tipo_Curva == 0 or Tipo_Curva == 1:
                    rampa = lib.Janela.Rampa(self.final,self.atual,self.passo,self.tempo)
                else:
                    rampa = True
                time.sleep(.1)
                if (rampa == True):
                    if lib.Modelo_PUC ==0:
                        lib.Fonte_Ciclagem = 1
                        lib.PUC.ExecuteCurve(lib.Ciclos_Puc, 0, 0, 1, 1, 0, 1)    ## Modulo PUC Antiga sem saida de clock
        ##                lib.PUC.ExecuteCurve(lib.Ciclos_Puc, 0, 1, 1, 0, 0, 1)    ## Modulo PUC Antiga com saida de clock
                        for i in range (self.rep_int):
                            for j in range (self.delay):
                                if lib.parartudo == 1:
                                    lib.PUC.StopCurve()
                                    lib.PUC.WriteDA(0)
                                    break
                                time.sleep(1)
                        while (self.n_ciclos>=0) and lib.parartudo==0:
                            if self.n_ciclos==0:
                                for i in range (2000):
                                    if lib.parartudo == 1:
                                        lib.PUC.StopCurve()
                                        lib.PUC.WriteDA(0)
                                        break
                                    status, ponto = lib.PUC.ReadStatusCurve()
                                    if ponto >= self.ponto_final:
                                        lib.PUC.StopCurve()
                                        break
                            else:
                                if lib.parartudo == 1:
                                    lib.PUC.StopCurve()
                                    lib.PUC.WriteDA(0)
                                    break
                                time.sleep(1/self.freq)
                            self.n_ciclos-=1
                    else:
                        if lib.Analise_Freq == 0:
                            lib.Fonte_Ciclagem = 1
                        Curva_Finalizada = 0
                        status = lib.PUC.WriteDigBit(4,0)
                        lib.PUC.ExecuteCurve(lib.Ciclos_Puc, 0, 0, 1, 1, 0, 0, 1, lib.Divisor_Puc, 1, 4) ## Modulo PUC Nova sem saida de clock
                        if lib.Analise_Freq == 1:
                            lib.Fonte_Ciclagem = 1
        ##                lib.PUC.ExecuteCurve(lib.Ciclos_Puc, 0, 1, 1, 1, 0, 0, 1, lib.Divisor_Puc, 1, 4) ## Modulo PUC Nova com saida de clock
                        time.sleep(1)
                        while Curva_Finalizada == 0 and lib.parartudo==0:
                            status = lib.PUC.ReadDigOut()
                            Curva_Finalizada = dec_bin(status,4)
                            time.sleep(0.1)
                        status = lib.PUC.WriteDigBit(4,0)
                        if lib.parartudo == 1:
                            lib.PUC.StopCurve() ## Para a curva
                            lib.PUC.WriteDA(0)  ## Zera a saida
                            return
                lib.Fonte_Pronta = 1
                lib.Fonte_Ciclagem = 0
                lib.Janela.ui.tabWidget_2.setEnabled(True)
                lib.Janela.ui.coletar.setEnabled(True)
                lib.Janela.ui.Carregar_Config_Fonte.setEnabled(True)
                lib.Janela.ui.Corrente_Atual.setEnabled(True)
        ##        QtGui.QApplication.processEvents()
                if self.index == 0: 
                    QtGui.QMessageBox.information(lib.Janela,'Ciclagem.','Processo de Ciclagem Concluído com Sucesso.',QtGui.QMessageBox.Ok)
                    QtGui.QApplication.processEvents()
            except:
                traceback.print_exc(file=sys.stdout)

        else:           #ACRESCENTADO#  Seleciona a fonte digital

            lib.Digital.EnableSigGen()
            if self.index == 0: 
                QtGui.QMessageBox.information(lib.Janela,'Ciclagem.','Processo de Ciclagem Concluído com Sucesso.',QtGui.QMessageBox.Ok)
                QtGui.QApplication.processEvents()
            
        
###############################################################################################


################################### Rampa de Corrente ##############################################
##class Rampa_Corrente(threading.Thread):
##    def __init__(self,final,atual,passo,tempo):
##        threading.Thread.__init__(self)
##        self.final = float(final)
##        self.atual = float(atual)
##        self.passo = float(passo)
##        self.tempo = float(tempo)
##        self.start()
##
##    def callback(self):
##        self._stop()
##        
##    def run(self):
##        ramp=10
##        try:
##            if self.final > self.atual:
##                faixa = numpy.arange(self.atual+self.passo,self.final,self.passo)
##            else:
##                faixa = numpy.arange(self.final,self.atual,self.passo)
##                faixa = faixa[::-1]
##            faixa[-1] = self.final
##            for i in faixa:
##                if (lib.parartudo == 0):
##                    time.sleep(self.tempo)
##                    lib.PUC.WriteDA(i)
##                else:
##                    lib.PUC.WriteDA(0)
##                    time.sleep(0.1)
##                    print(0)
##                    ramp = False
##            ramp = True
##        except:
##            try:
##                if ((self.final>self.atual) and ((self.final-self.atual)<self.passo)) or ((self.final<self.atual) and ((self.atual-self.final)<self.passo)):
##                    lib.PUC.WriteDA(final)
##                    ramp = True
##            except:
##                print(1)
##                ramp = False
##
##        if ramp == True:
##            QtGui.QMessageBox.information(lib.Janela,'Aviso.','Corrente atingida com Sucesso.',QtGui.QMessageBox.Ok)
##        else:
##            QtGui.QMessageBox.critical(lib.Janela,'Atenção.','Falha! Verifique Valores da Fonte.',QtGui.QMessageBox.Ok)
##        lib.Janela.ui.tabWidget_2.setEnabled(True)
##        lib.Janela.ui.coletar.setEnabled(True)
##        lib.Janela.ui.Carregar_Config_Fonte.setEnabled(True)
##        lib.Janela.ui.Corrente_Atual.setEnabled(True)
##        lib.Fonte_Pronta = 1
##        QtGui.QApplication.processEvents()

####################################################################################################


################################ Controle de Status Programa ######################################
class Controle_Status(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
    def callback(self):
        self._stop()
    def run(self):
        i=0
        while i==0:
            time.sleep(.2)
            QtGui.QApplication.processEvents()
            ### Status Fonte ###
            if (lib.Status_Fonte == 1):
                lib.Janela.ui.status_fonte.setText('Ligada')
                lib.Janela.ui.ligar_fonte.setText('Desligar')
            else:
                lib.Janela.ui.status_fonte.setText('Desligada')
                lib.Janela.ui.ligar_fonte.setText('Ligar')
            if (lib.controle_fonte == 0):                   #ACRESCENTADO# Selecionda a PUC    
                if (lib.PUC_Conectada == 1) and (lib.Status_Fonte == 1) and (lib.Fonte_Pronta == 1) and (lib.Fonte_Calibrada == [1,1]):
                    lib.Janela.ui.label_135.setText('OK')
                else:
                    lib.Janela.ui.label_135.setText('NOK')
            else:                                           #ACRESCENTADO# Seleciona a Digital
                if (lib.Digital_Conectada == 1) and (lib.Status_Fonte == 1) and (lib.Fonte_Pronta == 1) and (lib.Fonte_Calibrada == [1,1]):
                    lib.Janela.ui.label_135.setText('OK')
                else:
                    lib.Janela.ui.label_135.setText('NOK')
                
            if (lib.Fonte_Calibrada[1] == 1):
                lib.Janela.ui.label_equacao_saida.setText('Saída: OK')
            else:
                lib.Janela.ui.label_equacao_saida.setText('Saída: NOK')
                
            if (lib.Fonte_Calibrada[0] == 1):
                lib.Janela.ui.label_equacao_entrada.setText('Entrada: OK')
            else:
                lib.Janela.ui.label_equacao_entrada.setText('Entrada: NOK')
            #ACRESCENTADO - LEITURA DOS INTERLOCKS FONTE DIGITAL#
##            if (lib.Digital_Conectada == 1) and (lib.Status_Fonte == 1) and (lib.Fonte_Pronta == 1) and (lib.Fonte_Calibrada == [1,1]):                
##                status = lib.Digital.Read_ps_SoftInterlocks()
##                time.sleep(.5)
##                status2 = lib.Digital.Read_ps_HardInterlocks()
##                time.sleep(.5)
##                print('ok')
##                if (status != 0) or (status2 != 0):  
##                    QtGui.QMessageBox.critical(lib.Janela,'Atenção.','Interlock da Fonte Acionado.',QtGui.QMessageBox.Ok)
##                    resp = QtGui.QMessageBox.question(lib.Janela,'Interlock.','Interlock Acionado.\nDeseja resetar Interlocks?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)
##                    if resp == QtGui.QMessageBox.Yes:
##                        lib.Digital.ResetInterlocks()
##                    else:                    
##                        QtGui.QApplication.processEvents()
##                        return



                
            ### Status Coletas ###
##            if (lib.Janela.ui.Chk_Auto.isChecked()) and (lib.Janela.ui.Chk_Auto.isEnabled()):
##                lib.Janela.ui.Hab_Corretora.setEnabled(False)
##                lib.Janela.ui.C_Sucessivas.setEnabled(False)
##                time.sleep(.1)
##            else:
##                lib.Janela.ui.Hab_Corretora.setEnabled(True)
##                lib.Janela.ui.C_Sucessivas.setEnabled(True)
##            if (lib.Janela.ui.C_Sucessivas.isChecked()) and (lib.Janela.ui.C_Sucessivas.isEnabled()):
##                lib.Janela.ui.N_Coletas_Manual.setEnabled(True)
##                lib.Janela.ui.label_22.setEnabled(True)
##                lib.Janela.ui.Chk_Auto.setEnabled(False)
##                lib.Janela.ui.Hab_Corretora.setEnabled(False)
##                time.sleep(.1)
##            else:
##                lib.Janela.ui.N_Coletas_Manual.setEnabled(False)
##                lib.Janela.ui.label_22.setEnabled(False)
##                lib.Janela.ui.Hab_Corretora.setEnabled(True)
##                if (lib.Fonte_Pronta == 1):
##                    lib.Janela.ui.Chk_Auto.setEnabled(True) 
###################################################################################################            








################################################################# FINAL THREADING #################################################################
        

# ____________________________________________
# Objeto da janela de programa
class screen(object):
    def __init__(self):
        app = QtGui.QApplication(sys.argv)
        lib.Janela = JanelaGrafica()
        lib.Janela.show()
        time.sleep(0.5)
        app.exec_()
# ____________________________________________



# ____________________________________________
if __name__ == '__main__':
    tela = screen()
    lib.parartudo = 1
    print(threading.activeCount())
    lib.Janela.Emergencia_Fonte()
