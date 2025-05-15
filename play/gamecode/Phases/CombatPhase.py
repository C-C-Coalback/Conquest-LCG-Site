async def update_game_event_combat_section(self, name, game_update_string):
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
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
            if name == self.player_with_combat_turn:
                if self.number_with_combat_turn == "1":
                    self.number_with_combat_turn = "2"
                    self.player_with_combat_turn = self.name_2
                    self.p1.has_passed = True
                    self.reset_combat_positions()
                else:
                    self.number_with_combat_turn = "1"
                    self.player_with_combat_turn = self.name_1
                    self.p2.has_passed = True
                    self.reset_combat_positions()
                if self.p1.has_passed and self.p2.has_passed:
                    if self.mode == "Normal":
                        if self.ranged_skirmish_active:
                            print("Both players passed, end ranged skirmish")
                            self.p1.has_passed = False
                            self.p2.has_passed = False
                            self.reset_combat_turn()
                            self.ranged_skirmish_active = False
                        else:
                            print("Both players passed, need to run combat round end.")
                            self.p1.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.p2.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.p1.has_passed = False
                            self.p2.has_passed = False
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
                                await self.aoe_routine(primary_player, secondary_player, chosen_planet,
                                                       amount_aoe, faction=faction)
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
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            print("Unit clicked on.")
            if name == self.player_with_combat_turn:
                if self.mode == "RETREAT":
                    if game_update_string[1] == self.number_with_combat_turn:
                        chosen_planet = int(game_update_string[2])
                        chosen_unit = int(game_update_string[3])
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
                        if chosen_planet == self.last_planet_checked_for_battle:
                            if self.number_with_combat_turn == "1":
                                player = self.p1
                            else:
                                player = self.p2
                            can_continue = False
                            if self.ranged_skirmish_active:
                                is_ranged = player.get_ranged_given_pos(chosen_planet, chosen_unit)
                                if is_ranged:
                                    can_continue = True
                            else:
                                can_continue = True
                            if can_continue:
                                is_ready = player.check_ready_pos(chosen_planet, chosen_unit)
                                if is_ready:
                                    if player.cards_in_play[chosen_planet + 1][chosen_unit]\
                                            .get_card_type() == "Warlord":
                                        self.choices_available = ["Yes", "No"]
                                        self.choice_context = "Retreat Warlord?"
                                        self.name_player_making_choices = player.name_player
                                        self.resolving_search_box = True
                                    print("Unit ready, can be used")
                                    valid_unit = True
                                    player.cards_in_play[chosen_planet + 1][chosen_unit].resolving_attack = True
                                    player.set_aiming_reticle_in_play(chosen_planet, chosen_unit, "blue")
                                else:
                                    print("Unit not ready")
                        if valid_unit:
                            self.attacker_planet = chosen_planet
                            self.attacker_position = chosen_unit
                            self.may_move_defender = True
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
                                player.cards_in_play[self.attacker_planet + 1][self.attacker_position].\
                                    ethereal_movement_active = True
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Biel-Tan Warp Spiders":
                                self.choices_available = ["Own deck", "Enemy deck"]
                                self.name_player_making_choices = player.name_player
                                self.choice_context = "Which deck to use Biel-Tan Warp Spiders:"
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Flayed Ones Pack":
                                for _ in range(3):
                                    player.discard_top_card_deck()
                            if player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                    == "Ku'gath Plaguefather":
                                self.create_reaction("Ku'gath Plaguefather", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.get_ability_given_pos(chosen_planet, self.attacker_position) \
                                    == "Wailing Wraithfighter":
                                self.create_reaction("Wailing Wraith Fighter", player.name_player,
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
                                                                "Banshee Power Sword"):
                                self.create_reaction("Banshee Power Sword", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                            if player.search_attachments_at_pos(self.attacker_planet, self.attacker_position,
                                                                "The Plaguefather's Banner"):
                                self.create_reaction("The Plaguefather's Banner", player.name_player,
                                                     (int(player.number), self.attacker_planet,
                                                      self.attacker_position))
                elif self.defender_position == -1:
                    if game_update_string[1] != self.number_with_combat_turn:
                        armorbane_check = False
                        self.defender_planet = int(game_update_string[2])
                        self.defender_position = int(game_update_string[3])
                        print("Defender:", self.defender_planet, self.defender_position)
                        if self.number_with_combat_turn == "1":
                            primary_player = self.p1
                            secondary_player = self.p2
                        else:
                            primary_player = self.p2
                            secondary_player = self.p1
                        attack_value = primary_player.get_attack_given_pos(self.attacker_planet,
                                                                           self.attacker_position)
                        can_continue = True
                        if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position] \
                                .get_ability() == "Honored Librarian":
                            for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                if secondary_player.cards_in_play[self.defender_planet + 1][i] \
                                        .get_ability() != "Honored Librarian":
                                    can_continue = False
                        if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position] \
                                .get_ability() != "Lychguard Sentinel" or\
                                not secondary_player.get_ready_given_pos(self.defender_planet, self.defender_position):
                            for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                if secondary_player.cards_in_play[self.defender_planet + 1][i] \
                                        .get_ability() == "Lychguard Sentinel" and \
                                        secondary_player.get_ready_given_pos(self.defender_planet, i):
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
                                            self.last_defender_position = (self.defender_planet, self.defender_position)
                                            secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                        self.defender_position, "red")
                        if can_continue:
                            if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                    self.attacker_position) == "Starbane's Council":
                                if not secondary_player.get_ready_given_pos(self.defender_planet,
                                                                            self.defender_position):
                                    attack_value += 2
                            if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position]\
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
                                if primary_player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                        == "Roghrax Bloodhand":
                                    if self.bloodthirst_active[self.attacker_planet]:
                                        attack_value = attack_value * 2
                                self.attacker_location = (int(primary_player.number), self.attacker_planet,
                                                          self.attacker_position)
                                if primary_player.get_ability_given_pos(self.attacker_planet, self.attacker_position) \
                                        == "Burna Boyz":
                                    self.reactions_needing_resolving.append("Burna Boyz")
                                    self.positions_of_unit_triggering_reaction.append([int(primary_player.number),
                                                                                       self.attacker_planet,
                                                                                       self.attacker_position])
                                    self.player_who_resolves_reaction.append(primary_player.name_player)
                                    self.last_defender_pos = (self.defender_planet, self.defender_position)
                                can_shield = not primary_player.get_armorbane_given_pos(self.attacker_planet,
                                                                                        self.attacker_position)
                                took_damage, bodyguards = secondary_player.assign_damage_to_pos(
                                    self.defender_planet, self.defender_position, damage=attack_value,
                                    att_pos=self.attacker_location, can_shield=can_shield
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
                                                                                        self.defender_position, "red")
                                        else:
                                            secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                        self.defender_position, "blue")
                                    self.damage_from_attack = True
                            else:
                                primary_player.reset_aiming_reticle_in_play(self.attacker_planet,
                                                                            self.attacker_position)

                            self.reset_combat_positions()
                            self.number_with_combat_turn = secondary_player.get_number()
                            self.player_with_combat_turn = secondary_player.get_name_player()
                            if self.unit_will_move_after_attack:
                                self.need_to_move_to_hq = True
                        else:
                            self.defender_planet = -1
                            self.defender_position = -1
