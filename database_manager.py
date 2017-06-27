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
                 WHERE mr.meeting=?"""
        params = (meet_id,)
        rows = self.database.select(sql, params)
        for row in rows:
            referees.append(Referee(row))
        return referees

    def get_referee(self, id):
        row = self.database.select_one('SELECT * FROM referee WHERE id=?', (id,))
        return Referee(row) if row else None

    def get_meet_members(self, meeting_id):
        members = []
        sql = """SELECT m.*
                 FROM members m INNER JOIN meetmembers mm
                 ON m.id = mm.members
                 WHERE mm.meeting=?"""
        params = (meeting_id,)
        rows = self.database.select(sql, params)
        for row in rows:
            members.append(Member(row))
        return members

    def update_meeting(self, meeting):
        sql = """UPDATE meeting
                 SET name=?, sdate=?, edate=?, city=?, meetcount=?, mainreferee=?, mainclerk=? 
                 WHERE id=?"""
        params = (meeting.name.replace('\\', ''), meeting.start_date, meeting.end_date, meeting.city.replace('\\',''),
                  meeting.meetcount, meeting.main_referee_id, meeting.main_clerk_id, meeting.id)

        self.database.ins_upd(sql, params)

    def delete_meet_referees(self, meeting_id):
        sql = "DELETE FROM meetreferees WHERE meeting=?"
        params = (meeting_id,)
        self.database.delete(sql, params)

    def insert_meet_referee(self, meet_referee):
        sql = """INSERT INTO meetreferees(meeting, referee) VALUES (?, ?)"""
        params = (meet_referee.meeting_id, meet_referee.referee_id)
        self.database.ins_upd(sql, params)