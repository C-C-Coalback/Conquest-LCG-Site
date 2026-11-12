import unittest
from play.gamecode.GameClass import Game
from play.gamecode import Initfunctions
import random
from play.gamecode.tests.deckLoading import deck_content_1, deck_content_2, ooe_deck_content, cato_deck_content, nazdreg_deck_content, eldorath_deck_content, shadowsun_deck_content
from play.gamecode.tests.shortcuts import skip_to_battle_first_planet, standard_setup, click_choice, click_pass, click_action, click_planet, click_hand, click_hq, click_in_play, click_search, dummy_click, click_attachment_in_play, click_discard


card_array = Initfunctions.init_player_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()


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


class AutomatedElementsTest(unittest.IsolatedAsyncioTestCase):
    async def test_apoka_ae(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "Apoka", [], bot_is_present=True)
        test_game.bot_is_present = False
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.automated_1_has_passed_action = True
        test_game.automated_2_has_passed_action = True
        await click_pass(test_game, 1)
        test_game.automated_1_has_passed_action = True
        test_game.automated_2_has_passed_action = True
        await click_pass(test_game, 2)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)
        await click_planet(test_game, 1, 0)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/2", test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/3", test_game.last_automated_data_string)
        await click_in_play(test_game, 1, 2, 0, 1)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/2", test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/3", test_game.last_automated_data_string)

    async def test_ambush_army(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Eager Recruit"]
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hand(test_game, 1, 0)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_ambush_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Dire Mutation"]
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Void Pirate"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hand(test_game, 1, 0)
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)

    async def test_veteran_brother_maxos_is_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Eager Recruit"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Veteran Brother Maxos"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)

    async def test_nazdregs_gitz_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Nazdreg's Flash Gitz"), 0, already_exhausted=True)
        await dummy_click(test_game, 1)
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
        await dummy_click(test_game, 1)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)

    async def test_drop_pod_assault_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Drop Pod Assault"]
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_battle_cry_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Battle Cry"]
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_exterminatus_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Exterminatus"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Veteran Brother Maxos"), 2)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 3)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 4)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertNotIn("PLANETS/2", test_game.last_automated_data_string)
        self.assertIn("PLANETS/3", test_game.last_automated_data_string)
        self.assertIn("PLANETS/4", test_game.last_automated_data_string)

    async def test_snotling_attack_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Snotling Attack"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertEqual("GAME_INFO/AUTOMATED_DATA/Action/P1/|||PLANETS/0|||PLANETS/1|||PLANETS/2|||PLANETS/3|||PLANETS/4|||", test_game.last_automated_data_string)

    async def test_squig_bombin_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Squig Bombin'"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_ork_kannon_and_indirect(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ork Kannon"))
        await dummy_click(test_game, 1)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)
        await click_planet(test_game, 1, 0)
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        await click_in_play(test_game, 1, 1, 0, 0)
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        await click_in_play(test_game, 2, 2, 0, 0)
        self.assertEqual(test_game.what_is_required_automated, "Damage")

    async def test_tellyporta_offer_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Tellyporta Pad"))
        await dummy_click(test_game, 1)
        self.assertNotIn("HQ/1/0", test_game.last_automated_data_string)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Shoota Mob"))
        await dummy_click(test_game, 1)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("HQ/1/1", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_zarathurs_flamers_offer_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        await dummy_click(test_game, 1)
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 1)
        await dummy_click(test_game, 1)
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)

    async def test_tzeentchs_firestorm_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Tzeentch's Firestorm"]
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 1)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_splintered_path_acolyte_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Zarathur's Flamers"]
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Splintered Path Acolyte"))
        await click_hand(test_game, 1, 0)
        await click_planet(test_game, 1, 0)
        self.assertIn("HQ/1/1", test_game.last_automated_data_string)

    async def test_ravenous_flesh_hounds_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ravenous Flesh Hounds"), 0)
        await dummy_click(test_game, 1)
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p1.set_damage_given_pos(0, 1, 2)
        await dummy_click(test_game, 1)
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Chaos Fanatics"), 1)
        await dummy_click(test_game, 1)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        test_game.p1.set_damage_given_pos(0, 1, 0)
        await dummy_click(test_game, 1)
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertIn("IN_PLAY/1/1/0", test_game.last_automated_data_string)

    async def test_soul_grinder_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Soul Grinder"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 1)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_choice(test_game, 1, 0)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/1/0", test_game.last_automated_data_string)

    async def test_infernal_gateway_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Infernal Gateway"]
        await dummy_click(test_game, 1)
        print(test_game.last_automated_data_string)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.cards = ["Infernal Gateway", "Zarathur's Flamers"]
        await dummy_click(test_game, 1)
        print(test_game.last_automated_data_string)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hand(test_game, 1, 0)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_warpstorm_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Warpstorm"]
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_promise_of_glory_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Promise of Glory"]
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)

    async def test_khymera_den_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Khymera Den"))
        await dummy_click(test_game, 1)
        self.assertNotIn("SPECIAL_ACTION_HQ/1/0", test_game.last_automated_data_string)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Khymera"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Khymera"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Khymera"), 1)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Khymera"))
        await dummy_click(test_game, 1)
        self.assertIn("SPECIAL_ACTION_HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        self.assertIn("HQ/1/2", test_game.last_automated_data_string)
        self.assertNotIn("PLANETS/0", test_game.last_automated_data_string)
        await click_hq(test_game, 1, 1, 2)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        self.assertNotIn("HQ/1/2", test_game.last_automated_data_string)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_pact_of_the_haemonculi_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Pact of the Haemonculi"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Khymera"))
        await dummy_click(test_game, 1)
        print(test_game.last_automated_data_string)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertIn("HQ/1/1", test_game.last_automated_data_string)

    async def test_haemonculus_tormentor_offered(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Haemonculus Tormentor"))
        await dummy_click(test_game, 1)
        self.assertIn("SPECIAL_ACTION_HQ/1/1", test_game.last_automated_data_string)
        test_game.p1.resources = 0
        await dummy_click(test_game, 1)
        self.assertNotIn("SPECIAL_ACTION_HQ/1/1", test_game.last_automated_data_string)

    async def test_power_from_pain_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Power from Pain"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Incubus Warrior"))
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hand(test_game, 1, 0)
        self.assertIn("HQ/2/0", test_game.last_automated_data_string)

    async def test_archons_terror_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Archon's Terror"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hand(test_game, 1, 0)
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
        await dummy_click(test_game, 1)
        self.assertNotIn("HQ/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)

    async def test_eldorath_starbane_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(eldorath_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_choice(test_game, 1, 0)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)

    async def test_commander_shadowsun_execution_hand_only(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(shadowsun_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Shadowsun's Stealth Cadre"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 1, 0)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_commander_shadowsun_execution_discard_only(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(shadowsun_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.discard = ["Shadowsun's Stealth Cadre"]
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 1, 1)
        self.assertIn("IN_DISCARD/1/0", test_game.last_automated_data_string)
        await click_discard(test_game, 1, 1, 0)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_alaitoc_shrine_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Eldar Survivalist"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Alaitoc Shrine"))
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_choice(test_game, 1, 0)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)

    async def test_foresight_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Foresight"]
        test_game.p2.cards = []
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_choice(test_game, 1, 0)
        self.assertIn("PLANETS/1", test_game.last_automated_data_string)
        self.assertNotIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_wildrider_squadron_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Wildrider Squadron"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertIn("PLANETS/1", test_game.last_automated_data_string)
        self.assertNotIn("PLANETS/2", test_game.last_automated_data_string)

    async def test_wailing_wraithfighter_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p2.cards = ["No Mercy", "No Mercy"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Wailing Wraithfighter"), 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_in_play(test_game, 1, 1, 0, 1)
        await click_choice(test_game, 1, 0)
        self.assertIn("HAND/2/0", test_game.last_automated_data_string)

    async def test_spiritseer_erathal_no_damage(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Spiritseer Erathal"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Wailing Wraithfighter"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Wailing Wraithfighter"), 0)
        test_game.p1.set_damage_given_pos(0, 2, 1)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_in_play(test_game, 1, 1, 0, 1)
        await click_choice(test_game, 1, 0)
        self.assertIn("IN_PLAY/1/0/2", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/3", test_game.last_automated_data_string)


    async def test_shrouded_harlequin_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shrouded Harlequin"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Shrouded Harlequin"), 0)
        await dummy_click(test_game, 1)
        test_game.p1.destroy_card_in_play(0, 0)
        await dummy_click(test_game, 1)
        await click_choice(test_game, 1, 0)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        self.assertNotIn("HQ/2/0", test_game.last_automated_data_string)

    async def test_spiritseer_erathal_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Spiritseer Erathal"), 0)
        test_game.p1.set_damage_given_pos(0, 0, 1)
        test_game.p1.set_damage_given_pos(0, 1, 1)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_in_play(test_game, 1, 1, 0, 1)
        await click_choice(test_game, 1, 0)
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)

    async def test_army_units_as_attachs_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Shadowsun's Stealth Cadre", "Gun Drones"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        await dummy_click(test_game, 1)
        await click_hand(test_game, 1, 0)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 1)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_superiority(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Superiority"]
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 1)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        await click_choice(test_game, 1, 0)
        self.assertIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/1/0", test_game.last_automated_data_string)
        await click_in_play(test_game, 1, 2, 0, 0)
        await click_pass(test_game, 1)
        self.assertIn("P2", test_game.last_automated_data_string)

    async def test_nullify(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(eldorath_deck_content, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Promise of Glory"]
        test_game.p2.cards = ["Nullify"]
        await click_hand(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        self.assertIn("HQ/2/0", test_game.last_automated_data_string)

    async def test_gift_of_isha_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Gift of Isha"]
        test_game.p1.discard = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.discard = ["Starbane's Council"]
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hand(test_game, 1, 0)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_banshee_power_sword_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.cards = ["Gift of Isha"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Banshee Power Sword"), 0, 1)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_in_play(test_game, 1, 1, 0, 1)
        await click_choice(test_game, 1, 0)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        self.assertIn("pass-P1", test_game.last_automated_data_string)

    async def test_craftworld_gate_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Craftworld Gate"))
        await dummy_click(test_game, 1)
        self.assertNotIn("SPECIAL_ACTION_HQ/1/0", test_game.last_automated_data_string)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("SPECIAL_ACTION_HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_squadron_redeployment_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Squadron Redeployment"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.attach_card(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0, 0)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        await click_in_play(test_game, 1, 1, 0, 0)
        self.assertIn("PLANETS/1", test_game.last_automated_data_string)
        self.assertNotIn("PLANETS/0", test_game.last_automated_data_string)

    async def test_command_link_drone_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Command-link Drone"), 0, 0)
        await dummy_click(test_game, 1)
        self.assertIn("SPECIAL_ACTION_ATTACHMENT/IN_PLAY/1/0/0/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_attachment_in_play(test_game, 1, 1, 0, 0, 0)
        print(test_game.last_automated_data_string)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_friendly_even_the_odds_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p1.cards = ["Even the Odds"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.attach_card(test_game.preloaded_find_card("Ion Rifle"), 0, 0)
        test_game.p2.attach_card(test_game.preloaded_find_card("Ion Rifle"), 0, 0)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertIn("ATTACHMENT/IN_PLAY/1/0/0/0", test_game.last_automated_data_string)
        self.assertNotIn("ATTACHMENT/IN_PLAY/2/0/0/0", test_game.last_automated_data_string)
        await click_attachment_in_play(test_game, 1, 1, 0, 0, 0)
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        self.assertNotIn("HQ/1/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)

    async def test_unfriendly_even_the_odds_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p1.cards = ["Even the Odds"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p1.attach_card(test_game.preloaded_find_card("Ion Rifle"), 0, 0)
        test_game.p2.attach_card(test_game.preloaded_find_card("Ion Rifle"), 0, 0)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertNotIn("ATTACHMENT/IN_PLAY/1/0/0/0", test_game.last_automated_data_string)
        self.assertIn("ATTACHMENT/IN_PLAY/2/0/0/0", test_game.last_automated_data_string)
        await click_attachment_in_play(test_game, 1, 2, 0, 0, 0)
        print(test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)
        self.assertNotIn("HQ/2/0", test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)

    async def test_calculated_strike_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Calculated Strike"]
        test_game.p2.cards = []
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertIn("HQ/2/0", test_game.last_automated_data_string)

    async def test_crushface_insuff_resources_other_planets(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Burna Boyz"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Crushface"), 0)
        test_game.p1.resources = 3
        await click_hand(test_game, 1, 0)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)
        self.assertNotIn("PLANETS/1", test_game.last_automated_data_string)

    async def test_standard_deployment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Burna Boyz"]
        test_game.p2.cards = []
        test_game.p1.resources = 7
        await click_hand(test_game, 1, 0)
        self.assertIn("PLANETS/0", test_game.last_automated_data_string)
        self.assertIn("PLANETS/1", test_game.last_automated_data_string)

    async def test_deception_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Deception"]
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Ultramarines Dreadnought"), 0)
        await dummy_click(test_game, 1)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("10th Company Scout"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        self.assertIn("IN_PLAY/2/0/1", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/2/0/0", test_game.last_automated_data_string)

    async def test_ambush_platform_offered_and_execution(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ambush Platform"))
        test_game.p1.cards = ["Ion Rifle"]
        await dummy_click(test_game, 1)
        self.assertNotIn("HQ/1/0", test_game.last_automated_data_string)
        test_game.p1.cards = ["Ion Rifle", "Command-link Drone"]
        await dummy_click(test_game, 1)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("HAND/1/1", test_game.last_automated_data_string)
        self.assertNotIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 1)
        self.assertIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)
        await click_in_play(test_game, 1, 1, 0, 0)
        test_game.p1.ready_given_pos(-2, 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        await dummy_click(test_game, 1)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)

    async def test_ambush_platform_discounts_issue(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], bot_is_present=True)
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ambush Platform"))
        test_game.p1.cards = ["Shadowsun's Stealth Cadre"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Incubus Warrior"), 0)
        test_game.p1.resources = 0
        await dummy_click(test_game, 1)
        self.assertNotIn("HQ/1/0", test_game.last_automated_data_string)
        test_game.p1.resources = 1
        await dummy_click(test_game, 1)
        self.assertIn("HQ/1/0", test_game.last_automated_data_string)
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertIn("HAND/1/0", test_game.last_automated_data_string)
        await click_hand(test_game, 1, 0)
        print(test_game.last_automated_data_string)
        self.assertIn("IN_PLAY/1/0/1", test_game.last_automated_data_string)
        self.assertNotIn("IN_PLAY/1/0/0", test_game.last_automated_data_string)


