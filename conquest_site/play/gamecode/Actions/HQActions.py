async def update_game_event_action_hq(self, name, game_update_string):
    if not self.action_chosen:
        self.position_of_actioned_card = (-2, int(game_update_string[2]))
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if int(game_update_string[1]) == int(primary_player.get_number()):
            card = primary_player.headquarters[self.position_of_actioned_card[1]]
            ability = card.get_ability()
            if card.get_has_action_while_in_play():
                if card.get_allowed_phases_while_in_play() == self.phase or \
                        card.get_allowed_phases_while_in_play() == "ALL":
                    print("trying to resolve combat special")
                    if card.get_ability() == "Catachan Outpost":
                        if card.get_ready():
                            self.action_chosen = "Catachan Outpost"
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    elif ability == "Ork Kannon":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    elif ability == "Ambush Platform":
                        if card.get_ready():
                            self.action_chosen = "Ambush Platform"
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    elif ability == "Kraktoof Hall":
                        if card.get_ready():
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.chosen_second_card = False
                            self.misc_target_planet = -1
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    elif ability == "Craftworld Gate":
                        if card.get_ready():
                            self.action_chosen = "Craftworld Gate"
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    if ability == "Khymera Den":
                        if card.get_ready():
                            self.action_chosen = "Khymera Den"
                            self.khymera_to_move_positions = []
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    elif ability == "Ravenous Flesh Hounds":
                        self.action_chosen = "Ravenous Flesh Hounds"
                        primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                        await primary_player.send_hq()
                    elif card.get_ability() == "Tellyporta Pad":
                        if card.get_ready():
                            if self.planets_in_play_array[self.round_number]:
                                self.action_chosen = "Tellyporta Pad"
                                primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                                primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                                await primary_player.send_hq()
                            else:
                                await self.game_sockets[0].receive_game_update("First planet not in play")
                    elif ability == "Craftworld Gate":
                        if card.get_ready():
                            self.action_chosen = "Craftworld Gate"
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    elif ability == "Khymera Den":
                        if card.get_ready():
                            self.action_chosen = "Khymera Den"
                            self.khymera_to_move_positions = []
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            await primary_player.send_hq()
                    elif ability == "Ravenous Flesh Hounds":
                        self.action_chosen = "Ravenous Flesh Hounds"
                        primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                        await primary_player.send_hq()
    elif self.action_chosen == "Pact of the Haemonculi":
        if game_update_string[1] == self.number_with_deploy_turn:
            if self.number_with_deploy_turn == "1":
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
            if primary_player.sacrifice_card_in_hq(int(game_update_string[2])):
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
                await primary_player.send_hq()
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
        unit_pos = int(game_update_string[2])
        if player_being_hit.headquarters[unit_pos].get_limited():
            player_being_hit.destroy_card_in_hq(unit_pos)
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
            await player_being_hit.send_hq()
    elif self.action_chosen == "Command-Link Drone":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_is_unit():
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
    elif self.action_chosen == "Craftworld Gate":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_is_unit():
                primary_player.return_card_to_hand(planet_pos, unit_pos)
                self.action_chosen = ""
                self.mode = "Normal"
                self.player_with_action = ""
                if self.phase == "DEPLOY":
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.get_number()
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                await primary_player.send_hq()
                await primary_player.send_hand()
                await self.send_info_box()
                self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Khymera Den":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_name() == "Khymera":
                self.khymera_to_move_positions.append((planet_pos, unit_pos))
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                await primary_player.send_hq()
    elif self.action_chosen == "Ravenous Flesh Hounds":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.get_number() == game_update_string[1]:
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].check_for_a_trait("Cultist"):
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                primary_player.remove_damage_from_pos(self.position_of_actioned_card[0],
                                                      self.position_of_actioned_card[1], 999)
                primary_player.sacrifice_card_in_hq(unit_pos)
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                if self.phase == "DEPLOY":
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.get_number()
                await primary_player.send_hq()
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
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if primary_player.headquarters[unit_pos].get_attachments():
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.unit_to_move_position = [planet_pos, unit_pos]
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        await primary_player.send_hq()
        else:
            await self.game_sockets[0].receive_game_update("Already selected unit to move")
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
        unit_pos = int(game_update_string[2])
        card = player_returning.headquarters[unit_pos]
        if card.get_card_type() == "Army":
            if not card.check_for_a_trait("Elite"):
                player_returning.return_card_to_hand(-2, unit_pos)
                primary_player.aiming_reticle_color = None
                primary_player.aiming_reticle_coords_hand = None
                self.card_pos_to_deploy = -1
                self.player_with_action = ""
                self.action_chosen = ""
                self.player_with_deploy_turn = secondary_player.name_player
                self.number_with_deploy_turn = secondary_player.number
                self.mode = self.stored_mode
                await player_returning.send_hand()
                await player_returning.send_hq()
    elif self.action_chosen == "Catachan Outpost":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if int(game_update_string[1] == "1"):
            player_receiving_buff = self.p1
        else:
            player_receiving_buff = self.p2
        if player_receiving_buff.check_is_unit_at_pos(-2, int(game_update_string[2])):
            player_receiving_buff.increase_attack_of_unit_at_pos(-2, int(game_update_string[2]), 2,
                                                                 expiration="NEXT")
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            self.position_of_actioned_card = (-1, -1)
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            await primary_player.send_hq()
            await self.send_info_box()
    elif self.action_chosen == "Squig Bombin'":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if int(game_update_string[1] == "1"):
            player_destroying_support = self.p1
        else:
            player_destroying_support = self.p2
        unit_pos = int(game_update_string[2])
        if player_destroying_support.headquarters[unit_pos].get_card_type() == "Support":
            player_destroying_support.destroy_card_in_hq(unit_pos)
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            self.player_with_action = ""
            self.action_chosen = ""
            self.mode = "Normal"
            primary_player.aiming_reticle_coords_hand = None
            if self.phase == "DEPLOY":
                if not secondary_player.has_passed:
                    self.player_with_deploy_turn = secondary_player.get_name_player()
                    self.number_with_deploy_turn = secondary_player.get_number()
            await primary_player.send_hand()
            await primary_player.send_discard()
            await player_destroying_support.send_hq()
            await player_destroying_support.send_discard()
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
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            card = FindCard.find_card(primary_player.cards[hand_pos], self.card_array)
            army_unit_as_attachment = False
            discounts = primary_player.search_hq_for_discounts("", "", is_attachment=True)
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
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
                await primary_player.send_hand()
                if enemy_card:
                    await player_receiving_attachment.send_hq()
                await primary_player.send_hq()
                await primary_player.send_resources()
    elif self.action_chosen == "Tellyporta Pad":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if game_update_string[1] == primary_player.get_number():
            card = primary_player.headquarters[int(game_update_string[2])]
            if card.get_faction() == "Orks":
                if card.get_is_unit():
                    primary_player.move_unit_to_planet(-2, int(game_update_string[2]),
                                                       self.round_number)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.position_of_actioned_card = (-1, -1)
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
                    await primary_player.send_hq()
                    await primary_player.send_units_at_planet(self.round_number)
