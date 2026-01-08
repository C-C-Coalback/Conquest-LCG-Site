from .. import CardClasses


def blackstone_project_cards_init():
    blackstone_project_cards = [
        CardClasses.ArmyCard("Sicarian Ruststalker", "Armorbane.",
                             "Soldier. Skitarii.", 2, "Astra Militarum", "Common",
                             2, 2, 1, False, armorbane=True),
        CardClasses.WarlordCard("Forge Master Dominus", "Each unit you control with a blank text box gets"
                                                        " +1 ATK and +1 HP.\n Reaction: After you deploy a Vehicle"
                                                        " unit, treat its printed text box as blank until the end "
                                                        "of the game", "Tech-Priest.",
                                "Astra Militarum", 2, 7, 2, 6,
                                "Bloodied. \nForced Reaction: After you deploy a Vehicle unit, treat its printed"
                                " text box as blank until the end of the game.", 7, 7,
                                ["1x Dominus' Forge", "2x Devoted Enginseer",
                                 "2x Kastelan Crusher", "1x Servo-Harness",
                                 "2x Omnissiah's Blessing"]
                                ),
        CardClasses.ArmyCard("Devoted Enginseer", "Reaction: After a combat round begins at this planet, exhaust this"
                                                  " unit to place up to 3 Faith among Vehicle and Tech-Priest units"
                                                  " at this planet.", "Tech-Priest.",
                             2, "Astra Militarum", "Signature", 0, 3, 1, False),
        CardClasses.ArmyCard("Kastelan Crusher", "No Wargear Attachments.\n"
                                                 "This unit gains Sweep (3) while it has Faith.", "Vehicle.",
                             3, "Astra Militarum", "Signature", 3, 4, 0, False, wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("Servo-Harness", "Attach to your warlord. \n"
                                                    "Faith tokens on this unit are not removed during the HQ phase. \n"
                                                    "Reaction: After the combat phase ends, move all Faith tokens from "
                                                    "Vehicle units you control to attached unit.",
                                   "Bionics.", 1, "Astra Militarum", "Signature", 3, False,
                                   type_of_units_allowed_for_attachment="Warlord", must_be_own_unit=True),
        CardClasses.EventCard("Omnissiah's Blessing", "Combat Action: Ready a Vehicle or Tech-Priest unit you control "
                                                      "with Faith. Then place 1 Faith on it.",
                              "Tactic. Blessing.", 1, "Astra Militarum", "Signature", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.SupportCard("Dominus' Forge", "Each Astra Militarum Vehicle unit you control "
                                                  "that has Faith gets +1 ATK. \n"
                                                  "Reaction: After you deploy a Vehicle unit, place 1 Faith "
                                                  "token on it.",
                                "Location.", 2, "Astra Militarum", "Signature", False),
        CardClasses.SupportCard("Administratum Office", "Each unit you control with no printed command icons gains "
                                                        "1 command icon.",
                                "Location.", 2, "Astra Militarum", "Loyal", True),
        CardClasses.ArmyCard("Amalgamated Devotee", "This unit gets +1 ATK and +2 HP for each attachment on it. \n"
                                                    "While this unit has 2 or more attachments it gains"
                                                    " \"Immune to enemy events.\"", "Tech-Priest.",
                             4, "Astra Militarum", "Loyal", 2, 3, 2, False)
    ]
    return blackstone_project_cards
