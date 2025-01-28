from .PlanetBattleAbilities import resolve_planet_battle_effect

"""
def select_attacker(attacker, planet_id):
    attacker.extra_text = "Combat turn\nChoose Attacker"
    attacker.set_turn(True)
    while True:
        attacker.c.acquire()
        attacker.c.notify_all()
        current_active = attacker.position_activated
        attacker.c.release()
        print(current_active)
        if len(current_active) == 1:
            if current_active[0] == "PASS":
                return -1
        if len(current_active) == 4:
            if current_active[1] == "PLAY":
                if int(current_active[0][1]) == attacker.get_number():
                    print("Correct player and is in play. Advancing.")
                    pos_planet = int(current_active[2])
                    if pos_planet == planet_id:
                        print("Correct planet.")
                        pos_unit = int(current_active[3])
                        if len(attacker.get_cards_in_play()[planet_id + 1]) > pos_unit:
                            print("Valid unit.")
                            if attacker.check_ready_pos(planet_id, pos_unit):
                                print("Unit is ready. Selecting as attacker")
                                pos_attacker = pos_unit
                                attacker.exhaust_given_pos(planet_id, pos_attacker)
                                return pos_attacker

def select_defender(attacker, defender, planet_id):
    attacker.extra_text = "Combat turn\nChoose Defender"
    attacker.set_turn(True)
    while True:
        pygame.time.wait(500)
        attacker.c.acquire()
        attacker.c.notify_all()
        current_active = attacker.position_activated
        attacker.c.release()
        print(current_active)
        if len(current_active) == 4:
            if current_active[1] == "PLAY":
                if int(current_active[0][1]) == defender.get_number():
                    print("Correct player and is in play. Advancing.")
                    pos_planet = int(current_active[2])
                    if pos_planet == planet_id:
                        print("Correct planet.")
                        pos_unit = int(current_active[3])
                        if len(defender.get_cards_in_play()[planet_id + 1]) > pos_unit:
                            print("Valid unit. Selecting as defender,")
                            pos_defender = pos_unit
                            return pos_defender

def unit_attacks_unit(att, defe, planet_id, att_pos, defe_pos):
    att.set_turn(False)
    defe.set_turn(True)
    attack_value = att.get_attack_given_pos(planet_id, att_pos)
    # if att.get_cards_in_play()[planet_id + 1][att_pos].get_name() == "Tankbusta Bommaz":
    #     if defe.get_cards_in_play()[planet_id + 1][defe_pos].check_for_a_trait("Vehicle."):
    #         attack_value = 2 * attack_value
    damage_too_great = defe.assign_damage_to_pos(planet_id, defe_pos, attack_value)
    att.set_turn(True)
    defe.set_turn(False)
    if damage_too_great:
        print("Card must be discarded")
        # input("Hold attack")
        return 1
    # input("Hold attack")
    return 0

def combat_turn(attacker, defender, planet_id):
    print(attacker.get_name_player(), "\'s turn to attack")
    attacker.position_activated = []
    attacker.set_turn(True)
    defender.position_activated = []
    defender.set_turn(False)
    pos_attacker = select_attacker(attacker, planet_id)
    if pos_attacker == -1:
        return True
    pos_defender = select_defender(attacker, defender, planet_id)
    # input("COMBAT TURN:" + str(pos_attacker) + "ATTACKS" + str(pos_defender))
    unit_dead = unit_attacks_unit(attacker, defender, planet_id, pos_attacker, pos_defender)
    if unit_dead:
        if defender.check_if_warlord(planet_id, pos_defender):
            defender.bloody_warlord_given_pos(planet_id, pos_defender)
        else:
            defender.add_card_in_play_to_discard(planet_id, pos_defender)
    return False




def determine_combat_initiative(p_one, p_two, planet_id):
    p_one_has_warlord = p_one.check_for_warlord(planet_id)
    p_two_has_warlord = p_two.check_for_warlord(planet_id)
    if p_one_has_warlord == p_two_has_warlord:
        return p_one.get_initiative()
    return p_one_has_warlord

def combat_round(p_one, p_two, planet_id):
    planet_name = p_one.get_planet_name_given_position(planet_id - 1)
    p_one_passed = False
    p_two_passed = False
    print("Both have units present. Combat round begins at:", planet_name)
    print(p_one.get_name_player(), "units:")
    p_one.print_cards_at_planet(planet_id)
    print(p_two.get_name_player(), "units:")
    p_two.print_cards_at_planet(planet_id)
    while not p_one_passed or not p_two_passed:
        if determine_combat_initiative(p_one, p_two, planet_id):
            p_one.set_turn(True)
            p_two.set_turn(False)
            p_one_passed = combat_turn(p_one, p_two, planet_id)
            p_two_passed = combat_turn(p_two, p_one, planet_id)
        else:
            p_one.set_turn(False)
            p_two.set_turn(True)
            p_two_passed = combat_turn(p_two, p_one, planet_id)
            p_one_passed = combat_turn(p_one, p_two, planet_id)
    p_one.ready_all_at_planet(planet_id)
    p_two.ready_all_at_planet(planet_id)
    if determine_combat_initiative(p_one, p_two, planet_id):
        p_one.set_turn(True)
        p_two.set_turn(False)
        p_one.retreat_combat_window(planet_id)
        p_two.retreat_combat_window(planet_id)
    else:
        p_one.set_turn(False)
        p_two.set_turn(True)
        p_two.retreat_combat_window(planet_id)
        p_one.retreat_combat_window(planet_id)


def resolve_battle(p_one, p_two, planet_id, first_planet):
    player_one_check = p_one.check_if_units_present(planet_id)
    player_two_check = p_two.check_if_units_present(planet_id)
    while player_one_check and player_two_check:
        print("Combat round happens!")
        combat_round(p_one, p_two, planet_id)
        player_one_check = p_one.check_if_units_present(planet_id)
        player_two_check = p_two.check_if_units_present(planet_id)
    if player_one_check and not player_two_check:
        print(p_one.get_name_player(), "has units,", p_two.get_name_player(), "doesn't")
        print(p_two.get_name_player(), "wins the battle")
        resolve_planet_battle_effect(p_one, p_two, planet_id)
        if first_planet:
            p_one.retreat_all_at_planet(planet_id)
            p_one.capture_planet(planet_id)
    elif not player_one_check and player_two_check:
        print(p_two.get_name_player(), "has units,", p_one.get_name_player(), "doesn't")
        print(p_two.get_name_player(), "wins the battle")
        resolve_planet_battle_effect(p_two, p_one, planet_id)
        if first_planet:
            p_two.retreat_all_at_planet(planet_id)
            p_two.capture_planet(planet_id)
        elif not player_one_check and not player_two_check:
            print("Neither player has units")
    if first_planet:
        p_one.toggle_planet_in_play(planet_id)
        p_two.toggle_planet_in_play(planet_id)

def check_for_battle(p_one, p_two, planet_id, first_planet):
    planet_name = p_one.get_planet_name_given_position(planet_id - 1)
    print("Check for battle at:", planet_name)
    if first_planet:
        print(planet_name, "is first planet. Resolve battle")
        resolve_battle(p_one, p_two, planet_id - 1, first_planet)
    else:
        print(planet_name, "is not first planet. Check warlords")
        if p_one.check_for_warlord(planet_id - 1) or p_two.check_for_warlord(planet_id - 1):
            print("Battle is resolved at:", planet_name)
            resolve_battle(p_one, p_two, planet_id - 1, first_planet)

"""


def combat_phase(p_one, p_two, round_number):
    p_one.set_phase("Combat")
    p_two.set_phase("Combat")
    index = round_number
    planets_counted = 0
    first_planet = True
    while planets_counted < 5 and index < 7:
        check_for_battle(p_one, p_two, index, first_planet)
        first_planet = False
        index += 1
        planets_counted += 1
