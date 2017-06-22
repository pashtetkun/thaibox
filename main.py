# -*- coding: utf-8 -*-
''' TODO: 1. Сделать файл конфига в xml '''
''' TODO: 2. Сделать проверку существования базы данных '''
'''# TODO: 2.1 Сделать диалог выбора пути к базе, если она не находится по пути указанном в конфиге'''
'''# TODO: 2.2 Занести новый путь к базе в файл конфигурации'''
'''# TODO: 3. Если база не существует, то создать ее по пути указанном в конфиге'''
import sys, os
from PyQt5 import QtGui, QtWidgets
from tray import SystemTray
from config import Config as cfg
from database import Dbase as db

def main():

	app = QtWidgets.QApplication([])
	app.setQuitOnLastWindowClosed(False)

	# Get config parameters
	conf = cfg()
	conf.readconfig()
	# Connect to database
	base = db()

	trayIcon = SystemTray()
	trayIcon.show()

	app.exec_()

if __name__ == "__main__":
	main()