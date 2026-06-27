import copy
import os
import re

from .AbilityTargetsDictionary import ability_targets_dictionary
from .DetectPossibleActions import detect_possible_actions


def load_action_resolution_abilities():
    abilities = set()
    actions_dir = os.path.join(os.path.dirname(__file__), "Actions")
    equality_pattern = re.compile(r"self\.action_object\.action_chosen\s*==\s*[\"']([^\"']+)[\"']")
    list_pattern = re.compile(r"self\.action_object\.action_chosen\s+in\s+\[([^\]]+)\]")
    list_item_pattern = re.compile(r"[\"']([^\"']+)[\"']")
    try:
        file_names = os.listdir(actions_dir)
    except OSError:
        return abilities
    for file_name in file_names:
        if not file_name.endswith(".py"):
            continue
        if file_name in ["ActionClass.py", "__init__.py"]:
            continue
        file_path = os.path.join(actions_dir, file_name)
        try:
            with open(file_path, "r") as action_file:
                content = action_file.read()
        except OSError:
            continue
        for ability in equality_pattern.findall(content):
            abilities.add(ability)
        for list_match in list_pattern.findall(content):
            for ability in list_item_pattern.findall(list_match):
                abilities.add(ability)
    return abilities


ACTION_RESOLUTION_ABILITIES = load_action_resolution_abilities()


def check_if_deploy_action_has_non_pass_followup(self, primary_player, ability):
    original_what_is_required = self.what_is_required_automated
    original_player_waited_on = self.automated_player_waited_on
    original_mode = self.mode
    original_stored_mode = self.stored_mode
    original_clickable_items = copy.deepcopy(self.clickable_items_automated)
    original_action_object = copy.deepcopy(self.action_object)
    try:
        self.what_is_required_automated = "Action"
        self.automated_player_waited_on = primary_player.name_player
        self.mode = "ACTION"
        self.stored_mode = "Normal"
        self.action_object.reset_action_data()
        self.action_object.action_chosen = ability
        self.action_object.player_with_action = primary_player.name_player
        followup_moves = determine_valid_moves(self)
        for move in followup_moves:
            if move != "pass-P1":
                return True
        return False
    finally:
        self.what_is_required_automated = original_what_is_required
        self.automated_player_waited_on = original_player_waited_on
        self.mode = original_mode
        self.stored_mode = original_stored_mode
        self.clickable_items_automated = original_clickable_items
        self.action_object = original_action_object


def check_if_deploy_event_action_card_is_currently_legal(self, primary_player, hand_pos, possible_deploy_actions=None):
    card = primary_player.get_card_in_hand(hand_pos)
    if card is None:
        return False
    if card.get_card_type() != "Event":
        return True
    if not card.get_has_action_while_in_hand():
        return True
    if card.get_allowed_phases_while_in_hand() not in [self.phase, "ALL"]:
        return True
    if str(primary_player.number) == "1":
        secondary_player = self.p2
    else:
        secondary_player = self.p1
    ability = card.get_ability()
    if ability == "Raid":
        if not primary_player.get_can_play_limited():
            return False
        if primary_player.get_resources() >= secondary_player.get_resources():
            return False
    elif ability == "Tzeentch's Firestorm":
        if primary_player.get_resources() == 0:
            return False
    ability_needs_followup = ability in ability_targets_dictionary
    if possible_deploy_actions is None:
        possible_deploy_actions = detect_possible_actions(
            self, primary_player, secondary_player, combat_turn_action=False
        )
    special_action_token = "SPECIAL_ACTION_HAND/" + str(primary_player.number) + "/" + str(hand_pos)
    if special_action_token in possible_deploy_actions:
        if not ability_needs_followup:
            return True
        return check_if_deploy_action_has_non_pass_followup(self, primary_player, ability)
    if ability_needs_followup:
        return check_if_deploy_action_has_non_pass_followup(self, primary_player, ability)
    return True


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
        player, other_player = self.get_players_given_name(self.automated_player_waited_on)
        if player.indirect_damage_applied >= player.total_indirect_damage:
            self.automated_player_waited_on = other_player.name_player
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
    elif self.alt_shield_mode_active:
        self.what_is_required_automated = "Alt Shield"
        player_num = self.stored_damage[0].get_player_num_of_unit()
        if player_num == 1:
            self.automated_player_waited_on = self.name_1
        else:
            self.automated_player_waited_on = self.name_2
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
        self.automated_player_waited_on = self.player_mobiling
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
                if (not self.automated_1_has_passed_action or not self.automated_2_has_passed_action) and self.bot_is_present:  # Remove bot_is_present requirement if you want to manually test action windows between combat turns
                    self.automated_player_waited_on = self.get_action_window_between_combat_turns_player()
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
    elif self.phase.startswith("FIN"):
        self.what_is_required_automated = "Game Over"
        self.automated_player_waited_on = ""
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
    elif card_zone == "IN_DISCARD":
        valid_moves.append("IN_DISCARD/" + player.number + "/" + str(discard_pos))
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


def check_if_planet_is_valid_target(self, planet_pos, primary_player, secondary_player, ability, restrictions, misc_pla=-1, unit_pla=-1):
    non_first = restrictions["Non-first"]
    icons = restrictions["Icons"]
    not_same_planet = restrictions["Not Same Planet"]
    not_same_planet_unit = restrictions["Not Same Planet Unit"]
    if not self.planets_in_play_array[planet_pos]:
        return False
    if non_first:
        if self.round_number == planet_pos:
            return False
    if not_same_planet:
        if planet_pos == misc_pla:
            return False
    if not_same_planet_unit:
        if planet_pos == unit_pla:
            return False
    return True


def add_valid_planets_as_valid_moves(self, valid_moves, primary_player, secondary_player, ability, restrictions, misc_pla=-1, unit_pla=-1):
    for i in range(len(self.planets_in_play_array)):
        if check_if_planet_is_valid_target(self, i, primary_player, secondary_player, ability, restrictions, misc_pla=misc_pla, unit_pla=unit_pla):
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


def check_if_single_card_in_play_is_valid_target(self, ability, player, planet_pos, unit_pos, target_restrictions, enemy_ability=False, misc_pla=-1):
    unit_only = target_restrictions["Unit Only"]
    unique_required = target_restrictions["Unique"]
    ready_required = target_restrictions["Ready"]
    exhaust_required = target_restrictions["Exhaust"]
    faction_required = target_restrictions["Faction"]
    card_type_required = target_restrictions["Card Type"]
    forbidden_card_type = target_restrictions["Forbidden Card Type"]
    required_traits = target_restrictions["Required Traits"]
    forbidden_traits = target_restrictions["Forbidden Traits"]
    same_planet = target_restrictions["Same Planet"]
    targets = target_restrictions["Target"]
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
    if same_planet:
        if planet_pos != ability.get_planet_pos():
            return False
    if special_restrictions:
        if ability_type == "Reaction":
            if ability.get_reaction_name() == "Cato's Stronghold":
                if planet_pos not in ability.misc_list:
                    return False
            elif ability.get_reaction_name() == "Alaitoc Shrine":
                full_position = (int(player.get_number()), planet_pos, unit_pos)
                if full_position not in player.allowed_units_alaitoc_shrine:
                    return False
            elif ability.get_reaction_name() == "Sicarius's Chosen":
                if abs(ability.get_planet_pos() - planet_pos) != 1:
                    return False
            elif ability.get_reaction_name() == "Shrouded Harlequin":
                if planet_pos == -2:
                    return False
            elif ability.get_reaction_name() == "Spiritseer Erathal":
                if planet_pos == ability.get_planet_pos() and unit_pos == ability.get_unit_pos():
                    return False
                if player.get_damage_given_pos(planet_pos, unit_pos) == 0:
                    return False
            elif ability.get_reaction_name() == "Commander Shadowsun hand":
                shadowsun_player = ability.get_player_resolving_reaction()
                shadowsun_player = self.get_player_given_name(shadowsun_player)
                card = shadowsun_player.get_card_in_hand(shadowsun_player.aiming_reticle_coords_hand)
                if not player.check_if_can_attach_card(card, planet_pos, unit_pos):
                    return False
            elif ability.get_reaction_name() == "Commander Shadowsun discard":
                shadowsun_player = ability.get_player_resolving_reaction()
                shadowsun_player = self.get_player_given_name(shadowsun_player)
                card = shadowsun_player.get_card_in_discard(shadowsun_player.aiming_reticle_coords_discard)
                if not player.check_if_can_attach_card(card, planet_pos, unit_pos):
                    return False
            elif ability.get_reaction_name() == "Superiority":
                if planet_pos != self.last_planet_checked_command_struggle:
                    return False
        elif ability_type == "Action":
            if ability.action_chosen == "Preemptive Barrage":
                if player.get_ranged_given_pos(planet_pos, unit_pos):
                    return False
                if ability.misc_target_planet != -1:
                    if ability.misc_target_planet != planet_pos:
                        return False
            elif ability.action_chosen == "Captain Markis":
                if ability.misc_target_planet != planet_pos:
                    return False
            elif ability.action_chosen == "Suppressive Fire":
                if not ability.chosen_first_card:
                    other_player = player.get_other_player()
                    for i in range(len(other_player.cards_in_play[planet_pos + 1])):
                        if other_player.get_ready_given_pos(planet_pos, i):
                            if other_player.get_card_type_given_pos(planet_pos, i) != "Warlord":
                                return True
                    return False
                if ability.chosen_first_card:
                    if ability.misc_target_planet != planet_pos:
                        return False
            elif ability.action_chosen == "Kraktoof Hall":
                if not ability.chosen_first_card:
                    other_player = player.get_other_player()
                    if len(other_player.cards_in_play[planet_pos + 1]) + len(player.cards_in_play[planet_pos + 1]) < 2:
                        return False
                    if player.get_damage_given_pos(planet_pos, unit_pos) == 0:
                        return False
                if ability.chosen_first_card:
                    if ability.misc_target_planet != planet_pos:
                        return False
            elif ability.action_chosen == "Tellyporta Pad":
                if planet_pos == self.round_number:
                    return False
            elif ability.action_chosen == "Archon's Terror":
                if planet_pos == -2 and not player.get_ready_given_pos(planet_pos, unit_pos):
                    return False
                if player.get_unique_given_pos(planet_pos, unit_pos):
                    return False
            elif ability.action_chosen == "Squadron Redeployment":
                if planet_pos != -2 and self.count_planets_in_play() < 2:
                    return False
                if len(player.get_all_attachments_at_pos(planet_pos, unit_pos)) == 0:
                    return False
            elif ability.action_chosen == "Command-link Drone":
                if planet_pos == ability.get_planet_pos() and unit_pos == ability.get_unit_pos():
                    return False
        elif ability == "Planet":
            pass
    if targets and enemy_ability:
        if player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos, actual_check=False):
            return False
    return True


def check_if_single_card_in_hand_is_valid_target(self, ability, player, hand_pos, target_restrictions, planet_pos=-1, ability_type=""):
    faction_hand_card = target_restrictions["Faction"]
    card_type_hand_card = target_restrictions["Card Type"]
    max_cost_hand_card = target_restrictions["Max Cost"]
    payment_hand_card = target_restrictions["Payment"]
    card_enters_play = target_restrictions["Card Enters Play"]
    card = player.get_card_in_hand(hand_pos)
    if ability_type == "Reaction":
        if ability.get_reaction_name() == "Commander Shadowsun hand":
            if card.get_ability() == "Shadowsun's Stealth Cadre":
                return True
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


def find_all_valid_hand_locations_given_restrictions(self, ability, primary_player, secondary_player, target_restrictions, planet_pos=-1, ability_type=""):
    valid_moves = []
    for i in range(len(primary_player.cards)):
        if check_if_single_card_in_hand_is_valid_target(self, ability, primary_player, i, target_restrictions, planet_pos=planet_pos, ability_type=ability_type):
            valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
    return valid_moves


def check_if_single_card_in_discard_is_valid_target(self, ability, player, discard_pos, target_restrictions, planet_pos=-1, ability_type=""):
    faction_card = target_restrictions["Faction"]
    card_type_card = target_restrictions["Card Type"]
    max_cost_card = target_restrictions["Max Cost"]
    card_enters_play = target_restrictions["Card Enters Play"]
    card = player.get_card_in_discard(discard_pos)
    if ability_type == "Reaction":
        if ability.get_reaction_name() == "Commander Shadowsun discard":
            if card.get_ability() == "Shadowsun's Stealth Cadre":
                return True
    if faction_card:
        if faction_hand_card != card.get_faction():
            return False
    if card_type_card:
        if card_type_card != card.get_card_type():
            return False
    if max_cost_card:
        if card.get_cost() > max_cost_card:
            return False
    if card_enters_play:
        if not player.check_if_card_can_enter_play(card, planet_pos=planet_pos, triggered_card_effect=True):
            return False
    return True


def find_all_valid_discard_locations_given_restrictions(self, ability, primary_player, secondary_player, target_restrictions, planet_pos=-1, ability_type=""):
    valid_moves = []
    for i in range(len(primary_player.discard)):
        if check_if_single_card_in_discard_is_valid_target(self, ability, primary_player, i, target_restrictions, planet_pos=planet_pos, ability_type=ability_type):
            valid_moves = add_valid_move(valid_moves, primary_player, "IN_DISCARD", discard_pos=i)
    return valid_moves


def find_all_valid_unit_locations_given_restrictions(self, ability, primary_player, secondary_player, target_restrictions, planet_pos=-1):
    valid_moves = []
    own_unit = target_restrictions["Own Unit"]
    enemy_unit = target_restrictions["Enemy Unit"]
    if own_unit:
        for i in range(len(primary_player.headquarters)):
            if check_if_single_card_in_play_is_valid_target(self, ability, primary_player, -2, i, target_restrictions, misc_pla=planet_pos):
                valid_moves = add_valid_move(valid_moves, primary_player, "HQ", unit_pos=i)
        for i in range(7):
            for j in range(len(primary_player.cards_in_play[i + 1])):
                if check_if_single_card_in_play_is_valid_target(self, ability, primary_player, i, j, target_restrictions, misc_pla=planet_pos):
                    valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", planet_pos=i, unit_pos=j)
    if enemy_unit:
        for i in range(len(secondary_player.headquarters)):
            if check_if_single_card_in_play_is_valid_target(self, ability, secondary_player, -2, i, target_restrictions, enemy_ability=True, misc_pla=planet_pos):
                valid_moves = add_valid_move(valid_moves, secondary_player, "HQ", unit_pos=i)
        for i in range(7):
            for j in range(len(secondary_player.cards_in_play[i + 1])):
                if check_if_single_card_in_play_is_valid_target(self, ability, secondary_player, i, j, target_restrictions, enemy_ability=True, misc_pla=planet_pos):
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
                for unit_pos in range(len(primary_player.cards_in_play[planet_pos + 1])):
                    if primary_player.valid_nullify_unit(planet_pos, unit_pos):
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
            hand_disc = primary_player.search_hand_for_discounts(self.card_to_deploy.get_faction(), self.card_to_deploy.get_traits())
            if hand_disc > 0:
                if self.card_to_deploy.get_faction() == "Orks":
                    for i in range(len(primary_player.cards)):
                        if primary_player.cards[i] == "Bigga Is Betta":
                            valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
            if self.card_to_deploy.get_cost() <= primary_player.get_resources() - self.discounts_applied:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Deploy Turn":
            if self.mode == "ACTION" and self.card_to_deploy is None:
                valid_moves = detect_possible_actions(self, primary_player, secondary_player, combat_turn_action=True)
                if not valid_moves:
                    valid_moves = add_valid_move(valid_moves, primary_player, "pass")
            elif self.card_to_deploy is None:
                deploy_action_locations = detect_possible_actions(
                    self, primary_player, secondary_player, combat_turn_action=False
                )
                valid_moves = copy.copy(deploy_action_locations)
                for i in range(len(primary_player.cards)):
                    playability = primary_player.determine_playability(primary_player.cards[i])
                    if playability == "playable":
                        if not check_if_deploy_event_action_card_is_currently_legal(
                                self, primary_player, i, possible_deploy_actions=deploy_action_locations):
                            continue
                        valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
            else:
                selected_card = self.card_to_deploy
                selected_card_still_playable = True
                if selected_card.get_limited() and not primary_player.get_can_play_limited():
                    selected_card_still_playable = False
                if primary_player.determine_lowest_possible_cost_of_card(selected_card) > primary_player.get_resources():
                    selected_card_still_playable = False
                if selected_card_still_playable:
                    if selected_card.get_card_type() == "Army":
                        valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
                        non_attachs_that_can_be_played_as_attach = ["Gun Drones", "Shadowsun's Stealth Cadre",
                                                                    "Escort Drone"]
                        army_unit_as_attachment = selected_card.get_name() in non_attachs_that_can_be_played_as_attach
                        if army_unit_as_attachment:
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.check_if_can_attach_card(
                                        selected_card, -2, i, not_own_attachment=False):
                                    valid_moves = add_valid_move(valid_moves, primary_player, "HQ", unit_pos=i)
                            for i in range(7):
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.check_if_can_attach_card(
                                            selected_card, i, j, not_own_attachment=False):
                                        valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", planet_pos=i, unit_pos=j)
                            for i in range(len(secondary_player.headquarters)):
                                if secondary_player.check_if_can_attach_card(
                                        selected_card, -2, i, not_own_attachment=True):
                                    valid_moves = add_valid_move(valid_moves, secondary_player, "HQ", unit_pos=i)
                            for i in range(7):
                                for j in range(len(secondary_player.cards_in_play[i + 1])):
                                    if secondary_player.check_if_can_attach_card(
                                            selected_card, i, j, not_own_attachment=True):
                                        valid_moves = add_valid_move(valid_moves, secondary_player, "IN_PLAY", planet_pos=i, unit_pos=j)
                    if selected_card.get_card_type() == "Attachment":
                        if selected_card.planet_attachment:
                            for i in range(len(self.planets_in_play_array)):
                                if not self.planets_in_play_array[i]:
                                    continue
                                can_continue = True
                                if selected_card.get_ability() == "Trapped Objective" and i == self.round_number:
                                    can_continue = False
                                if selected_card.get_unique():
                                    if primary_player.search_for_unique_card(selected_card.get_name()):
                                        can_continue = False
                                if selected_card.get_limited():
                                    if not primary_player.get_can_play_limited():
                                        can_continue = False
                                if selected_card.limit_one_per_unit:
                                    for j in range(len(primary_player.attachments_at_planet[i])):
                                        if primary_player.attachments_at_planet[i][j].get_name() == selected_card.get_name():
                                            can_continue = False
                                if selected_card.red_required and not self.get_red_icon(i):
                                    can_continue = False
                                if selected_card.blue_required and not self.get_blue_icon(i):
                                    can_continue = False
                                if selected_card.green_required and not self.get_green_icon(i):
                                    can_continue = False
                                discounts = primary_player.search_hq_for_discounts("", "", is_attachment=True)
                                required_resources = selected_card.get_cost() - discounts
                                if required_resources < 0:
                                    required_resources = 0
                                if required_resources > primary_player.get_resources():
                                    can_continue = False
                                if can_continue:
                                    valid_moves = add_valid_move(valid_moves, None, "PLANETS", planet_pos=i)
                        else:
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.check_if_can_attach_card(
                                        selected_card, -2, i, not_own_attachment=False):
                                    valid_moves = add_valid_move(valid_moves, primary_player, "HQ", unit_pos=i)
                            for i in range(7):
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.check_if_can_attach_card(
                                            selected_card, i, j, not_own_attachment=False):
                                        valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", planet_pos=i,
                                                                     unit_pos=j)
                            for i in range(len(secondary_player.headquarters)):
                                if secondary_player.check_if_can_attach_card(
                                        selected_card, -2, i, not_own_attachment=True):
                                    valid_moves = add_valid_move(valid_moves, secondary_player, "HQ", unit_pos=i)
                            for i in range(7):
                                for j in range(len(secondary_player.cards_in_play[i + 1])):
                                    if secondary_player.check_if_can_attach_card(
                                            selected_card, i, j, not_own_attachment=True):
                                        valid_moves = add_valid_move(valid_moves, secondary_player, "IN_PLAY", planet_pos=i,
                                                                     unit_pos=j)
                if not valid_moves:
                    deploy_action_locations = detect_possible_actions(
                        self, primary_player, secondary_player, combat_turn_action=False
                    )
                    valid_moves = copy.copy(deploy_action_locations)
                    for i in range(len(primary_player.cards)):
                        playability = primary_player.determine_playability(primary_player.cards[i])
                        if playability == "playable":
                            if not check_if_deploy_event_action_card_is_currently_legal(
                                    self, primary_player, i, possible_deploy_actions=deploy_action_locations):
                                continue
                            valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
                    valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Commitment":
            valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
        elif self.what_is_required_automated == "Command not Commitment":
            if self.during_command_struggle:
                for i in range(len(primary_player.cards)):
                    if primary_player.cards[i] == "Superiority":
                        if primary_player.get_resources() > 0:
                            valid_moves = add_valid_move(valid_moves, primary_player, "HAND", hand_pos=i)
            elif self.after_command_struggle:
                valid_moves = detect_possible_actions(self, primary_player, secondary_player, combat_turn_action=False)
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Mobile":
            if self.misc_target_unit[0] != -1 and self.misc_target_unit[1] != -1:
                planet_pos = self.misc_target_unit[0]
                if planet_pos != 0:
                    if self.planets_in_play_array[planet_pos - 1]:
                        valid_moves = add_valid_move(valid_moves, primary_player, "PLANETS", planet_pos=planet_pos-1)
                if planet_pos != 6:
                    if self.planets_in_play_array[planet_pos + 1]:
                        valid_moves = add_valid_move(valid_moves, primary_player, "PLANETS", planet_pos=planet_pos+1)
            else:
                for planet_pos in range(7):
                    for unit_pos in range(len(primary_player.cards_in_play[planet_pos + 1])):
                        if primary_player.get_mobile_given_pos(planet_pos, unit_pos) and primary_player.get_available_mobile_given_pos(planet_pos, unit_pos):
                            valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", planet_pos=planet_pos, unit_pos=unit_pos)
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Bodyguard":
            valid_moves = primary_player.get_playable_borders()
        elif self.what_is_required_automated == "Indirect":
            valid_moves = primary_player.get_playable_borders()
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Outside Combat":
            valid_moves = detect_possible_actions(self, primary_player, secondary_player, combat_turn_action=False)
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Combat Turn":
            battle_planet = self.last_planet_checked_for_battle
            if self.attacker_planet == -1 or self.attacker_position == -1:
                for i in range(len(primary_player.cards_in_play[battle_planet + 1])):
                    if self.check_if_unit_can_be_declared_as_attacker(primary_player, secondary_player, battle_planet, i):
                        valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", battle_planet, i)
            else:
                for i in range(len(secondary_player.cards_in_play[battle_planet + 1])):
                    if self.check_if_unit_can_be_declared_as_defender(primary_player, secondary_player, battle_planet, i):
                        valid_moves = add_valid_move(valid_moves, secondary_player, "IN_PLAY", battle_planet, i)
                if primary_player.get_area_effect_given_pos(self.attacker_planet, self.attacker_position) > 0:
                    valid_moves = add_valid_move(valid_moves, primary_player, "PLANETS", planet_pos=battle_planet)
            if not valid_moves:
                valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Retreat Turn":
            battle_planet = self.last_planet_checked_for_battle
            for i in range(len(primary_player.cards_in_play[battle_planet + 1])):
                if primary_player.check_if_unit_can_retreat(battle_planet, i):
                    valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", battle_planet, i)
            valid_moves = add_valid_move(valid_moves, primary_player, "pass")
        elif self.what_is_required_automated == "Headquarters Action":
            valid_moves = detect_possible_actions(self, primary_player, secondary_player, combat_turn_action=False)
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
                if type_target == "In Play":
                    valid_moves = find_all_valid_unit_locations_given_restrictions(
                        self, planet_ability, primary_player, secondary_player, target_restrictions
                    )
                if type_target == "Hand":
                    valid_moves = find_all_valid_hand_locations_given_restrictions(
                        self, planet_ability, primary_player, secondary_player, target_restrictions, planet_pos=self.last_planet_checked_for_battle
                    )
                if type_target == "Planet":
                    valid_moves = add_valid_planets_as_valid_moves(self, valid_moves, primary_player, secondary_player,
                                                                   planet_ability, target_restrictions, misc_pla=misc_pla,
                                                                   unit_pla=self.misc_target_unit[0])
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
        elif self.what_is_required_automated == "Alt Shield":
            if self.alt_shield_name == "Glorious Intervention":
                valid_moves = primary_player.get_playable_borders()
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
                print("Target:", type_target)
                print("Restrictions:", target_restrictions)
                if type_target == "Special":
                    if self.action_object.action_chosen == "Khymera Den":
                        for i in range(7):
                            for j in range(len(primary_player.cards_in_play[i + 1])):
                                if primary_player.get_name_given_pos(i, j) == "Khymera":
                                    if primary_player.get_aiming_reticle_in_play(i, j) != "blue":
                                        valid_moves = add_valid_move(valid_moves, primary_player, "IN_PLAY", planet_pos=i, unit_pos=j)
                        for i in range(len(primary_player.headquarters)):
                            if primary_player.get_name_given_pos(-2, i) == "Khymera":
                                if primary_player.get_aiming_reticle_in_play(-2, i) != "blue":
                                    valid_moves = add_valid_move(valid_moves, primary_player, "HQ", unit_pos=i)
                    if self.action_object.misc_counter > 0:
                        valid_moves = add_active_planets_as_valid_moves(self, valid_moves)
                if type_target == "Hand":
                    valid_moves = find_all_valid_hand_locations_given_restrictions(
                        self, self.action_object, primary_player, secondary_player, target_restrictions, planet_pos=self.action_object.get_planet_pos()
                    )
                if type_target == "In Play":
                    valid_moves = find_all_valid_unit_locations_given_restrictions(
                        self, self.action_object, primary_player, secondary_player, target_restrictions, planet_pos=self.action_object.get_planet_pos()
                    )
                if type_target == "Planet":
                    if self.action_object.action_chosen == "Wildrider Squadron":
                        for i in range(7):
                            if not self.planets_in_play_array[i]:
                                continue
                            if abs(i - self.action_object.get_planet_pos()) == 1:
                                valid_moves = add_valid_move(valid_moves, None, "PLANETS", planet_pos=i)
                    else:
                        valid_moves = add_valid_planets_as_valid_moves(
                            self, valid_moves, primary_player, secondary_player, self.action_object.action_chosen,
                            target_restrictions, misc_pla=self.action_object.misc_target_planet
                        )
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
                if type_target == "In Play":
                    valid_moves = find_all_valid_unit_locations_given_restrictions(
                        self, self.reactions_needing_resolving[0], primary_player, secondary_player, target_restrictions
                    )
                if type_target == "Hand":
                    valid_moves = find_all_valid_hand_locations_given_restrictions(
                        self, self.reactions_needing_resolving[0], primary_player, secondary_player,
                        target_restrictions, planet_pos=self.reactions_needing_resolving[0].get_planet_pos(), ability_type="Reaction"
                    )
                    if current_reaction == "Banshee Power Sword":
                        valid_moves = add_valid_move(valid_moves, primary_player, "pass")
                if type_target == "Discard":
                    valid_moves = find_all_valid_discard_locations_given_restrictions(
                        self, self.reactions_needing_resolving[0], primary_player, secondary_player,
                        target_restrictions, planet_pos=self.reactions_needing_resolving[0].get_planet_pos(), ability_type="Reaction"
                    )
                if type_target == "Planet":
                    valid_moves = add_valid_planets_as_valid_moves(
                        self, valid_moves, primary_player, secondary_player, current_reaction, target_restrictions,
                        misc_pla=-1, unit_pla=self.reactions_needing_resolving[0].get_planet_pos())
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
                if type_target == "In Play":
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
