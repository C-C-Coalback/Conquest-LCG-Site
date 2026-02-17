# import pygame
# from FindCard import find_card
from . import DeployPhase


def resolve_planet_battle_effect(p_win, p_lose, planet_id):
    planet_name = p_win.get_planet_name_given_position(planet_id)
    print("Resolve battle ability:")
    print(planet_name)
    if planet_name == "Osus_IV" or planet_name == "Osus IV":
        osus_iv_ability(p_win, p_lose)
    elif planet_name == "Iridial":
        iridial_ability(p_win, p_lose)
    elif planet_name == "Plannum":
        plannum_ability(p_win, p_lose)
    elif planet_name == "Tarrus":
        tarrus_ability(p_win, p_lose)
    elif planet_name == "Y'varn":
        yvarn_ability(p_win, p_lose)
    elif planet_name == "Barlus":
        barlus_ability(p_lose)
    elif planet_name == "Ferrin":
        ferrin_ability(p_win, p_lose)
    elif planet_name == "Carnath":
        carnath_ability(p_win, p_lose)
    elif planet_name == "Elouith":
        elouith_ability(p_win, p_lose)
    elif planet_name == "Atrox_Prime" or planet_name == "Atrox Prime":
        atrox_prime_ability(p_win, p_lose, planet_id)


async def manual_atrox_prime_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        planet_pos = int(game_update_string[1])
        if abs(self.atrox_origin - planet_pos) == 1:
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                secondary_player.assign_damage_to_pos(planet_pos, i, 1, by_enemy_unit=False)
            self.damage_from_atrox = True
            if not self.stored_damage:
                self.damage_from_atrox = False
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                     game_update_string)
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            self.damage_from_atrox = True
            if game_update_string[1] == "1":
                player = self.p1
            else:
                player = self.p2
            for i in range(len(player.headquarters)):
                if player.check_is_unit_at_pos(-2, i):
                    player.assign_damage_to_pos(-2, i, 1, by_enemy_unit=False)
            if not self.stored_damage:
                self.damage_from_atrox = False
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                     game_update_string)


async def manual_plannum_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if self.chosen_first_card:
                primary_player.reset_aiming_reticle_in_play(self.misc_target_unit[0],
                                                            self.misc_target_unit[1])
                primary_player.move_unit_to_planet(self.misc_target_unit[0], self.misc_target_unit[1],
                                                   int(game_update_string[1]))
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                     game_update_string)
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == str(self.number_resolving_battle_ability):
                if primary_player.get_card_type_given_pos(-2, int(game_update_string[2])) not in ["Warlord", "Support"]:
                    if self.chosen_first_card:
                        primary_player.reset_aiming_reticle_in_play(self.misc_target_unit[0], self.misc_target_unit[1])
                    self.chosen_first_card = True
                    self.misc_target_unit = (-2, int(game_update_string[2]))
                    primary_player.set_aiming_reticle_in_play(-2, self.misc_target_unit[1], "blue")
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == str(self.number_resolving_battle_ability):
                if primary_player.get_card_type_given_pos(int(game_update_string[2]),
                                                          int(game_update_string[3])) not in ["Warlord", "Support"]:
                    if self.chosen_first_card:
                        primary_player.reset_aiming_reticle_in_play(self.misc_target_unit[0], self.misc_target_unit[1])
                    self.chosen_first_card = True
                    self.misc_target_unit = (int(game_update_string[2]), int(game_update_string[3]))
                    primary_player.set_aiming_reticle_in_play(self.misc_target_unit[0], self.misc_target_unit[1])


async def manual_gareth_prime_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if self.chosen_first_card:
                og_pla, og_pos = self.misc_target_unit
                destination = int(game_update_string[1])
                secondary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                secondary_player.move_unit_to_planet(og_pla, og_pos, destination)
                self.player_resolving_battle_ability = secondary_player.name_player
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                     game_update_string)
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == secondary_player.number:
                unit_pos = int(game_update_string[2])
                if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Army":
                    if not self.chosen_first_card:
                        self.chosen_first_card = True
                        self.misc_target_unit = (-2, unit_pos)
                        secondary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == secondary_player.number:
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if not self.chosen_first_card:
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
                        secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")


async def manual_iridial_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == "1":
                can_continue = True
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if self.player_resolving_battle_ability != self.p1.name_player:
                    possible_interrupts = self.p1.interrupt_cancel_target_check(planet_pos, unit_pos)
                    if possible_interrupts:
                        can_continue = False
                        await self.send_update_message(
                            "Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = self.p1.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = "Iridial"
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = self.p2.name_player
                        self.nullify_context = "Iridial"
                if can_continue:
                    self.p1.remove_damage_from_pos(int(game_update_string[2]), int(game_update_string[3]),
                                                   99, healing=True)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)
            elif game_update_string[1] == "2":
                can_continue = True
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if self.player_resolving_battle_ability != self.p2.name_player:
                    possible_interrupts = self.p2.interrupt_cancel_target_check(planet_pos, unit_pos)
                    if possible_interrupts:
                        can_continue = False
                        await self.send_update_message(
                            "Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = self.p2.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = "Iridial"
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = self.p1.name_player
                        self.nullify_context = "Iridial"
                if can_continue:
                    self.p2.remove_damage_from_pos(int(game_update_string[2]), int(game_update_string[3]),
                                                   99, healing=True)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == "1":
                can_continue = True
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if self.player_resolving_battle_ability != self.p1.name_player:
                    possible_interrupts = self.p1.interrupt_cancel_target_check(planet_pos, unit_pos)
                    if possible_interrupts:
                        can_continue = False
                        await self.send_update_message(
                            "Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = self.p1.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = "Iridial"
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = self.p2.name_player
                        self.nullify_context = "Iridial"
                if can_continue:
                    self.p1.remove_damage_from_pos(-2, int(game_update_string[2]), 99, healing=True)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)
            elif game_update_string[1] == "2":
                can_continue = True
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if self.player_resolving_battle_ability != self.p2.name_player:
                    possible_interrupts = self.p2.interrupt_cancel_target_check(planet_pos, unit_pos)
                    if possible_interrupts:
                        can_continue = False
                        await self.send_update_message(
                            "Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = self.p2.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = "Iridial"
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = self.p1.name_player
                        self.nullify_context = "Iridial"
                if can_continue:
                    self.p2.remove_damage_from_pos(-2, int(game_update_string[2]), 99, healing=True)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)


async def manual_excellor_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if planet_pos != self.misc_target_unit[0]:
                    if not self.misc_target_player:
                        self.misc_target_player = player_owning_card.name_player
                        self.misc_target_unit = (planet_pos, unit_pos)
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    elif self.misc_target_player == player_owning_card.name_player:
                        og_pla, og_pos = self.misc_target_unit
                        player_owning_card.cards_in_play[og_pla + 1].append(
                            player_owning_card.cards_in_play[planet_pos + 1][unit_pos])
                        player_owning_card.cards_in_play[planet_pos + 1].append(
                            player_owning_card.cards_in_play[og_pla + 1][og_pos])
                        del player_owning_card.cards_in_play[og_pla + 1][og_pos]
                        del player_owning_card.cards_in_play[planet_pos + 1][unit_pos]
                        player_owning_card.reset_all_aiming_reticles_play_hq()
                        await self.resolve_battle_conclusion(name, game_update_string)


async def manual_selphini_vii_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if player_owning_card.check_is_unit_at_pos(planet_pos, unit_pos):
                if (planet_pos, unit_pos) != self.misc_target_unit or \
                        self.misc_target_player != player_owning_card.name_player:
                    if not self.chosen_first_card:
                        if player_owning_card.get_damage_given_pos(planet_pos, unit_pos) > 0:
                            self.misc_target_player = player_owning_card.name_player
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.chosen_first_card = True
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    elif not self.chosen_second_card:
                        og_pla, og_pos = self.misc_target_unit
                        player_owning_first_card = self.p1
                        if self.misc_target_player != player_owning_first_card.name_player:
                            player_owning_first_card = self.p2
                        self.chosen_second_card = True
                        player_owning_first_card.remove_damage_from_pos(og_pla, og_pos, 1)
                        damage = player_owning_card.get_damage_given_pos(planet_pos, unit_pos)
                        player_owning_card.set_damage_given_pos(planet_pos, unit_pos, damage + 1)
                        if player_owning_card.check_if_card_is_destroyed(planet_pos, unit_pos):
                            primary_player.add_resources(1)
                        player_owning_first_card.reset_all_aiming_reticles_play_hq()
                        self.misc_target_unit = (-1, -1)
                    else:
                        if player_owning_card.get_damage_given_pos(planet_pos, unit_pos) > 0:
                            player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 1, True)
                            self.player_resolving_battle_ability = secondary_player.name_player
                            await self.resolve_battle_conclusion(name, game_update_string)


async def manual_vargus_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if player_owning_card.check_is_unit_at_pos(planet_pos, unit_pos):
                if (planet_pos, unit_pos) != self.misc_target_unit:
                    if not self.misc_target_player:
                        if player_owning_card.get_damage_given_pos(planet_pos, unit_pos) > 0:
                            self.misc_target_player = player_owning_card.name_player
                            self.misc_target_unit = (planet_pos, unit_pos)
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    else:
                        og_pla, og_pos = self.misc_target_unit
                        player_owning_first_card = self.p1
                        if self.misc_target_player != player_owning_first_card.name_player:
                            player_owning_first_card = self.p2
                        player_owning_first_card.remove_damage_from_pos(og_pla, og_pos, 1)
                        damage = player_owning_card.get_damage_given_pos(planet_pos, unit_pos)
                        player_owning_card.set_damage_given_pos(planet_pos, unit_pos, damage + 1)
                        if player_owning_card.check_if_card_is_destroyed(planet_pos, unit_pos):
                            primary_player.add_resources(1)
                        player_owning_first_card.reset_all_aiming_reticles_play_hq()
                        await self.resolve_battle_conclusion(name, game_update_string)


async def manual_jalayerid_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == secondary_player.get_number():
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if planet_pos in self.misc_misc:
                    secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.misc_misc_2.append((planet_pos, unit_pos))
                    self.misc_misc.remove(planet_pos)
                if not self.misc_misc:
                    for i in range(len(self.misc_misc_2)):
                        og_pla, og_pos = self.misc_misc_2[i]
                        secondary_player.assign_damage_to_pos(og_pla, og_pos, 1)
                    self.misc_misc = None
                    self.misc_misc_2 = None
                    self.damage_from_atrox = True
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == secondary_player.get_number():
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if secondary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                    if planet_pos in self.misc_misc:
                        secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                        self.misc_misc_2.append((planet_pos, unit_pos))
                        self.misc_misc.remove(planet_pos)
                    if not self.misc_misc:
                        for i in range(len(self.misc_misc_2)):
                            og_pla, og_pos = self.misc_misc_2[i]
                            secondary_player.assign_damage_to_pos(og_pla, og_pos, 1)
                        self.misc_misc = None
                        self.misc_misc_2 = None
                        self.damage_from_atrox = True


async def manual_erida_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == primary_player.number:
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                        primary_player.draw_card()
                        primary_player.draw_card()
                        primary_player.add_resources(2)
                        await self.resolve_battle_conclusion(name, game_update_string)
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == primary_player.number:
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.sacrifice_card_in_hq(unit_pos):
                        primary_player.draw_card()
                        primary_player.draw_card()
                        primary_player.add_resources(2)
                        await self.resolve_battle_conclusion(name, game_update_string)


async def manual_daemon_world_ivandis_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == primary_player.number:
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if game_update_string[1] == "1":
                    player_owning_card = self.p1
                else:
                    player_owning_card = self.p2
                if player_owning_card.check_is_unit_at_pos(planet_pos, unit_pos):
                    damage = player_owning_card.get_damage_given_pos(planet_pos, unit_pos)
                    self.choices_available = []
                    for i in range(damage + 1):
                        self.choices_available.append(str(i))
                    self.choice_context = "Daemon World Ivandis Healing"
                    self.name_player_making_choices = primary_player.name_player
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.misc_target_player = player_owning_card.name_player
                    self.resolving_search_box = True
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == primary_player.number:
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if game_update_string[1] == "1":
                    player_owning_card = self.p1
                else:
                    player_owning_card = self.p2
                if player_owning_card.check_is_unit_at_pos(planet_pos, unit_pos):
                    damage = player_owning_card.get_damage_given_pos(planet_pos, unit_pos)
                    self.choices_available = []
                    for i in range(damage + 1):
                        self.choices_available.append(str(i))
                    self.choice_context = "Daemon World Ivandis Healing"
                    self.name_player_making_choices = primary_player.name_player
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.misc_target_player = player_owning_card.name_player
                    self.resolving_search_box = True


async def manual_munos_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                cost = player_owning_card.get_cost_given_pos(planet_pos, unit_pos)
                player_owning_card.return_card_to_hand(planet_pos, unit_pos, return_attachments=True)
                player_owning_card.add_resources(cost)
                await self.resolve_battle_conclusion(name, game_update_string)
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                cost = player_owning_card.get_cost_given_pos(planet_pos, unit_pos)
                player_owning_card.return_card_to_hand(planet_pos, unit_pos, return_attachments=True)
                player_owning_card.add_resources(cost)
                await self.resolve_battle_conclusion(name, game_update_string)

async def manual_jaricho_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if int(game_update_string[1]) != self.last_planet_checked_for_battle and \
                    int(game_update_string[1]) != self.round_number:
                self.jaricho_target = int(game_update_string[1])
                self.jaricho_actual_triggered_planet = self.last_planet_checked_for_battle
                await self.resolve_battle_conclusion(name, game_update_string)
                self.active_jaricho_battle = True


async def manual_nectavus_xi_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            self.nectavus_target = int(game_update_string[1])
            self.nectavus_active = True
            self.nectavus_actual_current_planet = self.last_planet_checked_command_struggle
            self.last_planet_checked_command_struggle = int(game_update_string[1])
            if not self.resolve_remaining_cs_after_reactions:
                self.total_gains_command_struggle = [None, None, None, None, None, None, None]
            self.resolve_remaining_cs_after_reactions = False
            self.before_command_struggle = False
            self.p1.has_passed = True
            self.p2.has_passed = True
            self.interrupts_during_cs_allowed = True
            self.reactions_after_cs_allowed = True
            await self.resolve_battle_ability_routine(name, game_update_string)


async def manual_zarvoss_foundry_ability(self, name, game_update_string, primary_player, secondary_player):
    if self.misc_player_storage:
        card = self.preloaded_find_card(self.misc_player_storage)
        if card.get_card_type() == "Attachment":
            if len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    if card.planet_attachment:
                        primary_player.add_attachment_to_planet(int(game_update_string[1]), card)
                        await self.resolve_battle_conclusion(name, game_update_string)
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HQ":
                    if game_update_string[1] == "1":
                        player_owning_card = self.p1
                    else:
                        player_owning_card = self.p2
                    planet_pos = -2
                    unit_pos = int(game_update_string[2])
                    not_own_attachment = False
                    if player_owning_card.get_number() != primary_player.get_number():
                        not_own_attachment = True
                    if player_owning_card.attach_card(card, planet_pos, unit_pos,
                                                      not_own_attachment=not_own_attachment):
                        await self.resolve_battle_conclusion(name, game_update_string)
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if game_update_string[1] == "1":
                        player_owning_card = self.p1
                    else:
                        player_owning_card = self.p2
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    not_own_attachment = False
                    if player_owning_card.get_number() != primary_player.get_number():
                        not_own_attachment = True
                    if player_owning_card.attach_card(card, planet_pos, unit_pos,
                                                      not_own_attachment=not_own_attachment):
                        await self.resolve_battle_conclusion(name, game_update_string)


async def manual_fortress_world_garid_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HAND":
            if game_update_string[1] == primary_player.get_number():
                primary_player.discard_card_from_hand(int(game_update_string[2]))
                await self.resolve_battle_conclusion(name, game_update_string)


async def manual_xenos_world_talling_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if not self.chosen_first_card:
            if game_update_string[0] == "PLANETS":
                self.misc_target_planet = int(game_update_string[1])
                self.chosen_first_card = True
                await self.send_update_message(self.planet_array[int(game_update_string[1])] +
                                               " targeted for the Xenos World Tallin ability. " +
                                               secondary_player.name_player + " must move a unit.")
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_card_type_given_pos(-2, int(game_update_string[2])) == "Army":
                    primary_player.move_unit_to_planet(
                        -2, int(game_update_string[2]),
                        self.misc_target_planet)
                    await self.resolve_battle_conclusion(name, game_update_string)
    if len(game_update_string) == 4:
        if self.chosen_first_card and self.chosen_second_card:
            if game_update_string[0] == "IN_PLAY":
                if game_update_string[1] == primary_player.get_number():
                    if primary_player.get_card_type_given_pos(int(game_update_string[2]),
                                                              int(game_update_string[3])) == "Army":
                        if int(game_update_string[2]) != self.misc_target_planet:
                            primary_player.move_unit_to_planet(
                                int(game_update_string[2]), int(game_update_string[3]),
                                self.misc_target_planet)
                            await self.resolve_battle_conclusion(name, game_update_string)


async def manual_freezing_tower_ability(self, name, game_update_string, primary_player, secondary_player):
    if self.misc_target_choice == "Rout":
        if len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                player_owning_card = self.p1
                if game_update_string[1] == "2":
                    player_owning_card = self.p2
                if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    player_owning_card.rout_unit(planet_pos, unit_pos)
                    another_trigger = False
                    if primary_player.resources > 0 and self.cult_duplicity_available:
                        if self.replaced_planets[self.last_planet_checked_for_battle]:
                            if primary_player.search_card_in_hq("Cult of Duplicity"):
                                another_trigger = True
                    if another_trigger:
                        self.choices_available = ["Duplicate", "Pass"]
                        self.choice_context = "Cult of Duplicity"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                    else:
                        await self.resolve_battle_conclusion(name, game_update_string)
    else:
        if len(game_update_string) == 2 and self.chosen_first_card:
            if game_update_string[0] == "PLANETS":
                destination = int(game_update_string[1])
                if destination != self.misc_target_unit[1]:
                    og_pla, og_pos = self.misc_target_unit
                    primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    primary_player.move_unit_to_planet(og_pla, og_pos, destination)
                    another_trigger = False
                    if primary_player.resources > 0 and self.cult_duplicity_available:
                        if self.replaced_planets[self.last_planet_checked_for_battle]:
                            if primary_player.search_card_in_hq("Cult of Duplicity"):
                                another_trigger = True
                    if another_trigger:
                        self.choices_available = ["Duplicate", "Pass"]
                        self.choice_context = "Cult of Duplicity"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                    else:
                        await self.resolve_battle_conclusion(name, game_update_string)
        elif len(game_update_string) == 3 and not self.chosen_first_card:
            if game_update_string[0] == "HQ":
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if game_update_string[1] == primary_player.get_number():
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if primary_player.get_cost_given_pos(planet_pos, unit_pos) < 4:
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.chosen_first_card = True
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
        elif len(game_update_string) == 4 and not self.chosen_first_card:
            if game_update_string[0] == "IN_PLAY":
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if game_update_string[1] == primary_player.get_number():
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if primary_player.get_cost_given_pos(planet_pos, unit_pos) < 4:
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.chosen_first_card = True
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)


async def manual_mangeras_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == primary_player.get_number():
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if primary_player.get_damage_given_pos(planet_pos, unit_pos) > 0:
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        await self.resolve_battle_conclusion(name, game_update_string)
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == primary_player.get_number():
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.get_damage_given_pos(planet_pos, unit_pos) > 0:
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        await self.resolve_battle_conclusion(name, game_update_string)


async def manual_petrified_desolations_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            player_owning_card = self.p1
            if game_update_string[1] == "2":
                player_owning_card = self.p2
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if (int(player_owning_card.get_number()), planet_pos, unit_pos) not in self.misc_misc:
                if self.misc_target_choice == "Heal":
                    if player_owning_card.get_damage_given_pos(planet_pos, unit_pos) > 0:
                        player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                        self.misc_counter = self.misc_counter - 1
                        self.misc_misc.append((int(player_owning_card.get_number()), planet_pos, unit_pos))
                        if self.misc_counter < 1:
                            another_trigger = False
                            if primary_player.resources > 0 and self.cult_duplicity_available:
                                if self.replaced_planets[self.last_planet_checked_for_battle]:
                                    if primary_player.search_card_in_hq("Cult of Duplicity"):
                                        another_trigger = True
                            if another_trigger:
                                self.choices_available = ["Duplicate", "Pass"]
                                self.choice_context = "Cult of Duplicity"
                                self.name_player_making_choices = primary_player.name_player
                                self.resolving_search_box = True
                            else:
                                await self.resolve_battle_conclusion(name, game_update_string)
                else:
                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1)
                    self.misc_counter = self.misc_counter - 1
                    self.misc_misc.append((int(player_owning_card.get_number()), planet_pos, unit_pos))
                    if self.misc_counter < 1:
                        self.damage_from_atrox = True
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            player_owning_card = self.p1
            if game_update_string[1] == "2":
                player_owning_card = self.p2
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if (int(player_owning_card.get_number()), planet_pos, unit_pos) not in self.misc_misc:
                if self.misc_target_choice == "Heal":
                    if player_owning_card.get_damage_given_pos(planet_pos, unit_pos) > 0:
                        player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                        self.misc_counter = self.misc_counter - 1
                        self.misc_misc.append((int(player_owning_card.get_number()), planet_pos, unit_pos))
                        if self.misc_counter < 1:
                            another_trigger = False
                            if primary_player.resources > 0 and self.cult_duplicity_available:
                                if self.replaced_planets[self.last_planet_checked_for_battle]:
                                    if primary_player.search_card_in_hq("Cult of Duplicity"):
                                        another_trigger = True
                            if another_trigger:
                                self.choices_available = ["Duplicate", "Pass"]
                                self.choice_context = "Cult of Duplicity"
                                self.name_player_making_choices = primary_player.name_player
                                self.resolving_search_box = True
                            else:
                                await self.resolve_battle_conclusion(name, game_update_string)
                else:
                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1)
                    self.misc_counter = self.misc_counter - 1
                    self.misc_misc.append((int(player_owning_card.get_number()), planet_pos, unit_pos))
                    if self.misc_counter < 1:
                        self.damage_from_atrox = True


async def manual_contaminated_world_adracan_ability(self, name, game_update_string, primary_player, secondary_player):
    if not self.chosen_first_card:
        if len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                if game_update_string[1] == "1":
                    player_owning_card = self.p1
                else:
                    player_owning_card = self.p2
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if planet_pos == self.misc_target_planet or self.misc_target_planet == -1:
                    if (int(player_owning_card.number), planet_pos, unit_pos) not in self.misc_misc:
                        self.misc_misc.append((int(player_owning_card.number), planet_pos, unit_pos))
                        self.misc_counter = self.misc_counter - 1
                        self.misc_target_planet = planet_pos
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos)
                        if self.misc_counter < 1:
                            self.chosen_first_card = True
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "CWA: Infest Planet?"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                            await self.send_update_message("Infest the planet?")


async def manual_beheaded_hope_ability(self, name, game_update_string, primary_player, secondary_player):
    if self.misc_target_choice == "Return":
        if len(game_update_string) == 3:
            if game_update_string[0] == "HQ":
                if game_update_string[1] == primary_player.get_number():
                    planet_pos = -2
                    unit_pos = int(game_update_string[2])
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.return_card_to_hand(planet_pos, unit_pos)
                        primary_player.add_resources(3)
                        another_trigger = False
                        if primary_player.resources > 0 and self.cult_duplicity_available:
                            if self.replaced_planets[self.last_planet_checked_for_battle]:
                                if primary_player.search_card_in_hq("Cult of Duplicity"):
                                    another_trigger = True
                        if another_trigger:
                            self.choices_available = ["Duplicate", "Pass"]
                            self.choice_context = "Cult of Duplicity"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                        else:
                            await self.resolve_battle_conclusion(name, game_update_string)
        elif len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                if game_update_string[1] == primary_player.get_number():
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.return_card_to_hand(planet_pos, unit_pos)
                        primary_player.add_resources(3)
                        another_trigger = False
                        if primary_player.resources > 0 and self.cult_duplicity_available:
                            if self.replaced_planets[self.last_planet_checked_for_battle]:
                                if primary_player.search_card_in_hq("Cult of Duplicity"):
                                    another_trigger = True
                        if another_trigger:
                            self.choices_available = ["Duplicate", "Pass"]
                            self.choice_context = "Cult of Duplicity"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                        else:
                            await self.resolve_battle_conclusion(name, game_update_string)
    else:
        if self.chosen_first_card:
            if len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    await DeployPhase.deploy_card_routine(self, name, int(game_update_string[1]),
                                                          discounts=2)
                    another_trigger = False
                    if primary_player.resources > 0 and self.cult_duplicity_available:
                        if self.replaced_planets[self.last_planet_checked_for_battle]:
                            if primary_player.search_card_in_hq("Cult of Duplicity"):
                                another_trigger = True
                    if another_trigger:
                        self.choices_available = ["Duplicate", "Pass"]
                        self.choice_context = "Cult of Duplicity"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                    else:
                        await self.resolve_battle_conclusion(name, game_update_string)
        else:
            if len(game_update_string) == 3:
                if game_update_string[0] == "HAND":
                    if game_update_string[1] == primary_player.get_number():
                        hand_pos = int(game_update_string[2])
                        card = primary_player.get_card_in_hand(hand_pos)
                        if card.get_card_type() == "Army":
                            self.card_to_deploy = card
                            primary_player.aiming_reticle_coords_hand = hand_pos
                            primary_player.aiming_reticle_color = "blue"
                            self.chosen_first_card = True


async def manual_bhorsapolis_the_decadent_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HAND":
            if game_update_string[1] == primary_player.get_number():
                card = primary_player.get_card_in_hand(int(game_update_string[2]))
                if not card.check_for_a_trait("Elite"):
                    if card.get_card_type() == "Army":
                        primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                        primary_player.aiming_reticle_coords_discard = None
                        self.misc_target_choice = card.get_name()
                        self.choices_available = ["HQ", "Last Planet"]
                        self.choice_context = "BTD: Last Planet or HQ?"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
        if game_update_string[0] == "IN_DISCARD":
            if game_update_string[1] == primary_player.get_number():
                card = primary_player.get_card_in_discard(int(game_update_string[2]))
                if not card.check_for_a_trait("Elite"):
                    if card.get_card_type() == "Army":
                        primary_player.aiming_reticle_coords_discard = int(game_update_string[2])
                        primary_player.aiming_reticle_coords_hand = None
                        self.misc_target_choice = card.get_name()
                        self.choices_available = ["HQ", "Last Planet"]
                        self.choice_context = "BTD: Last Planet or HQ?"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True


async def manual_daprians_gate_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if player_owning_card.get_ready_given_pos(planet_pos, unit_pos):
                    player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                    player_owning_card.headquarters[unit_pos].cannot_ready_hq_phase = True
                    await self.resolve_battle_conclusion(planet_pos, unit_pos)
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if player_owning_card.get_ready_given_pos(planet_pos, unit_pos):
                    player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                    player_owning_card.cards_in_play[planet_pos + 1][unit_pos].cannot_ready_hq_phase = True
                    await self.resolve_battle_conclusion(planet_pos, unit_pos)


async def manual_ironforge_ability(self, name, game_update_string, primary_player, secondary_player):
    if self.chosen_first_card:
        if len(game_update_string) == 3:
            if game_update_string[0] == "HQ":
                if game_update_string[1] == primary_player.get_number():
                    planet_pos = -2
                    unit_pos = int(game_update_string[2])
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.increase_attack_of_unit_at_pos(
                            planet_pos, unit_pos, 2, expiration="EOG")
                        primary_player.increase_health_of_unit_at_pos(
                            planet_pos, unit_pos, 2, expiration="EOG")
                        await self.resolve_battle_conclusion(name, game_update_string)
    else:
        if len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                if game_update_string[1] == primary_player.get_number():
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                        self.chosen_first_card = True
                        await self.send_update_message("You may increase the stats of a unit in the HQ.")


async def manual_craftworld_lugath_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if self.misc_target_choice == "Copy Adjacent":
                if abs(self.last_planet_checked_for_battle - int(game_update_string[1])):
                    self.battle_ability_to_resolve = self.planet_array[int(game_update_string[1])]
                    self.choices_available = ["Yes", "No"]
                    self.choice_context = "Resolve Battle Ability?"
                    self.name_player_making_choices = name
            else:
                if self.last_planet_checked_for_battle != int(game_update_string[1]):
                    temp = self.planet_array[int(game_update_string[1])]
                    self.planet_array[int(game_update_string[1])] = \
                        self.planet_array[self.last_planet_checked_for_battle]
                    self.planet_array[self.last_planet_checked_for_battle] = temp
                    await self.resolve_battle_conclusion(name, game_update_string)


async def manual_baneful_veil_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if abs(self.last_planet_checked_for_battle - int(game_update_string[1])) == 1:
                self.battle_ability_to_resolve = self.planet_array[int(game_update_string[1])]
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Resolve Battle Ability?"
                self.name_player_making_choices = name


async def manual_kunarog_the_slave_market_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if self.misc_target_choice:
                for i in range(2):
                    primary_player.summon_token_at_planet(self.misc_target_choice,
                                                          int(game_update_string[1]),
                                                          already_exhausted=True)
                await self.resolve_battle_conclusion(name, game_update_string)


async def manual_tool_of_abolition_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            player_owning_card = self.p1
            if game_update_string[1] == "2":
                player_owning_card = self.p2
            if player_owning_card.check_is_unit_at_pos(planet_pos, unit_pos):
                if self.misc_target_choice == "Ready":
                    player_owning_card.ready_given_pos(planet_pos, unit_pos)
                    player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                    another_trigger = False
                    if primary_player.resources > 0 and self.cult_duplicity_available:
                        if self.replaced_planets[self.last_planet_checked_for_battle]:
                            if primary_player.search_card_in_hq("Cult of Duplicity"):
                                another_trigger = True
                    if another_trigger:
                        self.choices_available = ["Duplicate", "Pass"]
                        self.choice_context = "Cult of Duplicity"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                    else:
                        await self.resolve_battle_conclusion(name, game_update_string)
                elif player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 2)
                    self.damage_from_atrox = True
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            player_owning_card = self.p1
            if game_update_string[1] == "2":
                player_owning_card = self.p2
            if player_owning_card.check_is_unit_at_pos(planet_pos, unit_pos):
                if self.misc_target_choice == "Ready":
                    player_owning_card.ready_given_pos(planet_pos, unit_pos)
                    player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                    another_trigger = False
                    if primary_player.resources > 0 and self.cult_duplicity_available:
                        if self.replaced_planets[self.last_planet_checked_for_battle]:
                            if primary_player.search_card_in_hq("Cult of Duplicity"):
                                another_trigger = True
                    if another_trigger:
                        self.choices_available = ["Duplicate", "Pass"]
                        self.choice_context = "Cult of Duplicity"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                    else:
                        await self.resolve_battle_conclusion(name, game_update_string)
                elif player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 2)
                    self.damage_from_atrox = True


async def manual_hells_theet_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if game_update_string[1] == primary_player.get_number():
                if self.misc_target_choice == "Health":
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 3,
                                                                      expiration="EOG")
                        another_trigger = False
                        if primary_player.resources > 0 and self.cult_duplicity_available:
                            if self.replaced_planets[self.last_planet_checked_for_battle]:
                                if primary_player.search_card_in_hq("Cult of Duplicity"):
                                    another_trigger = True
                        if another_trigger:
                            self.choices_available = ["Duplicate", "Pass"]
                            self.choice_context = "Cult of Duplicity"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                        else:
                            await self.resolve_battle_conclusion(name, game_update_string)
                else:
                    if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                        primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                        self.misc_counter = self.misc_counter - 1
                        if self.misc_counter < 1:
                            another_trigger = False
                            if primary_player.resources > 0 and self.cult_duplicity_available:
                                if self.replaced_planets[self.last_planet_checked_for_battle]:
                                    if primary_player.search_card_in_hq("Cult of Duplicity"):
                                        another_trigger = True
                            if another_trigger:
                                self.choices_available = ["Duplicate", "Pass"]
                                self.choice_context = "Cult of Duplicity"
                                self.name_player_making_choices = primary_player.name_player
                                self.resolving_search_box = True
                            else:
                                await self.resolve_battle_conclusion(name, game_update_string)
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if game_update_string[1] == primary_player.get_number():
                if self.misc_target_choice == "Health":
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 3,
                                                                      expiration="EOG")
                        another_trigger = False
                        if primary_player.resources > 0 and self.cult_duplicity_available:
                            if self.replaced_planets[self.last_planet_checked_for_battle]:
                                if primary_player.search_card_in_hq("Cult of Duplicity"):
                                    another_trigger = True
                        if another_trigger:
                            self.choices_available = ["Duplicate", "Pass"]
                            self.choice_context = "Cult of Duplicity"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                        else:
                            await self.resolve_battle_conclusion(name, game_update_string)
                else:
                    primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        another_trigger = False
                        if primary_player.resources > 0 and self.cult_duplicity_available:
                            if self.replaced_planets[self.last_planet_checked_for_battle]:
                                if primary_player.search_card_in_hq("Cult of Duplicity"):
                                    another_trigger = True
                        if another_trigger:
                            self.choices_available = ["Duplicate", "Pass"]
                            self.choice_context = "Cult of Duplicity"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                        else:
                            await self.resolve_battle_conclusion(name, game_update_string)


async def manual_erekiel_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if game_update_string[1] == primary_player.get_number():
                if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                    primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        self.player_resolving_battle_ability = secondary_player.name_player
                        await self.resolve_battle_conclusion(name, game_update_string)
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if game_update_string[1] == primary_player.get_number():
                primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                self.misc_counter = self.misc_counter - 1
                if self.misc_counter < 1:
                    await self.resolve_battle_conclusion(name, game_update_string)


async def manual_essio_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HAND":
            if game_update_string[1] == primary_player.get_number():
                primary_player.discard_card_from_hand(int(game_update_string[2]))
                self.misc_counter += 1
                if self.misc_counter > 1:
                    self.choices_available = ["Gain 2 Resources", "Draw 2 Cards"]
                    self.choice_context = "Essio Spoils"
                    self.name_player_making_choices = primary_player.name_player
                    self.resolving_search_box = True


async def manual_belis_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HAND":
            if game_update_string[1] == primary_player.get_number():
                primary_player.discard_card_from_hand(int(game_update_string[2]))
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                     game_update_string)


async def manual_coradim_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    primary_player.sacrifice_card_in_hq(unit_pos)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)


async def manual_radex_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        if not primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.choices_available = ["Mobile", "Flying", "Armorbane",
                                                      "Sweep (3)", "Retaliate (4)"]
                            self.choice_context = "Radex Gain"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        if not primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.choices_available = ["Mobile", "Flying", "Armorbane",
                                                      "Sweep (3)", "Retaliate (4)"]
                            self.choice_context = "Radex Gain"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True


async def manual_langeran_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            target_player = self.p1
            if game_update_string[1] == "2":
                target_player = self.p2
            if target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" or \
                    target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                target_player.set_blanked_given_pos(planet_pos, unit_pos, exp="EOR2")
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                     game_update_string)
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            target_player = self.p1
            if game_update_string[1] == "2":
                target_player = self.p2
            if target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" or \
                    target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                target_player.set_blanked_given_pos(planet_pos, unit_pos, exp="EOR2")
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                     game_update_string)


async def manual_xorlom_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if game_update_string[1] == primary_player.get_number():
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    primary_player.rout_unit(planet_pos, unit_pos)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)


async def manual_josoon_ability(self, name, game_update_string, primary_player, secondary_player):
    if not self.chosen_first_card:
        if len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                target_player = self.p1
                if game_update_string[1] == "2":
                    target_player = self.p2
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if target_player.get_ready_given_pos(planet_pos, unit_pos):
                        target_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
                        self.misc_target_player = target_player.name_player
    else:
        if len(game_update_string) == 2:
            if game_update_string[0] == "PLANETS":
                target_player = self.p1
                if self.misc_target_player == self.name_2:
                    target_player = self.p2
                og_pla, og_pos = self.misc_target_unit
                chosen_planet = int(game_update_string[1])
                if abs(chosen_planet - og_pla) == 1:
                    target_player.move_unit_to_planet(og_pla, og_pos, chosen_planet)
                    await self.resolve_battle_conclusion(name, game_update_string)


async def manual_fenos_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 3:
        if game_update_string[0] == "HQ":
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            target_player = self.p1
            if game_update_string[1] == "2":
                target_player = self.p2
            if target_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if self.misc_target_unit == (-1, -1):
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.chosen_first_card = True
                    self.misc_target_player = target_player.name_player
                else:
                    first_dmg_pla, first_dmg_pos = self.misc_target_unit
                    self.damage_from_atrox = True
                    if self.misc_target_player == target_player.name_player and (first_dmg_pla, first_dmg_pos) == (
                            planet_pos, unit_pos):
                        target_player.assign_damage_to_pos(planet_pos, unit_pos, 2, by_enemy_unit=False)
                    else:
                        first_dmg_player = self.p1
                        if self.misc_target_player == self.name_2:
                            first_dmg_player = self.p2
                        first_dmg_player.assign_damage_to_pos(first_dmg_pla, first_dmg_pos, 1,
                                                              by_enemy_unit=False)
                        target_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            target_player = self.p1
            if game_update_string[1] == "2":
                target_player = self.p2
            if target_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if self.misc_target_unit == (-1, -1):
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.chosen_first_card = True
                    self.misc_target_player = target_player.name_player
                else:
                    first_dmg_pla, first_dmg_pos = self.misc_target_unit
                    self.damage_from_atrox = True
                    if self.misc_target_player == target_player.name_player and (
                            first_dmg_pla, first_dmg_pos) == (planet_pos, unit_pos):
                        target_player.assign_damage_to_pos(planet_pos, unit_pos, 2, by_enemy_unit=False)
                    else:
                        first_dmg_player = self.p1
                        if self.misc_target_player == self.name_2:
                            first_dmg_player = self.p2
                        first_dmg_player.assign_damage_to_pos(first_dmg_pla, first_dmg_pos, 1,
                                                              by_enemy_unit=False)
                        target_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)


async def manual_ice_world_hydras_iv_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            self.card_to_deploy = self.preloaded_find_card(self.misc_target_choice)
            primary_player.deck.remove(self.misc_target_choice)
            primary_player.shuffle_deck()
            self.misc_player_storage = "RESOLVING Ice World Hydras IV"
            await DeployPhase.deploy_card_routine(self, name, int(game_update_string[1]), discounts=1)
            self.misc_player_storage = ""
            await self.resolve_battle_conclusion(name, game_update_string)


async def manual_hissan_xi_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            self.player_resolving_battle_ability = secondary_player.name_player
            self.battle_ability_to_resolve = self.planet_array[int(game_update_string[1])]
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Resolve Battle Ability?"
            self.name_player_making_choices = secondary_player.name_player


async def manual_carnath_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            self.battle_ability_to_resolve = self.planet_array[int(game_update_string[1])]
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Resolve Battle Ability?"
            self.name_player_making_choices = name
            self.different_atrox_origin = int(game_update_string[1])


async def manual_ferrin_ability(self, name, game_update_string, primary_player, secondary_player):
    if len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            player_owning_card = primary_player
            if game_update_string[1] != player_owning_card.get_number():
                player_owning_card = secondary_player
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                can_continue = True
                if self.player_resolving_battle_ability != player_owning_card.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos, move_from_planet=True)
                    if possible_interrupts:
                        can_continue = False
                        await self.send_update_message(
                            "Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = "Ferrin"
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Ferrin"
                if can_continue:
                    player_owning_card.rout_unit(planet_pos, unit_pos)
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                         game_update_string)

def osus_iv_ability(p_win, p_lose):
    if p_lose.spend_resources(1):
        p_win.add_resources(1)


def iridial_ability(p_win, p_lose):
    print("Iridial ability")


def plannum_ability(p_win, p_lose):
    print("Plannum ability")


def tarrus_ability(p_win, p_lose):
    print("Tarrus ability")


def yvarn_ability(p_win, p_lose):
    print("Y'varn ability")


def barlus_ability(p_lose):
    print("Barlus ability")


def ferrin_ability(p_win, p_lose):
    print("Ferrin ability")


def carnath_ability(p_win, p_lose):
    print("Carnath ability")


def elouith_ability(p_win, p_lose):
    print("Elouith ability")


def atrox_prime_ability(p_win, p_lose, pos_planet):
    print("Atrox Prime ability")
