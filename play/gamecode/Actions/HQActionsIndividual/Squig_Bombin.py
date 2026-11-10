async def squig_bombin(self, game_update_string, primary_player, secondary_player, player_owning_card, planet_pos, unit_pos):
    if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
        can_continue = True
        is_support = True
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                -2, unit_pos, targeting_support=is_support, event=True)
            if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy events.")
            elif possible_interrupts:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_object.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
        if can_continue:
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
            if player_owning_card.get_ability_given_pos(planet_pos, unit_pos) == "Reveal The Blade":
                primary_player.discard_card_at_random()
                primary_player.discard_card_at_random()
            player_owning_card.destroy_card_in_hq(unit_pos)
            primary_player.resolve_played_any_event()
            self.action_cleanup()