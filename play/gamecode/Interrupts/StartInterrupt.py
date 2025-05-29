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
        elif self.interrupts_waiting_on_resolution[0] == "M35 Galaxy Lasgun":
            if "M35 Galaxy Lasgun" in primary_player.discard:
                primary_player.discard.remove("M35 Galaxy Lasgun")
                primary_player.cards.append("M35 Galaxy Lasgun")
            if "M35 Galaxy Lasgun" in primary_player.cards_recently_discarded:
                primary_player.cards_recently_discarded.remove("M35 Galaxy Lasgun")
            self.delete_interrupt()
        elif self.interrupts_waiting_on_resolution[0] == "Berzerker Warriors":
            if "Berzerker Warriors" not in primary_player.cards:
                self.delete_interrupt()
            else:
                primary_player.aiming_reticle_coords_hand = primary_player.cards.index("Berzerker Warriors")
                primary_player.aiming_reticle_color = "blue"
