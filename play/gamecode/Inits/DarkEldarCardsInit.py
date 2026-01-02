from .. import CardClasses


def dark_eldar_cards_init():
    faction = "Dark Eldar"
    dark_eldar_cards_array = [
        CardClasses.WarlordCard("Packmaster Kith", "Reaction: After this warlord commits "
                                                   "to a planet, put a Khymera token into "
                                                   "play at this planet.",
                                "Warrior. Succubus. Wych.", faction, 2, 6, 1, 5,
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
                             2, faction, "Common", 2, 2, 1, False, flying=True),
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
                                allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Solarite Avetys", "Flying.\n"
                                                "Reaction: After this unit takes damage by an attack "
                                                "from a non-flying unit, deal 2 damage to the attacker.", "Warrior.",
                             4, faction, "Loyal", 2, 4, 1, True, flying=True),
        CardClasses.EventCard("Dark Possession", "Action: As your next Action this phase, you may play an event card "
                                                 "in your opponent's discard pile as if it were in your hand. "
                                                 "(You pay its costs, choose its targets, "
                                                 "and follow all restrictions.)", "Tactic. Torture.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Treacherous Lhamaean", "While you control a non-Dark Eldar"
                                                     " warlord, this unit gains Armorbane.\n"
                                                     "Forced Interrupt: When this unit is destroyed, "
                                                     "sacrifice another army unit at this planet.", "Warrior.",
                             2, faction, "Common", 4, 1, 0, False),
        CardClasses.ArmyCard("Uber Grotesque", "No Wargear Attachments.\n"
                                               "Reaction: After you play a Torture event "
                                               "card, this unit gets +3 ATK until the end of the phase. "
                                               "(Limit once per phase.)", "Creature. Abomination. Elite.",
                             5, faction, "Common", 3, 5, 1, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Visions of Agony", "Action: Look at your opponent's hand. Then, choose and "
                                                  "discard 1 card from that hand.", "Tactic. Torture.",
                              3, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.SupportCard("Archon's Palace", "Interrupt: When your opponent wins a command struggle, exhaust "
                                                   "this support to cancel either the card bonus or the "
                                                   "resource bonus of that planet this phase.", "Location.",
                                2, faction, "Loyal", True),
        CardClasses.ArmyCard("Klaivex Warleader", "Ambush.\n"
                                                  "Reaction: After you deploy this unit during the combat phase, "
                                                  "destroy a target damaged army unit at this planet.", "Warrior.",
                             4, faction, "Loyal", 3, 3, 2, False, ambush=True,
                             allowed_phases_in_hand="COMBAT", action_in_hand=True),
        CardClasses.AttachmentCard("Bladed Lotus Rifle", "Attach to an army unit.\n"
                                                         "Attached unit gets +1 ATK.\n"
                                                         "If attached unit is a Kabalite, it gains Ranged.",
                                   "Wargear. Weapon.", 1, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", extra_attack=1),
        CardClasses.EventCard("Soul Seizure", "Action: Put a target army unit with printed cost X or lower from "
                                              "your opponent's discard pile into play under your control"
                                              " at a planet. X is the number of Torture cards in your discard pile.",
                              "Tactic. Torture.", 5, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Sslyth Mercenary", "Action: Pay 2 to take control of this unit if it is at a planet. "
                                                 "Any player may use this ability.", "Warrior.",
                             1, faction, "Common", 2, 2, 2, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Despise", "Combat Action: Each player must sacrifice an Ally "
                                         "unit he controls, if able.", "Tactic.",
                              0, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Bloodied Reavers", "No Wargear AttachmentsThis unit gets +2 ATK while it is"
                                                 " at a planet with a warlord.", "Vehicle.",
                             2, faction, "Common", 2, 2, 1, False, wargear_attachments_permitted=False),
        CardClasses.SupportCard("Crucible of Malediction", "Reaction: After you play a Torture event card, "
                                                           "exhaust this support to look at the top 3 cards of a deck. "
                                                           "Discard 1 of those cards, and place the remaining cards on"
                                                           " top of that deck in any order.", "Upgrade.",
                                1, faction, "Common", False),
        CardClasses.EventCard("Searing Brand", "Combat Action: Deal 3 unpreventable damage to a target non-warlord "
                                               "unit at a planet with your warlord. Your opponent may choose "
                                               "and discard 2 cards from his hand to cancel this effect.",
                              "Tactic. Torture.", 3, faction, "Loyal", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Kabalite Halfborn", "Interrupt: When this unit leaves play, draw 1 card.",
                             "Warrior. Kabalite.", 1, faction, "Common", 1, 1, 0, False),
        CardClasses.EventCard("Slake the Thirst", "Action: Exhaust your warlord to discard up to 3 cards at random "
                                                  "from a target player's hand. Then, that player draws cards "
                                                  "equal to the number of cards discarded.", "Tactic. Maneuver.",
                              0, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Shadow Field", "Attach to a Dark Eldar army unit.\n"
                                                   "Attached unit cannot be dealt damage by an army unit "
                                                   "with printed cost 2 or lower.", "Wargear.",
                                   2, faction, "Loyal", 2, False, unit_must_match_faction=True,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.WarlordCard("Urien Rakarth", "The cost for you to play each Torture event is reduced by 1.\n"
                                                 "The cost for you to play each non-Torture event is increased by 1.",
                                "Scholar. Haemonculus.", faction, 2, 6, 1, 6,
                                "Bloodied.", 8, 7,
                                ["4x Rakarth's Experimentations", "1x Ichor Gauntlet",
                                 "2x Twisted Wracks", "1x Urien's Oubliette"]),
        CardClasses.ArmyCard("Twisted Wracks", "Action: Discard a Torture card from your hand to ready this unit.",
                             "Creature. Abomination.", 2, faction, "Signature", 3, 3, 0, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Rakarth's Experimentations", "Action: Name a card type "
                                                            "(unit, support, attachment, event). "
                                                            "Your opponent must either discard 1 card of "
                                                            "that type from his hand or deal 1 damage to his warlord.",
                              "Tactic. Torture.", 1, faction, "Signature", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Ichor Gauntlet", "Attach to your warlord.\n"
                                                     "Reaction: After you play a Torture event card,"
                                                     " exhaust attached warlord to copy its effects. "
                                                     "You may choose new targets.", "Wargear. Weapon.",
                                   2, faction, "Signature", 3, False, type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True),
        CardClasses.SupportCard("Urien's Oubliette", "Your opponent plays with the top card of his deck revealed.\n"
                                                     "Action: Exhaust this support to discard the top "
                                                     "card of each player's deck or have each player draw 1 card.",
                                "Location.", 1, faction, "Signature", True, action_in_play=True,
                                allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Stalking Ur-Ghul", "No Attachments.\n"
                                                 "This unit gets -5 ATK while attacking a warlord "
                                                 "or undamaged army unit.", "Creature.",
                             3, faction, "Common", 5, 3, 0, False, no_attachments=True),
        CardClasses.SupportCard("Holding Cell", "Your opponent cannot deploy copies of the attached card.\n"
                                                "Reaction: After an enemy army unit is destroyed by an attack,"
                                                " if no card is attached to this support, "
                                                "attach that unit to this support.", "Location.",
                                1, faction, "Loyal", False),
        CardClasses.WarlordCard("Archon Salaine Morn", "Reaction: After a Kabalite or Raider unit enters play under "
                                                       "your control at a Material planet (red), "
                                                       "gain 1 resource. (Limit once per phase.)", "Warrior. Archon.",
                                faction, 2, 7, 2, 6, "Bloodied", 7, 7,
                                ["4x Shadowed Thorns Pillagers", "1x The Nexus of Shadows",
                                 "2x Inevitable Betrayal", "1x Last Breath"]),
        CardClasses.ArmyCard("Shadowed Thorns Pillagers", "Ambush.", "Warrior. Raider. Kabalite.",
                             2, faction, "Signature", 2, 2, 1, False, ambush=True,
                             action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.SupportCard("The Nexus of Shadows", "Action: Pay 2 resources to draw 1 card. "
                                                        "(Limit once per phase.)", "Location.",
                                1, faction, "Signature", True, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Inevitable Betrayal", "Action: Choose any number of undamaged enemy army units at a "
                                                     "target planet. Until the end of the phase, treat each of "
                                                     "those units as if its printed text box were blank.", "Tactic.",
                              2, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Last Breath", "Attach to a unique unit.\n"
                                                  "Reaction: After attached unit damages an army unit by attack, "
                                                  "the attacked unit gets -3 ATK until the end of the phase.",
                                   "Relic. Wargear. Weapon.", 1, faction, "Signature", 3, True,
                                   unit_must_be_unique=True),
        CardClasses.ArmyCard("Mandrake Fearmonger", "Reaction: After this unit damages an army unit by an attack, "
                                                    "discard 1 card at random from your opponent's hand.", "Warrior.",
                             3, faction, "Loyal", 1, 3, 1, False),
        CardClasses.AttachmentCard("Shadowed Thorns Bodysuit", "Attach to a Kabalite army unit.\n"
                                                               "Reaction: After attached unit is declared as a"
                                                               " defender, exhaust this attachment to cancel the"
                                                               " remainder of the attack.", "Wargear. Armor.",
                                   0, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", required_traits="Kabalite"),
        CardClasses.ArmyCard("Dying Sun Marauder", "Reaction: After you gain 1 or more resources, ready this unit.",
                             "Warrior. Raider. Kabalite.", 2, faction, "Loyal", 2, 3, 0, False),
        CardClasses.ArmyCard("Kabalite Harriers", "Reaction: After a Kabalite unit enters play at this planet,"
                                                  " deal 1 damage to a target undamaged unit at this planet.",
                             "Warrior. Kabalite.", 2, faction, "Common", 1, 2, 1, False),
        CardClasses.EventCard("Gut and Pillage", "Reaction: After you win a battle at a Material planet (red), "
                                                 "gain 3 resources. (Max 1 per round.)", "Tactic.",
                              0, faction, "Common", 1, False),
        CardClasses.ArmyCard("Shadowed Thorns Venom", "No Wargear Attachments.\n"
                                                      "Reaction: After you deploy this unit, you may move each "
                                                      "Kabalite army unit you control to a Material planet (red)."
                                                      " (Each unit can move to a different planet).",
                             "Vehicle. Raider. Elite.", 5, faction, "Common", 4, 4, 2, False,
                             wargear_attachments_permitted=False),
        CardClasses.EventCard("Rapid Assault", "Combat Action: Target a planet. Put a Kabalite unit with a printed"
                                               " cost 3 or lower into play from your hand exhausted at the "
                                               "targeted planet. Then, if the targeted planet is a Material planet"
                                               " (red), ready up to 2 Kabalite units at that planet.", "Tactic.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Flayed Skull Slaver", "While this unit is at a Material planet (red), it gains: "
                                                    "+2 resources when command struggle won at this planet.",
                             "Warrior. Kabalite. Ally.", 3, faction, "Common", 2, 3, 1, False),
        CardClasses.SupportCard("Raiding Portal", "Reaction: After you win a command struggle, exhaust this "
                                                  "support to move a target Kabalite army unit you control at"
                                                  " that planet to a Material planet (red). That unit gains 1"
                                                  " command icon until the end of the phase.", "Upgrade.",
                                1, faction, "Common", False),
        CardClasses.AttachmentCard("Hallucinogen Grenade", "Attach to a Kabalite army unit you control.\n"
                                                           "Combat Action: Sacrifice this attachment to exhaust a"
                                                           " target enemy non-Elite army unit at this planet. Then, "
                                                           "deal damage to that unit equal to its printed ATK value.",
                                   "Wargear.", 2, faction, "Loyal", 2, False, must_be_own_unit=True,
                                   required_traits="Kabalite", type_of_units_allowed_for_attachment="Army",
                                   action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Supplicant of Pain", "Each Elite army unit you control at this planet gains Armorbane"
                                                   " while attacking a damaged enemy unit.", "Creature. Abomination.",
                             2, faction, "Common", 1, 3, 1, False),
        CardClasses.SupportCard("Hunting Grounds", "Action: Exhaust this support and sacrifice a Khymera token to "
                                                   "ready a Creature army unit you control.", "Location.",
                                1, faction, "Common", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Mandrake Cutthroat", "Deep Strike (1).\n"
                                                   "Reaction: After you Deep Strike this unit, destroy a "
                                                   "target Ally unit at this planet.", "Warrior.",
                             3, faction, "Common", 2, 2, 1, False, deepstrike=1),
        CardClasses.EventCard("A Thousand Cuts", "Combat Action: Deal 1 damage to a target non-Elite army unit. "
                                                 "Then, shuffle this card back into your deck.", "Tactic. Torture.",
                              1, faction, "Loyal", 2, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.ArmyCard("Corrupted Clawed Fiend", "No Attachments.\n"
                                                       "Reaction: After a unit with printed cost 2 or lower "
                                                       "deals damage to this unit by an attack, rout that unit.",
                             "Creature. Elite.", 7, faction, "Common", 6, 7, 3, False, no_attachments=True),
        CardClasses.AttachmentCard("Electrocorrosive Whip", "Attach to an army unit you control.\n"
                                                            "Each non-Elite army unit dealt damage by attached "
                                                            "unit's attack cannot ready this phase.",
                                   "Wargear. Weapon.", 1, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.ArmyCard("Masked Hunter", "Reaction: After you declare this unit as an attacker, "
                                              "move a Khymera token from an adjacent planet to this planet.",
                             "Warrior. Beastmaster.", 3, faction, "Common", 2, 3, 1, False),
        CardClasses.EventCard("Run Down", "Deep Strike (0).\n"
                                          "Reaction: After you Deep Strike this event, target a non-Elite army unit "
                                          "in your opponent's HQ. Move the targeted unit to this planet.", "Tactic.",
                              0, faction, "Common", 1, False, deepstrike=0),
        CardClasses.ArmyCard("Kabalite Blackguard", "Reaction: After you win a battle at this planet, "
                                                    "take up to 2 resources from your opponent.", "Warrior. Kabalite.",
                             2, faction, "Loyal", 2, 3, 0, False),
        CardClasses.SupportCard("Abomination Workshop", "HEADQUARTERS ACTION: Sacrifice this support to have each "
                                                        "player discard cards from his hand until he has cards "
                                                        "equal to or less than the highest printed cost among "
                                                        "units he controls.", "Location.", 2, faction, "Common",
                                False, action_in_play=True, allowed_phases_in_play="HEADQUARTERS"),
        CardClasses.ArmyCard("Beastmaster Harvester", "Deep Strike (4).\n"
                                                      "Reaction: After you Deep Strike this unit, put 2 Khymera "
                                                      "tokens into play at this planet.",
                             "Warrior. Beastmaster. Elite.", 5, faction, "Common", 2, 5, 2, False, deepstrike=4),
        CardClasses.ArmyCard("Hydrae Stalker", "Reaction: After you deploy this unit, deal 2 damage to a target unit "
                                               "with printed cost 2 or lower.", "Warrior. Wych. Raider.",
                             3, faction, "Common", 2, 3, 0, False),
        CardClasses.AttachmentCard("The Shadow Suit", "Deep Strike (0).\n"
                                                      "Attach to an army unit.\n"
                                                      "Attached unit gets +2 ATK and +1 HP.\n"
                                                      "Interrupt: When attached unit leaves play, put this card in "
                                                      "reserve at a planet. Your opponent may exhaust a unit at that"
                                                      " planet to cancel this effect.", "Wargear. Weapon.",
                                   2, faction, "Loyal", 2, True, deepstrike=0, extra_health=1, extra_attack=2,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Raiding Kabal", "This unit gets Sweep (1) while it is not at the first planet.\n"
                                              "Reaction: After you win a battle at this planet, put a Khymera "
                                              "token into play at this planet.", "Kabalite.",
                             2, faction, "Loyal", 1, 2, 1, False),
        CardClasses.EventCard("Supply Line Incursion", "Action: Exhaust target support. Then, if that support is a"
                                                       " Limited card, draw one card and gain 1 resource.", "Tactic.",
                              1, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Kabal of the Ebon Law", "This unit gets +1 ATK while it is not at the first planet.\n"
                                                      "Forced Reaction: After a battle starts at this planet, each "
                                                      "player controlling a unit with 2 ATK or more, draws a card.",
                             "Kabalite.", 2, faction, "Loyal", 2, 2, 1, False),
        CardClasses.ArmyCard("Connoisseur of Terror", "Deep Strike (2).\n"
                                                      "Reaction: After this unit is turned face-up, draw 2 cards.",
                             "Scholar. Haemonculus.", 2, faction, "Loyal", 2, 2, 1, False, deepstrike=2),
        CardClasses.SupportCard("Willing Submission", "Forced Reaction: After the deploy phase begins, draw 1 card. "
                                                      "Then your opponent may choose 2 units he controls"
                                                      " (or his warlord if he controls no other unit) to draw 1 card."
                                                      " You may deal 1 damage to one of the chosen units.", "Torture.",
                                1, faction, "Loyal", False),
        CardClasses.WarlordCard("Yvraine", "You cannot include Chaos Elite units in your deck.\n"
                                           "Reaction: After this unit commits to a planet, a non-Elite army unit "
                                           "you control at an adjacent planet is considered to be a warlord while "
                                           "checking for a battle at that planet this round.", "Herald of Ynnead.",
                                faction, 2, 7, 2, 5, "Bloodied.", 7, 7,
                                ["1x Attuned Gyrinx", "1x Host of the Emissary",
                                 "2x Triumvirate of Ynnead", "4x Yvraine's Entourage"]),
        CardClasses.AttachmentCard("Attuned Gyrinx", "Attach to your warlord.\n"
                                                     "Attached unit gets +1 HP.\n"
                                                     "Combat Action: Exhaust this attachment to give an army unit you "
                                                     "control at each adjacent planet +1 ATK and +1 HP until "
                                                     "the end of the phase.", "Familiar.",
                                   1, faction, "Signature", 3, False, type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True, extra_health=1,
                                   action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Host of the Emissary", "Reaction: After your opponent wins a battle, exhaust this "
                                                        "support to have your opponent sacrifice an army unit at "
                                                        "that planet, if able.", "Warhost.",
                                3, faction, "Signature", False),
        CardClasses.EventCard("Triumvirate of Ynnead", "The effects of this event cannot be cancelled.\n"
                                                       "Deploy Action: Deploy 2 non-Elite units with a different name"
                                                       " from your discard pile at 2 different planets. "
                                                       "Reduce their cost by 1.", "Prophecy.",
                              0, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.ArmyCard("Yvraine's Entourage", "Reaction: After a battle begins at this planet, switch the "
                                                    "printed ATK values of two army units at this planet until"
                                                    " the end of a combat round.", "Warrior.",
                             2, faction, "Signature", 2, 2, 1, False),
        CardClasses.AttachmentCard("Torturer's Masks", "Ambush.\n"
                                                       "Attach to an army unit. Attached unit gets +1 ATK and +1 HP.\n"
                                                       "Reaction: After you use a shield card, if you have no cards "
                                                       "in hand, exhaust this attachment to draw a card.", "Wargear.",
                                   1, faction, "Loyal", 2, False, ambush=True, extra_attack=1, extra_health=1,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Dark Lance Raider", "No Wargear Attachments. Flying.\n"
                                                  "Reaction: After this unit is declared as an attacker, choose either "
                                                  "to deal 1 damage to up to 2 different enemy units at this planet or "
                                                  "3 damage to an enemy unit at this planet.",
                             "Vehicle. Raider. Kabalite.", 3, faction, "Common", 0, 2, 1, False,
                             flying=True, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Arrogant Haemonculus", "Increase the cost of each other Haemonculus unit deployed at "
                                                     "this planet by 1.\n"
                                                     "Forced Reaction: After you play a Torture card, deal 1 damage"
                                                     " to a target non-warlord unit at this planet.",
                             "Scholar. Haemonculus.", 1, faction, "Loyal", 1, 1, 1, False),
        CardClasses.ArmyCard("Mindless Pain Addict", "Cannot retreat or be Routed.\n"
                                                     "Reaction: After an army unit you control at this planet is"
                                                     " destroyed, take control of this unit. "
                                                     "Any player may use this ability.", "Creature. Abomination.",
                             2, faction, "Common", 4, 4, 0, False),
        CardClasses.ArmyCard("Pain Crafter", "Reaction: After you play a Dark Eldar event card, exhaust this unit to "
                                             "attach that event card to a Dark Eldar unit as a Wargear attachment"
                                             " with the text "
                                             "\"Attach to an army unit. Attached unit gets +1 ATK and +1 HP.\". "
                                             "(Limit once per phase.)", "Scholar. Haemonculus.",
                             2, faction, "Loyal", 1, 2, 1, False),
        CardClasses.EventCard("Catatonic Pain", "Reaction: After an enemy army unit enters play at a planet, "
                                                "move that unit to an adjacent planet of your choice.", "Torture.",
                              3, faction, "Common", 1, False),
        CardClasses.WarlordCard("Liatha", "Cards in your hand may be used as shield cards with 2 shield icons. "
                                          "When you use a card this way, remove it from the game face-down. "
                                          "As an interrupt your opponent may have you turn the card face-up, "
                                          "if it is a card with 2 printed shield icons, deal 1 unpreventable "
                                          "damage to a unit. If not, cancel that card's shielding effect."
                                          " (Limit three times per phase.)", "Assassin. Wych.", faction,
                                2, 7, 2, 5, "Bloodied.", 7, 7,
                                ["1x Cloak of Shade", "1x Reveal The Blade",
                                 "2x Shadow Hunt", "4x Liatha's Retinue"]),
        CardClasses.AttachmentCard("Cloak of Shade", "Attach to your warlord.\n"
                                                     "Each unit at this planet loses Armorbane.\n"
                                                     "Forced Interrupt: When you use a card as a shield card, "
                                                     "exhaust this attachment to have it gain 1 shield icon.",
                                   "Wargear.", 1, faction, "Signature", 3, False, must_be_own_unit=True,
                                   type_of_units_allowed_for_attachment="Warlord"),
        CardClasses.ArmyCard("Liatha's Retinue", "Reaction: After this unit is turned face-up, put it into play "
                                                 "exhausted at a planet where no battle is taking place.",
                             "Assassin. Warrior. Creature.", 3, faction, "Signature", 3, 2, 1, False),
        CardClasses.SupportCard("Reveal The Blade", "As an additional cost to target this support,"
                                                    " discard two cards at random from your hand.\n"
                                                    "Combat Action: Exhaust this support and turn face-up a face-down"
                                                    " card with no printed shield you removed from the game to "
                                                    "give an army unit +2 ATK for its next attack this phase.",
                                "Skill.", 1, faction, "Signature", False,
                                action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.EventCard("Shadow Hunt", "Reaction: After your opponent passes during the deploy phase, "
                                             "put a face-down, non-Elite Dark Eldar unit you removed from "
                                             "the game into play face-up at a target planet.", "Tactic.",
                              1, faction, "Signature", 1, False),
        CardClasses.ArmyCard("Distorted Talos", "Lumbering.\n"
                                                "Interrupt: When you use a shield card on this unit, remove all "
                                                "damage from it. (Limit once per phase.)",
                             "Abomination. Creature. Elite.", 3, faction, "Loyal", 5, 4, 1, False, lumbering=True),
        CardClasses.SupportCard("Prophets of Flesh", "Interrupt: When you deploy an Abomination or Scholar unit, "
                                                     "exhaust this support to reduce its cost by 1.",
                                "Pledge.", 1, faction, "Loyal", False),
        CardClasses.SupportCard("The Broken Sigil", "Target a non-first planet and choose a secret number"
                                                    " while deploying this card.\n"
                                                    "Forced Interrupt: When that planet is captured, reveal the secret"
                                                    " number, if it is odd the capturing player must sacrifice a unit,"
                                                    " otherwise they may draw 3 cards.",
                                "Pledge.", 1, faction, "Loyal", False),
        CardClasses.SupportCard("The Flayed Mask", "Secretly choose a non-first planet when you deploy this support.\n"
                                                   "Interrupt: When your opponent captures the chosen planet, reveal "
                                                   "your choice to have them choose either to: deal 5 indirect damage "
                                                   "among units they control, sacrifice a unit or forgo the capture.",
                                "Pledge.", 1, faction, "Loyal", False)
    ]
    return dark_eldar_cards_array
