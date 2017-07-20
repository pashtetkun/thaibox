import sys, os
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from list_meetings import Ui_Dialog as listmeeting
from database import Dbase as db
from database_manager import DbManager as dbmanager
from meeting_dialog import MeetingDialog
import re
import xlsxwriter
import datetime
import math


class ListMeetingSlots(listmeeting):

	def __init__(self):
		pass


class ListMeetingDialog(QDialog):

	def __init__(self):
		super(ListMeetingDialog, self).__init__()
		self.ui = ListMeetingSlots()
		self.ui.setupUi(self)
		self.ui.tableWidget.setColumnHidden(0, True)
		self.ui.edit.clicked.connect(self.edit_pressed)
		self.ui.exportxls.clicked.connect(self.exportxls_pressed)
		self.ui.cancel.clicked.connect(self.cancel_pressed)
		self.name = ''
		self.start = ''
		self.end = ''
		self.city = ''
		self.fightings_per_day = 0

		'''# TODO: Заполнить список соревнований'''
		database = db()
		row = database.select("SELECT * FROM meeting")
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

	def exportxls_pressed(self):

		def formatmergeV(row, col, font, size, color, bold, italic, rotate, align, valign, row_size, col_size):
			merge_format = workbook.add_format(
				{'font_name': font, 'font_size': size, 'font_color': color, 'bold': bold, 'italic': italic})
			merge_format.set_rotation(rotate)
			merge_format.set_align(align)
			merge_format.set_align(valign)
			worksheet.set_row(row, row_size)
			worksheet.set_column(col, col_size)

			return merge_format

		def formatmergeH(row, col, font, size, color, bold, italic, rotate, align, valign, row_size, col_size):
			merge_format = workbook.add_format(
				{'font_name': font, 'font_size': size, 'font_color': color, 'bold': bold, 'italic': italic})
			merge_format.set_rotation(rotate)
			merge_format.set_align(align)
			merge_format.set_align(valign)
			worksheet.set_row(row, row_size)
			worksheet.set_column(col, col_size)

			return merge_format

		'''# TODO: получить данные о участниках'''

		get_row = self.ui.tableWidget.currentRow()
		id = self.ui.tableWidget.item(get_row, 0).text()
		database = db()
		self.dbm = dbmanager()
		#meeting = database.select('SELECT * FROM meeting WHERE id=\'' + id + '\'')
		meeting = self.dbm.get_meeting(id)
		rings = database.select('SELECT * FROM ring')
		# worksheet.
		self.name = meeting.name
		self.start = meeting.start_date
		self.end = meeting.end_date
		self.city = meeting.city.replace("\\", "")
		self.fightings_per_day = meeting.meetcount
		self.mainref = meeting.main_referee_id
		self.mainclerk = meeting.main_clerk_id
		self.current_ring = 0
		self.current_meet = 1
		#
		row = database.select('SELECT count(*) FROM sortition WHERE idmeet=\'' + id + '\'')
		fightings_total = row[0][0] # количество боев в соревновании
		dstart = datetime.datetime.strptime(self.start, "%Y-%m-%d")
		dend = datetime.datetime.strptime(self.end, "%Y-%m-%d")
		delta = dend - dstart
		deltaday = delta.days + 1 # учитываем и первый день соревнования

		'''# TODO: сделать наименование листов в зависимости от ринга'''
		# TODO: учитывать количество боев в день
		# TODO: количество поединков в соревновании
		# TODO: количество дней соревнования
		# TODO: количество поединков в день
		''' Количество боев делим на количество поединков в день. Получим длительность соревнования в днях'''
		meet_days_total = math.ceil(fightings_total / self.fightings_per_day)
		''' Проверка длительности соревнования.
		Если сумма боев по дням меньше чем длительность соревнования в днях. То вывести предупреждение.
		Если сумма боев по дням больше чем длительность соревнования в днях. То вывести ошибку.'''
		if meet_days_total < deltaday:
			print('Предупреждение')
		elif meet_days_total > deltaday:
			print('Ошибка')
			return

		workbook = xlsxwriter.Workbook(self.name.replace("\\", "") + '.xlsx')

		###############################
		### Список участников по рингам
		###############################

		ringscount = len(rings)
		''' количество боев на одном ринге в день'''
		fightings_per_day_per_ring = math.ceil(self.fightings_per_day/ringscount)
		for r in rings:
			members = database.select('SELECT s.membera, s.memberb, r.ring FROM sortition AS s JOIN ring AS r ON s.ring = r.id WHERE s.idmeet=\'' + id + '\' AND r.id=\'' +str(r[0])+ '\'')
			day_count = 0
			current_index_member = 0
			start_day = datetime.datetime.strptime(self.start, "%Y-%m-%d") #
			y = 0
			while day_count < meet_days_total:
				worksheet = workbook.add_worksheet(r[1] + str(day_count+1))

				'''# TODO: старт с первой строки'''
				row = 1
				col = 1

				'''# TODO: Название'''
				merge_format = workbook.add_format({'font_name':'Times New Roman', 'font_size':'16', 'bold': True})
				merge_format.set_align('center')
				merge_format.set_align('vcenter')
				worksheet.set_row(row, 40.85)
				worksheet.merge_range('B2:H2', self.name, merge_format)
				worksheet.merge_range('I2:J2', r[1], formatmergeH(row, 'I:I', 'Times New Roman', '24', 'black', True,
																		False, 0, 'center', 'vcenter', 40.85, 3.7))
				''''# TODO: Ринг вывести '''
				row += 1 # 2
				format = workbook.add_format({'font_name':'Times New Roman', 'font_size':'16', 'bold': True})
				current_day = start_day + datetime.timedelta(days=day_count)
				worksheet.write_string(row, col, self.city + ", " + datetime.datetime.strftime(current_day, "%d %B %Y"), format)
				merge_format = workbook.add_format({'font_name':'Times New Roman', 'font_size':'16', 'bold': True})
				merge_format.set_align('right')
				merge_format.set_align('vcenter')
				worksheet.set_row(row, 22)
				worksheet.merge_range('I3:J3', 'Время начала', merge_format)
				row += 1 # 3
				worksheet.merge_range('B4:B5', '№ п/п', formatmergeV(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 90, 'center', 'vcenter', 22, 3.7))
				worksheet.merge_range('C4:C5', 'Категория', formatmergeV(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 22, 5.7))
				worksheet.merge_range('D4:D5', 'Бой', formatmergeV(row, 'D:D', 'Times New Roman', '12', 'black', True, False, 90, 'center', 'vcenter', 22, 3.7))
				worksheet.merge_range('E4:F4', 'Красный угол (Red)', formatmergeH(row, 'E:E', 'Times New Roman', '14', 'red', True, False, 0, 'center', 'vcenter', 22, 7.7))
				worksheet.merge_range('G4:H4', 'Синий угол (Blue)', formatmergeH(row, 'G:G', 'Times New Roman', '14', 'blue', True, False, 0, 'center', 'vcenter', 22, 7.7))
				row += 1 # 4
				worksheet.write_string(row, 4, 'ФИО', formatmergeH(row, 'E:E', 'Times New Roman', '14', 'black', True, False, 0, 'center', 'vcenter', 22, 3.7))
				worksheet.write_string(row, 5, 'Субъект', formatmergeH(row, 'F:F', 'Times New Roman', '14', 'black', True, False, 0, 'center', 'vcenter', 22, 3.7))
				worksheet.write_string(row, 6, 'ФИО', formatmergeH(row, 'E:E', 'Times New Roman', '14', 'black', True, False, 0, 'center', 'vcenter', 22, 3.7))
				worksheet.write_string(row, 7, 'Субъект', formatmergeH(row, 'F:F', 'Times New Roman', '14', 'black', True, False, 0, 'center', 'vcenter', 22, 3.7))
				worksheet.merge_range('I4:J5', 'Результат', formatmergeV(row, 'I:I', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 22, 5.7))
				#worksheet.write(row, col+1, self.start)
				row += 1 #6
				iterator = 1

				##### Вывести участников по количеству в день
				i = 0
				while i < fightings_per_day_per_ring:
					if y < len(members):
						meet = members[y]
					#for meet in members:
						# print(meet)
						mema = database.select('SELECT m.fio as fio, m.region, wc.wcategory as weight FROM members AS m JOIN weightcategory AS wc ON m.weight=wc.id WHERE m.id=\'' + str(meet[0]) + '\'')
						if meet[1] != 0:
							memb = database.select('SELECT m.fio as fio, m.region, wc.wcategory as weight FROM members AS m JOIN weightcategory AS wc ON m.weight=wc.id WHERE m.id=\'' + str(meet[1]) + '\'')
						else:
							memb = 'NULL'
						worksheet.write_string(row, 1, str(iterator), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
						worksheet.write_string(row, 2, re.sub(r'\\', r'', mema[0][2]), formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
						worksheet.write_string(row, 3, str(self.current_meet), formatmergeH(row, 'D:D', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
						worksheet.write_string(row, 4, re.sub(r'\\', r'', mema[0][0]), formatmergeH(row, 'E:E', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
						worksheet.write_string(row, 5, re.sub(r'\\', r'', mema[0][1]), formatmergeH(row, 'F:F', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
						if memb != 'NULL':
							worksheet.write_string(row, 6, re.sub(r'\\', r'', memb[0][0]), formatmergeH(row, 'G:G', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
							worksheet.write_string(row, 7, re.sub(r'\\', r'', memb[0][1]), formatmergeH(row, 'H:H', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
						else:
							worksheet.write_string(row, 6, 'Нет участника', formatmergeH(row, 'G:G', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
							worksheet.write_string(row, 7, '', formatmergeH(row, 'H:H', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
						worksheet.merge_range('I'+str(row)+':J'+str(row), '', formatmergeH(row, 'I:J', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 5.7))

						row += 1
						iterator += 1
						self.current_meet += 1
					i += 1
					y += 1
				day_count += 1

				'''# TODO: Добавить судей и секретаря '''
				mainreferee = database.select('SELECT r.fio, rf.category, rg.region FROM referee as r LEFT JOIN refereecat AS rf ON r.category=rf.id LEFT JOIN region AS rg ON r.region=rg.id WHERE r.id=\'' + str( self.mainref) + '\'')
				mainclerk = database.select('SELECT r.fio, rf.category, rg.region FROM referee as r LEFT JOIN refereecat AS rf ON r.category=rf.id LEFT JOIN region AS rg ON r.region=rg.id WHERE r.id=\'' + str(self.mainclerk) + '\'')
				row += 1
				worksheet.write_string(row, 1, "Главный судья,", formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
				worksheet.write_string(row, 7, mainreferee[0][0], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
				row += 1
				worksheet.write_string(row, 1, "судья " + mainreferee[0][1], formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
				worksheet.write_string(row, 7, mainreferee[0][2], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
				row += 1
				worksheet.write_string(row, 1, "Главный секретарь,", formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
				worksheet.write_string(row, 7, mainclerk[0][0], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
				row += 1
				worksheet.write_string(row, 1, "судья " + mainclerk[0][1], formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
				worksheet.write_string(row, 7, mainclerk[0][2], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
				row += 1


		### Судейская бригада
		meeting = database.select("SELECT name, sdate, edate, city FROM meeting WHERE id=\"" + id + "\"")
		referees = database.select("SELECT ref.fio, rp.position, reg.region, rc.category FROM meetreferees AS mr JOIN referee AS ref ON mr.referee=ref.id JOIN refereepos AS rp ON ref.position=rp.id JOIN region AS reg ON ref.region=reg.id JOIN refereecat AS rc ON ref.category=rc.id WHERE meeting=\"" + id + "\"")
		refmain = database.select("SELECT ref.fio, rp.position, reg.region, rc.category FROM meeting AS mt JOIN referee AS ref ON mt.mainreferee=ref.id JOIN refereepos AS rp ON ref.position=rp.id JOIN region AS reg ON ref.region=reg.id JOIN refereecat AS rc ON ref.category=rc.id WHERE mt.id=\"" + id + "\"")
		refclerk = database.select("SELECT ref.fio, rp.position, reg.region, rc.category FROM meeting AS mt JOIN referee AS ref ON mt.mainclerk=ref.id JOIN refereepos AS rp ON ref.position=rp.id JOIN region AS reg ON ref.region=reg.id JOIN refereecat AS rc ON ref.category=rc.id WHERE mt.id=\"" + id + "\"")

		worksheet = workbook.add_worksheet("Судьи")
		row = 0
		worksheet.merge_range("C1:G1", re.sub(r'\\', r'', meeting[0][0]), formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
		row += 1
		place = re.sub(r'\\', r'', meeting[0][3]) + ", " + meeting[0][1] + " - " + meeting[0][2]
		worksheet.merge_range("B2:G2", place, formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15,
														   3.7))
		row += 2
		worksheet.merge_range("A4:G4", "Судейская бригада соревнований:",
							  formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 15, 3.7))
		row += 1
		worksheet.write_string(row, 0, "№ п/п", formatmergeH(row, 'A:A', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 15,
															 3.7))
		worksheet.merge_range("B"+str(row+1)+":D"+str(row+1), "ФИО", formatmergeH(row, 'B:D', 'Times New Roman', '12', 'black', True, False, 0,
																			'center', 'vcenter', 15, 3.7))
		worksheet.write_string(row, 4, "Должность судьи", formatmergeH(row, 'E:E', 'Times New Roman', '12', 'black', True, False, 0, 'center',
																	 'vcenter', 15, 3.7))
		worksheet.write_string(row, 5, "Регион", formatmergeH(row, 'F:F', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 15,
														   3.7))
		worksheet.write_string(row, 6, "Судейская категория", formatmergeH(row, 'G:G', 'Times New Roman', '12', 'black', True, False, 0, 'center',
																	 'vcenter', 15, 3.7))
		row += 1
		i = 1
		for r in referees:
			worksheet.write_string(row, 0, str(i), formatmergeH(row, 'A:A', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter',
																15,	3.7))
			worksheet.merge_range("B" + str(row + 1) + ":D" + str(row + 1), r[0], formatmergeH(row, 'B:D', 'Times New Roman', '12', 'black', False,
																							   False, 0, 'left', 'vcenter', 15, 3.7))
			worksheet.write_string(row, 4, r[1], formatmergeH(row, 'E:E', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter',
																15,	3.7))
			worksheet.write_string(row, 5, r[2], formatmergeH(row, 'F:F', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter',
															  15, 3.7))
			worksheet.write_string(row, 6, r[3], formatmergeH(row, 'G:G', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter',
															  15, 3.7))

			i += 1
			row += 1

		row += 1
		worksheet.write_string(row, 0, "Главный судья,", formatmergeH(row, 'A:A', 'Times New Roman', '12', 'black', True, False, 0, 'left',
																	'vcenter', 15, 3.7))
		worksheet.write_string(row, 5, refmain[0][0], formatmergeH(row, 'F:F', 'Times New Roman', '12', 'black', True, False, 0, 'left',
																	'vcenter', 15, 3.7))
		row += 1
		worksheet.write_string(row, 0, refmain[0][3], formatmergeH(row, 'A:A', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))

		worksheet.write_string(row, 5, refmain[0][2], formatmergeH(row, 'F:F', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
		### График работы судей
		worksheet = workbook.add_worksheet("График работы судей")
		row = 0
		meetdays = dstart
		while meetdays <= dend:
			worksheet.merge_range("B" + str(row+1) + ":AG" + str(row+1), re.sub(r'\\', r'', meeting[0][0]), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 15, 3.7))
			row += 1
			date = datetime.datetime.strftime(meetdays, "%A %d, %B %Y")
			worksheet.write_string(row, 2, date, formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
			worksheet.merge_range("R" + str(row+1) + ":AG" + str(row+1), re.sub(r'\\', r'', meeting[0][3]), formatmergeH(row, 'R:AG', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
			row += 1
			worksheet.merge_range("B" + str(row+1) + ":AG" + str(row+1), "График работы судей", formatmergeH(row, 'R:AG', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
			row += 2
			worksheet.write_string(row, 0, "№", formatmergeH(row, 'A:A', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15, 3.7))
			worksheet.write_string(row, 1, "ФИО", formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15,
															   3.7))
			worksheet.write_string(row, 2, "Регион", formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15,
																3.7))
			worksheet.merge_range("D" + str(row+1) + ":AH" + str(row+1), "Замечания и оценка по боям", formatmergeH(row, 'R:AG', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 15, 3.7))
			worksheet.write_string(row, 34, "Ринг", formatmergeH(row, 'AF:AF', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15,
																3.7))
			worksheet.write_string(row, 35, "Итоговая оценка", formatmergeH(row, 'AG:AG', 'Times New Roman', '12', 'black', False, False, 0, 'center',
																		 'vcenter', 15, 3.7))
			row += 1
			y = 1
			while y<=31:
				worksheet.write_string(row, y+2, str(y), formatmergeH(row, 'E:E', 'Times New Roman', '12', 'black', False, False, 0, 'center',
																				'vcenter', 15, 3.7))
				y += 1
			y = 1
			row += 1
			for r in referees:
				worksheet.write_string(row, 0, str(y), formatmergeH(row, 'A:A', 'Times New Roman', '12', 'black', False, False, 0, 'right', 'vcenter', 15, 3.7))
				worksheet.write_string(row, 1, r[0], formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter',
																  15, 3.7))
				worksheet.write_string(row, 2, r[2]+", "+r[1], formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
				y += 1
				row += 1

			row += 1
			worksheet.write_string(row, 1, "Главный судья", formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left',
																		 'vcenter', 15, 3.7))
			worksheet.write_string(row, 19, refmain[0][0], formatmergeH(row, 'T:T', 'Times New Roman', '12', 'black', True, False, 0, 'left',
																		 'vcenter', 15, 3.7))
			row += 1
			worksheet.write_string(row, 1, "судья " + refmain[0][3], formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
			worksheet.write_string(row, 19, refmain[0][2],
								   formatmergeH(row, 'T:T', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
			meetdays = meetdays + datetime.timedelta(days=1)
			row += 1


		### Командное первенство
		'''#TODO: Собрать участников по региону'''
		meetmemb = database.select("SELECT mem.region FROM meetmembers AS mmb JOIN members AS mem ON mmb.members=mem.id WHERE meeting=\"" + str(id) + "\"")
		region = list()
		for r in meetmemb:
			reg = re.sub(r'\\', r'', r[0])
			if reg not in region:
				region.append(reg)
		#
		worksheet = workbook.add_worksheet("Командное первенство")
		row = 0
		worksheet.merge_range("B" + str(row+1) + ":C" + str(row+2), "ПРОТОКОЛ Командного первенства", formatmergeH(row, 'B:C', 'Times New Roman', '14', 'black', False, False, 0, 'left', 'vcenter', 55, 15.7))
		worksheet.merge_range("D" + str(row+1) + ":J" + str(row+1), re.sub(r'\\', r'', meeting[0][0]), formatmergeH(row, 'D:J', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 35, 15.7))
		row += 1
		worksheet.merge_range("D" + str(row+1) + ":G" + str(row+1), datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][1], "%Y-%m-%d"), "%d %B") + " - " + datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][2], "%Y-%m-%d"), "%d %B %Y") + " " + re.sub(r'\\', r'', meeting[0][3]), formatmergeH(row, 'D:G', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 35, 10.7))
		worksheet.merge_range("H" + str(row+1) + ":J" + str(row+1), "Общекомандное место", formatmergeH(row, 'H:J', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 35, 10.7))
		row += 1
		worksheet.merge_range("B" + str(row+1) + ":B" + str(row+2), "№ п/п", formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 90, 'center', 'vcenter', 35, 15.7))
		worksheet.merge_range("C" + str(row+1) + ":C" + str(row+2), "Регион", formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 35, 25.7))
		worksheet.merge_range("D" + str(row+1) + ":H" + str(row+1), "Очки", formatmergeH(row, 'D:H', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 35, 10.7))
		worksheet.merge_range("I" + str(row+1) + ":I" + str(row+2), "Всего", formatmergeH(row, 'I:I', 'Times New Roman', '12', 'black', True, False, 90, 'center', 'vcenter', 35, 10.7))
		worksheet.merge_range("J" + str(row+1) + ":J" + str(row+2), "Место", formatmergeH(row, 'J:J', 'Times New Roman', '12', 'black', True, False, 90, 'center', 'vcenter', 35, 10.7))
		row += 1
		worksheet.write_string(row, 3, "1/16", formatmergeH(row, 'D:D', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15, 10.7))
		worksheet.write_string(row, 4, "1/8", formatmergeH(row, 'E:E', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15, 10.7))
		worksheet.write_string(row, 5, "1/4", formatmergeH(row, 'F:F', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15, 10.7))
		worksheet.write_string(row, 6, "1/2", formatmergeH(row, 'G:G', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15, 10.7))
		worksheet.write_string(row, 7, "Финал", formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15, 10.7))
		y =1
		for reg in region:
			worksheet.write_string(row, 1, str(y), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'center', 'vcenter', 15, 10.7))
			worksheet.write_string(row, 2, reg, formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', False, False, 0, 'right', 'vcenter', 15, 10.7))
			y += 1
			row += 1
		row += 2
		worksheet.write_string(row, 2, "Главный судья,", formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
		worksheet.write_string(row, 7, refmain[0][0], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 10.7))
		row += 1
		worksheet.write_string(row, 2, "судья " + refmain[0][3], formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
		worksheet.write_string(row, 7, refmain[0][2], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 10.7))
		'''#TODO: Собрать только мужчин и женщин по региону'''
		### Итоговый протокол

		worksheet = workbook.add_worksheet("Итоговый протокол")
		row = 0
		worksheet.merge_range("A" + str(row+1) + ":S" + str(row+1), "МИНИСТЕРСТВО СПОРТА РФ", formatmergeH(row, 'A:S', 'Times New Roman', '14', 'black', False, False, 0, 'center', 'vcenter', 20, 5.7))
		row += 1
		worksheet.merge_range("A" + str(row + 1) + ":S" + str(row + 1), "ФЕДЕРАЦИЯ ТАЙСКОГО БОКСА РОССИИ", formatmergeH(row, 'A:S', 'Times New Roman', '14', 'black', False, False, 0, 'center', 'vcenter', 20, 5.7))
		row += 1
		worksheet.merge_range("A" + str(row + 1) + ":S" + str(row + 1), "МИНИСТЕРСТВО ФИЗИЧЕСКОЙ КУЛЬТУРЫ, СПОРТА И РАБОТЫ С МОЛОДЕЖЬЮ МОСКОВСКОЙ ОБЛАСТИ", formatmergeH(row, 'A:S', 'Times New Roman', '14', 'black', False, False, 0, 'center', 'vcenter', 20, 5.7))
		row += 1
		worksheet.merge_range("A" + str(row + 1) + ":S" + str(row + 1), "ООО «РОССИЙСКАЯ АССОЦИАЦИЯ ГЕРОЕВ»", formatmergeH(row, 'A:S', 'Times New Roman', '14', 'black', False, False, 0, 'center', 'vcenter', 20, 5.7))
		row += 1
		worksheet.merge_range("A" + str(row + 1) + ":S" + str(row + 1), "СЕНАТОРСКИЙ КЛУБ СОВЕТА ФЕДЕРАЦИИ ФС РФ", formatmergeH(row, 'A:S', 'Times New Roman', '14', 'black', False, False, 0, 'center', 'vcenter', 20, 5.7))
		row += 2
		worksheet.merge_range("A" + str(row + 1) + ":S" + str(row + 1), "ИТОГОВЫЙ ПРОТОКОЛ", formatmergeH(row, 'A:S', 'Times New Roman', '28', 'black', True, False, 0, 'center', 'vcenter', 35, 5.7))
		row += 1
		worksheet.merge_range("A" + str(row + 1) + ":S" + str(row + 1), re.sub(r'\\', r'', meeting[0][0]), formatmergeH(row, 'A:S', 'Times New Roman', '18', 'black', True, False, 0, 'center', 'vcenter', 35, 5.7))
		row += 2
		worksheet.write_string(row, 1, datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][1], "%Y-%m-%d"), "%d %B") + " - " + datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][2], "%Y-%m-%d"), "%d %B %Y"), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
		row += 2
		worksheet.merge_range("B" + str(row + 1) + ":B" + str(row + 2), "ФИО", formatmergeH(row, 'B:B', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 5.7))
		worksheet.merge_range("C" + str(row + 1) + ":C" + str(row + 2), "Дата\nрождения", formatmergeH(row, 'C:C', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 5.7))
		worksheet.merge_range("D" + str(row + 1) + ":D" + str(row + 2), "Разряд", formatmergeH(row, 'D:D', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 5.7))
		worksheet.merge_range("E" + str(row + 1) + ":E" + str(row + 2), "Субъект, город, спортивная организация", formatmergeH(row, 'E:E', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 35.7))
		worksheet.merge_range("F" + str(row + 1) + ":F" + str(row + 2), "Тренер", formatmergeH(row, 'F:F', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 35.7))
		worksheet.merge_range("G" + str(row + 1) + ":G" + str(row + 2), "№ п/ж", formatmergeH(row, 'G:G', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 35.7))
		worksheet.merge_range("H" + str(row + 1) + ":J" + str(row + 1), "Характер победы: победа +, поражение -", formatmergeH(row, 'H:H', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 35.7))
		worksheet.merge_range("K" + str(row + 1) + ":K" + str(row + 2), "Место", formatmergeH(row, 'K:K', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 25, 35.7))
		row += 1
		worksheet.write_string(row, 7, "1/4", formatmergeH(row, 'H:H', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 15,
														   3.7))
		worksheet.write_string(row, 8, "1/2", formatmergeH(row, 'I:I', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 15,
														   3.7))
		worksheet.write_string(row, 9, "Финал", formatmergeH(row, 'J:J', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 15, 3.7))

		itogmeetmem = database.select("SELECT mem.* FROM meetmembers AS mmrs JOIN members AS mem ON mmrs.members = mem.id WHERE meeting=\"" + str(id) + "\"")
		itogcat = {}
		for im in itogmeetmem:
			if im[4] in itogcat:
				itogcat[im[4]].append(im)
			else:
				itogcat[im[4]] = list()
				itogcat[im[4]].append(im)

		# worksheet.write_string(row, 1, datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][1], "%Y-%m-%d"), "%d %B") + " - " + datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][2], "%Y-%m-%d"), "%d %B %Y"), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
		# worksheet.write_string(row, 1, datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][1], "%Y-%m-%d"), "%d %B") + " - " + datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][2], "%Y-%m-%d"), "%d %B %Y"), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
		# worksheet.write_string(row, 1, datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][1], "%Y-%m-%d"), "%d %B") + " - " + datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][2], "%Y-%m-%d"), "%d %B %Y"), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
		# worksheet.write_string(row, 1, datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][1], "%Y-%m-%d"), "%d %B") + " - " + datetime.datetime.strftime(datetime.datetime.strptime(meeting[0][2], "%Y-%m-%d"), "%d %B %Y"), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
		### Мандатная

		print('Документы готовы')
		workbook.close()
		self.close()

	def edit_pressed(self):

		# Get data from base
		database = db()
		editable_row = self.ui.tableWidget.currentRow()
		col = 0
		col_count = self.ui.tableWidget.columnCount()
		items = []
		while col < col_count:
			items.append(self.ui.tableWidget.item(editable_row, col).text())
			col += 1

		meet = database.select('SELECT * FROM meeting WHERE id=\'' + str(items[0]) + '\'')
		edit_meets = MeetingDialog(meet[0])
		#edit_meets.edit_meet(meet[0])
		edit_meets.exec_()

		'''# TODO: Получить новые данные'''
		meet = database.select('SELECT * FROM meeting WHERE id=\'' + str(items[0]) + '\'')
		col = 0
		for y in meet[0][:len(items)]:
			newitem = QtWidgets.QTableWidgetItem(re.sub(r'\\', r'', str(y)))
			newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
			self.ui.tableWidget.setItem(editable_row, col, newitem)
			self.ui.tableWidget.resizeColumnToContents(col)
			col += 1

		return

	def cancel_pressed(self):

		self.close()
