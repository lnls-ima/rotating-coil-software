# -*- coding: utf-8 -*-
"""
Created on 15/01/2013
Versão 1.0
@author: James Citadini
"""
# Importa bibliotecas
import time
import threading
import numpy as np
import random # Teste graph

import Agilent_34401A as A34401A

from PyQt4 import QtCore, QtGui
from Interface_Agilent_34401A import *
import sys

class Interface(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self._stop()

    def run(self):
        self.app = QtGui.QApplication(sys.argv)
        self.myapp = MyForm()
        self.myapp.show()
        sys.exit(self.app.exec_())

class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        # Inicializa Interface
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        QtCore.QObject.connect(self.ui.pb_Conectar,QtCore.SIGNAL("clicked()"), self.Conectar)
        QtCore.QObject.connect(self.ui.le_nmedidas,QtCore.SIGNAL("editingFinished()"), self.VerificaValor)
        QtCore.QObject.connect(self.ui.le_intervalo,QtCore.SIGNAL("editingFinished()"), self.VerificaValor)
        QtCore.QObject.connect(self.ui.le_conversao,QtCore.SIGNAL("editingFinished()"), self.VerificaValor)
        QtCore.QObject.connect(self.ui.le_TempoEspera,QtCore.SIGNAL("editingFinished()"), self.VerificaValor)

        QtCore.QObject.connect(self.ui.pb_Iniciar,QtCore.SIGNAL("clicked()"), self.IniciarColetas)
        QtCore.QObject.connect(self.ui.pb_Parar,QtCore.SIGNAL("clicked()"), self.PararColetas)

        QtCore.QObject.connect(self.ui.tb_Acessar,QtCore.SIGNAL("clicked()"), self.Acessar)
        QtCore.QObject.connect(self.ui.tb_Reiniciar,QtCore.SIGNAL("clicked()"), self.Reiniciar)
        QtCore.QObject.connect(self.ui.tb_Limpar,QtCore.SIGNAL("clicked()"), self.Limpar)
        QtCore.QObject.connect(self.ui.tb_Configurar,QtCore.SIGNAL("clicked()"), self.Configurar)
        QtCore.QObject.connect(self.ui.tb_Medir,QtCore.SIGNAL("clicked()"), self.Medir)  

        self.ui.rb_TensaoV.setChecked(True)
        self.ui.le_TempoEspera.setText('50')
        self.ui.le_nmedidas.setText('10')
        self.ui.le_intervalo.setText('1')
        self.ui.le_TempoEspera.setText('0')
        self.ui.le_intervalo.setText('0')

    def Conectar(self):
        if self.ui.pb_Conectar.text() == 'Conectar Dispositivo':
            try:
                porta = self.ui.cb_PortaCom.currentIndex() + 1
                self.Volt = A34401A.SerialCom(porta)
                self.Volt.Conectar()
                self.PararTudo = False
                self.ui.gb_Geral.setEnabled(True)
                self.ui.cb_PortaCom.setEnabled(False)
                self.ui.pb_Conectar.setText('Desconectar Dispositivo')                
            except:
                QtGui.QMessageBox.warning(self,'Falha de Conexão','Falha na Conexão com o Dispositivo',QtGui.QMessageBox.Ok)
        else:
            try:
                self.ui.gb_Geral.setEnabled(False)
                self.ui.cb_PortaCom.setEnabled(True)
                self.ui.pb_Conectar.setText('Conectar Dispositivo')
                self.Volt.Desconectar()
            except:
                pass

    def IniciarColetas(self):
        self.PararTudo = False
        self.valores = 0
        self.dados = np.array([])

        self.ui.pb_Parar.setEnabled(True)
        self.ui.pb_Iniciar.setEnabled(False)
        self.ui.gb_medidas.setEnabled(False)
        self.ui.gb_btmanuais.setEnabled(False)
        self.ui.cb_Salvar.setEnabled(False)
        self.ui.cb_TIntegracao.setEnabled(False)
        self.ui.le_TempoEspera.setEnabled(False)
        
        self.ui.lcd_status.setProperty('value',0)
        npontos = int(self.ui.le_nmedidas.text())
        steps = 100/npontos
        intervalo = float(self.ui.le_intervalo.text())

        nomeArq = 'Dados_'+ time.strftime("%d-%m-%Y_%H%M", time.localtime()) + '.dat'
        
        if self.SalvarArquivo(nomeArq) == True:
            self.Volt.LimpaTxRx()
            self.Volt.Enviar(self.Volt.Acesso)
            self.Volt.Enviar(self.Volt.Reset)
            self.Volt.Enviar(self.Volt.Limpar)
            self.Volt.Enviar(self.Volt.ConfiguraVolt[self.ui.cb_TIntegracao.currentIndex()])
            self.Volt.LimpaTxRx()
            time.sleep(0.5)
            for i in range(npontos):
                if self.PararTudo == False:

                    datahora = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
                    
                    self.valores = self.Medir()

                    self.dados = np.append(self.dados,float(self.valores))

                    self.ui.lcd_leitura.setProperty('value','{0:0.6f}'.format(float(self.valores)))
                    
                    self.Graph()

                    self.ui.lcd_status.setProperty('value',i*steps)

                    if self.ui.cb_Salvar.isChecked():
                        self.filename = open(nomeArq,'a')
                        self.filename.writelines(str(i+1) + '\t' + datahora + '\t' + '{0:0.6f}'.format(self.valores) + '\n')
                        self.filename.close()

                    time.sleep(intervalo)

                    QtGui.QApplication.processEvents()
                else:
                    break

            self.ui.lcd_status.setProperty('value',100)
            
            if self.PararTudo == False:
                QtGui.QMessageBox.warning(self,'Finalizada','Medições Finalizadas',QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.warning(self,'Finalizada','Medições Interrompidas',QtGui.QMessageBox.Ok)
                self.PararTudo = False            

        self.ui.pb_Parar.setEnabled(False)
        self.ui.pb_Iniciar.setEnabled(True)
        self.ui.gb_medidas.setEnabled(True)
        self.ui.gb_btmanuais.setEnabled(True)
        self.ui.cb_Salvar.setEnabled(True)
        self.ui.cb_TIntegracao.setEnabled(True)
        self.ui.le_TempoEspera.setEnabled(True)

    def SalvarArquivo(self, nomeArq):
        if self.ui.cb_Salvar.isChecked():
            try:
                filename = open(nomeArq)
                print (nomeArq)
                print (filename)
                resp = QtGui.QMessageBox.warning(self,'Arquivo','Deseja sobrescrever o arquivo existente?',QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
                print (resp)
                if resp == 16384:
                    filename = open(nomeArq,'w')
                    if self.ui.rb_TensaoV.isChecked():
                        filename.writelines('nMed\tDataHora\tTensao\n')
                    elif self.ui.rb_CampoG.isChecked():
                        filename.writelines('nMed\tDataHora\tCampoG\n')
                    elif self.ui.rb_CampoT.isChecked():
                        filename.writelines('nMed\tDataHora\tCampoT\n')
                    filename.close()
                    return True
                else:
                    filename.close()
                    return False
            except:
                try:
                    filename = open(nomeArq,'w')
                    if self.ui.rb_TensaoV.isChecked():
                        filename.writelines('nMed\tDataHora\tTensao\n')
                    elif self.ui.rb_CampoG.isChecked():
                        filename.writelines('nMed\tDataHora\tCampoG\n')
                    elif self.ui.rb_CampoT.isChecked():
                        filename.writelines('nMed\tDataHora\tCampoT\n')
                    filename.close()
                    return True
                except:
                    return False
        else:
            return True
       
    def Graph(self):
        n = int(self.ui.cb_pontosgrafico.currentText()) * -1
        data = self.dados[n:]
        
        self.ui.widget.canvas.ax.clear()
        self.ui.widget.canvas.ax.plot(data)
        self.ui.widget.canvas.ax.set_xlabel('Número da Medida')
        if self.ui.rb_CampoT.isChecked():
            self.ui.widget.canvas.ax.set_ylabel('Campo [T]')
        elif self.ui.rb_CampoG.isChecked():
            self.ui.widget.canvas.ax.set_ylabel('Campo [G]')
        else:
            self.ui.widget.canvas.ax.set_ylabel('Tensão [V]')
        self.ui.widget.canvas.fig.tight_layout()
        self.ui.widget.canvas.draw()

        self.ui.le_media.setText('{0:0.6f}'.format(np.average(data)))
        self.ui.le_desvio.setText('{0:0.6f}'.format(np.std(data)))
        
    def PararColetas(self):
        self.PararTudo = True

    def Acessar(self):
        self.Volt.Enviar(self.Volt.Acesso)

    def Reiniciar(self):
        self.Volt.Enviar(self.Volt.Reset)

    def Limpar(self):
        self.Volt.Enviar(self.Volt.Limpar)

    def Configurar(self):
        self.Volt.Enviar(self.Volt.ConfiguraVolt[self.ui.cb_TIntegracao.currentIndex()])

    def Medir(self):
        try:
            self.Volt.Enviar(self.Volt.LerVolt)
            time.sleep(int(self.ui.le_TempoEspera.text()) / 1000 )
            intervalo = self.Volt.Delays[self.ui.cb_TIntegracao.currentText()] / 1000 # converte para segundos
            time.sleep(intervalo)
            Leitura = float(self.Volt.Ler(20))
            if self.ui.rb_CampoT.isChecked():
                Leitura = Leitura / float(self.ui.le_conversao.text())
            if self.ui.rb_CampoG.isChecked():
                Leitura = Leitura / float(self.ui.le_conversao.text()) * 10000
        except:
            Leitura = 0

        self.ui.lcd_leitura.setProperty('value',Leitura)
        return Leitura
        
    def VerificaValor(self):
        # Número de Medidas
        try:
            valor = int(self.ui.le_nmedidas.text())
        except:
            valor = 1
        self.ui.le_nmedidas.setText(str(valor))

        # Intervalo
        try:
            valor = float(self.ui.le_intervalo.text())
        except:
            valor = 1
        self.ui.le_intervalo.setText(str(valor))

        # Conversão Tensão Campo
        try:
            valor = float(self.ui.le_conversao.text())
        except:
            valor = 1
        self.ui.le_conversao.setText(str(valor))

        # Tempo Espera
        try:
            valor = int(self.ui.le_TempoEspera.text())
        except:
            valor = 100
        self.ui.le_TempoEspera.setText(str(valor))        
        
if __name__ == '__main__':
    
    # Exibe Tela Principal
    App = Interface()
