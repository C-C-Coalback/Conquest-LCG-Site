async def update_game_event_action_in_play(self, name, game_update_string):
    if name == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    planet_pos = int(game_update_string[2])
    unit_pos = int(game_update_string[3])
    if game_update_string[1] == "1":
        card_chosen = self.p1.cards_in_play[planet_pos + 1][unit_pos]
        player_owning_card = self.p1
    else:
        card_chosen = self.p2.cards_in_play[planet_pos + 1][unit_pos]
        player_owning_card = self.p2
    if not self.action_chosen:
        print("action not chosen")
        if card_chosen.get_has_action_while_in_play():
            if card_chosen.get_allowed_phases_while_in_play() == self.phase or \
                    card_chosen.get_allowed_phases_while_in_play() == "ALL":
                print("reached new in play unit action")
                ability = card_chosen.get_ability()
                if ability == "Haemonculus Tormentor":
                    if player_owning_card.name_player == name:
                        if player_owning_card.spend_resources(1):
                            player_owning_card.increase_attack_of_unit_at_pos(planet_pos, unit_pos,
                                                                              2, expiration="EOP")
                            self.player_with_action = ""
                            self.action_chosen = ""
                            self.mode = "Normal"
                            if self.phase == "DEPLOY":
                                self.player_with_deploy_turn = secondary_player.name_player
                                self.number_with_deploy_turn = secondary_player.get_number()
                            await player_owning_card.send_resources()
                            await self.game_sockets[0].receive_game_update("Haemonculus buffed")
                            await self.send_info_box()
                elif ability == "Captain Markis":
                    if not card_chosen.get_once_per_phase_used():
                        card_chosen.set_once_per_phase_used(True)
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        self.chosen_second_card = False
                        self.chosen_first_card = False
                        await player_owning_card.send_units_at_planet(planet_pos)
                elif ability == "Wildrider Squadron":
                    if not card_chosen.get_once_per_phase_used():
                        if player_owning_card.name_player == name:
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            await player_owning_card.send_units_at_planet(planet_pos)
                elif ability == "Veteran Brother Maxos":
                    if player_owning_card.name_player == name:
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        await player_owning_card.send_units_at_planet(planet_pos)
                elif ability == "Zarathur's Flamers":
                    if player_owning_card.name_player == name:
                        self.action_chosen = "Zarathur's Flamers"
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        await player_owning_card.send_units_at_planet(planet_pos)
                elif ability == "Ravenous Flesh Hounds":
                    if player_owning_card.name_player == name:
                        self.action_chosen = "Ravenous Flesh Hounds"
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        await player_owning_card.send_units_at_planet(planet_pos)
                elif ability == "Nazdreg's Flash Gitz":
                    if not card_chosen.get_once_per_phase_used():
                        if player_owning_card.name_player == name:
                            if not card_chosen.get_ready():
                                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1)
                                player_owning_card.set_aiming_reticle_in_play(planet_pos,
                                                                              unit_pos, "red")
                                player_owning_card.ready_given_pos(planet_pos, unit_pos)
                                card_chosen.set_once_per_phase_used(True)
                                self.player_with_action = ""
                                self.action_chosen = ""
                                self.mode = "Normal"
                                await player_owning_card.send_units_at_planet(planet_pos)
    elif self.action_chosen == "Twisted Laboratory":
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
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        can_continue = True
        if player_being_hit.name_player == secondary_player.name_player:
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
            elif secondary_player.communications_relay_check(planet_pos, unit_pos) and \
                    self.communications_relay_enabled:
                can_continue = False
                await self.game_sockets[0].receive_game_update("Communications Relay may be used.")
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Use Communications Relay?"
                self.nullified_card_pos = int(game_update_string[2])
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
                await self.send_search()
        if can_continue:
            if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
                player_being_hit.set_blanked_given_pos(planet_pos, unit_pos, exp="EOP")
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                if self.phase == "DEPLOY":
                    if not secondary_player.has_passed:
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.get_number()
                await self.send_info_box()
                await primary_player.send_hq()
    elif self.action_chosen == "Pact of the Haemonculi":
        if game_update_string[1] == self.number_with_deploy_turn:
            if self.number_with_deploy_turn == "1":
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
            if primary_player.sacrifice_card_in_play(int(game_update_string[2]),
                                                     int(game_update_string[3])):
                primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                secondary_player.discard_card_at_random()
                primary_player.draw_card()
                primary_player.draw_card()
                primary_player.aiming_reticle_color = None
                primary_player.aiming_reticle_coords_hand = None
                self.card_pos_to_deploy = -1
                self.player_with_action = ""
                self.action_chosen = ""
                self.player_with_deploy_turn = secondary_player.name_player
                self.number_with_deploy_turn = secondary_player.number
                self.mode = self.stored_mode
                await primary_player.dark_eldar_event_played()
                await primary_player.send_hand()
                await secondary_player.send_hand()
                await secondary_player.send_discard()
                await primary_player.send_discard()
                await primary_player.send_units_at_planet(int(game_update_string[2]))
    elif self.action_chosen == "Even the Odds":
        if self.chosen_first_card:
            if self.misc_player_storage == game_update_string[1]:
                if game_update_string[1] == "1":
                    player_owning_card = self.p1
                else:
                    player_owning_card = self.p2
                origin_planet, origin_pos, origin_attach_pos = self.misc_target_attachment
                dest_planet = int(game_update_string[2])
                dest_pos = int(game_update_string[3])
                can_continue = True
                if player_owning_card.name_player == secondary_player.name_player:
                    if secondary_player.get_immune_to_enemy_card_abilities(dest_planet, dest_pos):
                        can_continue = False
                        await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
                    if secondary_player.get_immune_to_enemy_events(dest_planet, dest_pos):
                        can_continue = False
                        await self.game_sockets[0].receive_game_update("Immune to enemy events.")
                if can_continue:
                    if player_owning_card.move_attachment_card(origin_planet, origin_pos, origin_attach_pos,
                                                               dest_planet, dest_pos):
                        player_owning_card.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                        self.chosen_second_card = True
                        self.action_chosen = ""
                        self.player_with_action = ""
                        self.mode = "Normal"
                        self.chosen_second_card = True
                        self.misc_target_attachment = (-1, -1, -1)
                        self.misc_player_storage = ""
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await player_owning_card.send_units_at_planet(dest_planet)
                        await player_owning_card.send_units_at_planet(origin_planet)
                    else:
                        await self.game_sockets[0].receive_game_update("Invalid attachment movement.")
    elif self.action_chosen == "Tzeentch's Firestorm":
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
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        can_continue = True
        if player_being_hit.name_player == secondary_player.name_player:
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
            if secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy events.")
        if can_continue:
            if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, self.amount_spend_for_tzeentch_firestorm)
                player_being_hit.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.amount_spend_for_tzeentch_firestorm = -1
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                if self.phase == "DEPLOY":
                    if not secondary_player.has_passed:
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.get_number()
                await self.send_info_box()
                await player_being_hit.send_units_at_planet(planet_pos)
                await primary_player.send_hand()
                await primary_player.send_discard()
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
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        can_continue = True
        if player_being_hit.name_player == secondary_player.name_player:
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
            if secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy events.")
        if can_continue:
            if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_limited():
                player_being_hit.destroy_card_in_play(planet_pos, unit_pos)
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
    elif self.action_chosen == "Command-Link Drone":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                planet, position, attachment_position = self.position_of_selected_attachment
                if primary_player.move_attachment_card(planet, position, attachment_position, planet_pos, unit_pos):
                    self.action_chosen = ""
                    self.mode = "Normal"
                    self.player_with_action = ""
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    await primary_player.send_units_at_planet(planet_pos)
                    await primary_player.send_units_at_planet(self.position_of_selected_attachment[0])
                    self.position_of_selected_attachment = (-1, -1, -1)
                    self.position_of_actioned_card = (-1, -1)
                    if self.phase == "DEPLOY":
                        if not secondary_player.has_passed:
                            self.player_with_deploy_turn = secondary_player.name_player
                            self.number_with_deploy_turn = secondary_player.get_number()
                    await self.send_info_box()
    elif self.action_chosen == "Preemptive Barrage":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        if self.misc_target_planet == -1:
            if card_chosen.get_faction() == "Astra Militarum":
                card_chosen.set_ranged(True)
                self.misc_target_planet = planet_pos
                self.misc_counter -= 1
                await self.game_sockets[0].receive_game_update(str(self.misc_counter) + " uses left")
        elif self.misc_target_planet == planet_pos:
            if card_chosen.get_faction() == "Astra Militarum":
                card_chosen.set_ranged(True)
                self.misc_counter -= 1
                await self.game_sockets[0].receive_game_update(str(self.misc_counter) + " uses left")
                if self.misc_counter == 0:
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    await primary_player.send_hand()
                    await primary_player.send_hq()
                    await primary_player.send_discard()
    elif self.action_chosen == "Kraktoof Hall":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        if not self.chosen_first_card:
            if primary_player.get_number() == game_update_string[1]:
                if primary_player.get_damage_given_pos(planet_pos, unit_pos) > 0:
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                    self.position_of_actioned_card = (planet_pos, unit_pos)
                    self.chosen_first_card = True
                    self.misc_target_planet = planet_pos
                    await primary_player.send_units_at_planet(planet_pos)
        elif self.misc_target_planet == planet_pos:
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            can_continue = True
            if player_owning_card.name_player == secondary_player.name_player:
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
            if can_continue:
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False)
                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                self.chosen_second_card = True
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
                await primary_player.send_hq()
                await primary_player.send_units_at_planet(planet_pos)
                await player_owning_card.send_units_at_planet(planet_pos)
    elif self.action_chosen == "Suppressive Fire":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                self.chosen_first_card = True
                self.misc_target_planet = planet_pos
                await primary_player.send_units_at_planet(planet_pos)
        else:
            if planet_pos == self.misc_target_planet:
                can_continue = True
                if player_owning_card.name_player == secondary_player.name_player:
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
                    if secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.game_sockets[0].receive_game_update("Immune to enemy events.")
                if can_continue:
                    if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                        player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                        self.chosen_second_card = True
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        self.action_chosen = ""
                        self.player_with_action = ""
                        self.mode = "Normal"
                        self.misc_target_planet = -1
                        await player_owning_card.send_units_at_planet(planet_pos)
                        await primary_player.send_hand()
                        await primary_player.send_discard()
    elif self.action_chosen == "Captain Markis":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        if planet_pos == self.position_of_actioned_card[0]:
            if not self.chosen_first_card:
                if primary_player.get_number() == game_update_string[1]:
                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_faction() == "Astra Militarum" \
                            and primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                        if self.position_of_actioned_card == (planet_pos, unit_pos):
                            self.position_of_actioned_card = (-1, -1)
                        elif self.position_of_actioned_card[1] > unit_pos:
                            self.position_of_actioned_card = (self.position_of_actioned_card[0],
                                                              self.position_of_actioned_card[1] - 1)
                        self.chosen_first_card = True
                        primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                        await primary_player.send_units_at_planet(planet_pos)
                        await primary_player.send_discard()
            else:
                can_continue = True
                if player_owning_card.name_player == secondary_player.name_player:
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
                if can_continue:
                    if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                        player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                        self.chosen_second_card = True
                        self.action_chosen = ""
                        self.player_with_action = ""
                        self.mode = "Normal"
                        if self.position_of_actioned_card != (-1, -1):
                            primary_player.reset_aiming_reticle_in_play(planet_pos, self.position_of_actioned_card[1])
                        self.position_of_actioned_card = (-1, -1)
                        if self.phase == "DEPLOY":
                            self.player_with_deploy_turn = secondary_player.name_player
                            self.number_with_deploy_turn = secondary_player.get_number()
                        await primary_player.send_units_at_planet(planet_pos)
                        await player_owning_card.send_units_at_planet(planet_pos)

    elif self.action_chosen == "Craftworld Gate":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                primary_player.return_card_to_hand(planet_pos, unit_pos)
                self.action_chosen = ""
                self.mode = "Normal"
                self.player_with_action = ""
                if self.phase == "DEPLOY":
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.number
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                await primary_player.send_hq()
                await primary_player.send_units_at_planet(planet_pos)
                self.position_of_actioned_card = (-1, -1)
                await primary_player.send_hand()
                await self.send_info_box()
    elif self.action_chosen == "Khymera Den":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_name() == "Khymera":
                self.khymera_to_move_positions.append((planet_pos, unit_pos))
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                await primary_player.send_units_at_planet(planet_pos)
    elif self.action_chosen == "Ravenous Flesh Hounds":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait("Cultist"):
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                primary_player.remove_damage_from_pos(self.position_of_actioned_card[0],
                                                      self.position_of_actioned_card[1], 999)
                primary_player.sacrifice_card_in_play(planet_pos, unit_pos)

                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                if self.phase == "DEPLOY":
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.number
                await primary_player.send_units_at_planet(planet_pos)
                await primary_player.send_units_at_planet(self.position_of_actioned_card[0])
                self.position_of_actioned_card = (-1, -1)
                await self.send_info_box()
    elif self.action_chosen == "Squadron Redeployment":
        if self.unit_to_move_position == [-1, -1]:
            if self.player_with_action == self.name_1:
                primary_player = self.p1
            else:
                primary_player = self.p2
            if game_update_string[1] == primary_player.get_number():
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments():
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.unit_to_move_position = [planet_pos, unit_pos]
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        await primary_player.send_units_at_planet(planet_pos)
        else:
            await self.game_sockets[0].receive_game_update("Already selected unit to move")
    elif self.action_chosen == "Archon's Terror":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_being_routed = self.p1
        else:
            player_being_routed = self.p2
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        can_continue = True
        if player_being_routed.name_player == secondary_player.name_player:
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
            elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy events.")
            elif secondary_player.communications_relay_check(planet_pos, unit_pos) and \
                    self.communications_relay_enabled:
                can_continue = False
                await self.game_sockets[0].receive_game_update("Communications Relay may be used.")
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Use Communications Relay?"
                self.nullified_card_pos = int(game_update_string[2])
                self.nullified_card_name = "Archon's Terror"
                self.cost_card_nullified = 2
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
                await self.send_search()
        if can_continue:
            if not player_being_routed.cards_in_play[planet_pos + 1][unit_pos].get_unique():
                player_being_routed.rout_unit(planet_pos, unit_pos)
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                await primary_player.dark_eldar_event_played()
                await primary_player.send_discard()
                await primary_player.send_hand()
                await player_being_routed.send_hq()
                await player_being_routed.send_units_at_planet(planet_pos)
    elif self.action_chosen == "Zarathur's Flamers":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_receiving_damage = self.p1
        else:
            player_receiving_damage = self.p2
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        can_continue = True
        if player_receiving_damage.name_player == secondary_player.name_player:
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
        if can_continue:
            if planet_pos == self.position_of_actioned_card[0]:
                hitting_self = False
                if player_receiving_damage.get_number() == primary_player.get_number():
                    if int(game_update_string[3]) == self.position_of_actioned_card[1]:
                        hitting_self = True
                        await self.game_sockets[0].receive_game_update("Dont hit yourself")
                if not hitting_self:
                    player_receiving_damage.assign_damage_to_pos(planet_pos, unit_pos, 2)
                    player_receiving_damage.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                    primary_player.sacrifice_card_in_play(self.position_of_actioned_card[0],
                                                          self.position_of_actioned_card[1])
                    self.position_of_actioned_card = (-1, -1)
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.get_number()
                    await primary_player.send_units_at_planet(planet_pos)
                    await secondary_player.send_units_at_planet(planet_pos)
                    await self.send_info_box()
    elif self.action_chosen == "Deception":
        if self.number_with_deploy_turn == "1":
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_returning = self.p1
        else:
            player_returning = self.p2
        planet_pos = int(game_update_string[2])
        unit_pos = int(game_update_string[3])
        can_continue = True
        if player_owning_card.name_player == secondary_player.name_player:
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
            if secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy events.")
        if can_continue:
            card = player_returning.cards_in_play[planet_pos + 1][unit_pos]
            if card.get_card_type() == "Army":
                if not card.check_for_a_trait("Elite"):
                    player_returning.return_card_to_hand(planet_pos, unit_pos)
                    primary_player.aiming_reticle_color = None
                    primary_player.aiming_reticle_coords_hand = None
                    primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                    self.card_pos_to_deploy = -1
                    self.player_with_action = ""
                    self.action_chosen = ""
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.number
                    self.mode = self.stored_mode
                    await player_returning.send_hand()
                    await player_returning.send_units_at_planet(planet_pos)
                    await primary_player.send_hand()
                    await primary_player.send_discard()
    elif self.action_chosen == "Ambush Platform":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if game_update_string[1] == "1":
            player_receiving_attachment = self.p1
        else:
            player_receiving_attachment = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is not None:
            hand_pos = primary_player.aiming_reticle_coords_hand_2
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            card = FindCard.find_card(primary_player.cards[hand_pos], self.card_array)
            army_unit_as_attachment = False
            discounts = primary_player.search_hq_for_discounts("", "",
                                                               is_attachment=True)
            if card.get_ability() == "Gun Drones" or \
                    card.get_ability() == "Shadowsun's Stealth Cadre":
                army_unit_as_attachment = True
            if primary_player.get_number() == player_receiving_attachment.get_number():
                print("Playing own card")
                played_card = primary_player. \
                    play_attachment_card_to_in_play(card, planet_pos, unit_pos,
                                                    army_unit_as_attachment=
                                                    army_unit_as_attachment,
                                                    discounts=discounts)
                enemy_card = False
            else:
                played_card = False
                if primary_player.spend_resources(int(card.get_cost()) - discounts):
                    played_card = player_receiving_attachment.play_attachment_card_to_in_play(
                        card, planet_pos, unit_pos, not_own_attachment=True,
                        army_unit_as_attachment=army_unit_as_attachment)
                    if not played_card:
                        primary_player.add_resources(int(card.get_cost()) - discounts)
                enemy_card = True
            if played_card:
                if card.get_limited():
                    primary_player.can_play_limited = False
                primary_player.remove_card_from_hand(hand_pos)
                print("Succeeded (?) in playing attachment")
                primary_player.aiming_reticle_coords_hand_2 = None
                primary_player.reset_aiming_reticle_in_play(
                    self.position_of_actioned_card[0],
                    self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
                await primary_player.send_hand()
                if enemy_card:
                    await player_receiving_attachment.send_units_at_planet(planet_pos)
                else:
                    await primary_player.send_units_at_planet(planet_pos)
                await primary_player.send_hq()
                await primary_player.send_resources()
    elif self.action_chosen == "Catachan Outpost":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if int(game_update_string[1] == "1"):
            player_receiving_buff = self.p1
        else:
            player_receiving_buff = self.p2
        can_continue = True
        if player_owning_card.name_player == secondary_player.name_player:
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
        if can_continue:
            player_receiving_buff.increase_attack_of_unit_at_pos(int(game_update_string[2]),
                                                                 int(game_update_string[3]), 2,
                                                                 expiration="NEXT")
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            self.position_of_actioned_card = (-1, -1)
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            await primary_player.send_hq()
            await self.send_info_box()
    elif self.action_chosen == "Tellyporta Pad":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if game_update_string[1] == primary_player.get_number():
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            card = primary_player.cards_in_play[planet_pos + 1][unit_pos]
            if card.get_faction() == "Orks":
                if card.get_is_unit():
                    primary_player.move_unit_to_planet(planet_pos, unit_pos,
                                                       self.round_number)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.position_of_actioned_card = (-1, -1)
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
                    await primary_player.send_hq()
                    await primary_player.send_units_at_planet(planet_pos)
                    await primary_player.send_units_at_planet(self.round_number)
