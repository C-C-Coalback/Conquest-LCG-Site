import copy

from .. import FindCard


async def resolve_in_play_interrupt(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = int(game_update_string[2])
    unit_pos = int(game_update_string[3])
    print("Check what player")
    print(self.player_who_resolves_reaction)
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
                    if attachments[i].get_name() in ["Shadowsun's Stealth Cadre", "Gun Drones"]:
                        army = True
                    if not primary_player.attach_card(attachments[i], planet_pos, unit_pos,
                                                      not_own_attachment=not_owner, army_unit_as_attachment=army):
                        attached_all = False
                if not attached_all:
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].attachments = copy_attachments
                if attached_all:
                    primary_player.cards_in_play[og_pla + 1][og_pos].attachments = []
                self.delete_interrupt()
    elif current_interrupt == "Mark of Slaanesh":
        if game_update_string[1] == primary_player.number:
            dest_planet = self.positions_of_units_interrupting[0][1]
            if dest_planet != planet_pos:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    primary_player.move_unit_to_planet(planet_pos, unit_pos, dest_planet)
                    self.delete_interrupt()
    elif current_interrupt == "Vanguard Soldiers":
        if game_update_string[1] == primary_player.number:
            primary_player.ready_given_pos(planet_pos, unit_pos)
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
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                        primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
    elif current_interrupt == "Glorious Intervention":
        if game_update_string[1] == primary_player.get_number():
            pos_holder = self.positions_of_units_to_take_damage[0]
            player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
            sac_planet_pos = int(game_update_string[2])
            sac_unit_pos = int(game_update_string[3])
            if sac_planet_pos == planet_pos:
                if sac_unit_pos != unit_pos:
                    if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos]. \
                            get_card_type() != "Warlord":
                        if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos] \
                                .check_for_a_trait("Warrior") or \
                                primary_player.cards_in_play[sac_planet_pos + 1][unit_pos] \
                                        .check_for_a_trait("Soldier"):
                            primary_player.aiming_reticle_coords_hand = None
                            primary_player.discard_card_from_hand(self.pos_shield_card)
                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.pos_shield_card = -1
                            printed_atk = primary_player.cards_in_play[
                                sac_planet_pos + 1][sac_unit_pos].attack
                            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                            if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                    self.damage_on_units_list_before_new_damage[0]:
                                primary_player.set_damage_given_pos(
                                    planet_pos, unit_pos,
                                    self.damage_on_units_list_before_new_damage[0])
                            primary_player.sacrifice_card_in_play(sac_planet_pos, sac_unit_pos)
                            att_num, att_pla, att_pos = \
                                self.positions_attackers_of_units_to_take_damage[0]
                            secondary_player.assign_damage_to_pos(att_pla, att_pos, printed_atk)
                            self.delete_interrupt()
                            await self.shield_cleanup(primary_player, secondary_player, planet_pos)
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
