import unittest
from play.gamecode.GameClass import Game
from play.gamecode import Initfunctions, FindCard
import os
import random


current_dir = os.path.dirname(__file__)


card_array = Initfunctions.init_player_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()


first_deck_location = os.path.join(current_dir, 'decksForTests/sample_deck_1.txt')
second_deck_location = os.path.join(current_dir, 'decksForTests/sample_deck_2.txt')

with open(first_deck_location, 'r') as file:
    deck_content_1 = file.read()
with open(second_deck_location, 'r') as file:
    deck_content_2 = file.read()

with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
    cato_deck_content = file.read()


class InterruptsTest(unittest.IsolatedAsyncioTestCase):
    async def test_enginseer_augur(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.deck = ["Catachan Outpost"]
        for _ in range(10):
            test_game.p1.deck.append("Promethium Mine")
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Enginseer Augur"), 0)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["SEARCH", "1"])
        await test_game.update_game_event("P1", ["SEARCH", "0"])
        self.assertEqual(len(test_game.p1.headquarters), 2)
        self.assertEqual(test_game.p1.get_ability_given_pos(-2, 1), "Catachan Outpost")


if __name__ == "__main__":
    unittest.main()
