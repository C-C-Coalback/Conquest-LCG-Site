from .. import CardClasses


def chaos_cards_init():
    faction = "Chaos"
    chaos_card_array = [
        CardClasses.WarlordCard("Zarathur, High Sorcerer",
                                "Interrupt: When damage is assigned to an enemy unit at this"
                                " planet, increase that damage by 1.", "Psyker. Tzeentch.",
                                "Chaos", 1, 6, 1, 5,
                                "Bloodied.", 7, 7,
                                ['1x Mark of Chaos', '1x Shrine of Warpflame',
                                 '2x Infernal Gateway', "4x Zarathur's Flamers"]
                                ),
        CardClasses.ArmyCard("Zarathur's Flamers", "Action: Sacrifice this unit to deal 2 "
                                                   "damage to a target non-warlord "
                                                   "unit at the same planet.",
                             "Daemon. Tzeentch.", 2, "Chaos", "Signature",
                             2, 2, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
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
                              1, "Chaos", "Signature", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Mark of Chaos", "Attach to an army unit.\n"
                                                    "Interrupt: When attached unit leaves play, "
                                                    "deal 1 damage to each enemy unit at this planet.",
                                   "Curse.", 0, "Chaos", "Signature", 3,
                                   False, type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Alpha Legion Infiltrator", "", "Alpha Legion. Scout.",
                             2, "Chaos", "Loyal", 4, 1, 1,
                             False, ""),
        CardClasses.ArmyCard("Possessed", "", "Daemon. Elite.", 5, "Chaos",
                             "Common", 9, 4, 1, False, ""),
        CardClasses.ArmyCard("Splintered Path Acolyte", "Interrupt: When you deploy a Daemon unit, "
                                                        "sacrifice this unit to "
                                                        "reduce its cost by 2.", "Cultist. Tzeentch",
                             1, "Chaos", "Common", 1, 1, 1,
                             False, ""),
        CardClasses.ArmyCard("Khorne Berzerker", "Brutal.", "Khorne. Warrior. World Eaters.",
                             3, "Chaos", "Common", 2, 4, 1, False, "", brutal=True),
        CardClasses.ArmyCard("Vicious Bloodletter", "Area Effect (3), No Wargear Attachments",
                             "Daemon. Elite. Khorne.", 5, "Chaos", "Loyal",
                             4, 4, 0, False, area_effect=3,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Umbral Preacher", "Each army unit at this "
                                                "planet cannot retreat from battle.",
                             "Cultist. Priest.", 3, "Chaos", "Common",
                             1, 4, 2, False, ""),
        CardClasses.ArmyCard("Black Legion Heldrake", "Flying, No Wargear Attachments",
                             "Black Legion. Daemon. Elite.", 8, "Chaos", "Loyal",
                             8, 8, 3, False, "", flying=True,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Ravenous Flesh Hounds", "No Attachments.\n"
                                                      "Action: Sacrifice a Cultist unit to "
                                                      "remove all damage from this unit.",
                             "Daemon. Elite. Khorne.", 5, "Chaos", "Common",
                             3, 6, 1, False, action_in_play=True, allowed_phases_in_play="ALL",
                             no_attachments=True),
        CardClasses.ArmyCard("Virulent Plague Squad", "This unit gets +1 ATK for each unit "
                                                      "in your opponent's discard pile.",
                             "Death Guard. Nurgle. Warrior.", 4, "Chaos", "Common",
                             1, 4, 1, False),
        CardClasses.ArmyCard("Chaos Fanatics", "", "Cultist.", 2, "Chaos",
                             "Common", 1, 2, 2, False, ""),
        CardClasses.ArmyCard("Soul Grinder", "No Wargear Attachments.\n"
                                             "Reaction: After you win a command "
                                             "struggle at this planet,"
                                             " your opponent must sacrifice a non-warlord unit"
                                             " at the same planet, if able.",
                             "Daemon. Elite. War Engine.", 6, "Chaos", "Common",
                             4, 6, 2, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Xavaes Split-Tongue", "Reaction: After an enemy unit at this "
                                                    "planet is destroyed, put a Cultist token "
                                                    "into play at your HQ.",
                             "Slaanesh. Warrior.", 3, "Chaos", "Loyal",
                             2, 3, 2, True, ""),
        CardClasses.EventCard("Warpstorm", "Combat Action: Deal 2 damage to each unit without"
                                           " any attachments at a target planet or HQ.", "Power.",
                              3, "Chaos", "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="COMBAT"),
        CardClasses.EventCard("Tzeentch's Firestorm", "Action: Deal X damage "
                                                      "to a target non-warlord unit.", "Power. Tzeentch.",
                              0, "Chaos", "Loyal", 2, False, action_in_hand=True,
                              allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Promise of Glory", "Deploy Action: Put 2 Cultist "
                                                  "tokens into play at your HQ.",
                              "Tactic.", 0, "Chaos", "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("Rune-Encrusted Armor", "Attach to an army unit.\n"
                                                           "Attached unit gets +2 ATK and +2 HP.",
                                   "Armor. Wargear.", 2, "Chaos", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", extra_attack=2,
                                   extra_health=2),
        CardClasses.AttachmentCard("Dire Mutation", "Ambush.\nAttach to an army unit.\n"
                                                    "Forced Interrupt: When attached unit exhaust,"
                                                    " deal it 1 damage.", "Curse. Tzeentch.",
                                   1, "Chaos", "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", ambush=True,
                                   action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.SupportCard("Fortress of Madness", "Limited.\nInterrupt: When you deploy"
                                                       " a Chaos unit, exhaust this support to "
                                                       "reduce that unit's cost by 1.",
                                "Location.", 1, "Chaos", "Common", True, "",
                                [True, 1, True],
                                is_faction_limited_unique_discounter=True, limited=True),
        CardClasses.SupportCard("Murder Cogitator", "Reaction: After a or unit you control "
                                                    "leaves play, exhaust this support to reveal the "
                                                    "top card of your deck. If that card is a "
                                                    "Chaos unit, add it to your hand.", "Upgrade.",
                                0, "Chaos", "Common", False, ""),
        CardClasses.ArmyCard("Roghrax Bloodhand", "Brutal.\n"
                                                  "BLOODTHIRST - During a combat round in which 1 or more units "
                                                  "have been destroyed at this planet, double this unit's ATK.",
                             "Warrior. Khorne. World Eaters.", 4, "Chaos", "Loyal", 2, 5, 1, True, brutal=True),
        CardClasses.EventCard("Ecstatic Seizures", "Action: Discard each attachment from "
                                                   "each unit at a target planet.", "Power. Slaanesh.",
                              2, "Chaos", "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Venomous Fiend", "While you control a non-Chaos warlord, this unit gains Mobile.\n"
                                               "Reaction: After this unit moves to a planet, deal X damage to a "
                                               "target enemy army unit at that planet. X is the number of command "
                                               "icons the target unit has.", "Daemon. Slaanesh. Elite.",
                             5, "Chaos", "Common", 3, 5, 2, False),
        CardClasses.ArmyCard("Death Guard Infantry", "", "Warrior. Death Guard. Nurgle.",
                             3, "Chaos", "Common", 2, 4, 1, False),
        CardClasses.ArmyCard("Heretek Inventor", "FORCED REACTION: After this unit enters play, your opponent may "
                                                 "move it to a planet of his choice.", "Scholar.",
                             1, "Chaos", "Loyal", 3, 3, 1, False),
        CardClasses.WarlordCard("Ku'gath Plaguefather", "Reaction: After this warlord is declared as an attacker, "
                                                        "move 1 damage from this warlord to another unit "
                                                        "at this planet.", "Deamon. Nurgle.", "Chaos",
                                1, 7, 1, 5, "Bloodied.", 7, 7,
                                ["4x Ku'gath's Nurglings", "1x Vile Laboratory",
                                 "1x The Plaguefather's Banner", "2x Fetid Haze"]),
        CardClasses.ArmyCard("Ku'gath's Nurglings", "FORCED REACTION: After a unit moves to this planet, "
                                                    "deal it 1 damage.", "Daemon. Nurgle.",
                             2, "Chaos", "Signature", 2, 2, 1, False),
        CardClasses.SupportCard("Vile Laboratory", "Deploy Action: Exhaust this support to have your opponent choose "
                                                   "and move a non-Vehicle unit he controls from a "
                                                   "target planet to an adjacent planet of his choice.",
                                "Location.", 2, faction, "Signature", False,
                                action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.AttachmentCard("The Plaguefather's Banner", "Attach to a Nurgle unit.\n"
                                                                "Attached unit gets +1 HP.\n"
                                                                "Reaction: After attached unit is declared as "
                                                                "an attacker, move 1 damage from attached unit "
                                                                "to another unit at this planet.", "Wargear. Standard.",
                                   1, faction, "Signature", 3, True, required_traits="Nurgle", extra_health=1),
        CardClasses.EventCard("Fetid Haze", "Combat Action: Remove all damage from a target Nurgle "
                                            "unit you control. Then, have your opponent deal an amount of "
                                            "indirect damage equal to the damage removed among army units he "
                                            "controls at the same planet.", "Power. Nurgle.",
                              3, faction, "Signature", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Rotten Plaguebearers", "Action: Exhaust this unit to deal 1 damage to a target "
                                                     "unit at this planet.", "Daemon. Nurgle.",
                             2, faction, "Common", 0, 2, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Nurgling Bomb", "Combat Action: Target a planet. For each non-Nurgle unit at that"
                                               " planet, its controller must choose to either deal 1 damage "
                                               "to it or rout it.", "Tactic. Nurgle.",
                              3, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.SupportCard("Throne of Vainglory", "Action: Exhaust this support to discard the top card of your "
                                                       "deck. If the printed cost of the discarded card is "
                                                       "3 or higher, put 2 Cultist tokens into play at your HQ.",
                                "Upgrade. Slaanesh.", 3, faction, "Loyal", False,
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Gleeful Plague Beast", "No Wargear Attachments.\n"
                                                     "FORCED REACTION: After the combat phase begins, deal 1 damage "
                                                     "to each unit at this planet.", "Daemon. Nurgle. Elite.",
                             5, faction, "Loyal", 3, 5, 1, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Doombolt", "Deploy Action: Deal X damage to a target enemy army unit. "
                                          "X is the amount of damage on that unit.", "Power.",
                              1, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("Blight Grenades", "Combat Action: Sacrifice this attachment to give attached "
                                                      "unit Area Effect (2) until the end of the combat phase.",
                                   "Wargear. Nurgle.", 1, faction, "Common", 1, False,
                                   action_in_play=True, allowed_phases_in_play="COMBAT",
                                   type_of_units_allowed_for_attachment="Army", required_traits="Nurgle"),
        CardClasses.ArmyCard("Noise Marine Zealots", "This unit gets +2 ATK while it is at a planet with a warlord.",
                             "Warrior. Slaanesh.", 3, faction, "Common", 2, 3, 1, False),
        CardClasses.SupportCard("Turbulent Rift", "Reaction: After you deploy an Elite unit, deal 1 damage to that "
                                                  "unit to deal 1 damage to each enemy unit at that planet.",
                                "Location.", 1, faction, "Common", False),
        CardClasses.EventCard("Cacophonic Choir", "Deploy Action: Exhaust your warlord to have your opponent deal "
                                                  "X indirect damage among units he controls. "
                                                  "X is the number of units your opponent controls.",
                              "Power. Maneuver. Slaanesh.", 2, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.ArmyCard("Ancient Keeper of Secrets", "No Wargear Attachments.\n"
                                                          "Action: Sacrifice a Cultist unit to ready this unit.",
                             "Daemon. Slaanesh. Elite.", 7, faction, "Common", 5, 5, 3, False,
                             wargear_attachments_permitted=False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Slaanesh's Temptation", "Attach to a planet.\n"
                                                            "Increase the cost of each enemy unit being deployed "
                                                            "at another planet by 1.\n"
                                                            "FORCED REACTION: After a battle at attached planet ends, "
                                                            "sacrifice this attachment.", "Power. Slaanesh.",
                                   2, faction, "Loyal", 2, True, planet_attachment=True),
        CardClasses.AttachmentCard("Doom Siren", "Attach to an army unit you control.\n"
                                                 "Reaction: After attached unit uses its Area Effect ability, "
                                                 "deal damage equal to its Area Effect value to each enemy unit "
                                                 "at each adjacent planet. Then, sacrifice the attached unit.",
                                   "Wargear. Slaanesh.", 2, faction, "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.ArmyCard("Ravening Psychopath", "Reaction: After this unit resolves an attack, deal 1 damage to "
                                                    "this unit to deal 1 damage to an enemy army unit at the "
                                                    "same planet.", "Ally. Cultist. Khorne.",
                             2, faction, "Common", 1, 3, 1, False),
        CardClasses.EventCard("Sowing Chaos", "Deploy Action: Destroy each army unit with printed cost 2"
                                              " or lower at each tech planet (blue).", "Tactic.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.WarlordCard("Ba'ar Zul the Hate-Bound", "Reaction: After a unit you control at this planet "
                                                            "takes damage, move all of that damage to this warlord.",
                                "Khorne. Warrior.", faction, 0, 5, 3, 11, "Bloodied.", 7, 7,
                                ["4x Ba'ar Zul's Cleavers", "1x Kaerux Erameas",
                                 "2x Blood For The Blood God!", "1x The Butcher's Nails"]),
        CardClasses.ArmyCard("Ba'ar Zul's Cleavers", "Action: Deal 2 damage to this unit to have it get +2 "
                                                     "ATK for its next attack this phase. (Limit once per phase)",
                             "Warrior. Khorne. World Eaters.", 3, faction, "Signature",
                             2, 5, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.SupportCard("Kaerux Erameas", "Combat Action: Exhaust this support to resolve a battle at a "
                                                  "non-first planet without a warlord. Use this ability only if no "
                                                  "battle has been initiated this phase.", "Location. Space Hulk.",
                                2, faction, "Signature", True, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.EventCard("Blood For The Blood God!", "Combat Action: Deal 1 damage to each undamaged unit "
                                                          "at a target planet.", "Tactic. Khorne.",
                              1, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("The Butcher's Nails", "Attach to your warlord.\n"
                                                          "Attached unit gains Brutal while it is hale.\n"
                                                          "Attached unit gains Armorbane while it is bloodied.",
                                   "Wargear. World Eaters.", 1, faction, "Signature", 3, False,
                                   type_of_units_allowed_for_attachment="Warlord", must_be_own_unit=True),
        CardClasses.ArmyCard("Prodigal Sons Disciple", "Reaction: After this unit resolves an attack against an "
                                                       "enemy army unit, deal X unpreventable damage to a target "
                                                       "enemy unit at this planet. X is the number of command icons"
                                                       " the targeted unit has.", "Psyker. Tzeentch. Elite.",
                             5, faction, "Loyal", 3, 6, 3, False),
        CardClasses.ArmyCard("Seer of Deceit", "While this unit is at a tech planet (blue), it gains: +1 card"
                                               " when command struggle won at this planet.", "Scholar. Ally.",
                             3, faction, "Common", 3, 3, 1, False),
        CardClasses.AttachmentCard("Khornate Chain Axe", "Attach to an army unit.\n"
                                                         "Attached unit gets +2 ATK.\n"
                                                         "BLOODTHIRST - During a round in which 1 or more units "
                                                         "have been destroyed at this planet, attached unit "
                                                         "gains Brutal.", "Wargear. Weapon. Khorne.",
                                   1, faction, "Common", 1, False, extra_attack=2,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Master Warpsmith", "Reaction: After you sacrifice a Cultist token, reduce the "
                                                 "cost of the next Elite unit you deploy this phase by 1.", "Scholar.",
                             4, faction, "Common", 2, 4, 2, False),
        CardClasses.SupportCard("Corrupted Teleportarium", "Action: Exhaust this support to move an Elite unit you"
                                                           " control from a tech planet (blue) to another planet.",
                                "Location.", 1, faction, "Common", False,
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Berzerker Warriors", "Interrupt: When an enemy unit is destroyed, "
                                                   "deploy this unit from your hand at the same "
                                                   "planet as the destroyed unit.", "Warrior. Khorne. World Eaters.",
                             2, faction, "Loyal", 3, 2, 0, False),
        CardClasses.SupportCard("Killing Field", "Action: Exhaust this support to have each unit at a target planet"
                                                 " lose Ranged until the end of the phase.", "Location.",
                                1, faction, "Common", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Staff of Change", "Attach to an army unit.\n"
                                                      "Limit 1 per unit.\n"
                                                      "Reaction: After you win a command struggle at this planet,"
                                                      " deal 2 damage to a target unit at this planet.",
                                   "Wargear. Weapon. Tzeentch.", 1, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", limit_one_per_unit=True),
        CardClasses.ArmyCard("Frenzied Bloodthirster", "No Wargear Attachments.\n"
                                                       "Immune to Power events.\n"
                                                       "BLOODTHIRST - During a combat round in which 1 or more units "
                                                       "have been destroyed at this planet, this unit gains "
                                                       "Armorbane, Brutal, and Flying.", "Daemon. Khorne. Elite.",
                             10, faction, "Loyal", 8, 8, 2, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Warp Rift", "HEADQUARTERS ACTION: Switch a target planet with an adjacent planet. "
                                           "(Units that were at a switched-out planet are now at "
                                           "the switched-in planet.)", "Power. Tzeentch.", 1, faction, "Loyal",
                              2, False, action_in_hand=True, allowed_phases_in_hand="HEADQUARTERS"),
        CardClasses.ArmyCard("Sathariel the Invokator", "Deep Strike (3).\n"
                                                        "Reaction: After a combat round at this planet begins, "
                                                        "return a Chaos Power event from your discard pile to"
                                                        " your hand.", "Psyker. Fallen. Elite.",
                             5, faction, "Common", 4, 4, 1, True, deepstrike=3),
        CardClasses.EventCard("The Prince's Might", "Deep Strike (1).\n"
                                                    "Reaction: After you Deep Strike this event, Daemon units at "
                                                    "this planet cannot be damaged by units with printed cost 2 "
                                                    "or lower until the end of the phase.", "Tactic.",
                              0, faction, "Loyal", 2, False, deepstrike=1),
        CardClasses.ArmyCard("Infectious Nurgling", "Armorbane.", "Daemon. Nurgle.",
                             1, faction, "Common", 2, 1, 0, False, armorbane=True),
        CardClasses.ArmyCard("Seekers of Slaanesh", "No Wargear Attachments.\n"
                                                    "Action: Sacrifice a Cultist unit at this planet to draw 1 card.",
                             "Daemon. Slaanesh. Elite.", 5, faction, "Common", 4, 5, 2, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Mark of Slaanesh", "Attach to an army unit you control.\n"
                                                       "Interrupt: When attached unit leaves play, "
                                                       "move an army unit you control to this planet.",
                                   "Curse. Slaanesh.", 0, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Disciple of Excess", "Each Elite unit you control at this planet gains "
                                                   "“Cannot be routed or exhausted by card effects.”",
                             "Cultist. Slaanesh.", 2, faction, "Common", 1, 3, 1, False),
        CardClasses.SupportCard("Blood Rain Tempest", "Reaction: After the combat phase begins, sacrifice this support"
                                                      " to reverse the order in which planets are checked for battles."
                                                      " (Start with the last planet and finish with the first planet.)",
                                "Upgrade.", 1, faction, "Common", False),
        CardClasses.ArmyCard("Noise Marines Warband", "Area Effect (1), Deep Strike (2)", "Soldier. Slaanesh.",
                             4, faction, "Loyal", 2, 3, 1, False, area_effect=2, deepstrike=2),
        CardClasses.EventCard("Ominous Wind", "Action: Draw X cards. X is the highest printed cost among units "
                                              "you control. Then, discard 4 cards from your hand.", "Power. Nurgle.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Sickening Helbrute", "Brutal.\n"
                                                   "FORCED REACTION: After a unit at this planet is declared as a "
                                                   "defender, deal 1 damage to it.", "Vehicle. Nurgle. Elite.",
                             7, faction, "Common", 2, 9, 2, False, brutal=True),
        CardClasses.ArmyCard("Purveyor of Hubris", "Interrupt: When your opponent deploys a non-Elite unit at this "
                                                   "planet, increase its cost by 2.", "Soldier. Slaanesh.",
                             4, faction, "Common", 3, 4, 2, False),
        CardClasses.AttachmentCard("Cloud of Flies", "Attach to a Nurgle army unit you control.\n"
                                                     "Reaction: After a combat round begins at this planet, "
                                                     "each player deals 2 indirect damage among non-Nurgle units "
                                                     "he controls at this planet, if able.", "Blessing.",
                                   1, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   must_be_own_unit=True, required_traits="Nurgle"),
        CardClasses.WarlordCard("Vha'shaelhur", "Area Effect (1).\n"
                                                "Reaction: After an enemy army unit is destroyed while this "
                                                "unit is attacking, put a Cultist token into play at your HQ. "
                                                "(Limit once per attack.)", "Daemon. Slaanesh.",
                                faction, 1, 8, 1, 6, "Bloodied.", 7, 7,
                                ["4x Alluring Daemonette", "1x Tower of Worship",
                                 "2x Daemonic Incursion", "1x Predatory Instinct"], area_effect=1),
        CardClasses.ArmyCard("Alluring Daemonette", "Combat Action: Sacrifice a Cultist unit you control to move an \n"
                                                    "enemy army unit at an adjacent planet to this planet. "
                                                    "(Limit once per phase.)", "Daemon. Slaanesh.", 3, faction,
                             "Signature", 3, 2, 1, False, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Tower of Worship", "Reaction: After you deploy a Daemon unit, put a "
                                                    "Cultist token into play at your HQ.", "Location. Slaanesh.",
                                1, faction, "Signature", True),
        CardClasses.EventCard("Daemonic Incursion", "Action: Search the top 6 cards of your deck for a Daemon unit. "
                                                    "Reveal it, add it to your hand, and put the remaining cards on"
                                                    " the bottom of your deck in any order.", "Power.",
                              1, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Predatory Instinct", "Attach to a Chaos unit you control."
                                                         "Attached unit gains Area Effect (1).", "Skill.",
                                   2, faction, "Signature", 3, False,
                                   unit_must_match_faction=True, must_be_own_unit=True),
        CardClasses.ArmyCard("Charging Juggernaut", "While this unit has an attachment, it gets +1 HP and it cannot be"
                                                    " routed until a combat round ended this round.\n"
                                                    "Forced Reaction: After the deploy phase begins, move this unit to"
                                                    " the first planet. Then deal 2 damage to an enemy unit"
                                                    " at that planet.", "Daemon. Khorne.",
                             3, faction, "Loyal", 4, 2, 1, False),
        CardClasses.ArmyCard("Advocator of Blood", "Brutal.\n"
                                                   "While any warlord is bloodied, this unit gains 1 command icon.\n"
                                                   "Reaction: After this unit enters play, move up to 2 damage from "
                                                   "Chaos army units and Khorne units to this unit.",
                             "Daemon. Khorne.", 3, faction, "Common", 1, 5, 1, False, brutal=True),
        CardClasses.ArmyCard("The Masque", "Sweep (1). Retaliate (4).\n"
                                           "Reaction: After this unit resolves an attack, put a Cultist token into "
                                           "play at this planet.", "Daemon. Slaanesh. Elite.",
                             6, faction, "Common", 3, 6, 2, True, sweep=1, retaliate=4),
        CardClasses.ArmyCard("Expendable Pawn", "Reaction: After a unit is assigned damage at this planet or an "
                                                "adjacent planet, sacrifice this unit to prevent 2 of that damage.",
                             "Cultist. Khorne.", 1, faction, "Common", 1, 1, 1, False),
        CardClasses.ArmyCard("Uncontrollable Rioters", "Cost of units you deploy is increased by 1.\n"
                                                       "This unit cannot change control more than once per round.\n"
                                                       "Action: Give control of this unit to your opponent.",
                             "Cultist. Mob.", 0, faction, "Loyal", 2, 1, 0, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Conjuring Warmaster", "While at a planet with your warlord, this unit gains Mobile.\n"
                                                    "Combat Action: Exhaust an Elite unit you control at a planet to "
                                                    "move it to this planet. (Limit once per phase.)",
                             "Warrior. Slaanesh.", 3, faction, "Loyal", 2, 3, 1, False,
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.WarlordCard("Vael the Gifted", "Effects of events you play cannot be cancelled.\n"
                                                   "When the game starts, remove each Ritual card"
                                                   " in your deck from the game.\n"
                                                   "You may play Ritual events you removed from the "
                                                   "game as if they were in your hand. (Limit once per round.)",
                                "Ritualist. Chaos Undivided.", faction, 2, 6, 2, 6,
                                "Bloodied.\n"
                                "You may play Ritual events you removed from the game as if they were "
                                "in your hand. (Limit once per game.)", 7, 7,
                                ["2x Drammask Nane", "1x Sacrificial Altar", "1x Talisman of Denial",
                                 "1x The Blood Pits", "1x The Grand Plan",
                                 "1x The Inevitable Decay", "1x The Orgiastic Feast"]),
        CardClasses.ArmyCard("Drammask Nane", "Reaction: After you play a Ritual event, sacrifice a unit at this planet"
                                              " to have up to 4 units you control at this planet get +1 ATK until"
                                              " the end of the phase.", "Sorcerer.",
                             3, faction, "Signature", 2, 4, 2, True),
        CardClasses.SupportCard("Sacrificial Altar", "Deploy Action: Exhaust this support and target a non first-planet"
                                                     " to draw 1 card an gain 1 resource. If your opponent wins a "
                                                     "command struggle at the targeted planet this round, they draw"
                                                     " 1 card and gain 1 resource.", "Location.",
                                1, faction, "Signature", False, action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.AttachmentCard("Talisman of Denial", "Attach to your warlord.\n"
                                                         "Attached unit gains 3 command icons.\n"
                                                         "Combat Action: Sacrifice this attachment to switch the"
                                                         " damage on your warlord with the damage on a "
                                                         "hale warlord at this planet.", "Wargear.",
                                   0, faction, "Signature", 3, False, type_of_units_allowed_for_attachment="Warlord",
                                   action_in_play=True, allowed_phases_in_play="COMBAT", must_be_own_unit=True,
                                   extra_command=3),
        CardClasses.EventCard("The Blood Pits", "Reaction: After your warlord commits to a planet with an enemy"
                                                " warlord, choose up to 1 enemy unit at each planet without a warlord."
                                                " Deal 2 damage to each chosen unit.", "Ritual. Khorne.",
                              1, faction, "Signature", 1, False),
        CardClasses.EventCard("The Grand Plan", "Interrupt: When a player places a planet in their victory display, "
                                                "sacrifice an army unit at a planet with no enemy army unit to remove"
                                                " that planet from the game instead. At the end of the next round, "
                                                "place the planet in that player's victory display and draw 4 cards.",
                              "Ritual. Tzeentch.", 1, faction, "Signature", 1, False),
        CardClasses.EventCard("The Inevitable Decay", "Reaction: After an enemy army unit enters play or moves to a "
                                                      "planet with a unique unit you control, exhaust it and move up "
                                                      "to 2 damage from units at the same planet to that enemy unit.",
                              "Ritual. Nurgle.", 1, faction, "Signature", 1, False),
        CardClasses.EventCard("The Orgiastic Feast", "Command Action: Rally 12 up to two units with cost 4 or lower, "
                                                     "put them into play at a target planet and shuffle your deck. "
                                                     "If those units are still in play at the end of the round, "
                                                     "return them to your hand.", "Ritual. Slaanesh.",
                              4, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="COMMAND"),
        CardClasses.ArmyCard("Galvax the Bloated", "This unit gets +1 ATK and +1 HP for each cultist"
                                                   " unit you control at this planet.\n"
                                                   "Reaction: After a Cultist unit you control leaves play from this "
                                                   "planet, deal 1 damage to a unit at this planet.",
                             "Touched. Nurgle.", 3, faction, "Loyal", 2, 4, 1, True),
        CardClasses.ArmyCard("Ireful Vanguard", "While any warlord is bloodied, this unit gets +1 ATK and +1 HP.\n"
                                                "Action: Deal 3 damage to an army unit at this planet."
                                                " Use this ability only if your opponent won a command struggle at"
                                                " this planet this round (Limit once per round.)", "Warrior. Khorne.",
                             3, faction, "Loyal", 3, 4, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Tides of Chaos", "Reaction: After your warlord commits to a planet, each army unit "
                                                "gains an amount of command icons equal to their ATK value "
                                                "until the end of the phase.", "Tactic.",
                              1, faction, "Loyal", 2, False),
        CardClasses.AttachmentCard("Medallion of Betrayal", "Attach to a non-warlord unit.\n"
                                                            "Attached unit gets +1 ATK and +1 HP,"
                                                            " double if it is a Cultist.\n"
                                                            "Reaction: After this card enters your discard pile, if you"
                                                            " control no Cultist token, put a Cultist token into "
                                                            "play at your HQ.", "Wargear. Weapon. Slaanesh.",
                                   1, faction, "Loyal", 2, False, extra_health=1, extra_attack=1,
                                   type_of_units_allowed_for_attachment="Army/Synapse/Token"),
        CardClasses.ArmyCard("Cajivak the Hateful", "Interrupt: When damage equal to or greater than your warlord's "
                                                    "remaining HP is assigned or moved to your warlord, either "
                                                    "(choose one): put this unit into play from your hand at a planet,"
                                                    " or discard this card from your hand to draw 2 cards.",
                             "Warrior. Khorne.", 2, faction, "Loyal", 2, 2, 2, True)
    ]
    return chaos_card_array
