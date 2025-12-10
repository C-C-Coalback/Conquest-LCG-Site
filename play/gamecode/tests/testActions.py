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


class ActionsTest(unittest.IsolatedAsyncioTestCase):
    async def test_snotling_attack(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, False, [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        test_game.p1.draw_card()
        test_game.p2.draw_card()
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Snotling Attack"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "1"])
        await test_game.update_game_event("P1", ["PLANETS", "4"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)
        self.assertEqual(len(test_game.p1.cards_in_play[2]), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[3]), 0)
        self.assertEqual(len(test_game.p1.cards_in_play[4]), 0)
        self.assertEqual(len(test_game.p1.cards_in_play[5]), 1)
        self.assertEqual(test_game.p1.get_name_given_pos(0, 0), "Snotlings")

    async def test_promise_of_glory(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, False, [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        test_game.p1.draw_card()
        test_game.p2.draw_card()
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Promise of Glory"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(len(test_game.p1.headquarters), 3)
        self.assertEqual(test_game.p1.get_name_given_pos(-2, 1), "Cultist")


if __name__ == "__main__":
    unittest.main()
