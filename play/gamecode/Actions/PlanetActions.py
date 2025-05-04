from .. import FindCard
from ..Phases import DeployPhase


async def update_game_event_action_planet(self, name, game_update_string):
    chosen_planet = int(game_update_string[1])
    if self.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if not self.action_chosen:
        pass
    elif self.action_chosen == "Ambush":
        if self.card_pos_to_deploy != -1 and self.planet_pos_to_deploy == -1:
            self.planet_pos_to_deploy = int(game_update_string[1])
            card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
            self.traits_of_card_to_play = card.get_traits()
            self.faction_of_card_to_play = card.get_faction()
            self.name_of_card_to_play = card.get_name()
            print("Trying to discount: ", card.get_name())
            self.discounts_applied = 0
            hand_dis = primary_player.search_hand_for_discounts(card.get_faction())
            hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits())
            in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits())
            same_planet_dis, same_planet_auto_dis = \
                primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
            num_termagants = 0
            if card.get_name() == "Burrowing Trygon":
                num_termagants = primary_player.get_most_termagants_at_single_planet()
                self.discounts_applied += num_termagants
            self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis + num_termagants
            print("Discounts", hq_dis, in_play_dis, same_planet_dis, hand_dis)
            self.discounts_applied += same_planet_auto_dis
            if self.available_discounts > self.discounts_applied:
                self.stored_mode = self.mode
                self.mode = "DISCOUNT"
                self.planet_aiming_reticle_position = int(game_update_string[1])
                self.planet_aiming_reticle_active = True
            else:
                primary_player.aiming_reticle_coords_hand = None
                await DeployPhase.deploy_card_routine(self, name, game_update_string[1],
                                                      discounts=self.discounts_applied)
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                self.card_pos_to_deploy = -1
                self.planet_pos_to_deploy = -1
    elif self.action_chosen == "Exterminatus":
        if self.round_number != chosen_planet:
            if self.number_with_deploy_turn == "1":
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p2
            primary_player.destroy_all_cards_at_planet(chosen_planet, enemy_event=False)
            secondary_player.destroy_all_cards_at_planet(chosen_planet, enemy_event=True)
            primary_player.discard_card_from_hand(self.card_pos_to_deploy)
            await self.complete_destruction_checks()
            primary_player.aiming_reticle_color = None
            primary_player.aiming_reticle_coords_hand = None
            self.card_pos_to_deploy = -1
            self.player_with_action = ""
            self.action_chosen = ""
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.number
            self.mode = self.stored_mode
    elif self.action_chosen == "Predation":
        adj_1 = chosen_planet - 1
        adj_2 = chosen_planet + 1
        adj_1_infested = False
        adj_2_infested = False
        if -1 < adj_1 < 7:
            if self.infested_planets[adj_1]:
                adj_1_infested = True
        if -1 < adj_2 < 7:
            if self.infested_planets[adj_2]:
                adj_2_infested = True
        if adj_1_infested or adj_2_infested:
            self.infested_planets[chosen_planet] = True
            primary_player.discard_card_from_hand(self.card_pos_to_deploy)
            self.mode = "Normal"
            self.action_chosen = ""
            self.player_with_action = ""
            primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Hunter Gargoyles":
        if self.infested_planets[chosen_planet]:
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            primary_player.move_unit_to_planet(
                self.position_of_actioned_card[0], self.position_of_actioned_card[1], chosen_planet)
            self.mode = "Normal"
            self.action_chosen = ""
            self.player_with_action = ""
            if self.phase == "DEPLOY":
                self.player_with_deploy_turn = secondary_player.name_player
                self.number_with_deploy_turn = secondary_player.number
            self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Infernal Gateway":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is None:
            await self.game_sockets[0].receive_game_update("Choose a valid unit first")
        else:
            pos_hand = primary_player.aiming_reticle_coords_hand_2
            pos_planet = int(game_update_string[1])
            card = FindCard.find_card(primary_player.cards[pos_hand], self.card_array)
            unit_pos = primary_player.add_card_to_planet(card, pos_planet)
            if unit_pos != -1:
                primary_player.cards_in_play[pos_planet + 1][unit_pos].set_sacrifice_end_of_phase(True)
                primary_player.aiming_reticle_coords_hand = None
                primary_player.aiming_reticle_coords_hand_2 = None
                primary_player.discard_card_from_hand(pos_hand)
                if pos_hand < self.card_pos_to_deploy:
                    self.card_pos_to_deploy -= 1
                primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                self.mode = "Normal"
                self.action_chosen = ""
                self.player_with_action = ""
    elif self.action_chosen == "Khymera Den":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p2
        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                    self.position_of_actioned_card[1])
        for i in range(len(self.khymera_to_move_positions)):
            planet_pos, unit_pos = self.khymera_to_move_positions[i]
            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
        for i in range(len(self.khymera_to_move_positions)):
            planet_pos, unit_pos = self.khymera_to_move_positions[i]
            if planet_pos != int(game_update_string[1]):
                primary_player.move_unit_to_planet(planet_pos, unit_pos, int(game_update_string[1]))
                for j in range(len(self.khymera_to_move_positions)):
                    planet_pos_2, unit_pos_2 = self.khymera_to_move_positions[j]
                    if planet_pos == planet_pos_2:
                        if unit_pos_2 > unit_pos:
                            unit_pos_2 -= 1
                            self.khymera_to_move_positions[j] = (planet_pos_2, unit_pos_2)
        if self.phase == "DEPLOY":
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.get_number()
        self.action_chosen = ""
        self.player_with_action = ""
        self.mode = "Normal"
    elif self.action_chosen == "Wildrider Squadron":
        if abs(chosen_planet - self.position_of_actioned_card[0]) == 1:
            origin_planet, origin_pos = self.position_of_actioned_card
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.cards_in_play[origin_planet + 1][origin_pos].set_once_per_phase_used(True)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
            self.action_chosen = ""
            self.mode = "Normal"
            self.player_with_action = ""
            self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Mechanical Enhancement":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.get_faction_given_pos(chosen_planet, i) == "Necrons":
                primary_player.cards_in_play[chosen_planet + 1][i].positive_hp_until_eop += 2
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        self.action_cleanup()
    elif self.action_chosen == "Ravenwing Escort":
        if self.chosen_first_card:
            if self.misc_target_planet != chosen_planet:
                origin_planet, origin_pos = self.misc_target_unit
                primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
                self.misc_target_unit = (-1, -1)
                self.action_cleanup()
    elif self.action_chosen == "Extermination":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.get_faction_given_pos(chosen_planet, i) != "Necrons" and \
                    not primary_player.cards_in_play[chosen_planet + 1][i].get_unique():
                primary_player.cards_in_play[chosen_planet + 1][i].negative_hp_until_eop += 3
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            if secondary_player.get_faction_given_pos(chosen_planet, i) != "Necrons" and \
                    not secondary_player.cards_in_play[chosen_planet + 1][i].get_unique() and \
                    secondary_player.get_ability_given_pos(chosen_planet, i) != "Stalwart Ogryn":
                secondary_player.cards_in_play[chosen_planet + 1][i].negative_hp_until_eop += 3
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        primary_player.has_passed = True
        self.action_cleanup()
    elif self.action_chosen == "Drudgery":
        card = FindCard.find_card(self.misc_target_choice, self.card_array)
        primary_player.add_card_to_planet(card, chosen_planet)
        primary_player.discard.remove(self.misc_target_choice)
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        self.action_cleanup()
    elif self.action_chosen == "Warpstorm":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p2
        first_unit_damaged = True
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.cards_in_play[chosen_planet + 1][i].get_is_unit():
                if not primary_player.cards_in_play[chosen_planet + 1][i].get_attachments():
                    primary_player.assign_damage_to_pos(chosen_planet, i, 2)
                    primary_player.set_aiming_reticle_in_play(chosen_planet, i, "blue")
                    if first_unit_damaged:
                        primary_player.set_aiming_reticle_in_play(chosen_planet, i, "red")
                        first_unit_damaged = False
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            if secondary_player.cards_in_play[chosen_planet + 1][i].get_is_unit():
                if not secondary_player.cards_in_play[chosen_planet + 1][i].get_attachments():
                    if not secondary_player.get_immune_to_enemy_events(chosen_planet, i):
                        secondary_player.assign_damage_to_pos(chosen_planet, i, 2)
                        secondary_player.set_aiming_reticle_in_play(chosen_planet, i, "blue")
                        if first_unit_damaged:
                            secondary_player.set_aiming_reticle_in_play(chosen_planet, i, "red")
                            first_unit_damaged = False
        self.mode = "Normal"
        primary_player.discard_card_from_hand(self.card_pos_to_deploy)
        primary_player.aiming_reticle_color = None
        primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Squadron Redeployment":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        origin_planet = self.unit_to_move_position[0]
        origin_pos = self.unit_to_move_position[1]
        dest_planet = int(game_update_string[1])
        hand_pos = primary_player.aiming_reticle_coords_hand
        primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
        new_pos = len(primary_player.cards_in_play[dest_planet + 1])
        if self.positions_of_units_to_take_damage:
            for i in range(len(self.positions_of_units_to_take_damage)):
                self.positions_of_units_to_take_damage[i] = [int(primary_player.get_number()),
                                                             dest_planet, new_pos]
        primary_player.move_unit_to_planet(origin_planet, origin_pos, dest_planet)
        self.action_chosen = ""
        self.player_with_action = ""
        self.mode = "Normal"
        self.card_pos_to_deploy = -1
        if self.phase == "DEPLOY":
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.number
        primary_player.discard_card_from_hand(hand_pos)
        primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Mycetic Spores":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.search_card_at_planet(chosen_planet, "Termagant", ability_checking=False):
            origin_planet = self.unit_to_move_position[0]
            origin_pos = self.unit_to_move_position[1]
            dest_planet = int(game_update_string[1])
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            new_pos = len(primary_player.cards_in_play[dest_planet + 1])
            if self.positions_of_units_to_take_damage:
                for i in range(len(self.positions_of_units_to_take_damage)):
                    self.positions_of_units_to_take_damage[i] = [int(primary_player.get_number()),
                                                                 dest_planet, new_pos]
            primary_player.move_unit_to_planet(origin_planet, origin_pos, dest_planet)
            self.position_of_actioned_card = (-1, -1)
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            self.card_pos_to_deploy = -1
    elif self.action_chosen == "Anrakyr the Traveller":
        if self.anrakyr_unit_position != -1:
            if self.anrakyr_deck_choice == primary_player.name_player:
                card = FindCard.find_card(primary_player.discard[self.anrakyr_unit_position], self.card_array)
            else:
                card = FindCard.find_card(secondary_player.discard[self.anrakyr_unit_position], self.card_array)
            self.card_to_deploy = card
            await self.calculate_available_discounts_unit(
                planet_chosen=chosen_planet, card=card, player=primary_player
            )
            await self.calculate_automatic_discounts_unit(
                planet_chosen=chosen_planet, card=card, player=primary_player
            )
            self.mode = "DISCOUNT"
            self.planet_aiming_reticle_position = int(game_update_string[1])
            if self.discounts_applied >= self.available_discounts:
                added_card_to_planet = False
                primary_player.play_card(
                    chosen_planet, card=self.card_to_deploy
                )
                if added_card_to_planet:
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.action_cleanup()
                    if self.anrakyr_deck_choice == primary_player.name_player:
                        del primary_player.discard[self.anrakyr_unit_position]
                    else:
                        del secondary_player.discard[self.anrakyr_unit_position]
    elif self.action_chosen == "Ecstatic Seizures":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            primary_player.discard_attachments_from_card(chosen_planet, i)
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            secondary_player.discard_attachments_from_card(chosen_planet, i)
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        if self.phase == "DEPLOY":
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.get_number()
        self.action_chosen = ""
        self.player_with_action = ""
        self.mode = "Normal"
    elif self.action_chosen == "Spore Burst":
        if self.infested_planets[chosen_planet]:
            primary_player.discard.remove(self.misc_target_choice)
            card = FindCard.find_card(self.misc_target_choice, self.card_array)
            primary_player.add_card_to_planet(card, chosen_planet)
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.get_number()
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
    elif self.action_chosen == "Ork Kannon":
        self.location_of_indirect = "PLANET"
        self.planet_of_indirect = int(game_update_string[1])
        self.p1.total_indirect_damage = 1
        self.p2.total_indirect_damage = 1
        self.p1.indirect_damage_applied = 0
        self.p2.indirect_damage_applied = 0
        self.action_chosen = ""
        self.player_with_action = ""
        self.mode = "Normal"
        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                    self.position_of_actioned_card[1])
    elif self.action_chosen == "Gift of Isha":
        discard = primary_player.get_discard()
        i = len(discard) - 1
        card_found = False
        while i > -1:
            card = primary_player.get_card_in_discard(i)
            if card.get_is_unit() and card.get_faction() == "Eldar":
                card_found = True
                if primary_player.add_card_to_planet(card, chosen_planet, sacrifice_end_of_phase=True) != -1:
                    del discard[i]
                    primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                    primary_player.aiming_reticle_color = None
                    primary_player.aiming_reticle_coords_hand = None
                    self.card_pos_to_deploy = -1
                    self.player_with_action = ""
                    self.action_chosen = ""
                    if self.phase == "DEPLOY":
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                    self.mode = "Normal"
                i = -1
            i = i - 1
        if not card_found:
            await self.game_sockets[0].receive_game_update("No valid unit in discard")
    elif self.action_chosen == "Snotling Attack":
        if self.number_with_deploy_turn == "1":
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        primary_player.summon_token_at_planet("Snotlings", int(game_update_string[1]))
        self.misc_counter = self.misc_counter - 1
        if self.misc_counter == 0:
            primary_player.discard_card_from_hand(self.card_pos_to_deploy)
            primary_player.aiming_reticle_color = None
            primary_player.aiming_reticle_coords_hand = None
            self.card_pos_to_deploy = -1
            self.player_with_action = ""
            self.action_chosen = ""
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.number
            self.mode = "Normal"
