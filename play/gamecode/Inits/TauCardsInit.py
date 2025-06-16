from .. import CardClasses


def tau_cards_init():
    faction = "Tau"
    tau_cards_array = [
        CardClasses.WarlordCard("Commander Shadowsun", "Reaction: After this warlord commits to "
                                                       "a planet, put a Tau attachment with printed "
                                                       "cost 2 or lower or "
                                                       "\"Shadowsun's Stealth Cadre\" "
                                                       "from your hand or discard pile into play "
                                                       "attached to an eligible unit at this planet.",
                                "Soldier. Shas'o.", faction, 1, 7, 1, 5, "Bloodied.", 7, 7,
                                ["4x Shadowsun's Stealth Cadre", "1x Communications Relay",
                                 "2x Squadron Redeployment", "1x Command-Link Drone"]),
        CardClasses.ArmyCard("Shadowsun's Stealth Cadre", "This card may enter play as an attachment "
                                                          "with the text \"Attach to a non-Vehicle "
                                                          "army unit. Attached unit gets "
                                                          "+2 ATK and +2 HP.\"", "Soldier. Pilot.",
                             2, faction, "Signature", 2, 2, 1, False),
        CardClasses.SupportCard("Communications Relay", "Interrupt: When your opponent triggers an "
                                                        "ability that targets a unit you control with "
                                                        "1 or more attachments, exhaust this support "
                                                        "to cancel its effects.", "Upgrade.",
                                1, faction, "Signature", False),
        CardClasses.EventCard("Squadron Redeployment", "Action: Exhaust an army unit with 1 or more "
                                                       "attachments to move it to a target planet.",
                              "Tactic.", 0, faction, "Signature", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Command-Link Drone", "Attach to a unit.\n"
                                                         "Attached unit gets +1 ATK.\n"
                                                         "Action: Pay 1 resource to attach this card "
                                                         "to a different unit.", "Drone.",
                                   0, faction, "Signature", 3, False, action_in_play=True,
                                   allowed_phases_in_play="ALL", extra_attack=1),
        CardClasses.ArmyCard("Recon Drone", "Limited.", "Drone. Ally.", 0, faction, "Loyal",
                             0, 1, 2, False, limited=True),
        CardClasses.ArmyCard("Vior'la Marksman", "Ranged.", "Scout. Shas'la.", 1, faction, "Common",
                             1, 2, 1, False, ranged=True),
        CardClasses.ArmyCard("Carnivore Pack", "Interrupt: When this unit is destroyed, "
                                               "gain 3 resources.", "Warrior. Kroot.",
                             3, faction, "Common", 3, 3, 0, False),
        CardClasses.ArmyCard("Vash'ya Trailblazer", "Mobile.", "Scout. Pilot.",
                             2, faction, "Common", 1, 1, 2, False, mobile=True),
        CardClasses.ArmyCard("Fire Warrior Elite", "Interrupt: When an enemy unit would declare an "
                                                   "attack against a unit you control at this planet, "
                                                   "declare this unit as the defender instead.",
                             "Soldier. Shas'la.", 3, faction, "Common", 1, 5, 0, False),
        CardClasses.ArmyCard("Fire Warrior Strike Team", "This unit gets +1 ATK "
                                                         "for every attachment on it.",
                             "Soldier. Shas'la.", 4, faction, "Common", 1, 5, 1, False),
        CardClasses.ArmyCard("Crisis Battle Guard", "Mobile.", "Soldier. Pilot. Elite.",
                             5, faction, "Loyal", 3, 5, 3, False, mobile=True),
        CardClasses.ArmyCard("Earth Caste Technician", "Reaction: After this unit enters play, "
                                                       "search the top 6 cards of your deck for an "
                                                       "attachment or Drone card. Reveal it, add it "
                                                       "to your hand, and place the remaining cards "
                                                       "on the bottom of your deck in any order.",
                             "Scholar. Ally.", 1, faction, "Common", 1, 1, 1, False),
        CardClasses.ArmyCard("Gun Drones", "You may deploy this card as a Drone attachment with the "
                                           "text, \"Attach to a non-Vehicle army unit."
                                           "Attached unit gains Area Effect (2).\"", "Drone.",
                             2, faction, "Loyal", 2, 2, 1, False),
        CardClasses.ArmyCard("Stingwing Swarm", "Ranged.", "Warrior. Vespid.", 4, faction, "Common",
                             3, 3, 1, False, ranged=True),
        CardClasses.ArmyCard("Fireblade Kais'vre", "Interrupt: When you use a Tau card as a shield card "
                                                   "at this planet, it gains 1 shield icon.",
                             "Solider. Hero.", 3, faction, "Loyal", 2, 3, 2, True),
        CardClasses.ArmyCard("Experimental Devilfish", "No Wargear Attachments.\n"
                                                       "Reaction: After this unit commits to a "
                                                       "planet, ready it.", "Vehicle. Transport.",
                             3, faction, "Common", 4, 2, 1, False,
                             wargear_attachments_permitted=False),
        CardClasses.EventCard("Even the Odds", "Action: Move a target attachment to another eligible "
                                               "unit controlled by the same player.", "Tactic.",
                              1, faction, "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Calculated Strike", "Action: Destroy a target Limited card.",
                              "Tactic.", 1, faction, "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Deception", "Deploy Action: Return a target non-Elite army "
                                           "unit to its owner's hand.", "Tactic.",
                              2, faction, "Loyal", 2, False, action_in_hand=True,
                              allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("Repulsor Impact Field", "Attach to an army unit."
                                                            "Limit 1 per unit.\n"
                                                            "Reaction: After attached unit is damaged "
                                                            "by an attack, deal 2 damage to the "
                                                            "attacker.", "Wargear.",
                                   2, faction, "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army", limit_one_per_unit=True),
        CardClasses.AttachmentCard("Ion Rifle", "Attach to an army unit.\n"
                                                "Attached unit gets +3 ATK.", "Wargear. Weapon.",
                                   1, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", extra_attack=3),
        CardClasses.SupportCard("Frontline Launch Bay", "Limited.\n"
                                                        "Interrupt: When you deploy a Tau unit, exhaust "
                                                        "this support to reduce that unit's cost by 1.",
                                "Location.", 1, faction, "Common", True,
                                applies_discounts=[True, 1, True],
                                is_faction_limited_unique_discounter=True, limited=True),
        CardClasses.SupportCard("Ambush Platform", "Interrupt: When you deploy an attachment, "
                                                   "reduce its cost by 1.\n"
                                                   "Combat Action: Exhaust this support to deploy "
                                                   "an attachment from your hand.",
                                "Upgrade.", 2, faction, "Common", False, action_in_play=True,
                                allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Pathfinder Shi Or'es", "Action: Discard an attachment on this unit to ready it."
                                                     " (Limit once per phase.)", "Scout.",
                             3, faction, "Loyal", 3, 3, 1, True, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.SupportCard("Repair Bay", "Deploy Action: Exhaust this support to place a Drone or Pilot "
                                              "card from your discard pile on top of your deck.", "Location.",
                                1, faction, "Common", False, action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.ArmyCard("Air Caste Courier", "While you control a non-Tau warlord, this unit gains Flying.\n"
                                                  "Combat Action: Exhaust this unit to move an attachment from a unit"
                                                  " you control at this planet to another eligible unit you control.",
                             "Scout. Pilot.", 2, faction, "Common", 1, 3, 1, False, action_in_play=True,
                             allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Piranha Hunter", "Mobile.\n"
                                               "No Wargear Attachments.\n"
                                               "Reaction: After this unit moves from one planet to another, "
                                               "draw 1 card.", "Vehicle. Speeder.",
                             3, faction, "Common", 2, 2, 0, False, wargear_attachments_permitted=False, mobile=True),
        CardClasses.ArmyCard("Aun'ui Prelate", "Ambush.\n"
                                               "FORCED REACTION: After this unit resolves its attack, "
                                               "move it to your HQ.\n"
                                               "Reaction: After you deploy this unit, each other Tau unit \n"
                                               "you control at this planet gets +1 ATK until the end of the phase.",
                             "Soldier. Ethereal.", 4, faction, "Loyal", 4, 3, 0, False, ambush=True,
                             action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.SupportCard("Homing Beacon", "Limited.\n"
                                                 "Reaction: After a unit you control moves to your HQ, "
                                                 "exhaust this support to gain 1 or draw 1 card.", "Upgrade.",
                                1, faction, "Common", False, limited=True),
        CardClasses.ArmyCard("Bork'an Recruits", "This unit gets +2 ATK while it is at a planet with a warlord.",
                             "Soldier.", 2, faction, "Common", 2, 2, 1, False),
        CardClasses.EventCard("Kauyon Strike", "Combat Action: Move 1 or more Ethereal units "
                                               "you control to a target planet.", "Tactic.",
                              1, faction, "Loyal", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Blacksun Filter", "Attach to an army unit.\n"
                                                      "After an enemy warlord commits to the same "
                                                      "planet as attached unit, gain 1 resource.", "Wargear.",
                                   0, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army"),
        CardClasses.WarlordCard("Aun'shi", "Each Tau unit you control at this planet gains Armorbane.\n"
                                           "FORCED REACTION: After this warlord resolves its attack,"
                                           " move it to your HQ.", "Ethereal. Soldier.", faction,
                                2, 7, 1, 5, "Bloodied.", 7, 7,
                                ["4x Ethereal Envoy", "1x Aun'shi's Sanctum",
                                 "1x Honor Blade", "2x Ethereal Wisdom"]),
        CardClasses.ArmyCard("Ethereal Envoy", "FORCED REACTION: After this unit resolves its attack, "
                                               "move it to your HQ.", "Ethereal. Soldier.",
                             1, faction, "Signature", 1, 3, 1, False),
        CardClasses.SupportCard("Aun'shi's Sanctum", "Action: Exhaust this support to ready a target unit at a "
                                                     "planet with 1 or more Ethereal units you control.", "Location.",
                                2, faction, "Signature", True, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Honor Blade", "Attach to an Ethereal unit.Attached unit gains, “Each other Tau "
                                                  "unit you control at this planet gets +1 ATK.”", "Wargear. Weapon.",
                                   1, faction, "Signature", 3, False, required_traits="Ethereal"),
        CardClasses.EventCard("Ethereal Wisdom", "Action: Until the end of the phase, a target Tau unit you control "
                                                 "gets +1 ATK and gains the Ethereal trait.", "Tactic.",
                              0, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Sa'cea XV88 Broadside", "This unit gain Area Effect (2) "
                                                      "while it has 1 or more attachments.",
                             "Soldier. Pilot. Elite.", 6, faction, "Loyal", 4, 6, 3, False),
        CardClasses.EventCard("Tense Negotiations", "Action: Exhaust your warlord to trigger the Battle "
                                                    "ability at the same planet as your warlord.", "Tactic."
                              , 1, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Heavy Marker Drone", "Attach to an enemy army unit.\n"
                                                         "Double damage dealt to attached unit.", "Drone.",
                                   1, faction, "Loyal", 2, False, type_of_units_allowed_for_attachment="Army",
                                   must_be_enemy_unit=True),
        CardClasses.ArmyCard("Fire Warrior Grenadiers", "For each Ethereal unit you control at this planet, "
                                                        "this unit gets +2 ATK and gains 1 command icon.",
                             "Soldier. Shas'la.", 3, faction, "Common", 2, 2, 0, False),
        CardClasses.SupportCard("Ksi'm'yen Orbital City", "Combat Action: Exhaust this support to move an Ethereal"
                                                          " unit from your HQ to a target planet. "
                                                          "Then, ready that unit.", "Location.",
                                2, faction, "Loyal", False, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Vior'la Warrior Cadre", "This unit gains Ranged while you control an"
                                                      " Ethereal unit at this planet.", "Soldier. Shas'la.",
                             4, faction, "Common", 4, 3, 1, False),
        CardClasses.EventCard("For the Tau'va", "Action: Exhaust your warlord to ready each unit "
                                                "you control with 1 or more attachments.", "Tactic. Maneuver.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.WarlordCard("Commander Starblaze", "You may include common Astra Militarum cards in your deck, "
                                                       "but cannot include other cards from a non-Tau faction.\n"
                                                       "Reaction: After this warlord commits to a planet, move 1 "
                                                       "Astra Militarum unit you control from an "
                                                       "adjacent planet to this planet.", "Shas'o. Soldier.",
                                faction, 2, 6, 2, 5, "Bloodied.", 7, 7,
                                ["4x Ardent Auxiliaries", "1x Starblaze's Outpost",
                                 "2x Bond of Brotherhood", "1x Searing Burst Cannon"]),
        CardClasses.ArmyCard("Ardent Auxiliaries", "Reaction: After this unit commits to a planet, if you control an "
                                                   "Astra Militarum unit at this planet, ready this unit.", "Soldier.",
                             2, faction, "Signature", 2, 2, 1, False),
        CardClasses.SupportCard("Starblaze's Outpost", "Action: Exhaust this support and return an Astra Militarum "
                                                       "army unit at a planet to your hand to put a Tau unit "
                                                       "with equal or lower printed cost into play from your "
                                                       "hand at the same planet.", "Location.",
                                2, faction, "Signature", True, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Bond of Brotherhood", "Action: Until the end of the phase, each Tau unit you control"
                                                     " at a target planet gets +2 HP and each Astra Militarum"
                                                     " unit you control at the targeted planet gets +2 ATK.", "Tactic.",
                              2, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Searing Burst Cannon", "Attach to a unit.\n"
                                                           "Interrupt: When attached unit damages an enemy unit by an"
                                                           " attack, if no shield card was used during this"
                                                           " attack, double the damage taken.", "Wargear. Weapon.",
                                   1, faction, "Signature", 3, False),
        CardClasses.ArmyCard("Prudent Fire Warriors", "Interrupt: When this unit leaves play, attach each attachment "
                                                      "on it to a target eligible unit at this planet.", "Soldier.",
                             2, faction, "Common", 2, 3, 0, False),
        CardClasses.ArmyCard("Exploratory Drone", "Reaction: After a non-Tau unit is deployed at this planet,"
                                                  " move this unit to an adjacent planet.", "Drone.",
                             1, faction, "Loyal", 0, 2, 1, False),
        CardClasses.AttachmentCard("Auxiliary Armor", "Attach to an army unit.\n"
                                                      "Attached unit gets +2 ATK and +1 HP.\n"
                                                      "If attached unit is a non-Tau unit, it gains 1 command icon.",
                                   "Wargear. Armor.", 2, faction, "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army", extra_attack=2, extra_health=1),
        CardClasses.ArmyCard("Prototype Crisis Suit", "Reaction: After you deploy this unit, search the top 9 cards "
                                                      "of your deck for up to 2 Tau attachments, each with printed "
                                                      "cost 2 or lower. Put each eligible attachment into play "
                                                      "attached to this unit. Then, shuffle the remaining cards "
                                                      "into your deck.", "Pilot. Elite.",
                             5, faction, "Common", 4, 4, 2, False),
        CardClasses.EventCard("Mont'ka Strike", "Combat Action: Exhaust each ready Soldier unit you control at a "
                                                "target planet to deal damage equal to their combined printed"
                                                " ATK value to an enemy army unit at the targeted planet.", "Tactic.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.SupportCard("Sae'lum Enclave", "Limited.\n"
                                                   "Interrupt: When you deploy a non-Tau unit, exhaust this support "
                                                   "to reduce that unit's cost by 2.", "Location.",
                                1, faction, "Loyal", True, limited=True),
        CardClasses.ArmyCard("Auxiliary Overseer", "For each non-Tau unit you conrol at this planet,"
                                                   " this unit gets +1 ATK.", "Soldier.",
                             2, faction, "Loyal", 1, 3, 1, False),
        CardClasses.AttachmentCard("Drone Defense System", "Attach to a Pilot or Vehicle unit.\n"
                                                           "Combat Action: Exhaust attached unit to deal 2 damage to"
                                                           " each exhausted enemy unit at this planet.", "Hardpoint.",
                                   1, faction, "Common", 1, False, required_traits="Vehicle/Pilot",
                                   type_of_units_allowed_for_attachment="Army", action_in_play=True,
                                   allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Sae'lum Pioneer", "While this unit is at a Material planet (red), it gains: "
                                                "+2 resources when command struggle won at this planet.",
                             "Scout. Ally.", 3, faction, "Common", 2, 2, 1, False),
        CardClasses.SupportCard("Colony Shield Generator", "Interrupt: When a support card you control would be "
                                                           "targeted, exhaust this support to have this card "
                                                           "be targeted instead (ignoring targeting restrictions).",
                                "Upgrade.", 0, faction, "Common", False),
        CardClasses.ArmyCard("Kroot Hunter", "Reaction: After you deploy this unit at a "
                                             "Material planet (red), gain 1 resource.", "Scout. Ally.",
                             1, faction, "Common", 2, 2, 0, False),
        CardClasses.EventCard("War of Ideas", "Interrupt: When a command struggle resolves at a planet, "
                                              "exhausted army units you control count their command "
                                              "icons during that command struggle.", "Tactic.",
                              0, faction, "Common", 1, False),
        CardClasses.ArmyCard("Kroot Guerrilla", "Reaction: After a battle a this planet begins, gain 1 resource.",
                             "Warrior. Kroot.", 3, faction, "Common", 2, 3, 1, False),
        CardClasses.ArmyCard("XV8-05 Enforcer", "Reaction: After damage from an attack by this unit has been assigned,"
                                                " reassign any amount of that damage to another enemy "
                                                "unit at this planet. (Limit once per attack.)", "Soldier. Pilot.",
                             4, faction, "Common", 4, 4, 1, False),
        CardClasses.ArmyCard("Grav Inhibitor Drone", "Each unit with printed cost 2 or lower at this planet cannot "
                                                     "attack while a unit with printed cost 3 or higher at"
                                                     " this planet is ready.", "Drone.",
                             1, faction, "Common", 0, 4, 0, False),
        CardClasses.AttachmentCard("Missile Pod", "Attach to a Pilot or Vehicle unit you control."
                                                  "Deploy Action: Sacrifice this attachment to deal 3 damage to a "
                                                  "target enemy army unit in your opponent's HQ or destroy a target "
                                                  "support card.", "Hardpoint.",2, faction, "Common", 1, False,
                                   must_be_own_unit=True, required_traits="Pilot/Vehicle", action_in_play=True,
                                   allowed_phases_in_play="DEPLOY"),
        CardClasses.ArmyCard("Sniper Drone Team", "Ranged.\n"
                                                  "Reaction: After the ranged skirmish at this planet ends, "
                                                  "ready this unit.", "Soldier. Drone.",
                             4, faction, "Loyal", 2, 5, 2, False, ranged=True),
        CardClasses.EventCard("Tactical Withdrawal", "Deep Strike (0).\n"
                                                     "Reaction: After you Deep Strike this event, move any number"
                                                     " of units you control at this planet to an adjacent planet.",
                              "Tactic.", 0, faction, "Loyal", 2, False, deepstrike=0),
        CardClasses.ArmyCard("Herald of the Tau'va", "Each Elite unit you control at this planet gains Mobile.\n"
                                                     "FORCED REACTION: After this unit resolves its attack,"
                                                     " move it to your HQ.", "Soldier. Ethereal.",
                             2, faction, "Common", 1, 3, 1, False),
        CardClasses.SupportCard("Beleaguered Garrison", "Each card you control in reserve is counted as a command "
                                                        "icon at its planet when resolving command struggles.",
                                "Location.", 1, faction, "Common", True),
        CardClasses.ArmyCard("XV25 Stealth Squad", "Deep Strike (3).\n"
                                                   "You may Deep Strike this card as an Action "
                                                   "during the combat phase.", "Soldier. Pilot. Elite.",
                             5, faction, "Common", 5, 3, 0, False, deepstrike=3),
        CardClasses.AttachmentCard("Kroot Hunting Rifle", "Deep Strike (0).\n"
                                                          "Attach to an army unit you control.\n"
                                                          "Reaction: After attached unit destroys an enemy unit "
                                                          "by an attack, gain 1 resource.", "Wargear. Kroot.",
                                   2, faction, "Common", 1, False, deepstrike=0,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.ArmyCard("Raging Krootox", "No Attachments.\n"
                                               "Combat Action: This unit gets +X ATK until the end of ths phase."
                                               " X is the number of in your resource pool. (Limit once per phase.)",
                             "Creature. Kroot. Elite.", 5, faction, "Loyal", 2, 6, 0, False,
                             no_attachments=True, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.EventCard("Hunter's Ploy", "Reaction: After the headquarters phase begins, each player gains "
                                               "resources equal to the highest printed cost among units he controls.",
                              "Tactic.", 0, faction, "Common", 1, False)
    ]
    return tau_cards_array
