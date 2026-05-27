def detect_possible_actions(game, primary_player, secondary_player, combat_turn_action=False):
    possible_action_locations = []
    for i in range(len(primary_player.cards)):
        card = game.preloaded_find_card(primary_player.cards[i])
        if card.get_has_action_while_in_hand():
            if card.get_allowed_phases_while_in_hand() == "All" or \
                    card.get_allowed_phases_while_in_hand() == game.phase:
                if primary_player.get_ambush_of_card(card):
                    if primary_player.determine_playability(card.get_name()):
                        possible_action_locations = add_action(possible_action_locations, "HAND/" + str(primary_player.number) + "/" + str(i), combat_turn_action=combat_turn_action)
                elif card.get_cost(urien_relevant=primary_player.urien_relevant) <= primary_player.resources:
                    if card.get_ability() in primary_player.events_requiring_battle:
                        if game.check_if_battle_taking_place():
                            possible_action_locations = add_action(possible_action_locations, "HAND/" + str(primary_player.number) + "/" + str(i), combat_turn_action=combat_turn_action)
                    else:
                        possible_action_locations = add_action(possible_action_locations, "HAND/" + str(primary_player.number) + "/" + str(i), combat_turn_action=combat_turn_action)
    if combat_turn_action:
        possible_action_locations.append("pass-P1")
    return possible_action_locations


def add_action(possible_action_locations, string_to_add, combat_turn_action=False):
    if not combat_turn_action:
        possible_action_locations.append("SPECIAL_ACTION_" + string_to_add)
    else:
        possible_action_locations.append(string_to_add)
    return possible_action_locations
