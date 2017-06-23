from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog
from meet import Ui_Dialog as createmeeting
from database import Dbase as db
from database_manager import DbManager as dbmanager
from validator import Valid
import re
from input_error_slots import InputErrorSlots
import random


class InputError(QDialog):

	def __init__(self):
		super(InputError, self).__init__()
		self.ui = InputErrorSlots()
		self.ui.setupUi(self)
		self.ui.okButton.clicked.connect(self.okPressed)

		return

	def okPressed(self):

		self.close()


class CreateMeetingSlots(createmeeting):

	def __init__(self):

		return


class MeetingDialog(QDialog):

	def __init__(self, meet = []):

		super(MeetingDialog, self).__init__()
		self.id = 0
		self.ui = CreateMeetingSlots()
		self.ui.setupUi(self)
		self.ui.addButton.clicked.connect(self.add_pressed)
		self.ui.removeButton.clicked.connect(self.remove_pressed)
		self.ui.raddButton.clicked.connect(self.radd_pressed)
		self.ui.rremoveButton.clicked.connect(self.rremove_pressed)
		# self.ui.refShedule.clicked.connect(self.refshed_pressed)
		self.ui.wsortitionButton.clicked.connect(self.wsortition_pressed)
		self.ui.sortitionButton.clicked.connect(self.sortition_pressed)
		self.ui.cancel.clicked.connect(self.cancel_pressed)
		self.ui.weightcatCBox.currentIndexChanged.connect(self.update_sportsmenlists)
		#
		self.ring = 1
		self.meeting = 0
		self.meet = meet

		self.dbm = dbmanager()

		'''# TODO: сделать список выбора и заполнить его весовыми категориями'''
		# TODO: при изменении списка выбора весовых категорий изменять значения списков спортсменов и участников
		# TODO: заносить участников в базу данных согласно выбранной весовой категории, если соревнование уже началось, в списке участников отмечать проигравших спортсменов как неактивные (нельзя удалить)
		# TODO: Сделать жеребьевку спортсменов согласно весовым категориям и текущей стадии соревнования (1/8, 1/4, полуфинал, финал)
		# TODO: Сделать возможность указывать результат проведенных поединков для спорсмена (выйграл/проиграл)
		# TODO: Сделать вывод жеребьевки согласно шаблону
		if self.meet:
			self.setWindowTitle("Изменение соревнования")
			self.edit_meet()

		else:
			self.setWindowTitle("Создание соревнования")

			'''# TODO: Заполнить список спортсменов'''
			members = self.dbm.get_all_members()
			for member in members:
				self.ui.athletesList.addItem(re.sub(r'\\', r'', member.fio))

			referees = self.dbm.get_all_referees()
			for referee in referees:
				self.ui.mainrefCBox.addItem(re.sub(r'\\', r'', referee.fio))
				self.ui.mainclerkCBox.addItem(re.sub(r'\\', r'', referee.fio))
				self.ui.refList.addItem(re.sub(r'\\', r'', referee.fio))

			weight_categories = self.dbm.get_all_weight_categories()
			for wcat in weight_categories:
				self.ui.weightcatCBox.addItem(re.sub(r'\\', r'', wcat.name))

			self.ui.wsortitionButton.hide()

	def update_sportsmenlists(self):

		print(self.ui.weightcatCBox.currentIndex())

		return

	def valid(self, res):

		if not res:
			# TODO: Вывести диалог с ошибкой
			val = InputError()
			val.exec_()

			return False

		return True

	def add_pressed(self):

		if self.update:
			self.ui.wsortitionButton.setEnabled(False)

		count = self.ui.athletesList.count()
		if count != 0:
			try:
				athname = self.ui.athletesList.currentItem().text()
				self.ui.membersList.addItem(athname)
				self.ui.athletesList.takeItem(self.ui.athletesList.row(self.ui.athletesList.currentItem()))
			except:
				pass

		return

	def remove_pressed(self):

		if self.update:
			self.ui.wsortitionButton.setEnabled(False)

		count = self.ui.membersList.count()
		if count != 0:
			try:
				memname = self.ui.membersList.currentItem().text()
				self.ui.athletesList.addItem(memname)
				self.ui.membersList.takeItem(self.ui.membersList.row(self.ui.membersList.currentItem()))
			except:
				pass
		return

	def radd_pressed(self):

		count = self.ui.refList.count()
		if count != 0:
			try:
				refname = self.ui.refList.currentItem().text()
				self.ui.refColList.addItem(refname)
				self.ui.refList.takeItem(self.ui.refList.row(self.ui.refList.currentItem()))
			except:
				pass
		return

	def rremove_pressed(self):

		count = self.ui.refColList.count()
		if count != 0:
			try:
				refcolname = self.ui.refColList.currentItem().text()
				self.ui.refList.addItem(refcolname)
				self.ui.refColList.takeItem(self.ui.refColList.row(self.ui.refColList.currentItem()))
			except:
				pass
		return

	# def refshed_pressed(self):

		'''# TODO: Сгенерировать таблицу с графиком работы судей'''

	#	pass

	def wsortition_pressed(self):

		database = db()
		validator = Valid()
		print(self.id)

		count = self.ui.membersList.count()
		#TODO: Если self.ui.meetCountEdit.text() пустое то установить его по количеству участников (боев будет не больше чем если каждый участник один выйдет на ринг)

		if self.ui.meetCountEdit.text() == '':
			self.ui.meetCountEdit.setText(str(count))

		'''# TODO: Изменить данные по соревнованию, главного судью и главного секретаря'''
		mainref = database.select('SELECT id FROM referee WHERE fio=\'' + self.ui.mainrefCBox.itemText(self.ui.mainrefCBox.currentIndex()) + '\'')
		mainclerk = database.select('SELECT id FROM referee WHERE fio=\'' + self.ui.mainclerkCBox.itemText(self.ui.mainclerkCBox.currentIndex()) + '\'')
		row = database.ins_upd('UPDATE meeting SET name=\'' + validator.escape(self.ui.nameEdit.text()) + '\', sdate=\'' + self.ui.startDate.date().toPyDate().strftime('%Y-%m-%d') + '\', edate=\'' + self.ui.endDate.date().toPyDate().strftime('%Y-%m-%d') + '\', city=\'' + validator.escape(self.ui.cityEdit.text()) + '\', meetcount=\'' + self.ui.meetCountEdit.text() + '\', mainreferee=\'' + str(mainref[0][0]) + '\', mainclerk=\'' + str(mainclerk[0][0]) + '\' WHERE id=\'' + str(self.id) + '\'')

		'''# TODO: Очистить таблицу судей от старых данных по текущему соревнованию'''
		database.delete('DELETE FROM meetreferees WHERE meeting=\'' + str(self.id) + '\'')
		count = self.ui.refColList.count()
		i = 0
		while i < count:
			ref = database.select('SELECT id FROM referee WHERE fio=\'' + self.ui.refColList.item(i).text() + '\'')
			database.ins_upd('INSERT INTO meetreferees(meeting, referee) VALUES (\'' + str(self.id) + '\', \'' + str(
				ref[0][0]) + '\')')
			i += 1

		self.close()

	def sortition(self, list):

		def change_ring():

			# TODO: количество рингов 2, проверять по таблице рингов

			# TODO: Жеребьевка на одном ринге

			if self.ring == 1:
				self.ring = 2
			else:
				self.ring = 1

		#print(list)
		''' проверить сколько элементов в списке, если больше или равно 3, то жеребьевка случайным образом взять два
		элемента (удалить их из списка)'''
		database = db()
		if self.update:
			self.meeting = self.id

		while len(list) > 0:
			if len(list) == 1:
				database.ins_upd('INSERT INTO sortition(idmeet, membera, memberb, ring) VALUES (' + str(self.meeting) + ', ' + str(list[0]) + ', 0, ' + str(self.ring) + ')')
				list = []
				#TODO: Смена ринга (сделать в форме запрос количества рингов)
				if self.ui.divrings.isChecked():
					change_ring()
				continue
			elif len(list) == 2:
				database.ins_upd('INSERT INTO sortition(idmeet, membera, memberb, ring) VALUES (' + str(self.meeting) + ', ' + str(list[0]) + ', ' + str(list[1]) + ', ' + str(self.ring) + ')')
				list = []
				# TODO: Смена ринга (сделать в форме запрос количества рингов)
				if self.ui.divrings.isChecked():
					change_ring()
				continue
			elif len(list) >= 3:
				# случайный жребий
				a = random.randint(0, len(list)-1)
				mem_a = list[a]
				list.pop(a)
				b = random.randint(0, len(list)-1)
				mem_b = list[b]
				list.pop(b)
				database.ins_upd('INSERT INTO sortition(idmeet, membera, memberb, ring) VALUES (' + str(self.meeting) + ', ' + str(mem_a) + ', ' + str(mem_b) + ', ' + str(self.ring) + ')')
				# TODO: Смена ринга (сделать в форме запрос количества рингов)
				if self.ui.divrings.isChecked():
					change_ring()

	def sortition_pressed(self):

		'''# TODO: 1. Создать запись о соревновании '''
		'''# TODO: 2. Заполнить таблицу участников основываясь на ID созданного соревнования и ID участника'''
		# TODO: Проверить валидность данных

		database = db()
		validator = Valid()

		'''# TODO: Если соревнование редактируется, то у далить старые данные'''
		'''# TODO: проверить не редактируется ли соревнование, если да, то удалить старые данные сортировки'''
		if self.update:
			database.delete('DELETE FROM meetmembers WHERE meeting=\'' + str(self.id) + '\'')
			database.delete('DELETE FROM meetreferees WHERE meeting=\'' + str(self.id) + '\'')
			database.delete('DELETE FROM sortition WHERE idmeet=\'' + str(self.id) + '\'')
			self.meeting = self.id
		else:
			self.meeting = 0

		if not self.valid(validator.validString(self.ui.nameEdit.text())):
			return
		if not self.valid(validator.validDigit(self.ui.meetCountEdit.text())):
			return

		mainref = database.select('SELECT id FROM referee WHERE fio=\'' + self.ui.mainrefCBox.itemText(self.ui.mainrefCBox.currentIndex()) + '\'')
		mainclerk = database.select('SELECT id FROM referee WHERE fio=\'' + self.ui.mainclerkCBox.itemText(self.ui.mainclerkCBox.currentIndex()) + '\'')

		count = self.ui.membersList.count()
		i = 0
		listmembers = []
		man = {}
		woman = {}
		cat = {}

		#TODO: Если self.ui.meetCountEdit.text() пустое то установить его по количеству участников (боев будет не больше чем если каждый участник один выйдет на ринг)

		if self.ui.meetCountEdit.text() == '':
			self.ui.meetCountEdit.setText(str(count))

		if self.update:
			row = database.ins_upd('UPDATE meeting SET name=\'' + validator.escape(self.ui.nameEdit.text()) + '\', sdate=\'' + self.ui.startDate.date().toPyDate().strftime('%Y-%m-%d') + '\', edate=\'' + self.ui.endDate.date().toPyDate().strftime('%Y-%m-%d') + '\', city=\'' + validator.escape(self.ui.cityEdit.text()) + '\', meetcount=\'' + self.ui.meetCountEdit.text() + '\', mainreferee=\'' + str(mainref[0][0]) + '\', mainclerk=\'' + str(mainclerk[0][0]) + '\' WHERE id=\'' + str(self.id) + '\'')
		else:
			self.meeting = database.ins_upd('INSERT INTO meeting(name, sdate, edate, city, meetcount, mainreferee, mainclerk) VALUES (\'' + validator.escape(self.ui.nameEdit.text()) + '\', \'' + self.ui.startDate.date().toPyDate().strftime('%Y-%m-%d') + '\', \'' + self.ui.endDate.date().toPyDate().strftime('%Y-%m-%d') + '\', \'' + validator.escape(self.ui.cityEdit.text()) + '\', \'' + self.ui.meetCountEdit.text() + '\', \'' + str(mainref[0][0]) + '\', \'' + str(mainclerk[0][0]) + '\')')



		while i < count:
			mem = database.select('SELECT id, sex, weight FROM members WHERE fio=\'' + validator.escape(
				self.ui.membersList.item(i).text()) + '\'')
			'''# TODO: 1. Разобрать участников по полу'''
			'''# TODO: 1.1 Получить список участников (в список)'''
			(id, sex, weight) = mem[0]
			if sex == 1:
				# если мужчина
				'''# TODO: Разобрать участников по весовой категории'''
				if weight in man:
					print("Мужчины - Есть")
					man[weight].append(id)
				else:
					print("Мужчины - Нет")
					man[weight] = list()
					man[weight].append(id)
			elif sex ==2:
				'''# TODO: Разобрать участников по весовой категории'''
				# если женщина
				if weight in woman:
					print("Женщины - Есть")
					woman[weight].append(id)
				else:
					print("Женщины - Нет")
					woman[weight] = list()
					woman[weight].append(id)
			database.ins_upd('INSERT INTO meetmembers(meeting, members) VALUES (\'' + str(self.meeting) + '\', \'' + str(id) + '\')')
			i += 1

		count = self.ui.refColList.count()
		i = 0
		while i < count:
			ref = database.select('SELECT id FROM referee WHERE fio=\'' + self.ui.refColList.item(i).text() + '\'')
			database.ins_upd('INSERT INTO meetreferees(meeting, referee) VALUES (\'' + str(self.meeting) + '\', \'' + str(ref[0][0]) + '\')')
			i += 1

		'''# TODO: Сделать жеребьевку'''
		# TODO: Отсортировать по рязряду (исправить в случае изменения порядка разрядов)
		# TODO: Сделать приоритет жеребьевки по разряду участника
		for key, value in man.items():
			self.sortition(value)
		for key, value in woman.items():
			self.sortition(value)

		'''# TODO: Сделать выборку из групп пока количество больше 1'''

		self.close()
		return

	def cancel_pressed(self):

		self.close()

	def edit_meet(self):

		database = db()

		# Заполнить список выбора весовых категорий
		#row = database.select("SELECT * FROM weightcategory")
		weight_categories = self.dbm.get_all_weight_categories()
		for wcat in weight_categories:
			self.ui.weightcatCBox.addItem(re.sub(r'\\', r'', wcat.name))

		#row = database.select("SELECT * FROM referee")
		referees = self.dbm.get_all_referees()
		for referee in referees:
			self.ui.mainrefCBox.addItem(re.sub(r'\\', r'', referee.fio))
			self.ui.mainclerkCBox.addItem(re.sub(r'\\', r'', referee.fio))



		self.id = self.meet[0]
		self.ui.nameEdit.setText(re.sub(r'\\', r'', self.meet[1]))
		self.ui.startDate.setDate(QtCore.QDate.fromString(self.meet[2], 'yyyy-MM-dd'))
		self.ui.endDate.setDate(QtCore.QDate.fromString(self.meet[3], 'yyyy-MM-dd'))
		self.ui.cityEdit.setText(re.sub(r'\\', r'', self.meet[4]))
		self.ui.meetCountEdit.setText(str(self.meet[5]))
		'''# TODO: Установить главного судью и секретаря'''
		#mainref = database.select('SELECT fio FROM referee WHERE id=\'' + str(self.meet[6]) + '\'')
		main_referee = self.dbm.get_referee(self.meet[6])
		#mainclerk = database.select('SELECT fio FROM referee WHERE id=\'' + str(self.meet[7]) + '\'')
		main_clerk = self.dbm.get_referee(self.meet[7])
		'''# TODO: Заполнить списки выбора судей'''
		self.ui.mainrefCBox.setCurrentIndex(self.ui.mainrefCBox.findText(main_referee.fio))
		self.ui.mainclerkCBox.setCurrentIndex(self.ui.mainclerkCBox.findText(main_clerk.fio))
		#meetref = database.select('SELECT * FROM meetreferees WHERE meeting=\'' + str(self.meet[0]) + '\'')
		#meet_refs = self.dbm.get_meet_referees(self.meet[0])
		#meet_referees = self.dbm.get_meet_referees2(self.meet[0])
		meet_refs = self.dbm.get_meet_refs(self.meet[0])
		refs_in_meet_ids = [item.referee_id for item in meet_refs]
		meet_referees = [referee for referee in referees if referee.id in refs_in_meet_ids]
		refcol = []
		for meet_referee in meet_referees:
			#ref = database.select('SELECT * FROM referee WHERE id=\'' + str(referee[2]) + '\'')
			#referee = self.dbm.get_referee(meet_ref[2])
			self.ui.refColList.addItem(re.sub(r'\\', r'', meet_referee.fio))
			refcol.append(meet_referee.id)
		for referee in referees:
			if referee.id not in refcol:
				self.ui.refList.addItem(re.sub(r'\\', r'', referee.fio))
		'''# TODO: Заполнить списки выборов спортсменов и участников'''
		#meetmems = database.select('SELECT * FROM meetmembers WHERE meeting=\'' + str(self.meet[0]) + '\'')
		meetmems = self.dbm.get_meet_members(self.meet[0])
		memcol = []
		for member in meetmems:
			mem = database.select('SELECT id, fio FROM members WHERE id =\'' + str(member[2]) + '\'')
			self.ui.membersList.addItem(re.sub(r'\\', r'', mem[0][1]))
			memcol.append(mem[0][0])
		#row = database.select("SELECT * FROM members")
		members = self.dbm.get_all_members()
		for member in members:
			if member.id not in memcol:
				self.ui.athletesList.addItem(re.sub(r'\\', r'', member.fio))

		return


