from .Inits import ChaosCardsInit, FinalCardInit, NeutralCardsInit, OrksCardsInit, PlanetCardsInit


def init_player_cards():
    orks_card_array = OrksCardsInit.orks_cards_init()
    chaos_card_array = ChaosCardsInit.chaos_cards_init()
    neutral_card_array = NeutralCardsInit.neutral_cards_init()
    final_card_array = FinalCardInit.final_card_init()
    card_array = orks_card_array + chaos_card_array + neutral_card_array + final_card_array
    return card_array


def init_planet_cards():
    planet_cards_array = PlanetCardsInit.planet_cards_init()
    return planet_cards_array
