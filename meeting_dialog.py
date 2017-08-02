from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QMenu, QAction, QMessageBox
from meet import Ui_Dialog as createmeeting
from database_manager import DbManager as dbmanager
from models import Meeting, MeetReferee, MeetMember, Fighting, MemberStatus, FightingsInWeigth
from fightings_service import FightingsService
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
        self.ui = CreateMeetingSlots()
        self.ui.setupUi(self)
        self.ui.addButton.clicked.connect(self.add_member_pressed)
        self.ui.removeButton.clicked.connect(self.remove_member_pressed)
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

        #элементы листбокса участников храню отдельно
        self.meet_members_items = {}

        self.fighting_service = FightingsService(self.meet)

        try:
            self.fill_data()
        except Exception as e:
            print(e)

        if self.fighting_service.fightings_count:
            self.ui.addButton.setEnabled(False)
            self.ui.removeButton.setEnabled(False)

        self.initialize = True

        self.ui.weightcatCBox.setCurrentIndex(-1)
        self.ui.weightcatCBox.setCurrentIndex(0)

        self.ui.membersList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.membersList.customContextMenuRequested.connect(self.show_cmenu)

        self.ui.membersList.itemPressed.connect(self.memberListItem_pressed)
        self.ui.athletesList.itemPressed.connect(self.athletesListItem_pressed)


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

        self.fill_comboboxes()

        refs_in_meet_ids = []
        mems_in_meet_ids = []
        if self.meet:
            self.setWindowTitle("Изменение соревнования")
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

        self.define_meet_member_statuses()

        self.refresh_referees_list()
        self.refresh_colreferees_list()
        # TODO: Заполнить список спортсменов

    #определить статусы участников
    def define_meet_member_statuses(self):
        for member in self.meet_members:
            status = self.fighting_service.get_member_status(member)
            member.status = status

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
                self.meet_members_items[member.id] = item

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

    def add_member_pressed(self):

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

    def remove_member_pressed(self):

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
            self.meet.id = 0
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

        count = len(self.meet_members)
        #TODO: Если self.ui.meetCountEdit.text() пустое то установить его по количеству участников (боев будет не больше чем если каждый участник один выйдет на ринг)

        if self.ui.meetCountEdit.text() == '':
            self.ui.meetCountEdit.setText(str(count))

        self.save_meeting_data()

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

        round = self.fighting_service.get_current_round() + 1
        buttonReply = QMessageBox.question(self, 'Сообщение', 'Провести жеребьевку %d-го раунда?' % round)
        if buttonReply != QMessageBox.Yes:
            return

        # TODO: Проверить валидность данных

        validator = Valid()

        if not self.valid(validator.validString(self.ui.nameEdit.text())):
            return
        if not self.valid(validator.validDigit(self.ui.meetCountEdit.text())):
            return

        #проверка что можно провести жеребъевку следующего раунда соревнований
        drawing_allow, message = self.fighting_service.is_drawing_allow()
        if not drawing_allow:
            QMessageBox.information(self, 'Сообщение', message)
            return

        print("проверка доступности жеребьевки пройдена!")

        # TODO: Если self.ui.meetCountEdit.text() пустое то установить его по количеству участников (боев будет не больше чем если каждый участник один выйдет на ринг)
        count = len(self.meet_members)
        if self.ui.meetCountEdit.text() == '':
            self.ui.meetCountEdit.setText(str(count))

        self.save_meeting_data()

        members_by_weigth = {}

        self.fighting_service.meeting = self.meet
        self.define_meet_member_statuses()
        #разбираем по весовым категориям
        for member in self.meet_members:
            #для жеребьевки отбираем только победителей предыдущего раунда или участники
            if member.status not in [MemberStatus.WINNER, MemberStatus.MEMBER]:
                continue
            if member.weight_id in members_by_weigth:
                members_by_weigth[member.weight_id].append(member)
            else:
                members_by_weigth[member.weight_id] = [member]

        '''# TODO: Сделать жеребьевку'''
        # TODO: Отсортировать по рязряду (исправить в случае изменения порядка разрядов)
        # TODO: Сделать приоритет жеребьевки по разряду участника
        for key, value in members_by_weigth.items():
            try:
                self.sortition(key, value)
            except Exception as e:
                print(e)

        '''# TODO: Сделать выборку из групп пока количество больше 1'''

        print("жеребьевка произведена!")
        #self.close()
        try:
            self.fighting_service.refresh_fightings_info()
            self.define_meet_member_statuses()
            self.refresh_members_list()
        except Exception as e:
            print(e)

        return

    def cancel_pressed(self):

        self.close()

    #сохранение данных о соревновании
    def save_meeting_data(self):
        self.meet = self.get_meeting_values()

        '''# TODO: 1. Создать запись о соревновании '''
        '''# TODO: 2. Заполнить таблицу участников основываясь на ID созданного соревнования и ID участника'''

        '''# TODO: Если соревнование редактируется, то удалить старые данные'''
        '''# TODO: проверить не редактируется ли соревнование, если да, то удалить старые данные сортировки'''
        if self.meet.id:
            self.dbm.delete_meet_referee(self.meet.id)
            # удаляем только если еще не было боёв
            # if not count_f:
            # self.dbm.delete_meet_member(self.meet.id)
            # провести пережеребьевку текущего раунда ???
            # self.dbm.delete_fightings_by_meeting(self.meet.id)

        if self.meet.id:
            self.dbm.update_meeting(self.meet)
        else:
            self.meet = self.dbm.insert_meeting(self.meet)
            for member in self.meet_members:
                meet_member = MeetMember()
                meet_member.meeting_id = self.meet.id
                meet_member.member_id = member.id
                member.status = MemberStatus.MEMBER
                try:
                    self.dbm.insert_meet_member(meet_member)
                except Exception as e:
                    print(e)

        # сохраняем судей
        for referee in self.meet_referees:
            meet_referee = MeetReferee()
            meet_referee.meeting_id = self.meet.id
            meet_referee.referee_id = referee.id
            self.dbm.insert_meet_referee(meet_referee)


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
        #или если у участника нет соперника
        fighting = self.fighting_service.get_fighting(member)
        not_rival = False
        if fighting:
            if not fighting.member_a_id or not fighting.member_b_id:
                not_rival = True

        if not self.fighting_service.fightings_count or not_rival:
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

        fighting = self.fighting_service.get_fighting(member)
        #соперник
        member_rival = None
        if fighting.member_a_id == member.id:
            if fighting.member_b_id:
                member_rival = next((m for m in self.meet_members if m.id == fighting.member_b_id), None)
        if fighting.member_b_id == member.id:
            if fighting.member_a_id:
                member_rival = next((m for m in self.meet_members if m.id == fighting.member_a_id), None)

        member_status_rival = MemberStatus.MEMBER
        if member_status == MemberStatus.WINNER:
            member_status_rival = MemberStatus.LOSER
        if member_status == MemberStatus.LOSER:
            member_status_rival = MemberStatus.WINNER

        winner = None
        loser = None
        if member_status == MemberStatus.WINNER:
            winner = member
            loser = member_rival
        if member_status == MemberStatus.LOSER:
            winner = member_rival
            loser = member

        winner_id = winner.id if winner else None
        loser_id = loser.id if loser else None
        self.fighting_service.set_fighting_result(fighting, winner_id, loser_id)
        fighting.winner_id = winner_id
        fighting.loser_id = loser_id
        self.set_item_background(current_item, member_status)
        self.memberListItem_pressed(current_item)

        if member_rival:
            member_rival.status = member_status_rival
            member_rival_item = self.meet_members_items[member_rival.id]
            self.set_item_background(member_rival_item, member_status_rival)


    def memberListItem_pressed(self, item):
        member = item.data(QtCore.Qt.UserRole)
        self.ui.addButton.setEnabled(False)
        if self.fighting_service.fightings_count:
            self.ui.removeButton.setEnabled(False)
        else:
            self.ui.removeButton.setEnabled(True)

    def athletesListItem_pressed(self, item):
        member = item.data(QtCore.Qt.UserRole)
        self.ui.removeButton.setEnabled(False)
        if self.fighting_service.fightings_count:
            self.ui.addButton.setEnabled(False)
        else:
            self.ui.addButton.setEnabled(True)

    def set_item_background(self, item, member_status):
        #member = item.data(QtCore.Qt.UserRole)
        background = "white"
        if member_status == MemberStatus.WINNER:
            background = "green"
        if member_status == MemberStatus.LOSER:
            background = "red"
        if member_status == MemberStatus.WITHDRAW:
            background = "lightGray"
        item.setBackground(QtGui.QColor(background))
