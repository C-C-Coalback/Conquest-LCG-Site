from .. import Initfunctions


def command_phase(p_one, p_two, game_round):
    planet_array = Initfunctions.init_planet_cards()
    p_one.commit_warlord_step()
    p_two.commit_warlord_step()
    planet_num = game_round
    planets_counted = 0
    c_res = [0, 0, 0, 0]
    while planet_num < 7 and planets_counted < 5:
        result = resolve_command_struggle(planet_num, p_one, p_two)
        if result == 1:
            planet_name = p_one.get_planet_name_given_position(planet_num - 1)
            for letter in planet_name:
                if letter == "_":
                    planet_name = planet_name.replace(letter, " ")
            for i in range(len(planet_array)):
                if planet_name == planet_array[i].get_name():
                    c_res[0] += planet_array[i].get_resources()
                    c_res[1] += planet_array[i].get_cards()
        elif result == 2:
            planet_name = p_one.get_planet_name_given_position(planet_num - 1)
            for letter in planet_name:
                if letter == "_":
                    planet_name = planet_name.replace(letter, " ")
            for i in range(len(planet_array)):
                if planet_name == planet_array[i].get_name():
                    c_res[2] += planet_array[i].get_resources()
                    c_res[3] += planet_array[i].get_cards()
        planets_counted += 1
        planet_num += 1
    print("Player one gets", c_res[0], "resources from command struggle")
    p_one.add_resources(c_res[0])
    print("Player one gets", c_res[1], "cards from command struggle")
    for i in range(c_res[1]):
        p_one.draw_card()
    print("Player two gets", c_res[2], "resources from command struggle")
    p_two.add_resources(c_res[2])
    print("Player two gets", c_res[3], "cards from command struggle")
    for i in range(c_res[3]):
        p_two.draw_card()


def resolve_command_struggle(planet_num, p_one, p_two):
    p_one_command = p_one.count_command_at_planet(planet_num)
    p_two_command = p_two.count_command_at_planet(planet_num)
    if p_one_command > p_two_command:
        return 1
    elif p_one_command < p_two_command:
        return 2
    return 0