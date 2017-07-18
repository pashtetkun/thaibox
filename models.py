

class Member():

    def __init__(self, row):
        self.id = row[0]
        self.fio = row[1]
        self.birthday = row[2]
        self.sex_id = row[3]
        self.weight_id = row[4]
        self.category = row[5]
        self.club = row[6]
        self.region = row[7]
        self.city = row[8]
        self.trainer = row[9]
        self.is_active = True


class Referee():
    def __init__(self, row):
        self.id = row[0]
        self.fio = row[1]
        self.position_id = row[2]
        self.region_id = row[3]
        self.category_id = row[4]


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
            self.is_active = row[3]


class MeetReferee():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.meeting_id = row[1]
            self.referee_id = row[2]


class Sortition():
    def __init__(self, row=[]):
        if row:
            self.id = row[0]
            self.meeting_id = row[1]
            self.member_a_id = row[2]
            self.wina = row[3]
            self.member_b_id = row[4]
            self.winb = row[5]
            self.ring = row[6]
            self.fractional_round = row[7]
            self.weightcategory_id = row[8]


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
            self.weightcategory_id = row[7]