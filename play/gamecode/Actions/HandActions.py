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
                    primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                    primary_player.aiming_reticle_color = "blue"
                    await primary_player.send_hand()
                elif primary_player.spend_resources(card.get_cost()):
                    if may_nullify and secondary_player.nullify_check():
                        primary_player.add_resources(card.get_cost())
                        await self.game_sockets[0].receive_game_update(primary_player.name_player + " wants to play " +
                                                                       ability + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = int(game_update_string[2])
                        self.nullified_card_name = ability
                        self.cost_card_nullified = card.get_cost()
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Regular Action"
                        await self.send_search()
                    elif ability == "Spawn Termagants":
                        for i in range(7):
                            if self.planets_in_play_array[i]:
                                primary_player.summon_token_at_planet("Termagant", i)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = "Normal"
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                        await primary_player.send_units_at_all_planets()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await primary_player.send_resources()
                    elif ability == "Battle Cry":
                        print("Resolve Battle Cry")
                        primary_player.increase_attack_of_all_units_in_play(2, required_faction="Orks",
                                                                            expiration="EOB")
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = "Normal"
                        self.player_with_action = ""
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await primary_player.send_resources()
                        await self.send_info_box()
                    elif ability == "Power from Pain":
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.reactions_needing_resolving.append(ability)
                        self.player_who_resolves_reaction.append(secondary_player.name_player)
                        self.positions_of_unit_triggering_reaction.append((int(secondary_player.get_number()),
                                                                           -1, -1))
                        self.mode = "Normal"
                        self.player_with_action = ""
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                        await primary_player.send_discard()
                        await self.send_info_box()
                    elif ability == "Suppressive Fire":
                        self.chosen_first_card = False
                        self.chosen_second_card = False
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Calculated Strike":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Even the Odds":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.chosen_second_card = False
                        self.chosen_first_card = False
                        self.misc_target_attachment = (-1, -1, -1)
                        self.misc_player_storage = ""
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Squig Bombin'":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Archon's Terror":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Drop Pod Assault":
                        if self.last_planet_checked_for_battle != -1:
                            self.action_chosen = "Drop Pod Assault"
                            self.choice_context = "Drop Pod Assault"
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                            primary_player.number_cards_to_search = 6
                            self.resolving.search_box = True
                            self.cards_in_search_box = primary_player.deck[0:primary_player.number_cards_to_search]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = str(primary_player.number)
                            self.what_to_do_with_searched_card = "PLAY TO BATTLE"
                            self.traits_of_searched_card = None
                            self.card_type_of_searched_card = "Army"
                            self.faction_of_searched_card = "Space Marines"
                            self.max_cost_of_searched_card = 3
                            self.all_conditions_searched_card_required = True
                            self.no_restrictions_on_chosen_card = False
                            await self.send_search()
                            await primary_player.send_hand()
                            await primary_player.send_resources()
                        else:
                            primary_player.add_resources(card.get_cost())
                            await self.game_sockets[0].receive_game_update("No battle taking place")
                    elif ability == "Squadron Redeployment":
                        self.action_chosen = "Squadron Redeployment"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Warpstorm":
                        print("Resolve Warpstorm")
                        self.action_chosen = "Warpstorm"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Tzeentch's Firestorm":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        self.choices_available = []
                        for i in range(primary_player.resources + 1):
                            self.choices_available.append(str(i))
                        self.name_player_making_choices = primary_player.name_player
                        self.choice_context = "Amount to spend for Tzeentch's Firestorm:"
                        self.amount_spend_for_tzeentch_firestorm = -1
                        await self.send_search()
                    elif ability == "Infernal Gateway":
                        self.action_chosen = "Infernal Gateway"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Promise of Glory":
                        print("Resolve Promise of Glory")
                        primary_player.summon_token_at_hq("Cultist", amount=2)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                        await primary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await primary_player.send_resources()
                        await self.send_info_box()
                    elif ability == "Doom":
                        print("Resolve Doom")
                        primary_player.destroy_all_cards_in_hq(ignore_uniques=True, units_only=True, enemy_event=False)
                        secondary_player.destroy_all_cards_in_hq(ignore_uniques=True, units_only=True, enemy_event=True)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                        await primary_player.send_hq()
                        await secondary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await primary_player.send_resources()
                        await self.send_info_box()
                    elif ability == "Pact of the Haemonculi":
                        print("Resolve PotH")
                        self.action_chosen = "Pact of the Haemonculi"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Gift of Isha":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Deception":
                        self.action_chosen = "Deception"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Exterminatus":
                        print("Resolve Exterminatus")
                        self.action_chosen = "Exterminatus"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Snotling Attack":
                        print("Resolve Snotling Attack")
                        self.action_chosen = "Snotling Attack"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.misc_counter = 4
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Preemptive Barrage":
                        self.action_chosen = ability
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        self.misc_target_planet = -1
                        self.misc_counter = 3
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Promise of Glory":
                        print("Resolve Promise of Glory")
                        primary_player.summon_token_at_hq("Cultist", amount=2)
                        primary_player.discard_card_from_hand(int(game_update_string[2]))
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                        await primary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await primary_player.send_resources()
                        await self.send_info_box()
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
                                    await primary_player.send_hand()
                                    await primary_player.send_discard()
                                    await primary_player.send_resources()
                                    await secondary_player.send_resources()
                                    await self.send_info_box()
                    else:
                        primary_player.add_resources(card.get_cost())
                        await self.game_sockets[0].receive_game_update(card.get_name() + " not "
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
                    await primary_player.send_hand()
        else:
            await self.game_sockets[0].receive_game_update("already chosen a valid attachment for ambush platform")
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
                    await primary_player.send_hand()
                    await primary_player.send_units_at_planet(self.position_of_actioned_card[0])
                    await primary_player.send_resources()
                    self.position_of_actioned_card = (-1, -1)
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
                        await primary_player.send_hand()
        else:
            await self.game_sockets[0].receive_game_update("already chosen a valid unit for infernal gateway")
