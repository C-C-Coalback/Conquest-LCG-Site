from .. import CardClasses


def planet_cards_init():
    planet_array = [
        CardClasses.PlanetCard("Plannum",
                               "Battle Ability: Move a non-warlord unit "
                               "you control to a planet of your choice.",
                               1, 1, False, True, True),
        CardClasses.PlanetCard("Atrox Prime", "Battle Ability: Deal 1 damage "
                                              "to each enemy unit at a target HQ or adjacent planet.",
                               1, 1, True, True, False),
        CardClasses.PlanetCard("Barlus", "Battle Ability: Discard 1 card at "
                                         "random from your opponent's hand.",
                               2, 0, False, False, True),
        CardClasses.PlanetCard("Elouith", "Battle Ability: Search the top 3 cards of your deck for a card. "
                                          "Add it to your hand, and place the remaining cards "
                                          "on the bottom of your deck in any order.", 2, 0, False, True,
                               False),
        CardClasses.PlanetCard("Carnath", "Battle Ability: Trigger the Battle ability "
                                          "of another planet in play",
                               1, 1, True, True, False),
        CardClasses.PlanetCard("Tarrus", "Battle Ability: If you control fewer units than your opponent, "
                                         "gain 3 resources or draw 3 cards.", 1, 1, True, False, True),
        CardClasses.PlanetCard("Osus IV", "Battle Ability: "
                                          "Take 1 resource from your opponent.", 0, 2, False, False, True),
        CardClasses.PlanetCard("Ferrin", "Battle Ability: Rout a target non-warlord unit.",
                               0, 2, True, False, False),
        CardClasses.PlanetCard("Y'varn", "Battle Ability: Each player puts a unit into play "
                                         "from his hand at his HQ.",
                               0, 1, True, True, True),
        CardClasses.PlanetCard("Iridial", "Battle Ability: Remove all damage from a target unit.",
                               1, 0, True, True, True),
        CardClasses.PlanetCard("Anshan", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Beckel", "", 1, 0, True, True, True),
        CardClasses.PlanetCard("Erida", "", 0, 1, True, True, True),
        CardClasses.PlanetCard("Excellor", "", 1, 1, False, True, True),
        CardClasses.PlanetCard("Jalayerid", "", 0, 2, True, False, False),
        CardClasses.PlanetCard("Jaricho", "", 1, 1, True, False, True),
        CardClasses.PlanetCard("Munos", "", 0, 2, False, False, True),
        CardClasses.PlanetCard("Navida Prime", "", 2, 0, False, False, True),
        CardClasses.PlanetCard("Nectavus XI", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Vargus", "", 2, 0, False, True, False),
        CardClasses.PlanetCard("Zarvoss Foundry", "", 1, 0, True, True, True),
        CardClasses.PlanetCard("Xenos World Tallin", "", 1, 1, False, True, True),
        CardClasses.PlanetCard("Mangeras", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Kunarog The Slave Market", "", 0, 2, True, False, False),
        CardClasses.PlanetCard("Ironforge", "", 2, 0, False, False, True),
        CardClasses.PlanetCard("Frontier World Jaris", "", 0, 1, True, True, True),
        CardClasses.PlanetCard("Daprian's Gate", "", 0, 2, False, False, True),
        CardClasses.PlanetCard("Craftworld Lugath", "", 2, 0, False, True, False),
        CardClasses.PlanetCard("Contaminated World Adracan", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Bhorsapolis The Decadent", "", 1, 1, True, False, True),
        CardClasses.PlanetCard("Wounded Scream", "", 1, 1, True, True, True),
        CardClasses.PlanetCard("Tool of Abolition", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("The Frozen Heart", "", 1, 0, True, True, True),
        CardClasses.PlanetCard("Petrified Desolations", "", 0, 2, True, False, False),
        CardClasses.PlanetCard("Immortal Sorrows", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Hell's Theet", "", 1, 1, False, True, True),
        CardClasses.PlanetCard("Freezing Tower", "", 0, 2, False, False, True),
        CardClasses.PlanetCard("Clipped Wings", "", 1, 1, True, False, True),
        CardClasses.PlanetCard("Beheaded Hope", "", 2, 0, False, False, True),
        CardClasses.PlanetCard("Baneful Veil", "", 2, 0, False, True, False),
        CardClasses.PlanetCard("Xorlom", "", 0, 2, False, False, True),
        CardClasses.PlanetCard("Selphini VII", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("New Vulcan", "", 1, 1, False, True, True),
        CardClasses.PlanetCard("Hissan XI", "", 2, 0, False, True, False),
        CardClasses.PlanetCard("Gareth Prime", "", 1, 0, True, True, True),
        CardClasses.PlanetCard("Erekiel", "", 2, 0, False, False, True),
        CardClasses.PlanetCard("Diamat", "", 1, 1, True, False, True),
        CardClasses.PlanetCard("Coradim", "", 0, 2, True, False, False),
        CardClasses.PlanetCard("Belis", "", 1, 1, True, True, True),
        CardClasses.PlanetCard("Agerath Minor", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Radex", "", 0, 1, True, True, True),
        CardClasses.PlanetCard("Langeran", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Josoon", "", 2, 0, False, True, False),
        CardClasses.PlanetCard("Ice World Hydras IV", "", 2, 0, False, False, True),
        CardClasses.PlanetCard("Heletine", "", 1, 1, True, False, True),
        CardClasses.PlanetCard("Fortress World Garid", "", 0, 2, True, False, False),
        CardClasses.PlanetCard("Fenos", "", 1, 1, False, True, True),
        CardClasses.PlanetCard("Essio", "", 1, 1, True, True, False),
        CardClasses.PlanetCard("Daemon World Ivandis", "", 0, 2, False, False, True),
        CardClasses.PlanetCard("Chiros The Great Bazaar", "", 1, 0, True, True, True),
        CardClasses.PlanetCard("Frontier World Egulth", "Activity: Exhaust a target army unit.\n"
                                                        "Battle: Put 1 Khymera token into play at each adjacent planet.",
                               1, 1, False, True, True),
        CardClasses.PlanetCard("Quarantined World Arkos",
                               "Activity: If you control no unit at this planet, draw a card.\n"
                               "Battle: Target army unit gains +1 ATK and HP.",
                               0, 2, True, False, False),
        CardClasses.PlanetCard("Mordatyne",
                               "Activity: Move a non-Elite army unit you control at this planet to an adjacent "
                               "planet.\n Battle: Rout a target army unit.", 2, 0, False, False, True),
        CardClasses.PlanetCard("Helvetis",
                               "Forced Activity: Flip a coin, on tails, each player deals 2 indirect damage among "
                               "units he controls at this planet. (Once for both players.)",
                               0, 2, False, False, True),
        CardClasses.PlanetCard("Zadruk Prime",
                               "Activity: Rally 6 a unit, deploy it at this planet, reducing its cost by 1.\n"
                               "Battle: Remove up to 3 damage among cards.",
                               1, 0, True, True, True),
        CardClasses.PlanetCard("Hostaryn XXI",
                               "Activity: Flip a coin, for each player, on tails: gain 1 Resource, on heads: "
                               "lose 1 Resource. \nBattle: Draw two cards.", 1, 1, True, True, False),
        CardClasses.PlanetCard("Deltadurne",
                               "Activity: If you control only units of your warlord's faction at this planet, draw "
                               "a card.\n Battle: Draw 1 card and gain 1 Resource.",
                               1, 1, True, True, False),
        CardClasses.PlanetCard("Caldera", "Activity: Deal 1 damage to an army unit.\n"
                                          "Battle: Your opponent must sacrifice an army unit.",
                               1, 1, True, False, True),
        CardClasses.PlanetCard("Hangyz", "Activity: Look at the top card of your deck, you may discard it.\n"
                                         "Battle: Give 1 command icon to an army unit.", 1, 1, True, True, True),
        CardClasses.PlanetCard("Forge World Dagon", "Activity: Remove 1 damage from your warlord.\n"
                                                    "Battle: Gain 2 Resources.", 2, 0, False, True, False),
        CardClasses.PlanetCard("FINAL CARD", "", -1, -1, False, False, False)
    ]
    return planet_array
