async def resolve_in_play_attachment_interrupt(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = int(game_update_string[3])
    unit_pos = int(game_update_string[4])
    attachment_pos = int(game_update_string[5])
    if game_update_string[1] == primary_player.number:
        player_owning_card = primary_player
    else:
        player_owning_card = secondary_player
    current_interrupt = self.interrupts_waiting_on_resolution[0]
    if current_interrupt == "World Engine Beam":
        player_owning_card.destroy_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
        self.delete_interrupt()
