async def tellyporta_pad(self, game_update_string, primary_player, planet_pos, unit_pos):
    if game_update_string[1] == primary_player.get_number():
        card = primary_player.headquarters[unit_pos]
        if card.get_faction() == "Orks":
            if card.get_is_unit():
                primary_player.move_unit_to_planet(planet_pos, unit_pos, self.round_number)
                primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0], self.action_object.position_of_actioned_card[1])
                self.action_cleanup()
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target", "Card is not an Orks unit.")