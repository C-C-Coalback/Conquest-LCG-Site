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


class BattleItemsTest(unittest.IsolatedAsyncioTestCase):
    async def test_veteran_brother_maxos(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["10th Company Scout"]
        test_game.p1.resources = 7
        card = test_game.preloaded_find_card("Veteran Brother Maxos")
        test_game.p1.add_card_to_planet(card, 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 3)

    async def test_nazdregs_flash_gitz(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = []
        test_game.p1.resources = 7
        card = test_game.preloaded_find_card("Nazdreg's Flash Gitz")
        test_game.p1.add_card_to_planet(card, 0, already_exhausted=True)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 1), 1)
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_captain_markis(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = []
        test_game.p2.cards = []
        card = test_game.preloaded_find_card("Captain Markis")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "2"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 1), False)
        self.assertEqual(test_game.p1.get_once_per_phase_used_given_pos(0, 1), True)

    async def test_zarathurs_flamers(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 0)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 2)

    async def test_haemonculus_tormentor(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_2, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Haemonculus Tormentor"))
        test_game.p1.resources = 7
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(test_game.p1.get_attack_given_pos(-2, 0), 4)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Haemonculus Tormentor"), 0)
        test_game.p1.resources = 7
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 4)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 6)

    async def test_wildrider_squadron(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = []
        test_game.p2.cards = []
        card = test_game.preloaded_find_card("Wildrider Squadron")
        test_game.p1.add_card_to_planet(card, 1)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)
        self.assertEqual(test_game.p1.get_once_per_phase_used_given_pos(0, 1), True)

    async def test_ravenous_flesh_hounds(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ravenous Flesh Hounds"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Cultist"), 0)
        test_game.p1.set_damage_given_pos(0, 0, 3)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 1)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 0)

