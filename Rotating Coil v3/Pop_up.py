# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Pop_up.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Pop_Up(object):
    def setupUi(self, Pop_Up):
        Pop_Up.setObjectName("Pop_Up")
        Pop_Up.resize(441, 407)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Images/imagens/magnetic.PNG"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Pop_Up.setWindowIcon(icon)
        self.label = QtWidgets.QLabel(Pop_Up)
        self.label.setGeometry(QtCore.QRect(10, -10, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.line = QtWidgets.QFrame(Pop_Up)
        self.line.setGeometry(QtCore.QRect(10, 20, 421, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.bB_ok_cancel = QtWidgets.QDialogButtonBox(Pop_Up)
        self.bB_ok_cancel.setGeometry(QtCore.QRect(150, 380, 156, 23))
        self.bB_ok_cancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bB_ok_cancel.setObjectName("bB_ok_cancel")
        self.le_magnet_name = QtWidgets.QLineEdit(Pop_Up)
        self.le_magnet_name.setGeometry(QtCore.QRect(167, 80, 161, 21))
        self.le_magnet_name.setText("")
        self.le_magnet_name.setObjectName("le_magnet_name")
        self.label_134 = QtWidgets.QLabel(Pop_Up)
        self.label_134.setGeometry(QtCore.QRect(87, 70, 71, 41))
        self.label_134.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_134.setObjectName("label_134")
        self.label_166 = QtWidgets.QLabel(Pop_Up)
        self.label_166.setGeometry(QtCore.QRect(67, 100, 91, 41))
        self.label_166.setObjectName("label_166")
        self.le_temperature = QtWidgets.QLineEdit(Pop_Up)
        self.le_temperature.setGeometry(QtCore.QRect(167, 110, 161, 21))
        self.le_temperature.setObjectName("le_temperature")
        self.groupBox_23 = QtWidgets.QGroupBox(Pop_Up)
        self.groupBox_23.setGeometry(QtCore.QRect(20, 250, 400, 120))
        self.groupBox_23.setObjectName("groupBox_23")
        self.te_meas_details = QtWidgets.QTextEdit(self.groupBox_23)
        self.te_meas_details.setGeometry(QtCore.QRect(15, 20, 370, 90))
        self.te_meas_details.setObjectName("te_meas_details")
        self.label_167 = QtWidgets.QLabel(Pop_Up)
        self.label_167.setGeometry(QtCore.QRect(107, 130, 51, 41))
        self.label_167.setObjectName("label_167")
        self.cb_operator = QtWidgets.QComboBox(Pop_Up)
        self.cb_operator.setGeometry(QtCore.QRect(167, 140, 161, 22))
        self.cb_operator.setObjectName("cb_operator")
        self.cb_operator.addItem("")
        self.cb_operator.addItem("")
        self.cb_operator.addItem("")
        self.cb_operator.addItem("")
        self.cb_operator.addItem("")
        self.cb_operator.addItem("")
        self.label_49 = QtWidgets.QLabel(Pop_Up)
        self.label_49.setGeometry(QtCore.QRect(77, 170, 81, 25))
        self.label_49.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_49.setObjectName("label_49")
        self.cb_magnet_model = QtWidgets.QComboBox(Pop_Up)
        self.cb_magnet_model.setGeometry(QtCore.QRect(167, 170, 161, 21))
        self.cb_magnet_model.setObjectName("cb_magnet_model")
        self.cb_magnet_model.addItem("")
        self.cb_magnet_model.addItem("")
        self.cb_magnet_model.addItem("")
        self.cb_magnet_model.addItem("")
        self.cb_magnet_model.addItem("")

        self.retranslateUi(Pop_Up)
        QtCore.QMetaObject.connectSlotsByName(Pop_Up)

    def retranslateUi(self, Pop_Up):
        _translate = QtCore.QCoreApplication.translate
        Pop_Up.setWindowTitle(_translate("Pop_Up", "Collect"))
        self.label.setText(_translate("Pop_Up", "Measurement features"))
        self.label_134.setText(_translate("Pop_Up", "Magnet Name:"))
        self.label_166.setText(_translate("Pop_Up", "Temperature (°C):"))
        self.groupBox_23.setTitle(_translate("Pop_Up", "Details"))
        self.label_167.setText(_translate("Pop_Up", "Operator:"))
        self.cb_operator.setItemText(0, _translate("Pop_Up", "James Citadini"))
        self.cb_operator.setItemText(1, _translate("Pop_Up", "Lucas Balthazar"))
        self.cb_operator.setItemText(2, _translate("Pop_Up", "Luana Vilela"))
        self.cb_operator.setItemText(3, _translate("Pop_Up", "Lidia Toledo"))
        self.cb_operator.setItemText(4, _translate("Pop_Up", "Reinaldo Basilio"))
        self.cb_operator.setItemText(5, _translate("Pop_Up", "Vitor Soares"))
        self.label_49.setText(_translate("Pop_Up", "Magnet Model:"))
        self.cb_magnet_model.setItemText(0, _translate("Pop_Up", "No Model"))
        self.cb_magnet_model.setItemText(1, _translate("Pop_Up", "Dipole"))
        self.cb_magnet_model.setItemText(2, _translate("Pop_Up", "Quadrupole"))
        self.cb_magnet_model.setItemText(3, _translate("Pop_Up", "Sextupole"))
        self.cb_magnet_model.setItemText(4, _translate("Pop_Up", "Skew Quadrupole"))

import resource_file_rc