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

    async def test_area_effect_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Vicious Bloodletter"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Predatory Instinct"), 0, 0)
        self.assertEqual(test_game.p1.get_area_effect_given_pos(0, 0), 4)

    async def test_sweep_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.attach_card(test_game.preloaded_find_card("The Dawn Blade"), -2, 0)
        self.assertEqual(test_game.p1.get_sweep_given_pos(-2, 0), 1)

    async def test_mobile_granting_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Mobility"), 0, 0)
        self.assertEqual(test_game.p1.get_mobile_given_pos(0, 0), True)

    async def test_wargear_attachment_fail_on_vehicles(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Experimental Devilfish"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Godwyn Pattern Bolter"), 0, 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Godwyn Pattern Bolter"), 0, 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 0)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 1)), 1)

    async def test_required_trait_for_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Experimental Devilfish"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Drone Defense System"), 0, 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Drone Defense System"), 0, 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 1)), 0)

    async def test_limit_one_per_unit_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ripper Swarm"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Regeneration"), 0, 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Regeneration"), 0, 0)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)

    async def test_required_unit_faction_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Void Pirate"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Warriors of Gidrim"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Gauss Flayer"), 0, 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Gauss Flayer"), 0, 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 0)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 1)), 1)

    async def test_required_card_type_of_unit_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ripper Swarm"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Regeneration"), 0, 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Regeneration"), 0, 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 1)), 0)

    async def test_deploy_attachment_to_planet(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Slaanesh's Temptation"]
        test_game.p2.cards = []
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["PLANETS", "4"])
        self.assertEqual(test_game.p1.get_resources(), 5)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(len(test_game.p1.attachments_at_planet[4]), 1)

    async def test_strakens_cunning(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ripper Swarm"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Straken's Cunning"), 0, 0)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.p1.cards), 3)
        test_game.p1.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ripper Swarm"))
        test_game.p1.attach_card(test_game.preloaded_find_card("Straken's Cunning"), -2, 1)
        test_game.p1.destroy_card_in_play(-2, 1)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.p1.cards), 3)

    async def test_cybork_body(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ripper Swarm"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Cybork Body"), 0, 0)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 2)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Enraged Ork"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Cybork Body"), 0, 1)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 1), 10)

    async def test_mark_of_chaos(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Mark of Chaos"), 0, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.stored_damage), 2)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 1)

    async def test_dire_mutation(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Dire Mutation"), 0, 0)
        test_game.p1.exhaust_given_pos(0, 0)
        await test_game.update_game_event("P1", [])
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 1)

    async def test_agonizer_of_bren(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Agonizer of Bren"), 0, 0)
        card = test_game.preloaded_find_card("Khymera")
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 2)
        test_game.p1.add_to_hq(card)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 3)
        test_game.p1.add_card_to_planet(card, 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 4)
        test_game.p1.add_card_to_planet(card, 1)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 5)

    async def test_hypex_injector(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = ["Raid"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Baleful Mandrake"), 0)
        test_game.p1.exhaust_given_pos(0, 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Hypex Injector"), 0, 0)
        test_game.p1.resources = 6
        test_game.p2.resources = 7
        await test_game.update_game_event("P1", ["action-button"])
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 0), True)

    async def test_shadowsuns_stealth_cadre(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0, 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 4)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 4)

    async def test_gun_drones(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Gun Drones"), 0, 0)
        self.assertEqual(test_game.p1.get_area_effect_given_pos(0, 0), 2)

    async def test_escort_drone(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shadowsun's Stealth Cadre"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Escort Drone"), 0, 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 4)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 3)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 0), "Escort Drone")
        test_game.p1.cards_in_play[1][0].print_info()


if __name__ == "__main__":
    unittest.main()
