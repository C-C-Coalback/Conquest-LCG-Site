def find_card(card_to_find, card_array, card_dict=None):
    if card_dict is not None:
        if card_to_find in card_dict:
            return card_dict[card_to_find]
        return card_array[-1]
    i = 0
    while card_array[i].get_shields() != -1:
        if card_to_find.lower() == card_array[i].get_name().lower():
            return card_array[i]
        else:
            i = i + 1
    return card_array[-1]


def find_planet_card(card_to_find, planet_array):
    i = 0
    for i in range(len(planet_array)):
        print(planet_array[i].get_name())
        if card_to_find.lower() == planet_array[i].get_name().lower():
            return planet_array[i]
    return planet_array[len(planet_array) - 1]
