from .. import FindCard
import copy


async def update_intercept_hq(self, primary_player, secondary_player, name, game_update_string, name_effect):
    planet_pos = -2
    unit_pos = int(game_update_string[2])
    if name_effect == "Catachan Outpost":
        if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 2, expiration="NEXT")
            name_unit = primary_player.get_name_given_pos(planet_pos, unit_pos)
            await self.send_update_message(name_unit + " got +2 ATK")
            self.action_cleanup()
            self.complete_intercept()
