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


class StandardTest(unittest.IsolatedAsyncioTestCase):
    async def test_experimental_devilfish(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Experimental Devilfish"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_ardent_auxiliaries(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ardent Auxiliaries"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Infantry Conscripts"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_ardent_auxiliaries_apoka(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "Apoka", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ardent Auxiliaries"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_ardent_auxiliaries_apokaless(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ardent Auxiliaries"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), False)
