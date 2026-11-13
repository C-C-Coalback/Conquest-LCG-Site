import unittest
from play.gamecode.GameClass import Game
from play.gamecode import Initfunctions
import random
from play.gamecode.tests.deckLoading import deck_content_1, deck_content_2, ooe_deck_content, meph_deck_content, cato_deck_content, nazdreg_deck_content, eldorath_deck_content, shadowsun_deck_content, straken_deck_content, zarathur_deck_content
from play.gamecode.tests.shortcuts import skip_to_battle_first_planet, standard_setup, click_in_play, click_action, click_choice, click_attachment_in_hq, click_attachment_in_play, click_discard, click_hand, click_hq, click_pass, click_planet, click_reserve, click_search, dummy_click


card_array = Initfunctions.init_player_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()


class PassiveEffectsTest(unittest.IsolatedAsyncioTestCase):
    async def test_colonel_straken(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(straken_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 3)

    async def test_nazdreg(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(nazdreg_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        self.assertEqual(test_game.p1.get_brutal_given_pos(0, 1), True)

    async def test_zarathur(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        await click_in_play(test_game, 1, 1, 0, 1)
        await click_in_play(test_game, 1, 2, 0, 0)
        await click_pass(test_game, 2)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 3)

    async def test_iron_hands_techmarine(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
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
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Infantry Conscripts")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Promethium Mine"))
        self.assertEqual(2, test_game.p1.get_attack_given_pos(0, 0))

    async def test_bad_dok(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
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
        await test_game.p1.setup_player(zarathur_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        card = test_game.preloaded_find_card("Rokkitboy")
        test_game.p1.add_card_to_planet(card, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Raven Guard Speeder"), 0)
        self.assertEqual(test_game.p2.get_flying_given_pos(0, 0), False)

    async def test_goff_boyz(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
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
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Void Pirate"), 0)
        test_game.p2.cards = []
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.cards), 3)

    async def test_extra_resource_winnings_from_command(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [], forced_planet_array=["Barlus", "Osus IV", "Elouith", "Ferrin", "Y'varn", "Iridial", "Carnath"])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p1.resources = 7
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Rogue Trader"), 0)
        test_game.p2.cards = []
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        self.assertEqual(test_game.p1.resources, 8)
        self.assertEqual(len(test_game.p1.cards), 2)

    async def test_fire_warrior_strike_team(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Fire Warrior Strike Team"), 0)
        test_game.p1.attach_card(test_game.preloaded_find_card("Ion Rifle"), 0, 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 5)

    async def test_ambush_platform_discount(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.cards = ["Ion Rifle"]
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Fire Warrior Strike Team"), 0)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ambush Platform"))
        test_game.p1.resources = 7
        await click_hand(test_game, 1, 0)
        await click_in_play(test_game, 1, 1, 0, 0)
        self.assertEqual(len(test_game.p1.cards), 0)
        self.assertEqual(test_game.p1.resources, 7)
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)

    async def test_brood_warriors(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Brood Warriors"), 0)
        self.assertEqual(test_game.p1.get_command_given_pos(0, 0), 1)

    async def test_strangler_brood(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 1)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Strangler Brood"), 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 2)

    async def test_termagant_spikers(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        self.assertFalse(test_game.p1.get_ranged_given_pos(0, 0))
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant Spikers"), 0)
        self.assertTrue(test_game.p1.get_ranged_given_pos(0, 0))

    async def test_swarm_guard(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 1)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Swarm Guard"), 0)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 3)

    async def test_biovore_spore_launcher(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        self.assertEqual(test_game.p1.get_area_effect_given_pos(0, 0), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Biovore Spore Launcher"), 0)
        self.assertEqual(test_game.p1.get_area_effect_given_pos(0, 0), 1)

    async def test_ymgarl_genestealer(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Ymgarl Genestealer"), 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 4)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 4)
        await skip_to_battle_first_planet(test_game)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 6)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 4)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Stalking Lictor"), 0)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 0), 6)
        self.assertEqual(test_game.p1.get_health_given_pos(0, 0), 6)

    async def test_burrowing_trygon(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await standard_setup(test_game)
        test_game.p1.resources = 10
        test_game.p1.cards = ["Burrowing Trygon"]
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 1)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 1)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Termagant"), 2)
        await click_hand(test_game, 1, 0)
        await click_planet(test_game, 1, 0)
        self.assertEqual(test_game.p1.resources, 4)

    async def test_savage_warrior_prime_not_same_planet(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(ooe_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await click_choice(test_game, 1, 0)
        await click_choice(test_game, 2, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_planet(test_game, 1, 0)
        self.assertEqual(len(test_game.p1.headquarters), 2)
        await click_planet(test_game, 1, 1)
        self.assertEqual(len(test_game.p1.headquarters), 0)

    async def test_savage_warrior_prime_init_stealing(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(ooe_deck_content, test_game.planet_array)
        await standard_setup(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 1)
        await click_planet(test_game, 2, 1)
        await click_planet(test_game, 2, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.cards = []
        test_game.p2.cards = []
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        self.assertEqual(test_game.player_with_combat_turn, test_game.name_2)

    async def test_savage_warrior_prime_failed_init_stealing(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(ooe_deck_content, test_game.planet_array)
        await standard_setup(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 1)
        await click_planet(test_game, 2, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.cards = []
        test_game.p2.cards = []
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        self.assertEqual(test_game.player_with_combat_turn, test_game.name_1)

    async def test_savage_warrior_prime_battle_starting(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(ooe_deck_content, test_game.planet_array)
        await standard_setup(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_planet(test_game, 1, 0)
        await click_planet(test_game, 2, 0)
        await click_planet(test_game, 2, 1)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.cards = []
        test_game.p2.cards = []
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.retreat_unit(0, 0)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        await click_choice(test_game, 2, 1)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        self.assertEqual(test_game.last_planet_checked_for_battle, 1)
        self.assertTrue(test_game.check_if_battle_taking_place())

    async def test_mephiston(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(meph_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        await click_pass(test_game, 1)
        self.assertEqual(test_game.p1.get_retaliate_given_pos(0, 1), 1)
        await click_in_play(test_game, 2, 2, 0, 0)
        await click_choice(test_game, 2, 1)
        await click_in_play(test_game, 2, 1, 0, 1)
        await click_in_play(test_game, 1, 1, 0, 1)
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 0), 1)
        self.assertEqual(test_game.p1.count_units_at_planet(0), 1)

    async def test_roghrax_bloodhand(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(meph_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await skip_to_battle_first_planet(test_game)
        await click_pass(test_game, 1)
        await click_pass(test_game, 2)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Roghrax Bloodhand"), 0)
        test_game.p1.set_damage_given_pos(0, 2, 3)
        test_game.p1.destroy_card_in_play(0, 1)
        await dummy_click(test_game, 1)
        self.assertEqual(test_game.p1.get_attack_given_pos(0, 1), 10)

if __name__ == "__main__":
    unittest.main()
