from .. import FindCard
from ..Phases import CombatPhase
import copy


async def start_resolving_reaction(self, name, game_update_string):
    num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
    extra_info = self.additional_reactions_info[0]
    if self.player_who_resolves_reaction[0] == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    current_reaction = self.reactions_needing_resolving[0]
    if not self.resolving_search_box:
        if current_reaction == "Enginseer Augur":
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "PLAY TO HQ"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = "Support"
            self.faction_of_searched_card = "Astra Militarum"
            self.max_cost_of_searched_card = 2
            self.all_conditions_searched_card_required = True
            self.no_restrictions_on_chosen_card = False
            primary_player.number_cards_to_search = 6
            if len(primary_player.deck) > 5:
                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
            else:
                self.cards_in_search_box = primary_player.deck[:len(primary_player.deck)]
            self.name_player_who_is_searching = primary_player.name_player
            self.number_who_is_searching = primary_player.number
            self.delete_reaction()
        elif current_reaction == "First Line Rhinos":
            primary_player.number_cards_to_search = 6
            for i in range(len(primary_player.headquarters)):
                if primary_player.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                    if primary_player.headquarters[i].counter > 0:
                        primary_player.number_cards_to_search += 2
            self.resolving_search_box = True
            if primary_player.number_cards_to_search > len(primary_player.deck):
                primary_player.number_cards_to_search = len(primary_player.deck)
            self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
            self.choice_context = "First Line Rhinos Rally"
            self.name_player_making_choices = primary_player.name_player
        elif current_reaction == "Gladius Strike Force":
            primary_player.headquarters[unit_pos].counter += 1
            self.delete_reaction()
        elif current_reaction == "Munitorum Support":
            card = self.preloaded_find_card("M35 Galaxy Lasgun")
            primary_player.headquarters[unit_pos].add_attachment(card, name_owner=primary_player.name_player)
            card = self.preloaded_find_card("Hot-Shot Laspistol")
            primary_player.headquarters[unit_pos].add_attachment(card, name_owner=primary_player.name_player)
            card = self.preloaded_find_card("Bodyguard")
            primary_player.headquarters[unit_pos].add_attachment(card, name_owner=primary_player.name_player)
            card = self.preloaded_find_card("Seal of the Ebon Chalice")
            primary_player.headquarters[unit_pos].add_attachment(card, name_owner=primary_player.name_player)
            card = self.preloaded_find_card("Defense Battery")
            primary_player.headquarters[unit_pos].add_attachment(card, name_owner=primary_player.name_player)
            self.delete_reaction()
        elif current_reaction == "Talon Strike Force":
            primary_player.headquarters[unit_pos].counter += 1
            self.delete_reaction()
        elif current_reaction == "Medallion of Betrayal":
            if primary_player.count_copies_in_play("Cultist") < 1:
                primary_player.summon_token_at_hq("Cultist")
            self.delete_reaction()
        elif current_reaction == "Torturer's Masks":
            if not primary_player.cards:
                self.chosen_first_card = False
                await self.send_update_message("Please choose which Torturer's Masks to exhaust.")
            else:
                self.delete_reaction()
        elif current_reaction == "Dark Lance Raider":
            self.choices_available = ["1 dmg to 2", "3 dmg to 1"]
            self.choice_context = "Dark Lance Raider Damage"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Sneaky Lootin'":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Sneaky Lootin'")
                        primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                        primary_player.add_resources(3)
                    self.delete_reaction()
            self.delete_reaction()
        elif current_reaction == "WAAAGH! Arbuttz Rally":
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = "Attachment"
            self.faction_of_searched_card = None
            self.max_cost_of_searched_card = 99
            self.all_conditions_searched_card_required = True
            self.no_restrictions_on_chosen_card = False
            primary_player.number_cards_to_search = 6
            if primary_player.number_cards_to_search > len(primary_player.deck):
                primary_player.number_cards_to_search = len(primary_player.deck)
            self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
            self.name_player_who_is_searching = primary_player.name_player
            self.number_who_is_searching = primary_player.number
            self.delete_reaction()
        elif current_reaction == "Water Caste Bureaucrat":
            if primary_player.spend_resources(1):
                secondary_player.add_resources(1)
                self.resolving_search_box = True
                self.what_to_do_with_searched_card = "DRAW"
                self.shuffle_after = True
                self.traits_of_searched_card = None
                self.card_type_of_searched_card = None
                self.faction_of_searched_card = None
                self.max_cost_of_searched_card = 99
                self.all_conditions_searched_card_required = True
                self.no_restrictions_on_chosen_card = True
                primary_player.number_cards_to_search = 999
                if primary_player.number_cards_to_search > len(primary_player.deck):
                    primary_player.number_cards_to_search = len(primary_player.deck)
                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                self.name_player_who_is_searching = primary_player.name_player
                self.number_who_is_searching = primary_player.number
            self.delete_reaction()
        elif current_reaction == "WAAAGH! Zanzag":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.increase_attack_of_unit_at_pos(warlord_pla, warlord_pos, 1, expiration="EOR")
            self.delete_reaction()
        elif current_reaction == "WAAAGH! Ungskar Deepstrike":
            found_brute = False
            i = 0
            while i < len(primary_player.cards_in_reserve[planet_pos]) and not found_brute:
                if primary_player.cards_in_reserve[planet_pos][i].get_ability() == "Squiggoth Brute":
                    if primary_player.spend_resources(2):
                        primary_player.deepstrike_unit(planet_pos, i, in_play_card=False)
                        found_brute = True
                i = i + 1
            self.delete_reaction()
        elif current_reaction == "WAAAGH! Ungskar":
            last_planet = self.determine_last_planet()
            card = copy.deepcopy(self.preloaded_find_card("Squiggoth Brute"))
            card.deepstrike = 99
            primary_player.cards_in_reserve[last_planet].append(card)
            self.delete_reaction()
        elif current_reaction == "Order of the Crimson Oath":
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = "Army"
            self.faction_of_searched_card = None
            self.max_cost_of_searched_card = 99
            self.all_conditions_searched_card_required = True
            self.no_restrictions_on_chosen_card = False
            primary_player.number_cards_to_search = 6
            if primary_player.number_cards_to_search > len(primary_player.deck):
                primary_player.number_cards_to_search = len(primary_player.deck)
            self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
            self.name_player_who_is_searching = primary_player.name_player
            self.number_who_is_searching = primary_player.number
            self.misc_counter = 2
            await self.send_update_message("Place 2 faith after the rally.")
        elif current_reaction == "Genestealer Brood":
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
                    self.cards_in_search_box = self.p1.deck[:self.p1.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p1.deck[:len(self.p1.deck)]
                self.name_player_who_is_searching = self.p1.name_player
                self.number_who_is_searching = str(self.p1.number)
            else:
                self.p2.number_cards_to_search = 6
                if len(self.p2.deck) > 5:
                    self.cards_in_search_box = self.p2.deck[:self.p2.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p2.deck[:len(self.p2.deck)]
                self.name_player_who_is_searching = self.p2.name_player
                self.number_who_is_searching = str(self.p2.number)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Endless Legions":
            self.misc_counter = 0
            self.chosen_first_card = False
            primary_player.exhaust_card_in_hq_given_name("Endless Legions")
        elif current_reaction == "Charging Juggernaut":
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.round_number)
        elif current_reaction == "Eldritch Council":
            primary_player.exhaust_card_in_hq_given_name("Eldritch Council")
            self.choices_available = ["Move Nothing"]
            for i in range(self.eldritch_council_value):
                if len(primary_player.deck) > i:
                    self.choices_available.append(primary_player.deck[i])
            self.choice_context = "Eldritch Council: Choose Card"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
            await self.send_update_message("Choose a card to move onto the bottom of your deck.")
        elif current_reaction == "Sautekh Royal Crypt":
            primary_player.exhaust_card_in_hq_given_name("Sautekh Royal Crypt")
        elif current_reaction == "Castellan Crowe":
            self.misc_counter = 0
        elif current_reaction == "The Masque":
            primary_player.summon_token_at_planet("Cultist", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Junk Chucka Kommando":
            self.chosen_first_card = False
        elif current_reaction == "Brotherhood Justicar":
            if not self.apoka:
                for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                    primary_player.increase_faith_given_pos(planet_pos, i, 1)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
            else:
                self.misc_counter = 0
        elif current_reaction == "Citadel of Vamii":
            if num == 1:
                self.p1.set_blanked_given_pos(planet_pos, unit_pos, exp="EOR")
            else:
                self.p2.set_blanked_given_pos(planet_pos, unit_pos, exp="EOR")
        elif current_reaction == "Fortress of Mangeras":
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Advocator of Blood":
            self.misc_counter = 0
        elif current_reaction == "The Blade of Antwyr":
            self.misc_misc = []
            if planet_pos != 0:
                if self.planets_in_play_array[planet_pos - 1]:
                    self.misc_misc.append(planet_pos - 1)
            if planet_pos != 6:
                if self.planets_in_play_array[planet_pos + 1]:
                    self.misc_misc.append(planet_pos + 1)
            if not self.misc_misc:
                self.delete_reaction()
        elif current_reaction == "Sautekh Royal Crypt Damage":
            self.misc_misc = [False, False, False, False, False, False, False]
            self.misc_misc[planet_pos] = True
            if planet_pos > 0:
                if self.planets_in_play_array[planet_pos - 1]:
                    self.misc_misc[planet_pos - 1] = True
            if planet_pos < 6:
                if self.planets_in_play_array[planet_pos + 1]:
                    self.misc_misc[planet_pos + 1] = True
            message = "The following planets can be hit by Sautekh Royal Crypt: "
            for i in range(len(self.misc_misc)):
                if self.misc_misc[i]:
                    message += self.planet_array[chosen_planet] + ", "
            message += ". Press pass when done."
            self.misc_misc_2 = []
            await self.send_update_message(message)
        elif current_reaction == "Trapped Objective":
            i = 0
            while i < len(primary_player.attachments_at_planet[planet_pos]):
                if primary_player.attachments_at_planet[planet_pos][i].get_ability() == "Trapped Objective":
                    primary_player.add_card_to_discard("Trapped Objective")
                    del primary_player.attachments_at_planet[planet_pos][i]
                    i = i - 1
                i = i + 1
            primary_player.draw_card()
        elif current_reaction == "Supreme Strategist":
            if primary_player.cards_in_play[planet_pos + 1]:
                primary_player.set_aiming_reticle_in_play(planet_pos, 0, "red")
                self.chosen_first_card = False
                self.misc_target_unit = (planet_pos, 0)
                self.choices_available = ["Exhaust", "Rout"]
                self.choice_context = "Rout or Exhaust (SS)"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            elif secondary_player.cards_in_play[planet_pos + 1]:
                secondary_player.set_aiming_reticle_in_play(planet_pos, 0, "red")
                self.chosen_first_card = True
                self.misc_target_unit = (planet_pos, 0)
                self.choices_available = ["Exhaust", "Rout"]
                self.choice_context = "Rout or Exhaust (SS)"
                self.name_player_making_choices = secondary_player.name_player
                self.resolving_search_box = True
            else:
                await self.send_update_message("No units present")
                self.delete_reaction()
        elif current_reaction == "Rumbling Tomb Stalker":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Illuminor Szeras":
            primary_player.add_resources(1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Blood Rain Tempest":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
            self.bloodrain_tempest_active = not self.bloodrain_tempest_active
            if self.last_planet_checked_for_battle == -1:
                self.last_planet_checked_for_battle = 6
            else:
                self.last_planet_checked_for_battle = -1
            self.delete_reaction()
        elif current_reaction == "Corrupted Clawed Fiend":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.rout_unit(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Leman Russ Conqueror":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 3, expiration="EOP")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Neophyte Apprentice":
            primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
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
                    self.cards_in_search_box = self.p1.deck[:self.p1.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p1.deck[:len(self.p1.deck)]
                self.name_player_who_is_searching = self.p1.name_player
                self.number_who_is_searching = str(self.p1.number)
            else:
                self.p2.number_cards_to_search = 6
                if len(self.p2.deck) > 5:
                    self.cards_in_search_box = self.p2.deck[:self.p2.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p2.deck[:len(self.p2.deck)]
                self.name_player_who_is_searching = self.p2.name_player
                self.number_who_is_searching = str(self.p2.number)
            self.delete_reaction()
        elif current_reaction == "Swordwind Farseer":
            if self.player_who_resolves_reaction[0] == self.name_1:
                self.p1.number_cards_to_search = 6
                self.name_player_who_is_searching = self.p1.name_player
                self.number_who_is_searching = "1"
                if len(self.p1.deck) > 5:
                    self.cards_in_search_box = self.p1.deck[:self.p1.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p1.deck[:len(self.p1.deck)]
            else:
                self.p2.number_cards_to_search = 6
                self.name_player_who_is_searching = self.p2.name_player
                self.number_who_is_searching = "2"
                if len(self.p2.deck) > 5:
                    self.cards_in_search_box = self.p2.deck[:self.p2.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p2.deck[:len(self.p2.deck)]
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = None
            self.faction_of_searched_card = None
            self.no_restrictions_on_chosen_card = True
            self.all_conditions_searched_card_required = False
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Experimental Devilfish":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.ready_unit_by_name("Experimental Devilfish", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Ardent Auxiliaries":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            am_present = False
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.get_faction_given_pos(planet_pos, i) == "Astra Militarum":
                    am_present = True
            if am_present:
                primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Obedience":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.chosen_first_card = False
            self.misc_target_unit = (-1, -1)
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
        elif current_reaction == "Repulsor Impact Field" or current_reaction == "Solarite Avetys":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True)
                self.advance_damage_aiming_reticle()
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True)
                self.advance_damage_aiming_reticle()
            self.delete_reaction()
        elif current_reaction == "Volatile Pyrovore":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 3, rickety_warbuggy=True)
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 3, rickety_warbuggy=True)
            self.delete_reaction()
        elif current_reaction == "Vengeance!":
            if primary_player.resources < 1:
                await self.send_update_message("Insufficient resources")
                self.delete_reaction()
        elif current_reaction == "Holy Fusillade":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.start_ranged_skirmish(self.last_planet_checked_for_battle)
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Court of the Stormlord":
            if len(primary_player.deck) > 2:
                self.choices_available = copy.copy(primary_player.deck[:3])
                self.choice_context = "Discard card (CotS)"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            else:
                await self.send_update_message("Not enough cards in deck for Court of the Stormlord")
                self.delete_reaction()
        elif current_reaction == "Pyrrhian Warscythe":
            primary_player.discard_top_card_deck()
            primary_player.discard_top_card_deck()
            self.delete_reaction()
        elif current_reaction == "Space Wolves Predator":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.permitted_commit_locs_warlord[planet_pos] = False
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Convoking Praetorians":
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            await self.create_necrons_wheel_choice(primary_player)
            self.delete_reaction()
        elif current_reaction == "Angel Shark Bomber":
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.get_ready_given_pos(planet_pos, i):
                    if primary_player.get_card_type_given_pos(planet_pos, i) == "Army":
                        if primary_player.get_cost_given_pos(planet_pos, i) < 3:
                            primary_player.exhaust_given_pos(planet_pos, i, card_effect=True)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if secondary_player.get_ready_given_pos(planet_pos, i):
                    if secondary_player.get_card_type_given_pos(planet_pos, i) == "Army":
                        if secondary_player.get_cost_given_pos(planet_pos, i) < 3:
                            secondary_player.exhaust_given_pos(planet_pos, i, card_effect=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Restorative Tunnels":
            primary_player.exhaust_card_in_hq_given_name(current_reaction)
            damage_on_unit = primary_player.get_damage_given_pos(planet_pos, unit_pos)
            self.choices_available = []
            for i in range(min(damage_on_unit, 3)):
                self.choices_available.append(str(i + 1))
            if not self.choices_available:
                self.delete_reaction()
            else:
                self.choice_context = "RT: Amount to Remove"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
        elif current_reaction == "Tomb Blade Squadron":
            self.chosen_first_card = False
            self.chosen_second_card = False
            self.need_to_reset_tomb_blade_squadron = True
            self.misc_target_unit = (-1, -1)
        elif current_reaction == "Omega Zero Command":
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Caustic Tyrannofex":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if planet_pos != -2:
                primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = True
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Ichor Gauntlet":
            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.exhaust_given_pos(warlord_planet, warlord_pos)
            card_target = primary_player.ichor_gauntlet_target
            card = FindCard.find_card(card_target, self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            if card.get_name() == "Rakarth's Experimentations":
                self.action_chosen = "Rakarth's Experimentations"
                self.player_with_action = primary_player.name_player
                self.choices_available = ["Army", "Support", "Attachment", "Event"]
                self.choice_context = "Rakarth's Experimentations card type"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
                self.mode = "ACTION"
            elif card.get_name() == "Visions of Agony":
                self.action_chosen = "Visions of Agony"
                self.player_with_action = primary_player.name_player
                self.choices_available = secondary_player.cards
                self.choice_context = "Visions of Agony Discard:"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
                self.mode = "ACTION"
            elif card.get_name() == "Power from Pain":
                self.action_chosen = "Power from Pain"
                self.player_with_action = secondary_player.name_player
                self.mode = "ACTION"
            elif card.has_action_while_in_hand:
                self.mode = "ACTION"
                self.player_with_action = primary_player.name_player
                self.action_chosen = card.get_name()
            else:
                self.create_reaction(card.get_name(),
                                     primary_player.name_player, (int(primary_player.number), -1, -1))
            self.delete_reaction()
        elif current_reaction == "Deathmark Assassins":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.discard_top_card_deck():
                last_card_discard = len(primary_player.discard) - 1
                card = FindCard.find_card(primary_player.discard[last_card_discard], self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                cost = card.get_cost()
                primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, cost, expiration="EOP")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Forge Master Dominus":
            primary_player.set_blanked_given_pos(planet_pos, unit_pos, exp="EOG")
            primary_player.set_blanked_given_pos(planet_pos, unit_pos, exp="EOG Traits")
            self.delete_reaction()
        elif current_reaction == "Devoted Enginseer":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.misc_counter = 3
        elif current_reaction == "Dominus' Forge":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.delete_reaction()
        elif current_reaction == "Planetary Defence Force":
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Sicarian Infiltrator":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 2)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Mars Pattern Hellhound":
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
        elif current_reaction == "Raven Guard Legion":
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
            primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Fungal Infestation":
            primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Promethium Mine":
            primary_player.add_resources(1)
            primary_player.headquarters[unit_pos].decrement_counter()
            self.delete_reaction()
        elif current_reaction == "Palace of Slaanesh":
            primary_player.summon_token_at_hq("Cultist")
            self.delete_reaction()
        elif current_reaction == "Necklace of Teef":
            found_necklace = False
            for i in range(len(primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_ability() == "Necklace of Teef":
                    if not found_necklace:
                        found_necklace = True
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].counter += 1
            self.delete_reaction()
        elif current_reaction == "Blessing of Mork":
            if primary_player.get_damage_given_pos(planet_pos, unit_pos) < 1:
                await self.send_update_message("No damage to move!")
                self.delete_reaction()
        elif current_reaction == "Klan Totem":
            primary_player.exhaust_card_in_hq_given_name("Klan Totem")
            self.chosen_first_card = False
        elif current_reaction == "Ravenwing Dark Talons":
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
            primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Fenrisian Wolf Pack":
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Bladeguard Veteran Squad":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
        elif current_reaction == "The Phalanx":
            primary_player.headquarters[unit_pos].increment_counter()
            self.delete_reaction()
        elif current_reaction == "Iron Hands Platoon":
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
            self.delete_reaction()
        elif current_reaction == "Imperial Fists Apothecary":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            primary_player.add_resources(1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Grey Hunters":
            if int(num) == 1:
                self.p1.destroy_card_in_play(planet_pos, unit_pos)
            else:
                self.p2.destroy_card_in_play(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Righteous Reprisal":
            if planet_pos != -2:
                primary_player.spend_resources(1)
                primary_player.discard_card_name_from_hand("Righteous Reprisal")
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                ATK = primary_player.cards_in_play[planet_pos + 1][unit_pos].attack
                for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                    if secondary_player.cards_in_play[planet_pos + 1][i].resolving_attack:
                        if not secondary_player.get_immune_to_enemy_events(planet_pos, i, power=True):
                            secondary_player.assign_damage_to_pos(planet_pos, i, 2 * ATK, by_enemy_unit=False)
            self.delete_reaction()
        elif current_reaction == "Spray and Pray":
            if self.spray_and_pray_amounts:
                primary_player.assign_damage_to_pos(planet_pos, unit_pos, self.spray_and_pray_amounts[0],
                                                    by_enemy_unit=False)
                del self.spray_and_pray_amounts[0]
            self.delete_reaction()
        elif current_reaction == "Servo-Harness":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            for i in range(len(primary_player.headquarters)):
                if warlord_pla != -2 or warlord_pos != i:
                    if primary_player.check_for_trait_given_pos(-2, i, "Vehicle"):
                        faith = primary_player.get_faith_given_pos(-2, i)
                        primary_player.remove_faith_given_pos(-2, i)
                        primary_player.increase_faith_given_pos(warlord_pla, warlord_pos, faith)
            for i in range(7):
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    if warlord_pla != i or warlord_pos != j:
                        if primary_player.check_for_trait_given_pos(i, j, "Vehicle"):
                            faith = primary_player.get_faith_given_pos(i, j)
                            primary_player.remove_faith_given_pos(i, j)
                            primary_player.increase_faith_given_pos(warlord_pla, warlord_pos, faith)
            self.delete_reaction()
        elif current_reaction == "Forge Master Dominus BLD":
            primary_player.set_blanked_given_pos(planet_pos, unit_pos, exp="EOG")
            primary_player.set_blanked_given_pos(planet_pos, unit_pos, exp="EOG Traits")
            self.delete_reaction()
        elif current_reaction == "Patrolling Wraith":
            await secondary_player.reveal_hand()
            i = 0
            while i < len(secondary_player.cards):
                if secondary_player.cards[i] == extra_info:
                    secondary_player.discard_card_from_hand(i)
                    i = i - 1
                i = i + 1
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Ravenous Haruspex":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.add_resources(self.ravenous_haruspex_gain)
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.cards_in_play[planet_pos + 1][i].resolving_attack:
                    primary_player.set_once_per_phase_used_given_pos(planet_pos, i, True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Parasitic Infection":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                self.advance_damage_aiming_reticle()
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                self.advance_damage_aiming_reticle()
            if planet_pos != -2:
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Savage Parasite":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                self.advance_damage_aiming_reticle()
            elif num == 2:
                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                self.advance_damage_aiming_reticle()
            if planet_pos != -2:
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Standard of Devastation":
            await self.send_update_message("Standard of Devastation used; Space Marines army units "
                                           "have received +1 ATK.")
            for i in range(len(primary_player.headquarters)):
                if primary_player.get_card_type_given_pos(-2, i) == "Army":
                    if primary_player.get_faction_given_pos(-2, i) == "Space Marines":
                        primary_player.increase_attack_of_unit_at_pos(-2, i, 1, expiration="EOP")
            for i in range(7):
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    if primary_player.get_card_type_given_pos(i, j) == "Army":
                        if primary_player.get_faction_given_pos(i, j) == "Space Marines":
                            primary_player.increase_attack_of_unit_at_pos(i, j, 1, expiration="EOP")
            self.delete_reaction()
        elif current_reaction == "Beastmaster Harvester":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Khymera", planet_pos)
            primary_player.summon_token_at_planet("Khymera", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Hunter's Ploy":
            self.chosen_first_card = False
            can_continue = True
            if self.nullify_enabled:
                if secondary_player.nullify_check():
                    await self.send_update_message(primary_player.name_player + " wants to play " + current_reaction +
                                                   "; Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = current_reaction
                    self.cost_card_nullified = 0
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                    can_continue = False
            if can_continue:
                primary_player.discard_card_name_from_hand("Hunter's Ploy")
                amount = primary_player.get_highest_cost_units()
                primary_player.add_resources(amount)
                amount = secondary_player.get_highest_cost_units()
                secondary_player.add_resources(amount)
                if primary_player.search_hand_for_card("Hunter's Ploy"):
                    self.create_reaction("Hunter's Ploy", primary_player.name_player,
                                         (int(primary_player.number), -1, -1))
                self.delete_reaction()
        elif current_reaction == "Optimized Protocol":
            can_continue = True
            if primary_player.resources < 1:
                can_continue = False
                self.delete_reaction()
            elif self.nullify_enabled:
                if secondary_player.nullify_check():
                    await self.send_update_message(primary_player.name_player + " wants to play " + current_reaction +
                                                   "; Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = current_reaction
                    self.cost_card_nullified = 1
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                    can_continue = False
            if can_continue:
                primary_player.spend_resources(1)
                in_hand = False
                in_discard = False
                if primary_player.search_hand_for_card("Optimized Protocol"):
                    in_hand = True
                if primary_player.search_discard_for_card("Optimized Protocol") and \
                        primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    in_discard = True
                if in_hand and in_discard:
                    self.choice_context = "Optimized Protocol from discard or hand?"
                    self.choices_available = ["Discard", "Hand"]
                    self.name_player_making_choices = primary_player.name_player
                    self.resolving_search_box = True
                elif in_hand:
                    primary_player.discard_card_name_from_hand("Optimized Protocol")
                elif in_discard:
                    primary_player.remove_card_from_game("Optimized Protocol")
                    primary_player.remove_card_name_from_discard("Optimized Protocol")
        elif current_reaction == "Royal Phylactery":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
            else:
                self.p2.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
            self.delete_reaction()
        elif current_reaction == "Resurrection Orb":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.discard:
                card = FindCard.find_card(primary_player.discard[-1], self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.get_card_type() == "Army" and card.get_faction() == "Necrons" and \
                        not card.check_for_a_trait("Elite"):
                    if primary_player.add_card_to_planet(card, planet_pos) != -1:
                        position_of_unit = len(primary_player.cards_in_play[planet_pos + 1]) - 1
                        primary_player.cards_in_play[planet_pos + 1][position_of_unit]. \
                            valid_target_dynastic_weaponry = True
                        if "Dynastic Weaponry" in primary_player.discard:
                            if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                                self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                                     (int(primary_player.get_number()), planet_pos, position_of_unit))
                        if primary_player.optimized_protocol_check():
                            self.create_reaction("Optimized Protocol", primary_player.name_player,
                                                 (int(primary_player.get_number()), planet_pos, position_of_unit))
                        del primary_player.discard[-1]
            self.delete_reaction()
        elif current_reaction == "Weight of the Aeons":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.discard_top_card_deck()
            primary_player.discard_top_card_deck()
            secondary_player.discard_top_card_deck()
            secondary_player.discard_top_card_deck()
            self.delete_reaction()
        elif current_reaction == "Black Heart Ravager":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.rout_unit(planet_pos, unit_pos)
            elif num == 2:
                self.p2.rout_unit(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Noxious Fleshborer":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.infest_planet(planet_pos, primary_player)
            self.delete_reaction()
        elif current_reaction == "Straken's Command Squad":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Pincer Tail":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.cards_in_play[planet_pos + 1][unit_pos].can_retreat = False
            elif num == 2:
                self.p2.cards_in_play[planet_pos + 1][unit_pos].can_retreat = False
            await self.send_update_message("Defender can no longer retreat!")
            self.delete_reaction()
        elif current_reaction == "Synaptic Link":
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Interrogator Acolyte":
            primary_player.draw_card()
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Hypex Injector":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.ready_given_pos(planet_pos, unit_pos)
            else:
                self.p2.ready_given_pos(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Wailing Wraithfighter":
            self.player_who_resolves_reaction[0] = secondary_player.name_player
        elif current_reaction == "Anxious Infantry Platoon":
            self.choices_available = ["Pay resource", "Retreat unit"]
            self.choice_context = "Anxious Infantry Platoon Payment"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif current_reaction == "Piranha Hunter":
            primary_player.draw_card()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Forward Barracks":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Ku'gath Plaguefather":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.get_damage_given_pos(planet_pos, unit_pos) < 1:
                self.delete_reaction()
        elif current_reaction == "The Plaguefather's Banner":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.get_damage_given_pos(planet_pos, unit_pos) < 1:
                self.delete_reaction()
        elif current_reaction == "Aun'ui Prelate":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if i != unit_pos:
                    if primary_player.get_faction_given_pos(planet_pos, i) == "Tau":
                        primary_player.cards_in_play[planet_pos + 1][i].extra_attack_until_end_of_phase += 1
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Uber Grotesque":
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 3, expiration="EOP")
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Shrieking Exarch":
            if self.apoka:
                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
        elif current_reaction == "Shrieking Harpy":
            if self.apoka:
                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if (secondary_player.get_card_type_given_pos(planet_pos, i) == "Army" and not
                        secondary_player.check_for_trait_given_pos(planet_pos, i, "Elite")) or \
                        secondary_player.get_card_type_given_pos(planet_pos, i) == "Token":
                    secondary_player.exhaust_given_pos(planet_pos, i, card_effect=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Sautekh Complex":
            self.resolving_search_box = True
            self.choices_available = ["Card", "Resource"]
            self.choice_context = "Sautekh Complex: Gain Card or Resource?"
            self.asking_if_reaction = False
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif current_reaction == "Old Zogwort":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Wyrdboy Stikk":
            if primary_player.enemy_has_wyrdboy_stikk:
                secondary_player.exhaust_all_cards_of_ability("Wyrdboy Stikk")
            else:
                primary_player.exhaust_all_cards_of_ability("Wyrdboy Stikk")
        elif current_reaction == "Blood Claw Pack":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
            else:
                self.delete_reaction()
        elif current_reaction == "Crucible of Malediction":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.choices_available = ["Own deck", "Enemy deck"]
            self.name_player_making_choices = primary_player.name_player
            self.choice_context = "Which deck to use Crucible of Malediction:"
            self.resolving_search_box = True
            self.delete_reaction()
        elif current_reaction == "Biel-Tan Warp Spiders":
            self.choices_available = ["Own deck", "Enemy deck"]
            self.name_player_making_choices = primary_player.name_player
            self.choice_context = "Which deck to use Biel-Tan Warp Spiders:"
            self.resolving_search_box = True
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Coteaz's Henchmen":
            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.ready_given_pos(warlord_planet, warlord_pos)
            self.delete_reaction()
        elif current_reaction == "Formosan Black Ship":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.summon_token_at_planet("Guardsman", primary_player.last_planet_sacrifice)
            primary_player.summon_token_at_planet("Guardsman", primary_player.last_planet_sacrifice)
            self.delete_reaction()
        elif current_reaction == "Secluded Apothecarion":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.add_resources(1)
            self.delete_reaction()
        elif current_reaction == "Zogwort's Runtherders":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Zogwort's Hovel":
            primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Warlock Destructor":
            self.resolving_search_box = True
            self.choices_available = ["Discard Card", "Lose Resource"]
            self.choice_context = "Warlock Destructor: pay fee or discard?"
            self.asking_if_reaction = False
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
        elif current_reaction == "Kroot Guerrilla":
            primary_player.add_resources(1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Blitza-Bommer":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.total_indirect_damage += 3
            self.location_of_indirect = "PLANET"
            self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
            self.planet_of_indirect = planet_pos
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Epistolary Vezuel":
            primary_player.draw_card()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Fulgaris":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            await self.send_update_message("Epistolary Vezuel receives +1/+1 from Fulgaris!")
            primary_player.increase_attack_of_unit_at_pos(warlord_pla, warlord_pos, 1, expiration="EOP")
            primary_player.increase_health_of_unit_at_pos(warlord_pla, warlord_pos, 1, expiration="EOP")
            self.delete_reaction()
        elif current_reaction == "Furious Wraithblade":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Goff Brawlers":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.p1.total_indirect_damage += 1
            self.p2.total_indirect_damage += 1
            self.location_of_indirect = "PLANET"
            self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
            self.planet_of_indirect = planet_pos
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Fenrisian Wolf":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.misc_target_planet = planet_pos
        elif current_reaction == "Blacksun Filter":
            primary_player.add_resources(1)
            self.delete_reaction()
        elif current_reaction == "Swarmling Termagants":
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
        elif current_reaction == "Toxic Venomthrope":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if not self.infested_planets[planet_pos]:
                self.infest_planet(planet_pos, primary_player)
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
            else:
                self.resolving_search_box = True
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                self.choices_available = ["Card", "Resource"]
                self.choice_context = "Toxic Venomthrope: Gain Card or Resource?"
                self.asking_if_reaction = False
                self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif current_reaction == "Homing Beacon":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.choices_available = ["Card", "Resource"]
            self.choice_context = "Homing Beacon: Gain Card or Resource?"
            self.asking_if_reaction = False
            self.resolving_search_box = True
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif current_reaction == "Doom Scythe Invader":
            self.choices_available = []
            for i in range(len(primary_player.discard)):
                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.get_is_unit():
                    if card.check_for_a_trait("Vehicle", primary_player.etekh_trait):
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
        elif current_reaction == "Great Scything Talons":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, self.great_scything_talons_value,
                                                          expiration="NEXT")
            self.delete_reaction()
            await self.send_update_message("Old One Eye attack increased by " +
                                           str(self.great_scything_talons_value))
        elif current_reaction == "Old One Eye":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
            if damage % 2 == 1:
                damage += 1
            damage = int(damage / 2)
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage, healing=True)
            primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Scything Hormagaunts":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.infest_planet(planet_pos, primary_player)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "The Bloodrunna":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.ready_given_pos(planet_pos, unit_pos)
            primary_player.set_once_per_phase_used_of_att_name(planet_pos, unit_pos, "The Bloodrunna", True)
            self.delete_reaction()
        elif current_reaction == "Mandrake Fearmonger":
            interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
            if interrupts:
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Enemy Discard Effect?"
                self.resolving_search_box = True
                self.stored_discard_and_target.append((current_reaction, primary_player.number))
            else:
                secondary_player.discard_card_at_random()
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
        elif current_reaction == "Storming Librarian":
            if planet_pos != -2:
                storm_lib_value = primary_player.cards_in_play[planet_pos + 1][unit_pos].card_id
                for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                    if storm_lib_value in secondary_player.cards_in_play[planet_pos + 1][i].\
                            hit_by_which_storming_librarians:
                        secondary_player.assign_damage_to_pos(planet_pos, i, 4, context="Storming Librarian",
                                                              rickety_warbuggy=True)
                        while storm_lib_value in secondary_player.cards_in_play[planet_pos + 1][i].\
                                hit_by_which_storming_librarians:
                            secondary_player.cards_in_play[planet_pos + 1][i].hit_by_which_storming_librarians.remove(
                                storm_lib_value)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Vamii Industrial Complex":
            self.chosen_first_card = False
            primary_player.headquarters[unit_pos].counter += 2
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Sacrifice Vamii Industrial Complex?"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Mobilize the Chapter Initiation":
            self.choices_available = ["Dark Angels", "Ultramarines", "Space Wolves", "Black Templars"]
            self.choice_context = "MtC Choose Trait:"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Dark Allegiance":
            self.misc_target_choice = ""
            for i in range(len(primary_player.headquarters)):
                if primary_player.headquarters[i].get_ability() == "Dark Allegiance":
                    self.misc_target_choice = primary_player.headquarters[i].misc_string
            primary_player.number_cards_to_search = 6
            if primary_player.number_cards_to_search > len(primary_player.deck):
                primary_player.number_cards_to_search = len(primary_player.deck)
            self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
            self.choice_context = "Dark Allegiance Rally"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Myriad Excesses":
            self.chosen_first_card = False
            await self.send_update_message("Choose planet.")
        elif current_reaction == "Unstoppable Tide":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.assign_damage_to_pos(warlord_pla, warlord_pos, primary_player.unstoppable_tide_value)
            primary_player.unstoppable_tide_value = 0
            self.delete_reaction()
        elif current_reaction == "Dark Allegiance Trait":
            self.choices_available = ["Nurgle", "Khorne", "Slaanesh", "Tzeentch"]
            self.choice_context = "DA Choose Trait:"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "The Flayed Mask Surprise":
            self.choices_available = ["Five Indirect", "Sacrifice Unit", "Forgo Capture"]
            self.choice_context = "The Flayed Mask Choice:"
            self.name_player_making_choices = secondary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Children of the Stars":
            primary_player.headquarters[unit_pos].counter += 1
            if primary_player.headquarters[unit_pos].counter > 2:
                self.resolving_search_box = True
                self.what_to_do_with_searched_card = "DRAW"
                self.traits_of_searched_card = None
                self.card_type_of_searched_card = "Attachment"
                self.faction_of_searched_card = None
                self.max_cost_of_searched_card = 99
                self.all_conditions_searched_card_required = True
                self.no_restrictions_on_chosen_card = False
                primary_player.number_cards_to_search = 6
                if primary_player.number_cards_to_search > len(primary_player.deck):
                    primary_player.number_cards_to_search = len(primary_player.deck)
                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                self.name_player_who_is_searching = primary_player.name_player
                self.number_who_is_searching = primary_player.number
            self.delete_reaction()
        elif current_reaction == "Bork'an Sept":
            self.choices_available = []
            for i in range(len(primary_player.deck)):
                card_name = primary_player.deck[i]
                card = self.preloaded_find_card(card_name)
                if card.get_card_type() == "Attachment" and card.get_faction() == "Tau" and \
                        card.get_loyalty() != "Signature" and not card.check_for_a_trait("Hardpoint"):
                    if card_name not in self.choices_available:
                        self.choices_available.append(card_name)
            if self.choices_available:
                self.choice_context = "Bork'an Sept Rally"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            else:
                await self.send_update_message("No acceptable cards found!")
                self.delete_reaction()
        elif current_reaction == "Followers of Asuryan":
            primary_player.headquarters[unit_pos].counter += 1
            self.delete_reaction()
        elif current_reaction == "Dal'yth Sept":
            primary_player.headquarters[unit_pos].counter += 1
            if primary_player.headquarters[unit_pos].counter > 1:
                primary_player.dalyth_sept_active = True
            self.delete_reaction()
        elif current_reaction == "Sautekh Dynasty":
            primary_player.exhaust_card_in_hq_given_name("Sautekh Dynasty")
            non_necron_count = primary_player.count_non_necron_factions()
            primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, non_necron_count, expiration="EOR")
            self.choices_available = ["Yes", "No"]
            self.choice_context = "SD: Change Enslavement?"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Novokh Dynasty Deepstrike":
            battle_planet = self.last_planet_checked_for_battle
            novokh_id = -1
            for i in range(len(primary_player.cards_in_reserve[battle_planet])):
                if primary_player.get_deepstrike_value_given_pos(battle_planet, i):
                    novokh_id = i
            if novokh_id != -1:
                cost = primary_player.cards_in_reserve[battle_planet][novokh_id].get_cost()
                if primary_player.resources >= cost - 1:
                    primary_player.add_resources(1)
                    primary_player.spend_resources(cost)
                    primary_player.deepstrike_unit(battle_planet, novokh_id, in_play_card=False)
            self.delete_reaction()
        elif current_reaction == "Novokh Dynasty Burying":
            self.misc_misc = ["Space Marines", "Astra Militarum", "Orks", "Chaos", "Dark Eldar", "Eldar", "Tau"]
            self.choices_available = copy.deepcopy(self.misc_misc)
            self.choice_context = "ND: Faction"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
            self.misc_counter = 5
        elif current_reaction == "Maynarkh Dynasty":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.remove_damage_from_pos(warlord_pla, warlord_pos, 1, healing=True)
            self.delete_reaction()
        elif current_reaction == "Hive Fleet Kraken":
            primary_player.headquarters[unit_pos].counter += 1
            self.delete_reaction()
        elif current_reaction == "Hive Fleet Behemoth":
            primary_player.headquarters[unit_pos].counter += 1
            if primary_player.headquarters[unit_pos].counter > 1:
                for i in range(7):
                    if self.planets_in_play_array[i]:
                        primary_player.summon_token_at_planet("Termagant", i)
            self.delete_reaction()
        elif current_reaction == "Mobilize the Chapter":
            chosen_trait = primary_player.headquarters[unit_pos].misc_string
            if primary_player.check_if_all_units_have_trait(chosen_trait):
                self.choices_available = ["Gain 1 Resource", "Draw 1 Card"]
                self.choice_context = "Mobilize the Chapter Reward:"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            else:
                self.delete_reaction()
        elif current_reaction == "The Emperor's Retribution":
            if "The Emperor's Retribution" in primary_player.cards and primary_player.resources > 0:
                primary_player.spend_resources(1)
                primary_player.discard_card_name_from_hand("The Emperor's Retribution")
                self.chosen_first_card = False
                self.misc_target_unit = (-1, -1)
            else:
                self.delete_reaction()
        elif current_reaction == "Aerial Deployment":
            if "Aerial Deployment" in primary_player.cards:
                primary_player.discard_card_name_from_hand("Aerial Deployment")
                primary_player.extra_deploy_turn_active = True
                primary_player.has_passed = False
                self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Thunderwolf Cavalry":
            if not primary_player.cards_in_play[planet_pos + 1]:
                self.delete_reaction()
        elif current_reaction == "Runts to the Front":
            primary_player.spend_resources(1)
            primary_player.discard_card_name_from_hand("Runts to the Front")
        elif current_reaction == "Deathwing Interceders":
            _, current_planet, current_unit = self.last_defender_position
            i = 0
            found = False
            while i < len(primary_player.cards_in_reserve[current_planet]) and not found:
                if primary_player.cards_in_reserve[current_planet][i].get_ability() == "Deathwing Interceders":
                    dv_value = primary_player.get_deepstrike_value_given_pos(current_planet, i)
                    if primary_player.spend_resources(dv_value):
                        primary_player.reset_aiming_reticle_in_play(current_planet, current_unit)
                        last_el_index = primary_player.deepstrike_unit(current_planet, i)
                        self.may_move_defender = False
                        print("Calling defender in the funny way")
                        new_game_update_string = ["IN_PLAY", primary_player.get_number(), str(current_planet),
                                                  str(last_el_index)]
                        await CombatPhase.update_game_event_combat_section(
                            self, secondary_player.name_player, new_game_update_string)
                        found = True
                i = i + 1
            if not found:
                last_game_update_string = ["IN_PLAY", primary_player.get_number(), str(current_planet),
                                           str(current_unit)]
                await CombatPhase.update_game_event_combat_section(
                    self, secondary_player.name_player, last_game_update_string)
            self.delete_reaction()
        elif current_reaction == "Command Predator":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            self.player_with_combat_turn = primary_player.name_player
            self.number_with_combat_turn = primary_player.number
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Outflank'em":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Outflank'em")
                        self.player_with_combat_turn = primary_player.name_player
                        self.number_with_combat_turn = primary_player.number
                    self.delete_reaction()
            self.delete_reaction()
        elif current_reaction == "Taurox APC":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            destination = self.last_planet_checked_for_battle
            primary_player.move_unit_to_planet(planet_pos, unit_pos, destination)
            self.delete_reaction()
        elif current_reaction == "Declare the Crusade":
            if primary_player.resources > 1:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play Declare the Crusade; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Declare the Crusade"
                    self.cost_card_nullified = 2
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Win Battle Reaction Event"
                if can_continue:
                    if primary_player.spend_resources(2):
                        primary_player.discard_card_name_from_hand("Declare the Crusade")
                        self.choices_available = self.planets_removed_from_game
                        self.choice_context = "Which planet to add (DtC)"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                    else:
                        self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Sword Brethren Dreadnought":
            if self.planet_array[planet_pos] != "Jaricho" and \
                    (self.planet_array[planet_pos] != "Nectavus XI" or self.resolve_remaining_cs_after_reactions):
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
            else:
                self.delete_reaction()
        elif current_reaction == "Crushing Blow":
            can_continue = True
            if self.nullify_enabled:
                if secondary_player.nullify_check():
                    await self.send_update_message(primary_player.name_player + " wants to play " +
                                                   current_reaction + "; Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = current_reaction
                    self.cost_card_nullified = 1
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                    can_continue = False
            if can_continue:
                primary_player.discard_card_name_from_hand(current_reaction)
                await self.send_update_message("Select unit to damage")
        elif current_reaction == "Rallying Thunderbolt":
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if not primary_player.get_ready_given_pos(planet_pos, i):
                    if primary_player.get_card_type_given_pos(planet_pos, i) == "Army":
                        if primary_player.get_cost_given_pos(planet_pos, i) > 2:
                            primary_player.ready_given_pos(planet_pos, i)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Swordwind Wave Serpent":
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
        elif current_reaction == "Shadowseer":
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
            extra_num, extra_pla, extra_pos = extra_info
            secondary_player.set_aiming_reticle_in_play(extra_pla, extra_pos, "red")
        elif current_reaction == "The Fury of Sicarius":
            if primary_player.resources > 1:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    if primary_player.spend_resources(2):
                        primary_player.discard_card_name_from_hand(current_reaction)
                        secondary_player.destroy_card_in_play(planet_pos, unit_pos)
                        self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Unexpected Ferocity":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand(current_reaction)
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, preventable=False)
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].armorbane_next = True
                        self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Death Jesters":
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 3, expiration="NEXT")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "DX-4 Technical Drone":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if num == 1:
                self.p1.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
            else:
                self.p2.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
            self.delete_reaction()
        elif current_reaction == "Peacekeeper Drone":
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.last_planet_checked_for_battle)
            self.delete_reaction()
        elif current_reaction == "Aun'la Prince":
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
            self.delete_reaction()
        elif current_reaction == "Howling Exarch":
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
            self.misc_misc = []
        elif current_reaction == "Rapid Ingress":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand(current_reaction)
            else:
                self.delete_reaction()
        elif current_reaction == "Gene Implantation":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Gene Implantation")
                        name_card = extra_info
                        planet = self.last_planet_checked_for_battle
                        if name_card in secondary_player.discard:
                            card = FindCard.find_card(name_card, self.card_array, self.cards_dict,
                                                      self.apoka_errata_cards, self.cards_that_have_errata)
                            if primary_player.add_card_to_planet(card, planet, is_owner_of_card=False) != -1:
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
            else:
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
        elif current_reaction == "Triarch Stalkers Procession":
            secondary_player.draw_card()
            secondary_player.draw_card()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Krak Grenade":
            for i in range(len(primary_player.cards_in_play[planet_pos + 1][unit_pos].attachments)):
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].attachments[i].get_ability() == "Krak Grenade":
                    primary_player.sacrifice_attachment_from_pos(planet_pos, unit_pos, i)
                    break
            primary_player.cards_in_play[planet_pos + 1][unit_pos].attack_set_next = 5
            self.delete_reaction()
        elif current_reaction == "Gleeful Plague Beast":
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                primary_player.assign_damage_to_pos(planet_pos, i, 1, by_enemy_unit=False)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                secondary_player.assign_damage_to_pos(planet_pos, i, 1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Shadowed Thorns Bodysuit":
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
        elif current_reaction == "Dripping Scythes":
            primary_player.discard_attachment_name_from_card(planet_pos, unit_pos, "Dripping Scythes")
            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
            secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
            self.reset_combat_positions()
            self.shining_blade_active = False
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            self.need_to_move_to_hq = True
            self.attack_being_resolved = False
            self.delete_reaction()
        elif current_reaction == "Reclamation Pool":
            primary_player.exhaust_card_in_hq_given_name(current_reaction)
        elif current_reaction == "Excavated Minerals":
            primary_player.add_resources(1)
            self.delete_reaction()
        elif current_reaction == "Hybrid Metamorph":
            self.misc_target_unit = (planet_pos, unit_pos)
            self.resolving_search_box = True
            self.what_to_do_with_searched_card = "Hybrid Metamorph"
            self.traits_of_searched_card = None
            self.card_type_of_searched_card = "Attachment"
            self.faction_of_searched_card = None
            self.max_cost_of_searched_card = 99
            self.all_conditions_searched_card_required = True
            self.no_restrictions_on_chosen_card = False
            primary_player.number_cards_to_search = 6
            if len(primary_player.deck) > 5:
                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
            else:
                self.cards_in_search_box = primary_player.deck[:len(primary_player.deck)]
            self.name_player_who_is_searching = primary_player.name_player
            self.number_who_is_searching = primary_player.number
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Carnifex":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Death Guard Preachers":
            self.chosen_first_card = False
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
        elif current_reaction == "Support Fleet Transfer":
            self.choices_available = []
            for i in range(len(primary_player.headquarters[unit_pos].attachments)):
                self.choices_available.append(primary_player.headquarters[unit_pos].attachments[i].get_name())
            self.choice_context = "Support Fleet Transfer Target"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Gue'vesa Overseer":
            self.misc_target_unit = (-1, -1)
            self.chosen_first_card = False
            await self.send_update_message("Choose target for +1 ATK first.")
        elif current_reaction == "Rail Rifle":
            if primary_player.retreat_unit(planet_pos, unit_pos):
                self.misc_target_planet = planet_pos
            else:
                self.delete_reaction()
        elif current_reaction == "Pathfinder Team":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.draw_card()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Vanguard Pack":
            secondary_player.exhaust_given_pos(planet_pos, unit_pos)
            if secondary_player.resources < 1:
                self.delete_reaction()
            else:
                self.choices_available = ["Give 1 resource", "Pass"]
                self.choice_context = "Vanguard Pack Payment"
                self.name_player_making_choices = secondary_player.name_player
                self.resolving_search_box = True
        elif current_reaction == "Support Fleet":
            primary_player.number_cards_to_search = 16
            self.misc_counter = 4
            if primary_player.number_cards_to_search > len(primary_player.deck):
                primary_player.number_cards_to_search = len(primary_player.deck)
            if primary_player.number_cards_to_search < 1:
                self.delete_reaction()
            else:
                self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
                self.choice_context = "Support Fleet Rally"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
        elif current_reaction == "Farsight Vanguard":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            self.chosen_first_card = False
        elif current_reaction == "Farsight":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            primary_player.add_resources(2)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "War Cabal":
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.most_recently_revealed_planet)
            last_el_index = len(primary_player.cards_in_play[self.most_recently_revealed_planet + 1]) - 1
            if last_el_index != -1:
                primary_player.exhaust_given_pos(self.most_recently_revealed_planet, last_el_index)
            self.delete_reaction()
        elif current_reaction == "Tras the Corrupter":
            await self.send_update_message("Choose planet to replace.")
        elif current_reaction == "Quartermasters":
            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Kaptin's Hook":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.exhaust_attachment_name_pos(warlord_pla, warlord_pos, "Kaptin's Hook")
            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
            primary_player.move_unit_to_planet(planet_pos, unit_pos, warlord_pla)
            secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
            self.reset_combat_positions()
            self.shining_blade_active = False
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            self.need_to_move_to_hq = True
            self.attack_being_resolved = False
            self.delete_reaction()
        elif current_reaction == "Fake Ooman Base":
            primary_player.exhaust_card_in_hq_given_name("Fake Ooman Base")
            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
            primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
            secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
            self.reset_combat_positions()
            self.shining_blade_active = False
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            self.need_to_move_to_hq = True
            self.attack_being_resolved = False
            self.delete_reaction()
        elif current_reaction == "Pain Crafter":
            self.chosen_first_card = False
            await self.send_update_message("Choose Pain Crafter to exhaust.")
        elif current_reaction == "Champion of Khorne":
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.last_planet_checked_for_battle)
            self.delete_reaction()
        elif current_reaction == "Mindless Pain Addict":
            self.take_control_of_card(primary_player, secondary_player, planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "War Walker Squadron":
            attachments = primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()
            name_targets = []
            for i in range(len(attachments)):
                if attachments[i].get_ready() and attachments[i].check_for_a_trait("Hardpoint"):
                    name_targets.append(attachments[i].get_name())
            cancel_attack = False
            if len(name_targets) == 0:
                await self.send_update_message("Somehow did not detect an exhaustible hardpoint. "
                                               "Proceeding as though one did exist.")
                cancel_attack = True
            elif len(name_targets) == 1:
                await self.send_update_message("Only one hardpoint; automatically selecting it.")
                primary_player.exhaust_attachment_name_pos(planet_pos, unit_pos, name_targets[0])
                cancel_attack = True
            else:
                await self.send_update_message("Multiple possible hardpoints; please indicate which.")
                self.choices_available = name_targets
                self.choice_context = "War Walker Attach Exhaust"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            if cancel_attack:
                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
                self.reset_combat_positions()
                self.shining_blade_active = False
                self.number_with_combat_turn = primary_player.get_number()
                self.player_with_combat_turn = primary_player.get_name_player()
                self.need_to_move_to_hq = True
                self.attack_being_resolved = False
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
        elif current_reaction == "Sniper Drone Team":
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Tactical Withdrawal":
            self.misc_target_planet = -1
            self.chosen_first_card = False
            await self.send_update_message("Please choose the planet to move to first.")
        elif current_reaction == "Catatonic Pain":
            cost_card = 3
            if primary_player.urien_relevant:
                cost_card = 2
            if primary_player.resources > cost_card - 1:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play " + current_reaction + "; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = current_reaction
                    self.cost_card_nullified = cost_card
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                if can_continue:
                    primary_player.spend_resources(cost_card)
                    primary_player.discard_card_name_from_hand("Catatonic Pain")
            else:
                self.delete_reaction()
        elif current_reaction == "Shadow Hunt":
            if primary_player.resources > 0:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play " +
                        current_reaction + "; Nullify window offered."
                    )
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = current_reaction
                    self.cost_card_nullified = 1
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Shadow Hunt")
                        self.chosen_first_card = False
                    else:
                        self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Alaitoc Shrine":
            if not primary_player.exhaust_card_in_hq_given_name(current_reaction):
                self.delete_reaction()
        elif current_reaction == "Herald of the WAAGH!":
            self.herald_of_the_waagh_active = True
            self.begin_battle(planet_pos)
            self.set_battle_initiative()
            if not self.start_battle_deepstrike:
                self.begin_combat_round()
                self.start_ranged_skirmish(planet_pos)
            self.planet_aiming_reticle_active = True
            self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
            self.p1.has_passed = False
            self.p2.has_passed = False
            self.delete_reaction()
        elif current_reaction == "Inspirational Fervor":
            if primary_player.resources > 0:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play Inspirational Fervor; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Inspirational Fervor"
                    self.cost_card_nullified = 1
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Win Battle Reaction Event"
                if can_continue:
                    if primary_player.spend_resources(1):
                        self.chosen_first_card = False
                        self.misc_target_planet = self.last_planet_checked_for_battle
                        self.misc_target_unit = (-1, -1)
                        self.misc_target_unit_2 = (-1, -1)
                        primary_player.discard_card_name_from_hand("Inspirational Fervor")
                    else:
                        self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Talyesin's Spiders":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.attacker_planet)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Hostile Acquisition":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Hostile Acquisition")
                        self.take_control_of_card(primary_player, secondary_player, planet_pos, unit_pos)
                    self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Sacaellum Infestors":
            primary_player.exhaust_card_in_hq_given_name("Sacaellum Infestors")
            self.resolving_search_box = True
            self.choice_context = "Choice Sacaellum Infestors"
            self.name_player_making_choices = primary_player.name_player
            self.choices_available = ["Cards", "Resources"]
        elif current_reaction == "Defense Battery":
            self.chosen_first_card = False
        elif current_reaction== "Ragnar Blackmane":
            planet_pos = self.positions_of_unit_triggering_reaction[0][1]
            if not secondary_player.check_for_warlord(planet_pos, True, primary_player.name_player):
                self.delete_reaction()
        elif current_reaction == "The Swarmlord":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            planet_1 = planet_pos - 1
            planet_2 = planet_pos + 1
            if 7 > planet_1 > -1:
                if self.planets_in_play_array[planet_1]:
                    primary_player.summon_token_at_planet("Termagant", planet_1)
            if 7 > planet_2 > -1:
                if self.planets_in_play_array[planet_2]:
                    primary_player.summon_token_at_planet("Termagant", planet_2)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Packmaster Kith":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Khymera", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Bone Sabres":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Gravid Tervigon":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            if self.infested_planets[planet_pos]:
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Xavaes Split-Tongue":
            primary_player.summon_token_at_hq("Cultist")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Captain Cato Sicarius":
            primary_player.add_resources(1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Termagant Sentry":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.cards_in_play[planet_pos + 1][i].get_ability() == "Termagant Sentry":
                    primary_player.ready_given_pos(planet_pos, i)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Termagant Horde":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Cadian Mortar Squad":
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Carnivore Pack":
            primary_player.add_resources(3)
            self.delete_reaction()
        elif current_reaction == "Soul Grinder":
            self.player_who_resolves_reaction[0] = secondary_player.name_player
        elif current_reaction == "Banner of the Ashen Sky":
            primary_player.exhaust_card_in_hq_given_name("Banner of the Ashen Sky")
        elif current_reaction == "Cry of the Wind":
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
        elif current_reaction == "Big Shoota Battlewagon":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for _ in range(4):
                primary_player.summon_token_at_planet("Snotlings", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Primal Howl":
            can_continue = True
            if self.nullify_enabled:
                if secondary_player.nullify_check():
                    await self.send_update_message(primary_player.name_player + " wants to play Primal Howl" +
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
                self.primal_howl_used = True
                primary_player.discard_card_name_from_hand("Primal Howl")
                for _ in range(3):
                    primary_player.draw_card()
                self.delete_reaction()
        elif current_reaction == "Mighty Wraithknight":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if not primary_player.cards_in_play[planet_pos + 1][i].check_for_a_trait(
                        "Spirit", primary_player.etekh_trait):
                    if primary_player.get_ready_given_pos(planet_pos, i):
                        primary_player.exhaust_given_pos(planet_pos, i, card_effect=True)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if not secondary_player.cards_in_play[planet_pos + 1][i].check_for_a_trait(
                        "Spirit", primary_player.etekh_trait):
                    if secondary_player.get_ready_given_pos(planet_pos, i):
                        secondary_player.exhaust_given_pos(planet_pos, i, card_effect=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Firedrake Terminators":
            self.damage_abilities_defender_active = True
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True)
            self.delete_reaction()
        elif current_reaction == "Calibration Error":
            cost = 2
            if primary_player.urien_relevant:
                cost += 1
            can_continue = True
            if primary_player.resources >= cost:
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play Calibration Error" +
                                                       "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = "Calibration Error"
                        self.cost_card_nullified = cost
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    primary_player.spend_resources(cost)
                    primary_player.discard_card_name_from_hand("Calibration Error")
                    secondary_player.exhaust_given_pos(planet_pos, unit_pos)
                    printed_attack = secondary_player.cards_in_play[planet_pos + 1][unit_pos].attack
                    secondary_player.total_indirect_damage = printed_attack
                    secondary_player.indirect_damage_applied = 0
                    self.location_of_indirect = "PLANET"
                    self.valid_targets_for_indirect = ["Army", "Synapse", "Token"]
                    self.planet_of_indirect = planet_pos
                    self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Anvil Strike Force":
            primary_player.headquarters[unit_pos].counter += 1
            self.delete_reaction()
        elif current_reaction == "Theater of War Response":
            await self.send_update_message("You may exhaust your warlord to use a different battle ability. "
                                           "Please choose a planet if you wish to do so.")
        elif current_reaction == "Scheming Warlock":
            primary_player.number_cards_to_search = 3
            if 3 > len(primary_player.deck):
                primary_player.number_cards_to_search = len(primary_player.deck)
            self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
            self.choice_context = "Scheming Warlock Rally"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Luring Troupe":
            self.chosen_first_card = False
        elif current_reaction == "Cegorach's Jesters":
            self.player_who_resolves_reaction[0] = secondary_player.name_player
            secondary_player.cegorach_jesters_active = True
            await self.send_update_message("Making Cegorach's Jesters choices. Choose which cards to reveal. "
                                           "Press pass to confirm revealed cards.")
            self.misc_misc = []
        elif current_reaction == "Erekiel Next":
            self.misc_counter = 4
        elif current_reaction == "Neurotic Obliterator":
            self.damage_abilities_defender_active = True
        elif current_reaction == "Sweep":
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
            primary_player.cards_in_play[planet_pos + 1][unit_pos].resolving_attack = True
            self.attacker_planet = planet_pos
            self.attacker_position = unit_pos
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            self.sweep_active = True
            self.attack_being_resolved = True
            self.delete_reaction()
        elif current_reaction == "Elusive Escort":
            primary_player.draw_card()
        elif current_reaction == "Wisdom of Biel-tan":
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Rampaging Knarloc":
            self.damage_abilities_defender_active = True
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            for i in range(7):
                for j in range(len(secondary_player.cards_in_play[i + 1])):
                    if secondary_player.cards_in_play[i + 1][j].resolving_attack:
                        secondary_player.assign_damage_to_pos(i, j, 4, rickety_warbuggy=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "The Black Sword":
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, by_enemy_unit=False)
            self.delete_reaction()
        elif current_reaction == "Commissar Somiel":
            primary_player.summon_token_at_hq("Guardsman")
            self.delete_reaction()
        elif current_reaction == "Krieg Armoured Regiment":
            if "Krieg Armoured Regiment" in primary_player.discard and \
                    "Krieg Armoured Regiment" in primary_player.stored_cards_recently_discarded:
                primary_player.discard.remove("Krieg Armoured Regiment")
                primary_player.deck.append("Krieg Armoured Regiment")
                primary_player.number_cards_to_search = 6
                self.resolving_search_box = True
                try:
                    primary_player.stored_cards_recently_discarded.remove("Krieg Armoured Regiment")
                    primary_player.stored_cards_recently_destroyed.remove("Krieg Armoured Regiment")
                except ValueError:
                    pass
                if len(primary_player.deck) > 5:
                    self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
                else:
                    self.choices_available = primary_player.deck[:len(primary_player.deck)]
                self.choice_context = "Krieg Armoured Regiment result:"
                self.name_player_making_choices = primary_player.name_player
            else:
                await self.send_update_message("No Krieg Armoured Regiment found in discard!")
                self.delete_reaction()
        elif current_reaction == "Convent Prioris Advisor":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Sacrifice Convent Prioris Advisor?"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Holy Battery":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Exalted Celestians":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Sanctified Bolter":
            self.misc_counter = 0
        elif current_reaction == "Sororitas Command Squad":
            if num == 1:
                if self.p1.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                    self.p1.assign_damage_to_pos(planet_pos, unit_pos, self.sororitas_command_squad_value)
            else:
                if self.p2.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                    self.p2.assign_damage_to_pos(planet_pos, unit_pos, self.sororitas_command_squad_value)
            self.delete_reaction()
        elif current_reaction == "Eloquent Confessor":
            await self.send_update_message("Please pay 1 faith.")
        elif current_reaction == "Devoted Hospitaller":
            self.chosen_first_card = False
            self.misc_counter = 0
        elif current_reaction == "Penitent Engine":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="NEXT")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Sacred Rose Immolator":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            if planet_pos != -2:
                if not primary_player.get_once_per_round_used_given_pos(planet_pos, unit_pos):
                    primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, 1)
                else:
                    primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, 2)
                self.misc_misc = []
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
            else:
                self.delete_reaction()
        elif current_reaction == "Dominion Eugenia":
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.get_ability_given_pos(planet_pos, i) == "Dominion Eugenia":
                    primary_player.increase_faith_given_pos(planet_pos, i, 1)
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.delete_reaction()
        elif current_reaction == "Kabalite Halfborn":
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Exploratory Drone":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        elif current_reaction == "Loamy Broodhive":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.exhaust_card_in_hq_given_name("Loamy Broodhive")
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Turbulent Rift":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
            secondary_player.suffer_area_effect(planet_pos, 1)
            self.delete_reaction()
        elif current_reaction == "Squiggoth Brute":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if secondary_player.get_card_type_given_pos(planet_pos, i) == "Army":
                    secondary_player.cards_in_play[planet_pos + 1][i].lost_keywords_eop = True
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Salamander Flamer Squad":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            salamander_id = -1
            if planet_pos == -2:
                salamander_id = primary_player.headquarters[unit_pos].card_id
            else:
                salamander_id = primary_player.cards_in_play[planet_pos + 1][unit_pos].card_id
            for i in range(len(secondary_player.headquarters)):
                if salamander_id in secondary_player.headquarters[i].hit_by_which_salamanders:
                    secondary_player.assign_damage_to_pos(-2, i, 1, context="Salamander Flamer Squad")
            for i in range(7):
                for j in range(len(secondary_player.cards_in_play[i + 1])):
                    if salamander_id in secondary_player.cards_in_play[i + 1][j].hit_by_which_salamanders:
                        secondary_player.assign_damage_to_pos(
                            i, j, 1, context="Salamander Flamer Squad", rickety_warbuggy=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Kith's Khymeramasters":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Khymera", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Murder of Razorwings":
            interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
            if interrupts:
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Enemy Discard Effect?"
                self.resolving_search_box = True
                self.stored_discard_and_target.append((current_reaction, primary_player.number))
            else:
                secondary_player.discard_card_at_random()
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
        elif current_reaction == "Siege Regiment Manticore":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
        elif current_reaction == "Armour of Saint Katherine":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.delete_reaction()
        elif current_reaction == "Heralding Cherubim":
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
        elif current_reaction == "Miraculous Intervention":
            if "Miraculous Intervention" in primary_player.cards and primary_player.resources > 0:
                primary_player.spend_resources(1)
                primary_player.discard_card_name_from_hand("Miraculous Intervention")
                warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                primary_player.increase_faith_given_pos(warlord_pla, warlord_pos, 2)
                primary_player.commit_warlord_to_planet_from_planet(warlord_pla, self.last_planet_checked_for_battle)
                self.create_reaction("Miraculous Intervention: Pay 1 Resource?", primary_player.name_player,
                                     (int(primary_player.number), self.last_planet_checked_for_battle, -1))
            self.delete_reaction()
        elif current_reaction == "Miraculous Intervention: Pay 1 Resource?":
            if primary_player.spend_resources(1):
                unit_diff = secondary_player.count_units_at_planet(planet_pos)\
                            - primary_player.count_units_at_planet(planet_pos)
                if unit_diff > 0:
                    for _ in range(unit_diff):
                        primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.delete_reaction()
        elif current_reaction == "Agra's Preachings Deploy":
            card_name = primary_player.get_next_agras_preachings_name()
            if card_name:
                card = self.preloaded_find_card(card_name)
                primary_player.delete_next_agras_preachings_name()
                if primary_player.play_card(planet_pos, card, discounts=2):
                    pass
                else:
                    primary_player.add_card_to_discard(card_name)
            self.delete_reaction()
        elif current_reaction == "Agra's Preachings":
            primary_player.exhaust_card_in_hq_given_name("Agra's Preachings")
        elif current_reaction == "Wrathful Retribution":
            if primary_player.spend_resources(1):
                primary_player.discard_card_name_from_hand("Wrathful Retribution")
                self.misc_counter = primary_player.wrathful_retribution_value
                self.chosen_first_card = False
                if self.misc_counter < 1:
                    await self.send_update_message("No faith to place! Skipping to ready a unit with faith step.")
                    self.chosen_first_card = True
                else:
                    await self.send_update_message("Please place " + str(self.misc_counter) + " faith.")
            else:
                self.delete_reaction()
        elif current_reaction == "Until Justice is Done":
            card = self.preloaded_find_card("Until Justice is Done")
            if secondary_player.attach_card(card, planet_pos, unit_pos, not_own_attachment=True):
                if "Until Justice is Done" in primary_player.cards:
                    primary_player.cards.remove("Until Justice is Done")
            self.delete_reaction()
        elif current_reaction == "Tunneling Mawloc":
            self.chosen_first_card = False
            self.misc_target_planet = planet_pos
            self.misc_counter = 0
        elif current_reaction == "Tomb Blade Diversionist":
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True)
            self.delete_reaction()
        elif current_reaction == "Shedding Hive Crone":
            num_termagants = 3
            if self.infested_planets[planet_pos]:
                num_termagants = 4
            for i in range(num_termagants):
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Coliseum Fighters":
            i = len(primary_player.discard) - 1
            found_card = False
            while i > -1 and not found_card:
                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.get_card_type() == "Event":
                    primary_player.cards.append(card.get_name())
                    del primary_player.discard[i]
                    found_card = True
                i = i - 1
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Saint Erika":
            self.chosen_first_card = False
            await self.send_update_message("Please pay 1 faith.")
        elif current_reaction == "Zealous Cantus":
            times_used = primary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos)
            if not times_used:
                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, 1)
            elif times_used == 1:
                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, 2)
            else:
                self.delete_reaction()
        elif current_reaction == "Vengeful Seraphim":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
            primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
            else:
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Ready Vengeful Seraphim?"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
        elif current_reaction == "Patron Saint":
            self.misc_counter = 3
            self.chosen_first_card = False
        elif current_reaction == "Heavy Flamer Retributor":
            self.misc_counter = primary_player.get_faith_given_pos(planet_pos, unit_pos)
            if self.misc_counter < 1:
                await self.send_update_message("No faith is present on the HFR!")
                self.delete_reaction()
            else:
                self.misc_misc = []
        elif current_reaction == "Hydra Flak Tank":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
        elif current_reaction == "Celestian Amelia":
            primary_player.celestian_amelia_active = True
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "23rd Mechanised Battalion":
            if primary_player.retreat_unit(planet_pos, unit_pos):
                for i in range(4):
                    primary_player.summon_token_at_planet("Guardsman", planet_pos)
            last_el = len(primary_player.headquarters) - 1
            primary_player.assign_damage_to_pos(-2, last_el, 5, by_enemy_unit=False)
            self.delete_reaction()
        elif current_reaction == "Weirdboy Maniak":
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if unit_pos != i:
                    primary_player.assign_damage_to_pos(planet_pos, i, 1, rickety_warbuggy=True)
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                secondary_player.assign_damage_to_pos(planet_pos, i, 1, rickety_warbuggy=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Ravening Psychopath":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, shadow_field_possible=True,
                                                by_enemy_unit=False)
        elif current_reaction == "Holding Cell":
            found = False
            name_card = self.name_of_attacked_unit
            for i in range(len(primary_player.headquarters)):
                if primary_player.headquarters[i].get_ability() == "Holding Cell":
                    if not primary_player.headquarters[i].get_attachments() and not found:
                        found = True
                        card = FindCard.find_card(name_card, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
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
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Burst Forth":
            self.misc_target_planet = self.positions_of_unit_triggering_reaction[0][1]
        elif current_reaction == "The Mask of Jain Zar":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
            self.delete_reaction()
        elif current_reaction == "Blood Axe Strategist":
            self.choices_available = ["HQ", "Adjacent Planet"]
            self.choice_context = "Blood Axe Strategist Destination"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Griffon Escort":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            primary_player.summon_token_at_planet("Guardsman", planet_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Deathwing Terminators":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = True
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Archon Salaine Morn":
            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
            if not primary_player.get_once_per_phase_used_given_pos(warlord_planet, warlord_pos):
                primary_player.set_once_per_phase_used_given_pos(warlord_planet, warlord_pos, True)
                primary_player.add_resources(1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Dying Sun Marauder":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Wildrider Vyper":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        elif current_reaction == "Vow of Honor":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " + current_reaction +
                                                       "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Vow of Honor")
                    else:
                        self.delete_reaction()
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
            if primary_player.resources >= cost:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play Gut and Pillage; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Gut and Pillage"
                    self.cost_card_nullified = cost
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Win Battle Reaction Event"
                if can_continue:
                    if primary_player.spend_resources(cost):
                        primary_player.discard_card_name_from_hand("Gut and Pillage")
                        if self.apoka:
                            primary_player.add_resources(2)
                        else:
                            primary_player.add_resources(3)
                            if self.blackstone:
                                primary_player.can_play_limited = False
                        primary_player.gut_and_pillage_used = True
                        await primary_player.dark_eldar_event_played()
                    self.delete_reaction()
            else:
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
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
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
        elif current_reaction == "Accept Any Challenge":
            if primary_player.resources > 0:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play Accept Any Challenge; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Accept Any Challenge"
                    self.cost_card_nullified = 1
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Win Battle Reaction Event"
                if can_continue:
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
            else:
                self.delete_reaction()
        elif current_reaction == "Scavenging Run":
            if primary_player.resources > 0:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play Scavenging Run; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Scavenging Run"
                    self.cost_card_nullified = 1
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Win Battle Reaction Event"
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Scavenging Run")
                        self.chosen_first_card = False
                    else:
                        self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Earth Caste Technician":
            if self.player_who_resolves_reaction[0] == self.name_1:
                self.p1.number_cards_to_search = 6
                if len(self.p1.deck) > 5:
                    self.cards_in_search_box = self.p1.deck[:self.p1.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p1.deck[:len(self.p1.deck)]
            else:
                self.p2.number_cards_to_search = 6
                if len(self.p2.deck) > 5:
                    self.cards_in_search_box = self.p2.deck[:self.p2.number_cards_to_search]
                else:
                    self.cards_in_search_box = self.p2.deck[:len(self.p2.deck)]
            self.resolving_search_box = True
            self.name_player_who_is_searching = primary_player.name_player
            self.number_who_is_searching = primary_player.number
            self.what_to_do_with_searched_card = "DRAW"
            self.traits_of_searched_card = "Drone"
            self.card_type_of_searched_card = "Attachment"
            self.faction_of_searched_card = None
            self.no_restrictions_on_chosen_card = False
            self.all_conditions_searched_card_required = False
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Shrine of Warpflame":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Shrine of Warpflame?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.delete_reaction()
        elif current_reaction == "Acquisition Phalanx":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
            primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
            await self.send_update_message("Acquistion Phalanx gained +1 ATK and +1 HP")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Syren Zythlex":
            secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Contaminated Convoys":
            if primary_player.resources > 0:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play Contaminated Convoys; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Accept Any Challenge"
                    self.cost_card_nullified = 1
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                if can_continue:
                    if primary_player.spend_resources(1):
                        primary_player.discard_card_name_from_hand("Contaminated Convoys")
                        primary_player.contaminated_convoys = True
                    self.delete_reaction()
        elif current_reaction == "Unconquerable Fear":
            if primary_player.resources > 0:
                can_continue = True
                if secondary_player.nullify_check() and self.nullify_enabled:
                    can_continue = False
                    await self.send_update_message(
                        primary_player.name_player + " wants to play Unconquerable Fear; "
                                                     "Nullify window offered.")
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Use Nullify?"
                    self.nullified_card_pos = -1
                    self.nullified_card_name = "Unconquerable Fear"
                    self.cost_card_nullified = 1
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Reaction Event"
                if can_continue:
                    cost = 3
                    if primary_player.urien_relevant:
                        cost = cost - 1
                    if primary_player.spend_resources(cost):
                        primary_player.discard_card_name_from_hand("Unconquerable Fear")
                        primary_player.unconquerable_fear_used = True
                        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                        primary_player.exhaust_given_pos(warlord_pla, warlord_pos)
                        interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
                        if interrupts:
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Enemy Discard Effect?"
                            self.resolving_search_box = True
                            self.stored_discard_and_target.append((current_reaction, primary_player.number))
                        else:
                            secondary_player.discard_card_at_random()
                            secondary_player.discard_card_at_random()
                            await primary_player.dark_eldar_event_played()
                            primary_player.torture_event_played()
                            secondary_player.create_enemy_played_event_reactions()
                            self.delete_reaction()
                    else:
                        self.delete_reaction()
        elif current_reaction == "Drifting Spore Mines":
            self.misc_target_unit = (planet_pos, unit_pos)
            if planet_pos != 6 or self.planets_in_play_array[5]:
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                self.player_who_resolves_reaction[0] = secondary_player.name_player
                self.chosen_first_card = False
                await self.send_update_message(secondary_player.name_player + ", please move the unit.")
            else:
                self.delete_reaction()
                await self.send_update_message("No planet to move the unit to.")
        elif current_reaction == "Magus Harid":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            if primary_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                for i in range(len(primary_player.headquarters)):
                    if primary_player.headquarters[i].get_ability() == "Imperial Bastion":
                        primary_player.headquarters[i].once_per_round_used = True
            self.chosen_first_card = False
        elif current_reaction == "Hive Ship Tendrils":
            primary_player.headquarters[unit_pos].counter += 1
            self.choices_available = ["Sacrifice", "Don't"]
            self.choice_context = "Sacrifice Hive Ship Tendrils?"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Vale Tenndrac":
            primary_player.summon_token_at_planet("Termagant", planet_pos)
            if planet_pos != 0:
                if self.infested_planets[planet_pos - 1] and self.planets_in_play_array[planet_pos - 1]:
                    primary_player.summon_token_at_planet("Termagant", planet_pos - 1)
            if planet_pos != 6:
                if self.infested_planets[planet_pos + 1] and self.planets_in_play_array[planet_pos + 1]:
                    primary_player.summon_token_at_planet("Termagant", planet_pos + 1)
            self.delete_reaction()
        elif current_reaction == "Goliath Rockgrinder":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            for _ in range(self.goliath_rockgrinder_value):
                primary_player.summon_token_at_planet("Termagant", planet_pos)
            self.goliath_rockgrinder_value = 0
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Adaptative Thorax Swarm":
            self.misc_counter = 0
            first_index = -1
            for i in range(len(primary_player.cards)):
                if primary_player.cards[i] == "Adaptative Thorax Swarm":
                    if first_index == -1:
                        first_index = i
            if first_index == -1:
                self.delete_reaction()
                await self.send_update_message("Adaptative Thorax Swarm not found in hand")
            else:
                primary_player.aiming_reticle_coords_hand = first_index
                primary_player.aiming_reticle_color = "blue"
                self.misc_player_storage = [first_index]
        elif current_reaction == "Seething Mycetic Spore":
            self.misc_counter = 0
            self.misc_player_storage = ""
            self.misc_target_planet = planet_pos
        elif current_reaction == "Canoptek Scarab Swarm":
            seen_a_canoptek = False
            allowed_cards = []
            for i in range(len(primary_player.discard)):
                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
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
        elif current_reaction == "Murder Cogitator":
            primary_player.exhaust_card_in_hq_given_name("Murder Cogitator")
            await primary_player.reveal_top_card_deck()
            card = primary_player.get_top_card_deck()
            if card is not None:
                if card.get_is_unit() and card.get_faction() == "Chaos":
                    await self.send_update_message("Card is drawn")
                    primary_player.draw_card()
                else:
                    await self.send_update_message("Card is not drawn")
            if primary_player.search_card_in_hq("Murder Cogitator", ready_relevant=True):
                self.create_reaction("Murder Cogitator", primary_player.name_player,
                                     (int(primary_player.number), -1, -1))
            self.delete_reaction()
        elif current_reaction == "Fall Back!":
            if primary_player.resources < 1:
                self.delete_reaction()
            elif primary_player.urien_relevant and primary_player.resources < 2:
                self.delete_reaction()
            else:
                self.resolving_search_box = True
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Use Fall Back?"
                self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif current_reaction == "Third Eye of Trazyn":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            self.misc_target_planet = planet_pos
            primary_player.exhaust_attachment_name_pos(planet_pos, unit_pos, "Third Eye of Trazyn")
            self.chosen_first_card = False
        elif current_reaction == "Sweep Attack":
            self.chosen_first_card = False
            self.misc_counter = -1
            self.choices_available = ["Deck", "Discard"]
            self.choice_context = "Sweep Attack: Search which area?"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Parasite of Mortrex":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, True)
            self.chosen_first_card = False
            self.misc_counter = -1
            self.choices_available = ["Deck", "Discard"]
            self.choice_context = "Parasite of Mortrex: Search which area?"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Elysian Assault Team":
            if primary_player.search_hand_for_card("Elysian Assault Team"):
                card = self.preloaded_find_card("Elysian Assault Team")
                primary_player.add_card_to_planet(card, planet_pos)
                primary_player.remove_card_name_from_hand("Elysian Assault Team")
                if primary_player.search_hand_for_card("Elysian Assault Team"):
                    self.create_reaction("Elysian Assault Team", primary_player.name_player,
                                         (int(primary_player.number), planet_pos, -1))
            self.delete_reaction()
        elif current_reaction == "The Emperor Protects":
            if secondary_player.nullify_check() and self.nullify_enabled:
                await self.send_update_message(
                    primary_player.name_player + " wants to play The Emperor Protects; "
                                                 "Nullify window offered.")
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Use Nullify?"
                self.nullified_card_pos = -1
                self.nullified_card_name = "The Emperor Protects"
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "The Emperor Protects"
            else:
                self.choices_available = primary_player.stored_targets_the_emperor_protects
                self.choice_context = "Target The Emperor Protects:"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
        elif current_reaction == "Kroot Hunter":
            primary_player.add_resources(1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Raiding Portal":
            if not primary_player.exhaust_card_in_hq_given_name("Raiding Portal"):
                self.delete_reaction()
            else:
                self.chosen_first_card = False
                self.misc_target_planet = self.positions_of_unit_triggering_reaction[0][1]
        elif current_reaction == "Made Ta Fight":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Made Ta Fight?"
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            self.misc_target_planet = warlord_pla
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
        elif current_reaction == "Doom Siren":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if planet_pos != 0:
                if self.planets_in_play_array[planet_pos + 1]:
                    secondary_player.suffer_area_effect(planet_pos + 1, self.value_doom_siren)
            if planet_pos != 6:
                if self.planets_in_play_array[planet_pos - 1]:
                    secondary_player.suffer_area_effect(planet_pos - 1, self.value_doom_siren)
            primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Inquisitor Caius Wroth":
            primary_player.discard_inquis_caius_wroth = True
            secondary_player.discard_inquis_caius_wroth = True
        elif current_reaction == "Leviathan Hive Ship":
            primary_player.aiming_reticle_coords_discard = None
            self.chosen_first_card = False
            primary_player.exhaust_card_in_hq_given_name("Leviathan Hive Ship")
        elif current_reaction == "Holy Sepulchre":
            self.resolving_search_box = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Holy Sepulchre?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.delete_reaction()
        elif current_reaction == "Cato's Stronghold":
            primary_player.exhaust_card_in_hq_given_name("Cato's Stronghold")
        elif current_reaction == "Ardaci-strain Broodlord":
            primary_player.draw_card()
        elif current_reaction == "Seekers of Pleasure":
            target_pla = self.additional_reactions_info[0]
            if target_pla is not None:
                if primary_player.move_unit_to_planet(planet_pos, unit_pos, target_pla):
                    last_el_index = len(primary_player.cards_in_play[target_pla + 1]) - 1
                    primary_player.increase_sweep_given_pos_eor(target_pla, last_el_index, 1)
            self.delete_reaction()
        elif current_reaction == "Commander Shadowsun":
            await self.send_update_message("Resolve shadowsun")
            self.resolving_search_box = True
            self.choices_available = ["Hand", "Discard"]
            self.choice_context = "Shadowsun plays attachment from hand or discard?"
            self.name_player_making_choices = self.player_who_resolves_reaction[0]
            self.misc_target_planet = self.positions_of_unit_triggering_reaction[0][1]
        elif current_reaction == "Repurposed Pariah":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos)
            enemy_pla, enemy_pos = self.additional_reactions_info[0]
            secondary_player.exhaust_given_pos(enemy_pla, enemy_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "The Price of Success":
            battle_planet = self.last_planet_checked_for_battle
            for i in range(len(primary_player.cards_in_reserve[battle_planet])):
                if primary_player.cards_in_reserve[battle_planet][i].get_ability() == "The Price of Success":
                    if primary_player.spend_resources(primary_player.get_deepstrike_value_given_pos(battle_planet, i)):
                        primary_player.deepstrike_event(battle_planet, i)
                        interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
                        if interrupts:
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Enemy Discard Effect?"
                            self.resolving_search_box = True
                            self.stored_discard_and_target.append((current_reaction, primary_player.number))
                        else:
                            secondary_player.discard_card_at_random()
                            secondary_player.discard_card_at_random()
                            for j in range(len(primary_player.cards_in_reserve[battle_planet])):
                                if primary_player.cards_in_reserve[battle_planet][
                                    j].get_ability() == "The Price of Success":
                                    self.create_reaction("The Price of Success", primary_player.name_player,
                                                         (int(primary_player.number), -1, -1))
                            await primary_player.dark_eldar_event_played()
                            self.delete_reaction()
                        break
        elif current_reaction == "Liatha's Loyal Hound":
            if primary_player.cards_removed_from_game:
                primary_player.cards_removed_from_game_hidden[-1] = "N"
            else:
                self.delete_reaction()
        elif current_reaction == "Razorwing Jetfighter":
            primary_player.set_once_per_phase_used_given_pos(
                planet_pos, unit_pos, primary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos) + 1)
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Chaos Maulerfiend":
            target_pla, target_pos = extra_info
            secondary_player.cards_in_play[target_pla + 1][target_pos].cannot_remove_damage_eor = True
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Decayed Gardens":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
        elif current_reaction == "Sickening Helbrute":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True)
            self.delete_reaction()
        elif current_reaction == "Kroot Hunting Rifle":
            primary_player.add_resources(1)
            self.delete_reaction()
        elif current_reaction == "Awakened Geomancer":
            self.misc_counter = 3
        elif current_reaction == "Shambling Revenant":
            primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
            self.delete_reaction()
        elif current_reaction == "Overseer Drone":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            pla, pos = extra_info
            primary_player.increase_attack_of_unit_at_pos(pla, pos, 2, expiration="NEXT")
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Lokhust Destroyer":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos)
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Prognosticator":
            primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, True)
        elif current_reaction == "Interceptor Squad":
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
            await self.send_update_message("Choose planet to move to.")
            self.chosen_first_card = False
        elif current_reaction == "Fierce Purgator":
            self.misc_misc = []
            self.misc_misc_2 = []
            self.misc_misc.append(planet_pos)
            if planet_pos != 0:
                if self.planets_in_play_array[planet_pos - 1]:
                    self.misc_misc.append(planet_pos - 1)
            if planet_pos != 6:
                if self.planets_in_play_array[planet_pos + 1]:
                    self.misc_misc.append(planet_pos + 1)
        elif current_reaction == "Avenging Squad":
            primary_player.increase_retaliate_given_pos_eop(planet_pos, unit_pos, 1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Invasion Site":
            i_site_loc = -1
            for i in range(len(primary_player.headquarters)):
                if primary_player.get_ability_given_pos(-2, i) == "Invasion Site":
                    i_site_loc = i
            if i_site_loc != -1:
                if self.apoka or self.blackstone:
                    primary_player.add_resources(3)
                else:
                    primary_player.add_resources(primary_player.highest_cost_invasion_site)
                primary_player.sacrifice_card_in_hq(i_site_loc)
            self.delete_reaction()
        elif current_reaction == "Vha'shaelhur":
            primary_player.summon_token_at_hq("Cultist", 1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Slavering Mawloc":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            if planet_pos != -2:
                primary_player.cards_in_play[planet_pos + 1][unit_pos].armorbane_eop = True
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Tower of Worship":
            primary_player.summon_token_at_hq("Cultist", 1)
            self.delete_reaction()
        elif current_reaction == "Shard of the Deceiver":
            if not primary_player.cards:
                num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                primary_player.add_card_in_play_to_discard(planet_pos, unit_pos)
                self.delete_reaction()
        elif current_reaction == "Avatar of Khaine":
            if not primary_player.cards:
                num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                primary_player.add_card_in_play_to_discard(planet_pos, unit_pos)
                self.delete_reaction()
        elif current_reaction == "Flayed Ones Revenants":
            primary_player.draw_card()
            primary_player.draw_card()
            primary_player.add_resources(2)
            self.delete_reaction()
        elif current_reaction == "Lictor Vine Lurker":
            secondary_player.discard_card_at_random()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Kabalite Blackguard":
            self.choices_available = ["0", "1", "2"]
            if secondary_player.resources < 2 or self.apoka:
                self.choices_available.remove("2")
            if secondary_player.resources < 1:
                self.choices_available.remove("1")
            self.choice_context = "Kabalite Blackguard Amount"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Cloud of Flies":
            self.location_of_indirect = "PLANET"
            self.planet_of_indirect = self.positions_of_unit_triggering_reaction[0][1]
            self.valid_targets_for_indirect = ["Army", "Warlord", "Synapse", "Token"]
            primary_player.indirect_damage_applied = 0
            primary_player.total_indirect_damage = 2
            secondary_player.indirect_damage_applied = 0
            secondary_player.total_indirect_damage = 2
            self.forbidden_traits_indirect = "Nurgle"
            self.delete_reaction()
        elif current_reaction == "Drammask Nane":
            self.chosen_first_card = False
            self.misc_target_planet = planet_pos
        elif current_reaction == "Connoisseur of Terror":
            primary_player.draw_card()
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Close Quarters Doctrine":
            primary_player.draw_card()
            self.delete_reaction()
        elif current_reaction == "Masters of the Webway":
            primary_player.sacrifice_card_in_hq(unit_pos)
            self.masters_of_the_webway = True
            self.delete_reaction()
        elif current_reaction == "Scavenging Kroot Rider":
            self.chosen_first_card = False
            await self.send_update_message("Exhaust enemy Limited support first.")
        elif current_reaction == "The Dawnsinger":
            self.choices_available = ["Lose 2 cards", "Opponent draws 2 cards"]
            self.choice_context = "The Dawnsinger Choice"
            self.name_player_making_choices = secondary_player.name_player
            self.misc_counter = 0
            self.resolving_search_box = True
            self.player_who_resolves_reaction[0] = secondary_player.name_player
        elif current_reaction == "The Blinded Princess":
            self.player_who_resolves_reaction[0] = secondary_player.name_player
        elif current_reaction == "The Webway Witch":
            secondary_player.webway_witch = planet_pos
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Commander Bravestorm":
            if not primary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos) or not self.apoka:
                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
                primary_player.draw_card()
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "The Dance Without End":
            if primary_player.resources > 0:
                can_continue = True
                if self.nullify_enabled:
                    if secondary_player.nullify_check():
                        await self.send_update_message(primary_player.name_player + " wants to play " +
                                                       current_reaction + "; Nullify window offered.")
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Use Nullify?"
                        self.nullified_card_pos = -1
                        self.nullified_card_name = current_reaction
                        self.cost_card_nullified = 1
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Reaction Event"
                        can_continue = False
                if can_continue:
                    primary_player.spend_resources(1)
                    primary_player.discard_card_name_from_hand("The Dance Without End")
                    self.chosen_first_card = False
                    self.chosen_second_card = False
                    await self.send_update_message("Choose card to return to hand.")
            else:
                self.delete_reaction()
        elif current_reaction == "Yvraine's Entourage":
            self.misc_misc = None
            self.chosen_first_card = False
        elif current_reaction == "Phantasmatic Masque":
            primary_player.exhaust_given_pos(planet_pos, unit_pos)
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            for planet in range(7):
                for i in range(len(secondary_player.cards_in_play[planet + 1])):
                    if secondary_player.cards_in_play[planet + 1][i].resolving_attack:
                        secondary_player.assign_damage_to_pos(planet, i, 2,
                                                              rickety_warbuggy=True, shadow_field_possible=True)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Host of the Emissary":
            primary_player.exhaust_card_in_hq_given_name("Host of the Emissary")
            self.player_who_resolves_reaction[0] = secondary_player.name_player
        elif current_reaction == "Impulsive Loota Reserve" or current_reaction == "Impulsive Loota In Play":
            self.chosen_first_card = False
            await self.send_update_message("Please choose the card to deepstrike.")
        elif current_reaction == "Willing Submission":
            primary_player.draw_card()
            self.chosen_first_card = False
            self.choice_context = "WillSub: Draw Card for Damage?"
            self.choices_available = ["Yes", "No"]
            self.name_player_making_choices = secondary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Tides of Chaos":
            resources_to_spend = 1
            if primary_player.urien_relevant:
                resources_to_spend = 2
            if primary_player.spend_resources(resources_to_spend):
                primary_player.discard_card_name_from_hand("Tides of Chaos")
                for i in range(len(primary_player.headquarters)):
                    if primary_player.get_card_type_given_pos(-2, i) == "Army":
                        primary_player.headquarters[i].extra_command_eop += primary_player.get_attack_given_pos(-2, i)
                for i in range(len(secondary_player.headquarters)):
                    if secondary_player.get_card_type_given_pos(-2, i) == "Army":
                        secondary_player.headquarters[i].extra_command_eop += secondary_player.get_attack_given_pos(-2, i)
                for i in range(7):
                    for j in range(len(primary_player.cards_in_play[i + 1])):
                        if primary_player.get_card_type_given_pos(i, j) == "Army":
                            primary_player.cards_in_play[i + 1][j].extra_command_eop += \
                                primary_player.get_attack_given_pos(i, j)
                    for j in range(len(secondary_player.cards_in_play[i + 1])):
                        if secondary_player.get_card_type_given_pos(i, j) == "Army":
                            secondary_player.cards_in_play[i + 1][j].extra_command_eop +=\
                                secondary_player.get_attack_given_pos(i, j)
            self.delete_reaction()
        elif current_reaction == "The Inevitable Decay":
            if primary_player.resources > 0:
                if "The Inevitable Decay" in primary_player.cards:
                    primary_player.spend_resources(1)
                    self.chosen_first_card = False
                    primary_player.discard_card_name_from_hand("The Inevitable Decay")
                elif "The Inevitable Decay" in primary_player.cards_removed_from_game:
                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                    vael_relevant = False
                    vael_bloodied = False
                    if primary_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                            primary_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                    elif primary_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                            and not primary_player.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                        vael_bloodied = True
                    if vael_relevant:
                        primary_player.spend_resources(1)
                        self.chosen_first_card = False
                        primary_player.cards_removed_from_game.remove("The Inevitable Decay")
                        del primary_player.cards_removed_from_game_hidden[0]
                        primary_player.add_card_to_discard("The Inevitable Decay")
                        if vael_bloodied:
                            primary_player.set_once_per_game_used_given_pos(warlord_pla, warlord_pos, True)
                        else:
                            primary_player.set_once_per_round_used_given_pos(warlord_pla, warlord_pos, True)
                    else:
                        self.delete_reaction()
                else:
                    self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "The Grand Plan":
            if primary_player.resources > 0:
                if "The Grand Plan" in primary_player.cards:
                    primary_player.spend_resources(1)
                    primary_player.discard_card_name_from_hand("The Grand Plan")
                elif "The Grand Plan" in primary_player.cards_removed_from_game:
                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                    vael_relevant = False
                    vael_bloodied = False
                    if primary_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                            primary_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                    elif primary_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                            and not primary_player.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                        vael_bloodied = True
                    if vael_relevant:
                        primary_player.spend_resources(1)
                        primary_player.cards_removed_from_game.remove("The Grand Plan")
                        del primary_player.cards_removed_from_game_hidden[0]
                        primary_player.add_card_to_discard("The Grand Plan")
                        if vael_bloodied:
                            primary_player.set_once_per_game_used_given_pos(warlord_pla, warlord_pos, True)
                        else:
                            primary_player.set_once_per_round_used_given_pos(warlord_pla, warlord_pos, True)
                    else:
                        self.delete_reaction()
                else:
                    self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "The Blood Pits":
            if primary_player.resources > 0:
                if "The Blood Pits" in primary_player.cards:
                    primary_player.spend_resources(1)
                    primary_player.discard_card_name_from_hand("The Blood Pits")
                    self.misc_misc = []
                    await self.send_update_message("Press pass button to deal the damage after choosing units.")
                elif "The Blood Pits" in primary_player.cards_removed_from_game:
                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                    vael_relevant = False
                    vael_bloodied = False
                    if primary_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                            primary_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                    elif primary_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                            and not primary_player.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                        vael_bloodied = True
                    if vael_relevant:
                        primary_player.spend_resources(1)
                        primary_player.cards_removed_from_game.remove("The Blood Pits")
                        del primary_player.cards_removed_from_game_hidden[0]
                        primary_player.add_card_to_discard("The Blood Pits")
                        self.misc_misc = []
                        await self.send_update_message("Press pass button to deal the damage after choosing units.")
                        if vael_bloodied:
                            primary_player.set_once_per_game_used_given_pos(warlord_pla, warlord_pos, True)
                        else:
                            primary_player.set_once_per_round_used_given_pos(warlord_pla, warlord_pos, True)
                    else:
                        self.delete_reaction()
                else:
                    self.delete_reaction()
            else:
                self.delete_reaction()
        elif current_reaction == "Vargus Commit":
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            bloodied = False
            if warlord_pla == -2:
                bloodied = primary_player.headquarters[warlord_pos].get_bloodied()
            elif warlord_pla != -1:
                bloodied = primary_player.cards_in_play[warlord_pla + 1][warlord_pos].get_bloodied()
            if bloodied:
                primary_player.add_resources(2)
            else:
                primary_player.add_resources(1)
            self.delete_reaction()
        elif current_reaction == "Raiding Kabal":
            primary_player.summon_token_at_planet("Khymera", self.last_planet_checked_for_battle)
            self.delete_reaction()
        elif current_reaction == "Erida Commit":
            await self.send_update_message("Please handle the hand size limit yourself.")
            self.delete_reaction()
        elif current_reaction == "Munos Commit":
            if not primary_player.deck:
                self.delete_reaction()
            else:
                self.choices_available = [primary_player.deck[0], "Do Nothing"]
                self.choice_context = "Munos Topdeck"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
        elif current_reaction == "Anshan Commit":
            self.choices_available = ["Draw 1 card", "Gain 1 resource"]
            self.choice_context = "Anshan own gains"
            self.name_player_making_choices = primary_player.name_player
            self.resolving_search_box = True
        elif current_reaction == "Patient Infiltrator":
            primary_player.ready_given_pos(planet_pos, unit_pos)
        elif current_reaction == "Kabal of the Ebon Law":
            will_draw = False
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.get_attack_given_pos(planet_pos, i) > 1:
                    will_draw = True
            if will_draw:
                primary_player.draw_card()
            will_draw = False
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if secondary_player.get_attack_given_pos(planet_pos, i) > 1:
                    will_draw = True
            if will_draw:
                secondary_player.draw_card()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif current_reaction == "Sootblade Assashun":
            self.location_of_indirect = "PLANET"
            self.indirect_exhaust_only = True
            self.planet_of_indirect = self.positions_of_unit_triggering_reaction[0][1]
            self.valid_targets_for_indirect = ["Army", "Warlord", "Synapse", "Token"]
            secondary_player.indirect_damage_applied = 0
            secondary_player.total_indirect_damage = 2
            self.delete_reaction()
        elif current_reaction == "Mark of Chaos":
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                secondary_player.assign_damage_to_pos(planet_pos, i, 1)
            self.delete_reaction()
