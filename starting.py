# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'starting.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialog(object):
    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        dialog.resize(403, 74)
        self.progress = QtWidgets.QProgressBar(dialog)
        self.progress.setGeometry(QtCore.QRect(10, 40, 381, 23))
        self.progress.setProperty("value", 24)
        self.progress.setObjectName("progress")
        self.start = QtWidgets.QLabel(dialog)
        self.start.setGeometry(QtCore.QRect(10, 10, 371, 24))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.start.setFont(font)
        self.start.setObjectName("start")

        self.retranslateUi(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("dialog", "Создание базы"))
        self.start.setText(_translate("dialog", "Идет первоначальная настройка базы данных..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_dialog()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())

