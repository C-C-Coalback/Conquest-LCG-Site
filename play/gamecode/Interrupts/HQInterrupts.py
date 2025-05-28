import copy

from .. import FindCard


async def resolve_in_play_interrupt(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = -2
    unit_pos = int(game_update_string[2])
    print("Check what player")
    print(self.player_who_resolves_reaction)
    current_interrupt = self.interrupts_waiting_on_resolution[0]
    if current_interrupt == "Vanguard Soldiers":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                primary_player.ready_given_pos(planet_pos, unit_pos)
                self.delete_interrupt()

