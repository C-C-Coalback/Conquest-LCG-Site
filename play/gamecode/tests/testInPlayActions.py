import unittest
from play.gamecode.GameClass import Game
from play.gamecode import Initfunctions
import random
from play.gamecode.tests.deckLoading import deck_content_1, deck_content_2, imotekh_deck_content, ooe_deck_content, cato_deck_content, nazdreg_deck_content, eldorath_deck_content, shadowsun_deck_content
from play.gamecode.tests.shortcuts import skip_to_battle_first_planet, standard_setup, click_action, click_planet, click_hand, click_hq, click_in_play, click_attachment_in_play, click_choice, click_pass, click_discard


card_array = Initfunctions.init_player_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()


class InPlayActionsTest(unittest.IsolatedAsyncioTestCase):
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
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        await click_hand(test_game, 1, 0)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 3)

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
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
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
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        await click_in_play(test_game, 1, 1, 0, 2)
        await click_in_play(test_game, 1, 2, 0, 1)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 2)
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 1), False)
        self.assertEqual(test_game.p1.get_once_per_phase_used_given_pos(0, 1), True)

    async def test_zarathurs_flamers(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 0)
        await click_in_play(test_game, 1, 2, 0, 0)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 0)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 2)

    async def test_haemonculus_tormentor(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_2, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Haemonculus Tormentor"))
        test_game.p1.resources = 7
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(test_game.p1.get_attack_given_pos(-2, 0), 4)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Haemonculus Tormentor"), 0)
        test_game.p1.resources = 7
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertEqual(test_game.p1.resources, 6)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 4)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
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
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 1, 0)
        await click_planet(test_game, 1, 0)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 2)
        self.assertEqual(test_game.p1.get_once_per_phase_used_given_pos(0, 1), True)

    async def test_ravenous_flesh_hounds(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ravenous Flesh Hounds"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Cultist"), 0)
        test_game.p1.set_damage_given_pos(0, 0, 3)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 0)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 1)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 0)

    async def test_awakening_cavern(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ripper Swarm"), 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.exhaust_given_pos(0, 0)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Awakening Cavern"))
        await click_action(test_game, 1)
        await click_hq(test_game, 1, 1, 0)
        await click_in_play(test_game, 1, 1, 0, 0)
        self.assertFalse(test_game.p1.get_ready_given_pos(-2, 0))
        self.assertTrue(test_game.p1.get_ready_given_pos(0, 0))

    async def test_hunter_gargoyles(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Hunter Gargoyles"), 3)
        test_game.infest_planet(0, test_game.p1)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 3, 0)
        await click_planet(test_game, 1, 1)
        await click_planet(test_game, 1, 0)
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 1), "Hunter Gargoyles")

    async def test_virulent_spore_sacs(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Virulent Spore Sacs"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Blood Angels Veterans"), 0)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertEqual(len(test_game.stored_damage), 2)
        self.assertTrue(test_game.infested_planets[0])

    async def test_imotekh_army(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(imotekh_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game, necron_1=True)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Flayed Ones Pack"), 0)
        test_game.p1.discard = ["White Scars Bikers"]
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 0)
        await click_discard(test_game, 1, 1, 0)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 1), "White Scars Bikers")
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 5)

    async def test_imotekh_attachment(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(imotekh_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game, necron_1=True)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Flayed Ones Pack"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Dynastic Weaponry"), 0, 1)
        test_game.p1.discard = ["Gauss Flayer"]
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 0)
        await click_discard(test_game, 1, 1, 0)
        await click_attachment_in_play(test_game, 1, 1, 0, 1, 0)
        await click_action(test_game, 1)
        await click_attachment_in_play(test_game, 1, 1, 0, 1, 0)
        self.assertFalse(test_game.p1.get_ready_given_pos(0, 1))

    async def test_imotekh_support(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(imotekh_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game, necron_1=True)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        test_game.p1.discard = ["Eternity Gate"]
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 0, 0)
        await click_discard(test_game, 1, 1, 0)
        await click_hq(test_game, 1, 1, 0)
        self.assertEqual(test_game.p1.get_ability_given_pos(-2, 0), "Eternity Gate")

    async def test_boss_zugnog(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(nazdreg_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Boss Zugnog"), 3)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Enraged Ork"), 3)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Enraged Ork"), 3)
        await click_action(test_game, 1)
        await click_in_play(test_game, 1, 1, 3, 0)
        await click_in_play(test_game, 1, 1, 3, 0)
        await click_in_play(test_game, 1, 1, 3, 1)
        self.assertEqual(test_game.p1.count_units_at_planet(3), 1)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 3)
        self.assertEqual(len(test_game.stored_damage), 2)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 1), 1)
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 2), 1)
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 1), "Boss Zugnog")
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 2), "Enraged Ork")


if __name__ == "__main__":
    unittest.main()
