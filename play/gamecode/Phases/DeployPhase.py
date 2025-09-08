import copy
from . import CombatPhase


async def update_game_event_deploy_section(self, name, game_update_string):
    print("Need to run deploy turn code.")
    print(self.player_with_deploy_turn, self.number_with_deploy_turn)
    print(name == self.player_with_deploy_turn)
    if self.herald_of_the_waagh_active:
        await CombatPhase.update_game_event_combat_section(self, name, game_update_string)
    elif self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif len(game_update_string) == 1:
        if game_update_string[0] == "action-button":
            if self.get_actions_allowed() and not self.paying_shrieking_exarch_cost:
                print("Need to run action code")
                if self.player_with_deploy_turn == name:
                    self.stored_mode = self.mode
                    self.mode = "ACTION"
                    self.player_with_action = name
                    print("Special deploy action")
                    await self.send_update_message(name + " wants to take an action.")
                    if self.player_with_action == self.name_1 and self.p1.dark_possession_active:
                        self.choices_available = ["Dark Possession", "Regular Action"]
                        self.choice_context = "Use Dark Possession?"
                        self.name_player_making_choices = self.player_with_action
                    elif self.player_with_action == self.name_2 and self.p2.dark_possession_active:
                        self.choices_available = ["Dark Possession", "Regular Action"]
                        self.choice_context = "Use Dark Possession?"
                        self.name_player_making_choices = self.player_with_action
        elif game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
            print("Need to pass")
            continue_to_warlord = True
            if name == self.player_with_deploy_turn:
                if self.mode == "ACTION":
                    self.mode = self.stored_mode
                    self.stored_mode = ""
                    await self.send_update_message(name + " cancelled their action request.")
                elif self.mode == "Normal":
                    if self.paying_shrieking_exarch_cost:
                        await self.send_update_message("Cancelling cards payment for Shrieking Exarch")
                        self.paying_shrieking_exarch_cost = False
                        self.card_pos_to_deploy = -1
                        self.p1.aiming_reticle_coords_hand = None
                        self.p2.aiming_reticle_coords_hand = None
                    elif self.number_with_deploy_turn == "1":
                        self.number_with_deploy_turn = "2"
                        self.player_with_deploy_turn = self.name_2
                        self.p1.has_passed = True
                        self.discounts_applied = 0
                        self.available_discounts = 0
                        if self.p2.search_hand_for_card("The Emperor's Retribution"):
                            self.create_reaction("The Emperor's Retribution", self.name_2, (2, -1, -1))
                        if self.p2.search_hand_for_card("Shadow Hunt"):
                            self.create_reaction("Shadow Hunt", self.name_2, (2, -1, -1))
                        await self.send_update_message(self.name_1 + " passes their deploy turn.")
                    else:
                        self.number_with_deploy_turn = "1"
                        self.player_with_deploy_turn = self.name_1
                        self.p2.has_passed = True
                        self.discounts_applied = 0
                        self.available_discounts = 0
                        if self.p1.search_hand_for_card("The Emperor's Retribution"):
                            self.create_reaction("The Emperor's Retribution", self.name_1, (1, -1, -1))
                        if self.p1.search_hand_for_card("Shadow Hunt"):
                            self.create_reaction("Shadow Hunt", self.name_1, (1, -1, -1))
                        await self.send_update_message(self.name_2 + " passes their deploy turn.")
                elif self.mode == "DISCOUNT":
                    print("Play card with not all discounts")
                    await deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                              discounts=self.discounts_applied)
            if self.p1.has_passed and self.p2.has_passed:
                if self.p1.search_hand_for_card("Aerial Deployment"):
                    continue_to_warlord = False
                    self.reactions_on_end_deploy_phase = True
                    self.create_reaction("Aerial Deployment", self.name_1, (1, -1, -1))
                if self.p2.search_hand_for_card("Aerial Deployment"):
                    continue_to_warlord = False
                    self.reactions_on_end_deploy_phase = True
                    self.create_reaction("Aerial Deployment", self.name_2, (1, -1, -1))
                if continue_to_warlord:
                    await self.send_update_message("Both passed, move to warlord movement.")
                    await self.change_phase("COMMAND")
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HAND":
            if self.mode == "Normal":
                if name == self.player_with_deploy_turn:
                    print(game_update_string[1] == self.number_with_deploy_turn)
                    if game_update_string[1] == self.number_with_deploy_turn:
                        print("Deploy card in hand at pos", game_update_string[2])
                        self.deepstrike_deployment_active = False
                        previous_card_pos_to_deploy = self.card_pos_to_deploy
                        self.card_pos_to_deploy = int(game_update_string[2])
                        if self.number_with_deploy_turn == "1":
                            primary_player = self.p1
                            secondary_player = self.p2
                        else:
                            primary_player = self.p2
                            secondary_player = self.p1
                        card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
                        has_deepstrike = card.get_has_deepstrike()
                        if card.get_card_type() == "Attachment" and primary_player.farsight_relevant:
                            has_deepstrike = True
                        self.faction_of_card_to_play = card.get_faction()
                        self.name_of_card_to_play = card.get_name()
                        self.traits_of_card_to_play = card.get_traits()
                        if self.paying_shrieking_exarch_cost:
                            if self.card_pos_to_deploy != previous_card_pos_to_deploy:
                                primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                                if self.card_pos_to_deploy < previous_card_pos_to_deploy:
                                    previous_card_pos_to_deploy = previous_card_pos_to_deploy - 1
                            self.card_pos_to_deploy = previous_card_pos_to_deploy
                            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                            self.misc_counter += 1
                            if self.misc_counter > 1:
                                await self.send_update_message("Additional cost for Shrieking Exarch paid."
                                                               "You may continue deployment.")
                                self.paying_shrieking_exarch_cost = False
                        elif card.get_card_type() == "Support":
                            if card.check_for_a_trait("Pledge") and not primary_player.can_play_pledge:
                                await self.send_update_message("Pledges can only be played on the first deploy turn.")
                            else:
                                played_support = primary_player.play_card_if_support(self.card_pos_to_deploy,
                                                                                     already_checked=True, card=card)[0]
                                primary_player.aiming_reticle_color = ""
                                primary_player.aiming_reticle_coords_hand = -1
                                print(played_support)
                                if played_support == "SUCCESS":
                                    primary_player.cards.remove(primary_player.cards[self.card_pos_to_deploy])
                                    self.queued_sound = "onplay"
                                    self.action_cleanup()
                                    if primary_player.extra_deploy_turn_active:
                                        primary_player.extra_deploy_turn_active = False
                                        primary_player.has_passed = True
                                        if self.p1.has_passed and self.p2.has_passed:
                                            await self.send_update_message("Both passed, move to warlord movement.")
                                            await self.change_phase("COMMAND")
                            self.card_pos_to_deploy = -1
                        elif has_deepstrike and primary_player.resources > 0 and self.deepstrike_allowed:
                            print("deepstrike", card.get_deepstrike_value())
                            self.stored_deploy_string = game_update_string
                            self.choices_available = ["Normal Deploy", "Deploy into Reserve"]
                            self.choice_context = "Deploy into reserve?"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                        elif card.get_name() in self.cards_with_dash_cost or card.get_name() == "Genestealer Hybrids":
                            self.card_pos_to_deploy = -1
                            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                        elif card.get_card_type() == "Army":
                            if (primary_player.warlord_faction == "Necrons" and (
                                    card.get_faction() == primary_player.enslaved_faction or
                                    card.get_faction() == "Necrons" or
                                    card.get_faction() == "Neutral" or
                                    (primary_player.search_card_in_hq("Hollow Sun") and
                                     primary_player.count_units_of_faction(card.get_faction()) == 0))) or\
                                    primary_player.warlord_faction != "Necrons":
                                if not primary_player.enemy_holding_cell_check(card.get_name()):
                                    if card.get_name() == "Shrieking Exarch" and not self.shrieking_exarch_cost_payed:
                                        if len(primary_player.cards) > 2:
                                            await self.send_update_message("You must discard 2 cards to play "
                                                                           "Shrieking Exarch")
                                            self.paying_shrieking_exarch_cost = True
                                            primary_player.aiming_reticle_color = "blue"
                                            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                                            self.card_type_of_selected_card_in_hand = "Army"
                                            self.misc_counter = 0
                                    else:
                                        primary_player.aiming_reticle_color = "blue"
                                        primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                                        self.card_type_of_selected_card_in_hand = "Army"
                                        if card.get_name() == "Quartermasters":
                                            self.choices_available = ["HQ", "Normal"]
                                            self.choice_context = "Quartermasters to HQ?"
                                            self.name_player_making_choices = primary_player.name_player
                                            self.resolving_search_box = True
                        elif card.get_card_type() == "Attachment":
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                            self.card_type_of_selected_card_in_hand = "Attachment"
                            if primary_player.search_card_in_hq("WAAAGH! Arbuttz", ready_relevant=True):
                                self.choices_available = ["Yes", "No"]
                                self.choice_context = "Use WAAAGH! Arbuttz?"
                                self.name_player_making_choices = primary_player.name_player
                                self.resolving_search_box = True
                        else:
                            self.card_pos_to_deploy = previous_card_pos_to_deploy
        elif game_update_string[0] == "HQ":
            if name == self.player_with_deploy_turn:
                if self.mode == "Normal":
                    if game_update_string[1] == self.number_with_deploy_turn:
                        await deploy_card_routine_attachment(self, name, game_update_string)
                    else:
                        await deploy_card_routine_attachment(self, name, game_update_string)
                if self.mode == "DISCOUNT":
                    if game_update_string[1] == self.number_with_deploy_turn:
                        if self.number_with_deploy_turn == "1":
                            player = self.p1
                        else:
                            player = self.p2
                        if self.card_type_of_selected_card_in_hand == "Army":
                            discount_received = player.perform_discount_at_pos_hq(int(game_update_string[2]),
                                                                                  self.faction_of_card_to_play,
                                                                                  self.traits_of_card_to_play,
                                                                                  self.planet_aiming_reticle_position)
                            if discount_received > 0:
                                self.discounts_applied += discount_received
                            if self.discounts_applied >= self.available_discounts:
                                await deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                          discounts=self.discounts_applied)
                                self.mode = "Normal"

    elif len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if name == self.player_with_deploy_turn:
                if self.card_pos_to_deploy != -1 and not self.paying_shrieking_exarch_cost:
                    if self.number_with_deploy_turn == "1":
                        player = self.p1
                        other_player = self.p2
                    else:
                        player = self.p2
                        other_player = self.p1
                    planet_chosen = int(game_update_string[1])
                    card = player.get_card_in_hand(self.card_pos_to_deploy)
                    if self.deepstrike_deployment_active:
                        if player.put_card_into_reserve(card, planet_chosen):
                            player.remove_card_from_hand(self.card_pos_to_deploy)
                            player.aiming_reticle_coords_hand = None
                            self.card_pos_to_deploy = -1
                            self.deepstrike_deployment_active = False
                            self.action_cleanup()
                            if player.extra_deploy_turn_active:
                                player.extra_deploy_turn_active = False
                                player.has_passed = True
                                if self.p1.has_passed and self.p2.has_passed:
                                    await self.send_update_message("Both passed, move to warlord movement.")
                                    await self.change_phase("COMMAND")
                    elif card.get_card_type() == "Army":
                        if other_player.search_card_at_planet(planet_chosen, "Raving Cryptek"):
                            await self.send_update_message("Raving Cryptek detected! Please choose two")
                            self.choices_available = []
                            for i in range(len(player.cards)):
                                card = self.preloaded_find_card(player.cards[i])
                                if card.get_is_unit():
                                    self.choices_available.append(card.get_name())
                            if len(self.choices_available) < 2:
                                await self.send_update_message("Not enough units to satisfy Raving Cryptek.")
                                self.choices_available = []
                            else:
                                self.choice_context = "Raving Cryptek: Choose first card"
                                self.name_player_making_choices = player.name_player
                                self.resolving_search_box = True
                                self.misc_target_planet = planet_chosen
                        else:
                            self.discounts_applied = 0
                            await self.calculate_available_discounts_unit(planet_chosen, card, player)
                            await self.calculate_automatic_discounts_unit(planet_chosen, card, player)
                            if card.check_for_a_trait("Elite"):
                                player.master_warpsmith_count = 0
                            self.card_to_deploy = card
                            if self.available_discounts > self.discounts_applied:
                                self.stored_mode = self.mode
                                self.mode = "DISCOUNT"
                                self.planet_aiming_reticle_position = int(game_update_string[1])
                                self.planet_aiming_reticle_active = True
                            else:
                                await deploy_card_routine(self, name, game_update_string[1],
                                                          discounts=self.discounts_applied)
                    elif card.get_card_type() == "Attachment":
                        if card.planet_attachment and (card.ability != "Trapped Objective" or
                                                       planet_chosen != self.round_number):
                            can_continue = True
                            if card.get_unique():
                                if player.search_for_unique_card(card.get_name()):
                                    can_continue = False
                            if card.get_limited():
                                if not player.can_play_limited:
                                    can_continue = False
                            if card.limit_one_per_unit:
                                for i in range(len(player.attachments_at_planet[planet_chosen])):
                                    if player.attachments_at_planet[planet_chosen][i].get_name() == card.get_name():
                                        can_continue = False
                            if card.red_required:
                                if not self.get_red_icon(planet_chosen):
                                    can_continue = False
                            if card.blue_required:
                                if not self.get_blue_icon(planet_chosen):
                                    can_continue = False
                            if card.green_required:
                                if not self.get_green_icon(planet_chosen):
                                    can_continue = False
                            if can_continue:
                                cost = card.get_cost()
                                discounts = player.search_hq_for_discounts("", "", is_attachment=True)
                                cost = cost - discounts
                                if player.spend_resources(cost):
                                    player.add_attachment_to_planet(planet_chosen, card)
                                    player.remove_card_from_hand(self.card_pos_to_deploy)
                                    self.card_pos_to_deploy = -1
                                    self.planet_pos_to_deploy = -1
                                    player.aiming_reticle_coords_hand = None
                                    self.action_cleanup()
                                    if player.extra_deploy_turn_active:
                                        player.extra_deploy_turn_active = False
                                        player.has_passed = True
                                        if self.p1.has_passed and self.p2.has_passed:
                                            await self.send_update_message("Both passed, move to warlord movement.")
                                            await self.change_phase("COMMAND")
    elif len(game_update_string) == 4:
        if game_update_string[0] == "IN_PLAY":
            if self.mode == "Normal":
                if name == self.player_with_deploy_turn:
                    await deploy_card_routine_attachment(self, name, game_update_string)
            elif self.mode == "DISCOUNT":
                if game_update_string[1] == self.number_with_deploy_turn:
                    if self.number_with_deploy_turn == "1":
                        player = self.p1
                    else:
                        player = self.p2
                    if self.card_type_of_selected_card_in_hand == "Army":
                        discount_received = player.perform_discount_at_pos_in_play(int(game_update_string[2]),
                                                                                   int(game_update_string[3]),
                                                                                   self.traits_of_card_to_play)
                        if discount_received > 0:
                            self.discounts_applied += discount_received
                        if self.discounts_applied >= self.available_discounts:
                            await deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                      discounts=self.discounts_applied)
                            self.mode = "Normal"


async def deploy_card_routine(self, name, planet_pos, discounts=0):
    print("Deploy card at planet", planet_pos)
    planet_pos = int(planet_pos)
    primary_player = self.p1
    secondary_player = self.p2
    is_an_interrupt = False
    is_a_reaction = False
    is_battle_ability = False
    if self.interrupts_waiting_on_resolution and self.already_resolving_interrupt:
        if self.interrupts_waiting_on_resolution[0] == "Magus Harid" or \
                self.interrupts_waiting_on_resolution[0] == "Berzerker Warriors" or \
                self.interrupts_waiting_on_resolution[0] == "Catachan Devils Patrol":
            is_an_interrupt = True
            primary_player = self.p1
            secondary_player = self.p2
            if self.player_resolving_interrupts[0] == self.name_2:
                primary_player = self.p2
                secondary_player = self.p1
    if not is_an_interrupt:
        if self.reactions_needing_resolving and self.already_resolving_reaction:
            if self.reactions_needing_resolving[0] == "Vamii Industrial Complex":
                is_a_reaction = True
                primary_player = self.p1
                secondary_player = self.p2
                if self.player_who_resolves_reaction[0] == self.name_2:
                    primary_player = self.p2
                    secondary_player = self.p1
            if self.reactions_needing_resolving[0] == "The Dance Without End":
                is_a_reaction = True
                primary_player = self.p1
                secondary_player = self.p2
                if self.player_who_resolves_reaction[0] == self.name_2:
                    primary_player = self.p2
                    secondary_player = self.p1
    if not is_an_interrupt and not is_a_reaction:
        if self.battle_ability_to_resolve:
            is_battle_ability = True
            if self.player_resolving_battle_ability == self.name_1:
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
        else:
            if self.phase != "DEPLOY":
                if self.player_with_action == self.name_1:
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
            else:
                if self.number_with_deploy_turn == "1":
                    primary_player = self.p1
                    secondary_player = self.p2
                else:
                    primary_player = self.p2
                    secondary_player = self.p1
    if primary_player.webway_witch > -1:
        if self.planets_in_play_array[primary_player.webway_witch]:
            planet_pos = primary_player.webway_witch
    primary_player.reset_all_aiming_reticles_play_hq()
    damage_to_take = sum(self.damage_for_unit_to_take_on_play)
    print("position hand of unit: ", self.card_pos_to_deploy)
    print("Damage to take: ", damage_to_take)
    self.bigga_is_betta_active = True
    own_card = True
    if self.action_chosen == "Anrakyr the Traveller":
        if self.anrakyr_deck_choice == secondary_player.get_name_player():
            own_card = False
    if (primary_player.bluddflagg_relevant or secondary_player.bluddflagg_relevant) and not primary_player.bluddflagg_used:
        if self.card_to_deploy is not None:
            if self.card_to_deploy.get_card_type() == "Army":
                planet_pos = -2
    played_card, position_of_unit = primary_player.play_card(planet_pos,
                                                             card=self.card_to_deploy,
                                                             discounts=discounts,
                                                             damage_to_take=damage_to_take,
                                                             is_owner_of_card=own_card)
    if played_card == "SUCCESS":
        primary_player.webway_witch = -1
        self.queued_sound = "onplay"
        if (not self.action_chosen or self.action_chosen == "Ambush" or self.action_chosen == "Staging Ground" or
                self.action_chosen == "Behind Enemy Lines") \
                and not self.misc_player_storage == "RESOLVING MAGUS HARID" \
                and not self.misc_player_storage == "RESOLVING Ice World Hydras IV":
            primary_player.cards.remove(self.card_to_deploy.get_name())
        elif self.action_chosen == "Decaying Warrior Squad":
            del primary_player.discard[primary_player.aiming_reticle_coords_discard]
            primary_player.aiming_reticle_coords_discard = -1
            primary_player.cards_in_play[planet_pos + 1][position_of_unit]. \
                valid_target_dynastic_weaponry = True
            if "Dynastic Weaponry" in primary_player.discard:
                if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                    self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                         (int(primary_player.get_number()), planet_pos, position_of_unit))
            if primary_player.search_hand_for_card("Optimized Protocol"):
                self.create_reaction("Optimized Protocol", primary_player.name_player,
                                     (int(primary_player.get_number()), planet_pos, position_of_unit))
        elif self.action_chosen == "Triumvirate of Ynnead":
            del primary_player.discard[primary_player.aiming_reticle_coords_discard]
            primary_player.aiming_reticle_coords_discard = -1
            self.chosen_first_card = False
            self.trium_tracker = (self.card_to_deploy.get_name(), planet_pos)
            self.trium_count += 1
        elif self.action_chosen == "Anrakyr the Traveller":
            if self.anrakyr_deck_choice == primary_player.name_player:
                del primary_player.discard[self.anrakyr_unit_position]
            else:
                del secondary_player.discard[self.anrakyr_unit_position]
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            primary_player.cards_in_play[planet_pos + 1][position_of_unit]. \
                valid_target_dynastic_weaponry = True
            if "Dynastic Weaponry" in primary_player.discard:
                if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                    self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                         (int(primary_player.get_number()), planet_pos, position_of_unit))
            if primary_player.search_hand_for_card("Optimized Protocol"):
                self.create_reaction("Optimized Protocol", primary_player.name_player,
                                     (int(primary_player.get_number()), planet_pos, position_of_unit))
        elif self.action_chosen == "Accelerated Gestation":
            og_pla, og_pos, og_att = self.misc_target_attachment
            num = self.misc_target_player
            if num == int(primary_player.get_number()):
                del primary_player.cards_in_play[og_pla + 1][og_pos].get_attachments()[og_att]
                if not primary_player.get_immune_to_enemy_events(og_pla, og_pos):
                    primary_player.assign_damage_to_pos(og_pla, og_pos, 1, preventable=False,
                                                        by_enemy_unit=False)
            else:
                del secondary_player.cards_in_play[og_pla + 1][og_pos].get_attachments()[og_att]
                if not secondary_player.get_immune_to_enemy_events(og_pla, og_pos):
                    secondary_player.assign_damage_to_pos(og_pla, og_pos, 1, preventable=False,
                                                          by_enemy_unit=False)
    self.bigga_is_betta_active = False
    if played_card == "SUCCESS":
        if damage_to_take > 0:
            self.damage_is_taken_one_at_a_time = True
            primary_player.set_aiming_reticle_in_play(planet_pos, position_of_unit, "red")
    if self.action_chosen == "Triumvirate of Ynnead":
        if self.trium_count > 1:
            self.action_cleanup()
    elif self.action_chosen == "Behind Enemy Lines":
        self.chosen_second_card = True
        self.misc_target_planet = planet_pos
    else:
        self.action_cleanup()
    if self.interrupts_waiting_on_resolution and self.already_resolving_interrupt:
        if self.interrupts_waiting_on_resolution[0] == "Berzerker Warriors":
            self.delete_interrupt()
        if self.interrupts_waiting_on_resolution[0] == "Magus Harid":
            primary_player.discard.remove(self.card_to_deploy.get_name())
            self.misc_player_storage = ""
            self.delete_interrupt()
            self.action_cleanup()
        elif self.interrupts_waiting_on_resolution[0] == "Catachan Devils Patrol":
            self.delete_interrupt()
            self.choices_available = ["Take Damage", "Cancel Attack"]
            self.choice_context = "Catachan Devils Patrol: make a choice"
            self.name_player_making_choices = secondary_player.get_name_player()
            self.resolving_search_box = True
    if self.reactions_needing_resolving and self.already_resolving_reaction:
        if self.reactions_needing_resolving[0] == "Vamii Industrial Complex":
            self.delete_reaction()
    if is_battle_ability:
        pass
    if primary_player.extra_deploy_turn_active:
        primary_player.extra_deploy_turn_active = False
        primary_player.has_passed = True
        if self.p1.has_passed and self.p2.has_passed:
            await self.send_update_message("Both passed, move to warlord movement.")
            await self.change_phase("COMMAND")
    self.damage_for_unit_to_take_on_play = []
    self.card_pos_to_deploy = -1
    self.card_to_deploy = None
    primary_player.aiming_reticle_color = None
    primary_player.aiming_reticle_coords_hand = None
    self.planet_aiming_reticle_active = False
    self.planet_aiming_reticle_position = -1
    if self.phase == "COMBAT":
        self.planet_aiming_reticle_active = True
        self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
    self.discounts_applied = 0
    self.available_discounts = 0
    self.faction_of_card_to_play = ""
    self.name_of_card_to_play = ""
    print("Finished deploying card")


async def deploy_card_routine_attachment(self, name, game_update_string, special_action=False):
    if game_update_string[0] == "HQ":
        game_update_string = ["HQ", game_update_string[1], "-2", game_update_string[2]]
    print("Deploy attachment to: player ", game_update_string[1], "planet ", game_update_string[2],
          "position ", game_update_string[3])
    print("Position of card in hand: ", self.card_pos_to_deploy)
    if self.number_with_deploy_turn == "1":
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if special_action:
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
    if game_update_string[1] == "1":
        player_gaining_attachment = self.p1
    else:
        player_gaining_attachment = self.p2
    card = None
    magus_harid = False
    impulsive_loota = False
    if self.reactions_needing_resolving:
        if self.reactions_needing_resolving[0] == "Impulsive Loota Reserve"\
                or self.reactions_needing_resolving[0] == "Impulsive Loota In Play":
            card = self.card_to_deploy
            impulsive_loota = True
            primary_player = self.p1
            secondary_player = self.p2
            if self.player_who_resolves_reaction[0] == self.name_2:
                primary_player = self.p2
                secondary_player = self.p1
    if self.interrupts_waiting_on_resolution:
        if self.interrupts_waiting_on_resolution[0] == "Magus Harid":
            card = self.card_to_deploy
            magus_harid = True
            primary_player = self.p1
            secondary_player = self.p2
            if self.player_resolving_interrupts[0] == self.name_2:
                primary_player = self.p2
                secondary_player = self.p1
    if card is None:
        card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
    discounts = primary_player.search_hq_for_discounts("", "", is_attachment=True)
    if primary_player.waaagh_arbuttz_active:
        discounts += 1
    can_continue = False
    army_unit_as_attachment = False
    non_attachs_that_can_be_played_as_attach = ["Gun Drones", "Shadowsun's Stealth Cadre", "Escort Drone"]
    if card.get_card_type() == "Attachment":
        can_continue = True
    elif card.get_ability() in non_attachs_that_can_be_played_as_attach:
        can_continue = True
        army_unit_as_attachment = True
    if can_continue:
        limited = card.get_limited()
        print("Limited state of card:", limited)
        print("Name of card:", card.get_name())
        if not primary_player.can_play_limited and limited:
            pass
        else:
            if primary_player.get_number() == player_gaining_attachment.get_number():
                print("Playing own card")
                played_card = primary_player.play_attachment_card_to_in_play(card, int(game_update_string[2]),
                                                                             int(game_update_string[3]),
                                                                             army_unit_as_attachment=
                                                                             army_unit_as_attachment,
                                                                             discounts=discounts)
                enemy_card = False
            else:
                played_card = False
                if primary_player.spend_resources(int(card.get_cost()) - discounts):
                    played_card = secondary_player.play_attachment_card_to_in_play(
                        card, int(game_update_string[2]), int(game_update_string[3]), not_own_attachment=True,
                        army_unit_as_attachment=army_unit_as_attachment)
                    if not played_card:
                        primary_player.add_resources(int(card.get_cost()) - discounts, refund=True)
                enemy_card = True
            if played_card:
                if limited:
                    primary_player.can_play_limited = False
                for i in range(len(primary_player.headquarters)):
                    if primary_player.get_ability_given_pos(-2, i) == "Talon Strike Force":
                        self.create_reaction("Talon Strike Force", primary_player.name_player,
                                             (int(primary_player.number), -2, i))
                if not enemy_card:
                    if primary_player.waaagh_arbuttz_active:
                        primary_player.assign_damage_to_pos(int(game_update_string[2]), int(game_update_string[3]), 1,
                                                            by_enemy_unit=False)
                        self.create_reaction("WAAAGH! Arbuttz Rally", primary_player.name_player,
                                             (int(primary_player.number), -2, -1))
                else:
                    if primary_player.waaagh_arbuttz_active:
                        secondary_player.assign_damage_to_pos(int(game_update_string[2]), int(game_update_string[3]), 1,
                                                              by_enemy_unit=False)
                        self.create_reaction("WAAAGH! Arbuttz Rally", primary_player.name_player,
                                             (int(primary_player.number), -2, -1))
                primary_player.remove_card_from_hand(self.card_pos_to_deploy)
                print("Succeeded (?) in playing attachment")
                primary_player.aiming_reticle_coords_hand = -1
                self.card_pos_to_deploy = -1
                self.action_cleanup()
                if primary_player.extra_deploy_turn_active:
                    primary_player.extra_deploy_turn_active = False
                    primary_player.has_passed = True
                    if self.p1.has_passed and self.p2.has_passed:
                        await self.send_update_message("Both passed, move to warlord movement.")
                        await self.change_phase("COMMAND")
                self.card_type_of_selected_card_in_hand = ""
                self.faction_of_card_to_play = ""
                self.name_of_card_to_play = ""
                if magus_harid:
                    primary_player.discard.remove(primary_player.magus_harid_waiting_cards[0])
                    self.misc_player_storage = ""
                    self.delete_interrupt()
                    self.action_cleanup()
                if impulsive_loota:
                    primary_player.discard.remove(card.get_name())
                    self.delete_reaction()
