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
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.EventCard("Lucky Shot", "Action: Until the end of the phase, a target Ranged unit gets +1 "
                                            "ATK and Armorbane.", "Tactic.", 1, "Astra Militarum", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Imperial Fists Legion", "Reaction: After this unit is declared as an attacker, remove 1 "
                                                      "damage from a target support card.", "Soldier. Imperial Fists.",
                             1, "Space Marines", "Common", 1, 2, 1, False),
        CardClasses.EventCard("Righteous Reprisal", "Reaction: After a Space Marines unit you control is damaged by an"
                                                    " attack, exhaust that unit to deal damage equal to twice the"
                                                    " unit's printed ATK to the attacker.", "Power.",
                              1, "Space Marines", "Loyal", 2, False),
        CardClasses.SupportCard("Launch Pads", "Combat Action: Exhaust this support to deploy a Space Marines unit"
                                               " with a printed cost of exactly 3 from your hand at a planet.",
                                "Upgrade.", 2, "Space Marines", "Common", False, action_in_play=True,
                                allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Orbital Relay", "Interrupt: When you deploy a support card, reduce its cost by 1.",
                                "Upgrade.", 2, "Space Marines", "Common", False),
        CardClasses.ArmyCard("Raven Guard Legion", "Reaction: After this unit enters play, it gets +1 ATK and +1 HP"
                                                   " until the end of the phase.", "Soldier. Raven Guard.",
                             2, "Space Marines", "Common", 2, 3, 1, False),
        CardClasses.ArmyCard("Dark Angels Purifier", "Deep Strike (2).\n"
                                                     "Interrupt: When this unit is destroyed, Deep Strike a Dark "
                                                     "Angels unit you control in reserve at the same planet.",
                             "Soldier. Dark Angels.", 3, "Space Marines", "Common", 3, 3, 1, False, deepstrike=2),
        CardClasses.ArmyCard("Parched Neophyte", "Bloodthirst - During a combat round in which 1 or more units have"
                                                 " been destroyed at this planet, this unit gains Retaliate (3).",
                             "Scout. Blood Angels.", 1, "Space Marines", "Loyal", 2, 1, 0, False),
        CardClasses.ArmyCard("Grey Hunters", "Forced Reaction: After a token unit at this planet resolves an attack,"
                                             " destroy that unit.",
                             "Soldier. Space Wolves.", 4, "Space Marines", "Loyal", 4, 3, 2, False),
        CardClasses.ArmyCard("Fenrisian Wolf Pack", "No Attachments.\n"
                                                    "Reaction: After this unit deals damage by an attack, remove 1 "
                                                    "damage from it.", "Creature. Space Wolves.",
                             2, "Space Marines", "Common", 3, 3, 0, False, no_attachments=True),
        CardClasses.ArmyCard("Aurora Predator", "No Wargear Attachments.\n"
                                                "While this unit has faith it gets +3 ATK.",
                             "Vehicle. Grey Knights. Elite.", 5, "Space Marines", "Common", 4, 6, 1, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Imperial Fists Apothecary", "Reaction: After a Space Marines unit you control at this "
                                                          "planet is destroyed, gain 1 resource. "
                                                          "(Limit once per phase)", "Scholar. Imperial Fists.",
                             2, "Space Marines", "Loyal", 1, 2, 2, False),
        CardClasses.ArmyCard("Bladeguard Veteran Squad", "Reaction: After an attack by this unit against an army unit "
                                                         "doesn't destroy the defender, ready a target Space Marines "
                                                         "unit you control. (Limit once per phase)",
                             "Soldier. Ultramarines.", 3, "Space Marines", "Common", 3, 3, 1, False),
        CardClasses.ArmyCard("Iron Hands Platoon", "Reaction: After an enemy army unit with 2 or more printed command "
                                                   "icons enters play at this planet, deal 1 damage to that unit.",
                             "Soldier. Iron Hands.", 2, "Space Marines", "Common", 2, 3, 1, False),
        CardClasses.SupportCard("The Phalanx", "This support can be used as a shield card while it is in play. "
                                               "It has shield icons equal to 2 + the number of tokens on it.\n"
                                               "Reaction: After your opponent places a planet in their victory display,"
                                               " place 1 resource on this support.", "Location. Imperial Fists.",
                                1, "Space Marines", "Loyal", True),
        CardClasses.AttachmentCard("Imposing Presence", "Attach to a Soldier army unit. Limit 1 per unit.\n"
                                                        "While attached unit is ready, each enemy army and token unit "
                                                        "at this planet has -1 ATK.", "Skill.",
                                   1, "Space Marines", "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   required_traits="Soldier", limit_one_per_unit=True),
        CardClasses.ArmyCard("Ravenwing Dark Talons", "No Wargear Attachments. Flying.\n"
                                                      "Reaction: After this unit resolves an attack against a warlord "
                                                      "unit, this unit gets +1 ATK and +1 HP until the end of the"
                                                      " game.", "Vehicle. Raven Guard.", 2, "Space Marines",
                             "Loyal", 1, 2, 1, False, wargear_attachments_permitted=False, flying=True),
        CardClasses.SupportCard("Klan Totem", "Reaction: After a unit with the Deep Strike keyword is destroyed, "
                                              "exhaust this support to put that unit into reserve at a non-first "
                                              "planet from your discard pile.", "Upgrade. Relic.",
                                2, "Orks", "Loyal", True),
        CardClasses.ArmyCard("Baddfrag", "Deep Strike (2).\n"
                                         "Each Vehicle unit you control at this planet gets +1 ATK.",
                             "Warrior. Blood Axe.", 3, "Orks", "Common", 3, 3, 0, True, deepstrike=2),
        CardClasses.ArmyCard("Shok Troopa", "Retaliate (1).\n"
                                            "Forced Interrupt: When this unit leaves play, deal 1 damage to "
                                            "each unit at this planet.", "Scout. Boyz. Ally.",
                             1, "Orks", "Loyal", 1, 1, 1, False, retaliate=1),
        CardClasses.ArmyCard("Cowardly Squig", "No Attachments. \n"
                                               "This unit's ATK is equal to its remaining HP.",
                             "Creature. Squig.", 4, "Orks", "Loyal", 0, 6, 0, False, no_attachments=True),
        CardClasses.ArmyCard("Abrasive Squigherder", "Action: Exhaust this unit to Rally 6 a card with the Squig "
                                                     "trait, add it to your hand.", "Oddboy.",
                             2, "Orks", "Common", 1, 2, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Immature Squig", "No Attachments.\n"
                                               "You may include up to 6 copies of this card in your deck. \n"
                                               "This unit gets +1 ATK for every other Squig unit at this planet.",
                             "Creature. Squig.", 2, "Orks", "Common", 1, 3, 0, False),
        CardClasses.AttachmentCard("Unstable Runtgun", "Ambush.\n"
                                                       "Attach to a Runt unit. \n"
                                                       "Attached unit gets +3 ATK. \n"
                                                       "Forced Reaction: After attached unit resolves an attack, "
                                                       "deal 1 damage to it.",
                                   "Wargear. Weapon.", 1, "Orks", "Common", 1, False, action_in_hand=True,
                                   allowed_phases_in_hand=True, extra_attack=3, required_traits="Runt", ambush=True),
        CardClasses.AttachmentCard("Fungal Infestation", "Attach to a planet. Limit 1 per planet. \n"
                                                         "Reaction: After a non-token unit you control leaves play "
                                                         "from this planet, put a Snotlings token into play under "
                                                         "your control at this planet. ", "Upgrade.",
                                   3, "Orks", "Loyal", 2, False, planet_attachment=True, limit_one_per_unit=True),
        CardClasses.AttachmentCard("Speed Freakz Warpaint", "Deep Strike (1). \n"
                                                            "Attach to an Orks army unit.\n"
                                                            "Attached unit gains the Red trait. \n"
                                                            "Attached unit gains \"Goes Fasta - This unit gets +3 ATK"
                                                            " while your opponent has the initiative.\"", "Upgrade.",
                                   1, "Orks", "Common", 1, False, unit_must_match_faction=True,
                                   type_of_units_allowed_for_attachment="Army", deepstrike=1),
        CardClasses.SupportCard("Convincing Cutouts", "Action: Exhaust this support to move a target non-warlord unit "
                                                      "you control at a planet without an enemy warlord to your HQ.",
                                "Upgrade.", 1, "Orks", "Common", False, action_in_play=True,
                                allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Goff Shokboyz", "Reaction: After this unit enters play, treat the printed text box of a"
                                              " target army unit at this planet as if it were blank (except for Traits)"
                                              " until the end of the round.", "Warrior. Boyz. Ally.",
                             1, "Orks", "Common", 2, 1, 0, False),
        CardClasses.EventCard("Mob Up!", "Action: Exhaust each Snotlings token you control to deal X damage to a target"
                                         " army unit, where X is the number of Snotlings tokens exhausted by this"
                                         " effect.", "Tactic.", 1, "Orks", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Necklace of Teef", "Attach to an army unit.\n"
                                                       "Attached unit gets +1 ATK for each Resource on this"
                                                       " attachment.\n"
                                                       "Reaction: After a combat round begins at this planet, place"
                                                       " 1 Resource on this attachment.", "Wargear.",
                                   1, "Orks", "Common", 1, False, type_of_units_allowed_for_attachment="Army"),
        CardClasses.EventCard("Blessing of Mork", "Play only during a battle.\n"
                                                  "Combat Action: For the remainder of the combat round, after an Ork "
                                                  "unit you control destroys an army unit by an attack, move 1 damage "
                                                  "from the attacker to a target unit at the same planet.", "Power.",
                              2, "Orks", "Loyal", 2, False, action_in_hand=True,
                              allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Deff Dread", "No Wargear Attachments.\n"
                                           "Brutal.\n"
                                           "Reaction: After this unit is assigned damage by an attack, you may deal "
                                           "2 damage to this unit to deal 3 damage to the attacker.",
                             "Vehicle. Elite.", 7, "Orks", "Loyal", 4, 7, 3, False, brutal=True,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Inexperienced Weirdboy", "Combat Action: Deal X damage to a target army unit at this "
                                                       "planet. Then deal X damage to this unit. X is equal to the "
                                                       "number of cards in your hand. (Limit once per combat round)",
                             "Psyker. Oddboy.", 3, "Orks", "Common", 1, 4, 2, False,
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Palace of Slaanesh", "Limited.\n"
                                                      "Reaction: After the headquarters phase begins, put a "
                                                      "Cultist token into play at your HQ.",
                                "Location.", 1, "Chaos", "Common", False, limited=True),
        CardClasses.EventCard("Test of Faith", "Limit one non-signature Ritual per deck. \n"
                                               "Action: Sacrifice a Cultist token at a planet with a unique unit you "
                                               "control to place 2 Faith tokens on each Cultist and Ritualist unit you "
                                               "control at the same planet.", "Ritual. Chaos Undivided.",
                              1, "Chaos", "Loyal", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Kairos Fateweaver", "Action: Reveal cards from the top of your deck until you reveal a"
                                                  " unit. Replace this unit's textbox with the discarded unit's until "
                                                  "the end of the phase. Discard that unit, and shuffle the remaining "
                                                  "cards into your deck.", "Daemon. Tzeentch. Elite.",
                             5, "Chaos", "Loyal", 4, 5, 3, True, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Venomcrawler", "Reduce the cost of this unit by 1 for each Cultist token "
                                             "sacrificed while paying its cost.", "Daemon. Elite.",
                             7, "Chaos", "Common", 6, 6, 1, True),
        CardClasses.EventCard("Putrescent Corpulence", "Action: Rally 12 up to 2 Blessing or Curse attachments, "
                                                          "add them to your hand.", "Power. Nurgle.",
                              1, "Chaos", "Loyal", 2, False, action_in_hand=True, allowed_phases_in_hand="ALL")
    ]
    return blackstone_project_cards
