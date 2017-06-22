# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'inputtext.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 76)
        self.inputtext = QtWidgets.QLineEdit(Dialog)
        self.inputtext.setGeometry(QtCore.QRect(10, 10, 381, 20))
        self.inputtext.setObjectName("inputtext")
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setGeometry(QtCore.QRect(220, 40, 162, 26))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.ok = QtWidgets.QPushButton(self.splitter)
        self.ok.setObjectName("ok")
        self.cancel = QtWidgets.QPushButton(self.splitter)
        self.cancel.setObjectName("cancel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.ok.setText(_translate("Dialog", "Ok"))
        self.cancel.setText(_translate("Dialog", "Отменить"))

