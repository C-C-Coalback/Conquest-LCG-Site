def find_card(card_to_find, card_array):
    i = 0
    while card_array[i].get_shields() != -1:
        print(card_array[i].get_name())
        if card_to_find.lower() == card_array[i].get_name().lower():
            # print("Card found! :", orks_card_array[i].get_name())
            return card_array[i]
        else:
            i = i + 1
    return card_array[i]
