from .. import FindCard


async def update_game_event_action_hand(self, name, game_update_string, may_nullify=True):
    if self.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    card = primary_player.get_card_in_hand(int(game_update_string[2]))
    ability = card.get_ability()
    print(card.get_allowed_phases_while_in_hand(), self.phase)
    print(card.get_has_action_while_in_hand())
    if not self.action_chosen:
        self.card_pos_to_deploy = int(game_update_string[2])
        if card.get_has_action_while_in_hand():
            if card.get_allowed_phases_while_in_hand() == self.phase or \
                    card.get_allowed_phases_while_in_hand() == "ALL":
                if primary_player.get_ambush_of_card(card):
                    self.card_pos_to_deploy = int(game_update_string[2])
                    self.action_chosen = "Ambush"
                    self.card_to_deploy = card
                    primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                    primary_player.aiming_reticle_color = "blue"
                elif primary_player.spend_resources(card.get_cost()):
                    if may_nullify and secondary_player.nullify_check():
                        primary_player.add_resources(card.get_cost())
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       ability + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = int(game_update_string[2])
                        self.nullified_card_name = ability
                        self.cost_card_nullified = card.get_cost()
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
                    elif ability == "Muster the Guard":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            primary_player.muster_the_guard_count += 1
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.action_cleanup()
                    elif ability == "To Arms!":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Nurgling Bomb":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.action_chosen = ability
                    elif ability == "Know No Fear":
                        warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_planet, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
                            self.action_chosen = ability
                            primary_player.discard_card_from_hand(int(game_update_string[2]))
                            self.misc_counter = 3
                            self.planets_free_for_know_no_fear = [True, True, True, True, True, True, True]
                            self.chosen_first_card = False
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
                                    primary_player.assign_damage_to_pos(-2, i, 1)
                            for i in range(len(secondary_player.headquarters)):
                                if not secondary_player.get_immune_to_enemy_events(-2, i):
                                    if secondary_player.headquarters[i].get_is_unit():
                                        secondary_player.assign_damage_to_pos(-2, i, 1)
                            for i in range(7):
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.cards_in_play[i + 1][j].get_is_unit():
                                        primary_player.assign_damage_to_pos(i, j, 1)
                                for j in range(len(secondary_player.cards_in_play[i + 1])):
                                    if secondary_player.cards_in_play[i + 1][j].get_is_unit():
                                        if not secondary_player.get_immune_to_enemy_events(i, j):
                                            secondary_player.assign_damage_to_pos(i, j, 1)
                            self.action_cleanup()
                    elif ability == "Battle Cry":
                        print("Resolve Battle Cry")
                        primary_player.increase_attack_of_all_units_in_play(2, required_faction="Orks",
                                                                            expiration="EOB")
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = "Normal"
                        self.player_with_action = ""
                    elif ability == "Power from Pain":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.reactions_needing_resolving.append(ability)
                        self.player_who_resolves_reaction.append(secondary_player.name_player)
                        self.positions_of_unit_triggering_reaction.append((int(secondary_player.get_number()),
                                                                           -1, -1))
                        self.mode = "Normal"
                        self.player_with_action = ""
                    elif ability == "Soul Seizure":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
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
                            card = FindCard.find_card(primary_player.discard[i], self.card_array)
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
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                            self.name_player_making_choices = primary_player.name_player
                            self.choices_available = []
                            self.choice_context = ability
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                                if card.get_is_unit() and card.get_faction() != "Necrons" and card.get_cost() < 4:
                                    self.choices_available.append(card.get_name())
                            self.resolving_search_box = True
                            if not self.choices_available:
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                                self.resolving_search_box = False
                                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                                primary_player.aiming_reticle_coords_hand = None
                                await self.send_update_message(
                                    "No valid targets for Drudgery"
                                )
                                self.action_cleanup()
                    elif ability == "Dark Possession":
                        self.action_chosen = ""
                        self.name_player_with_action = ""
                        self.mode = "Normal"
                        primary_player.dark_possession_active = True
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        if self.phase == "DEPLOY":
                            self.player_with_deploy_turn = secondary_player.name_player
                            self.number_with_deploy_turn = secondary_player.number
                        await primary_player.dark_eldar_event_played()
                        primary_player.torture_event_played()
                    elif ability == "Hate":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Subdual":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
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
                            choices = []
                            for i in range(len(primary_player.discard)):
                                c = FindCard.find_card(primary_player.discard[i], primary_player.card_array)
                                if c.get_cost() < 4 and c.get_card_type() == "Army":
                                    choices.append(c.get_name())
                            if choices:
                                self.action_chosen = ability
                                primary_player.aiming_reticle_color = "blue"
                                primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                                self.choices_available = choices
                                self.choice_context = "Spore Burst"
                                self.name_player_making_choices = primary_player.name_player
                            else:
                                primary_player.add_resources(2)
                                await self.send_update_message(
                                    "No valid targets in discard for spore burst."
                                )
                        else:
                            primary_player.add_resources(2)
                            await self.send_update_message(
                                "No valid planets for spore burst."
                            )
                    elif ability == "Ferocious Strength":
                        if self.phase == "COMBAT":
                            self.action_chosen = ability
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        else:
                            primary_player.add_resources(card.get_cost())
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
                            self.action_chosen = "Drop Pod Assault"
                            self.choice_context = "Drop Pod Assault"
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                            primary_player.number_cards_to_search = 6
                            self.resolving.search_box = True
                            if len(primary_player.deck) >= primary_player.number_cards_to_search:
                                self.cards_in_search_box = primary_player.deck[0:primary_player.number_cards_to_search]
                            else:
                                self.cards_in_search_box = primary_player.deck[0:primary_player.deck]
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
                            primary_player.add_resources(card.get_cost())
                            await self.send_update_message("No battle taking place")
                    elif ability == "Squadron Redeployment":
                        self.action_chosen = "Squadron Redeployment"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Warpstorm":
                        print("Resolve Warpstorm")
                        self.action_chosen = "Warpstorm"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
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
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
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
                        print("Resolve Exterminatus")
                        self.action_chosen = "Exterminatus"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif ability == "Snotling Attack":
                        print("Resolve Snotling Attack")
                        self.action_chosen = "Snotling Attack"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.misc_counter = 4
                    elif ability == "Preemptive Barrage":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.misc_target_planet = -1
                        self.misc_counter = 3
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
                    elif ability == "Visions of Agony":
                        if secondary_player.cards:
                            self.choices_available = secondary_player.cards
                            self.choice_context = "Visions of Agony Discard:"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                            self.name_player_making_choices = primary_player.name_player
                        else:
                            primary_player.add_resources(card.get_cost())
                            await self.send_update_message("No cards to look at with Visions of Agony")
                    else:
                        primary_player.add_resources(card.get_cost())
                        await self.send_update_message(card.get_name() + " not "
                                                                         "implemented")
    elif self.action_chosen == "Ambush Platform":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is None:
            card = FindCard.find_card(primary_player.cards[int(game_update_string[2])], self.card_array)
            if card.get_card_type() == "Attachment" or card.get_ability() == "Gun Drones" or \
                    card.get_ability() == "Shadowsun's Stealth Cadre":
                if not card.get_limited() or primary_player.can_play_limited:
                    primary_player.aiming_reticle_coords_hand_2 = int(game_update_string[2])
                    primary_player.aiming_reticle_color = "blue"
        else:
            await self.send_update_message("already chosen a valid attachment for ambush platform")
    elif self.action_chosen == "Canoptek Spyder":
        if not self.chosen_first_card:
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.get_card_type() == "Army":
                primary_player.discard_card_from_hand(int(game_update_string[2]))
                self.chosen_first_card = True
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
    elif self.action_chosen == "Slumbering Tomb":
        primary_player.discard_card_from_hand(int(game_update_string[2]))
        self.misc_counter += 1
        if self.misc_counter >= 2:
            self.action_cleanup()
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
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
    elif self.action_chosen == "Recycle":
        if primary_player.aiming_reticle_coords_hand != int(game_update_string[2]):
            primary_player.discard_card_from_hand(int(game_update_string[2]))
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
            card = FindCard.find_card(primary_player.cards[int(game_update_string[2])], self.card_array)
            if card.get_is_unit():
                if card.get_faction() == "Chaos":
                    if card.get_cost() <= 3:
                        primary_player.aiming_reticle_coords_hand_2 = int(game_update_string[2])
                        primary_player.aiming_reticle_color = "blue"
        else:
            await self.send_update_message("already chosen a valid unit for infernal gateway")
