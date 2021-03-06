import sys, os
import sqlite3
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtWidgets import QFileDialog, QDialog
from config import Config as cfg
from database_slots import CreateBaseSlots
from starting import Ui_dialog as insdata
import re


CURRENT_VERSION = 6

class CreateBase(QDialog):
    def __init__(self):
        super(CreateBase, self).__init__()
        self.ui = CreateBaseSlots()
        self.ui.setupUi(self)
        self.ui.Ok.clicked.connect(self.ok_press)
        self.ui.Cancel.clicked.connect(self.cancel_press)

    def ok_press(self):
        self.CreateDB = False
        self.close()

    def cancel_press(self):
        self.CreateDB = True
        self.close()

class InsertingDataSlot(insdata):
    def __init__(self):
        pass

class InsertingData(QDialog):
    def __init__(self):
        super(InsertingData, self).__init__()
        self.ui = InsertingDataSlot()
        self.ui.setupUi(self)
        self.ui.progress.setValue(0)

class Dbase():

    def __init__(self):

        # Get config parameters
        conf = cfg()
        conf.readconfig()

        if len(conf.base_path) == 0:
            conf.base_path.append(os.getcwd())
        #print(conf.base_path[0])
        #print(conf.base_file[0])
        self.path = conf.base_path[0] + '/' + conf.base_file[0]
        self.path_el = re.split('\/', self.path)  # проверить как ведет себя в Windows
        self.file = self.path_el[-1]

        self.connection = None
        self.cursor = None

        try:
            if self.base_exist(self.path):
                self.connection = self.connect(self.path)
                self.cursor = self.connection.cursor()
                # self.conn = sqlite3.connect(path)
                self.check_updates(CURRENT_VERSION)
            else:
                print("Base don't exist")
                '''# TODO: database: Спросить надо ли указать другой путь к базе'''
                self.create = CreateBase()
                self.create.exec_()

                if self.create.CreateDB:
                    # создать базу чистуаю данных
                    self.base_create(self.path)
                    print("Creating...")
                    print("Base created.")
                else:
                    self.change_path_base()

        except IOError as e:
            print(e)
        except Exception as e:
            print(e)

    def find_base(self, path):

        # print(path)
        if self.base_exist(path + '/' + self.file):
            return True
        else:
            '''# TODO: database: Спросить надо ли указать другой путь к базе'''
            self.create = CreateBase()
            self.create.exec_()
            if self.create.CreateDB:
                # создать базу чистуаю данных
                self.base_create(path)
            else:
                self.change_path_base()

    def change_path_base(self):
        # изменить путь к базе данных
        self.path = str(QFileDialog.getExistingDirectory())
        conf = cfg()
        conf.updateconfig(self.path)
        self.find_base(self.path)

    def base_exist(self, filename):

        if os.path.exists(filename):
            return True
        else:
            return False

    def base_create(self, filename):

        def default_data(cursor):

            refereepos = ["Главный судья", "Главный секретарь", "Зам.главного судьи", "Рефери", "Судья сбоку ринга"]
            refereecat = ["MK(IFMA)/BK", "MK(IFMA)", "BK", "I кат.", "II кат.", "III кат."]
            region = ["Московская обл.", "Санк-Петербург", "Калининградская обл.", "Нижегородская обл.", "Новгородская обл.", "Челябинская обл.", "респ.Башкортостан"]
            # Default data for region
            for i in region:
                cursor.execute("INSERT INTO region(region) VALUES(\"" + i + "\")")
            # Default data for referee category
            for i in refereecat:
                cursor.execute("INSERT INTO refereecat(category) VALUES(\"" + i + "\")")
            # Default data for referee position
            for i in refereepos:
                cursor.execute("INSERT INTO refereepos(position) VALUES(\"" + i + "\")")

        # TODO: Сделать splash экран во время создания базы данных
        #self.insertdata = InsertingData()
        #pixmap = QPixmap('')
        #self.insertdata = QSplashScreen(pixmap)
        #self
        #self.insertdata.show()

        self.conn = self.connect(filename)
        self.cursor = self.conn.cursor()
        #self.insertdata.ui.progress.setValue(10)

        # TODO: создать таблицы
        referee = "CREATE TABLE referee (id INTEGER UNIQUE PRIMARY KEY ASC AUTOINCREMENT, fio CHAR (255), position INT (3) REFERENCES refereepos (id) DEFAULT (1), region INT (3) REFERENCES region (id)	DEFAULT (1), category INT (3) REFERENCES refereecat (id) DEFAULT (1));"
        refereecat = "CREATE TABLE refereecat (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, category CHAR (255));"
        refereepos = "CREATE TABLE refereepos (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, position CHAR (255));"
        region = "CREATE TABLE region (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, region CHAR (255));"
        sex = "CREATE TABLE sex (id  INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, sex CHAR (255));"
        members = "CREATE TABLE members (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, fio CHAR (255), bday DATE NOT NULL DEFAULT (date()), sex INT(1) REFERENCES sex (id) DEFAULT (1), weight INT (3) REFERENCES weightcategory (id), category CHAR (255), club CHAR (255), region CHAR (255), city CHAR (255), trainer CHAR (255));"
        ring = "CREATE TABLE ring (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, ring CHAR (255));"
        weightcategory = "CREATE TABLE weightcategory (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, wcategory CHAR (255) UNIQUE);"
        meeting = "CREATE TABLE meeting (id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name CHAR (254), sdate DATE, edate DATE, city CHAR (254), meetcount INTEGER (3), mainreferee INTEGER REFERENCES referee (id), mainclerk INTEGER REFERENCES referee (id));"
        meetmembers = "CREATE TABLE meetmembers (id INTEGER PRIMARY KEY ASC AUTOINCREMENT, meeting INTEGER REFERENCES meeting (id), members INTEGER REFERENCES members (id));"
        meetreferees = "CREATE TABLE meetreferees (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, meeting INTEGER REFERENCES meeting (id), referee INTEGER REFERENCES referee (id));"
        sortition = """CREATE TABLE sortition 
                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                        idmeet INTEGER (9) REFERENCES meeting (id), 
                        membera INTEGER (9) REFERENCES members (id), 
                        wina BOOLEAN DEFAULT False, 
                        memberb INTEGER (9) REFERENCES members (id) DEFAULT (0), 
                        winb BOOLEAN DEFAULT False, 
                        ring INTEGER (2) REFERENCES ring (id),
                        fractional_round INTEGER (9) NOT NULL,
                        weightcategory_id INTEGER (9) REFERENCES weightcategory (id));"""
        category = "CREATE TABLE category (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, category CHAR (255));"
        version = """CREATE TABLE version (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, version int DEFAULT(0));"""
        fightings = """CREATE TABLE fightings 
                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                        meeting INTEGER (9) REFERENCES meeting (id),
                        fractional_round INTEGER (9) NOT NULL,
                        membera INTEGER (9) REFERENCES members (id) NOT NULL, 
                        memberb INTEGER (9) REFERENCES members (id), 
                        ring INTEGER (2) REFERENCES ring (id),
                        winner INTEGER (9) REFERENCES members (id),
                        loser INTEGER (9) REFERENCES members (id),
                        weightcategory_id INTEGER (9) REFERENCES weightcategory (id),
                        order_num INTEGER (9) NOT NULL);"""
        self.cursor.execute(referee)
        self.cursor.execute(refereecat)
        self.cursor.execute(refereepos)
        self.cursor.execute(region)
        self.cursor.execute(sex)
        self.cursor.execute(members)
        self.cursor.execute(ring)
        self.cursor.execute(weightcategory)
        self.cursor.execute(meeting)
        self.cursor.execute(meetmembers)
        self.cursor.execute(meetreferees)
        self.cursor.execute(sortition)
        self.cursor.execute(category)
        self.cursor.execute(version)
        self.cursor.execute(fightings)

        self.conn.commit()

        default_data(self.cursor)
        self.conn.commit()

        self.cursor.close()

        # TODO: Заполнить таблицы
        self.ins_upd("INSERT INTO sex (sex) VALUES (\"" + "мужской" + "\")")
        self.ins_upd("INSERT INTO sex (sex) VALUES (\"" + "женский" + "\")")
        # self.insertdata.ui.progress.setValue(10)
        self.ins_upd("INSERT INTO ring (ring) VALUES (\"" + "Ринг А" + "\")")
        self.ins_upd("INSERT INTO ring (ring) VALUES (\"" + "Ринг Б" + "\")")
        # разряд
        # Не забывать испралять нижший и высший разряд в алгоритме жеребьевки (meeting_dialog.py)
        self.ins_upd("INSERT INTO category (category) VALUES (\"" + "5-й разряд" + "\")")
        self.ins_upd("INSERT INTO category (category) VALUES (\"" + "4-й разряд" + "\")")
        self.ins_upd("INSERT INTO category (category) VALUES (\"" + "3-й разряд" + "\")")
        self.ins_upd("INSERT INTO category (category) VALUES (\"" + "2-й разряд" + "\")")
        self.ins_upd("INSERT INTO category (category) VALUES (\"" + "1-й разряд" + "\")")
        self.ins_upd("INSERT INTO category (category) VALUES (\"" + "КМС" + "\")")
        self.ins_upd("INSERT INTO category (category) VALUES (\"" + "МС" + "\")")
        # self.insertdata.ui.progress.setValue(20)
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 51 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 57 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 60 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 63.5 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 67 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 71 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 75 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 81 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 86 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины до 91 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Мужчины свыше 91 кг" + "\")")
        # self.insertdata.ui.progress.setValue(30)
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 48 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 51 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 54 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 57 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 60 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 63.5 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 67 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины до 75 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Женщины свыше 75 кг" + "\")")
        #self.insertdata.ui.progress.setValue(40)
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 51 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 54 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 57 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 63.5 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 67 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 71 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 75 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 81 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юниоры 16-17 лет до 91 кг и выше" + "\")")
        #self.insertdata.ui.progress.setValue(50)
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 42 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 45 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 48 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 51 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 54 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 57 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 60 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 63.5 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 67 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет до 71 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 14-15 лет свыше 81 кг" + "\")")
        #self.insertdata.ui.progress.setValue(60)
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Девушки 14-15 лет до 51 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Девушки 14-15 лет до 54 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Девушки 14-15 лет до 60 кг" + "\")")
        #self.insertdata.ui.progress.setValue(70)
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 32 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 34 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 40 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 42 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 44 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 46 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 48 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 50 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 54 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 56 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 67 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Юноши 12-13 лет до 71 кг" + "\")")
        #self.insertdata.ui.progress.setValue(90)
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Девушки 12-13 лет до 46 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Девушки 12-13 лет до 48 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Девушки 12-13 лет до 52 кг" + "\")")
        self.ins_upd("INSERT INTO weightcategory(wcategory) VALUES (\"" + "Девушки 12-13 лет до 60 кг" + "\")")

        self.ins_upd("INSERT INTO version(version) VALUES (%d)" % CURRENT_VERSION)
        #self.insertdata.ui.progress.setValue(100)

        #self.insertdata.close()

    def connect(self, path):

        return sqlite3.connect(path)

    def select(self, select, params=None):

        self.conn = self.connect(self.path)
        self.cursor = self.conn.cursor()
        if params:
            self.cursor.execute(select, params)
        else:
            self.cursor.execute(select)
        rows = self.cursor.fetchall()
        self.cursor.close()

        return rows

    def select_one(self, select, params=None):

        self.conn = self.connect(self.path)
        self.cursor = self.conn.cursor()
        if params:
            self.cursor.execute(select, params)
        else:
            self.cursor.execute(select)
        row = self.cursor.fetchone()
        self.cursor.close()

        return row


    def ins_upd(self, ins_upd, params=None):

        lastid_row = 0
        # Insert or update record into base
        self.conn = self.connect(self.path)
        self.cursor = self.conn.cursor()
        if params:
            self.cursor.execute(ins_upd, params)
        else:
            self.cursor.execute(ins_upd)
        lastid_row = self.cursor.lastrowid
        self.conn.commit()

        self.cursor.close()

        return lastid_row

    def delete(self, delete, params=None):

        self.conn = self.connect(self.path)
        self.cursor = self.conn.cursor()
        if params:
            self.cursor.execute(delete, params)
        else:
            self.cursor.execute(delete)

        self.conn.commit()

    def check_updates(self, current_version):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS version (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, version int DEFAULT(0))""")
        self.connection.commit()
        self.cursor.execute("""SELECT id, version FROM version LIMIT 1""")
        version = 0
        id = 0
        row = self.cursor.fetchone()
        if not row:
            self.cursor.execute("""INSERT INTO version (version) VALUES(%d)""" % version)
            id = self.cursor.lastrowid
            self.connection.commit()
        else:
            id = row[0]
            version = row[1]

        if current_version > version:
            print("Требуется обновление версии с %d до %d" % (version, current_version))

            # 0 --> 1 - добавлен флаг активности участника
            if version == 0:
                self.cursor.execute("""ALTER TABLE meetmembers ADD COLUMN is_active int DEFAULT(1)""")
                self.cursor.execute("""UPDATE version SET version=%d WHERE id=%d""" % (1, id))
                self.connection.commit()
                version = 1
            # 1 --> 2 - добавлена таблица fightings (неиспользуется)
            if version == 1:
                self.cursor.execute("""CREATE TABLE fightings 
                    (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                    meeting INTEGER (9) REFERENCES meeting (id),
                    fractional_round INTEGER (9) NOT NULL,
                    membera INTEGER (9) REFERENCES members (id) NOT NULL, 
                    memberb INTEGER (9) REFERENCES members (id), 
                    ring INTEGER (2) REFERENCES ring (id),
                    winner INTEGER (9) REFERENCES members (id))""")
                self.cursor.execute("""UPDATE version SET version=%d WHERE id=%d""" % (2, id))
                self.connection.commit()
                version = 2
            # 2 --> 3 - добавлен номер раунда при жеребьевке (принудительное удаление старых данных)
            if version == 2:
                self.cursor.execute("""DROP TABLE fightings""")
                self.cursor.execute("""DROP TABLE sortition""")
                self.connection.commit()
                self.cursor.execute("""CREATE TABLE sortition 
                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                        idmeet INTEGER (9) REFERENCES meeting (id), 
                        membera INTEGER (9) REFERENCES members (id), 
                        wina BOOLEAN DEFAULT False, 
                        memberb INTEGER (9) REFERENCES members (id) DEFAULT (0), 
                        winb BOOLEAN DEFAULT False, 
                        ring INTEGER (2) REFERENCES ring (id),
                        fractional_round INTEGER (9) NOT NULL)""")
                self.cursor.execute("""CREATE TABLE fightings 
                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                        meeting INTEGER (9) REFERENCES meeting (id),
                        fractional_round INTEGER (9) NOT NULL,
                        membera INTEGER (9) REFERENCES members (id) NOT NULL, 
                        memberb INTEGER (9) REFERENCES members (id), 
                        ring INTEGER (2) REFERENCES ring (id),
                        winner INTEGER (9) REFERENCES members (id))""")
                self.connection.commit()
                self.cursor.execute("""UPDATE version SET version=%d WHERE id=%d""" % (3, id))
                self.connection.commit()
                version = 3
            # 3 --> 4 - добавлено поле весовой категории в таблицу сортировок и таблицу боёв (принудительное удаление старых данных)
            if version == 3:
                self.cursor.execute("""DROP TABLE fightings""")
                self.cursor.execute("""DROP TABLE sortition""")
                self.connection.commit()
                self.cursor.execute("""CREATE TABLE sortition 
                                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                                        idmeet INTEGER (9) REFERENCES meeting (id), 
                                        membera INTEGER (9) REFERENCES members (id), 
                                        wina BOOLEAN DEFAULT False, 
                                        memberb INTEGER (9) REFERENCES members (id) DEFAULT (0), 
                                        winb BOOLEAN DEFAULT False, 
                                        ring INTEGER (2) REFERENCES ring (id),
                                        fractional_round INTEGER (9) NOT NULL,
                                        weightcategory_id INTEGER (9) REFERENCES weightcategory (id))""")
                self.cursor.execute("""CREATE TABLE fightings 
                                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                                        meeting INTEGER (9) REFERENCES meeting (id),
                                        fractional_round INTEGER (9) NOT NULL,
                                        membera INTEGER (9) REFERENCES members (id) NOT NULL, 
                                        memberb INTEGER (9) REFERENCES members (id), 
                                        ring INTEGER (2) REFERENCES ring (id),
                                        winner INTEGER (9) REFERENCES members (id),
                                        weightcategory_id INTEGER (9) REFERENCES weightcategory (id))""")
                self.connection.commit()
                self.cursor.execute("""UPDATE version SET version=%d WHERE id=%d""" % (4, id))
                self.connection.commit()
                version = 4
            # 4 --> 5 добавлено поле с проигравшим fightings.loser(принудительное удаление старых данных)
            if version == 4:
                self.cursor.execute("""DROP TABLE fightings""")
                self.connection.commit()
                self.cursor.execute("""CREATE TABLE fightings 
                                                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                                                        meeting INTEGER (9) REFERENCES meeting (id),
                                                        fractional_round INTEGER (9) NOT NULL,
                                                        membera INTEGER (9) REFERENCES members (id) NOT NULL, 
                                                        memberb INTEGER (9) REFERENCES members (id), 
                                                        ring INTEGER (2) REFERENCES ring (id),
                                                        winner INTEGER (9) REFERENCES members (id),
                                                        loser INTEGER (9) REFERENCES members (id),
                                                        weightcategory_id INTEGER (9) REFERENCES weightcategory (id))""")
                self.connection.commit()
                self.cursor.execute("""UPDATE version SET version=%d WHERE id=%d""" % (5, id))
                self.connection.commit()
                version = 5
            # 5 --> 6 добавлено поле с проигравшим fightings.order_num(принудительное удаление старых данных)
            if version == 5:
                self.cursor.execute("""DROP TABLE fightings""")
                self.connection.commit()
                self.cursor.execute("""CREATE TABLE fightings 
                                                        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT UNIQUE, 
                                                        meeting INTEGER (9) REFERENCES meeting (id),
                                                        fractional_round INTEGER (9) NOT NULL,
                                                        membera INTEGER (9) REFERENCES members (id) NOT NULL, 
                                                        memberb INTEGER (9) REFERENCES members (id), 
                                                        ring INTEGER (2) REFERENCES ring (id),
                                                        winner INTEGER (9) REFERENCES members (id),
                                                        loser INTEGER (9) REFERENCES members (id),
                                                        weightcategory_id INTEGER (9) REFERENCES weightcategory (id),
                                                        order_num INTEGER (9) NOT NULL)""")
                self.connection.commit()
                self.cursor.execute("""UPDATE version SET version=%d WHERE id=%d""" % (6, id))
                self.connection.commit()
                version = 6

            print("Обновление успешно завершено")


