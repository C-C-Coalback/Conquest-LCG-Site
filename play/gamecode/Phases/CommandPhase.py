from .. import FindCard


async def update_game_event_command_section(self, name, game_update_string):
    print("Run command code.")
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif self.committing_warlords:
        print("Warlord assignment")
        if len(game_update_string) == 2:
            if game_update_string[0] == "PLANETS":
                print("Save warlord to this planet")
                if name == self.name_1:
                    if not self.p1.committed_warlord:
                        self.p1.warlord_commit_location = int(game_update_string[1])
                        self.p1.committed_warlord = True
                        await self.send_update_message(self.name_1 + " has chosen a planet to commit "
                                                                     "their warlord.")
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
                        else:
                            await self.send_update_message(
                                self.name_1 + " has chosen a planet to commit their synapse.")

                else:
                    if not self.p2.committed_warlord:
                        self.p2.warlord_commit_location = int(game_update_string[1])
                        self.p2.committed_warlord = True
                        await self.send_update_message(self.name_2 + " has chosen a planet to commit "
                                                                     "their warlord.")
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
                        else:
                            await self.send_update_message(
                                self.name_2 + " has chosen a planet to commit their synapse.")
                if self.p1.committed_warlord and self.p2.committed_warlord and \
                        self.p1.committed_synapse and self.p2.committed_synapse:
                    print("Both warlords need to be committed.")
                    print(self.p1.warlord_commit_location, self.p2.warlord_commit_location)
                    self.p1.commit_warlord_to_planet()
                    self.p2.commit_warlord_to_planet()
                    self.p1.commit_synapse_to_planet()
                    self.p2.commit_synapse_to_planet()
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
                elif name == self.name_2:
                    self.p2.has_passed = True
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HQ":
                if name == self.name_1:
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
                if game_update_string[1] == primary_player.get_number():
                    unit_pos = int(game_update_string[2])
                    if primary_player.get_ability_given_pos(-2, unit_pos) == "Archon's Palace":
                        if primary_player.get_ready_given_pos(-2, unit_pos):
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.mode = "ACTION"
                            self.action_chosen = "Archon's Palace"
                            self.player_with_action = primary_player.name_player
                            self.position_of_actioned_card = (-2, unit_pos)
                            primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
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
                    elif primary_player.cards[hand_pos] == "Superiority":
                        if secondary_player.nullify_check() and self.nullify_enabled:
                            await self.send_update_message(
                                primary_player.name_player + " wants to play Superiority; "
                                                             "Nullify window offered.")
                            self.choices_available = ["Yes", "No"]
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Use Nullify?"
                            self.nullified_card_pos = int(game_update_string[2])
                            self.nullified_card_name = "Superiority"
                            self.cost_card_nullified = 1
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Superiority"
                        elif primary_player.spend_resources(1):
                            self.positions_of_unit_triggering_reaction.append([int(primary_player.get_number()),
                                                                               -1, -1])
                            self.reactions_needing_resolving.append("Superiority")
                            self.player_who_resolves_reaction.append(primary_player.name_player)
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
    elif self.after_command_struggle:
        print("After command struggle")
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if name == self.name_1:
                    self.p1.has_passed = True
                elif name == self.name_2:
                    self.p2.has_passed = True
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
            resolve_command_struggle(self)
            self.before_command_struggle = False
            self.after_command_struggle = True
            self.p1.has_passed = False
            self.p2.has_passed = False
            await self.send_update_message("Window given for actions after command struggle.")
        elif self.after_command_struggle:
            self.before_command_struggle = False
            self.after_command_struggle = False
            await self.change_phase("COMBAT")
            self.p1.set_available_mobile_all(True)
            self.p2.set_available_mobile_all(True)
            self.p1.mobile_resolved = False
            self.p2.mobile_resolved = False
            if not self.p1.search_cards_for_available_mobile():
                self.p1.mobile_resolved = True
            if not self.p2.search_cards_for_available_mobile():
                self.p2.mobile_resolved = True
            if self.p1.mobile_resolved and self.p2.mobile_resolved:
                self.check_battle(self.round_number)
                self.begin_battle(self.round_number)
                self.begin_combat_round()
                self.set_battle_initiative()
                self.planet_aiming_reticle_active = True
                self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
                self.p1.has_passed = False
                self.p2.has_passed = False


def resolve_command_struggle(self):
    storage_command_struggle = [None, None, None, None, None, None, None]
    for i in range(len(self.planet_array)):
        if self.planets_in_play_array[i]:
            print("Resolve command struggle at:", self.planet_array[i])
            storage_command_struggle[i] = resolve_command_struggle_at_planet(self, i)
    for i in range(len(storage_command_struggle)):
        if storage_command_struggle[i] is not None:
            if storage_command_struggle[i][0] == "1":
                self.p1.add_resources(storage_command_struggle[i][1])
                for _ in range(storage_command_struggle[i][2]):
                    self.p1.draw_card()
            else:
                self.p2.add_resources(storage_command_struggle[i][1])
                for _ in range(storage_command_struggle[i][2]):
                    self.p2.draw_card()


def resolve_command_struggle_at_planet(self, planet_id):
    fbk_1 = self.p1.search_card_at_planet(planet_id, "Freebooter Kaptain")
    fbk_2 = self.p2.search_card_at_planet(planet_id, "Freebooter Kaptain")
    command_p1 = self.p1.count_command_at_planet(planet_id, fbk=fbk_2)
    command_p2 = self.p2.count_command_at_planet(planet_id, fbk=fbk_1)
    if command_p1 > command_p2:
        print("P1 wins command")
        chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
        if self.canceled_resource_bonuses[planet_id]:
            resources_won = 0
        else:
            resources_won = chosen_planet.get_resources()
        if self.canceled_card_bonuses[planet_id]:
            cards_won = 0
        else:
            cards_won = chosen_planet.get_cards()
        extra_resources, extra_cards = self.p1.get_bonus_winnings_at_planet(planet_id)
        resources_won += extra_resources
        cards_won += extra_cards
        ret_val = ["1", resources_won, cards_won]
        already_noxious = False
        if self.p1.search_card_in_hq("Omega Zero Command"):
            self.p1.summon_token_at_planet("Guardsman", planet_id)
        for i in range(len(self.p1.cards_in_play[planet_id + 1])):
            if self.p1.cards_in_play[planet_id + 1][i].get_ability() == "Soul Grinder":
                self.p1.set_aiming_reticle_in_play(planet_id, i, "blue")
                self.positions_of_unit_triggering_reaction.append(["1", planet_id, i])
                self.reactions_needing_resolving.append("Soul Grinder")
                self.player_who_resolves_reaction.append(self.name_2)
            if self.p1.cards_in_play[planet_id + 1][i].get_ability() == "Toxic Venomthrope":
                self.p1.set_aiming_reticle_in_play(planet_id, i, "blue")
                self.create_reaction("Toxic Venomthrope", self.name_1, ("1", planet_id, i))
            attachments = self.p1.cards_in_play[planet_id + 1][i].get_attachments()
            for j in range(len(attachments)):
                if attachments[j].get_ability() == "Noxious Fleshborer":
                    if not already_noxious and not self.infested_planets[planet_id]:
                        already_noxious = True
                        self.create_reaction("Noxious Fleshborer", self.name_1, ("1", planet_id, i))
        return ret_val
    elif command_p2 > command_p1:
        print("P2 wins command")
        chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
        if self.canceled_resource_bonuses[planet_id]:
            resources_won = 0
        else:
            resources_won = chosen_planet.get_resources()
        if self.canceled_card_bonuses[planet_id]:
            cards_won = 0
        else:
            cards_won = chosen_planet.get_cards()
        extra_resources, extra_cards = self.p2.get_bonus_winnings_at_planet(planet_id)
        resources_won += extra_resources
        cards_won += extra_cards
        ret_val = ["2", resources_won, cards_won]
        already_noxious = False
        if self.p2.search_card_in_hq("Omega Zero Command"):
            self.p2.summon_token_at_planet("Guardsman", planet_id)
        for i in range(len(self.p2.cards_in_play[planet_id + 1])):
            if self.p2.cards_in_play[planet_id + 1][i].get_ability() == "Soul Grinder":
                self.p2.set_aiming_reticle_in_play(planet_id, i, "blue")
                self.positions_of_unit_triggering_reaction.append(["2", planet_id, i])
                self.reactions_needing_resolving.append("Soul Grinder")
                self.player_who_resolves_reaction.append(self.name_1)
            if self.p2.cards_in_play[planet_id + 1][i].get_ability() == "Toxic Venomthrope":
                self.p2.set_aiming_reticle_in_play(planet_id, i, "blue")
                self.create_reaction("Toxic Venomthrope", self.name_2, ("2", planet_id, i))
            attachments = self.p2.cards_in_play[planet_id + 1][i].get_attachments()
            for j in range(len(attachments)):
                if attachments[j].get_ability() == "Noxious Fleshborer":
                    if not already_noxious and not self.infested_planets[planet_id]:
                        already_noxious = True
                        self.create_reaction("Noxious Fleshborer", self.name_2, ("2", planet_id, i))
        return ret_val
    return None
