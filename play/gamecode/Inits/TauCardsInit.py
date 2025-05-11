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
                                1, faction, "Common", False, limited=True)
    ]
    return tau_cards_array
