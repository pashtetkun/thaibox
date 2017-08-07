
from database_manager import DbManager as dbmanager
from models import FightingsInWeigth, MemberStatus


#сервис работы с боями
class FightingsService():
    def __init__(self, meeting):
        self.meeting = meeting
        self.dbm = dbmanager()
        self.fightings_info = {}
        self.fightings_count = 0
        self.refresh_fightings_info()

    #получение данных о всех боях в соревновании
    def refresh_fightings_info(self):
        self.fightings_info = {}
        fightings = self.dbm.get_fightings_by_meeting(self.meeting.id) if self.meeting else []
        weight_categories = self.dbm.get_all_weight_categories()
        for wcat in weight_categories:
            fightings_by_round = {}
            fightings_by_weight = [f for f in fightings if f.weightcategory_id == wcat.id]
            current_fr_round = 999
            #fightings_by_round[current_fr_round] = []
            for f in fightings_by_weight:
                if f.fractional_round not in fightings_by_round:
                    fightings_by_round[f.fractional_round] = [f]
                else:
                    fightings_by_round[f.fractional_round].append(f)

                if f.fractional_round < current_fr_round:
                    current_fr_round = f.fractional_round

            self.fightings_info[wcat.id] = FightingsInWeigth(wcat, current_fr_round, fightings_by_round)

        self.fightings_count = self.get_fightings_count()

    #возвращает весовые категории в соревновании
    def get_active_weight_categories(self):
        if not self.fightings_count:
            return []

        result = []
        weight_categories = self.dbm.get_all_weight_categories()
        for wcat in weight_categories:
            if self.fightings_info[wcat.id].fightings_by_round:
                result.append(wcat)

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
        has_not_final_round = False#имеется ли не финальный раунд
        message = ""
        current_round = self.get_current_round()
        if not current_round:
            return True, ""

        for wcat_id in self.fightings_info:
            fightings_in_weight = self.fightings_info[wcat_id]
            current_fr_round = fightings_in_weight.current_fr_round
            # еще не было жеребьевки
            if current_fr_round == 999 and fightings_in_weight.fightings_by_round:
                has_not_final_round = True
                continue
            # после финала - не нужна дальнейшая жеребьевка
            if current_fr_round == 1:
                continue

            not_defined_winners = []
            if fightings_in_weight.fightings_by_round:
                not_defined_winners = [f for f in fightings_in_weight.fightings_by_round[current_fr_round] if not f.winner_id]

            if not_defined_winners:
                message = "Жеребьевка недоступна - не указаны все результаты в категории %s , раунд: 1/%d" % (fightings_in_weight.weight_category.name,
                      current_fr_round)
                print(message)
                drawing_allow = False
                break

            if fightings_in_weight.fightings_by_round:
                has_not_final_round = True

        if drawing_allow and not has_not_final_round:
            drawing_allow = False
            message = "Текущая стадия - финал. Жеребьёвка невозможна"
        return drawing_allow, message

    #возвращает порядковый номер текущего раунда
    def get_current_round(self):
        round = 0
        for wcat_id in self.fightings_info:
            fightings_in_weight = self.fightings_info[wcat_id]
            if round < len(fightings_in_weight.fightings_by_round):
                round = len(fightings_in_weight.fightings_by_round)

        return round

    #возвращает число боёв
    def get_fightings_count(self):
        count = 0
        for wcat_id in self.fightings_info:
            for round, fightings in self.fightings_info[wcat_id].fightings_by_round.items():
                count += len(fightings)
        return count

    #вернуть бой участника в текущем раунде
    def get_fighting(self, member):
        f_in_w = self.fightings_info[member.weight_id]
        current_fr_round = f_in_w.current_fr_round
        if current_fr_round == 999:
            return None
        f_by_r = f_in_w.fightings_by_round
        fs = f_by_r[current_fr_round]
        fighting = next((f for f in fs if f.member_a_id == member.id or f.member_b_id == member.id), None)
        return fighting

    #установить результат боя
    def set_fighting_result(self, fighting, winner_id, loser_id):
        #fighting = self.get_fighting(member)
        return self.dbm.set_fighting_result(fighting.id, winner_id, loser_id)

