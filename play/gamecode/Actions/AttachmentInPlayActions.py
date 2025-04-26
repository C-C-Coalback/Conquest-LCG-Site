async def update_game_event_action_attachment_in_play(self, name, game_update_string):
    if name == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    planet_pos = int(game_update_string[3])
    unit_pos = int(game_update_string[4])
    attachment_pos = int(game_update_string[5])
    if game_update_string[2] == "1":
        card_chosen = self.p1.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
        player_owning_card = self.p1
        other_player = self.p2
    else:
        card_chosen = self.p2.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
        player_owning_card = self.p2
        other_player = self.p1
    if not self.action_chosen:
        print("action not chosen")
        if card_chosen.get_has_action_while_in_play():
            if card_chosen.get_allowed_phases_while_in_play() == self.phase or \
                    card_chosen.get_allowed_phases_while_in_play() == "ALL":
                ability = card_chosen.get_ability()
                print("ability:", ability)
                if ability == "Command-Link Drone":
                    if primary_player.get_name_player() == self.player_with_action:
                        if primary_player.spend_resources(1):
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                            await self.game_sockets[0].receive_game_update(ability + " activated")
                            await player_owning_card.send_units_at_planet(planet_pos)
                            await primary_player.send_resources()
                elif ability == "Regeneration":
                    if card_chosen.get_ready():
                        if primary_player.get_name_player() == self.player_with_action:
                            player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 2)
                            card_chosen.exhaust_card()
                            if self.phase == "DEPLOY":
                                self.player_with_deploy_turn = other_player.name_player
                                self.number_with_deploy_turn = other_player.number
                            self.action_chosen = ""
                            self.mode = "Normal"
                            self.player_with_action = ""
                            await player_owning_card.send_units_at_planet(planet_pos)
                elif ability == "Heavy Venom Cannon":
                    if not card_chosen.get_once_per_phase_used():
                        if primary_player.get_name_player() == self.player_with_action:
                            self.choice_context = "Heavy Venom Cannon"
                            self.choices_available = ["Armorbane", "Area Effect (2)"]
                            self.name_player_making_choices = primary_player.get_name_player()
                            self.misc_target_attachment = (planet_pos, unit_pos, attachment_pos)
                            await self.send_search()
    elif self.action_chosen == "Even the Odds":
        if not self.chosen_first_card:
            self.misc_player_storage = player_owning_card.get_number()
            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
            await self.game_sockets[0].receive_game_update(card_chosen.get_name() + " chosen")
            self.misc_target_attachment = (planet_pos, unit_pos, attachment_pos)
            self.chosen_first_card = True
            await player_owning_card.send_units_at_planet(planet_pos)
    elif self.action_chosen == "Calculated Strike":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_limited():
            player_being_hit.destroy_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            if self.phase == "DEPLOY":
                if not secondary_player.has_passed:
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.get_number()
            await self.send_info_box()
            await primary_player.send_hand()
            await primary_player.send_discard()
            await player_being_hit.send_discard()
            await player_being_hit.send_units_at_planet(planet_pos)
