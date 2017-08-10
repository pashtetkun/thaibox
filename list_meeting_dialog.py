from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QMessageBox
from list_meetings import Ui_Dialog as listmeeting
from database import Dbase as db
from database_manager import DbManager as dbmanager
from meeting_dialog import MeetingDialog
from fightings_service import FightingsService
import re
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell, xl_cell_to_rowcol
import datetime
import math
import subprocess


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
        self.meeting = None
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
        meeting = self.dbm.get_meeting(id)
        self.meeting = self.dbm.get_meeting(id)
        rings = self.dbm.get_all_rings()
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
        fightings = self.dbm.get_fightings_by_meeting(id)
        fightings_total = len(fightings)  # количество боев в соревновании
        dstart = datetime.datetime.strptime(self.start, "%Y-%m-%d")
        dend = datetime.datetime.strptime(self.end, "%Y-%m-%d")
        delta = dend - dstart
        deltaday = delta.days + 1 # учитываем и первый день соревнования

        path = self.name.replace("\\", "") + '.xlsx'

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

        workbook = xlsxwriter.Workbook(path)

        ###############################
        ### Список участников по рингам
        ###############################
        all_members = self.dbm.get_all_members()
        weight_categories = self.dbm.get_all_weight_categories()
        ringscount = len(rings)
        ''' количество боев на одном ринге в день'''
        fightings_per_day_per_ring = math.ceil(self.fightings_per_day/ringscount)
        for ring in rings:
            fightings_by_ring = [f for f in fightings if f.ring == ring.id]
            day_count = 0
            start_day = datetime.datetime.strptime(self.start, "%Y-%m-%d") #
            y = 0
            while day_count < meet_days_total:
                worksheet = workbook.add_worksheet(ring.name + str(day_count+1))

                c_width = 33.7
                e_width = 37.7
                f_width = 20.7
                g_width = 33.7
                h_width = 20.7
                i_width = 10.7
                j_width = 10.7

                '''# TODO: старт с первой строки'''
                row = 1
                col = 1

                '''# TODO: Название'''
                format_title = workbook.add_format({'font_name':'Times New Roman', 'font_size':'16', 'bold': True,
                                                    'align': 'center', 'valign': 'vcenter'})
                worksheet.set_row(row, 40.85)
                worksheet.merge_range('B2:H2', self.name, format_title)
                worksheet.merge_range('I2:J2', ring.name, formatmergeH(row, 'I:I', 'Times New Roman', '24', 'black', True,
                                                                        False, 0, 'center', 'vcenter', 40.85, i_width))
                ''''# TODO: Ринг вывести '''
                row += 1 # 2
                format_ring = workbook.add_format({'font_name':'Times New Roman', 'font_size':'16', 'bold': True})
                current_day = start_day + datetime.timedelta(days=day_count)
                worksheet.write_string(row, col, self.city + ", " + datetime.datetime.strftime(current_day, "%d %B %Y"), format_ring)
                format_time = workbook.add_format({'font_name': 'Times New Roman', 'font_size': '16', 'bold': True,
                                                    'align': 'right', 'valign': 'vcenter'})
                worksheet.set_row(row, 22)
                worksheet.merge_range('I3:J3', 'Время начала', format_time)
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
                worksheet.merge_range('I4:J5', 'Результат', formatmergeV(row, 'I:I', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 22, i_width))
                #worksheet.write(row, col+1, self.start)
                row += 1 #6
                iterator = 1

                ##### Вывести участников по количеству в день
                i = 0
                while i < fightings_per_day_per_ring:
                    if y < len(fightings_by_ring):
                        fighting = fightings_by_ring[y]
                    #for meet in members:
                        # print(meet)
                        member_a = next((m for m in all_members if m.id == fighting.member_a_id), None)
                        member_b = None
                        if fighting.member_b_id:
                            member_b = next((m for m in all_members if m.id == fighting.member_b_id), None)
                        weight_category = next((w for w in weight_categories if w.id == member_a.weight_id), None)

                        worksheet.write_string(row, 1, str(iterator), formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
                        worksheet.write_string(row, 2, weight_category.name.replace("\\", ""), formatmergeH(row, 'C:C', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, c_width))
                        worksheet.write_string(row, 3, str(self.current_meet), formatmergeH(row, 'D:D', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, 3.7))
                        worksheet.write_string(row, 4, member_a.fio.replace("\\", ""), formatmergeH(row, 'E:E', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, e_width))
                        worksheet.write_string(row, 5, member_a.region.replace("\\", ""), formatmergeH(row, 'F:F', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 33, f_width))
                        if member_b:
                            worksheet.write_string(row, 6, member_b.fio.replace("\\", ""), formatmergeH(row, 'G:G', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, g_width))
                            worksheet.write_string(row, 7, member_b.region.replace("\\", ""), formatmergeH(row, 'H:H', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 33, h_width))
                        else:
                            worksheet.write_string(row, 6, 'Нет участника', formatmergeH(row, 'G:G', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, g_width))
                            worksheet.write_string(row, 7, ' ', formatmergeH(row, 'H:H', 'Times New Roman', '10', 'black', True, False, 0, 'center', 'vcenter', 33, h_width))
                        worksheet.merge_range('I'+str(row)+':J'+str(row), '', formatmergeH(row, 'I:J', 'Times New Roman', '12', 'black', True, False, 0, 'center', 'vcenter', 33, i_width))

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
                worksheet.write_string(row, 7, mainreferee[0][0], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, h_width))
                row += 1
                worksheet.write_string(row, 1, "судья " + mainreferee[0][1], formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
                worksheet.write_string(row, 7, mainreferee[0][2], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, h_width))
                row += 1
                worksheet.write_string(row, 1, "Главный секретарь,", formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, 3.7))
                worksheet.write_string(row, 7, mainclerk[0][0], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', True, False, 0, 'left', 'vcenter', 15, h_width))
                row += 1
                worksheet.write_string(row, 1, "судья " + mainclerk[0][1], formatmergeH(row, 'B:B', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, 3.7))
                worksheet.write_string(row, 7, mainclerk[0][2], formatmergeH(row, 'H:H', 'Times New Roman', '12', 'black', False, False, 0, 'left', 'vcenter', 15, h_width))
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
        #QMessageBox.information(self, 'Сообщение', 'Документы готовы')
        #subprocess.call(path, shell=True)

        #workbook.close()

        try:
            self.export_drawing(self.meeting)
        except Exception as e:
            print(e)

        self.close()

    #Вывод сетки жеребьевки
    def export_drawing(self, meeting):
        fighting_service = FightingsService(meeting)
        active_weight_categories = fighting_service.get_active_weight_categories()

        pathDrawing = self.name.replace("\\", "") + '_сетки жеребьевки.xlsx'
        workbook = xlsxwriter.Workbook(pathDrawing)

        #fightings = self.dbm.get_fightings_by_meeting(meeting.id)
        #members = self.dbm.get_meet_members(meeting.id)
        #weight_categories = self.dbm.get_all_weight_categories()

        #fighting_service
        for wcat in active_weight_categories:
            self.create_drawing_sheet(workbook, wcat)
        workbook.close()

    def create_drawing_sheet(self, workbook, wcat):
        sheet_name = wcat.name if len(wcat.name) < 31 else wcat.name[:31]
        worksheet = workbook.add_worksheet(sheet_name)

        print(wcat.name)

        widthColPage1 = 0.92  # ширина колонок на первой странице
        widthColPage2 = 2.43  # ширина колонок на второй странице
        rangeColPage1 = 'A:BO'
        rangeColPage2 = 'BQ:CU'
        hiddenCol = 'BP:BP'

        heightRow = 4.5

        cell_left_top = xl_cell_to_rowcol('A1')
        cell_right_top = xl_cell_to_rowcol('A387')
        cell_left_bottom = xl_cell_to_rowcol('C387')
        cell_right_bottom = xl_cell_to_rowcol('CU387')
        print(cell_left_top, cell_right_top, cell_left_bottom, cell_right_bottom)

        worksheet.hide_gridlines(2)

        for row in range(cell_right_bottom[0]):
            worksheet.set_row(row, heightRow)

        # размеры колонок
        worksheet.set_column(rangeColPage1, widthColPage1)
        worksheet.set_column(rangeColPage2, widthColPage2)
        worksheet.set_column(hiddenCol, None, None, {'hidden': True})

        #######################################
        #шапка
        #######################################
        format_header_big = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                             'align': 'center', 'valign': 'top', 'font_size': 11})
        format_header_small = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                                 'align': 'center', 'valign': 'top', 'font_size': 10})
        worksheet.merge_range('F1:BN8', self.meeting.name, format_header_big)
        worksheet.merge_range('F9:BN11', 'с %s по %s, %s' % (self.meeting.start_date, self.meeting.end_date,
                                                             self.meeting.city), format_header_small)
        worksheet.merge_range('F12:BN14', wcat.name, format_header_small)

        #######################################
        #сетка жеребьевки
        #######################################
        format_merge_fighting_member = workbook.add_format({'bg_color': 'white'})
        format_border_top = workbook.add_format({'top': 1})
        format_border_bottom = workbook.add_format({'bottom': 1})
        format_border_right = workbook.add_format({'right': 1})
        format_border_left = workbook.add_format({'left': 1})
        format_border_result = workbook.add_format({'right': 1, 'top': 1, 'bottom': 1})
        format_border_corner_top_right = workbook.add_format({'right': 1, 'top': 1})
        format_border_corner_bottom_right = workbook.add_format({'right': 1, 'bottom': 1})
        format_border_all = workbook.add_format({'right': 1, 'top': 1, 'bottom': 1, 'left': 1})

        #стадия 1
        template_stage1_merge = 'C%d:AA%d'
        stage1_fightings = 16
        stage1_first_row_fightings_top = 17
        stage1_first_row_fightings_bottom = 23
        stage1_interval_fightings = 10
        for i in range(stage1_fightings):
            #участник 1
            num_top = stage1_first_row_fightings_top+i*stage1_interval_fightings
            merge_cells_top = template_stage1_merge % (num_top, num_top+1)
            worksheet.merge_range(merge_cells_top, '', format_merge_fighting_member)

            row = stage1_first_row_fightings_top + 2 + i * stage1_interval_fightings
            row_col_start = xl_cell_to_rowcol('C%d' % row)
            row_col_end = xl_cell_to_rowcol('Z%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row - 1, col, '', format_border_top)

            #участник 2
            num_bottom = stage1_first_row_fightings_bottom + i * stage1_interval_fightings
            merge_cells_bottom = template_stage1_merge % (num_bottom, num_bottom + 1)
            worksheet.merge_range(merge_cells_bottom, '', format_merge_fighting_member)

            row = stage1_first_row_fightings_bottom - 1 + i * stage1_interval_fightings
            row_col_start = xl_cell_to_rowcol('C%d' % row)
            row_col_end = xl_cell_to_rowcol('Z%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row - 1, col, '', format_border_bottom)

            #результат
            row = stage1_first_row_fightings_top + 2 + i * stage1_interval_fightings
            merge_cells_result1 = 'R%d:Z%d' % (row, row+3)
            worksheet.merge_range(merge_cells_result1, '', format_border_result)

        #стадия 2
        template_stage2_merge = 'AA%d:AM%d'
        stage2_fightings = 8
        stage2_first_row_fightings_top = 19
        stage2_first_row_fightings_bottom = 31
        stage2_interval_fightings = 20
        for i in range(stage2_fightings):
            #участник 1
            num_top = stage2_first_row_fightings_top+i*stage2_interval_fightings
            merge_cells_top = template_stage2_merge % (num_top, num_top+1)
            worksheet.merge_range(merge_cells_top, '', format_merge_fighting_member)

            row = stage2_first_row_fightings_top + 2 + i * stage2_interval_fightings
            row_col_start = xl_cell_to_rowcol('AA%d' % row)
            row_col_end = xl_cell_to_rowcol('AG%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row - 1, col, '', format_border_top)

            #участник 2
            num_bottom = stage2_first_row_fightings_bottom + i * stage2_interval_fightings
            merge_cells_bottom = template_stage2_merge % (num_bottom, num_bottom + 1)
            worksheet.merge_range(merge_cells_bottom, '', format_merge_fighting_member)

            row = stage2_first_row_fightings_bottom - 1 + i * stage2_interval_fightings
            row_col_start = xl_cell_to_rowcol('AA%d' % row)
            row_col_end = xl_cell_to_rowcol('AG%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row - 1, col, '', format_border_bottom)

            # результат
            row1 = stage2_first_row_fightings_top + 2 + i * stage2_interval_fightings
            row2 = stage2_first_row_fightings_bottom - 1 + i * stage2_interval_fightings
            merge_cells_result2 = 'AB%d:AG%d' % (row1, row2)
            worksheet.merge_range(merge_cells_result2, '', format_border_result)

        #стадия 3
        template_stage3_merge = 'AH%d:AT%d'
        stage3_fightings = 4
        stage3_first_row_fightings_top = 23
        stage3_first_row_fightings_bottom = 46
        stage3_interval_fightings = 40
        for i in range(stage3_fightings):
            #участник 1
            num_top = stage3_first_row_fightings_top+i*stage3_interval_fightings
            merge_cells_top = template_stage3_merge % (num_top, num_top+2)
            worksheet.merge_range(merge_cells_top, '', format_merge_fighting_member)

            row = stage3_first_row_fightings_top + 2 + i * stage3_interval_fightings
            row_col_start = xl_cell_to_rowcol('AH%d' % row)
            row_col_end = xl_cell_to_rowcol('AN%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row, col, '', format_border_top)

            #участник 2
            num_bottom = stage3_first_row_fightings_bottom + i * stage3_interval_fightings
            merge_cells_bottom = template_stage3_merge % (num_bottom, num_bottom + 2)
            worksheet.merge_range(merge_cells_bottom, '', format_merge_fighting_member)

            row = stage3_first_row_fightings_bottom - 1 + i * stage3_interval_fightings
            row_col_start = xl_cell_to_rowcol('AH%d' % row)
            row_col_end = xl_cell_to_rowcol('AN%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row - 1, col, '', format_border_bottom)

            # результат
            row = stage3_first_row_fightings_top + 11 + i * stage3_interval_fightings
            merge_cells_result3 = 'AI%d:AN%d' % (row, row+3)
            worksheet.merge_range(merge_cells_result3, '')

            #правая граница
            row1 = stage3_first_row_fightings_top + 1 + i * stage3_interval_fightings
            row2 = stage3_first_row_fightings_bottom - 1 + i * stage3_interval_fightings
            cell_template = 'AN%d'
            for j in range(row2-row1+1):
                format = format_border_right
                if j == 0:
                    format == format_border_corner_top_right
                if j == row2-row1:
                    format == format_border_corner_bottom_right
                cell = cell_template % (row1+j)
                worksheet.write(cell, '', format)

        #стадия 4
        template_stage4_merge = 'AO%d:BA%d'
        stage4_fightings = 2
        stage4_first_row_fightings_top = 33
        stage4_first_row_fightings_bottom = 76
        stage4_interval_fightings = 80

        for i in range(stage4_fightings):
            #участник 1
            num_top = stage4_first_row_fightings_top+i*stage4_interval_fightings
            merge_cells_top = template_stage4_merge % (num_top, num_top+2)
            worksheet.merge_range(merge_cells_top, '', format_merge_fighting_member)

            row = stage4_first_row_fightings_top + 2 + i * stage4_interval_fightings
            row_col_start = xl_cell_to_rowcol('AO%d' % row)
            row_col_end = xl_cell_to_rowcol('AU%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row, col, '', format_border_top)

            #участник 2
            num_bottom = stage4_first_row_fightings_bottom + i * stage4_interval_fightings
            merge_cells_bottom = template_stage4_merge % (num_bottom, num_bottom + 2)
            worksheet.merge_range(merge_cells_bottom, '', format_merge_fighting_member)

            row = stage4_first_row_fightings_bottom - 1 + i * stage4_interval_fightings
            row_col_start = xl_cell_to_rowcol('AO%d' % row)
            row_col_end = xl_cell_to_rowcol('AU%d' % row)
            for j in range(row_col_end[1] - row_col_start[1] + 1):
                col = row_col_start[1] + j
                worksheet.write(row - 1, col, '', format_border_bottom)

            # результат
            row = stage4_first_row_fightings_top + 21 + i * stage4_interval_fightings
            merge_cells_result4 = 'AI%d:AN%d' % (row, row + 3)
            worksheet.merge_range(merge_cells_result4, '')

            # правая граница
            row1 = stage4_first_row_fightings_top + 1 + i * stage4_interval_fightings
            row2 = stage4_first_row_fightings_bottom - 1 + i * stage4_interval_fightings
            cell_template = 'AU%d'
            for j in range(row2 - row1 + 1):
                format = format_border_right
                if j == 0:
                    format == format_border_corner_top_right
                if j == row2 - row1:
                    format == format_border_corner_bottom_right
                cell = cell_template % (row1 + j)
                worksheet.write(cell, '', format)



        #стадия 5
        template_stage5_merge = 'AV%d:BJ%d'
        stage5_first_row_fightings_top = 53
        stage5_first_row_fightings_bottom = 136

        #участник 1
        num_top = stage5_first_row_fightings_top
        merge_cells_top = template_stage5_merge % (num_top, num_top + 2)
        worksheet.merge_range(merge_cells_top, '', format_merge_fighting_member)

        row = stage5_first_row_fightings_top + 2
        row_col_start = xl_cell_to_rowcol('AV%d' % row)
        row_col_end = xl_cell_to_rowcol('BB%d' % row)
        for j in range(row_col_end[1] - row_col_start[1] + 1):
            col = row_col_start[1] + j
            worksheet.write(row, col, '', format_border_top)

        #участник 2
        num_bottom = stage5_first_row_fightings_bottom
        merge_cells_bottom = template_stage5_merge % (num_bottom, num_bottom + 2)
        worksheet.merge_range(merge_cells_bottom, '', format_merge_fighting_member)

        row = stage5_first_row_fightings_bottom - 1
        row_col_start = xl_cell_to_rowcol('AV%d' % row)
        row_col_end = xl_cell_to_rowcol('BB%d' % row)
        for j in range(row_col_end[1] - row_col_start[1] + 1):
            col = row_col_start[1] + j
            worksheet.write(row - 1, col, '', format_border_bottom)

        # результат
        row = stage5_first_row_fightings_top + 41
        merge_cells_result5 = 'AT%d:BB%d' % (row, row + 4)
        worksheet.merge_range(merge_cells_result5, '')

        # правая граница
        row1 = stage5_first_row_fightings_top
        row2 = stage5_first_row_fightings_bottom - 1
        cell_template = 'BB%d'
        for j in range(row2 - row1 + 1):
            format = format_border_right
            if j == 0:
                format == format_border_corner_top_right
            if j == row2 - row1:
                format == format_border_corner_bottom_right
            cell = cell_template % (row1 + j)
            worksheet.write(cell, '', format)

        #стадия 6
        worksheet.merge_range('BC93:BN95', '', format_merge_fighting_member)
        row = 95
        row_col_start = xl_cell_to_rowcol('BC%d' % row)
        row_col_end = xl_cell_to_rowcol('BN%d' % row)
        for j in range(row_col_end[1] - row_col_start[1] + 1):
            col = row_col_start[1] + j
            worksheet.write(row, col, '', format_border_top)

        worksheet.write('BC93', 'чемпион')

        ##########################################
        #судьи
        ##########################################
        main_referee = self.dbm.get_referee(self.meeting.main_referee_id)
        main_referee_category = self.dbm.get_referee_category(main_referee.category_id)
        main_referee_region = self.dbm.get_region(main_referee.region_id)
        main_clerk = self.dbm.get_referee(self.meeting.main_clerk_id)
        main_clerk_category = self.dbm.get_referee_category(main_clerk.category_id)
        main_clerk_region = self.dbm.get_region(main_clerk.region_id)

        format_main_referee = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                             'valign': 'bottom', 'font_size': 9})
        format_main_referee_info = workbook.add_format({'font_name': 'Times New Roman', 'bold': False,
                                                   'valign': 'bottom', 'font_size': 9})

        format_main_clerk = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                                   'valign': 'top', 'font_size': 9})

        format_main_clerk_info = workbook.add_format({'font_name': 'Times New Roman', 'bold': False,
                                                 'valign': 'bottom', 'font_size': 9})


        worksheet.merge_range('C177:M178', 'Главный судья', format_main_referee)
        worksheet.merge_range('C179:M180', 'судья кат ' + main_referee_category.name, format_main_referee_info)
        worksheet.merge_range('C181:M182', 'Главный секретарь', format_main_clerk)
        worksheet.merge_range('C183:M184', 'судья кат ' + main_clerk_category.name, format_main_clerk_info)

        worksheet.merge_range('AA177:AL178', main_referee.get_short_name(), format_main_referee)
        worksheet.merge_range('AA179:AL180', main_referee_region.name, format_main_referee_info)
        worksheet.merge_range('AA181:AL182', main_clerk.get_short_name(), format_main_clerk)
        worksheet.merge_range('AA183:AL184', main_clerk_region.name, format_main_clerk_info)

        worksheet.merge_range('AO170:AP171', '1')
        worksheet.merge_range('AQ170:BN171', '', format_border_bottom)
        worksheet.merge_range('AO174:AP175', '2')
        worksheet.merge_range('AQ174:BN175', '', format_border_bottom)
        worksheet.merge_range('AO178:AP179', '3')
        worksheet.merge_range('AQ178:BN179', '', format_border_bottom)
        worksheet.merge_range('AO182:AP183', '4')
        worksheet.merge_range('AQ182:BN183', '', format_border_bottom)

        ############################
        #вторая страница
        ############################

        format_table_header = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                                   'align': 'center', 'valign': 'center', 'font_size': 12})
        format_table_place = workbook.add_format({'font_name': 'Times New Roman', 'bold': False,
                                                   'valign': 'bottom', 'font_size': 10})
        format_table_date = workbook.add_format({'font_name': 'Times New Roman', 'bold': False,
                                                   'align': 'right', 'valign': 'bottom', 'font_size': 10})

        worksheet.merge_range('BT185:CS192', self.meeting.name, format_table_header)
        worksheet.merge_range('BQ195:BZ197', self.meeting.city, format_table_place)
        worksheet.merge_range('CO195:CU197', 'с %s по %s' % (self.meeting.start_date, self.meeting.end_date),
                              format_table_date)

        format_table_protocol = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                                   'align': 'center', 'valign': 'vcenter', 'font_size': 14, 'border': 1})
        format_table_thaibox = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                                     'align': 'center', 'valign': 'vcenter', 'font_size': 12,
                                                     'left': 1})
        format_table_wcat = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                                    'align': 'center', 'valign': 'vcenter', 'font_size': 10,
                                                    'top': 1, 'bottom': 1})
        format_table_count = workbook.add_format({'font_name': 'Times New Roman', 'bold': True,
                                                 'align': 'center', 'valign': 'vcenter', 'font_size': 10,
                                                 'right': 1})


        worksheet.merge_range('BQ200:CU202', 'Стартовый протокол соревнований', format_table_protocol)
        worksheet.merge_range('BQ203:BV205', 'Тайский бокс', format_table_thaibox)
        worksheet.merge_range('BW203:CN205', wcat.name, format_table_wcat)
        worksheet.merge_range('CO203:CU205', '32 человека', format_table_count)

        format_table_cell_center = workbook.add_format({'font_name': 'Times New Roman', 'bold': False,
                                                  'align': 'center', 'valign': 'top', 'font_size': 10,
                                                  'border': 1})
        format_table_cell_left = workbook.add_format({'font_name': 'Times New Roman', 'bold': False,
                                                 'valign': 'top', 'font_size': 10,
                                                 'border': 1})

        worksheet.merge_range('BQ206:BR208', '№ п/жр', format_table_cell_center)
        worksheet.merge_range('BS206:BZ208', 'Участник / команда', format_table_cell_center)
        worksheet.merge_range('CA206:CD208', 'Дата рождения', format_table_cell_center)
        worksheet.merge_range('CE206:CH208', 'Разряд', format_table_cell_center)
        worksheet.merge_range('CI206:CN208', 'Регион', format_table_cell_center)
        worksheet.merge_range('CO206:CU208', 'Тренер', format_table_cell_center)

        meet_members = self.dbm.get_meet_members(self.meeting.id)
        first_row = 209
        for i in range(32):
            member_and_team = ''
            birthday = ''
            rank = ''
            region = ''
            trainer = ''
            if i <= len(meet_members)-1:
                member = meet_members[i]
                member_and_team = '%s, %s' % (member.get_short_name(), member.club)
                birthday = member.birthday
                member_category = self.dbm.get_member_category(member.category)
                rank = member_category.name
                region = member.region.replace('\\', "")
                trainer = member.trainer.replace('\\', "")

            row = first_row  + i * 5
            worksheet.merge_range('BQ%d:BR%d' % (row, row+4), str(i+1), format_table_cell_center)
            worksheet.merge_range('BS%d:BZ%d' % (row, row+4), member_and_team.replace('\\', ""), format_table_cell_left)
            worksheet.merge_range('CA%d:CD%d' % (row, row+4), birthday, format_table_cell_center)
            worksheet.merge_range('CE%d:CH%d' % (row, row+4), rank, format_table_cell_center)
            worksheet.merge_range('CI%d:CN%d' % (row, row+4), region, format_table_cell_left)
            worksheet.merge_range('CO%d:CU%d' % (row, row+4), trainer, format_table_cell_left)

        worksheet.merge_range('BQ371:BX373', 'Главный судья', format_main_referee)
        worksheet.merge_range('BQ374:BX376', 'судья кат ' + main_referee_category.name, format_main_referee_info)
        worksheet.merge_range('BQ377:BX379', 'Главный секретарь', format_main_clerk)
        worksheet.merge_range('BQ380:BX382', 'судья кат ' + main_clerk_category.name, format_main_clerk_info)

        worksheet.merge_range('CG371:CN373', main_referee.get_short_name(), format_main_referee)
        worksheet.merge_range('CG374:CN376', main_referee_region.name, format_main_referee_info)
        worksheet.merge_range('CG377:CN379', main_clerk.get_short_name(), format_main_clerk)
        worksheet.merge_range('CG380:CN382', main_clerk_region.name, format_main_clerk_info)

        worksheet.merge_range('CO379:CU382', 'Дата проведения мандатной комиссии')





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
