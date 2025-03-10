from .. import CardClasses


def astra_militarum_cards_init():
    faction = "Astra Militarum"
    astra_militarum_cards_array = [CardClasses.WarlordCard("Colonel Straken", "Each other soldier or warrior unit "
                                                                              "you control at this planet gets "
                                                                              "+1 ATK.", "Soldier. Catachan.",
                                                           faction, 2, 6, 2, 5,
                                                           "Bloodied.", 7, 7,
                                                           ["4x Straken's Command Squad", "2x Glorious Intervention",
                                                            "1x Omega Zero Command", "1x Straken's Cunning"]
                                                           ),
                                   CardClasses.ArmyCard("Straken's Command Squad", "Interrupt: When this unit leaves "
                                                                                   "play, put a Guardsman token "
                                                                                   "into play at the same planet.",
                                                        "Soldier. Catachan.", 2, faction, "Signature",
                                                        2, 2, 1, False),
                                   CardClasses.SupportCard("Omega Zero Command", "Reaction: After you win a command "
                                                                                 "struggle, put a Guardsman token "
                                                                                 "into play at that planet.",
                                                           "Location.", 2, faction, "Signature", False),
                                   CardClasses.EventCard("Glorious Intervention", "Reaction: After a unit is assigned "
                                                                                  "damage by an attack, sacrifice a "
                                                                                  "Soldier or Warrior unit at the same "
                                                                                  "planet to prevent all of that "
                                                                                  "damage. Then, deal X damage to the "
                                                                                  "attacker. X is the sacrificed "
                                                                                  "unit's printed ATK value.",
                                                         "Tactic.", 1, faction, "Signature", 1, False),
                                   CardClasses.AttachmentCard("Straken's Cunning", "Attach to an army unit.\n"
                                                                                   "Attached unit gets +1 ATK.\n"
                                                                                   "Interrupt: When attached unit "
                                                                                   "leaves play, draw 3 cards.",
                                                              "Skill.", 1, faction, "Signature", 3, False),
                                   CardClasses.ArmyCard("Ratling Deadeye", "Ranged. (This unit attacks during the "
                                                                           "ranged skirmish at the beginning of"
                                                                           " a battle.)", "Scout. Abhuman.", 1,
                                                        faction, "Common", 1, 1, 1, False, ranged=True),
                                   CardClasses.ArmyCard("Cadian Mortar Squad", "Ranged. (This unit attacks during the "
                                                                               "ranged skirmish at the beginning of"
                                                                               " a battle.)\n"
                                                                               "Reaction: After an army unit you "
                                                                               "control at this planet leaves play, "
                                                                               "ready this unit.", "Soldier. Cadia.",
                                                        3, faction, "Loyal", 1, 3, 2, False, ranged=True),
                                   CardClasses.ArmyCard("Sanctioned Psyker", "", "Psyker.", 2, faction, "Common",
                                                        0, 4, 2, False),
                                   CardClasses.ArmyCard("Leman Russ Battle Tank", "No Wargear Attachments.",
                                                        "Vehicle. Tank. Elite.", 5, faction, "Loyal",
                                                        4, 6, 4, False),
                                   CardClasses.ArmyCard("Mordian Hellhound", "No Wargear Attachments.\n"
                                                                             "Area Effect (1). (When this unit "
                                                                             "attacks it may instead deal its "
                                                                             "Area Effect damage to each enemy "
                                                                             "unit at this planet.",
                                                        "Vehicle. Tank. Mordian.", 4, faction, "Common",
                                                        3, 3, 2, False, area_effect=1),
                                   CardClasses.ArmyCard("Assault Valkyrie", "No Wargear Attachments.\n Flying. (This "
                                                                            "unit takes half damage from non-Flying "
                                                                            "units.", "Vehicle. Transport.",
                                                        4, faction, "Common", 4, 4, 1, False),
                                   CardClasses.ArmyCard("Stalwart Ogryn", "Immune to enemy events.",
                                                        "Warrior. Abhuman.", 2, faction, "Common",
                                                        2, 2, 1, False),
                                   CardClasses.ArmyCard("Captain Markis", "Action: Sacrifice an Astra Militarum unit "
                                                                          "at this planet to exhaust a target "
                                                                          "non-warlord unit at this planet. "
                                                                          "(Limit once per phase.)",
                                                        "Soldier. Officer. Vostroya.",
                                                        3, faction, "Loyal", 2, 3, 2, True,
                                                        action_in_play=True, allowed_phases_in_play="ALL"),
                                   CardClasses.ArmyCard("Enginseer Augur", "Interrupt: When this unit leaves play, "
                                                                           "search the top 6 cards of your deck for "
                                                                           "an Astra Militarum support card with "
                                                                           "printed cost 2 or lower. Put that card "
                                                                           "into play at your HQ, and place the "
                                                                           "remaining cards on the bottom of your deck "
                                                                           "in any order.", "Scholar. Tech-Priest.",
                                                        2, faction, "Common", 2, 2, 0, False),
                                   CardClasses.ArmyCard("Penal Legionnaire", "", "Conscript. Ally.",
                                                        0, faction, "Common", 1, 1, 0, False),
                                   CardClasses.ArmyCard("Infantry Conscripts", "This unit gets +2 ATK for each "
                                                                               "support you control.", "Conscript.",
                                                        4, faction, "Common", 0, 5, 0, False),
                                   CardClasses.ArmyCard("Elysian Assault Team", "Interrupt: When a Soldier or Warrior "
                                                                                "unit you control leaves play from a "
                                                                                "planet, put this unit into play "
                                                                                "from your hand at the same planet.",
                                                        "Soldier. Elysia.", 2, faction, "Common", 2, 1, 0, False),
                                   CardClasses.EventCard("Preemptive Barrage", "Combat Action: Target up to 3 Astra "
                                                                               "Militarum units you control at the "
                                                                               "same planet. Each targeted unit gains "
                                                                               "Ranged until the end of the phase. "
                                                                               "(Units with Ranged attack during the "
                                                                               "ranged skirmish at the beginning "
                                                                               "of the battle.)", "Tactic.", 1,
                                                         faction, "Loyal", 2, False, action_in_hand=True,
                                                         allowed_phases_in_hand="COMBAT"),
                                   CardClasses.EventCard("Suppressive Fire", "Combat Action: Exhaust a unit you "
                                                                             "control to exhaust a target non-warlord "
                                                                             "unit at the same planet.", "Tactic.",
                                                         0, faction, "Common", 1, False, action_in_hand=True,
                                                         allowed_phases_in_hand="COMBAT"),
                                   CardClasses.AttachmentCard("Hostile Environment Gear", "Attach to an army unit.\n"
                                                                                          "Attached unit gets +3 HP.",
                                                              "Wargear. Armor.", 1, faction, "Common", 1, False),
                                   CardClasses.AttachmentCard("Bodyguard", "Attach to an army unit you control.\n"
                                                                           "Forced Reaction: After a unit you control "
                                                                           "is assigned damage by an attack at this "
                                                                           "planet, reassign 1 of that damage to "
                                                                           "attached unit.", "Condition.", 0,
                                                              faction, "Loyal", 2, False),
                                   CardClasses.SupportCard("Imperial Bunker", "Limited. (Limit one Limited card "
                                                                              "per round.)\n"
                                                                              "Interrupt: When you deploy an Astra "
                                                                              "Militarum unit, exhaust this support "
                                                                              "to reduce that unit's cost by 1.",
                                                           "Location.", 1, faction, "Common", True,
                                                           applies_discounts=[True, 1, True],
                                                           is_faction_limited_unique_discounter=True, limited=True),
                                   CardClasses.SupportCard("Rockrete Bunker", "If this card has 4 or more damage on "
                                                                              "it, sacrifice it.\n"
                                                                              "Reaction: After damage is assigned to "
                                                                              "a unit you control, exhaust this "
                                                                              "support to reassign 1 of that damage "
                                                                              "to this support.", "Upgrade.", 1,
                                                           faction, "Common", False),
                                   CardClasses.SupportCard("Catachan Outpost", "Combat Action: Exhaust this support to "
                                                                               "give a target unit +2 ATK for its "
                                                                               "next attack this phase.", "Location.",
                                                           2, faction, "Common", False, action_in_play=True,
                                                           allowed_phases_in_play="COMBAT"),
                                   ]
    return astra_militarum_cards_array
