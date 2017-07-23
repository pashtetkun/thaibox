from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QMenu, QAction
from meet import Ui_Dialog as createmeeting
from database_manager import DbManager as dbmanager
from models import Meeting, MeetReferee, MeetMember, Fighting, MemberStatus, FightingsInWeigth
from validator import Valid
from input_error_slots import InputErrorSlots
import random
import operator
import math


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
		self.initialize = False
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
		self.ui.weightcatCBox.currentIndexChanged.connect(self.weight_category_changed)
		self.ui.mainrefCBox.currentIndexChanged.connect(self.main_referee_changed)
		self.ui.mainclerkCBox.currentIndexChanged.connect(self.main_clerk_changed)
		#
		self.ring = 1
		self.meeting = 0
		self.meet = None
		if meet:
			self.meet = Meeting(meet)

		self.dbm = dbmanager()

		self.members = []
		self.referees = []
		self.weight_categories = []
		self.meet_referees = []
		self.not_meet_referees = []
		self.meet_members = []
		self.not_meet_members = []
		self.current_weight_category = None
		self.main_referee = None
		self.main_clerk = None

		#словарь боёв {weightcat_id : FightingsInWeight}
		self.dict_fightings_in_weights = {}

		try:
			self.fill_data()
		except Exception as e:
			print(e)

		self.initialize = True

		self.ui.weightcatCBox.setCurrentIndex(-1)
		self.ui.weightcatCBox.setCurrentIndex(0)

		self.ui.membersList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.ui.membersList.customContextMenuRequested.connect(self.show_cmenu)

		self.ui.membersList.itemPressed.connect(self.memberListItem_pressed)


		'''# TODO: сделать список выбора и заполнить его весовыми категориями'''
		# TODO: при изменении списка выбора весовых категорий изменять значения списков спортсменов и участников
		# TODO: заносить участников в базу данных согласно выбранной весовой категории, если соревнование уже началось, в списке участников отмечать проигравших спортсменов как неактивные (нельзя удалить)
		# TODO: Сделать жеребьевку спортсменов согласно весовым категориям и текущей стадии соревнования (1/8, 1/4, полуфинал, финал)
		# TODO: Сделать возможность указывать результат проведенных поединков для спорсмена (выйграл/проиграл)
		# TODO: Сделать вывод жеребьевки согласно шаблону

	#заполнить форму соревнования данными
	def fill_data(self):
		self.members = self.dbm.get_all_members()
		self.members.sort(key=operator.attrgetter("fio"), reverse=False)
		self.referees = self.dbm.get_all_referees()
		self.referees.sort(key=operator.attrgetter("fio"), reverse=False)
		self.weight_categories = self.dbm.get_all_weight_categories()

		fightings = self.dbm.get_fightings_by_meeting(self.meet.id)
		for wcat in self.weight_categories:
			dict_fightings_by_round = {}
			fightings_by_weight = [f for f in fightings if f.weightcategory_id == wcat.id]
			current_fr_round = 999
			for f in fightings_by_weight:
				if f.fractional_round not in dict_fightings_by_round:
					dict_fightings_by_round[f.fractional_round] = [f]
				else:
					dict_fightings_by_round[f.fractional_round].append(f)

				if f.fractional_round < current_fr_round:
					current_fr_round = f.fractional_round

			#self.dict_fightings_in_weights[wcat.id] = dict_fightings_by_round
			self.dict_fightings_in_weights[wcat.id] = FightingsInWeigth(wcat, current_fr_round, dict_fightings_by_round)


		self.fill_comboboxes()

		refs_in_meet_ids = []
		mems_in_meet_ids = []
		if self.meet:
			self.setWindowTitle("Изменение соревнования")
			self.id = self.meet.id
			self.ui.nameEdit.setText(self.meet.name.replace('\\',''))
			self.ui.startDate.setDate(QtCore.QDate.fromString(self.meet.start_date, 'yyyy-MM-dd'))
			self.ui.endDate.setDate(QtCore.QDate.fromString(self.meet.end_date, 'yyyy-MM-dd'))
			self.ui.cityEdit.setText(self.meet.city.replace('\\',''))
			self.ui.meetCountEdit.setText(str(self.meet.meetcount))
			'''# TODO: Установить главного судью и секретаря'''
			self.main_referee = self.dbm.get_referee(self.meet.main_referee_id)
			self.main_clerk = self.dbm.get_referee(self.meet.main_clerk_id)
			'''# TODO: Заполнить списки выбора судей'''
			self.ui.mainrefCBox.setCurrentIndex(self.ui.mainrefCBox.findText(self.main_referee.fio))
			self.ui.mainclerkCBox.setCurrentIndex(self.ui.mainclerkCBox.findText(self.main_clerk.fio))

			self.meet_referees = self.dbm.get_meet_referees(self.meet.id)
			self.meet_referees.sort(key=operator.attrgetter("fio"), reverse=False)
			refs_in_meet_ids = [referee.id for referee in self.meet_referees]

			'''# TODO: Заполнить списки выборов спортсменов и участников'''
			self.meet_members = self.dbm.get_meet_members(self.meet.id)
			self.meet_members.sort(key=operator.attrgetter("fio"), reverse=False)
			mems_in_meet_ids = [member.id for member in self.meet_members]
			#для участников определяем их текущие статусы
			for member in self.meet_members:
				status = MemberStatus.MEMBER
				fightings_in_weight = self.dict_fightings_in_weights[member.weight_id]
				current_fr_round = fightings_in_weight.current_fr_round
				fightings_by_round = fightings_in_weight.fightings_by_round
				if current_fr_round in fightings_by_round:
					fs = fightings_by_round[current_fr_round]
					#бой участника в текущем раунде
					fighting = next((f for f in fs if f.member_a_id == member.id or f.member_b_id == member.id), None)
					if fighting:
						if fighting.winner_id == member.id:
							status = MemberStatus.WINNER
						if fighting.loser_id == member.id:
							status = MemberStatus.LOSER
					else:
						status = MemberStatus.WITHDRAW

				member.status = status


		else:
			self.setWindowTitle("Создание соревнования")
			self.ui.wsortitionButton.hide()

		for referee in self.referees:
			if referee.id not in refs_in_meet_ids:
				self.not_meet_referees.append(referee)
		self.not_meet_referees.sort(key=operator.attrgetter("fio"), reverse=False)

		for member in self.members:
			if member.id not in mems_in_meet_ids:
				self.not_meet_members.append(member)
		self.not_meet_members.sort(key=operator.attrgetter("fio"), reverse=False)

		self.refresh_referees_list()
		self.refresh_colreferees_list()
		# TODO: Заполнить список спортсменов

	#заполнить комбобоксы
	def fill_comboboxes(self):
		self.ui.weightcatCBox.clear()
		self.ui.weightcatCBox.addItem("Все категории")
		for wcat in self.weight_categories:
			self.ui.weightcatCBox.addItem(wcat.name.replace('\\', ''))

		self.ui.mainrefCBox.clear()
		self.ui.mainclerkCBox.clear()
		for referee in self.referees:
			self.ui.mainrefCBox.addItem(referee.fio.replace('\\', ''))
			self.ui.mainclerkCBox.addItem(referee.fio.replace('\\', ''))


	#обновить листбокс спортсменов
	def refresh_athletes_list(self):
		self.ui.athletesList.clear()
		for member in self.not_meet_members:
			if not self.current_weight_category or (self.current_weight_category and member.weight_id == self.current_weight_category.id):
				item = QListWidgetItem(member.fio.replace('\\', ''))
				item.setData(QtCore.Qt.UserRole, member)
				self.ui.athletesList.addItem(item)

	#обновить листбокс участников
	def refresh_members_list(self):
		self.ui.membersList.clear()
		for member in self.meet_members:
			if not self.current_weight_category or (self.current_weight_category and member.weight_id == self.current_weight_category.id):
				item = QListWidgetItem(member.fio.replace('\\', ''))
				item.setData(QtCore.Qt.UserRole, member)
				#item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
				#item.setCheckState(QtCore.Qt.Checked)
				self.set_item_background(item, member.status)
				self.ui.membersList.addItem(item)

	def weight_category_changed(self):
		indx = self.ui.weightcatCBox.currentIndex()
		if not self.initialize or indx == -1:
			self.current_weight_category = None
			return

		print(indx)
		self.current_weight_category = None if indx == 0 else self.weight_categories[indx-1]
		
		self.refresh_athletes_list()
		self.refresh_members_list()

	def main_referee_changed(self):
		indx = self.ui.mainrefCBox.currentIndex()
		self.main_referee = self.referees[indx]


	def main_clerk_changed(self):
		indx = self.ui.mainclerkCBox.currentIndex()
		self.main_clerk = self.referees[indx]

	#обновить список судей
	def refresh_referees_list(self):
		self.ui.refList.clear()
		for referee in self.not_meet_referees:
			item = QListWidgetItem(referee.fio.replace('\\', ''))
			item.setData(QtCore.Qt.UserRole, referee)
			self.ui.refList.addItem(item)

	#обновить коллегию судей
	def refresh_colreferees_list(self):
		self.ui.refColList.clear()
		for meet_referee in self.meet_referees:
			item = QListWidgetItem(meet_referee.fio.replace('\\', ''))
			item.setData(QtCore.Qt.UserRole, meet_referee)
			self.ui.refColList.addItem(item)

	def valid(self, res):

		if not res:
			# TODO: Вывести диалог с ошибкой
			val = InputError()
			val.exec_()

			return False

		return True

	def add_pressed(self):

		if self.meet:
			self.ui.wsortitionButton.setEnabled(False)

		item = self.ui.athletesList.currentItem()
		if not item:
			return
		member = item.data(QtCore.Qt.UserRole)

		if self.meet:
		    meet_member = MeetMember()
		    meet_member.meeting_id = self.meet.id
		    meet_member.member_id = member.id
		    meet_member.status = MemberStatus.MEMBER
		    self.dbm.insert_meet_member(meet_member)

		self.not_meet_members.remove(member)
		self.not_meet_members.sort(key=operator.attrgetter("fio"), reverse=False)
		self.meet_members.append(member)
		self.meet_members.sort(key=operator.attrgetter("fio"), reverse=False)
		self.refresh_members_list()
		self.refresh_athletes_list()

	def remove_pressed(self):

		if self.meet:
			self.ui.wsortitionButton.setEnabled(False)

		item = self.ui.membersList.currentItem()
		if not item:
			return
		member = item.data(QtCore.Qt.UserRole)

		if self.meet:
		    self.dbm.delete_meet_member(self.meet.id, member.id)

		self.meet_members.remove(member)
		self.meet_members.sort(key=operator.attrgetter("fio"), reverse=False)
		self.not_meet_members.append(member)
		self.not_meet_members.sort(key=operator.attrgetter("fio"), reverse=False)
		self.refresh_members_list()
		self.refresh_athletes_list()

	def radd_pressed(self):

		item =  self.ui.refList.currentItem()
		if not item:
			return
		referee = item.data(QtCore.Qt.UserRole)
		self.not_meet_referees.remove(referee)
		self.not_meet_referees.sort(key=operator.attrgetter("fio"), reverse=False)
		self.meet_referees.append(referee)
		self.meet_referees.sort(key=operator.attrgetter("fio"), reverse=False)
		self.refresh_referees_list()
		self.refresh_colreferees_list()

	def rremove_pressed(self):

		item = self.ui.refColList.currentItem()
		if not item:
			return
		referee = item.data(QtCore.Qt.UserRole)
		self.meet_referees.remove(referee)
		self.meet_referees.sort(key=operator.attrgetter("fio"), reverse=False)
		self.not_meet_referees.append(referee)
		self.not_meet_referees.sort(key=operator.attrgetter("fio"), reverse=False)
		self.refresh_referees_list()
		self.refresh_colreferees_list()


	# def refshed_pressed(self):

		'''# TODO: Сгенерировать таблицу с графиком работы судей'''

	#	pass

	def get_meeting_values(self):
		if not self.meet:
			self.meet = Meeting()
		validator = Valid()
		self.meet.main_referee_id = self.main_referee.id
		self.meet.main_clerk_id = self.main_clerk.id
		self.meet.name = validator.escape(self.ui.nameEdit.text())
		self.meet.start_date = self.ui.startDate.date().toPyDate().strftime('%Y-%m-%d')
		self.meet.end_date = self.ui.endDate.date().toPyDate().strftime('%Y-%m-%d')
		self.meet.city = validator.escape(self.ui.cityEdit.text())
		self.meet.meetcount = self.ui.meetCountEdit.text()
		self.meet.main_referee_id = self.main_referee.id
		self.meet.main_clerk_id = self.main_clerk.id
		return self.meet

	def wsortition_pressed(self):

		print(self.id)

		count = len(self.meet_members)
		#TODO: Если self.ui.meetCountEdit.text() пустое то установить его по количеству участников (боев будет не больше чем если каждый участник один выйдет на ринг)

		if self.ui.meetCountEdit.text() == '':
			self.ui.meetCountEdit.setText(str(count))

		'''# TODO: Изменить данные по соревнованию, главного судью и главного секретаря'''
		self.meet = self.get_meeting_values()
		self.dbm.update_meeting(self.meet)

		'''# TODO: Очистить таблицу судей от старых данных по текущему соревнованию'''
		self.dbm.delete_meet_referee(self.meet.id)
		count = len(self.meet_referees)

		for referee in self.meet_referees:
			meet_referee = MeetReferee()
			meet_referee.meeting_id = self.meet.id
			meet_referee.referee_id = referee.id
			self.dbm.insert_meet_referee(meet_referee)

		self.close()

	def sortition(self, weightcatid, members=[]):

		def change_ring():

			# TODO: количество рингов 2, проверять по таблице рингов

			# TODO: Жеребьевка на одном ринге

			if self.ring == 1:
				self.ring = 2
			else:
				self.ring = 1

		''' проверить сколько элементов в списке, если больше или равно 3, то жеребьевка случайным образом взять два
		элемента (удалить их из списка)'''

		if self.meet:
			self.meeting = self.id

		if not members:
			return

		#если число участников - не степень двойки, то раунд будет больше на 1
		rounds = 0
		val_rounds = math.log2(len(members))
		if not float(val_rounds).is_integer():
			rounds = math.ceil(val_rounds)#до наибольшего целого
		else:
			rounds = math.trunc(val_rounds)#усекаем дробную часть (дробный ноль)
		if rounds == 0: #если один участник всего
			rounds = 1

		fractional_round = math.trunc(math.pow(2, rounds-1))
		wcat = next((x for x in self.weight_categories if x.id == weightcatid), None)
		print("weightcategory: ", wcat.name, "members: ", len(members), "fr_round: ", fractional_round)

		while len(members) > 0:

			fighting = Fighting()
			fighting.meeting_id = self.meet.id
			fighting.ring = self.ring
			fighting.fractional_round = fractional_round
			fighting.weightcategory_id = weightcatid
			fighting.winner_id = None
			fighting.loser_id = None

			if len(members) == 1:
				fighting.member_a_id = members[0].id
				fighting.member_b_id = None
				fighting.winner_id = members[0].id
				members.clear()
			elif len(members) == 2:
				fighting.member_a_id = members[0].id
				fighting.member_b_id = members[1].id
				members.clear()
			elif len(members) >= 3:
				# случайный жребий
				mem_a = random.choice(members)
				members.remove(mem_a)
				mem_b = random.choice(members)
				members.remove(mem_b)
				fighting.member_a_id = mem_a.id
				fighting.member_b_id = mem_b.id

			try:
				self.dbm.insert_fighting(fighting)
			except Exception as e:
				print(e)

			# TODO: Смена ринга (сделать в форме запрос количества рингов)
			if self.ui.divrings.isChecked():
				change_ring()

	def sortition_pressed(self):

		#проверка что можно провести жеребъевку следующего раунда соревнований
		#fightings = self.dbm.get_fightings_by_meeting(self.meet.id)
		drawing_allow = True
		#if fightings:
			#dict_fightings_by_weight_and_rounds = {}
		for wcat_id in self.dict_fightings_in_weights:
			fightings_in_weight = self.dict_fightings_in_weights[wcat_id]
			current_fr_round = fightings_in_weight.current_fr_round
			#еще не было жеребьевки
			if current_fr_round == 999:
				continue
			# после финала - не нужна дальнейшая жеребьевка
			if current_fr_round == 1:
				continue

			not_defined_winners = [f for f in fightings_in_weight.fightings_by_round[current_fr_round] if f.winner_id == None]
			if not_defined_winners:
				print("Не указаны все проигравшие в ", fightings_in_weight.weight_category.name, ", раунд: 1/%d" % current_fr_round)
				drawing_allow = False
				break
			#for wcat in self.weight_categories:
				#dict_fightings_by_round = {}
				#fightings_by_weight = [f for f in fightings if f.weightcategory_id == wcat.id]
				#current_fr_round = 999
				#for f in fightings_by_weight:
					#if f.fractional_round not in dict_fightings_by_round:
						#dict_fightings_by_round[f.fractional_round] = [f]
					#else:
						#dict_fightings_by_round[f.fractional_round].append(f)

					#if f.fractional_round < current_fr_round:
						#current_fr_round = f.fractional_round

				#после финала - не нужна дальнейшая жеребьевка
				#if current_fr_round == 1:
					#continue

				#dict_fightings_by_weight_and_rounds[wcat.id] = dict_fightings_by_round
				#fightings_by_round = dict_fightings_by_round.get(current_fr_round, [])
				#if fightings_by_round:
					#not_defined_winners = [f for f in fightings_by_round if f.winner_id == None]
					#if not_defined_winners:
						#print("Не указаны все проигравшие в ", wcat.name, ", раунд: 1/%d" % current_fr_round)
						#drawing_allow = False
						#break

		if not drawing_allow:
			return

		#count_f = self.dbm.get_count_fightings_by_meeting(self.meet.id)

		print("проверка доступности жеребьевки пройдена!")

		'''# TODO: 1. Создать запись о соревновании '''
		'''# TODO: 2. Заполнить таблицу участников основываясь на ID созданного соревнования и ID участника'''
		# TODO: Проверить валидность данных

		validator = Valid()

		'''# TODO: Если соревнование редактируется, то удалить старые данные'''
		'''# TODO: проверить не редактируется ли соревнование, если да, то удалить старые данные сортировки'''
		if self.meet:
			self.dbm.delete_meet_referee(self.meet.id)
			#удаляем только если еще не было боёв
			#if not count_f:
			    #self.dbm.delete_meet_member(self.meet.id)
				#провести пережеребьевку текущего раунда ???
			    #self.dbm.delete_fightings_by_meeting(self.meet.id)
			self.meeting = self.id
		else:
			self.meeting = 0

		if not self.valid(validator.validString(self.ui.nameEdit.text())):
			return
		if not self.valid(validator.validDigit(self.ui.meetCountEdit.text())):
			return

		count = len(self.meet_members)
		members_by_weigth = {}

		#TODO: Если self.ui.meetCountEdit.text() пустое то установить его по количеству участников (боев будет не больше чем если каждый участник один выйдет на ринг)

		if self.ui.meetCountEdit.text() == '':
			self.ui.meetCountEdit.setText(str(count))

		self.meet = self.get_meeting_values()

		if self.meet:
			self.dbm.update_meeting(self.meet)
		else:
			self.meet = self.dbm.insert_meeting(self.meet)

		#сохраняем участников - только если еще не было жеребьевки вообще

		#if count_f:
		#    for member in self.meet_members:
		#	    meet_member = MeetMember()
		#	    meet_member.meeting_id = self.meet.id
		#	    meet_member.member_id = member.id
		#	    meet_member.status = MemberStatus.MEMBER
		#	    self.dbm.insert_meet_member(meet_member)


		#разбираем по весовым категориям
		for member in self.meet_members:
			#для жеребьевки отбираем только активных участников
			if member.status != MemberStatus.MEMBER:
				continue
			if member.weight_id in members_by_weigth:
				members_by_weigth[member.weight_id].append(member)
			else:
				members_by_weigth[member.weight_id] = [member]

		#сохраняем судей
		for referee in self.meet_referees:
			meet_referee = MeetReferee()
			meet_referee.meeting_id = self.meet.id
			meet_referee.referee_id = referee.id
			self.dbm.insert_meet_referee(meet_referee)

		'''# TODO: Сделать жеребьевку'''
		# TODO: Отсортировать по рязряду (исправить в случае изменения порядка разрядов)
		# TODO: Сделать приоритет жеребьевки по разряду участника
		for key, value in members_by_weigth.items():
			self.sortition(key, value)

		'''# TODO: Сделать выборку из групп пока количество больше 1'''

		print("жеребьевка произведена!")
		self.close()
		return

	def cancel_pressed(self):

		self.close()

	#контекстное меню
	def show_cmenu(self, pos):
		current_item = self.ui.membersList.currentItem()
		if not current_item:
			return
		member = current_item.data(QtCore.Qt.UserRole)
		menu = QMenu(self)
		actionSetWin = menu.addAction('-> победил', lambda: self.set_member_status(current_item, MemberStatus.WINNER))
		actionSetLose = menu.addAction('-> проиграл', lambda: self.set_member_status(current_item, MemberStatus.LOSER))
		actionSetMember = menu.addAction('<- участник', lambda: self.set_member_status(current_item, MemberStatus.MEMBER))

		#доступность пунктов меню
		#если боев вообще нет, то и меню недоступны
		count_f = self.dbm.get_count_fightings_by_meeting(self.meet.id)
		if not count_f:
			actionSetWin.setEnabled(False)
			actionSetLose.setEnabled(False)
			actionSetMember.setEnabled(False)
		else:
		    actionSetWin.setEnabled(member.status != MemberStatus.WITHDRAW and member.status != MemberStatus.WINNER)
		    actionSetLose.setEnabled(member.status != MemberStatus.WITHDRAW and member.status != MemberStatus.LOSER)
		    actionSetMember.setEnabled(member.status != MemberStatus.WITHDRAW and member.status != MemberStatus.MEMBER)
		menu.exec_(QtGui.QCursor.pos())

	#установить статус участника
	def set_member_status(self, current_item, member_status):
		member = current_item.data(QtCore.Qt.UserRole)

		member.status = member_status

		f_in_w = self.dict_fightings_in_weights[member.weight_id]
		current_fr_round = f_in_w.current_fr_round
		f_by_r = f_in_w.fightings_by_round
		fs = f_by_r[current_fr_round]
		fighting = next((f for f in fs if f.member_a_id == member.id or f.member_b_id == member.id), None)
		winner_id = None
		loser_id = None
		if member_status == MemberStatus.WINNER:
			winner_id = member.id
			loser_id = fighting.loser_id
		if member_status == MemberStatus.LOSER:
			winner_id = fighting.loser_id
			loser_id = member.id
		self.dbm.set_fighting_result(fighting.id, winner_id, loser_id)

		self.set_item_background(current_item, member_status)
		self.memberListItem_pressed(current_item)

	def memberListItem_pressed(self, item):
		member = item.data(QtCore.Qt.UserRole)
		self.ui.removeButton.setEnabled(member.status != MemberStatus.WITHDRAW)

	def set_item_background(self, item, member_status):
		member = item.data(QtCore.Qt.UserRole)
		background = "white"
		if member_status == MemberStatus.WINNER:
			background = "green"
		if member_status == MemberStatus.LOSER:
			background = "red"
		if member_status == MemberStatus.WITHDRAW:
			background = "lightGray"
		item.setBackground(QtGui.QColor(background))
