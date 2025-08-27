from .. import FindCard


async def resolve_hand_reaction(self, name, game_update_string, primary_player, secondary_player):
    current_reaction = self.reactions_needing_resolving[0]
    hand_pos = int(game_update_string[2])
    if game_update_string[1] == primary_player.get_number():
        print("hand reaction num ok")
        if self.reactions_needing_resolving[0] == "Wailing Wraithfighter":
            hand_pos = int(game_update_string[2])
            primary_player.discard_card_from_hand(hand_pos)
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                self.create_reaction("The Mask of Jain Zar", primary_player.name_player,
                                     (int(secondary_player.number), planet_pos, unit_pos))
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Banshee Power Sword":
            hand_pos = int(game_update_string[2])
            primary_player.discard_card_from_hand(hand_pos)
            self.banshee_power_sword_extra_attack += 1
        elif self.reactions_needing_resolving[0] == "Commander Shadowsun hand":
            if self.location_hand_attachment_shadowsun == -1:
                hand_pos = int(game_update_string[2])
                card = FindCard.find_card(primary_player.cards[hand_pos], self.card_array,
                                          self.cards_dict, self.apoka_errata_cards, self.cards_that_have_errata)
                if (card.get_card_type() == "Attachment" and card.get_faction() == "Tau" and
                        card.get_cost() < 3) or card.get_name() == "Shadowsun's Stealth Cadre":
                    self.location_hand_attachment_shadowsun = hand_pos
                    primary_player.aiming_reticle_coords_hand = hand_pos
                    primary_player.aiming_reticle_color = "blue"
        elif self.reactions_needing_resolving[0] == "Elysian Assault Team":
            hand_pos = int(game_update_string[2])
            if primary_player.cards[hand_pos] == "Elysian Assault Team":
                planet_pos = self.positions_of_unit_triggering_reaction[0][1]
                card = FindCard.find_card("Elysian Assault Team", self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                primary_player.add_card_to_planet(card, planet_pos)
                del primary_player.cards[hand_pos]
                more = False
                for i in range(len(primary_player.cards)):
                    if primary_player.cards[i] == "Elysian Assault Team":
                        more = True
                if not more:
                    self.delete_reaction()
        elif current_reaction == "Adaptative Thorax Swarm":
            if hand_pos not in self.misc_player_storage:
                primary_player.aiming_reticle_coords_hand_2 = hand_pos
                self.misc_player_storage.append(hand_pos)
                if len(self.misc_player_storage) > 2:
                    names_list = []
                    i = 0
                    while i < len(self.misc_player_storage):
                        names_list.append(primary_player.cards[self.misc_player_storage[i]])
                        primary_player.remove_card_from_hand(self.misc_player_storage[i])
                        primary_player.deck.append(names_list[i])
                        j = i + 1
                        while j < len(self.misc_player_storage):
                            if self.misc_player_storage[j] > self.misc_player_storage[i]:
                                self.misc_player_storage[j] = self.misc_player_storage[j] - 1
                            j = j + 1
                        i = i + 1
                    cards_removed = ", ".join(names_list)
                    await self.send_update_message("Cards put on bottom of deck: " + cards_removed)
                    for _ in range(len(self.misc_player_storage)):
                        primary_player.draw_card()
                    primary_player.aiming_reticle_coords_hand = None
                    primary_player.aiming_reticle_coords_hand_2 = None
                    if primary_player.search_hand_for_card("Adaptative Thorax Swarm"):
                        self.create_reaction("Adaptative Thorax Swarm", primary_player.name_player,
                                             (int(primary_player.number), -1, -1))
                    self.delete_reaction()
        elif current_reaction == "Magus Harid":
            if not self.chosen_first_card:
                self.misc_player_storage = hand_pos
                self.chosen_first_card = True
                primary_player.aiming_reticle_coords_hand = hand_pos
                primary_player.aiming_reticle_color = "blue"
        elif current_reaction == "Seething Mycetic Spore":
            card = primary_player.get_card_in_hand(hand_pos)
            if card.get_card_type() == "Army" and card.get_cost() < 2 and card.get_name() != self.misc_player_storage:
                primary_player.add_card_to_planet(card, self.misc_target_planet)
                primary_player.remove_card_from_hand(hand_pos)
                self.misc_counter += 1
                self.misc_player_storage = card.get_name()
                if self.misc_counter > 1:
                    self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Inquisitor Caius Wroth":
            primary_player.discard_card_from_hand(int(game_update_string[2]))
        elif current_reaction == "Jaricho Commit":
            await self.send_update_message(primary_player.name_player + " reveals a " +
                                           primary_player.cards[hand_pos] + " from their hand.")
            self.delete_reaction()
        elif current_reaction == "Vamii Industrial Complex":
            if not self.chosen_first_card:
                card = primary_player.get_card_in_hand(hand_pos)
                if card.get_is_unit():
                    self.card_pos_to_deploy = hand_pos
                    self.card_to_deploy = card
                    print("card name: ", self.card_to_deploy.get_name())
                    self.card_type_of_selected_card_in_hand = card.get_card_type()
                    primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                    primary_player.aiming_reticle_color = "blue"
                    self.chosen_first_card = True
        elif current_reaction == "Shard of the Deceiver":
            primary_player.discard_card_from_hand(int(game_update_string[2]))
            if not primary_player.cards:
                num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                primary_player.add_card_in_play_to_discard(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Salvaged Battlewagon":
            if not self.chosen_first_card:
                card = primary_player.get_card_in_hand(int(game_update_string[2]))
                if card.get_faction() == "Orks" and card.get_cost() < 4 and card.get_card_type() == "Army":
                    primary_player.aiming_reticle_coords_hand = int(game_update_string[2])
                    primary_player.aiming_reticle_color = "blue"
                    self.chosen_first_card = True
        elif self.reactions_needing_resolving[0] == "Blood Claw Pack":
            card = primary_player.get_card_in_hand(int(game_update_string[2]))
            if card.check_for_a_trait("Space Wolves", primary_player.etekh_trait):
                if card.get_is_unit():
                    num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                    primary_player.add_card_to_planet(card, planet_pos)
                    primary_player.remove_card_from_hand(int(game_update_string[2]))
                    self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                    self.delete_reaction()
