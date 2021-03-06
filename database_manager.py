from database import Dbase as db
from models import *


# класс работы с БД (CRUD-операции)
class DbManager():

    def __init__(self):
        self.database = db()

    def get_all_members(self):
        members = []
        rows = self.database.select("SELECT * FROM members")
        for row in rows:
            members.append(Member(row))
        return members

    def get_all_members_dict(self):
        members_dict = {}
        members = self.get_all_members()
        for member in members:
            members_dict[member.id] = member
        return members_dict

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
        sql = """SELECT m.*, mm.is_active
                 FROM members m INNER JOIN meetmembers mm
                 ON m.id = mm.members
                 WHERE mm.meeting=?"""
        params = (meeting_id,)
        rows = self.database.select(sql, params)
        for row in rows:
            member = Member(row)
            #member.is_active = row[-1]
            members.append(member)
        return members

    def update_meeting(self, meeting):
        sql = """UPDATE meeting
                 SET name=?, sdate=?, edate=?, city=?, meetcount=?, mainreferee=?, mainclerk=? 
                 WHERE id=?"""
        params = (meeting.name.replace('\\', ''), meeting.start_date, meeting.end_date, meeting.city.replace('\\',''),
                  meeting.meetcount, meeting.main_referee_id, meeting.main_clerk_id, meeting.id)

        self.database.ins_upd(sql, params)

    def insert_meeting(self, meeting):
        sql = """INSERT INTO meeting(name, sdate, edate, city, meetcount, mainreferee, mainclerk)
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
        params = (meeting.name, meeting.start_date, meeting.end_date, meeting.city, meeting.meetcount,
                  meeting.main_referee_id, meeting.main_clerk_id)
        self.database.ins_upd(sql, params)

    def delete_meet_referee(self, meeting_id):
        sql = "DELETE FROM meetreferees WHERE meeting=?"
        params = (meeting_id,)
        self.database.delete(sql, params)

    def insert_meet_referee(self, meet_referee):
        sql = """INSERT INTO meetreferees(meeting, referee) VALUES (?, ?)"""
        params = (meet_referee.meeting_id, meet_referee.referee_id)
        self.database.ins_upd(sql, params)

    def delete_meet_members(self, meeting_id):
        sql = "DELETE FROM meetmembers WHERE meeting=?"
        params = (meeting_id,)
        self.database.delete(sql, params)

    def delete_meet_member(self, meeting_id, member_id):
        sql = "DELETE FROM meetmembers WHERE meeting=? AND members=?"
        params = (meeting_id, member_id)
        self.database.delete(sql, params)

    def delete_fightings_by_meeting(self, meeting_id):
        sql = "DELETE FROM fightings WHERE meeting=?"
        params = (meeting_id,)
        self.database.delete(sql, params)

    def get_meeting(self, id):
        row = self.database.select_one('SELECT * FROM meeting WHERE id=?', (id,))
        return Meeting(row) if row else None

    def get_fighting(self, id):
        row = self.database.select_one('SELECT * FROM fightings WHERE id=?', (id,))
        return Fighting(row) if row else None

    def insert_meeting(self, meeting):
        sql = """INSERT INTO meeting(name, sdate, edate, city, meetcount, mainreferee, mainclerk) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
        params = (meeting.name.replace('\\', ''), meeting.start_date, meeting.end_date, meeting.city.replace('\\',''),
                  meeting.meetcount, meeting.main_referee_id, meeting.main_clerk_id)
        id = self.database.ins_upd(sql, params)
        return self.get_meeting(id)

    def insert_meet_member(self, meet_member):
        sql = """INSERT INTO meetmembers(meeting, members) VALUES (?, ?)"""
        params = (meet_member.meeting_id, meet_member.member_id)
        self.database.ins_upd(sql, params)

    def insert_fighting(self, fighting):
        sql = """INSERT INTO fightings(meeting, membera, memberb, ring, fractional_round, weightcategory_id, winner, 
                 loser, order_num) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        params = (fighting.meeting_id, fighting.member_a_id, fighting.member_b_id, fighting.ring,
                  fighting.fractional_round, fighting.weightcategory_id, fighting.winner_id, fighting.loser_id,
                  fighting.order_num)
        self.database.ins_upd(sql, params)

    def set_fighting_result(self, fighting_id, winner_id, loser_id):
        sql = """UPDATE fightings
                         SET winner=?, loser=? 
                         WHERE id=?"""
        params = (winner_id, loser_id, fighting_id)
        self.database.ins_upd(sql, params)
        return self.get_fighting(fighting_id)

    def get_version(self):
        row = self.database.select_one('SELECT * FROM version LIMIT 1')
        return Version(row) if row else None

    def get_all_rings(self):
        rings = []
        rows = self.database.select("SELECT * FROM ring")
        for row in rows:
            rings.append(Ring(row))
        return rings

    def get_fightings_by_meeting(self, meeting_id):
        fightings = []
        sql = 'SELECT * FROM fightings WHERE meeting=?'
        params = (meeting_id, )
        rows = self.database.select(sql, params)
        for row in rows:
            fightings.append(Fighting(row))
        return fightings

    def get_count_fightings_by_meeting(self, meeting_id):
        sql = 'SELECT count(*) FROM fightings WHERE meeting=?'
        params = (meeting_id, )
        row = self.database.select_one(sql, params)
        return row[0] if row else 0

    def get_referee_category(self, id):
        row = self.database.select_one('SELECT * FROM refereecat WHERE id=?', (id,))
        return RefereeCategory(row) if row else None

    def get_region(self, id):
        row = self.database.select_one('SELECT * FROM region WHERE id=?', (id,))
        return Region(row) if row else None

    def get_member_category(self, id):
        row = self.database.select_one('SELECT * FROM category WHERE id=?', (id,))
        return MemberCategory(row) if row else None

    def get_all_member_categories(self):
        categories = []
        rows = self.database.select("SELECT * FROM category")
        for row in rows:
            categories.append(MemberCategory(row))
        return categories

    def get_all_member_categories_dict(self):
        categories_dict = {}
        categories = self.get_all_member_categories()
        for category in categories:
            categories_dict[category.id] = category
        return categories_dict