from .. import CardClasses


def blackstone_errata_cards_init():
    blackstone_errata_cards_array = [
        CardClasses.ArmyCard("Ardent Auxiliaries", "This unit is an Astra Militarum unit in addition to Tau.\n"
                                                   "Reaction: After this unit commits to a planet, if you control an "
                                                   "Astra Militarum unit at this planet, ready this unit.", "Soldier.",
                             2, "Tau", "Signature", 2, 2, 1, False),
        CardClasses.ArmyCard("Ba'ar Zul's Cleavers", "Action: Deal 2 damage to this unit to have it get +2 "
                                                     "ATK for its next attack this phase. (Limit once per phase)",
                             "Warrior. Khorne. World Eaters.", 2, "Chaos", "Signature",
                             2, 5, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Commander Bravestorm", "Reaction: After you attach a non-Drone attachment to a "
                                                     "unit at this planet, draw a card. (Limit once per phase)",
                             "Soldier. Pilot. Shas'o.",
                             3, "Tau", "Loyal", 2, 4, 1, True),
        CardClasses.EventCard("Death Serves the Emperor", "Interrupt: When a Vehicle unit you control is destroyed, "
                                                          "gain resources equal to its printed cost. Max 1 per round.",
                              "Tactic.", 2, "Astra Militarum", "Common", 1, False),
        CardClasses.SupportCard("Endless Legions", "Reaction: After a Necrons unit enters your discard pile from play, "
                                                   "exhaust this support and place 2 units from your discard pile at "
                                                   "the bottom of your deck to Rally 6 a Necrons unit with a printed "
                                                   "cost of 3 or lower, put it into play exhausted at a planet "
                                                   "where no battle is taking place.",
                                "Upgrade.", 1, "Necrons", "Common", False),
        CardClasses.EventCard("Gut and Pillage", "Reaction: After you win a battle at a Material planet (red), "
                                                 "gain 3 resources.", "Tactic.",
                              0, "Dark Eldar", "Common", 1, False, limited=True),
        CardClasses.SupportCard("Invasion Site", "Reaction: After an Elite unit you control is destroyed, "
                                                 "sacrifice this support to gain 3 resources. ", "Location.",
                                0, "Tyranids", "Common", True),
        CardClasses.ArmyCard("Klaivex Warleader", "Ambush.\n"
                                                  "Reaction: After you deploy this unit during the combat phase, "
                                                  "destroy a target damaged army unit at this planet.", "Warrior.",
                             4, "Dark Eldar", "Loyal", 1, 3, 2, False, ambush=True,
                             allowed_phases_in_hand="COMBAT", action_in_hand=True),
        CardClasses.ArmyCard("Kroot Hunter", "Reaction: After you deploy this unit at a "
                                             "Material planet (red), gain 1 resource.", "Scout. Ally. Kroot.",
                             1, "Tau", "Common", 2, 2, 0, False),
        CardClasses.ArmyCard("Maksim's Squadron", "No Wargear Attachments.\n"
                                                  "Interrupt: When you use a shield card to "
                                                  "prevent this unit from taking "
                                                  "damage, that card gains 1 shield icon and you draw 1 card."
                                                  "(Limit once per phase.)",
                             "Vehicle. Tank. Vostroya.",
                             3, "Astra Militarum", "Signature", 2, 3, 1, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Shrieking Exarch", "Reaction: After an army unit is destroyed at this planet, draw 1 card"
                                                 " and deal 1 damage to a target enemy unit. (Limit once per phase.)",
                             "Warrior. Elite.", 5, "Eldar", "Common", 4, 6, 2, False),
        CardClasses.ArmyCard("Genestealer Hybrids", "Cannot be deployed from your hand.\n"
                                                    "Each other unit you control at this planet "
                                                    "cannot be damaged by Area Effect.\n"
                                                    "This unit must be declared as a defender, if able.",
                             "Hybrid. Genestealer.", 2, "Tyranids", "Signature", 2, 2, 1, False),
        CardClasses.ArmyCard("Triarch Stalkers Procession", "No Wargear Attachments.\n"
                                                            "Forced Reaction: After this unit enters play, "
                                                            "have your opponent draw 2 cards.", "Vehicle.",
                             3, faction, "Common", 4, 6, 2, False, wargear_attachments_permitted=False),
        CardClasses.SupportCard("Imperial Bastion", "Your warlord's ability can trigger twice "
                                                    "per round instead of once.", "Location. Genestealer.",
                                1, faction, "Signature", False),
    ]
    return blackstone_errata_cards_array
