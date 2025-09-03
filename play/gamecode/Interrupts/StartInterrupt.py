from .. import FindCard
from ..Phases import DeployPhase
from .. import CardClasses
import copy


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
        elif current_interrupt == "3rd Company Tactical Squad":
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = "Support"
            self.faction_of_searched_card = None
            self.max_cost_of_searched_card = 999
            self.all_conditions_searched_card_required = True
            self.no_restrictions_on_chosen_card = False
            primary_player.number_cards_to_search = 6
            if len(primary_player.deck) > 5:
                self.cards_in_search_box = primary_player.deck[0:primary_player.number_cards_to_search]
            else:
                self.cards_in_search_box = primary_player.deck[0:len(primary_player.deck)]
            self.name_player_who_is_searching = primary_player.name_player
            self.number_who_is_searching = primary_player.number
            self.delete_interrupt()
        elif self.interrupts_waiting_on_resolution[0] == "M35 Galaxy Lasgun":
            if "M35 Galaxy Lasgun" in primary_player.discard:
                primary_player.discard.remove("M35 Galaxy Lasgun")
                primary_player.cards.append("M35 Galaxy Lasgun")
            if "M35 Galaxy Lasgun" in primary_player.cards_recently_discarded:
                primary_player.cards_recently_discarded.remove("M35 Galaxy Lasgun")
            self.delete_interrupt()
        elif current_interrupt == "Escort Drone":
            card = copy.deepcopy(self.preloaded_find_card("Escort Drone"))
            card.name_owner = primary_player.name_player
            if planet_pos == -2:
                primary_player.headquarters.append(card)
            else:
                primary_player.cards_in_play[planet_pos + 1].append(card)
            if "Escort Drone" in primary_player.discard:
                primary_player.discard.remove("Escort Drone")
            self.delete_interrupt()
        elif current_interrupt == "Truck Wreck Launcha":
            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
            else:
                primary_player.ready_given_pos(planet_pos, unit_pos)
                self.delete_interrupt()
        elif current_interrupt == "Frontline Counsellor":
            destination = int(self.extra_interrupt_info[0])
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            primary_player.move_unit_to_planet(planet_pos, unit_pos, destination)
            self.delete_interrupt()
        elif current_interrupt == "The Sun Prince":
            self.player_resolving_interrupts[0] = secondary_player.name_player
        elif self.interrupts_waiting_on_resolution[0] == "Berzerker Warriors":
            if "Berzerker Warriors" not in primary_player.cards:
                self.delete_interrupt()
            else:
                primary_player.aiming_reticle_coords_hand = primary_player.cards.index("Berzerker Warriors")
                primary_player.aiming_reticle_color = "blue"
        elif current_interrupt == "Mucolid Spores":
            self.misc_counter = 0
        elif current_interrupt == "Fairly 'Quipped Kommando":
            attachment_name = self.extra_interrupt_info[0]
            if attachment_name in primary_player.discard:
                primary_player.cards.append(attachment_name)
                primary_player.discard.remove(attachment_name)
            self.delete_interrupt()
        elif current_interrupt == "Blood of Martyrs":
            self.misc_counter = 3
            self.misc_misc = []
            primary_player.exhaust_card_in_hq_given_name("Blood of Martyrs")
            self.chosen_first_card = False
            self.misc_target_planet = -1
            self.misc_target_unit = (-1, -1)
            await self.send_update_message("Select which unit to move faith from.")
        elif current_interrupt == "The Shadow Suit":
            self.chosen_first_card = False
        elif current_interrupt == "First Line Rhinos":
            extra_info = self.extra_interrupt_info[0]
            if extra_info is not None:
                card = self.preloaded_find_card(extra_info)
                primary_player.add_card_to_planet(card, planet_pos, already_exhausted=True)
                if extra_info in primary_player.discard:
                    primary_player.discard.remove(extra_info)
            self.delete_interrupt()
        elif current_interrupt == "Saint Celestine: Rebirth":
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 5, by_enemy_unit=False)
            primary_player.set_once_per_game_used_given_pos(planet_pos, unit_pos, True)
            self.delete_interrupt()
        elif current_interrupt == "Embarked Squads":
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_interrupt()
        elif current_interrupt == "Seal of the Ebon Chalice":
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, self.ebon_chalice_value,
                                                  by_enemy_unit=False)
            self.delete_interrupt()
        elif current_interrupt == "Dodging Land Speeder":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
        elif current_interrupt == "Mephiston":
            self.choices_available = ["Draw Card", "Gain Resource"]
            self.choice_context = "Mephiston Gains"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_interrupt == "Grand Master Belial":
            planet_belial = -1
            pos_belial = -1
            for i in range(7):
                for j in range(len(primary_player.cards_in_reserve[i])):
                    if primary_player.cards_in_reserve[i][j].get_ability() == "Grand Master Belial":
                        planet_belial = i
                        pos_belial = j
            if planet_belial != -1:
                cost = primary_player.get_deepstrike_value_given_pos(planet_belial, pos_belial)
                if primary_player.spend_resources(cost + 1):  # Grand Master Belial requires 1 more resource than normal
                    del primary_player.cards_in_reserve[planet_belial][pos_belial]
                    card = CardClasses.WarlordCard("Grand Master Belial", "", "", "Space Marines", 2, 6, 2, 6,
                                                   "", 7, 7, [])
                    primary_player.cards_in_play[planet_belial + 1].append(card)
                    primary_player.belial_deepstrike(planet_belial)
            else:
                primary_player.warlord_just_got_destroyed = True
            self.delete_interrupt()
        elif current_interrupt == "Catachan Devils Patrol":
            if "Catachan Devils Patrol" not in primary_player.cards:
                self.delete_interrupt()
            else:
                for i in range(len(primary_player.cards)):
                    if primary_player.cards[i] == "Catachan Devils Patrol":
                        primary_player.aiming_reticle_coords_hand = i
                card = self.preloaded_find_card("Catachan Devils Patrol")
                self.card_to_deploy = card
                self.card_pos_to_deploy = primary_player.aiming_reticle_coords_hand
                self.planet_pos_to_deploy = planet_pos
                self.traits_of_card_to_play = card.get_traits()
                self.faction_of_card_to_play = card.get_faction()
                self.name_of_card_to_play = card.get_name()
                print("Trying to discount: ", card.get_name())
                self.discounts_applied = 0
                hand_dis = primary_player.search_hand_for_discounts(card.get_faction())
                hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits())
                in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction())
                same_planet_dis, same_planet_auto_dis = \
                    primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
                self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis
                if self.available_discounts > self.discounts_applied:
                    self.stored_mode = self.mode
                    self.mode = "DISCOUNT"
                    self.planet_aiming_reticle_position = int(game_update_string[1])
                    self.planet_aiming_reticle_active = True
                else:
                    await DeployPhase.deploy_card_routine(self, name, self.planet_pos_to_deploy,
                                                          discounts=self.discounts_applied)
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
                if primary_player.add_card_to_planet(card, planet_pos + 1) != -1:
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
