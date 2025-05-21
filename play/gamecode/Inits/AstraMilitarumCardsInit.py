from .. import CardClasses


def astra_militarum_cards_init():
    faction = "Astra Militarum"
    astra_militarum_cards_array = [
        CardClasses.WarlordCard("Colonel Straken", "Each other soldier or warrior unit "
                                                   "you control at this planet gets "
                                                   "+1 ATK.", "Soldier. Catachan.",
                                faction, 2, 6, 2, 5,
                                "Bloodied.", 7, 7,
                                ["4x Straken's Command Squad", "2x Glorious Intervention",
                                 "1x Omega Zero Command", "1x Straken's Cunning"]
                                ),
        CardClasses.ArmyCard("Straken's Command Squad", "Interrupt: When this unit leaves "
                                                        "play, put a Guardsman token "
                                                        "into play at the same planet.",
                             "Soldier. Catachan.", 2, faction, "Signature",
                             2, 2, 1, False),
        CardClasses.SupportCard("Omega Zero Command", "Reaction: After you win a command "
                                                      "struggle, put a Guardsman token "
                                                      "into play at that planet.",
                                "Location.", 2, faction, "Signature", False),
        CardClasses.EventCard("Glorious Intervention", "Reaction: After a unit is assigned "
                                                       "damage by an attack, sacrifice a "
                                                       "Soldier or Warrior unit at the same "
                                                       "planet to prevent all of that "
                                                       "damage. Then, deal X damage to the "
                                                       "attacker. X is the sacrificed "
                                                       "unit's printed ATK value.",
                              "Tactic.", 1, faction, "Signature", 1, False),
        CardClasses.AttachmentCard("Straken's Cunning", "Attach to an army unit.\n"
                                                        "Attached unit gets +1 ATK.\n"
                                                        "Interrupt: When attached unit "
                                                        "leaves play, draw 3 cards.",
                                   "Skill.", 1, faction, "Signature", 3, False,
                                   type_of_units_allowed_for_attachment="Army",
                                   extra_attack=1),
        CardClasses.ArmyCard("Ratling Deadeye", "Ranged. (This unit attacks during the "
                                                "ranged skirmish at the beginning of"
                                                " a battle.)", "Scout. Abhuman.", 1,
                             faction, "Common", 1, 1, 1, False, ranged=True),
        CardClasses.ArmyCard("Cadian Mortar Squad", "Ranged. (This unit attacks during the "
                                                    "ranged skirmish at the beginning of"
                                                    " a battle.)\n"
                                                    "Reaction: After an army unit you "
                                                    "control at this planet leaves play, "
                                                    "ready this unit.", "Soldier. Cadia.",
                             3, faction, "Loyal", 1, 3, 2, False, ranged=True),
        CardClasses.ArmyCard("Sanctioned Psyker", "", "Psyker.", 2, faction, "Common",
                             0, 4, 2, False),
        CardClasses.ArmyCard("Leman Russ Battle Tank", "No Wargear Attachments.",
                             "Vehicle. Tank. Elite.", 5, faction, "Loyal",
                             4, 6, 4, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Mordian Hellhound", "No Wargear Attachments.\n"
                                                  "Area Effect (1). (When this unit "
                                                  "attacks it may instead deal its "
                                                  "Area Effect damage to each enemy "
                                                  "unit at this planet.",
                             "Vehicle. Tank. Mordian.", 4, faction, "Common",
                             3, 3, 2, False, area_effect=1,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Assault Valkyrie", "No Wargear Attachments.\n Flying. (This "
                                                 "unit takes half damage from non-Flying "
                                                 "units.", "Vehicle. Transport.",
                             4, faction, "Common", 4, 4, 1, False,
                             wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Stalwart Ogryn", "Immune to enemy events.",
                             "Warrior. Abhuman.", 2, faction, "Common",
                             2, 2, 1, False),
        CardClasses.ArmyCard("Captain Markis", "Action: Sacrifice an Astra Militarum unit "
                                               "at this planet to exhaust a target "
                                               "non-warlord unit at this planet. "
                                               "(Limit once per phase.)",
                             "Soldier. Officer. Vostroya.",
                             3, faction, "Loyal", 2, 3, 2, True,
                             action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Enginseer Augur", "Interrupt: When this unit leaves play, "
                                                "search the top 6 cards of your deck for "
                                                "an Astra Militarum support card with "
                                                "printed cost 2 or lower. Put that card "
                                                "into play at your HQ, and place the "
                                                "remaining cards on the bottom of your deck "
                                                "in any order.", "Scholar. Tech-Priest.",
                             2, faction, "Common", 2, 2, 0, False),
        CardClasses.ArmyCard("Penal Legionnaire", "", "Conscript. Ally.",
                             0, faction, "Common", 1, 1, 0, False),
        CardClasses.ArmyCard("Infantry Conscripts", "This unit gets +2 ATK for each "
                                                    "support you control.", "Conscript.",
                             4, faction, "Common", 0, 5, 0, False),
        CardClasses.ArmyCard("Elysian Assault Team", "Interrupt: When a Soldier or Warrior "
                                                     "unit you control leaves play from a "
                                                     "planet, put this unit into play "
                                                     "from your hand at the same planet.",
                             "Soldier. Elysia.", 2, faction, "Common", 2, 1, 0, False),
        CardClasses.EventCard("Preemptive Barrage", "Combat Action: Target up to 3 Astra "
                                                    "Militarum units you control at the "
                                                    "same planet. Each targeted unit gains "
                                                    "Ranged until the end of the phase. "
                                                    "(Units with Ranged attack during the "
                                                    "ranged skirmish at the beginning "
                                                    "of the battle.)", "Tactic.", 1,
                              faction, "Loyal", 2, False, action_in_hand=True,
                              allowed_phases_in_hand="COMBAT"),
        CardClasses.EventCard("Suppressive Fire", "Combat Action: Exhaust a unit you "
                                                  "control to exhaust a target non-warlord "
                                                  "unit at the same planet.", "Tactic.",
                              0, faction, "Common", 1, False, action_in_hand=True,
                              allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Hostile Environment Gear", "Attach to an army unit.\n"
                                                               "Attached unit gets +3 HP.",
                                   "Wargear. Armor.", 1, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army",
                                   extra_health=3),
        CardClasses.AttachmentCard("Bodyguard", "Attach to an army unit you control.\n"
                                                "Forced Reaction: After a unit you control "
                                                "is assigned damage by an attack at this "
                                                "planet, reassign 1 of that damage to "
                                                "attached unit.", "Condition.", 0,
                                   faction, "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army",
                                   must_be_own_unit=True),
        CardClasses.SupportCard("Imperial Bunker", "Limited. (Limit one Limited card "
                                                   "per round.)\n"
                                                   "Interrupt: When you deploy an Astra "
                                                   "Militarum unit, exhaust this support "
                                                   "to reduce that unit's cost by 1.",
                                "Location.", 1, faction, "Common", True,
                                applies_discounts=[True, 1, True],
                                is_faction_limited_unique_discounter=True, limited=True),
        CardClasses.SupportCard("Rockcrete Bunker", "If this card has 4 or more damage on "
                                                    "it, sacrifice it.\n"
                                                    "Reaction: After damage is assigned to "
                                                    "a unit you control, exhaust this "
                                                    "support to reassign 1 of that damage "
                                                    "to this support.", "Upgrade.", 1,
                                faction, "Common", False),
        CardClasses.SupportCard("Catachan Outpost", "Combat Action: Exhaust this support to "
                                                    "give a target unit +2 ATK for its "
                                                    "next attack this phase.", "Location.",
                                2, faction, "Common", False, action_in_play=True,
                                allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Seraphim Superior Allegra", "Reaction: After this unit is "
                                                          "declared as an attacker, ready a "
                                                          "target support card you control.",
                             "Ecclesiarchy. Soldier.", 4, faction, "Loyal", 3, 4, 2, True),
        CardClasses.SupportCard("Holy Fusillade", "Reaction: After a combat round begins, "
                                                  "exhaust this support to resolve a "
                                                  "ranged skirmish at this battle.",
                                "Upgrade. Ecclesiarchy.", 1, faction, "Common", False),
        CardClasses.ArmyCard("Standard Bearer", "While you control a non-Astra Militarum warlord, you may deploy this "
                                                "unit from your hand as if it had Ambush.\n"
                                                "Reaction: After this unit enters play, ready an army "
                                                "unit you control at this planet.", "Soldier.",
                             3, faction, "Common", 2, 2, 1, False, action_in_hand=True,
                             allowed_phases_in_hand="COMBAT", ambush=True),
        CardClasses.ArmyCard("Interrogator Acolyte", "Interrupt: When this unit leaves play, draw 2 cards.",
                             "Soldier. Inquisitor.", 3, faction, "Loyal", 2, 2, 1, False),
        CardClasses.EventCard("Muster the Guard", "Deploy Action: Exhaust your warlord to reduce the cost of "
                                                  "each Astra Militarum unit you deploy this phase by 1.",
                              "Tactic. Maneuver.", 0, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.EventCard("Noble Deed", "Action: Sacrifice an Astra Militarum unit to deal damage equal to its "
                                            "printed ATK value to a target enemy army unit at the same planet.",
                              "Tactic.", 1, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Iron Guard Recruits", "", "Conscript. Mordian.",
                             2, faction, "Common", 1, 2, 2, False),
        CardClasses.AttachmentCard("Dozer Blade", "Attached to a vehicle army unit.\n"
                                                  "Attached unit gets +2 HP.", "Hardpoint.",
                                   0, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", required_traits="Vehicle",
                                   extra_health=2),
        CardClasses.SupportCard("Inquisitorial Fortress", "Action: Exhaust and sacrifice this support "
                                                          "to rout a target army unit.", "Location.",
                                2, faction, "Loyal", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Mystic Warden", "FORCED REACTION: After a battle at this planet ends, "
                                              "sacrifice this unit.", "Psyker.",
                             0, faction, "Common", 2, 2, 0, False),
        CardClasses.EventCard("To Arms!", "Action: Ready a target support card.", "Tactic.",
                              0, faction, "Loyal", 2, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Honorifica Imperialis", "Attach to an army unit.\n"
                                                            "While at a planet with an enemy warlord attached unit "
                                                            "gains Armorbane and Ranged.", "Wargear. Award.",
                                   2, faction, "Loyal", 2, False,
                                   type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Steel Legion Chimera", "No Wargear Attachments.\n"
                                                     "Reaction: After a non-Vehicle unit you control at this "
                                                     "planet is assigned damage by an attack, prevent 1 of "
                                                     "that damage.", "Vehicle. Transport.",
                             3, faction, "Common", 2, 4, 1, False, wargear_attachments_permitted=False),
        CardClasses.ArmyCard("Tallarn Raiders", "This unit gets +2 ATK while it is at a planet with a warlord.",
                             "Soldier. Tallarn.", 1, faction, "Common", 0, 2, 1, False),
        CardClasses.SupportCard("Staging Ground", "Action: Exhaust this support to deploy a unit"
                                                  " with printed cost 2 or lower at a planet",
                                "Location.", 1, faction, "Common", False,
                                action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.WarlordCard("Torquemada Coteaz", "Combat Action: Sacrifice a unit at this planet to give "
                                                     "this warlord +3 ATK for its next attack this phase. "
                                                     "(Limit once per attack).", "Soldier. Inquisitor.",
                                faction, 0, 8, 1, 6,
                                "Bloodied.", 8, 8,
                                ["4x Coteaz's Henchmen", "2x The Emperor Protects",
                                 "1x Formosan Black Ship", "1x The Glovodan Eagle"],
                                action_in_play=True, allowed_phases_in_play="COMBAT"
                                ),
        CardClasses.ArmyCard("Coteaz's Henchmen", "Interrupt: When this unit leaves play, ready your warlord",
                             "Soldier.", 2, faction, "Signature", 1, 3, 1, False),
        CardClasses.SupportCard("Formosan Black Ship", "Interrupt: When you sacrifice a non-token unit, exhaust "
                                                       "this support to put 2 Guardsman tokens into play at the "
                                                       "same planet as the sacrificed unit.", "Upgrade.",
                                1, faction, "Signature", False),
        CardClasses.AttachmentCard("The Glovodan Eagle", "Attach to your warlord.\n"
                                                         "Attached warlord gets +1 ATK.\n"
                                                         "Combat Action: Detach this card to have it become an army "
                                                         "unit with 1 ATK and 1 HP and the text: "
                                                         "“Action: Return this unit to your hand.”", "Familiar.",
                                   1, faction, "Signature", 3, True, action_in_play=True,
                                   allowed_phases_in_play="COMBAT", type_of_units_allowed_for_attachment="Warlord",
                                   must_be_own_unit=True, extra_attack=1),
        CardClasses.EventCard("The Emperor Protects", "Interrupt: When a unit you control leaves play from a "
                                                      "planet with your warlord, return that unit to your "
                                                      "hand instead.", "Tactic.",
                              0, faction, "Signature", 1, False),
        CardClasses.ArmyCard("Shrieking Basilisk", "No Wargear Attachments.\n"
                                                   "Ranged.\n"
                                                   "Reaction: After this unit damages an enemy unit, "
                                                   "exhaust a target support card.", "Vehicle. Artillery. Elite.",
                             6, faction, "Common", 3, 5, 3, False, wargear_attachments_permitted=False, ranged=True),
        CardClasses.EventCard("The Emperor's Warrant", "Combat Action: Exhaust a target enemy unit at a planet "
                                                       "without an enemy warlord. Then, deal damage equal to "
                                                       "that unit's ATK value to another target unit at that planet.",
                              "Tactic.", 2, faction, "Loyal", 2, False, action_in_hand=True,
                              allowed_phases_in_hand="COMBAT"),
        CardClasses.WarlordCard("Broderick Worr", "Army units that retreat from this planet are destroyed instead.\n"
                                                  "Each other Astra Militarum unit you control at a "
                                                  "Stronghold planet (green)"
                                                  " gets +1 ATK and gains, “Cannot retreat or be routed.”",
                                "Soldier. Commissar.", faction, 2, 6, 2, 5, "Bloodied.", 7, 7,
                                ["4x Anxious Infantry Platoon", "2x Summary Execution",
                                 "1x Forward Barracks", "1x Commissarial Bolt Pistol"]
                                ),
        CardClasses.ArmyCard("Anxious Infantry Platoon", "FORCED REACTION: After a combat round at this planet ends, "
                                                         "you may pay 1 resource. If you do not, retreat this unit.",
                             "Soldier.", 2, faction, "Signature", 3, 3, 1, False),
        CardClasses.SupportCard("Forward Barracks", "Reaction: After a combat round ends, if you control an "
                                                    "Astra Militarum unit at the planet where the battle is taking "
                                                    "place, put 1 Guardsman token into play at that planet.",
                                "Location.", 2, faction, "Signature", False),
        CardClasses.EventCard("Summary Execution", "Play only during a battle.\n"
                                                   "Combat Action: Sacrifice a unit at a planet with your warlord "
                                                   "to have that planet gain a Stronghold icon (green) until the "
                                                   "end of the battle. Then, draw 1 card.", "Tactic.",
                              1, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Commissarial Bolt Pistol", "Attach to a Commissar unit.\n"
                                                               "Attached unit gets +1 ATK.\n"
                                                               "Reaction: After an army unit you control at this "
                                                               "planet leaves play, deal 1 damage to a target army "
                                                               "unit at this planet.", "Wargear. Weapon.",
                                   1, faction, "Signature", 3, False, extra_attack=1, required_traits="Commissar"),
        CardClasses.ArmyCard("Sacaellum Shrine Guard", "While this unit is at a Stronghold planet (green) it gets"
                                                       " +1 ATK and +1 HP.", "Soldier. Sacaellum. Ally.",
                             1, faction, "Common", 1, 1, 1, False),
        CardClasses.SupportCard("Troop Transport", "Limited.\n"
                                                   "Action: Sacrifice this support to either put a Guardsman "
                                                   "token into play at a planet, or put 2 Guardsman tokens into "
                                                   "play at a Stronghold planet (green).", "Upgrade.",
                                0, faction, "Loyal", False, limited=True),
        CardClasses.ArmyCard("Death Korps Engineers", "Action: Sacrifice this unit to destroy a "
                                                      "target exhausted support card.", "Soldier. Krieg.",
                             2, faction, "Common", 2, 3, 0, False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.ArmyCard("Vanguard Soldiers", "Interrupt: When this unit leaves play, "
                                                  "ready another target army unit you control.", "Soldier. Sacaellum.",
                             3, faction, "Loyal", 3, 3, 1, False),
        CardClasses.EventCard("Inspirational Fervor", "Reaction: After you win a battle at a "
                                                      "Stronghold planet (green), move up to 2 non-warlord units"
                                                      " you control at that planet to a target planet.", "Tactic.",
                              1, faction, "Common", 1, False),
        CardClasses.ArmyCard("Taurox APC", "No Wargear Attachments.\n"
                                           "Reaction: After a combat round at a Stronghold planet (green) ends, "
                                           "move this unit to that planet.", "Vehicle. Transport.",
                             2, faction, "Common", 2, 2, 1, False, wargear_attachments_permitted=False),
        CardClasses.AttachmentCard("M35 Galaxy Lasgun", "Attach to a non-warlord unit.\n"
                                                        "Attached unit gets +1 ATK and +1 HP.\n"
                                                        "Interrupt: When attached unit leaves play, return this "
                                                        "attachment to your hand.", "Wargear. Weapon.",
                                   1, faction, "Common", 1, False, extra_attack=1, extra_health=1,
                                   type_of_units_allowed_for_attachment="Army/Token/Synapse"),
        CardClasses.ArmyCard("Sacaellum's Finest", "Reaction: After you win a battle at a non-first Stronghold planet"
                                                   " (green), instead of triggering the planet's Battle ability, "
                                                   "put this unit into play from your hand at a Stronghold planet"
                                                   " (green).", "Soldier. Sacaellum.",
                             4, faction, "Loyal", 3, 4, 2, False),
        CardClasses.SupportCard("Cathedral of Saint Camila", "Combat Action: Exhaust this support to target up to 1 "
                                                             "non-Elite enemy army unit at each Stronghold planet"
                                                             " (green). Exhaust each targeted unit. "
                                                             "(Limit once per phase.)", "Location. Ecclesiarchy.",
                                3, faction, "Loyal", True, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Leman Russ Conqueror", "No Wargear Attachments.\n"
                                                     "Reaction: After this unit resolves an attack, it gets +3 ATK "
                                                     "until the end of the phase.", "Vehicle. Tank. Elite.",
                             6, faction, "Common", 3, 7, 3, False, wargear_attachments_permitted=False),
        CardClasses.EventCard("Bolster the Defense", "Combat Action: Put a support card into play from your hand with"
                                                     " printed cost equal to or lower than the highest"
                                                     " number of army unit you control at a planet.", "Tactic.",
                              0, faction, "Loyal", 2, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Imperial Rally Point", "Attach to a Stronghold planet (green).\n"
                                                           "Reduce the cost of each Astra Militarum unit you deploy "
                                                           "at this planet by 1 (to a minimum of 1).", "Location.",
                                   1, faction, "Common", 1, False, planet_attachment=True)
    ]
    return astra_militarum_cards_array
