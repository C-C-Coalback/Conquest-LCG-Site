async def catachan_outpost(self, primary_player, player_owning_card, unit_pos):
    if player_owning_card.check_is_unit_at_pos(-2, unit_pos):
        player_owning_card.increase_attack_of_unit_at_pos(-2, unit_pos, 2, expiration="NEXT")
        primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0], self.action_object.position_of_actioned_card[1])
        self.action_cleanup()