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
        rows = self.database.select("SELECT * FROM weightcategory WHERE wcategory != '' ORDER BY wcategory")
        for row in rows:
            weight_categories.append(WeightCategory(row))
        return weight_categories

    def get_meet_referees(self, meet_id):
        referees = []
        sql = """SELECT r.*
                 FROM referee r INNER JOIN meetreferees mr 
                 ON r.id = mr.referee 
                 WHERE mr.meeting=%d""" % meet_id
        rows = self.database.select(sql)
        for row in rows:
            referees.append(Referee(row))
        return referees

    def get_referee(self, id):
        row = self.database.select_one('SELECT * FROM referee WHERE id=%d' % id)
        return Referee(row) if row else None

    def get_meet_members(self, meeting_id):
        members = []
        sql = """SELECT m.*
                 FROM members m INNER JOIN meetmembers mm
                         ON m.id = mm.members
                         WHERE mm.meeting=%d""" % meeting_id
        rows = self.database.select(sql)
        for row in rows:
            members.append(Member(row))
        return members

    def insert_or_update_meeting(self, meeting):
        #sql = """UPDATE meeting
        #         SET name=%s, sdate=%s, edate=%s, city=%s, meetcount=%s, mainreferee=%d, mainclerk=%d
        #         WHERE id=%d""" % (meeting.name, meeting.start_date, meeting.end_date, meeting.city, meeting.meetcount,
        #                           meeting.main_referee_id, meeting.main_clerk_id, meeting.id)
        sql = "UPDATE meeting SET name=?, sdate=?, edate=?, city=?, meetcount=?, mainreferee=?, mainclerk=? WHERE id=?", (meeting.name, meeting.start_date, meeting.end_date, meeting.city, meeting.meetcount, meeting.main_referee_id, meeting.main_clerk_id, meeting.id)
        self.database.ins_upd(sql)