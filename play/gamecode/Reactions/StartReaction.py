from .. import FindCard


async def start_resolving_reaction(self, name, game_update_string):
    if self.player_who_resolves_reaction[0] == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    current_reaction = self.reactions_needing_resolving[0]
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
        elif self.reactions_needing_resolving[0] == "Genestealer Brood":
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = "Genestealer"
            self.card_type_of_searched_card = None
            self.faction_of_searched_card = None
            self.max_cost_of_searched_card = 99
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
        elif current_reaction == "Leman Russ Conqueror":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 3, expiration="EOP")
            self.delete_reaction()
        elif current_reaction == "Neophyte Apprentice":
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "PLAY TO BATTLE"
            self.traits_of_searched_card = "Black Templars"
            self.card_type_of_searched_card = "Army"
            self.faction_of_searched_card = None
            self.max_cost_of_searched_card = 4
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
        elif current_reaction == "Ardent Auxiliaries":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            am_present = False
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.get_faction_given_pos(planet_pos, i) == "Astra Militarum":
                    am_present = True
            if am_present:
                primary_player.ready_given_pos(planet_pos, unit_pos)
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
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True)
                self.advance_damage_aiming_reticle()
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True)
                self.advance_damage_aiming_reticle()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Volatile Pyrovore":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 3, rickety_warbuggy=True)
                self.p1.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 3, rickety_warbuggy=True)
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
        elif self.reactions_needing_resolving[0] == "Space Wolves Predator":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.permitted_commit_locs_warlord[planet_pos] = False
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
            self.chosen_first_card = False
            self.chosen_second_card = False
            self.need_to_reset_tomb_blade_squadron = True
            self.misc_target_unit = (-1, -1)
        elif self.reactions_needing_resolving[0] == "Ichor Gauntlet":
            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
            card_target = primary_player.ichor_gauntlet_target
            card = FindCard.find_card(card_target, self.card_array, self.cards_dict)
            primary_player.add_resources(card.get_cost(urien_relevant=primary_player.urien_relevant), refund=True)
            if card_target in primary_player.discard:
                primary_player.discard.remove(card_target)
            primary_player.cards.append(card_target)
            last_element = len(primary_player.cards) - 1
            self.player_with_action = primary_player.name_player
            if self.phase == "DEPLOY":
                self.player_with_deploy_turn = primary_player.name_player
                self.number_with_deploy_turn = primary_player.number
            self.mode = "ACTION"
            string_to_use = ["HAND", primary_player.number, str(last_element)]
            self.delete_reaction()
            await self.update_game_event_action(name, string_to_use)
        elif self.reactions_needing_resolving[0] == "Deathmark Assassins":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.discard_top_card_deck():
                last_card_discard = len(primary_player.discard) - 1
                card = FindCard.find_card(primary_player.discard[last_card_discard], self.card_array, self.cards_dict)
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
            if num == 1:
                self.p1.remove_damage_from_pos(planet_pos, unit_pos, 1)
            else:
                self.p2.remove_damage_from_pos(planet_pos, unit_pos, 1)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Resurrection Orb":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.discard:
                card = FindCard.find_card(primary_player.discard[-1], self.card_array, self.cards_dict)
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
            self.infest_planet(planet_pos)
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
        elif self.reactions_needing_resolving[0] == "Hypex Injector":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.ready_given_pos(planet_pos, unit_pos)
            else:
                self.p2.ready_given_pos(planet_pos, unit_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Wailing Wraithfighter":
            self.player_who_resolves_reaction[0] = secondary_player.name_player
        elif self.reactions_needing_resolving[0] == "Anxious Infantry Platoon":
            self.choices_available = ["Pay resource", "Retreat unit"]
            self.choice_context = "Anxious Infantry Platoon Payment"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif self.reactions_needing_resolving[0] == "Piranha Hunter":
            primary_player.draw_card()
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Forward Barracks":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Ku'gath Plaguefather":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.get_damage_given_pos(planet_pos, unit_pos) < 1:
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "The Plaguefather's Banner":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.get_damage_given_pos(planet_pos, unit_pos) < 1:
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Aun'ui Prelate":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if i != unit_pos:
                    if primary_player.get_faction_given_pos(planet_pos, i) == "Tau":
                        primary_player.cards_in_play[planet_pos + 1][i].extra_attack_until_end_of_phase += 1
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Uber Grotesque":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 3, expiration="EOP")
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
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
        elif self.reactions_needing_resolving[0] == "Old Zogwort":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Wyrdboy Stikk":
            if primary_player.enemy_has_wyrdboy_stikk:
                secondary_player.exhaust_all_cards_of_ability("Wyrdboy Stikk")
            else:
                primary_player.exhaust_all_cards_of_ability("Wyrdboy Stikk")
        elif self.reactions_needing_resolving[0] == "Blood Claw Pack":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
            else:
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Crucible of Malediction":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.choices_available = ["Own deck", "Enemy deck"]
            self.name_player_making_choices = primary_player.name_player
            self.choice_context = "Which deck to use Crucible of Malediction:"
            self.resolving_search_box = True
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Biel-Tan Warp Spiders":
            self.choices_available = ["Own deck", "Enemy deck"]
            self.name_player_making_choices = primary_player.name_player
            self.choice_context = "Which deck to use Biel-Tan Warp Spiders:"
            self.resolving_search_box = True
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Coteaz's Henchmen":
            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.ready_given_pos(warlord_planet, warlord_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Formosan Black Ship":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.summon_token_at_planet("Guardsman", primary_player.last_planet_sacrifice)
            primary_player.summon_token_at_planet("Guardsman", primary_player.last_planet_sacrifice)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Secluded Apothecarion":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.add_resources(1)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Zogwort's Runtherders":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Zogwort's Hovel":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Warlock Destructor":
            self.resolving_search_box = True
            self.choices_available = ["Discard Card", "Lose Resource"]
            self.choice_context = "Warlock Destructor: pay fee or discard?"
            self.asking_if_reaction = False
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif self.reactions_needing_resolving[0] == "Goff Brawlers":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.p1.total_indirect_damage += 1
            self.p2.total_indirect_damage += 1
            self.location_of_indirect = "PLANET"
            self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
            self.planet_of_indirect = planet_pos
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Fenrisian Wolf":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.misc_target_planet = planet_pos
        elif self.reactions_needing_resolving[0] == "Blacksun Filter":
            primary_player.add_resources(1)
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
                self.infest_planet(planet_pos)
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                self.delete_reaction()
            else:
                self.resolving_search_box = True
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                self.choices_available = ["Card", "Resource"]
                self.choice_context = "Toxic Venomthrope: Gain Card or Resource?"
                self.asking_if_reaction = False
                self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif self.reactions_needing_resolving[0] == "Homing Beacon":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.choices_available = ["Card", "Resource"]
            self.choice_context = "Homing Beacon: Gain Card or Resource?"
            self.asking_if_reaction = False
            self.resolving_search_box = True
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif self.reactions_needing_resolving[0] == "Doom Scythe Invader":
            self.choices_available = []
            for i in range(len(primary_player.discard)):
                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict)
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
            self.infest_planet(planet_pos)
            self.delete_reaction()
        elif current_reaction == "The Bloodrunna":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.ready_given_pos(planet_pos, unit_pos)
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            self.delete_reaction()
        elif current_reaction == "Mandrake Fearmonger":
            secondary_player.discard_card_at_random()
            self.delete_reaction()
        elif current_reaction == "Outflank'em":
            if primary_player.spend_resources(1):
                primary_player.discard_card_name_from_hand("Outflank'em")
                self.player_with_combat_turn = primary_player.name_player
                self.number_with_combat_turn = primary_player.number
            self.delete_reaction()
        elif current_reaction == "Taurox APC":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            destination = self.last_planet_checked_for_battle
            primary_player.move_unit_to_planet(planet_pos, unit_pos, destination)
            self.delete_reaction()
        elif current_reaction == "Declare the Crusade":
            if primary_player.spend_resources(2):
                primary_player.discard_card_name_from_hand("Declare the Crusade")
                self.choices_available = self.planets_removed_from_game
                self.choice_context = "Which planet to add (DtC)"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            else:
                self.delete_reaction()
        elif current_reaction == "Sword Brethren Dreadnought":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.delete_reaction()
            self.need_to_resolve_battle_ability = True
            self.resolving_search_box = True
            self.battle_ability_to_resolve = self.planet_array[planet_pos]
            self.player_resolving_battle_ability = primary_player.name_player
            self.number_resolving_battle_ability = primary_player.number
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Resolve Battle Ability?"
            self.name_player_making_choices = primary_player.name_player
            self.tense_negotiations_active = True
        elif current_reaction == "Gene Implantation":
            if primary_player.spend_resources(1):
                primary_player.discard_card_name_from_hand("Gene Implantation")
                name_card = self.name_of_attacked_unit
                planet = self.last_planet_checked_for_battle
                if name_card in secondary_player.discard:
                    card = FindCard.find_card(name_card, self.card_array, self.cards_dict)
                    primary_player.add_card_to_planet(card, planet, is_owner_of_card=False)
                    last_index = len(secondary_player.discard) - 1
                    found = False
                    while last_index > -1 and not found:
                        if secondary_player.discard[last_index] == name_card:
                            del secondary_player.discard[last_index]
                            if name_card in secondary_player.cards_recently_discarded:
                                secondary_player.cards_recently_discarded.remove(name_card)
                            if name_card in secondary_player.cards_recently_destroyed:
                                secondary_player.cards_recently_destroyed.remove(name_card)
                            found = True
                        last_index -= 1
                self.delete_reaction()
        elif current_reaction == "Prototype Crisis Suit":
            if len(primary_player.deck) > 8:
                self.choices_available = primary_player.deck[:9]
                self.choice_context = "Prototype Crisis Suit choices"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
                self.misc_counter = 0
            else:
                self.delete_reaction()
        elif current_reaction == "Shadowed Thorns Bodysuit":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_attachment_name_pos(planet_pos, unit_pos, "Shadowed Thorns Bodysuit")
            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
            secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
            self.reset_combat_positions()
            self.shining_blade_active = False
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            self.need_to_move_to_hq = True
            self.attack_being_resolved = False
            self.delete_reaction()
        elif current_reaction == "Inspirational Fervor":
            if primary_player.spend_resources(1):
                self.chosen_first_card = False
                self.misc_target_planet = self.last_planet_checked_for_battle
                self.misc_target_unit = (-1, -1)
                self.misc_target_unit_2 = (-1, -1)
                primary_player.discard_card_name_from_hand("Inspirational Fervor")
            else:
                self.delete_reaction()
        elif current_reaction == "Talyesin's Spiders":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.attacker_planet)
            self.delete_reaction()
        elif current_reaction == "Hostile Acquisition":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.spend_resources(1):
                primary_player.discard_card_name_from_hand("Hostile Acquisition")
                self.take_control_of_card(primary_player, secondary_player, planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Sacaellum Infestors":
            primary_player.exhaust_card_in_hq_given_name("Sacaellum Infestors")
            self.resolving_search_box = True
            self.choice_context = "Choice Sacaellum Infestors"
            self.name_player_making_choices = primary_player.name_player
            self.choices_available = ["Cards", "Resources"]
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
                if self.planets_in_play_array[planet_1]:
                    primary_player.summon_token_at_planet("Termagant", planet_1)
            if 7 > planet_2 > -1:
                if self.planets_in_play_array[planet_2]:
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
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Soul Grinder":
            self.player_who_resolves_reaction[0] = secondary_player.name_player
        elif self.reactions_needing_resolving[0] == "Banner of the Ashen Sky":
            primary_player.exhaust_card_in_hq_given_name("Banner of the Ashen Sky")
        elif self.reactions_needing_resolving[0] == "Cry of the Wind":
            self.chosen_first_card = False
            can_continue = True
            if self.nullify_enabled:
                if secondary_player.nullify_check():
                    await self.send_update_message(primary_player.name_player + " wants to play Cry of the Wind" +
                                                   "; Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Cry of the Wind"
                    self.cost_card_nullified = 0
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                    can_continue = False
            if can_continue:
                primary_player.discard_card_name_from_hand("Cry of the Wind")
        elif self.reactions_needing_resolving[0] == "Big Shoota Battlewagon":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for _ in range(4):
                primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Primal Howl":
            can_continue = True
            if self.nullify_enabled:
                if secondary_player.nullify_check():
                    await self.send_update_message(primary_player.name_player + " wants to play Cry of the Wind" +
                                                   "; Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Primal Howl"
                    self.cost_card_nullified = 0
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                    can_continue = False
            if can_continue:
                primary_player.discard_card_name_from_hand("Primal Howl")
                for _ in range(3):
                    primary_player.draw_card()
        elif self.reactions_needing_resolving[0] == "Mighty Wraithknight":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if not primary_player.cards_in_play[planet_pos + 1][i].check_for_a_trait("Spirit"):
                    if primary_player.get_ready_given_pos(planet_pos, i):
                        primary_player.exhaust_given_pos(planet_pos, i)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if not secondary_player.cards_in_play[planet_pos + 1][i].check_for_a_trait("Spirit"):
                    if secondary_player.get_ready_given_pos(planet_pos, i):
                        secondary_player.exhaust_given_pos(planet_pos, i)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Firedrake Terminators":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True)
            self.delete_reaction()
        elif current_reaction == "The Black Sword":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Kabalite Halfborn":
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Exploratory Drone":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        elif self.reactions_needing_resolving[0] == "Turbulent Rift":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_card_in_hq_given_name("Turbulent Rift")
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
            secondary_player.suffer_area_effect(planet_pos, 1)
            self.delete_reaction()
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
                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict)
                if card.get_card_type() == "Event":
                    primary_player.cards.append(card.get_name())
                    del primary_player.discard[i]
                i = i - 1
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Weirdboy Maniak":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if unit_pos != i:
                    primary_player.assign_damage_to_pos(planet_pos, i, 1, rickety_warbuggy=True)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                secondary_player.assign_damage_to_pos(planet_pos, i, 1, rickety_warbuggy=True)
            self.delete_reaction()
        elif current_reaction == "Ravening Psychopath":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, shadow_field_possible=True)
        elif current_reaction == "Holding Cell":
            found = False
            name_card = self.name_of_attacked_unit
            for i in range(len(primary_player.headquarters)):
                if primary_player.headquarters[i].get_ability() == "Holding Cell":
                    if not primary_player.headquarters[i].get_attachments() and not found:
                        found = True
                        card = FindCard.find_card(name_card, self.card_array, self.cards_dict)
                        primary_player.headquarters[i].add_attachment(card, name_owner=secondary_player.name_player)
            if found:
                last_index = len(secondary_player.discard) - 1
                found = False
                while last_index > -1 and not found:
                    if secondary_player.discard[last_index] == name_card:
                        del secondary_player.discard[last_index]
                        if name_card in secondary_player.cards_recently_discarded:
                            secondary_player.cards_recently_discarded.remove(name_card)
                        if name_card in secondary_player.cards_recently_destroyed:
                            secondary_player.cards_recently_destroyed.remove(name_card)
                        found = True
                    last_index -= 1
            self.delete_reaction()
        elif current_reaction == "Ba'ar Zul the Hate-Bound":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, self.damage_amounts_baarzul[0])
            current_damage = primary_player.get_damage_given_pos(warlord_planet, warlord_pos)
            primary_player.set_damage_given_pos(warlord_planet, warlord_pos,
                                                current_damage + self.damage_amounts_baarzul[0])
            self.delete_reaction()
        elif current_reaction == "Archon Salaine Morn":
            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
            if not primary_player.get_once_per_phase_used_given_pos(warlord_planet, warlord_pos):
                primary_player.set_once_per_phase_used_given_pos(warlord_planet, warlord_pos, True)
                primary_player.add_resources(1)
            self.delete_reaction()
        elif current_reaction == "Dying Sun Marauder":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Wildrider Vyper":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        elif current_reaction == "Vow of Honor":
            if primary_player.spend_resources(1):
                primary_player.discard_card_name_from_hand("Vow of Honor")
            else:
                self.delete_reaction()
        elif current_reaction == "Salvaged Battlewagon":
            self.chosen_first_card = False
        elif current_reaction == "Shadowed Thorns Venom":
            for i in range(len(primary_player.headquarters)):
                if primary_player.get_card_type_given_pos(-2, i) == "Army":
                    if primary_player.check_for_trait_given_pos(-2, i, "Kabalite"):
                        primary_player.headquarters[i].shadowed_thorns_venom_valid = True
            for i in range(7):
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    if primary_player.get_card_type_given_pos(i, j) == "Army":
                        if primary_player.check_for_trait_given_pos(i, j, "Kabalite"):
                            primary_player.cards_in_play[i + 1][j].shadowed_thorns_venom_valid = True
            self.chosen_first_card = False
        elif current_reaction == "Sacaellum's Finest":
            if not primary_player.search_hand_for_card("Sacaellum's Finest"):
                self.delete_reaction()
        elif current_reaction == "Gut and Pillage":
            cost = 0
            if primary_player.urien_relevant:
                cost += 1
            if primary_player.spend_resources(cost):
                primary_player.discard_card_name_from_hand("Gut and Pillage")
                primary_player.add_resources(3)
                primary_player.gut_and_pillage_used = True
            self.delete_reaction()
        elif current_reaction == "Last Breath":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if planet_pos != -2:
                if num == 1:
                    self.p1.cards_in_play[planet_pos + 1][unit_pos].extra_attack_until_end_of_phase += -3
                else:
                    self.p2.cards_in_play[planet_pos + 1][unit_pos].extra_attack_until_end_of_phase += -3
            self.delete_reaction()
        elif current_reaction == "Striking Ravener":
            planet_pos = self.positions_of_unit_triggering_reaction[0][1]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.cards_in_play[planet_pos + 1][i].resolving_attack:
                    primary_player.ready_given_pos(planet_pos, i)
            self.delete_reaction()
        elif current_reaction == "Deathly Web Shrine":
            if not primary_player.search_card_in_hq("Deathly Web Shrine", ready_relevant=True):
                self.delete_reaction()
            else:
                primary_player.exhaust_card_in_hq_given_name("Deathly Web Shrine")
        elif current_reaction == "Prophetic Farseer":
            if len(secondary_player.deck) > 2:
                self.choices_available = secondary_player.deck[:3]
                self.name_player_making_choices = primary_player.name_player
                self.choice_context = "Prophetic Farseer Discard"
                self.resolving_search_box = True
            else:
                self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Accept Any Challenge":
            if primary_player.spend_resources(1):
                primary_player.discard_card_name_from_hand("Accept Any Challenge")
                planet_pos = self.last_planet_checked_for_battle
                count = 0
                for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                    if primary_player.check_for_trait_given_pos(planet_pos, i, "Black Templars"):
                        count += 1
                for i in range(count):
                    primary_player.draw_card()
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
        elif self.reactions_needing_resolving[0] == "Syren Zythlex":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Canoptek Scarab Swarm":
            seen_a_canoptek = False
            allowed_cards = []
            for i in range(len(primary_player.discard)):
                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict)
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
        elif self.reactions_needing_resolving[0] == "The Emperor Protects":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use The Emperor Protects?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Made Ta Fight":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Made Ta Fight?"
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            self.misc_target_planet = warlord_pla
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif self.reactions_needing_resolving[0] == "Doom Siren":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if planet_pos != 0:
                if self.planets_in_play_array[planet_pos + 1]:
                    secondary_player.suffer_area_effect(planet_pos + 1, self.value_doom_siren)
            if planet_pos != 6:
                if self.planets_in_play_array[planet_pos - 1]:
                    secondary_player.suffer_area_effect(planet_pos - 1, self.value_doom_siren)
            primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Inquisitor Caius Wroth":
            primary_player.discard_inquis_caius_wroth = True
            secondary_player.discard_inquis_caius_wroth = True
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
