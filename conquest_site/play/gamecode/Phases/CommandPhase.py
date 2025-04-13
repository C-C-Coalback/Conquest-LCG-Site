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
                else:
                    if not self.p2.committed_warlord:
                        self.p2.warlord_commit_location = int(game_update_string[1])
                        self.p2.committed_warlord = True
                if self.p1.committed_warlord and self.p2.committed_warlord:
                    print("Both warlords need to be committed.")
                    print(self.p1.warlord_commit_location, self.p2.warlord_commit_location)
                    self.p1.commit_warlord_to_planet()
                    self.p2.commit_warlord_to_planet()
                    await self.p1.send_hq()
                    await self.p2.send_hq()
                    await self.send_planet_array()
                    await self.p1.send_units_at_all_planets()
                    await self.p2.send_units_at_all_planets()
                    self.p1.has_passed = False
                    self.p2.has_passed = False
                    self.committing_warlords = False
                    self.before_command_struggle =True
                    await self.game_sockets[0].receive_game_update("Both players are given a chance to resolve "
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
            if game_update_string[0] == "HAND":
                if name == self.name_1:
                    primary_player = self.p1
                else:
                    primary_player = self.p2
                if game_update_string[1] == primary_player.get_number():
                    hand_pos = int(game_update_string[2])
                    if primary_player.cards[hand_pos] == "Foresight":
                        warlord_planet = primary_player.warlord_commit_location
                        self.positions_of_unit_triggering_reaction.append([int(primary_player.get_number()),
                                                                           warlord_planet, -1])
                        self.reactions_needing_resolving.append("Foresight")
                        self.player_who_resolves_reaction.append(primary_player.name_player)
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        await primary_player.send_hand()
                    elif primary_player.cards[hand_pos] == "Superiority":
                        if primary_player.spend_resources(1):
                            self.positions_of_unit_triggering_reaction.append([int(primary_player.get_number()),
                                                                               -1, -1])
                            self.reactions_needing_resolving.append("Superiority")
                            self.player_who_resolves_reaction.append(primary_player.name_player)
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                            await primary_player.send_hand()
    elif self.after_command_struggle:
        print("After command struggle")
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if name == self.name_1:
                    self.p1.has_passed = True
                elif name == self.name_2:
                    self.p2.has_passed = True
            if game_update_string[0] == "action-button":
                if self.actions_allowed and self.mode != "ACTION":
                    self.stored_mode = self.mode
                    self.mode = "ACTION"
                    self.player_with_action = name
                    await self.game_sockets[0].receive_game_update(name + " wants to take an action.")
    if self.p1.has_passed and self.p2.has_passed:
        print("Both passed")
        if self.before_command_struggle:
            resolve_command_struggle(self)
            await self.p1.send_hand()
            await self.p2.send_hand()
            await self.p1.send_resources()
            await self.p2.send_resources()
            await self.p1.send_units_at_all_planets()
            await self.p2.send_units_at_all_planets()
            self.before_command_struggle = False
            self.after_command_struggle = True
            self.p1.has_passed = False
            self.p2.has_passed = False
            await self.game_sockets[0].receive_game_update("Window given for actions after command struggle.")
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
                self.last_planet_checked_for_battle = self.round_number
                self.set_battle_initiative()
                self.planet_aiming_reticle_active = True
                self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
                await self.send_planet_array()
                self.p1.has_passed = False
                self.p2.has_passed = False
                await self.send_info_box()


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
    command_p1 = self.p1.count_command_at_planet(planet_id)
    command_p2 = self.p2.count_command_at_planet(planet_id)
    if command_p1 > command_p2:
        print("P1 wins command")
        chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
        resources_won = chosen_planet.get_resources()
        cards_won = chosen_planet.get_cards()
        extra_resources, extra_cards = self.p1.get_bonus_winnings_at_planet(planet_id)
        resources_won += extra_resources
        cards_won += extra_cards
        ret_val = ["1", resources_won, cards_won]
        if self.p1.search_card_in_hq("Omega Zero Command"):
            self.p1.summon_token_at_planet("Guardsman", planet_id)
        for i in range(len(self.p1.cards_in_play[planet_id + 1])):
            if self.p1.cards_in_play[planet_id + 1][i].get_ability() == "Soul Grinder":
                self.p1.set_aiming_reticle_in_play(planet_id, i, "blue")
                self.positions_of_unit_triggering_reaction.append(["1", planet_id, i])
                self.reactions_needing_resolving.append("Soul Grinder")
                self.player_who_resolves_reaction.append(self.name_2)
        return ret_val
    elif command_p2 > command_p1:
        print("P2 wins command")
        chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
        resources_won = chosen_planet.get_resources()
        cards_won = chosen_planet.get_cards()
        extra_resources, extra_cards = self.p2.get_bonus_winnings_at_planet(planet_id)
        resources_won += extra_resources
        cards_won += extra_cards
        ret_val = ["2", resources_won, cards_won]
        if self.p2.search_card_in_hq("Omega Zero Command"):
            self.p2.summon_token_at_planet("Guardsman", planet_id)
        for i in range(len(self.p1.cards_in_play[planet_id + 1])):
            if self.p1.cards_in_play[planet_id + 1][i].get_ability() == "Soul Grinder":
                self.p1.set_aiming_reticle_in_play(planet_id, i, "blue")
                self.positions_of_unit_triggering_reaction.append(["1", planet_id, i])
                self.reactions_needing_resolving.append("Soul Grinder")
                self.player_who_resolves_reaction.append(self.name_2)
        return ret_val
    return None

