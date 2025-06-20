from .. import FindCard


async def resolve_discard_reaction(self, name, game_update_string, primary_player, secondary_player):
    chosen_discard = int(game_update_string[1])
    pos_discard = int(game_update_string[2])
    print("Check what player")
    print(self.player_who_resolves_reaction)
    current_reaction = self.reactions_needing_resolving[0]
    if name == self.player_who_resolves_reaction[0]:
        if current_reaction == "Sathariel the Invokator":
            if chosen_discard == int(primary_player.number):
                card = primary_player.get_card_in_discard(pos_discard)
                if card.get_faction() == "Chaos" and card.get_card_type() == "Event":
                    if card.check_for_a_trait("Power"):
                        primary_player.cards.append(card.get_name())
                        del primary_player.discard[pos_discard]
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        self.delete_reaction()
        elif current_reaction == "Parasite of Mortrex":
            if not self.chosen_first_card:
                if chosen_discard == int(primary_player.number):
                    card = primary_player.get_card_in_discard(pos_discard)
                    if card.check_for_a_trait("Condition") and card.get_card_type() == "Attachment":
                        primary_player.aiming_reticle_coords_discard = pos_discard
                        self.misc_player_storage = card.get_name()
                        self.chosen_first_card = True
                        self.misc_counter = 1
        elif current_reaction == "Ghost Ark of Orikan":
            if chosen_discard == int(primary_player.number):
                card = primary_player.get_card_in_discard(pos_discard)
                if card.get_card_type() == "Army" and card.get_faction() == "Necrons" and \
                        (card.check_for_a_trait("Warrior") or card.check_for_a_trait("Soldier")):
                    if card.get_cost() < self.ghost_ark_of_orikan:
                        num, planet, unit = self.positions_of_unit_triggering_reaction[0]
                        primary_player.add_card_to_planet(card, planet)
                        primary_player.remove_card_from_discard(pos_discard)
                        self.delete_reaction()
        elif current_reaction == "Seething Mycetic Spore":
            if chosen_discard == int(primary_player.number):
                card = primary_player.get_card_in_discard(pos_discard)
                if card.get_card_type() == "Army" and card.get_cost() < 2\
                        and card.get_name() != self.misc_player_storage:
                    primary_player.add_card_to_planet(card, self.misc_target_planet)
                    primary_player.remove_card_from_discard(pos_discard)
                    self.misc_counter += 1
                    self.misc_player_storage = card.get_name()
                    if self.misc_counter > 1:
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        self.delete_reaction()
        elif current_reaction == "Hive Ship Tendrils":
            if not self.chosen_first_card:
                if chosen_discard == int(primary_player.number):
                    card = primary_player.get_card_in_discard(pos_discard)
                    if card.get_card_type() == "Army" and card.has_hive_mind:
                        primary_player.aiming_reticle_coords_discard = pos_discard
                        self.chosen_first_card = True
        elif current_reaction == "Spreading Genestealer Brood":
            if chosen_discard == int(primary_player.number):
                card = primary_player.get_card_in_discard(pos_discard)
                if card.get_is_unit() and card.check_for_a_trait("Brood"):
                    primary_player.add_card_to_planet(card, self.positions_of_unit_triggering_reaction[0][1])
                    primary_player.remove_card_from_discard(pos_discard)
                    self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                    self.delete_reaction()
        elif current_reaction == "Sweep Attack":
            if not self.chosen_first_card:
                if chosen_discard == int(primary_player.number):
                    card = primary_player.get_card_in_discard(pos_discard)
                    if card.check_for_a_trait("Condition") and card.get_card_type() == "Attachment":
                        primary_player.aiming_reticle_coords_discard = pos_discard
                        self.misc_player_storage = card.get_name()
                        self.chosen_first_card = True
                        self.misc_counter = 1
        elif current_reaction == "Clearing the Path":
            if chosen_discard == int(primary_player.number):
                card = primary_player.get_card_in_discard(pos_discard)
                if card.get_faction() == "Astra Militarum" and card.get_card_type() == "Support":
                    primary_player.add_to_hq(card)
                    del primary_player.discard[pos_discard]
                    self.delete_reaction()
