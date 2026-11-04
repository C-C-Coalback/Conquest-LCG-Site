import unittest
from play.gamecode.GameClass import Game
from play.gamecode import Initfunctions
import random
from play.gamecode.tests.deckLoading import deck_content_1, deck_content_2, ooe_deck_content, cato_deck_content, nazdreg_deck_content, eldorath_deck_content, shadowsun_deck_content
from play.gamecode.tests.shortcuts import skip_to_battle_first_planet, standard_setup, click_pass, click_action, click_planet, click_hand, click_hq, click_in_play, click_choice, click_search, dummy_click

card_array = Initfunctions.init_player_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()


class AbilityPreventionsTest(unittest.IsolatedAsyncioTestCase):
    async def test_land_raider(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        card = test_game.preloaded_find_card("Land Raider")
        test_game.p1.add_card_to_planet(card, 0)
        card = test_game.preloaded_find_card("10th Company Scout")
        test_game.p1.add_card_to_planet(card, 0)
        card = test_game.preloaded_find_card("Raven Guard Speeder")
        test_game.p1.add_card_to_planet(card, 0)
        card = test_game.preloaded_find_card("Sicarius's Chosen")
        test_game.p2.add_card_to_planet(card, 1)
        await dummy_click(test_game, 2)
        await click_choice(test_game, 2, 0)
        self.assertEqual(len(test_game.reactions_needing_resolving), 1)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 3)
        await click_in_play(test_game, 2, 1, 0, 1)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 3)
        await click_in_play(test_game, 2, 1, 0, 2)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 2)
        self.assertEqual(len(test_game.reactions_needing_resolving), 0)
