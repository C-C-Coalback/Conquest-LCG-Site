async def squadron_redeployment(self, game_update_string, primary_player, planet_pos, unit_pos):
    if not self.action_object.chosen_first_card:
        if game_update_string[1] == primary_player.get_number():
            if primary_player.headquarters[unit_pos].get_attachments():
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    self.action_object.position_of_actioned_card = (planet_pos, unit_pos)
                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                    self.action_object.misc_target_unit = (planet_pos, unit_pos)
                    self.action_object.chosen_first_card = True
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target", "Card is not a ready unit.")
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target", "Card has not attachments.")
    else:
        await self.send_update_message("Already selected unit to move")
