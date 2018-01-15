#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, math
import PyQt4.QtGui
import PyQt4.QtCore
import time

from interface import *

sys.path.append('../pypucsp/')
import pucsp

DEBUG = False
TIMER_FREQ = 60e3
UPDATE_INTERVAL = 150

class Client(QtGui.QDialog, Ui_Interface):
    puc = None
    connected = False
    hasAnalog = False
    hasDigital = False

    def setStatus(self, text):
        txt = ""
        try:
            txt = QtCore.QString.fromUtf8(text)
        except AttributeError:
            txt = text
        self.txtStatus.setText(txt)
        QtGui.QApplication.processEvents()

    def __init__(self, parent = None):
        super(Client, self).__init__(parent)
        self.setupUi(self)

        self.DICheckBoxes = \
        (self.chkDI0, self.chkDI1, self.chkDI2, self.chkDI3, \
         self.chkDI4, self.chkDI5, self.chkDI6, self.chkDI7)

        self.DOCheckBoxes = \
        (self.chkDO0, self.chkDO1, self.chkDO2, self.chkDO3, \
         self.chkDO4, self.chkDO5, self.chkDO6, self.chkDO7)

        self.connected = False

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(UPDATE_INTERVAL)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()

        self.on_spinSyncClkDiv_valueChanged()
        self.on_cbSyncClkSrc_currentIndexChanged()
        self.checkConnected()

    @QtCore.pyqtSlot()
    def refresh(self):
        if not self.puc or not self.connected:
            return

        state, index = self.puc.sync.getState()
        self.txtSyncStatus.setText(state)

        stopped = state == "STOPPED"
        running = state == "RUNNING"

        # Sync frames
        self.frameSyncGen.setEnabled(stopped)
        self.frameReadCapture.setEnabled(stopped)
        self.frameSyncCfg.setEnabled(stopped)

        # Sync executon control buttons
        self.btSyncStart.setEnabled(not running)
        self.btSyncPause.setEnabled(running)
        self.btSyncStop.setEnabled(not stopped)

        # Sync progress bar
        if self.lastSyncNPts == None:
            progSyncValue = 0
        else:
            progSyncValue = int((float(index)/self.lastSyncNPts)*100)
        self.progSync.setValue(progSyncValue)

        if not running:
            self.timer.stop()

    # Connection panel

    def on_btConnect_released(self):
        if self.connected:
            self.connected = False
            self.puc.disconnect()
            self.puc = None
            self.setStatus("Desconectado")
        else:
            self.setStatus("Conectando...")
            port = str(self.txtSerialPort.text())
            pucAddr = int(self.spinSerialAddress.text())
            try:
                self.puc = pucsp.SerialPUC(port, pucAddr, debug=DEBUG)
            except:
                self.setStatus("Falha ao conectar")
                return

            self.puc.sync.stop()
            self.lastSyncNPts = None
            self.lastSyncWidePt = None

            if self.puc.ads:
                self.AI = self.puc.ads[0]   # Analog Input
                self.AO = self.puc.das[0]   # Analog Output
                self.updateAI()
                self.updateAO()

            if self.puc.digins:
                self.DI = self.puc.digins[0]    # Digital Input
                self.DO = self.puc.digouts[0]   # Digital Output
                self.updateDI()
                self.updateDO()

            stFmt = "Conectado. Porta: {}, Endereço: {}"
            self.setStatus(stFmt.format(port, pucAddr))
            self.connected = True
        self.checkConnected()

    def checkConnected(self):
        self.txtSerialPort.setEnabled(not self.connected)
        self.spinSerialAddress.setEnabled(not self.connected)
        self.btReset.setEnabled(self.connected)
        connectTxt = "Desconectar" if self.connected else "Conectar"
        self.btConnect.setText(connectTxt)

        enableDigital = bool(self.puc.digins) if self.connected else False
        enableAnalog = bool(self.puc.ads) if self.connected else False

        self.hasDigital = enableDigital
        self.hasAnalog = enableAnalog

        # Analog dependant items
        self.frameAnalog.setEnabled(enableAnalog)
        self.frameSyncCfg.setEnabled(enableAnalog)
        self.frameSyncGen.setEnabled(enableAnalog)
        self.frameSyncExec.setEnabled(enableAnalog)
        self.frameReadCapture.setEnabled(enableAnalog)

        # Digital dependant items
        self.frameDigital.setEnabled(enableDigital)
        self.cbSyncClkOutBit.setEnabled(enableDigital)
        self.cbSyncClkPulseBit.setEnabled(enableDigital)

    def norm(self,c):
        return [max(min(p, 10.0),-10.0) for p in c]

    def genLinear(self, nPoints, begin, end):
        b = begin
        e = end
        n = nPoints
        return self.norm([b+(e-b)*x/float(n-1) for x in range(n)])

    def genSinusoid(self, nPoints, realFreq, Vpp, freq, phase, off):
        A = Vpp/2.0
        Phi = phase*math.radians(phase)
        w = 2*math.pi*freq/realFreq
        f = lambda x: off+A*math.sin(w*x+Phi)
        return self.norm([f(x) for x in range(nPoints)])

    def genSquare(self, nPoints, realFreq, Vpp, freq, phase, off):
        sin = self.genSinusoid(nPoints, realFreq, Vpp, freq, phase, 0)
        A = Vpp/2.0
        f = lambda x: A if x > 0.0 else -A
        return self.norm([off+f(x) for x in sin])

    def genTrapezoid(self, nPoints, base, top, risePerc, topPerc):
        riseNPoints = int(nPoints*risePerc/100.0)
        topNPoints = int(nPoints*topPerc/100.0)
        fallNPoints = int(nPoints - topNPoints - riseNPoints)

        rise = self.genLinear(riseNPoints, base, top)
        plateau = self.genLinear(topNPoints, top, top)
        fall = self.genLinear(fallNPoints, top, base)

        return rise+plateau+fall

    # Analog panel

    def updateAI(self):
        self.txtAIValue.setText("{:-02.3f}".format(self.AI.read()))

    def on_btAIRead_released(self):
        self.updateAI()

    def updateAO(self):
        self.txtAOValue.setText("{:-02.3f}".format(self.AO.read()))

    def on_btAORead_released(self):
        self.updateAO()

    def on_sldAOValue_valueChanged(self):
        fmt="{:-02.3f}"
        self.txtAOValue.setText(fmt.format(float(self.sldAOValue.value())))
        self.on_btAOWrite_released()

    def on_btAOWrite_released(self):
        self.AO.write(float(self.txtAOValue.text()))
        self.updateAO()

    # Digital panel

    def updateDigital(self, var, boxes):
        v = var.read()
        for i, box in enumerate(boxes):
            c = QtCore.Qt.Checked if (v & (1<<i) ) != 0 else QtCore.Qt.Unchecked
            box.setCheckState(c)

    def updateDI(self):
        self.updateDigital(self.DI, self.DICheckBoxes)

    def on_btDIRead_released(self):
        self.updateDI()

    def updateDO(self):
        self.updateDigital(self.DO, self.DOCheckBoxes)

    def on_btDORead_released(self):
        self.updateDO()

    def on_chkDO0_stateChanged(self):
        self.writeDO()

    def on_chkDO1_stateChanged(self):
        self.writeDO()

    def on_chkDO2_stateChanged(self):
        self.writeDO()

    def on_chkDO3_stateChanged(self):
        self.writeDO()

    def on_chkDO4_stateChanged(self):
        self.writeDO()

    def on_chkDO5_stateChanged(self):
        self.writeDO()

    def on_chkDO6_stateChanged(self):
        self.writeDO()

    def on_chkDO7_stateChanged(self):
        self.writeDO()

    def writeDO(self):
        value = 0
        for i, chkbox in enumerate(self.DOCheckBoxes):
            if chkbox.isChecked():
                value += 1 << i
        self.DO.write(value)
        self.updateDO()

    # Sync Configuration Panel
    def on_cbSyncClkSrc_currentIndexChanged(self):

        # Frequency field  [Sources: 0:Timer, 1:External, 2:Serial]
        clkSource = self.cbSyncClkSrc.currentIndex()

        if clkSource == 0: # Timer
            self.spinSyncClkDiv.setEnabled(True)
            self.txtSyncFreq.setStyleSheet("border: 0px")
            self.txtSyncFreq.setReadOnly(True)
            self.on_spinSyncClkDiv_valueChanged()

        elif clkSource == 1: # External
            self.spinSyncClkDiv.setEnabled(False)
            self.txtSyncFreq.setStyleSheet("")
            self.txtSyncFreq.setReadOnly(False)
            self.txtSyncFreq.setText("")
            self.txtSyncFreq.setFocus()

        else: # Serial
            self.spinSyncClkDiv.setEnabled(False)
            self.txtSyncFreq.setStyleSheet("border: 0px")
            self.txtSyncFreq.setReadOnly(True)
            self.txtSyncFreq.setText("")

    def on_cbSyncPtSize_currentIndexChanged(self):
        widePoint = self.cbSyncPtSize.currentIndex() > 0
        self.spinSyncNPts.setMaximum(65536 if not widePoint else 32768)

    def on_spinSyncClkDiv_valueChanged(self):
        freqValue = TIMER_FREQ/(1+self.spinSyncClkDiv.value())
        self.txtSyncFreq.setText("{:02.2f}".format(freqValue))

    def checkSyncIO(self):
        execEn = self.chkSyncInEn.isChecked() or self.chkSyncOutEn.isChecked()
        self.frameSyncExec.setEnabled(execEn)

    def on_chkSyncInEn_stateChanged(self):
        self.checkSyncIO()

    def on_chkSyncOutEn_stateChanged(self):
        self.checkSyncIO()

    # Sync Execution Panel

    def on_btSyncStart_released(self):
        if self.puc.sync.getState()[0] == "PAUSED":
            self.puc.sync.start()
            self.timer.start()
            return

        cfg = pucsp.SyncConfig()
        if self.hasAnalog:
            cfg.inEnable = self.chkSyncInEn.isChecked()
            cfg.outEnable = self.chkSyncOutEn.isChecked()
            cfg.widePoint = bool(self.cbSyncPtSize.currentIndex())

        cfg.clkSource = self.cbSyncClkSrc.currentIndex()
        cfg.nPoints = self.spinSyncNPts.value()
        cfg.clkDivisor = self.spinSyncClkDiv.value()

        if self.hasDigital:
            clkOutBit = self.cbSyncClkOutBit.currentIndex()
            clkPulseBit = self.cbSyncClkPulseBit.currentIndex()
            cfg.clkOutEn = bool(clkOutBit)
            cfg.clkOutBit = 0 if not cfg.clkOutEn else clkOutBit-1
            cfg.clkPulseEn = bool(clkPulseBit)
            cfg.clkPulseBit = 0 if not cfg.clkPulseBit else clkPulseBit-1
        self.puc.sync.setConfig(cfg)

        self.puc.sync.start()
        self.lastSyncNPts = cfg.nPoints
        self.lastSyncWidePt = cfg.widePoint
        self.timer.start()

    def on_btSyncStep_released(self):
        self.puc.sync.step()

    def on_btSyncPause_released(self):
        self.puc.sync.pause()

    def on_btSyncStop_released(self):
        self.puc.sync.stop()

    # Curve generation panel

    def on_btGenFileSelect_released(self):
        self.txtGenFilePath.setText(PyQt4.QtGui.QFileDialog.getOpenFileName())

    def on_btSyncGenSend_released(self):
        self.setStatus("Enviando curva...")

        clkSrc = self.cbSyncClkSrc.currentIndex()
        nPoints = int(self.spinSyncNPts.value())
        if clkSrc == 0:
            realFreq = TIMER_FREQ/(float(self.spinSyncClkDiv.value())+1)
        elif clkSrc == 1:
            realFreq = float(self.txtSyncFreq.text())
        else:
            self.setStatus("Selecione uma fonte de clock diferente")
            return

        tab = self.tabGen.currentIndex()

        if tab == 0: # Periodic
            try:
                Vpp   = float(self.txtGenPerAmpl.text())
                freq  = float(self.txtGenPerFreq.text())
                off   = float(self.txtGenPerOff.text())
                phase = float(self.txtGenPerPhase.text())
                nPts  = nPoints
            except:
                self.setStatus("Valor(es) inválido(s) na aba 'Periódica'")
                return

            if self.cbGenPerType.currentIndex() == 0:
                pts = self.genSinusoid(nPoints, realFreq, Vpp, freq, phase, off)
            else:
                pts = self.genSquare(nPoints, realFreq, Vpp, freq, phase, off)

        elif tab == 1: # Trapezoid
            try:
                base    = float(self.txtGenTrapBaseV.text())
                top     = float(self.txtGenTrapTopV.text())
                rise    = float(self.txtGenTrapRiseTime.text())
                plateau = float(self.txtGenTrapPlateauTime.text())
                fall    = float(self.txtGenTrapFallTime.text())
                pts     = self.genTrapezoid(nPoints, base, top, rise, plateau)
                nPts    = nPoints
            except:
                self.setStatus("Valor(es) inválido(s) na aba 'Trapezóide'")
                return

        elif tab == 2: # Linear
            try:
                begin = float(self.txtGenLinStartV.text())
                end   = float(self.txtGenLinEndV.text())
                pts   = self.genLinear(nPoints, begin, end)
                nPts  = nPoints
            except:
                self.setStatus("Valor(es) inválido(s) na aba 'Linear'")
                return

        else: # File
            path = self.txtGenFilePath.text()
            try:
                with open(path) as f:
                    pts = [float(line) for line in f]
                    maxPts = self.spinSyncNPts.maximum()
                    if len(pts) > maxPts:
                        pts = pts[:maxPts]
                    nPts = len(pts)
            except IOError:
                self.setStatus("Falha ao abrir '{}'".format(path))
                return
            except ValueError:
                self.setStatus("Falha ao converter valor dentro do arquivo")
                return
            except:
                self.setStatus("Falha não determinada ao se processar o arquivo")
                return

        widePoint = self.cbSyncPtSize.currentIndex() == 1
        self.puc.sync.outCurve.write(pts, widePoint)
        self.spinSyncNPts.setValue(nPts)
        self.setStatus("{} pontos enviados com sucesso".format(nPts))

    def checkTrap(self, txt1, txt2):
        try:
            value1 = int(txt1.text())
        except:
            value1 = 0

        if value1 < 0:
            value1 = 0

        value2 = int(txt2.text())
        if value1 + value2 > 100:
            value1 = 100 - value2

        txt1.setText(str(value1))

        self.txtGenTrapFallTime.setText(str(100-value1-value2))

    def on_txtGenTrapRiseTime_editingFinished(self):
        txt1 = self.txtGenTrapRiseTime
        txt2 = self.txtGenTrapPlateauTime
        self.checkTrap(txt1, txt2)

    def on_txtGenTrapPlateauTime_editingFinished(self):
        txt1 = self.txtGenTrapPlateauTime
        txt2 = self.txtGenTrapRiseTime
        self.checkTrap(txt1, txt2)

    def on_btReadCaptureFileChoose_released(self):
        self.txtReadCaptureFilePath.setText(QtGui.QFileDialog.getOpenFileName())

    def on_btReadCapture_released(self):
        if self.lastSyncWidePt == None:
            self.setStatus("Nenhuma curva executada ainda")
            return

        path = self.txtReadCaptureFilePath.text()
        pts = self.puc.sync.inCurve.read(self.lastSyncNPts, self.lastSyncWidePt)
        npts = len(pts)
        try:
            with open(path, 'w') as f:
                for pt in pts:
                    f.write("{:-02.3f}\n".format(pt))
            self.setStatus("{} pontos lidos para o arquivo".format(npts))
        except:
            self.setStatus("Falha ao manipular arquivo {}".format(path))


    def on_btReset_released(self):
        try:
            self.puc.reset()
        except:
            pass
        time.sleep(.5)
        self.setStatus("Reset enviado")

app = PyQt4.QtGui.QApplication(sys.argv)
client = Client()
client.exec_()

