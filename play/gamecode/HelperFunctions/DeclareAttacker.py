async def declare_attacker(self, name, game_update_string):
    chosen_planet = int(game_update_string[2])
    chosen_unit = int(game_update_string[3])
    if self.number_with_combat_turn == "1":
        player = self.p1
        secondary_player = self.p2
    else:
        player = self.p2
        secondary_player = self.p1
    other_player = secondary_player
    valid_unit = False
    if self.check_if_unit_can_be_declared_as_attacker(player, secondary_player, chosen_planet, chosen_unit):
        valid_unit = True
        if not secondary_player.cards_in_play[chosen_planet + 1]:
            valid_unit = False
            await self.send_update_message("No enemy units to declare as defender. Combat ends.")
            await self.check_combat_end(player.name_player)
        elif player.get_card_type_given_pos(chosen_planet, chosen_unit) == "Warlord" and self.can_retreat_warlord:
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Retreat Warlord?"
            self.name_player_making_choices = player.name_player
            self.resolving_search_box = True
            self.last_game_update_string = game_update_string
            valid_unit = False
            player.set_aiming_reticle_in_play(chosen_planet, chosen_unit, "blue")
            self.attacker_planet = chosen_planet
            self.attacker_position = chosen_unit
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
            if player.get_card_type_given_pos(
                    self.attacker_planet, self.attacker_position
            ) == "Warlord":
                if player.get_bloodied_given_pos(self.attacker_planet, self.attacker_position):
                    player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                        ethereal_movement_active = False
                    self.unit_will_move_after_attack = False
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
        self.sweep_active = False
        self.sweep_value = 0
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
        if player.search_hand_for_card("Unexpected Ferocity") and player.get_resources() > 0:
            self.create_reaction("Unexpected Ferocity", player.name_player,
                                 (int(player.number), self.attacker_planet, self.attacker_position))
        if player.check_for_trait_given_pos(
                self.attacker_planet, self.attacker_position, "Ecclesiarchy"):
            if player.check_if_faction_given_pos(self.attacker_planet, self.attacker_position, "Astra Militarum"):
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
        if player.search_attachments_at_pos(self.attacker_planet, self.attacker_position, "Staff of Tomorrow"):
            self.create_reaction("Staff of Tomorrow", player.name_player, 
                                 (int(player.number), self.attacker_planet, self.attacker_position))
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