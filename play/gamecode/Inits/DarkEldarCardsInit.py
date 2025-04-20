from .. import CardClasses


def dark_eldar_cards_init():
    faction = "Dark Eldar"
    dark_eldar_cards_array = [CardClasses.WarlordCard("Packmaster Kith", "Reaction: After this warlord commits "
                                                                         "to a planet, put a Khymera token into "
                                                                         "play at this planet.",
                                                      "Warrior. Succubus. Witch.", faction, 2, 6, 1, 5,
                                                      "Bloodied.", 7, 7,
                                                      ["4x Kith's Khymeramasters", "1x Khymera Den",
                                                       "2x Pact of the Haemonculi", "1x Agonizer of Bren"]),
                              CardClasses.ArmyCard("Kith's Khymeramasters", "Reaction: After this unit enters play, "
                                                                            "put a Khymera token into play at this "
                                                                            "planet.", "Warrior. Beastmaster. Wych.",
                                                   2, faction, "Signature", 1, 2, 1, False),
                              CardClasses.SupportCard("Khymera Den", "Action: Exhaust this support to move any "
                                                                     "number of Khymera tokens you control to "
                                                                     "a target planet.", "Location.",
                                                      1, faction, "Signature", False, action_in_play=True,
                                                      allowed_phases_in_play="ALL"),
                              CardClasses.EventCard("Pact of the Haemonculi", "Deploy Action: Sacrifice a unit to "
                                                                              "discard 1 card at random from your "
                                                                              "opponent's hand. Then, draw 2 cards.",
                                                    "Tactic.", 2, faction, "Signature", 1, False,
                                                    action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
                              CardClasses.AttachmentCard("Agonizer of Bren", "Attach to an army unit.\n"
                                                                             "Attached unit gets +1 ATK for each "
                                                                             "Khymera token you control.",
                                                         "Wargear. Weapon.", 1, faction, "Signature", 3, False,
                                                         type_of_units_allowed_for_attachment="Army"),
                              CardClasses.ArmyCard("Sybarite Marksman", "Ranged. (This unit attacks during the "
                                                                        "ranged skirmish at the beginning of"
                                                                        " a battle.)", "Warrior. Kabalite.",
                                                   1, faction, "Common", 2, 1, 0, False, ranged=True),
                              CardClasses.ArmyCard("Incubus Warrior", "", "Warrior.", 2, faction,
                                                   "Common", 3, 1, 2, False),
                              CardClasses.ArmyCard("Haemonculus Tormentor", "Action: Pay 1 resource to give this "
                                                                            "unit +2 ATK until the end of the phase.",
                                                   "Scholar. Haemonculus.", 4, faction,
                                                   "Common", 2, 4, 1, False, action_in_play=True,
                                                   allowed_phases_in_play="ALL"),
                              CardClasses.ArmyCard("Hellion Gang", "Flying. (This unit takes half damage from "
                                                                   "non-Flying units.", "Scout. Raider.",
                                                   2, faction, "Common", 2, 2, 1, False),
                              CardClasses.ArmyCard("Beasthunter Wyches", "Reaction: After you play a Dark Eldar event "
                                                                         "card, pay 1 resource to put a Khymera token "
                                                                         "into play at your HQ", "Warrior. Wych.",
                                                   3, faction, "Common", 1, 3, 2, False),
                              CardClasses.ArmyCard("Baleful Mandrake", "Ranged. (This unit attacks during the "
                                                                       "ranged skirmish at the beginning of"
                                                                       " a battle.)", "Warrior.",
                                                   3, faction, "Common", 3, 2, 1, False, ranged=True),
                              CardClasses.ArmyCard("Vile Raider", "No Wargear Attachments.\n"
                                                                  "Mobile. (At the beginning of the combat phase, "
                                                                  "this unit may move to an adjacent planet.",
                                                   "Vehicle. Transport.", 4, faction, "Common", 2, 4, 2, False,
                                                   wargear_attachments_permitted=False, mobile=True),
                              CardClasses.ArmyCard("Black Heart Ravager", "No Wargear Attachments.\n"
                                                                          "Flying. (This unit takes half damage from "
                                                                          "non-Flying units.)\n"
                                                                          "Reaction: After this unit damages a "
                                                                          "non-warlord unit, rout that unit.",
                                                   "Vehicle. Tank. Elite.", 6, faction, "Loyal", 2, 5, 2, False,
                                                   wargear_attachments_permitted=False, flying=True),
                              CardClasses.ArmyCard("Murder of Razorwings", "No Attachments.\n"
                                                                           "Reaction: After you deploy this unit, "
                                                                           "discard 1 card at random from your "
                                                                           "opponent's hand.", "Creature. Ally.",
                                                   1, faction, "Loyal", 1, 1, 0, False, no_attachments=True),
                              CardClasses.ArmyCard("Coliseum Fighters", "Reaction: After this unit enters play, "
                                                                        "return the topmost event card from your "
                                                                        "discard pile to your hand.",
                                                   "Warrior. Wych.", 2, faction, "Common", 1, 2, 0, False),
                              CardClasses.ArmyCard("Kabalite Strike Force", "Area Effect (1). (When this unit "
                                                                            "attacks it may instead deal its "
                                                                            "Area Effect damage to each enemy "
                                                                            "unit at this planet.",
                                                   "Warrior. Kabalite.", 2, faction, "Common", 2, 2, 0, False,
                                                   area_effect=1),
                              CardClasses.ArmyCard("Syren Zythlex", "Reaction: After an enemy unit is deployed at "
                                                                    "this planet, exhaust it.",
                                                   "Warrior. Wych.", 3, faction, "Loyal", 2, 3, 2, True),
                              CardClasses.EventCard("Power from Pain", "Combat Action: Your opponent must sacrifice "
                                                                       "an army unit if able.", "Power. Torture.",
                                                    2, faction, "Common", 1, False, action_in_hand=True,
                                                    allowed_phases_in_hand="COMBAT"),
                              CardClasses.EventCard("Archon's Terror", "Combat Action: Rout a target non-unique unit.",
                                                    "Power.", 2, faction, "Common", 1, False, action_in_hand=True,
                                                    allowed_phases_in_hand="COMBAT"),
                              CardClasses.EventCard("Raid", "Limited. (Limit one Limited card per round.)\n"
                                                            "Action: Take 1 resource from your opponent if he has "
                                                            "more resources than you.", "Tactic.",
                                                    0, faction, "Loyal", 2, False, action_in_hand=True,
                                                    allowed_phases_in_hand="ALL", limited=True),
                              CardClasses.AttachmentCard("Suffering", "Attach to an army unit.\n"
                                                                      "Attached unit gets -2 ATK.",
                                                         "Condition. Torture.", 1, faction, "Loyal", 2, False,
                                                         type_of_units_allowed_for_attachment="Army",
                                                         extra_attack=-2),
                              CardClasses.AttachmentCard("Hypex Injector", "Attach to an army unit.\n"
                                                                           "Reaction: After you play a Dark Eldar "
                                                                           "event card, ready attached unit.",
                                                         "Wargear.", 0, faction, "Common", 1, False,
                                                         type_of_units_allowed_for_attachment="Army"),
                              CardClasses.SupportCard("Altar of Torment", "Limited. (Limit one Limited card per "
                                                                          "round.)\n"
                                                                          "Interrupt: When you deploy a Dark Eldar "
                                                                          "unit, exhaust this support to reduce "
                                                                          "that unit's cost by 1.",
                                                      "Location.", 1, faction, "Common", True, "",
                                                      applies_discounts=[True, 1, True],
                                                      is_faction_limited_unique_discounter=True, limited=True),
                              CardClasses.SupportCard("Twisted Laboratory", "Action: Exhaust this support to treat the "
                                                                            "printed text box of a target army unit "
                                                                            "as if it were blank (except for Traits) "
                                                                            "until the end of the phase.",
                                                      "Location.", 2, faction, "Loyal", False, action_in_play=True,
                                                      allowed_phases_in_play="ALL")
                              ]
    return dark_eldar_cards_array
