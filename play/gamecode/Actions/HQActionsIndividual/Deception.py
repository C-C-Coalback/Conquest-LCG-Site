async def deception(self, game_update_string, primary_player, secondary_player, player_owning_card, planet_pos, unit_pos):
    can_continue = True
    if player_owning_card.name_player == secondary_player.name_player:
        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos, event=True)
        if secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
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
            self.cost_card_nullified = 2
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "Event Action"
    if can_continue:
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                player_owning_card.return_card_to_hand(planet_pos, unit_pos)
                self.action_cleanup()
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target", "Card is an Elite unit.")
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target", "Card is not an army unit.")