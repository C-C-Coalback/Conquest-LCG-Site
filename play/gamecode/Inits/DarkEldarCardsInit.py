from .. import CardClasses


def dark_eldar_cards_init():
    faction = "Dark Eldar"
    dark_eldar_cards_array = [
        CardClasses.WarlordCard("Packmaster Kith", "Reaction: After this warlord commits "
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
                                allowed_phases_in_play="ALL")
    ]
    return dark_eldar_cards_array
