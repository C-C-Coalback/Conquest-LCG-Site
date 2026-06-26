from .. import FindCard
from ..Phases import DeployPhase


async def update_game_event_action_planet(self, name, game_update_string):
    chosen_planet = int(game_update_string[1])
    if self.action_object.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if not self.action_object.action_chosen:
        pass
    elif self.action_object.action_chosen == "Ruined Passages":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.check_for_trait_given_pos(chosen_planet, i, "Genestealer"):
                primary_player.ready_given_pos(chosen_planet, i)
        self.action_cleanup()
    elif self.action_object.action_chosen == "Ambush":
        if self.card_to_deploy and \
                (not self.omega_ambush_active or self.infested_planets[chosen_planet]) and \
                (not self.sanguinary_ambush_active or primary_player.check_for_warlord(chosen_planet)) and \
                (not primary_player.followers_of_asuryan_relevant or self.round_number != chosen_planet):
            self.planet_pos_to_deploy = int(game_update_string[1])
            card = self.card_to_deploy
            print("Trying to discount: ", card.get_name())
            self.discounts_applied = 0
            hand_dis = primary_player.search_hand_for_discounts(card.get_faction(), card.get_traits())
            hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits(),
                                                            planet_chosen=chosen_planet, name_of_card=card.get_name())
            in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction(),
                                                                          name_of_card=card.get_name())
            same_planet_dis, same_planet_auto_dis = \
                primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
            num_termagants = 0
            if primary_player.gorzod_relevant:
                if card.get_faction() == "Astra Militarum" or card.get_faction() == "Space Marines":
                    if card.get_cost() > 1:
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        primary_player.set_aiming_reticle_in_play(warlord_planet, warlord_pos, "green")
                        self.available_discounts += 1
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
                self.action_cleanup()
                self.planet_pos_to_deploy = -1
    elif self.action_object.action_chosen == "Theater of War":
        primary_player.resolve_played_any_event()
        self.action_cleanup()
        self.need_to_resolve_battle_ability = True
        self.battle_ability_to_resolve = self.get_planet_ability_given_pos(chosen_planet)
        self.player_resolving_battle_ability = primary_player.name_player
        self.number_resolving_battle_ability = str(primary_player.number)
        self.choices_available = ["Yes", "No"]
        self.choice_context = "Resolve Battle Ability?"
        self.name_player_making_choices = primary_player.name_player
        self.tense_negotiations_active = True
        self.theater_of_war_active = True
    elif self.action_object.action_chosen == "Evangelizing Ships":
        if not self.action_object.chosen_second_card:
            if self.action_object.chosen_first_card:
                if not self.get_green_icon(chosen_planet):
                    primary_player.summon_token_at_planet("Guardsman", chosen_planet)
                    self.action_object.chosen_second_card = True
                    self.action_object.player_with_action = secondary_player.name_player
                    await self.send_update_message(secondary_player.name_player +
                                                   " must move the Evangelizing Ships to a planet.")
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Evangelizing Ships only puts units into play at non-strongpoint (green) planets.")
        else:
            og_pla, og_pos = self.action_object.position_of_actioned_card
            if chosen_planet != og_pla:
                secondary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                secondary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.action_cleanup()
    elif self.action_object.action_chosen == "Imperial Blockade":
        self.imperial_blockades_active[chosen_planet] = self.imperial_blockades_active[chosen_planet] + 1
        planet_name = self.get_planet_name(chosen_planet)
        await self.send_update_message(planet_name + " targeted for Imperial Blockade.")
        primary_player.resolve_played_any_event()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Saim-Hann Jetbike":
        if not self.action_object.chosen_first_card:
            og_pla, og_pos = self.action_object.position_of_actioned_card
            if og_pla != chosen_planet:
                if (self.get_green_icon(og_pla) and self.get_green_icon(chosen_planet)) or\
                    (self.get_red_icon(og_pla) and self.get_red_icon(chosen_planet)) or\
                        (self.get_blue_icon(og_pla) and self.get_blue_icon(chosen_planet)):
                    self.action_object.chosen_first_card = True
                    primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                    self.action_object.misc_target_planet = chosen_planet
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "That planet does not share a type with the original planet.")
    elif self.action_object.action_chosen == "Teleportarium":
        if self.action_object.chosen_first_card:
            og_pla, og_pos = self.action_object.misc_target_unit
            if abs(chosen_planet - og_pla) == 1:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Teleportarium only moves to adjacent planets.")
    elif self.action_object.action_chosen == "Corrupted Teleportarium":
        if self.action_object.chosen_first_card:
            og_pla, og_pos = self.action_object.misc_target_unit
            if chosen_planet != og_pla:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.action_cleanup()
    elif self.action_object.action_chosen == "Merciless Reclamation":
        if self.action_object.chosen_first_card and self.action_object.chosen_second_card:
            self.planet_pos_to_deploy = int(game_update_string[1])
            card = self.preloaded_find_card(primary_player.discard[self.anrakyr_unit_position])
            self.card_to_deploy = card
            print("Trying to discount: ", card.get_name())
            self.discounts_applied = 1
            hand_dis = primary_player.search_hand_for_discounts(card.get_faction(), card.get_traits())
            hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits())
            in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction())
            same_planet_dis, same_planet_auto_dis = \
                primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
            self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis + 1
            if self.available_discounts > self.discounts_applied:
                self.stored_mode = self.mode
                self.mode = "DISCOUNT"
                self.planet_aiming_reticle_position = int(game_update_string[1])
                self.planet_aiming_reticle_active = True
            else:
                await DeployPhase.deploy_card_routine(self, name, self.planet_pos_to_deploy,
                                                      discounts=self.discounts_applied)
                self.action_cleanup()
                self.planet_pos_to_deploy = -1
    elif self.action_object.action_chosen == "Decaying Warrior Squad":
        self.planet_pos_to_deploy = int(game_update_string[1])
        card = self.preloaded_find_card("Decaying Warrior Squad")
        self.card_to_deploy = card
        print("Trying to discount: ", card.get_name())
        self.discounts_applied = 0
        hand_dis = primary_player.search_hand_for_discounts(card.get_faction(), card.get_traits())
        hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits())
        in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction())
        same_planet_dis, same_planet_auto_dis = \
            primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
        self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis
        if self.available_discounts > self.discounts_applied:
            self.stored_mode = self.mode
            self.mode = "DISCOUNT"
            self.planet_aiming_reticle_position = int(game_update_string[1])
            self.planet_aiming_reticle_active = True
        else:
            await DeployPhase.deploy_card_routine(self, name, self.planet_pos_to_deploy,
                                                  discounts=self.discounts_applied)
            self.action_cleanup()
            self.planet_pos_to_deploy = -1
    elif self.action_object.action_chosen == "Exterminatus":
        if self.round_number != chosen_planet:
            primary_player.destroy_all_cards_at_planet(chosen_planet, enemy_event=False)
            secondary_player.destroy_all_cards_at_planet(chosen_planet, enemy_event=True)
            await self.complete_destruction_checks()
            primary_player.resolve_played_any_event()
            self.action_cleanup()
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Exterminatus cannot target the first planet.")
    elif self.action_object.action_chosen == "Predation":
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
            self.infest_planet(chosen_planet, primary_player)
            primary_player.resolve_played_any_event()
            self.action_cleanup()
            primary_player.aiming_reticle_coords_hand = None
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Planet is not adjacent to an infested planet.")
    elif self.action_object.action_chosen == "Hunter Gargoyles":
        if self.infested_planets[chosen_planet]:
            primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                        self.action_object.position_of_actioned_card[1])
            primary_player.move_unit_to_planet(
                self.action_object.position_of_actioned_card[0], self.action_object.position_of_actioned_card[1], chosen_planet)
            self.mode = "Normal"
            self.action_object.action_chosen = ""
            self.action_object.player_with_action = ""
            if self.phase == "DEPLOY":
                self.player_with_deploy_turn = secondary_player.name_player
                self.number_with_deploy_turn = secondary_player.number
            self.action_object.position_of_actioned_card = (-1, -1)
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Planet is not infested.")
    elif self.action_object.action_chosen == "Infernal Gateway":
        if not self.action_object.chosen_first_card:
            await self.send_update_message("Choose a valid unit first")
        else:
            pos_hand = primary_player.aiming_reticle_coords_hand_2
            pos_planet = int(game_update_string[1])
            card = FindCard.find_card(primary_player.cards[pos_hand], self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            unit_pos = primary_player.add_card_to_planet(card, pos_planet)
            if unit_pos != -1:
                primary_player.cards_in_play[pos_planet + 1][unit_pos].set_sacrifice_end_of_phase(True)
                primary_player.aiming_reticle_coords_hand = None
                primary_player.aiming_reticle_coords_hand_2 = None
                primary_player.discard_card_from_hand(pos_hand)
                self.action_cleanup()
    elif self.action_object.action_chosen == "Khymera Den":
        primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                    self.action_object.position_of_actioned_card[1])
        i = 0
        while i < len(primary_player.headquarters):
            if primary_player.get_name_given_pos(-2, i) == "Khymera":
                if primary_player.get_aiming_reticle_in_play(-2, i) == "blue":
                    if primary_player.move_unit_to_planet(-2, i, chosen_planet):
                        i = i - 1
            i = i + 1
        for i in range(7):
            if i != chosen_planet:
                j = 0
                while j < len(primary_player.cards_in_play[i + 1]):
                    if primary_player.get_aiming_reticle_in_play(i, j) == "blue":
                        if primary_player.get_name_given_pos(i, j) == "Khymera":
                            if primary_player.move_unit_to_planet(i, j, chosen_planet):
                                j = j - 1
                    j = j + 1
        primary_player.reset_all_aiming_reticles_play_hq()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Kauyon Strike":
        if self.action_object.chosen_first_card:
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = -1
            i = 0
            while i < len(primary_player.headquarters):
                if primary_player.get_aiming_reticle_in_play(-2, i) == "blue":
                    if primary_player.check_for_trait_given_pos(-2, i, "Ethereal"):
                        if primary_player.move_unit_to_planet(-2, i, chosen_planet):
                            i = i - 1
                i = i + 1
            for i in range(7):
                if i != chosen_planet:
                    j = 0
                    while j < len(primary_player.cards_in_play[i + 1]):
                        if primary_player.get_aiming_reticle_in_play(i, j) == "blue":
                            if primary_player.check_for_trait_given_pos(i, j, "Ethereal"):
                                if primary_player.move_unit_to_planet(i, j, chosen_planet):
                                    j = j - 1
                        j = j + 1
            primary_player.reset_all_aiming_reticles_play_hq()
            primary_player.resolve_played_any_event()
            self.action_cleanup()
    elif self.action_object.action_chosen == "Wildrider Squadron":
        if abs(chosen_planet - self.action_object.position_of_actioned_card[0]) == 1:
            origin_planet, origin_pos = self.action_object.position_of_actioned_card
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.cards_in_play[origin_planet + 1][origin_pos].set_once_per_phase_used(True)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
            self.action_cleanup()
            self.action_object.position_of_actioned_card = (-1, -1)
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Wildrider Squadron can only move to adjacent planets.")
    elif self.action_object.action_chosen == "Shroud Cruiser":
        if self.action_object.chosen_first_card:
            og_pla, og_pos = self.action_object.misc_target_unit
            if abs(chosen_planet - og_pla) == 1:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Shroud Cruiser only moves to adjacent planets.")
    elif self.action_object.action_chosen == "Searchlight":
        og_pla, og_pos = self.action_object.position_of_actioned_card
        if og_pla != chosen_planet:
            primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
            primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
            self.action_cleanup()
    elif self.action_object.action_chosen == "Biomass Extraction":
        if self.infested_planets[chosen_planet]:
            self.infested_planets[chosen_planet] = False
            primary_player.add_resources(1)
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Planet is not infested.")
    elif self.action_object.action_chosen == "Vivisection":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.check_if_faction_given_pos(chosen_planet, i, "Necrons", own_event=True):
                if primary_player.get_damage_given_pos(chosen_planet, i) > 0:
                    primary_player.remove_damage_from_pos(chosen_planet, i, 1, healing=True)
            else:
                primary_player.assign_damage_to_pos(chosen_planet, i, 1, by_enemy_unit=False)
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            if not secondary_player.check_if_faction_given_pos(chosen_planet, i, "Necrons"):
                if not secondary_player.get_immune_to_enemy_events(chosen_planet, i):
                    secondary_player.assign_damage_to_pos(chosen_planet, i, 1, by_enemy_unit=False)
        primary_player.resolve_played_any_event()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Sacrificial Altar":
        if chosen_planet != self.round_number:
            secondary_player.sac_altar_rewards[chosen_planet] += 1
            primary_player.draw_card()
            primary_player.add_resources(1)
            self.action_cleanup()
            planet_name = self.get_planet_name(chosen_planet)
            await self.send_update_message(planet_name + " was targeted for Sacrificial Altar.")
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Sacrifical Altar must target a non-first planet.")
    elif self.action_object.action_chosen == "Triumvirate of Ynnead":
        if self.action_object.chosen_first_card:
            if self.trium_tracker[1] != chosen_planet:
                await DeployPhase.deploy_card_routine(self, name, chosen_planet, discounts=1)
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Triumvirate of Ynnead must deploy the units to different planets.")
    elif self.action_object.action_chosen == "The Orgiastic Feast":
        card_names = self.misc_target_choice.split(sep="/")
        for i in range(len(card_names)):
            if card_names[i]:
                card = self.preloaded_find_card(card_names[i])
                if primary_player.add_card_to_planet(card, chosen_planet, triggered_card_effect=True) != -1:
                    last_el = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
                    primary_player.cards_in_play[chosen_planet + 1][last_el].return_to_hand_eor = True
                else:
                    primary_player.add_card_to_discard(card_names[i])
        primary_player.drammask_nane_check()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Da Workship":
        num_snotlings = len(secondary_player.victory_display)
        for _ in range(num_snotlings):
            primary_player.summon_token_at_planet("Snotlings", chosen_planet)
        self.action_cleanup()
    elif self.action_object.action_chosen == "Call The Storm":
        if chosen_planet != self.action_object.misc_target_planet:
            if self.action_object.chosen_first_card:
                if primary_player.check_for_trait_at_planet(chosen_planet, "Space Wolves"):
                    og_pla, og_pos = self.action_object.misc_target_unit
                    secondary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    secondary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                    self.action_cleanup()
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "No Space Wolves unit present ath that planet.")
    elif self.action_object.action_chosen == "Terminator Armour":
        if primary_player.check_for_trait_at_planet(chosen_planet, "Scout"):
            og_pla, og_pos = self.action_object.misc_target_unit
            if og_pla != chosen_planet:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.action_cleanup()
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "No Scout unit present at that planet.")
    elif self.action_object.action_chosen == "Spore Burst":
        if self.action_object.chosen_first_card:
            if self.infested_planets[chosen_planet]:
                card = self.preloaded_find_card(primary_player.discard[primary_player.aiming_reticle_coords_discard])
                primary_player.add_card_to_planet(card, chosen_planet)
                del primary_player.discard[primary_player.aiming_reticle_coords_discard]
                primary_player.aiming_reticle_coords_discard = None
                primary_player.resolve_played_any_event()
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Planet is not infested.")
    elif self.action_object.action_chosen == "Kaerux Erameas":
        if chosen_planet != self.round_number:
            if primary_player.check_for_warlord(chosen_planet) == 0 and \
                    secondary_player.check_for_warlord(chosen_planet) == 0:
                self.kaerux_erameas_active = True
                self.actions_between_battle = False
                self.p1.has_passed = False
                self.p2.has_passed = False
                self.begin_battle(chosen_planet)
                self.set_battle_initiative()
                if not self.start_battle_deepstrike:
                    self.begin_combat_round()
                    self.start_ranged_skirmish(chosen_planet)
                self.planet_aiming_reticle_active = True
                self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Kaerux Erameas cannot target planets with a warlord.")
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Kaerux Erameas cannot target the first planet.")
    elif self.action_object.action_chosen == "Bond of Brotherhood":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.check_if_faction_given_pos(chosen_planet, i, "Tau", own_event=True):
                primary_player.cards_in_play[chosen_planet + 1][i].positive_hp_until_eop += 2
            if primary_player.check_if_faction_given_pos(chosen_planet, i, "Astra Militarum"):
                primary_player.cards_in_play[chosen_planet + 1][i].extra_attack_until_end_of_phase += 2
        primary_player.resolve_played_any_event()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Mechanical Enhancement":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.check_if_faction_given_pos(chosen_planet, i, "Necrons", own_event=True):
                primary_player.cards_in_play[chosen_planet + 1][i].positive_hp_until_eop += 2
        if not primary_player.harbinger_of_eternity_active:
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
        primary_player.resolve_played_any_event()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Ravenwing Escort":
        if self.action_object.chosen_first_card:
            if self.action_object.misc_target_planet != chosen_planet:
                origin_planet, origin_pos = self.action_object.misc_target_unit
                primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
                self.action_object.misc_target_unit = (-1, -1)
                self.action_cleanup()
    elif self.action_object.action_chosen == "Move Psyker":
        if self.action_object.chosen_first_card:
            planet_pos, unit_pos = self.action_object.misc_target_unit
            if chosen_planet != planet_pos:
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                primary_player.move_unit_to_planet(planet_pos, unit_pos, chosen_planet)
                primary_player.resolve_played_any_event()
                self.action_cleanup()
    elif self.action_object.action_chosen == "Crypt of Saint Camila":
        if self.action_object.chosen_first_card:
            if self.get_blue_icon(chosen_planet):
                card = primary_player.get_card_in_hand(primary_player.aiming_reticle_coords_hand)
                if card is None:
                    return None
                primary_player.add_card_to_planet(card, chosen_planet)
                primary_player.remove_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Planet is not a technological (blue) planet.")
    elif self.action_object.action_chosen == "Rapid Assault":
        if not self.action_object.chosen_second_card and self.action_object.chosen_first_card:
            card = primary_player.get_card_in_hand(primary_player.aiming_reticle_coords_hand)
            if card is None:
                return None
            self.action_object.chosen_second_card = True
            primary_player.add_card_to_planet(card, chosen_planet, already_exhausted=True)
            primary_player.remove_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
            if self.get_red_icon(chosen_planet):
                self.action_object.misc_counter = 0
                self.action_object.misc_target_planet = chosen_planet
                await self.send_update_message("Rapid Assault can ready units at the planet")
            else:
                primary_player.resolve_played_any_event()
                self.action_cleanup()
    elif self.action_object.action_chosen == "Killing Field":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            primary_player.cards_in_play[chosen_planet + 1][i].lost_ranged_eop = True
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            secondary_player.cards_in_play[chosen_planet + 1][i].lost_ranged_eop = True
        self.action_cleanup()
    elif self.action_object.action_chosen == "Extermination":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.check_if_faction_given_pos(chosen_planet, i, "Necrons", own_event=True) and \
                    not primary_player.cards_in_play[chosen_planet + 1][i].get_unique():
                primary_player.cards_in_play[chosen_planet + 1][i].negative_hp_until_eop += 3
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            if secondary_player.check_if_faction_given_pos(chosen_planet, i, "Necrons") and \
                    not secondary_player.cards_in_play[chosen_planet + 1][i].get_unique() and \
                    not secondary_player.get_immune_to_enemy_events(chosen_planet, i):
                secondary_player.cards_in_play[chosen_planet + 1][i].negative_hp_until_eop += 3
        if not primary_player.harbinger_of_eternity_active:
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
        primary_player.has_passed = True
        primary_player.resolve_played_any_event()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Troop Transport":
        primary_player.summon_token_at_planet("Guardsman", chosen_planet)
        if self.get_green_icon(chosen_planet):
            primary_player.summon_token_at_planet("Guardsman", chosen_planet)
        self.action_cleanup()
    elif self.action_object.action_chosen == "Blood For The Blood God!":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.get_damage_given_pos(chosen_planet, i) == 0:
                primary_player.assign_damage_to_pos(chosen_planet, i, 1, by_enemy_unit=False)
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            if not secondary_player.get_immune_to_enemy_events(chosen_planet, i):
                if secondary_player.get_damage_given_pos(chosen_planet, i) == 0:
                    secondary_player.assign_damage_to_pos(chosen_planet, i, 1, by_enemy_unit=False)
        self.action_cleanup()
    elif self.action_object.action_chosen == "Vile Laboratory":
        if not self.action_object.chosen_first_card:
            valid = False
            for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                if not secondary_player.cards_in_play[chosen_planet + 1][i].check_for_a_trait(
                        "Vehicle", secondary_player.etekh_trait):
                    valid = True
            if valid:
                self.action_object.chosen_first_card = True
                self.action_object.misc_target_planet = chosen_planet
                planet_name = self.planet_array[chosen_planet]
                self.action_object.player_with_action = secondary_player.name_player
                await self.send_update_message(
                    planet_name + " chosen as the target for Vile Laboratory."
                )
            else:
                planet_name = self.planet_array[chosen_planet]
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "No valid targets for Vile Laboratory at " + planet_name + "!")
        elif self.action_object.chosen_first_card and self.action_object.chosen_second_card:
            if abs(chosen_planet - self.action_object.misc_target_planet) == 1:
                primary_player.reset_aiming_reticle_in_play(self.action_object.misc_target_unit[0], self.action_object.misc_target_unit[1])
                secondary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                              self.action_object.position_of_actioned_card[1])
                primary_player.move_unit_to_planet(self.action_object.misc_target_unit[0], self.action_object.misc_target_unit[1], chosen_planet)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Adjacent planet movement only.")
    elif self.action_object.action_chosen == "Empower":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.cards_in_play[chosen_planet + 1][i].get_is_unit():
                if primary_player.check_if_faction_given_pos(chosen_planet, i, "Eldar", own_event=True):
                    primary_player.cards_in_play[chosen_planet + 1][i].increase_extra_attack_until_end_of_battle(1)
                    primary_player.cards_in_play[chosen_planet + 1][i].positive_hp_until_eob += 1
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        primary_player.resolve_played_any_event()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Nesting Chamber":
        if not self.infested_planets[chosen_planet]:
            num_genestealers = 0
            for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
                if primary_player.check_for_trait_given_pos(chosen_planet, i, "Genestealer"):
                    num_genestealers += 1
            if num_genestealers > 1:
                self.infest_planet(chosen_planet, primary_player)
            self.action_cleanup()
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Planet is already infested.")
    elif self.action_object.action_chosen == "Vanguarding Horror":
        if self.action_object.chosen_first_card:
            if abs(chosen_planet - self.action_object.misc_target_planet) == 1:
                planet_pos, unit_pos = self.action_object.misc_target_unit
                primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                            self.action_object.position_of_actioned_card[1])
                primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = None
                primary_player.cards_in_reserve[chosen_planet].append(
                    primary_player.cards_in_reserve[planet_pos][unit_pos]
                )
                del primary_player.cards_in_reserve[planet_pos][unit_pos]
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Adjacent planet movement only.")
    elif self.action_object.action_chosen == "Daring Assault":
        if self.action_object.chosen_first_card:
            planet_pos, unit_pos = self.action_object.misc_target_unit
            if planet_pos != chosen_planet:
                primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                            self.action_object.position_of_actioned_card[1])
                primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = None
                primary_player.cards_in_reserve[chosen_planet].append(
                    primary_player.cards_in_reserve[planet_pos][unit_pos]
                )
                del primary_player.cards_in_reserve[planet_pos][unit_pos]
                self.action_object.chosen_first_card = False
    elif self.action_object.action_chosen == "Guerrilla Tactics":
        if secondary_player.cards_in_play[chosen_planet + 1]:
            target_planet = FindCard.find_planet_card(self.planet_array[chosen_planet], self.planet_cards_array)
            secondary_player.spend_resources(min(target_planet.get_resources(), secondary_player.resources))
            cards_to_discard = min(target_planet.get_cards(), len(secondary_player.cards))
            self.action_object.misc_target_planet = chosen_planet
            await self.send_update_message(target_planet.get_name() + " targeted for Guerrilla Tactics!")
            if cards_to_discard > 0:
                self.action_object.action_chosen = "Guerrilla Tactics Discard"
                self.action_object.misc_counter = cards_to_discard
                self.action_object.player_with_action = secondary_player.name_player
            else:
                self.action_object.action_chosen = "Guerrilla Tactics Move"
                self.action_object.chosen_first_card = False
                self.action_object.misc_target_unit = (-1, -1)
    elif self.action_object.action_chosen == "Agnok's Shadows":
        if self.action_object.chosen_first_card:
            og_pla, og_pos = self.action_object.position_of_actioned_card
            if abs(og_pla - chosen_planet) == 1:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Adjacent planet movement only.")
    elif self.action_object.action_chosen == "The Dawn Blade":
        if self.misc_target_choice == "Move":
            if self.action_object.chosen_first_card:
                planet_pos, unit_pos = self.action_object.misc_target_unit
                if not secondary_player.check_for_warlord(chosen_planet):
                    primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                                self.action_object.position_of_actioned_card[1])
                    primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = None
                    primary_player.cards_in_reserve[chosen_planet].append(
                        primary_player.cards_in_reserve[planet_pos][unit_pos]
                    )
                    del primary_player.cards_in_reserve[planet_pos][unit_pos]
                    self.action_cleanup()
    elif self.action_object.action_chosen == "Korporal Snagbrat":
        if self.action_object.chosen_first_card:
            if self.misc_target_choice == "RESERVE":
                planet_pos, unit_pos = self.action_object.misc_target_unit
                if abs(planet_pos - chosen_planet) == 1:
                    if not secondary_player.check_for_warlord(chosen_planet):
                        primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                                    self.action_object.position_of_actioned_card[1])
                        primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = None
                        primary_player.cards_in_reserve[chosen_planet].append(
                            primary_player.cards_in_reserve[planet_pos][unit_pos]
                        )
                        del primary_player.cards_in_reserve[planet_pos][unit_pos]
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Adjacent planet movement only.")
            else:
                planet_pos, unit_pos = self.action_object.misc_target_unit
                if abs(planet_pos - chosen_planet) == 1:
                    if not secondary_player.check_for_warlord(chosen_planet):
                        primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                                    self.action_object.position_of_actioned_card[1])
                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                        primary_player.move_unit_to_planet(planet_pos, unit_pos, chosen_planet)
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Adjacent planet movement only.")
    elif self.action_object.action_chosen == "Indiscriminate Bombing":
        if not self.action_object.chosen_first_card:
            self.action_object.chosen_first_card = True
            planet_name = self.planet_array[chosen_planet]
            self.action_object.misc_target_planet = chosen_planet
            await self.send_update_message(planet_name + " targeted for Indiscriminate Bombing.")
    elif self.action_object.action_chosen == "Kaptin Bluddflagg":
        if self.action_object.chosen_first_card:
            if chosen_planet != self.determine_leftmost_planet():
                og_pla, og_pos = self.action_object.misc_target_unit
                siv_pla, siv_pos = self.action_object.position_of_actioned_card
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.reset_aiming_reticle_in_play(siv_pla, siv_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                last_element_index = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
                if last_element_index != -1:
                    primary_player.ready_given_pos(chosen_planet, last_element_index)
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                self.action_cleanup()
            else:
                await self.send_update_message("That is the leftmost planet!")
    elif self.action_object.action_chosen == "Sivarla Soulbinder":
        if self.action_object.chosen_first_card:
            og_pla, og_pos = self.action_object.misc_target_unit
            siv_pla, siv_pos = self.action_object.position_of_actioned_card
            if og_pla != chosen_planet:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.reset_aiming_reticle_in_play(siv_pla, siv_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                self.action_cleanup()
    elif self.action_object.action_chosen == "Archon's Palace":
        self.action_object.misc_target_planet = chosen_planet
        self.choices_available = ["Cards", "Resources"]
        self.choice_context = "Archon's Palace"
        self.name_player_making_choices = primary_player.name_player
    elif self.action_object.action_chosen == "Drudgery":
        if self.action_object.chosen_first_card:
            card = self.preloaded_find_card(self.misc_target_choice)
            primary_player.add_card_to_planet(card, chosen_planet)
            primary_player.aiming_reticle_coords_discard = None
            primary_player.discard.remove(self.misc_target_choice)
            if primary_player.optimized_protocol_check():
                self.create_reaction("Optimized Protocol", primary_player.name_player,
                                     (int(primary_player.get_number()), chosen_planet, -1))
            primary_player.resolve_played_any_event()
            self.action_cleanup()
    elif self.action_object.action_chosen == "Steed of Slaanesh":
        if not secondary_player.check_for_warlord(chosen_planet):
            if self.action_object.position_of_actioned_card[0] != chosen_planet:
                primary_player.move_unit_to_planet(self.action_object.position_of_actioned_card[0], self.action_object.position_of_actioned_card[1],
                                                   chosen_planet)
                self.action_cleanup()
    elif self.action_object.action_chosen == "Warpstorm":
        additional_tax = secondary_player.get_additional_costs_target_planet(chosen_planet)
        if primary_player.spend_resources(additional_tax):
            for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
                if primary_player.cards_in_play[chosen_planet + 1][i].get_is_unit():
                    if not primary_player.cards_in_play[chosen_planet + 1][i].get_attachments() and \
                            primary_player.get_ability_given_pos(chosen_planet, i) != "Frenzied Bloodthirster":
                        primary_player.assign_damage_to_pos(chosen_planet, i, 2, by_enemy_unit=False)
            for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                if secondary_player.cards_in_play[chosen_planet + 1][i].get_is_unit():
                    if not secondary_player.cards_in_play[chosen_planet + 1][i].get_attachments():
                        if not secondary_player.get_immune_to_enemy_events(chosen_planet, i, power=True):
                            secondary_player.assign_damage_to_pos(chosen_planet, i, 2, by_enemy_unit=False)
            primary_player.resolve_played_any_event()
            self.action_cleanup()
        else:
            await self.send_update_message("Cannot target planet; insufficient resources for tax effects.")
    elif self.action_object.action_chosen == "Core Destabilization":
        if chosen_planet != self.round_number:
            additional_tax = secondary_player.get_additional_costs_target_planet(chosen_planet)
            if primary_player.spend_resources(additional_tax):
                for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
                    if primary_player.cards_in_play[chosen_planet + 1][i].get_card_type() == "Army":
                        if primary_player.get_cost_given_pos(chosen_planet, i) > 2:
                            if primary_player.get_ability_given_pos(chosen_planet, i) != "Frenzied Bloodthirster":
                                primary_player.assign_damage_to_pos(chosen_planet, i, 3, by_enemy_unit=False)
                for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                    if secondary_player.cards_in_play[chosen_planet + 1][i].get_card_type() == "Army":
                        if secondary_player.get_cost_given_pos(chosen_planet, i) > 2:
                            if not secondary_player.get_immune_to_enemy_events(chosen_planet, i, power=True):
                                secondary_player.assign_damage_to_pos(chosen_planet, i, 3, by_enemy_unit=False)
                if chosen_planet != 0:
                    for i in range(len(primary_player.cards_in_play[chosen_planet])):
                        if primary_player.get_ability_given_pos(chosen_planet - 1, i) != "Frenzied Bloodthirster":
                            primary_player.assign_damage_to_pos(chosen_planet - 1, i, 1, by_enemy_unit=False)
                    for i in range(len(secondary_player.cards_in_play[chosen_planet])):
                        if not secondary_player.get_immune_to_enemy_events(chosen_planet - 1, i, power=True):
                            secondary_player.assign_damage_to_pos(chosen_planet - 1, i, 1, by_enemy_unit=False)
                if chosen_planet != 6:
                    for i in range(len(primary_player.cards_in_play[chosen_planet + 2])):
                        if primary_player.get_ability_given_pos(chosen_planet + 1, i) != "Frenzied Bloodthirster":
                            primary_player.assign_damage_to_pos(chosen_planet + 1, i, 1, by_enemy_unit=False)
                    for i in range(len(secondary_player.cards_in_play[chosen_planet + 2])):
                        if not secondary_player.get_immune_to_enemy_events(chosen_planet + 1, i, power=True):
                            secondary_player.assign_damage_to_pos(chosen_planet + 1, i, 1, by_enemy_unit=False)
                primary_player.resolve_played_any_event()
                self.action_cleanup()
            else:
                await self.send_update_message("Cannot target planet; insufficient resources for tax effects.")
    elif self.action_object.action_chosen == "Squadron Redeployment":
        if self.action_object.chosen_first_card:
            origin_planet, origin_pos = self.action_object.misc_target_unit
            dest_planet = chosen_planet
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, dest_planet)
            primary_player.resolve_played_any_event()
            self.action_cleanup()
    elif self.action_object.action_chosen == "Mycetic Spores":
        if self.action_object.chosen_first_card:
            if primary_player.search_card_at_planet(chosen_planet, "Termagant", ability_checking=False):
                origin_planet, origin_pos = self.action_object.misc_target_unit
                dest_planet = chosen_planet
                primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                primary_player.move_unit_to_planet(origin_planet, origin_pos, dest_planet)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "No Termagant tokens present at that planet.")
    elif self.action_object.action_chosen == "Anrakyr the Traveller":
        if self.anrakyr_unit_position != -1:
            self.planet_pos_to_deploy = int(game_update_string[1])
            if self.anrakyr_deck_choice == primary_player.name_player:
                card = FindCard.find_card(primary_player.discard[self.anrakyr_unit_position], self.card_array,
                                          self.cards_dict, self.apoka_errata_cards, self.cards_that_have_errata)
            else:
                card = FindCard.find_card(secondary_player.discard[self.anrakyr_unit_position], self.card_array,
                                          self.cards_dict, self.apoka_errata_cards, self.cards_that_have_errata)
            self.card_to_deploy = card
            print("Trying to discount: ", card.get_name())
            self.discounts_applied = 0
            hand_dis = primary_player.search_hand_for_discounts(card.get_faction(), card.get_traits())
            hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits())
            in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction())
            same_planet_dis, same_planet_auto_dis = \
                primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
            self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis
            if self.discounts_applied >= self.available_discounts:
                added_card_to_planet = False
                own_card = True
                if self.anrakyr_deck_choice == secondary_player.name_player:
                    own_card = False
                added_card_to_planet, _ = primary_player.play_card(
                    chosen_planet, card=self.card_to_deploy, is_owner_of_card=own_card
                )
                if added_card_to_planet == "SUCCESS":
                    self.queued_sound = "onplay"
                    primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                                self.action_object.position_of_actioned_card[1])
                    position_of_unit = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
                    primary_player.cards_in_play[chosen_planet + 1][position_of_unit].\
                        valid_target_dynastic_weaponry = True
                    if "Dynastic Weaponry" in primary_player.discard:
                        if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                            self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                                 (int(primary_player.get_number()), chosen_planet, position_of_unit))
                    if primary_player.optimized_protocol_check():
                        self.create_reaction("Optimized Protocol", primary_player.name_player,
                                             (int(primary_player.get_number()), chosen_planet, position_of_unit))
                    self.action_cleanup()
                    if self.anrakyr_deck_choice == primary_player.name_player:
                        del primary_player.discard[self.anrakyr_unit_position]
                    else:
                        del secondary_player.discard[self.anrakyr_unit_position]
            else:
                self.stored_mode = self.mode
                self.mode = "DISCOUNT"
                self.planet_aiming_reticle_position = int(game_update_string[1])
                self.planet_aiming_reticle_active = True
    elif self.action_object.action_chosen == "Warp Rift":
        if not self.action_object.chosen_first_card:
            self.action_object.chosen_first_card = True
            self.action_object.misc_target_planet = chosen_planet
            await self.send_update_message("Chose " + self.planet_array[chosen_planet] +
                                           " as first target for Warp Rift")
        else:
            if abs(self.action_object.misc_target_planet - chosen_planet) == 1:
                temp = self.planet_array[chosen_planet]
                self.planet_array[chosen_planet] = self.planet_array[self.action_object.misc_target_planet]
                self.planet_array[self.action_object.misc_target_planet] = temp
                temp = self.replaced_planets[chosen_planet]
                self.replaced_planets[chosen_planet] = self.replaced_planets[self.action_object.misc_target_planet]
                self.replaced_planets[self.action_object.misc_target_planet] = temp
                temp = self.original_planet_array[chosen_planet]
                self.original_planet_array[chosen_planet] = self.original_planet_array[self.action_object.misc_target_planet]
                self.original_planet_array[self.action_object.misc_target_planet] = temp
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                primary_player.resolve_played_any_event()
                self.action_cleanup()
    elif self.action_object.action_chosen == "Ecstatic Seizures":
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            if primary_player.get_ability_given_pos(chosen_planet, i) != "Frenzied Bloodthirster":
                primary_player.discard_attachments_from_card(chosen_planet, i)
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            if not secondary_player.get_immune_to_enemy_events(chosen_planet, i, power=True):
                secondary_player.discard_attachments_from_card(chosen_planet, i)
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        primary_player.resolve_played_any_event()
        self.action_cleanup()
    elif self.action_object.action_chosen == "Spore Burst":
        if self.infested_planets[chosen_planet]:
            primary_player.discard.remove(self.misc_target_choice)
            card = FindCard.find_card(self.misc_target_choice, self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            primary_player.add_card_to_planet(card, chosen_planet)
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
            primary_player.resolve_played_any_event()
            self.action_cleanup()
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Planet is not infested.")
    elif self.action_object.action_chosen == "Ork Kannon":
        self.location_of_indirect = "PLANET"
        self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
        self.planet_of_indirect = int(game_update_string[1])
        self.p1.total_indirect_damage = 1
        self.p2.total_indirect_damage = 1
        self.p1.indirect_damage_applied = 0
        self.p2.indirect_damage_applied = 0
        primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                    self.action_object.position_of_actioned_card[1])
        self.action_cleanup()
        await self.send_update_message(self.get_planet_name(self.planet_of_indirect) + " targeted for Ork Kannon")
    elif self.action_object.action_chosen == "Rapid Evolution Termagant":
        primary_player.summon_token_at_planet("Termagant", chosen_planet)
        self.action_object.action_chosen = "Rapid Evolution"
        await self.send_update_message("You many now continue with Rapid Evolution")
    elif self.action_object.action_chosen == "Soul Seizure":
        if self.action_object.chosen_first_card:
            card = FindCard.find_card(secondary_player.discard[secondary_player.aiming_reticle_coords_discard], self.card_array,
                                      self.cards_dict, self.apoka_errata_cards, self.cards_that_have_errata)
            primary_player.add_card_to_planet(card, chosen_planet, is_owner_of_card=False)
            del secondary_player.discard[secondary_player.aiming_reticle_coords_discard]
            secondary_player.aiming_reticle_coords_discard = None
            await primary_player.dark_eldar_event_played()
            primary_player.torture_event_played("Soul Seizure")
            primary_player.resolve_played_any_event()
            self.action_cleanup()
    elif self.action_object.action_chosen == "Rain of Mycetic Spores":
        if abs(self.action_object.misc_target_planet - chosen_planet) == 1:
            if not self.infested_planets[chosen_planet]:
                self.infest_planet(chosen_planet, primary_player)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Planet is already infested.")
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                              "Adjacent planet only.")
    elif self.action_object.action_chosen == "Nurgling Bomb":
        self.action_object.chosen_first_card = True
        found_nurgling_bomb_target_p1 = False
        for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
            primary_player.cards_in_play[chosen_planet + 1][i].choice_nurgling_bomb = ""
            if not primary_player.check_for_trait_given_pos(chosen_planet, i, "Nurgle"):
                primary_player.cards_in_play[chosen_planet + 1][i].need_to_resolve_nurgling_bomb = True
                primary_player.set_aiming_reticle_in_play(chosen_planet, i, "blue")
                found_nurgling_bomb_target_p1 = True
        found_nurgling_bomb_target_p2 = False
        for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
            secondary_player.cards_in_play[chosen_planet + 1][i].choice_nurgling_bomb = ""
            if not secondary_player.check_for_trait_given_pos(chosen_planet, i, "Nurgle"):
                if not secondary_player.get_immune_to_enemy_events(chosen_planet, i):
                    secondary_player.cards_in_play[chosen_planet + 1][i].need_to_resolve_nurgling_bomb = True
                    secondary_player.set_aiming_reticle_in_play(chosen_planet, i, "blue")
                    found_nurgling_bomb_target_p2 = True
        if found_nurgling_bomb_target_p1:
            self.action_object.player_with_action = primary_player.name_player
        elif found_nurgling_bomb_target_p2:
            self.action_object.player_with_action = secondary_player.name_player
        else:
            self.complete_nurgling_bomb(chosen_planet, primary_player)
    elif self.action_object.action_chosen == "Behind Enemy Lines":
        if self.action_object.chosen_first_card:
            planet_chosen = int(game_update_string[1])
            card = self.game.card_to_deploy
            await self.discount_begin_routine(planet_chosen, card, primary_player)
            if card.check_for_a_trait("Elite"):
                primary_player.master_warpsmith_count = 0
            if self.available_discounts > self.discounts_applied:
                self.stored_mode = self.mode
                self.mode = "DISCOUNT"
                self.planet_aiming_reticle_position = int(game_update_string[1])
                self.planet_aiming_reticle_active = True
            else:
                await DeployPhase.deploy_card_routine(self, name, game_update_string[1],
                                                      discounts=self.discounts_applied)
    elif self.action_object.action_chosen == "Staging Ground" or self.action_object.action_chosen == "Launch Pads":
        if self.action_object.chosen_first_card:
            planet_chosen = int(game_update_string[1])
            card = self.card_to_deploy
            if card is None:
                return None
            await self.discount_begin_routine(planet_chosen, card, primary_player)
            if card.check_for_a_trait("Elite"):
                primary_player.master_warpsmith_count = 0
            if self.available_discounts > self.discounts_applied:
                self.stored_mode = self.mode
                self.mode = "DISCOUNT"
                self.planet_aiming_reticle_position = int(game_update_string[1])
                self.planet_aiming_reticle_active = True
            else:
                await DeployPhase.deploy_card_routine(self, name, game_update_string[1],
                                                      discounts=self.discounts_applied)
    elif self.action_object.action_chosen == "Know No Fear":
        if self.action_object.chosen_first_card:
            if self.planets_free_for_know_no_fear[chosen_planet]:
                primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                            self.action_object.position_of_actioned_card[1])
                primary_player.move_unit_to_planet(self.action_object.position_of_actioned_card[0],
                                                   self.action_object.position_of_actioned_card[1], chosen_planet)
                self.planets_free_for_know_no_fear[chosen_planet] = False
                self.action_object.misc_counter -= 1
                if self.action_object.misc_counter > 0:
                    self.action_object.chosen_first_card = False
                    self.action_object.position_of_actioned_card = (-1, -1)
                    await self.send_update_message(str(self.action_object.misc_counter) + " uses left of Know No Fear")
                else:
                    primary_player.resolve_played_any_event()
                    self.action_cleanup()
                    self.planets_free_for_know_no_fear = [True, True, True, True, True, True, True]
    elif self.action_object.action_chosen == "Gift of Isha":
        discard = primary_player.get_discard()
        i = len(discard) - 1
        card_found = False
        while i > -1:
            card = primary_player.get_card_in_discard(i)
            if card.get_is_unit() and card.get_faction() == "Eldar":
                card_found = True
                if primary_player.add_card_to_planet(card, chosen_planet, sacrifice_end_of_phase=True) != -1:
                    del discard[i]
                    primary_player.resolve_played_any_event()
                    self.action_cleanup()
                i = -1
            i = i - 1
        if not card_found:
            await self.send_update_message("No valid unit in discard")
    elif self.action_object.action_chosen == "Smash 'n Bash":
        if not self.action_object.chosen_first_card:
            if not secondary_player.check_for_warlord(chosen_planet):
                for i in range(len(primary_player.cards_in_play[chosen_planet + 1])):
                    primary_player.assign_damage_to_pos(chosen_planet, i, 1, by_enemy_unit=False)
                self.action_object.misc_counter = 3
                self.action_object.misc_target_planet = chosen_planet
                self.action_object.chosen_first_card = True
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Enemy warlord is present.")
    elif self.action_object.action_chosen == "Ksi'm'yen Orbital City":
        if self.action_object.chosen_first_card:
            origin_planet, origin_pos = self.action_object.misc_target_unit
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
            new_pos = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
            primary_player.ready_given_pos(chosen_planet, new_pos)
            self.action_cleanup()
    elif self.action_object.action_chosen == "Fungal Turf":
        primary_player.summon_token_at_planet("Snotlings", int(game_update_string[1]))
        self.action_object.misc_counter = self.action_object.misc_counter - 1
        await self.send_update_message(str(self.action_object.misc_counter) + " Snotlings left to place.")
        if self.action_object.misc_counter == 0:
            self.action_cleanup()
    elif self.action_object.action_chosen == "Dread Command Barge":
        if self.action_object.chosen_first_card:
            og_pla, og_pos = self.action_object.position_of_actioned_card
            if abs(og_pla - chosen_planet) == 1:
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                primary_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Adjacent planet movement only.")
    elif self.action_object.action_chosen == "Snotling Attack":
        primary_player.summon_token_at_planet("Snotlings", int(game_update_string[1]))
        self.action_object.misc_counter = self.action_object.misc_counter - 1
        if self.action_object.misc_counter == 0:
            primary_player.resolve_played_any_event()
            self.action_cleanup()
