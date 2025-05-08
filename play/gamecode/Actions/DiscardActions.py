from .. import FindCard


async def update_game_event_action_discard(self, name, game_update_string):
    chosen_discard = int(game_update_string[1])
    pos_discard = int(game_update_string[2])
    if self.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    card_chosen = primary_player.discard[pos_discard]
    if chosen_discard == int(primary_player.number):
        if not self.action_chosen:
            if card_chosen == "Decaying Warrior Squad":
                if self.phase == "COMBAT":
                    primary_player.aiming_reticle_coords_discard = pos_discard
                    print("found a decaying warrior squad.")
                    self.action_chosen = card_chosen
