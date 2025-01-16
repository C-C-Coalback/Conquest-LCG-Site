import CardClasses


def chaos_cards_init():
    chaos_card_array = [CardClasses.WarlordCard("Zarathur, High Sorcerer",
                                                "Interrupt: When damage is assigned to an enemy unit at this"
                                                " planet, increase that damage by 1.","Psyker. Tzeentch.",
                                                "Chaos", 1, 6, 1, 5,
                                                "Bloodied.", 7, 7,""),
                        CardClasses.ArmyCard("Zarathur's Flamers", "Action: Sacrifice this unit to deal 2 "
                                                                   "damage to a target non-warlord "
                                                                   "unit at the same planet.",
                                             "Daemon. Tzeentch.", 2, "Chaos", "Signature",
                                             2, 2, 1, False, ""),
                        CardClasses.SupportCard("Shrine of Warpflame", "Reaction: After an enemy unit is "
                                                                       "destroyed, exhaust this support to return "
                                                                       "the topmost Tzeentch card from "
                                                                       "your discard pile to your hand.",
                                                "Location.", 1, "Chaos", "Signature",
                                                False, ""),
                        CardClasses.EventCard("Infernal Gateway", "Combat Action: Put a Chaos unit with "
                                                                  "printed cost 3 or lower into play "
                                                                  "from your hand at a planet. If that unit "
                                                                  "is still in play at the "
                                                                  "end of the phase, sacrifice it.", "Power. Tzeentch",
                                              1, "Chaos", "Signature", 1, False, ""),
                        CardClasses.AttachmentCard("Mark of Chaos", "Attach to an army unit.\n"
                                                                    "Interrupt: When attached unit leaves play, "
                                                                    "deal 1 damage to each enemy unit at this planet.",
                                                   "Curse.", 0, "Chaos", "Signature", 3,
                                                   False, ""),
                        CardClasses.ArmyCard("Alpha Legion Infiltrator", "", "Alpha Legion. Scout.",
                                             2, "Chaos", "Loyal", 4, 1, 1,
                                             False, ""),
                        CardClasses.ArmyCard("Possessed", "", "Daemon. Elite.", 5, "Chaos",
                                             "Common", 9, 4, 1, False, ""),
                        CardClasses.ArmyCard("Splintered Path Acolyte", "Interrupt: When you deploy a Daemon unit, "
                                                                        "sacrifice this unit to "
                                                                        "reduce its cost by 2.", "Cultist, Tzeentch",
                                             1, "Chaos", "Common", 1, 1, 1,
                                             False, ""),
                        CardClasses.ArmyCard("Khorne Berzerker", "Brutal.", "Khorne. Warrior. World Eaters.",
                                             3, "Chaos", "Common", 2, 4, 1, False, ""
                                             , brutal=True),
                        CardClasses.ArmyCard("Vicious Bloodletter", "Area Effect (3), No Wargear Attachments",
                                             "Daemon. Elite. Khorne.", 5, "Chaos", "Loyal",
                                             4, 4, 0, False, ""),
                        CardClasses.ArmyCard("Umbral Preacher", "Each army unit at this "
                                                                "planet cannot retreat from battle.",
                                             "Cultist. Priest.", 3, "Chaos", "Common",
                                             1, 4, 2, False, ""),
                        CardClasses.ArmyCard("Black Legion Heldrake", "Flying, No Wargear Attachments",
                                             "Black Legion. Daemon. Elite.", 8, "Chaos", "Loyal",
                                             8, 8, 3, False, ""),
                        CardClasses.ArmyCard("Ravenous Flesh Hounds", "No Attachments.\n"
                                                                      "Action: Sacrifice a Cultist unit to "
                                                                      "remove all damage from this unit.",
                                             "Daemon. Elite. Khorne.", 5, "Chaos", "Common",
                                             3, 6, 1, False, ""),
                        CardClasses.ArmyCard("Virulent Plague Squad", "This unit gets +1 ATK for each unit "
                                                                      "in your opponent's discard pile.",
                                             "Death Guard. Nurgle. Warrior.", 4, "Chaos", "Common",
                                             1, 4, 1, False, ""),
                        CardClasses.ArmyCard("Chaos Fanatics", "", "Cultist.", 2, "Chaos",
                                             "Common", 1, 2, 2, False, ""),
                        CardClasses.ArmyCard("Soul Grinder", "No Wargear Attachments.\n"
                                                             "Reaction: After you win a command struggle at this planet,"
                                                             " your opponent must sacrifice a non-warlord unit"
                                                             " at the same planet, if able.",
                                             "Daemon. Elite. War Engine.", 6, "Chaos", "Common",
                                             4, 6, 2, False, ""),
                        CardClasses.ArmyCard("Xavaes Split-Tongue", "Reaction: After an enemy unit at this "
                                                                    "planet is destroyed, put a Cultist token "
                                                                    "into play at your HQ.",
                                             "Slaanesh. Warrior.", 3, "Chaos", "Loyal",
                                             2, 3, 2, True, ""),
                        CardClasses.EventCard("Warpstorm", "Combat Action: Deal 2 damage to each unit without"
                                                           " any attachments at a target planet or HQ.", "Power.",
                                              3, "Chaos", "Common", 1, False, ""),
                        CardClasses.EventCard("Tzeentch's Firestorm", "Action: Deal X damage "
                                                                      "to a target non-warlord unit.", "Power. Tzeentch.",
                                              999, "Chaos", "Loyal", 2, False, ""),
                        CardClasses.EventCard("Promise of Glory", "Deploy Action: Put 2 Cultist "
                                                                  "tokens into play at your HQ.",
                                              "Tactic.", 0, "Chaos", "Common", 1, False, ""),
                        CardClasses.AttachmentCard("Rune-Encrusted Armor", "Attach to an army unit.\n"
                                                                           "Attached unit gets +2 ATK and +2 HP.",
                                                   "Armor. Wargear.", 2, "Chaos", "Common", 1, False, ""),
                        CardClasses.AttachmentCard("Dire Mutation", "Ambush.\nAttach to an army unit.\n"
                                                                    "Forced Interrupt: When attached unit exhaust,"
                                                                    " deal it 1 damage.", "Curse. Tzeentch.",
                                                   1, "Chaos", "Common", 1, False, ""),
                        CardClasses.SupportCard("Fortress of Madness", "Limited.\nInterrupt: When you deploy"
                                                                       " a Chaos unit, exhaust this support to "
                                                                       "reduce that unit's cost by 1.",
                                                "Location.", 1, "Chaos", "Common", True, "",
                                                [True, 1, True]),
                        CardClasses.SupportCard("Murder Cogitator", "Reaction: After a or unit you control "
                                                                    "leaves play, exhaust this support to reveal the "
                                                                    "top card of your deck. If that card is a "
                                                                    "Chaos unit, add it to your hand.", "Upgrade.",
                                                0, "Chaos", "Common", False, "")]
    return chaos_card_array