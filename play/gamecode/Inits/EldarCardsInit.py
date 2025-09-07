from .. import CardClasses


def eldar_cards_init():
    faction = "Eldar"
    eldar_cards_array = [
        CardClasses.WarlordCard("Eldorath Starbane", "Reaction: After this warlord commits to a "
                                                     "planet, exhaust a target non-warlord unit "
                                                     "at that planet.",
                                "Psyker. Alaitoc.", faction, 1, 7, 1, 6, "Bloodied.", 7, 7,
                                ["4x Starbane's Council", "1x Alaitoc Shrine",
                                 "2x Foresight", "1x Mobility"]),
        CardClasses.ArmyCard("Starbane's Council", "This unit gets +2 ATK while attacking an "
                                                   "exhausted unit.", "Psyker. Alaitoc.",
                             3, faction, "Signature", 3, 3, 1, False),
        CardClasses.SupportCard("Alaitoc Shrine", "Reaction: After an Eldar unit moves to a planet, "
                                                  "exhaust this support to ready that unit.",
                                "Location. Alaitoc.", 1, faction, "Signature", False),
        CardClasses.EventCard("Foresight", "Reaction: After your warlord commits to a planet, "
                                           "commit it to a different planet.", "Power.",
                              1, faction, "Signature", 1, False),
        CardClasses.AttachmentCard("Mobility", "Attach to an army unit.\n"
                                               "Attached unit gains Mobile.", "Skill.",
                                   0, faction, "Signature", 3, False,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Biel-Tan Guardians", "", "Warrior. Biel-Tan. Ally.",
                             1, faction, "Loyal", 1, 1, 2, False),
        CardClasses.ArmyCard("Altansar Rangers", "Ranged.", "Scout. Altansar.", 3, faction,
                             "Common", 2, 2, 2, False, ranged=True),
        CardClasses.ArmyCard("Eldar Survivalist", "+1 resource and +1 card when command struggle"
                                                  "is won at this planet.",
                             "Scout. Ally.", 2, faction, "Common", 0, 2, 1, False,
                             additional_resources_command_struggle=1,
                             additional_cards_command_struggle=1),
        CardClasses.ArmyCard("Wildrider Squadron", "No Wargear Attachments.\n"
                                                   "Combat Action: Move this unit to an adjacent"
                                                   " planet. (Limit once per phase.)",
                             "Vehicle. Saim-Hann.", 4, faction, "Common", 3, 4, 1, False,
                             action_in_play=True, allowed_phases_in_play="COMBAT",
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Soaring Falcon", "No Wargear Attachments.\n"
                                               "Mobile.", "Vehicle.",
                             3, faction, "Common", 1, 5, 2, False,
                             wargear_attachments_permitted=False, mobile=True),
        CardClasses.ArmyCard("Wailing Wraithfighter", "No Wargear Attachments.\n"
                                                      "Flying.\n"
                                                      "Reaction: After this unit is declared as an "
                                                      "attacker, your opponent must choose and "
                                                      "discard 1 card from his hand, if able.",
                             "Vehicle. Spirit. Elite.", 6, faction, "Loyal", 3, 5, 2, False,
                             wargear_attachments_permitted=False, flying=True),
        CardClasses.ArmyCard("Iyanden Wraithguard", "Armorbane.", "Drone. Spirit. Iyanden.",
                             3, faction, "Loyal", 4, 2, 1, False, armorbane=True),
        CardClasses.ArmyCard("Shrouded Harlequin", "Interrupt: When this unit is destroyed, exhaust "
                                                   "a target enemy unit at a planet of your choice.",
                             "Warrior. Harlequin.", 2, faction, "Common", 2, 1, 1, False),
        CardClasses.ArmyCard("Swordwind Farseer", "Reaction: After this unit enters play, "
                                                  "search the top 6 cards of your deck for a card. "
                                                  "Add it to your hand, and place the remaining cards "
                                                  "on the bottom of your deck in any order.",
                             "Psyker. Biel-Tan.", 3, faction, "Loyal", 2, 2, 1, False),
        CardClasses.ArmyCard("Silvered Blade Avengers", "Reaction: After this unit is declared as an "
                                                        "attacker against a non-warlord unit, "
                                                        "exhaust that unit.", "Warrior.",
                             4, faction, "Common", 1, 4, 1, False),
        CardClasses.ArmyCard("Biel-Tan Warp Spiders", "Reaction: After this unit is declared as "
                                                      "an attacker, look at the top 2 cards of "
                                                      "any player's deck. You may discard 1 "
                                                      "of those cards.", "Warrior. Biel-Tan.",
                             2, faction, "Common", 1, 3, 1, False),
        CardClasses.ArmyCard("Spiritseer Erathal", "Reaction: After this unit is declared as an "
                                                   "attacker, remove 1 damage from another target "
                                                   "at this planet.", "Psyker. Saim-Hann.",
                             3, faction, "Loyal", 2, 3, 2, True),
        CardClasses.EventCard("Superiority", "Interrupt: When a command struggle at a planet begins, "
                                             "a target army unit at that planet loses all command "
                                             "icons until the end of that command struggle.",
                              "Tactic.", 1, faction, "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="COMMAND"),
        CardClasses.EventCard("Nullify", "Interrupt: When your opponent plays an event card, "
                                         "exhaust a unique Eldar unit to cancel its effects.",
                              "Power.", 0, faction, "Common", 1, False),
        CardClasses.EventCard("Doom", "Deploy Action: Destroy each non-unique unit at "
                                      "each player's HQ.", "Power.",
                              4, faction, "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="DEPLOY"),
        CardClasses.EventCard("Gift of Isha", "Action: Put the topmost Eldar unit from your discard "
                                              "pile into play at a planet. If that unit is still "
                                              "in play at the end of the phase, discard it.",
                              "Power. Blessing.", 2, faction, "Loyal", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Banshee Power Sword", "Attach to an army unit.\n"
                                                          "Attached unit gets +1 ATK.\n"
                                                          "Interrupt: When attached unit declares an "
                                                          "attack against a non-warlord unit, discard "
                                                          "X cards from your hand to give attached "
                                                          "unit +X ATK for that attack.",
                                   "Wargear, Weapon.", 1, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", extra_attack=1),
        CardClasses.SupportCard("Corsair Trading Port", "Limited.\n"
                                                        "Interrupt: When you deploy an Eldar unit, "
                                                        "exhaust this support to reduce that "
                                                        "unit's cost by 1.",
                                "Location.", 1, faction, "Common", True,
                                applies_discounts=[True, 1, True],
                                is_faction_limited_unique_discounter=True, limited=True),
        CardClasses.SupportCard("Craftworld Gate", "Action: Exhaust this support to return a target "
                                                   "army unit you control to your hand.",
                                "Location.", 1, faction, "Loyal", False,
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Autarch Celachia", "Action: Pay 1 to give this unit one of the following keywords"
                                                 " until the end of the round (choose one): Area Effect (1), "
                                                 "Armorbane, or Mobile. (Limit once per round.)",
                             "Warrior. Autarch. Ulthwe.", 4, faction, "Loyal", 3, 3, 1, True,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Subdual", "Action: Place a target support card or "
                                         "attachment on top of its owner's deck.",
                              "Power.", 2, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Nightshade Interceptor", "Flying.\n"
                                                       "No Wargear Attachments.\n"
                                                       "While you control a non-Eldar warlord, "
                                                       "this unit gains Area Effect (2).", "Vehicle. Elite.",
                             6, faction, "Common", 4, 4, 2, False),
        CardClasses.ArmyCard("Vaulting Harlequin", "Combat Action: Exhaust this unit to have it gain "
                                                   "Flying until the end of the phase.", "Warrior. Harlequin.",
                             3, faction, "Common", 1, 4, 2, False,
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.EventCard("Empower", "Play only during a battle.\n"
                                         "Combat Action: Each Eldar unit you control at a target planet "
                                         "gets +1 ATK and +1HP until the end of the battle.", "Power.",
                              3, faction, "Loyal", 2, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Starcannon", "Attach to an Eldar Vehicle unit.\n"
                                                 "Attached unit gains Armorbane.", "Hardpoint. Weapon.",
                                   0, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army",
                                   unit_must_match_faction=True, required_traits="Vehicle"),
        CardClasses.ArmyCard("Black Guardians", "", "Warrior. Ulthwe.", 2, faction, "Common", 2, 4, 0, False),
        CardClasses.EventCard("Death from Above", "Deploy Action: Put a non-Elite mobile unit into play "
                                                  "from your hand at the last planet.", "Tactic.",
                              1, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.SupportCard("Dome of Crystal Seers", "Interrupt: When you search your deck, search "
                                                         "an additional 3 cards.", "Location.",
                                1, faction, "Loyal", False),
        CardClasses.ArmyCard("Warlock Destructor", "FORCED REACTION: After the deploy phase begins, pay 1 Resource"
                                                   " or discard this unit.", "Psyker.",
                             2, faction, "Common", 3, 4, 1, False),
        CardClasses.ArmyCard("Eldritch Corsair", "This unit gets +2 ATK while it is at a planet with a warlord.",
                             "Warrior. Iyanden.", 3, faction, "Common", 2, 3, 1, False),
        CardClasses.EventCard("Foretell", "Interrupt: When a Battle ability triggers, exhaust your warlord to cancel "
                                          "its effects. Then, draw 1 card.", "Power. Maneuver.",
                              0, faction, "Common", 1, False),
        CardClasses.ArmyCard("Vectored Vyper Squad", "No Wargear Attachments.\n"
                                                     "This unit gains Mobile while it is undamaged.",
                             "Vehicle. Alaitoc.", 4, faction, "Loyal", 3, 3, 1, False,
                             wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("Guardian Mesh Armor", "Attach to an Eldar army unit.\n"
                                                          "Interrupt: When you use a shield card to prevent damage "
                                                          "to attached unit, exhaust this attachment to double "
                                                          "the nunber of shields on that card.",
                                   "Wargear. Armor.", 1, faction, "Common", 1, False,
                                   unit_must_match_faction=True, type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Mighty Wraithknight", "No Wargear Attachments.\n"
                                                    "Reaction: After this unit enters play, exhaust each non-Spirit"
                                                    " unit at this planet.", "Vehicle. Spirit. Elite.",
                             6, faction, "Common", 5, 5, 2, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Seer's Exodus", "Action: Move 1 or more units you control at a "
                                               "planet with your warlord to your HQ.", "Power.",
                              0, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.SupportCard("Slumbering Gardens", "Interrupt: When an effect would move a unit you control "
                                                      "from a planet, exhaust this support to cancel that effect.",
                                "Location.", 1, faction, "Common", False),
        CardClasses.WarlordCard("Baharroth", "Mobile.", "Warrior. Phoenix Lord.",
                                faction, 2, 6, 1, 5, "Bloodied.", 7, 7,
                                ["4x Baharroth's Hawks", "1x Banner of the Ashen Sky",
                                 "2x Cry of the Wind", "1x The Shining Blade"], mobile=True),
        CardClasses.ArmyCard("Baharroth's Hawks", "Mobile.\n"
                                                  "This unit gets +3 ATK while it is at a planet with your warlord.",
                             "Warrior.", 3, faction, "Signature", 0, 2, 2, False, mobile=True),
        CardClasses.SupportCard("Banner of the Ashen Sky", "Reaction: After a unit moves from one planet to another, "
                                                           "exhaust this support to give that unit "
                                                           "+2 ATK for its next attack this phase.", "Upgrade.",
                                1, faction, "Signature", False),
        CardClasses.AttachmentCard("The Shining Blade", "Attach to a mobile unit.\n"
                                                        "Interrupt: When attached unit declares an attack, "
                                                        "declare that attack against an enemy unit at an "
                                                        "adjacent planet instead.", "Relic. Wargear.",
                                   1, faction, "Signature", 3, True),
        CardClasses.EventCard("Cry of the Wind", "Reaction: After a unit moves from one planet to another,"
                                                 " move that unit to an adjacent planet.",
                              "Tactic.", 0, faction, "Signature", 1, False),
        CardClasses.ArmyCard("Prophetic Farseer", "Reaction: After you deploy this unit, "
                                                  "look at the top 3 cards of your opponent's deck. "
                                                  "Discard any number of those cards with 1 or more shield icons"
                                                  " and place the remaining cards on top of his deck in any order.",
                             "Psyker. Saim-Hann.", 3, faction, "Common", 2, 4, 1, False),
        CardClasses.ArmyCard("Wraithguard Revenant", "Interrupt: When you win a command struggle at a "
                                                     "Stronghold planet (green), put this unit into play from your"
                                                     " discard pile or hand at that planet instead of taking the "
                                                     "planet's card and resource bonuses.", "Drone. Spirit.",
                             2, faction, "Common", 3, 2, 0, False),
        CardClasses.SupportCard("Deathly Web Shrine", "Combat Action: After you move a unit you control from one "
                                                      "planet to another, exhaust this support to exhaust a non-Elite "
                                                      "army unit at the same planet as the unit just moved.",
                                "Location.", 2, faction, "Loyal", True),
        CardClasses.ArmyCard("Dire Avenger Exarch", "A Warrior unit you control at this planet must be declared "
                                                    "as a defender, if able.", "Warrior.",
                             3, faction, "Loyal", 2, 4, 1, False),
        CardClasses.EventCard("Mind War", "Action: Exhaust a target non-Elite army unit at"
                                          " a planet with a Psyker army unit you control.", "Power.",
                              1, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Fire Prism", "No Wargear Attachments.\n"
                                           "Ranged.\n"
                                           "Reaction: After this unit damages an army unit by an attack, exhaust a "
                                           "target enemy army unit at this planet.", "Vehicle. Tank. Elite.",
                             6, faction, "Loyal", 3, 7, 3, False, wargear_attachments_permitted=False, ranged=True),
        CardClasses.AttachmentCard("Saim-Hann Jetbike", "Attach to an army unit you control.\n"
                                                        "Limit 1 per unit.\n"
                                                        "Combat Action: Exhaust this attachment to move attached"
                                                        " unit to a planet with a type shared with this planet. "
                                                        "Then, deal 1 damage to an army unit at this planet.",
                                   "Wargear. Vehicle. Saim-Hann.", 2, faction, "Loyal", 2, False,
                                   must_be_own_unit=True, type_of_units_allowed_for_attachment="Army",
                                   limit_one_per_unit=1, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Wildrider Vyper", "No Wargear Attachments.\n"
                                                "Mobile.\n"
                                                "Reaction: After another unit moves from this planet to "
                                                "another planet, move this unit to that planet.",
                             "Vehicle. Saim-Hann. Elite.", 5, faction, "Common", 5, 4, 2, False, mobile=True),
        CardClasses.SupportCard("Bonesinger Choir", "Limited.\n"
                                                    "Interrupt: When you deploy an Vehicle or Drone unit, "
                                                    "exhaust this support to reduce"
                                                    " its cost by 2 (to a minimum of 1).", "Upgrade.",
                                2, faction, "Common", False, limited=True,
                                applies_discounts=[True, 2, True]),
        CardClasses.ArmyCard("Saim-Hann Kinsman", "While this unit is at a Stronghold planet (green) "
                                                  "it gets +1 ATK and +1 HP.", "Scout. Saim-Hann. Ally.",
                             1, faction, "Common", 1, 1, 1, False),
        CardClasses.EventCard("Eldritch Storm", "Combat Action: Target up to 1 enemy unit at each Stronghold planet"
                                                " (green). Deal 2 damage to each targeted unit.", "Power.",
                              2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Shuriken Catapult", "Ambush.\n"
                                                        "Attach to a Warrior army unit.\n"
                                                        "Attached unit gets +3 ATK.", "Wargear. Weapon.",
                                   2, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT",
                                   ambush=True, extra_attack=3, type_of_units_allowed_for_attachment="Army",
                                   required_traits="Warrior"),
        CardClasses.WarlordCard("Talyesin Fharenal", "Each unit you control at this planet with the"
                                                     " Psyker or Warrior trait gets +1 HP.\n"
                                                     "While you control a Psyker unit and a Warrior unit at this "
                                                     "planet, each unit you control at this planet with the"
                                                     " Psyker or Warrior trait gets +1 ATK.\n", "Autarch. Saim-Hann.",
                                faction, 2, 6, 2, 5, "Bloodied.", 7, 7,
                                ["2x Talyesin's Spiders", "2x Talyesin's Warlocks", "1x Wisdom of the Serpent",
                                 "2x Path of the Leader", "1x Autarch Powersword"]),
        CardClasses.ArmyCard("Talyesin's Spiders", "Reaction: After a Psyker unit you control is declared as an "
                                                   "attacker, move this unit to the same planet as that unit.",
                             "Warrior. Saim-Hann.", 2, faction, "Signature", 2, 3, 1, False),
        CardClasses.ArmyCard("Talyesin's Warlocks", "Combat Action: Discard a Warrior card from your hand to ready "
                                                    "this unit. (Limit once per combat round.)", "Psyker. Saim-Hann.",
                             3, faction, "Signature", 3, 2, 1, False,
                             action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Wisdom of the Serpent", "HEADQUARTERS ACTION: Exhaust this support to choose"
                                                         " Psyker or Warrior. Then, search the top 3 cards of your "
                                                         "deck for a unit with the chosen Trait. Reveal it, add it "
                                                         "to your hand, and place the remaining cards on the bottom"
                                                         " of your deck in any order.", "Upgrade.",
                                1, faction, "Signature", False,
                                action_in_play=True, allowed_phases_in_play="HEADQUARTERS"),
        CardClasses.EventCard("Path of the Leader", "Action: Either (choose one): gain 1 resource, have a Warrior unit"
                                                    " you control get +1 ATK until the end of the phase, "
                                                    "or exhaust a Psyker unit you control to move it "
                                                    "from one planet to another.", "Tactic.",
                              0, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Autarch Powersword", "Attach to a unit you control.\n"
                                                         "Attached unit gets +1 ATK and +1 HP.\n"
                                                         "If attached unit is an army unit, "
                                                         "it gains the Warrior and Psyker traits.", "Wargear. Weapon.",
                                   1, faction, "Signature", 3, False, extra_attack=1, extra_health=1,
                                   must_be_own_unit=True),
        CardClasses.ArmyCard("Seer Adept", "Reaction: After the command phase begins, "
                                           "look at a target card your opponent controls in reserve.", "Psyker.",
                             3, faction, "Common", 2, 4, 1, False),
        CardClasses.ArmyCard("Furious Wraithblade", "Reaction: After this unit resolves an attack, ready it. "
                                                    "(Limit once per phase.)", "Drone. Spirit.",
                             3, faction, "Common", 3, 3, 0, False),
        CardClasses.AttachmentCard("Hidden Strike Chainsword", "Deep Strike (0).\n"
                                                               "Attach to an army unit you control.\n"
                                                               "While attacking a non-Warlord unit, "
                                                               "attached unit gets +2 ATK.", "Wargear. Weapon.",
                                   1, faction, "Common", 1, False, deepstrike=0,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.ArmyCard("Adherent Outcast", "Each Elite unit you control at this planet gains Flying.",
                             "Scout.", 2, faction, "Common", 1, 3, 0, False),
        CardClasses.EventCard("Concealing Darkness", "Deep Strike (1).\n"
                                                     "Reaction: After you Deep Strike this event, you may deploy "
                                                     "each unit in your hand at this planet as though it had "
                                                     "Ambush until the end of the phase.", "Power.",
                              0, faction, "Common", 1, False, deepstrike=1),
        CardClasses.ArmyCard("War Walker Squadron", "No Wargear Attachments.\n"
                                                    "Reaction: After this unit is chosen as a defender, "
                                                    "exhaust a Hardpoint attachment on it to cancel that attack.",
                             "Vehicle. Elite.", 5, faction, "Common", 4, 3, 1, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Phoenix Attack Fighter", "Flying. No Wargear Attachments.\n"
                                                       "Reaction: After units are committed to this planet, deal 3 "
                                                       "damage to an exhausted enemy unit at this planet.",
                             "Vehicle. Elite.", 6, faction, "Loyal", 2, 6, 1, False,
                             wargear_attachments_permitted=False, flying=True),
        CardClasses.SupportCard("Webway Passage", "Deploy Action: Exhaust this support to switch the locations of "
                                                  "two target army units you control.", "Upgrade.",
                                1, faction, "Loyal", False, action_in_play=True, allowed_phases_in_play="DEPLOY"),
        CardClasses.ArmyCard("Shrieking Exarch", "Reaction: After an army unit is destroyed at this planet, "
                                                 "draw 1 card and deal 1 damage to a target enemy unit.",
                             "Warrior. Elite.", 5, faction, "Common", 4, 6, 2, False),
        CardClasses.AttachmentCard("Ulthwe Spirit Stone", "Attach to an army unit you control\n"
                                                          ".Interrupt: When attached unit would be destroyed, "
                                                          "return it to your hand instead.", "Wargear. Ulthwe.",
                                   0, faction, "Common", 1, False, unit_must_match_faction=True,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.WarlordCard("Jain Zar", "Interrupt: When your opponent targets a unit you control at this planet "
                                            "with a triggered effect, cancel that effect. (Limit once per round.)",
                                "Phoenix Lord. Warrior.", faction, 2, 6, 1, 6, "Bloodied.", 7, 7,
                                ["4x Banshee Assault Squad", "1x Intercept",
                                 "2x Storm of Silence", "1x The Mask of Jain Zar"]),
        CardClasses.ArmyCard("Banshee Assault Squad", "Reaction: After you cancel a card effect, put this unit into "
                                                      "play from you hand at a planet.", "Warrior.",
                             2, faction, "Signature", 2, 2, 1, False),
        CardClasses.SupportCard("Intercept", "Reaction: After your opponent targets a single unit with a card effect, "
                                             "exhaust this support to change the target of that effect to "
                                             "a target unit you control (ignoring targeting restrictions).",
                                "Upgrade.", 2, faction, "Signature", False),
        CardClasses.EventCard("Storm of Silence", "Interrupt: When a card effect targets a unit, cancel that effect. "
                                                  "If the targeted unit was a unit you control, ready your warlord.",
                              "Power.", 2, faction, "Signature", 1, False),
        CardClasses.AttachmentCard("The Mask of Jain Zar", "Attach to your warlord.\n"
                                                           "After an enemy unit at this planet triggers an ability, "
                                                           "deal 1 damage to that unit.", "Wargear. Relic.",
                                   1, faction, "Signature", 3, True, must_be_own_unit=True,
                                   type_of_units_allowed_for_attachment="Warlord"),
        CardClasses.ArmyCard("Scorpion Striker", "Deep Strike (2).\n"
                                                 "Reaction: After you Deep Strike this unit, exhaust a target "
                                                 "non-Elite army unit at this planet.", "Warrior.",
                             4, faction, "Common", 3, 3, 1, False, deepstrike=1),
        CardClasses.EventCard("Piercing Wail", "Deploy Action: Exhaust up to 2 units each with printed cost X or lower."
                                               " X is equal to the highest printed cost among units you control.",
                              "Power.", 4, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.ArmyCard("Evanescent Players", "Deep Strike (1).\n"
                                                   "Interrupt: When this unit is assigned damage by an enemy army unit,"
                                                   " prevent all but 2 of that damage. Then deal damage to that unit"
                                                   " damage equal to the damage prevented. (Limit once per phase.)",
                             "Psyker. Harlequin.", 2, faction, "Loyal", 2, 2, 1, False, deepstrike=1),
        CardClasses.AttachmentCard("Warhost Helmet", "Attach to a Saim-Hann unit. Limit 1 per unit.\n"
                                                     "Attached unit gets +2 HP.\n"
                                                     "Reaction: After attached unit is assigned damage, exhaust it"
                                                     " and this attachment to prevent all of that damage. "
                                                     "Then attached unit gets +1 ATK for its next attack this phase.",
                                   "Wargear.", 0, faction, "Loyal", 2, False, limit_one_per_unit=True,
                                   required_traits="Saim-Hann", extra_health=2,
                                   type_of_units_allowed_for_attachment="Army/Warlord/Synapse/Token"),
        CardClasses.ArmyCard("Phantasmatic Masque", "This unit gets +1 ATK for each remaining HP.\n"
                                                    "Reaction: After an attack against this unit resolves, exhaust "
                                                    "this unit to deal 2 damage to the attacker."
                                                    " (Limit once per phase.)", "Warrior. Harlequin.",
                             2, faction, "Loyal", 0, 3, 1, False),
        CardClasses.ArmyCard("Noble Shining Spears", "Mobile.\n"
                                                     "This unit gets +3 ATK while attacking an undamaged unit.\n"
                                                     "Reaction: After a Mobile unit you control is assigned damage at "
                                                     "this planet, reassign 1 of that damage to this unit.",
                             "Warrior. Hero.", 4, faction, "Common", 3, 4, 2, False, mobile=True),
        CardClasses.AttachmentCard("Close Quarters Doctrine", "Deep Strike (0).\n"
                                                              "Attach to a planet. Limit 1 per planet.\n"
                                                              "Each unit with a printed cost 3 or higher at"
                                                              " this planet gets -1 ATK.\n"
                                                              "Reaction: After a battle end at "
                                                              "this planet, draw a card.", "Tactic.",
                                   1, faction, "Common", 1, False,
                                   deepstrike=0, planet_attachment=True, limit_one_per_unit=True),
        CardClasses.EventCard("The Dance Without End", "Reaction: After a Harlequin unit enters your discard pile "
                                                       "from a planet, return it to your hand to deploy a Harlequin"
                                                       " unit with a different name at the same planet.", "Power.",
                              1, faction, "Loyal", 2, False),
        CardClasses.WarlordCard("Zen Xi Aonia", "Each unit at this planet loses the Area Effect keyword.\n"
                                                "Forced Interrupt: When a unit you control at this planet is chosen as"
                                                " a defender, declare another eligible unit at this planet as the"
                                                " defender instead, if able.", "Shadowseer. Harlequin.",
                                faction, 2, 6, 2, 6, "Bloodied.", 7, 7,
                                ["2x Access to the Black Library", "1x Masters of the Webway", "1x Starmist Raiment",
                                 "1x The Blinded Princess", "1x The Dawnsinger",
                                 "1x The Sun Prince", "1x The Webway Witch"]),
        CardClasses.EventCard("Access to the Black Library", "Deploy Action: Search your deck for 2 cards with a "
                                                             "different name. Reveal them, have your opponent choose "
                                                             "one, add it to your hand, and shuffle the remaining"
                                                             " card in your deck.", "Power.",
                              1, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.SupportCard("Masters of the Webway", "Reaction: After the deploy phase begins, sacrifice this "
                                                         "support to have each player exchange their "
                                                         "command dial value the next time they reveal "
                                                         "their command dial this round.", "Location.",
                                1, faction, "Signature", False),
        CardClasses.AttachmentCard("Starmist Raiment", "Attach to a Harlequin unit you control.\n"
                                                       "Interrupt: When damage is assigned to a Harlequin unit you "
                                                       "control at this planet, exhaust this attachment "
                                                       "to reassign 1 of that damage to another non-warlord "
                                                       "unit at this planet.", "Wargear. Armor.",
                                   1, faction, "Signature", 3, True, required_traits="Harlequin",
                                   type_of_units_allowed_for_attachment="Army/Warlord/Synapse/Token",
                                   must_be_own_unit=True),
        CardClasses.ArmyCard("The Blinded Princess", "Forced Reaction: After this unit enters play, your opponent may "
                                                     "exhaust a unit at a planet to move this unit to that planet.",
                             "Warrior. Harlequin.", 1, faction, "Signature", 3, 3, 1, False),
        CardClasses.ArmyCard("The Dawnsinger", "Reaction: After this unit is destroyed, your opponent must choose to "
                                               "either put 2 cards from his hand on the top of his deck in any "
                                               "order or you draw 2 cards.", "Psyker. Harlequin.",
                             2, faction, "Signature", 2, 3, 1, False),
        CardClasses.ArmyCard("The Sun Prince", "Interrupt: When this unit leaves play, your opponent must choose, at "
                                               "the same planet, either to exhaust a unit he controls "
                                               "or ready a unit you control.", "Warrior. Harlequin.",
                             2, faction, "Signature", 3, 2, 1, False),
        CardClasses.ArmyCard("The Webway Witch", "Reaction: After you deploy this unit, the next time your opponent"
                                                 " deploys a unit this phase, he must deploy it at this planet,"
                                                 " if able.", "Psyker. Harlequin.",
                             2, faction, "Signature", 1, 2, 2, False),
        CardClasses.AttachmentCard("Flickering Holosuit", "Attach to an army unit.\n"
                                                          "Attached unit gets +1 HP.\n"
                                                          "Forced Interrupt: When attaced unit is assigned damage, "
                                                          "exhaust this attachment to prevent 2 of that damage. "
                                                          "If this attachment was already exhausted, ready it instead.",
                                   "Wargear. Armor.", 1, faction, "Common", 1, False, extra_health=1,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.EventCard("Clash of Wings", "Combat Action: Target a planet with your warlord. "
                                                "Until the end of the combat round, each Mobile unit you control at"
                                                " that planet gains Flying.", "Tactic.",
                              1, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.WarlordCard("Farseer Tadheris", "You choose your allied faction as if you were Astra Militarum.\n"
                                                    "Action: Perform a mulligan with your current hand size."
                                                    " (Limit once per round.)", "Psyker. Prophet.", faction,
                                2, 6, 2, 5, "Bloodied.\n"
                                            "Action: Deal 1 damage to this unit to perform a mulligan with your "
                                            "current hand size. (Limit once per game.)", 7, 7,
                                ["2x Back to the Shadows", "4x Elusive Escort",
                                 "1x Singing Spear", "1x Wisdom of Biel-tan"],
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Back to the Shadows", "Interrupt: When an army unit you control is assigned damage, "
                                                     "return it and each attachment you control on it to"
                                                     " your hand. Then draw a card.", "Power.",
                              0, faction, "Signature", 1, False),
        CardClasses.ArmyCard("Elusive Escort", "Reaction: After this unit enters play, draw a card. Then remove from "
                                               "the game facedown a card from your hand. When this unit "
                                               "leaves play, return the facedown card to your hand.",
                             "Scout.", 2, faction, "Signature", 2, 3, 1, False),
        CardClasses.AttachmentCard("Singing Spear", "Attach to an army unit.\n"
                                                    "Attached unit gets +2 ATK and +2 HP.\n"
                                                    "Interrupt: When you perform a mulligan, reveal this card from"
                                                    " your hand to move an army unit you control to the last planet.",
                                   "Wargear.", 0, faction, "Signature", 3, False, extra_health=2, extra_attack=2,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.SupportCard("Wisdom of Biel-tan", "Reaction: After you perform a mulligan, draw a card.",
                                "Doctrine.", 0, faction, "Signature", False),
        CardClasses.ArmyCard("Cegorach's Jesters", "Reaction: After a battle at this planet begins, your opponent may"
                                                   " reveal any number of cards from him hand. He cannot use "
                                                   "unrevealed event or attachment cards as shield cards during "
                                                   "this battle.", "Psyker. Harlequin.",
                             2, faction, "Loyal", 2, 2, 1, False),
        CardClasses.ArmyCard("Luring Troupe", "Reaction: After you deploy this unit, move a target army unit at this "
                                              "planet to an adjacent planet. At the end of next phase, move "
                                              "that unit back to this planet, if able.", "Psyker. Harlequin.",
                             2, faction, "Loyal", 3, 2, 1, False),
        CardClasses.ArmyCard("Scheming Warlock", "Reaction: After you deploy this unit, look at the top 3 cards of "
                                                 "your deck for a card with the Deep Strike keyword. Reveal it, "
                                                 "and add it to your hand. Then, put each remaining card on the "
                                                 "bottom of your deck in any order.", "Psyker.",
                             3, faction, "Loyal", 2, 3, 1, False),
        CardClasses.SupportCard("Wraithbone Armour", "Units you control with a printed ATK of 0 get +1 HP.\n"
                                                     "Combat Action: Exhaust this support to move 1 damage from a targ"
                                                     "et enemy unit at a planet with a unit you control with a printed"
                                                     " ATK of 0 to another unit at the same planet.", "Upgrade.",
                                1, faction, "Loyal", True, action_in_play=True, allowed_phases_in_play="COMBAT")
    ]
    return eldar_cards_array
