from .. import FindCard
from ..Phases import CombatPhase


async def resolve_in_play_reaction(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = int(game_update_string[2])
    unit_pos = int(game_update_string[3])
    print("Check what player")
    print(self.player_who_resolves_reaction)
    current_reaction = self.reactions_needing_resolving[0]
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
        elif self.reactions_needing_resolving[0] == "Commander Shadowsun hand":
            if self.location_hand_attachment_shadowsun != -1:
                if planet_pos == primary_player.warlord_commit_location:
                    if game_update_string[1] == primary_player.number:
                        player_receiving_attachment = primary_player
                        not_own_attachment = False
                    else:
                        player_receiving_attachment = secondary_player
                        not_own_attachment = True
                    card = FindCard.find_card(primary_player.cards[self.location_hand_attachment_shadowsun],
                                              self.card_array, self.cards_dict)
                    army_unit_as_attachment = False
                    if card.get_name() == "Shadowsun's Stealth Cadre":
                        army_unit_as_attachment = True
                    if player_receiving_attachment.play_attachment_card_to_in_play(
                            card, planet_pos, unit_pos, discounts=card.get_cost(),
                            not_own_attachment=not_own_attachment,
                            army_unit_as_attachment=army_unit_as_attachment):
                        primary_player.remove_card_from_hand(self.location_hand_attachment_shadowsun)
                        primary_player.aiming_reticle_coords_hand = None
                        self.shadowsun_chose_hand = False
                        self.location_hand_attachment_shadowsun = -1
                        self.resolving_search_box = False
                        self.delete_reaction()
                    else:
                        await self.send_update_message("Invalid target")
        elif self.reactions_needing_resolving[0] == "Commander Shadowsun discard":
            if planet_pos == primary_player.warlord_commit_location:
                if game_update_string[1] == primary_player.number:
                    player_receiving_attachment = primary_player
                    own_attachment = True
                else:
                    player_receiving_attachment = secondary_player
                    own_attachment = False
                card = FindCard.find_card(self.name_attachment_discard_shadowsun, self.card_array,
                                          self.cards_dict)
                army_unit_as_attachment = False
                if card.get_name() == "Shadowsun's Stealth Cadre":
                    army_unit_as_attachment = True
                if player_receiving_attachment.play_attachment_card_to_in_play(
                        card, planet_pos, unit_pos, discounts=card.get_cost(),
                        not_own_attachment=own_attachment,
                        army_unit_as_attachment=army_unit_as_attachment):
                    i = 0
                    removed_card = False
                    while i < len(primary_player.discard) and not removed_card:
                        if primary_player.discard[i] == self.name_attachment_discard_shadowsun:
                            removed_card = True
                            del primary_player.discard[i]
                    self.name_attachment_discard_shadowsun = ""
                    self.resolving_search_box = False
                    self.delete_reaction()
                else:
                    await self.send_update_message("Invalid target")
        elif self.reactions_needing_resolving[0] == "Ku'gath Plaguefather":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if primary_player.number == game_update_string[1]:
                    if unit_pos != self.positions_of_unit_triggering_reaction[0][2]:
                        primary_player.remove_damage_from_pos(self.positions_of_unit_triggering_reaction[0][1],
                                                              self.positions_of_unit_triggering_reaction[0][2], 1)
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False, is_reassign=True,
                                                            rickety_warbuggy=True)
                        self.delete_reaction()
                else:
                    primary_player.remove_damage_from_pos(self.positions_of_unit_triggering_reaction[0][1],
                                                          self.positions_of_unit_triggering_reaction[0][2], 1)
                    secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False, is_reassign=True,
                                                          rickety_warbuggy=True)
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
        elif current_reaction == "Inspirational Fervor":
            if game_update_string[1] == primary_player.number:
                if self.misc_target_planet == planet_pos:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                        self.chosen_first_card = True
                        if self.misc_target_unit == (-1, -1):
                            self.misc_target_unit = (planet_pos, unit_pos)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        elif self.misc_target_unit_2 == (-1, -1):
                            self.misc_target_unit_2 = (planet_pos, unit_pos)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
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
        elif self.reactions_needing_resolving[0] == "Prodigal Sons Disciple":
            if game_update_string[1] == secondary_player.number:
                att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
                if att_pla == planet_pos:
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
                            command = secondary_player.get_command_given_pos(planet_pos, unit_pos)
                            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, command, preventable=False,
                                                                  rickety_warbuggy=True)
                            self.delete_reaction()
        elif current_reaction == "Vezuel's Hunters":
            if game_update_string[1] == secondary_player.number:
                att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
                if att_pla == planet_pos:
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
                            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, preventable=False,
                                                                  rickety_warbuggy=True)
                            self.delete_reaction()
        elif current_reaction == "Mandrake Cutthroat":
            att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
            if att_pla == planet_pos:
                if game_update_string[1] == "1":
                    player_being_hit = self.p1
                else:
                    player_being_hit = self.p2
                if player_being_hit.check_for_trait_given_pos(planet_pos, unit_pos, "Ally"):
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
        elif current_reaction == "Deathstorm Drop Pod":
            if game_update_string[1] == secondary_player.number:
                att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
                if att_pla == planet_pos:
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
                        self.delete_reaction()
        elif current_reaction == "Crush of Sky-Slashers":
            if game_update_string[1] == secondary_player.number:
                att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
                if att_pla == planet_pos:
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if secondary_player.get_cost_given_pos(planet_pos, unit_pos) < 3:
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
                                secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, preventable=False,
                                                                      rickety_warbuggy=True, shadow_field_possible=True)
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
        elif self.reactions_needing_resolving[0] == "Commander Starblaze":
            if game_update_string[1] == primary_player.number:
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum":
                    war_num, war_pla, war_pos = self.positions_of_unit_triggering_reaction[0]
                    if abs(war_pla - planet_pos) == 1:
                        primary_player.move_unit_to_planet(planet_pos, unit_pos, war_pla)
                        self.delete_reaction()
        elif current_reaction == "Ravening Psychopath":
            if game_update_string[1] == secondary_player.number:
                if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, shadow_field_possible=True,
                                                              rickety_warbuggy=True)
                        self.delete_reaction()
        elif current_reaction == "Deathly Web Shrine":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if game_update_string[1] == "1":
                    player_being_hit = self.p1
                else:
                    player_being_hit = self.p2
                if not player_being_hit.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        player_being_hit.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                        self.delete_reaction()
        elif current_reaction == "Wildrider Vyper":
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            og_num, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
            if og_pla != planet_pos:
                if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].valid_target_ashen_banner:
                    primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    primary_player.move_unit_to_planet(og_pla, og_pos, planet_pos)
                    self.delete_reaction()
        elif current_reaction == "Staff of Change":
            if secondary_player.get_number() == game_update_string[1]:
                if self.positions_of_unit_triggering_reaction[0][1] == planet_pos:
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
                        secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2)
                        self.delete_reaction()
        elif current_reaction == "Shadowed Thorns Venom":
            if not self.chosen_first_card:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].shadowed_thorns_venom_valid:
                        self.chosen_first_card = True
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].shadowed_thorns_venom_valid = False
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                        self.misc_target_unit = (planet_pos, unit_pos)
        elif current_reaction == "Vow of Honor":
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].valid_target_vow_of_honor:
                primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 3, expiration="NEXT")
                self.delete_reaction()
                target_name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                await self.send_update_message(target_name + " got +3 ATK from Vow of Honor")
                if primary_player.resources > 0 and primary_player.search_hand_for_card("Vow of Honor"):
                    self.create_reaction("Vow of Honor", primary_player.name_player,
                                         (int(primary_player.number), -1, -1))
        elif self.reactions_needing_resolving[0] == "Kabalite Harriers":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if game_update_string[1] == "1":
                    player_being_hit = self.p1
                else:
                    player_being_hit = self.p2
                if player_being_hit.get_damage_given_pos(planet_pos, unit_pos) == 0:
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
                        player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True)
                        self.advance_damage_aiming_reticle()
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
                        player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 2, context="Veteran Barbrus",
                                                              rickety_warbuggy=True)
                        self.advance_damage_aiming_reticle()
                        self.delete_reaction()
                else:
                    await self.send_update_message(
                        "Forbidden faction for Veteran Barbrus.")
        elif self.reactions_needing_resolving[0] == "Blazing Zoanthrope":
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
                                secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True)
                            else:
                                secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True)
                            secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Fire Prism":
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
                            secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                            self.delete_reaction()
        elif current_reaction == "Devourer Venomthrope":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if secondary_player.get_number() == game_update_string[1]:
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if not secondary_player.check_for_trait_given_pos(planet_pos, unit_pos):
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
                                secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Obedience":
            if game_update_string[1] == primary_player.number:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) != "Necrons":
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        elif current_reaction == "8th Company Assault Squad":
            if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                if game_update_string[1] == "1":
                    target_player = self.p1
                else:
                    target_player = self.p2
                if not target_player.get_ready_given_pos(planet_pos, unit_pos) and\
                        target_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                    can_continue = True
                    if target_player.name_player == secondary_player.name_player:
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
                        target_player.ready_given_pos(planet_pos, unit_pos)
                        self.delete_reaction()
        elif current_reaction == "Kommando Sneakaz":
            if game_update_string[1] == primary_player.get_number():
                if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Orks":
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Invasive Genestealers":
            if game_update_string[1] == secondary_player.get_number():
                if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
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
                        secondary_player.cards_in_play[planet_pos + 1][unit_pos].negative_hp_until_eop += 1
                        _, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
                        primary_player.cards_in_play[og_pla + 1][og_pos].positive_hp_until_eop += 1
                        self.delete_reaction()
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
        elif current_reaction == "Raiding Portal":
            if not self.chosen_first_card:
                if planet_pos == self.misc_target_planet:
                    if game_update_string[1] == primary_player.get_number():
                        if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Kabalite"):
                            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                                self.misc_target_unit = (planet_pos, unit_pos)
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                                self.chosen_first_card = True
        elif self.reactions_needing_resolving[0] == "Made Ta Fight":
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            if self.misc_target_planet == planet_pos:
                if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                    can_continue = True
                    if player_being_hit.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos, power=True):
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
                            self.cost_card_nullified = 2
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction Event"
                    if can_continue:
                        primary_player.spend_resources(2)
                        primary_player.discard_card_name_from_hand("Made Ta Fight")
                        player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter)
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
                            player_exhausting_unit.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
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
                        secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, context="Ragnar Blackmane",
                                                              rickety_warbuggy=True)
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
        elif current_reaction == "Tactical Withdrawal":
            if self.chosen_first_card:
                if game_update_string[1] == primary_player.get_number():
                    _, og_pla, _ = self.positions_of_unit_triggering_reaction[0]
                    dest = self.misc_target_planet
                    if planet_pos == og_pla:
                        primary_player.move_unit_to_planet(planet_pos, unit_pos, dest)
        elif current_reaction == "Phoenix Attack Fighter":
            if game_update_string[1] == secondary_player.number:
                if self.positions_of_unit_triggering_reaction[0][1] == planet_pos:
                    if not secondary_player.get_ready_given_pos(planet_pos, unit_pos):
                        secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 3, rickety_warbuggy=True)
                        self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Shrouded Harlequin":
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
                    secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
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
        elif self.reactions_needing_resolving[0] == "Commissarial Bolt Pistol":
            og_num, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
            if planet_pos == og_pla:
                can_continue = True
                if og_num == int(game_update_string[1]):
                    player_owning_card = primary_player
                else:
                    player_owning_card = secondary_player
                if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if player_owning_card.name_player == secondary_player.name_player:
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
                            self.nullified_card_name = "Commissarial Bolt Pistol"
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Reaction"
                    if can_continue:
                        player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1)
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
                            secondary_player.assign_damage_to_pos(origin_planet, target_unit_pos, 1,
                                                                  rickety_warbuggy=True)
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
                            secondary_player.assign_damage_to_pos(origin_planet, target_unit_pos, damage,
                                                                  rickety_warbuggy=True)
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
                                                                  context="Sicarius's Chosen",
                                                                  rickety_warbuggy=True)
                            self.delete_reaction()
