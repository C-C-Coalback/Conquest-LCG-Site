from ..HelperFunctions.DeclareAttacker import declare_attacker
from ..HelperFunctions.DeclareDefender import declare_defender


async def update_game_event_combat_section(self, name, game_update_string):
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif self.actions_between_battle:
        if game_update_string[0] == "action-button":
            if self.get_actions_allowed():
                self.stored_mode = self.mode
                self.mode = "ACTION"
                self.action_object.player_with_action = name
                await self.send_update_message(name + " wants to take an action.")
                if self.action_object.player_with_action == self.name_1 and self.p1.dark_possession_active:
                    self.choices_available = ["Dark Possession", "Regular Action"]
                    self.choice_context = "Use Dark Possession?"
                    self.name_player_making_choices = self.action_object.player_with_action
                elif self.action_object.player_with_action == self.name_2 and self.p2.dark_possession_active:
                    self.choices_available = ["Dark Possession", "Regular Action"]
                    self.choice_context = "Use Dark Possession?"
                    self.name_player_making_choices = self.action_object.player_with_action
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
                        "Battle begins at " + self.get_planet_name(self.last_planet_checked_for_battle) +
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
                self.action_object.player_with_action = name
                print("Special combat action")
                await self.send_update_message(name + " wants to take an action.")
                if self.action_object.player_with_action == self.name_1 and self.p1.dark_possession_active:
                    self.choices_available = ["Dark Possession", "Regular Action"]
                    self.choice_context = "Use Dark Possession?"
                    self.name_player_making_choices = self.action_object.player_with_action
                elif self.action_object.player_with_action == self.name_2 and self.p2.dark_possession_active:
                    self.choices_available = ["Dark Possession", "Regular Action"]
                    self.choice_context = "Use Dark Possession?"
                    self.name_player_making_choices = self.action_object.player_with_action
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
                        if self.deepstruck_attachment_is_in_play:
                            player.add_card_to_discard(player.cards_in_play[og_pla + 1][og_pos].deepstrike_card_name)
                            del player.cards_in_play[og_pla + 1][og_pos]
                        else:
                            player.add_card_to_discard(player.cards_in_reserve[og_pla][og_pos].get_name())
                            del player.cards_in_reserve[og_pla][og_pos]
                        player.deepstrike_attachment_extras(og_pla)
                        self.choosing_target_for_deepstruck_attachment = False
                        self.deepstruck_attachment_pos = (-1, -1)
                        self.deepstruck_attachment_is_in_play = False
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
                    can_continue = True
                    if self.mode == "Normal":
                        if self.p1.search_ready_unit_at_planet(self.last_planet_checked_for_battle):
                            if len(self.p2.cards_in_play[self.last_planet_checked_for_battle + 1]) == 0:
                                can_continue = False
                    if not can_continue:
                        await self.send_update_message("You are forced to win the battle if you don't have a way to exhaust your units.")
                        await self.check_combat_end(name)
                    else:
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
                    can_continue = True
                    if self.mode == "Normal":
                        if self.p2.search_ready_unit_at_planet(self.last_planet_checked_for_battle):
                            if len(self.p1.cards_in_play[self.last_planet_checked_for_battle + 1]) == 0:
                                can_continue = False
                    if not can_continue:
                        await self.send_update_message("You are forced to win the battle if you don't have a way to exhaust your units.")
                        await self.check_combat_end(name)
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
                            if name == self.name_1:
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
            if self.mode == "Normal":
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
                                if player.check_if_faction_given_pos(self.attacker_planet, self.attacker_position, "Orks", own_event=True):
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
                                        self.deepstruck_attachment_is_in_play = False
                                        await self.send_update_message("deepstriking attachment")

        elif game_update_string[0] == "IN_PLAY":
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
                        if self.deepstruck_attachment_is_in_play:
                            card = self.preloaded_find_card(
                                player.cards_in_play[og_pla + 1][og_pos].deepstrike_card_name)
                        else:
                            card = player.cards_in_reserve[og_pla][og_pos]
                        if ((not self.deepstruck_attachment_is_in_play) or
                            ((og_pla, og_pos) != (chosen_planet, chosen_unit)) or
                                player_receiving_attachment.name_player != player.name_player) and \
                                og_pla == chosen_planet:
                            if player_receiving_attachment.attach_card(card, chosen_planet, chosen_unit,
                                                                       not_own_attachment=not_own_att):
                                if not self.deepstruck_attachment_is_in_play:
                                    del player.cards_in_reserve[og_pla][og_pos]
                                else:
                                    player.discard_attachments_from_card(og_pla, og_pos)
                                    del player.cards_in_play[og_pla + 1][og_pos]
                                player.deepstrike_attachment_extras(chosen_planet)
                                self.choosing_target_for_deepstruck_attachment = False
                                self.deepstruck_attachment_pos = (-1, -1)
                                self.deepstruck_attachment_is_in_play = False
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
                                                self.deepstruck_attachment_is_in_play = True
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
                        await declare_attacker(self, name, game_update_string)
                elif self.defender_position == -1:
                    await declare_defender(self, name, game_update_string)