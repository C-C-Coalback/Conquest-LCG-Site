import CardClasses


def planet_cards_init():
    planet_array = [CardClasses.PlanetCard("Plannum",
                                           "Battle Ability: Move a non-warlord unit "
                                           "you control to a planet of your choice.",
                                           1, 1, False, True, True,"Plannum"),
                    CardClasses.PlanetCard("Atrox Prime", "Battle Ability: Deal 1 damage "
                                                          "to each enemy unit at a target HQ or adjacent planet.",
                                           1, 1, True, True, False,"Atrox_Prime"),
                    CardClasses.PlanetCard("Barlus", "Battle Ability: Discard 1 card at "
                                                     "random from your opponent's hand.",
                                           2, 0, False, False, True, "Barlus"),
                    CardClasses.PlanetCard("Elouith", "Battle Ability: Search the top 3 cards of your deck for a card. "
                                                      "Add it to your hand, and place the remaining cards "
                                                      "on the bottom of your deck in any order.", 2, 0, False, True,
                                           False, "Elouith"),
                    CardClasses.PlanetCard("Carnath", "Battle Ability: Trigger the Battle ability "
                                                      "of another planet in play",
                                           1, 1, True, True, False, "Carnath"),
                    CardClasses.PlanetCard("Tarrus", "Battle Ability: If you control fewer units than your opponent, "
                                                     "gain 3 resources or draw 3 cards.", 1, 1, True, False, True,
                                           "Tarrus"),
                    CardClasses.PlanetCard("Osus IV", "Battle Ability: "
                                                      "Take 1 resource from your opponent.", 0, 2, False, False, True,
                                           "Osus_IV"),
                    CardClasses.PlanetCard("Ferrin", "Battle Ability: Rout a target non-warlord unit.",
                                           0, 2, True, False, False, "Ferrin"),
                    CardClasses.PlanetCard("Y'varn", "Battle Ability: Each player puts a unit into play "
                                                     "from his hand at his HQ.",
                                           0, 1, True, True, True, "Y'varn"),
                    CardClasses.PlanetCard("Iridial", "Battle Ability: Remove all damage from a target unit.",
                                           1, 0, True, True, True, "Iridial"),
                    CardClasses.PlanetCard("FINAL CARD", "", -1, -1, False, False, False, "NO IMAGE")]
    return planet_array
