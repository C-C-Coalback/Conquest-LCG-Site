from .AbilityTargetsDictionary import ability_targets_dictionary
from .DetectPossibleActions import detect_possible_actions


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
    elif self.action_object.action_chosen:
        self.what_is_required_automated = "Action"
        self.automated_player_waited_on = self.action_object.player_with_action
    elif self.mode == "RETREAT":
        self.what_is_required_automated = "Retreat Turn"
        self.automated_player_waited_on = self.player_with_combat_turn
    elif self.phase == "DEPLOY":
        if self.check_if_battle_taking_place():
            if self.mode == "RETREAT":
                self.what_is_required_automated = "Retreat Turn"
                self.automated_player_waited_on = self.player_with_combat_turn
            else:
                self.what_is_required_automated = "Combat Turn"
                self.automated_player_waited_on = self.player_with_combat_turn
        else:
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
                if not self.automated_1_has_passed_action or not self.automated_2_has_passed_action:
                    if self.p1.has_initiative_for_battle and not self.automated_1_has_passed_action:
                        self.automated_player_waited_on = self.name_1
                    elif not self.automated_2_has_passed_action:
                        self.automated_player_waited_on = self.name_2
                    else:
                        self.automated_player_waited_on = self.name_1
                    self.what_is_required_automated = "Action Window Between Combat Turns"
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
        else:
            valid_moves.append("ATTACHMENT/IN_PLAY/" + player.number + "/" + str(planet_pos) + "/" + str(unit_pos) + "/" + str(attachment_pos))
    return valid_moves


def check_if_planet_is_valid_target(self, planet_pos, primary_player, secondary_player, ability, restrictions, misc_pla=-1):
    non_first = restrictions["Non-first"]
    icons = restrictions["Icons"]
    not_same_planet = restrictions["Not Same Planet"]
    if not self.planets_in_play_array[planet_pos]:
        return False
    if non_first:
        if self.round_number == planet_pos:
            return False
    if not_same_planet:
        if planet_pos == misc_pla:
            return False
    return True


def add_valid_planets_as_valid_moves(self, valid_moves, primary_player, secondary_player, ability, restrictions, misc_pla=-1):
    for i in range(len(self.planets_in_play_array)):
        if check_if_planet_is_valid_target(self, i, primary_player, secondary_player, ability, restrictions, misc_pla=misc_pla):
            valid_moves = add_valid_move(valid_moves, None, "PLANETS", planet_pos=i)
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


def check_if_single_card_in_play_is_valid_target(self, ability, player, planet_pos, unit_pos, target_restrictions):
    unit_only = target_restrictions["Unit Only"]
    unique_required = target_restrictions["Unique"]
    ready_required = target_restrictions["Ready"]
    exhaust_required = target_restrictions["Exhaust"]
    faction_required = target_restrictions["Faction"]
    card_type_required = target_restrictions["Card Type"]
    forbidden_card_type = target_restrictions["Forbidden Card Type"]
    required_traits = target_restrictions["Required Traits"]
    forbidden_traits = target_restrictions["Forbidden Traits"]
    special_restrictions = target_restrictions["Special"]
    ability_type = target_restrictions["Ability Type"]
    if unit_only:
        if not player.check_is_unit_at_pos(planet_pos, unit_pos):
            return False
    if unique_required:
        if not player.get_unique_given_pos(planet_pos, unit_pos):
            return False
    if ready_required:
        if not player.get_ready_given_pos(planet_pos, unit_pos):
            return False
    elif exhaust_required:
        if player.get_ready_given_pos(planet_pos, unit_pos):
            return False
    if faction_required:
        if not player.check_if_faction_given_pos(planet_pos, unit_pos, faction_required):
            return False
    if card_type_required:
        if player.get_card_type_given_pos(planet_pos, unit_pos) != card_type_required:
            return False
    if forbidden_card_type:
        if player.get_card_type_given_pos(planet_pos, unit_pos) == forbidden_card_type:
            return False
    if required_traits:
        for trait in required_traits:
            if not player.check_for_trait_given_pos(planet_pos, unit_pos, trait):
                return False
    if forbidden_traits:
        for trait in forbidden_traits:
            if player.check_for_trait_given_pos(planet_pos, unit_pos, trait):
                return False
    if special_restrictions:
        if ability_type == "Reaction":
            if ability.get_reaction_name() == "Cato's Stronghold":
                if planet_pos not in ability.misc_list:
                    return False
            elif ability.get_reaction_name() == "Sicarius's Chosen":
                if abs(ability.get_planet_pos() - planet_pos) != 1:
                    return False
        elif ability == "Planet":
            pass
    return True


def check_if_single_card_in_hand_is_valid_target(self, ability, player, hand_pos, target_restrictions, planet_pos=-1):
    faction_hand_card = target_restrictions["Faction"]
    card_type_hand_card = target_restrictions["Card Type"]
    max_cost_hand_card = target_restrictions["Max Cost"]
    payment_hand_card = target_restrictions["Payment"]
    card_enters_play = target_restrictions["Card Enters Play"]
    card = player.get_card_in_hand(hand_pos)
    if faction_hand_card:
        if faction_hand_card:
            if faction_hand_card != card.get_faction():
                return False
    if card_type_hand_card:
        if card_type_hand_card != card.get_card_type():
            return False
    if max_cost_hand_card:
        if card.get_cost() > max_cost_hand_card:
            return False
    if payment_hand_card:
        is_deploy = target_restrictions["Payment Details"]["Deploy"]
        if is_deploy:
            if player.determine_lowest_possible_cost_of_card(card) > player.get_resources():
                return False
        else:
            if card.get_cost() > player.get_resources():
                return False
    if card_enters_play:
        if not player.check_if_card_can_enter_play(card, planet_pos=planet_pos, triggered_card_effect=True):
            return False
    return True


def find_all_valid_hand_locations_given_restrictions(self, ability, primary_player, secondary_player, target_restrictions, planet_pos=-1):
    valid_moves = []
    for i in range(len(primary_player.cards)):
        if check_if_single_card_in_hand_is_valid_target(self, ability, primary_player, i, target_restrictions, planet_pos=planet_pos):
            valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
    return valid_moves


def find_all_valid_unit_locations_given_restrictions(self, ability, primary_player, secondary_player, target_restrictions):
    valid_moves = []
    own_unit = target_restrictions["Own Unit"]
    enemy_unit = target_restrictions["Enemy Unit"]
    if own_unit:
        for i in range(len(primary_player.headquarters)):
            if check_if_single_card_in_play_is_valid_target(self, ability, primary_player, -2, i, target_restrictions):
                valid_moves = add_valid_move(valid_moves, primary_player, "HQ", unit_pos=i)
        for i in range(7):
            for j in range(len(primary_player.cards_in_play[i + 1])):
                if check_if_single_card_in_play_is_valid_target(self, ability, primary_player, i, j, target_restrictions):
                    valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", planet_pos=i, unit_pos=j)
    if enemy_unit:
        for i in range(len(secondary_player.headquarters)):
            if check_if_single_card_in_play_is_valid_target(self, ability, secondary_player, -2, i, target_restrictions):
                valid_moves = add_valid_move(valid_moves, secondary_player, "HQ", unit_pos=i)
        for i in range(7):
            for j in range(len(secondary_player.cards_in_play[i + 1])):
                if check_if_single_card_in_play_is_valid_target(self, ability, secondary_player, i, j, target_restrictions):
                    valid_moves = add_valid_move(valid_moves, secondary_player, "IN_PLAY", planet_pos=i, unit_pos=j)
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
            if self.card_to_deploy.get_cost() <= primary_player.get_resources() - self.discounts_applied:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
            if not valid_moves:
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
            valid_moves = detect_possible_actions(self, primary_player, secondary_player, combat_turn_action=False)
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
                if primary_player.get_area_effect_given_pos(self.attacker_planet, self.attacker_position) > 0:
                    valid_moves = add_valid_move(valid_moves, primary_player, "PLANETS", planet_pos=battle_planet)
        elif self.what_is_required_automated == "Retreat Turn":
            battle_planet = self.last_planet_checked_for_battle
            for i in range(len(primary_player.cards_in_play[battle_planet + 1])):
                if primary_player.check_if_unit_can_retreat(battle_planet, i):
                    valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", battle_planet, i)
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Headquarters Action":
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Battle Ability":
            planet_ability = self.battle_ability_to_resolve
            if planet_ability in ability_targets_dictionary:
                target_restriction_data = ability_targets_dictionary[planet_ability]
                num_stages = target_restriction_data["Num Stages"]
                stage_number = "1"
                if self.chosen_first_card and num_stages > 1:
                    stage_number = "2"
                if self.chosen_second_card and num_stages > 2:
                    stage_number = "3"
                type_target = target_restriction_data["Type " + stage_number]
                target_restrictions = target_restriction_data["Restrictions " + stage_number]
                misc_pla = self.last_planet_checked_for_battle
                if type_target == "Unit":
                    valid_moves = find_all_valid_unit_locations_given_restrictions(
                        self, planet_ability, primary_player, secondary_player, target_restrictions
                    )
                if type_target == "Hand":
                    valid_moves = find_all_valid_hand_locations_given_restrictions(
                        self, planet_ability, primary_player, secondary_player, target_restrictions, planet_pos=self.last_planet_checked_for_battle
                    )
                if type_target == "Planet":
                    valid_moves = add_valid_planets_as_valid_moves(self, valid_moves, primary_player, secondary_player,
                                                                   planet_ability, target_restrictions, misc_pla=misc_pla)
            else:
                if planet_ability == "Atrox Prime":
                    if len(primary_player.headquarters) > 0:
                        valid_moves = add_valid_move(valid_moves, primary_player, "HQ", unit_pos=0)
                    if len(secondary_player.headquarters) > 0:
                        valid_moves = add_valid_move(valid_moves, secondary_player, "HQ", unit_pos=0)
                    if self.atrox_origin != 0:
                        if len(secondary_player.cards_in_play[self.atrox_origin]) > 0:
                            valid_moves = add_valid_move(valid_moves, secondary_player, "PLANETS", planet_pos=self.atrox_origin - 1)
                    if self.atrox_origin != 6:
                        if len(secondary_player.cards_in_play[self.atrox_origin + 1]) > 0:
                            valid_moves = add_valid_move(valid_moves, secondary_player, "PLANETS", planet_pos=self.atrox_origin + 1)
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Damage":
            if self.stored_damage[0].get_position_unit()[0] == int(primary_player.get_number()):
                valid_moves = primary_player.get_playable_borders()
                for i in range(len(primary_player.cards)):
                    playability = primary_player.determine_playability(primary_player.cards[i])
                    if playability == "playable":
                        valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
                hurt_num, hurt_pla, hurt_pos = self.stored_damage[0].get_position_unit()
                print("attachment check")
                for i in range(len(primary_player.get_all_attachments_at_pos(hurt_pla, hurt_pos))):
                    print(primary_player.get_attachment_at_pos(hurt_pla, hurt_pos, i).get_ability())
                    if primary_player.check_if_attachment_ability_usable_during_shield(hurt_pla, hurt_pos, i):
                        valid_moves = add_valid_move(
                            valid_moves, primary_player, "ATTACHMENT",
                            planet_pos=hurt_pla, unit_pos=hurt_pos, attachment_pos=i
                        )
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Action Window Between Combat Turns":
            valid_moves = detect_possible_actions(self, primary_player, secondary_player, combat_turn_action=True)
        elif self.what_is_required_automated == "Action":
            if self.action_object.action_chosen == "Ambush":
                valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
            elif self.action_object.action_chosen in ability_targets_dictionary:
                target_restriction_data = ability_targets_dictionary[self.action_object.action_chosen]
                num_stages = target_restriction_data["Num Stages"]
                stage_number = "1"
                if self.action_object.chosen_first_card and num_stages > 1:
                    stage_number = "2"
                if self.action_object.chosen_second_card and num_stages > 2:
                    stage_number = "3"
                type_target = target_restriction_data["Type " + stage_number]
                target_restrictions = target_restriction_data["Restrictions " + stage_number]
                if type_target == "Hand":
                    valid_moves = find_all_valid_hand_locations_given_restrictions(
                        self, self.action_object, primary_player, secondary_player, target_restrictions, planet_pos=self.action_object.get_planet_pos()
                    )
                if type_target == "Planet":
                    if target_restrictions["Non-first"]:
                        valid_moves = add_active_non_first_planets_as_valid_moves(self, valid_moves)
                    else:
                        valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Reaction":
            current_reaction = self.reactions_needing_resolving[0].get_reaction_name()
            if current_reaction in ability_targets_dictionary:
                target_restriction_data = ability_targets_dictionary[current_reaction]
                num_stages = target_restriction_data["Num Stages"]
                stage_number = "1"
                if self.reactions_needing_resolving[0].chosen_first_card and num_stages > 1:
                    stage_number = "2"
                if self.reactions_needing_resolving[0].chosen_second_card and num_stages > 2:
                    stage_number = "3"
                type_target = target_restriction_data["Type " + stage_number]
                target_restrictions = target_restriction_data["Restrictions " + stage_number]
                if type_target == "Unit":
                    valid_moves = find_all_valid_unit_locations_given_restrictions(
                        self, self.reactions_needing_resolving[0], primary_player, secondary_player, target_restrictions
                    )
                if type_target == "Planet":
                    valid_moves = add_valid_planets_as_valid_moves(self, valid_moves, primary_player, secondary_player,
                                                                   current_reaction, target_restrictions, misc_pla=-1)
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Interrupt":
            current_interrupt = self.interrupts_waiting_on_resolution[0].get_interrupt_name()
            if current_interrupt in ability_targets_dictionary:
                target_restriction_data = ability_targets_dictionary[current_interrupt]
                num_stages = target_restriction_data["Num Stages"]
                stage_number = "1"
                if self.interrupts_waiting_on_resolution[0].chosen_first_card and num_stages > 1:
                    stage_number = "2"
                if self.interrupts_waiting_on_resolution[0].chosen_second_card and num_stages > 2:
                    stage_number = "3"
                type_target = target_restriction_data["Type " + stage_number]
                target_restrictions = target_restriction_data["Restrictions " + stage_number]
                if type_target == "Unit":
                    valid_moves = find_all_valid_unit_locations_given_restrictions(
                        self, self.interrupts_waiting_on_resolution[0], primary_player, secondary_player, target_restrictions
                    )
                if type_target == "Planet":
                    valid_moves = add_valid_planets_as_valid_moves(self, valid_moves, primary_player, secondary_player,
                                                                   current_interrupt, target_restrictions, misc_pla=-1)
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        else:
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
    return valid_moves
