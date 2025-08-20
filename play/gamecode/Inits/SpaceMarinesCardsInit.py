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
                              0, faction, "Common", 1, False),
        CardClasses.ArmyCard("Blood Claw Pack", "Reaction: After an enemy warlord commits to this planet, "
                                                "exhaust this unit to put a Space Wolves unit into play from "
                                                "your hand at this planet.", "Soldier. Space Wolves.",
                             3, faction, "Common", 2, 2, 1, False),
        CardClasses.EventCard("Rally the Charge", "Action: Until the end of the phase, a target Space Marines "
                                                  "unit you control at a planet with your warlord gets +2 "
                                                  "ATK for each command icon it has.", "Tactic.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.SupportCard("Secluded Apothecarion", "Reaction: After a Space Marines unit you control is "
                                                         "destroyed, exhaust this support to gain 1 resource.",
                                "Location.", 1, faction, "Loyal", False),
        CardClasses.ArmyCard("Firedrake Terminators", "Reaction: After this unit is declared as a defender, "
                                                      "deal 1 damage to the attacker.", "Soldier. Salamanders. Elite.",
                             5, faction, "Common", 3, 6, 2, False),
        CardClasses.ArmyCard("Imperial Fists Siege Force", "Reaction: After you deploy this unit, rout 1 or more target"
                                                           " Ally units at this planet.", "Soldier. Imperial Fists.",
                             2, faction, "Common", 2, 2, 1, False),
        CardClasses.AttachmentCard("Nocturne-Ultima Storm Bolter", "Attach to an army unit.\n"
                                                                   "After attached unit damages an enemy "
                                                                   "unit by an attack, deal damage equal "
                                                                   "to the attached unit's ATK value to "
                                                                   "another target unit at the same planet.",
                                   "Wargear. Weapon.", 3, faction, "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Space Wolves Predator", "No Wargear Attachments.\n"
                                                      "Reaction: After you deploy this unit, your opponent cannot "
                                                      "commit his warlord to this planet this round unless it is "
                                                      "the only planet in play.", "Vehicle. Space Wolves. Elite.",
                             7, faction, "Common", 5, 5, 3, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Primal Howl", "Reaction: After your warlord commits to a planet with an "
                                             "enemy warlord, draw 3 cards. Max 1 per round.",
                              "Power. Space Wolves.", 0, faction, "Loyal", 2, False),
        CardClasses.SupportCard("Hallow Librarium", "Action: Exhaust this support to have a target unit at a "
                                                    "planet without an enemy warlord get -2 ATK until"
                                                    " the end of the phase.", "Location.",
                                2, faction, "Common", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Lone Wolf", "Action: Exhaust this unit to move it to a target planet with an enemy "
                                          "warlord and without any unit you control.", "Soldier. Space Wolves.",
                             3, faction, "Loyal", 3, 3, 1, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Righteous Initiate", "UNSTOPPABLE - The first time this unit is assigned damage this"
                                                   " round, prevent 1 of that damage and this unit gets "
                                                   "+2 ATK until the end of the phase.", "Soldier. Black Templars.",
                             2, faction, "Common", 1, 2, 1, False, unstoppable=True),
        CardClasses.EventCard("Accept Any Challenge", "Reaction: After you win a battle at a Tech planet (blue), "
                                                      "draw 1 card for each Black Templars unit you"
                                                      " control at that planet. (Max 1 per round.)", "Tactic. Vow.",
                              1, faction, "Common", 1, False),
        CardClasses.ArmyCard("Neophyte Apprentice", "FORCED REACTION: After this unit damages an enemy unit by an "
                                                    "attack, sacrifice it to search the top 6 cards of your"
                                                    " deck for a Black Templars unit with cost 4 or lower. "
                                                    "Put that unit into play at this planet, and shuffle the"
                                                    " remaining cards into your deck.",
                             "Ally. Black Templars. Soldier.", 1, faction, "Common", 1, 1, 1, False),
        CardClasses.AttachmentCard("The Black Sword", "Attach to a Black Templars army unit.\n"
                                                      "Reaction: After attached unit is declared as a defender,"
                                                      " deal 2 damage to the attacker.", "Relic. Weapon.",
                                   2, faction, "Loyal", 2, True, required_traits="Black Templars",
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Imperial Fists Devastators", "Reaction: After you deploy this unit to a tech planet "
                                                           "(blue), destroy a target Location support card.",
                             "Soldier. Imperial Fists.", 4, faction, "Common", 4, 3, 2, False),
        CardClasses.SupportCard("Teleportarium", "Action: Exhaust this support to move a Space Marines army unit you "
                                                 "control with printed cost 3 or lower from a Tech planet "
                                                 "(blue) to an adjacent planet.", "Location.",
                                2, faction, "Common", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Sword Brethren Dreadnought", "No Wargear Attachments.\n"
                                                           "UNSTOPPABLE - The first time this unit is assigned damage "
                                                           "this round, prevent 1 of that damage and you may trigger"
                                                           " the Battle ability of this planet.",
                             "Vehicle. Black Templars. Elite.", 7, faction, "Loyal", 5, 6, 3, False,
                             unstoppable=True, wargear_attachments_permitted=False),
        CardClasses.EventCard("Declare the Crusade", "Reaction: After you win a battle at a tech planet (blue), "
                                                     "choose another planet in play and a planet that has been"
                                                     " removed from the game. Switch the chosen planets.", "Tactic.",
                              2, faction, "Common", 1, False),
        CardClasses.AttachmentCard("Cenobyte Servitor", "Attach to a Black Templars unit.\n"
                                                        "Attached unit gets +1 HP.\n"
                                                        "Action: Sacrifice this attachment to put a Relic attachment "
                                                        "into play from your hand attached to an eligible unit.",
                                   "Drone.", 1, faction, "Common", 1, False,
                                   extra_health=1, required_traits="Black Templars",
                                   action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.WarlordCard("Chaplain Mavros", "Action: Deal 1 damage to a target Space Marines unit you "
                                                   "control at a tech planet (blue). The targeted unit gets +1 "
                                                   "ATK until the end of the phase. (Limit twice per phase.)",
                                "Soldier. Black Templars.", faction, 2, 7, 1, 6, "Bloodied.", 7, 7,
                                ["3x Reclusiam Templars", "1x The Emperor's Champion", "1x Faith and Hatred",
                                 "2x Vow of Honor", "1x Ancient Crozius Arcanum"],
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Reclusiam Templars", "UNSTOPPABLE - The first time this unit is assigned damage this"
                                                   " round, prevent 1 of that damage and ready this unit.",
                             "Soldier. Black Templars.", 3, faction, "Signature", 2, 3, 1, False, unstoppable=True),
        CardClasses.ArmyCard("The Emperor's Champion", "Combat Action: A target ready enemy army unit at this planet "
                                                       "must be declared as an attacker and this unit declared as a "
                                                       "defender during your opponent's next combat turn, if able. "
                                                       "(Limit once per combat phase.)",
                             "Soldier. Black Templars. Elite.", 5, faction, "Signature",
                             3, 6, 2, True, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Faith and Hatred", "Reaction: After a unit you control is assigned damage "
                                                    "by an attack, exhaust this support to prevent 1 of that damage.",
                                "Creed.", 0, faction, "Signature", False),
        CardClasses.EventCard("Vow of Honor", "Reaction: After a Space Marines unit you control takes damage, that "
                                              "unit gets +3 ATK for its next attack this phase.", "Power. Vow.",
                              1, faction, "Signature", 1, False),
        CardClasses.AttachmentCard("Ancient Crozius Arcanum", "Attach to a unit you control.\n"
                                                              "Attached unit gains, “Unstoppable - The first time this"
                                                              " unit is assigned damage this round, prevent 1 of that"
                                                              " damage and remove 1 damage from this unit.”",
                                   "Wargear. Weapon.", 1, faction, "Signature", 3, False, must_be_own_unit=True),
        CardClasses.ArmyCard("Reliquary Techmarine", "While this unit is at a tech planet (blue), "
                                                     "it gains: +1 card when command struggle won at this planet.",
                             "Soldier. Black Templars. Ally.", 3, faction, "Common", 2, 4, 1, False),
        CardClasses.SupportCard("Crypt of Saint Camila", "Deploy Action: Exhaust this support to put a non-Elite "
                                                         "Space Marines unit into play from your hand at a "
                                                         "tech planet (blue). (Limit once per phase.)",
                                "Location. Ecclesiarchy.", 4, faction, "Loyal", True,
                                action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.ArmyCard("8th Company Assault Squad", "Deep Strike (2).\n"
                                                          "Reaction: After you Deep Strike this unit, ready a target "
                                                          "Space Marines unit at this planet.", "Soldier. Dark Angels.",
                             3, faction, "Common", 3, 3, 1, False, deepstrike=2),
        CardClasses.AttachmentCard("Valkyris Pattern Jump Pack", "Deep Strike (0).\n"
                                                                 "Attach to an army unit you control.\n"
                                                                 "Attached unit gains Flying.", "Wargear.",
                                   2, faction, "Loyal", 2, False, must_be_own_unit=True,
                                   type_of_units_allowed_for_attachment="Army", deepstrike=0),
        CardClasses.WarlordCard("Epistolary Vezuel", "Reaction: After you Deep Strike a card, draw 1 card.",
                                "Dark Angels. Psyker.", faction, 2, 6, 2, 6, "Bloodied.", 7, 7,
                                ["4x Vezuel's Hunters", "1x Dark Angels Cruiser",
                                 "2x Unseen Strike", "1x Fulgaris"]),
        CardClasses.ArmyCard("Vezuel's Hunters", "Deep Strike (1).\n"
                                                 "Reaction: After you Deep Strike this unit, deal 2 damage to a "
                                                 "target enemy army unit at this planet.", "Soldier. Dark Angels.",
                             3, faction, "Signature", 2, 2, 1, False, deepstrike=1),
        CardClasses.SupportCard("Dark Angels Cruiser", "Deploy Action: Exhaust this support to put a target unit"
                                                       " you control at a planet in reserve.", "Dark Angels. Upgrade.",
                                0, faction, "Signature", False, action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.EventCard("Unseen Strike", "Deep Strike (1).\n"
                                               "Reaction: After you Deep Strike this event, you gain the "
                                               "initiative in this battle.", "Tactic.",
                              0, faction, "Signature", 1, False, deepstrike=1),
        CardClasses.AttachmentCard("Fulgaris", "Attach to your warlord.\n"
                                               "Reaction: After you Deep Strike a card, attached unit gets "
                                               "+1 ATK and +1 HP until the end of the phase.", "Wargear. Weapon.",
                                   1, faction, "Signature", 3, True, type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True),
        CardClasses.ArmyCard("Salamander Flamer Squad", "Area Effect (1).\n"
                                                        "Reaction: After this unit readies, deal 1 damage to each "
                                                        "enemy unit damaged by this unit this phase.",
                             "Soldier. Salamanders.", 4, faction, "Common", 2, 5, 2, False, area_effect=1),
        CardClasses.ArmyCard("Techmarine Aspirant", "Each Elite unit you control at this planet gains, “Action: Pay "
                                                    "1 resource to ready this unit. (Limit once per round.)”",
                             "Soldier. Dark Angels.", 2, faction, "Common", 1, 3, 1, False,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.SupportCard("Deathstorm Drop Pod", "Reaction: After you Deep Strike a card, deal 1 damage to an"
                                                       " enemy army unit at the same planet as that card.",
                                "Upgrade. Artillery.", 1, faction, "Common", False),
        CardClasses.ArmyCard("Deathwing Terminators", "Deep Strike (3).\n"
                                                      "Reaction: After you Deep Strike this unit, "
                                                      "it cannot be targeted by enemy card effects until the "
                                                      "end of the first combat round.", "Soldier. Dark Angels. Elite.",
                             5, faction, "Common", 4, 5, 2, False, deepstrike=3),
        CardClasses.EventCard("Repent!", "Action: Each player exhausts a unit he controls with the highest printed "
                                         "cost among units he controls. Then, each unit exhausted by this effect deals"
                                         " X damage, where X is its ATK value, to the other player's unit exhausted by"
                                         " this effect.", "Tactic.", 2, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Dark Angels Vindicator", "No Wargear Attachments.\n"
                                                       "While this unit is attacking it gets +2 ATK for each command "
                                                       "icon the defender has.", "Vehicle. Tank. Dark Angels.",
                             4, faction, "Common", 1, 5, 2, False, wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("Imperial Power Fist", "Attach to an army unit you control.\n"
                                                          "While each other unit you control at this planet is "
                                                          "exhausted, attached unit gets +5 ATK.", "Wargear. Weapon.",
                                   2, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   must_be_own_unit=True),
        CardClasses.ArmyCard("Iron Hands Centurion", "While this unit is ready, each unit with printed cost 2 or lower"
                                                     " at this planet cannot be declared as an attacker.",
                             "Soldier. Iron Hands. Elite.", 5, faction, "Common", 3, 7, 3, False),
        CardClasses.ArmyCard("Land Speeder Vengeance", "Area Effect (3).\n Flying.\n No Wargear Attachments.",
                             "Vehicle. Dark Angels. Elite.", 6, faction, "Loyal", 4, 3, 1, False,
                             area_effect=3, flying=False, wargear_attachments_permitted=False),
        CardClasses.SupportCard("Standard of Devastation", "Reaction: After a Dark Angels unit you control is "
                                                           "destroyed, each other Space Marines army unit "
                                                           "you control gets +1 ATK until the end of the phase.",
                                "Relic. Upgrade.", 3, faction, "Common", True),
        CardClasses.ArmyCard("First Line Rhinos", "No Wargear Attachments.\n"
                                                  "Reaction: After you deploy this unit, Rally 6 a non-Vehicle "
                                                  "Space Marines unit with printed cost 3 or lower, "
                                                  "attach it to this unit."
                                                  " When this unit leaves play, as an interrupt, put the attached unit"
                                                  " into play exhausted at the same planet.",
                             "Vehicle. Ultramarines.", 2, faction, "Loyal", 2, 2, 1, False,
                             wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("Centurion Warsuit", "Attach to a non-Elite army unit you control.\n"
                                                        "Attached unit gets +2 ATK, +4 HP and Lumbering.",
                                   "Wargear.", 1, faction, "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army", forbidden_traits="Elite",
                                   extra_attack=2, extra_health=4, must_be_own_unit=True),
        CardClasses.ArmyCard("Avenging Squad", "Retaliate (1).\n"
                                               "Reaction: After another unit you control at this planet is dealt damage"
                                               " by an enemy unit, this unit gains Retaliate (1) until the end"
                                               " of the phase.", "Soldier. Ultramarines.",
                             1, faction, "Common", 1, 2, 1, False, retaliate=1),
        CardClasses.ArmyCard("Dodging Land Speeder", "No Wargear Attachments.\n"
                                                     "Deep Strike (1). Flying.\n"
                                                     "Cannot be damaged by Area Effect.\n"
                                                     "Interrupt: When this unit is chosen as a defender, exhaust it "
                                                     "and move it to an adjacent planet to cancel the attack.",
                             "Vehicle. Dark Angels.", 2, faction, "Loyal", 3, 1, 1, False,
                             deepstrike=1, wargear_attachments_permitted=False, flying=True),
        CardClasses.ArmyCard("Dutiful Castellan", "While you control an Ecclesiarchy unit, "
                                                  "reduce the cost of this unit by 1.\n"
                                                  "Unstoppable - The first time this unit is assigned damage this turn,"
                                                  " prevent 1 of that damage and deal 1 damage to a target unit"
                                                  " at this planet.", "Martyr. Black Templars.",
                             3, faction, "Loyal", 3, 3, 1, False, unstoppable=True),
        CardClasses.ArmyCard("Fierce Purgator", "While this unit has faith, it gains Retaliate (3).\n"
                                                "Reaction: After this unit resolves its attack, deal 1 damage to a unit"
                                                " at this planet and each adjacent planet.", "Soldier. Grey Knights.",
                             3, faction, "Common", 1, 4, 1, False),
        CardClasses.ArmyCard("Grand Master Belial", "Deep Strike (2).\n"
                                                    "Interrupt: When your Bloodied warlord is defeated, discard it and"
                                                    " pay 1 resource and Deep Strike this unit to have it be considered"
                                                    " a warlord. If it is defeated you lose the game.",
                             "Soldier. Dark Angels.", -1, faction, "Loyal", 2, 6, 0, True, deepstrike=2),
        CardClasses.ArmyCard("Fighting Company Daras",
                             "Sweep (1).\n"
                             "Unstoppable - The first time this unit is assigned damage this"
                             " turn, prevent 1 of that damage and this unit gains "
                             "Retaliate (2) until the end of the phase.", "Soldier. Black Templars.",
                             3, faction, "Loyal", 2, 3, 1, False, sweep=1, unstoppable=True),
        CardClasses.ArmyCard("Frenzied Wulfen", "Retaliate (2).\n"
                                                "Reaction: After this unit enters play, a target army unit at this "
                                                "planet is considered a warlord for your card effects.",
                             "Warrior. Mutant. Space Wolves.", 3, faction, "Loyal", 3, 3, 1, False, retaliate=2),
        CardClasses.ArmyCard("Hjorvath Coldstorm", "While this unit is at a planet with an enemy warlord it "
                                                   "gets -2 ATK and -2 HP.\n"
                                                   "Interrupt: When your opponent triggers an ability that discards a"
                                                   " card from your hand, put this unit into play at a planet. Then "
                                                   "deal 1 damage to an enemy unit at that planet and draw a card.",
                             "Soldier. Space Wolves.", 1, faction, "Loyal", 3, 3, 1, True),
        CardClasses.ArmyCard("Inspiring Sergeant", "Retaliate (1).\n"
                                                   "Reaction: After this unit resolves its attack, a target unit at"
                                                   " this planet gets +1 ATK and +1 HP until the end of the phase.",
                             "Soldier. Space Marines.", 2, faction, "Loyal", 2, 2, 1, False, retaliate=1),
        CardClasses.ArmyCard("Interceptor Squad", "While this unit has faith, it gains Mobile.\n"
                                                  "Reaction: After a unit enters play at an adjacent planet, move this"
                                                  " unit to that planet. Then you may deal 1 damage to that unit."
                                                  " (Limit once per phase.)", "Soldier. Grey Knights.",
                             3, faction, "Common", 2, 4, 1, False),
        CardClasses.ArmyCard("Knight Paladin Voris", "No Attachments. Lumbering. Retaliate (5).\n"
                                                     "Cannot be targeted.\n"
                                                     "Each other unit you control at this"
                                                     " planet gets +1 ATK and +1 HP.", "Questor Imperialis.",
                             6, faction, "Loyal", 5, 9, 6, False, no_attachments=True, retaliate=5, lumbering=True)
    ]
    return space_marines_card_array
