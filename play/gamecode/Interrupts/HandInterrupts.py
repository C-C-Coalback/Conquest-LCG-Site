import copy

from .. import FindCard


async def resolve_hand_interrupt(self, name, game_update_string, primary_player, secondary_player):
    hand_pos = int(game_update_string[2])
    current_interrupt = self.interrupts_waiting_on_resolution[0]
    if current_interrupt == "Flayed Ones Revenants":
        primary_player.discard_card_from_hand(hand_pos)
        self.misc_counter += 1
        if self.misc_counter > 1:
            self.delete_interrupt()
