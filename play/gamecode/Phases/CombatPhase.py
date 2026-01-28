async def update_game_event_combat_section(self, name, game_update_string):
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif self.actions_between_battle:
        if game_update_string[0] == "action-button":
            if self.get_actions_allowed():
                self.stored_mode = self.mode
                self.mode = "ACTION"
                self.player_with_action = name
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
                if not self.p1.has_passed:
                    await self.send_update_message(self.name_1 + " is ready to proceed to the next battle.")
                self.p1.has_passed = True
            else:
                if not self.p2.has_passed:
                    await self.send_update_message(self.name_2 + " is ready to proceed to the next battle.")
                self.p2.has_passed = True
            if self.p1.has_passed and self.p2.has_passed:
                self.actions_between_battle = False
                self.p1.has_passed = False
                self.p2.has_passed = False
                another_battle = self.find_next_planet_for_combat()
                if another_battle:
                    self.set_battle_initiative()
                    if not self.start_battle_deepstrike:
                        self.p1.has_passed = False
                        self.p2.has_passed = False
                    self.planet_aiming_reticle_active = True
                    self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
                    await self.send_update_message(
                        "Battle begins at the " + self.get_planet_name(self.last_planet_checked_for_battle) +
                        ". Players take combat turns. Press the action button between turns to take an action.")
                else:
                    await self.change_phase("HEADQUARTERS")
                    await self.send_update_message(
                        "Window provided for reactions and actions during HQ phase."
                    )
    elif len(game_update_string) == 1:
        if game_update_string[0] == "action-button":
            if self.get_actions_allowed():
                print("Need to run action code")
                self.stored_mode = self.mode
                self.mode = "ACTION"
                self.player_with_action = name
                print("Special combat action")
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
            if self.start_battle_deepstrike:
                if name == self.name_player_deepstriking:
                    if self.choosing_target_for_deepstruck_attachment:
                        if self.num_player_deepstriking == "1":
                            player = self.p1
                            other_player = self.p2
                        else:
                            player = self.p2
                            other_player = self.p1
                        og_pla, og_pos = self.deepstruck_attachment_pos
                        player.add_card_to_discard(player.cards_in_reserve[og_pla][og_pos].get_name())
                        del player.cards_in_reserve[og_pla][og_pos]
                        player.deepstrike_attachment_extras(og_pla)
                        self.choosing_target_for_deepstruck_attachment = False
                        self.deepstruck_attachment_pos = (-1, -1)
                        player.has_passed = True
                        if not other_player.has_passed:
                            self.name_player_making_choices = other_player.name_player
                            self.choice_context = "Deepstrike cards?"
                            self.choices_available = ["Yes", "No"]
                            self.resolving_search_box = True
                            await self.send_update_message(
                                other_player.name_player + " can deepstrike")
                        if player.has_passed and other_player.has_passed:
                            self.end_start_battle_deepstrike()
                            self.resolving_search_box = False
                            self.reset_choices_available()
                            player.has_passed = False
                            other_player.has_passed = False
                            await self.send_update_message("Deepstrike is complete")
                            self.start_ranged_skirmish(self.last_planet_checked_for_battle)
                    else:
                        if self.num_player_deepstriking == "1":
                            player = self.p1
                            other_player = self.p2
                        else:
                            player = self.p2
                            other_player = self.p1
                        player.has_passed = True
                        if not other_player.has_passed:
                            self.name_player_making_choices = other_player.name_player
                            self.choice_context = "Deepstrike cards?"
                            self.choices_available = ["Yes", "No"]
                            self.resolving_search_box = True
                            await self.send_update_message(other_player.name_player + " can deepstrike")
                        if player.has_passed and other_player.has_passed:
                            self.end_start_battle_deepstrike()
                            self.resolving_search_box = False
                            self.reset_choices_available()
                            player.has_passed = False
                            other_player.has_passed = False
                            await self.send_update_message("Deepstrike is complete")
                            self.start_ranged_skirmish(self.last_planet_checked_for_battle)
            elif self.area_effect_active:
                if name == self.player_with_combat_turn:
                    if self.number_with_combat_turn == "1":
                        primary_player = self.p1
                        secondary_player = self.p2
                    else:
                        primary_player = self.p2
                        secondary_player = self.p1
                    for i in range(len(self.misc_misc)):
                        planet_pos, unit_pos = self.misc_misc[i]
                        can_shield = not primary_player.get_armorbane_given_pos(self.attacker_planet,
                                                                                self.attacker_position)
                        shadow_field = False
                        if primary_player.get_cost_given_pos(
                                self.attacker_planet, self.attacker_position) < 3 \
                                and primary_player.get_card_type_given_pos(
                            self.attacker_planet, self.attacker_position) == "Army":
                            shadow_field = True
                        preventable = True
                        if primary_player.search_attachments_at_pos(
                                self.attacker_planet, self.attacker_position, "Acid Maw"):
                            preventable = False
                        took_damage, bodyguards = secondary_player.assign_damage_to_pos(
                            planet_pos, unit_pos, damage=self.stored_area_effect_value,
                            att_pos=None, can_shield=can_shield,
                            shadow_field_possible=shadow_field, rickety_warbuggy=True,
                            preventable=preventable
                        )
                    if primary_player.search_attachments_at_pos(self.attacker_planet,
                                                                self.attacker_position,
                                                                "Doom Siren", must_match_name=True):
                        self.create_reaction("Doom Siren", primary_player.name_player,
                                             (int(primary_player.number), self.attacker_planet,
                                              self.attacker_position))
                        self.value_doom_siren = self.stored_area_effect_value
                    self.area_effect_active = False
                    self.misc_misc = []
                    self.reset_combat_positions()
                    self.number_with_combat_turn = secondary_player.get_number()
                    self.player_with_combat_turn = secondary_player.get_name_player()
            elif name == self.player_with_combat_turn:
                if self.number_with_combat_turn == "1":
                    self.number_with_combat_turn = "2"
                    self.player_with_combat_turn = self.name_2
                    self.p1.has_passed = True
                    self.reset_combat_positions()
                    for planet in range(7):
                        for j in range(len(self.p1.cards_in_play[planet + 1])):
                            self.p1.cards_in_play[planet + 1][j].cannot_be_declared_as_attacker = False
                    if self.mode == "Normal":
                        await self.send_update_message(self.name_1 + " passes their combat turn.")
                    else:
                        await self.send_update_message(self.name_1 + " passes their retreat turn.")
                else:
                    self.number_with_combat_turn = "1"
                    self.player_with_combat_turn = self.name_1
                    self.p2.has_passed = True
                    self.reset_combat_positions()
                    for planet in range(7):
                        for j in range(len(self.p2.cards_in_play[planet + 1])):
                            self.p2.cards_in_play[planet + 1][j].cannot_be_declared_as_attacker = False
                    if self.mode == "Normal":
                        await self.send_update_message(self.name_2 + " passes their combat turn.")
                    else:
                        await self.send_update_message(self.name_2 + " passes their retreat turn.")
                if self.p1.has_passed and self.p2.has_passed:
                    if self.mode == "Normal":
                        if self.ranged_skirmish_active:
                            await self.send_update_message("Both players passed, ranged skirmish ends.")
                            self.p1.has_passed = False
                            self.p2.has_passed = False
                            self.reset_combat_turn()
                            self.ranged_skirmish_active = False
                            self.p1.ranged_skirmish_ends_triggers(self.last_planet_checked_for_battle)
                            self.p2.ranged_skirmish_ends_triggers(self.last_planet_checked_for_battle)
                        else:
                            await self.send_update_message("Both players passed, combat round ends.")
                            self.p1.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.p2.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.combat_round_number += 1
                            self.p1.has_passed = False
                            self.p2.has_passed = False
                            self.p1.resolve_combat_round_ends_effects(self.last_planet_checked_for_battle)
                            self.p2.resolve_combat_round_ends_effects(self.last_planet_checked_for_battle)
                            self.reset_combat_turn()
                            self.mode = "RETREAT"
                            self.combat_reset_eocr_values()
                            if self.combat_round_number > 2:
                                await self.check_stalemate(name)
                    elif self.mode == "RETREAT":
                        self.p1.has_passed = False
                        self.p2.has_passed = False
                        self.p1.reset_can_retreat_values()
                        self.p2.reset_can_retreat_values()
                        self.reset_combat_turn()
                        self.mode = "Normal"
                        self.begin_combat_round()
    elif len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if self.mode == "Normal":
                if name == self.player_with_combat_turn:
                    chosen_planet = int(game_update_string[1])
                    if chosen_planet == self.last_planet_checked_for_battle:
                        if self.attacker_position != -1 and self.defender_position == -1:
                            if self.number_with_combat_turn == "1":
                                primary_player = self.p1
                                secondary_player = self.p2
                            else:
                                primary_player = self.p2
                                secondary_player = self.p1
                            amount_aoe = primary_player.get_area_effect_given_pos(self.attacker_planet,
                                                                                  self.attacker_position)
                            faction = primary_player.get_faction_given_pos(self.attacker_planet,
                                                                           self.attacker_position)
                            if amount_aoe > 0:
                                self.unit_will_move_after_attack = False
                                primary_player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                                    ethereal_movement_active = False
                                self.damage_from_attack = True
                                self.attacker_location = (int(primary_player.number), self.attacker_planet,
                                                          self.attacker_position)
                                if self.apoka:
                                    self.area_effect_active = True
                                    self.misc_counter = self.max_aoe_targets
                                    self.stored_area_effect_value = amount_aoe
                                    self.misc_misc = []
                                    await self.send_update_message("You are using Apoka's version of AOE; please "
                                                                   "select up to " + str(self.misc_counter)
                                                                   + " targets.")
                                else:
                                    if primary_player.search_attachments_at_pos(self.attacker_planet,
                                                                                self.attacker_position,
                                                                                "Doom Siren", must_match_name=True):
                                        self.create_reaction("Doom Siren", primary_player.name_player,
                                                             (int(primary_player.number), self.attacker_planet,
                                                              self.attacker_position))
                                        self.value_doom_siren = amount_aoe
                                    shadow_field = False
                                    if primary_player.get_cost_given_pos(
                                            self.attacker_planet, self.attacker_position) < 3 \
                                            and primary_player.get_card_type_given_pos(
                                        self.attacker_planet, self.attacker_position) == "Army":
                                        shadow_field = True
                                    await self.aoe_routine(primary_player, secondary_player, chosen_planet,
                                                           amount_aoe, faction=faction,
                                                           shadow_field_possible=shadow_field,
                                                           actual_aoe=True)
                                    self.reset_combat_positions()
                                    self.number_with_combat_turn = secondary_player.get_number()
                                    self.player_with_combat_turn = secondary_player.get_name_player()
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HAND":
            print("Card in hand clicked on")
            if self.mode == "SHIELD":
                if name == self.player_who_is_shielding:
                    if game_update_string[1] == self.number_who_is_shielding:
                        hand_pos = int(game_update_string[2])
            elif self.mode == "Normal":
                if name == self.player_with_combat_turn:
                    if game_update_string[1] == self.number_with_combat_turn:
                        if self.attacker_position != -1:
                            hand_pos = int(game_update_string[2])
                            if self.number_with_combat_turn == "1":
                                player = self.p1
                                other_player = self.p2
                            else:
                                player = self.p2
                                other_player = self.p1
                            if player.cards[hand_pos] == "Launch da Snots":
                                print("is launch")
                                if player.get_faction_given_pos(self.attacker_planet, self.attacker_position) == "Orks":
                                    print("is orks")
                                    if player.resources > 0:
                                        if self.nullify_enabled and other_player.nullify_check():
                                            await self.send_update_message(
                                                player.name_player + " wants to play " +
                                                "Launcha da Snots" + "; Nullify window offered.")
                                            self.choices_available = ["Yes", "No"]
                                            self.name_player_making_choices = other_player.name_player
                                            self.choice_context = "Use Nullify?"
                                            self.nullified_card_pos = int(game_update_string[2])
                                            self.nullified_card_name = "Launch da Snots"
                                            self.cost_card_nullified = 1
                                            self.first_player_nullified = player.name_player
                                            self.nullify_context = "Launch da Snots"
                                        else:
                                            player.spend_resources(1)
                                            extra_attack = player.count_copies_at_planet(self.attacker_planet,
                                                                                         "Snotlings")
                                            player.increase_attack_of_unit_at_pos(self.attacker_planet,
                                                                                  self.attacker_position,
                                                                                  extra_attack, expiration="NEXT")
                                            attack_name = player.get_name_given_pos(self.attacker_planet,
                                                                                    self.attacker_position)
                                            await self.send_update_message(
                                                attack_name + " gained " + str(extra_attack)
                                                + " ATK from Launch Da Snots!"
                                            )
                                            player.discard_card_from_hand(hand_pos)
    elif len(game_update_string) == 6:
        if game_update_string[0] == "ATTACHMENT" and game_update_string[1] == "IN_PLAY":
            if game_update_string[2] == self.number_with_combat_turn:
                if self.number_with_combat_turn == "1":
                    player = self.p1
                else:
                    player = self.p2
                planet_pos = int(game_update_string[3])
                unit_pos = int(game_update_string[4])
                attachment_pos = int(game_update_string[5])
                if planet_pos == self.attacker_planet and unit_pos == self.attacker_position:
                    if player.cards_in_play[planet_pos + 1][unit_pos]. \
                            get_attachments()[attachment_pos].get_ability() == "The Shining Blade" \
                            and player.cards_in_play[planet_pos + 1][unit_pos]. \
                            get_attachments()[attachment_pos].name_owner == player.name_player:
                        if player.cards_in_play[planet_pos + 1][unit_pos]. \
                                get_attachments()[attachment_pos].get_ready():
                            player.cards_in_play[planet_pos + 1][unit_pos]. \
                                get_attachments()[attachment_pos].exhaust_card()
                            self.shining_blade_active = True
                            await self.send_update_message("The Shining Blade activated!")
    elif len(game_update_string) == 4:
        if game_update_string[0] == "RESERVE":
            if self.start_battle_deepstrike:
                if name == self.name_player_deepstriking:
                    if game_update_string[1] == self.num_player_deepstriking:
                        chosen_planet = int(game_update_string[2])
                        chosen_unit = int(game_update_string[3])
                        if chosen_planet == self.last_planet_checked_for_battle:
                            if self.num_player_deepstriking == "1":
                                player = self.p1
                                other_player = self.p2
                            else:
                                player = self.p2
                                other_player = self.p1
                            cost = player.get_deepstrike_value_given_pos(chosen_planet, chosen_unit)
                            if player.spend_resources(cost):
                                if player.get_card_type_in_reserve(chosen_planet, chosen_unit) != "Attachment":
                                    if player.get_card_type_in_reserve(chosen_planet, chosen_unit) == "Army":
                                        player.deepstrike_unit(chosen_planet, chosen_unit)
                                    elif player.get_card_type_in_reserve(chosen_planet, chosen_unit) == "Event":
                                        player.deepstrike_event(chosen_planet, chosen_unit)
                                    if not player.check_for_cards_in_reserve(chosen_planet):
                                        player.has_passed = True
                                        if not other_player.has_passed:
                                            self.name_player_making_choices = other_player.name_player
                                            self.choice_context = "Deepstrike cards?"
                                            self.choices_available = ["Yes", "No"]
                                            self.resolving_search_box = True
                                            await self.send_update_message(
                                                other_player.name_player + " can deepstrike")
                                        if player.has_passed and other_player.has_passed:
                                            self.end_start_battle_deepstrike()
                                            self.resolving_search_box = False
                                            self.reset_choices_available()
                                            player.has_passed = False
                                            other_player.has_passed = False
                                            await self.send_update_message("Deepstrike is complete")
                                            self.start_ranged_skirmish(self.last_planet_checked_for_battle)
                                else:
                                    if player.cards_in_reserve[chosen_planet][chosen_unit].planet_attachment:
                                        player.add_attachment_to_planet(
                                            chosen_planet, player.cards_in_reserve[chosen_planet][chosen_unit])
                                        del player.cards_in_reserve[chosen_planet][chosen_unit]
                                        player.deepstrike_attachment_extras(chosen_planet)
                                        if not player.check_for_cards_in_reserve(chosen_planet):
                                            player.has_passed = True
                                            if not other_player.has_passed:
                                                self.name_player_making_choices = other_player.name_player
                                                self.choice_context = "Deepstrike cards?"
                                                self.choices_available = ["Yes", "No"]
                                                self.resolving_search_box = True
                                                await self.send_update_message(
                                                    other_player.name_player + " can deepstrike")
                                            if player.has_passed and other_player.has_passed:
                                                self.end_start_battle_deepstrike()
                                                self.resolving_search_box = False
                                                self.reset_choices_available()
                                                player.has_passed = False
                                                other_player.has_passed = False
                                                await self.send_update_message("Deepstrike is complete")
                                                self.start_ranged_skirmish(self.last_planet_checked_for_battle)
                                    else:
                                        self.choosing_target_for_deepstruck_attachment = True
                                        player.cards_in_reserve[chosen_planet][chosen_unit]. \
                                            aiming_reticle_color = "blue"
                                        self.deepstruck_attachment_pos = (chosen_planet, chosen_unit)
                                        await self.send_update_message("deepstriking attachment")

        elif game_update_string[0] == "IN_PLAY":
            print("Unit clicked on.")
            chosen_planet = int(game_update_string[2])
            chosen_unit = int(game_update_string[3])
            if self.start_battle_deepstrike:
                if name == self.name_player_deepstriking:
                    if self.num_player_deepstriking == "1":
                        player = self.p1
                        other_player = self.p2
                    else:
                        player = self.p2
                        other_player = self.p1
                    if self.choosing_target_for_deepstruck_attachment:
                        if game_update_string[1] == player.number:
                            player_receiving_attachment = player
                            not_own_att = False
                        else:
                            player_receiving_attachment = other_player
                            not_own_att = True
                        og_pla, og_pos = self.deepstruck_attachment_pos
                        if not player.idden_base_active:
                            card = player.cards_in_reserve[og_pla][og_pos]
                        else:
                            card = self.preloaded_find_card(
                                player.cards_in_play[og_pla + 1][og_pos].deepstrike_card_name)
                        if ((not player.idden_base_active) or ((og_pla, og_pos) != (chosen_planet, chosen_unit)) or
                                player_receiving_attachment.name_player != player.name_player) and \
                                og_pla == chosen_planet:
                            if player_receiving_attachment.attach_card(card, chosen_planet, chosen_unit,
                                                                       not_own_attachment=not_own_att):
                                if not player.idden_base_active:
                                    del player.cards_in_reserve[og_pla][og_pos]
                                else:
                                    player.discard_attachments_from_card(og_pla, og_pos)
                                    del player.cards_in_play[og_pla + 1][og_pos]
                                player.deepstrike_attachment_extras(chosen_planet)
                                self.choosing_target_for_deepstruck_attachment = False
                                self.deepstruck_attachment_pos = (-1, -1)
                                if not other_player.has_passed:
                                    self.name_player_making_choices = other_player.name_player
                                    self.choice_context = "Deepstrike cards?"
                                    self.choices_available = ["Yes", "No"]
                                    self.resolving_search_box = True
                                    await self.send_update_message(
                                        other_player.name_player + " can deepstrike")
                                if player.has_passed and other_player.has_passed:
                                    self.end_start_battle_deepstrike()
                                    self.resolving_search_box = False
                                    self.reset_choices_available()
                                    player.has_passed = False
                                    other_player.has_passed = False
                                    await self.send_update_message("Deepstrike is complete")
                                    self.start_ranged_skirmish(self.last_planet_checked_for_battle)
                    else:
                        if game_update_string[1] == self.num_player_deepstriking:
                            chosen_planet = int(game_update_string[2])
                            chosen_unit = int(game_update_string[3])
                            if chosen_planet == self.last_planet_checked_for_battle:
                                if self.num_player_deepstriking == "1":
                                    player = self.p1
                                    other_player = self.p2
                                else:
                                    player = self.p2
                                    other_player = self.p1
                                cost = player.get_deepstrike_value_given_pos(chosen_planet, chosen_unit,
                                                                             in_play_card=True)
                                if cost != -1:
                                    if player.spend_resources(cost):
                                        if player.get_card_type_in_reserve(chosen_planet, chosen_unit,
                                                                           in_play_card=True) != "Attachment":
                                            if player.get_card_type_in_reserve(chosen_planet, chosen_unit,
                                                                               in_play_card=True) == "Army":
                                                player.deepstrike_unit(chosen_planet, chosen_unit, in_play_card=True)
                                            elif player.get_card_type_in_reserve(chosen_planet, chosen_unit,
                                                                                 in_play_card=True) == "Event":
                                                player.deepstrike_event(chosen_planet, chosen_unit, in_play_card=True)
                                            if not player.check_for_cards_in_reserve(chosen_planet):
                                                player.has_passed = True
                                                if not other_player.has_passed:
                                                    self.name_player_making_choices = other_player.name_player
                                                    self.choice_context = "Deepstrike cards?"
                                                    self.choices_available = ["Yes", "No"]
                                                    self.resolving_search_box = True
                                                    await self.send_update_message(
                                                        other_player.name_player + " can deepstrike")
                                                if player.has_passed and other_player.has_passed:
                                                    self.end_start_battle_deepstrike()
                                                    self.resolving_search_box = False
                                                    self.reset_choices_available()
                                                    player.has_passed = False
                                                    other_player.has_passed = False
                                                    await self.send_update_message("Deepstrike is complete")
                                                    self.start_ranged_skirmish(self.last_planet_checked_for_battle)
                                        else:
                                            card_name = player.cards_in_play[
                                                chosen_planet + 1][chosen_unit].deepstrike_card_name
                                            card = self.preloaded_find_card(card_name)
                                            if card.planet_attachment:
                                                player.add_attachment_to_planet(
                                                    chosen_planet, card)
                                                player.discard_attachments_from_card(chosen_planet, chosen_unit)
                                                del player.cards_in_play[chosen_planet + 1][chosen_unit]
                                                player.deepstrike_attachment_extras(chosen_planet)
                                                if not player.check_for_cards_in_reserve(chosen_planet):
                                                    player.has_passed = True
                                                    if not other_player.has_passed:
                                                        self.name_player_making_choices = other_player.name_player
                                                        self.choice_context = "Deepstrike cards?"
                                                        self.choices_available = ["Yes", "No"]
                                                        self.resolving_search_box = True
                                                        await self.send_update_message(
                                                            other_player.name_player + " can deepstrike")
                                                    if player.has_passed and other_player.has_passed:
                                                        self.end_start_battle_deepstrike()
                                                        self.resolving_search_box = False
                                                        self.reset_choices_available()
                                                        player.has_passed = False
                                                        other_player.has_passed = False
                                                        await self.send_update_message("Deepstrike is complete")
                                                        self.start_ranged_skirmish(self.last_planet_checked_for_battle)
                                            else:
                                                self.choosing_target_for_deepstruck_attachment = True
                                                player.cards_in_play[chosen_planet + 1][chosen_unit]. \
                                                    aiming_reticle_color = "blue"
                                                self.deepstruck_attachment_pos = (chosen_planet, chosen_unit)
                                                await self.send_update_message("deepstriking attachment")
            elif name == self.player_with_combat_turn:
                print(self.number_with_combat_turn)
                print(self.player_with_combat_turn)
                print(self.attacker_position)
                if self.mode == "RETREAT":
                    if game_update_string[1] == self.number_with_combat_turn:
                        print("Retreat unit", chosen_planet, chosen_unit)
                        if chosen_planet == self.last_planet_checked_for_battle:
                            if self.number_with_combat_turn == "1":
                                player = self.p1
                            else:
                                player = self.p2
                            player.retreat_unit(chosen_planet, chosen_unit, exhaust=True)
                elif self.area_effect_active:
                    if self.number_with_combat_turn == "1":
                        primary_player = self.p1
                        secondary_player = self.p2
                    else:
                        primary_player = self.p2
                        secondary_player = self.p1
                    if game_update_string[1] == secondary_player.number:
                        chosen_planet = int(game_update_string[2])
                        chosen_unit = int(game_update_string[3])
                        if chosen_planet == self.last_planet_checked_for_battle:
                            if secondary_player.get_ability_given_pos(chosen_planet, chosen_unit) not in \
                                    self.units_immune_to_aoe:
                                genestealer_hybrids_relevant = False
                                for j in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                                    if secondary_player.get_ability_given_pos(chosen_planet, j) == \
                                            "Genestealer Hybrids" and chosen_unit != j:
                                        genestealer_hybrids_relevant = True
                                if not genestealer_hybrids_relevant:
                                    if (chosen_planet, chosen_unit) not in self.misc_misc:
                                        secondary_player.set_aiming_reticle_in_play(chosen_planet, chosen_unit)
                                        self.misc_misc.append((chosen_planet, chosen_unit))
                                        self.misc_counter = self.misc_counter - 1
                                    if self.misc_counter < 1:
                                        for i in range(len(self.misc_misc)):
                                            planet_pos, unit_pos = self.misc_misc[i]
                                            can_shield = not primary_player.get_armorbane_given_pos(
                                                self.attacker_planet,
                                                self.attacker_position)
                                            shadow_field = False
                                            if primary_player.get_cost_given_pos(
                                                    self.attacker_planet, self.attacker_position) < 3 \
                                                    and primary_player.get_card_type_given_pos(
                                                self.attacker_planet, self.attacker_position) == "Army":
                                                shadow_field = True
                                            preventable = True
                                            if primary_player.search_attachments_at_pos(
                                                    self.attacker_planet, self.attacker_position, "Acid Maw"):
                                                preventable = False
                                            took_damage, bodyguards = secondary_player.assign_damage_to_pos(
                                                planet_pos, unit_pos, damage=self.stored_area_effect_value,
                                                att_pos=None, can_shield=can_shield,
                                                shadow_field_possible=shadow_field, rickety_warbuggy=True,
                                                preventable=preventable
                                            )
                                        if primary_player.search_attachments_at_pos(self.attacker_planet,
                                                                                    self.attacker_position,
                                                                                    "Doom Siren", must_match_name=True):
                                            self.create_reaction("Doom Siren", primary_player.name_player,
                                                                 (int(primary_player.number), self.attacker_planet,
                                                                  self.attacker_position))
                                            self.value_doom_siren = self.stored_area_effect_value
                                        self.area_effect_active = False
                                        self.misc_misc = []
                                        self.reset_combat_positions()
                                        self.number_with_combat_turn = secondary_player.get_number()
                                        self.player_with_combat_turn = secondary_player.get_name_player()
                                else:
                                    await self.send_update_message("Genestealer Hybrids prevents AOE")
                            else:
                                await self.send_update_message("Immune to AOE")
                elif self.attacker_position == -1:
                    if game_update_string[1] == self.number_with_combat_turn:
                        chosen_planet = int(game_update_string[2])
                        chosen_unit = int(game_update_string[3])
                        valid_unit = False
                        if self.number_with_combat_turn == "1":
                            player = self.p1
                            secondary_player = self.p2
                        else:
                            player = self.p2
                            secondary_player = self.p1
                        if chosen_planet == self.last_planet_checked_for_battle:
                            grav_inhib_rel = player.search_card_at_planet(chosen_planet, "Grav Inhibitor Drone")
                            if not grav_inhib_rel:
                                grav_inhib_rel = secondary_player.search_card_at_planet(chosen_planet,
                                                                                        "Grav Inhibitor Drone")
                            if grav_inhib_rel:
                                grav_inhib_rel = False
                                for i in range(len(player.cards_in_play[chosen_planet + 1])):
                                    if player.get_card_type_given_pos(chosen_planet, i) == "Army":
                                        if player.get_cost_given_pos(chosen_planet, i) > 2:
                                            if player.get_ready_given_pos(chosen_planet, i):
                                                grav_inhib_rel = True
                                for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                                    if secondary_player.get_card_type_given_pos(chosen_planet, i) == "Army":
                                        if secondary_player.get_cost_given_pos(chosen_planet, i) > 2:
                                            if secondary_player.get_ready_given_pos(chosen_planet, i):
                                                grav_inhib_rel = True
                            if grav_inhib_rel:
                                grav_inhib_rel = False
                                if player.get_card_type_given_pos(chosen_planet, chosen_unit) == "Army":
                                    if player.get_cost_given_pos(chosen_planet, chosen_unit) < 3:
                                        grav_inhib_rel = True
                            iron_hands_cent_rel = player.search_card_at_planet(chosen_planet, "Iron Hands Centurion",
                                                                               ready_relevant=True)
                            if not iron_hands_cent_rel:
                                iron_hands_cent_rel = secondary_player.search_card_at_planet(chosen_planet,
                                                                                             "Iron Hands Centurion",
                                                                                             ready_relevant=True)
                            if iron_hands_cent_rel:
                                iron_hands_cent_rel = False
                                if player.get_card_type_given_pos(chosen_planet, chosen_unit) == "Army":
                                    if player.get_cost_given_pos(chosen_planet, chosen_unit) < 3:
                                        iron_hands_cent_rel = True
                            pinning_razorback = False
                            if player.cards_in_play[chosen_planet + 1][chosen_unit].cannot_be_declared_as_attacker:
                                pinning_razorback = True
                            can_continue = False
                            print("check enemy cards")
                            print(len(secondary_player.cards_in_play[chosen_planet + 1]))
                            if grav_inhib_rel:
                                can_continue = False
                                valid_unit = False
                                await self.send_update_message("Grav Inhibitor Drone is preventing "
                                                               "this unit from attacking")
                            elif iron_hands_cent_rel:
                                can_continue = False
                                valid_unit = False
                                await self.send_update_message("Iron Hands Centurion is preventing "
                                                               "this unit from attacking")
                            elif pinning_razorback:
                                can_continue = False
                                valid_unit = False
                                await self.send_update_message("Pinning Razorback is preventing "
                                                               "this unit from attacking")
                            elif not secondary_player.cards_in_play[chosen_planet + 1]:
                                valid_unit = False
                                can_continue = False
                                await self.send_update_message("No enemy units to declare as defender. Combat ends.")
                                await self.check_combat_end(player.name_player)
                            elif self.ranged_skirmish_active:
                                for i in range(len(player.cards_in_play[chosen_planet + 1])):
                                    if player.cards_in_play[chosen_planet + 1][i].emperor_champion_active:
                                        if player.get_ready_given_pos(chosen_planet, i):
                                            if player.get_ranged_given_pos(chosen_planet, i):
                                                chosen_unit = i
                                is_ranged = player.get_ranged_given_pos(chosen_planet, chosen_unit)
                                if is_ranged:
                                    can_continue = True
                            else:
                                for i in range(len(player.cards_in_play[chosen_planet + 1])):
                                    if player.cards_in_play[chosen_planet + 1][i].emperor_champion_active:
                                        if player.get_ready_given_pos(chosen_planet, i):
                                            chosen_unit = i
                                can_continue = True
                            if can_continue:
                                is_ready = player.check_ready_pos(chosen_planet, chosen_unit)
                                if is_ready:
                                    if player.cards_in_play[chosen_planet + 1][chosen_unit] \
                                            .get_card_type() == "Warlord":
                                        self.choices_available = ["Yes", "No"]
                                        self.choice_context = "Retreat Warlord?"
                                        self.name_player_making_choices = player.name_player
                                        self.resolving_search_box = True
                                    print("Unit ready, can be used")
                                    valid_unit = True
                                else:
                                    print("Unit not ready")
                        if valid_unit:
                            player.cards_in_play[chosen_planet + 1][chosen_unit].resolving_attack = True
                            player.set_aiming_reticle_in_play(chosen_planet, chosen_unit, "blue")
                            self.attacker_planet = chosen_planet
                            self.attacker_position = chosen_unit
                            self.may_move_defender = True
                            self.additional_attack_effects_allowed = True
                            self.shadow_thorns_body_allowed = True
                            self.attack_being_resolved = True
                            print("Attacker:", self.attacker_planet, self.attacker_position)
                            if self.number_with_combat_turn == "1":
                                player = self.p1
                                other_player = self.p2
                            else:
                                player = self.p2
                                other_player = self.p1
                            player.has_passed = False
                            player.exhaust_given_pos(self.attacker_planet, self.attacker_position)
                            if player.get_card_type_given_pos(self.attacker_planet, self.attacker_position) == "Army":
                                for i in range(len(other_player.attachments_at_planet[self.attacker_planet])):
                                    if other_player.attachments_at_planet[self.attacker_planet][i] \
                                            .get_ability() == "Repulsor Minefield":
                                        player.assign_damage_to_pos(self.attacker_planet, self.attacker_position, 1,
                                                                    by_enemy_unit=False)
                                for i in range(len(player.attachments_at_planet[self.attacker_planet])):
                                    if player.attachments_at_planet[self.attacker_planet][i] \
                                            .get_ability() == "Repulsor Minefield":
                                        player.assign_damage_to_pos(self.attacker_planet, self.attacker_position, 1,
                                                                    by_enemy_unit=False)
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    in self.units_move_hq_attack:
                                self.unit_will_move_after_attack = True
                                player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                                    ethereal_movement_active = True
                            if player.get_card_type_given_pos(self.attacker_planet,
                                                              self.attacker_position) != "Warlord":
                                i = 0
                                while i < len(player.attachments_at_planet[self.attacker_planet]):
                                    if player.attachments_at_planet[self.attacker_planet][i] \
                                            .get_ability() == "Improvised Minefield":
                                        player.assign_damage_to_pos(self.attacker_planet, self.attacker_position, 3,
                                                                    by_enemy_unit=False)
                                        player.add_card_to_discard("Improvised Minefield")
                                        del player.attachments_at_planet[self.attacker_planet][i]
                                        i = i - 1
                                    i = i + 1
                                i = 0
                                while i < len(other_player.attachments_at_planet[self.attacker_planet]):
                                    if other_player.attachments_at_planet[self.attacker_planet][i] \
                                            .get_ability() == "Improvised Minefield":
                                        player.assign_damage_to_pos(self.attacker_planet, self.attacker_position, 3,
                                                                    by_enemy_unit=False)
                                        other_player.add_card_to_discard("Improvised Minefield")
                                        del other_player.attachments_at_planet[self.attacker_planet][i]
                                        i = i - 1
                                    i = i + 1
                            valid_adjacent_and_self_planets = []
                            if self.attacker_planet != 0:
                                valid_adjacent_and_self_planets.append(self.attacker_planet - 1)
                            valid_adjacent_and_self_planets.append(self.attacker_planet)
                            if self.attacker_planet != 6:
                                valid_adjacent_and_self_planets.append(self.attacker_planet + 1)
                            for overseer_planet in valid_adjacent_and_self_planets:
                                for i in range(len(player.cards_in_play[overseer_planet + 1])):
                                    if player.get_ability_given_pos(overseer_planet, i) == "Overseer Drone":
                                        if player.get_ready_given_pos(overseer_planet, i):
                                            self.create_reaction("Overseer Drone", player.name_player,
                                                                 (int(player.number), overseer_planet, i),
                                                                 (self.attacker_planet, self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Biel-Tan Warp Spiders":
                                self.create_reaction("Biel-Tan Warp Spiders", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.search_hand_for_card("Rapid Ingress") and player.get_resources() > 0:
                                if self.get_green_icon(self.attacker_planet):
                                    if len(player.cards_in_play[self.attacker_planet + 1]) == 1:
                                        self.create_reaction("Rapid Ingress", player.name_player,
                                                             (int(player.number), self.attacker_planet, -1))
                            if player.search_hand_for_card("Unexpected Ferocity") and player.get_resources() > 0:
                                self.create_reaction("Unexpected Ferocity", player.name_player,
                                                     (int(player.number), self.attacker_planet, self.attacker_position))
                            if player.check_for_trait_given_pos(
                                    self.attacker_planet, self.attacker_position, "Ecclesiarchy"):
                                if player.get_faction_given_pos(
                                        self.attacker_planet, self.attacker_position) == "Astra Militarum":
                                    for i in range(len(player.cards_in_play[self.attacker_planet + 1])):
                                        if i != self.attacker_position:
                                            if player.get_ability_given_pos(
                                                    self.attacker_planet, i
                                            ) == "Dominion Eugenia":
                                                self.create_reaction("Dominion Eugenia", player.name_player,
                                                                     (int(player.number), self.attacker_planet,
                                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Masked Hunter":
                                self.create_reaction("Masked Hunter", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Imperial Fists Legion":
                                self.create_reaction("Imperial Fists Legion", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Salamander Flamer Squad":
                                self.flamers_damage_active = True
                                self.id_of_the_active_flamer = \
                                    player.cards_in_play[self.attacker_planet + 1][self.attacker_position].card_id
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Farsight Vanguard":
                                if not player.get_once_per_phase_used_given_pos(self.attacker_planet,
                                                                                self.attacker_position):
                                    self.create_reaction("Farsight Vanguard", player.name_player,
                                                         (int(player.number), self.attacker_planet,
                                                          self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Flayed Ones Pack":
                                for _ in range(3):
                                    player.discard_top_card_deck()
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Parasite of Mortrex":
                                if not player.get_once_per_round_used_given_pos(self.attacker_planet,
                                                                                self.attacker_position):
                                    self.create_reaction("Parasite of Mortrex", player.name_player,
                                                         (int(player.number), self.attacker_planet,
                                                          self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Mars Alpha Exterminator":
                                self.create_reaction("Mars Alpha Exterminator", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position,
                                                            bloodied_relevant=True) \
                                    == "Ku'gath Plaguefather":
                                self.create_reaction("Ku'gath Plaguefather", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(chosen_planet, self.attacker_position) \
                                    == "Wailing Wraithfighter":
                                self.create_reaction("Wailing Wraithfighter", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(chosen_planet, self.attacker_position) \
                                    == "Seraphim Superior Allegra":
                                self.create_reaction("Seraphim Superior Allegra", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Dark Lance Raider":
                                self.create_reaction("Dark Lance Raider", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Spiritseer Erathal":
                                self.create_reaction("Spiritseer Erathal", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position,
                                                            bloodied_relevant=True) \
                                    == "Old Zogwort":
                                self.create_reaction("Old Zogwort", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Shrieking Harpy" and \
                                    (not self.apoka or not player.get_once_per_phase_used_given_pos(
                                        self.attacker_planet, self.attacker_position)):
                                if self.infested_planets[self.attacker_planet]:
                                    self.create_reaction(
                                        "Shrieking Harpy", player.name_player,
                                        (int(player.number), self.attacker_planet, self.attacker_position))
                            for i in range(len(other_player.cards_in_play[self.attacker_planet + 1])):
                                current_name = other_player.cards_in_play[self.attacker_planet + 1][i].get_ability()
                                if current_name == "Celestian Amelia":
                                    if not other_player.get_once_per_phase_used_given_pos(self.attacker_planet, i):
                                        self.create_reaction("Celestian Amelia", other_player.name_player,
                                                             (int(other_player.number), self.attacker_planet, i))
                            if player.search_attachments_at_pos(self.attacker_planet, self.attacker_position,
                                                                "Pyrrhian Warscythe"):
                                self.create_reaction("Pyrrhian Warscythe", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.search_attachments_at_pos(self.attacker_planet, self.attacker_position,
                                                                "Banshee Power Sword", must_match_name=True):
                                self.create_reaction("Banshee Power Sword", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.search_attachments_at_pos(self.attacker_planet, self.attacker_position,
                                                                "The Plaguefather's Banner", must_match_name=True):
                                self.create_reaction("The Plaguefather's Banner", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            attachments = player.get_all_attachments_at_pos(self.attacker_planet, self.attacker_position)
                            for i in range(len(attachments)):
                                if attachments[i].get_ability() == "Beastmaster's Whip":
                                    self.create_reaction("Beastmaster's Whip", player.name_player,
                                                         (int(player.number), self.attacker_planet,
                                                          self.attacker_position))
                            if player.search_card_at_planet(self.attacker_planet, "Gorgul Da Slaya"):
                                self.create_interrupt("Gorgul Da Slaya", player.name_player,
                                                      (int(player.number), self.attacker_planet, -1))
                            if player.check_for_trait_given_pos(self.attacker_planet, self.attacker_position, "Psyker"):
                                for i in range(7):
                                    if i != self.attacker_planet:
                                        for j in range(len(player.cards_in_play[i + 1])):
                                            if player.get_ability_given_pos(i, j) == "Talyesin's Spiders":
                                                self.create_reaction("Talyesin's Spiders", player.name_player,
                                                                     (int(player.number), i, j))
                                for i in range(len(player.headquarters)):
                                    if player.get_ability_given_pos(-2, i) == "Talyesin's Spiders":
                                        self.create_reaction("Talyesin's Spiders", player.name_player,
                                                             (int(player.number), -2, i))
                elif self.defender_position == -1:
                    can_continue = False
                    if int(game_update_string[2]) == self.attacker_planet:
                        can_continue = True
                    elif self.shining_blade_active:
                        if abs(int(game_update_string[2]) - self.attacker_planet) == 1:
                            can_continue = True
                    if can_continue:
                        if game_update_string[1] != self.number_with_combat_turn:
                            if self.number_with_combat_turn == "1":
                                primary_player = self.p1
                                secondary_player = self.p2
                            else:
                                primary_player = self.p2
                                secondary_player = self.p1
                            u_pos = int(game_update_string[3])
                            if primary_player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                                    emperor_champion_active:
                                for i in range(len(secondary_player.cards_in_play[self.attacker_planet + 1])):
                                    if secondary_player.get_name_given_pos(self.attacker_planet, i) == \
                                            "The Emperor's Champion":
                                        u_pos = i
                            primary_player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                                emperor_champion_active = False
                            self.defender_planet = int(game_update_string[2])
                            self.defender_position = u_pos
                            print("Defender:", self.defender_planet, self.defender_position)
                            attack_value = 0
                            if self.sweep_active:
                                attack_value = self.sweep_value
                            else:
                                attack_value = primary_player.get_attack_given_pos(self.attacker_planet,
                                                                                   self.attacker_position)
                            can_continue = True
                            exa = secondary_player.search_card_at_planet(self.defender_planet, "Dire Avenger Exarch")
                            print("Found exarch", exa)
                            is_ready_lych = (secondary_player.get_ability_given_pos(
                                self.defender_planet, self.defender_position) != "Lychguard Sentinel" or
                                             not secondary_player.get_ready_given_pos(
                                                 self.defender_planet, self.defender_position))
                            is_fl = secondary_player.get_ability_given_pos(
                                self.defender_planet, self.defender_position) != "Front Line 'Ard Boyz"
                            is_exa_can = not (exa and secondary_player.check_for_trait_given_pos(
                                self.defender_planet, self.defender_position, "Warrior"))
                            is_gene_hybrid = secondary_player.get_ability_given_pos(
                                self.defender_planet, self.defender_position) != "Genestealer Hybrids"
                            print(is_ready_lych, is_fl, is_exa_can)
                            if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position] \
                                    .get_ability() == "Honored Librarian":
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if secondary_player.cards_in_play[self.defender_planet + 1][i] \
                                            .get_ability() != "Honored Librarian":
                                        can_continue = False
                            if is_ready_lych and is_fl and is_exa_can and is_gene_hybrid:
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if not self.sweep_active or secondary_player.cards_in_play[
                                            self.defender_planet + 1][i].valid_sweep_target:
                                        if (secondary_player.get_ability_given_pos(
                                                self.defender_planet, i) == "Lychguard Sentinel" and
                                            secondary_player.get_ready_given_pos(self.defender_planet, i)) or \
                                                secondary_player.get_ability_given_pos(
                                                    self.defender_planet, i) == "Front Line 'Ard Boyz" or \
                                                secondary_player.get_ability_given_pos(
                                                    self.defender_planet, i) == "Genestealer Hybrids" or \
                                                (exa and secondary_player.check_for_trait_given_pos(
                                                    self.defender_planet, i, "Warrior")):
                                            can_continue = False
                                            print("Found FL")
                            if self.sweep_active and can_continue:
                                if not secondary_player.cards_in_play[self.defender_planet + 1][
                                        self.defender_position].valid_sweep_target:
                                    can_continue = False
                                    await self.send_update_message("That unit has already been attacked!")
                                else:
                                    print(secondary_player.cards_in_play[self.defender_planet + 1][
                                              self.defender_position].valid_sweep_target)
                                    print("Sweep ok")
                            if self.may_move_defender and can_continue:
                                if secondary_player.search_card_at_planet(self.defender_planet, "Zen Xi Aonia"):
                                    can_continue = False
                                    self.create_interrupt("Zen Xi Aonia", secondary_player.name_player,
                                                          (int(secondary_player.number), self.defender_planet, -1))
                                    self.last_defender_position = (secondary_player.number,
                                                                   self.defender_planet,
                                                                   self.defender_position)
                                    secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                self.defender_position,
                                                                                "red")
                            if self.may_move_defender and can_continue:
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if i != self.defender_position:
                                        if secondary_player.get_ability_given_pos(self.defender_planet,
                                                                                  i) == "Fire Warrior Elite":
                                            if not self.fire_warrior_elite_active \
                                                    and not secondary_player.hit_by_gorgul:
                                                self.fire_warrior_elite_active = True
                                                can_continue = False
                                                self.create_reaction("Fire Warrior Elite", secondary_player.name_player,
                                                                     (int(secondary_player.number),
                                                                      self.defender_planet, -1))
                                                self.last_defender_position = (secondary_player.number,
                                                                               self.defender_planet,
                                                                               self.defender_position)
                                                secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                            self.defender_position,
                                                                                            "red")
                            if can_continue and self.may_move_defender:
                                ready_runt = False
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if secondary_player.get_ready_given_pos(self.defender_planet, i) and \
                                            secondary_player.check_for_trait_given_pos(self.defender_planet, i, "Runt"):
                                        ready_runt = True
                                if ready_runt:
                                    if secondary_player.search_hand_for_card(
                                            "Runts to the Front") and secondary_player.resources > 0:
                                        can_continue = False
                                        self.create_reaction("Runts to the Front", secondary_player.name_player,
                                                             (int(secondary_player.number),
                                                              self.defender_planet, -1))
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                                        secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                    self.defender_position,
                                                                                    "red")
                            if can_continue and self.may_move_defender:
                                for i in range(len(secondary_player.cards_in_reserve[self.defender_planet])):
                                    if secondary_player.cards_in_reserve[self.defender_planet][i].get_ability() \
                                            == "Deathwing Interceders":
                                        if secondary_player.resources > 1:
                                            if not secondary_player.hit_by_gorgul:
                                                self.fire_warrior_elite_active = True
                                                can_continue = False
                                                self.create_reaction("Deathwing Interceders",
                                                                     secondary_player.name_player,
                                                                     (int(secondary_player.number),
                                                                      self.defender_planet, -1))
                                                self.last_defender_position = (secondary_player.number,
                                                                               self.defender_planet,
                                                                               self.defender_position)
                                                secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                            self.defender_position,
                                                                                            "red")
                            if can_continue and self.additional_attack_effects_allowed:
                                if secondary_player.check_for_trait_given_pos(self.defender_planet, self.defender_position, "Elite"):
                                    if not primary_player.cards_in_play[self.attacker_planet + 1][self.attacker_position].attack_set_next is not None:
                                        if primary_player.search_attachments_at_pos(self.attacker_planet, self.attacker_position, "Krak Grenade"):
                                            can_continue = False
                                            self.additional_attack_effects_allowed = False
                                            await self.send_update_message(
                                                "Krak Grenade can be used."
                                            )
                                            secondary_player.set_aiming_reticle_in_play(
                                                self.defender_planet, self.defender_position, "blue"
                                            )
                                            self.create_reaction(
                                                "Krak Grenade", primary_player.name_player,
                                                (int(primary_player.number), self.attacker_planet,
                                                 self.attacker_position)
                                            )
                                            self.last_defender_position = (secondary_player.number,
                                                                           self.defender_planet,
                                                                           self.defender_position)
                            if can_continue and self.shadow_thorns_body_allowed:
                                if secondary_player.search_attachments_at_pos(
                                        self.defender_planet, self.defender_position,
                                        "Shadowed Thorns Bodysuit", ready_relevant=True, must_match_name=True
                                ):
                                    can_continue = False
                                    await self.send_update_message(
                                        "Shadowed Thorns Bodysuit can be used to cancel the attack"
                                    )
                                    secondary_player.set_aiming_reticle_in_play(
                                        self.defender_planet, self.defender_position, "blue"
                                    )
                                    self.create_reaction(
                                        "Shadowed Thorns Bodysuit", secondary_player.name_player,
                                        (int(secondary_player.number), self.defender_planet, self.defender_position)
                                    )
                                    self.last_defender_position = (secondary_player.number,
                                                                   self.defender_planet,
                                                                   self.defender_position)
                                elif secondary_player.search_attachments_at_pos(
                                        self.defender_planet, self.defender_position,
                                        "Dripping Scythes", must_match_name=True
                                ):
                                    can_continue = False
                                    await self.send_update_message(
                                        "Dripping Scythes can be used to cancel the attack"
                                    )
                                    secondary_player.set_aiming_reticle_in_play(
                                        self.defender_planet, self.defender_position, "blue"
                                    )
                                    self.create_reaction(
                                        "Dripping Scythes", secondary_player.name_player,
                                        (int(secondary_player.number), self.defender_planet, self.defender_position)
                                    )
                                    self.last_defender_position = (secondary_player.number,
                                                                   self.defender_planet,
                                                                   self.defender_position)
                                elif secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position) == "War Walker Squadron":
                                    attachments = secondary_player.cards_in_play[
                                        self.defender_planet + 1][self.defender_position].get_attachments()
                                    found_hardpoint = False
                                    for i in range(len(attachments)):
                                        if attachments[i].check_for_a_trait("Hardpoint") and attachments[i].get_ready():
                                            found_hardpoint = True
                                    if found_hardpoint:
                                        can_continue = False
                                        await self.send_update_message(
                                            "War Walker Squadron can be used to cancel the attack"
                                        )
                                        secondary_player.set_aiming_reticle_in_play(
                                            self.defender_planet, self.defender_position, "blue"
                                        )
                                        self.create_reaction(
                                            "War Walker Squadron", secondary_player.name_player,
                                            (int(secondary_player.number), self.defender_planet,
                                             self.defender_position)
                                        )
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                                elif secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position
                                ) == "Dodging Land Speeder" and secondary_player.get_ready_given_pos(
                                    self.defender_planet, self.defender_position
                                ):
                                    can_continue = False
                                    await self.send_update_message(
                                        "Dodging Land Speeder can be used to cancel the attack"
                                    )
                                    secondary_player.set_aiming_reticle_in_play(
                                        self.defender_planet, self.defender_position, "blue"
                                    )
                                    self.create_interrupt(
                                        "Dodging Land Speeder", secondary_player.name_player,
                                        (int(secondary_player.number), self.defender_planet, self.defender_position)
                                    )
                                    self.last_defender_position = (secondary_player.number,
                                                                   self.defender_planet,
                                                                   self.defender_position)
                                elif "Catachan Devils Patrol" in secondary_player.cards:
                                    card = self.preloaded_find_card("Catachan Devils Patrol")
                                    self.discounts_applied = 0
                                    hand_dis = secondary_player.search_hand_for_discounts(card.get_faction(),
                                                                                          card.get_traits())
                                    hq_dis = secondary_player.search_hq_for_discounts(card.get_faction(),
                                                                                      card.get_traits())
                                    in_play_dis = secondary_player.search_all_planets_for_discounts(
                                        card.get_traits(), card.get_faction())
                                    same_planet_dis, same_planet_auto_dis = \
                                        secondary_player.search_same_planet_for_discounts(
                                            card.get_faction(), self.defender_planet)
                                    self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis
                                    if self.available_discounts + secondary_player.resources >= card.get_cost():
                                        can_continue = False
                                        await self.send_update_message(
                                            "Catachan Devils Patrol can be deployed"
                                        )
                                        secondary_player.set_aiming_reticle_in_play(
                                            self.defender_planet, self.defender_position, "blue"
                                        )
                                        self.create_interrupt(
                                            "Catachan Devils Patrol", secondary_player.name_player,
                                            (int(secondary_player.number), self.defender_planet, self.defender_position)
                                        )
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                                elif secondary_player.search_card_in_hq("Fake Ooman Base", ready_relevant=True):
                                    if secondary_player.get_faction_given_pos(
                                            self.defender_planet, self.defender_position) == "Orks" and \
                                            secondary_player.check_for_trait_given_pos(
                                                self.defender_planet, self.defender_position, "Soldier") and \
                                            secondary_player.get_card_type_given_pos(
                                                self.defendet_planet, self.defender_position
                                            ) == "Army":
                                        can_continue = False
                                        await self.send_update_message(
                                            "Fake Ooman Base can be used to cancel the attack"
                                        )
                                        secondary_player.set_aiming_reticle_in_play(
                                            self.defender_planet, self.defender_position, "blue"
                                        )
                                        self.create_reaction(
                                            "Fake Ooman Base", secondary_player.name_player,
                                            (int(secondary_player.number), self.defender_planet,
                                             self.defender_position)
                                        )
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                                else:
                                    warlord_pla, warlord_pos = secondary_player.get_location_of_warlord()
                                    if abs(warlord_pla - self.defender_planet) == 1:
                                        if not secondary_player.check_for_trait_given_pos(self.defender_planet,
                                                                                          self.defender_position,
                                                                                          "Elite"):
                                            if secondary_player.search_attachments_at_pos(warlord_pla, warlord_pos,
                                                                                          "Kaptin's Hook",
                                                                                          ready_relevant=True):
                                                can_continue = False
                                                await self.send_update_message(
                                                    "Kaptin's Hook can be used to cancel the attack"
                                                )
                                                secondary_player.set_aiming_reticle_in_play(
                                                    self.defender_planet, self.defender_position, "blue"
                                                )
                                                self.create_reaction(
                                                    "Kaptin's Hook", secondary_player.name_player,
                                                    (int(secondary_player.number), self.defender_planet,
                                                     self.defender_position)
                                                )
                                                self.last_defender_position = (secondary_player.number,
                                                                               self.defender_planet,
                                                                               self.defender_position)
                            if can_continue and self.allow_damage_abilities_defender:
                                if secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position) == "Firedrake Terminators":
                                    can_continue = False
                                    await self.send_update_message(
                                        "Firedrake Terminators must fire before the rest of the attack."
                                    )
                                    secondary_player.set_aiming_reticle_in_play(
                                        self.defender_planet, self.defender_position, "blue"
                                    )
                                    self.create_reaction("Firedrake Terminators", secondary_player.name_player,
                                                         (int(primary_player.number), self.attacker_planet,
                                                          self.attacker_position))
                                    self.last_defender_position = (secondary_player.number,
                                                                   self.defender_planet,
                                                                   self.defender_position)
                            if can_continue and self.allow_damage_abilities_defender:
                                if secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position) == "Rampaging Knarloc":
                                    if secondary_player.get_ready_given_pos(
                                            self.defender_planet, self.defender_position):
                                        can_continue = False
                                        await self.send_update_message(
                                            "Rampaging Knarloc must fire before the rest of the attack."
                                        )
                                        secondary_player.set_aiming_reticle_in_play(
                                            self.defender_planet, self.defender_position, "blue"
                                        )
                                        self.create_reaction("Rampaging Knarloc", secondary_player.name_player,
                                                             (int(secondary_player.number), self.defender_planet,
                                                              self.defender_position))
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                            if can_continue and self.allow_damage_abilities_defender:
                                if secondary_player.get_card_type_given_pos(
                                        self.defender_planet, self.defender_position) == "Warlord":
                                    if not secondary_player.counterblow_used and secondary_player.search_hand_for_card(
                                            "Counterblow"):
                                        can_continue = False
                                        await self.send_update_message(
                                            "Counterblow must fire before the rest of the attack."
                                        )
                                        secondary_player.set_aiming_reticle_in_play(
                                            self.defender_planet, self.defender_position, "blue"
                                        )
                                        self.create_interrupt("Counterblow", secondary_player.name_player,
                                                              (int(primary_player.number), self.attacker_planet,
                                                               self.attacker_position))
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                            if can_continue and self.allow_damage_abilities_defender:
                                if secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position) == "Trap Laying Hunter":
                                    if not secondary_player.cards_in_play[self.defender_planet + 1][
                                            self.defender_position].misc_ability_used:
                                        can_continue = False
                                        await self.send_update_message(
                                            "Trap Laying Hunter must fire before the rest of the attack."
                                        )
                                        secondary_player.set_aiming_reticle_in_play(
                                            self.defender_planet, self.defender_position, "blue"
                                        )
                                        self.create_interrupt("Trap Laying Hunter", secondary_player.name_player,
                                                              (int(secondary_player.number), self.defender_planet,
                                                               self.defender_position))
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                            if can_continue and self.allow_damage_abilities_defender:
                                if secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position) == "Neurotic Obliterator":
                                    ready_weapon = False
                                    for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1][
                                                           self.defender_position].get_attachments())):
                                        if secondary_player.cards_in_play[self.defender_planet + 1][
                                            self.defender_position].get_attachments()[i].get_ready() and \
                                                secondary_player.cards_in_play[self.defender_planet + 1][
                                                    self.defender_position].get_attachments()[i].check_for_a_trait(
                                                    "Weapon"):
                                            ready_weapon = True
                                    if ready_weapon:
                                        can_continue = False
                                        await self.send_update_message(
                                            "Neutoric Obliterator must fire before the rest of the attack."
                                        )
                                        secondary_player.set_aiming_reticle_in_play(
                                            self.defender_planet, self.defender_position, "blue"
                                        )
                                        self.create_reaction("Neurotic Obliterator", secondary_player.name_player,
                                                             (int(primary_player.number), self.attacker_planet,
                                                              self.attacker_position))
                                        self.last_defender_position = (secondary_player.number,
                                                                       self.defender_planet,
                                                                       self.defender_position)
                            if can_continue:
                                self.allow_damage_abilities_defender = True
                                faction = primary_player.get_faction_given_pos(self.attacker_planet,
                                                                               self.attacker_position)
                                print("atk faction:", faction)
                                if faction in self.energy_weapon_sounds:
                                    self.queued_sound = "necrons_attack"
                                if faction in self.gunfire_weapon_sounds:
                                    self.queued_sound = "gunfire_attack"
                                if secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position) == "Tomb Blade Diversionist":
                                    secondary_player.cards_in_play[
                                        self.defender_planet + 1][self.defender_position].misc_ability_used = True
                                for i in range(len(primary_player.cards_in_play[self.defender_planet + 1])):
                                    if primary_player.get_ability_given_pos(
                                            self.defender_planet, i) == "Sickening Helbrute":
                                        self.create_reaction("Sickening Helbrute", secondary_player.name_player,
                                                             (int(secondary_player.number), self.defender_planet,
                                                              self.defender_position))
                                if primary_player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                        == "Storming Librarian":
                                    value_storming_librarion = primary_player.cards_in_play[self.attacker_planet + 1][
                                        self.attacker_position].card_id
                                    secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position]. \
                                        hit_by_which_storming_librarians.append(value_storming_librarion)
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if secondary_player.get_ability_given_pos(
                                            self.defender_planet, i) == "Sickening Helbrute":
                                        self.create_reaction("Sickening Helbrute", secondary_player.name_player,
                                                             (int(secondary_player.number), self.defender_planet,
                                                              self.defender_position))
                                if not self.sweep_active:
                                    if primary_player.get_ability_given_pos(
                                            self.attacker_planet, self.attacker_position) == "Starbane's Council":
                                        if not secondary_player.get_ready_given_pos(self.defender_planet,
                                                                                    self.defender_position):
                                            attack_value += 2
                                    if primary_player.get_ability_given_pos(
                                            self.attacker_planet, self.attacker_position) == "Dark Angels Vindicator":
                                        command = secondary_player.get_command_given_pos(self.defender_planet,
                                                                                         self.defender_position)
                                        if secondary_player.get_card_type_given_pos(
                                                self.defender_planet, self.defender_position) == "Warlord":
                                            command = command - 999
                                        attack_value += 2 * max(command, 0)
                                    if primary_player.get_ability_given_pos(
                                            self.attacker_planet, self.attacker_position) == "Storm Guardians":
                                        if secondary_player.check_for_trait_given_pos(
                                                self.defender_planet, self.defender_position, "Soldier") or\
                                            secondary_player.check_for_trait_given_pos(
                                                self.defender_planet, self.defender_position, "Warrior"):
                                            attack_value += 2
                                    for i in range(len(primary_player.cards_in_play[self.attacker_planet + 1][
                                            self.attacker_position].get_attachments())):
                                        if primary_player.cards_in_play[self.attacker_planet + 1][
                                                self.attacker_position].get_attachments()[
                                                i].get_ability() == "Hidden Strike Chainsword":
                                            if secondary_player.get_card_type_given_pos(
                                                    self.defender_planet, self.defender_position) != "Warlord":
                                                attack_value += 2
                                    if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position]\
                                            .get_card_type() != "Warlord":
                                        attack_value += self.banshee_power_sword_extra_attack
                                        self.banshee_power_sword_extra_attack = 0
                                att_flying = primary_player.get_flying_given_pos(self.attacker_planet,
                                                                                 self.attacker_position)
                                def_flying = secondary_player.get_flying_given_pos(self.defender_planet,
                                                                                   self.defender_position)
                                att_ignores_flying = primary_player.get_ignores_flying_given_pos(
                                    self.attacker_planet, self.attacker_position)
                                if primary_player.get_ability_given_pos(
                                        self.attacker_planet, self.attacker_position) == "Silvered Blade Avengers":
                                    if secondary_player.cards_in_play[
                                        self.defender_planet + 1][self.defender_position] \
                                            .get_card_type() != "Warlord":
                                        secondary_player.exhaust_given_pos(self.defender_planet,
                                                                           self.defender_position)
                                if secondary_player.get_ability_given_pos(
                                        self.defender_planet, self.defender_position) == "Farsight Vanguard":
                                    if not secondary_player.get_once_per_phase_used_given_pos(
                                            self.defender_planet, self.defender_position):
                                        self.create_reaction("Farsight Vanguard", secondary_player.name_player,
                                                             (int(secondary_player.number), self.defender_planet,
                                                              self.defender_position))
                                if secondary_player.cards_in_play[
                                    self.defender_planet + 1][self.defender_position] \
                                        .get_card_type() == "Warlord" or primary_player.name_player \
                                        in secondary_player.cards_in_play[self.defender_planet + 1][
                                        self.defender_position].hit_by_frenzied_wulfen_names:
                                    if primary_player.get_card_type_given_pos(self.attacker_planet,
                                                                              self.attacker_position) == "Warlord":
                                        for i in range(len(primary_player.headquarters)):
                                            if primary_player.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                                                self.create_reaction("Gladius Strike Force", primary_player.name_player,
                                                                     (int(primary_player.number), -2, i))
                                    if secondary_player.search_card_in_hq("Zogwort's Hovel"):
                                        self.create_reaction("Zogwort's Hovel", secondary_player.name_player,
                                                             (int(secondary_player.number), self.defender_planet,
                                                              -1))
                                if secondary_player.search_attachments_at_pos(
                                        self.defender_planet, self.defender_position, "The Black Sword"
                                ):
                                    self.create_reaction("The Black Sword", secondary_player.name_player,
                                                         (int(primary_player.number), self.attacker_planet,
                                                          self.attacker_position))
                                # Flying check
                                if def_flying and not att_flying and not att_ignores_flying:
                                    attack_value = int(attack_value / 2 + (attack_value % 2))
                                self.damage_on_unit_before_new_damage = \
                                    secondary_player.get_damage_given_pos(self.defender_planet,
                                                                          self.defender_position)
                                if not self.sweep_active:
                                    if primary_player.check_for_trait_given_pos(self.attacker_planet,
                                                                                self.attacker_position, "Space Wolves"):
                                        if primary_player.search_card_in_hq("Ragnar's Warcamp"):
                                            if primary_player.check_for_warlord(self.attacker_planet, True,
                                                                                primary_player.name_player):
                                                if secondary_player.get_card_type_given_pos(
                                                        self.defender_planet, self.defender_position) == "Warlord":
                                                    attack_value = attack_value * 2
                                                elif primary_player.name_player in secondary_player.cards_in_play[
                                                    self.defender_planet + 1][
                                                    self.defender_position].hit_by_frenzied_wulfen_names:
                                                    attack_value = attack_value * 2
                                    if secondary_player.check_for_trait_given_pos(self.defender_planet,
                                                                                  self.defender_position, "Vehicle"):
                                        if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                                self.attacker_position) \
                                                == "Tankbusta Bommaz":
                                            attack_value = attack_value * 2
                                        if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                                self.attacker_position) \
                                                == "Fire Dragons":
                                            attack_value = attack_value * 2
                                    if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                            self.attacker_position) \
                                            == "Hydra Flak Tank":
                                        if secondary_player.get_flying_given_pos(self.defender_planet,
                                                                                 self.defender_position):
                                            attack_value = attack_value * 2
                                        elif secondary_player.get_mobile_given_pos(self.defender_planet,
                                                                                   self.defender_position):
                                            attack_value = attack_value * 2
                                    if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                            self.attacker_position) \
                                            == "Noble Shining Spears":
                                        if secondary_player.get_damage_given_pos(self.defender_planet,
                                                                                 self.defender_position) == 0:
                                            attack_value += 3
                                    if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                            self.attacker_position) \
                                            == "Stalking Ur-Ghul":
                                        if secondary_player.get_card_type_given_pos(self.defender_planet,
                                                                                    self.defender_position) \
                                                == "Warlord":
                                            attack_value = attack_value - 5
                                        elif secondary_player.get_card_type_given_pos(self.defender_planet,
                                                                                      self.defender_position) \
                                                == "Army":
                                            if secondary_player.get_damage_given_pos(self.defender_planet,
                                                                                     self.defender_position) == 0:
                                                attack_value = attack_value - 5
                                    if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                            self.attacker_position) \
                                            == "Roghrax Bloodhand":
                                        if self.bloodthirst_active[self.attacker_planet]:
                                            attack_value = attack_value * 2
                                if secondary_player.get_all_attachments_at_pos(
                                        self.defender_planet, self.defender_position):
                                    for i in range(len(primary_player.get_all_attachments_at_pos(
                                            self.attacker_planet, self.attacker_position))):
                                        if primary_player.get_attachment_at_pos(
                                            self.attacker_planet, self.attacker_position, i
                                        ).get_ability() == "Acidic Venom Cannon":
                                            attack_value += 3
                                            if secondary_player.get_card_type_given_pos(
                                                    self.defender_planet, self.defender_position
                                            ) != "Warlord":
                                                self.create_delayed_reaction(
                                                    "Acidic Venom Cannon", primary_player.name_player,
                                                    (int(secondary_player.number), self.defender_planet,
                                                     self.defender_position)
                                                )
                                if secondary_player.get_damage_given_pos(self.defender_planet,
                                                                         self.defender_position) > 0:
                                    if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                            self.attacker_position) \
                                            == "Havocs of Khorne":
                                        attack_value = attack_value * 2
                                secondary_player.cards_in_play[self.defender_planet + 1][
                                    self.defender_position].valid_sweep_target = False
                                print("unit is no longer a valid sweep target")
                                self.card_type_defender = secondary_player.get_card_type_given_pos(
                                    self.defender_planet, self.defender_position)
                                self.defender_is_flying_or_mobile = secondary_player.get_flying_given_pos(
                                    self.defender_planet, self.defender_position) or \
                                                                    secondary_player.get_mobile_given_pos(
                                    self.defender_planet, self.defender_position)
                                self.defender_is_also_warlord = \
                                    primary_player.name_player in \
                                    secondary_player.cards_in_play[self.defender_planet + 1
                                    ][self.defender_position].hit_by_frenzied_wulfen_names
                                self.attacker_location = (int(primary_player.number), self.attacker_planet,
                                                          self.attacker_position)
                                if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                        self.attacker_position) \
                                        == "Burna Boyz":
                                    self.create_reaction("Burna Boyz", primary_player.name_player,
                                                         (int(primary_player.number), self.attacker_planet,
                                                          self.attacker_position))
                                if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                        self.attacker_position) \
                                        == "Fenrisian Wolf Pack":
                                    if attack_value > 0:
                                        self.create_reaction("Fenrisian Wolf Pack", primary_player.name_player,
                                                             (int(primary_player.number), self.attacker_planet,
                                                              self.attacker_position))
                                self.last_defender_position = (secondary_player.number,
                                                               self.defender_planet, self.defender_position)
                                if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                        self.attacker_position) \
                                        == "Torquemada Coteaz":
                                    primary_player.reset_card_name_misc_ability("Torquemada Coteaz")
                                enemy_unit_damage = secondary_player.get_damage_given_pos(self.defender_planet,
                                                                                          self.defender_position)
                                can_shield = not primary_player.get_armorbane_given_pos(self.attacker_planet,
                                                                                        self.attacker_position,
                                                                                        enemy_unit_damage)
                                shadow_field = False
                                if primary_player.get_cost_given_pos(
                                        self.attacker_planet, self.attacker_position) < 3 \
                                        and primary_player.get_card_type_given_pos(
                                    self.attacker_planet, self.attacker_position) == "Army":
                                    shadow_field = True
                                preventable = True
                                if primary_player.search_attachments_at_pos(
                                        self.attacker_planet, self.attacker_position, "Acid Maw"):
                                    preventable = False
                                if preventable and primary_player.get_card_type_given_pos(
                                        self.attacker_planet, self.attacker_position) != "Warlord":
                                    attack_value = attack_value - self.jungle_trench_count
                                primary_player.reset_extra_attack_until_next_attack_given_pos(self.attacker_planet,
                                                                                              self.attacker_position
                                                                                              )
                                took_damage, bodyguards = secondary_player.assign_damage_to_pos(
                                    self.defender_planet, self.defender_position, damage=attack_value,
                                    att_pos=self.attacker_location, can_shield=can_shield,
                                    shadow_field_possible=shadow_field, rickety_warbuggy=True,
                                    preventable=preventable
                                )
                                if self.manual_bodyguard_resolution:
                                    await self.send_update_message(
                                        "Too many Bodyguards! Proceeding to manual bodyguard reassignment."
                                    )
                                    await self.send_update_message(
                                        "Damage left to reassign: " + str(self.damage_bodyguard)
                                    )
                                else:
                                    print(took_damage)
                                    if primary_player.get_ability_given_pos(
                                            self.attacker_planet, self.attacker_position) == "XV8-05 Enforcer":
                                        if self.positions_of_units_to_take_damage:
                                            self.xv805_enforcer_active = True
                                            self.asking_if_use_xv805_enforcer = True
                                            self.asking_amount_xv805_enforcer = False
                                            self.player_using_xv805 = primary_player.name_player
                                            d_i = len(self.positions_of_units_to_take_damage) - 1
                                            self.damage_index_xv805 = d_i
                                            self.amount_xv805_enforcer = \
                                                self.amount_that_can_be_removed_by_shield[d_i]
                                            self.og_pos_xv805_target = (chosen_planet, chosen_unit)
                                    if took_damage:
                                        if primary_player.get_ability_given_pos(
                                                self.attacker_planet,
                                                self.attacker_position) == "Rumbling Tomb Stalker":
                                            if primary_player.get_damage_given_pos(self.attacker_planet,
                                                                                   self.attacker_position) > 0:
                                                self.create_reaction("Rumbling Tomb Stalker",
                                                                     primary_player.name_player,
                                                                     (int(primary_player.number),
                                                                      self.attacker_planet,
                                                                      self.attacker_position))
                                        if bodyguards == 0:
                                            secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                        self.defender_position,
                                                                                        "red")
                                        else:
                                            secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                        self.defender_position,
                                                                                        "blue")
                                        self.damage_from_attack = True
                                    else:
                                        primary_player.reset_aiming_reticle_in_play(self.attacker_planet,
                                                                                    self.attacker_position)
                                self.reset_combat_positions()
                                self.shining_blade_active = False
                                self.number_with_combat_turn = secondary_player.get_number()
                                self.player_with_combat_turn = secondary_player.get_name_player()
                                if self.unit_will_move_after_attack:
                                    self.need_to_move_to_hq = True
                                self.attack_being_resolved = True
                            else:
                                self.defender_planet = -1
                                self.defender_position = -1
