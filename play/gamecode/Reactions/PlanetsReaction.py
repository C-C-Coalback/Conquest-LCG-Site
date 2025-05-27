from .. import FindCard


async def resolve_planet_reaction(self, name, game_update_string, primary_player, secondary_player):
    chosen_planet = int(game_update_string[1])
    current_reaction = self.reactions_needing_resolving[0]
    if self.reactions_needing_resolving[0] == "Blackmane's Hunt":
        warlord_planet = primary_player.warlord_commit_location
        new_planet = int(game_update_string[1])
        if abs(warlord_planet - new_planet) == 1:
            primary_player.commit_warlord_to_planet_from_planet(warlord_planet, new_planet)
            self.delete_reaction()
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
    elif current_reaction == "Exploratory Drone":
        p_num, origin_planet, origin_pos = self.positions_of_unit_triggering_reaction[0]
        if abs(origin_planet - chosen_planet) == 1:
            primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
        self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Foresight":
        warlord_planet = primary_player.warlord_commit_location
        new_planet = int(game_update_string[1])
        if warlord_planet != new_planet:
            primary_player.commit_warlord_to_planet_from_planet(warlord_planet, new_planet)
            self.delete_reaction()
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
    elif self.reactions_needing_resolving[0] == "Wyrdboy Stikk":
        primary_player.summon_token_at_planet("Snotlings", chosen_planet)
        self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Cry of the Wind":
        if self.chosen_first_card:
            origin_planet, origin_pos = self.misc_target_unit
            if abs(origin_planet - chosen_planet) == 1:
                primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
                self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Heretek Inventor":
        p_num, origin_planet, origin_pos = self.positions_of_unit_triggering_reaction[0]
        if origin_planet != chosen_planet:
            secondary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
            self.delete_reaction()
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
                self.positions_of_unit_triggering_reaction[0] = (int(primary_player.number),
                                                                 chosen_planet, new_pos)
    elif self.reactions_needing_resolving[0] == "Spore Chimney":
        self.infest_planet(int(game_update_string[1]))
        self.delete_reaction()
