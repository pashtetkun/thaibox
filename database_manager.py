from database import Dbase as db


class DbManager():

    def __init__(self):
        self.database = db()

    def get_all_members(self):
        return self.database.select("SELECT * FROM members")

    def get_all_referees(self):
        return self.database.select("SELECT * FROM referee")

    def get_all_weightcategories(self):
        return self.database.select("SELECT * FROM weightcategory")

    def get_meet_referees(self, meeting):
        return self.database.select('SELECT * FROM meetreferees WHERE meeting=\'' + str(meeting) + '\'')

    def get_referee(self, id):
        return self.database.select('SELECT * FROM referee WHERE id=\'' + str(id) + '\'')

    def get_meet_members(self, meeting):
        return self.database.select('SELECT * FROM meetmembers WHERE meeting=\'' + str(meeting) + '\'')