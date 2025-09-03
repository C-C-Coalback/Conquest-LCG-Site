from .. import CardClasses


def apoka_errata_cards_init():
    apoka_errata_cards_array = [
        CardClasses.ArmyCard("Ba'ar Zul's Cleavers", "Action: Deal 2 damage to this unit to have it get +2 "
                                                     "ATK for its next attack this phase. (Limit once per phase)",
                             "Warrior. Khorne. World Eaters.", 2, "Chaos", "Signature",
                             2, 5, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Maksim's Squadron", "No Wargear Attachments.\n"
                                                  "Interrupt: When you use a shield card to "
                                                  "prevent this unit from taking "
                                                  "damage, that card gains 1 shield icon and you draw 1 card."
                                                  "(Limit once per phase.)",
                             "Vehicle. Tank. Vostroya.",
                             3, "Astra Militarum", "Signature", 2, 3, 1, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Captain Markis", "Action: Sacrifice an Astra Militarum unit "
                                               "at this planet to exhaust a target "
                                               "non-warlord unit at this planet. "
                                               "(Limit once per round.)",
                             "Soldier. Officer. Vostroya.", 3, "Astra Militarum", "Loyal", 2, 3, 2, True,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Death Serves the Emperor", "Interrupt: When a Vehicle unit you control is destroyed, "
                                                          "gain 2 resources.",
                              "Tactic.", 0, "Astra Militarum", "Common", 1, False),
        CardClasses.SupportCard("STC Fragment", "Limited.\n"
                                                "Interrupt: When you deploy an Elite unit, exhaust this support to "
                                                "reduce the cost of that unit by 2. Then exhaust that unit.", "Relic.",
                                1, "Neutral", "Common", True, limited=True, applies_discounts=[True, 2, False]),
        CardClasses.ArmyCard("Shrieking Harpy", "Flying.\n"
                                                "Combat Action: After this unit is declared as an attacker at an "
                                                "infested planet, exhaust each enemy non-Elite army unit and "
                                                "token unit at this planet. (Limit once per phase.)",
                             "Creature. Kraken. Elite.", 6, "Tyranids", "Common", 2, 5, 2, False, flying=True),
        CardClasses.SupportCard("Loamy Broodhive", "Reaction: After you deploy an Elite unit, exhaust this support to "
                                                   "put 2 Termagant tokens into play at the same planet as that unit.",
                                "Location.", 1, "Tyranids", "Common", True),
        CardClasses.SupportCard("Invasion Site", "Reaction: After an Elite unit you control is destroyed, "
                                                 "sacrifice this support to gain 3 resources. ", "Location.",
                                0, "Tyranids", "Common", True),
        CardClasses.ArmyCard("Syren Zythlex", "Forced Reaction: After an enemy unit is deployed at "
                                              "this planet, exhaust it. (Limit once per phase.)",
                             "Warrior. Wych.", 3, "Dark Eldar", "Loyal", 2, 3, 2, True),
        CardClasses.ArmyCard("Klaivex Warleader", "Ambush.\n"
                                                  "Reaction: After you deploy this unit during the combat phase, "
                                                  "destroy a target damaged army unit at this planet.", "Warrior.",
                             4, "Dark Eldar", "Loyal", 1, 3, 2, False, ambush=True,
                             allowed_phases_in_hand="COMBAT", action_in_hand=True),
        CardClasses.ArmyCard("Kabalite Blackguard", "Reaction: After you win a battle at this planet, "
                                                    "take up to 1 resources from your opponent.", "Warrior. Kabalite.",
                             2, "Dark Eldar", "Loyal", 2, 3, 0, False),
        CardClasses.EventCard("Gut and Pillage", "Reaction: After you win a battle at a Material planet (red), "
                                                 "gain 2 resources. (Max 1 per round.)", "Tactic.",
                              0, "Dark Eldar", "Common", 1, False),
        CardClasses.ArmyCard("Mighty Wraithknight", "No Wargear Attachments.\n"
                                                    "Reaction: After this unit enters play, exhaust 2 non-Spirit"
                                                    " units of each player at this planet.", "Vehicle. Spirit. Elite.",
                             6, "Eldar", "Common", 5, 5, 2, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Shrieking Exarch", "Reaction: After an army unit is destroyed at this planet, draw 1 card"
                                                 " and deal 1 damage to a target enemy unit. (Limit once per phase.)",
                             "Warrior. Elite.", 5, "Eldar", "Common", 4, 6, 2, False),
        CardClasses.EventCard("For the Tau'va", "Action: Ready a unit "
                                                "you control with 1 or more attachments.", "Tactic. Maneuver.",
                              2, "Tau", "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Kroot Hunter", "Reaction: After you deploy this unit at a "
                                             "Material planet (red), gain 1 resource.", "Scout. Ally. Kroot.",
                             1, "Tau", "Common", 2, 2, 0, False),
        CardClasses.ArmyCard("Ardent Auxiliaries", "This unit is an Astra Militarum unit in addition to Tau.\n"
                                                   "Reaction: After this unit commits to a planet, if you control an "
                                                   "Astra Militarum unit at this planet, ready this unit.", "Soldier.",
                             2, "Tau", "Signature", 2, 2, 1, False),
        CardClasses.SupportCard("Endless Legions", "Reaction: After a Necrons unit enters your discard pile from play, "
                                                   "exhaust this support and place 2 units from your discard pile at "
                                                   "the bottom of your deck to Rally 6 a Necrons unit with a printed "
                                                   "cost of 3 or lower, put it into play exhausted at a planet "
                                                   "where no battle is taking place.",
                                "Upgrade.", 1, "Necrons", "Common", False),
        CardClasses.ArmyCard("Brotherhood Justicar", "Unstoppable - The first time this unit is assigned damage this "
                                                     "turn, prevent 1 of that damage and place 1 faith on it.\n"
                                                     "Reaction: After you deploy this unit, place 2 faith among units "
                                                     "you control at this planet.", "Soldier. Grey Knights.",
                             3, "Space Marines", "Signature", 3, 3, 1, False, unstoppable=True),
        CardClasses.ArmyCard("Commander Bravestorm", "Reaction: After you attach a non-Drone attachment to a "
                                                     "unit at this planet, draw a card.", "Soldier. Pilot. Shas'o.",
                             3, "Tau", "Loyal", 2, 4, 1, False)
    ]
    return apoka_errata_cards_array
