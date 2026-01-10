from .. import FindCard
from ..Phases import DeployPhase
from .. import CardClasses
import copy


async def update_game_event_action_in_play(self, name, game_update_string):
    if name == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    planet_pos = int(game_update_string[2])
    unit_pos = int(game_update_string[3])
    if game_update_string[1] == "1":
        card_chosen = self.p1.cards_in_play[planet_pos + 1][unit_pos]
        player_owning_card = self.p1
    else:
        card_chosen = self.p2.cards_in_play[planet_pos + 1][unit_pos]
        player_owning_card = self.p2
    card = card_chosen
    if not self.action_chosen:
        print("action not chosen")
        if card_chosen.get_has_action_while_in_play():
            if card_chosen.get_allowed_phases_while_in_play() == self.phase or \
                    card_chosen.get_allowed_phases_while_in_play() == "ALL" or card_chosen.get_ability() == "Cardback":
                print("reached new in play unit action")
                ability = card_chosen.get_ability(bloodied_relevant=True)
                self.position_of_actioned_card = (planet_pos, unit_pos)
                if player_owning_card.name_player != name:
                    if ability == "Sslyth Mercenary":
                        if primary_player.spend_resources(2):
                            self.take_control_of_card(primary_player, secondary_player, planet_pos, unit_pos)
                            self.action_cleanup()
                if player_owning_card.name_player == name:
                    if ability == "Haemonculus Tormentor":
                        if player_owning_card.spend_resources(1):
                            player_owning_card.increase_attack_of_unit_at_pos(planet_pos, unit_pos,
                                                                              2, expiration="EOP")
                            self.mask_jain_zar_check_actions(primary_player, secondary_player)
                            self.action_cleanup()
                            await self.send_update_message("Haemonculus buffed")
                    elif ability == "Virulent Spore Sacs":
                        player_owning_card.sacrifice_card_in_play(planet_pos, unit_pos)
                        self.infest_planet(planet_pos, player_owning_card)
                        for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                            secondary_player.assign_damage_to_pos(planet_pos, i, 1, shadow_field_possible=True,
                                                                  rickety_warbuggy=True)
                        self.action_cleanup()
                    elif ability == "The Glovodan Eagle":
                        primary_player.return_card_to_hand(planet_pos, unit_pos)
                        self.action_cleanup()
                    elif ability == "Captain Markis":
                        if self.apoka:
                            if not card_chosen.get_once_per_round_used():
                                card_chosen.set_once_per_round_used(True)
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                self.chosen_second_card = False
                                self.chosen_first_card = False
                        elif not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.chosen_second_card = False
                            self.chosen_first_card = False
                    elif ability == "Air Caste Courier":
                        if card_chosen.get_ready():
                            player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.chosen_second_card = False
                    elif ability == "Big Mek Kagdrak":
                        if not card.get_once_per_round_used():
                            card.set_once_per_round_used(True)
                            await self.send_update_message("Choose target for Big Mek Kagrak.")
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Big Mek Kagdrak BLOODIED":
                        if not card.get_once_per_game_used():
                            card.set_once_per_game_used(True)
                            await self.send_update_message("Choose target for Big Mek Kagrak.")
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Wildrider Squadron":
                        if not card_chosen.get_once_per_phase_used():
                            if player_owning_card.name_player == name:
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Canoness Vardina":
                        if not card_chosen.bloodied:
                            if not card_chosen.get_once_per_round_used():
                                card_chosen.set_once_per_round_used(True)
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.misc_counter = 2
                                if secondary_player.check_for_warlord(planet_pos, True, primary_player.name_player):
                                    self.misc_counter = 3
                                await self.send_update_message("Place " + str(self.misc_counter) + " faith tokens.")
                        else:
                            if not card_chosen.get_once_per_game_used():
                                card_chosen.set_once_per_game_used(True)
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                self.action_chosen = ability + " BLD"
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.misc_counter = 2
                                await self.send_update_message("Place " + str(self.misc_counter) + " faith tokens.")
                    elif ability == "Vaulting Harlequin":
                        if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].flying_eop = True
                            self.mask_jain_zar_check_actions(primary_player, secondary_player)
                            self.action_cleanup()
                    elif ability == "Boss Zugnog":
                        if not card_chosen.get_once_per_phase_used():
                            if self.planets_in_play_array[self.round_number]:
                                card_chosen.set_once_per_phase_used(True)
                                self.action_chosen = ability
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.misc_target_planet = planet_pos
                                self.misc_counter = 0
                    elif ability == "Hunter Gargoyles":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    elif ability == "Castellan Crowe BLOODIED":
                        if not card_chosen.get_once_per_game_used():
                            card_chosen.set_once_per_game_used(True)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Torquemada Coteaz":
                        if not card_chosen.misc_ability_used:
                            card_chosen.misc_ability_used = True
                            self.action_chosen = ability
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    elif ability == "Canoptek Spyder":
                        if not card_chosen.once_per_combat_round_used:
                            if planet_pos == self.last_planet_checked_for_battle:
                                card_chosen.once_per_combat_round_used = True
                                self.action_chosen = ability
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.chosen_first_card = False
                    elif ability == "Mandragoran Immortals":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    elif ability == "Autarch Celachia":
                        if not card_chosen.once_per_round_used:
                            if primary_player.spend_resources(1):
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                if self.phase == "DEPLOY":
                                    self.player_with_deploy_turn = secondary_player.name_player
                                    self.number_with_deploy_turn = secondary_player.number
                                self.choices_available = ["Area Effect (1)", "Armorbane", "Mobile"]
                                self.choice_context = "Autarch Celachia"
                                self.name_player_making_choices = primary_player.name_player
                    elif ability == "Immortal Legion":
                        if card_chosen.get_ready():
                            if secondary_player.warlord_faction == primary_player.enslaved_faction:
                                target_planet = secondary_player.get_planet_of_warlord()
                                if target_planet != -2 and target_planet != -1:
                                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                    primary_player.move_unit_to_planet(planet_pos, unit_pos, target_planet)
                                    self.action_cleanup()
                    elif ability == "Lone Wolf":
                        if card_chosen.get_ready():
                            target_planet = secondary_player.get_planet_of_warlord()
                            if target_planet != -2 and target_planet != -1:
                                if not primary_player.cards_in_play[target_planet + 1]:
                                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                    primary_player.move_unit_to_planet(planet_pos, unit_pos, target_planet)
                                    self.action_cleanup()
                    elif ability == "Pattern IX Immolator":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.misc_counter = secondary_player.command_struggles_won_this_phase - 1
                            if self.misc_counter < 1:
                                await self.send_update_message("Opponent did not win enough command struggles for "
                                                               "Pattern IX Immolator to do anything.")
                                self.action_cleanup()
                            else:
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                                self.misc_misc = []
                                self.action_chosen = ability
                                self.chosen_first_card = False
                                await self.send_update_message("Deal " + str(self.misc_counter) + " damage first.")
                    elif ability == "The Emperor's Champion":
                        if not card_chosen.once_per_combat_round_used:
                            card_chosen.once_per_combat_round_used = True
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    elif ability == "Ba'ar Zul's Cleavers":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 2, "NEXT")
                            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, by_enemy_unit=False)
                            self.mask_jain_zar_check_actions(primary_player, secondary_player)
                            self.action_cleanup()
                    elif ability == "Agnok's Shadows":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.misc_target_planet = planet_pos
                            self.action_chosen = ability
                            self.chosen_first_card = False
                    elif ability == "Ravenwing Escort":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.misc_target_planet = planet_pos
                            self.action_chosen = ability
                            self.chosen_first_card = False
                    elif ability == "Dread Monolith":
                        if not card_chosen.once_per_round_used:
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].set_once_per_round_used(True)
                            self.action_chosen = ability
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            cards_discard = []
                            for _ in range(3):
                                if primary_player.discard_top_card_deck():
                                    last_element = len(primary_player.discard) - 1
                                    cards_discard.append(primary_player.discard[last_element])
                            self.choices_available = []
                            for i in range(len(cards_discard)):
                                card = FindCard.find_card(cards_discard[i], self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
                                if card.get_is_unit() and card.get_faction() == "Necrons":
                                    if not card.check_for_a_trait("Vehicle", primary_player.etekh_trait):
                                        self.choices_available.append(card.get_name())
                            if self.choices_available:
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.choice_context = "Target Dread Monolith:"
                                self.name_player_making_choices = primary_player.name_player
                            else:
                                await self.send_update_message(
                                    "No valid targets for Dread Monolith; better luck next time!"
                                )
                                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                                self.action_cleanup()
                    elif ability == "Pathfinder Shi Or'es":
                        if not card_chosen.get_once_per_phase_used():
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            card_chosen.set_once_per_phase_used(True)
                    elif ability == "Twisted Wracks":
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Rotten Plaguebearers":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Seekers of Slaanesh":
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        self.misc_target_planet = planet_pos
                    elif ability == "Inexperienced Weirdboy":
                        if not card_chosen.once_per_combat_round_used:
                            if planet_pos == self.last_planet_checked_for_battle:
                                card_chosen.once_per_combat_round_used = True
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                self.misc_target_planet = planet_pos
                    elif ability == "Aun'Len BLOODIED":
                        if self.planet_array[planet_pos] != "Jaricho" and \
                                (self.planet_array[
                                     planet_pos] != "Nectavus XI" or self.resolve_remaining_cs_after_reactions):
                            if not primary_player.get_once_per_game_used_given_pos(planet_pos, unit_pos):
                                primary_player.set_once_per_game_used_given_pos(planet_pos, unit_pos, True)
                                self.action_cleanup()
                                self.need_to_resolve_battle_ability = True
                                self.resolving_search_box = True
                                self.battle_ability_to_resolve = self.planet_array[planet_pos]
                                self.player_resolving_battle_ability = primary_player.name_player
                                self.number_resolving_battle_ability = primary_player.number
                                self.choices_available = ["Yes", "No"]
                                self.choice_context = "Resolve Battle Ability?"
                                self.name_player_making_choices = primary_player.name_player
                                self.tense_negotiations_active = True
                    elif ability == "Abrasive Squigherder":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.resolving_search_box = True
                            self.what_to_do_with_searched_card = "DRAW"
                            self.traits_of_searched_card = "Squig"
                            self.card_type_of_searched_card = None
                            self.faction_of_searched_card = None
                            self.max_cost_of_searched_card = 999
                            self.all_conditions_searched_card_required = True
                            self.no_restrictions_on_chosen_card = False
                            primary_player.number_cards_to_search = 6
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                                    if primary_player.headquarters[i].counter > 0:
                                        primary_player.number_cards_to_search += 2
                            if primary_player.number_cards_to_search > len(primary_player.deck):
                                primary_player.number_cards_to_search = len(primary_player.deck)
                            self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = primary_player.number
                            self.mask_jain_zar_check_actions(primary_player, secondary_player)
                            self.action_cleanup()
                    elif ability == "Korporal Snagbrat":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.misc_target_choice = ""
                            self.misc_target_unit = (-1, -1)
                            self.chosen_first_card = False
                    elif ability == "Raging Krootox":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            amount = primary_player.resources
                            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, amount, "EOP")
                            await self.send_update_message("Raging Krootox gained +" + str(amount) + " ATK.")
                            self.mask_jain_zar_check_actions(primary_player, secondary_player)
                            self.action_cleanup()
                    elif ability == "Dread Command Barge":
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.chosen_first_card = False
                    elif ability == "Pinning Razorback":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    elif ability == "Alluring Daemonette":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.chosen_first_card = False
                    elif ability == "Da 'Eavy":
                        primary_player.retreat_unit(planet_pos, unit_pos)
                        self.action_cleanup()
                    elif ability == "Mekaniak Repair Krew":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Veteran Brother Maxos":
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Death Korps Engineers":
                        self.action_chosen = ability
                        player_owning_card.sacrifice_card_in_play(planet_pos, unit_pos)
                    elif ability == "Imotekh the Stormlord":
                        if not card_chosen.get_once_per_phase_used():
                            if not card_chosen.bloodied:
                                card_chosen.set_once_per_phase_used(True)
                                self.action_chosen = ability
                                self.chosen_first_card = False
                                self.misc_target_player = ""
                                await self.send_update_message("Imotekh activated; only army units supported.")
                    elif ability == "Chaplain Mavros":
                        if primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_phase_used is False:
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_phase_used = 1
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                        elif primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_phase_used < 2:
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_phase_used += 1
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Zarathur's Flamers":
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                    elif ability == "Scribe Servo-Skull":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Saint Celestine":
                        if not card_chosen.get_once_per_phase_used():
                            if not card_chosen.bloodied:
                                card_chosen.set_once_per_phase_used(True)
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.chosen_first_card = False
                    elif ability == "Ravenous Flesh Hounds":
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    elif ability == "Conjuring Warmaster":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    elif ability == "Sivarla Soulbinder":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.misc_target_unit = (-1, -1)
                            self.chosen_first_card = False
                    elif ability == "Uncontrollable Rioters":
                        if not card_chosen.get_once_per_round_used():
                            card_chosen.set_once_per_round_used(True)
                            self.take_control_of_card(secondary_player, primary_player, planet_pos, unit_pos)
                            self.action_cleanup()
                    elif ability == "Replicating Scarabs":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Vanguarding Horror":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.misc_target_planet = planet_pos
                    elif ability == "Lekor Blight-Tongue":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Plagueburst Crawler":
                        if not card.get_ready():
                            primary_player.ready_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Improbable Runt Machine":
                        if not card_chosen.get_once_per_round_used():
                            card_chosen.set_once_per_round_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Kaptin Bluddflagg":
                        if not card.get_once_per_round_used():
                            card.set_once_per_round_used(True)
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Ireful Vanguard":
                        if not card.get_once_per_round_used():
                            if secondary_player.won_command_struggles_planets_round[planet_pos]:
                                card.set_once_per_round_used(True)
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    elif ability == "Cardback":
                        if card_chosen.actually_a_deepstrike:
                            actual_ability = card_chosen.deepstrike_card_name
                            if actual_ability == "Patient Infiltrator":
                                ds_value = primary_player.get_deepstrike_value_given_pos(planet_pos, unit_pos,
                                                                                         in_play_card=True)
                                if primary_player.spend_resources(ds_value):
                                    primary_player.deepstrike_unit(planet_pos, unit_pos, in_play_card=True)
                                    self.action_cleanup()
                            elif actual_ability == "XV25 Stealth Squad":
                                ds_value = primary_player.get_deepstrike_value_given_pos(planet_pos, unit_pos,
                                                                                         in_play_card=True)
                                if primary_player.spend_resources(ds_value):
                                    primary_player.deepstrike_unit(planet_pos, unit_pos, in_play_card=True)
                                    self.action_cleanup()
                    elif ability == "Farseer Tadheris":
                        if not card.get_bloodied():
                            if not primary_player.get_once_per_round_used_given_pos(planet_pos, unit_pos):
                                primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, True)
                                primary_player.mulligan_hand()
                                self.action_cleanup()
                        else:
                            if not primary_player.get_once_per_game_used_given_pos(planet_pos, unit_pos):
                                primary_player.set_once_per_game_used_given_pos(planet_pos, unit_pos, True)
                                primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                                primary_player.mulligan_hand()
                                self.action_cleanup()
                    elif ability == "Slave-powered Wagons":
                        if not card_chosen.get_once_per_round_used():
                            card_chosen.set_once_per_round_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Evangelizing Ships":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.chosen_first_card = False
                            self.chosen_second_card = False
                            await self.send_update_message("Please pay 1 faith")
                    elif ability == "Techmarine Aspirant":
                        if primary_player.resources > 0:
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.misc_target_planet = planet_pos
                    elif ability == "Keening Maleceptor":
                        if not primary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos):
                            if self.infested_planets[planet_pos] and self.planet_array[planet_pos] != "Jaricho":
                                self.infested_planets[planet_pos] = False
                                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
                                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                                self.action_cleanup()
                                self.need_to_resolve_battle_ability = True
                                self.battle_ability_to_resolve = self.planet_array[planet_pos]
                                self.player_resolving_battle_ability = primary_player.name_player
                                self.number_resolving_battle_ability = str(primary_player.number)
                                self.choices_available = ["Yes", "No"]
                                self.choice_context = "Resolve Battle Ability?"
                                self.name_player_making_choices = primary_player.name_player
                                self.tense_negotiations_active = True
                    elif ability == "Talyesin's Warlocks":
                        if not primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_combat_round_used:
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_combat_round_used = True
                    elif ability == "Ancient Keeper of Secrets":
                        if player_owning_card.name_player == name:
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Nazdreg's Flash Gitz":
                        if not card_chosen.get_once_per_phase_used():
                            if player_owning_card.name_player == name:
                                if not card_chosen.get_ready():
                                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1,
                                                                            by_enemy_unit=False)
                                    player_owning_card.ready_given_pos(planet_pos, unit_pos)
                                    card_chosen.set_once_per_phase_used(True)
                                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                                    self.action_cleanup()
    elif self.action_chosen == "Twisted Laboratory":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos,
                                                                                 intercept_possible=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = self.action_chosen
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "In Play Action"
        if can_continue:
            if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
                player_being_hit.set_blanked_given_pos(planet_pos, unit_pos, exp="EOP")
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                await self.send_update_message(
                    "Twisted Laboratory used on " + player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_name()
                    + ", located at planet " + str(planet_pos) + ", position " + str(unit_pos))
                self.action_cleanup()
    elif self.action_chosen == "Ravenwing Escort":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if self.misc_target_planet == planet_pos:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
    elif self.action_chosen == "Crown of Control":
        if game_update_string[1] == primary_player.number:
            if self.misc_target_planet == planet_pos:
                if primary_player.get_damage_given_pos(planet_pos, unit_pos) > 0:
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                    self.misc_counter += 1
                    if self.misc_counter > 1:
                        self.action_cleanup()
    elif self.action_chosen == "Agnok's Shadows":
        if not self.chosen_first_card:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                if self.misc_target_planet == planet_pos:
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        player_owning_card.increase_attack_of_unit_at_pos(planet_pos, unit_pos, -2, expiration="EOP")
                        self.chosen_first_card = True
                        await self.send_update_message(player_owning_card.get_name_given_pos(planet_pos, unit_pos) +
                                                       " received -2 ATK!")
    elif self.action_chosen == "Evolutionary Adaptation":
        if self.chosen_first_card:
            if primary_player.get_number() == game_update_string[1]:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" and \
                        primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Kroot"):
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        if self.misc_target_choice == "Brutal":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].brutal_eor = True
                        if self.misc_target_choice == "Armorbane":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].armorbane_eor = True
                        if self.misc_target_choice == "Flying":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].flying_eor = True
                        if self.misc_target_choice == "Mobile":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].mobile_eor = True
                        if self.misc_target_choice == "Ranged":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].ranged_eor = True
                        if self.misc_target_choice == "Area Effect":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].area_effect_eor = \
                                self.stored_area_effect_value
                        name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                        if self.misc_target_choice == "Area Effect":
                            self.misc_target_choice += " (" + str(self.stored_area_effect_value) + ")"
                        await self.send_update_message(
                            name + " gained " + self.misc_target_choice + "."
                        )
                        self.action_cleanup()
                        self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Behind Enemy Lines":
        if self.chosen_second_card:
            if game_update_string[1] == secondary_player.get_number():
                if self.misc_target_planet == planet_pos:
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if not secondary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                            if secondary_player.get_ready_given_pos(planet_pos, unit_pos):
                                can_continue = True
                                possible_interrupts = []
                                if player_owning_card.name_player == primary_player.name_player:
                                    possible_interrupts = secondary_player.intercept_check()
                                if player_owning_card.name_player == secondary_player.name_player:
                                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                                        planet_pos, unit_pos, intercept_possible=True, event=True)
                                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                        can_continue = False
                                        await self.send_update_message("Immune to enemy card abilities.")
                                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                                        can_continue = False
                                        await self.send_update_message("Immune to enemy events.")
                                if possible_interrupts and can_continue:
                                    can_continue = False
                                    await self.send_update_message("Some sort of interrupt may be used.")
                                    self.choices_available = possible_interrupts
                                    self.choices_available.insert(0, "No Interrupt")
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Interrupt Effect?"
                                    self.nullified_card_name = self.action_chosen
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Event Action"
                                if can_continue:
                                    secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                                    self.action_cleanup()
    elif self.action_chosen == "Mont'ka Strike":
        if game_update_string[1] == secondary_player.get_number():
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                total_atk = 0
                for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                    if primary_player.check_for_trait_given_pos(planet_pos, i, "Soldier"):
                        primary_player.exhaust_given_pos(planet_pos, i)
                        total_atk += primary_player.cards_in_play[planet_pos + 1][unit_pos].attack
                if not secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    secondary_player.assign_damage_to_pos(planet_pos, unit_pos, total_atk, by_enemy_unit=False)
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Saim-Hann Jetbike":
        if self.chosen_first_card:
            if self.misc_target_planet == planet_pos:
                if game_update_string[1] == "1":
                    player_being_hit = self.p1
                else:
                    player_being_hit = self.p2
                if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                    self.action_cleanup()
    elif self.action_chosen == "Fetid Haze":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                        "Nurgle", primary_player.etekh_trait):
                    damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
                    self.location_of_indirect = "PLANET"
                    self.planet_of_indirect = planet_pos
                    self.valid_targets_for_indirect = ["Army"]
                    secondary_player.indirect_damage_applied = 0
                    secondary_player.total_indirect_damage = damage
                    self.action_cleanup()
    elif self.action_chosen == "Vile Laboratory":
        if self.chosen_first_card and not self.chosen_second_card:
            if planet_pos == self.misc_target_planet:
                if not primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                        "Vehicle", primary_player.etekh_trait):
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.chosen_second_card = True
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Inquisitorial Fortress":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos,
                                                                                     intercept_possible=True,
                                                                                     move_from_planet=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
            if can_continue:
                player_being_hit.rout_unit(planet_pos, unit_pos)
                self.action_cleanup()
    elif self.action_chosen == "Hate":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        can_continue = False
        if primary_player.resources >= player_being_hit.get_cost_given_pos(planet_pos, unit_pos) and \
                primary_player.enslaved_faction == player_being_hit.get_faction_given_pos(planet_pos, unit_pos):
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
        if can_continue:
            primary_player.spend_resources(player_being_hit.get_cost_given_pos(planet_pos, unit_pos))
            if player_being_hit.name_player == secondary_player.name_player:
                if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Flayed Ones Revenants":
                    self.create_reaction("Flayed Ones Revenants", secondary_player.name_player,
                                         (int(secondary_player.number), planet_pos, -1))
            player_being_hit.destroy_card_in_play(planet_pos, unit_pos)
            if not primary_player.harbinger_of_eternity_active:
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
            self.action_cleanup()
    elif self.action_chosen == "Imotekh the Stormlord":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not primary_player.get_unique_given_pos(planet_pos, unit_pos) and not\
                        primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    og_card = self.preloaded_find_card(self.misc_target_player)
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_armorbane = og_card.armorbane
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_ambush = og_card.ambush
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_mobile = og_card.mobile
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_brutal = og_card.brutal
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_sweep = og_card.sweep
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_area_effect = og_card.area_effect
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_ranged = og_card.ranged
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_limited = og_card.limited
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_lumbering = og_card.lumbering
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_unstoppable = og_card.unstoppable
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_flying = og_card.flying
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_additional_resources_command_struggle = \
                        og_card.additional_resources_command_struggle
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_additional_cards_command_struggle = \
                        og_card.additional_cards_command_struggle
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].new_ability = self.misc_target_player
                    card_name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                    self.action_cleanup()
                    await self.send_update_message(card_name + " at " +
                                                   self.planet_array[planet_pos] + " gained " +
                                                   self.misc_target_player + "'s text box!")
    elif self.action_chosen == "Iridescent Wand":
        if planet_pos == self.misc_target_planet:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if self.misc_target_unit != (planet_pos, unit_pos):
                    self.misc_target_unit = (planet_pos, unit_pos)
                    player_owning_card.cards_in_play[planet_pos + 1][unit_pos].increase_sweep_eop(1)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        self.action_cleanup()
    elif self.action_chosen == "Torturer of Worlds":
        if game_update_string[1] == primary_player.get_number():
            if self.replaced_planets[planet_pos]:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if self.misc_target_unit[0] != planet_pos:
                        if not self.chosen_first_card:
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.chosen_first_card = True
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                        else:
                            og_pla, og_pos = self.misc_target_unit
                            primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                            primary_player.cards_in_play[planet_pos + 1].append(primary_player.cards_in_play[og_pla + 1][og_pos])
                            primary_player.cards_in_play[og_pla + 1].append(primary_player.cards_in_play[planet_pos + 1][unit_pos])
                            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                            del primary_player.cards_in_play[og_pla + 1][og_pos]
                            self.action_cleanup()
    elif self.action_chosen == "Canoptek Spyder":
        if self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if self.position_of_actioned_card[0] == planet_pos:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" and \
                            primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
    elif self.action_chosen == "Inexperienced Weirdboy":
        if self.position_of_actioned_card[0] == planet_pos:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    cards_in_hand = len(primary_player.cards)
                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, cards_in_hand)
                    primary_player.assign_damage_to_pos(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1], cards_in_hand,
                                                        by_enemy_unit=False)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "Test of Faith":
        if game_update_string[1] == primary_player.number:
            unique_found = False
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.get_unique_given_pos(planet_pos, i):
                    unique_found = True
            if unique_found:
                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Cultist":
                    if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                        for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                            if primary_player.check_for_trait_given_pos(planet_pos, i, "Cultist") or\
                                    primary_player.check_for_trait_given_pos(planet_pos, i, "Ritualist"):
                                primary_player.increase_faith_given_pos(planet_pos, i, 2)
                        primary_player.drammask_nane_check()
                        self.action_cleanup()
    elif self.action_chosen == "The Strength of the Enemy":
        if self.chosen_first_card:
            if game_update_string[1] == primary_player.number:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if self.misc_target_planet == planet_pos:
                        og_card = self.preloaded_find_card(self.misc_target_player)
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_armorbane = og_card.armorbane
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_ambush = og_card.ambush
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_mobile = og_card.mobile
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_brutal = og_card.brutal
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_sweep = og_card.sweep
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_area_effect = og_card.area_effect
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_ranged = og_card.ranged
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_limited = og_card.limited
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_lumbering = og_card.lumbering
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_unstoppable = og_card.unstoppable
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_flying = og_card.flying
                        primary_player.cards_in_play[planet_pos + 1][
                            unit_pos].new_additional_resources_command_struggle = \
                            og_card.additional_resources_command_struggle
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_additional_cards_command_struggle = \
                            og_card.additional_cards_command_struggle
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].new_ability = self.misc_target_player
                        card_name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                        self.action_cleanup()
                        await self.send_update_message(card_name + " at " +
                                                       self.planet_array[planet_pos] + " gained " +
                                                       self.misc_target_player + "'s text box!")
        else:
            if game_update_string[1] == secondary_player.number:
                if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    self.misc_target_planet = planet_pos
                    self.misc_target_player = secondary_player.get_name_given_pos(planet_pos, unit_pos)
                    await self.send_update_message("Stealing " + self.misc_target_player + "'s text box.")
                    secondary_player.set_blanked_given_pos(planet_pos, unit_pos)
                    self.chosen_first_card = True
    elif self.action_chosen == "Air Caste Courier":
        print("ACC")
        if self.chosen_first_card:
            print("chosen")
            if game_update_string[1] == primary_player.get_number():
                print("num")
                origin_pla, origin_pos, origin_att = self.misc_target_attachment
                print(origin_pla != planet_pos, origin_pos != unit_pos)
                if origin_pla != planet_pos or origin_pos != unit_pos:
                    if primary_player.move_attachment_card(origin_pla, origin_pos, origin_att,
                                                           planet_pos, unit_pos):
                        primary_player.reset_aiming_reticle_in_play(origin_pla, origin_pos)
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
    elif self.action_chosen == "Pact of the Haemonculi":
        if game_update_string[1] == self.number_with_deploy_turn:
            if primary_player.sacrifice_card_in_play(int(game_update_string[2]),
                                                     int(game_update_string[3])):
                primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
                primary_player.aiming_reticle_coords_hand = None
                if interrupts:
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Enemy Discard Effect?"
                    self.resolving_search_box = True
                    self.stored_discard_and_target.append((self.action_chosen, primary_player.number))
                else:
                    secondary_player.discard_card_at_random()
                    primary_player.draw_card()
                    primary_player.draw_card()
                    primary_player.aiming_reticle_color = None
                    self.card_pos_to_deploy = -1
                    self.action_cleanup()
                    await primary_player.dark_eldar_event_played()
    elif self.action_chosen == "Even the Odds":
        if self.chosen_first_card:
            if self.misc_player_storage == game_update_string[1]:
                if game_update_string[1] == "1":
                    player_owning_card = self.p1
                else:
                    player_owning_card = self.p2
                origin_planet, origin_pos, origin_attach_pos = self.misc_target_attachment
                dest_planet = int(game_update_string[2])
                dest_pos = int(game_update_string[3])
                can_continue = True
                if player_owning_card.name_player == secondary_player.name_player:
                    if secondary_player.get_immune_to_enemy_card_abilities(dest_planet, dest_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    if secondary_player.get_immune_to_enemy_events(dest_planet, dest_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if can_continue:
                    if player_owning_card.move_attachment_card(origin_planet, origin_pos, origin_attach_pos,
                                                               dest_planet, dest_pos):
                        player_owning_card.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                        self.chosen_second_card = True
                        self.action_cleanup()
                        self.chosen_second_card = True
                        self.misc_target_attachment = (-1, -1, -1)
                        self.misc_player_storage = ""
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                    else:
                        await self.send_update_message("Invalid attachment movement.")
    elif self.action_chosen == "Boss Zugnog":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" and\
                    primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Orks":
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                self.misc_counter += 1
            if self.misc_counter >= 2:
                i = 0
                while i < len(primary_player.cards_in_play[planet_pos + 1]):
                    if primary_player.cards_in_play[planet_pos + 1][i].aiming_reticle_color == "blue":
                        primary_player.move_unit_to_planet(planet_pos, i, self.round_number, force=True)
                        i = i - 1
                    i = i + 1
                for j in range(len(primary_player.cards_in_play[self.round_number + 1])):
                    if primary_player.cards_in_play[self.round_number + 1][j].aiming_reticle_color == "blue":
                        primary_player.assign_damage_to_pos(self.round_number, j, 1, rickety_warbuggy=True,
                                                            by_enemy_unit=False)
                self.advance_damage_aiming_reticle()
                self.misc_counter = 0
                self.action_cleanup()
    elif self.action_chosen == "Particle Whip":
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = self.action_chosen
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "In Play Action"
        if can_continue:
            if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
                if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter,
                                                            by_enemy_unit=False)
                    self.misc_counter = 0
                    self.action_cleanup()
    elif self.action_chosen == "Doombolt":
        if game_update_string[1] == secondary_player.number:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, move_from_planet=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    damage = secondary_player.get_damage_given_pos(planet_pos, unit_pos)
                    secondary_player.assign_damage_to_pos(planet_pos, unit_pos, damage, by_enemy_unit=False)
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    self.action_cleanup()
    elif self.action_chosen == "Searing Brand":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        can_continue = True
        if primary_player.check_for_warlord(planet_pos, True, primary_player.name_player):
            if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                if player_being_hit.name_player == secondary_player.name_player:
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, context="Searing Brand", event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Event Action"
                    if can_continue:
                        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                            player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 3, preventable=False,
                                                                  by_enemy_unit=False)
                            await primary_player.dark_eldar_event_played()
                            primary_player.torture_event_played("Searing Brand")
                            self.action_cleanup()
    elif self.action_chosen == "Torquemada Coteaz":
        if planet_pos == self.position_of_actioned_card[0]:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                    primary_player.increase_attack_of_unit_at_pos(warlord_planet, warlord_pos, 3, expiration="NEXT")
                    primary_player.reset_aiming_reticle_in_play(warlord_planet, warlord_pos)
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "A Thousand Cuts":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
            if not player_being_hit.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                    primary_player.shuffle_deck()
                    await primary_player.dark_eldar_event_played()
                    primary_player.torture_event_played("A Thousand Cuts")
                    self.action_cleanup()
    elif self.action_chosen == "Power from Pain":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    self.action_cleanup()
                    await secondary_player.dark_eldar_event_played()
                    secondary_player.torture_event_played("Power from Pain")
    elif self.action_chosen == "Overrun":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
            if can_continue:
                player_being_hit.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                primary_player.discard_card_name_from_hand("Overrun")
                primary_player.aiming_reticle_coords_hand = None
                if player_being_hit.name_player == secondary_player.name_player:
                    self.choices_available = ["Sacrifice to Rout", "No Sacrifice"]
                    self.choice_context = "Overrun: Followup Rout?"
                    self.action_chosen = "Overrun Rout"
                    self.name_player_making_choices = primary_player.name_player
                    self.misc_target_unit = (planet_pos, unit_pos)
                else:
                    self.action_cleanup()
    elif self.action_chosen == "Overrun Rout":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                og_pla, og_pos = self.misc_target_unit
                secondary_player.rout_unit(og_pla, og_pos)
                self.action_cleanup()
    elif self.action_chosen == "Improbable Runt Machine":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Runt"):
                name_card = primary_player.get_name_given_pos(planet_pos, unit_pos)
                card_to_add = CardClasses.AttachmentCard(name_card, "", "Copilot.", 0, "Orks", "Common",
                                                         0, False)
                primary_player.attach_card(card_to_add, self.position_of_actioned_card[0],
                                           self.position_of_actioned_card[1])
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                self.action_cleanup()
    elif self.action_chosen == "Keep Firing!":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Tank"):
                if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Event Action"
                    if can_continue:
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        self.action_cleanup()
    elif self.action_chosen == "Tzeentch's Firestorm":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
            if can_continue:
                player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, self.amount_spend_for_tzeentch_firestorm,
                                                      by_enemy_unit=False)
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.amount_spend_for_tzeentch_firestorm = -1
                self.action_cleanup()
    elif self.action_chosen == "Pattern IX Immolator":
        if planet_pos == self.position_of_actioned_card[0]:
            if not self.chosen_first_card:
                if game_update_string[1] == secondary_player.get_number():
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                        secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                        self.misc_misc.append((planet_pos, unit_pos))
                        self.misc_counter = self.misc_counter - 1
                        if self.misc_counter < 1:
                            self.chosen_first_card = True
                            self.misc_counter = secondary_player.command_struggles_won_this_phase - 1
                            await self.send_update_message("Now place " + str(self.misc_counter) + " faith.")
            else:
                if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    player_owning_card.increase_faith_given_pos(planet_pos, unit_pos, 1)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        while self.misc_misc:
                            i = 0
                            num_times_shown_up = 0
                            current_pla, current_pos = self.misc_misc[0]
                            while i < len(self.misc_misc):
                                if self.misc_misc[i] == (current_pla, current_pos):
                                    num_times_shown_up += 1
                                    del self.misc_misc[i]
                                    i = i - 1
                                i = i + 1
                            secondary_player.assign_damage_to_pos(current_pla, current_pos, num_times_shown_up,
                                                                  rickety_warbuggy=True)
                        self.misc_misc = None
                        self.action_cleanup()
    elif self.action_chosen == "Mandragoran Immortals":
        if game_update_string[1] == primary_player.get_number():
            if planet_pos == self.position_of_actioned_card[0]:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_faction() != "Necrons" and \
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                            "Soldier", primary_player.etekh_trait):
                    primary_player.ready_given_pos(self.position_of_actioned_card[0],
                                                   self.position_of_actioned_card[1])
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Calculated Strike":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True, event=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
            elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy events.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = self.action_chosen
            self.cost_card_nullified = 1
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "Event Action"
        if can_continue:
            if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_limited():
                player_being_hit.destroy_card_in_play(planet_pos, unit_pos)
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Alluring Daemonette":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Cultist"):
                    if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                        self.chosen_first_card = True
                        og_pla, og_pos = self.position_of_actioned_card
                        if og_pla == planet_pos:
                            if og_pos > unit_pos:
                                self.position_of_actioned_card = (og_pla, og_pos - 1)
        elif game_update_string[1] == secondary_player.get_number():
            og_pla, og_pos = self.position_of_actioned_card
            if abs(og_pla - planet_pos) == 1:
                if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    can_continue = True
                    if self.slumbering_gardens_enabled:
                        if secondary_player.search_card_in_hq("Slumbering Gardens", ready_relevant=True):
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = ["Slumbering Gardens"]
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "In Play Action"
                    if can_continue:
                        secondary_player.move_unit_to_planet(planet_pos, unit_pos, og_pla)
                        primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
    elif self.action_chosen == "Canoness Vardina":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                self.misc_counter = self.misc_counter - 1
                if self.misc_counter < 1:
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "Holy Crusade":
        if game_update_string[1] == primary_player.get_number():
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.misc_counter = self.misc_counter - 1
            if self.misc_counter < 1:
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.action_cleanup()
    elif self.action_chosen == "Canoness Vardina BLD":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Ecclesiarchy"):
                if planet_pos == self.position_of_actioned_card[0]:
                    player_owning_card.increase_faith_given_pos(planet_pos, unit_pos, 1)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
    elif self.action_chosen == "Embarked Squads":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Vehicle") and not \
                        primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Upgrade"):
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].embarked_squads_active = True
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].extra_traits_eor += "Upgrade. Transport."
                        await self.send_update_message(primary_player.cards_in_play[planet_pos + 1][unit_pos].name +
                                                       "gained the Embarked Squads effect!")
                        primary_player.reset_all_aiming_reticles_play_hq()
                        self.action_cleanup()
    elif self.action_chosen == "Piercing Wail":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if player_being_hit.get_cost_given_pos(planet_pos, unit_pos) <= self.misc_counter:
                can_continue = True
                if player_being_hit.name_player == secondary_player.name_player:
                    if secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                if can_continue:
                    player_being_hit.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                    if not self.chosen_first_card:
                        self.chosen_first_card = True
                    else:
                        self.action_cleanup()
    elif self.action_chosen == "Command-link Drone":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                planet, position, attachment_position = self.position_of_selected_attachment
                og_player = self.misc_target_player
                if og_player == primary_player.name_player:
                    if primary_player.move_attachment_card(planet, position, attachment_position, planet_pos, unit_pos):
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
                else:
                    card = secondary_player.get_attachment_at_pos(planet, position, attachment_position)
                    if primary_player.attach_card(card, planet_pos, unit_pos):
                        secondary_player.remove_attachment_from_pos(planet, position, attachment_position)
                        secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                      self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
        else:
            if secondary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                planet, position, attachment_position = self.position_of_selected_attachment
                og_player = self.misc_target_player
                if og_player == secondary_player.name_player:
                    card = secondary_player.get_attachment_at_pos(planet, position, attachment_position)
                    if secondary_player.attach_card(card, planet_pos, unit_pos, not_own_attachment=True):
                        secondary_player.remove_attachment_from_pos(planet, position, attachment_position)
                        secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                      self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
                else:
                    card = primary_player.get_attachment_at_pos(planet, position, attachment_position)
                    if secondary_player.attach_card(card, planet_pos, unit_pos, not_own_attachment=True):
                        primary_player.remove_attachment_from_pos(planet, position, attachment_position)
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
    elif self.action_chosen == "Reanimation Protocol":
        if primary_player.get_number() == game_update_string[1]:
            if card_chosen.get_faction() == "Necrons" and card_chosen.get_is_unit():
                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                if not primary_player.harbinger_of_eternity_active:
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Slave-powered Wagons":
        og_pla, og_pos = self.position_of_actioned_card
        if og_pla == planet_pos or abs(og_pla - planet_pos) == 1:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Token":
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    og_pla, og_pos = self.position_of_actioned_card
                    player_owning_card.destroy_card_in_play(planet_pos, unit_pos)
                    if planet_pos == og_pla and game_update_string[1] == primary_player.get_number():
                        if og_pos > unit_pos:
                            og_pos = og_pos - 1
                    primary_player.increase_attack_of_unit_at_pos(og_pla, og_pos, 1, expiration="EOP")
                    primary_player.increase_health_of_unit_at_pos(og_pla, og_pos, 1, expiration="EOP")
                    primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "Preemptive Barrage":
        if game_update_string[1] == primary_player.get_number():
            if self.misc_target_planet == -1 or self.misc_target_planet == planet_pos:
                if card_chosen.get_faction() == "Astra Militarum":
                    card_chosen.ranged_eop = True
                    self.misc_target_planet = planet_pos
                    self.misc_counter -= 1
                    await self.send_update_message(str(self.misc_counter) + " uses left")
                    if self.misc_counter == 0:
                        self.action_cleanup()
    elif self.action_chosen == "Gauss Flayer":
        if secondary_player.get_number() == game_update_string[1]:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    secondary_player.cards_in_play[planet_pos + 1][unit_pos].negative_hp_until_eop += 2
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.position_of_actioned_card = (-1, -1)
                    self.position_of_selected_attachment = (-1, -1, -1)
                    self.action_cleanup()
    elif self.action_chosen == "Ambush":
        if not self.omega_ambush_active or self.infested_planets[planet_pos]:
            if self.card_type_of_selected_card_in_hand == "Attachment":
                await DeployPhase.deploy_card_routine_attachment(self, name, game_update_string, True)
    elif self.action_chosen == "Cenobyte Servitor":
        if self.chosen_first_card:
            card = primary_player.get_card_in_hand(primary_player.aiming_reticle_coords_hand)
            player_getting_attachment = self.p1
            if game_update_string[1] == "2":
                player_getting_attachment = self.p2
            not_own_attachment = False
            if player_getting_attachment.number != primary_player.number:
                not_own_attachment = True
            if player_getting_attachment.attach_card(card, planet_pos, unit_pos, not_own_attachment=not_own_attachment):
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Prey on the Weak":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Synapse":
                name_synapse = primary_player.get_name_given_pos(planet_pos, unit_pos)
                primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                self.choice_context = "Choose a new Synapse: (PotW)"
                self.choices_available = primary_player.synapse_list
                try:
                    self.choices_available.remove(name_synapse)
                except ValueError:
                    pass
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
    elif self.action_chosen == "Replicating Scarabs":
        if planet_pos == self.position_of_actioned_card[0]:
            if player_owning_card.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                    self.action_cleanup()
    elif self.action_chosen == "Korporal Snagbrat":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].actually_a_deepstrike:
                    self.chosen_first_card = True
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.misc_target_choice = "IN_PLAY"
                    self.misc_target_unit = (planet_pos, unit_pos)
    elif self.action_chosen == "Rotten Plaguebearers":
        if planet_pos == self.position_of_actioned_card[0]:
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
            if can_continue:
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1, shadow_field_possible=True,
                                                        rickety_warbuggy=True)
                if self.position_of_actioned_card != (-1, -1):
                    primary_player.reset_aiming_reticle_in_play(planet_pos, self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                self.action_cleanup()
    elif self.action_chosen == "Conjuring Warmaster":
        if game_update_string[1] == primary_player.number:
            if planet_pos != self.position_of_actioned_card[0]:
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                            if primary_player.move_unit_to_planet(
                                    planet_pos, unit_pos, self.position_of_actioned_card[0]):
                                last_element_index = len(
                                    primary_player.cards_in_play[self.position_of_actioned_card[0] + 1]) - 1
                                primary_player.exhaust_given_pos(self.position_of_actioned_card[0],
                                                                 last_element_index)
                                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                            self.position_of_actioned_card[1])
                                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                                self.action_cleanup()
    elif self.action_chosen == "Imperial Bastion":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        attachments = player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_attachments()
        magus_card = False
        for i in range(len(attachments)):
            if attachments[i].from_magus_harid:
                magus_card = True
        if magus_card:
            player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
            self.action_cleanup()
    elif self.action_chosen == "Indiscriminate Bombing":
        if self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if self.misc_target_planet == planet_pos:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                        if not self.chosen_second_card:
                            self.player_with_action = secondary_player.name_player
                            self.chosen_second_card = True
                        else:
                            self.action_cleanup()
    elif self.action_chosen == "Kraktoof Hall":
        if not self.chosen_first_card:
            if primary_player.get_number() == game_update_string[1]:
                if primary_player.get_damage_given_pos(planet_pos, unit_pos) > 0:
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                    self.position_of_actioned_card = (planet_pos, unit_pos)
                    self.chosen_first_card = True
                    self.misc_target_planet = planet_pos
        elif self.misc_target_planet == planet_pos:
            if game_update_string[1] == "1":
                player_owning_card = self.p1
            else:
                player_owning_card = self.p2
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
            if can_continue:
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1, can_shield=False, by_enemy_unit=False)
                self.chosen_second_card = True
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.action_cleanup()
    elif self.action_chosen == "Summary Execution":
        if primary_player.get_number() == game_update_string[1]:
            if self.misc_target_planet == planet_pos:
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    self.additional_icons_planets_eob[planet_pos].append("green")
                    primary_player.draw_card()
                    self.action_cleanup()
    elif self.action_chosen == "Ireful Vanguard":
        if self.position_of_actioned_card[0] == planet_pos:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 3, rickety_warbuggy=True)
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.action_cleanup()
    elif self.action_chosen == "Master Program":
        if primary_player.get_number() == game_update_string[1]:
            if not self.chosen_first_card:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                        "Drone", primary_player.etekh_trait):
                    if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                        self.chosen_first_card = True
            else:
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        can_continue = True
                        possible_interrupts = []
                        if player_owning_card.name_player == primary_player.name_player:
                            possible_interrupts = secondary_player.intercept_check()
                        if player_owning_card.name_player == secondary_player.name_player:
                            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                                planet_pos, unit_pos, intercept_possible=True)
                            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy card abilities.")
                        if possible_interrupts and can_continue:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "In Play Action"
                        if can_continue:
                            primary_player.ready_given_pos(planet_pos, unit_pos)
                            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
                            self.action_cleanup()
    elif self.action_chosen == "Hyperphase Sword":
        print("cool sword")
        if self.chosen_first_card:
            print("already discarded")
            origin_pla, origin_pos, origin_att = self.misc_target_attachment
            if origin_pla == planet_pos and origin_pos != unit_pos:
                print("ok planet and pos")
                if primary_player.move_attachment_card(origin_pla, origin_pos, origin_att,
                                                       planet_pos, unit_pos):
                    primary_player.reset_aiming_reticle_in_play(origin_pla, origin_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Breach and Clear":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if player_owning_card.get_ready_given_pos(planet_pos, unit_pos):
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    self.misc_target_planet = planet_pos
                    player_owning_card.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                    self.action_chosen = "Breach and Clear Sacrifice"
                    self.choices_available = ["Sacrifice", "Pass"]
                    self.choice_context = "BaC: Sacrifice Attachment?"
                    self.name_player_making_choices = primary_player.name_player
                    self.resolving_search_box = True
    elif self.action_chosen == "Sivarla Soulbinder":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Cultist"):
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.chosen_first_card = True
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
    elif self.action_chosen == "Reveal The Blade":
        if self.chosen_first_card:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                player_owning_card.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 2, expiration="NEXT")
                self.action_cleanup()
    elif self.action_chosen == "Everlasting Rage":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Khorne"):
                if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                    x_value = int(self.misc_target_choice)
                    damage_on_unit = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                    if damage_on_unit > 0:
                        damage_to_remove = min(damage_on_unit, x_value)
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage_to_remove, healing=True)
                        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, x_value,
                                                                      expiration="NEXT")
                        self.action_cleanup()
    elif self.action_chosen == "Plagueburst Crawler":
        if not player_owning_card.get_unique_given_pos(planet_pos, unit_pos):
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
            if can_continue:
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 2)
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                self.action_cleanup()
    elif self.action_chosen == "Lekor Blight-Tongue":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
            if can_continue:
                player_owning_card.cards_in_play[planet_pos + 1][unit_pos].infection_lekor += 1
                await self.send_update_message(player_owning_card.get_name_given_pos(planet_pos, unit_pos) +
                                               " gained an infection token!")
                if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].infection_lekor > 1:
                    player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 3)
                    player_owning_card.cards_in_play[planet_pos + 1][unit_pos].infection_lekor = 0
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                self.action_cleanup()
    elif self.action_chosen == "Forward Outpost":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Drone"):
                player_owning_card.cards_in_play[planet_pos + 1][unit_pos].sweep_next += 2
                self.action_cleanup()
    elif self.action_chosen == "Guerrilla Tactics Move":
        if game_update_string[1] == primary_player.number:
            if planet_pos == self.misc_target_planet:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Kroot"):
                        if planet_pos != self.round_number:
                            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.round_number)
                        self.action_cleanup()
    elif self.action_chosen == "Wraithbone Armour":
        if not self.chosen_first_card:
            if game_update_string[1] == secondary_player.get_number():
                zero_attack = False
                for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                    if primary_player.cards_in_play[planet_pos + 1][i].attack == 0:
                        zero_attack = True
                if zero_attack:
                    if secondary_player.get_damage_given_pos(planet_pos, unit_pos) > 0:
                        can_continue = True
                        possible_interrupts = []
                        if player_owning_card.name_player == primary_player.name_player:
                            possible_interrupts = secondary_player.intercept_check()
                        if player_owning_card.name_player == secondary_player.name_player:
                            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                                planet_pos, unit_pos, intercept_possible=True, event=True)
                            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy card abilities.")
                        if possible_interrupts and can_continue:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "In Play Action"
                        if can_continue:
                            self.misc_target_unit = (planet_pos, unit_pos)
                            secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.chosen_first_card = True
        else:
            if planet_pos == self.misc_target_unit[0]:
                og_pla, og_pos = self.misc_target_unit
                secondary_player.remove_damage_from_pos(og_pla, og_pos, 1)
                player_owning_card.resolve_moved_damage_to_pos(planet_pos, unit_pos, 1)
                secondary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                self.action_cleanup()
    elif self.action_chosen == "Breach and Clear 2":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if player_owning_card.get_ready_given_pos(planet_pos, unit_pos) and planet_pos == self.misc_target_planet:
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    self.misc_target_planet = planet_pos
                    player_owning_card.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                    self.action_cleanup()
    elif self.action_chosen == "Suppressive Fire":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                self.chosen_first_card = True
                self.misc_target_planet = planet_pos
        else:
            if planet_pos == self.misc_target_planet:
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                        player_owning_card.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                        self.chosen_second_card = True
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        self.action_cleanup()
                        self.misc_target_planet = -1
    elif self.action_chosen == "Castellan Crowe BLOODIED":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                og_pla, og_pos = self.position_of_actioned_card
                primary_player.increase_attack_of_unit_at_pos(og_pla, og_pos, 3, expiration="NEXT")
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                self.action_cleanup()
    elif self.action_chosen == "The Black Rage":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
                        primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
                        primary_player.increase_retaliate_given_pos_eop(planet_pos, unit_pos, 1)
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].sacrifice_end_of_phase = True
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.action_cleanup()
    elif self.action_chosen == "Call The Storm":
        if not self.chosen_first_card:
            if planet_pos == self.misc_target_planet:
                if game_update_string[1] == secondary_player.get_number():
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        can_continue = True
                        possible_interrupts = []
                        if player_owning_card.name_player == primary_player.name_player:
                            possible_interrupts = secondary_player.intercept_check()
                        if player_owning_card.name_player == secondary_player.name_player:
                            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                                planet_pos, unit_pos, intercept_possible=True, event=True)
                            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy card abilities.")
                        if possible_interrupts and can_continue:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "In Play Action"
                        if can_continue:
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.chosen_first_card = True
                            secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
    elif self.action_chosen == "Captain Markis":
        if planet_pos == self.position_of_actioned_card[0]:
            if not self.chosen_first_card:
                if primary_player.get_number() == game_update_string[1]:
                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_faction() == "Astra Militarum" \
                            and primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                        if self.position_of_actioned_card == (planet_pos, unit_pos):
                            self.position_of_actioned_card = (-1, -1)
                        elif self.position_of_actioned_card[1] > unit_pos:
                            self.position_of_actioned_card = (self.position_of_actioned_card[0],
                                                              self.position_of_actioned_card[1] - 1)
                        self.chosen_first_card = True
                        primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
            else:
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                        player_owning_card.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                        self.chosen_second_card = True
                        if self.position_of_actioned_card != (-1, -1):
                            primary_player.reset_aiming_reticle_in_play(planet_pos, self.position_of_actioned_card[1])
                        try:
                            self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        except:
                            pass
                        self.action_cleanup()
    elif self.action_chosen == "Awakening Cavern":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    primary_player.ready_given_pos(planet_pos, unit_pos)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.action_cleanup()
                    self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Dark Cunning":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    primary_player.ready_given_pos(planet_pos, unit_pos)
                    if self.infested_planets[planet_pos]:
                        primary_player.add_resources(1)
                    self.action_cleanup()
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Aun'shi's Sanctum":
        ethereal_present = False
        for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                    "Ethereal", primary_player.etekh_trait):
                ethereal_present = True
        if ethereal_present:
            primary_player.ready_given_pos(planet_pos, unit_pos)
            self.action_cleanup()
    elif self.action_chosen == "Saint Celestine":
        if self.chosen_first_card:
            if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                self.misc_counter = self.misc_counter - 1
                if self.misc_counter < 1:
                    card = primary_player.get_card_in_hand(primary_player.aiming_reticle_coords_hand)
                    del primary_player.cards[primary_player.aiming_reticle_coords_hand]
                    target_planet = self.position_of_actioned_card[0]
                    final_pos = primary_player.add_card_to_planet(card, target_planet)
                    if final_pos != -1:
                        primary_player.cards_in_play[target_planet + 1][final_pos].saint_celestine_active = True
                    primary_player.aiming_reticle_coords_hand = None
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0], self.position_of_actioned_card[1])
                    self.action_cleanup()
    elif self.action_chosen == "Omnissiah's Blessing":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Vehicle") or \
                    primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Tech-Priest"):
                if primary_player.get_has_faith_given_pos(planet_pos, unit_pos):
                    if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                        self.action_cleanup()
    elif self.action_chosen == "Rally the Charge":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                    if primary_player.check_for_warlord(planet_pos, True, primary_player.name_player):
                        can_continue = True
                        possible_interrupts = []
                        if player_owning_card.name_player == primary_player.name_player:
                            possible_interrupts = secondary_player.intercept_check()
                        if player_owning_card.name_player == secondary_player.name_player:
                            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                                planet_pos, unit_pos, intercept_possible=True, event=True)
                            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy card abilities.")
                            elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy events.")
                        if possible_interrupts and can_continue:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Event Action"
                        if can_continue:
                            command = 2 * primary_player.get_command_given_pos(planet_pos, unit_pos)
                            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos,
                                                                          command, expiration="EOP")
                            name_card = primary_player.get_name_given_pos(planet_pos, unit_pos)
                            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                            primary_player.aiming_reticle_coords_hand = None
                            await self.send_update_message(
                                name_card + " gained +" + str(command) + " ATK from Rally the Charge!"
                            )
                            self.action_cleanup()
    elif self.action_chosen == "Ethereal Wisdom":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Tau":
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Event Action"
                    if can_continue:
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].extra_traits_eop += "Ethereal"
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].extra_attack_until_end_of_phase += 1
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        self.action_cleanup()
    elif self.action_chosen == "Clogged with Corpses":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Termagant"):
                primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                self.misc_counter += 1
    elif self.action_chosen == "Ferocious Strength":
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Synapse" or \
                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Warlord":
                primary_player.cards_in_play[planet_pos + 1][unit_pos].brutal_eocr = True
                card_name = primary_player.cards_in_play[planet_pos + 1][unit_pos].get_name()
                await self.send_update_message("Made " + card_name + " Brutal for one combat round.")
                self.action_cleanup()
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Mob Up!":
        can_continue = True
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                if possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
            if can_continue:
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter, by_enemy_unit=False)
                self.action_cleanup()
    elif self.action_chosen == "Convincing Cutouts":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if not primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Warlord":
                    if not secondary_player.check_for_warlord(planet_pos):
                        primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                        self.action_cleanup()
    elif self.action_chosen == "Craftworld Gate":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    primary_player.return_card_to_hand(planet_pos, unit_pos)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.action_cleanup()
    elif self.action_chosen == "World Engine Beam":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                self.misc_target_unit = (planet_pos, unit_pos)
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                health_remaining = primary_player.get_health_given_pos(planet_pos, unit_pos)
                health_remaining = health_remaining - primary_player.get_damage_given_pos(planet_pos, unit_pos)
                self.choices_available = []
                for i in range(health_remaining):
                    self.choices_available.append(str(i + 1))
                self.choice_context = "Amount of damage (WEB)"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
    elif self.action_chosen == "Khymera Den":
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = int(game_update_string[2])
            unit_pos = int(game_update_string[3])
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_name() == "Khymera":
                self.khymera_to_move_positions.append((planet_pos, unit_pos))
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Shroud Cruiser":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.number:
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.chosen_first_card = True
                    self.misc_target_unit = (planet_pos, unit_pos)
    elif self.action_chosen == "Brutal Cunning":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.number:
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Orks":
                    if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                        dmg = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                        if dmg > 0:
                            if dmg == 1:
                                self.misc_counter = 1
                            primary_player.remove_damage_from_pos(planet_pos, unit_pos, self.misc_counter)
                            self.chosen_first_card = True
                            self.misc_target_planet = planet_pos
        elif planet_pos == self.misc_target_planet:
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not player_being_hit.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Event Action"
                    if can_continue:
                        damage = player_being_hit.get_damage_given_pos(planet_pos, unit_pos)
                        player_being_hit.set_damage_given_pos(planet_pos, unit_pos, damage + self.misc_counter)
                        self.action_cleanup()
    elif self.action_chosen == "Techmarine Aspirant":
        if game_update_string[1] == primary_player.number:
            if planet_pos == self.misc_target_planet and not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    og_pla, og_pos = self.position_of_actioned_card
                    techmarine_id = primary_player.cards_in_play[og_pla + 1][og_pos].card_id
                    if techmarine_id not in primary_player.cards_in_play[planet_pos + 1][unit_pos].used_techmarine_ids:
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].used_techmarine_ids.append(techmarine_id)
                        primary_player.spend_resources(1)
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                        if secondary_player.search_card_at_planet(og_pla, "The Mask of Jain Zar"):
                            self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                 (int(primary_player.number), planet_pos, unit_pos))
                        self.action_cleanup()
    elif self.action_chosen == "Clearcut Refuge":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
            can_continue = True
            if player_being_hit.name_player == secondary_player.name_player:
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = self.amount_spend_for_tzeentch_firestorm
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
            if can_continue:
                highest_cost = primary_player.get_highest_cost_units()
                player_being_hit.increase_health_of_unit_at_pos(planet_pos, unit_pos, highest_cost, expiration="EOP")
                name_unit = player_being_hit.get_name_given_pos(planet_pos, unit_pos)
                await self.send_update_message(name_unit + " gained +" + str(highest_cost) + " HP.")
                self.action_cleanup()
    elif self.action_chosen == "Dark Angels Cruiser":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.number:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].deepstrike != -1:
                    primary_player.set_damage_given_pos(planet_pos, unit_pos, 0)
                    primary_player.discard_attachments_from_card(planet_pos, unit_pos)
                    card = primary_player.cards_in_play[planet_pos + 1][unit_pos]
                    primary_player.cards_in_reserve[planet_pos].append(card)
                    primary_player.remove_card_from_play(planet_pos, unit_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Repent!":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.get_cost_given_pos(planet_pos, unit_pos) >= self.misc_counter:
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    if not self.chosen_first_card:
                        self.misc_target_unit = (planet_pos, unit_pos)
                        self.chosen_first_card = True
                        self.player_with_action = secondary_player.name_player
                        self.misc_counter = secondary_player.get_highest_cost_units()
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    else:
                        self.player_with_action = secondary_player.name_player
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        atk1 = primary_player.get_attack_given_pos(planet_pos, unit_pos)
                        other_pla, other_pos = self.misc_target_unit
                        atk2 = secondary_player.get_attack_given_pos(other_pla, other_pos)
                        secondary_player.exhaust_given_pos(other_pla, other_pos)
                        secondary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, atk2, by_enemy_unit=False)
                        secondary_player.assign_damage_to_pos(other_pla, other_pos, atk1, by_enemy_unit=False)
                        self.action_cleanup()
    elif self.action_chosen == "Kauyon Strike":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                    "Ethereal", primary_player.etekh_trait):
                self.khymera_to_move_positions.append((planet_pos, unit_pos))
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                self.chosen_first_card = True
    elif self.action_chosen == "Eldritch Lance":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if planet_pos == self.misc_target_planet:
            if player_being_hit.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                player_being_hit.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                self.action_cleanup()
    elif self.action_chosen == "Sudden Reinforcements":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Transport"):
                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                    primary_player.summon_token_at_planet("Guardsman", planet_pos)
                    primary_player.summon_token_at_planet("Guardsman", planet_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Unending Barrage":
        if primary_player.get_number() == game_update_string[1]:
            if not self.chosen_first_card:
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Artillery"):
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.misc_counter += 1
                        await self.send_update_message("Total artillery: " + str(self.misc_counter))
    elif self.action_chosen == "Lucky Shot":
        if player_owning_card.check_is_unit_at_pos(planet_pos, unit_pos):
            if player_owning_card.get_ranged_given_pos(planet_pos, unit_pos):
                player_owning_card.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                player_owning_card.cards_in_play[planet_pos + 1][unit_pos].armorbane_eop = True
                self.action_cleanup()
    elif self.action_chosen == "Ravenous Flesh Hounds":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                    "Cultist", primary_player.etekh_trait):
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    if planet_pos == self.position_of_actioned_card[0]:
                        if self.position_of_actioned_card[1] > unit_pos:
                            self.position_of_actioned_card = (planet_pos, self.position_of_actioned_card[1] - 1)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    primary_player.remove_damage_from_pos(self.position_of_actioned_card[0],
                                                          self.position_of_actioned_card[1], 999, healing=True)
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "Chaplain Mavros":
        if primary_player.get_number() == game_update_string[1]:
            if self.get_blue_icon(planet_pos):
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                    primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True,
                                                        by_enemy_unit=False)
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "Ancient Keeper of Secrets":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                    "Cultist", primary_player.etekh_trait):
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    if planet_pos == self.position_of_actioned_card[0]:
                        if self.position_of_actioned_card[1] > unit_pos:
                            self.position_of_actioned_card = (planet_pos, self.position_of_actioned_card[1] - 1)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    primary_player.ready_given_pos(self.position_of_actioned_card[0],
                                                   self.position_of_actioned_card[1])
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
                    self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "The Dawn Blade":
        if self.chosen_first_card:
            og_pla, og_pos = self.misc_target_unit
            if og_pla == planet_pos:
                card = primary_player.cards_in_reserve[og_pla][og_pos]
                if player_owning_card.attach_card(card, planet_pos, unit_pos):
                    del primary_player.cards_in_reserve[og_pla][og_pos]
                    self.action_cleanup()
    elif self.action_chosen == "Kommando Cunning":
        if not self.chosen_first_card:
            if primary_player.get_number() == game_update_string[1]:
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].actually_a_deepstrike:
                    actual_card_name = primary_player.cards_in_play[planet_pos + 1][unit_pos].deepstrike_card_name
                    actual_card = self.preloaded_find_card(actual_card_name)
                    if actual_card.get_card_type() == "Army":
                        primary_player.deepstrike_unit(planet_pos, unit_pos, in_play_card=True)
                        self.action_cleanup()
                    elif actual_card.get_card_type() == "Event":
                        primary_player.deepstrike_event(planet_pos, unit_pos, in_play_card=True)
                        self.action_cleanup()
                    elif actual_card.get_card_type() == "Attachment":
                        if actual_card.planet_attachment:
                            primary_player.add_attachment_to_planet(
                                planet_pos, actual_card)
                            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                            primary_player.deepstrike_attachment_extras(planet_pos)
                            self.action_cleanup()
                        else:
                            self.chosen_first_card = True
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.misc_target_choice = "IN_PLAY"
        else:
            og_pla, og_pos = self.misc_target_unit
            if og_pla == planet_pos:
                if self.misc_target_choice == "RESERVE":
                    card = primary_player.cards_in_reserve[og_pla][og_pos]
                    if player_owning_card.attach_card(card, planet_pos, unit_pos):
                        del primary_player.cards_in_reserve[og_pla][og_pos]
                        self.action_cleanup()
                else:
                    card_name = primary_player.cards_in_play[og_pla + 1][og_pos].deepstrike_card_name
                    card = self.preloaded_find_card(card_name)
                    if player_owning_card.attach_card(card, planet_pos, unit_pos):
                        del primary_player.cards_in_play[og_pla + 1][og_pos]
                        self.action_cleanup()
    elif self.action_chosen == "Soot-Blackened Axe":
        if planet_pos == self.misc_target_unit[0]:
            if not player_owning_card.get_unique_given_pos(planet_pos, unit_pos):
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                    elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    player_owning_card.resolve_moved_damage_to_pos(planet_pos, unit_pos, 1)
                    original_player = self.p1
                    if self.misc_target_choice == "2":
                        original_player = self.p2
                    original_player.remove_damage_from_pos(self.misc_target_unit[0], self.misc_target_unit[1], 1)
                    original_player.reset_aiming_reticle_in_play(self.misc_target_unit[0], self.misc_target_unit[1])
                    self.action_cleanup()
    elif self.action_chosen == "Painboy Surjery":
        if game_update_string[1] == primary_player.get_number():
            if self.misc_target_unit == (-1, -1) or self.misc_target_unit == (planet_pos, unit_pos):
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Orks":
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        if not primary_player.deck:
                            self.action_cleanup()
                        else:
                            card_name = primary_player.deck[0]
                            card = self.preloaded_find_card(card_name)
                            self.misc_target_unit = (planet_pos, unit_pos)
                            await self.send_update_message("Revealed a " + card.get_name())
                            if card.get_card_type() == "Attachment":
                                if not card.planet_attachment:
                                    if primary_player.attach_card(card, planet_pos, unit_pos):
                                        del primary_player.deck[0]
                                        primary_player.shuffle_deck()
                                        self.action_cleanup()
                                    else:
                                        primary_player.deck.append(primary_player.deck[0])
                                        del primary_player.deck[0]
                                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1,
                                                                            by_enemy_unit=False)
                                else:
                                    primary_player.deck.append(primary_player.deck[0])
                                    del primary_player.deck[0]
                                    primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                            else:
                                primary_player.deck.append(primary_player.deck[0])
                                del primary_player.deck[0]
                                primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
    elif self.action_chosen == "Evangelizing Ships":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                    await self.send_update_message("Faith paid, please continue.")
                    self.chosen_first_card = True
                    self.chosen_second_card = False
    elif self.action_chosen == "Squadron Redeployment":
        if self.unit_to_move_position == [-1, -1]:
            if game_update_string[1] == primary_player.get_number():
                planet_pos = int(game_update_string[2])
                unit_pos = int(game_update_string[3])
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments():
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.unit_to_move_position = [planet_pos, unit_pos]
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        else:
            await self.send_update_message("Already selected unit to move")
    elif self.action_chosen == "Starblaze's Outpost":
        if game_update_string[1] == primary_player.get_number():
            if not self.chosen_first_card:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum":
                        cost = primary_player.cards_in_play[planet_pos + 1][unit_pos].get_cost()
                        primary_player.return_card_to_hand(planet_pos, unit_pos)
                        self.chosen_first_card = True
                        self.misc_counter = cost
                        self.misc_target_planet = planet_pos
    elif self.action_chosen == "Brood Chamber":
        if not self.chosen_first_card:
            if secondary_player.get_number() == game_update_string[1]:
                choices = secondary_player.get_keywords_given_pos(planet_pos, unit_pos)
                if choices:
                    self.misc_target_planet = planet_pos
                    if len(choices) == 1:
                        self.misc_target_choice = choices[0]
                        await self.send_update_message(
                            "Only one keyword: skipping asking which one to take."
                        )
                    else:
                        self.choices_available = choices
                        self.name_player_making_choices = primary_player.name_player
                        self.choice_context = "Keyword copied from Brood Chamber"
                    self.chosen_first_card = True
                else:
                    await self.send_update_message(
                        "Target has no keywords to copy."
                    )
        else:
            if primary_player.get_number() == game_update_string[1]:
                if planet_pos == self.misc_target_planet:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if self.misc_target_choice == "Brutal":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].brutal_eop = True
                        if self.misc_target_choice == "Armorbane":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].armorbane_eop = True
                        if self.misc_target_choice == "Flying":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].flying_eop = True
                        if self.misc_target_choice == "Mobile":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].mobile_eop = True
                        if self.misc_target_choice == "Ranged":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].ranged_eop = True
                        if self.misc_target_choice == "Area Effect":
                            primary_player.cards_in_play[planet_pos + 1][unit_pos].area_effect_eop = \
                                self.stored_area_effect_value
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                        if self.misc_target_choice == "Area Effect":
                            self.misc_target_choice += " (" + str(self.stored_area_effect_value) + ")"
                        await self.send_update_message(
                            name + " gained " + self.misc_target_choice + "."
                        )
                        self.action_cleanup()
                        self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "The Wolf Within":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Space Wolves"):
                if (planet_pos, unit_pos) != self.misc_target_unit:
                    self.misc_target_unit = (planet_pos, unit_pos)
                    primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                    primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                    await self.send_update_message(primary_player.get_name_given_pos(planet_pos, unit_pos) +
                                                   " gained +1 ATK and +1 HP!")
                    self.misc_counter = self.misc_counter + 1
                    warlord_count = 0
                    for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                        if primary_player.get_card_type_given_pos(planet_pos, i) == "Warlord" or \
                                primary_player.name_player in \
                                primary_player.cards_in_play[planet_pos + 1][i].hit_by_frenzied_wulfen_names:
                            warlord_count += 1
                    for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                        if secondary_player.get_card_type_given_pos(planet_pos, i) == "Warlord" or \
                                primary_player.name_player in \
                                secondary_player.cards_in_play[planet_pos + 1][i].hit_by_frenzied_wulfen_names:
                            warlord_count += 1
                    if warlord_count > 1:
                        self.misc_counter_2 += 1
                    if self.misc_counter > 1:
                        if self.misc_counter_2 > 1:
                            primary_player.add_resources(1)
                        self.action_cleanup()
    elif self.action_chosen == "Pinning Razorback":
        if self.position_of_actioned_card[0] == planet_pos:
            if secondary_player.number == game_update_string[1]:
                if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.reactions_needing_resolving[0]
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        secondary_player.cards_in_play[planet_pos + 1][unit_pos].cannot_be_declared_as_attacker = True
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
    elif self.action_chosen == "Mycetic Spores":
        if self.unit_to_move_position == [-1, -1]:
            if self.player_with_action == self.name_1:
                primary_player = self.p1
            else:
                primary_player = self.p2
            if game_update_string[1] == primary_player.get_number():
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].has_hive_mind:
                    self.unit_to_move_position = [planet_pos, unit_pos]
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Rapid Assault":
        if self.chosen_second_card:
            if self.misc_target_planet == planet_pos:
                if game_update_string[1] == primary_player.number:
                    if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Kabalite"):
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        self.misc_counter += 1
                        if self.misc_counter > 1:
                            await primary_player.dark_eldar_event_played()
                            self.action_cleanup()
                        else:
                            await self.send_update_message(str(self.misc_counter) + " uses left of Rapid Assault")
    elif self.action_chosen == "Holy Chapel":
        if player_owning_card.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum" or \
                player_owning_card.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                player_owning_card.increase_faith_given_pos(planet_pos, unit_pos, 1)
                self.misc_counter = self.misc_counter - 1
                if self.misc_counter < 1:
                    self.action_cleanup()
                    await self.send_update_message("Completed Holy Chapel")
                else:
                    await self.send_update_message(str(self.misc_counter) + " targets left for Holy Chapel")
    elif self.action_chosen == "Move Psyker":
        if not self.chosen_first_card:
            if primary_player.number == game_update_string[1]:
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Psyker"):
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.misc_target_unit = (planet_pos, unit_pos)
                        self.chosen_first_card = True
    elif self.action_chosen == "Consumed by the Kindred":
        if game_update_string[1] == primary_player.get_number():
            if not self.chosen_first_card:
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Kroot"):
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
            else:
                if not primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Vehicle"):
                    if (planet_pos, unit_pos) != self.misc_target_unit:
                        cost = primary_player.get_cost_given_pos(planet_pos, unit_pos)
                        if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                            primary_player.add_resources(cost)
                            self.action_cleanup()
    elif self.action_chosen == "+1 ATK Warrior":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Warrior"):
                primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                self.action_cleanup()
    elif self.action_chosen == "Indescribable Horror":
        if game_update_string[1] == "1":
            player_being_routed = self.p1
        else:
            player_being_routed = self.p2
        unit_count = primary_player.count_tyranid_units_at_planet(planet_pos)
        unit_cost = player_being_routed.cards_in_play[planet_pos + 1][unit_pos].get_cost()
        can_continue = True
        if player_being_routed.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Army":
            can_continue = False
        elif unit_count < unit_cost:
            can_continue = False
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True, event=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
            elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy events.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = self.action_chosen
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "Event Action"
        if can_continue:
            if not player_being_routed.cards_in_play[planet_pos + 1][unit_pos].get_unique():
                player_being_routed.rout_unit(planet_pos, unit_pos)
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Attuned Gyrinx":
        if abs(self.position_of_actioned_card[0] - planet_pos) == 1:
            if self.misc_target_unit[0] != planet_pos:
                if game_update_string[1] == primary_player.number:
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        self.misc_target_unit = (planet_pos, unit_pos)
                        self.misc_counter += 1
                        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                        primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                        await self.send_update_message(primary_player.get_name_given_pos(planet_pos, unit_pos) +
                                                       " gained +1 ATK and +1 HP!")
                        if self.misc_counter > 1:
                            self.action_cleanup()
    elif self.action_chosen == "The Emperor's Warrant":
        if not self.chosen_first_card:
            if not secondary_player.check_for_warlord(planet_pos):
                if game_update_string[1] == secondary_player.number:
                    if secondary_player.get_ready_given_pos(planet_pos, unit_pos):
                        can_continue = True
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Event Action"
                        if can_continue:
                            secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                            self.misc_counter = secondary_player.get_attack_given_pos(planet_pos, unit_pos)
                            self.misc_target_planet = planet_pos
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.chosen_first_card = True
        elif self.misc_target_planet == planet_pos:
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            can_continue = True
            if secondary_player.get_number() == game_update_string[1]:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos, event=True)
                if planet_pos == self.misc_target_unit[0] and unit_pos == self.misc_target_unit[1]:
                    can_continue = False
                    await self.send_update_message("Can't hit itself.")
                elif secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 2
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
            if can_continue:
                primary_player.discard_card_name_from_hand("The Emperor's Warrant")
                player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter, by_enemy_unit=False)
                self.action_cleanup()
    elif self.action_chosen == "Archon's Terror":
        if game_update_string[1] == "1":
            player_being_routed = self.p1
        else:
            player_being_routed = self.p2
        if not player_being_routed.cards_in_play[planet_pos + 1][unit_pos].get_unique():
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
            if can_continue:
                if not player_being_routed.cards_in_play[planet_pos + 1][unit_pos].get_unique():
                    player_being_routed.rout_unit(planet_pos, unit_pos)
                    self.action_cleanup()
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    await primary_player.dark_eldar_event_played()
    elif self.action_chosen == "Big Mek Kagdrak":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                self.misc_target_unit = (planet_pos, unit_pos)
                self.misc_target_player = player_owning_card.name_player
                self.choices_available = ["Flying", "Armorbane", "Brutal",
                                          "Area Effect (1)", "Sweep (2)", "Retaliate (3)"]
                if primary_player.last_kagrak_trait in self.choices_available:
                    self.choices_available.remove(primary_player.last_kagrak_trait)
                self.choice_context = "Big Mek Kagdrak Keyword"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
    elif self.action_chosen == "Big Mek Kagdrak BLOODIED":
        if self.position_of_actioned_card[0] == planet_pos:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.misc_target_player = player_owning_card.name_player
                    self.choices_available = ["Flying", "Armorbane", "Brutal",
                                              "Area Effect (1)", "Sweep (2)", "Retaliate (3)"]
                    if primary_player.last_kagrak_trait in self.choices_available:
                        self.choices_available.remove(primary_player.last_kagrak_trait)
                    self.choice_context = "Big Mek Kagdrak Keyword"
                    self.name_player_making_choices = primary_player.name_player
                    self.resolving_search_box = True
    elif self.action_chosen == "Drivin' Ambishun'":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if self.misc_target_planet == planet_pos:
                can_continue = True
                possible_interrupts = []
                if player_owning_card.name_player == primary_player.name_player:
                    possible_interrupts = secondary_player.intercept_check()
                if player_owning_card.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        planet_pos, unit_pos, intercept_possible=True, event=True)
                    if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy card abilities.")
                if possible_interrupts and can_continue:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
                if can_continue:
                    health_gained = len(primary_player.get_keywords_given_pos(planet_pos, unit_pos, False))
                    primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, health_gained, expiration="EOR")
                    await self.send_update_message(primary_player.get_name_given_pos(planet_pos, unit_pos) +
                                                   " gained +" + str(health_gained) + " HP!")
                    self.action_cleanup()
    elif self.action_chosen == "The Emperor's Champion":
        if game_update_string[1] == secondary_player.get_number() and planet_pos == self.position_of_actioned_card[0]:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if secondary_player.get_ready_given_pos(planet_pos, unit_pos):
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        secondary_player.cards_in_play[planet_pos + 1][unit_pos].emperor_champion_active = True
                        primary_player.reset_aiming_reticle_in_play(planet_pos, self.position_of_actioned_card[1])
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
    elif self.action_chosen == "Teleportarium":
        if primary_player.get_number() == game_update_string[1]:
            if not self.chosen_first_card:
                if self.get_blue_icon(planet_pos):
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if primary_player.get_cost_given_pos(planet_pos, unit_pos) < 4:
                            if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                                self.chosen_first_card = True
                                self.misc_target_unit = (planet_pos, unit_pos)
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Corrupted Teleportarium":
        if primary_player.get_number() == game_update_string[1]:
            if not self.chosen_first_card:
                if self.get_blue_icon(planet_pos):
                    if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Despise":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                    "Ally", primary_player.etekh_trait):
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    self.player_with_action = secondary_player.name_player
                    primary_player.sacced_card_for_despise = True
                    if primary_player.sacced_card_for_despise and secondary_player.sacced_card_for_despise:
                        self.action_cleanup()
                        await secondary_player.dark_eldar_event_played()
    elif self.action_chosen == "Zarathur's Flamers":
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = self.action_chosen
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "In Play Action"
        if can_continue:
            if planet_pos == self.position_of_actioned_card[0]:
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 2, shadow_field_possible=True,
                                                        rickety_warbuggy=True)
                self.action_cleanup()
    elif self.action_chosen == "Inevitable Betrayal":
        if secondary_player.number == game_update_string[1]:
            if self.misc_target_planet == -1 or self.misc_target_planet == planet_pos:
                if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if secondary_player.get_damage_given_pos(planet_pos, unit_pos) == 0:
                        secondary_player.set_blanked_given_pos(planet_pos, unit_pos)
                        secondary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                        self.misc_target_planet = planet_pos
    elif self.action_chosen == "Hunting Grounds":
        if game_update_string[1] == primary_player.number:
            if not self.chosen_first_card:
                if primary_player.get_name_given_pos(planet_pos, unit_pos) == "Khymera":
                    if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                        self.chosen_first_card = True
            else:
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Creature"):
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                            primary_player.ready_given_pos(planet_pos, unit_pos)
                            self.action_cleanup()
    elif self.action_chosen == "Mind War":
        psyker_present = False
        for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
            if primary_player.check_for_trait_given_pos(planet_pos, i, "Psyker") and \
                    primary_player.get_card_type_given_pos(planet_pos, i) == "Army":
                psyker_present = True
        if psyker_present:
            if game_update_string[1] == "1":
                player_returning = self.p1
            else:
                player_returning = self.p2
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
            if can_continue:
                card = player_returning.cards_in_play[planet_pos + 1][unit_pos]
                if card.get_card_type() == "Army":
                    if not card.check_for_a_trait("Elite"):
                        player_owning_card.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        self.action_cleanup()
    elif self.action_chosen == "Deception":
        if game_update_string[1] == "1":
            player_returning = self.p1
        else:
            player_returning = self.p2
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True, event=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
            elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy events.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = self.action_chosen
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "Event Action"
        if can_continue:
            card = player_returning.cards_in_play[planet_pos + 1][unit_pos]
            if card.get_card_type() == "Army":
                if not card.check_for_a_trait("Elite"):
                    player_returning.return_card_to_hand(planet_pos, unit_pos)
                    primary_player.aiming_reticle_color = None
                    primary_player.aiming_reticle_coords_hand = None
                    primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                    self.card_pos_to_deploy = -1
                    self.action_cleanup()
    elif self.action_chosen == "Noble Deed":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum":
                    attack_value = primary_player.cards_in_play[planet_pos + 1][unit_pos].attack
                    if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                        self.chosen_first_card = True
                        self.misc_counter = attack_value
                        self.misc_target_planet = planet_pos
        else:
            if game_update_string[1] == secondary_player.get_number():
                if self.misc_target_planet == planet_pos:
                    if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        can_continue = True
                        possible_interrupts = []
                        if player_owning_card.name_player == primary_player.name_player:
                            possible_interrupts = secondary_player.intercept_check()
                        if player_owning_card.name_player == secondary_player.name_player:
                            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                                planet_pos, unit_pos, intercept_possible=True, event=True)
                            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy card abilities.")
                            elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy events.")
                        if possible_interrupts and can_continue:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Event Action"
                        if can_continue:
                            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter,
                                                                  by_enemy_unit=False)
                            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                            primary_player.aiming_reticle_coords_hand = None
                            self.action_cleanup()
    elif self.action_chosen == "Smash 'n Bash":
        if self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if self.misc_target_planet == planet_pos:
                    primary_player.ready_given_pos(planet_pos, unit_pos)
                    self.misc_counter -= 1
                    await self.send_update_message(str(self.misc_counter) + " uses of Smash 'n Bash left")
                    if self.misc_counter < 1:
                        self.action_cleanup()
    elif self.action_chosen == "Seer's Exodus":
        if game_update_string[1] == primary_player.get_number():
            if planet_pos == self.misc_target_planet:
                primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
    elif self.action_chosen == "Lethal Toxin Sacs":
        if game_update_string[1] == primary_player.get_number():
            card = FindCard.find_card("Lethal Toxin Sacs", self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            played_card = primary_player. \
                play_attachment_card_to_in_play(card, planet_pos, unit_pos, army_unit_as_attachment=False, discounts=0)
            if played_card:
                primary_player.discard.remove("Lethal Toxin Sacs")
                primary_player.aiming_reticle_coords_discard = None
                self.action_cleanup()
    elif self.action_chosen == "Sudden Adaptation":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Tyranids":
                        self.misc_counter = primary_player.get_cost_given_pos(planet_pos, unit_pos)
                        self.misc_target_planet = planet_pos
                        self.misc_target_choice = primary_player.get_name_given_pos(planet_pos, unit_pos)
                        primary_player.return_card_to_hand(planet_pos, unit_pos)
                        self.chosen_first_card = True
    elif self.action_chosen == "Cathedral of Saint Camila":
        if secondary_player.get_number() == game_update_string[1]:
            if self.misc_counter[planet_pos]:
                if secondary_player.get_card_type_given_pos(planet_pos, unit_pos):
                    if not secondary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                        can_continue = True
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(planet_pos, unit_pos)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "In Play Action"
                        if can_continue:
                            self.misc_counter[planet_pos] = False
                            secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
    elif self.action_chosen == "Webway Passage":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not self.chosen_first_card:
                    self.misc_target_unit = (planet_pos, unit_pos)
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.chosen_first_card = True
                else:
                    other_pla, other_pos = self.misc_target_unit
                    primary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                    if other_pla != planet_pos:
                        card1 = primary_player.get_card_given_pos(planet_pos, unit_pos)
                        card2 = primary_player.get_card_given_pos(other_pla, other_pos)
                        if other_pla == -2:
                            primary_player.headquarters.append(copy.deepcopy(card1))
                        else:
                            primary_player.cards_in_play[other_pla + 1].append(copy.deepcopy(card1))
                        if planet_pos == -2:
                            primary_player.headquarters.append(copy.deepcopy(card2))
                        else:
                            primary_player.cards_in_play[planet_pos + 1].append(copy.deepcopy(card2))
                        if planet_pos == -2:
                            del primary_player.headquarters[unit_pos]
                        else:
                            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                        if other_pla == -2:
                            del primary_player.headquarters[other_pos]
                        else:
                            del primary_player.cards_in_play[other_pla + 1][other_pos]
                    self.action_cleanup()
    elif self.action_chosen == "Lost in the Webway Harlequin":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Harlequin"):
                if not self.chosen_first_card:
                    self.misc_target_unit = (planet_pos, unit_pos)
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.chosen_first_card = True
                else:
                    other_pla, other_pos = self.misc_target_unit
                    primary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                    if other_pla != planet_pos:
                        card1 = primary_player.get_card_given_pos(planet_pos, unit_pos)
                        card2 = primary_player.get_card_given_pos(other_pla, other_pos)
                        if other_pla == -2:
                            primary_player.headquarters.append(copy.deepcopy(card1))
                        else:
                            primary_player.cards_in_play[other_pla + 1].append(copy.deepcopy(card1))
                        if planet_pos == -2:
                            primary_player.headquarters.append(copy.deepcopy(card2))
                        else:
                            primary_player.cards_in_play[planet_pos + 1].append(copy.deepcopy(card2))
                        if planet_pos == -2:
                            del primary_player.headquarters[unit_pos]
                        else:
                            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                        if other_pla == -2:
                            del primary_player.headquarters[other_pos]
                        else:
                            del primary_player.cards_in_play[other_pla + 1][other_pos]
                    self.action_cleanup()
    elif self.action_chosen == "Lost in the Webway Opponent":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not self.chosen_first_card:
                    self.misc_target_unit = (planet_pos, unit_pos)
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.chosen_first_card = True
                else:
                    other_pla, other_pos = self.misc_target_unit
                    primary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                    if other_pla != planet_pos:
                        card1 = primary_player.get_card_given_pos(planet_pos, unit_pos)
                        card2 = primary_player.get_card_given_pos(other_pla, other_pos)
                        if other_pla == -2:
                            primary_player.headquarters.append(copy.deepcopy(card1))
                        else:
                            primary_player.cards_in_play[other_pla + 1].append(copy.deepcopy(card1))
                        if planet_pos == -2:
                            primary_player.headquarters.append(copy.deepcopy(card2))
                        else:
                            primary_player.cards_in_play[planet_pos + 1].append(copy.deepcopy(card2))
                        if planet_pos == -2:
                            del primary_player.headquarters[unit_pos]
                        else:
                            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                        if other_pla == -2:
                            del primary_player.headquarters[other_pos]
                        else:
                            del primary_player.cards_in_play[other_pla + 1][other_pos]
                    self.action_cleanup()
    elif self.action_chosen == "Hallucinogen Grenade":
        if secondary_player.get_number() == game_update_string[1]:
            if planet_pos == self.misc_target_planet:
                if not secondary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    if secondary_player.get_ready_given_pos(planet_pos, unit_pos):
                        can_continue = True
                        possible_interrupts = []
                        if player_owning_card.name_player == primary_player.name_player:
                            possible_interrupts = secondary_player.intercept_check()
                        if player_owning_card.name_player == secondary_player.name_player:
                            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                                planet_pos, unit_pos, intercept_possible=True)
                            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                can_continue = False
                                await self.send_update_message("Immune to enemy card abilities.")
                        if possible_interrupts and can_continue:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "In Play Action"
                        if can_continue:
                            secondary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                            atk = secondary_player.cards_in_play[planet_pos + 1][unit_pos].attack
                            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, atk, by_enemy_unit=False)
                            self.action_cleanup()
    elif self.action_chosen == "Eldritch Storm":
        if secondary_player.get_number() == game_update_string[1]:
            if self.misc_counter[planet_pos]:
                if secondary_player.get_card_type_given_pos(planet_pos, unit_pos):
                    if not secondary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                        can_continue = True
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, event=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                        elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos, power=True):
                            can_continue = False
                            await self.send_update_message("Immune to enemy events.")
                        elif possible_interrupts:
                            can_continue = False
                            await self.send_update_message("Some sort of interrupt may be used.")
                            self.choices_available = possible_interrupts
                            self.choices_available.insert(0, "No Interrupt")
                            self.name_player_making_choices = secondary_player.name_player
                            self.choice_context = "Interrupt Effect?"
                            self.nullified_card_name = self.action_chosen
                            self.cost_card_nullified = 0
                            self.nullify_string = "/".join(game_update_string)
                            self.first_player_nullified = primary_player.name_player
                            self.nullify_context = "Event Action"
                        if can_continue:
                            self.misc_counter[planet_pos] = False
                            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, by_enemy_unit=False)
    elif self.action_chosen == "Seekers of Slaanesh":
        if self.misc_target_planet == planet_pos:
            if game_update_string[1] == primary_player.number:
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Cultist"):
                    if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                        pla, pos = self.position_of_actioned_card
                        if pos > unit_pos:
                            pos = pos - 1
                        primary_player.reset_aiming_reticle_in_play(pla, pos)
                        primary_player.draw_card()
                        self.position_of_actioned_card = (pla, pos)
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
    elif self.action_chosen == "Ambush Platform":
        if game_update_string[1] == "1":
            player_receiving_attachment = self.p1
        else:
            player_receiving_attachment = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is not None:
            hand_pos = primary_player.aiming_reticle_coords_hand_2
            card = FindCard.find_card(primary_player.cards[hand_pos], self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            army_unit_as_attachment = False
            discounts = primary_player.search_hq_for_discounts("", "",
                                                               is_attachment=True)
            if card.get_ability() == "Gun Drones" or \
                    card.get_ability() == "Shadowsun's Stealth Cadre" or \
                    card.get_ability() == "Escort Drone":
                army_unit_as_attachment = True
            if primary_player.get_number() == player_receiving_attachment.get_number():
                print("Playing own card")
                played_card = primary_player. \
                    play_attachment_card_to_in_play(card, planet_pos, unit_pos,
                                                    army_unit_as_attachment=
                                                    army_unit_as_attachment,
                                                    discounts=discounts)
                enemy_card = False
            else:
                played_card = False
                if primary_player.spend_resources(int(card.get_cost()) - discounts):
                    played_card = player_receiving_attachment.play_attachment_card_to_in_play(
                        card, planet_pos, unit_pos, not_own_attachment=True,
                        army_unit_as_attachment=army_unit_as_attachment)
                    if not played_card:
                        primary_player.add_resources(int(card.get_cost()) - discounts, refund=True)
                enemy_card = True
            if played_card:
                if card.get_limited():
                    primary_player.can_play_limited = False
                primary_player.remove_card_from_hand(hand_pos)
                print("Succeeded (?) in playing attachment")
                primary_player.aiming_reticle_coords_hand_2 = None
                primary_player.reset_aiming_reticle_in_play(
                    self.position_of_actioned_card[0],
                    self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Hallow Librarium":
        if game_update_string[1] == "1":
            player_receiving_buff = self.p1
        else:
            player_receiving_buff = self.p2
        can_continue = True
        if not secondary_player.check_for_warlord(planet_pos):
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
            if can_continue:
                player_receiving_buff.increase_attack_of_unit_at_pos(planet_pos, unit_pos, -2,
                                                                     expiration="EOP")
                await self.send_update_message(
                    "Hallow Librarium used on " + player_receiving_buff.cards_in_play[int(game_update_string[2]) + 1]
                    [int(game_update_string[3])].get_name() + ", located at planet " + game_update_string[2] +
                    ", position " + game_update_string[3])
                self.position_of_actioned_card = (-1, -1)
                self.action_cleanup()
    elif self.action_chosen == "Squiggify":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if not player_being_hit.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait(
                "Vehicle", player_being_hit.etekh_trait) and \
                player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
            if possible_interrupts and can_continue:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
            if can_continue:
                player_being_hit.cards_in_play[planet_pos + 1][unit_pos].extra_traits_eop += "Squig"
                player_being_hit.set_blanked_given_pos(planet_pos, unit_pos)
                player_being_hit.cards_in_play[planet_pos + 1][unit_pos].attack_set_eop = 1
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                name_card = player_being_hit.get_name_given_pos(planet_pos, unit_pos)
                await self.send_update_message(
                    name_card + " got Squiggified!"
                )
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Catachan Outpost":
        if game_update_string[1] == "1":
            player_receiving_buff = self.p1
        else:
            player_receiving_buff = self.p2
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = self.action_chosen
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "In Play Action"
        if can_continue:
            player_receiving_buff.increase_attack_of_unit_at_pos(int(game_update_string[2]),
                                                                 int(game_update_string[3]), 2,
                                                                 expiration="NEXT")
            await self.send_update_message(
                "Catachan Outpost used on " + player_receiving_buff.cards_in_play[int(game_update_string[2]) + 1]
                [int(game_update_string[3])].get_name() + ", located at planet " + game_update_string[2] +
                ", position " + game_update_string[3])
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            self.position_of_actioned_card = (-1, -1)
            self.action_cleanup()
    elif self.action_chosen == "Tellyporta Pad":
        if game_update_string[1] == primary_player.get_number():
            card = primary_player.cards_in_play[planet_pos + 1][unit_pos]
            if card.get_faction() == "Orks":
                if card.get_is_unit():
                    can_continue = True
                    possible_interrupts = []
                    if player_owning_card.name_player == primary_player.name_player:
                        possible_interrupts = secondary_player.intercept_check()
                    if player_owning_card.name_player == secondary_player.name_player:
                        possible_interrupts = secondary_player.interrupt_cancel_target_check(
                            planet_pos, unit_pos, intercept_possible=True)
                        if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                            can_continue = False
                            await self.send_update_message("Immune to enemy card abilities.")
                    if possible_interrupts and can_continue:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "In Play Action"
                    if can_continue:
                        primary_player.move_unit_to_planet(planet_pos, unit_pos,
                                                           self.round_number)
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.action_cleanup()
