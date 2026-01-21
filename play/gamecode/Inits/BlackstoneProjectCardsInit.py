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
        CardClasses.ArmyCard("Rallying Thunderbolt", "Flying. No Wargear attachments.\n"
                                                     "Reaction: After this unit moves to a planet, ready each unit "
                                                     "with printed cost 3 or greater you control at that planet.",
                             "Vehicle. Elite.", 7, "Astra Militarum", "Common", 3, 5, 3, False,
                             flying=True, wargear_attachments_permitted=False),
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
                             "Creature. Squig.", 4, "Orks", "Common", 0, 6, 0, False, no_attachments=True),
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
                              1, "Chaos", "Loyal", 2, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Great Unclean One", "Lumbering.\n"
                                                  "Each army unit you control at this planet gains Sweep (2).",
                             "Daemon. Nurgle. Elite.", 7, "Chaos", "Loyal", 2, 9, 4, False, lumbering=True),
        CardClasses.ArmyCard("Seekers of Pleasure", "Reaction: After a Slaanesh unit you control takes damage, move "
                                                    "this unit to that planet to have this unit gain Sweep (1) "
                                                    "until the end of the round.", "Cultist. Slaanesh.",
                             2, "Chaos", "Common", 1, 3, 1, False),
        CardClasses.ArmyCard("Word Bearers Chaplain", "This unit gets +1 ATK for each different trait among Tzeentch,"
                                                      " Khorne, Nurgle, and Slaanesh among units you control at "
                                                      "this planet.", "Soldier. Chaos Undivided.",
                             3, "Chaos", "Common", 1, 4, 1, False),
        CardClasses.AttachmentCard("Steed of Slaanesh", "Attach to a Slaanesh army unit you control. \n"
                                                        "Action: Exhaust this attachment to move attached unit to a "
                                                        "planet without an enemy warlord.",
                                   "Wargear. Daemon. Slaanesh.", 1, "Chaos", "Loyal", 2, False,
                                   action_in_play=True, allowed_phases_in_play="ALL",
                                   type_of_units_allowed_for_attachment="Army", required_traits="Slaanesh",
                                   must_be_own_unit=True),
        CardClasses.AttachmentCard("Soul Furnace", "Attach to a Daemon army unit. \n"
                                                   "Attached unit gets +1 ATK and +1 HP.\n"
                                                   "Combat Action: Sacrifice a Cultist unit at this planet to give "
                                                   "attached unit +2 ATK and +2 HP until the end of the phase. "
                                                   "(Limit twice per phase)", "War Engine.",
                                   2, "Chaos", "Common", 1, False,
                                   action_in_play=True, allowed_phases_in_play="COMBAT",
                                   type_of_units_allowed_for_attachment="Army", required_traits="Daemon",
                                   extra_attack=1, extra_health=1),
        CardClasses.ArmyCard("Chaos Maulerfiend", "No Wargear Attachments.\n"
                                                  "Reaction: After this unit damages an enemy unit by an attack, "
                                                  "damage cannot be removed from that unit until the end of the "
                                                  "round.", "Daemon. War Engine.",
                             4, "Chaos", "Common", 3, 6, 0, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Screamers", "No Wargear Attachments.\n"
                                          "Flying.", "Daemon. Tzeentch.",
                             1, "Chaos", "Loyal", 2, 1, 0, False, wargear_attachments_permitted=False, flying=True),
        CardClasses.AttachmentCard("Disc of Tzeentch", "Deep Strike (0).\n"
                                                       "Attach to a Psyker army unit.\n"
                                                       "Attached unit gains Sweep (1) and Ranged.",
                                   "Daemon. Tzeentch.", 2, "Chaos", "Common", 1, False, deepstrike=0,
                                   type_of_units_allowed_for_attachment="Army", required_traits="Psyker"),
        CardClasses.EventCard("Core Destabilization", "Combat Action: Target a non-first planet. Deal 3 damage to "
                                                      "each unit with printed cost 3 or higher at that planet, "
                                                      "and deal 1 damage to each unit at each adjacent planet.",
                              "Power.", 4, "Chaos", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Havocs of Khorne", "Sweep (1).\n"
                                                 "This unit deals double damage while attacking a damaged unit.",
                             "Warrior. Khorne.", 3, "Chaos", "Common", 2, 3, 1, False, sweep=1),
        CardClasses.ArmyCard("Khornate Heldrake", "No Wargear Attachments. Flying.\n"
                                                  "Reaction: After you win a battle at this planet, destroy a "
                                                  "target enemy army unit.", "Daemon. Khorne. Elite.",
                             8, "Chaos", "Loyal", 7, 5, 2, False, flying=True, wargear_attachments_permitted=False),
        CardClasses.SupportCard("Decayed Gardens", "Reaction: After the combat phase begins, exhaust this support to "
                                                   "give a target Lumbering unit +3 ATK for its next attack "
                                                   "this phase.", "Location. Nurgle.",
                                1, "Chaos", "Loyal", False),
        CardClasses.AttachmentCard("Necrotoxin Missile", "Attach to a Vehicle unit.\n"
                                                         "Attached unit gets +1 ATK.\n"
                                                         "Enemy non-Elite army units at this planet cannot retreat.",
                                   "Hardpoint.", 1, "Dark Eldar", "Common", 1, False,
                                   required_traits="Vehicle", extra_attack=1),
        CardClasses.ArmyCard("Bloodied Kabal", "Reaction: After an enemy token unit or an enemy army unit with "
                                               "printed cost 1 or lower is destroyed at this planet, add a "
                                               "Kabalite card in your discard pile to your hand.",
                             "Warrior. Kabalite.", 1, "Dark Eldar", "Loyal", 1, 2, 1, False),
        CardClasses.ArmyCard("Incubus of the Severed", "This unit cannot be damaged by Area Effect.\n"
                                                       "Action: If this unit is in your HQ, add it to your hand.",
                             "Warrior. Kabalite.", 3, "Dark Eldar", "Common", 3, 4, 1, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Final Expiration", "Action: Deal X damage to a target non-warlord unit. X is equal to "
                                                  "the number of Torture cards in your discard pile.",
                              "Torture. Power.", 3, "Dark Eldar", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.SupportCard("Tower of Despair", "Action: Sacrifice a unit to Rally 6 a Torture card, add it to your"
                                                    " hand. You may exhaust any number of Haemonculus units you control"
                                                    " to add an equal number of other Torture cards from the remaining"
                                                    " cards to your hand.", "Location.",
                                0, "Dark Eldar", "Loyal", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Incubus Cleavers", "Forced Interrupt: When this unit would be assigned damage by an "
                                                 "attack or the Area Effect keyword, instead deal that damage to "
                                                 "another target unit at the same planet. (Limit once per phase)",
                             "Assassin. Warrior.", 3, "Dark Eldar", "Loyal", 3, 1, 1, False),
        CardClasses.EventCard("Medusae Pact", "Action: Each player must discard down to 5 cards in hand.",
                              "Torture. Power.", 1, "Dark Eldar", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Desperate Captives", "No Wargear Attachments.\n"
                                                   "Interrupt: When you sacrifice this unit, your opponent deals X "
                                                   "indirect damage among units they control in their HQ. X "
                                                   "is equal to twice the number of units in their HQ.",
                             "Ally.", 0, "Dark Eldar", "Common", 0, 1, 0, False, wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("Beastmaster's Whip", "Attach to a Beastmaster army unit.\n"
                                                         "Attached unit gets +1 ATK.\n"
                                                         "Reaction: After attached unit is declared as an attacker, "
                                                         "ready a non-Elite Creature unit you control at this planet.",
                                   "Weapon. Wargear.", 1, "Dark Eldar", "Common", 1, False,
                                   required_traits="Beastmaster", type_of_units_allowed_for_attachment="Army",
                                   extra_attack=1),
        CardClasses.ArmyCard("Razorwing Jetfighter", "No Wargear Attachments. Flying.\n"
                                                     "Reaction: After this unit resolves an attack against a unit with "
                                                     "the Flying or Mobile keyword, ready this unit. "
                                                     "(Limit twice per phase)", "Vehicle. Elite.",
                             6, "Dark Eldar", "Loyal", 3, 5, 2, False, flying=True,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Liatha's Loyal Hound", "No Attachments.\n"
                                                     "Reaction: After this card is removed from the game face-down, "
                                                     "flip it and another facedown card with no printed shield icons "
                                                     "you removed from the game face-up to put this unit into play "
                                                     "at the last planet.", "Creature. Abomination.",
                             4, "Dark Eldar", "Loyal", 3, 3, 2, True, no_attachments=True),
        CardClasses.ArmyCard("Stalking Scourge", "Flying.", "Warrior.", 2, "Dark Eldar", "Loyal",
                             1, 2, 2, False, flying=True),
        CardClasses.EventCard("Unconquerable Fear", "Reaction: After your opponent plays an event card, exhaust your "
                                                    "warlord to discard two cards at random from their hand. "
                                                    "Max 1 per round.", "Power. Torture. Maneuver.",
                              3, "Dark Eldar", "Loyal", 2, False),
        CardClasses.ArmyCard("Draining Cronos", "No Attachments.\n"
                                                "Reaction: After this unit destroys an enemy unit by an attack, "
                                                "a target unit you control at the same planet gets +1 ATK and "
                                                "+2 HP until the end of the phase.", "Creature. Abomination. Elite.",
                             5, "Dark Eldar", "Common", 5, 5, 1, False, no_attachments=True),
        CardClasses.ArmyCard("Looming Grotesque", "No Wargear Attachments.\n"
                                                  "While there are 5 or fewer Torture cards in your discard pile, "
                                                  "this unit gains Lumbering.", "Creature. Abomination.",
                             4, "Dark Eldar", "Common", 5, 6, 1, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("The Price of Success", "Deep Strike (1).\n"
                                                      "Reaction: After your opponent wins a battle at this planet, "
                                                      "you may Deep Strike this event to discard two cards at random "
                                                      "from their hand.", "Tactic.",
                              -1, "Dark Eldar", "Common", 1, False, deepstrike=1),
        CardClasses.ArmyCard("Swordwind Wave Serpent", "Reaction: After this unit resolves an attack,"
                                                       " move it to an adjacent planet.", "Vehicle. Biel-Tan.",
                             4, "Eldar", "Common", 4, 3, 2, False),
        CardClasses.ArmyCard("Avatar of Khaine", "X is equal to the number of exhausted units at this planet.\n"
                                                 "Forced Reaction: After a combat round at this planet ends, discard a "
                                                 "card from your hand. If you cannot, sacrifice this unit.",
                             "Elite. Alaitoc.", 6, "Eldar", "Loyal", 0, 7, 1, True),
        CardClasses.ArmyCard("Storm Guardians", "This unit gets +2 ATK while attacking a Soldier or Warrior unit.",
                             "Warrior. Alaitoc.", 2, "Eldar", "Common", 2, 2, 1, False),
        CardClasses.ArmyCard("Shadowseer", "Reaction: After an enemy army unit enters play at this planet, "
                                           "exhaust an attachment on this unit to deal 2 damage to that unit.",
                             "Psyker. Harlequin.", 3, "Eldar", "Loyal", 2, 3, 1, False),
        CardClasses.ArmyCard("Fire Dragons", "This unit deals double damage to enemy Vehicle units.", "Warrior.",
                             3, "Eldar", "Common", 3, 4, 1, False),
        CardClasses.ArmyCard("Voidscarred Corsair", "Sweep (1).\n"
                                                    "Reaction: After this unit enters play, a target army unit at this"
                                                    " planet cannot ready until the end of the phase.",
                             "Warrior.", 2, "Eldar", "Common", 2, 1, 1, False, sweep=1),
        CardClasses.EventCard("Rapid Ingress", "Reaction: After a unit you control is declared as an attacker at a "
                                               "Strongpoint planet, if it is the only unit you control at that planet, "
                                               "move a target army unit you control at an adjacent planet to that "
                                               "planet.", "Tactic.",
                              1, "Eldar", "Loyal", 2, False),
        CardClasses.EventCard("Unshrouded Truth", "Action: Your opponent may reveal any number of cards in their hand."
                                                  " For each card that was not revealed, gain 1 resource.",
                              "Power. Harlequin.", 2, "Eldar", "Loyal", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Iyanden Farseer", "While a battle is being resolved at this planet, your opponent cannot "
                                                "play events.",
                             "Psyker. Iyanden.", 3, "Eldar", "Loyal", 2, 4, 1, False),
        CardClasses.SupportCard("Garden of Solitude", "Action: Exhaust this card to look at the top card of your deck. "
                                                      "You may put that card on the bottom of your deck.", "Location.",
                                0, "Eldar", "Loyal", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Death Jesters", "Reaction: After this unit enters play, it gets +3 ATK for its next "
                                              "attack for this phase.", "Warrior. Harlequin.",
                             2, "Eldar", "Common", 1, 3, 1, False),
        CardClasses.AttachmentCard("Ghostglaive", "Attach to a Spirit army unit.\n"
                                                  "Attached unit gains Sweep (2).", "Wargear. Weapon.",
                                   1, "Eldar", "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   required_traits="Spirit"),
        CardClasses.ArmyCard("Ulthwé Night Spinner", "No Wargear Attachments.\n"
                                                     "Area Effect (2).", "Vehicle. Ulthwé.",
                             4, "Eldar", "Loyal", 3, 5, 0, False, area_effect=2, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Howling Exarch", "Reaction: After you cancel a card effect, deal 1 damage to up to "
                                               "two units at this planet.", "Warrior.",
                             3, "Eldar", "Loyal", 2, 3, 1, False),
        CardClasses.EventCard("Whirling Death", "Deploy Action: Destroy five non-unique units or supports "
                                                "at each player's HQ.", "Power.",
                              5, "Eldar", "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.EventCard("Counteroffensive",
                              "Action: Ready a target unit you control at a planet with a Psyker unit.", "Tactic.",
                              2, "Eldar", "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Peacekeeper Drone", "Reaction: After a battle begins at a planet, "
                                                  "move this unit to that planet. \n"
                                                  "Combat Action: A target non-warlord unit at this planet gets "
                                                  "-1 ATK until the end of the phase. (Limit once per phase)",
                             "Drone.", 1, "Tau", "Common", 0, 3, 0, False,
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Aun'la Prince", "Forced Reaction: After a non-Ethereal unit moves from this planet, "
                                              "deal it 1 damage.\n"
                                              "Forced Reaction: After this unit resolves its attack, move it "
                                              "to your HQ.", "Soldier. Ethereal.",
                             2, "Tau", "Loyal", 2, 3, 1, False),
        CardClasses.SupportCard("Air Protection Fleet", "Limited.\n"
                                                        "Interrupt: When you deploy a Soldier or Scout unit, exhaust "
                                                        "this support to reduce the cost of that unit by 1. If that "
                                                        "unit is an Astra Militarum unit, put a Guardsman token into "
                                                        "play at that planet.", "Upgrade. Fleet.",
                                2, "Tau", "Common", False),
        CardClasses.AttachmentCard("Riptide Battlesuit", "Attach to an army unit.\n"
                                                         "Attached unit gets +2 HP.\n"
                                                         "Action: Exhaust this attachment to give attached unit +2 HP "
                                                         "until the end of the phase.",
                                   "Wargear. Armor.", 1, "Tau", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army",
                                   extra_health=2, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Kroot Infiltrator", "Deep Strike (1).", "Soldier. Kroot.",
                             2, "Tau", "Common", 2, 4, 0, False, deepstrike=1),
        CardClasses.ArmyCard("Fire Caste Cadre", "Action: Return an attachment on this unit to your hand. "
                                                 "(Limit once per round)", "Soldier. Shas'la.",
                             3, "Tau", "Common", 2, 3, 1, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Exertion Drone", "Each non-Ethereal army unit you control at this planet gets +1 HP "
                                               "and gains 1 command icon.\n"
                                               "Forced Reaction: After this unit resolves its attack, move it "
                                               "to your HQ.", "Drone. Ethereal.",
                             2, "Tau", "Loyal", 0, 3, 1, False),
        CardClasses.EventCard("Force Reallocation", "Deploy Action: Exhaust any number of units you control. "
                                                    "Gain 1 resource for each unit exhausted by this effect.",
                              "Tactic.", 1, "Tau", "Loyal", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("DX-4 Technical Drone", "Attach to a Vehicle or Pilot army unit.\n"
                                                           "Each Tau Soldier unit you control at this planet "
                                                           "gets +1 ATK.\n"
                                                           "Reaction: After a combat round begins at this planet, "
                                                           "remove 1 damage from attached unit.",
                                   "Drone.", 1, "Tau", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.AttachmentCard("Reeducation Protocol", "Attach to an army unit you control.\n"
                                                           "Attached unit gains 2 command icons.\n"
                                                           "Attached unit's ATK and HP are set to 1.",
                                   "Negotiation.", 1, "Tau", "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True,
                                   extra_command=2),
        CardClasses.AttachmentCard("Industrial Boom", "Attach to a planet. Limit 1 per planet.\n"
                                                      "Forced Interrupt: When a player wins a command struggle at "
                                                      "attached planet, they draw 1 card and gain 1 resource.",
                                   "Negotiation.", 1, "Tau", "Common", 1, False, planet_attachment=True,
                                   limit_one_per_unit=True),
        CardClasses.EventCard("Scavenging Run", "Reaction: After you win a battle at a Material planet where you "
                                                "control a Kroot unit, return up to 2 attachments from your discard "
                                                "pile to your hand.", "Tactic.",
                              1, "Tau", "Common", 1, False),
        CardClasses.ArmyCard("Broadside Shas'vre", "Action: Exhaust this unit to deal damage equal to this unit's ATK "
                                                   "to a target enemy army unit.", "Soldier. Pilot.",
                             4, "Tau", "Common", 4, 4, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Guided Fire", "Action: A target non-Kroot army unit at a planet with a Shas'la unit "
                                             "you control gains Ranged until the end of the round.",
                              "Tactic.", 1, "Tau", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Winged Vespid Cadre", "Flying.\n"
                                                    "This unit gets +2 ATK while your opponent does not control a "
                                                    "ready unit at this planet.", "Soldier. Vespid.",
                             2, "Tau", "Common", 1, 3, 1, False, flying=True),
        CardClasses.ArmyCard("Water Caste Bureaucrat", "Reaction: After this unit enters play at a planet with an "
                                                       "enemy unit, you may give your opponent 1 of your resources "
                                                       "to search your deck for a card, add it to your hand. "
                                                       "Then shuffle your deck.", "Scout.",
                             1, "Tau", "Common", 1, 1, 1, False),
        CardClasses.ArmyCard("Angel Shark Bomber", "No Wargear attachments.\n"
                                                   "Area Effect (1). Sweep (3).\n"
                                                   "Reaction: After this unit enters play, exhaust each unit with "
                                                   "printed cost 2 or lower at this planet.", "Vehicle. Elite.",
                             6, "Tau", "Common", 4, 4, 2, False, area_effect=1, sweep=3,
                             wargear_attachments_permitted=False),
        CardClasses.WarlordCard("Red Terror", "Each army unit you control with 3 or fewer damage tokens on it gains"
                                              " brutal.", "Creature. Behemoth.",
                                "Tyranids", 2, 6, 0, 6, "Bloodied. Brutal.", 6, 6,
                                ["1x Restorative Tunnels", "2x Unexpected Ferocity",
                                 "1x Dripping Scythes", "4x Formless Leaper"]),
        CardClasses.ArmyCard("Formless Leaper", "This unit cannot be targeted by enemy card effects while it is the "
                                                "only unit you control at this planet.", "Creature. Behemoth.",
                             2, "Tyranids", "Signature", 1, 4, 1, False),
        CardClasses.EventCard("Unexpected Ferocity", "Reaction: After a unit you control is declared as an attacker,"
                                                     " deal 1 damage to it to have that unit gain Armorbane "
                                                     "for the duration of the attack.", "Tactic.",
                              1, "Tyranids", "Signature", 1, False),
        CardClasses.SupportCard("Restorative Tunnels", "Reaction: After a unit you control destroys an enemy unit by "
                                                       "an attack, exhaust this support to remove up to 3 damage "
                                                       "tokens from the attacker.", "Location.",
                                1, "Tyranids", "Signature", False),
        CardClasses.AttachmentCard("Dripping Scythes", "Attach to your Warlord.\n"
                                                       "Attached unit gets +2 HP.\n"
                                                       "Reaction: After attached unit is declared as a defender, "
                                                       "discard this attachment to cancel the attack.", "Biomorph.",
                                   1, "Tyranids", "Signature", 3, False, type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True, extra_health=2),
        CardClasses.ArmyCard("Manipulative Venomthrope", "While you are the only player to control a unit named "
                                                         "\"Manipulative Venomthrope\" at this planet, the printed "
                                                         "textbox of each damaged enemy army unit at this planet "
                                                         "is treated as blank (except for Traits).",
                             "Creature. Psyker. Elite.", 5, "Tyranids", "Common", 3, 6, 3, False),
        CardClasses.EventCard("Biomass Extraction", "Limited.\n"
                                                    "Action: Remove any number of infestation tokens from planets to "
                                                    "gain 1 Resource for each token removed.", "Tactic.",
                              1, "Tyranids", "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="ALL", limited=True),
        CardClasses.ArmyCard("Lurking Termagant", "Deep Strike (1).\n"
                                                  "Cannot be damaged by Area Effect. \n"
                                                  "This unit is considered to be a Termagant token for the purpose of "
                                                  "the Hive Mind specialization.", "Creature. Termagant.",
                             1, "Tyranids", "Common", 1, 1, 1, False, deepstrike=1),
        CardClasses.AttachmentCard("Acidic Venom Cannon", "Attach to an army unit you control. \n"
                                                          "Attached unit gets +3 ATK while it is attacking a unit "
                                                          "that has at least one attachment. \n"
                                                          "Reaction: After attached unit resolves an attack against a "
                                                          "non-warlord unit, discard an attachment from the defender.",
                                   "Wargear. Biomorph.", 1, "Tyranids", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.ArmyCard("Gargoyle Swarm", "Retaliate (1).\n"
                                               "Hive Mind - Each Termagant token you control at this planet gains "
                                               "Retaliate (1).", "Creature. Leviathan.",
                             2, "Tyranids", "Common", 2, 3, 0, False, retaliate=1, hive_mind=True),
        CardClasses.AttachmentCard("Catalyst of the Hive Mind", "Attach to an army unit you control. \n"
                                                                "Limit 1 per unit. \n"
                                                                "While at a planet with a synapse unit you control, "
                                                                "attached unit gains a command icon, +2 ATK and +2 HP.",
                                   "Biomorph.", 1, "Tyranids", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True,
                                   limit_one_per_unit=True),
        CardClasses.ArmyCard("Carnifex", "Bloodthirst - During a combat round in which 1 or more units have been"
                                         " destroyed at this planet, this unit gains Armorbane.\n"
                                         "Forced Reaction: After this unit enters play, exhaust it.",
                             "Creature. Behemoth. Elite.", 5, "Tyranids", "Common", 7, 7, 1, False),
        CardClasses.SynapseCard("Ravenous Horror", "Action: Sacrifice an army unit at this planet to give this unit "
                                                   "+1 ATK and +1 HP until the end of the game. (Limit once per round)",
                                "Creature. Behemoth. Elite.", 1, 4, 1, True,
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Psychic Zoanthrope", "Reaction: After your opponent plays an event card, deal 2 damage"
                                                   " to a target unit at this planet.", "Creature. Kraken. Psyker.",
                             3, "Tyranids", "Common", 3, 2, 2, False),
        CardClasses.ArmyCard("Hybrid Metamorph", "Reaction: After this unit enters play, Rally 6 an attachment, deploy "
                                                 "it to this unit, reducing the cost of that attachment by 1.",
                             "Creature. Genestealer.", 4, "Tyranids", "Common", 3, 4, 2, False),
        CardClasses.ArmyCard("Deathleaper", "Deep Strike (5). Armorbane.\n"
                                            "You may Deep Strike this card as an action during the combat phase.",
                             "Creature. Leviathan. Elite.", 6, "Tyranids", "Common", 6, 4, 3, False,
                             deepstrike=5, armorbane=True),
        CardClasses.SupportCard("Reclamation Pool", "Limited.\n"
                                                    "Reaction: After you win a battle at a planet, you may exhaust "
                                                    "this support and sacrifice a unit at that planet to gain 2 "
                                                    "Resources.", "Location.",
                                1, "Tyranids", "Common", False),
        CardClasses.ArmyCard("Repurposed Pariah", "This unit gets +1 ATK and +1 HP for each Psyker unit you control "
                                                  "at this planet.\n"
                                                  "Reaction: After an enemy Psyker unit enters play at this planet, "
                                                  "exhaust it. (Limit once per phase)", "Soldier. Novokh.",
                             3, "Necrons", "Common", 2, 3, 1, False),
        CardClasses.SupportCard("Unearthed Crypt", "Interrupt: When an army unit enters your discard pile, exhaust "
                                                   "this support to draw 1 card.", "Location.",
                                1, "Necrons", "Common", False),
        CardClasses.ArmyCard("Thundering Wraith", "Deep Strike (3).\n"
                                                  "Reaction: After you deep strike this unit, target an enemy army "
                                                  "unit. Your opponent must either deal 4 damage to that unit or "
                                                  "rout it.", "Drone. Elite.",
                             5, "Necrons", "Common", 4, 5, 1, False, deepstrike=3),
        CardClasses.ArmyCard("Lokhust Destroyer", "No Wargear Attachments.\n"
                                                  "Reaction: After a unit whose faction matches your enslavement dial "
                                                  "is destroyed at this planet, ready this unit. "
                                                  "(Limit once per phase)", "Warrior.",
                             3, "Necrons", "Common", 3, 3, 1, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Overseer Drone", "Reaction: After a unit you control at either this planet or an "
                                               "adjacent planet is declared as an attacker, exhaust this unit to"
                                               " give the attacker +2 ATK for the duration of the attack.",
                             "Drone.", 2, "Necrons", "Common", 1, 2, 1, False),
        CardClasses.EventCard("I Do Not Serve", "Reaction: After a Sautekh or Novokh unit you control is assigned "
                                                "damage by an attack from a unit matching your enslaved faction, "
                                                "prevent all of that damage.", "Power.",
                              0, "Necrons", "Common", 1, False),
        CardClasses.ArmyCard("Awakened Geomancer", "Reaction: After this unit enters play, discard up to three cards in"
                                                   " your hand to gain 1 resource for each card discarded.", "Scholar.",
                             4, "Necrons", "Common", 3, 4, 2, False),
        CardClasses.ArmyCard("Shambling Revenant",
                             "Forced Reaction: After this unit resolves its attack, sacrifice it.", "Warrior.",
                             0, "Necrons", "Common", 3, 1, 0, False),
        CardClasses.AttachmentCard("Flayer Affliction", "Attach to an army unit.\n"
                                                        "Deep Strike (1).\n"
                                                        "Forced Reaction: After attached unit resolves an attack, its "
                                                        "controller deals damage equal to its ATK to another unit "
                                                        "they control at the same planet.", "Tactic. Flaw.",
                                   2, "Necrons", "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   deepstrike=1),
        CardClasses.AttachmentCard("Gauntlet of Fire", "Attach to your warlord.\n"
                                                       "Action: Exhaust this attachment to either deal 2 damage to a "
                                                       "target army unit at the same planet as your warlord, or set "
                                                       "your enslavement dial to another faction.",
                                   "Wargear. Weapon. Relic.", 2, "Necrons", "Common", 2, True,
                                   type_of_units_allowed_for_attachment="Warlord", must_be_own_unit=True,
                                   action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.SupportCard("Null Shield Matrix", "Reaction: After an exhausted Necrons unit you control is "
                                                      "assigned damage, prevent 1 of that damage.", "Location.",
                                2, "Necrons", "Common", True),
        CardClasses.SupportCard("Merciless Reclamation", "Deploy Action: Discard a Necrotic Warrior or Necrotic Soldier"
                                                         " unit from your hand to deploy a Necrotic Warrior or Necrotic"
                                                         " Soldier unit with a printed cost exactly 1 greater than the"
                                                         " discarded unit from your discard pile at a planet, reducing"
                                                         " the cost of that unit by 1.", "Upgrade.",
                                1, "Necrons", "Common", False, action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.AttachmentCard("Disruption Field", "Attach to a Necrons Vehicle unit you control.\n"
                                                       "Treat the printed text box of each damaged enemy army unit at "
                                                       "this planet as if it were blank (except for Traits).",
                                   "Hardpoint.", 1, "Necrons", "Common", 2, False, required_traits="Vehicle",
                                   unit_must_match_faction=True, must_be_own_unit=True),
        CardClasses.ArmyCard("Harbinger of the Storm", "As an additional cost for your opponent to target either this "
                                                       "planet or a unit at this planet with an event, they must pay"
                                                       " 2 resources.", "Scholar. Elite.",
                             5, "Necrons", "Common", 3, 5, 3, True),
        CardClasses.AttachmentCard("Nightmare Shroud", "Attach to a Necrotic Scholar unit. Limit 1 per unit.\n"
                                                       "While attached unit is exhausted, each non-warlord unit at "
                                                       "this planet gets -1 ATK.", "Wargear.",
                                   2, "Necrons", "Common", 2, True, unit_must_match_faction=True,
                                   limit_one_per_unit=True, required_traits="Scholar"),
        CardClasses.AttachmentCard("Fabricator Claw Array", "Attach to a Necrotic Drone unit you control.\n"
                                                            "Combat Action: Exhaust attached unit to remove X damage "
                                                            "from a target Necrotic unit at the same planet. X is "
                                                            "equal to the ATK of the attached unit.",
                                   "Wargear.", 1, "Necrons", "Common", 1, False, unit_must_match_faction=True,
                                   required_traits="Drone", action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Explosive Scarabs", "Reaction: After this unit resolves its attack, sacrifice it to deal "
                                                  "damage equal to it's remaining HP to a target unit at this planet.",
                             "Drone.", 2, "Necrons", "Common", 1, 4, 0, False),
        CardClasses.EventCard("Excavated Minerals", "Reaction: After this card is discarded from your deck, "
                                                    "gain 1 Resource.", "Fortune.",
                              0, "Neutral", "Common", 1, False),
        CardClasses.ArmyCard("Scavenger Corps", "This planet has +1 Resource and +1 Card bonuses.",
                             "Ally. Scavenger.", 3, "Neutral", "Common", 1, 3, 1, False,
                             additional_cards_command_struggle=1, additional_resources_command_struggle=1),
        CardClasses.EventCard("Boast of Strength", "Action: You may sacrifice an army unit. Then your opponent may "
                                                   "sacrifice an army unit. Repeat until 1 player declines to "
                                                   "sacrifice a unit. Gain 2 Resources and draw 1 card if your "
                                                   "opponent declines.", "Gambit.",
                              0, "Neutral", "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Krak Grenade", "Attach to a Soldier or Warrior army unit.\n"
                                                   "Reaction: After attached unit is declared as an attacker against "
                                                   "an Elite unit, sacrifice this attachment to set attached unit's "
                                                   "attack to 5 for the remainder of the attack.",
                                   "Wargear. Weapon.", 0, "Neutral", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.AttachmentCard("Extra Munitions", "Attach to an army unit with a printed Area Effect keyword.\n"
                                                      "Attached unit gains Area Effect (1).", "Wargear. Weapon.",
                                   1, "Neutral", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army")
    ]
    return blackstone_project_cards
