import unittest
from play.gamecode.GameClass import Game
from play.gamecode import Initfunctions
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


async def skip_to_battle_first_planet(test_game):
    await test_game.update_game_event("P1", ["CHOICE", "0"])
    await test_game.update_game_event("P2", ["CHOICE", "0"])
    test_game.p1.cards = []
    test_game.p2.cards = []
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])
    await test_game.update_game_event("P1", ["PLANETS", "0"])
    await test_game.update_game_event("P2", ["PLANETS", "0"])
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])


class AutomatedElementsTest(unittest.IsolatedAsyncioTestCase):
    async def test_veteran_brother_maxos_is_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Eager Recruit"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Veteran Brother Maxos"), 0)
        await test_game.update_game_event("P1", [])
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)

    async def test_nazdregs_gitz_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Nazdreg's Flash Gitz"), 0, already_exhausted=True)
        await test_game.update_game_event("P1", [])
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)

    async def test_kraktoof_hall_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Nazdreg's Flash Gitz"), 0, already_exhausted=True)
        test_game.p1.set_damage_given_pos(0, 1, 2)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Kraktoof Hall"))
        await test_game.update_game_event("P1", [])
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)

    async def test_drop_pod_assault_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Drop Pod Assault"]
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_battle_cry_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Battle Cry"]
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
