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
                                                        "reduce its cost by 2.", "Cultist, Tzeentch",
                             1, "Chaos", "Common", 1, 1, 1,
                             False, ""),
        CardClasses.ArmyCard("Khorne Berzerker", "Brutal.", "Khorne. Warrior. World Eaters.",
                             3, "Chaos", "Common", 2, 4, 1, False, ""
                             , brutal=True),
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
                                   type_of_units_allowed_for_attachment="Army"),
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
                             1, "Chaos", "Common", 3, 3, 1, False),
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
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True)
    ]
    return chaos_card_array
