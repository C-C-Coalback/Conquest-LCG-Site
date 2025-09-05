from .. import FindCard
from ..Phases import CommandPhase
from ..Phases import DeployPhase


async def resolve_planet_reaction(self, name, game_update_string, primary_player, secondary_player):
    chosen_planet = int(game_update_string[1])
    current_reaction = self.reactions_needing_resolving[0]
    num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
    if self.reactions_needing_resolving[0] == "Blackmane's Hunt":
        warlord_planet = primary_player.warlord_commit_location
        new_planet = int(game_update_string[1])
        if abs(warlord_planet - new_planet) == 1:
            primary_player.commit_warlord_to_planet_from_planet(warlord_planet, new_planet)
            self.delete_reaction()
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
    elif current_reaction == "Exploratory Drone":
        p_num, origin_planet, origin_pos = self.positions_of_unit_triggering_reaction[0]
        if abs(origin_planet - chosen_planet) == 1:
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
        self.delete_reaction()
    elif current_reaction == "The Emperor's Retribution":
        if self.chosen_first_card:
            og_pla, og_pos = self.misc_target_unit
            if chosen_planet != self.round_number:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                last_el_index = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
                primary_player.cards_in_play[chosen_planet][last_el_index].command_until_combat += 1
                self.delete_reaction()
    elif current_reaction == "Shadow Hunt":
        card_name = primary_player.cards_removed_from_game[self.misc_counter]
        card = self.preloaded_find_card(card_name)
        primary_player.add_card_to_planet(card, chosen_planet)
        target_index = -1
        for i in range(len(primary_player.cards_removed_from_game)):
            if primary_player.cards_removed_from_game[i] == card_name:
                if primary_player.cards_removed_from_game_hidden[i] == "N":
                    target_index = i
        if target_index != -1:
            del primary_player.cards_removed_from_game[target_index]
            del primary_player.cards_removed_from_game_hidden[target_index]
        await primary_player.dark_eldar_event_played()
        self.delete_reaction()
    elif current_reaction == "Tras the Corrupter":
        self.misc_target_planet = chosen_planet
        await self.send_update_message("Replacing " + self.planet_array[chosen_planet] + ". Choose new planet.")
        self.choices_available = self.available_breach_planets
        if not self.choices_available:
            await self.send_update_message("No planets left to replace with!")
            self.delete_reaction()
        else:
            self.choice_context = "Tras Replacement"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
    elif current_reaction == "Liatha's Retinue":
        if chosen_planet != self.last_planet_checked_for_battle:
            card = self.preloaded_find_card("Liatha's Retinue")
            primary_player.add_card_to_planet(card, chosen_planet, already_exhausted=True)
            retinue_index = -1
            for i in range(len(primary_player.cards_removed_from_game)):
                if primary_player.cards_removed_from_game[i] == "Liatha's Retinue":
                    if primary_player.cards_removed_from_game_hidden[i] == "N":
                        retinue_index = i
            if retinue_index != -1:
                del primary_player.cards_removed_from_game[retinue_index]
                del primary_player.cards_removed_from_game_hidden[retinue_index]
            self.delete_reaction()
    elif current_reaction == "Navida Prime Commit":
        if abs(chosen_planet - self.positions_of_unit_triggering_reaction[0][1]) == 1:
            self.create_reaction(self.planet_array[chosen_planet] + " Commit", primary_player.name_player,
                                 (int(primary_player.number), self.positions_of_unit_triggering_reaction[0][1], -1))
            self.delete_reaction()
    elif current_reaction == "Catatonic Pain":
        if abs(planet_pos - chosen_planet) == 1:
            secondary_player.move_unit_to_planet(planet_pos, unit_pos, chosen_planet)
            await primary_player.dark_eldar_event_played()
            primary_player.torture_event_played()
            self.delete_reaction()
    elif current_reaction == "Vamii Industrial Complex":
        if self.chosen_first_card:
            if chosen_planet != self.round_number:
                self.discounts_applied = 0
                card = self.card_to_deploy
                await self.calculate_available_discounts_unit(chosen_planet, card, primary_player)
                await self.calculate_automatic_discounts_unit(chosen_planet, card, primary_player)
                if card.check_for_a_trait("Elite"):
                    primary_player.master_warpsmith_count = 0
                self.card_to_deploy = card
                if self.available_discounts > self.discounts_applied:
                    self.stored_mode = self.mode
                    self.mode = "DISCOUNT"
                    self.planet_aiming_reticle_position = chosen_planet
                    self.planet_aiming_reticle_active = True
                else:
                    await DeployPhase.deploy_card_routine(self, name, chosen_planet, discounts=self.discounts_applied)
    elif current_reaction == "Interceptor Squad":
        if not self.chosen_first_card:
            p_num, origin_planet, origin_pos = self.positions_of_unit_triggering_reaction[0]
            if abs(origin_planet - chosen_planet) == 1:
                can_move = False
                for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
                    if primary_player.cards_in_play[chosen_planet + 1][i].just_entered_play:
                        can_move = True
                if not can_move:
                    for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                        if secondary_player.cards_in_play[chosen_planet + 1][i].just_entered_play:
                            can_move = True
                if can_move:
                    primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                    primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
                    self.chosen_first_card = True
                    self.misc_target_planet = chosen_planet
    elif current_reaction == "Heralding Cherubim":
        p_num, origin_planet, origin_pos = self.positions_of_unit_triggering_reaction[0]
        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
        if warlord_pla != -2:
            if abs(warlord_pla - chosen_planet) == 1:
                primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
                self.delete_reaction()
    elif current_reaction == "Undying Saint":
        if self.round_number != chosen_planet or secondary_player.has_initiative:
            if "Undying Saint" in primary_player.discard:
                primary_player.add_card_to_planet(self.preloaded_find_card("Undying Saint"), chosen_planet)
                primary_player.discard.remove("Undying Saint")
            if "Undying Saint" in primary_player.discard:
                self.create_reaction("Undying Saint", primary_player.name_player, (int(primary_player.number), -1, -1))
            self.delete_reaction()
    elif current_reaction == "Agra's Preachings":
        if len(secondary_player.cards_in_play[chosen_planet + 1]) > 0:
            if len(primary_player.deck) > 5:
                self.choices_available = primary_player.deck[:6]
                self.choice_context = "Agra's Preachings choices"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
                self.misc_counter = 0
                self.misc_target_planet = chosen_planet
                primary_player.number_cards_to_search = 6
            else:
                self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Foresight":
        warlord_planet = primary_player.warlord_commit_location
        new_planet = int(game_update_string[1])
        if warlord_planet != new_planet:
            primary_player.commit_warlord_to_planet_from_planet(warlord_planet, new_planet)
            self.delete_reaction()
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
    elif self.reactions_needing_resolving[0] == "Wyrdboy Stikk":
        primary_player.summon_token_at_planet("Snotlings", chosen_planet)
        self.delete_reaction()
    elif current_reaction == "Blood Axe Strategist":
        if abs(planet_pos - chosen_planet) == 1:
            primary_player.move_unit_to_planet(planet_pos, unit_pos, chosen_planet)
            self.delete_reaction()
    elif current_reaction == "Banshee Assault Squad":
        primary_player.remove_card_name_from_hand("Banshee Assault Squad")
        card = FindCard.find_card("Banshee Assault Squad", self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)
        primary_player.add_card_to_planet(card, chosen_planet)
        self.delete_reaction()
        if primary_player.search_hand_for_card("Banshee Assault Squad"):
            self.create_reaction("Banshee Assault Squad", primary_player.name_player,
                                 (int(primary_player.number), -1, -1))
    elif current_reaction == "Tactical Withdrawal":
        if not self.chosen_first_card:
            if abs(planet_pos - chosen_planet) == 1:
                self.misc_target_planet = chosen_planet
                self.chosen_first_card = True
                planet_name = self.planet_array[chosen_planet]
                await self.send_update_message("You may now move units to " + planet_name + ".")
    elif self.reactions_needing_resolving[0] == "Cry of the Wind":
        if self.chosen_first_card:
            origin_planet, origin_pos = self.misc_target_unit
            if abs(origin_planet - chosen_planet) == 1:
                primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
                self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Heretek Inventor":
        p_num, origin_planet, origin_pos = self.positions_of_unit_triggering_reaction[0]
        if origin_planet != chosen_planet:
            secondary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
            self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Obedience":
        if self.chosen_first_card:
            origin_planet, origin_pos = self.misc_target_unit
            new_planet = int(game_update_string[1])
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, new_planet)
            self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
        if self.chosen_first_card and not self.chosen_second_card:
            current_planet, current_position = self.misc_target_unit
            if current_planet != chosen_planet:
                primary_player.move_unit_to_planet(current_planet, current_position, chosen_planet)
                self.chosen_second_card = True
                new_pos = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
                self.misc_target_unit = (chosen_planet, new_pos)
                self.positions_of_unit_triggering_reaction[0] = (int(primary_player.number),
                                                                 chosen_planet, new_pos)
    elif current_reaction == "Sacaellum's Finest":
        if self.get_green_icon(chosen_planet):
            primary_player.remove_card_name_from_hand("Sacaellum's Finest")
            card = FindCard.find_card("Sacaellum's Finest", self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            primary_player.add_card_to_planet(card, chosen_planet)
            self.sacaellums_finest_active = True
            self.delete_reaction()
    elif current_reaction == "Raiding Portal":
        if self.chosen_first_card:
            if chosen_planet != self.misc_target_planet:
                if self.get_red_icon(chosen_planet):
                    og_pla, og_pos = self.misc_target_unit
                    primary_player.cards_in_play[og_pla + 1][og_pos].extra_command_eop += 1
                    primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                    self.delete_reaction()
    elif current_reaction == "Shadowed Thorns Venom":
        if self.chosen_first_card:
            if self.get_red_icon(chosen_planet):
                og_pla, og_pos = self.misc_target_unit
                if og_pla != chosen_planet:
                    primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                    self.chosen_first_card = False
                    self.misc_target_unit = (-1, -1)
    elif current_reaction == "Sautekh Royal Crypt":
        secondary_player.sautekh_royal_crypt = chosen_planet
        await self.send_update_message(self.planet_array[chosen_planet] +
                                       " was predicted as the warlord commit location.")
        self.delete_reaction()
        await CommandPhase.update_game_event_command_section(self, secondary_player.name_player, game_update_string)
    elif current_reaction == "Endless Legions":
        if self.chosen_first_card:
            if self.apoka:
                if chosen_planet != self.last_planet_checked_for_battle:
                    card_name = self.misc_target_choice
                    card = self.preloaded_find_card(card_name)
                    primary_player.add_card_to_planet(card, chosen_planet, already_exhausted=True)
                    self.delete_reaction()
            else:
                card_name = self.misc_target_choice
                card = self.preloaded_find_card(card_name)
                primary_player.add_card_to_planet(card, chosen_planet)
                self.delete_reaction()
    elif current_reaction == "Reinforced Synaptic Network":
        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
        if abs(warlord_pla - chosen_planet) == 1:
            if primary_player.headquarters[unit_pos].get_ability() == "Gravid Tervigon":
                self.create_reaction("Gravid Tervigon", self.name_player,
                                     (int(self.number), chosen_planet, -1))
            if primary_player.headquarters[unit_pos].get_ability() == "Venomthrope Polluter":
                self.create_reaction("Venomthrope Polluter", self.name_player,
                                     (int(self.number), chosen_planet, -1))
            primary_player.move_unit_to_planet(-2, unit_pos, chosen_planet)
            for j in range(len(primary_player.headquarters)):
                if primary_player.headquarters[j].get_ability() == "Synaptic Link":
                    primary_player.create_reaction("Synaptic Link", primary_player.name_player,
                                                   (int(primary_player.number), -1, -1))
        self.delete_reaction()
    elif current_reaction == "Salvaged Battlewagon":
        if self.chosen_first_card:
            if abs(chosen_planet - self.positions_of_unit_triggering_reaction[0][1]) == 1:
                card_name = primary_player.cards[primary_player.aiming_reticle_coords_hand]
                card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                primary_player.add_card_to_planet(card, chosen_planet)
                primary_player.remove_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.delete_reaction()
    elif current_reaction == "Hive Ship Tendrils":
        if self.chosen_first_card:
            card = primary_player.get_card_in_discard(primary_player.aiming_reticle_coords_discard)
            primary_player.add_card_to_planet(card, chosen_planet)
            del primary_player.discard[primary_player.aiming_reticle_coords_discard]
            primary_player.aiming_reticle_coords_discard = None
            self.delete_reaction()
    elif current_reaction == "Drifting Spore Mines":
        if not self.chosen_first_card:
            if abs(chosen_planet - planet_pos) == 1:
                secondary_player.move_unit_to_planet(planet_pos, unit_pos, chosen_planet)
                last_element_index = len(secondary_player.cards_in_play[chosen_planet + 1]) - 1
                self.misc_target_unit = (chosen_planet, last_element_index)
                self.player_who_resolves_reaction[0] = secondary_player.name_player
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Damage Drifting Spore Mines?"
                self.resolving_search_box = True
                self.name_player_making_choices = secondary_player.name_player
    elif current_reaction == "Declare the Crusade":
        planet_to_add = self.misc_target_choice
        planet_to_remove = self.planet_array[chosen_planet]
        self.planets_removed_from_game.remove(planet_to_add)
        self.planets_removed_from_game.append(planet_to_remove)
        self.planet_array[chosen_planet] = planet_to_add
        self.delete_reaction()
    elif current_reaction == "Inspirational Fervor":
        if self.chosen_first_card:
            if chosen_planet != self.misc_target_planet:
                i = 0
                og_planet = self.misc_target_planet
                while i < len(primary_player.cards_in_play[og_planet + 1]):
                    if primary_player.cards_in_play[og_planet + 1][i].aiming_reticle_color == "blue":
                        primary_player.reset_aiming_reticle_in_play(og_planet, i)
                        primary_player.move_unit_to_planet(og_planet, i, chosen_planet)
                        i = i - 1
                    i = i + 1
                self.delete_reaction()
    elif current_reaction == "Ardaci-strain Broodlord":
        if abs(chosen_planet - planet_pos) == 1:
            if not self.infested_planets[chosen_planet]:
                self.infest_planet(chosen_planet, primary_player)
                primary_player.draw_card()
                for i in range(len(primary_player.headquarters)):
                    if primary_player.get_ability_given_pos(-2, i) == "Ardaci-strain Broodlord":
                        primary_player.set_once_per_phase_used_given_pos(-2, i, True)
                for i in range(7):
                    for j in range(len(primary_player.cards_in_play[i + 1])):
                        if primary_player.get_ability_given_pos(i, j) == "Ardaci-strain Broodlord":
                            primary_player.set_once_per_phase_used_given_pos(i, j, True)
                self.delete_reaction()
    elif current_reaction == "Third Eye of Trazyn":
        if self.chosen_first_card:
            if abs(self.misc_target_planet - chosen_planet) == 1:
                og_pla, og_pos = self.misc_target_unit
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.delete_reaction()
    elif current_reaction == "Spore Chimney":
        self.infest_planet(chosen_planet, primary_player)
        self.delete_reaction()
