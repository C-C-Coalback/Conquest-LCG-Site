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


first_deck_location = os.path.join(current_dir, 'decksForTests/sample_deck_1.txt')
second_deck_location = os.path.join(current_dir, 'decksForTests/sample_deck_2.txt')

with open(first_deck_location, 'r') as file:
    deck_content_1 = file.read()
with open(second_deck_location, 'r') as file:
    deck_content_2 = file.read()


class StandardTest(unittest.IsolatedAsyncioTestCase):
    async def test_basic(self):
        self.assertEqual(True, True)
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        self.assertEqual(len(test_game.p1.cards), 7)
        self.assertEqual(len(test_game.p2.cards), 7)
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(test_game.p2.resources, 7)
        test_game.p1.draw_card()
        self.assertEqual(len(test_game.p1.cards), 8)
        test_game.p2.draw_card()
        self.assertEqual(len(test_game.p2.cards), 8)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["10th Company Scout"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "3"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)


if __name__ == "__main__":
    unittest.main()
