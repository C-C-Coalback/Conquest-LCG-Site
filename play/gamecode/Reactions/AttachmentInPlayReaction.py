

async def resolve_attachment_in_play_reaction(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = int(game_update_string[3])
    unit_pos = int(game_update_string[4])
    attachment_pos = int(game_update_string[5])
    player_owning_card = self.p1
    if game_update_string[1] == "2":
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
