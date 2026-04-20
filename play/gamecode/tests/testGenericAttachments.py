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


class GenericAttachmentsTest(unittest.IsolatedAsyncioTestCase):
    async def test_deploy_attachment_to_own_in_play(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Godwyn Pattern Bolter"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_deploy_attachment_to_enemy_in_play(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Godwyn Pattern Bolter"]
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(len(test_game.p2.get_all_attachments_at_pos(0, 0)), 1)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_deploy_attachment_to_own_hq(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Godwyn Pattern Bolter"]
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Eager Recruit"))
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "1"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(-2, 1)), 1)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_deploy_attachment_to_enemy_hq(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Godwyn Pattern Bolter"]
        test_game.p2.cards = []
        test_game.p2.add_to_hq(test_game.preloaded_find_card("Eager Recruit"))
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "2", "1"])
        self.assertEqual(len(test_game.p2.get_all_attachments_at_pos(-2, 1)), 1)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_attachment_extra_health(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Godwyn Pattern Bolter"), 0, 0)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 2)
        test_game.p1.attach_card(test_game.preloaded_find_card("Hostile Environment Gear"), 0, 0)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 5)

    async def test_attachment_extra_attack(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Godwyn Pattern Bolter"), 0, 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 3)
        test_game.p1.attach_card(test_game.preloaded_find_card("Hot-Shot Laspistol"), 0, 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 5)

    async def test_attachment_extra_command(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Promotion"), 0, 0)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 2)

    async def test_unique_unit_only_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Tallassarian Tempest Blade"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 0)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(-2, 0)), 1)

    async def test_armorbane_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Tallassarian Tempest Blade"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["HQ", "1", "0"])
        self.assertEqual(test_game.p1.get_armorbane_given_pos(-2, 0), True)

    async def test_ranged_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Rokkit Launcha"), 0, 0)
        self.assertEqual(test_game.p1.get_ranged_given_pos(0, 0), True)

    async def test_flying_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Valkyris Pattern Jump Pack"), 0, 0)
        self.assertEqual(test_game.p1.get_flying_given_pos(0, 0), True)

    async def test_retaliate_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Vitarus, the Sanguine Sword"), 0, 0)
        self.assertEqual(test_game.p1.get_retaliate_given_pos(0, 0), 3)

    async def test_lumbering_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Centurion Warsuit"), 0, 0)
        self.assertEqual(test_game.p1.get_lumbering_given_pos(0, 0), True)

    async def test_immune_to_enemy_events_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Lucky Warpaint"), 0, 0)
        self.assertEqual(test_game.p1.get_immune_to_enemy_events(0, 0), True)

    async def test_additional_traits_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Lucky Warpaint"), 0, 0)
        self.assertEqual(test_game.p1.check_for_trait_given_pos(0, 0, "Blue"), True)

