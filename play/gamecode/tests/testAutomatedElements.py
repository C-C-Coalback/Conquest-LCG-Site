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
eldorath_deck_location = os.path.join(current_dir, "decksForTests/StarbaneCore.txt")
shadowsun_deck_location = os.path.join(current_dir, "decksForTests/ShadowsunCore.txt")

with open(first_deck_location, 'r') as file:
    deck_content_1 = file.read()
with open(second_deck_location, 'r') as file:
    deck_content_2 = file.read()
with open(eldorath_deck_location, 'r') as file:
    eldorath_deck_content = file.read()
with open(shadowsun_deck_location, 'r') as file:
    shadowsun_deck_content = file.read()


# IMPORTANT: How automated combat turn actions work
# There are not dedicated action windows during combat turns, as passing through these
# repeatedly is frustrating for both players. Bots can communicate their combat turn action window status by sending
# "AUTOMATED_SPECIAL_ACTION_CHOICE/{name_player}/{choice_content}" instead of the usual "SPECIAL_ACTION" indicator.
# Bots can tell if they are in a combat turn action window if they receive "Action Window Between Combat Turns" in AUTOMATED_DATA.
# e.g. to pass a combat turn action window: "AUTOMATED_SPECIAL_ACTION_CHOICE/P1/pass-P1"
# to take an action: "AUTOMATED_SPECIAL_ACTION_CHOICE/P1/HAND/1/0"
#
# This approach will not work when there is one human and one bot. At that point we will need dedicated action windows,
# or a "bot wants to take action, do you want to take one first?" choice. But that is a future problem.
#
# The main advantage of this approach is processing speed, as we avoid the computationally heavy game update loop;
# especially important as 99% of the time we don't want to take an action. This lets me train my models faster.


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

    async def test_exterminatus_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Exterminatus"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_snotling_attack_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Snotling Attack"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual("GAME_INFO/AUTOMATED_DATA/Action/P1/|||PLANETS/0|||PLANETS/1|||PLANETS/2|||PLANETS/3|||PLANETS/4|||", test_game.last_automated_data_string)

    async def test_squig_bombin_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Squig Bombin'"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        # await test_game.update_game_event("P1", ["HAND", "1", "0"])

    async def test_ork_kannon_and_indirect(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ork Kannon"))
        await test_game.update_game_event("P1", [])
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.what_is_required_automated, "Damage")

    async def test_tellyporta_offer_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Tellyporta Pad"))
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HQ/1/0", test_game.last_automated_data_string)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Shoota Mob"))
        await test_game.update_game_event("P1", [])
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        self.assertIn("HQ/1/1", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_zarathurs_flamers_offer_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        await test_game.update_game_event("P1", [])
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 1)
        await test_game.update_game_event("P1", [])
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 0)
        await test_game.update_game_event("P1", [])
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)

    async def test_tzeentchs_firestorm_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Tzeentch's Firestorm"]
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 1)
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_splintered_path_acolyte_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Zarathur's Flamers"]
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Splintered Path Acolyte"))
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertIn("HQ/1/1", test_game.last_automated_data_string)

    async def test_ravenous_flesh_hounds_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ravenous Flesh Hounds"), 0)
        await test_game.update_game_event("P1", [])
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p1.set_damage_given_pos(0, 1, 2)
        await test_game.update_game_event("P1", [])
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Chaos Fanatics"), 1)
        await test_game.update_game_event("P1", [])
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p1.set_damage_given_pos(0, 1, 0)
        await test_game.update_game_event("P1", [])
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertIn("IN_PLAY/1/1/0", test_game.last_automated_data_string)

    async def test_soul_grinder_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Soul Grinder"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 1)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/1/0", test_game.last_automated_data_string)

    async def test_infernal_gateway_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Infernal Gateway"]
        await test_game.update_game_event("P1", [])
        print(test_game.last_automated_data_string)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.cards = ["Infernal Gateway", "Zarathur's Flamers"]
        await test_game.update_game_event("P1", [])
        print(test_game.last_automated_data_string)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_warpstorm_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Warpstorm"]
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_promise_of_glory_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Promise of Glory"]
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_khymera_den_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Khymera Den"))
        await test_game.update_game_event("P1", [])
        self.assertNotIn("SPECIAL_ACTION_HQ/1/1", test_game.last_automated_data_string)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Khymera"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Khymera"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Khymera"), 1)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Khymera"))
        await test_game.update_game_event("P1", [])
        self.assertIn("SPECIAL_ACTION_HQ/1/1", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        self.assertIn("HQ/1/2", test_game.last_automated_data_string)
        self.assertNotIn("PLANETS/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["HQ", "1", "2"])
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        self.assertNotIn("HQ/1/2", test_game.last_automated_data_string)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_pact_of_the_haemonculi_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Pact of the Haemonculi"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Khymera"))
        await test_game.update_game_event("P1", [])
        print(test_game.last_automated_data_string)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertIn("HQ/1/1", test_game.last_automated_data_string)

    async def test_haemonculus_tormentor_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Haemonculus Tormentor"))
        await test_game.update_game_event("P1", [])
        self.assertIn("SPECIAL_ACTION_HQ/1/1", test_game.last_automated_data_string)
        test_game.p1.resources = 0
        await test_game.update_game_event("P1", [])
        self.assertNotIn("SPECIAL_ACTION_HQ/1/1", test_game.last_automated_data_string)

    async def test_power_from_pain_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Power from Pain"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Incubus Warrior"))
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertIn("HQ/2/0", test_game.last_automated_data_string)

    async def test_archons_terror_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Archon's Terror"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await test_game.update_game_event("P1", [])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)

    async def test_twisted_laboratory_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Twisted Laboratory"))
        await test_game.update_game_event("P1", [])
        self.assertNotIn("HQ/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await test_game.update_game_event("P1", [])
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)

    async def test_eldorath_starbane_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(eldorath_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)

    async def test_commander_shadowsun_execution_hand_only(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(shadowsun_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Shadowsun's Stealth Cadre"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_commander_shadowsun_execution_discard_only(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(shadowsun_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.discard = ["Shadowsun's Stealth Cadre"]
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        self.assertIn("IN_DISCARD/1/0", test_game.last_automated_data_string)
        await test_game.update_game_event("P1", ["IN_DISCARD", "1", "0"])
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_alaitoc_shrine_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Eldar Survivalist"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Alaitoc Shrine"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)

    async def test_foresight_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Foresight"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertIn("PLANETS/1", test_game.last_automated_data_string)
        self.assertNotIn("PLANETS/0", test_game.last_automated_data_string)