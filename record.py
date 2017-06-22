import sys, os
from PyQt5.QtWidgets import QDialog
from record_slots import CreateRecordSlots
from database import Dbase as db
from validator import Valid
from input_error_slots import InputErrorSlots


class InputError(QDialog):

	def __init__(self):
		super(InputError,self).__init__()
		self.ui = InputErrorSlots()
		self.ui.setupUi(self)
		self.ui.okButton.clicked.connect(self.okPressed)

		return

	def okPressed(self):

		self.close()

class RecordDialog(QDialog):

	# TODO: проверить правильность ввода данных

	def __init__(self, id=''):
		super(RecordDialog, self).__init__()
		self.id = id
		self.ui = CreateRecordSlots()
		self.ui.setupUi(self)
		self.ui.add.clicked.connect(self.addrecord_pressed)
		self.ui.cancel.clicked.connect(self.cancel_pressed)

		'''# TODO: Заполнить список категорий'''

		if self.id == "category":
			self.setWindowTitle("Список судейских категорий")
			database = db()
			row = database.select("SELECT * FROM refereecat")

			for i in row:
				self.ui.recordlist.addItem(i[1])

		elif self.id == "position":
			self.setWindowTitle("Список должностей судей")
			database = db()
			row = database.select("SELECT * FROM refereepos")

			for i in row:
				self.ui.recordlist.addItem(i[1])

		elif self.id == "region":
			self.setWindowTitle("Список регионов")
			database = db()
			row = database.select("SELECT * FROM region")

			for i in row:
				self.ui.recordlist.addItem(i[1])

		elif self.id == "weight":
			self.setWindowTitle("Список весовых категорий")
			database = db()
			row = database.select("SELECT * FROM weightcategory")

			for i in row:
				self.ui.recordlist.addItem(i[1])

	def valid(self, res):

		if not res:
			'''# TODO: Вывести диалог с ошибкой'''
			val = InputError()
			val.exec_()

			return False

		return True

	def addrecord_pressed(self):

		validator = Valid()

		if self.id == "category":
			text = self.ui.Add("Добавить категорию")
			if not self.valid(validator.validString(text)):
				return

			self.ui.recordlist.addItem(text)

			database = db()
			row = database.ins_upd("INSERT INTO refereecat(category) VALUES(\"" + text + "\")")

		elif self.id == "position":

			text = self.ui.Add("Добавить позицию")
			if not self.valid(validator.validString(text)):
				return

			self.ui.recordlist.addItem(text)

			database = db()
			row = database.ins_upd("INSERT INTO refereepos(position) VALUES(\"" + text + "\")")

		elif self.id == "region":

			text = self.ui.Add("Добавить регион")
			if not self.valid(validator.validString(text)):
				return

			self.ui.recordlist.addItem(text)

			database = db()
			row = database.ins_upd("INSERT INTO region(region) VALUES(\"" + text + "\")")

		elif self.id == "weight":

			text = self.ui.Add("Добавить весовую категорию")
			if not self.valid(validator.validString(text)):
				return

			self.ui.recordlist.addItem(text)

			database = db()
			row = database.ins_upd("INSERT INTO weightcategory(wcategory) VALUES(\"" + text + "\")")

	def cancel_pressed(self):

		self.close()
