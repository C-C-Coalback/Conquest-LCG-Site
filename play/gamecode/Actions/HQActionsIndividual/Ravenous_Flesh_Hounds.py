async def ravenous_flesh_hounds(self, game_update_string, primary_player, secondary_player, planet_pos, unit_pos):
    if primary_player.get_number() == game_update_string[1]:
        if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Cultist"):
            if primary_player.sacrifice_card_in_hq(unit_pos):
                if planet_pos == self.action_object.position_of_actioned_card[0]:
                    if self.action_object.position_of_actioned_card[1] > unit_pos:
                        self.action_object.position_of_actioned_card = (planet_pos, self.action_object.position_of_actioned_card[1] - 1)
                primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0], self.action_object.position_of_actioned_card[1])
                primary_player.remove_damage_from_pos(self.action_object.position_of_actioned_card[0], self.action_object.position_of_actioned_card[1], 999, healing=True)
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                self.action_cleanup()
                self.action_object.position_of_actioned_card = (-1, -1)
        else:
            await self.send_mistarget_message(primary_player.name_player, "Invalid Target", "Card is not a Cultist unit.")