from database import Dbase as db
from models import *


class DbManager():

    def __init__(self):
        self.database = db()

    def get_all_members(self):
        members = []
        rows = self.database.select("SELECT * FROM members")
        for row in rows:
            members.append(Member(row))
        return members

    def get_all_referees(self):
        referees =[]
        rows = self.database.select("SELECT * FROM referee")
        for row in rows:
            referees.append(Referee(row))
        return referees

    def get_all_weight_categories(self):
        weight_categories = []
        rows = self.database.select("SELECT * FROM weightcategory")
        for row in rows:
            weight_categories.append(WeightCategory(row))
        return weight_categories

    def get_meet_refs(self, meet_id):
        meet_refs = []
        rows = self.database.select('SELECT * FROM meetreferees WHERE meeting=\'' + str(meet_id) + '\'')
        for row in rows:
            meet_refs.append(MeetReferee(row))
        return meet_refs

    '''
    def get_meet_referees2(self, meet_id):
        referees = []
        rows = self.database.select('SELECT r.* FROM meetreferees mr INNER JOIN referee r ON mr.members = r.id WHERE mr.meeting=\'' + str(meet_id) + '\'')
        for row in rows:
            referees.append(Referee(row))
        return referees
    '''

    def get_referee(self, id):
        row = self.database.select_one('SELECT * FROM referee WHERE id=\'' + str(id) + '\'')
        return Referee(row) if row else None

    def get_meet_members(self, meeting):
        return self.database.select('SELECT * FROM meetmembers WHERE meeting=\'' + str(meeting) + '\'')