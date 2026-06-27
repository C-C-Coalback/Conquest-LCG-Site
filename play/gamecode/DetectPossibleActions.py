from .AbilityTargetsDictionary import action_ability_starts


def detect_possible_actions(game, primary_player, secondary_player, combat_turn_action=False):
    """
    Identifies any "Action:" effects that can be played in the current game-state.
    Does not return more standard elements such as which cards be deployed.

    :param game: the game
    :param primary_player: player with priority
    :param secondary_player: other player
    :param combat_turn_action: whether we are in a combat turn action window
    :return: possible action locations: list of strings of possible actions
    """


    possible_action_locations = []
    for i in range(len(primary_player.cards)):
        card = game.preloaded_find_card(primary_player.cards[i])
        if card.get_has_action_while_in_hand():
            if card.get_allowed_phases_while_in_hand() == "ALL" or \
                    card.get_allowed_phases_while_in_hand() == game.phase:
                if primary_player.get_ambush_of_card(card):
                    if primary_player.determine_playability(card.get_name()):
                        possible_action_locations = add_action(possible_action_locations, "HAND/" + str(primary_player.number) + "/" + str(i), combat_turn_action=combat_turn_action)
                elif card.get_cost(urien_relevant=primary_player.urien_relevant) <= primary_player.resources:
                    ability = card.get_ability()
                    if ability in action_ability_starts:
                        prereqs = action_ability_starts[ability]
                        if check_if_action_can_start(game, ability, prereqs, primary_player, secondary_player, card=card):
                            if ability in primary_player.events_requiring_battle:
                                if game.check_if_battle_taking_place():
                                    possible_action_locations = add_action(possible_action_locations, "HAND/" + str(primary_player.number) + "/" + str(i), combat_turn_action=combat_turn_action)
                            else:
                                possible_action_locations = add_action(possible_action_locations, "HAND/" + str(primary_player.number) + "/" + str(i), combat_turn_action=combat_turn_action)
    for i in range(len(primary_player.headquarters)):
        card = primary_player.get_card_given_pos(-2, i)
        if card.get_has_action_while_in_play():
            if card.get_allowed_phases_while_in_play() in [game.phase, "ALL"]:
                ability = primary_player.get_ability_given_pos(-2, i)
                if ability in action_ability_starts:
                    prereqs = action_ability_starts[ability]
                    if check_if_action_can_start(game, ability, prereqs, primary_player, secondary_player, planet_pos=-2, card=card):
                        possible_action_locations = add_action(possible_action_locations, "HQ/" + str(primary_player.number) + "/" + str(i), combat_turn_action=combat_turn_action)
        attachments = primary_player.get_all_attachments_at_pos(-2, i)
        for k in range(len(attachments)):
            card = attachments[k]
            if card.get_has_action_while_in_play():
                if card.get_allowed_phases_while_in_play() in [game.phase, "ALL"]:
                    ability = card.get_ability()
                    if ability in action_ability_starts:
                        prereqs = action_ability_starts[ability]
                        if check_if_action_can_start(game, ability, prereqs, primary_player, secondary_player, card=card, planet_pos=-2, attachment_pos=k):
                            possible_action_locations = add_action(possible_action_locations, "ATTACHMENT/HQ/" + str(primary_player.number) + "/" + str(i) + "/" + str(k), combat_turn_action=combat_turn_action)
    for i in range(7):
        for j in range(len(primary_player.cards_in_play[i + 1])):
            card = primary_player.get_card_given_pos(i, j)
            if card.get_has_action_while_in_play():
                if card.get_allowed_phases_while_in_play() in [game.phase, "ALL"]:
                    print("card has action and right phase")
                    ability = primary_player.get_ability_given_pos(i, j)
                    if ability in action_ability_starts:
                        prereqs = action_ability_starts[ability]
                        print("checking if action can start")
                        if check_if_action_can_start(game, ability, prereqs, primary_player, secondary_player, planet_pos=i, card=card):
                            possible_action_locations = add_action(possible_action_locations, "IN_PLAY/" + str(primary_player.number) + "/" + str(i) + "/" + str(j), combat_turn_action=combat_turn_action)
            attachments = primary_player.get_all_attachments_at_pos(i, j)
            for k in range(len(attachments)):
                card = attachments[k]
                if card.get_has_action_while_in_play():
                    if card.get_allowed_phases_while_in_play() in [game.phase, "ALL"]:
                        ability = card.get_ability()
                        if ability in action_ability_starts:
                            prereqs = action_ability_starts[ability]
                            if check_if_action_can_start(game, ability, prereqs, primary_player, secondary_player, card=card, planet_pos=i, attachment_pos=k):
                                possible_action_locations = add_action(possible_action_locations, "ATTACHMENT/IN_PLAY/" + str(primary_player.number) + "/" + str(i) + "/" + str(j) + "/" + str(k), combat_turn_action=combat_turn_action)
    if combat_turn_action:
        possible_action_locations.append("pass-P1")
    return possible_action_locations


def check_single_card_in_hand(game, action_ability, prereqs, primary_player, secondary_player, planet_pos, hand_pos):
    faction_hand_card = prereqs["Attributes Hand Card"]["Faction"]
    card_type_hand_card = prereqs["Attributes Hand Card"]["Card Type"]
    max_cost_hand_card = prereqs["Attributes Hand Card"]["Max Cost"]
    payment_hand_card = prereqs["Attributes Hand Card"]["Payment"]
    card_enters_play = prereqs["Attributes Hand Card"]["Card Enters Play"]
    card = primary_player.get_card_in_hand(hand_pos)
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
        is_deploy = prereqs["Attributes Hand Card"]["Payment Details"]["Deploy"]
        if is_deploy:
            if primary_player.determine_lowest_possible_cost_of_card(card) > primary_player.get_resources():
                return False
        else:
            if card.get_cost() > primary_player.get_resources():
                return False
    if card_enters_play:
        if not primary_player.check_if_card_can_enter_play(card, planet_pos=planet_pos, triggered_card_effect=True):
            return False
    return True


def check_single_card_in_play(game, action_ability, prereqs, primary_player, secondary_player, planet_pos, unit_pos, src_planet=-1):
    faction_card = prereqs["Attributes In Play Card"]["Faction"]
    card_type_card = prereqs["Attributes In Play Card"]["Card Type"]
    forbidden_card_type_card = prereqs["Attributes In Play Card"]["Forbidden Card Type"]
    must_be_same_planet = prereqs["Attributes In Play Card"]["Same Planet"]
    must_be_a_unit = prereqs["Attributes In Play Card"]["Must Be Unit"]
    special = prereqs["Special"]
    if must_be_same_planet:
        if src_planet != planet_pos:
            return False
    if must_be_a_unit:
        if not primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
            return False
    if faction_card:
        if not primary_player.check_if_faction_given_pos(planet_pos, unit_pos, faction_card):
            return False
    if card_type_card:
        if primary_player.get_card_type_given_pos(planet_pos, unit_pos) != card_type_card:
            return False
    elif forbidden_card_type_card:
        if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == forbidden_card_type_card:
            return False
    if special:
        if action_ability == "Preemptive Barrage":
            if primary_player.get_ranged_given_pos(planet_pos, unit_pos):
                return False
        if action_ability == "Tellyporta Pad":
            if planet_pos == game.round_number or not game.planets_in_play_array[game.round_number]:
                return False
        if action_ability == "Archon's Terror":
            if primary_player.get_unique_given_pos(planet_pos, unit_pos):
                return False
        if action_ability == "Squadron Redeployment":
            if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                return False
            if len(primary_player.get_all_attachments_at_pos(planet_pos, unit_pos)) == 0:
                return False
            if planet_pos != -2 and game.count_planets_in_play() < 2:
                return False
    return True


def check_if_action_can_start(game, action_ability, prereqs, primary_player, secondary_player, planet_pos=-1, card=None, attachment_pos=-1):
    requires_hand_card = prereqs["Requires Hand Card"]
    requires_in_play_card = prereqs["Requires In Play Card"]
    once_per_phase = prereqs["Once Per Phase"]
    ready_required = prereqs["Ready Required"]
    exhaust_required = prereqs["Exhaust Required"]
    special = prereqs["Special"]
    if ready_required:
        if card is None:
            return False
        if not card.get_ready():
            return False
    if exhaust_required:
        if card is None:
            return False
        if card.get_ready():
            return False
    if once_per_phase:
        if card is None:
            return False
        if card.get_once_per_phase_used():
            return False
    if special:
        if action_ability == "Tzeentch's Firestorm":
            if primary_player.get_resources() == 0:
                return False
        if action_ability == "Wildrider Squadron":
            if planet_pos == -2:
                return False
            if game.count_planets_in_play() <= 1:
                return False
            return True
        if action_ability == "Gift of Isha":
            for i in range(len(primary_player.discard)):
                card = game.preloaded_find_card(primary_player.discard[i])
                if card.get_card_type() == "Army" and card.get_faction() == "Eldar":
                    return True
            return False
        if action_ability == "Command-link Drone":
            if primary_player.get_resources() == 0:
                return False
            return primary_player.count_units_in_play_all() > 1
        if action_ability == "Even the Odds":
            for i in range(len(primary_player.headquarters)):
                attachments = primary_player.get_all_attachments_at_pos(-2, i)
                for j in range(len(attachments)):
                    for k in range(len(primary_player.headquarters)):
                        if i != k:
                            if primary_player.check_if_can_attach_card(attachments[j], -2, k):
                                return True
                    for k in range(7):
                        for l in range(len(primary_player.cards_in_play[k + 1])):
                            if primary_player.check_if_can_attach_card(attachments[j], k, l):
                                return True
            for i in range(7):
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    attachments = primary_player.get_all_attachments_at_pos(i, j)
                    for k in range(len(attachments)):
                        for l in range(len(primary_player.headquarters)):
                            if primary_player.check_if_can_attach_card(attachments[j], k, l):
                                return True
                        for l in range(7):
                            for m in range(len(primary_player.cards_in_play[l + 1])):
                                if i != l or j != m:
                                    if primary_player.check_if_can_attach_card(attachments[j], l, m):
                                        return True
            for i in range(len(secondary_player.headquarters)):
                attachments = secondary_player.get_all_attachments_at_pos(-2, i)
                for j in range(len(attachments)):
                    for k in range(len(secondary_player.headquarters)):
                        if i != k:
                            if secondary_player.check_if_can_attach_card(attachments[j], -2, k):
                                return True
                    for k in range(7):
                        for l in range(len(secondary_player.cards_in_play[k + 1])):
                            if secondary_player.check_if_can_attach_card(attachments[j], k, l):
                                return True
            for i in range(7):
                for j in range(len(secondary_player.cards_in_play[i + 1])):
                    attachments = secondary_player.get_all_attachments_at_pos(i, j)
                    for k in range(len(attachments)):
                        for l in range(len(secondary_player.headquarters)):
                            if secondary_player.check_if_can_attach_card(attachments[j], k, l):
                                return True
                        for l in range(7):
                            for m in range(len(secondary_player.cards_in_play[l + 1])):
                                if i != l or j != m:
                                    if secondary_player.check_if_can_attach_card(attachments[j], l, m):
                                        return True
            return False
        if action_ability == "Calculated Strike":
            for i in range(len(secondary_player.headquarters)):
                if secondary_player.headquarters[i].get_limited():
                    return True
                attachments = secondary_player.get_all_attachments_at_pos(-2, i)
                for k in range(len(attachments)):
                    if attachments[k].get_limited():
                        return True
            for i in range(7):
                for j in range(len(secondary_player.cards_in_play[i + 1])):
                    if secondary_player.cards_in_play[i + 1][j].get_limited():
                        return True
                    attachments = secondary_player.get_all_attachments_at_pos(i, j)
                    for k in range(len(attachments)):
                        if attachments[k].get_limited():
                            return True
            return False
    if requires_hand_card:
        for i in range(len(primary_player.cards)):
            if check_single_card_in_hand(game, action_ability, prereqs, primary_player, secondary_player, planet_pos, i):
                return True
    if requires_in_play_card:
        in_play_card_reqs = prereqs["Attributes In Play Card"]
        own_card = in_play_card_reqs["Own Unit"]
        enemy_card = in_play_card_reqs["Enemy Unit"]
        if own_card:
            if in_play_card_reqs["At Planet"]:
                for i in range(7):
                    for j in range(len(primary_player.cards_in_play[i + 1])):
                        if check_single_card_in_play(game, action_ability, prereqs, primary_player, secondary_player, i, j, src_planet=planet_pos):
                            return True
            if in_play_card_reqs["At HQ"]:
                for i in range(len(primary_player.headquarters)):
                    if check_single_card_in_play(game, action_ability, prereqs, primary_player, secondary_player, -2, i, src_planet=planet_pos):
                        return True
        if enemy_card:
            if in_play_card_reqs["At Planet"]:
                for i in range(7):
                    for j in range(len(secondary_player.cards_in_play[i + 1])):
                        if check_single_card_in_play(game, action_ability, prereqs, secondary_player, primary_player, i, j, src_planet=planet_pos):
                            return True
            if in_play_card_reqs["At HQ"]:
                for i in range(len(secondary_player.headquarters)):
                    if check_single_card_in_play(game, action_ability, prereqs, secondary_player, secondary_player, -2, i, src_planet=planet_pos):
                        return True
    if special:
        if action_ability == "Exterminatus":
            if game.round_number != 6:
                return True
        if action_ability == "Captain Markis":
            if planet_pos == -2:
                return False
            sac_unit_check = False
            for i in range(len(primary_player.cards_in_play[planet_pos + 1])):
                if primary_player.check_if_faction_given_pos(planet_pos, i, "Astra Militarum"):
                    if primary_player.get_card_type_given_pos(planet_pos, i) != "Warlord":
                        sac_unit_check = True
            if sac_unit_check:
                exhaustible_unit_check = False
                for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                    if secondary_player.get_ready_given_pos(planet_pos, i):
                        if secondary_player.get_card_type_given_pos(planet_pos, i) != "Warlord":
                            exhaustible_unit_check = True
                if exhaustible_unit_check:
                    return True
        if action_ability == "Suppressive Fire":
            for i in range(7):
                has_own_ready_unit = False
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    if primary_player.get_ready_given_pos(i, j):
                        has_own_ready_unit = True
                if has_own_ready_unit:
                    for j in range(len(secondary_player.cards_in_play[i + 1])):
                        if secondary_player.get_ready_given_pos(i, j):
                            if secondary_player.get_card_type_given_pos(i, j) != "Warlord":
                                if not secondary_player.get_immune_to_enemy_events(i, j):
                                    return True
        if action_ability == "Ravenous Flesh Hounds":
            if card.get_damage() == 0:
                return False
            for i in range(7):
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    if primary_player.check_for_trait_given_pos(i, j, "Cultist"):
                        return True
        if action_ability == "Khymera Den":
            for i in range(7):
                for j in range(len(primary_player.cards_in_play[i + 1])):
                    if primary_player.get_name_given_pos(i, j) == "Khymera":
                        return True
            for i in range(len(primary_player.headquarters)):
                if primary_player.get_name_given_pos(-2, i) == "Khymera":
                    return True
        if action_ability == "Haemonculus Tormentor":
            if primary_player.get_resources() > 0:
                return True
    if not special and not requires_hand_card and not requires_in_play_card:
        return True
    return False


def add_action(possible_action_locations, string_to_add, combat_turn_action=False):
    if not combat_turn_action:
        possible_action_locations.append("SPECIAL_ACTION_" + string_to_add)
    else:
        possible_action_locations.append(string_to_add)
    return possible_action_locations
