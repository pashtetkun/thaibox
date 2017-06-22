# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'record_list.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 260)
        self.recordlist = QtWidgets.QListWidget(Dialog)
        self.recordlist.setGeometry(QtCore.QRect(10, 10, 291, 241))
        self.recordlist.setObjectName("recordlist")
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setGeometry(QtCore.QRect(310, 197, 81, 51))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.add = QtWidgets.QPushButton(self.splitter)
        self.add.setObjectName("add")
        self.cancel = QtWidgets.QPushButton(self.splitter)
        self.cancel.setObjectName("cancel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Список категорий"))
        self.add.setText(_translate("Dialog", "Добавить"))
        self.cancel.setText(_translate("Dialog", "Отмена"))

