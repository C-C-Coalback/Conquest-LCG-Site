async def declare_defender(self, name, game_update_string):
    chosen_planet = int(game_update_string[2])
    chosen_unit = int(game_update_string[3])
    if self.number_with_combat_turn == "1":
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if game_update_string[1] != self.number_with_combat_turn:
        if not self.check_if_unit_can_be_declared_as_defender(primary_player, secondary_player, chosen_planet,
                                                              chosen_unit):
            if self.sweep_active:
                if not secondary_player.cards_in_play[self.defender_planet + 1][
                    self.defender_position].valid_sweep_target:
                    await self.send_update_message("That unit has already been attacked!")
        else:
            self.defender_planet = chosen_planet
            self.defender_position = chosen_unit
            can_continue = True
            if self.may_move_defender and can_continue:
                if secondary_player.search_card_at_planet(self.defender_planet, "Zen Xi Aonia"):
                    if len(secondary_player.cards_in_play[self.defender_planet + 1]) > 1:
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
                            if not secondary_player.hit_by_gorgul:
                                if not secondary_player.check_if_already_have_reaction("Fire Warrior Elite"):
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
                    if not primary_player.cards_in_play[self.attacker_planet + 1][
                               self.attacker_position].attack_set_next is not None:
                        if primary_player.search_attachments_at_pos(self.attacker_planet, self.attacker_position,
                                                                    "Krak Grenade"):
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
            self.last_defender_id = secondary_player.get_id_given_pos(self.defender_planet, self.defender_position)
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
                    if secondary_player.check_if_faction_given_pos(self.defender_planet, self.defender_position,
                                                                   "Orks") and \
                            secondary_player.check_for_trait_given_pos(
                                self.defender_planet, self.defender_position, "Soldier") and \
                            secondary_player.get_card_type_given_pos(
                                self.defender_planet, self.defender_position
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
                if secondary_player.search_attachments_at_pos(
                        self.defender_planet, self.defender_position, "The Black Sword"
                ):
                    can_continue = False
                    await self.send_update_message(
                        "The Black Sword must fire before the rest of the attack."
                    )
                    secondary_player.set_aiming_reticle_in_play(
                        self.defender_planet, self.defender_position, "blue"
                    )
                    self.create_reaction("The Black Sword", secondary_player.name_player,
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
                if self.sweep_active:
                    attack_value = self.sweep_value
                else:
                    attack_value = primary_player.get_attack_given_pos(self.attacker_planet,
                                                                       self.attacker_position)
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
                    for i in range(len(primary_player.cards_in_play[self.attacker_planet + 1][
                                           self.attacker_position].get_attachments())):
                        if primary_player.cards_in_play[self.attacker_planet + 1][
                            self.attacker_position].get_attachments()[
                            i].get_ability() == "Hidden Strike Chainsword":
                            if secondary_player.get_card_type_given_pos(
                                    self.defender_planet, self.defender_position) != "Warlord":
                                attack_value += 2
                    if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position] \
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
                        if self.stored_damage:
                            self.xv805_enforcer_active = True
                            self.asking_if_use_xv805_enforcer = True
                            self.asking_amount_xv805_enforcer = False
                            self.player_using_xv805 = primary_player.name_player
                            d_i = len(self.stored_damage) - 1
                            self.damage_index_xv805 = d_i
                            self.amount_xv805_enforcer = \
                                self.stored_damage[d_i].get_amount_that_can_be_blocked()
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
