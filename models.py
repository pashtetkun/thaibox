

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


class MeetMember():
    def __init__(self, row):
        self.id = row[0]
        self.meeting_id = row[1]
        self.member_id = row[2]


class MeetReferee():
    def __init__(self, row):
        self.id = row[0]
        self.meeting_id = row[1]
        self.referee_id = row[2]