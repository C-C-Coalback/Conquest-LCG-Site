ability_targets_dictionary = {
    "Exterminatus": "Non-first planet"
}


def update_automated_attributes(self):
    if self.debug_mode is not None:
        self.what_is_required_automated = "None"
        self.automated_player_waited_on = ""
    elif self.choosing_unit_for_nullify:
        self.what_is_required_automated = "Nullify"
        self.automated_player_waited_on = self.name_player_using_nullify
    elif self.intercept_active:
        self.what_is_required_automated = "Intercept"
        self.automated_player_waited_on = self.name_player_intercept
    elif self.xv805_enforcer_active:
        self.what_is_required_automated = "XV805 Enforcer"
        self.automated_player_waited_on = self.player_using_xv805
    elif self.resolving_consumption:
        self.what_is_required_automated = "Consumption"
        self.automated_player_waited_on = self.player_with_initiative
    elif self.manual_bodyguard_resolution:
        self.what_is_required_automated = "Bodyguard"
        self.automated_player_waited_on = self.name_player_manual_bodyguard
    elif self.rearranging_deck:
        self.what_is_required_automated = "Rearrange"
        self.automated_player_waited_on = self.name_player_rearranging_deck
    elif self.cards_in_search_box:
        self.what_is_required_automated = "Search"
        self.automated_player_waited_on = self.name_player_who_is_searching
    elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
        self.what_is_required_automated = "Indirect"
        self.automated_player_waited_on = self.player_with_initiative
    elif self.choices_available:
        self.what_is_required_automated = "Choice"
        self.automated_player_waited_on = self.name_player_making_choices
    elif self.mode == "DISCOUNT":
        self.what_is_required_automated = "Discount"
        player, _ = self.determine_player_with_discounts()
        self.automated_player_waited_on = player.name_player
    elif self.interrupting_discard_effect_active:
        self.what_is_required_automated = "Discard Interrupt"
        self.automated_player_waited_on = ""
    elif self.interrupts_waiting_on_resolution:
        self.what_is_required_automated = "Interrupt"
        self.automated_player_waited_on = self.interrupts_waiting_on_resolution[0].get_player_resolving_interrupt()
    elif self.stored_damage:
        self.what_is_required_automated = "Damage"
        player_num = self.stored_damage[0].get_player_num_of_unit()
        if player_num == 1:
            self.automated_player_waited_on = self.name_1
        else:
            self.automated_player_waited_on = self.name_2
    elif self.resolving_kugath_nurglings:
        self.what_is_required_automated = "Kugaths Nurglings"
        self.automated_player_waited_on = ""
    elif self.reactions_needing_resolving:
        self.what_is_required_automated = "Reaction"
        self.automated_player_waited_on = self.reactions_needing_resolving[0].get_player_resolving_reaction()
    elif not self.p1.mobile_resolved or not self.p2.mobile_resolved:
        self.what_is_required_automated = "Mobile"
        self.automated_player_waited_on = ""  # TODO: Less stupid mobile player
    elif self.battle_ability_to_resolve:
        self.what_is_required_automated = "Battle Ability"
        self.automated_player_waited_on = self.player_resolving_battle_ability
        if self.battle_ability_to_resolve == "Y'varn":
            if not self.p1_triggered_yvarn and not self.p2_triggered_yvarn:
                self.automated_player_waited_on = self.name_1
            elif self.p1_triggered_yvarn and not self.p2_triggered_yvarn:
                self.automated_player_waited_on = self.name_2
            else:
                self.automated_player_waited_on = self.name_1
    elif self.action_chosen:
        self.what_is_required_automated = "Action"
        self.automated_player_waited_on = self.player_with_action
    elif self.phase == "DEPLOY":
        self.what_is_required_automated = "Deploy Turn"
        self.automated_player_waited_on = self.player_with_deploy_turn
    elif self.phase == "COMMAND":
        if self.committing_warlords:
            self.what_is_required_automated = "Commitment"
            if not self.p1.committed_warlord and not self.p2.committed_warlord:
                self.automated_player_waited_on = self.player_with_initiative
            elif not self.p1.committed_warlord:
                self.automated_player_waited_on = self.name_1
            else:
                self.automated_player_waited_on = self.name_2
        else:
            self.what_is_required_automated = "Command not Commitment"
            if not self.p1.has_passed and not self.p2.has_passed:
                self.automated_player_waited_on = self.player_with_initiative
            elif not self.p1.has_passed:
                self.automated_player_waited_on = self.name_1
            else:
                self.automated_player_waited_on = self.name_2
    elif self.phase == "COMBAT":
        if not self.check_if_battle_taking_place():
            self.what_is_required_automated = "Outside Combat"
            if not self.p1.has_passed and not self.p2.has_passed:
                self.automated_player_waited_on = self.player_with_initiative
            elif not self.p1.has_passed:
                self.automated_player_waited_on = self.name_1
            else:
                self.automated_player_waited_on = self.name_2
        else:
            if self.mode == "RETREAT":
                self.what_is_required_automated = "Retreat Turn"
                self.automated_player_waited_on = self.player_with_combat_turn
            else:
                self.what_is_required_automated = "Combat Turn"
                self.automated_player_waited_on = self.player_with_combat_turn
    elif self.phase == "HEADQUARTERS":
        self.what_is_required_automated = "Headquarters Action"
        if not self.p1.has_passed and not self.p2.has_passed:
            self.automated_player_waited_on = self.player_with_initiative
        elif not self.p1.has_passed:
            self.automated_player_waited_on = self.name_1
        else:
            self.automated_player_waited_on = self.name_2
    elif self.phase == "SETUP":
        self.what_is_required_automated = "SETUP"
        if not self.p1.deck_loaded:
            self.automated_player_waited_on = self.name_1
        else:
            self.automated_player_waited_on = self.name_2
    self.clickable_items_automated = determine_valid_moves(self)


def add_valid_move(valid_moves, player, card_zone, planet_pos=-1, unit_pos=-1, hand_pos=-1, discard_pos=-1,
                   choice_pos=-1, attachment_pos=-1):
    if card_zone.capitalize() == "Pass" or card_zone == "pass-P1":
        valid_moves.append("pass-P1")
    elif card_zone == "PLANETS":
        valid_moves.append("PLANETS/" + str(planet_pos))
    elif card_zone == "HQ":
        valid_moves.append("HQ/" + player.number + "/" + str(unit_pos))
    elif card_zone == "IN_PLAY":
        valid_moves.append("IN_PLAY/" + player.number + "/" + str(planet_pos) + "/" + str(unit_pos))
    elif card_zone == "HAND":
        valid_moves.append("HAND/" + player.number + "/" + str(hand_pos))
    elif card_zone == "CHOICE":
        valid_moves.append("CHOICE/" + str(choice_pos))
    elif card_zone == "SEARCH":
        valid_moves.append("SEARCH/" + str(choice_pos))
    elif card_zone == "ATTACHMENT":
        if planet_pos == -2:
            valid_moves.append("ATTACHMENT/HQ/" + player.number + "/" + str(unit_pos) + "/" + str(attachment_pos))
        elif card_zone == "IN_PLAY":
            valid_moves.append("ATTACHMENT/IN_PLAY/" + player.number + "/" + str(planet_pos) + "/" + str(unit_pos) + "/" + str(attachment_pos))
    return valid_moves


def add_active_planets_as_valid_moves(self, valid_moves):
    for i in range(len(self.planets_in_play_array)):
        if self.planets_in_play_array[i]:
            valid_moves = add_valid_move(valid_moves, None, "PLANETS", planet_pos=i)
    return valid_moves


def add_active_non_first_planets_as_valid_moves(self, valid_moves):
    for i in range(len(self.planets_in_play_array)):
        if self.round_number != i:
            if self.planets_in_play_array[i]:
                valid_moves = add_valid_move(valid_moves, None, "PLANETS", planet_pos=i)
    return valid_moves


def determine_valid_moves(self):
    valid_moves = []
    primary_player, secondary_player = self.get_players_given_name(self.automated_player_waited_on)
    if primary_player is not None:
        if self.what_is_required_automated == "Nullify":
            for i in range(len(primary_player.headquarters)):
                if primary_player.valid_nullify_unit(-2, i):
                    valid_moves = add_valid_move(valid_moves, primary_player, "HQ", unit_pos=i)
            for planet_pos in range(7):
                for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                    if self.valid_nullify_unit(planet_pos, unit_pos):
                        valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", planet_pos=planet_pos, unit_pos=unit_pos)
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Search":
            for i in range(len(self.cards_in_search_box)):
                if self.check_if_search_pos_satisfies_conditions(primary_player, i):
                    valid_moves = add_valid_move(valid_moves, primary_player, "SEARCH", choice_pos=i)
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Choice":
            for i in range(len(self.choices_available)):
                valid_moves = add_valid_move(valid_moves, primary_player, "CHOICE", choice_pos=i)
        elif self.what_is_required_automated == "Discount":
            valid_moves = primary_player.get_playable_borders()
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Deploy Turn":
            if self.card_to_deploy is None:
                for i in range(len(primary_player.cards)):
                    playability = primary_player.determine_playability(primary_player.cards[i])
                    if playability == "playable":
                        valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
            else:
                if self.card_to_deploy.get_card_type() == "Army":
                    valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
                if self.card_to_deploy.get_card_type() == "Attachment":
                    if self.card_to_deploy.planet_attachment:
                        valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
                    else:
                        valid_moves = primary_player.get_playable_borders()
        elif self.what_is_required_automated == "Commitment":
            valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
        elif self.what_is_required_automated == "Command not Commitment":
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Outside Combat":
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Combat Turn":
            battle_planet = self.last_planet_checked_for_battle
            if self.attacker_planet == -1 and self.attacker_position == -1:
                for i in range(len(primary_player.cards_in_play[battle_planet + 1])):
                    if self.check_if_unit_can_be_declared_as_attacker(primary_player, secondary_player, battle_planet, i):
                        valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", battle_planet, i)
            else:
                for i in range(len(secondary_player.cards_in_play[battle_planet + 1])):
                    if self.check_if_unit_can_be_declared_as_defender(primary_player, secondary_player, battle_planet, i):
                        valid_moves = add_valid_move(valid_moves, secondary_player, "IN_PLAY", battle_planet, i)
        elif self.what_is_required_automated == "Retreat Turn":
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Headquarters Action":
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Planet Ability":
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Damage":
            if self.stored_damage[0].get_position_unit()[0] == int(primary_player.get_number()):
                valid_moves = primary_player.get_playable_borders()
                for i in range(len(primary_player.cards)):
                    playability = primary_player.determine_playability(primary_player.cards[i])
                    if playability == "playable":
                        valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
                hurt_num, hurt_pla, hurt_pos = self.stored_damage[0].get_position_unit()
                for i in range(len(primary_player.get_all_attachments_at_pos(hurt_pla, hurt_pos))):
                    if primary_player.check_if_attachment_ability_usable_during_shield(hurt_pla, hurt_pos, i):
                        valid_moves = add_valid_move(
                            valid_moves, primary_player, "ATTACHMENT",
                            planet_pos=hurt_pla, unit_pos=hurt_pos, attachment_pos=i
                        )
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Action":
            if self.action_chosen in ability_targets_dictionary:
                type_of_targets = ability_targets_dictionary[self.action_chosen]
                if type_of_targets == "Non-first planet":
                    valid_moves = add_active_non_first_planets_as_valid_moves(self, valid_moves)
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        else:
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
    return valid_moves
