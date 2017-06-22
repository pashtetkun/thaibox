# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'input_error.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 177)
        self.LString = QtWidgets.QLabel(Dialog)
        self.LString.setGeometry(QtCore.QRect(10, 39, 381, 61))
        self.LString.setLocale(QtCore.QLocale(QtCore.QLocale.Russian, QtCore.QLocale.Russia))
        self.LString.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.LString.setWordWrap(True)
        self.LString.setObjectName("LString")
        self.LDigit = QtWidgets.QLabel(Dialog)
        self.LDigit.setGeometry(QtCore.QRect(10, 99, 381, 31))
        self.LDigit.setLocale(QtCore.QLocale(QtCore.QLocale.Russian, QtCore.QLocale.Russia))
        self.LDigit.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.LDigit.setWordWrap(True)
        self.LDigit.setObjectName("LDigit")
        self.LTitle = QtWidgets.QLabel(Dialog)
        self.LTitle.setGeometry(QtCore.QRect(10, 10, 381, 21))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.LTitle.setFont(font)
        self.LTitle.setTextFormat(QtCore.Qt.AutoText)
        self.LTitle.setScaledContents(False)
        self.LTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.LTitle.setObjectName("LTitle")
        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(160, 140, 80, 24))
        self.okButton.setObjectName("okButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Введены недопустимые символы"))
        self.LString.setText(_translate("Dialog", "Для ввода в текстовые поля допустимы только символы русского или английского алфавитов (а-я, А-Я, a-z, A-Z), цифры (0-9), разделительная точка, символ двойных кавычек \" и символ подчеркивания _"))
        self.LDigit.setText(_translate("Dialog", "Для ввода в числовые поля допустимы только цифры (0-9) и разделительная точка."))
        self.LTitle.setText(_translate("Dialog", "Недопустимый ввод!"))
        self.okButton.setText(_translate("Dialog", "Ok"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

