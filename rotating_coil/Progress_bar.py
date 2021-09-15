# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Progress_bar.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_progress_bar(object):
    def setupUi(self, progress_bar):
        progress_bar.setObjectName("progress_bar")
        progress_bar.resize(423, 115)
        self.progressBar = QtWidgets.QProgressBar(progress_bar)
        self.progressBar.setGeometry(QtCore.QRect(40, 50, 351, 31))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(progress_bar)
        self.label.setGeometry(QtCore.QRect(150, 10, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(progress_bar)
        QtCore.QMetaObject.connectSlotsByName(progress_bar)

    def retranslateUi(self, progress_bar):
        _translate = QtCore.QCoreApplication.translate
        progress_bar.setWindowTitle(_translate("progress_bar", "Progress Bar"))
        self.label.setText(_translate("progress_bar", "Cycling progress"))

