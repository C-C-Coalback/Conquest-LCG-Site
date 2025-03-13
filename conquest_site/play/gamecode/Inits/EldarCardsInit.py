from .. import CardClasses


def eldar_cards_init():
    faction = "Eldar"
    eldar_cards_array = [CardClasses.WarlordCard("Eldorath Starbane", "Reaction: After this warlord commits to a "
                                                                      "planet, exhaust a target non-warlord unit "
                                                                      "at that planet.",
                                                 "Psyker. Alaitoc.", faction, 1, 7, 1, 6, "Bloodied.", 7, 7,
                                                 ["4x Starbane's Council", "1x Alaitoc Shrine",
                                                  "2x Foresight", "1x Mobility"]),
                         CardClasses.ArmyCard("Starbane's Council", "This unit gets +2 ATK while attacking an "
                                                                    "exhausted unit.", "Psyker. Alaitoc.",
                                              3, faction, "Signature", 3, 3, 1, False),
                         CardClasses.SupportCard("Alaitoc Shrine", "Reaction: After an Eldar unit moves to a planet, "
                                                                   "exhaust this support to ready that unit.",
                                                 "Location. Alaitoc.", 1, faction, "Signature", False),
                         CardClasses.EventCard("Foresight", "Reaction: After your warlord commits to a planet, "
                                                            "commit it to a different planet.", "Power.",
                                               1, faction, "Signature", 1, False),
                         CardClasses.AttachmentCard("Mobility", "Attach to an army unit.\n"
                                                                "Attached unit gains Mobile.", "Skill.",
                                                    0, faction, "Signature", 3, False,
                                                    type_of_units_allowed_for_attachment="Army"),
                         CardClasses.ArmyCard("Biel-Tan Guardians", "", "Warrior. Biel-Tan. Ally.",
                                              1, faction, "Loyal", 1, 1, 2, False),
                         CardClasses.ArmyCard("Altansar Rangers", "Ranged.", "Scout. Altansar.", 3, faction,
                                              "Common", 2, 2, 2, False, ranged=True),
                         CardClasses.ArmyCard("Eldar Survivalist", "+1 resource and +1 card when command struggle"
                                                                   "is won at this planet."
                                              , "Scout. Ally.", 2, faction, "Common", 0, 2, 1, False),
                         CardClasses.ArmyCard("Wildrider Squadron", "No Wargear Attachments.\n"
                                                                    "Combat Action: Move this unit to an adjacent"
                                                                    " planet. (Limit once per phase.)",
                                              "Vehicle. Saim-Hann.", 4, faction, "Common", 3, 4, 1, False,
                                              action_in_play=True, allowed_phases_in_play="COMBAT",
                                              wargear_attachments_permitted=False),
                         CardClasses.ArmyCard("Soaring Falcon", "No Wargear Attachments.\n"
                                                                "Mobile.", "Vehicle.",
                                              3, faction, "Common", 1, 5, 2, False,
                                              wargear_attachments_permitted=False),
                         CardClasses.ArmyCard("Wailing Wraithfighter", "No Wargear Attachments.\n"
                                                                       "Flying.\n"
                                                                       "Reaction: After this unit is declared as an "
                                                                       "attacker, your opponent must choose and "
                                                                       "discard 1 card from his hand, if able.",
                                              "Vehicle. Spirit. Elite.", 6, faction, "Loyal", 3, 5, 2, False,
                                              wargear_attachments_permitted=False),
                         CardClasses.ArmyCard("Iyanden Wraithguard", "Armorbane.", "Drone. Spirit. Iyanden.",
                                              3, faction, "Loyal", 4, 2, 1, False, armorbane=True),
                         CardClasses.ArmyCard("Shrouded Harlequin", "Interrupt: When this unit is destroyed, exhaust "
                                                                    "a target enemy unit at a planet of your choice.",
                                              "Warrior. Harlequin.", 2, faction, "Common", 2, 1, 1, False),
                         CardClasses.ArmyCard("Swordwind Farseer", "Reaction: After this unit enters play, "
                                                                   "search the top 6 cards of your deck for a card. "
                                                                   "Add it to your hand, and place the remaining cards "
                                                                   "on the bottom of your deck in any order.",
                                              "Psyker. Biel-Tan.", 3, faction, "Loyal", 2, 2, 1, False),
                         CardClasses.ArmyCard("Silvered Blade Avengers", "Reaction: After this unit is declared as an "
                                                                         "attacker against a non-warlord unit, "
                                                                         "exhaust that unit.", "Warrior.",
                                              4, faction, "Common", 1, 4, 1, False),
                         CardClasses.ArmyCard("Biel-Tan Warp Spiders", "Reaction: After this unit is declared as "
                                                                       "an attacker, look at the top 2 cards of "
                                                                       "any player's deck. You may discard 1 "
                                                                       "of those cards.", "Warrior. Biel-Tan.",
                                              2, faction, "Common", 1, 3, 1, False),
                         CardClasses.ArmyCard("Spiritseer Erathal", "Reaction: After this unit is declared as an "
                                                                    "attacker, remove 1 damage from another target "
                                                                    "at this planet.", "Psyker. Saim-Hann.",
                                              3, faction, "Loyal", 2, 3, 2, True),
                         CardClasses.EventCard("Superiority", "Interrupt: When a command struggle at a planet begins, "
                                                              "a target army unit at that planet loses all command "
                                                              "icons until the end of that command struggle.",
                                               "Tactic.", 1, faction, "Common", 1, False, action_in_hand=True,
                                               allowed_phases_in_hand="COMMAND"),
                         CardClasses.EventCard("Nullify", "Interrupt: When your opponent plays an event card, "
                                                          "exhaust a unique Eldar unit to cancel its effects.",
                                               "Power.", 0, faction, "Common", 1, False),
                         CardClasses.EventCard("Doom", "Deploy Action: Destroy each non-unique unit at "
                                                       "each player's HQ.", "Power.",
                                               4, faction, "Common", 1, False, action_in_hand=True,
                                               allowed_phases_in_hand="DEPLOY"),
                         CardClasses.EventCard("Gift of Isha", "Action: Put the topmost Eldar unit from your discard "
                                                               "pile into play at a planet. If that unit is still "
                                                               "in play at the end of the phase, discard it.",
                                               "Power. Blessing.", 2, faction, "Loyal", 2, False,
                                               action_in_hand=True, allowed_phases_in_hand="ALL"),
                         CardClasses.AttachmentCard("Banshee Power Sword", "Attach to an army unit.\n"
                                                                           "Attached unit gets +1 ATK.\n"
                                                                           "Interrupt: When attached unit declares an "
                                                                           "attack against a non-warlord unit, discard "
                                                                           "X cards from your hand to give attached "
                                                                           "unit +X ATK for that attack.",
                                                    "Wargear, Weapon.", 1, faction, "Common", 1, False,
                                                    type_of_units_allowed_for_attachment="Army"),
                         CardClasses.SupportCard("Corsair Trading Port", "Limited.\n"
                                                                         "Interrupt: When you deploy an Eldar unit, "
                                                                         "exhaust this support to reduce that "
                                                                         "unit's cost by 1.",
                                                 "Location.", 1, faction, "Common", True,
                                                 applies_discounts=[True, 1, True],
                                                 is_faction_limited_unique_discounter=True, limited=True),
                         CardClasses.SupportCard("Craftworld Gate", "Action: Exhaust this support to return a target "
                                                                    "army unit you control to your hand.",
                                                 "Location.", 1, faction, "Loyal", False,
                                                 action_in_play=True, allowed_phases_in_play="ALL")
                         ]
    return eldar_cards_array
