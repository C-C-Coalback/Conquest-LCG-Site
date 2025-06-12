from .. import FindCard


async def start_resolving_interrupt(self, name, game_update_string):
    if self.player_resolving_interrupts[0] == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    current_interrupt = self.interrupts_waiting_on_resolution[0]
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
        elif current_interrupt == "Mucolid Spores":
            self.misc_counter = 0
        elif current_interrupt == "Ulthwe Spirit Stone":
            num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
            primary_player.return_card_to_hand(planet_pos, unit_pos)
            self.reset_choices_available()
            self.delete_interrupt()
        elif current_interrupt == "Death Serves the Emperor":
            primary_player.add_resources(primary_player.highest_death_serves_value)
            primary_player.discard_card_name_from_hand("Death Serves the Emperor")
            self.delete_interrupt()
        elif current_interrupt == "Gorgul Da Slaya":
            secondary_player.hit_by_gorgul = True
            self.mask_jain_zar_check_interrupts(primary_player, secondary_player)
            self.delete_interrupt()
