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


class MiscActionsTest(unittest.IsolatedAsyncioTestCase):
    async def test_command_link_drone(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.resources = 7
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Command-link Drone"), 0, 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["ATTACHMENT", "IN_PLAY", "1", "0", "0", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(-2, 0)), 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 0)
        self.assertEqual(test_game.p1.get_resources(), 6)
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["ATTACHMENT", "HQ", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(-2, 0)), 0)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)
        self.assertEqual(test_game.p1.get_resources(), 5)


if __name__ == "__main__":
    unittest.main()
