import sys, os
from PyQt5.QtWidgets import QDialog
from add_referee_slots import AddRefereeSlots
from database import Dbase as db


class AddRefereeDialog(QDialog):

	def __init__(self, update=False):
		super(AddRefereeDialog, self).__init__()
		self.id = 0
		self.ui = AddRefereeSlots()
		self.ui.setupUi(self)
		self.ui.add.clicked.connect(self.add_pressed)
		self.ui.cancel.clicked.connect(self.cancel_pressed)
		self.ui.update.clicked.connect(self.update_pressed)

		'''TODO: заполнить списки выбора'''
		database = db()
		row = database.select("SELECT * FROM refereepos")
		for i in row:
			self.ui.positionList.addItem(i[1])

		row = database.select("SELECT * FROM region")
		for i in row:
			self.ui.regionList.addItem(i[1])

		row = database.select("SELECT * FROM refereecat")
		for i in row:
			self.ui.categoryList.addItem(i[1])

		if update:
			self.ui.add.hide()
			self.setWindowTitle("Update referee")
		else:
			self.ui.update.hide()
			self.setWindowTitle("Add referee")

	def add_pressed(self):

		self.fio = self.ui.fioEdit.text()

		database = db()
		''' TODO: при добавлении id из связанных таблиц проверять соответсвие текста и id'''
		# TODO: упростить вызов базы данных (вместо трех селектов добавить их в insert)
		self.position = database.select("SELECT id FROM refereepos WHERE \"position\"=\"" + self.ui.positionList.itemText(self.ui.positionList.currentIndex()) + "\"")
		self.region = database.select("SELECT id FROM region WHERE \"region\"=\"" + self.ui.regionList.itemText(self.ui.regionList.currentIndex()) + "\"")
		self.category = database.select("SELECT id FROM refereecat WHERE \"category\"=\"" + self.ui.categoryList.itemText(self.ui.categoryList.currentIndex()) + "\"")
		database.ins_upd("INSERT INTO referee(fio, position, region, category) VALUES(\"" + self.fio + "\", " + str(self.position[0][0]) + ", " + str(self.region[0][0]) + ", " + str(self.category[0][0]) + ")")

		self.ui.positionList.setCurrentIndex(0)
		self.ui.regionList.setCurrentIndex(0)
		self.ui.categoryList.setCurrentIndex(0)
		self.ui.fioEdit.clear()

		return

	def update_pressed(self):

		database = db()
		#row = database.select("SELECT * FROM referee WHERE id=\"" + self.id + "\"")
		self.fio = self.ui.fioEdit.text()
		self.position = database.select("SELECT id FROM refereepos WHERE \"position\"=\"" + self.ui.positionList.itemText(self.ui.positionList.currentIndex()) + "\"")
		self.region = database.select("SELECT id FROM region WHERE \"region\"=\"" + self.ui.regionList.itemText(self.ui.regionList.currentIndex()) + "\"")
		self.category = database.select("SELECT id FROM refereecat WHERE \"category\"=\"" + self.ui.categoryList.itemText(self.ui.categoryList.currentIndex()) + "\"")
		database.ins_upd("UPDATE referee SET fio=\"" + self.fio + "\", position=\"" + str(self.position[0][0]) + "\", region=\"" + str(self.region[0][0]) + "\", category=\"" + str(self.category[0][0]) + "\" WHERE id=\"" + str(self.id) + "\"")

		self.close()

	def cancel_pressed(self):

		self.close()

	def edit_referee(self, items=[]):

		# позиции данных в items - [0](int) referee.id, [1](text) referee.fio, [2](text) referee.position,
		# [3](text) referee.region, [4](text) referee.category

		self.id = items[0]
		self.ui.fioEdit.setText(items[1])
		self.ui.positionList.setCurrentIndex(self.ui.positionList.findText(items[2]))
		self.ui.regionList.setCurrentIndex(self.ui.regionList.findText(items[3]))
		self.ui.categoryList.setCurrentIndex(self.ui.categoryList.findText(items[4]))
		return
