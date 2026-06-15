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
    async def test_attack(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.stored_damage), 1)

    async def test_retreat_warlord_combat_turn(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 0)

    async def test_armorbane(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Iyanden Wraithguard"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.stored_damage[0].get_can_shield(), False)

    async def test_ranged(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ratling Deadeye"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.stored_damage), 1)
        self.assertEqual(test_game.ranged_skirmish_active, True)

    async def test_brutal(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Enraged Ork"), 0)
        test_game.p1.set_damage_given_pos(0, 1, 2)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.stored_damage), 1)
        self.assertEqual(test_game.stored_damage[0].get_amount_that_can_be_blocked(), 3)  # Zarathur +1

    async def test_area_effect(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        self.assertEqual(len(test_game.stored_damage), 2)

    async def test_area_effect_apoka(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "Apoka", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Tactical Squad Cardinis"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "2"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "3"])
        self.assertEqual(len(test_game.stored_damage), 3)

    async def test_flying(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Assault Valkyrie"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(len(test_game.stored_damage), 1)
        self.assertEqual(test_game.stored_damage[0].get_amount_that_can_be_blocked(), 2)  # Zarathur +1

    async def test_godwyn_pattern_bolter(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Assault Valkyrie"), 0)
        card = test_game.preloaded_find_card("Godwyn Pattern Bolter")
        test_game.p1.attach_card(card, 0, 1)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(len(test_game.stored_damage), 1)
        self.assertEqual(test_game.stored_damage[0].get_amount_that_can_be_blocked(), 4)  # Zarathur +1

    async def test_lumbering(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
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
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Plagueburst Crawler"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), False)

    async def test_fury_sicarius(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Vicious Bloodletter"), 0)
        test_game.p1.cards = ["The Fury of Sicarius"]
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 1)
        self.assertEqual(test_game.p1.get_resources(), 5)

    async def test_indomitable(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.cards = ["Indomitable"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        self.assertEqual(test_game.p1.get_resources(), 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 0)
        test_game.p2.ready_given_pos(0, 1)
        test_game.p1.cards = ["Indomitable"]
        await test_game.update_game_event("P1", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Infantry Conscripts"), 0)
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 1), 1)
        self.assertEqual(len(test_game.stored_damage), 0)

    async def test_glorious_intervention(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Infantry Conscripts"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Guardsman"), 0)
        test_game.p1.cards = ["Glorious Intervention"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.choice_context, "Use alternative shield effect?")
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 3)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "2"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)
        self.assertEqual(len(test_game.stored_damage), 1)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 1), 1)
        self.assertEqual(test_game.p1.get_resources(), 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 0)

    async def test_iron_halo(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Iron Halo"), 0, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["ATTACHMENT", "IN_PLAY", "1", "0", "0", "0"])
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 0)
        self.assertEqual(len(test_game.stored_damage), 0)
        self.assertEqual(test_game.p1.get_attachment_at_pos(0, 0, 0).get_ready(), False)

    async def test_vengeance(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.exhaust_given_pos(0, 1)
        test_game.p1.cards = ["Vengeance!"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "2"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.get_resources(), 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_junk_chucka_kommando(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Junk Chucka Kommando"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Rokkit Launcha"), 0, 1)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["ATTACHMENT", "IN_PLAY", "1", "0", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 1)
        self.assertEqual(len(test_game.p1.discard), 1)
        self.assertEqual(len(test_game.p2.discard), 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 1)), 0)

    async def test_honored_librarian(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        card = test_game.preloaded_find_card("Honored Librarian")
        test_game.p2.add_card_to_planet(card, 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(len(test_game.stored_damage), 0)
        test_game.p2.move_unit_at_planet_to_hq(0, 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.stored_damage), 1)

    async def test_blood_angels_veterans(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        card = test_game.preloaded_find_card("Blood Angels Veterans")
        test_game.p2.add_card_to_planet(card, 0)
        test_game.p1.add_card_to_planet(card, 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 1), 2)
        await test_game.update_game_event("P2", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["pass-P1"])
        self.assertEqual(test_game.p1.discard, ["Blood Angels Veterans"])

    async def test_bodyguard_one_bodyguard(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        card = test_game.preloaded_find_card("Blood Angels Veterans")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(card, 0)
        test_game.p2.attach_card(test_game.preloaded_find_card("Bodyguard"), 0, 1)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 2)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 1), 1)

    async def test_rockcrete(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        card = test_game.preloaded_find_card("Blood Angels Veterans")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Rockcrete Bunker"))
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P2", ["HQ", "2", "0"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 2)
        self.assertEqual(test_game.p2.get_damage_given_pos(-2, 0), 1)

    async def test_tankbusta_bommaz(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        card = test_game.preloaded_find_card("Tankbusta Bommaz")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 3)
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.ready_given_pos(0, 1)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(6, test_game.p2.get_damage_given_pos(0, 1))

    async def test_burna_boyz(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        card = test_game.preloaded_find_card("Burna Boyz")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 5)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 1), 1)

    async def test_umbral_preacher(self):
        random.seed(42)
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            cato_deck_content = file.read()
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(nazdreg_deck_content, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        card = test_game.preloaded_find_card("Umbral Preacher")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Land Raider"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 1)
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 2)


if __name__ == "__main__":
    unittest.main()
