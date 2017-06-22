# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_base.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 108)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 381, 71))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.Ok = QtWidgets.QPushButton(Dialog)
        self.Ok.setGeometry(QtCore.QRect(310, 70, 79, 24))
        self.Ok.setObjectName("Ok")
        self.Cancel = QtWidgets.QPushButton(Dialog)
        self.Cancel.setGeometry(QtCore.QRect(220, 70, 79, 24))
        self.Cancel.setObjectName("Cancel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "База данных"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p>По указанному пути, в файле конфигурации, база данных не существует. Нажмите &quot;Отменить&quot;, что бы указать путь к существующей базе данных, или &quot;Создать&quot;, что бы создать базу данных заново.</p></body></html>"))
        self.Ok.setText(_translate("Dialog", "Отменить"))
        self.Cancel.setText(_translate("Dialog", "Создать"))

