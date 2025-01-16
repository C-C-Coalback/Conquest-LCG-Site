import CardClasses


def neutral_cards_init():
    neutral_card_array = [CardClasses.EventCard("No Mercy", "Interrupt: When an opponent uses a shield card, "
                                                            "exhaust a unique unit you control to cancel that card's "
                                                            "shielding effect.", "Tactic.", 0, "Neutral",
                                                "Common", 1, False, ""),
                          CardClasses.ArmyCard("Void Pirate", "+1 card when command struggle won at this planet.",
                                               "Ally.", 1, "Neutral", "Common", 0, 1, 1,
                                               False, ""),
                          CardClasses.ArmyCard("Rogue Trader", "+1 resource when "
                                                               "command struggle won at this planet.", "Ally.",
                                               1, "Neutral", "Common", 0, 1, 1,
                                               False, ""),
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
                                                  ""),
                          CardClasses.AttachmentCard("Promotion", "Limited.\nAttach to an army unit.\n"
                                                                  "Attached unit gains 2 command icons.", "Skill.",
                                                     0, "Neutral", "Common", 1, False, "")]
    return neutral_card_array