from .. import FindCard


async def start_resolving_interrupt(self, name, game_update_string):
    if self.player_resolving_interrupts[0] == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if not self.resolving_search_box:
        if self.interrupts_waiting_on_resolution[0] == "Interrogator Acolyte":
            primary_player.draw_card()
            primary_player.draw_card()
            self.delete_interrupt()
