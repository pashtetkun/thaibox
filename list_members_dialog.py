import sys, os
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
# from list_members_slots import ListRefereeSlots
from list_members import Ui_Dialog as listmem
from database import Dbase as db
from add_member_dialog import AddMemberDialog
import re


class ListMemberSlots(listmem):

	def __init__(self):

		return


class ListMemberDialog(QDialog):

	def __init__(self):
		super(ListMemberDialog, self).__init__()
		self.ui = ListMemberSlots()
		self.ui.setupUi(self)
		self.ui.tableWidget.setColumnHidden(0, True)
		self.ui.edit.clicked.connect(self.edit_pressed)
		self.ui.cancel.clicked.connect(self.cancel_pressed)

		database = db()
		row = database.select("SELECT members.id, members.fio, members.bday, sex.sex, weightcategory.wcategory, category.category, members.club, members.region, members.city, members.trainer FROM members, sex, weightcategory, category WHERE members.sex=sex.id AND members.weight=weightcategory.id AND members.category=category.id")
		r = 0
		for i in row:
			self.ui.tableWidget.setRowCount(len(row))
			col = 0
			for y in i:
				newitem = QtWidgets.QTableWidgetItem(re.sub(r'\\', r'', str(y)))
				newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.ui.tableWidget.setItem(r, col, newitem)
				self.ui.tableWidget.resizeColumnToContents(col)
				col += 1
			r += 1

	def update_table(self, row):

		return

	def edit_pressed(self):

		# Get data from row
		editable_row = self.ui.tableWidget.currentRow()
		col = 0
		col_count = self.ui.tableWidget.columnCount()
		items = []
		while col < col_count:
			items.append(self.ui.tableWidget.item(editable_row, col).text())
			col += 1

		edit_members = AddMemberDialog(True)
		edit_members.edit_member(items)
		edit_members.exec_()

		'''# TODO: Неправильно работает, проверить'''
		# Get new data from base
		database = db()
		row = database.select("SELECT members.id, members.fio, members.bday, sex.sex, weightcategory.wcategory, category.category, members.club, members.region, members.city, members.trainer FROM members, sex, weightcategory, category WHERE members.id=\"" + str(items[0]) + "\" AND members.sex=sex.id AND members.weight=weightcategory.id AND members.category=category.id")
		for i in row:
			col =0
			for y in i:
				newitem = QtWidgets.QTableWidgetItem(re.sub(r'\\', r'', str(y)))
				newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.ui.tableWidget.setItem(editable_row, col, newitem)
				self.ui.tableWidget.resizeColumnToContents(col)
				col += 1

		return

	def cancel_pressed(self):

		self.close()

