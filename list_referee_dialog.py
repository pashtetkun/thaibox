import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from list_referee_slots import ListRefereeSlots
from database import Dbase as db
from add_referee_dialog import AddRefereeDialog

class ListRefereeDialog(QDialog):

	def __init__(self):
		super(ListRefereeDialog, self).__init__()
		self.ui = ListRefereeSlots()
		self.ui.setupUi(self)
		self.ui.tableWidget.setColumnHidden(0, True)
		self.ui.edit.clicked.connect(self.edit_pressed)
		self.ui.cancel.clicked.connect(self.cancel_pressed)

		database = db()
		row = database.select("SELECT referee.id, referee.fio, refereepos.position, region.region, refereecat.category FROM referee, refereepos, region, refereecat WHERE referee.position=refereepos.id AND referee.region=region.id AND referee.category=refereecat.id")
		r = 0
		for i in row:
			self.ui.tableWidget.setRowCount(len(row))
			col = 0
			for y in i:
				newitem = QtWidgets.QTableWidgetItem(str(y))
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

		edit_referee = AddRefereeDialog(True)
		edit_referee.edit_referee(items)
		edit_referee.exec_()

		# Get new data from base
		database = db()
		row = database.select("SELECT referee.id, referee.fio, refereepos.position, region.region, refereecat.category FROM referee, refereepos, region, refereecat WHERE referee.id=\"" + str(items[0]) + "\" AND referee.position=refereepos.id AND referee.region=region.id AND referee.category=refereecat.id")
		for i in row:
			col =0
			for y in i:
				newitem = QtWidgets.QTableWidgetItem(str(y))
				self.ui.tableWidget.setItem(editable_row, col, newitem)
				self.ui.tableWidget.resizeColumnToContents(col)
				col += 1

		return

	def cancel_pressed(self):

		self.close()

