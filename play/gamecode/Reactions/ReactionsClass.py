class Reaction:
    def __init__(self, reaction_name, player_name_resolving, position_trigger, additional_info):
        self.reaction_name = reaction_name
        self.name_player_resolving_reaction = player_name_resolving
        self.position_unit_triggering_reaction = position_trigger
        self.additional_reaction_info = additional_info

    def get_reaction_name(self):
        return self.reaction_name

    def set_reaction_name(self, new_val):
        self.reaction_name = new_val

    def get_player_resolving_reaction(self):
        return self.name_player_resolving_reaction

    def set_player_resolving_reaction(self, new_val):
        self.name_player_resolving_reaction = new_val

    def get_position_unit(self):
        return self.get_position_unit_triggering()

    def get_position_unit_triggering(self):
        return self.position_unit_triggering_reaction

    def set_position_unit_triggering(self, new_val):
        self.position_unit_triggering_reaction = new_val

    def get_additional_reaction_info(self):
        return self.additional_reaction_info

    def set_additional_reaction_info(self, new_val):
        self.additional_reaction_info = new_val

    def get_number(self):
        return self.position_unit_triggering_reaction[0]

    def get_planet_pos(self):
        return self.position_unit_triggering_reaction[1]

    def get_unit_pos(self):
        return self.position_unit_triggering_reaction[2]

    def check_position_unit(self, position_tuple):
        return self.position_unit_triggering_reaction == position_tuple