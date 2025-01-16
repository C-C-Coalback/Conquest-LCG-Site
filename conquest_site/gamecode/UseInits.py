from Inits import OrksCardsInit, ChaosCardsInit, NeutralCardsInit, FinalCardInit, PlanetCardsInit

orks_card_array = OrksCardsInit.orks_cards_init()
chaos_card_array = ChaosCardsInit.chaos_cards_init()
neutral_card_array = NeutralCardsInit.neutral_cards_init()
final_card_array = FinalCardInit.final_card_init()
card_array = orks_card_array + chaos_card_array + neutral_card_array + final_card_array
planet_array = PlanetCardsInit.planet_cards_init()
faction_wheel = ["Astra Militarum", "Space Marines", "Tau", "Eldar",
                 "Dark Eldar", "Chaos", "Orks", "Astra Militarum", "Space Marines"]