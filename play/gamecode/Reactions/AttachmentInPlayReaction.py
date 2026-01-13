

async def resolve_attachment_in_play_reaction(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = int(game_update_string[3])
    unit_pos = int(game_update_string[4])
    attachment_pos = int(game_update_string[5])
    extra_info = self.additional_reactions_info[0]
    player_owning_card = self.p1
    if game_update_string[2] == "2":
        player_owning_card = self.p2
    print("Check what player")
    print(self.player_who_resolves_reaction)
    current_reaction = self.reactions_needing_resolving[0]
    if current_reaction == "Junk Chucka Kommando":
        if not self.chosen_first_card:
            if game_update_string[2] == primary_player.get_number():
                og_num, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
                if og_pla == planet_pos and og_pos == unit_pos:
                    primary_player.set_aiming_reticle_in_play(og_pla, og_pos)
                    attachment_name = primary_player.cards_in_play[
                        og_pla + 1][og_pos].get_attachments()[attachment_pos].get_name()
                    await self.send_update_message(attachment_name + " selected for Junk Chucka Kommando!")
                    self.chosen_first_card = True
                    self.misc_target_attachment = (og_pla, og_pos, attachment_pos)
    elif current_reaction == "Neurotic Obliterator":
        og_num, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
        if primary_player.get_number() == game_update_string[2]:
            if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Neurotic Obliterator":
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].check_for_a_trait("Weapon") and \
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_ready():
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].exhaust_card()
                    secondary_player.assign_damage_to_pos(og_pla, og_pos, 1, rickety_warbuggy=True)
                    self.delete_reaction()
    elif current_reaction == "Shadowseer":
        _, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
        if game_update_string[2] == primary_player.get_number():
            if og_pla == planet_pos and og_pos == unit_pos:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_ready():
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].exhaust_card()
                    primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    _, ext_pla, ext_pos = extra_info
                    secondary_player.assign_damage_to_pos(ext_pla, ext_pos, 2)
                    self.delete_reaction()
    elif current_reaction == "Farsight Vanguard":
        if game_update_string[2] == primary_player.get_number():
            if self.chosen_first_card:
                _, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
                second_pla, second_pos = self.misc_target_unit
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].name_owner == primary_player.name_player:
                    if not primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].check_for_a_trait("Drone"):
                        if og_pla == planet_pos and og_pos == unit_pos:
                            if primary_player.move_attachment_card(planet_pos, unit_pos, attachment_pos,
                                                                   second_pla, second_pos):
                                primary_player.reset_aiming_reticle_in_play(second_pla, second_pos)
                                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                                self.delete_reaction()
                        elif second_pla == planet_pos and second_pos == unit_pos:
                            if primary_player.move_attachment_card(planet_pos, unit_pos, attachment_pos,
                                                                   og_pla, og_pos):
                                primary_player.reset_aiming_reticle_in_play(second_pla, second_pos)
                                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                                self.delete_reaction()
    elif current_reaction == "Torturer's Masks":
        if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_ability() == "Torturer's Masks":
            if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].name_owner == primary_player.name_player:
                if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_ready():
                    player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].exhaust_card()
                    primary_player.draw_card()
                    self.delete_reaction()
