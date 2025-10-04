from .. import FindCard


async def update_game_event_command_section(self, name, game_update_string):
    print("Run command code.")
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif self.committing_warlords and not self.nectavus_active:
        print("Warlord assignment")
        if len(game_update_string) == 2:
            if game_update_string[0] == "PLANETS":
                print("Save warlord to this planet")
                if name == self.name_1:
                    if not self.p1.committed_warlord:
                        if self.p1.permitted_commit_locs_warlord[int(game_update_string[1])]:
                            self.p1.warlord_commit_location = int(game_update_string[1])
                            self.p1.committed_warlord = True
                            await self.send_update_message(self.name_1 + " has chosen a planet to commit "
                                                                         "their warlord.")
                            if self.p2.search_card_in_hq("Sautekh Royal Crypt", ready_relevant=True):
                                self.create_reaction("Sautekh Royal Crypt", self.name_2,
                                                     (2, -2, -1))
                            if self.p1.search_synapse_in_hq():
                                await self.send_update_message(self.name_1 + " has a synapse; please"
                                                                             " commit this as well")
                                self.p1.committed_synapse = False
                                self.p1.synapse_commit_location = -1
                        else:
                            await self.send_update_message(
                                self.name_1 + ", your warlord may not commit there this round!"
                            )
                            self.p1.illegal_commits_warlord += 1
                            if self.p1.illegal_commits_warlord > 4:
                                await self.send_update_message(
                                    "Automatically determining \"Most Legal\" warlord commit."
                                )
                                last_planet = 0
                                for i in range(len(self.planets_in_play_array)):
                                    if self.planets_in_play_array[i]:
                                        last_planet = i
                                current_target = last_planet
                                found_planet = False
                                while current_target > -1 and not found_planet:
                                    if not self.planets_in_play_array[current_target]:
                                        current_target = current_target - 1
                                    elif not self.p1.permitted_commit_locs_warlord[current_target]:
                                        current_target = current_target - 1
                                    else:
                                        found_planet = True
                                if not found_planet:
                                    current_target = last_planet
                                self.p1.warlord_commit_location = current_target
                                self.p1.committed_warlord = True
                                await self.send_update_message(self.name_1 + " has chosen a planet to commit "
                                                                             "their warlord.")
                                if self.p2.search_card_in_hq("Sautekh Royal Crypt", ready_relevant=True):
                                    self.create_reaction("Sautekh Royal Crypt", self.name_2,
                                                         (2, -2, -1))
                                if self.p1.search_synapse_in_hq():
                                    await self.send_update_message(self.name_1 + " has a synapse; please"
                                                                                 " commit this as well")
                                    self.p1.committed_synapse = False
                                    self.p1.synapse_commit_location = -1
                    elif not self.p1.committed_synapse:
                        self.p1.synapse_commit_location = int(game_update_string[1])
                        self.p1.committed_synapse = True
                        if self.p1.synapse_name == "Savage Warrior Prime" and \
                                self.p1.warlord_commit_location == self.p1.synapse_commit_location:
                            self.p1.synapse_commit_location = -1
                            self.p1.committed_synapse = False
                            await self.send_update_message(
                                "Savage Warrior Prime can't go to the same planet as your warlord. Pick again.")
                            self.p1.illegal_commits_synapse += 1
                            if self.p1.illegal_commits_synapse > 4:
                                await self.send_update_message(
                                    "Automatically determining \"Most Legal\" synapse commit."
                                )
                                last_planet = 0
                                for i in range(len(self.planets_in_play_array)):
                                    if self.planets_in_play_array[i]:
                                        last_planet = i
                                current_target = last_planet
                                found_planet = False
                                while current_target > -1 and not found_planet:
                                    if not self.planets_in_play_array[current_target]:
                                        current_target = current_target - 1
                                    elif current_target == self.p1.warlord_commit_location:
                                        current_target = current_target - 1
                                    else:
                                        found_planet = True
                                if not found_planet:
                                    current_target = last_planet
                                self.p1.synapse_commit_location = current_target
                                self.p1.committed_synapse = True
                                await self.send_update_message(self.name_1 + " has chosen a planet to commit "
                                                                             "their synapse.")
                        else:
                            await self.send_update_message(
                                self.name_1 + " has chosen a planet to commit their synapse.")
                else:
                    if not self.p2.committed_warlord:
                        if self.p2.permitted_commit_locs_warlord[int(game_update_string[1])]:
                            self.p2.warlord_commit_location = int(game_update_string[1])
                            self.p2.committed_warlord = True
                            await self.send_update_message(self.name_2 + " has chosen a planet to commit "
                                                                         "their warlord.")
                            if self.p1.search_card_in_hq("Sautekh Royal Crypt", ready_relevant=True):
                                self.create_reaction("Sautekh Royal Crypt", self.name_1,
                                                     (1, -2, -1))
                            if self.p2.search_synapse_in_hq():
                                await self.send_update_message(self.name_2 + " has a synapse; please"
                                                                             " commit this as well")
                                self.p2.committed_synapse = False
                                self.p2.synapse_commit_location = -1
                        else:
                            await self.send_update_message(
                                self.name_2 + ", your warlord may not commit there this round!"
                            )
                            self.p2.illegal_commits_warlord += 1
                            if self.p2.illegal_commits_warlord > 4:
                                await self.send_update_message(
                                    "Automatically determining \"Most Legal\" warlord commit."
                                )
                                last_planet = 0
                                for i in range(len(self.planets_in_play_array)):
                                    if self.planets_in_play_array[i]:
                                        last_planet = i
                                current_target = last_planet
                                found_planet = False
                                while current_target > -1 and not found_planet:
                                    if not self.planets_in_play_array[current_target]:
                                        current_target = current_target - 1
                                    elif not self.p2.permitted_commit_locs_warlord[current_target]:
                                        current_target = current_target - 1
                                    else:
                                        found_planet = True
                                if not found_planet:
                                    current_target = last_planet
                                self.p2.warlord_commit_location = current_target
                                self.p2.committed_warlord = True
                                await self.send_update_message(self.name_2 + " has chosen a planet to commit "
                                                                             "their warlord.")
                                if self.p1.search_card_in_hq("Sautekh Royal Crypt", ready_relevant=True):
                                    self.create_reaction("Sautekh Royal Crypt", self.name_1,
                                                         (1, -2, -1))
                                if self.p2.search_synapse_in_hq():
                                    await self.send_update_message(self.name_2 + " has a synapse; please"
                                                                                 " commit this as well")
                                    self.p2.committed_synapse = False
                                    self.p2.synapse_commit_location = -1
                    elif not self.p2.committed_synapse:
                        self.p2.synapse_commit_location = int(game_update_string[1])
                        self.p2.committed_synapse = True
                        if self.p2.synapse_name == "Savage Warrior Prime" and \
                                self.p2.warlord_commit_location == self.p2.synapse_commit_location:
                            self.p2.synapse_commit_location = -1
                            self.p2.committed_synapse = False
                            await self.send_update_message(
                                "Savage Warrior Prime can't go to the same planet as your warlord. Pick again.")
                            self.p2.illegal_commits_synapse += 1
                            if self.p2.illegal_commits_synapse > 4:
                                await self.send_update_message(
                                    "Automatically determining \"Most Legal\" synapse commit."
                                )
                                last_planet = 0
                                for i in range(len(self.planets_in_play_array)):
                                    if self.planets_in_play_array[i]:
                                        last_planet = i
                                current_target = last_planet
                                found_planet = False
                                while current_target > -1 and not found_planet:
                                    if not self.planets_in_play_array[current_target]:
                                        current_target = current_target - 1
                                    elif current_target == self.p2.warlord_commit_location:
                                        current_target = current_target - 1
                                    else:
                                        found_planet = True
                                if not found_planet:
                                    current_target = last_planet
                                self.p2.synapse_commit_location = current_target
                                self.p2.committed_synapse = True
                                await self.send_update_message(self.name_2 + " has chosen a planet to commit "
                                                                             "their synapse.")
                        else:
                            await self.send_update_message(
                                self.name_2 + " has chosen a planet to commit their synapse.")
                if self.p1.committed_warlord and self.p2.committed_warlord and \
                        self.p1.committed_synapse and self.p2.committed_synapse \
                        and not self.reactions_needing_resolving:
                    print("Both warlords need to be committed.")
                    if self.masters_of_the_webway:
                        temp = self.p1.warlord_commit_location
                        self.p1.warlord_commit_location = self.p2.warlord_commit_location
                        self.p2.warlord_commit_location = temp
                    print(self.p1.warlord_commit_location, self.p2.warlord_commit_location)
                    self.p1.commit_warlord_to_planet()
                    self.p2.commit_warlord_to_planet()
                    self.p1.resolve_enemy_warlord_committed_to_planet(self.p2.warlord_commit_location)
                    self.p2.resolve_enemy_warlord_committed_to_planet(self.p1.warlord_commit_location)
                    self.p1.commit_synapse_to_planet()
                    self.p2.commit_synapse_to_planet()
                    if self.p1.warlord_commit_location == self.p2.warlord_commit_location:
                        warlord_pla, warlord_pos = self.p1.get_location_of_warlord()
                        vael_relevant = False
                        if self.p1.search_card_in_hq("WAAAGH! Zanzag"):
                            self.create_reaction("WAAAGH! Zanzag", self.name_1, (1, -1, -1))
                        if self.p2.search_card_in_hq("WAAAGH! Zanzag"):
                            self.create_reaction("WAAAGH! Zanzag", self.name_2, (2, -1, -1))
                        if self.p1.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                                self.p1.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                            vael_relevant = True
                        elif self.p1.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" and \
                                not self.p1.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                            vael_relevant = True
                        if "The Blood Pits" in self.p1.cards or \
                                ("The Blood Pits" in self.p1.cards_removed_from_game and vael_relevant):
                            if self.p1.resources > 0:
                                self.create_reaction("The Blood Pits", self.name_1, (1, -1, -1))
                        warlord_pla, warlord_pos = self.p2.get_location_of_warlord()
                        vael_relevant = False
                        if self.p2.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                                self.p2.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                            vael_relevant = True
                        elif self.p2.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" and \
                                not self.p2.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                            vael_relevant = True
                        if "The Blood Pits" in self.p2.cards or \
                                ("The Blood Pits" in self.p2.cards_removed_from_game and vael_relevant):
                            if self.p2.resources > 0:
                                self.create_reaction("The Blood Pits", self.name_2, (2, -1, -1))
                    for i in range(len(self.p1.headquarters)):
                        if self.p1.get_card_type_given_pos(-2, i) == "Synapse":
                            self.create_reaction("Reinforced Synaptic Network", self.name_1, (1, -2, i))
                        if self.p1.get_ability_given_pos(-2, i) == "Heralding Cherubim":
                            self.create_reaction("Heralding Cherubim", self.name_1, (1, -2, i))
                    for i in range(len(self.p2.headquarters)):
                        if self.p2.get_card_type_given_pos(-2, i) == "Synapse":
                            self.create_reaction("Reinforced Synaptic Network", self.name_2, (2, -2, i))
                        if self.p2.get_ability_given_pos(-2, i) == "Heralding Cherubim":
                            self.create_reaction("Heralding Cherubim", self.name_2, (2, -2, i))
                    for i in range(7):
                        for j in range(len(self.p1.cards_in_play[i + 1])):
                            if self.p1.get_ability_given_pos(i, j) == "Heralding Cherubim":
                                self.create_reaction("Heralding Cherubim", self.name_1, (1, i, j))
                        for j in range(len(self.p2.cards_in_play[i + 1])):
                            if self.p2.get_ability_given_pos(i, j) == "Heralding Cherubim":
                                self.create_reaction("Heralding Cherubim", self.name_2, (2, i, j))
                    planets_committed_to = [self.p1.warlord_commit_location, self.p2.warlord_commit_location,
                                            self.p1.synapse_commit_location, self.p2.synapse_commit_location]
                    planets_committed_to = [x for x in planets_committed_to if x != -1]
                    warlord_planets_committed_to = [self.p1.warlord_commit_location, self.p2.warlord_commit_location]
                    warlord_planets_committed_to = [x for x in warlord_planets_committed_to if x != -1]
                    self.p1.phoenix_attack_fighter_triggers(planets_committed_to)
                    self.p2.phoenix_attack_fighter_triggers(planets_committed_to)
                    self.p1.create_warlord_committed_to_planet_reactions(warlord_planets_committed_to)
                    self.p2.create_warlord_committed_to_planet_reactions(warlord_planets_committed_to)
                    self.p1.has_passed = False
                    self.p2.has_passed = False
                    self.committing_warlords = False
                    self.before_command_struggle = True
                    await self.send_update_message("Both players are given a chance to resolve "
                                                   "cards/reactions before the command struggle.")
    elif self.before_command_struggle:
        print("Before command struggle")
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if name == self.name_1:
                    self.p1.has_passed = True
                    await self.send_update_message(self.name_1 + " is ready to start the command struggle.")
                elif name == self.name_2:
                    self.p2.has_passed = True
                    await self.send_update_message(self.name_2 + " is ready to start the command struggle.")
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                if name == self.name_1:
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
                if game_update_string[1] == primary_player.get_number():
                    hand_pos = int(game_update_string[2])
                    if primary_player.cards[hand_pos] == "Foresight":
                        if secondary_player.nullify_check() and self.nullify_enabled:
                            await self.send_update_message(
                                primary_player.name_player + " wants to play Foresight; "
                                                             "Nullify window offered.")
                            self.choices_available = ["Yes", "No"]
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Use Nullify?"
                            self.nullified_card_pos = int(game_update_string[2])
                            self.nullified_card_name = "Foresight"
                            self.cost_card_nullified = 1
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Foresight"
                        elif primary_player.spend_resources(1):
                            warlord_planet = primary_player.warlord_commit_location
                            self.positions_of_unit_triggering_reaction.append([int(primary_player.get_number()),
                                                                               warlord_planet, -1])
                            self.reactions_needing_resolving.append("Foresight")
                            self.player_who_resolves_reaction.append(primary_player.name_player)
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif primary_player.cards[hand_pos] == "Sweep Attack":
                        if secondary_player.nullify_check() and self.nullify_enabled:
                            await self.send_update_message(
                                primary_player.name_player + " wants to play Sweep Attack; "
                                                             "Nullify window offered.")
                            self.choices_available = ["Yes", "No"]
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Use Nullify?"
                            self.nullified_card_pos = int(game_update_string[2])
                            self.nullified_card_name = "Sweep Attack"
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Sweep Attack"
                        else:
                            warlord_planet = primary_player.warlord_commit_location
                            self.positions_of_unit_triggering_reaction.append([int(primary_player.get_number()),
                                                                               warlord_planet, -1])
                            self.reactions_needing_resolving.append("Sweep Attack")
                            self.player_who_resolves_reaction.append(primary_player.name_player)
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    elif primary_player.cards[hand_pos] == "Blackmane's Hunt":
                        if secondary_player.nullify_check() and self.nullify_enabled:
                            await self.send_update_message(
                                primary_player.name_player + " wants to play Blackmane's Hunt; "
                                                             "Nullify window offered.")
                            self.choices_available = ["Yes", "No"]
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Use Nullify?"
                            self.nullified_card_pos = int(game_update_string[2])
                            self.nullified_card_name = "Blackmane's Hunt"
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Blackmane's Hunt"
                        else:
                            warlord_planet = primary_player.warlord_commit_location
                            self.positions_of_unit_triggering_reaction.append([int(primary_player.get_number()),
                                                                               warlord_planet, -1])
                            self.reactions_needing_resolving.append("Blackmane's Hunt")
                            self.player_who_resolves_reaction.append(primary_player.name_player)
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
    elif self.during_command_struggle:
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if name == self.name_1:
                    self.p1.has_passed = True
                    await self.send_update_message(self.name_1 + " does not wish to use an ability.")
                elif name == self.name_2:
                    self.p2.has_passed = True
                    await self.send_update_message(self.name_2 + " does not wish to use an ability.")
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                if name == self.name_1:
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
                if self.interrupts_before_cs_allowed:
                    if game_update_string[1] == primary_player.get_number():
                        hand_pos = int(game_update_string[2])
                        if primary_player.cards[hand_pos] == "Superiority":
                            cost = 1
                            if primary_player.urien_relevant:
                                cost += 1
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.send_update_message(
                                    primary_player.name_player + " wants to play Superiority; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = int(game_update_string[2])
                                self.nullified_card_name = "Superiority"
                                self.cost_card_nullified = cost
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "Superiority"
                            elif primary_player.spend_resources(cost):
                                self.create_reaction("Superiority", primary_player.name_player,
                                                     (int(primary_player.get_number()), -1, -1))
                                primary_player.aiming_reticle_color = "blue"
                                primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        elif primary_player.cards[hand_pos] == "War of Ideas":
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.send_update_message(
                                    primary_player.name_player + " wants to play Superiority; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = int(game_update_string[2])
                                self.nullified_card_name = "War of Ideas"
                                self.cost_card_nullified = 0
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "War of Ideas"
                            else:
                                primary_player.discard_card_from_hand(hand_pos)
                                await self.send_update_message(primary_player.name_player + " activated War of Ideas!")
                                primary_player.war_of_ideas_active = True
                elif self.interrupts_during_cs_allowed:
                    if game_update_string[1] == primary_player.get_number():
                        hand_pos = int(game_update_string[2])
                        if primary_player.cards[hand_pos] == "Wraithguard Revenant":
                            if self.get_green_icon(self.last_planet_checked_command_struggle):
                                card = primary_player.get_card_in_hand(hand_pos)
                                primary_player.add_card_to_planet(card, self.last_planet_checked_command_struggle)
                                del primary_player.cards[hand_pos]
                                self.p1.has_passed = True
                                self.p2.has_passed = True
                                self.canceled_resource_bonuses[self.last_planet_checked_command_struggle] = True
                                self.canceled_card_bonuses[self.last_planet_checked_command_struggle] = True
            elif game_update_string[0] == "IN_DISCARD":
                if name == self.name_1:
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
                if self.interrupts_during_cs_allowed:
                    if game_update_string[1] == primary_player.get_number():
                        discard_pos = int(game_update_string[2])
                        if primary_player.discard[discard_pos] == "Wraithguard Revenant":
                            if self.get_green_icon(self.last_planet_checked_command_struggle):
                                card = primary_player.get_card_in_discard(discard_pos)
                                primary_player.add_card_to_planet(card, self.last_planet_checked_command_struggle)
                                del primary_player.discard[discard_pos]
                                self.p1.has_passed = True
                                self.p2.has_passed = True
                                self.canceled_resource_bonuses[self.last_planet_checked_command_struggle] = True
                                self.canceled_card_bonuses[self.last_planet_checked_command_struggle] = True
            elif game_update_string[0] == "HQ":
                if name == self.name_1:
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
                if self.interrupts_before_cs_allowed:
                    pass
                if self.interrupts_during_cs_allowed:
                    if game_update_string[1] == primary_player.get_number():
                        unit_pos = int(game_update_string[2])
                        if primary_player.get_ability_given_pos(-2, unit_pos) == "Archon's Palace":
                            if primary_player.get_ready_given_pos(-2, unit_pos):
                                primary_player.exhaust_given_pos(-2, unit_pos, card_effect=True)
                                self.mode = "ACTION"
                                self.action_chosen = "Archon's Palace"
                                self.player_with_action = primary_player.name_player
                                self.misc_target_planet = self.last_planet_checked_command_struggle
                                self.choices_available = ["Cards", "Resources"]
                                self.choice_context = "Archon's Palace"
                                self.name_player_making_choices = primary_player.name_player
                                self.position_of_actioned_card = (-2, unit_pos)
                                primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                        elif primary_player.get_ability_given_pos(-2, unit_pos) == "The Duke of Debris":
                            if not primary_player.get_once_per_phase_used_given_pos(-2, unit_pos):
                                planet_pos = -2
                                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
                                self.resolving_search_box = True
                                self.what_to_do_with_searched_card = "DRAW"
                                self.traits_of_searched_card = None
                                self.card_type_of_searched_card = None
                                self.faction_of_searched_card = None
                                self.max_cost_of_searched_card = 999
                                self.all_conditions_searched_card_required = True
                                self.no_restrictions_on_chosen_card = False
                                self.canceled_card_bonuses[self.last_planet_checked_command_struggle] = True
                                primary_player.number_cards_to_search = 2
                                for i in range(len(primary_player.headquarters)):
                                    if primary_player.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                                        if primary_player.headquarters[i].counter > 0:
                                            primary_player.number_cards_to_search += 2
                                if len(primary_player.deck) < primary_player.number_cards_to_search:
                                    primary_player.number_cards_to_search = len(primary_player.deck)
                                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                                self.name_player_who_is_searching = primary_player.name_player
                                self.number_who_is_searching = primary_player.number
        elif len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                if name == self.name_1:
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
                if self.interrupts_before_cs_allowed:
                    pass
                if self.interrupts_during_cs_allowed:
                    if game_update_string[1] == primary_player.get_number():
                        planet_pos = int(game_update_string[2])
                        unit_pos = int(game_update_string[3])
                        if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "The Duke of Debris":
                            if not primary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos):
                                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
                                self.resolving_search_box = True
                                self.what_to_do_with_searched_card = "DRAW"
                                self.traits_of_searched_card = None
                                self.card_type_of_searched_card = None
                                self.faction_of_searched_card = None
                                self.max_cost_of_searched_card = 999
                                self.all_conditions_searched_card_required = True
                                self.no_restrictions_on_chosen_card = False
                                primary_player.number_cards_to_search = 2
                                for i in range(len(primary_player.headquarters)):
                                    if primary_player.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                                        if primary_player.headquarters[i].counter > 0:
                                            primary_player.number_cards_to_search += 2
                                self.canceled_card_bonuses[self.last_planet_checked_command_struggle] = True
                                if len(primary_player.deck) < primary_player.number_cards_to_search:
                                    primary_player.number_cards_to_search = len(primary_player.deck)
                                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                                self.name_player_who_is_searching = primary_player.name_player
                                self.number_who_is_searching = primary_player.number
    elif self.after_command_struggle:
        print("After command struggle")
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if name == self.name_1:
                    self.p1.has_passed = True
                    await self.send_update_message(self.name_1 + " is ready to end the command phase.")
                elif name == self.name_2:
                    self.p2.has_passed = True
                    await self.send_update_message(self.name_2 + " is ready to end the command phase.")
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
    if self.p1.has_passed and self.p2.has_passed:
        print("Both passed")
        if self.before_command_struggle:
            self.before_command_struggle = False
            self.during_command_struggle = True
            self.last_planet_checked_command_struggle = self.round_number
            self.total_gains_command_struggle = [None, None, None, None, None, None, None]
            ret_val = try_entire_command(self, self.last_planet_checked_command_struggle)
            await interpret_command_state(self, ret_val)
        elif self.during_command_struggle:
            if self.interrupts_before_cs_allowed:
                self.interrupts_before_cs_allowed = False
            elif self.interrupts_during_cs_allowed:
                self.interrupts_during_cs_allowed = False
            ret_val = try_entire_command(self, self.last_planet_checked_command_struggle)
            await interpret_command_state(self, ret_val)
        elif self.after_command_struggle:
            self.before_command_struggle = False
            self.after_command_struggle = False
            await self.change_phase("COMBAT")
            self.actions_between_battle = True
            self.last_planet_checked_for_battle = -1
            self.p1.has_passed = False
            self.p2.has_passed = False
            self.p1.set_available_mobile_all(True)
            self.p2.set_available_mobile_all(True)
            self.p1.mobile_resolved = False
            self.p2.mobile_resolved = False
            if not self.p1.search_cards_for_available_mobile():
                self.p1.mobile_resolved = True
            if not self.p2.search_cards_for_available_mobile():
                self.p2.mobile_resolved = True
            if self.p1.mobile_resolved and self.p2.mobile_resolved:
                await self.send_update_message("Window granted for players to use "
                                               "reactions/actions before the battle begins.")
        elif self.nectavus_active:
            ret_val = try_entire_command(self, self.nectavus_target)
            await interpret_command_state(self, ret_val)


async def interpret_command_state(self, ret_val):
    if ret_val == "COMPLETE":
        receive_winnings(self)
        self.planet_aiming_reticle_position = -1
        if not self.nectavus_active:
            self.after_command_struggle = True
        self.during_command_struggle = False
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.resolve_remaining_cs_after_reactions = False
        if not self.nectavus_active:
            await self.send_update_message("Window given for actions after command struggle.")
        if self.nectavus_active:
            self.nectavus_active = False
    elif ret_val == "INTERRUPT PRE STRUGGLE":
        message = "Window given for effects pre-command struggle at " + \
                  self.planet_array[self.last_planet_checked_command_struggle] + "."
        await self.send_update_message(message)
    elif ret_val == "INTERRUPT DURING STRUGGLE":
        message = "Window given for effects mid-command struggle at " + \
                  self.planet_array[self.last_planet_checked_command_struggle] + "."
        await self.send_update_message(message)
    elif ret_val == "REACTIONS":
        message = "Reactions need resolving before command struggles may continue."
        await self.send_update_message(message)


def try_entire_command(self, planet_pos):
    self.planet_aiming_reticle_position = planet_pos
    if planet_pos > 6:
        return "COMPLETE"
    if self.nectavus_active:
        if planet_pos > self.nectavus_target:
            return "COMPLETE"
    if not self.planets_in_play_array[planet_pos]:
        return try_entire_command(self, planet_pos + 1)
    if self.interrupts_before_cs_allowed:
        self.p1.has_passed = False
        self.p2.has_passed = False
        if self.p1.search_hand_for_card("Superiority") and self.p2.count_command_at_planet(planet_pos) > 0:
            cost = 1
            if self.p1.urien_relevant:
                cost += 1
            if self.p1.resources >= cost:
                return "INTERRUPT PRE STRUGGLE"
        elif self.p1.search_hand_for_card("War of Ideas"):
            for i in range(len(self.p1.cards_in_play[planet_pos])):
                if not self.p1.get_ready_given_pos(planet_pos, i):
                    return "INTERRUPT PRE STRUGGLE"
        elif self.p2.search_hand_for_card("Superiority") and self.p1.count_command_at_planet(planet_pos) > 0:
            cost = 1
            if self.p2.urien_relevant:
                cost += 1
            if self.p2.resources >= cost:
                return "INTERRUPT PRE STRUGGLE"
        elif self.p2.search_hand_for_card("War of Ideas"):
            for i in range(len(self.p2.cards_in_play[planet_pos])):
                if not self.p2.get_ready_given_pos(planet_pos, i):
                    return "INTERRUPT PRE STRUGGLE"
    name_winner = determine_winner_command_struggle(self, planet_pos)
    if self.interrupts_during_cs_allowed:
        self.interrupts_before_cs_allowed = False
        self.p1.has_passed = False
        self.p2.has_passed = False
        if name_winner == "":
            pass
        elif name_winner == self.name_1:
            if self.get_green_icon(planet_pos):
                if self.p1.search_hand_for_card("Wraithguard Revenant"):
                    return "INTERRUPT DURING STRUGGLE"
                if self.p1.search_discard_for_card("Wraithguard Revenant"):
                    return "INTERRUPT DURING STRUGGLE"
            if self.p1.search_for_card_everywhere("The Duke of Debris", limit_phase_rel=True):
                return "INTERRUPT DURING STRUGGLE"
            if self.p2.search_card_in_hq("Archon's Palace", ready_relevant=True):
                return "INTERRUPT DURING STRUGGLE"
            warlord_pla, warlord_pos = self.p2.get_location_of_warlord()
            auto_interrupts = False
            if self.p2.get_ability_given_pos(warlord_pla, warlord_pos) == "Shaper Agnok":
                if self.p2.check_for_trait_at_planet(planet_pos, "Kroot"):
                    self.create_interrupt("Shaper Agnok", self.name_2, (2, -1, -1))
                    auto_interrupts = True
            tau_present = False
            for i in range(len(self.p2.cards_in_play[planet_pos + 1])):
                if self.p2.get_faction_given_pos(planet_pos, i) == "Tau":
                    tau_present = True
            if tau_present:
                if self.p2.search_for_card_everywhere("Arrangement at Elova IV"):
                    self.create_interrupt("Arrangement at Elova IV", self.name_2, (2, -1, -1))
                    auto_interrupts = True
            if auto_interrupts:
                return "INTERRUPT DURING STRUGGLE"
        elif name_winner == self.name_2:
            if self.get_green_icon(planet_pos):
                if self.p2.search_hand_for_card("Wraithguard Revenant"):
                    return "INTERRUPT DURING STRUGGLE"
                if self.p2.search_discard_for_card("Wraithguard Revenant"):
                    return "INTERRUPT DURING STRUGGLE"
            if self.p2.search_for_card_everywhere("The Duke of Debris", limit_phase_rel=True):
                return "INTERRUPT DURING STRUGGLE"
            if self.p1.search_card_in_hq("Archon's Palace", ready_relevant=True):
                return "INTERRUPT DURING STRUGGLE"
            warlord_pla, warlord_pos = self.p1.get_location_of_warlord()
            auto_interrupts = False
            if self.p1.get_ability_given_pos(warlord_pla, warlord_pos) == "Shaper Agnok":
                if self.p1.check_for_trait_at_planet(planet_pos, "Kroot"):
                    self.create_interrupt("Shaper Agnok", self.name_1, (1, -1, -1))
                    auto_interrupts = True
            tau_present = False
            for i in range(len(self.p1.cards_in_play[planet_pos + 1])):
                if self.p1.get_faction_given_pos(planet_pos, i) == "Tau":
                    tau_present = True
            if tau_present:
                if self.p1.search_for_card_everywhere("Arrangement at Elova IV"):
                    self.create_interrupt("Arrangement at Elova IV", self.name_1, (1, -1, -1))
                    auto_interrupts = True
            if auto_interrupts:
                return "INTERRUPT DURING STRUGGLE"
    winnings = None
    if name_winner == self.name_1:
        winnings = resolve_winnings(self, self.p1, self.p2, planet_pos)
    elif name_winner == self.name_2:
        winnings = resolve_winnings(self, self.p2, self.p1, planet_pos)
    self.total_gains_command_struggle[planet_pos] = winnings
    self.last_planet_checked_command_struggle += 1
    self.interrupts_during_cs_allowed = True
    self.interrupts_before_cs_allowed = True
    self.p1.clear_effects_end_of_cs()
    self.p2.clear_effects_end_of_cs()
    if not self.reactions_needing_resolving:
        return try_entire_command(self, self.last_planet_checked_command_struggle)
    self.resolve_remaining_cs_after_reactions = True
    return "REACTIONS"


def receive_winnings(self):
    for i in range(len(self.total_gains_command_struggle)):
        if self.total_gains_command_struggle[i] is not None:
            if (self.total_gains_command_struggle[i][0] == "1" and not self.nectavus_active) or\
                    (self.total_gains_command_struggle[i][0] == "2" and self.nectavus_active):
                self.p1.command_struggles_won_this_phase += 1
                self.p1.add_resources(self.total_gains_command_struggle[i][1])
                for _ in range(self.total_gains_command_struggle[i][2]):
                    self.p1.draw_card()
            elif (self.total_gains_command_struggle[i][0] == "2" and not self.nectavus_active) or\
                    (self.total_gains_command_struggle[i][0] == "1" and self.nectavus_active):
                self.p2.command_struggles_won_this_phase += 1
                self.p2.add_resources(self.total_gains_command_struggle[i][1])
                for _ in range(self.total_gains_command_struggle[i][2]):
                    self.p2.draw_card()


def resolve_winnings(self, winner, loser, planet_id):
    chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
    while winner.sac_altar_rewards[planet_id] > 0:
        winner.sac_altar_rewards[planet_id] = winner.sac_altar_rewards[planet_id] - 1
        winner.draw_card()
        winner.add_resources(1)
    winner.won_command_struggles_planets_round[planet_id] = True
    resources_won = chosen_planet.get_resources()
    cards_won = chosen_planet.get_cards()
    extra_resources, extra_cards = winner.get_bonus_winnings_at_planet(planet_id)
    resources_won += extra_resources
    cards_won += extra_cards
    if self.canceled_resource_bonuses[planet_id]:
        resources_won = 0
    if self.canceled_card_bonuses[planet_id]:
        cards_won = 0
    ret_val = [winner.number, resources_won, cards_won]
    already_noxious = False
    if winner.search_card_in_hq("Omega Zero Command"):
        self.create_reaction("Omega Zero Command", winner.name_player, (int(winner.get_number()), planet_id, -1))
    if loser.search_card_in_hq("Humanity's Shield"):
        self.create_reaction("Humanity's Shield", loser.name_player, (int(loser.get_number()), planet_id, -1))
    if self.infested_planets[planet_id]:
        for i in range(len(self.planet_array)):
            for j in range(len(winner.cards_in_play[i + 1])):
                if winner.get_ability_given_pos(i, j) == "Devourer Venomthrope":
                    self.create_reaction("Devourer Venomthrope", winner.name_player,
                                         (int(winner.get_number()), i, j))
    for i in range(len(winner.cards_in_play[planet_id + 1])):
        if winner.cards_in_play[planet_id + 1][i].get_ability() == "Soul Grinder":
            self.create_reaction("Soul Grinder", winner.name_player, (int(winner.get_number()), planet_id, i))
        if winner.cards_in_play[planet_id + 1][i].get_ability() == "Toxic Venomthrope":
            self.create_reaction("Toxic Venomthrope", winner.name_player, (int(winner.get_number()), planet_id, i))
        if winner.cards_in_play[planet_id + 1][i].get_ability() == "Caustic Tyrannofex":
            self.create_reaction("Caustic Tyrannofex", winner.name_player, (int(winner.get_number()), planet_id, i))
        if winner.check_for_trait_given_pos(planet_id, i, "Kabalite"):
            if winner.get_card_type_given_pos(planet_id, i) == "Army":
                if winner.search_card_in_hq("Raiding Portal", ready_relevant=True):
                    self.create_reaction("Raiding Portal", winner.name_player,
                                         (int(winner.get_number()), planet_id, -1))
        attachments = winner.cards_in_play[planet_id + 1][i].get_attachments()
        for j in range(len(attachments)):
            if attachments[j].get_ability() == "Noxious Fleshborer" and not attachments[j].from_magus_harid:
                if not already_noxious and not self.infested_planets[planet_id]:
                    already_noxious = True
                    own = attachments[j].name_owner
                    self.create_reaction("Noxious Fleshborer", own, (int(winner.number), planet_id, i))
            if attachments[j].get_ability() == "Staff of Change":
                own = attachments[j].name_owner
                if own == winner.name_player:
                    self.create_reaction("Staff of Change", own, (int(winner.get_number()), planet_id, i))
    return ret_val


def determine_winner_command_struggle(self, planet_id):
    fbk_1 = self.p1.search_card_at_planet(planet_id, "Freebooter Kaptain")
    fbk_2 = self.p2.search_card_at_planet(planet_id, "Freebooter Kaptain")
    command_p1 = self.p1.count_command_at_planet(planet_id, fbk=fbk_2, actual_cs=True)
    command_p2 = self.p2.count_command_at_planet(planet_id, fbk=fbk_1, actual_cs=True)
    if command_p1 > command_p2:
        return self.name_1
    elif command_p2 > command_p1:
        return self.name_2
    return ""
