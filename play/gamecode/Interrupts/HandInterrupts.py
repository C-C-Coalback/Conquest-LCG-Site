import copy

from .. import FindCard


async def resolve_hand_interrupt(self, name, game_update_string, primary_player, secondary_player):
    hand_pos = int(game_update_string[2])
    interrupt = self.interrupts_waiting_on_resolution[0]
    current_interrupt = interrupt.get_interrupt_name()
    if current_interrupt == "Flayed Ones Revenants":
        primary_player.discard_card_from_hand(hand_pos)
        interrupt.misc_counter += 1
        if interrupt.misc_counter > 1:
            self.delete_interrupt()
