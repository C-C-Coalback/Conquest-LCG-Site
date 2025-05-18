from .. import FindCard


async def resolve_hand_reaction(self, name, game_update_string, primary_player, secondary_player):
    if game_update_string[1] == primary_player.get_number():
        if self.reactions_needing_resolving[0] == "Wailing Wraithfighter":
            hand_pos = int(game_update_string[2])
            primary_player.discard_card_from_hand(hand_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Banshee Power Sword":
            hand_pos = int(game_update_string[2])
            primary_player.discard_card_from_hand(hand_pos)
            self.banshee_power_sword_extra_attack += 1
        elif self.reactions_needing_resolving[0] == "Elysian Assault Team":
            hand_pos = int(game_update_string[2])
            if primary_player.cards[hand_pos] == "Elysian Assault Team":
                planet_pos = self.positions_of_unit_triggering_reaction[0][1]
                card = FindCard.find_card("Elysian Assault Team", self.card_array)
                primary_player.add_card_to_planet(card, planet_pos)
                del primary_player.cards[hand_pos]
                more = False
                for i in range(len(primary_player.cards)):
                    if primary_player.cards[i] == "Elysian Assault Team":
                        more = True
                if not more:
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Blood Claw Pack":
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.check_for_a_trait("Space Wolves"):
                if card.get_is_unit():
                    num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                    primary_player.add_card_to_planet(card, planet_pos)
                    primary_player.remove_card_from_hand(int(game_update_string[2]))
                    self.delete_reaction()
