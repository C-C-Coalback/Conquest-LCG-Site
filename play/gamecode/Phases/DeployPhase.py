async def update_game_event_deploy_section(self, name, game_update_string):
    print("Need to run deploy turn code.")
    print(self.player_with_deploy_turn, self.number_with_deploy_turn)
    print(name == self.player_with_deploy_turn)
    if self.mode == "ACTION":
        await self.update_game_event_action(name, game_update_string)
    elif len(game_update_string) == 1:
        if game_update_string[0] == "action-button":
            if self.get_actions_allowed():
                print("Need to run action code")
                if self.player_with_deploy_turn == name:
                    self.stored_mode = self.mode
                    self.mode = "ACTION"
                    self.player_with_action = name
                    print("Special deploy action")
                    await self.game_sockets[0].receive_game_update(name + " wants to take an action.")
                    if self.player_with_action == self.name_1 and self.p1.dark_possession_active:
                        self.choices_available = ["Dark Possession", "Regular Action"]
                        self.choice_context = "Use Dark Possession?"
                        self.name_player_making_choices = self.player_with_action
                        await self.send_search()
                    elif self.player_with_action == self.name_2 and self.p2.dark_possession_active:
                        self.choices_available = ["Dark Possession", "Regular Action"]
                        self.choice_context = "Use Dark Possession?"
                        self.name_player_making_choices = self.player_with_action
                        await self.send_search()
        elif game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
            print("Need to pass")
            if name == self.player_with_deploy_turn:
                if self.mode == "ACTION":
                    self.mode = self.stored_mode
                    self.stored_mode = ""
                    await self.game_sockets[0].receive_game_update(name + " cancelled their action request.")
                elif self.mode == "Normal":
                    if self.number_with_deploy_turn == "1":
                        self.number_with_deploy_turn = "2"
                        self.player_with_deploy_turn = self.name_2
                        self.p1.has_passed = True
                        self.discounts_applied = 0
                        self.available_discounts = 0
                    else:
                        self.number_with_deploy_turn = "1"
                        self.player_with_deploy_turn = self.name_1
                        self.p2.has_passed = True
                        self.discounts_applied = 0
                        self.available_discounts = 0
                elif self.mode == "DISCOUNT":
                    print("Play card with not all discounts")
                    await deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                              discounts=self.discounts_applied)
            if self.p1.has_passed and self.p2.has_passed:
                print("Both passed, move to warlord movement.")
                await self.change_phase("COMMAND")
            await self.send_info_box()
    elif len(game_update_string) == 3:
        if game_update_string[0] == "HAND":
            if self.mode == "DISCOUNT":
                if name == self.player_with_deploy_turn:
                    if game_update_string[1] == self.number_with_deploy_turn:
                        if self.card_type_of_selected_card_in_hand == "Army":
                            if self.number_with_deploy_turn == "1":
                                player = self.p1
                                secondary_player = self.p2
                            else:
                                player = self.p2
                                secondary_player = self.p1
                            discount_received, damage = player.perform_discount_at_pos_hand(
                                int(game_update_string[2]),
                                self.faction_of_card_to_play
                            )
                            if discount_received > 0:
                                if secondary_player.nullify_check() and self.nullify_enabled:
                                    await self.game_sockets[0].receive_game_update(
                                        player.name_player + " wants to play Bigga Is Betta; "
                                                             "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = int(game_update_string[2])
                                    self.nullified_card_name = "Bigga Is Betta"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = player.name_player
                                    self.nullify_context = "Bigga Is Betta"
                                    await self.send_search()
                                else:
                                    self.discounts_applied += discount_received
                                    player.discard_card_from_hand(int(game_update_string[2]))
                                    if self.card_pos_to_deploy > int(game_update_string[2]):
                                        self.card_pos_to_deploy -= 1
                                    if damage > 0:
                                        self.damage_for_unit_to_take_on_play.append(damage)
                                    if self.discounts_applied >= self.available_discounts:
                                        await deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                                  discounts=self.discounts_applied)
                                    else:
                                        await player.send_hand()
                                        await player.send_discard()
            elif self.mode == "Normal":
                if name == self.player_with_deploy_turn:
                    print(game_update_string[1] == self.number_with_deploy_turn)
                    if game_update_string[1] == self.number_with_deploy_turn:
                        print("Deploy card in hand at pos", game_update_string[2])
                        previous_card_pos_to_deploy = self.card_pos_to_deploy
                        self.card_pos_to_deploy = int(game_update_string[2])
                        if self.number_with_deploy_turn == "1":
                            primary_player = self.p1
                            secondary_player = self.p2
                        else:
                            primary_player = self.p2
                            secondary_player = self.p1
                        card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
                        self.faction_of_card_to_play = card.get_faction()
                        self.name_of_card_to_play = card.get_name()
                        self.traits_of_card_to_play = card.get_traits()
                        if card.get_card_type() == "Support":
                            played_support = primary_player.play_card_if_support(self.card_pos_to_deploy,
                                                                                 already_checked=True, card=card)[0]
                            primary_player.aiming_reticle_color = ""
                            primary_player.aiming_reticle_coords_hand = -1
                            print(played_support)
                            if played_support == "SUCCESS":
                                await primary_player.send_hand()
                                await primary_player.send_hq()
                                await primary_player.send_resources()
                                if not secondary_player.has_passed:
                                    self.player_with_deploy_turn = secondary_player.get_name_player()
                                    self.number_with_deploy_turn = secondary_player.get_number()
                                    await self.send_info_box()
                            self.card_pos_to_deploy = -1
                        elif card.get_card_type() == "Army":
                            if (primary_player.warlord_faction == "Necrons" and
                                    card.get_faction() == primary_player.enslaved_faction or
                                    card.get_faction() == "Neutral") or primary_player.warlord_faction != "Necrons":
                                primary_player.aiming_reticle_color = "blue"
                                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                                self.card_type_of_selected_card_in_hand = "Army"
                                await primary_player.send_hand()
                        elif card.get_card_type() == "Attachment":
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                            self.card_type_of_selected_card_in_hand = "Attachment"
                            await primary_player.send_hand()
                        else:
                            self.card_type_of_selected_card_in_hand = ""
                            self.card_pos_to_deploy = previous_card_pos_to_deploy
        elif game_update_string[0] == "HQ":
            if name == self.player_with_deploy_turn:
                if game_update_string[1] == self.number_with_deploy_turn:
                    if self.mode == "Normal":
                        await deploy_card_routine_attachment(self, name, game_update_string)
                    if self.mode == "DISCOUNT":
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
                                await player.send_hq()
                            if self.discounts_applied >= self.available_discounts:
                                await deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                          discounts=self.discounts_applied)
                                self.mode = "Normal"

    elif len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            if name == self.player_with_deploy_turn:
                if self.card_pos_to_deploy != -1:
                    if self.number_with_deploy_turn == "1":
                        player = self.p1
                    else:
                        player = self.p2
                    card = player.get_card_in_hand(self.card_pos_to_deploy)
                    if card.get_card_type() == "Army":
                        self.discounts_applied = 0
                        planet_chosen = int(game_update_string[1])
                        self.available_discounts = player.search_hq_for_discounts(self.faction_of_card_to_play,
                                                                                  self.traits_of_card_to_play,
                                                                                  planet_chosen=planet_chosen)
                        hand_disc = player.search_hand_for_discounts(self.faction_of_card_to_play)
                        self.available_discounts += hand_disc
                        if hand_disc > 0:
                            await self.game_sockets[0].receive_game_update(
                                "Bigga Is Betta detected, may be used as a discount."
                            )
                        temp_av_disc, temp_auto_disc = player. \
                            search_same_planet_for_discounts(self.faction_of_card_to_play, int(game_update_string[1]))
                        num_termagants = 0
                        if self.name_of_card_to_play == "Burrowing Trygon":
                            num_termagants = player.get_most_termagants_at_single_planet()
                            self.discounts_applied += num_termagants
                        self.available_discounts += num_termagants
                        self.available_discounts += player.search_all_planets_for_discounts(self.traits_of_card_to_play)
                        self.available_discounts += temp_av_disc
                        self.discounts_applied += temp_auto_disc
                        await player.send_units_at_all_planets()
                        await player.send_hq()
                        if self.available_discounts > self.discounts_applied:
                            self.stored_mode = self.mode
                            self.mode = "DISCOUNT"
                            self.planet_aiming_reticle_position = int(game_update_string[1])
                            self.planet_aiming_reticle_active = True
                            await self.send_planet_array()
                            await self.send_info_box()
                        else:
                            await deploy_card_routine(self, name, game_update_string[1],
                                                      discounts=self.discounts_applied)
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
                            await player.send_units_at_planet(int(game_update_string[2]))
                        if self.discounts_applied >= self.available_discounts:
                            await deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                      discounts=self.discounts_applied)
                            self.mode = "Normal"


async def deploy_card_routine(self, name, planet_pos, discounts=0):
    print("Deploy card at planet", planet_pos)
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
    primary_player.reset_all_aiming_reticles_play_hq()
    damage_to_take = sum(self.damage_for_unit_to_take_on_play)
    print("position hand of unit: ", self.card_pos_to_deploy)
    print("Damage to take: ", damage_to_take)
    self.bigga_is_betta_active = True
    played_card, position_of_unit = primary_player.play_card(int(planet_pos),
                                                             position_hand=self.card_pos_to_deploy,
                                                             discounts=discounts,
                                                             damage_to_take=damage_to_take)
    self.bigga_is_betta_active = False
    if played_card == "SUCCESS":
        if secondary_player.search_card_at_planet(int(planet_pos), "Syren Zythlex"):
            primary_player.exhaust_given_pos(int(planet_pos), position_of_unit)
        if damage_to_take > 0:
            self.damage_is_taken_one_at_a_time = True
            primary_player.set_aiming_reticle_in_play(int(planet_pos), position_of_unit, "red")
        await primary_player.send_hand()
        await secondary_player.send_hand()
        await primary_player.send_discard()
        await secondary_player.send_discard()
        await primary_player.send_units_at_all_planets()
        await secondary_player.send_units_at_planet(int(planet_pos))
        await primary_player.send_resources()
    self.mode = "Normal"
    if not secondary_player.has_passed:
        self.player_with_deploy_turn = secondary_player.get_name_player()
        self.number_with_deploy_turn = secondary_player.get_number()
    self.damage_for_unit_to_take_on_play = []
    self.card_pos_to_deploy = -1
    primary_player.aiming_reticle_color = None
    primary_player.aiming_reticle_coords_hand = None
    self.planet_aiming_reticle_active = False
    self.planet_aiming_reticle_position = -1
    self.discounts_applied = 0
    self.available_discounts = 0
    self.faction_of_card_to_play = ""
    self.name_of_card_to_play = ""
    await primary_player.send_hand()
    await primary_player.send_hq()
    await self.send_planet_array()
    print("Finished deploying card")


async def deploy_card_routine_attachment(self, name, game_update_string):
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
    if game_update_string[1] == "1":
        player_gaining_attachment = self.p1
    else:
        player_gaining_attachment = self.p2
    card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
    discounts = primary_player.search_hq_for_discounts("", "", is_attachment=True)
    can_continue = False
    army_unit_as_attachment = False
    non_attachs_that_can_be_played_as_attach = ["Gun Drones", "Shadowsun's Stealth Cadre"]
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
                        primary_player.add_resources(int(card.get_cost()) - discounts)
                enemy_card = True
            if played_card:
                if limited:
                    primary_player.can_play_limited = False
                primary_player.remove_card_from_hand(self.card_pos_to_deploy)
                print("Succeeded (?) in playing attachment")
                primary_player.aiming_reticle_coords_hand = -1
                await primary_player.send_hand()
                if enemy_card:
                    if game_update_string[2] == "-2":
                        await secondary_player.send_hq()
                    else:
                        await secondary_player.send_units_at_planet(int(game_update_string[2]))
                else:
                    if game_update_string[2] == "-2":
                        await primary_player.send_hq()
                    else:
                        await primary_player.send_units_at_planet(int(game_update_string[2]))
                await primary_player.send_resources()
                if not secondary_player.has_passed:
                    if self.phase == "DEPLOY":
                        self.player_with_deploy_turn = secondary_player.get_name_player()
                        self.number_with_deploy_turn = secondary_player.get_number()
                    await self.send_info_box()
                self.card_pos_to_deploy = -1
                self.mode = "Normal"
                self.card_type_of_selected_card_in_hand = ""
                self.faction_of_card_to_play = ""
                self.name_of_card_to_play = ""

