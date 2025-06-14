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
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, False)
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

    async def test_assign_damage(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, False)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        test_game.p1.draw_card()
        test_game.p2.draw_card()
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["10th Company Scout"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "3"])
        test_game.p1.assign_damage_to_pos(3, 0, 3)
        await test_game.update_game_event("P2", [])
        await test_game.update_game_event("P1", ["pass-P1"])
        self.assertEqual(len(test_game.p1.cards_in_play[4]), 0)
        self.assertEqual(len(test_game.damage_on_units_list_before_new_damage), 0)
        self.assertEqual(len(test_game.damage_is_preventable), 0)
        self.assertEqual(len(test_game.positions_of_units_to_take_damage), 0)
        self.assertEqual(len(test_game.damage_can_be_shielded), 0)
        self.assertEqual(len(test_game.positions_attackers_of_units_to_take_damage), 0)
        self.assertEqual(len(test_game.card_names_triggering_damage), 0)
        self.assertEqual(len(test_game.amount_that_can_be_removed_by_shield), 0)
        test_game.p1.assign_damage_to_pos(-2, 0, 3)
        await test_game.update_game_event("P2", [])
        await test_game.update_game_event("P1", ["pass-P1"])
        self.assertEqual(len(test_game.p1.cards_in_play[4]), 0)
        self.assertEqual(len(test_game.damage_on_units_list_before_new_damage), 0)
        self.assertEqual(len(test_game.damage_is_preventable), 0)
        self.assertEqual(len(test_game.positions_of_units_to_take_damage), 0)
        self.assertEqual(len(test_game.damage_can_be_shielded), 0)
        self.assertEqual(len(test_game.positions_attackers_of_units_to_take_damage), 0)
        self.assertEqual(len(test_game.card_names_triggering_damage), 0)
        self.assertEqual(len(test_game.amount_that_can_be_removed_by_shield), 0)
        self.assertEqual(test_game.p1.get_damage_given_pos(-2, 0), 3)


if __name__ == "__main__":
    unittest.main()
