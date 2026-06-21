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

with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
    cato_deck_content = file.read()


class InterruptsTest(unittest.IsolatedAsyncioTestCase):
    async def test_enginseer_augur(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.deck = ["Catachan Outpost"]
        for _ in range(10):
            test_game.p1.deck.append("Promethium Mine")
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Enginseer Augur"), 0)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["SEARCH", "1"])
        await test_game.update_game_event("P1", ["SEARCH", "0"])
        self.assertEqual(len(test_game.p1.headquarters), 2)
        self.assertEqual(test_game.p1.get_ability_given_pos(-2, 1), "Catachan Outpost")

    async def test_superiority(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        test_game.p1.cards = ["Superiority"]
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Rogue Trader"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(test_game.p2.cards_in_play[1][1].hit_by_superiority, True)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.after_command_struggle, True)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p2.cards), 0)
        self.assertEqual(test_game.p2.resources, 7)

    async def test_shrouded_harlequin(self):
        # FIXME: MAKE SHROUDED HARLEQUIN AN ACTUAL INTERRUPT INSTEAD OF A REACTION
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        card = test_game.preloaded_find_card("Shrouded Harlequin")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(card, 1)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "1", "0"])
        self.assertEqual(test_game.p2.get_ready_given_pos(1, 0), False)

    async def test_nullify_event_action(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Raid"]
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Spiritseer Erathal"), 0)
        test_game.p2.cards = ["Nullify"]
        test_game.p1.resources = 6
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 0), False)
        self.assertEqual(test_game.p1.cards, [])
        self.assertEqual(test_game.p2.cards, [])
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(test_game.p2.resources, 7)
        self.assertEqual(test_game.mode, "Normal")
        self.assertEqual(test_game.player_with_deploy_turn, "P2")
        self.assertEqual(test_game.p1.discard, ["Raid"])
        self.assertEqual(test_game.p2.discard, ["Nullify"])

    async def test_nullify_event_reaction(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        test_game.p1.cards = ["Contaminated Convoys", "No Mercy", "No Mercy", "No Mercy", "Indomitable", "Indomitable", "Indomitable"]
        test_game.p2.cards = ["Nullify", "No Mercy", "No Mercy", "No Mercy", "Indomitable", "Indomitable", "Indomitable"]
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Spiritseer Erathal"), 0)
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        await test_game.update_game_event("P2", ["CHOICE", "1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 0), False)
        self.assertEqual(len(test_game.p1.cards), 6)
        self.assertEqual(len(test_game.p2.cards), 6)
        self.assertEqual(test_game.p1.contaminated_convoys, False)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(test_game.p2.resources, 7)
        self.assertEqual(test_game.p1.discard, ["Contaminated Convoys"])
        self.assertEqual(test_game.p2.discard, ["Nullify"])

    async def test_nullify_event_pseudo_interrupt(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Spiritseer Erathal"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        test_game.p1.cards = ["Superiority"]
        test_game.p2.cards = ["Nullify"]
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Rogue Trader"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 0), False)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p2.cards), 0)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(test_game.p2.resources, 7)
        self.assertEqual(test_game.p1.discard, ["Superiority"])
        self.assertEqual(test_game.p2.discard, ["Nullify"])

    async def test_nullify_event_interrupt(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Spiritseer Erathal"), 0)
        test_game.p1.cards = ["No Mercy"]
        test_game.p2.cards = ["Nullify", "Indomitable"]
        test_game.p2.assign_damage_to_pos(0, 0, 1)
        await test_game.update_game_event("P2", [])
        await test_game.update_game_event("P2", ["HAND", "2", "1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        # FIXME: MISSING REQUIRED EXHAUSTION DUE TO NULLIFY FIRING FIRST
        # await test_game.update_game_event_action("P1", ["HQ", "1", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P2", ["HAND", "2", "0"])  # FIXME: SHOULD NOT REQUIRE THIS EXTRA STEP
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 0), False)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p2.cards), 0)
        # self.assertEqual(test_game.p1.get_ready_given_pos(-2, 0), False)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 0)

    async def test_communications_relay(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Communications Relay"))
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0, 0)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Inquisitorial Fortress"))
        test_game.p2.cards = []
        test_game.p1.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["action-button"])
        await test_game.update_game_event("P2", ["HQ", "2", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "0"])
        print(len(test_game.p1.cards_in_play[1]))
        print(test_game.choices_available)
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        self.assertEqual(test_game.p1.get_ready_given_pos(-2, 1), False)
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 1)
        self.assertEqual(test_game.mode, "Normal")

    async def test_carnivore_pack(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Carnivore Pack"), 0)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.resources, 10)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Carnivore Pack"))
        test_game.p1.destroy_card_in_play(-2, 1)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.resources, 13)

    async def test_fireblade_kaisvre(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Ion Rifle", "Promotion"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Fireblade Kais'vre"), 0)
        test_game.p1.assign_damage_to_pos(0, 0, 2)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 0)
        test_game.p1.assign_damage_to_pos(0, 0, 2)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 1)


if __name__ == "__main__":
    unittest.main()
