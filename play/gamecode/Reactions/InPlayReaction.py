from .. import FindCard


async def resolve_in_play_reaction(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = int(game_update_string[2])
    unit_pos = int(game_update_string[3])
    print("Check what player")
    print(self.player_who_resolves_reaction)
    if name == self.player_who_resolves_reaction[0]:
        if self.reactions_needing_resolving[0] == "Power from Pain":
            if int(primary_player.get_number()) == int(
                    self.positions_of_unit_triggering_reaction[0][0]):
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
                    primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                    self.delete_reaction()
                    await secondary_player.dark_eldar_event_played()
                    secondary_player.torture_event_played("Power from Pain")
        elif self.reactions_needing_resolving[0] == "Nullify":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.valid_nullify_unit(planet_pos, unit_pos):
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                if primary_player.urien_relevant:
                    primary_player.spend_resources(1)
                primary_player.num_nullify_played += 1
                self.nullify_count += 1
                if secondary_player.nullify_check():
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    await self.send_update_message(secondary_player.name_player +
                                                   " counter nullify offered.")
                else:
                    await self.complete_nullify()
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Ku'gath Plaguefather":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if primary_player.number == game_update_string[1]:
                    if unit_pos != self.positions_of_unit_triggering_reaction[0][2]:
                        primary_player.remove_damage_from_pos(self.positions_of_unit_triggering_reaction[0][1],
                                                              self.positions_of_unit_triggering_reaction[0][2], 1)
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False, is_reassign=True)
                        self.delete_reaction()
                else:
                    primary_player.remove_damage_from_pos(self.positions_of_unit_triggering_reaction[0][1],
                                                          self.positions_of_unit_triggering_reaction[0][2], 1)
                    secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False, is_reassign=True)
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "The Plaguefather's Banner":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if primary_player.number == game_update_string[1]:
                    if unit_pos != self.positions_of_unit_triggering_reaction[0][2]:
                        primary_player.remove_damage_from_pos(self.positions_of_unit_triggering_reaction[0][1],
                                                              self.positions_of_unit_triggering_reaction[0][2], 1)
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False, is_reassign=True)
                        self.delete_reaction()
                else:
                    primary_player.remove_damage_from_pos(self.positions_of_unit_triggering_reaction[0][1],
                                                          self.positions_of_unit_triggering_reaction[0][2], 1)
                    secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False, is_reassign=True)
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Klaivex Warleader":
            att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
            if att_pla == planet_pos:
                if game_update_string[1] == "1":
                    player_being_hit = self.p1
                else:
                    player_being_hit = self.p2
                if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if player_being_hit.get_damage_given_pos(planet_pos, unit_pos) > 0:
                        can_continue = True
                        if player_being_hit.number == secondary_player.number:
                            possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message(
                                    "Immune to enemy card abilities.")
                            elif possible_interrupts:
                                can_continue = False
                                await self.send_update_message("Some sort of interrupt may be used.")
                                self.choices_available = possible_interrupts
                                self.choices_available.insert(0, "No Interrupt")
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Interrupt Effect?"
                                self.nullified_card_name = self.reactions_needing_resolving[0]
                                self.cost_card_nullified = 0
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "Reaction"
                        if can_continue:
                            player_being_hit.destroy_card_in_play(planet_pos, unit_pos)
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Fenrisian Wolf":
            att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
            if att_pla == planet_pos:
                if game_update_string[1] == "1":
                    player_being_hit = self.p1
                else:
                    player_being_hit = self.p2
                if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    can_continue = True
                    if player_being_hit.number == secondary_player.number:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message(
                                "Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                    if can_continue:
                        att_value = primary_player.get_attack_given_pos(att_pla, att_pos)
                        player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, att_value)
                        self.advance_damage_aiming_reticle()
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Vengeance!":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if primary_player.number == game_update_string[1]:
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines" \
                            and primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.spend_resources(1)
                        primary_player.discard_card_name_from_hand("Vengeance!")
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Veteran Barbrus":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if game_update_string[1] == "1":
                    player_being_hit = self.p1
                else:
                    player_being_hit = self.p2
                faction = player_being_hit.get_faction_given_pos(planet_pos, unit_pos)
                if faction not in ["Chaos", "Astra Militarum", "Space Marines"]:
                    can_continue = True
                    if player_being_hit.number == secondary_player.number:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message(
                                "Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                    if can_continue:
                        player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 2, context="Veteran Barbrus")
                        self.advance_damage_aiming_reticle()
                        self.delete_reaction()
                else:
                    await self.send_update_message(
                        "Forbidden faction for Veteran Barbrus.")
        elif self.reactions_needing_resolving[0] == "Blazing Zoanthrope":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if secondary_player.get_number() == game_update_string[1]:
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        can_continue = True
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message(
                                "Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                        if can_continue:
                            if self.infested_planets[planet_pos]:
                                secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2)
                            else:
                                secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
                            secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Obedience":
            if game_update_string[1] == primary_player.number:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) != "Necrons":
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        elif self.reactions_needing_resolving[0] == "Soul Grinder":
            if primary_player.get_number() == game_update_string[1]:
                planet_pos_sg = self.positions_of_unit_triggering_reaction[0][1]
                unit_pos_sg = self.positions_of_unit_triggering_reaction[0][2]
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if planet_pos == planet_pos_sg:
                    if primary_player.cards_in_play[planet_pos + 1][unit_pos]. \
                            get_card_type() != "Warlord":
                        primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                        secondary_player.reset_aiming_reticle_in_play(planet_pos_sg, unit_pos_sg)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Fire Warrior Elite":
            if game_update_string[1] == primary_player.get_number():
                _, current_planet, current_unit = self.last_defender_position
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                    if primary_player.get_ability_given_pos(
                            planet_pos, unit_pos) == "Fire Warrior Elite":
                        primary_player.reset_aiming_reticle_in_play(current_planet, current_unit)
                        self.may_move_defender = False
                        print("Calling defender in the funny way")
                        await CombatPhase.update_game_event_combat_section(
                            self, secondary_player.name_player, game_update_string)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
            if not self.chosen_first_card and not self.chosen_second_card:
                if game_update_string[1] == primary_player.get_number():
                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Tomb Blade Squadron":
                        if not primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used:
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = True
                            self.chosen_first_card = True
                            self.misc_target_unit = (planet_pos, unit_pos)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
            elif self.chosen_first_card and self.chosen_second_card:
                current_planet, current_pos = self.misc_target_unit
                if current_planet == planet_pos:
                    if game_update_string[1] == "1":
                        player_being_hit = self.p1
                    else:
                        player_being_hit = self.p2
                    can_continue = True
                    if player_being_hit.name_player == secondary_player.name_player:
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                    if can_continue:
                        if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                            secondary_player.apply_negative_health_eop(planet_pos, unit_pos, 1)
                            primary_player.reset_aiming_reticle_in_play(current_planet, current_pos)
                            self.misc_target_unit = (-1, -1)
                            self.chosen_first_card = False
                            self.chosen_second_card = False
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Eldorath Starbane":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if game_update_string[1] == "1":
                    player_exhausting_unit = self.p1
                else:
                    player_exhausting_unit = self.p2
                can_continue = True
                if player_exhausting_unit.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif possible_interrupts:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.reactions_needing_resolving[0]
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction"
                if can_continue:
                    if self.positions_of_unit_triggering_reaction[0][1] == planet_pos:
                        if player_exhausting_unit.cards_in_play[planet_pos + 1][unit_pos]. \
                                get_card_type() != "Warlord":
                            player_exhausting_unit.exhaust_given_pos(planet_pos, unit_pos)
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Blackmane Sentinel":
            if game_update_string[1] == primary_player.get_number():
                warlord_pla = primary_player.find_warlord_planet()
                if warlord_pla != planet_pos and warlord_pla != -1:
                    if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Blackmane Sentinel":
                        primary_player.move_unit_to_planet(planet_pos, unit_pos, warlord_pla)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Ragnar Blackmane":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if game_update_string[1] == secondary_player.get_number():
                    can_continue = True
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif possible_interrupts:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.reactions_needing_resolving[0]
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction"
                    if can_continue:
                        secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, context="Ragnar Blackmane")
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Nahumekh":
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            can_continue = True
            if game_update_string[1] != primary_player.get_number():
                possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.reactions_needing_resolving[0]
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction"
            if can_continue:
                if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    player_being_hit.apply_negative_health_eop(planet_pos, unit_pos,
                                                               primary_player.nahumekh_value)
                    name = player_being_hit.get_name_given_pos(planet_pos, unit_pos)
                    await self.send_update_message(
                        name + " received -" + str(primary_player.nahumekh_value) + " HP."
                    )
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Shrouded Harlequin":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if game_update_string[1] != primary_player.get_number():
                can_continue = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.reactions_needing_resolving[0]
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction"
                if can_continue:
                    secondary_player.exhaust_given_pos(planet_pos, unit_pos)
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Imperial Fists Siege Force":
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            if self.positions_of_unit_triggering_reaction[0][1] == planet_pos:
                if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait("Ally"):
                    can_continue = True
                    if player_being_hit.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos,
                                                                                             move_from_planet=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                    if can_continue:
                        player_being_hit.rout_unit(planet_pos, unit_pos)
        elif self.reactions_needing_resolving[0] == "Superiority":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            can_continue = True
            if player_being_hit.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.reactions_needing_resolving[0]
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
            if can_continue:
                if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
                    player_being_hit.cards_in_play[planet_pos + 1][unit_pos].hit_by_superiority = True
                    card_name = player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_name()
                    text = card_name + ", position " + str(planet_pos) \
                           + " " + str(unit_pos) + " hit by superiority."
                    await self.send_update_message(text)
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Venomthrope Polluter":
            if game_update_string[1] == primary_player.number:
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.check_for_warlord(planet_pos):
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                        dest_planet = self.positions_of_unit_triggering_reaction[0][1]
                        primary_player.move_unit_to_planet(planet_pos, unit_pos, dest_planet)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Alaitoc Shrine":
            if int(primary_player.get_number()) == int(
                    self.positions_of_unit_triggering_reaction[0][0]):
                if self.alaitoc_shrine_activated:
                    player_num = int(primary_player.get_number())
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    full_position = [player_num, planet_pos, unit_pos]
                    if full_position in self.allowed_units_alaitoc_shrine:
                        if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                            primary_player.ready_given_pos(planet_pos, unit_pos)
                            self.delete_reaction()
                            self.alaitoc_shrine_activated = False
                            self.allowed_units_alaitoc_shrine = []
                        else:
                            await self.send_update_message("Unit already ready")
        elif self.reactions_needing_resolving[0] == "Cato's Stronghold":
            if int(primary_player.get_number()) == int(
                    self.positions_of_unit_triggering_reaction[0][0]):
                if self.cato_stronghold_activated:
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    if planet_pos in self.allowed_planets_cato_stronghold:
                        if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                            primary_player.ready_given_pos(planet_pos, unit_pos)
                            self.delete_reaction()
                            self.allowed_planets_cato_stronghold = []
                            self.cato_stronghold_activated = False
                        else:
                            await self.send_update_message("Unit already ready")
        elif self.reactions_needing_resolving[0] == "Beasthunter Wyches":
            if int(primary_player.get_number()) == int(
                    self.positions_of_unit_triggering_reaction[0][0]):
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Beasthunter Wyches":
                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_reaction_available():
                        if primary_player.spend_resources(1):
                            primary_player.cards_in_play[planet_pos + 1][unit_pos]. \
                                set_reaction_available(False)
                            primary_player.summon_token_at_hq("Khymera", 1)
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Spiritseer Erathal":
            if primary_player.get_number() == game_update_string[1]:
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if self.attacker_planet == int(game_update_string[2]):
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Standard Bearer":
            if primary_player.get_number() == game_update_string[1]:
                if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Nocturne-Ultima Storm Bolter":
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            origin_planet = self.positions_of_unit_triggering_reaction[0][1]
            origin_pos = self.positions_of_unit_triggering_reaction[0][2]
            if int(game_update_string[2]) == origin_planet:
                num, prev_def_planet, prev_def_pos = self.last_defender_position
                target_unit_pos = int(game_update_string[3])
                if target_unit_pos == prev_def_pos and int(num) == int(game_update_string[1]):
                    await self.send_update_message("Can't select last defender")
                else:
                    can_continue = True
                    if player_being_hit.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(origin_planet,
                                                                               target_unit_pos):
                            can_continue = False
                            await self.send_update_message(
                                "Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                    if can_continue:
                        attack = primary_player.get_attack_given_pos(origin_planet, origin_pos)
                        player_being_hit.assign_damage_to_pos(origin_planet, target_unit_pos, attack)
                        player_being_hit.set_aiming_reticle_in_play(origin_planet, target_unit_pos, "blue")
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Burna Boyz":
            if primary_player.get_number() != game_update_string[1]:
                origin_planet = self.positions_of_unit_triggering_reaction[0][1]
                if int(game_update_string[2]) == origin_planet:
                    _, prev_def_planet, prev_def_pos = self.last_defender_position
                    target_unit_pos = int(game_update_string[3])
                    if target_unit_pos == prev_def_pos:
                        await self.send_update_message("Can't select last defender")
                    else:
                        can_continue = True
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(origin_planet,
                                                                               target_unit_pos):
                            can_continue = False
                            await self.send_update_message(
                                "Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                        if can_continue:
                            secondary_player.assign_damage_to_pos(origin_planet, target_unit_pos, 1)
                            secondary_player.set_aiming_reticle_in_play(origin_planet, target_unit_pos,
                                                                        "blue")
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Venomous Fiend":
            if primary_player.get_number() != game_update_string[1]:
                origin_planet = self.positions_of_unit_triggering_reaction[0][1]
                if int(game_update_string[2]) == origin_planet:
                    target_unit_pos = int(game_update_string[3])
                    if secondary_player.get_card_type_given_pos(origin_planet, target_unit_pos) == "Army":
                        can_continue = True
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(origin_planet,
                                                                               target_unit_pos):
                            can_continue = False
                            await self.send_update_message(
                                "Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                        if can_continue:
                            damage = secondary_player.get_command_given_pos(origin_planet, target_unit_pos)
                            secondary_player.assign_damage_to_pos(origin_planet, target_unit_pos, damage)
                            secondary_player.set_aiming_reticle_in_play(origin_planet, target_unit_pos, "blue")
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Treacherous Lhamaean":
            num, origin_planet, origin_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.number == game_update_string[1]:
                if origin_planet == planet_pos and origin_pos != unit_pos:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Defense Battery":
            if self.chosen_first_card:
                if game_update_string[1] == secondary_player.get_number():
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if secondary_player.cards_in_play[planet_pos + 1][unit_pos].valid_defense_battery_target:
                            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2)
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Banner of the Ashen Sky":
            if game_update_string[1] == primary_player.number:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].valid_target_ashen_banner:
                    primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 2, expiration="NEXT")
                    card_name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                    await self.send_update_message(card_name + " gained +2 ATK from Banner!")
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Cry of the Wind":
            if not self.chosen_first_card:
                if game_update_string[1] == primary_player.number:
                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].valid_target_ashen_banner:
                        self.misc_target_unit = (planet_pos, unit_pos)
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.chosen_first_card = True
        elif self.reactions_needing_resolving[0] == "Sicarius's Chosen":
            print("Resolve Sicarius's chosen")
            origin_planet = self.positions_of_unit_triggering_reaction[0][1]
            target_planet = int(game_update_string[2])
            target_pos = int(game_update_string[3])
            if int(game_update_string[1]) == int(secondary_player.get_number()):
                if abs(origin_planet - target_planet) == 1:
                    if secondary_player.cards_in_play[target_planet + 1][
                            target_pos].get_card_type() == "Army":
                        can_continue = True
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos,
                                                                                             move_from_planet=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(target_planet,
                                                                               target_pos):
                            can_continue = False
                            await self.send_update_message(
                                "Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.reactions_needing_resolving[0]
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                        if can_continue:
                            secondary_player.move_unit_to_planet(target_planet,
                                                                 int(game_update_string[3]),
                                                                 origin_planet)
                            new_unit_pos = len(secondary_player.cards_in_play[origin_planet + 1]) - 1
                            secondary_player.assign_damage_to_pos(origin_planet, new_unit_pos, 1,
                                                                  context="Sicarius's Chosen")
                            secondary_player.set_aiming_reticle_in_play(origin_planet, new_unit_pos,
                                                                        "red")
                            self.delete_reaction()
