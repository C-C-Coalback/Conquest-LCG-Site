from .. import FindCard
from ..Phases import DeployPhase


async def start_resolving_interrupt(self, name, game_update_string):
    if self.player_resolving_interrupts[0] == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
    current_interrupt = self.interrupts_waiting_on_resolution[0]
    if not self.resolving_search_box:
        if self.interrupts_waiting_on_resolution[0] == "Interrogator Acolyte":
            primary_player.draw_card()
            primary_player.draw_card()
            self.delete_interrupt()
        elif self.interrupts_waiting_on_resolution[0] == "M35 Galaxy Lasgun":
            if "M35 Galaxy Lasgun" in primary_player.discard:
                primary_player.discard.remove("M35 Galaxy Lasgun")
                primary_player.cards.append("M35 Galaxy Lasgun")
            if "M35 Galaxy Lasgun" in primary_player.cards_recently_discarded:
                primary_player.cards_recently_discarded.remove("M35 Galaxy Lasgun")
            self.delete_interrupt()
        elif self.interrupts_waiting_on_resolution[0] == "Berzerker Warriors":
            if "Berzerker Warriors" not in primary_player.cards:
                self.delete_interrupt()
            else:
                primary_player.aiming_reticle_coords_hand = primary_player.cards.index("Berzerker Warriors")
                primary_player.aiming_reticle_color = "blue"
        elif current_interrupt == "Mucolid Spores":
            self.misc_counter = 0
        elif current_interrupt == "Ulthwe Spirit Stone":
            num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
            primary_player.return_card_to_hand(planet_pos, unit_pos)
            self.reset_choices_available()
            self.delete_interrupt()
        elif current_interrupt == "Savage Parasite":
            if "Savage Parasite" not in primary_player.discard:
                self.delete_interrupt()
                await self.send_update_message("No Savage Parasite present in discard")
        elif current_interrupt == "Prey on the Weak":
            primary_player.exhaust_card_in_hq_given_name("Prey on the Weak")
        elif current_interrupt == "Death Serves the Emperor":
            if self.apoka:
                primary_player.add_resources(2)
                primary_player.discard_card_name_from_hand("Death Serves the Emperor")
            else:
                primary_player.add_resources(primary_player.highest_death_serves_value)
                primary_player.discard_card_name_from_hand("Death Serves the Emperor")
            self.delete_interrupt()
        elif current_interrupt == "Transcendent Blessing":
            self.chosen_first_card = False
            await self.send_update_message("Please pay 1 faith.")
        elif current_interrupt == "Surrogate Host":
            can_continue = True
            if secondary_player.nullify_check() and self.nullify_enabled:
                can_continue = False
                await self.send_update_message(
                    primary_player.name_player + " wants to play " + current_interrupt + "; "
                                                 "Nullify window offered.")
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Use Nullify?"
                self.nullified_card_pos = -1
                self.nullified_card_name = current_interrupt
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Interrupt Event"
            if can_continue:
                primary_player.discard_card_name_from_hand("Surrogate Host")
        elif current_interrupt == "Necrodermis":
            if primary_player.resources > 0:
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play " + current_interrupt + "; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = current_interrupt
                    self.cost_card_nullified = 1
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Interrupt Event"
                else:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Necrodermis")
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                        if primary_player.played_necrodermis:
                            await self.send_update_message(
                                "----GAME END----"
                                "Victory for " + secondary_player.name_player + "; "
                                + primary_player.name_player + " played a second Necrodermis whilst "
                                + primary_player.name_player + "already have one active."
                                                               "----GAME END----"
                            )
                        elif secondary_player.played_necrodermis:
                            await self.send_update_message(
                                "----GAME END----"
                                "Victory for " + primary_player.name_player + "; "
                                + primary_player.name_player + " played a second Necrodermis whilst "
                                + secondary_player.name_player + "already have one active."
                                                                 "----GAME END----"
                            )
                        primary_player.played_necrodermis = True
                        self.delete_interrupt()
                    else:
                        self.delete_interrupt()
            else:
                self.delete_interrupt()
        elif current_interrupt == "Flayed Ones Revenants":
            self.choices_available = ["Discard Cards", "Pay Resources"]
            self.choice_context = "Flayed Ones Revenants additional costs"
            self.name_player_making_choices = primary_player.name_player
            self.misc_counter = 0
            self.resolving_search_box = True
        elif current_interrupt == "World Engine Beam":
            primary_player.sacrifice_card_in_hq(unit_pos)
        elif current_interrupt == "Quantum Shielding":
            num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
            card = FindCard.find_card("Quantum Shielding", self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            primary_player.attach_card(card, planet_pos, unit_pos)
            if "Quantum Shielding" in primary_player.discard:
                primary_player.discard.remove("Quantum Shielding")
            self.delete_interrupt()
        elif current_interrupt == "Growing Tide":
            num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
            if planet_pos != 6 and unit_pos != -1:
                primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = False
                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
                primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
                primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
                primary_player.move_unit_to_planet(planet_pos, unit_pos, planet_pos + 1)
                await self.send_update_message("The Growing Tide grows...")
            elif planet_pos != 6:
                card = FindCard.find_card("Growing Tide", self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                primary_player.add_card_to_planet(card, planet_pos + 1)
                last_element_index = len(primary_player.cards_in_play[planet_pos + 1]) - 1
                primary_player.increase_attack_of_unit_at_pos(planet_pos + 1, last_element_index, 1, expiration="EOG")
                primary_player.increase_health_of_unit_at_pos(planet_pos + 1, last_element_index, 1, expiration="EOG")
                await self.send_update_message("The Growing Tide grows...")
            else:
                await self.send_update_message("No planet to move to!")
            self.delete_interrupt()
        elif current_interrupt == "Magus Harid":
            self.misc_player_storage = "RESOLVING MAGUS HARID"
            card_name = primary_player.magus_harid_waiting_cards[0]
            await self.send_update_message("Magus is deploying a " + card_name)
            card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            self.card_to_deploy = card
            self.misc_target_planet = planet_pos
            if card.get_card_type() == "Army":
                self.planet_pos_to_deploy = planet_pos
                self.traits_of_card_to_play = card.get_traits()
                self.faction_of_card_to_play = card.get_faction()
                self.name_of_card_to_play = card.get_name()
                self.discounts_applied = 0
                hand_dis = primary_player.search_hand_for_discounts(card.get_faction())
                hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits(),
                                                                planet_chosen=planet_pos)
                in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction())
                same_planet_dis, same_planet_auto_dis = \
                    primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
                self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis
                if self.available_discounts > self.discounts_applied:
                    self.stored_mode = self.mode
                    self.mode = "DISCOUNT"
                    self.planet_aiming_reticle_position = planet_pos
                    self.planet_aiming_reticle_active = True
                else:
                    await DeployPhase.deploy_card_routine(self, name, self.planet_pos_to_deploy,
                                                          discounts=self.discounts_applied)
            else:
                pass
        elif current_interrupt == "Icy Trygon":
            num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
            primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = False
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
            primary_player.discard_attachments_from_card(planet_pos, unit_pos)
            primary_player.cards_in_reserve[planet_pos].append(primary_player.cards_in_play[planet_pos + 1][unit_pos])
            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
            self.delete_interrupt()
        elif current_interrupt == "Gorgul Da Slaya":
            secondary_player.hit_by_gorgul = True
            self.mask_jain_zar_check_interrupts(primary_player, secondary_player)
            self.delete_interrupt()
