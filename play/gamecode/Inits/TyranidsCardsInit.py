from .. import CardClasses


def tyranids_cards_init():
    faction = "Tyranids"
    tyranids_card_array = [
        CardClasses.WarlordCard("Old One Eye", "Reaction: After this warlord readies, remove half the damage from "
                                               "it. (Limit once per round.)", "Creature. Behemoth.",
                                faction, 2, 6, 1, 6, "Bloodied.", 6, 6,
                                ["4x Lurking Hormagaunt", "1x Awakening Cavern", "2x Ferocious Strength",
                                 "1x Great Scything Talons"]),
        CardClasses.ArmyCard("Lurking Hormagaunt", "Reaction: After this unit is assigned damage, reassign up to 2 of "
                                                   "that damage to your warlord instead.", "Creature. Behemoth.",
                             2, faction, "Signature", 3, 1, 1, False),
        CardClasses.SupportCard("Awakening Cavern", "Action: Exhaust this support to ready a target unit you control.",
                                "Location.", 3, faction, "Signature", False, action_in_play=True,
                                allowed_phases_in_play="ALL"),
        CardClasses.EventCard("Ferocious Strength", "Action: Your warlord or a synapse unit you control gains Brutal "
                                                    "until the end of the combat round.", "Power.",
                              1, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.AttachmentCard("Great Scything Talons", "Attach to your warlord.\n"
                                                            "Attached unit gets +1 HP.\n"
                                                            "Reaction: After damage is removed from attached unit, it "
                                                            "gets +X ATK for its next attack this phase. "
                                                            "X is the amount of damage removed.", "Wargear. Biomorph.",
                                   1, faction, "Signature", 3, False,
                                   type_of_units_allowed_for_attachment="Warlord", extra_health=1),
        CardClasses.WarlordCard("The Swarmlord", "Reaction: After this warlord commits to a planet, put 1 Termagant"
                                                 " token into play at each adjacent planet.", "Creature. Behemoth.",
                                faction, 2, 6, 2, 5, "Bloodied.", 6, 6,
                                ["4x Brood Warriors", "1x Leviathan Hive Ship", "2x Indescribable Horror",
                                 "1x Bone Sabres"]),
        CardClasses.ArmyCard("Brood Warriors", "HIVE MIND - Each Termagant token you control at this planet "
                                               "gains 1 command icon.", "Creature. Leviathan.", 2, faction,
                             "Signature", 2, 2, 1, False, hive_mind=True),
        CardClasses.SupportCard("Leviathan Hive Ship", "Reaction: After a unit you control with the Hive Mind "
                                                       "specialization and printed cost 3 or lower is destroyed, "
                                                       "exhaust this support to put that unit into play from your "
                                                       "discard pile exhausted at a planet.", "Upgrade.",
                                3, faction, "Signature", False),
        CardClasses.EventCard("Indescribable Horror", "Combat Action: Rout a target army unit with printed cost equal "
                                                      "to or lower than the number of Tyranid units you "
                                                      "control at that planet.", "Tactic.",
                              2, faction, "Signature", 1, False, action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.AttachmentCard("Bone Sabres", "Attach to your warlord.\n"
                                                  "Attached unit gets +1 ATK.\n"
                                                  "Reaction: After attached unit destroys an enemy army unit by an"
                                                  " attack, put 1 Termagant token into play at this planet.",
                                   "Biomorph. Wargear.", 1, faction, "Signature", 3, True,
                                   type_of_units_allowed_for_attachment="Warlord", extra_attack=1),
        CardClasses.SynapseCard("Savage Warrior Prime", "This unit must commit to a "
                                                        "different planet than your warlord, if able.\n"
                                                        "While checking for a battle and determining initiative at "
                                                        "this planet, this unit is considered to be a warlord, "
                                                        "unless an enemy warlord is at this planet.",
                                "Creature. Leviathan. Elite.", 2, 5, 0, True),
        CardClasses.SynapseCard("Blazing Zoanthrope", "Reaction: After the combat phase begins, deal 1 damage to a "
                                                      "target army unit at this planet. "
                                                      "If this planet is infested, deal 2 damage instead.",
                                "Creature. Behemoth. Elite.", 1, 4, 1, True),
        CardClasses.SynapseCard("Gravid Tervigon", "Reaction: After this unit commits to a planet, put 1 Termagant "
                                                   "token into play at this planet. If this planet is infested, "
                                                   "put 2 Termagant tokens into play at this planet instead.",
                                "Creature. Kraken. Elite.", 0, 4, 1, True),
        CardClasses.SynapseCard("Stalking Lictor", "", "Creature. Behemoth. Elite.", 1, 4, 2, True),
        CardClasses.SynapseCard("Venomthrope Polluter", "Reaction: After this unit commits to a planet, move a "
                                                        "non-warlord unit you control from the planet "
                                                        "with your warlord to this planet.",
                                "Creature. Behemoth. Elite", 1, 4, 1, True),
        CardClasses.ArmyCard("Ripper Swarm", "Limited.", "Creature.", 0,
                             faction, "Common", 1, 1, 1, False, limited=True),
        CardClasses.ArmyCard("Strangler Brood", "HIVE MIND - Each Termagant token you "
                                                "control at this planet gets +1 ATK.",
                             "Creature. Leviathan.", 1, faction, "Common", 1, 2, 0, False, hive_mind=True),
        CardClasses.ArmyCard("Termagant Sentry", "Reaction: After a Termagant token you control is "
                                                 "destroyed at this planet, ready this unit.",
                             "Creature. Kraken. Termagant.", 1, faction, "Common", 1, 2, 1, False),
        CardClasses.ArmyCard("Hunter Gargoyles", "Combat Action: Move this unit to an infest planet. "
                                                 "(Limit once per phase.)", "Creature. Kraken.", 1, faction, "Common",
                             2, 1, 0, False, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Virulent Spore Sacs", "Combat Action: Sacrifice this unit to deal 1 damage to each "
                                                    "enemy unit at this planet and infest this plant.",
                             "Creature. Drone.", 2, faction, "Common", 0, 1, 1, False, action_in_play=True,
                             allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Scything Hormagaunts", "Reaction: After you deploy this unit, infest this planet.",
                             "Creature. Leviathan.", 2, faction, "Common", 2, 2, 1, False),
        CardClasses.ArmyCard("Toxic Venomthrope", "Reaction: After you win a command struggle at this planet, "
                                                  "infest it. If it was already infested, either gain 1 resource "
                                                  "or draw 1 card instead of infesting it.", "Creature. Kraken.",
                             2, faction, "Common", 0, 2, 2, False),
        CardClasses.ArmyCard("Termagant Horde", "Reaction: After a combat round at this planet begins, "
                                                "put 1 Termagant token into play at this planet.",
                             "Creature. Leviathan. Termagant.", 3, faction, "Common", 1, 3, 1, False),
        CardClasses.ArmyCard("Volatile Pyrovore", "Interrupt: When this unit is destroyed by an attack, "
                                                  "deal 3 damage to the attacker.", "Creature. Behemoth.",
                             3, faction, "Common", 3, 3, 1, False),
        CardClasses.ArmyCard("Termagant Spikers", "Ranged.\nHIVE MIND - Each Termagant token you control "
                                                  "at this planet gains Ranged.", "Behemoth. Creature. Termagant.",
                             3, faction, "Common", 1, 3, 0, False, hive_mind=True, ranged=True),
        CardClasses.ArmyCard("Tyranid Warrior", "", "Creature. Behemoth.", 3, faction, "Common", 2, 4, 2, False),
        CardClasses.ArmyCard("Swarm Guard", "HIVE MIND - Each Termagant token you control at this planet gets +2 HP.",
                             "Creature. Leviathan.", 3, faction, "Common", 1, 5, 1, False, hive_mind=True),
        CardClasses.ArmyCard("Adamant Hive Guard", "Reaction: After a unit with the Hive Mind specialization or "
                                                   "Termagant token at this planet is assigned damage, reassign "
                                                   "all of that damage to this unit instead.", "Creature. Behemoth.",
                             4, faction, "Common", 2, 5, 0, False),
        CardClasses.ArmyCard("Ymgarl Genestealer", "This unit gets +2 HP while it is at a planet with a synapse unit.\n"
                                                   "This unit gets +2 ATK while it is at a planet with a warlord.",
                             "Creature. Genestealer. Elite.", 5, faction, "Common", 4, 4, 2, False),
        CardClasses.ArmyCard("Ravenous Haruspex", "Reaction: After this unit destroys an enemy army unit by an attack, "
                                                  "gain X resources. X is equal to the "
                                                  "printed cost of the destroyed unit. (Limit once per phase.)",
                             "Creature. Behemoth. Elite.", 5, faction, "Common", 3, 5, 1, False),
        CardClasses.ArmyCard("Biovore Spore Launcher", "Area Effect (1)\n"
                                                       "HIVE MIND - Each Termagant token you control at this planet "
                                                       "gains Area Effect (1).", "Creature. Leviathan. Elite.",
                             6, faction, "Common", 3, 6, 1, False, hive_mind=True, area_effect=1),
        CardClasses.ArmyCard("Shrieking Harpy", "Flying.\n"
                                                "Combat Action: After this unit is declared as an attacker at an "
                                                "infested planet, exhaust each enemy non-Elite army unit and "
                                                "token unit at this planet.", "Creature. Kraken. Elite.",
                             6, faction, "Common", 2, 5, 2, False, flying=True),
        CardClasses.ArmyCard("Burrowing Trygon", "Reduce the cost to deploy this unit by X. X is the highest number of "
                                                 "Termagant tokens you control at a single planet.",
                             "Creature. Behemoth. Elite.", 10, faction, "Common", 7, 7, 3, False),
        CardClasses.EventCard("Clogged with Corpses", "Action: Sacrifice X Termagant units to destroy a target"
                                                      " support card with printed cost X or lower.",
                              "Tactic.", 0, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Predation", "Action: Infest a planet adjacent to an infested planet.", "Tactic.",
                              0, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.EventCard("Spawn Termagants", "Deploy Action: Put 1 Termagant token into play at each planet.",
                              "Power.", 2, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.EventCard("Spore Burst", "Deploy Action: Put a unit with printed cost 3 or lower into play from "
                                             "your discard pile at an infested planet.", "Power.",
                              2, faction, "Common", 2, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.EventCard("Dark Cunning", "Combat Action: Ready a target non-warlord unit you control. "
                                              "Then, if that unit is at an infested planet, gain 1 resource.",
                              "Tactic.", 2, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="COMBAT"),
        CardClasses.EventCard("Consumption", "Deploy Action: Each player must sacrifice a "
                                             "unit at each planet, if able.", "Tactic.",
                              4, faction, "Common", 1, False, action_in_hand=True, allowed_phases_in_hand="DEPLOY"),
        CardClasses.AttachmentCard("Regeneration", "Attach to an army unit.\n"
                                                   "Limit 1 per unit.\n"
                                                   "Attached unit gets +2 HP.\n"
                                                   "Action: Exhaust this attachment to remove 2 "
                                                   "damage from attached unit.", "Condition.",
                                   1, faction, "Common", 1, False, limit_one_per_unit=True,
                                   type_of_units_allowed_for_attachment="Army", extra_health=2,
                                   action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Noxious Fleshborer", "Attach to an army unit.\n"
                                                         "Attached unit gets +1 ATK and +1 HP while it "
                                                         "is at an infested planet.\n"
                                                         "Reaction: After you win a command struggle "
                                                         "at this planet, infest it.", "Wargear. Biomorph.",
                                   1, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army"),
        CardClasses.AttachmentCard("Pincer Tail", "Attach to an army unit.\n"
                                                  "Attached unit gets +1 ATK.\n"
                                                  "Reaction: After attached unit damages an enemy non-warlord "
                                                  "unit by an attack, the damaged unit cannot retreat before "
                                                  "the start of the next combat round.", "Wargear. Biomorph.",
                                   1, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   extra_attack=1),
        CardClasses.AttachmentCard("Parasitic Infection", "Attach to an enemy army unit.\n"
                                                          "Reaction: After the combat phase begins, put 1 "
                                                          "Termagant token into play at this planet and "
                                                          "deal attached unit 1 damage.", "Condition.",
                                   2, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   must_be_enemy_unit=True),
        CardClasses.AttachmentCard("Heavy Venom Cannon", "Attach to an Elite army unit.\n"
                                                         "Attached unit gets +2 ATK.\n"
                                                         "Combat Action: Attached unit, until the end of the phase, "
                                                         "gain either (choose one): Area Effect (2) or Armorbane. "
                                                         "(Limit once per phase.)", "Wargear. Biomorph.",
                                   3, faction, "Common", 2, False, type_of_units_allowed_for_attachment="Army",
                                   extra_attack=2, action_in_play=True, allowed_phases_in_play="COMBAT",
                                   required_traits="Elite"),
        CardClasses.SupportCard("Brood Chamber", "Combat Action: Exhaust this support to give a target army unit you "
                                                 "control a keyword (and all associated values) printed on a "
                                                 "target enemy unit at that planet until the end of the phase.",
                                "Location.", 0, faction, "Common", False,
                                action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Digestion Pool", "Limited.\n"
                                                  "Interrupt: When you deploy a Tyranids unit at an infested planet, "
                                                  "exhaust this support to reduce the unit's cost by 2.",
                                "Upgrade.", 1, faction, "Common", True, limited=True,
                                applies_discounts=[True, 2, True]),
        CardClasses.SupportCard("Mycetic Spores", "Combat Action: Exhaust this support to move a unit you control with "
                                                  "the Hive Mind specialization to a planet with a Termagant token.",
                                "Upgrade.", 2, faction, "Common", False,
                                action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.SupportCard("Spore Chimney", "Reaction: After the headquarters phase begins, "
                                                 "infest a target planet.", "Upgrade.",
                                2, faction, "Common", False),
        CardClasses.SupportCard("Synaptic Link", "Reaction: After a synapse unit you control commits "
                                                 "to a planet, draw 1 card.", "Upgrade.",
                                2, faction, "Common", False),
        CardClasses.ArmyCard("Swarmling Termagants", "Interrupt: When this unit is destroyed, put X Termagant tokens "
                                                     "into play at this planet. X is the number of factions among "
                                                     "enemy units at this planet.", "Creature. Leviathan. Termagant.",
                             2, faction, "Common", 1, 1, 1, False),
        CardClasses.ArmyCard("Striking Ravener", "Reaction: After this unit destroys an "
                                                 "army unit by an attack, ready this unit.", "Creature. Kraken. Elite.",
                             5, faction, "Common", 3, 5, 2, False),
        CardClasses.AttachmentCard("Acid Maw", "Attach to an army unit you control.\n"
                                               "Damage dealt by attached unit cannot be prevented.",
                                   "Wargear. Biomorph.", 2, faction, "Common", 1, False,
                                   type_of_units_allowed_for_attachment="Army", must_be_own_unit=True),
        CardClasses.ArmyCard("Soaring Gargoyles", "Flying. HIVE MIND - Each Termagant token you control at"
                                                  " this planet gains Flying.", "Creature. Leviathan.",
                             2, faction, "Common", 2, 3, 0, False, flying=True, hive_mind=True),
        CardClasses.SupportCard("Sacaellum Infestors", "Reaction: After a planet is infested, exhaust this support to "
                                                       "take either the card bonus or the resource "
                                                       "bonus of that planet.", "Upgrade.",
                                2, faction, "Common", True),
        CardClasses.ArmyCard("Genestealer Prowler", "", "Creature. Genestealer.",
                             1, faction, "Common", 2, 2, 0, False),
        CardClasses.EventCard("Biomass Sacrifice", "Action: Discard 1 or more unit cards from your hand to gain "
                                                   "resources equal to the number of cards discarded by this effect.",
                              "Tactic.", 0, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.WarlordCard("Subject Omega-X62113", "Each Genestealer card in your hand may be deployed to "
                                                        "infested planets as if it had ambush.",
                                "Creature. Genestealer.", faction, 2, 6, 2, 5, "Bloodied.", 6, 6,
                                ["4x Invasive Genestealers", "1x Ruined Passages",
                                 "2x Gene Implantation", "1x Lethal Toxin Sacs"]),
        CardClasses.ArmyCard("Invasive Genestealers", "Reaction: After you deploy this unit, target an enemy army "
                                                      "unit at this planet. Until the end of the phase, the"
                                                      " targeted unit gets -1 HP and this unit gets +1 HP.",
                             "Creature. Genestealer.", 3, faction, "Signature", 2, 3, 1, False),
        CardClasses.SupportCard("Ruined Passages", "Combat Action: Exhaust and sacrifice this support to ready each "
                                                   "Genestealer unit you control at a target planet.", "Location.",
                                3, faction, "Signature", False, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.EventCard("Gene Implantation", "Reaction: After a Genestealer unit you control destroys an "
                                                   "enemy unit with printed cost 3 or lower by an attack,"
                                                   " put that unit into play from your opponent's discard pile "
                                                   "under your control at the same planet.", "Power.",
                              1, faction, "Signature", 1, False),
        CardClasses.AttachmentCard("Lethal Toxin Sacs", "You may deploy this attachment from your discard pile.\n"
                                                        "Attach to an army unit you control.\n"
                                                        "Attached unit gets +3 ATK and -1 HP.", "Genestealer. Wargear.",
                                   2, faction, "Signature", 3, False, extra_attack=3, extra_health=-1,
                                   must_be_own_unit=True, type_of_units_allowed_for_attachment="Army"),
        CardClasses.ArmyCard("Devourer Venomthrope", "Reaction: After you win a command struggle at an "
                                                     "infested planet, exhaust a target non-Elite army"
                                                     " unit at this planet.", "Creature. Psyker. Kraken.",
                             4, faction, "Common", 4, 2, 2, False),
        CardClasses.ArmyCard("Genestealer Brood", "Reaction: After you deploy this unit, search the top 6 cards of"
                                                  " your deck for a Genestealer card. Reveal it, add it to your "
                                                  "hand, and place the remaining cards on the bottom of your deck "
                                                  "in any order.", "Creature. Genestealer.",
                             3, faction, "Common", 3, 2, 1, False),
        CardClasses.EventCard("Sudden Adaptation", "Action: Return a Tyranids army unit at a planet to your hand to "
                                                   "put a Tyranids army unit with equal or lower printed cost and a "
                                                   "different name into play from your hand at the same planet.",
                              "Power.", 2, faction, "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="ALL"),
        CardClasses.ArmyCard("Genestealer Harvesters", "Reaction: While this unit is at an infested planet, it gains:"
                                                       " +1 card and +1 resource when command struggle"
                                                       " won at this planet.", "Creature. Genestealer.",
                             2, faction, "Common", 2, 2, 1, False),
        CardClasses.SupportCard("Nesting Chamber", "Action: Exhaust this support to infest a planet with 2 or "
                                                   "more Genestealer units at it.", "Upgrade.",
                                1, faction, "Common", False, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.AttachmentCard("Ymgarl Factor", "Attach to an army unit you control.\n"
                                                    "Action: Pay 1 resource to have attached unit get, until the end "
                                                    "of the phase, either: +2 ATK or +2 HP.", "Skill. Genestealer.",
                                   1, faction, "Common", 2, False, type_of_units_allowed_for_attachment="Army",
                                   must_be_own_unit=True, action_in_play=True, allowed_phases_in_play="ALL"),
        CardClasses.SynapseCard("Keening Maleceptor", "Combat Action: Remove an infestation token from this "
                                                      "planet to trigger its Battle ability. (Limit once per phase.)",
                                "Creature. Leviathan. Elite.", 1, 5, 1, True,
                                action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Crush of Sky-Slashers", "Flying.\n"
                                                      "Reaction: After a combat round begins at this planet, "
                                                      "deal 1 damage to a target enemy unit at this planet with "
                                                      "printed cost 2 or lower.", "Creature.",
                             1, faction, "Common", 1, 2, 0, False, flying=True),
        CardClasses.ArmyCard("Caustic Tyrannofex", "Reaction: After you win a command struggle at this planet, until"
                                                   " the end of the round, this unit gains “Hive Mind -"
                                                   " Each Termagant token you control at "
                                                   "this planet gains Armorbane.”", "Creature. Leviathan. Elite.",
                             5, faction, "Common", 4, 4, 3, False, hive_mind=True),
        CardClasses.SupportCard("Loamy Broodhive", "Reaction: After you deploy an Elite unit, exhaust this support to "
                                                   "put 2 Termagant tokens into play at the same planet as that unit.",
                                "Location.", 1, faction, "Common", False),
        CardClasses.ArmyCard("Focal Warrior", "Each Elite unit you control at this planet gains Brutal.",
                             "Creature. Kraken.", 2, faction, "Common", 1, 3, 1, False),
        CardClasses.AttachmentCard("Flesh Hooks", "Deep Strike (1).\n"
                                                  "Attach to an enemy army unit with printed cost 2 or lower.\n"
                                                  "Attached unit cannot be readied.", "Wargear. Biomorph.",
                                   1, faction, "Common", 1, False, must_be_enemy_unit=True,
                                   type_of_units_allowed_for_attachment="Army", deepstrike=1),
        CardClasses.ArmyCard("Mucolid Spores", "Flying. Mobile. \n"
                                               "Interrupt: When this unit is destroyed, destroy "
                                               "up to 2 target enemy support cards.", "Creature.",
                             3, faction, "Common", 0, 2, 1, False, flying=True, mobile=True),
        CardClasses.EventCard("Burst Forth", "Deep Strike (0).\n"
                                             "Reaction: After you Deep Strike this event, commit either your "
                                             "warlord or a synapse unit you control to this planet.", "Tactic.",
                              0, faction, "Common", 1, False, deepstrike=0),
        CardClasses.ArmyCard("Lictor Vine Lurker", "Deep Strike (2).\n"
                                                   "Reaction: After you Deep Strike this unit, discard 1 "
                                                   "card at random from your opponent's hand.", "Creature. Leviathan.",
                             4, faction, "Common", 3, 3, 1, False, deepstrike=2),
        CardClasses.SupportCard("Invasion Site", "Reaction: After an Elite unit you control is destroyed, "
                                                 "sacrifice this support to gain X resources. "
                                                 "X is equal to that unit's printed cost.", "Location.",
                                0, faction, "Common", True),
        CardClasses.ArmyCard("Slavering Mawloc", "Deep Strike (3).\n"
                                                 "Reaction: After you Deep Strike this unit, it gains Armorbane "
                                                 "until the end of the phase.", "Creature. Leviathan. Elite.",
                             6, faction, "Common", 3, 6, 0, False, deepstrike=3),
        CardClasses.AttachmentCard("Armored Shell", "Attach to an army unit you control.\n"
                                                    "Reaction: After attached unit is assigned damage by an attack, "
                                                    "prevent all but 2 of that damage.", "Wargear. Biomorph.",
                                   2, faction, "Common", 1, False, type_of_units_allowed_for_attachment="Army",
                                   must_be_own_unit=True),
        CardClasses.WarlordCard("Parasite of Mortrex", "Flying.\n"
                                                       "Reaction: After this warlord is declared as an attacker, "
                                                       "search your discard pile or your deck for a Condition "
                                                       "attachment. Reveal it, and put it into play attached to "
                                                       "an eligible enemy unit at this planet. "
                                                       "Then, shuffle your deck.", "Creature. Kraken.",
                                faction, 1, 7, 1, 5, "Flying. Bloodied.", 6, 6,
                                ["4x Savage Parasite", "2x Swarming Rippers", "1x Sweep Attack",
                                 "1x Prey on the Weak"], flying=True),
        CardClasses.AttachmentCard("Savage Parasite", "Attach to a non-warlord unit.\n"
                                                      "Reaction: After the combat phase begins, put 1 Termagant "
                                                      "token into play at this planet, and deal attached "
                                                      "unit 1 damage.\n"
                                                      "Interrupt: When this attachment leaves play, "
                                                      "attach it to a target eligible unit instead.", "Condition.",
                                   6, faction, "Signature", 1, False,
                                   type_of_units_allowed_for_attachment="Army/Synapse/Token"),
        CardClasses.ArmyCard("Swarming Rippers", "Each enemy unit with 1 or more Condition attachments "
                                                 "at this planet gets -1 ATK.", "Creature. Swarm.",
                             2, faction, "Signature", 2, 2, 1, False),
        CardClasses.EventCard("Sweep Attack", "Reaction: After your warlord commits to a planet, "
                                              "search your discard pile or your deck for a Condition attachment. "
                                              "Reveal it, and put it into play attached to an eligible "
                                              "enemy unit at an adjacent planet. Then, shuffle your deck.", "Tactic.",
                              0, faction, "Signature", 3, False),
        CardClasses.SupportCard("Prey on the Weak", "Interrupt: When an enemy unit with a Condition attachment leaves "
                                                    "play from a planet, exhaust this support to infest that planet. "
                                                    "\nAction: Sacrifice a Synapse unit to put a Synapse unit "
                                                    "with a different name into play at your HQ "
                                                    "from the card collection. (Limit once per game.)", "Upgrade.",
                                1, faction, "Signature", False, action_in_play=True,
                                allowed_phases_in_play="ALL"),
        CardClasses.SynapseCard("Ardaci-strain Broodlord", "Reaction: After you infest a planet, draw a card and "
                                                           "infest an adjacent planet. (Limit once per phase.)",
                                "Creature. Genestealer. Elite.", 1, 4, 1, True),
        CardClasses.SynapseCard("Aberrant Alpha", "Each army unit you control at an infested planet gets +1 HP.",
                                "Genestealer. Elite.", 1, 4, 1, True),
        CardClasses.SynapseCard("Praetorian Shadow", "While this unit is at the same or adjacent planet as "
                                                     "your warlord, your warlord gets +1 ATK.\n"
                                                     "Reaction: After your warlord is assigned damage, exhaust this "
                                                     "unit to prevent 1 of that damage.", "Creature. Elite.",
                                1, 5, 1, True),
        CardClasses.SynapseCard("Vanguarding Horror", "Reduce the Deep Strike value of each card you control at "
                                                      "each adjacent planet by 1.\n"
                                                      "Combat Action: Exhaust this unit to move a card in reserve "
                                                      "either: from this planet to an adjacent planet or "
                                                      "from an adjacent planet to this planet.", "Creature. Elite.",
                                1, 4, 1, True, action_in_play=True, allowed_phases_in_play="COMBAT"),
        CardClasses.ArmyCard("Seething Mycetic Spore", "Deep Strike (1).\n"
                                                       "Reaction: After you Deep Strike this unit, put 2 army units "
                                                       "into play from your hand or discard pile at this planet. "
                                                       "They must have different names and a printed cost of "
                                                       "1 or less.", "Creature. Transport.",
                             0, faction, "Common", 1, 3, 0, False, deepstrike=1),
        CardClasses.ArmyCard("Spreading Genestealer Brood", "Reaction: After this unit enters play, put a Brood "
                                                            "unit into play from your discard pile at this planet.",
                             "Creature. Genestealer. Brood.", 1, faction, "Common", 1, 1, 1, False),
        CardClasses.ArmyCard("Icy Trygon", "Deep Strike (1).\n"
                                           "Interrupt: When this unit would be destroyed by taking damage, remove "
                                           "all damage from it and put it into reserve at this planet instead.",
                             "Creature.", 3, faction, "Common", 2, 4, 1, False, deepstrike=1),
        CardClasses.ArmyCard("Emergent Cultists", "While at an infested planet, this unit gets +1 HP.\n"
                                                  "Reaction: After you deploy this unit, "
                                                  "exhaust a target enemy support card.", "Hybrid. Genestealer.",
                             2, faction, "Common", 3, 2, 1, False)
    ]
    return tyranids_card_array
