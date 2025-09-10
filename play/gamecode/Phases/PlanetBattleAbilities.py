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
    if p_lose.spend_resources(1):
        p_win.add_resources(1)


def iridial_ability(p_win, p_lose):
    print("Iridial ability")


def plannum_ability(p_win, p_lose):
    print("Plannum ability")


def tarrus_ability(p_win, p_lose):
    print("Tarrus ability")


def yvarn_ability(p_win, p_lose):
    print("Y'varn ability")


def barlus_ability(p_lose):
    print("Barlus ability")


def ferrin_ability(p_win, p_lose):
    print("Ferrin ability")


def carnath_ability(p_win, p_lose):
    print("Carnath ability")


def elouith_ability(p_win, p_lose):
    print("Elouith ability")


def atrox_prime_ability(p_win, p_lose, pos_planet):
    print("Atrox Prime ability")
