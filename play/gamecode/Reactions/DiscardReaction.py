from .. import FindCard
from ..Phases import DeployPhase


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
        elif current_reaction == "Saint Erika":
            if chosen_discard == int(primary_player.number):
                card = primary_player.get_card_in_discard(pos_discard)
                if card.get_name() in primary_player.stored_cards_recently_discarded:
                    if card.get_faction() == "Astra Militarum" and card.get_card_type() == "Army":
                        if not card.check_for_a_trait("Elysia") and not card.check_for_a_trait("Saint"):
                            primary_player.cards.append(card.get_name())
                            del primary_player.discard[pos_discard]
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
                        (card.check_for_a_trait("Warrior", primary_player.etekh_trait) or
                         card.check_for_a_trait("Soldier", primary_player.etekh_trait)):
                    if card.get_cost() < self.ghost_ark_of_orikan:
                        num, planet, unit = self.positions_of_unit_triggering_reaction[0]
                        if primary_player.add_card_to_planet(card, planet) != -1:
                            position_of_unit = len(primary_player.cards_in_play[planet + 1]) - 1
                            primary_player.cards_in_play[planet + 1][position_of_unit]. \
                                valid_target_dynastic_weaponry = True
                            if "Dynastic Weaponry" in primary_player.discard:
                                if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                                    self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                                         (int(primary_player.get_number()), planet, position_of_unit))
                            if primary_player.search_hand_for_card("Optimized Protocol"):
                                self.create_reaction("Optimized Protocol", primary_player.name_player,
                                                     (int(primary_player.get_number()), planet, position_of_unit))
                            primary_player.remove_card_from_discard(pos_discard)
                        self.delete_reaction()
        elif current_reaction == "Endless Legions":
            if not self.chosen_first_card:
                if chosen_discard == int(primary_player.number):
                    card = primary_player.get_card_in_discard(pos_discard)
                    if card.get_is_unit():
                        self.misc_counter += 1
                        primary_player.deck.append(card.get_name())
                        primary_player.remove_card_from_discard(pos_discard)
                        if self.misc_counter > 1:
                            self.chosen_first_card = True
                            self.resolving_search_box = True
                            self.what_to_do_with_searched_card = "STORE"
                            self.traits_of_searched_card = None
                            self.card_type_of_searched_card = "Army"
                            self.faction_of_searched_card = "Necrons"
                            self.max_cost_of_searched_card = 3
                            self.all_conditions_searched_card_required = True
                            self.no_restrictions_on_chosen_card = False
                            primary_player.number_cards_to_search = 6
                            if len(primary_player.deck) > 5:
                                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                            else:
                                self.cards_in_search_box = primary_player.deck[:len(primary_player.deck)]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = primary_player.number
        elif current_reaction == "Impulsive Loota Reserve" or current_reaction == "Impulsive Loota In Play":
            if chosen_discard == int(primary_player.number):
                if self.chosen_first_card:
                    card = primary_player.get_card_in_discard(pos_discard)
                    if card.get_card_type() == "Attachment" and \
                            (card.get_name() in primary_player.stored_cards_recently_discarded or
                             card.get_name() in primary_player.cards_recently_discarded):
                        if not card.planet_attachment:
                            planet_pos, unit_pos = self.misc_target_unit
                            self.card_to_deploy = card
                            new_game_update_string = ["IN_PLAY", primary_player.number, str(planet_pos), str(unit_pos)]
                            await DeployPhase.deploy_card_routine_attachment(self, name, new_game_update_string)
        elif current_reaction == "Scavenging Kroot Rider":
            if self.chosen_first_card:
                if chosen_discard == int(primary_player.number):
                    card = primary_player.get_card_in_discard(pos_discard)
                    if card.get_card_type() == "Attachment":
                        if not card.planet_attachment:
                            _, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                            if primary_player.attach_card(card, planet_pos, unit_pos):
                                primary_player.remove_card_from_discard(pos_discard)
                                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                                self.delete_reaction()
        elif current_reaction == "The Dance Without End":
            if not self.chosen_first_card:
                if chosen_discard == int(primary_player.number):
                    card = primary_player.get_card_in_discard(pos_discard)
                    if card.get_card_type() == "Army" and card.check_for_a_trait("Harlequin") and \
                            (card.get_name() in primary_player.stored_cards_recently_discarded or
                             card.get_name() in primary_player.cards_recently_discarded):
                        primary_player.cards.append(card.get_name())
                        primary_player.remove_card_from_discard(pos_discard)
                        self.misc_target_choice = card.get_name()
                        await self.send_update_message("Choose card to deploy. Must have a different name.")
                        self.chosen_first_card = True
        elif current_reaction == "Optimized Protocol":
            if chosen_discard == int(primary_player.number):
                card = primary_player.get_card_in_discard(pos_discard)
                if card.get_faction() == "Necrons" and card.get_cost() < 4 and card.get_is_unit():
                    num, planet, unit = self.positions_of_unit_triggering_reaction[0]
                    if primary_player.add_card_to_planet(card, planet) != -1:
                        position_of_unit = len(primary_player.cards_in_play[planet + 1]) - 1
                        primary_player.cards_in_play[planet + 1][position_of_unit]. \
                            valid_target_dynastic_weaponry = True
                        if "Dynastic Weaponry" in primary_player.discard:
                            if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                                self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                                     (int(primary_player.get_number()), planet, position_of_unit))
                        if primary_player.search_hand_for_card("Optimized Protocol"):
                            self.create_reaction("Optimized Protocol", primary_player.name_player,
                                                 (int(primary_player.get_number()), planet, position_of_unit))
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
                if card.get_is_unit() and card.check_for_a_trait("Brood", primary_player.etekh_trait):
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
