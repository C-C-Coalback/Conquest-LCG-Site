def find_card(card_to_find, card_array, card_dict=None):
    if card_dict is not None:
        if card_to_find in card_dict:
            return card_dict[card_to_find]
        return card_array[-1]
    i = 0
    while card_array[i].get_shields() != -1:
        if card_to_find == card_array[i].get_name():
            # print("Card found! :", orks_card_array[i].get_name())
            return card_array[i]
        else:
            i = i + 1
    return card_array[i]
