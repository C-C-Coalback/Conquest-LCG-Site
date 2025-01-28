# import pygame
# from FindCard import find_card


def resolve_planet_battle_effect(p_win, p_lose, planet_id):
    planet_name = p_win.get_planet_name_given_position(planet_id)
    print("Resolve battle ability:")
    print(planet_name)
    if planet_name == "Osus_IV" or planet_name == "Osus IV":
        osus_iv_ability(p_win, p_lose)
    elif planet_name == "Iridial":
        iridial_ability(p_win, p_lose)
    elif planet_name == "Plannum":
        plannum_ability(p_win, p_lose)
    elif planet_name == "Tarrus":
        tarrus_ability(p_win, p_lose)
    elif planet_name == "Y'varn":
        yvarn_ability(p_win, p_lose)
    elif planet_name == "Barlus":
        barlus_ability(p_lose)
    elif planet_name == "Ferrin":
        ferrin_ability(p_win, p_lose)
    elif planet_name == "Carnath":
        carnath_ability(p_win, p_lose)
    elif planet_name == "Elouith":
        elouith_ability(p_win, p_lose)
    elif planet_name == "Atrox_Prime" or planet_name == "Atrox Prime":
        atrox_prime_ability(p_win, p_lose, planet_id)


def osus_iv_ability(p_win, p_lose):
    print("Osus IV ability")
    if p_lose.spend_resources(1):
        p_win.add_resources(1)


def iridial_ability(p_win, p_lose):
    print("Iridial ability")
    """pos_unit, pos_planet = ClickDetection.prompt_pos_unit_anywhere(p_win, game_screen)
    if pos_unit != -1 and pos_planet != -1:
        p_win.remove_damage_from_pos(pos_planet, pos_unit, 999)
    if pos_unit != -1 and pos_planet == -1:
        p_win.remove_damage_from_pos_headquarters(pos_unit, 999)"""


def plannum_ability(p_win, p_lose):
    print("Plannum ability")
    """pos_unit, pos_planet = ClickDetection.prompt_pos_unit_anywhere(p_win, game_screen, pygame.Color("blue"))
    if pos_unit != -1 and pos_planet != -1:
        if p_win.get_cards_in_play()[pos_planet + 1][pos_unit].get_card_type() == "Warlord":
            print("Unit is a Warlord, movement forbidden with Plannum")
        else:
            target_planet = ClickDetection.prompt_pos_planet()
            p_win.move_unit_from_planet_to_planet(pos_unit, pos_planet, target_planet)
    if pos_unit != -1 and pos_planet == -1:
        if p_win.get_headquarters()[pos_unit] == "Warlord" or p_win.get_headquarters()[pos_unit] == "Support":
            print("Unit is a Warlord / Support, movement forbidden with Plannum")
        else:
            target_planet = ClickDetection.prompt_pos_planet()
            p_win.move_unit_from_hq_to_planet(pos_unit, target_planet)"""


def tarrus_ability(p_win, p_lose):
    print("Tarrus ability")
    """if p_win.count_number_units_in_play() < p_lose.count_number_units_in_play():
        choice = ClickDetection.prompt_two_choices(p_win, game_screen, ["Resources", "Cards"])
        if choice == 1:
            p_win.add_resources(3)
        elif choice == 2:
            p_win.draw_card()
            p_win.draw_card()
            p_win.draw_card()"""


def yvarn_ability(p_win, p_lose):
    print("Y'varn ability")
    """position = ClickDetection.prompt_pos_hand(p_win)
    if position != -1:
        object_holder = find_card(p_win.get_cards()[position])
        if p_win.play_unit_without_cost(object_holder, True):
            print("Card played")
    position = ClickDetection.prompt_pos_hand(p_lose)
    if position != -1:
        object_holder = find_card(p_lose.get_cards()[position])
        if p_lose.play_unit_without_cost(object_holder, True) == 0:
            print("Card played")"""


def barlus_ability(p_lose):
    print("Barlus ability")
    # p_lose.random_discard_from_hand()


def ferrin_ability(p_win, p_lose):
    print("Ferrin ability")
    """p_no, unit_pos, planet_pos = prompt_pos_unit_anywhere_all_players(p_win, p_lose, game_screen)
    if p_no == p_win.get_number():
        if unit_pos != -1 and planet_pos != -1:
            if p_win.get_cards_in_play()[planet_pos + 1][unit_pos].get_card_type() == "Warlord":
                print("Unit is a Warlord, routing with Ferrin forbidden")
            else:
                p_win.rout_unit_from_planet(planet_pos, unit_pos)
        elif unit_pos != -1 and planet_pos == -1:
            if p_win.get_headquarters()[unit_pos] == "Warlord" or p_win.get_headquarters()[unit_pos] == "Support":
                print("Card is Warlord / Support, routing with Ferrin forbidden")
            else:
                p_win.exhaust_card_in_hq()
    else:
        if unit_pos != -1 and planet_pos != -1:
            if p_lose.get_cards_in_play()[planet_pos + 1][unit_pos].get_card_type() == "Warlord":
                print("Unit is a Warlord, routing with Ferrin forbidden")
            else:
                p_lose.rout_unit_from_planet(planet_pos, unit_pos)
        elif unit_pos != -1 and planet_pos == -1:
            if p_lose.get_headquarters()[unit_pos] == "Warlord" or p_lose.get_headquarters()[unit_pos] == "Support":
                print("Card is Warlord / Support, routing with Ferrin forbidden")
            else:
                p_lose.exhaust_card_in_hq(unit_pos)"""


def carnath_ability(p_win, p_lose):
    print("Carnath ability")
    """pos_planet = ClickDetection.prompt_pos_planet()
    resolve_planet_battle_effect(p_win, p_lose, pos_planet, game_screen)"""


def elouith_ability(p_win, p_lose):
    print("Elouith ability")
    """card_names = p_win.top_n_cards(3)
    print(card_names)
    choice = ClickDetection.prompt_n_choices(p_win, game_screen, card_names)
    p_win.draw_card_from_position_deck(choice)"""


def atrox_prime_ability(p_win, p_lose, pos_planet):
    print("Atrox Prime ability")
    """target_planet = ClickDetection.prompt_pos_planet()
    if abs(target_planet - pos_planet) == 1:
        print("Planet in range of Atrox Prime")
        p_lose.suffer_area_effect_at_planet(p_win, 1, target_planet, game_screen)
    else:
        print("Target invalid")"""
