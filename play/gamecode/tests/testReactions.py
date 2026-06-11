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


class StandardTest(unittest.IsolatedAsyncioTestCase):
    async def test_experimental_devilfish(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Experimental Devilfish"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_captain_cato_sicarius(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.move_unit_to_planet(-2, 0, 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Shoota Mob"), 0)
        test_game.p2.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_resources(), 8)

    async def test_sicarius_chosen(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Sicarius's Chosen"), 1)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(len(test_game.p2.cards_in_play[1]), 0)
        self.assertEqual(len(test_game.p2.cards_in_play[2]), 1)
        self.assertEqual(test_game.p2.get_damage_given_pos(1, 0), 1)

    async def test_cato_stronghold(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(cato_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Void Pirate"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Rogue Trader"), 0)
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Cato's Stronghold"))
        test_game.p1.exhaust_given_pos(0, 0)
        test_game.p1.exhaust_given_pos(0, 1)
        test_game.p2.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "1"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 0), False)
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_ardent_auxiliaries(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ardent Auxiliaries"))
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Infantry Conscripts"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_ardent_auxiliaries_apoka(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "Apoka", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ardent Auxiliaries"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), True)

    async def test_ardent_auxiliaries_apokaless(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        await test_game.p1.setup_player(deck_content_1, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Ardent Auxiliaries"))
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ready_given_pos(0, 1), False)

    async def test_packmaster_kith(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/KithCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.p1.cards_in_play[1]), 2)

    async def test_eldorath_starbane(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/StarbaneCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        self.assertEqual(test_game.p2.get_ready_given_pos(0, 0), False)

    async def test_commander_shadowsun_hand(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ShadowsunCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.cards = ["Shadowsun's Stealth Cadre"]
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.choice_context, "Shadowsun plays attachment from hand or discard?")
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.reactions_needing_resolving), 1)
        self.assertEqual(test_game.choices_available, [])
        self.assertEqual(test_game.reactions_needing_resolving[0].get_reaction_name(), "Commander Shadowsun hand")
        await test_game.update_game_event("P1", ["HAND", "1", "0"])
        self.assertEqual(test_game.location_hand_attachment_shadowsun, 0)
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)
        self.assertEqual(len(test_game.p1.cards), 0)

    async def test_commander_shadowsun_discard(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ShadowsunCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.discard = ["Shadowsun's Stealth Cadre"]
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["CHOICE", "1"])
        await test_game.update_game_event("P1", ["IN_DISCARD", "1", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        self.assertEqual(len(test_game.p1.get_all_attachments_at_pos(0, 0)), 1)
        self.assertEqual(len(test_game.p1.discard), 0)

    async def test_strakens_cunning(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ShadowsunCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Eager Recruit"), 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.attach_card(test_game.preloaded_find_card("Straken's Cunning"), 0, 0)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(len(test_game.p1.cards), 3)

    async def test_blood_angels_veterans(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ShadowsunCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Blood Angels Veterans"), 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.assign_damage_to_pos(0, 0, 3)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 2)
        test_game.p1.exhaust_given_pos(0, 0)
        test_game.p1.set_damage_given_pos(0, 0, 0)
        test_game.p1.assign_damage_to_pos(0, 0, 2)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "1", "0", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        self.assertEqual(test_game.p1.get_damage_given_pos(0, 0), 2)

    async def test_holy_sepulchre(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ShadowsunCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Blood Angels Veterans"), 0)
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_to_hq(test_game.preloaded_find_card("Holy Sepulchre"))
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_DISCARD", "1", "0"])
        self.assertEqual(len(test_game.p1.cards), 1)
        self.assertEqual(len(test_game.p1.discard), 0)

    async def test_veteran_barbrus(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/ShadowsunCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Chaos Fanatics"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Goff Nob"), 0)
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Veteran Barbrus"), 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "0"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "0", "1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.p2.get_damage_given_pos(0, 1), 2)

    async def test_drifting_spore_mines(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Drifting Spore Mines"), 0)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Zarathur's Flamers"), 1)
        test_game.p2.add_card_to_planet(test_game.preloaded_find_card("Veteran Brother Maxos"), 1)
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["PLANETS", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P2", ["pass-P1"])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["PLANETS", "1"])
        self.assertEqual(test_game.choice_context, "Damage Drifting Spore Mines?")
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P1", ["pass-P1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "1", "1"])
        await test_game.update_game_event("P1", ["IN_PLAY", "2", "1", "0"])
        await test_game.update_game_event("P2", ["pass-P1"])
        self.assertEqual(test_game.p2.get_damage_given_pos(1, 0), 1)
        self.assertEqual(test_game.p2.get_damage_given_pos(1, 1), 0)
        self.assertEqual(test_game.p1.get_damage_given_pos(1, 0), 1)

    async def test_strakens_command_squad(self):
        random.seed(42)
        test_game = Game("NaN", "P1", "P2", card_array, planet_array, cards_dict, "", [])
        with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
            new_warlord_deck_content = file.read()
        await test_game.p1.setup_player(new_warlord_deck_content, test_game.planet_array)
        await test_game.p2.setup_player(deck_content_2, test_game.planet_array)
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        await test_game.update_game_event("P2", ["CHOICE", "0"])
        test_game.p1.cards = []
        test_game.p2.cards = []
        test_game.p1.add_card_to_planet(test_game.preloaded_find_card("Straken's Command Squad"), 0)
        test_game.p1.destroy_card_in_play(0, 0)
        await test_game.update_game_event("P1", [])
        await test_game.update_game_event("P1", ["CHOICE", "0"])
        self.assertEqual(test_game.p1.get_ability_given_pos(0, 0), "Guardsman")


if __name__ == "__main__":
    unittest.main()
