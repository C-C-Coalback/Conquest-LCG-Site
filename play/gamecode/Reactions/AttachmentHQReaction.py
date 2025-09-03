

async def resolve_attachment_hq_reaction(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = -2
    unit_pos = int(game_update_string[3])
    attachment_pos = int(game_update_string[4])
    player_owning_card = self.p1
    if game_update_string[1] == "2":
        player_owning_card = self.p2
    print("Check what player")
    print(self.player_who_resolves_reaction)
    current_reaction = self.reactions_needing_resolving[0]
    if current_reaction == "Torturer's Masks":
        if player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos].get_ability() == "Torturer's Masks":
            if player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos].name_owner == primary_player.name_player:
                if player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos].get_ready():
                    player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos].exhaust_card()
                    primary_player.draw_card()
                    self.delete_reaction()
