from .. import CardClasses


def neutral_cards_init():
    neutral_card_array = [
        CardClasses.EventCard("No Mercy", "Interrupt: When an opponent uses a shield card, "
                                          "exhaust a unique unit you control to cancel that card's "
                                          "shielding effect.", "Tactic.", 0, "Neutral",
                              "Common", 1, False, ""),
        CardClasses.ArmyCard("Void Pirate", "+1 card when command struggle won at this planet.",
                             "Ally.", 1, "Neutral", "Common", 0, 1, 1,
                             False, additional_cards_command_struggle=1),
        CardClasses.ArmyCard("Rogue Trader", "+1 resource when "
                                             "command struggle won at this planet.", "Ally.",
                             1, "Neutral", "Common", 0, 1, 1,
                             False, additional_resources_command_struggle=1),
        CardClasses.EventCard("Fall Back!", "Reaction: After an Elite unit is destroyed, "
                                            "put it into play from your discard pile at your HQ.",
                              "Tactic.", 1, "Neutral", "Common", 1,
                              False, ""),
        CardClasses.SupportCard("Promethium Mine", "Limited.\nFORCED REACTION: After this"
                                                   " card enters play, place 4 resources on it.\n"
                                                   "Reaction: After the deploy phase begins, transfer"
                                                   " 1 resource from this card to "
                                                   "your resource pool.",
                                "Location.", 1, "Neutral", "Common", False,
                                limited=True),
        CardClasses.AttachmentCard("Promotion", "Limited.\nAttach to an army unit.\n"
                                                "Attached unit gains 2 command icons.", "Skill.",
                                   0, "Neutral", "Common", 1, False, limited=True,
                                   type_of_units_allowed_for_attachment="Army",
                                   extra_command=2),
        CardClasses.ArmyCard("Freebooter Kaptain", "Army units with printed cost 2 or lower do not count their command "
                                                   "icons during command struggles at this planet.", "Ally.",
                             3, "Neutral", "Common", 3, 3, 1, False),
        CardClasses.EventCard("Backlash", "Interrupt: When your opponent triggers an ability that targets an Elite "
                                          "unit you control, cancel its effects. Then, if that ability was "
                                          "triggered from an army unit, destroy it.", "Tactic.",
                              1, "Neutral", "Common", 1, False),
        CardClasses.AttachmentCard("Defense Battery", "Attach to a planet.\n"
                                                      "Action: After an enemy army unit moves to or from attached "
                                                      "planet, exhaust this attachment to deal 2 damage to that unit.",
                                   "Artillery.", 1, "Neutral", "Common", 1, False, planet_attachment=True),
        CardClasses.SupportCard("STC Fragment", "Limited.\n"
                                                "Interrupt: When you deploy an Elite unit, exhaust this support "
                                                "to reduce the cost of that unit by 2.", "Relic.",
                                1, "Neutral", "Common", True, limited=True, applies_discounts=[True, 2, False]),
        CardClasses.EventCard("Calamity", "HEADQUARTERS ACTION: Return each army unit with printed cost 2 or "
                                          "lower to its owner's hand.", "Disaster.",
                              1, "Neutral", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="HEADQUARTERS"),
        CardClasses.ArmyCard("Inquisitor Caius Wroth", "Reaction: After this unit enters play, each player must "
                                                       "choose and discard down to 4 cards in his hand, if able.",
                             "Psyker. Inquisitor.", 4, "Neutral", "Common", 3, 5, 1, True),
        CardClasses.EventCard("Imperial Blockade", "Deploy Action: Pay 1 resource per copy of this card in your discard"
                                                   " pile and draw a card to target a planet. Until the end of the"
                                                   " round, at that planet, players must pay 1 resource to trigger"
                                                   " a non-warlord card effect that moves a unit to that planet, rout"
                                                   " a unit or makes a non-Runt unit enter play.", "Tactic.",
                              0, "Neutral", "Common", 1, False,
                              action_in_hand=True, allowed_phases_in_hand="DEPLOY")
    ]
    return neutral_card_array
