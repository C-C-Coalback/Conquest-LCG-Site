from .. import FindCard
import copy


async def update_game_event_action_hand(self, name, game_update_string, may_nullify=True):
    if self.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    hand_pos = int(game_update_string[2])
    card = primary_player.get_card_in_hand(int(game_update_string[2]))
    ability = card.get_ability()
    urien_rel = primary_player.urien_relevant
    cost = card.get_cost(urien_rel)
    print(card.get_allowed_phases_while_in_hand(), self.phase)
    print(card.get_has_action_while_in_hand())
    if not self.action_chosen:
        self.card_pos_to_deploy = int(game_update_string[2])
        can_continue = True
        if primary_player.subject_omega_relevant and self.phase == "COMBAT":
            if primary_player.get_ambush_of_card(card):
                if not primary_player.enemy_holding_cell_check(card.get_name()):
                    self.card_pos_to_deploy = int(game_update_string[2])
                    self.action_chosen = "Ambush"
                    self.card_to_deploy = card
                    self.card_type_of_selected_card_in_hand = card.get_card_type()
                    primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                    primary_player.aiming_reticle_color = "blue"
                    self.omega_ambush_active = True
                    can_continue = False
        if card.get_ability() == "Sanguinary Guard" and self.phase == "COMBAT" and can_continue:
            if not primary_player.enemy_holding_cell_check(card.get_name()):
                self.card_pos_to_deploy = int(game_update_string[2])
                self.action_chosen = "Ambush"
                self.card_to_deploy = card
                self.card_type_of_selected_card_in_hand = card.get_card_type()
                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                primary_player.aiming_reticle_color = "blue"
                self.sanguinary_ambush_active = True
        elif primary_player.get_ambush_of_card(card) and self.phase == "COMBAT" and can_continue:
            if not primary_player.enemy_holding_cell_check(card.get_name()):
                self.card_pos_to_deploy = int(game_update_string[2])
                self.action_chosen = "Ambush"
                self.card_to_deploy = card
                self.card_type_of_selected_card_in_hand = card.get_card_type()
                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                primary_player.aiming_reticle_color = "blue"
        elif card.get_has_action_while_in_hand() and not self.action_chosen and can_continue:
            if card.get_allowed_phases_while_in_hand() == self.phase or \
                    card.get_allowed_phases_while_in_hand() == "ALL":
                if primary_player.get_ambush_of_card(card):
                    if not primary_player.enemy_holding_cell_check(card.get_name()):
                        self.card_pos_to_deploy = int(game_update_string[2])
                        self.action_chosen = "Ambush"
                        self.card_to_deploy = card
                        self.card_type_of_selected_card_in_hand = card.get_card_type()
                        primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                        primary_player.aiming_reticle_color = "blue"
                elif primary_player.spend_resources(cost):
                    if may_nullify and secondary_player.nullify_check() and ability != "Triumvirate of Ynnead" and \
                            ability != "Daring Assault" and ability != "The Siege Masters":
                        primary_player.add_resources(cost, refund=True)
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       ability + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = int(game_update_string[2])
                        self.nullified_card_name = ability
                        self.cost_card_nullified = cost
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Regular Action"
                    elif ability == "Spawn Termagants":
                        for i in range(7):
                            if self.planets_in_play_array[i]:
                                primary_player.summon_token_at_planet("Termagant", i)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = "Normal"
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                    elif ability == "Test of Faith":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Putrescent Corpulence":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        primary_player.number_cards_to_search = 12
                        if primary_player.number_cards_to_search > len(primary_player.deck):
                            primary_player.number_cards_to_search = len(primary_player.deck)
                        self.choices_available = \
                            primary_player.deck[:primary_player.number_cards_to_search]
                        if self.choices_available:
                            self.choice_context = "Putrescent Corpulence 1"
                            self.misc_target_choice = ""
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                            self.action_chosen = ability
                    elif ability == "The Orgiastic Feast":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        primary_player.number_cards_to_search = 12
                        if primary_player.number_cards_to_search > len(primary_player.deck):
                            primary_player.number_cards_to_search = len(primary_player.deck)
                        self.choices_available = \
                            primary_player.deck[:primary_player.number_cards_to_search]
                        if self.choices_available:
                            self.choice_context = "The Orgiastic Feast Rally 1"
                            self.misc_target_choice = ""
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                            self.action_chosen = ability
                    elif ability == "Triumvirate of Ynnead":
                        self.action_chosen = "Triumvirate of Ynnead"
                        self.chosen_first_card = False
                        self.trium_count = 0
                        self.trium_tracker = ("name", -1)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                    elif ability == "Rakarth's Experimentations":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.choices_available = ["Army", "Support", "Attachment", "Event"]
                        self.choice_context = "Rakarth's Experimentations card type"
                        self.name_player_making_choices = primary_player.name_player
                    elif ability == "Final Expiration":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                    elif ability == "Medusae Pact":
                        self.chosen_first_card = False
                        primary_player.discard_card_from_hand(hand_pos)
                        self.action_chosen = ability
                        if len(primary_player.cards) < 6:
                            self.chosen_first_card = True
                            if len(secondary_player.cards) < 6:
                                primary_player.torture_event_played(ability)
                                await primary_player.dark_eldar_event_played()
                                self.action_cleanup()
                            else:
                                self.player_with_action = secondary_player.name_player
                                await self.send_update_message("Please discard down to 5 cards.")
                    elif ability == "Access to the Black Library":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.choices_available = []
                        for i in range(len(primary_player.deck)):
                            if primary_player.deck[i] not in self.choices_available:
                                self.choices_available.append(primary_player.deck[i])
                        if not self.choices_available or len(self.choices_available) == 1:
                            self.reset_choices_available()
                            self.action_cleanup()
                        else:
                            self.choice_context = "Access to the Black Library"
                            self.name_player_making_choices = primary_player.name_player
                            self.chosen_first_card = False
                            self.misc_target_choice = ""
                    elif ability == "Tempting Ceasefire":
                        if not primary_player.tempting_ceasefire_used:
                            primary_player.tempting_ceasefire_used = True
                            primary_player.discard_card_from_hand(hand_pos)
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.choices_available = ["1", "2", "3", "4", "5"]
                            self.choice_context = "Tempting Ceasefire Number"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                    elif ability == "Guerrilla Tactics":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.action_chosen = ability
                        self.chosen_first_card = False
                        self.misc_target_planet = -1
                    elif ability == "Breach and Clear":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                    elif ability == "Kwik' Konstruckshun":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                    elif ability == "Clash of Wings":
                        warlord_pla, _ = primary_player.get_location_of_warlord()
                        if warlord_pla != -2 and warlord_pla != -1:
                            for i in range(len(primary_player.cards_in_play[warlord_pla + 1])):
                                if primary_player.get_mobile_given_pos(warlord_pla, i):
                                    primary_player.cards_in_play[warlord_pla + 1][i].flying_eocr = True
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_cleanup()
                    elif ability == "Muster the Guard":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            primary_player.muster_the_guard_count += 1
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.action_cleanup()
                    elif ability == "Keep Firing!":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Consumed by the Kindred":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.action_chosen = ability
                        self.misc_target_unit = (-1, -1)
                        self.chosen_first_card = False
                    elif ability == "Supply Line Incursion":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "The Siege Masters":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Looted Skrap":
                        if primary_player.can_play_limited:
                            if self.last_planet_checked_for_battle != -1:
                                primary_player.can_play_limited = False
                                primary_player.looted_skrap_active = True
                                primary_player.looted_skrap_count = 3
                                primary_player.looted_skrap_planet = self.last_planet_checked_for_battle
                                primary_player.discard_card_from_hand(hand_pos)
                                self.action_cleanup()
                    elif ability == "The Bloodied Host":
                        if not primary_player.bloodied_host_used and self.last_planet_checked_for_battle != -1:
                            primary_player.bloodied_host_used = True
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.check_is_unit_at_pos(-2, i):
                                    primary_player.headquarters[i].health_eocr += 2
                            for i in range(7):
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    primary_player.cards_in_play[i + 1][j].health_eocr += 2
                            self.action_cleanup()
                        else:
                            primary_player.add_resources(1, refund=True)
                    elif ability == "Brutal Cunning":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.misc_counter = 0
                        self.misc_target_planet = -1
                        self.chosen_first_card = False
                        self.choices_available = ["1", "2"]
                        self.choice_context = "Brutal Cunning: amount of damage"
                        self.name_player_making_choices = primary_player.name_player
                    elif ability == "Lost in the Webway":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.misc_target_unit = (-1, -1)
                        self.chosen_first_card = False
                        self.choices_available = ["Harlequin", "Opponent"]
                        self.choice_context = "Lost in the Webway"
                        self.name_player_making_choices = primary_player.name_player
                    elif ability == "Theater of War":
                        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                        enemy_pla, enemy_pos = secondary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_pla, warlord_pos) and \
                                secondary_player.get_ready_given_pos(warlord_pla, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_pla, warlord_pos)
                            primary_player.discard_card_from_hand(hand_pos)
                            self.action_chosen = ability
                            await self.send_update_message("Choose planet.")
                        else:
                            primary_player.add_resources(1, refund=True)
                    elif ability == "Everlasting Rage":
                        if not primary_player.everlasting_rage_used:
                            primary_player.everlasting_rage_used = True
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.action_chosen = ability
                            self.choices_available = []
                            copies_khorne = primary_player.count_units_with_trait("Khorne")
                            if copies_khorne < 1:
                                self.action_cleanup()
                            else:
                                for i in range(copies_khorne):
                                    self.choices_available.append(str(i + 1))
                                self.choice_context = "Everlasting Rage: Amount"
                                self.name_player_making_choices = primary_player.name_player
                    elif ability == "Indiscriminate Bombing":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.action_chosen = ability
                        self.chosen_first_card = False
                        self.chosen_second_card = False
                    elif ability == "Daring Assault":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.action_chosen = ability
                        primary_player.draw_card()
                        self.chosen_first_card = False
                    elif ability == "Torturer of Worlds":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.chosen_first_card = False
                        self.misc_target_unit = (-1, -1)
                        self.action_chosen = ability
                    elif ability == "Our Last Stand":
                        if not primary_player.our_last_stand_used:
                            primary_player.our_last_stand_used = True
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            for i in range(len(primary_player.cards_in_play[self.round_number + 1])):
                                if primary_player.get_faction_given_pos(self.round_number, i) == "Astra Militarum":
                                    primary_player.increase_faith_given_pos(self.round_number, i, 1)
                            icons = secondary_player.get_icons_on_captured()
                            if icons[0] > 1:
                                if self.get_red_icon(self.round_number):
                                    primary_player.our_last_stand_bonus_active = True
                            if icons[1] > 1:
                                if self.get_blue_icon(self.round_number):
                                    primary_player.our_last_stand_bonus_active = True
                            if icons[2] > 1:
                                if self.get_green_icon(self.round_number):
                                    primary_player.our_last_stand_bonus_active = True
                            if primary_player.our_last_stand_bonus_active:
                                await self.send_update_message("Warlord has gained the additional damage reduction "
                                                               "bonus from Our Last Stand.")
                            self.action_cleanup()
                    elif ability == "Summary Execution":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if warlord_planet != -2:
                            self.action_chosen = ability
                            self.misc_target_planet = warlord_planet
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                    elif ability == "Eldritch Storm":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.misc_counter = [False, False, False, False, False, False, False]
                        for i in range(7):
                            if self.get_green_icon(i):
                                self.misc_counter[i] = True
                    elif ability == "Sudden Adaptation":
                        self.chosen_first_card = False
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.misc_counter = 0
                        self.misc_target_planet = -1
                    elif ability == "Seer's Exodus":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if warlord_planet != -2:
                            self.misc_target_planet = warlord_planet
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.action_chosen = ability
                    elif ability == "To Arms!":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Nurgling Bomb":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Blood For The Blood God!":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Inevitable Betrayal":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.misc_target_planet = -1
                    elif ability == "Imperial Blockade":
                        extra_cost = 0
                        for i in range(len(primary_player.discard)):
                            if primary_player.discard[i] == "Imperial Blockade":
                                extra_cost += 1
                        if primary_player.spend_resources(extra_cost):
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            primary_player.draw_card()
                            self.action_chosen = ability
                    elif ability == "Rok Bombardment":
                        if self.last_planet_checked_for_battle != -1:
                            secondary_player.rok_bombardment_active.append("Enemy")
                            if not self.get_red_icon(self.last_planet_checked_for_battle):
                                primary_player.rok_bombardment_active.append("Own")
                        else:
                            primary_player.add_resources(cost, refund=True)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_cleanup()
                    elif ability == "Behind Enemy Lines":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.chosen_first_card = False
                        self.chosen_second_card = False
                        self.action_chosen = ability
                    elif ability == "Mind War":
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        primary_player.aiming_reticle_color = "blue"
                        self.action_chosen = ability
                    elif ability == "Mont'ka Strike":
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        primary_player.aiming_reticle_color = "blue"
                        self.action_chosen = ability
                    elif ability == "No Surprises":
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        primary_player.aiming_reticle_color = "blue"
                        self.action_chosen = ability
                    elif ability == "Biomass Sacrifice":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Bond of Brotherhood":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Piercing Wail":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.misc_counter = primary_player.get_highest_cost_units()
                        await self.send_update_message("You many exhaust units with a "
                                                       "maximum cost of " + str(self.misc_counter))
                        self.chosen_first_card = False
                    elif ability == "Daemonic Incursion":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.resolving_search_box = True
                        self.what_to_do_with_searched_card = "DRAW"
                        self.traits_of_searched_card = "Daemon"
                        self.card_type_of_searched_card = "Army"
                        self.faction_of_searched_card = None
                        self.max_cost_of_searched_card = 99
                        self.all_conditions_searched_card_required = True
                        self.no_restrictions_on_chosen_card = False
                        primary_player.number_cards_to_search = 6
                        if len(primary_player.deck) > 5:
                            self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                        else:
                            self.cards_in_search_box = primary_player.deck[:len(primary_player.deck)]
                        self.name_player_who_is_searching = primary_player.name_player
                        self.number_who_is_searching = primary_player.number
                        self.action_cleanup()
                    elif ability == "A Thousand Cuts":
                        self.action_chosen = ability
                        primary_player.deck.append(primary_player.cards[hand_pos])
                        primary_player.remove_card_from_hand(hand_pos)
                    elif ability == "Overrun":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Eldritch Reaping":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.choices_available = ["0", "1", "2", "3", "4", "5"]
                        self.choice_context = "Eldritch Reaping: Enemy Announce"
                        self.name_player_making_choices = secondary_player.name_player
                        self.misc_target_choice = ""
                        self.action_chosen = ability
                    elif ability == "The Strength of the Enemy":
                        primary_player.discard_card_from_hand(hand_pos)
                        self.action_chosen = ability
                        self.chosen_first_card = False
                        await self.send_update_message("Please choose an enemy unit first.")
                    elif ability == "Rapid Evolution":
                        if primary_player.can_play_limited:
                            self.action_chosen = ability
                            primary_player.can_play_limited = True
                            self.misc_counter = [0, 0, 0]
                            primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Know No Fear":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            self.action_chosen = ability
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.misc_counter = 3
                            self.planets_free_for_know_no_fear = [True, True, True, True, True, True, True]
                            self.chosen_first_card = False
                    elif ability == "Rapid Assault":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.chosen_first_card = False
                        self.chosen_second_card = False
                        self.misc_counter = 0
                    elif ability == "Despise":
                        self.action_chosen = ability
                        primary_player.sacced_card_for_despise = False
                        secondary_player.sacced_card_for_despise = False
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        await self.send_update_message("Both players must sacrifice an Ally unit for Despise.")
                    elif ability == "Dakka Dakka Dakka!":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.headquarters[i].get_is_unit():
                                    primary_player.assign_damage_to_pos(-2, i, 1, by_enemy_unit=False)
                            for i in range(len(secondary_player.headquarters)):
                                if not secondary_player.get_immune_to_enemy_events(-2, i):
                                    if secondary_player.headquarters[i].get_is_unit():
                                        secondary_player.assign_damage_to_pos(-2, i, 1, by_enemy_unit=False)
                            for i in range(7):
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.cards_in_play[i + 1][j].get_is_unit():
                                        primary_player.assign_damage_to_pos(i, j, 1, by_enemy_unit=False)
                                for j in range(len(secondary_player.cards_in_play[i + 1])):
                                    if secondary_player.cards_in_play[i + 1][j].get_is_unit():
                                        if not secondary_player.get_immune_to_enemy_events(i, j):
                                            secondary_player.assign_damage_to_pos(i, j, 1, by_enemy_unit=False)
                            self.action_cleanup()
                    elif ability == "Battle Cry":
                        primary_player.increase_attack_of_all_units_in_play(2, required_faction="Orks",
                                                                            expiration="EOB")
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_cleanup()
                    elif ability == "Power from Pain":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                        self.player_with_action = secondary_player.name_player
                    elif ability == "Soul Seizure":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                        self.chosen_first_card = False
                        primary_player.soul_seizure_value = primary_player.count_tortures_in_discard()
                    elif ability == "Suppressive Fire":
                        self.chosen_first_card = False
                        self.chosen_second_card = False
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Death from Above":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Calculated Strike":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Kommando Cunning":
                        self.action_chosen = ability
                        self.chosen_first_card = False
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Painboy Surjery":
                        await self.send_update_message("For safety, you are required to click the "
                                                       "unit again after every instance of damage.")
                        self.misc_target_unit = (-1, -1)
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Noble Deed":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.chosen_first_card = False
                    elif ability == "Smash 'n Bash":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        primary_player.aiming_reticle_coords_hand = None
                        self.chosen_first_card = False
                    elif ability == "Fetid Haze":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        primary_player.aiming_reticle_coords_hand = None
                        self.chosen_first_card = False
                    elif ability == "Indescribable Horror":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Predation":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Doombolt":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Searing Brand":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Cacophonic Choir":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.action_cleanup()
                            self.location_of_indirect = "ALL"
                            self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
                            secondary_player.indirect_damage_applied = 0
                            secondary_player.total_indirect_damage = secondary_player.count_units_in_play_all()
                    elif ability == "Slake the Thirst":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.choices_available = ["Yourself", "Opponent"]
                            self.choice_context = "Which Player? (Slake the Thirst):"
                            self.name_player_making_choices = primary_player.name_player
                    elif ability == "Bolster the Defense":
                        highest_num = 0
                        for i in range(7):
                            current_count = 0
                            for j in range(len(primary_player.cards_in_play[i + 1])):
                                if primary_player.get_card_type_given_pos(i, j) == "Army":
                                    current_count += 1
                            if highest_num < current_count:
                                highest_num = current_count
                        self.misc_counter = highest_num
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Tense Negotiations":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if warlord_planet != -2:
                            if primary_player.get_ready_given_pos(warlord_planet, warlord_pos) and \
                                    self.planet_array[warlord_planet] != "Jaricho":
                                primary_player.discard_card_from_hand(int(game_update_string[2]))
                                primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                                self.action_cleanup()
                                self.need_to_resolve_battle_ability = True
                                self.battle_ability_to_resolve = self.planet_array[warlord_planet]
                                self.player_resolving_battle_ability = primary_player.name_player
                                self.number_resolving_battle_ability = str(primary_player.number)
                                self.choices_available = ["Yes", "No"]
                                self.choice_context = "Resolve Battle Ability?"
                                self.name_player_making_choices = primary_player.name_player
                                self.tense_negotiations_active = True
                    elif ability == "Clogged with Corpses":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.misc_counter = 0
                    elif ability == "Reanimation Protocol":
                        if not primary_player.used_reanimation_protocol:
                            primary_player.used_reanimation_protocol = True
                            self.action_chosen = ability
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Mechanical Enhancement":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Extermination":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Recycle":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.misc_counter = 0
                    elif ability == "Ecstatic Seizures":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Awake the Sleepers":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.name_player_making_choices = primary_player.name_player
                        self.choices_available = []
                        self.choice_context = "Awake the Sleepers"
                        for i in range(len(primary_player.discard)):
                            card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                                      self.apoka_errata_cards, self.cards_that_have_errata)
                            if card.get_faction() == "Necrons":
                                self.choices_available.append(card.get_name())
                        self.resolving_search_box = True
                        if not self.choices_available:
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            if not primary_player.harbinger_of_eternity_active:
                                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                                primary_player.aiming_reticle_coords_hand = None
                            await self.send_update_message(
                                "No valid targets for Awake the Sleepers"
                            )
                            self.action_cleanup()
                        else:
                            await self.send_update_message(
                                "Press the pass button to stop shuffling any more cards in."
                            )
                    elif ability == "Drudgery":
                        if primary_player.can_play_limited:
                            primary_player.can_play_limited = False
                            self.action_chosen = ability
                            primary_player.discard_card_from_hand(hand_pos)
                            self.chosen_first_card = False
                        else:
                            primary_player.add_resources(2, refund=True)
                            await self.send_update_message("Already played a Limited card!")
                    elif ability == "Dark Possession":
                        primary_player.dark_possession_active = True
                        primary_player.discard_card_from_hand(hand_pos)
                        self.action_cleanup()
                        await primary_player.dark_eldar_event_played()
                        primary_player.torture_event_played()
                    elif ability == "Sudden Reinforcements":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Blessing of Mork":
                        if self.last_planet_checked_for_battle != -1:
                            primary_player.discard_card_from_hand(hand_pos)
                            primary_player.mork_blessings_count += 1
                            self.action_cleanup()
                    elif ability == "Mob Up!":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                        snotlings_total = 0
                        for i in range(len(primary_player.headquarters)):
                            if primary_player.get_ability_given_pos(-2, i) == "Snotlings":
                                if primary_player.get_ready_given_pos(-2, i):
                                    primary_player.exhaust_given_pos(-2, i, card_effect=True)
                                    snotlings_total += 1
                        for i in range(7):
                            for j in range(len(primary_player.cards_in_play[i + 1])):
                                if primary_player.get_ability_given_pos(i, j) == "Snotlings":
                                    if primary_player.get_ready_given_pos(i, j):
                                        primary_player.exhaust_given_pos(i, j, card_effect=True)
                                        snotlings_total += 1
                        self.misc_counter = snotlings_total
                    elif ability == "Unending Barrage":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                        self.misc_counter = 0
                        self.chosen_first_card = False
                    elif ability == "Lucky Shot":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Hate":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Omnissiah's Blessing":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Squiggify":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Subdual":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Path of the Leader":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.choices_available = ["Gain 1 Resource", "+1 ATK Warrior", "Move Psyker"]
                        self.choice_context = "Path of the Leader choice"
                        self.name_player_making_choices = primary_player.name_player
                    elif ability == "The Emperor's Warrant":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.chosen_first_card = False
                        self.misc_target_planet = -1
                        self.misc_counter = -1
                    elif ability == "Sowing Chaos":
                        for i in range(7):
                            if self.get_blue_icon(i):
                                j = 0
                                while j < len(primary_player.cards_in_play[i + 1]):
                                    if primary_player.get_card_type_given_pos(i, j) == "Army":
                                        if primary_player.get_cost_given_pos(i, j) < 3:
                                            primary_player.destroy_card_in_play(i, j)
                                            j = j - 1
                                    j = j + 1
                                j = 0
                                while j < len(secondary_player.cards_in_play[i + 1]):
                                    if secondary_player.get_card_type_given_pos(i, j) == "Army":
                                        if secondary_player.get_cost_given_pos(i, j) < 3:
                                            if not secondary_player.get_immune_to_enemy_events(i, j):
                                                if secondary_player.get_ability_given_pos(
                                                        i, j) == "Flayed Ones Revenants":
                                                    self.create_reaction("Flayed Ones Revenants",
                                                                         secondary_player.name_player,
                                                                         (int(secondary_player.number), i, -1))
                                                secondary_player.destroy_card_in_play(i, j)
                                                j = j - 1
                                    j = j + 1
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_cleanup()
                    elif ability == "Accelerated Gestation":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Ominous Wind":
                        self.misc_counter = primary_player.get_highest_cost_units()
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        for _ in range(self.misc_counter):
                            primary_player.draw_card()
                        self.misc_counter = 4
                        self.action_chosen = ability
                        await self.send_update_message("4 cards left to discard")
                    elif ability == "Repent!":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.misc_counter = primary_player.get_highest_cost_units()
                        self.action_chosen = ability
                        self.chosen_first_card = False
                        self.misc_target_unit = (-1, -1)
                    elif ability == "Vivisection":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "For the Tau'va":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.headquarters[i].get_attachments():
                                    primary_player.ready_given_pos(-2, i)
                            for i in range(7):
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.cards_in_play[i + 1][j].get_attachments():
                                        primary_player.ready_given_pos(i, j)
                            self.action_cleanup()
                    elif ability == "Consumption":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.resolving_consumption = True
                        primary_player.consumption_sacs_list = self.planets_in_play_array
                        secondary_player.consumption_sacs_list = self.planets_in_play_array
                    elif ability == "Spore Burst":
                        any_infested = False
                        for i in range(len(self.infested_planets)):
                            if self.infested_planets and self.planets_in_play_array:
                                any_infested = True
                        if any_infested:
                            self.chosen_first_card = False
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.action_chosen = ability
                        else:
                            primary_player.add_resources(2, refund=True)
                            await self.send_update_message(
                                "No valid planets for spore burst."
                            )
                    elif ability == "Ferocious Strength":
                        if self.phase == "COMBAT":
                            self.action_chosen = ability
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        else:
                            primary_player.add_resources(cost, refund=True)
                    elif ability == "Dark Cunning":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Kauyon Strike":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.chosen_first_card = False
                        self.khymera_to_move_positions = []
                    elif ability == "Ethereal Wisdom":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Even the Odds":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.chosen_second_card = False
                        self.chosen_first_card = False
                        self.misc_target_attachment = (-1, -1, -1)
                        self.misc_player_storage = ""
                    elif ability == "Squig Bombin'":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Archon's Terror":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Drop Pod Assault":
                        if self.last_planet_checked_for_battle != -1:
                            self.action_chosen = ability
                            self.choice_context = ability
                            primary_player.discard_card_from_hand(hand_pos)
                            primary_player.number_cards_to_search = 6
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                                    if primary_player.headquarters[i].counter > 0:
                                        primary_player.number_cards_to_search += 2
                            self.resolving_search_box = True
                            if primary_player.number_cards_to_search > len(primary_player.deck):
                                primary_player.number_cards_to_search = len(primary_player.deck)
                            self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = str(primary_player.number)
                            self.what_to_do_with_searched_card = "PLAY TO BATTLE"
                            self.traits_of_searched_card = None
                            self.card_type_of_searched_card = "Army"
                            self.faction_of_searched_card = "Space Marines"
                            self.max_cost_of_searched_card = 3
                            self.all_conditions_searched_card_required = True
                            self.no_restrictions_on_chosen_card = False
                        else:
                            primary_player.add_resources(cost, refund=True)
                            await self.send_update_message("No battle taking place")
                    elif ability == "Squadron Redeployment":
                        self.action_chosen = "Squadron Redeployment"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Warpstorm":
                        self.action_chosen = "Warpstorm"
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Tzeentch's Firestorm":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.choices_available = []
                        for i in range(primary_player.resources + 1):
                            self.choices_available.append(str(i))
                        self.name_player_making_choices = primary_player.name_player
                        self.choice_context = "Amount to spend for Tzeentch's Firestorm:"
                        self.amount_spend_for_tzeentch_firestorm = -1
                    elif ability == "Infernal Gateway":
                        self.action_chosen = "Infernal Gateway"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Promise of Glory":
                        print("Resolve Promise of Glory")
                        primary_player.summon_token_at_hq("Cultist", amount=2)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                    elif ability == "Calamity":
                        i = 0
                        while i < len(primary_player.headquarters):
                            if primary_player.get_card_type_given_pos(-2, i) == "Army":
                                if primary_player.get_cost_given_pos(-2, i) < 3:
                                    primary_player.return_card_to_hand(-2, i)
                                    i = i - 1
                            i += 1
                        i = 0
                        while i < len(secondary_player.headquarters):
                            if secondary_player.get_card_type_given_pos(-2, i) == "Army":
                                if not secondary_player.get_immune_to_enemy_events(-2, i):
                                    if secondary_player.get_cost_given_pos(-2, i) < 3:
                                        secondary_player.return_card_to_hand(-2, i)
                                        i = i - 1
                            i += 1
                        for planet_pos in range(7):
                            i = 0
                            while i < len(primary_player.cards_in_play[planet_pos + 1]):
                                if primary_player.get_card_type_given_pos(planet_pos, i) == "Army":
                                    if primary_player.get_cost_given_pos(planet_pos, i) < 3:
                                        primary_player.return_card_to_hand(planet_pos, i)
                                        i = i - 1
                                i += 1
                            i = 0
                            while i < len(secondary_player.cards_in_play[planet_pos + 1]):
                                if secondary_player.get_card_type_given_pos(planet_pos, i) == "Army":
                                    if not secondary_player.get_immune_to_enemy_events(planet_pos, i):
                                        if secondary_player.get_cost_given_pos(planet_pos, i) < 3:
                                            secondary_player.return_card_to_hand(planet_pos, i)
                                            i = i - 1
                                i += 1
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_cleanup()
                    elif ability == "Doom":
                        print("Resolve Doom")
                        primary_player.destroy_all_cards_in_hq(ignore_uniques=True, units_only=True, enemy_event=False)
                        secondary_player.destroy_all_cards_in_hq(ignore_uniques=True, units_only=True, enemy_event=True)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_cleanup()
                    elif ability == "Warp Rift":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.chosen_first_card = False
                        self.misc_target_planet = -1
                    elif ability == "Pact of the Haemonculi":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Empower":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Gift of Isha":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Deception":
                        self.action_chosen = "Deception"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Rally the Charge":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Exterminatus":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Snotling Attack":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.misc_counter = 4
                    elif ability == "Preemptive Barrage":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                        self.misc_target_planet = -1
                        self.misc_counter = 3
                    elif ability == "Core Destabilization":
                        self.action_chosen = ability
                        primary_player.discard_card_from_hand(hand_pos)
                    elif ability == "Promise of Glory":
                        print("Resolve Promise of Glory")
                        primary_player.summon_token_at_hq("Cultist", amount=2)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                    elif ability == "Raid":
                        if primary_player.can_play_limited:
                            if primary_player.resources < secondary_player.resources:
                                if secondary_player.spend_resources(1):
                                    primary_player.add_resources(1)
                                    primary_player.can_play_limited = False
                                    primary_player.discard_card_from_hand(int(game_update_string[2]))
                                    self.mode = self.stored_mode
                                    self.player_with_action = ""
                                    self.player_with_deploy_turn = secondary_player.name_player
                                    self.number_with_deploy_turn = secondary_player.number
                                    await primary_player.dark_eldar_event_played()
                    elif ability == "Planet Absorption":
                        if primary_player.planet_absorption_played or secondary_player.planet_absorption_played:
                            await self.send_update_message(
                                "----GAME END----"
                                "Victory for " + secondary_player.name_player + "; "
                                + primary_player.name_player + " played a second Planet Absorption."
                                "----GAME END----"
                            )
                            await self.send_victory_proper(secondary_player.name_player, "Planet Absorption")
                        primary_player.draw_card()
                        primary_player.draw_card()
                        primary_player.draw_card()
                        primary_player.add_resources(3)
                        primary_player.discard_card_from_hand(hand_pos)
                        if primary_player.victory_display:
                            self.choices_available = []
                            self.name_player_making_choices = primary_player.name_player
                            self.choice_context = "Absorb a planet:"
                            self.resolving_search_box = True
                            for i in range(len(primary_player.victory_display)):
                                self.choices_available.append(primary_player.victory_display[i].get_name())
                        self.action_cleanup()
                    elif ability == "Reinforced Synaptic Network":
                        primary_player.discard_card_from_hand(hand_pos)
                        primary_player.reinforced_synaptic_network_played = True
                        self.choices_available = copy.copy(primary_player.allowed_units_rsn)
                        self.choice_context = "Select new synapse (RSN):"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                        self.action_cleanup()
                    elif ability == "Visions of Agony":
                        if secondary_player.cards:
                            interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                            if interrupts:
                                await self.send_update_message("Some sort of interrupt may be used.")
                                self.choices_available = interrupts
                                self.choices_available.insert(0, "No Interrupt")
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Interrupt Enemy Discard Effect?"
                                self.resolving_search_box = True
                                self.stored_discard_and_target.append((ability, primary_player.number))
                            else:
                                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                                primary_player.aiming_reticle_coords_hand = None
                                self.choices_available = secondary_player.cards
                                self.choice_context = "Visions of Agony Discard:"
                                self.name_player_making_choices = primary_player.name_player
                                self.resolving_search_box = True
                        else:
                            primary_player.add_resources(cost, refund=True)
                            await self.send_update_message("No cards to look at with Visions of Agony")
                    else:
                        primary_player.add_resources(cost, refund=True)
                        await self.send_update_message(card.get_name() + " not "
                                                                         "implemented")
    elif self.action_chosen == "Ambush Platform":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is None:
            card = FindCard.find_card(primary_player.cards[int(game_update_string[2])], self.card_array,
                                      self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            if card.get_card_type() == "Attachment" or card.get_ability() == "Gun Drones" or \
                    card.get_ability() == "Shadowsun's Stealth Cadre" or \
                    card.get_ability() == "Escort Drone":
                if not card.get_limited() or primary_player.can_play_limited:
                    primary_player.aiming_reticle_coords_hand_2 = int(game_update_string[2])
                    primary_player.aiming_reticle_color = "blue"
        else:
            await self.send_update_message("already chosen a valid attachment for ambush platform")
    elif self.action_chosen == "Starblaze's Outpost":
        if self.chosen_first_card:
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.get_card_type() == "Army":
                if card.get_faction() == "Tau":
                    if card.get_cost() <= self.misc_counter:
                        primary_player.add_card_to_planet(card, self.misc_target_planet)
                        primary_player.remove_card_from_hand(int(game_update_string[2]))
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.action_cleanup()
    elif self.action_chosen == "Medusae Pact":
        primary_player.discard_card_from_hand(hand_pos)
        if len(primary_player.cards) < 6:
            if not self.chosen_first_card:
                self.chosen_first_card = True
                if len(secondary_player.cards) > 5:
                    self.player_with_action = secondary_player.name_player
                    await self.send_update_message("Please discard down to 5 cards.")
                else:
                    await primary_player.dark_eldar_event_played()
                    primary_player.torture_event_played(self.action_chosen)
                    self.action_cleanup()
            else:
                await secondary_player.dark_eldar_event_played()
                secondary_player.torture_event_played(self.action_chosen)
                self.action_cleanup()
    elif self.action_chosen == "Rapid Evolution":
        if card.get_card_type() == "Army":
            if self.misc_counter[0] < 2:
                self.misc_counter[0] = self.misc_counter[0] + 1
                primary_player.discard_card_from_hand(hand_pos)
                self.action_chosen = "Rapid Evolution Termagant"
                await self.send_update_message("Please choose a planet to place a Termagant")
        elif card.get_card_type() == "Attachment":
            if self.misc_counter[1] < 2:
                self.misc_counter[1] = self.misc_counter[1] + 1
                primary_player.discard_card_from_hand(hand_pos)
                primary_player.draw_card()
        elif card.get_card_type() == "Support":
            if self.misc_counter[2] < 2:
                self.misc_counter[2] = self.misc_counter[2] + 1
                primary_player.discard_card_from_hand(hand_pos)
                primary_player.add_resources(1)
    elif self.action_chosen == "Dread Command Barge":
        if not self.chosen_first_card:
            if card.get_faction() != "Necrons":
                primary_player.discard_card_from_hand(int(game_update_string[2]))
                self.chosen_first_card = True
    elif self.action_chosen == "Saint Celestine":
        if not self.chosen_first_card:
            if card.get_is_unit() and not card.check_for_a_trait("Elite"):
                primary_player.aiming_reticle_coords_hand = hand_pos
                primary_player.aiming_reticle_color = "blue"
                self.chosen_first_card = True
                self.misc_counter = card.get_cost()
                if self.misc_counter < 1:
                    target_planet = self.position_of_actioned_card[0]
                    del primary_player.cards[hand_pos]
                    primary_player.add_card_to_planet(card, target_planet)
                    primary_player.aiming_reticle_coords_hand = None
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0], self.position_of_actioned_card[1])
                    self.action_cleanup()
                else:
                    await self.send_update_message("Please pay " + str(self.misc_counter) + " faith.")
    elif self.action_chosen == "Rapid Assault":
        if not self.chosen_first_card:
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.get_card_type() == "Army" and card.check_for_a_trait("Kabalite", primary_player.etekh_trait):
                if card.get_cost() < 4:
                    self.chosen_first_card = True
                    primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
    elif self.action_chosen == "Canoptek Spyder":
        if not self.chosen_first_card:
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.get_card_type() == "Army":
                primary_player.discard_card_from_hand(int(game_update_string[2]))
                self.chosen_first_card = True
    elif self.action_chosen == "Guerrilla Tactics Discard":
        primary_player.discard_card_from_hand(hand_pos)
        self.misc_counter = self.misc_counter - 1
        if self.misc_counter < 1:
            self.action_chosen = "Guerrilla Tactics Move"
            self.chosen_first_card = False
            self.misc_target_unit = (-1, -1)
            self.player_with_action = secondary_player.name_player
    elif self.action_chosen == "Twisted Wracks":
        card = FindCard.find_card(primary_player.cards[int(game_update_string[2])], self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)
        if card.check_for_a_trait("Torture"):
            primary_player.discard_card_from_hand(int(game_update_string[2]))
            planet_pos, unit_pos = self.position_of_actioned_card
            primary_player.ready_given_pos(planet_pos, unit_pos)
            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
            self.action_cleanup()
    elif self.action_chosen == "Cenobyte Servitor":
        if not self.chosen_first_card:
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.get_card_type() == "Attachment" and card.check_for_a_trait("Relic"):
                self.chosen_first_card = True
                primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                primary_player.aiming_reticle_color = "blue"
    elif self.action_chosen == "Sudden Adaptation":
        if self.chosen_first_card:
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.get_cost() <= self.misc_counter and card.get_card_type() == "Army":
                if card.get_faction() == "Tyranids" and self.misc_target_choice != card.get_name():
                    primary_player.add_card_to_planet(card, self.misc_target_planet)
                    primary_player.remove_card_from_hand(int(game_update_string[2]))
                    self.action_cleanup()
    elif self.action_chosen == "Merciless Reclamation":
        if not self.chosen_first_card:
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.get_card_type() == "Army" and card.get_faction() == "Necrons":
                if card.check_for_a_trait("Soldier", primary_player.etekh_trait) or \
                        card.check_for_a_trait("Warrior", primary_player.etekh_trait):
                    self.misc_counter = card.get_cost()
                    primary_player.discard_card_from_hand(hand_pos)
                    self.chosen_first_card = True
    elif self.action_chosen == "Abomination Workshop":
        primary_player.discard_card_from_hand(hand_pos)
        if self.misc_counter >= len(primary_player.cards):
            if self.chosen_first_card:
                self.player_with_action = primary_player.name_player
                self.action_cleanup()
            self.chosen_first_card = True
            self.player_with_action = secondary_player.name_player
            self.misc_counter = secondary_player.get_highest_cost_units()
            if self.misc_counter >= len(secondary_player.cards):
                self.player_with_action = primary_player.name_player
                self.action_cleanup()
    elif self.action_chosen == "Talyesin's Warlocks":
        card = primary_player.get_card_in_hand(int(game_update_string[2]))
        if card.check_for_a_trait("Warrior", primary_player.etekh_trait):
            primary_player.discard_card_from_hand(int(game_update_string[2]))
            planet_pos, unit_pos = self.position_of_actioned_card
            primary_player.ready_given_pos(planet_pos, unit_pos)
            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
            self.mask_jain_zar_check_actions(primary_player, secondary_player)
            self.action_cleanup()
    elif self.action_chosen == "Behind Enemy Lines":
        card = primary_player.get_card_in_hand(int(game_update_string[2]))
        if card.get_is_unit():
            self.chosen_first_card = True
            self.card_pos_to_deploy = int(game_update_string[2])
            self.faction_of_card_to_play = card.get_faction()
            self.name_of_card_to_play = card.get_name()
            self.traits_of_card_to_play = card.get_traits()
            primary_player.aiming_reticle_color = "blue"
            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
            self.card_type_of_selected_card_in_hand = "Army"
    elif self.action_chosen == "Staging Ground":
        card = primary_player.get_card_in_hand(int(game_update_string[2]))
        if card.get_is_unit():
            if card.get_cost() < 3:
                self.chosen_first_card = True
                self.card_pos_to_deploy = int(game_update_string[2])
                self.faction_of_card_to_play = card.get_faction()
                self.name_of_card_to_play = card.get_name()
                self.traits_of_card_to_play = card.get_traits()
                primary_player.aiming_reticle_color = "blue"
                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                self.card_type_of_selected_card_in_hand = "Army"
    elif self.action_chosen == "Launch Pads":
        card = primary_player.get_card_in_hand(int(game_update_string[2]))
        if card.get_is_unit():
            if card.get_cost() == 3 and card.get_faction() == "Space Marines":
                self.chosen_first_card = True
                self.card_pos_to_deploy = int(game_update_string[2])
                self.faction_of_card_to_play = card.get_faction()
                self.name_of_card_to_play = card.get_name()
                self.traits_of_card_to_play = card.get_traits()
                primary_player.aiming_reticle_color = "blue"
                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                self.card_type_of_selected_card_in_hand = "Army"
    elif self.action_chosen == "Kwik' Konstruckshun":
        card = primary_player.get_card_in_hand(hand_pos)
        if card.get_card_type() == "Support" and card.get_cost() < 4:
            if primary_player.add_to_hq(card):
                primary_player.remove_card_from_hand(hand_pos)
                last_el_index = len(primary_player.headquarters) - 1
                primary_player.headquarters[last_el_index].quick_construct = True
                self.action_cleanup()
    elif self.action_chosen == "Crypt of Saint Camila":
        if not self.chosen_first_card:
            card = primary_player.get_card_in_hand(hand_pos)
            if not card.check_for_a_trait("Elite") and card.get_faction() == "Space Marines":
                if card.get_card_type() == "Army":
                    self.chosen_first_card = True
                    primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    primary_player.aiming_reticle_color = "blue"
    elif self.action_chosen == "Slumbering Tomb":
        primary_player.discard_card_from_hand(int(game_update_string[2]))
        self.misc_counter += 1
        if self.misc_counter >= 2:
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            self.action_cleanup()
    elif self.action_chosen == "Death from Above":
        if card.get_is_unit():
            if card.get_mobile() and not card.check_for_a_trait("Elite"):
                last_planet = self.determine_last_planet()
                primary_player.add_card_to_planet(card, last_planet)
                primary_player.remove_card_from_hand(int(game_update_string[2]))
                if int(game_update_string[2]) < primary_player.aiming_reticle_coords_hand:
                    primary_player.aiming_reticle_coords_hand -= 1
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Biomass Sacrifice":
        if card.get_is_unit():
            primary_player.discard_card_from_hand(int(game_update_string[2]))
            primary_player.add_resources(1)
    elif self.action_chosen == "Veteran Brother Maxos":
        if card.get_is_unit() and card.get_faction() == "Space Marines":
            if primary_player.spend_resources(card.get_cost()):
                if primary_player.add_card_to_planet(card, self.position_of_actioned_card[0]) != -1:
                    primary_player.remove_card_from_hand(int(game_update_string[2]))
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
                    self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Hyperphase Sword":
        if not self.chosen_first_card:
            primary_player.discard_card_from_hand(int(game_update_string[2]))
            self.chosen_first_card = True
    elif self.action_chosen == "Bolster the Defense":
        card = primary_player.get_card_in_hand(int(game_update_string[2]))
        if card.get_card_type() == "Support" and card.get_cost() <= self.misc_counter:
            primary_player.add_to_hq(card)
            primary_player.remove_card_from_hand(int(game_update_string[2]))
            self.action_cleanup()
    elif self.action_chosen == "Ominous Wind":
        primary_player.discard_card_from_hand(int(game_update_string[2]))
        self.misc_counter = self.misc_counter - 1
        if self.misc_counter > 0:
            await self.send_update_message(str(self.misc_counter) + " cards left to discard")
        else:
            self.action_cleanup()
    elif self.action_chosen == "Recycle":
        if primary_player.aiming_reticle_coords_hand != int(game_update_string[2]):
            primary_player.discard_card_from_hand(int(game_update_string[2]))
            if primary_player.aiming_reticle_coords_hand is not None:
                if primary_player.aiming_reticle_coords_hand > int(game_update_string[2]):
                    primary_player.aiming_reticle_coords_hand -= 1
            self.misc_counter += 1
            if self.misc_counter > 1:
                if not primary_player.harbinger_of_eternity_active:
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                for _ in range(3):
                    primary_player.draw_card()
                self.action_cleanup()
    elif self.action_chosen == "Infernal Gateway":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is None:
            card = FindCard.find_card(primary_player.cards[int(game_update_string[2])], self.card_array,
                                      self.cards_dict, self.apoka_errata_cards, self.cards_that_have_errata)
            if card.get_is_unit():
                if card.get_faction() == "Chaos":
                    if card.get_cost() <= 3:
                        primary_player.aiming_reticle_coords_hand_2 = int(game_update_string[2])
                        primary_player.aiming_reticle_color = "blue"
        else:
            await self.send_update_message("already chosen a valid unit for infernal gateway")
