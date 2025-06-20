import copy

from .. import FindCard


async def resolve_hq_interrupt(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = -2
    unit_pos = int(game_update_string[2])
    if game_update_string[1] == primary_player.number:
        player_owning_card = primary_player
    else:
        player_owning_card = secondary_player
    current_interrupt = self.interrupts_waiting_on_resolution[0]
    if current_interrupt == "Vanguard Soldiers":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                primary_player.ready_given_pos(planet_pos, unit_pos)
                self.delete_interrupt()
    elif self.interrupts_waiting_on_resolution[0] == "No Mercy":
        if game_update_string[1] == primary_player.number:
            hq_pos = int(game_update_string[2])
            if primary_player.headquarters[hq_pos].get_is_unit() and \
                    primary_player.headquarters[hq_pos].get_unique() and \
                    primary_player.headquarters[hq_pos].get_ready():
                primary_player.exhaust_given_pos(-2, hq_pos)
                primary_player.discard_card_name_from_hand("No Mercy")
                try:
                    secondary_player.discard_card_from_hand(self.pos_shield_card)
                except:
                    pass
                self.delete_interrupt()
                await self.better_shield_card_resolution(secondary_player.name_player, ["pass-P1"],
                                                         alt_shields=False, can_no_mercy=False)
    elif current_interrupt == "World Engine Beam":
        if not player_owning_card.headquarters[unit_pos].get_unique() or \
                player_owning_card.get_card_type_given_pos(-2, unit_pos) == "Support":
            player_owning_card.destroy_card_in_hq(unit_pos)
            self.delete_interrupt()
    elif current_interrupt == "Mucolid Spores":
        if game_update_string[1] == secondary_player.number:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                can_continue = True
                is_support = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    -2, unit_pos, targeting_support=is_support)
                if possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Interrupt"
                if can_continue:
                    secondary_player.destroy_card_in_hq(unit_pos)
                    self.misc_counter += 1
                    if self.misc_counter > 1:
                        self.delete_interrupt()


