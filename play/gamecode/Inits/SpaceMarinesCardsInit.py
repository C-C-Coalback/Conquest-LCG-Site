from .. import CardClasses


def space_marines_cards_init():
    faction = "Space Marines"
    space_marines_card_array = [
        CardClasses.WarlordCard("Captain Cato Sicarius",
                                "Reaction: After an enemy unit at this planet"
                                "is destoyed, gain 1 resource.", "Soldier. Ultramarines.",
                                faction, 2, 6, 2, 5,
                                "Bloodied.", 7, 7,
                                ["1x Cato's Stronghold", "1x Tallassarian Tempest Blade",
                                 "2x The Fury of Sicarius", "4x Sicarius's Chosen"]
                                ),
        CardClasses.ArmyCard("Sicarius's Chosen", "Reaction: After this unit enters play, "
                                                  "move a target enemy army unit at an "
                                                  "adjacent planet to this planet "
                                                  "and deal it 1 damage.",
                             "Soldier. Ultramarines.", 3, faction, "Signature",
                             2, 3, 1, False, ""),
        CardClasses.SupportCard("Cato's Stronghold", "Reaction: After an enemy unit is "
                                                     "destroyed, exhaust this support to "
                                                     "ready a target Space Marines unit "
                                                     "at the same planet", "Location.",
                                2, faction, "Signature", False, ""),
        CardClasses.EventCard("The Fury of Sicarius", "Reaction: After a Space Marines unit "
                                                      "damages an enemy non-warlord unit by "
                                                      "an attack, destroy the attacked unit.",
                              "Tactic.", 2, faction, "Signature", 1, False, ""),
        CardClasses.AttachmentCard("Tallassarian Tempest Blade", "Limit 1 Relic per player.\n"
                                                                 "Attach to a unique unit.\n"
                                                                 "Attached unit gets +1 ATK "
                                                                 "and gains Armorbane. (Shield "
                                                                 "cards cannot be used while "
                                                                 "this unit is attacking.",
                                   "Relic. Weapon.", 1, faction, "Signature", 3, True,
                                   unit_must_be_unique=True, extra_attack=1),
        CardClasses.ArmyCard("10th Company Scout", "", "Scout. Ultramarines.", 1, faction,
                             "Common", 2, 1, 1, False, ""),
        CardClasses.ArmyCard("Tactical Squad Cardinis", "Area Effect (1). (When this unit "
                                                        "attacks it may instead deal its "
                                                        "Area Effect damage to each enemy "
                                                        "unit at this planet.",
                             "Soldier. Ultramarines.", 2, faction,
                             "Common", 1, 3, 1, False, area_effect=1),
        CardClasses.ArmyCard("Honored Librarian", "Enemy units cannot attack this unit while "
                                                  "you control a unit not named "
                                                  "\"Honored Librarian\" at this planet",
                             "Psyker. Ultramarines.", 3, faction,
                             "Loyal", 4, 2, 1, False, ""),
        CardClasses.ArmyCard("Blood Angels Veterans", "While this unit is ready, it gains, "
                                                      "\"Reaction: After this unit is "
                                                      "assigned damage, prevent "
                                                      "1 of that damage.\"",
                             "Soldier. Blood Angels.", 3, faction,
                             "Common", 3, 3, 1, False, ""),
        CardClasses.ArmyCard("Daring Assault Squad", "Area Effect (2). (When this unit "
                                                     "attacks it may instead deal its "
                                                     "Area Effect damage to each enemy "
                                                     "unit at this planet.",
                             "Soldier. Blood Angels.", 4, faction,
                             "Common", 3, 3, 1, False, area_effect=2),
        CardClasses.ArmyCard("Land Raider", "No Wargear Attachments.\n Non-Vehicle units you "
                                            "control at this planet cannot be targeted by "
                                            "enemy card abilities.", "Vehicle. Tank. Elite.",
                             5, faction, "Common", 3, 7, 3, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Ultramarines Dreadnought", "No Wargear Attachments.",
                             "Vehicle. Ultramarines. Elite.", 6, faction, "Loyal",
                             8, 8, 0, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Veteran Brother Maxos", "Combat Action: Pay the printed cost "
                                                      "of a Space Marines unit in your hand "
                                                      "to put it into play at this planet.",
                             "Soldier. Ultramarines.", 3, faction, "Loyal", 2, 3, 2, True,
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Eager Recruit", "Ambush. (You may deploy this card during"
                                              " the combat phase.", "Scout. Ultramarines.",
                             1, faction, "Common", 2, 1, 0, False,
                             action_in_hand=True, allowed_phases_in_hand="COMBAT",
                             ambush=True),
        CardClasses.ArmyCard("Iron Hands Techmarine", "This unit gains 1 command icon "
                                                      "for each enemy unit at this planet.",
                             "Soldier. Iron Hands.", 3, faction, "Common", 1, 3, 1, False, ""),
        CardClasses.ArmyCard("Raven Guard Speeder", "No Wargear Attachments.\n Flying. (This "
                                                    "unit takes half damage from non-Flying "
                                                    "units.", "Vehicle. Raven Guard.",
                             4, faction, "Common", 3, 3, 2, False, flying=True,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Deathwing Guard", "", "Soldier. Dark Angels. Elite.", 5, faction,
                             "Loyal", 2, 9, 4, False, ""),
        CardClasses.EventCard("Drop Pod Assault", "Combat Action: Target a planet where a "
                                                  "battle is taking place. Search the top 6 "
                                                  "cards for a Space Marines unit with printed "
                                                  "cost 3 or lower. Put that unit into play at "
                                                  "the targeted planet, and place the "
                                                  "remaining cards on the bottom of your deck "
                                                  "in any order.", "Tactic.", 2, faction,
                              "Loyal", 2, False, action_in_hand=True,
                              allowed_phases_in_hand="COMBAT"),
        CardClasses.EventCard("Indomitable", "Reaction: After a Space Marines unit is assigned "
                                             "damage by an attack, prevent all of that damage.",
                              "Power.", 1, faction, "Common", 1, False, ""),
        CardClasses.EventCard("Exterminatus",
                              "Deploy Action: Destroy all non-unique units at a "
                              "target non-first planet.", "Tactic.",
                              3, faction, "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("Godwyn Pattern Bolter", "Attach to an army unit.\n"
                                                            "Attached unit gets +1 ATK, +1HP, "
                                                            "and while attacking ignores the "
                                                            "Flying keyword on enemy units.",
                                   "Wargear. Weapon.", 1, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army",
                                   extra_attack=1, extra_health=1),
        CardClasses.AttachmentCard("Iron Halo", "Limit 1 Relic per player.\n"
                                                "Attach to a unique unit.\n"
                                                "Reaction: After attached unit is assigned "
                                                "damage by an attack, exhaust this attachment "
                                                "to prevent all of that damage.",
                                   "Relic. Wargear.", 3, faction, "Loyal", 2, True,
                                   unit_must_be_unique=True),
        CardClasses.SupportCard("Fortress-Monastery", "Limited.\nInterrupt: When you deploy"
                                                      " a Space Marines unit, exhaust this "
                                                      "support to reduce that "
                                                      "unit's cost by 1.",
                                "Location.", 1, faction, "Common", True, "",
                                applies_discounts=[True, 1, True],
                                is_faction_limited_unique_discounter=True, limited=True),
        CardClasses.SupportCard("Holy Sepulchre", "Reaction: After a Space Marines unit enters "
                                                  "your discard pile, exhaust this support to "
                                                  "return that unit to your hand.", "Location",
                                2, faction, "Common", False, ""),
        CardClasses.ArmyCard("Veteran Barbrus", "Ambush.\n"
                                                "Reaction: After this unit enters play, deal 2 damage to a target "
                                                "army unit at this planet. This ability cannot target "
                                                "Space Marines, Astra Militarum, or Chaos units.",
                             "Soldier. Deathwatch.", 4, faction, "Loyal", 2, 4, 2, True,
                             action_in_hand=True, allowed_phases_in_hand="COMBAT", ambush=True),
        CardClasses.EventCard("Vengeance!", "Reaction: After a unit you control is destroyed by an attack, ready a "
                                            "target Space Marines army unit you control at that planet.", "Tactic.",
                              1, faction, "Common", 1, False),
        CardClasses.ArmyCard("Ravenwing Escort", "While you control a non-Space Marines warlord, "
                                                 "this unit gains Mobile.\n"
                                                 "Combat Action: Exhaust this unit to move an army unit you "
                                                 "control at this planet to another planet.", "Scout. Dark Angels.",
                             4, faction, "Common", 2, 3, 1, False, action_in_play=True,
                             allowed_phases_in_play="COMBAT"),
        CardClasses.WarlordCard("Ragnar Blackmane", "Reaction: After your warlord commits to a planet with an enemy "
                                                    "warlord, deal 2 damage to a target enemy unit at that planet.",
                                "Soldier. Space Wolves.", faction, 2, 7, 2, 5, "Bloodied.", 7, 7,
                                ["4x Blackmane Sentinel", "1x Frostfang",
                                 "1x Ragnar's Warcamp", "2x Blackmane's Hunt"]),
        CardClasses.ArmyCard("Blackmane Sentinel", "Reaction: After your warlord commits to a planet, "
                                                   "move this unit to that planet.", "Soldier. Space Wolves.",
                             2, faction, "Signature", 2, 2, 1, False),
        CardClasses.AttachmentCard("Frostfang", "Attach to a Space Wolves unit.\n"
                                                "Attached unit gets +2 ATK and +2 HP while it is at a planet with an "
                                                "enemy warlord.", "Relic. Wargear. Weapon.",
                                   2, faction, "Signature", 3, True, required_traits="Space Wolves"),
        CardClasses.SupportCard("Ragnar's Warcamp", "Each Space Wolves unit you control at a planet with your "
                                                    "warlord deals double damage while attacking an enemy warlord.",
                                "Location.", 3, faction, "Signature", True),
        CardClasses.EventCard("Blackmane's Hunt", "Reaction: After your warlord commits to a planet, "
                                                  "commit your warlord to an adjacent planet.",
                              "Tactic.", 0, faction, "Signature", 1, False),
        CardClasses.ArmyCard("Morkai Rune Priest", "Forced Interrupt: When a non-Space Wolves unit retreats from this"
                                                   " planet, deal 1 damage to that unit.", "Psyker. Space Wolves.",
                             4, faction, "Loyal", 3, 4, 1, False),
        CardClasses.AttachmentCard("Fenrisian Wolf", "Attach to an army unit.\n"
                                                     "Reaction: After a battle at this planet begins,"
                                                     " exhaust attached unit to deal damage equal to its ATK "
                                                     "value to a target army unit at the same planet.", "Creature.",
                                   2, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("White Scars Bikers", "This unit gets +2 ATK while it is at a planet with a warlord.",
                             "Soldier. White Scars.", 3, faction, "Common", 2, 3, 1, False),
        CardClasses.EventCard("Know No Fear", "Deploy Action: Exhaust your warlord to move up to 3 Space Marines units"
                                              " from your HQ, each to a different planet.", "Tactic. Maneuver.",
                              1, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.EventCard("Crushing Blow", "Reaction: After a Space Marines unit damages an enemy unit, deal 1 "
                                               "unpreventable damage to that enemy unit.", "Tactic.",
                              0, faction, "Common", 1, False)
    ]
    return space_marines_card_array
