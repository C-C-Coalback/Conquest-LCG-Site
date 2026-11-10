async def pact_of_the_haemonculi(self, game_update_string, primary_player, secondary_player, unit_pos):
    if game_update_string[1] == self.number_with_deploy_turn:
        if primary_player.sacrifice_card_in_hq(unit_pos):
            interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
            primary_player.aiming_reticle_coords_hand = None
            if interrupts:
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Enemy Discard Effect?"
                self.resolving_search_box = True
                self.stored_discard_and_target.append((self.action_object.action_chosen, primary_player.number))
            else:
                secondary_player.discard_card_at_random()
                primary_player.draw_card()
                primary_player.draw_card()
                self.action_cleanup()
                await primary_player.dark_eldar_event_played()
                primary_player.resolve_played_any_event()