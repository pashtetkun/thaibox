from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import qApp, QWidget, QDialog
from record import RecordDialog
from add_referee_dialog import AddRefereeDialog
from list_referee_dialog import ListRefereeDialog
from add_member_dialog import AddMemberDialog
from meeting_dialog import MeetingDialog
from list_members_dialog import ListMemberDialog
from list_meeting_dialog import ListMeetingDialog


class RightClickMenu(QtWidgets.QMenu):

	def addcategory(self):
		self.category = RecordDialog(id="category")
		self.category.exec_()

	def addposition(self):
		self.position = RecordDialog(id="position")
		self.position.exec_()

	def addregion(self):
		self.region = RecordDialog(id="region")
		self.region.exec_()

	def addreferee(self):
		referee = AddRefereeDialog()
		referee.exec_()

	def listreferees(self):
		list = ListRefereeDialog()
		list.exec_()

	# def schedulereferees(self):
	#
	# 	return

	def addmember(self):
		member = AddMemberDialog()
		member.exec_()

	def listmembers(self):
		list = ListMemberDialog()
		list.exec_()

	def addweightcategory(self):
		self.category = RecordDialog(id="weight")
		self.category.exec_()

	def meeting(self):

		game = MeetingDialog()
		game.exec_()

	def listmeeting(self):
		list = ListMeetingDialog()
		list.exec_()
		#pass

	# def sortitionmembers(self):
	#
	# 	return

	def __init__(self, parent=None):
		QtWidgets.QMenu.__init__(self, "File", parent)

		#icon = QtGui.QIcon.fromTheme("folder")
		icon = QtGui.QIcon('hand.ico')

		addrefereeAction = QtWidgets.QAction(icon, "Добавить судью", self)
		addrefereeAction.triggered.connect(self.addreferee)
		self.addAction(addrefereeAction)
		addcategoryAction = QtWidgets.QAction(icon, "Добавить судейскую категорию", self)
		addcategoryAction.triggered.connect(self.addcategory)
		self.addAction(addcategoryAction)
		addpositionAction = QtWidgets.QAction(icon, "Добавить должность", self)
		addpositionAction.triggered.connect(self.addposition)
		self.addAction(addpositionAction)
		addregionAction = QtWidgets.QAction(icon, "Добавить регион", self)
		addregionAction.triggered.connect(self.addregion)
		self.addAction(addregionAction)
		listrefereesAction = QtWidgets.QAction(icon, "Список судей", self)
		listrefereesAction.triggered.connect(self.listreferees)
		self.addAction(listrefereesAction)
		# schedulerefereesAction = QtWidgets.QAction(icon, "График работы судей", self)
		# schedulerefereesAction.triggered.connect(self.schedulereferees)
		# self.addAction(schedulerefereesAction)

		self.addSeparator()

		addmemberAction = QtWidgets.QAction(icon, "Добавить спортсмена", self)
		addmemberAction.triggered.connect(self.addmember)
		self.addAction(addmemberAction)
		addweightcategoryAction = QtWidgets.QAction(icon, "Добавить весовую категорию", self)
		addweightcategoryAction.triggered.connect(self.addweightcategory)
		# TODO: Сделать упорядочивание введенных весовых категорий участников
		self.addAction(addweightcategoryAction)
		listmembersAction = QtWidgets.QAction(icon, "Список спортсменов", self)
		listmembersAction.triggered.connect(self.listmembers)
		self.addAction(listmembersAction)

		self.addSeparator()
		# TODO: Тут генерятся документы и таблицы

		meetingAction = QtWidgets.QAction(icon, "Создать соревнование", self)
		meetingAction.triggered.connect(self.meeting)
		self.addAction(meetingAction)
		listmeetingAction = QtWidgets.QAction(icon, "Список соревнований", self)
		listmeetingAction.triggered.connect(self.listmeeting)
		self.addAction(listmeetingAction)
		# sortitionmembersAction = QtWidgets.QAction(icon, "Members Sortition", self)
		# sortitionmembersAction.triggered.connect(self.sortitionmembers)
		# self.addAction(sortitionmembersAction)

		self.addSeparator()

		icon = QtGui.QIcon.fromTheme("application-exit")
		exitAction = QtWidgets.QAction(icon, "Exit", self)
		exitAction.triggered.connect(qApp.quit)
		self.addAction(exitAction)


class SystemTray(QtWidgets.QSystemTrayIcon):
	def __init__(self, parent=None):
		QtWidgets.QSystemTrayIcon.__init__(self, parent)
		#self. setIcon(QtGui.QIcon('./picts/icon.png'))
		self.setIcon(QtGui.QIcon('logo64.ico'))

		self.menu = RightClickMenu()
		self.setContextMenu(self.menu)