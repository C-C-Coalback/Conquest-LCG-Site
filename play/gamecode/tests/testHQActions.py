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


class HQActionsTest(unittest.IsolatedAsyncioTestCase):
    async def test_kraktoof_hall(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Kraktoof Hall"))
        test_game.p1.set_damage_given_pos(0, 0, 3)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.stored_damage), 0)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 2)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 1)
        self.assertEqual(test_game.action_chosen, "")

    async def test_ork_kannon(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_2, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ork Kannon"))
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.stored_damage), 2)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 1)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 1)

    async def test_tellyporta_pad(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_2, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Tellyporta Pad"))
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 3)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "3", "0"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Shoota Mob"))
        test_game.p1.ready_given_pos(-2, 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 3)

    async def test_khymera_den(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_2, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Khymera Den"))
        card = test_game.preloaded_find_card("Khymera")
        test_game.p1.add_card_to_planet(card, 3)
        test_game.p1.add_card_to_planet(card, 4)
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p1.add_to_hq(card)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "3", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "4", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 5)
        self.assertEqual(len(test_game.p1.cards_in_play[2]), 0)
        self.assertEqual(len(test_game.p1.cards_in_play[3]), 0)
        self.assertEqual(len(test_game.p1.cards_in_play[4]), 0)
        self.assertEqual(len(test_game.p1.cards_in_play[5]), 0)
        self.assertEqual(len(test_game.p1.headquarters), 1)

    async def test_catachan_outpost(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Catachan Outpost"))
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 4)
        self.assertEqual(test_game.action_chosen, "")

    async def test_twisted_laboratory(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Enraged Ork"), 0)
        test_game.p2.set_damage_given_pos(0, 1, 3)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Twisted Laboratory"))
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(test_game.p2.get_attack_given_pos(0, 1), 0)
        self.assertEqual(test_game.p2.get_blanked_given_pos(0, 1), True)
        self.assertEqual(test_game.p2.get_brutal_given_pos(0, 1), False)
        self.assertEqual(test_game.action_chosen, "")


if __name__ == "__main__":
    unittest.main()
