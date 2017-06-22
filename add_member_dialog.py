import sys
import os
import re
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog
from add_member_slots import AddMemberSlots
from database import Dbase as db
from validator import Valid
from input_error_slots import InputErrorSlots


class InputError(QDialog):

	def __init__(self):
		super(InputError, self).__init__()
		self.ui = InputErrorSlots()
		self.ui.setupUi(self)
		self.ui.okButton.clicked.connect(self.okPressed)

		return

	def okPressed(self):

		self.close()


class AddMemberDialog(QDialog):

	def __init__(self, update=False):

		super(AddMemberDialog, self).__init__()
		self.id = 0
		self.ui = AddMemberSlots()
		self.ui.setupUi(self)
		self.ui.addButton.clicked.connect(self.add_pressed)
		self.ui.updateButton.clicked.connect(self.update_pressed)
		self.ui.cancelButton.clicked.connect(self.cancel_pressed)

		'''# TODO: заполнить списки выбора'''
		database = db()
		row = database.select("SELECT * FROM sex")
		for i in row:
			self.ui.sexCBox.addItem(i[1])

		row = database.select("SELECT * FROM weightcategory")
		for i in row:
			self.ui.weightcatCBox.addItem(i[1])

		row = database.select("SELECT * FROM category")
		for i in row:
			self.ui.categoryCBox.addItem(i[1])

		if update:
			self.ui.addButton.hide()
			self.setWindowTitle("Изменить данные спортсмена")
		else:
			self.ui.updateButton.hide()
			self.setWindowTitle("Добавить спортсмена")
		return

	def valid(self, res):

		if not res:
			# TODO: Вывести диалог с ошибкой
			val = InputError()
			val.exec_()

			return False

		return True

	def add_pressed(self):

		database = db()
		validator = Valid()
		self.fio = self.ui.fioEdit.text()
		bday_temp = self.ui.dateEdit.date()
		self.bday = bday_temp.toPyDate()
		self.sex = database.select("SELECT id FROM sex WHERE sex=\"" + self.ui.sexCBox.itemText(self.ui.sexCBox.currentIndex()) + "\"")
		self.weight = self.ui.weightcatCBox.itemText(self.ui.weightcatCBox.currentIndex())
		self.weightid = database.select("SELECT id FROM weightcategory WHERE wcategory=\"" + self.ui.weightcatCBox.itemText(self.ui.weightcatCBox.currentIndex()) + "\"") # self.ui.weightEdit.text()
		self.category = database.select("SELECT id FROM category WHERE category=\"" + self.ui.categoryCBox.itemText(self.ui.categoryCBox.currentIndex()) + "\"")
		# if not self.valid(validator.validDigit(self.weight)):
		# 	return
		#self.category = self.ui.categoryEdit.text()
		self.club = self.ui.clubEdit.text()
		self.trainer = self.ui.trainerEdit.text()
		self.region = self.ui.regionEdit.text()
		self.city = self.ui.cityEdit.text()
		if not (self.valid(validator.validSString(self.fio, self.weight, self.club, self.trainer, self.region, self.city))):
			return


		# TODO: сделать проверку корректности введенных данных QValidator
		'''# TODO: настроить фокус на поле'''

		database.ins_upd('INSERT INTO members(fio, bday, sex, weight, category, club, trainer, region, city) VALUES (\'' + validator.escape(self.fio) + '\', \'' + self.bday.strftime('%Y-%m-%d') + '\', \'' + str(self.sex[0][0]) + '\', \'' + str(self.weightid[0][0]) + '\', \'' + str(self.category[0][0]) + '\', \'' + validator.escape(self.club) + '\', \'' + validator.escape(self.trainer) + '\', \'' + validator.escape(self.region) + '\', \'' + validator.escape(self.city) + '\')')


		self.ui.fioEdit.clear()
		self.ui.dateEdit.setDate(QtCore.QDate())
		self.ui.sexCBox.setCurrentIndex(0)
		# self.ui.weightEdit.clear()
		# self.ui.categoryEdit.clear()
		self.ui.clubEdit.clear()
		self.ui.trainerEdit.clear()
		self.ui.regionEdit.clear()
		self.ui.cityEdit.clear()
		self.ui.fioEdit.setFocus()

		return

	def update_pressed(self):

		database = db()
		validator = Valid()

		# row = database.select("SELECT * FROM referee WHERE id=\"" + self.id + "\"")
		self.fio = self.ui.fioEdit.text()
		self.sex = database.select("SELECT id FROM sex WHERE sex=\"" + self.ui.sexCBox.itemText(self.ui.sexCBox.currentIndex()) + "\"")
		self.weightid = database.select("SELECT id FROM weightcategory WHERE wcategory=\"" + self.ui.weightcatCBox.itemText(self.ui.weightcatCBox.currentIndex()) + "\"")
		bday_temp = self.ui.dateEdit.date()
		self.bday = bday_temp.toPyDate()
		self.category = database.select("SELECT id FROM category WHERE category=\"" + self.ui.categoryCBox.itemText(self.ui.categoryCBox.currentIndex()) + "\"")
		self.club = self.ui.clubEdit.text()
		self.trainer = self.ui.trainerEdit.text()
		self.region = self.ui.regionEdit.text()
		self.city = self.ui.cityEdit.text()
		database.ins_upd('UPDATE members SET fio=\'' + validator.escape(self.fio) + '\', bday=\'' + self.bday.strftime('%Y-%m-%d') + '\', sex=\'' + str(self.sex[0][0]) + '\', weight=\'' + str(self.weightid[0][0]) + '\', category=\'' + str(self.category[0][0]) + '\', club=\'' + validator.escape(self.club) + '\', trainer=\'' + validator.escape(self.trainer) + '\', region=\'' + validator.escape(self.region) + '\', city=\'' + validator.escape(self.city) + '\' WHERE id=\'' + str(self.id) + '\'')
		# database.ins_upd("UPDATE referee SET fio=\"" + self.fio + "\", position=\"" + str(self.position[0][0]) + "\", region=\"" + str(self.region[0][0]) + "\", category=\"" + str(self.category[0][0]) + "\" WHERE id=\"" + str(self.id) + "\"")


		self.close()

	def cancel_pressed(self):

		self.close()

	def edit_member(self, item=[]):

		self.id = item[0]
		self.ui.fioEdit.setText(item[1])
		self.ui.dateEdit.setDate(QtCore.QDate.fromString(item[2], 'yyyy-MM-dd'))
		self.ui.sexCBox.setCurrentIndex(self.ui.sexCBox.findText(item[3]))
		self.ui.weightcatCBox.setCurrentIndex(self.ui.weightcatCBox.findText(item[4]))
		self.ui.categoryCBox.setCurrentIndex(self.ui.categoryCBox.findText(item[5]))
		self.ui.trainerEdit.setText(item[9])
		self.ui.regionEdit.setText(item[7])
		self.ui.cityEdit.setText(item[8])
		self.ui.clubEdit.setText(item[6])


