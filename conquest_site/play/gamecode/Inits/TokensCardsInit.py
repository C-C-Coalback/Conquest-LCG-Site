from .. import CardClasses


def tokens_cards_init():
    tokens_card_array = [CardClasses.TokenCard("Snotlings", "", "Runt.", "Orks", 1, 1),
                         CardClasses.TokenCard("Cultist", "Interrupt: When you deploy a Daemon unit, "
                                                          "sacrifice this unit to reduce its cost by 1.",
                                               "Cultist.", "Chaos", 1, 1, applies_discounts=[True, 1, False]),
                         CardClasses.TokenCard("Guardsmen", "", "Soldier.", "Guardsmen", 1, 2),
                         CardClasses.TokenCard("Khymera", "No Attachments.", "Creature.", "Dark Eldar", 2, 1),
                         CardClasses.TokenCard("Termagant", "", " Creature. Termagant.", "Tyranids", 1, 1)]
    return tokens_card_array
