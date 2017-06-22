# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_referee.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 174)
        self.fioEdit = QtWidgets.QLineEdit(Dialog)
        self.fioEdit.setGeometry(QtCore.QRect(45, 10, 341, 24))
        self.fioEdit.setObjectName("fioEdit")
        self.positionList = QtWidgets.QComboBox(Dialog)
        self.positionList.setEnabled(True)
        self.positionList.setGeometry(QtCore.QRect(127, 40, 261, 24))
        self.positionList.setObjectName("positionList")
        self.fio = QtWidgets.QLabel(Dialog)
        self.fio.setGeometry(QtCore.QRect(10, 12, 29, 20))
        self.fio.setObjectName("fio")
        self.position = QtWidgets.QLabel(Dialog)
        self.position.setGeometry(QtCore.QRect(10, 42, 112, 20))
        self.position.setObjectName("position")
        self.region = QtWidgets.QLabel(Dialog)
        self.region.setGeometry(QtCore.QRect(10, 73, 44, 20))
        self.region.setObjectName("region")
        self.regionList = QtWidgets.QComboBox(Dialog)
        self.regionList.setGeometry(QtCore.QRect(58, 71, 331, 24))
        self.regionList.setObjectName("regionList")
        self.category = QtWidgets.QLabel(Dialog)
        self.category.setGeometry(QtCore.QRect(10, 107, 137, 20))
        self.category.setObjectName("category")
        self.categoryList = QtWidgets.QComboBox(Dialog)
        self.categoryList.setGeometry(QtCore.QRect(153, 105, 236, 24))
        self.categoryList.setObjectName("categoryList")
        self.update = QtWidgets.QPushButton(Dialog)
        self.update.setGeometry(QtCore.QRect(220, 140, 77, 26))
        self.update.setObjectName("update")
        self.cancel = QtWidgets.QPushButton(Dialog)
        self.cancel.setGeometry(QtCore.QRect(303, 140, 77, 26))
        self.cancel.setObjectName("cancel")
        self.add = QtWidgets.QPushButton(Dialog)
        self.add.setGeometry(QtCore.QRect(220, 140, 77, 26))
        self.add.setObjectName("add")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.fio.setText(_translate("Dialog", "ФИО"))
        self.position.setText(_translate("Dialog", "Должность судьи"))
        self.region.setText(_translate("Dialog", "Регион"))
        self.category.setText(_translate("Dialog", "Судейская категория"))
        self.update.setText(_translate("Dialog", "Обновить"))
        self.cancel.setText(_translate("Dialog", "Отменить"))
        self.add.setText(_translate("Dialog", "Добавить"))

