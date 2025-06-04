async def update_game_event_combat_section(self, name, game_update_string):
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif self.before_first_combat:
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
                    await self.send_update_message(self.name_1 + " is ready to proceed to the battle "
                                                                 "for the first planet")
                self.p1.has_passed = True
            else:
                if not self.p2.has_passed:
                    await self.send_update_message(self.name_2 + " is ready to proceed to the battle "
                                                                 "for the first planet")
                self.p2.has_passed = True
            if self.p1.has_passed and self.p2.has_passed:
                self.before_first_combat = False
                self.p1.has_passed = False
                self.p2.has_passed = False
                self.check_battle(self.round_number)
                self.begin_battle(self.round_number)
                self.begin_combat_round()
                await self.send_update_message("Battle begins at the first planet. Players take combat turns. "
                                               "Press the action button between turns to take an action.")
                self.set_battle_initiative()
                self.planet_aiming_reticle_active = True
                self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
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
                        player.discard.append(player.cards_in_reserve[og_pla][og_pos].get_name())
                        del player.cards_in_reserve[og_pla][og_pos]
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
                            self.start_battle_deepstrike = False
                            self.resolving_search_box = False
                            self.reset_choices_available()
                            player.has_passed = False
                            other_player.has_passed = False
                            await self.send_update_message("Deepstrike is complete")
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
                            self.start_battle_deepstrike = False
                            self.resolving_search_box = False
                            self.reset_choices_available()
                            player.has_passed = False
                            other_player.has_passed = False
                            await self.send_update_message("Deepstrike is complete")
            elif name == self.player_with_combat_turn:
                if self.number_with_combat_turn == "1":
                    self.number_with_combat_turn = "2"
                    self.player_with_combat_turn = self.name_2
                    self.p1.has_passed = True
                    self.reset_combat_positions()
                    await self.send_update_message(self.name_1 + " passes their combat/retreat turn.")
                else:
                    self.number_with_combat_turn = "1"
                    self.player_with_combat_turn = self.name_1
                    self.p2.has_passed = True
                    self.reset_combat_positions()
                    await self.send_update_message(self.name_2 + " passes their combat/retreat turn.")
                if self.p1.has_passed and self.p2.has_passed:
                    if self.mode == "Normal":
                        if self.ranged_skirmish_active:
                            await self.send_update_message("Both players passed, ranged skirmish ends.")
                            self.p1.has_passed = False
                            self.p2.has_passed = False
                            self.reset_combat_turn()
                            self.ranged_skirmish_active = False
                        else:
                            await self.send_update_message("Both players passed, combat round ends.")
                            self.p1.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.p2.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.p1.has_passed = False
                            self.p2.has_passed = False
                            self.p1.resolve_combat_round_ends_effects(self.last_planet_checked_for_battle)
                            self.p2.resolve_combat_round_ends_effects(self.last_planet_checked_for_battle)
                            self.reset_combat_turn()
                            self.mode = "RETREAT"
                            await self.check_combat_end(name)
                    elif self.mode == "RETREAT":
                        self.p1.has_passed = False
                        self.p2.has_passed = False
                        self.p1.reset_can_retreat_values()
                        self.p2.reset_can_retreat_values()
                        self.reset_combat_turn()
                        self.mode = "Normal"
                        self.begin_combat_round()
                        await self.check_combat_end(name)
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
                                self.damage_from_attack = True
                                self.attacker_location = (int(primary_player.number), self.attacker_planet,
                                                          self.attacker_position)
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
                                                       shadow_field_possible=shadow_field)
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
                                    if not player.cards_in_reserve[chosen_planet]:
                                        player.has_passed = True
                                        if not other_player.has_passed:
                                            self.name_player_making_choices = other_player.name_player
                                            self.choice_context = "Deepstrike cards?"
                                            self.choices_available = ["Yes", "No"]
                                            self.resolving_search_box = True
                                            await self.send_update_message(
                                                other_player.name_player + " can deepstrike")
                                        if player.has_passed and other_player.has_passed:
                                            self.start_battle_deepstrike = False
                                            self.resolving_search_box = False
                                            self.reset_choices_available()
                                            player.has_passed = False
                                            other_player.has_passed = False
                                            await self.send_update_message("Deepstrike is complete")
                                else:
                                    if player.cards_in_reserve[chosen_planet][chosen_unit].planet_attachment:
                                        player.add_attachment_to_planet(
                                            chosen_planet, player.cards_in_reserve[chosen_planet][chosen_unit])
                                        del player.cards_in_reserve[chosen_planet][chosen_unit]
                                        if not player.cards_in_reserve[chosen_planet]:
                                            player.has_passed = True
                                            if not other_player.has_passed:
                                                self.name_player_making_choices = other_player.name_player
                                                self.choice_context = "Deepstrike cards?"
                                                self.choices_available = ["Yes", "No"]
                                                self.resolving_search_box = True
                                                await self.send_update_message(
                                                    other_player.name_player + " can deepstrike")
                                            if player.has_passed and other_player.has_passed:
                                                self.start_battle_deepstrike = False
                                                self.resolving_search_box = False
                                                self.reset_choices_available()
                                                player.has_passed = False
                                                other_player.has_passed = False
                                                await self.send_update_message("Deepstrike is complete")
                                    else:
                                        self.choosing_target_for_deepstruck_attachment = True
                                        self.deepstruck_attachment_pos = (chosen_planet, chosen_unit)
                                        await self.send_update_message("deepstriking attachment")

        elif game_update_string[0] == "IN_PLAY":
            print("Unit clicked on.")
            chosen_planet = int(game_update_string[2])
            chosen_unit = int(game_update_string[3])
            if self.start_battle_deepstrike:
                if name == self.name_player_deepstriking:
                    if self.choosing_target_for_deepstruck_attachment:
                        if self.num_player_deepstriking == "1":
                            player = self.p1
                            other_player = self.p2
                        else:
                            player = self.p2
                            other_player = self.p1
                        if game_update_string[1] == player.number:
                            player_receiving_attachment = player
                            not_own_att = False
                        else:
                            player_receiving_attachment = other_player
                            not_own_att = True
                        og_pla, og_pos = self.deepstruck_attachment_pos
                        card = player.cards_in_reserve[og_pla][og_pos]
                        if player_receiving_attachment.attach_card(card, chosen_planet, chosen_unit,
                                                                   not_own_attachment=not_own_att):
                            del player.cards_in_reserve[og_pla][og_pos]
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
                                self.start_battle_deepstrike = False
                                self.resolving_search_box = False
                                self.reset_choices_available()
                                player.has_passed = False
                                other_player.has_passed = False
                                await self.send_update_message("Deepstrike is complete")
            if name == self.player_with_combat_turn:
                if self.mode == "RETREAT":
                    if game_update_string[1] == self.number_with_combat_turn:
                        print("Retreat unit", chosen_planet, chosen_unit)
                        if chosen_planet == self.last_planet_checked_for_battle:
                            if self.number_with_combat_turn == "1":
                                player = self.p1
                            else:
                                player = self.p2
                            player.retreat_unit(chosen_planet, chosen_unit, exhaust=True)

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
                            can_continue = False
                            print("check enemy cards")
                            print(len(secondary_player.cards_in_play[chosen_planet + 1]))
                            if not secondary_player.cards_in_play[chosen_planet + 1]:
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
                            self.shadow_thorns_body_allowed = True
                            print("Attacker:", self.attacker_planet, self.attacker_position)
                            if self.number_with_combat_turn == "1":
                                player = self.p1
                                other_player = self.p2
                            else:
                                player = self.p2
                                other_player = self.p1
                            player.has_passed = False
                            player.exhaust_given_pos(self.attacker_planet, self.attacker_position)
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    in self.units_move_hq_attack:
                                self.unit_will_move_after_attack = True
                                player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                                    ethereal_movement_active = True
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Biel-Tan Warp Spiders":
                                self.create_reaction("Biel-Tan Warp Spiders", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                                self.choices_available = ["Own deck", "Enemy deck"]
                                self.name_player_making_choices = player.name_player
                                self.choice_context = "Which deck to use Biel-Tan Warp Spiders:"
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Flayed Ones Pack":
                                for _ in range(3):
                                    player.discard_top_card_deck()
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
                                    == "Shrieking Harpy":
                                if self.infested_planets[self.attacker_planet]:
                                    self.create_reaction(
                                        "Shrieking Harpy", player.name_player,
                                        (int(player.number), self.attacker_planet, self.attacker_position))
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
                            if player.check_for_trait_given_pos(self.attacker_planet, self.attacker_position, "Psyker"):
                                for i in range(7):
                                    if i != self.attacker_planet:
                                        for j in range(len(player.cards_in_play[i + 1])):
                                            if player.get_ability_given_pos(i, j) == "Talyesin's Spiders":
                                                self.create_reaction("Talyesin's Spiders", player.name_player,
                                                                     (int(player.number), i, j))
                elif self.defender_position == -1:
                    can_continue = False
                    if int(game_update_string[2]) == self.attacker_planet:
                        can_continue = True
                    elif self.shining_blade_active:
                        if abs(int(game_update_string[2]) - self.attacker_planet) == 1:
                            can_continue = True
                    if can_continue:
                        if game_update_string[1] != self.number_with_combat_turn:
                            armorbane_check = False
                            if self.number_with_combat_turn == "1":
                                primary_player = self.p1
                                secondary_player = self.p2
                            else:
                                primary_player = self.p2
                                secondary_player = self.p1
                            u_pos = int(game_update_string[3])
                            if primary_player.cards_in_play[self.attacker_planet + 1][self.attacker_position].\
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
                            attack_value = primary_player.get_attack_given_pos(self.attacker_planet,
                                                                               self.attacker_position)
                            can_continue = True
                            exa = secondary_player.search_card_at_planet(self.defender_planet, "Dire Avenger Exarch")
                            if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position] \
                                    .get_ability() == "Honored Librarian":
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if secondary_player.cards_in_play[self.defender_planet + 1][i] \
                                            .get_ability() != "Honored Librarian":
                                        can_continue = False
                            if (secondary_player.get_ability_given_pos(
                                    self.defender_planet, self.defender_position) != "Lychguard Sentinel" or
                                    not secondary_player.get_ready_given_pos(
                                        self.defender_planet, self.defender_position)) and \
                                    secondary_player.get_ability_given_pos(
                                    self.defender_planet, self.defender_position) != "Front Line 'Ard Boyz" and \
                                    (exa and not secondary_player.check_for_trait_given_pos(
                                        self.defender_planet, self.defender_position, "Warrior")):
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if (secondary_player.get_ability_given_pos(
                                        self.defender_planet, i) == "Lychguard Sentinel" and
                                            secondary_player.get_ready_given_pos(self.defender_planet, i)) or \
                                            secondary_player.get_ability_given_pos(
                                            self.defender_planet, i) == "Front Line 'Ard Boyz" or \
                                            (exa and secondary_player.check_for_trait_given_pos(
                                            self.defender_planet, i, "Warrior")):
                                        can_continue = False
                            if self.may_move_defender:
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if i != self.defender_position:
                                        if secondary_player.get_ability_given_pos(self.defender_planet,
                                                                                  i) == "Fire Warrior Elite":
                                            if not self.fire_warrior_elite_active:
                                                self.fire_warrior_elite_active = True
                                                can_continue = False
                                                self.reactions_needing_resolving.append("Fire Warrior Elite")
                                                self.positions_of_unit_triggering_reaction.append(
                                                    [int(secondary_player.number),
                                                     self.defender_planet,
                                                     -1])
                                                self.player_who_resolves_reaction.append(secondary_player.name_player)
                                                self.last_defender_position = (secondary_player.number,
                                                                               self.defender_planet,
                                                                               self.defender_position)
                                                secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                            self.defender_position,
                                                                                            "red")
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
                            if can_continue:
                                faction = primary_player.get_faction_given_pos(self.attacker_planet,
                                                                               self.attacker_position)
                                print("atk faction:", faction)
                                if faction in self.energy_weapon_sounds:
                                    self.queued_sound = "necrons_attack"
                                if faction in self.gunfire_weapon_sounds:
                                    self.queued_sound = "gunfire_attack"
                                if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                        self.attacker_position) == "Starbane's Council":
                                    if not secondary_player.get_ready_given_pos(self.defender_planet,
                                                                                self.defender_position):
                                        attack_value += 2
                                if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position] \
                                        .get_card_type() != "Warlord":
                                    attack_value += self.banshee_power_sword_extra_attack
                                    self.banshee_power_sword_extra_attack = 0
                                if attack_value > 0:
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
                                    if secondary_player.cards_in_play[
                                        self.defender_planet + 1][self.defender_position] \
                                            .get_card_type() == "Warlord":
                                        if secondary_player.search_card_in_hq("Zogwort's Hovel"):
                                            self.create_reaction("Zogwort's Hovel", secondary_player.name_player,
                                                                 (int(secondary_player.number), self.defender_planet,
                                                                  -1))
                                    if secondary_player.get_ability_given_pos(
                                            self.defender_planet, self.defender_position) == "Firedrake Terminators":
                                        self.create_reaction("Firedrake Terminators", secondary_player.name_player,
                                                             (int(primary_player.number), self.attacker_planet,
                                                              self.attacker_position))
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
                                    primary_player.reset_extra_attack_until_next_attack_given_pos(self.attacker_planet,
                                                                                                  self.attacker_position
                                                                                                  )
                                    if primary_player.check_for_trait_given_pos(self.attacker_planet,
                                                                                self.attacker_position, "Space Wolves"):
                                        if primary_player.search_card_in_hq("Ragnar's Warcamp"):
                                            if primary_player.check_for_warlord(self.attacker_planet):
                                                if secondary_player.get_card_type_given_pos(
                                                        self.defender_planet, self.defender_position) == "Warlord":
                                                    attack_value = attack_value * 2
                                    if secondary_player.check_for_trait_given_pos(self.defender_planet,
                                                                                  self.defender_position, "Vehicle"):
                                        if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                                self.attacker_position) \
                                                == "Tankbusta Bommaz":
                                            attack_value = attack_value * 2
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
                                    self.attacker_location = (int(primary_player.number), self.attacker_planet,
                                                              self.attacker_position)
                                    if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                            self.attacker_position) \
                                            == "Burna Boyz":
                                        self.create_reaction("Burna Boyz", primary_player.name_player,
                                                             (int(primary_player.number), self.attacker_planet,
                                                              self.attacker_position))
                                    self.last_defender_position = (secondary_player.number,
                                                                   self.defender_planet, self.defender_position)
                                    if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                            self.attacker_position) \
                                            == "Torquemada Coteaz":
                                        primary_player.reset_card_name_misc_ability("Torquemada Coteaz")
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
                                        if took_damage:
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
