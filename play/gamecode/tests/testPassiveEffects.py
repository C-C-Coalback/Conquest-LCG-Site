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


class PassiveEffectsTest(unittest.IsolatedAsyncioTestCase):
    async def test_colonel_straken(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/StrakenCore.txt')) as file:
            straken_deck_content = file.read()
        await test_game.p1.setup_player(straken_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 3)

    async def test_nazdreg(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
            nazdreg_deck_content = file.read()
        await test_game.p1.setup_player(nazdreg_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        self.assertEqual(test_game.p1.get_brutal_given_pos(0, 1), True)

    async def test_zarathur(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
            zarathur_deck_content = file.read()
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 3)

    async def test_iron_hands_techmarine(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
            zarathur_deck_content = file.read()
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Iron Hands Techmarine")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(card, 0)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 2)
        test_game.p2.add_card_to_planet(card, 0)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 3)
        card = test_game.preloaded_find_card("Cultist")
        test_game.p2.add_card_to_planet(card, 0)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 4)

    async def test_infantry_conscripts(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
            zarathur_deck_content = file.read()
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Infantry Conscripts")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        self.assertEqual(2, test_game.p1.get_attack_given_pos(0, 0))

    async def test_bad_dok(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
            zarathur_deck_content = file.read()
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Bad Dok")
        test_game.p1.add_card_to_planet(card, 0)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 1)
        test_game.p1.increase_damage_at_pos(0, 0, 1)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 4)

    async def test_rokkitboy(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
            zarathur_deck_content = file.read()
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Rokkitboy")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Raven Guard Speeder"), 0)
        self.assertEqual(test_game.p2.get_flying_given_pos(0, 0), False)

    async def test_goff_boyz(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
            zarathur_deck_content = file.read()
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Goff Boyz")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p1.add_card_to_planet(card, 1)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 3)
        self.assertEqual(test_game.p1.get_attack_given_pos(1, 0), 0)

    async def test_virulent_plague_squad(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
            zarathur_deck_content = file.read()
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Virulent Plague Squad")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.discard = ["Zarathur's Flamers", "Promise of Glory"]
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 2)
        test_game.p2.discard.append("Zarathur's Flamers")
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 3)

    async def test_extra_card_winnings_from_command(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], forced_planet_array=["Barlus", "Osus IV", "Elouith", "Ferrin", "Y'varn", "Iridial", "Carnath"])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Void Pirate"), 0)
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 3)

    async def test_extra_resource_winnings_from_command(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], forced_planet_array=["Barlus", "Osus IV", "Elouith", "Ferrin", "Y'varn", "Iridial", "Carnath"])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p1.resources = 7
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Rogue Trader"), 0)
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.p1.resources, 8)
        self.assertEqual(len(test_game.p1.cards), 2)

    async def test_fire_warrior_strike_team(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], forced_planet_array=["Barlus", "Osus IV", "Elouith", "Ferrin", "Y'varn", "Iridial", "Carnath"])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Fire Warrior Strike Team"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Ion Rifle"), 0, 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 5)


if __name__ == "__main__":
    unittest.main()