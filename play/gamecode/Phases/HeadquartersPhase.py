async def update_game_event_headquarters_section(self, name, game_update_string):
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif len(game_update_string) == 1:
        if game_update_string[0] == "action-button":
            if self.get_actions_allowed():
                print("Need to run action code")
                self.stored_mode = self.mode
                self.mode = "ACTION"
                self.player_with_action = name
                print("Special HQ action")
                await self.send_update_message(name + " wants to take an action.")
                if self.player_with_action == self.name_1 and self.p1.dark_possession_active:
                    self.choices_available = ["Dark Possession", "Regular Action"]
                    self.choice_context = "Use Dark Possession?"
                    self.name_player_making_choices = self.player_with_action
                elif self.player_with_action == self.name_2 and self.p2.dark_possession_active:
                    self.choices_available = ["Dark Possession", "Regular Action"]
                    self.choice_context = "Use Dark Possession?"
                    self.name_player_making_choices = self.player_with_action
        elif game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
            if name == self.name_1:
                self.p1.has_passed = True
                await self.send_update_message(self.name_1 + " is ready to move on to the next round.")
            elif name == self.name_2:
                self.p2.has_passed = True
                await self.send_update_message(self.name_2 + " is ready to move on to the next round.")
            if self.p1.has_passed and self.p2.has_passed:
                self.automated_headquarters_phase()
                await self.change_phase("DEPLOY")
                self.reset_values_for_new_round()


def headquarters_phase(p_one, p_two, round_number):
    print("hq:", round_number)
    p_one.ready_all_in_play()
    p_two.ready_all_in_play()
    p_one.add_resources(4)
    p_two.add_resources(4)
    p_one.draw_card()
    p_one.draw_card()
    p_two.draw_card()
    p_two.draw_card()
    p_one.toggle_initiative()
    p_two.toggle_initiative()
    print(p_one.get_resources())
    print(p_two.get_resources())
    p_one.increment_round_number()
    p_two.increment_round_number()
    if round_number < 3:
        p_one.toggle_planet_in_play(round_number + 4)
        p_two.toggle_planet_in_play(round_number + 4)
