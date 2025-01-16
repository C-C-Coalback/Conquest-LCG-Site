import CardClasses


def orks_cards_init():
    orks_card_array = [CardClasses.WarlordCard("Nazdreg",
                                               "Each other unit you control at this planet gains Brutal. ",
                                               "Warrior. Warboss.", "Orks", 2, 7, 2, 5, "Bloodied.", 7, 7,
                                               "Nazdreg"),
                       CardClasses.ArmyCard("Nazdreg's Flash Gitz",
                                            "Combat Action: Deal this unit 1 damage to ready it. "
                                            "(Limit once per phase.)",
                                            "Nob. Warrior.", 3, "Orks", "Signature", 2, 4, 1, False,
                                            "Nazdreg's_Flash_Gitz",
                                            action_in_play=True, allowed_phases_in_play="Combat"),
                       CardClasses.SupportCard("Kraktoof Hall",
                                               "Combat Action: Exhaust this support to move 1 damage from a "
                                               "target unit you control to another target unit "
                                               "at the same planet.", "Location.", 2, "Orks", "Signature",
                                               False, "Kraktoof_Hall", action_in_play=True,
                                               allowed_phases_in_play="Combat"),
                       CardClasses.EventCard("Bigga is Betta", "Interrupt: When you deploy an Orks unit, "
                                                               "reduce its cost by 2. "
                                                               "Deal 1 damage to that unit after it enters play.",
                                             "Tactic.",
                                             0, "Orks", "Signature", 1, False,
                                             "Bigga_is_Betta", [True, 2, True]),
                       CardClasses.AttachmentCard("Cybork Body", "Attach to an army unit.\nDouble attached unit's HP.",
                                                  "Wargear. Bionics.", 1, "Orks", "Signature", 3, False,
                                                  "Cybork_Body"),
                       CardClasses.ArmyCard("Sniveling Grot", "", "Runt. Ally.", 0, "Orks", "Common", 1, 1, 0, False,
                                            "Sniveling_Grot"),
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
                                            "Rugged_Killa_Kans", brutal=True),
                       CardClasses.ArmyCard("Enraged Ork", "Brutal.", "Warrior. Boyz.", 2, "Orks", "Loyal", 0, 5, 1,
                                            False, "Enraged_Ork", brutal=True),
                       CardClasses.ArmyCard("Crushface", "Interrupt: When you deploy another Orks unit at this planet, "
                                                         "reduce its cost by 1.", "Warrior. Nob.", 3, "Orks", "Loyal",
                                            2, 3, 2, True, "Crushface", applies_discounts=[True, 1, True]),
                       CardClasses.ArmyCard("Bad Dok", "This unit gains 3 command icons while it is damaged.",
                                            "Oddboy. Nob.", 2,
                                            "Orks", "Common", 1, 4, 1, False, "Bad_Dok"),
                       CardClasses.ArmyCard("Rokkit Boy", "Each enemy unit at this planet loses the Flying keyword.",
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
                                             "Battle_Cry", action_in_hand=True, allowed_phases_in_hand="Combat"),
                       CardClasses.EventCard("Snotling Attack", "Deploy Action: Put 4 Snotlings tokens "
                                                                "into play divided among any number of planets.",
                                             "Tactic.",
                                             2, "Orks", "Common", 1, False,
                                             "Snotling_Attack", action_in_hand=True, allowed_phases_in_hand="Deploy"),
                       CardClasses.EventCard("Squig Bombin'", "Action: Destroy a target support card.", "Tactic.",
                                             2, "Orks", "Common", 1, False, "Squig_Bombin'", action_in_hand=True,
                                             allowed_phases_in_hand="All"),
                       CardClasses.AttachmentCard("Rokkit Launcha",
                                                  "Attach to an army unit.Attached unit gains Ranged.",
                                                  "Wargear. Weapon.", 1, "Orks", "Common", 1, False,
                                                  "Rokkit_Launcha"),
                       CardClasses.SupportCard("Ork Kannon", "Combat Action: Exhaust this support to target a planet. "
                                                             "Each player deals 1 indirect damage "
                                                             "among the units he controls at "
                                                             "that planet.", "Artillery. Weapon.", 1, "Orks", "Common",
                                               False, "Ork_Kannon"),
                       CardClasses.SupportCard("Bigtoof Banna", "Limited.\nInterrupt: When you deploy an Orks unit, "
                                                                "exhaust this support to reduce that unit's cost by 1.",
                                               "Upgrade.", 1, "Orks", "Common", True,
                                               "Bigtoof_Banna", applies_discounts=[True, 1, True]),
                       CardClasses.SupportCard("Tellyporta Pad",
                                               "Combat Action: Exhaust this support to move an Orks unit "
                                               "you control to the first planet.",
                                               "Location.", 2, "Orks", "Common", False,
                                               "Tellyporta_Pad")]
    return orks_card_array
