from .. import CardClasses


def orks_cards_init():
    faction = "Orks"
    orks_card_array = [
        CardClasses.WarlordCard("Nazdreg",
                                "Each other unit you control at this planet gains Brutal. ",
                                "Warrior. Warboss.", "Orks", 2, 7, 2, 5, "Bloodied.", 7, 7,
                                ['1x Cybork Body', '1x Kraktoof Hall',
                                 '2x Bigga Is Betta', "4x Nazdreg's Flash Gitz"]
                                ),
        CardClasses.ArmyCard("Nazdreg's Flash Gitz",
                             "Combat Action: Deal this unit 1 damage to ready it. "
                             "(Limit once per phase.)",
                             "Nob. Warrior.", 3, "Orks", "Signature", 2, 4, 1, False,
                             "Nazdreg's_Flash_Gitz",
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Kraktoof Hall",
                                "Combat Action: Exhaust this support to move 1 damage from a "
                                "target unit you control to another target unit "
                                "at the same planet.", "Location.", 2, "Orks", "Signature",
                                False, "Kraktoof_Hall", action_in_play=True,
                                allowed_phases_in_play="COMBAT"),
        CardClasses.EventCard("Bigga Is Betta", "Interrupt: When you deploy an Orks unit, "
                                                "reduce its cost by 2. "
                                                "Deal 1 damage to that unit after it enters play.",
                              "Tactic.",
                              0, "Orks", "Signature", 1, False,
                              "Bigga_Is_Betta", [True, 2, True]),
        CardClasses.AttachmentCard("Cybork Body", "Attach to an army unit.\nDouble attached unit's HP.",
                                   "Wargear. Bionics.", 1, "Orks", "Signature", 3, False,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Sniveling Grot", "", "Runt. Ally.", 0, "Orks", "Common", 1, 1, 0, False),
        CardClasses.ArmyCard("Goff Nob", "", "Warrior. Nob. Elite.", 5, "Orks", "Loyal", 6, 6, 0, False,
                             "Goff_Nob"),
        CardClasses.ArmyCard("Weirdboy Maniak", "Reaction: After this unit enters play, "
                                                "deal 1 damage to each other unit at this planet.",
                             "Oddboy. Psyker.", 3, "Orks", "Loyal", 2, 4, 1, False,
                             "Weirdboy_Maniak"),
        CardClasses.ArmyCard("Tankbusta Bommaz", "This unit deals double damage to enemy Vehicle units.",
                             "Warrior. Boyz.", 4, "Orks", "Common", 3, 4, 2, False,
                             "Tankbusta_Bommaz"),
        CardClasses.ArmyCard("Rugged Killa Kans", "No Wargear Attachments.\nBrutal.", "Vehicle. Walker.",
                             4, "Orks", "Loyal", 2, 5, 2, False,
                             "Rugged_Killa_Kans", brutal=True, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Enraged Ork", "Brutal.", "Warrior. Boyz.", 2, "Orks", "Loyal", 0, 5, 1,
                             False, "Enraged_Ork", brutal=True),
        CardClasses.ArmyCard("Crushface", "Interrupt: When you deploy another Orks unit at this planet, "
                                          "reduce its cost by 1.", "Warrior. Nob.", 3, "Orks", "Loyal",
                             2, 3, 2, True, "Crushface", applies_discounts=[True, 1, True]),
        CardClasses.ArmyCard("Bad Dok", "This unit gains 3 command icons while it is damaged.",
                             "Oddboy. Nob.", 2,
                             "Orks", "Common", 1, 4, 1, False, "Bad_Dok"),
        CardClasses.ArmyCard("Rokkitboy", "Each enemy unit at this planet loses the Flying keyword.",
                             "Warrior. Boyz.", 2, "Orks", "Common", 2, 2, 1, False,
                             "Rokkit_Boy"),
        CardClasses.ArmyCard("Goff Boyz", "This unit gets +3 ATK while it is at the first planet.",
                             "Warrior. Boyz. Ally.", 1, "Orks", "Common", 0, 2, 0, False,
                             "Goff_Boyz"),
        CardClasses.ArmyCard("Shoota Mob", "", "Warrior. Boyz.", 1, "Orks", "Common", 2, 1, 1, False,
                             "Shoota_Mob"),
        CardClasses.ArmyCard("Burna Boyz",
                             "Reaction: After this unit declares an attack against an enemy unit, "
                             "deal 1 damage to a different enemy unit at the same planet.",
                             "Warrior. Boyz.", 4, "Orks", "Common", 5, 3, 1, False,
                             "Burna_Boyz"),
        CardClasses.EventCard("Battle Cry", "Play only during a battle.\nCombat Action: "
                                            "Each unit you control gets "
                                            "+2 ATK until the end of the battle.",
                              "Power.", 3, "Orks", "Loyal", 2, False,
                              "Battle_Cry", action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.EventCard("Snotling Attack", "Deploy Action: Put 4 Snotlings tokens "
                                                 "into play divided among any number of planets.",
                              "Tactic.",
                              2, "Orks", "Common", 1, False,
                              "Snotling_Attack", action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.EventCard("Squig Bombin'", "Action: Destroy a target support card.", "Tactic.",
                              2, "Orks", "Common", 1, False, "Squig_Bombin'", action_in_hand=True,
                              allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Rokkit Launcha",
                                   "Attach to an army unit.Attached unit gains Ranged.",
                                   "Wargear. Weapon.", 1, "Orks", "Common", 1, False,
                                   "Rokkit_Launcha", type_of_units_allowed_for_attachment="Army"),
        CardClasses.SupportCard("Ork Kannon", "Combat Action: Exhaust this support to target a planet. "
                                              "Each player deals 1 indirect damage "
                                              "among the units he controls at "
                                              "that planet.", "Artillery. Weapon.", 1, "Orks", "Common",
                                False, "Ork_Kannon", action_in_play=True,
                                allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Bigtoof Banna", "Limited.\nInterrupt: When you deploy an Orks unit, "
                                                 "exhaust this support to reduce that unit's cost by 1.",
                                "Upgrade.", 1, "Orks", "Common", True,
                                "Bigtoof_Banna", applies_discounts=[True, 1, True],
                                is_faction_limited_unique_discounter=True, limited=True),
        CardClasses.SupportCard("Tellyporta Pad",
                                "Combat Action: Exhaust this support to move an Orks unit "
                                "you control to the first planet.",
                                "Location.", 2, "Orks", "Common", False,
                                "Tellyporta_Pad", action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Boss Zugnog", "Combat Action: Target up to 2 Orks army units you control at this planet. "
                                            "Deal 1 damage to each targeted unit to move them to the first "
                                            "planet. (Limit once per phase.)", "Warrior. Nob.",
                             4, "Orks", "Loyal", 4, 4, 1, True, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Ork Landa", "Combat Action: Exhaust this support to discard the top card of "
                                             "your deck. If it is an Orks card with an odd printed cost, "
                                             "your opponent deals X indirect damage among units he controls. "
                                             "X is the printed cost of the discarded card.", "Upgrade.",
                                2, "Orks", "Common", True, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Goff Brawlers", "While you control a non-Orks warlord, this unit gains 1 command icon.\n"
                                              "Reaction: After this unit readies, each player deals 1 indirect damage "
                                              "among units he controls at this planet.", "Warrior. Boyz.",
                             2, "Orks", "Common", 2, 3, 0, False),
        CardClasses.ArmyCard("Deathskull Lootas", "Reaction: After this unit damages an enemy unit by an attack,"
                                                  " destroy a target enemy support card.", "Warrior.",
                             4, "Orks", "Common", 2, 3, 2, False),
        CardClasses.EventCard("Smash 'n Bash", "Combat Action: Deal 1 damage to each unit you control at a target "
                                               "planet without an enemy warlord to ready up to 3 "
                                               "units you control at that planet.", "Tactic.",
                              2, "Orks", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Attack Squig Herd", "No Wargear Attachments.", "Creature. Squig.",
                             4, faction, "Common", 4, 6, 0, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Dakka Dakka Dakka!", "Deploy Action: Exhaust your warlord to"
                                                    " deal 1 damage to each unit.", "Tactic. Maneuver.",
                              2, faction, "Loyal", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.SupportCard("Kustom Field Generator", "Reaction: After an Orks unit you control is assigned "
                                                          "damage by an attack, exhaust this support to prevent "
                                                          "all of that damage. Then, deal an amount of indirect "
                                                          "damage equal to the damage prevented among Orks units "
                                                          "you control at the same planet as the defender.",
                                "Upgrade.", 2, faction, "Common", False),
        CardClasses.ArmyCard("Mekaniak Repair Krew", "Action: Exhaust this unit to ready a target Orks support card "
                                                     "you control. Then deal 1 damage to this unit.", "Oddboy.",
                             3, faction, "Loyal", 2, 3, 1, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Goff Big Choppa", "Attach to an army unit.\n"
                                                      "Attached unit gets +2 ATK and gains Armorbane.",
                                   "Wargear. Weapon.", 2, faction, "Common", 1, False,
                                   extra_attack=2, type_of_units_allowed_for_attachment="Army"),
        CardClasses.SupportCard("Ammo Depot", "Action: Exhaust this support to draw 1 card if you have 3 or "
                                              "fewer cards in your hand.", "Location.",
                                1, faction, "Common", False,
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.WarlordCard("Old Zogwort",
                                "Reaction: After this warlord commits to a planet or is declared as an attacker, "
                                "put a Snotlings token into play at this planet.",
                                "Psyker. Oddboy.", faction, 1, 7, 1, 6,
                                "Bloodied.\n"
                                "FORCED REACTION: After the combat phase ends, destroy each "
                                "Snotlings token you control.", 7, 7,
                                ['1x Wyrdboy Stikk', "1x Zogwort's Hovel",
                                 '2x Launch da Snots', "4x Zogwort's Runtherders"]
                                ),
        CardClasses.ArmyCard("Zogwort's Runtherders", "Interrupt: When this unit takes damage, "
                                                      "put a Snotlings token into play at this planet.", "Oddboy.",
                             3, faction, "Signature", 1, 3, 1, False),
        CardClasses.SupportCard("Zogwort's Hovel", "Reaction: After your warlord is declared as a defender, "
                                                   "put a Snotlings token into play at the "
                                                   "same planet as your warlord.", "Location.",
                                2, faction, "Signature", False),
        CardClasses.AttachmentCard("Wyrdboy Stikk", "Attach to an Oddboy unit.\n"
                                                    "Reaction: After a Snotlings token is destroyed, exhaust "
                                                    "this attachment to put a Snotlings token into play at a planet.",
                                   "Wargear. Weapon.", 0, faction, "Signature", 3, False,
                                   required_traits="Oddboy"),
        CardClasses.EventCard("Launch da Snots", "Reaction: After an Orks unit you control is declared as an attacker,"
                                                 " it gets +X ATK for that attack. X is the number of "
                                                 "Snotlings tokens at the same planet as the attacking unit.",
                              "Tactic.", 1, faction, "Signature", 1, False),
        CardClasses.ArmyCard("Snakebite Thug", "FORCED REACTION: After this unit resolves its attack, "
                                               "deal 1 damage to it.", "Warrior. Boyz.",
                             2, faction, "Common", 3, 4, 1, False),
        CardClasses.ArmyCard("Evil Sunz Warbiker", "This unit gets +2 ATK while it is at a planet with a warlord.",
                             "Warrior. Boyz.", 2, faction, "Common", 2, 2, 1, False),
        CardClasses.SupportCard("Mork's Great Heap", "Each non-token Orks unit you control gets +1 HP.",
                                "Upgrade.", 3, faction, "Loyal", True),
        CardClasses.ArmyCard("Big Shoota Battlewagon", "No Wargear Attachments.\n"
                                                       "Interrupt: When this unit is destroyed, put 4"
                                                       " Snotlings tokens into play at this planet.", "Vehicle. Elite.",
                             6, faction, "Common", 4, 4, 1, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Made Ta Fight", "Interrupt: When an army unit you control leaves play from a planet"
                                               " with your warlord, deal damage equal to that army unit's"
                                               " printed ATK value to a target non-warlord unit at the same planet.",
                              "Power.", 2, faction, "Common", 1, False),
        CardClasses.EventCard("Squiggify", "Combat Action: Target a non-Vehicle army unit. "
                                           "Until the end of the phase, set that unit's ATK value to 1,"
                                           " its printed text box is treated as blank (except for Traits),"
                                           " and it gains the Squig trait.", "Power.",
                              3, faction, "Loyal", 2, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Rickety Warbuggy", "No Wargear Attachments.\n"
                                                 "GOES FASTA! - While your opponent has the initiative, this unit "
                                                 "cannot be dealt damage by units while you control an army unit at "
                                                 "this planet not named “Rickety Warbuggy”.",
                             "Vehicle.", 1, faction, "Loyal", 3, 1, 0, False, wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("Lucky Warpaint", "Attach to an Orks unit.\n"
                                                     "Attached unit gains the Blue trait.\n"
                                                     "Attached unit gains Immune to enemy events.", "Upgrade.",
                                   1, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   unit_must_match_faction=True),
        CardClasses.ArmyCard("Front Line 'Ard Boyz", "This unit must be declared as a defender, if able.",
                             "Warrior. Boyz.", 4, faction, "Common", 2, 5, 2, False),
        CardClasses.ArmyCard("Ramshackle Trukk", "No Wargear Attachments.\n"
                                                 "GOES FASTA! - While your opponent has the initiative, "
                                                 "this unit gets +4 HP.", "Vehicle. Elite.",
                             5, faction, "Loyal", 7, 3, 2, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Rok Bombardment", "Combat Action: Target a planet where a battle is taking place. "
                                                 "Until the end of the battle, after each unit at the targeted planet"
                                                 " resolves an attack, deal 1 damage to it. If the targeted planet"
                                                 " is a Material planet (red), this effect only deals damage to enemy"
                                                 " units instead.", "Tactic.", 2, faction, "Orks", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.WarlordCard("Gorzod", "You may include common Vehicle units from both the Astra Militarum and "
                                          "Space Marines factions, but cannot include other "
                                          "cards from a non-Orks faction.", "Oddboy. Warboss.", faction,
                                2, 7, 2, 5, "Bloodied.", 7, 7,
                                ["4x Gorzod's Wagons", "1x Kustomisation Station",
                                 "2x Hostile Acquisition", "1x The Bloodrunna"]),
        CardClasses.ArmyCard("Gorzod's Wagons", "No Wargear Attachments.\n"
                                                "GOES FASTA! - While your opponent has the initiative, "
                                                "this unit gets +2 ATK.", "Vehicle.",
                             2, faction, "Signature", 1, 3, 1, False),
        CardClasses.SupportCard("Kustomisation Station", "Each Vehicle unit you control loses all faction "
                                                         "affiliations and gains the Orks faction affiliation.\n"
                                                         "Orks Vehicle units you control get +1 ATK and +1 HP.",
                                "Location.", 3, faction, "Signature", False),
        CardClasses.EventCard("Hostile Acquisition", "Reaction: After your warlord damages a Vehicle army unit by "
                                                     "an attack, gain control of that unit.", "Tactic.",
                              1, faction, "Signature", 1, False),
        CardClasses.AttachmentCard("The Bloodrunna", "Attach to your warlord.\n"
                                                     "Attached unit gets +2 HP and gains “Reaction: After a Vehicle "
                                                     "unit is destroyed at this planet, ready this unit. "
                                                     "(Limit once per phase.)”", "Vehicle.",
                                   1, faction, "Signature", 3, True, type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True, extra_health=2),
        CardClasses.ArmyCard("Skrap Nabba", "While this unit is at a Material planet (red), it gains: "
                                            "+2 resources when command struggle won at this planet.", "Oddboy. Ally.",
                             2, faction, "Common", 1, 2, 1, False),
        CardClasses.EventCard("Outflank'em", "Reaction: After your combat turn ends, take a combat turn.", "Tactic.",
                              1, faction, "Common", 1, False),
        CardClasses.SupportCard("Smasha Gun Battery", "Deploy Action: Exhaust this support to have each player deal an "
                                                      "amount of damage equal to the number of cards in his hand"
                                                      " among units he controls.", "Weapon. Artillery.", 3, faction,
                                "Common", False, action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.ArmyCard("Salvaged Battlewagon", "No Wargear Attachments.\n"
                                                     "Reaction: After this unit destroys an enemy unit by an attack, "
                                                     "put an Orks unit with printed cost 3 or lower into play from "
                                                     "your hand at an adjacent planet.", "Vehicle. Elite.",
                             7, faction, "Common", 5, 6, 2, False, wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("Huge Chain-Choppa", "Attach to a non-warlord unit.\n"
                                                        "Attached unit gets +4 ATK.\n"
                                                        "Attached unit cannot ready between combat rounds "
                                                        "during the combat phase.", "Wargear. Weapon.",
                                   1, faction, "Common", 1, False, extra_attack=4,
                                   type_of_units_allowed_for_attachment="Army/Synapse/Token"),
        CardClasses.ArmyCard("Corpulent Ork", "While a battle is being resolved at a planet where you are the "
                                              "only player to control a unit named “Corpulent Ork”, your"
                                              " opponent is considered to have the initiative for the "
                                              "purposes of card abilities. (Initiative for determining "
                                              "combat turn order does not change.)", "Warrior.",
                             3, faction, "Common", 1, 5, 2, False),
        CardClasses.SupportCard("Painboy Tent", "Each damaged Orks army unit you control gains 1 command icon.",
                                "Location.", 2, faction, "Loyal", True),
        CardClasses.ArmyCard("Blitza-Bommer", "No Wargear Attachments.\n"
                                              "While this unit is ready it gains Flying.\n"
                                              "Reaction: After this units readies, have your opponent deal 3 "
                                              "indirect damage among units they control at this planet.",
                             "Vehicle. Elite.", 5, faction, "Loyal", 3, 5, 2, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Kommando Sneakaz", "Ambush.\n"
                                                 "Reaction: After you deploy this unit, ready a target Orks unit"
                                                 " you control at this planet and deal it 1 damage.", "Soldier.",
                             3, faction, "Common", 2, 3, 0, False,
                             action_in_hand=True, allowed_phases_in_hand="COMBAT", ambush=True),
        CardClasses.ArmyCard("Gorgul Da Slaya", "Interrupt: When a unit you control at this planet is declared as an "
                                                "attacker, your opponent cannot trigger effects until after "
                                                "that attack resolves.", "Soldier. Nob.",
                             4, faction, "Loyal", 4, 5, 0, True),
        CardClasses.AttachmentCard("Great Iron Gob", "Attach to an Orks army unit you control.\n"
                                                     "Attached unit gains the Nob trait.\n"
                                                     "Each army unit you control at this planet gains a command icon.",
                                   "Wargear.", 2, faction, "Loyal", 2, False, unit_must_match_faction=True,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.ArmyCard("Squiggoth Brute", "Brutal, No Attachments.\n"
                                                "Reaction: After the combat phase begins, each enemy army unit "
                                                "at this planet loses all keywords until the end of the phase.",
                             "Creature. Elite.", 6, faction, "Common", 5, 9, 0, False,
                             no_attachments=True, brutal=True),
        CardClasses.EventCard("Brutal Cunning", "Combat Action: Move up to 2 damage from a target Orks unit you"
                                                " control to a target non-Elite army unit at the same planet",
                              "Tactic.", 2, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Blood Axe Strategist", "Reaction: After an Orks unit you control at this planet resolves "
                                                     "an attack, move it to an adjacent planet or your HQ.", "Soldier.",
                             3, faction, "Common", 2, 4, 2, False),
        CardClasses.SupportCard("'idden Base", "Each card you control in reserve is treated as a 2 ATK, 2 HP Orks"
                                               " army unit during the combat phase.", "Location.",
                                1, faction, "Common", False),
        CardClasses.ArmyCard("Sootblade Assashun", "Deep Strike (2).\n"
                                                   "After you Deep Strike this unit, have your opponent deal 2 "
                                                   "indirect damage among exhausted units he controls at this planet.",
                             "Soldier.", 4, faction, "Common", 3, 3, 1, False, deepstrike=1),
        CardClasses.AttachmentCard("Repulsor Minefield", "Deep Strike (1).\n"
                                                         "Attach to a planet.\n"
                                                         "FORCED REACTION: After an enemy army unit is declared as "
                                                         "an attacker at this planet, deal it 1 damage.", "Upgrade.",
                                   2, faction, "Common", 1, False, deepstrike=1, planet_attachment=True),
        CardClasses.ArmyCard("Follower of Gork", "Each Elite unit you control at this planet gains, "
                                                 "“Interrupt: When this unit is assigned damage, "
                                                 "reduce that damage by 2.”", "Warrior.",
                             2, faction, "Common", 1, 3, 1, False),
        CardClasses.SupportCard("Fungal Turf", "HEADQUARTERS ACTION: Sacrifice this support to put X Snotling tokens "
                                               "into play divided among any number of planets. "
                                               "X is the highest printed cost among units you control.", "Location.",
                                2, faction, "Loyal", False, action_in_play=True, allowed_phases_in_play="HEADQUARTERS")
    ]
    return orks_card_array
