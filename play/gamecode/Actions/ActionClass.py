class Action:
    def __init__(self):
        self.action_chosen = ""
        self.player_with_action = ""
        self.position_of_actioned_card = (-1, -1)
        self.chosen_first_card = False
        self.chosen_second_card = False
        self.misc_target_planet = -1
        self.misc_target_unit = (-1, -1)
        self.misc_counter = 0
        self.misc_counter_2 = 0
        self.misc_target_unit_2 = (-1, -1)
        self.misc_target_attachment = (-1, -1, -1)
        self.misc_player_storage = ""
        self.misc_target_player = ""
        self.misc_misc = None
        self.misc_misc_2 = None
        self.misc_list = []

    def reset_action_data(self):
        self.action_chosen = ""
        self.player_with_action = ""
        self.position_of_actioned_card = (-1, -1)
        self.chosen_first_card = False
        self.chosen_second_card = False
        self.misc_target_planet = -1
        self.misc_target_unit = (-1, -1)
        self.misc_counter = 0
        self.misc_counter_2 = 0
        self.misc_target_unit_2 = (-1, -1)
        self.misc_target_attachment = (-1, -1, -1)
        self.misc_player_storage = ""
        self.misc_target_player = ""
        self.misc_misc = None
        self.misc_misc_2 = None
        self.misc_list = []
