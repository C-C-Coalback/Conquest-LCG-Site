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
                             4, "Astra Militarum", "Loyal", 2, 3, 2, False),
        CardClasses.AttachmentCard("Planetary Defence Force", "Attach to a planet.\n"
                                                              "Each Guardsman token you control at this planet gains"
                                                              " the Ranged keyword.\n"
                                                              "Reaction: After a combat round ends at this planet, put"
                                                              " a Guardsman token into play under your control at this"
                                                              " planet.",
                                   "Fortification.", 3, "Astra Militarum", "Common", 1, False,
                                   planet_attachment=True),
        CardClasses.ArmyCard("Mars Pattern Hellhound", "While you control a token unit at this planet, "
                                                       "this unit cannot be routed. \n"
                                                       "Reaction: After an enemy unit moves to an adjacent planet, "
                                                       "move this unit to that planet.", "Vehicle. Tank. Vostroya.",
                             4, "Astra Militarum", "Common", 3, 5, 1, False),
        CardClasses.AttachmentCard("Scribe Servo-Skull", "Attach to a Tech-Priest unit. \n"
                                                         "Attached unit gains 1 command icon.\n"
                                                         "Action: Detach this card to have it become a Drone army unit "
                                                         "with 0 ATK, 1 HP and \"Action: Exhaust this unit to ready an"
                                                         " attachment at this planet.\"", "Drone.",
                                   1, "Astra Militarum", "Loyal", 2, False, required_traits="Tech-Priest",
                                   action_in_play=True, allowed_phases_in_play="ALL", extra_command=1),
        CardClasses.EventCard("Sudden Reinforcements", "Action: Exhaust a Transport unit you control to put into play "
                                                       "2 Guardsman tokens at the same planet.", "Tactic.",
                              1, "Astra Militarum", "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Unending Barrage", "Headquarters Action: Exhaust any number of Artillery cards you "
                                                  "control. For each card exhausted, deal 1 damage to a target "
                                                  "non-warlord unit in a player's headquarters.", "Tactic.",
                              1, "Astra Militarum", "Loyal", 2, False, action_in_hand=True,
                              allowed_phases_in_hand="HEADQUARTERS"),
        CardClasses.ArmyCard("Sicarian Infiltrator", "Deep Strike (2). You may Deep Strike this card as an Action "
                                                     "during the combat phase. \n"
                                                     "Reaction: After you Deep Strike this unit, place 2 faith on it.",
                             "Soldier. Skitarii.", 3, "Astra Militarum", "Loyal", 3, 2, 1, False, deepstrike=2),
        CardClasses.AttachmentCard("Spray and Pray", "Attach to a Soldier army unit. \n"
                                                     "Attached unit gains Sweep (X), where X is equal to its"
                                                     " printed ATK. \n"
                                                     "Forced Reaction: After damage assigned by this unit is prevented,"
                                                     " deal damage to this unit equal to the amount prevented.",
                                   "Tactic.", 1, "Astra Militarum", "Common", 1, False, required_traits="Soldier",
                                   type_of_units_allowed_for_attachment="Army")
    ]
    return blackstone_project_cards
