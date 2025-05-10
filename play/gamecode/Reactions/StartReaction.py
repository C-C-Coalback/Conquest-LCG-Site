from .. import FindCard


async def start_resolving_reaction(self, name, game_update_string):
    if self.player_who_resolves_reaction[0] == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if not self.resolving_search_box:
        if self.reactions_needing_resolving[0] == "Enginseer Augur":
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "PLAY TO HQ"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = "Support"
            self.faction_of_searched_card = "Astra Militarum"
            self.max_cost_of_searched_card = 2
            self.all_conditions_searched_card_required = True
            self.no_restrictions_on_chosen_card = False
            if self.player_who_resolves_reaction[0] == self.name_1:
                self.p1.number_cards_to_search = 6
                if len(self.p1.deck) > 5:
                    self.cards_in_search_box = self.p1.deck[0:self.p1.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p1.deck[0:len(self.p1.deck)]
                self.name_player_who_is_searching = self.p1.name_player
                self.number_who_is_searching = str(self.p1.number)
            else:
                self.p2.number_cards_to_search = 6
                if len(self.p2.deck) > 5:
                    self.cards_in_search_box = self.p2.deck[0:self.p2.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p2.deck[0:len(self.p2.deck)]
                self.name_player_who_is_searching = self.p2.name_player
                self.number_who_is_searching = str(self.p2.number)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Swordwind Farseer":
            if self.player_who_resolves_reaction[0] == self.name_1:
                self.p1.number_cards_to_search = 6
                self.name_player_who_is_searching = self.p1.name_player
                self.number_who_is_searching = "1"
                if len(self.p1.deck) > 5:
                    self.cards_in_search_box = self.p1.deck[0:self.p1.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p1.deck[0:len(self.p1.deck)]
            else:
                self.p2.number_cards_to_search = 6
                self.name_player_who_is_searching = self.p2.name_player
                self.number_who_is_searching = "2"
                if len(self.p2.deck) > 5:
                    self.cards_in_search_box = self.p2.deck[0:self.p2.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p2.deck[0:len(self.p2.deck)]
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = None
            self.faction_of_searched_card = None
            self.no_restrictions_on_chosen_card = True
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Experimental Devilfish":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.ready_unit_by_name("Experimental Devilfish", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Obedience":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.chosen_first_card = False
            self.misc_target_unit = (-1, -1)
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
        elif self.reactions_needing_resolving[0] == "Repulsor Impact Field" or \
                self.reactions_needing_resolving[0] == "Solarite Avetys":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 2)
                self.advance_damage_aiming_reticle()
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 2)
                self.advance_damage_aiming_reticle()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Volatile Pyrovore":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 3)
                self.p1.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 3)
                self.p2.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Vengeance!":
            if primary_player.resources < 1:
                await self.send_update_message("Insufficient resources")
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Holy Fusillade":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.ranged_skirmish_active = True
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Pyrrhian Warscythe":
            primary_player.discard_top_card_deck()
            primary_player.discard_top_card_deck()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
            self.chosen_first_card = False
            self.chosen_second_card = False
            self.need_to_reset_tomb_blade_squadron = True
            """
            for i in range(len(primary_player.headquarters)):
                if primary_player.headquarters[i].get_ability() == "Tomb Blade Squadron":
                    primary_player.headquarters[i].misc_ability_used = False
            for i in range(7):
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    if primary_player.cards_in_play[i + 1][j].get_ability() == "Tomb Blade Squadron":
                        primary_player.cards_in_play[i + 1][j].misc_ability_used = False
            """
            self.misc_target_unit = (-1, -1)
        elif self.reactions_needing_resolving[0] == "Deathmark Assassins":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.discard_top_card_deck():
                last_card_discard = len(primary_player.discard) - 1
                card = FindCard.find_card(primary_player.discard[last_card_discard], self.card_array)
                cost = card.get_cost()
                primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, cost, expiration="EOP")
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Patrolling Wraith":
            await secondary_player.reveal_hand()
            i = 0
            while i < len(secondary_player.cards):
                if secondary_player.cards[i] == self.name_of_attacked_unit:
                    secondary_player.discard_card_from_hand(i)
                    i = i - 1
                i = i + 1
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Ravenous Haruspex":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.add_resources(self.ravenous_haruspex_gain)
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.cards_in_play[planet_pos + 1][i].resolving_attack:
                    primary_player.set_once_per_phase_used_given_pos(planet_pos, i, True)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Parasitic Infection":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 1)
                self.advance_damage_aiming_reticle()
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 1)
                self.advance_damage_aiming_reticle()
            if planet_pos != -2:
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Royal Phylactery":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Resurrection Orb":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.discard:
                card = FindCard.find_card(primary_player.discard[-1], self.card_array)
                if card.get_card_type() == "Army" and card.get_faction() == "Necrons" and \
                        not card.check_for_a_trait("Elite"):
                    primary_player.add_card_to_planet(card, planet_pos)
                    del primary_player.discard[-1]
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Weight of the Aeons":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.discard_top_card_deck()
            primary_player.discard_top_card_deck()
            secondary_player.discard_top_card_deck()
            secondary_player.discard_top_card_deck()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Black Heart Ravager":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.rout_unit(planet_pos, unit_pos)
            elif num == 2:
                self.p2.rout_unit(planet_pos, unit_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Noxious Fleshborer":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.infested_planets[planet_pos] = True
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Straken's Command Squad":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Pincer Tail":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.cards_in_play[planet_pos + 1][unit_pos].can_retreat = False
            elif num == 2:
                self.p2.cards_in_play[planet_pos + 1][unit_pos].can_retreat = False
            await self.send_update_message("Defender can no longer retreat!")
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Synaptic Link":
            primary_player.draw_card()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Interrogator Acolyte":
            primary_player.draw_card()
            primary_player.draw_card()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Shrieking Harpy":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if (secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" and not
                        secondary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite")) or \
                        secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Token":
                    secondary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Sautekh Complex":
            self.resolving_search_box = True
            self.choices_available = ["Card", "Resource"]
            self.choice_context = "Sautekh Complex: Gain Card or Resource?"
            self.asking_if_reaction = False
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif self.reactions_needing_resolving[0] == "Goff Brawlers":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.p1.total_indirect_damage += 1
            self.p2.total_indirect_damage += 1
            self.location_of_indirect = "PLANET"
            self.planet_of_indirect = planet_pos
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Swarmling Termagants":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            unique_factions = []
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                new_faction = secondary_player.cards_in_play[planet_pos + 1][i].get_faction()
                if new_faction not in unique_factions:
                    unique_factions.append(new_faction)
            if "Neutral" in unique_factions:
                unique_factions.remove("Neutral")
            count = len(unique_factions)
            for _ in range(count):
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Toxic Venomthrope":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if not self.infested_planets[planet_pos]:
                self.infested_planets[planet_pos] = True
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                self.delete_reaction()
            else:
                await self.send_update_message("Resolve Toxic venomthrope gains")
                self.resolving_search_box = True
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                self.choices_available = ["Card", "Resource"]
                self.choice_context = "Toxic Venomthrope: Gain Card or Resource?"
                self.asking_if_reaction = False
                self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif self.reactions_needing_resolving[0] == "Doom Scythe Invader":
            self.choices_available = []
            for i in range(len(primary_player.discard)):
                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                if card.get_is_unit():
                    if card.check_for_a_trait("Vehicle"):
                        if not card.check_for_a_trait("Elite"):
                            self.choices_available.append(card.get_name())
            if self.choices_available:
                self.choice_context = "Target Doom Scythe Invader:"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            else:
                self.choices_available = []
                await self.send_update_message(
                    "No valid targets for Doom Scythe Invader!"
                )
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Great Scything Talons":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, self.great_scything_talons_value,
                                                          expiration="NEXT")
            self.delete_reaction()
            await self.send_update_message("Old One Eye attack increased by " +
                                           str(self.great_scything_talons_value))
        elif self.reactions_needing_resolving[0] == "Old One Eye":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
            if damage % 2 == 1:
                damage += 1
            damage = int(damage / 2)
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage)
            primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, True)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Scything Hormagaunts":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.infested_planets[planet_pos] = True
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Defense Battery":
            self.chosen_first_card = False
        elif self.reactions_needing_resolving[0] == "Ragnar Blackmane":
            planet_pos = self.positions_of_unit_triggering_reaction[0][1]
            if not secondary_player.check_for_warlord(planet_pos):
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "The Swarmlord":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            planet_1 = planet_pos - 1
            planet_2 = planet_pos + 1
            if 7 > planet_1 > -1:
                primary_player.summon_token_at_planet("Termagant", planet_1)
            if 7 > planet_2 > -1:
                primary_player.summon_token_at_planet("Termagant", planet_2)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Packmaster Kith":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Khymera", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Bone Sabres":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Gravid Tervigon":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            if self.infested_planets[planet_pos]:
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Xavaes Split-Tongue":
            primary_player.summon_token_at_hq("Cultist")
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Captain Cato Sicarius":
            primary_player.add_resources(1)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Termagant Sentry":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.cards_in_play[planet_pos + 1][i].get_ability() == "Termagant Sentry":
                    primary_player.ready_given_pos(planet_pos, i)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Termagant Horde":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Cadian Mortar Squad":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.cards_in_play[planet_pos + 1][i].get_ability() == "Cadian Mortar Squad":
                    primary_player.ready_given_pos(planet_pos, i)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Carnivore Pack":
            primary_player.add_resources(3)
        elif self.reactions_needing_resolving[0] == "Kith's Khymeramasters":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Khymera", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Murder of Razorwings":
            secondary_player.discard_card_at_random()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Coliseum Fighters":
            i = len(primary_player.discard) - 1
            while i > -1:
                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                if card.get_card_type() == "Event":
                    primary_player.cards.append(card.get_name())
                    del primary_player.discard[i]
                i = i - 1
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Weirdboy Maniak":
            no_units_damaged = True
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if unit_pos != i:
                    if no_units_damaged:
                        primary_player.set_aiming_reticle_in_play(planet_pos, i, "red")
                        no_units_damaged = False
                    else:
                        primary_player.set_aiming_reticle_in_play(planet_pos, i, "blue")
                    primary_player.assign_damage_to_pos(planet_pos, i, 1)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if no_units_damaged:
                    secondary_player.set_aiming_reticle_in_play(planet_pos, i, "red")
                    no_units_damaged = False
                else:
                    secondary_player.set_aiming_reticle_in_play(planet_pos, i, "blue")
                secondary_player.assign_damage_to_pos(planet_pos, i, 1)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Earth Caste Technician":
            if self.player_who_resolves_reaction[0] == self.name_1:
                self.p1.number_cards_to_search = 6
                if len(self.p1.deck) > 5:
                    self.cards_in_search_box = self.p1.deck[0:self.p1.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p1.deck[0:len(self.p1.deck)]
            else:
                self.p2.number_cards_to_search = 6
                if len(self.p2.deck) > 5:
                    self.cards_in_search_box = self.p2.deck[0:self.p2.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p2.deck[0:len(self.p2.deck)]
            self.resolving_search_box = True
            self.name_player_who_is_searching = primary_player.name_player
            self.number_who_is_searching = primary_player.number
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = "Drone"
            self.card_type_of_searched_card = "Attachment"
            self.faction_of_searched_card = None
            self.no_restrictions_on_chosen_card = False
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Shrine of Warpflame":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Shrine of Warpflame?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Canoptek Scarab Swarm":
            seen_a_canoptek = False
            allowed_cards = []
            for i in range(len(primary_player.discard)):
                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                if card.get_faction() == "Necrons" and card.get_card_type() == "Army":
                    if card.get_name() != "Canoptek Scarab Swarm":
                        allowed_cards.append(card.get_name())
                    else:
                        if not seen_a_canoptek:
                            seen_a_canoptek = True
                        else:
                            allowed_cards.append(card.get_name())
            if allowed_cards:
                self.choices_available = allowed_cards
                self.name_player_making_choices = primary_player.name_player
                self.choice_context = "Choose target for Canoptek Scarab Swarm:"
                self.resolving_search_box = True
            else:
                await self.send_update_message(
                    "No valid targets for Canoptek Scarab Swarm!"
                )
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Fall Back!":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Fall Back?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Leviathan Hive Ship":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Leviathan Hive Ship?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Holy Sepulchre":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Holy Sepulchre?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Commander Shadowsun":
            await self.send_update_message("Resolve shadowsun")
            self.resolving_search_box = True
            self.choices_available = ["Hand", "Discard"]
            self.choice_context = "Shadowsun plays attachment from hand or discard?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.misc_target_planet = self.positions_of_unit_triggering_reaction[0][1]
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Mark of Chaos":
            if self.positions_of_unit_triggering_reaction[0][0] == 1:
                secondary_player = self.p2
            else:
                secondary_player = self.p1
            loc_of_mark = self.positions_of_unit_triggering_reaction[0][1]
            secondary_player.suffer_area_effect(loc_of_mark, 1)
            self.number_of_units_left_to_suffer_damage = \
                secondary_player.get_number_of_units_at_planet(loc_of_mark)
            if self.number_of_units_left_to_suffer_damage > 0:
                secondary_player.set_aiming_reticle_in_play(loc_of_mark, 0, "red")
                for j in range(1, self.number_of_units_left_to_suffer_damage):
                    secondary_player.set_aiming_reticle_in_play(loc_of_mark, j, "blue")
            self.delete_reaction()
