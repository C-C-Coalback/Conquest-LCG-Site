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


async def standard_setup(test_game):
    await test_game.update_game_event("P1", ["CHOICE", "0"])
    await test_game.update_game_event("P2", ["CHOICE", "0"])
    test_game.p1.cards = []
    test_game.p2.cards = []


async def skip_to_battle_first_planet(test_game):
    await standard_setup(test_game)
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


class ActionsTest(unittest.IsolatedAsyncioTestCase):
    async def test_snotling_attack(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
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
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
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

    async def test_exterminatus(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 1)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 1)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 1,)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Stalwart Ogryn"), 1)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 1)
        test_game.p1.cards = ["Exterminatus"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(test_game.mode, "ACTION")
        await test_game.update_game_event("P1", ["PLANETS", "1"])
        self.assertEqual(test_game.p1.resources, 4)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 4)
        self.assertEqual(len(test_game.p2.discard), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[2]), 0)
        self.assertEqual(len(test_game.p2.cards_in_play[2]), 1)
        self.assertEqual(test_game.p2.get_name_given_pos(1, 0), "Stalwart Ogryn")

    async def test_drop_pod_assault(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Drop Pod Assault"]
        test_game.p1.deck = ["Eager Recruit" for _ in range(10)]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["SEARCH", "0"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)
        self.assertEqual(test_game.p1.get_name_given_pos(0, 1), "Eager Recruit")

    async def test_battle_cry(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        card = test_game.preloaded_find_card("Burna Boyz")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        test_game.p1.cards = ["Battle Cry"]
        test_game.p1.resources = 7
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.resources, 4)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 7)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 2), 3)

    async def test_squig_bombin(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Squig Bombin'"]
        test_game.p2.cards = []
        test_game.p1.resources = 7
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "2", "1"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p2.headquarters), 1)

    async def test_pact_of_the_haemonculi(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Pact of the Haemonculi", "Pact of the Haemonculi"]
        test_game.p2.cards = ["Rogue Trader", "Void Pirate"]
        test_game.p1.resources = 7
        card = test_game.preloaded_find_card("Khymera")
        test_game.p1.add_to_hq(card)
        test_game.p1.add_card_to_planet(card, 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.headquarters), 1)
        self.assertEqual(len(test_game.p1.cards), 3)
        self.assertEqual(len(test_game.p2.cards), 1)
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        self.assertEqual(test_game.p1.resources, 3)
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 0)
        self.assertEqual(len(test_game.p1.cards), 4)
        self.assertEqual(len(test_game.p2.cards), 0)

    async def test_know_no_fear(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Know No Fear"]
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Eager Recruit"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Eager Recruit"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Eager Recruit"))
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        await test_game.update_game_event("P1", ["PLANETS", "1"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        await test_game.update_game_event("P1", ["PLANETS", "2"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[2]), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[3]), 1)
        self.assertEqual(test_game.p1.get_name_given_pos(0, 0), "Eager Recruit")
        self.assertEqual(test_game.p1.get_name_given_pos(1, 0), "Eager Recruit")
        self.assertEqual(test_game.p1.get_name_given_pos(2, 0), "Eager Recruit")
        self.assertEqual(test_game.p1.get_ready_given_pos(-2, 0), False)

    async def test_rally_the_charge(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Rally the Charge"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 9)

    async def test_power_from_pain(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Power from Pain"]
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 2)
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 1)
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)

    async def test_archons_terror(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Archon's Terror"]
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 1)
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)

    async def test_raid(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Raid"]
        test_game.p2.cards = []
        test_game.p1.resources = 7
        test_game.p2.resources = 7
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.cards, ["Raid"])
        test_game.p1.resources = 6
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.cards, [])
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(test_game.p2.resources, 6)

    async def test_doom(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Doom"]
        test_game.p2.cards = []
        test_game.p1.resources = 7
        test_game.p2.resources = 7
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Craftworld Gate"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Eldar Survivalist"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Spiritseer Erathal"))
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Black Legion Heldrake"))
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.cards, [])
        self.assertEqual(test_game.p1.resources, 3)
        self.assertEqual(len(test_game.p2.headquarters), 1)
        self.assertEqual(len(test_game.p1.headquarters), 3)
        self.assertEqual(test_game.p1.get_ability_given_pos(-2, 1), "Craftworld Gate")
        self.assertEqual(test_game.p1.get_ability_given_pos(-2, 2), "Spiritseer Erathal")

    async def test_gift_of_isha(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Gift of Isha"]
        test_game.p2.cards = []
        test_game.p1.resources = 7
        test_game.p2.resources = 7
        test_game.p1.discard = ["Eldar Survivalist", "Wailing Wraithfighter", "Gift of Isha"]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 0), "Wailing Wraithfighter")
        self.assertEqual(test_game.p1.cards_in_play[1][0].sacrifice_end_of_phase, True)
        self.assertEqual(test_game.p1.cards, [])
        self.assertEqual(test_game.p1.discard, ["Eldar Survivalist", "Gift of Isha", "Gift of Isha"])
        self.assertEqual(test_game.p1.resources, 5)

    async def test_squadron_redeployment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0, 0)
        test_game.p2.cards = []
        test_game.p1.cards = ["Squadron Redeployment"]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 0), False)
        await test_game.update_game_event("P1", ["PLANETS", "2"])
        self.assertEqual(len(test_game.p1.cards_in_play[3]), 1)
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.ready_given_pos(2, 0)
        test_game.p1.retreat_unit(2, 0, exhaust=False)
        test_game.p1.cards = ["Squadron Redeployment"]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(len(test_game.p1.headquarters), 2)
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        await test_game.update_game_event("P1", ["PLANETS", "2"])
        self.assertEqual(len(test_game.p1.headquarters), 1)
        self.assertEqual(len(test_game.p1.cards_in_play[3]), 1)

    async def test_repent(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Repent!"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Alpha Legion Infiltrator"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 0), False)
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 0), False)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 4)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 3)
        self.assertEqual(len(test_game.stored_damage), 2)

    async def test_the_siege_masters(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["The Siege Masters"]
        test_game.p2.cards = []
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Fortress of Madness"))
        test_game.p1.deck = ["Fortress-Monastery" for _ in range(10)]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "2", "1"])
        await test_game.update_game_event("P1", ["SEARCH", "0"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 1)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(test_game.p2.get_ready_given_pos(-2, 1), False)

    async def test_the_bloodied_host(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["The Bloodied Host"]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 8)

    async def test_ambush_unit(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Eager Recruit"]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)

    async def test_ambush_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Dire Mutation"]
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p2.get_attachment_at_pos(0, 1, 0).get_ability(), "Dire Mutation")

    async def test_preemptive_barrage(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Preemptive Barrage"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "2"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "3"])
        self.assertEqual(test_game.p1.get_ranged_given_pos(0, 1), True)
        self.assertEqual(test_game.p1.get_ranged_given_pos(0, 2), True)
        self.assertEqual(test_game.p1.get_ranged_given_pos(0, 3), True)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_suppressive_fire(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Suppressive Fire"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 0), False)
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 1), False)
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_warpstorm(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p2.cards = []
        test_game.p1.cards = ["Warpstorm"]
        test_game.p1.resources = 7
        card = test_game.preloaded_find_card("Sniveling Grot")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(card, 0)
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Promotion"), 0, 1)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(len(test_game.stored_damage), 0)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 2)
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 0), "Zarathur, High Sorcerer")
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 1), "Sniveling Grot")
        self.assertEqual(test_game.p1.get_attachment_at_pos(0, 1, 0).get_ability(), "Promotion")
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 3)
        self.assertEqual(test_game.p1.resources, 4)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_warpstorm_hq(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p2.cards = []
        test_game.p1.cards = ["Warpstorm"]
        test_game.p1.resources = 7
        card = test_game.preloaded_find_card("Sniveling Grot")
        test_game.p2.add_to_hq(card)
        test_game.p2.add_to_hq(card)
        test_game.p2.attach_card(test_game.preloaded_find_card("Promotion"), -2, 1)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "2", "0"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(len(test_game.stored_damage), 0)
        self.assertEqual(test_game.p2.get_damage_given_pos(-2, 0), 0)
        self.assertEqual(test_game.p2.get_ability_given_pos(-2, 0), "Sniveling Grot")
        self.assertEqual(test_game.p2.get_attachment_at_pos(-2, 0, 0).get_ability(), "Promotion")
        self.assertEqual(test_game.p1.resources, 4)
        self.assertEqual(len(test_game.p1.cards), 0)
        test_game.p2.print_headquarters()

    async def test_tzeentchs_firestorm(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Tzeentch's Firestorm"]
        test_game.p1.resources = 7
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Goff Boyz"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "3"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 1), 4)
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 1)
        self.assertEqual(test_game.p1.resources, 4)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_infernal_gateway(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Infernal Gateway", "Zarathur's Flamers"]
        test_game.p1.resources = 7
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 1), "Zarathur's Flamers")
        self.assertEqual(test_game.p1.cards_in_play[1][1].get_sacrifice_end_of_phase(), True)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_muster_the_guard(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Muster the Guard"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.cards = ["Cadian Mortar Squad"]
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(-2, 0), False)
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_noble_deed(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Noble Deed"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 0)
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 1)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 1)
        self.assertEqual(test_game.stored_damage[0].get_amount_that_can_be_blocked(), 1)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_to_arms(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["To Arms!"]
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Fortress-Monastery"))
        test_game.p1.exhaust_given_pos(-2, 1)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        self.assertEqual(test_game.p1.get_ready_given_pos(-2, 1), True)
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_the_emperors_warrant(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.move_unit_to_planet(0, 0, 1)
        test_game.p2.move_unit_to_planet(0, 0, 1)
        test_game.p1.cards = ["The Emperor's Warrant"]
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(test_game.p1.resources, 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 1), 2)
        self.assertEqual(test_game.stored_damage[0].get_amount_that_can_be_blocked(), 2)
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 0), False)
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 1), True)

    async def test_summary_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Summary Execution"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 1)
        self.assertEqual("green" in test_game.additional_icons_planets_eob[0], True)
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 1)

    async def test_bolster_the_defense(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.cards = ["Bolster the Defense", "Staging Ground"]
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(len(test_game.p1.headquarters), 1)
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_no_surprises(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.cards = ["No Surprises"]
        test_game.p2.put_card_into_reserve(test_game.preloaded_find_card("Vezuel's Hunters"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(len(test_game.p2.cards_in_reserve[0]), 1)
        await test_game.update_game_event("P1", ["RESERVE", "2", "0", "0"])
        self.assertEqual(len(test_game.p2.cards_in_reserve[0]), 0)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_keep_firing(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.cards = ["Keep Firing!"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Mordian Hellhound"), 0)
        test_game.p1.exhaust_given_pos(0, 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 0), True)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_our_last_stand_faith_only(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.cards = ["Our Last Stand"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Mordian Hellhound"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Mordian Hellhound"), 1)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Penal Legionnaire"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Guardsman"), 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.get_faith_given_pos(0, 0), 1)
        self.assertEqual(test_game.p1.get_faith_given_pos(1, 0), 0)
        self.assertEqual(test_game.p1.get_faith_given_pos(0, 1), 1)
        self.assertEqual(test_game.p1.get_faith_given_pos(0, 2), 0)
        self.assertEqual(test_game.p1.get_faith_given_pos(0, 3), 1)
        self.assertEqual(test_game.p1.get_faith_given_pos(-2, 0), 0)

    async def test_even_the_odds(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.cards = ["Even the Odds"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Fire Warrior Strike Team"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Fire Warrior Strike Team"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Ion Rifle"), 0, 0)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["ATTACHMENT", "IN_PLAY", "1", "0", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 0)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 1)), 1)
        self.assertEqual(test_game.p1.cards, [])
        self.assertEqual(test_game.p1.resources, 6)

if __name__ == "__main__":
    unittest.main()
