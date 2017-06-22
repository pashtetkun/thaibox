from record_list import Ui_Dialog as rec
from PyQt5.QtWidgets import QDialog
from inputtext_slots import AddRecordSlots

class AddRecord(QDialog):

	def __init__(self, title):
		super(AddRecord, self).__init__()
		self.ui = AddRecordSlots()
		self.ui.setupUi(self)
		self.ui.ok.clicked.connect(self.ok_pressed)
		self.ui.cancel.clicked.connect(self.cancel_pressed)
		self.setWindowTitle(title)
		self.text = ''

	def ok_pressed(self):

		self.text = self.ui.getText()
		self.close()

	def cancel_pressed(self):

		self.close()


class CreateRecordSlots(rec):

	def __init__(self):

		return

	def Add(self, title):

		self.addrecord = AddRecord(title)
		self.addrecord.exec_()

		return self.addrecord.text
