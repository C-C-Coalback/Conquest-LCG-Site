from .. import FindCard


async def resolve_planet_reaction(self, name, game_update_string, primary_player, secondary_player):
    chosen_planet = int(game_update_string[1])
    if self.reactions_needing_resolving[0] == "Foresight":
        warlord_planet = primary_player.warlord_commit_location
        new_planet = int(game_update_string[1])
        if abs(warlord_planet - new_planet) == 1:
            primary_player.commit_warlord_to_planet_from_planet(warlord_planet, new_planet)
            self.delete_reaction()
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
    elif self.reactions_needing_resolving[0] == "Obedience":
        if self.chosen_first_card:
            origin_planet, origin_pos = self.misc_target_unit
            new_planet = int(game_update_string[1])
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, new_planet)
            self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
        if self.chosen_first_card and not self.chosen_second_card:
            current_planet, current_position = self.misc_target_unit
            if current_planet != chosen_planet:
                primary_player.move_unit_to_planet(current_planet, current_position, chosen_planet)
                self.chosen_second_card = True
                new_pos = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
                self.misc_target_unit = (chosen_planet, new_pos)
    elif self.reactions_needing_resolving[0] == "Spore Chimney":
        self.infested_planets[int(game_update_string[1])] = True
        self.delete_reaction()
