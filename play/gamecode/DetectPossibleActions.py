def detect_possible_actions(game, primary_player, secondary_player):
    possible_action_locations = []
    for i in range(len(primary_player.cards)):
        card = game.preloaded_find_card(primary_player.cards[i])
        if card.get_has_action_while_in_hand():
            if card.get_allowed_phases_while_in_hand() == "All" or \
                    card.get_allowed_phases_while_in_hand() == game.phase:
                if card.get_ability() in primary_player.events_requiring_battle:
                    if game.check_if_battle_taking_place():
                        if card.get_cost(urien_relevant=primary_player.urien_relevant) <= primary_player.resources:
                            possible_action_locations.append("HAND/" + str(primary_player.number) + "/" + str(i))
                    else:
                        possible_action_locations.append("HAND/" + str(primary_player.number) + "/" + str(i))
    possible_action_locations.append("pass-P1")
    return possible_action_locations
