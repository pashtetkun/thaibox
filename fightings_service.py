
from database_manager import DbManager as dbmanager
from models import FightingsInWeigth, MemberStatus


#сервис работы с боями
class FightingsService():
    def __init__(self, meeting_id):
        self.meeting_id = meeting_id
        self.dbm = dbmanager()
        self.fightings_info = self.get_fightings_info()

    #получение данных о всех боях в соревновании
    def get_fightings_info(self):
        result = {}
        fightings = self.dbm.get_fightings_by_meeting(self.meeting_id)
        weight_categories = self.dbm.get_all_weight_categories()
        for wcat in weight_categories:
            fightings_by_round = {}
            fightings_by_weight = [f for f in fightings if f.weightcategory_id == wcat.id]
            current_fr_round = 999
            for f in fightings_by_weight:
                if f.fractional_round not in fightings_by_round:
                    fightings_by_round[f.fractional_round] = [f]
                else:
                    fightings_by_round[f.fractional_round].append(f)

                if f.fractional_round < current_fr_round:
                    current_fr_round = f.fractional_round

            result[wcat.id] = FightingsInWeigth(wcat, current_fr_round, fightings_by_round)

        return result

    #определяем статус участника
    def get_member_status(self, member):
        status = MemberStatus.MEMBER
        fightings_in_weight = self.fightings_info[member.weight_id]
        current_fr_round = fightings_in_weight.current_fr_round
        fightings_by_round = fightings_in_weight.fightings_by_round
        if current_fr_round in fightings_by_round:
            fs = fightings_by_round[current_fr_round]
            # бой участника в текущем раунде
            fighting = next((f for f in fs if f.member_a_id == member.id or f.member_b_id == member.id), None)
            if fighting:
                if fighting.winner_id == member.id:
                    status = MemberStatus.WINNER
                if fighting.loser_id == member.id:
                    status = MemberStatus.LOSER
            else:
                status = MemberStatus.WITHDRAW

        return status

    #определяет можно ли провести жеребъевку следующего раунда
    def is_drawing_allow(self):
        drawing_allow = True
        for wcat_id in self.fightings_info:
            fightings_in_weight = self.fightings_info[wcat_id]
            current_fr_round = fightings_in_weight.current_fr_round
            # еще не было жеребьевки
            if current_fr_round == 999:
                continue
            # после финала - не нужна дальнейшая жеребьевка
            if current_fr_round == 1:
                continue

            not_defined_winners = [f for f in fightings_in_weight.fightings_by_round[current_fr_round] if
                                   f.winner_id == None]
            if not_defined_winners:
                print("Не указаны все проигравшие в ", fightings_in_weight.weight_category.name,
                      ", раунд: 1/%d" % current_fr_round)
                drawing_allow = False
                break
        return drawing_allow