
from enum import Enum


class MemberStatus(Enum):
    #статусы в текущем раунде
    MEMBER = 1
    WINNER = 2
    LOSER = 3
    #выбыл ранее
    WITHDRAW = 4


#класс, описывающий бои в указанном весе
class FightingsInWeigth():
    def __init__(self, weight_category, current_fr_round, fightings_by_round):
        self.weight_category = weight_category
        self.current_fr_round = current_fr_round
        self.fightings_by_round = fightings_by_round


class Member():

    def __init__(self, row):
        self.id = row[0]
        self.fio = row[1].replace("\\", "")
        self.birthday = row[2]
        self.sex_id = row[3]
        self.weight_id = row[4]
        self.category = row[5]
        self.club = row[6].replace("\\", "")
        self.region = row[7].replace("\\", "")
        self.city = row[8].replace("\\", "")
        self.trainer = row[9].replace("\\", "")
        self.status = None

    def get_short_name(self):
        parts = self.fio.split(' ')
        result = ''
        for i, part in enumerate(parts):
            if i == 0:
                result += part + ' '
                continue
            result += part[0].capitalize() + "."
        return result


class Referee():
    def __init__(self, row):
        self.id = row[0]
        self.fio = row[1]
        self.position_id = row[2]
        self.region_id = row[3]
        self.category_id = row[4]

    def get_short_name(self):
        parts = self.fio.split(' ')
        result = ''
        for i, part in enumerate(parts):
            if i == 0:
                result += part + ' '
                continue
            result += part[0].capitalize() + "."
        return result


class WeightCategory():
    def __init__(self, row):
        self.id = row[0]
        self.name = row[1]


class Meeting():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.name = row[1]
            self.start_date = row[2]
            self.end_date = row[3]
            self.city = row[4]
            self.meetcount = row[5]
            self.main_referee_id = row[6]
            self.main_clerk_id = row[7]


class MeetMember():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.meeting_id = row[1]
            self.member_id = row[2]
            #self.is_active = row[3]


class MeetReferee():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.meeting_id = row[1]
            self.referee_id = row[2]


class Version():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.version = row[1]


class Fighting():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.meeting_id = row[1]
            self.fractional_round = row[2]
            self.member_a_id = row[3]
            self.member_b_id = row[4]
            self.ring = row[5]
            self.winner_id = row[6]
            self.loser_id = row[7]
            self.weightcategory_id = row[8]
            self.order_num = row[9]


class Ring():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.name = row[1]


class RefereeCategory():
    def __init__(self, row):
        if row:
            self.id = row[0]
            self.name = row[1]


class Region():
    def __init__(self, row):
        if row:
            self.id = row[0]
            self.name = row[1]


class MemberCategory():
    def __init__(self, row):
        if row:
            self.id = row[0]
            self.name = row[1]