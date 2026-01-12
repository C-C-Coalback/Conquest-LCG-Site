import copy

from .. import FindCard
from ..Phases import DeployPhase, CombatPhase
from .. import CardClasses


async def resolve_in_play_interrupt(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = int(game_update_string[2])
    unit_pos = int(game_update_string[3])
    if game_update_string[1] == primary_player.number:
        player_owning_card = primary_player
    else:
        player_owning_card = secondary_player
    current_interrupt = self.interrupts_waiting_on_resolution[0]
    if current_interrupt == "Prudent Fire Warriors":
        og_num, og_pla, og_pos = self.positions_of_units_interrupting[0]
        if og_pla == planet_pos and og_pos != unit_pos:
            if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                attachments = primary_player.cards_in_play[og_pla + 1][og_pos].get_attachments()
                copy_attachments = copy.deepcopy(
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments())
                attached_all = True
                for i in range(len(attachments)):
                    owner = attachments[i].name_owner
                    if owner == primary_player.name_player:
                        not_owner = True
                    else:
                        not_owner = False
                    army = False
                    if attachments[i].get_name() in ["Shadowsun's Stealth Cadre", "Gun Drones", "Escort Drone"]:
                        army = True
                    if not primary_player.attach_card(attachments[i], planet_pos, unit_pos,
                                                      not_own_attachment=not_owner, army_unit_as_attachment=army):
                        attached_all = False
                if not attached_all:
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].attachments = copy_attachments
                if attached_all:
                    primary_player.cards_in_play[og_pla + 1][og_pos].attachments = []
                self.delete_interrupt()
    elif current_interrupt == "World Engine Beam":
        if not player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_unique():
            player_owning_card.destroy_card_in_play(planet_pos, unit_pos)
            self.delete_interrupt()
    elif current_interrupt == "Cardinal Agra Decree":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            player_owning_card.increase_faith_given_pos(planet_pos, unit_pos, 1)
            primary_player.draw_card()
            self.delete_interrupt()
    elif current_interrupt == "The Shadow Suit":
        if self.chosen_first_card:
            if planet_pos == self.misc_target_planet:
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                    self.delete_interrupt()
    elif current_interrupt == "Mark of Slaanesh":
        if game_update_string[1] == primary_player.number:
            dest_planet = self.positions_of_units_interrupting[0][1]
            if dest_planet != planet_pos:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    primary_player.move_unit_to_planet(planet_pos, unit_pos, dest_planet)
                    self.delete_interrupt()
    elif current_interrupt == "Liatha Punishment":
        player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1)
        self.delete_interrupt()
    elif current_interrupt == "Raging Daemonhost":
        if self.positions_of_units_interrupting[0][1] == planet_pos:
            card = CardClasses.AttachmentCard(
                "Raging Daemonhost", "Attach to a non-Daemon, non-Vehicle army unit. \n"
                                     "Attached unit gets +3 ATK, +3 HP and the Khorne trait.",
                "Daemon. Cultist. Khorne.", 4, "Chaos", "Common", 0, False,
                type_of_units_allowed_for_attachment="Army", extra_attack=3, extra_health=3
            )
            not_own_attachment = False
            if player_owning_card.number != primary_player.number:
                not_own_attachment = True
            if player_owning_card.attach_card(card, planet_pos, unit_pos, not_own_attachment=not_own_attachment):
                self.delete_interrupt()
                if "Raging Daemonhost" in primary_player.discard:
                    primary_player.discard.remove("Raging Daemonhost")
    elif current_interrupt == "Trap Laying Hunter":
        if self.positions_of_units_interrupting[0][1] == planet_pos:
            if primary_player.get_number() == game_update_string[1]:
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                    self.mask_jain_zar_check_interrupts(secondary_player, primary_player)
                    self.delete_interrupt()
    elif current_interrupt == "Truck Wreck Launcha":
        if game_update_string[1] == secondary_player.get_number():
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                if planet_pos == self.extra_interrupt_info[0]:
                    secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                    self.delete_interrupt()
    elif current_interrupt == "The Broken Sigil Sacrifice Unit":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    self.delete_interrupt()
    elif current_interrupt == "Data Analyzer Aggressive":
        if game_update_string[1] == secondary_player.get_number():
            _, og_pla, og_pos = self.positions_of_units_interrupting[0]
            if og_pla == planet_pos:
                if (og_pla, og_pos) != (planet_pos, unit_pos):
                    secondary_player.remove_damage_from_pos(og_pla, og_pos, 1)
                    secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1,
                                                          by_enemy_unit=False, is_reassign=True)
                    self.delete_interrupt()
                    need_to_cleanup_shielding = False
                    need_to_delete_shielding = False
                    position_damage = -1
                    for i in range(len(self.positions_attackers_of_units_to_take_damage)):
                        if self.positions_attackers_of_units_to_take_damage[i] is not None:
                            self.amount_that_can_be_removed_by_shield[i] += -1
                            if self.amount_that_can_be_removed_by_shield[i] < 0:
                                if i == 0:
                                    need_to_cleanup_shielding = True
                                else:
                                    position_damage = i
                                    need_to_delete_shielding = True
                    if need_to_cleanup_shielding:
                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                    elif need_to_delete_shielding:
                        del self.damage_on_units_list_before_new_damage[position_damage]
                        del self.damage_is_preventable[position_damage]
                        del self.positions_of_units_to_take_damage[position_damage]
                        del self.damage_can_be_shielded[position_damage]
                        del self.positions_attackers_of_units_to_take_damage[position_damage]
                        del self.card_names_triggering_damage[position_damage]
                        del self.amount_that_can_be_removed_by_shield[position_damage]
    elif current_interrupt == "Singing Spear":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                last_planet = self.determine_last_planet()
                if planet_pos != last_planet:
                    primary_player.move_unit_to_planet(planet_pos, unit_pos, last_planet)
                    self.delete_interrupt()
    elif current_interrupt == "The Sun Prince":
        if planet_pos == self.positions_of_units_interrupting[0][1]:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                    self.delete_interrupt()
            else:
                if not secondary_player.get_ready_given_pos(planet_pos, unit_pos):
                    secondary_player.ready_given_pos(planet_pos, unit_pos)
                    self.delete_interrupt()
    elif current_interrupt == "Vanguard Soldiers":
        if game_update_string[1] == primary_player.number:
            can_continue = True
            possible_interrupts = secondary_player.intercept_check()
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = current_interrupt
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Interrupt"
            if can_continue:
                primary_player.ready_given_pos(planet_pos, unit_pos)
                self.delete_interrupt()
    elif current_interrupt == "Incubus Cleavers":
        if self.positions_of_units_interrupting[0][1] == planet_pos:
            can_continue = True
            possible_interrupts = []
            if game_update_string[1] == primary_player.number:
                possible_interrupts = secondary_player.intercept_check()
            else:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = current_interrupt
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Interrupt"
            if can_continue:
                dmg = primary_player.cards_in_play[self.positions_of_units_interrupting[0][1] + 1][
                    self.positions_of_units_interrupting[0][2]].counter
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, dmg, rickety_warbuggy=True)
                self.mask_jain_zar_check_interrupts(primary_player, secondary_player)
                self.delete_interrupt()
    elif current_interrupt == "Prognosticator":
        valid_planet = False
        for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
            if primary_player.cards_in_play[planet_pos + 1][i].recently_assigned_damage:
                valid_planet = True
        if valid_planet:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                player_owning_card.increase_faith_given_pos(planet_pos, unit_pos, 1)
                self.mask_jain_zar_check_interrupts(primary_player, secondary_player)
                self.delete_interrupt()
    elif current_interrupt == "Blood of Martyrs":
        if game_update_string[1] == primary_player.number:
            if not self.chosen_first_card:
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum":
                    if primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                        self.misc_misc = []
                        self.misc_counter = 3
                        self.chosen_first_card = True
                        self.chosen_second_card = False
                        self.misc_target_unit = (planet_pos, unit_pos)
                        self.misc_target_planet = planet_pos
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, color="red")
                        await self.send_update_message("Now select up to three army units.")
            elif not self.chosen_second_card:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if planet_pos == self.misc_target_planet:
                        if (planet_pos, unit_pos) != self.misc_target_unit:
                            if (planet_pos, unit_pos) not in self.misc_misc:
                                self.misc_misc.append((planet_pos, unit_pos))
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                                self.misc_counter = self.misc_counter - 1
                                if self.misc_counter < 1:
                                    self.chosen_second_card = True
                                    if primary_player.get_faith_given_pos(self.misc_target_unit[0],
                                                                          self.misc_target_unit[1]) < 1:
                                        await self.send_update_message("No faith to move; skipping directly to "
                                                                       "increasing the attack of the units step.")
                                        for i in range(len(self.misc_misc)):
                                            primary_player.increase_attack_of_unit_at_pos(self.misc_misc[i][0],
                                                                                          self.misc_misc[i][1], 1,
                                                                                          expiration="NEXT")
                                        if primary_player.check_for_trait_given_pos(
                                                self.misc_target_unit[0], self.misc_target_unit[1], "Martyr"):
                                            primary_player.draw_card()
                                        primary_player.reset_all_aiming_reticles_play_hq()
                                        self.delete_interrupt()
            else:
                if (planet_pos, unit_pos) in self.misc_misc:
                    primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                    primary_player.spend_faith_given_pos(self.misc_target_unit[0], self.misc_target_unit[1], 1)
                    if primary_player.get_faith_given_pos(self.misc_target_unit[0],
                                                          self.misc_target_unit[1]) < 1:
                        await self.send_update_message("No faith left, increasing the attack of the units.")
                        for i in range(len(self.misc_misc)):
                            primary_player.increase_attack_of_unit_at_pos(self.misc_misc[i][0],
                                                                          self.misc_misc[i][1], 1,
                                                                          expiration="NEXT")
                        if primary_player.check_for_trait_given_pos(
                                self.misc_target_unit[0], self.misc_target_unit[1], "Martyr"):
                            primary_player.draw_card()
                        primary_player.reset_all_aiming_reticles_play_hq()
                        self.delete_interrupt()
    elif current_interrupt == "Zen Xi Aonia":
        if game_update_string[1] == primary_player.get_number():
            _, current_planet, current_unit = self.last_defender_position
            if planet_pos == self.positions_of_units_interrupting[0][1]:
                if current_unit != unit_pos:
                    primary_player.reset_aiming_reticle_in_play(current_planet, current_unit)
                    self.may_move_defender = False
                    print("Calling defender in the funny way")
                    await CombatPhase.update_game_event_combat_section(
                        self, secondary_player.name_player, game_update_string)
                    self.delete_interrupt()
    elif current_interrupt == "Banner of the Cult":
        if game_update_string[1] == secondary_player.number:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if planet_pos == self.positions_of_units_interrupting[0][1]:
                    can_continue = True
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True)
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = current_interrupt
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Interrupt"
                    if can_continue:
                        secondary_player.exhaust_given_pos(planet_pos, unit_pos)
                        primary_player.cards.append("Banner of the Cult")
                        try:
                            primary_player.discard.remove("Banner of the Cult")
                        except:
                            pass
                        self.delete_interrupt()
    elif current_interrupt == "Reanimating Warriors":
        print("reanimating warriors")
        if not self.asked_if_resolve_effect:
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Reanimating Warriors?"
            self.name_player_making_choices = name
        elif not self.chosen_first_card:
            if game_update_string[1] == primary_player.number:
                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == \
                        "Reanimating Warriors" \
                        and not primary_player.cards_in_play[planet_pos + 1][unit_pos] \
                        .once_per_phase_used:
                    if primary_player.check_damage_too_great_given_pos(planet_pos, unit_pos) == 0:
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
                        primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
    elif current_interrupt == "Transcendent Blessing":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.number:
                if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                    self.chosen_first_card = True
                    await self.send_update_message("Select target for the attachment.")
        else:
            card = self.preloaded_find_card("Transcendent Blessing")
            player_getting_attachment = self.p1
            if game_update_string[1] == "2":
                player_getting_attachment = self.p2
            not_own_attachment = False
            if player_getting_attachment.number != primary_player.number:
                not_own_attachment = True
            if player_getting_attachment.attach_card(card, planet_pos, unit_pos, not_own_attachment=not_own_attachment):
                if "Transcendent Blessing" in primary_player.discard:
                    primary_player.discard.remove("Transcendent Blessing")
                self.delete_interrupt()
    elif current_interrupt == "Armored Fist Squad":
        if planet_pos == self.positions_of_units_interrupting[0][1]:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                player_owning_card.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                self.delete_interrupt()
    elif current_interrupt == "Savage Parasite":
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = current_interrupt
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "Interrupt"
        if can_continue:
            player_owning_card = self.p1
            if player_owning_card.get_number() != game_update_string[1]:
                player_owning_card = self.p2
            not_own_card = True
            if player_owning_card.name_player == primary_player.name_player:
                not_own_card = False
            card = FindCard.find_card("Savage Parasite", self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            if player_owning_card.attach_card(card, planet_pos, unit_pos, not_own_attachment=not_own_card):
                self.delete_interrupt()
                try:
                    primary_player.discard.remove("Savage Parasite")
                except ValueError:
                    pass
    elif current_interrupt == "Magus Harid":
        if planet_pos == self.misc_target_planet:
            await DeployPhase.deploy_card_routine_attachment(self, name, game_update_string)
    elif current_interrupt == "No Mercy":
        if game_update_string[1] == primary_player.number:
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit() and \
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_unique() and \
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_ready():
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                primary_player.discard_card_name_from_hand("No Mercy")
                try:
                    secondary_player.discard_card_from_hand(self.pos_shield_card)
                except:
                    pass
                self.delete_interrupt()
                await self.better_shield_card_resolution(secondary_player.name_player, ["pass-P1"],
                                                         alt_shields=False, can_no_mercy=False)
