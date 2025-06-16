from .. import CardClasses


def necrons_cards_init():
    faction = "Necrons"
    necrons_card_array = [
        CardClasses.WarlordCard("Nahumekh", "Reaction: After the combat phase begins, a target army unit at this "
                                            "planet gets -X HP until the end of the phase. X is the number "
                                            "of non-Necrons factions among units you control.", "Warrior. Sautekh.",
                                faction, 2, 6, 1, 6, "Bloodied.", 7, 7,
                                ["4x Destroyer Cultist", "1x Obedience", "2x Hate", "1x The Staff of Command"]),
        CardClasses.ArmyCard("Destroyer Cultist", "This unit gets +1 ATK for each non-Necrons faction"
                                                  " among units you control.", "Warrior. Sautekh.",
                             3, faction, "Signature", 1, 4, 1, False),
        CardClasses.SupportCard("Obedience", "Reaction: After a phase begins, exhaust this support to move a "
                                             "non-Necrons unit you control to a target planet.", "Upgrade.",
                                2, faction, "Signature", False),
        CardClasses.EventCard("Hate", "Deploy Action: Destroy a target army unit with a faction symbol that "
                                      "matches your enslaved faction. X is that unit's printed cost.", "Tactic.",
                              0, faction, "Signature", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("The Staff of Command", "Attach to your warlord.\n"
                                                           "Action: Exhaust this attachment to set your enslavement "
                                                           "dial to another faction.", "Wargear. Weapon.",
                                   0, faction, "Loyal", 3, True, type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.WarlordCard("Anrakyr the Traveller", "Deploy Action: Deploy the topmost unit card in a target "
                                                         "discard pile. (Limit once per phase.)", "Soldier.",
                                faction, 2, 7, 1, 6, "Bloodied.", 7, 7,
                                ["5x Pyrrhian Eternals", "1x Slumbering Tomb", "1x Awake the Sleepers",
                                 "1x Pyrrhian Warscythe"], action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.ArmyCard("Pyrrhian Eternals", "For each card named Pyrrhian Eternals in your discard pile, "
                                                  "this unit gets +1 ATK and +1 HP.", "Soldier.",
                             2, faction, "Signature", 1, 1, 1, False),
        CardClasses.SupportCard("Slumbering Tomb", "Action: Exhaust this support to draw 2 cards. Then"
                                                   ", discard 2 cards from your hand.", "Location.",
                                1, faction, "Signature", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Awake the Sleepers", "Action: Shuffle any number of Necrons cards from your"
                                                    " discard pile into your deck.", "Tactic.",
                              1, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Pyrrhian Warscythe", "Attach to your warlord.\n"
                                                         "Attached unit gets +1 ATK.\n"
                                                         "Reaction: After attached unit is declared as an attacker, "
                                                         "discard the top 2 cards of your deck.", "Wargear. Weapon.",
                                   1, faction, "Signature", 3, False, extra_attack=1,
                                   type_of_units_allowed_for_attachment="Warlord", must_be_own_unit=True),
        CardClasses.ArmyCard("Canoptek Scarab Swarm", "Interrupt: When this unit is destroyed, return a target Necrons "
                                                      "unit from your discard pile to your hand.", "Drone.",
                             1, faction, "Common", 2, 2, 0, False),
        CardClasses.ArmyCard("Warriors of Gidrim", "This unit gains 1 command icon while you have 2 or more non-Necrons"
                                                   " factions among units you control.", "Warrior. Sautekh.",
                             1, faction, "Common", 1, 1, 1, False),
        CardClasses.ArmyCard("Flayed Ones Pack", "FORCED REACTION: After this unit is declared as an attacker, "
                                                 "discard the top 3 cards of your deck.", "Warrior.",
                             2, faction, "Common", 3, 2, 1, False),
        CardClasses.ArmyCard("Immortal Vanguard", "Each non-Necrons Warrior unit you control"
                                                  " at this planet gets +1 ATK and +1 HP.", "Soldier. Novokh.",
                             2, faction, "Common", 1, 3, 1, False),
        CardClasses.ArmyCard("Patrolling Wraith", "Reaction: After this unit destroys an enemy unit by an attack, "
                                                  "your opponent must reveal his hand and discard "
                                                  "each revealed card with the same name as the destroyed unit.",
                             "Drone.", 2, faction, "Common", 2, 3, 0, False),
        CardClasses.ArmyCard("Decaying Warrior Squad", "Combat Action: Deploy this card from your "
                                                       "discard pile at a planet.", "Warrior.",
                             2, faction, "Common", 2, 2, 0, False),
        CardClasses.ArmyCard("Deathmark Assassins", "Reaction: After the combat phase begins, discard the top card of"
                                                    " your deck. This unit gets +X ATK until the end of the phase. "
                                                    "X is the printed cost of the discarded card.", "Scout.",
                             3, faction, "Common", 2, 3, 0, False),
        CardClasses.ArmyCard("Mandragoran Immortals", "Ranged.\n"
                                                      "Action: Sacrifice a non-Necrons Soldier unit at this planet to "
                                                      "ready this unit. (Limit once per phase.)", "Soldier. Sautekh.",
                             3, faction, "Common", 2, 3, 1, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Tomb Blade Squadron", "No Wargear Attachments.\n"
                                                    "Reaction: After you deploy a non-Necrons"
                                                    " Scout unit, move this unit to a planet. Then, a target "
                                                    "non-warlord unit at this planet gets -1 HP until the end "
                                                    "of the phase.", "Vehicle. Sautekh.",
                             3, faction, "Common", 0, 3, 2, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Reanimating Warriors", "Interrupt: When this unit would be destroyed by taking damage, "
                                                     "remove all damage from it and move this unit to an"
                                                     " adjacent planet instead. (Limit once per phase.)", "Warrior.",
                             3, faction, "Common", 2, 2, 1, False),
        CardClasses.ArmyCard("Canoptek Spyder", "Combat Action: During a battle at this planet, discard a unit card "
                                                "from your hand to remove 2 damage from a Necrons army unit you "
                                                "control at this planet. (Limit once per combat round.)", "Drone.",
                             4, faction, "Common", 4, 3, 1, False, action_in_play=True,
                             allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Immortal Legion", "Combat Action: Exhaust this unit to move it to a planet with an "
                                                "enemy warlord with a faction symbol that matches"
                                                " your enslaved faction.", "Soldier. Sautekh.",
                             4, faction, "Common", 4, 4, 1, False, action_in_play=True,
                             allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Praetorian Ancient", "While you have 6 or more units in your discard pile, "
                                                   "this unit gets +2 ATK and gains Armorbane.", "Soldier.",
                             4, faction, "Common", 3, 4, 1, False),
        CardClasses.ArmyCard("Harbinger of Eternity", "You may play each event card from your discard pile "
                                                      "as if it were in your hand.\n"
                                                      "FORCED REACTION: After you play a event card from your"
                                                      " discard pile, remove that card from the game.",
                             "Scholar. Elite.", 5, faction, "Common", 3, 5, 3, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Lychguard Sentinel", "While you have 6 or more units in your discard pile, "
                                                   "this unit gets +4 HP.Your opponent must declare a ready unit"
                                                   " named Lychguard Sentinel as defender, if able.",
                             "Soldier. Elite.", 5, faction, "Common", 2, 6, 2, False),
        CardClasses.ArmyCard("Doom Scythe Invader", "No Wargear Attachments.\n"
                                                    "Reaction: After you deploy this unit, put a non-Elite Vehicle"
                                                    " unit into play from your discard pile at this planet.",
                             "Vehicle. Sautekh. Elite.", 6, faction, "Common", 4, 4, 2, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Doomsday Ark", "Area Effect (X).\n"
                                             "No Wargear Attachments.\n"
                                             "X is the number of non- factions among units you control.",
                             "Vehicle. Elite.", 6, faction, "Common", 5, 5, 2, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Dread Monolith", "No Wargear Attachments.\n"
                                               "Combat Action: Discard the top 3 cards of your deck. "
                                               "Then, put a Necrons non-Vehicle unit discarded by this effect into "
                                               "play at this planet. (Limit once per round.)", "Vehicle. Elite.",
                             8, faction, "Common", 5, 7, 5, False, action_in_play=True,
                             allowed_phases_in_play="COMBAT", wargear_attachments_permitted=False),
        CardClasses.EventCard("Reanimation Protocol", "Action: Remove up to 2 damage from a Necrons unit you control."
                                                      " Max 1 per round.", "Tactic.", 0, faction, "Common",
                              1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Recycle", "Action: Discard 2 cards from your hand. Then, draw 3 cards.", "Power.",
                              1, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Mechanical Enhancement", "Combat Action: Each Necrons unit you control at a target"
                                                        " planet gets +2 HP until the end of the phase.", "Tactic.",
                              2, faction, "Common", 2, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.EventCard("Drudgery", "Limited.\n"
                                          "Action: Put a target non-Necrons unit with printed cost 3 or "
                                          "lower into play from your discard pile at a planet.", "Tactic.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL",
                              limited=True),
        CardClasses.EventCard("Extermination", "Deploy Action: Each non-unique non-Necrons unit at a target planet "
                                               "gets -3 HP until the end of the phase. You must pass during "
                                               "your next deployment turn.", "Tactic.",
                              5, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("Gauss Flayer", "Attach to a Necrons army unit.\n"
                                                   "Combat Action: During a battle at this planet, "
                                                   "exhaust attached unit to give a target enemy army unit at this "
                                                   "planet -2 HP until the end of the phase.", "Wargear. Weapon.",
                                   1, faction, "Common", 1, False, action_in_play=True, allowed_phases_in_play="COMBAT",
                                   type_of_units_allowed_for_attachment="Army",
                                   unit_must_match_faction=True),
        CardClasses.AttachmentCard("Royal Phylactery",
                                   "Attach to a Necrons army unit.\n"
                                   "Reaction: After a phase begins or a combat round at this planet begins, "
                                   "remove 1 damage from attached unit.", "Wargear.",
                                   1, faction, "Common", 2, False, type_of_units_allowed_for_attachment="Army",
                                   unit_must_match_faction=True),
        CardClasses.AttachmentCard("Hyperphase Sword", "Attach to a Necrons army unit.\n"
                                                       "Attached unit gets +1 ATK and gains Armorbane.\n"
                                                       "Action: Discard a card from your hand to attach this card to "
                                                       "another eligible unit at this planet.", "Wargear. Weapon.",
                                   2, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   unit_must_match_faction=True, extra_attack=1, action_in_play=True,
                                   allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Resurrection Orb", "Attach to an Elite Necrons unit you control.\n"
                                                       "Reaction: After a combat round at this planet begins, if the "
                                                       "topmost card of your discard pile is a non-Elite unit, put it "
                                                       "into play at this planet.", "Wargear.",
                                   2, faction, "Common", 2, False, required_traits="Elite",
                                   unit_must_match_faction=True),
        CardClasses.AttachmentCard("Mind Shackle Scarab", "Attach to a non-Elite army unit.\n"
                                                          "Action: If attached unit's faction symbol matches your "
                                                          "enslaved faction, exhaust this attachment to gain control "
                                                          "of attached unit until the end of the phase.", "Drone.",
                                   3, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   action_in_play=True, allowed_phases_in_play="ALL", forbidden_traits="Elite"),
        CardClasses.SupportCard("Timeworn Stasis-Crypt", "Limited.\n"
                                                         "Interrupt: When you deploy a Necrons card, exhaust this "
                                                         "support to reduce the card's cost by 1.", "Location.",
                                1, faction, "Common", True, applies_discounts=[True, 1, True],
                                is_faction_limited_unique_discounter=True, limited=True),
        CardClasses.SupportCard("Weight of the Aeons", "Reaction: After a phase begins, exhaust this support to have "
                                                       "each player discard the top 2 cards of his deck.", "Upgrade.",
                                1, faction, "Common", False),
        CardClasses.SupportCard("Eternity Gate", "Action: Exhaust this support to choose a card in a target player's "
                                                 "discard pile and place it on top of that discard pile.", "Upgrade.",
                                1, faction, "Common", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.SupportCard("Sautekh Complex", "Limited.\n"
                                                   "Reaction: After you deploy a unit from a non-Necrons "
                                                   "faction, if you control no other units from that "
                                                   "faction, gain 1 resource or draw 1 card.",
                                "Location.", 1, faction, "Common", False, limited=True),
        CardClasses.SupportCard("Master Program", "Action: Exhaust this support and sacrifice a Drone card to remove "
                                                  "all damage from target army unit you control and ready it.",
                                "Upgrade.", 2, faction, "Common", True,
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.SupportCard("Particle Whip", "Headquarters action: Exhaust this support and shuffle any number "
                                                 "of unit cards from your discard pile into your deck to deal X "
                                                 "damage to a target non-Elite army unit. X is the number of "
                                                 "cards shuffled into your deck.", "Artillery. Upgrade.",
                                3, faction, "Common", False, action_in_play=True,
                                allowed_phases_in_play="HEADQUARTERS"),
        CardClasses.ArmyCard("Immortal Loyalist", "Each Elite unit you control at this planet gains, "
                                                  "“Interrupt: When this unit is targeted by a triggered effect "
                                                  "for the first time this round, cancel that effect.”", "Soldier.",
                             2, faction, "Common", 1, 3, 1, False),
        CardClasses.SupportCard("Shroud Cruiser", "Action: Exhaust this support to move an Elite "
                                                  "unit you control to an adjacent planet.", "Upgrade.",
                                2, faction, "Common", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Hunting Acanthrites", "Each unit with printed cost 2 or lower at this planet gets -1 HP",
                             "Drone.", 3, faction, "Common", 1, 3, 0, False),
        CardClasses.EventCard("Defensive Protocols", "Deep Strike (2).\n"
                                                     "Reaction: After you Deep Strike this event, until the end of "
                                                     "this battle's first combat round, reduce all damage taken "
                                                     "by Necrons units you control to 1.", "Tactic.",
                              0, faction, "Common", 1, False, deepstrike=2),
        CardClasses.ArmyCard("Rumbling Tomb Stalker", "Reaction: After this unit assigns damage by an attack, "
                                                      "remove 1 damage from it.", "Drone. Elite.",
                             5, faction, "Common", 2, 7, 1, False),
        CardClasses.WarlordCard("Illuminor Szeras", "Reaction: After you remove any amount of damage from a"
                                                    " Necrons army unit, gain 1 resource.", "Scholar.",
                                faction, 1, 8, 1, 5, "Bloodied.", 7, 6,
                                ["4x Augmented Warriors", "1x Dissection Chamber",
                                 "2x Vivisection", "1x Eldritch Lance"]),
        CardClasses.ArmyCard("Augmented Warriors", "FORCED REACTION: After this unit enters play, deal "
                                                   "it 2 unpreventable damage.", "Soldier.",
                             2, faction, "Signature", 2, 4, 1, False),
        CardClasses.SupportCard("Dissection Chamber", "FORCED REACTION: After an army unit enters play,"
                                                      " deal it 1 damage.", "Location.",
                                2, faction, "Signature", False),
        CardClasses.EventCard("Vivisection", "Action: Target a planet. Remove 1 damage from each Necrons unit you "
                                             "control at the targeted planet and deal 1 damage to each non-Necrons"
                                             " unit at the targeted planet.", "Tactic.",
                              3, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Eldritch Lance", "Attach to your warlord.\n"
                                                     "Attached unit gets +1 ATK.\n"
                                                     "Combat Action: Exhaust this attachment to remove 1 damage "
                                                     "from a unit at this planet.", "Wargear. Weapon.",
                                   1, faction, "Signature", 3, False, type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True, action_in_play=True, allowed_phases_in_play="COMBAT",
                                   extra_attack=1),
        CardClasses.ArmyCard("Risen Warriors", "Deep Strike (0)", "Soldier.",
                             3, faction, "Common", 2, 2, 0, False, deepstrike=0),
        CardClasses.AttachmentCard("Quantum Shielding", "Attach to a Necrons Vehicle unit you control.\n"
                                                        "Attached unit gets +2 HP.\n"
                                                        "Interrupt: When this card is discarded as a shield card, "
                                                        "attach it to the shielded unit instead of discarding it,"
                                                        " if eligible.", "Hardpoint.",
                                   2, faction, "Common", 1, False, extra_health=2, required_traits="Vehicle",
                                   unit_must_match_faction=True, must_be_own_unit=True),
        CardClasses.ArmyCard("Dread Command Barge", "No Wargear Attachments.\n"
                                                    "COMMAND ACTION: Discard a non-Necrons card from your hand "
                                                    "to move this unit to an adjacent planet.", "Vehicle.",
                             4, faction, "Common", 3, 3, 3, False, wargear_attachments_permitted=False,
                             action_in_play=True, allowed_phases_in_play="COMMAND"),
        CardClasses.ArmyCard("Shard of the Deceiver", "X is equal to the number of cards in your discard pile.\n"
                                                      "FORCED REACTION: After a phase or combat round at this planet "
                                                      "begins, discard a card. If you have no cards in your hand, "
                                                      "discard this unit.", "C'tan. Elite.",
                             7, faction, "Common", 0, 0, 2, False),
        CardClasses.ArmyCard("Triarch Stalkers Procession", "No Wargear Attachments.\n"
                                                            "Forced Reaction: After you deploy this unit, "
                                                            "have your opponent draw 2 cards.", "Vehicle.",
                             3, faction, "Common", 4, 6, 2, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Parasitic Scarabs", "No Wargear attachments.\n"
                                                  "Interrupt: When you deploy a Necrons unit, deal 1 damage to "
                                                  "this unit and the deployed unit to reduce its cost by 1. "
                                                  "Then discard the top card of your deck.", "Drone.",
                             2, faction, "Common", 0, 4, 1, False, applies_discounts=[True, 1, True]),
        CardClasses.ArmyCard("Replicating Scarabs", "Combat Action: Exhaust this unit to remove 1 damage from "
                                                    "a Necrons army unit at this planet.", "Drone.",
                             2, faction, "Common", 1, 3, 0, False,
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.AttachmentCard("Traumatophobia", "Attach to an enemy army unit.\n"
                                                     "Attached unit gains Lumbering.", "Power.",
                                   2, faction, "Common", 2, False, must_be_enemy_unit=True,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.WarlordCard("Trazyn the Infinite", "Interrupt: When your warlord would be defeated, move it to "
                                                       "a target planet to remove all damagge from it instead.",
                                "Substitute.", faction, 2, 2, 2, 7, "Bloodied.", 7, 7,
                                ["4x Acquisition Phalanx", "1x Reign of Solemnace",
                                 "2x Surrogate Host", "1x Third Eye of Trazyn"]),
        CardClasses.ArmyCard("Acquisition Phalanx", "Reaction: After a unit you control moves to this planet, "
                                                    "this unit gets +1 ATK and +1 HP until the end of the phase.",
                             "Soldier.", 2, faction, "Signature", 2, 3, 1, False),
        CardClasses.EventCard("Surrogate Host", "Interrupt: When a unit you control is destroyed, move your warlord "
                                                "to the same planet.", "Tactic.",
                              0, faction, "Signature", 1, False),
        CardClasses.SupportCard("Reign of Solemnace", "Each army unit you control at a planet with your warlord "
                                                      "gets +1HP.", "Tomb World.", 1, faction, "Signature", False),
        CardClasses.AttachmentCard("Third Eye of Trazyn", "Attach to your warlord.\n"
                                                          "Attached unit gets +1 HP.\n"
                                                          "Combat Reaction: After your warlord moves to a planet, "
                                                          "exhaust this attachment to move an army unit you control "
                                                          "at that planet to an adjacent planet.", "Wargear.",
                                   1, faction, "Signature", 3, False, extra_health=1,
                                   must_be_own_unit=True, type_of_units_allowed_for_attachment="Warlord")
    ]
    return necrons_card_array
