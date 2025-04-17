def find_card(card_to_find, card_array):
    i = 0
    print(card_to_find)
    while card_array[i].get_shields() != -1:
        # print(card_array[i].get_name())
        if card_to_find.lower() == card_array[i].get_name().lower():
            print("Card found! :", card_array[i].get_name())
            return card_array[i]
        else:
            i = i + 1
    print("Card not found")
    return card_array[i]


def find_planet_card(card_to_find, planet_array):
    i = 0
    for i in range(len(planet_array)):
        print(planet_array[i].get_name())
        if card_to_find.lower() == planet_array[i].get_name().lower():
            return planet_array[i]
    return planet_array[len(planet_array) - 1]
