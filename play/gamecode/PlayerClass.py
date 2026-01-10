from . import FindCard
import random
from random import shuffle
import copy
import threading
from . import CardClasses


def clean_received_deck(raw_deck):
    split_deck = raw_deck.split("----------------------------------------------------------------------")
    split_deck = "\n".join(split_deck)
    split_deck = split_deck.split("\n")
    split_deck = [x for x in split_deck if x]
    del split_deck[0]
    del split_deck[1]
    pledge = split_deck[1]
    if pledge == "Signature Squad":
        pledge = ""
    else:
        del split_deck[1]
    i = 0
    while i < len(split_deck):
        if split_deck[i] == "Signature Squad" or split_deck[i] == "Army" or split_deck[i] == "Event" or \
                split_deck[i] == "Support" or split_deck[i] == "Attachment" \
                or split_deck[i] == "Synapse" or split_deck[i] == "Planet":
            del split_deck[i]
            i = i - 1
        i = i + 1
    deck_as_single_cards = [split_deck[0]]
    i = 1
    while i < len(split_deck):
        number_of_cards = split_deck[i][0]
        card_name = split_deck[i][3:]
        i = i + 1
        for _ in range(int(number_of_cards)):
            deck_as_single_cards.append(card_name)
    if pledge:
        deck_as_single_cards.append(pledge)
    print(deck_as_single_cards)
    return deck_as_single_cards


class Player:
    def __init__(self, name, number, card_array, cards_dict, apoka_errata_cards, game):
        self.game = game
        self.card_array = card_array
        self.cards_dict = cards_dict
        self.apoka_errata_cards = apoka_errata_cards
        self.cards_that_have_errata = []
        for i in range(len(self.apoka_errata_cards)):
            self.cards_that_have_errata.append(self.apoka_errata_cards[i].get_name())
        self.number = str(number)
        self.name_player = name
        self.position_activated = []
        self.has_initiative = True
        self.has_initiative_for_battle = False
        self.has_turn = True
        self.retreating = False
        self.has_passed = False
        self.phase = "Deploy"
        self.round_number = 1
        self.resources = 0
        self.cards = []
        self.victory_display = []
        self.icons_gained = [0, 0, 0]
        self.headquarters = []
        self.deck = []
        self.discard = []
        self.planets_in_play = [True, True, True, True, True, False, False]
        self.cards_in_play = [[] for _ in range(8)]
        self.bonus_boxes = ""
        self.extra_text = "No advice"
        self.deck_loaded = False
        self.committed_warlord = False
        self.committed_synapse = True
        self.warlord_commit_location = -1
        self.synapse_commit_location = -1
        self.idden_base_active = False
        self.warlord_just_got_bloodied = False
        self.condition_player_main = threading.Condition()
        self.condition_player_sub = threading.Condition()
        self.aiming_reticle_color = "blue"
        self.aiming_reticle_coords_hand = None
        self.aiming_reticle_coords_hand_2 = None
        self.aiming_reticle_coords_discard = -1
        self.aiming_reticle_color_discard = "blue"
        self.can_play_limited = True
        self.number_cards_to_search = 0
        self.phalanx_shield_value = 0
        self.mobile_resolved = True
        self.indirect_damage_applied = 0
        self.total_indirect_damage = 0
        self.cards_recently_discarded = []
        self.stored_cards_recently_discarded = []
        self.stored_targets_the_emperor_protects = []
        self.cards_recently_destroyed = []
        self.stored_cards_recently_destroyed = []
        self.num_nullify_played = 0
        self.warlord_just_got_destroyed = False
        self.lost_due_to_deck = False
        self.already_lost_due_to_deck = False
        self.sac_altar_rewards = [0, 0, 0, 0, 0, 0, 0]
        self.mulligan_done = False
        self.synapse_list = ["Savage Warrior Prime", "Blazing Zoanthrope", "Gravid Tervigon",
                             "Stalking Lictor", "Venomthrope Polluter", "Keening Maleceptor",
                             "Aberrant Alpha", "Vanguarding Horror", "Praetorian Shadow",
                             "Ardaci-strain Broodlord"]
        self.tyranid_warlord_list = ["Old One Eye", "The Swarmlord", "Subject Omega-X62113",
                                     "Parasite of Mortrex", "Magus Harid"]
        self.synapse_name = ""
        self.warlord_faction = ""
        self.consumption_sacs_list = [True, True, True, True, True, True, True]
        self.dark_possession_active = False
        self.force_due_to_dark_possession = False
        self.pos_card_dark_possession = -1
        self.dark_possession_remove_after_play = False
        self.enslaved_faction = ""
        self.chosen_enslaved_faction = False
        self.erekiels_queued = 0
        self.nahumekh_value = 0
        self.last_hand_string = ""
        self.last_hq_string = ""
        self.last_planet_strings = ["", "", "", "", "", "", ""]
        self.last_resources_string = ""
        self.last_discard_string = ""
        self.used_reanimation_protocol = False
        self.senatorum_directives_used = False
        self.waaagh_arbuttz_active = False
        self.harbinger_of_eternity_active = False
        self.position_discard_of_card = -1
        self.attachments_at_planet = [[], [], [], [], [], [], []]
        self.muster_the_guard_count = 0
        self.soul_seizure_value = 0
        self.plus_two_atk_if_warlord = ["Ymgarl Genestealer", "Bork'an Recruits", "White Scars Bikers",
                                        "Eldritch Corsair", "Tallarn Raiders", "Bloodied Reavers",
                                        "Evil Sunz Warbiker", "Noise Marine Zealots"]
        self.sacced_card_for_despise = True
        self.foretell_permitted = True
        self.last_planet_sacrifice = -1
        self.urien_relevant = False
        self.gorzod_relevant = False
        self.subject_omega_relevant = False
        self.grigory_maksim_relevant = False
        self.followers_of_asuryan_relevant = False
        self.illuminor_szeras_relevant = False
        self.unstoppable_tide_value = 0
        self.bluddflagg_relevant = False
        self.farsight_relevant = False
        self.bluddflagg_used = False
        self.vael_relevent = False
        self.castellan_crowe_relevant = False
        self.castellan_crowe_2_relevant = False
        self.tempting_ceasefire_used = False
        self.valid_aunlen_planets = [True, True, True, True, True, True, True]
        self.ichor_gauntlet_target = ""
        self.permitted_commit_locs_warlord = [True, True, True, True, True, True, True]
        self.illegal_commits_warlord = 0
        self.illegal_commits_synapse = 0
        self.primal_howl_used = False
        self.the_flayed_mask_planet = -1
        self.flayed_mask_active = False
        self.extra_deploy_turn_active = False
        self.discard_inquis_caius_wroth = False
        self.optimized_landing_used = False
        self.enemy_has_wyrdboy_stikk = False
        self.accept_any_challenge_used = False
        self.rok_bombardment_active = []
        self.bloodied_host_used = False
        self.master_warpsmith_count = 0
        self.gut_and_pillage_used = False
        self.valid_planets_berzerker_warriors = [False, False, False, False, False, False, False]
        self.war_of_ideas_active = False
        self.cards_in_reserve = [[], [], [], [], [], [], []]
        self.cards_in_reserve_hq = []
        self.the_princes_might_active = [False, False, False, False, False, False, False]
        self.hit_by_gorgul = False
        self.mork_blessings_count = 0
        self.concealing_darkness_active = False
        self.defensive_protocols_active = False
        self.counterblow_used = False
        self.death_serves_used = False
        self.our_last_stand_used = False
        self.everlasting_rage_used = False
        self.our_last_stand_bonus_active = False
        self.highest_death_serves_value = 0
        self.highest_cost_invasion_site = 0
        self.valid_prey_on_the_weak = [False, False, False, False, False, False, False]
        self.valid_surrogate_host = [False, False, False, False, False, False, False]
        self.contaminated_convoys = False
        self.magus_harid_waiting_cards = []
        self.planet_absorption_played = False
        self.reinforced_synaptic_network_played = False
        self.allowed_units_rsn = copy.copy(self.synapse_list)
        self.preparation_cards = ["Pulsating Carapace", "Mobilize the Chapter", "Support Fleet"]
        for i in range(len(self.card_array)):
            if "Pledge" in self.card_array[i].traits:
                self.preparation_cards.append(self.card_array[i].get_name())
        self.played_necrodermis = False
        self.necrodermis_allowed = True
        self.etekh_trait = ""
        self.sautekh_royal_crypt = -1
        self.command_struggles_won_this_phase = 0
        self.celestian_amelia_active = False
        self.wrathful_retribution_value = 0
        self.can_play_pledge = True
        self.last_kagrak_trait = ""
        self.looted_skrap_active = False
        self.looted_skrap_count = 0
        self.looted_skrap_planet = -1
        self.cards_removed_from_game = []
        self.cards_removed_from_game_hidden = []
        self.ritual_cards = ["The Blood Pits", "The Grand Plan", "The Inevitable Decay", "The Orgiastic Feast",
                             "Test of Faith"]
        self.last_removed_string = ""
        self.broken_sigil_planet = -1
        self.broken_sigil_effect = ""
        self.played_grand_plan = False
        self.won_command_struggles_planets_round = [False, False, False, False, False, False, False]
        self.webway_witch = -1
        self.fortress_world_garid_used = False
        self.cegorach_jesters_active = False
        self.cegorach_jesters_permitted = []
        self.dalyth_sept_active = False

    def put_card_into_reserve(self, card, planet_pos, payment=True):
        if planet_pos == -2:
            self.cards_in_reserve_hq.append(copy.deepcopy(card))
            return True
        if not payment:
            self.cards_in_reserve[planet_pos].append(copy.deepcopy(card))
            return True
        if self.spend_resources(1):
            self.cards_in_reserve[planet_pos].append(copy.deepcopy(card))
            self.game.queued_sound = "onplay"
            return True
        return False

    def setup_player_no_send(self, raw_deck, planet_array):
        self.condition_player_main.acquire()
        deck_list = clean_received_deck(raw_deck)
        self.headquarters.append(copy.deepcopy(FindCard.find_card(deck_list[0], self.card_array, self.cards_dict,
                                                                  self.apoka_errata_cards, self.cards_that_have_errata
                                                                  )))
        self.warlord_faction = self.headquarters[0].get_faction()
        self.headquarters[0].name_owner = self.name_player
        if self.headquarters[0].get_name() == "Urien Rakarth":
            self.urien_relevant = True
        if self.headquarters[0].get_name() == "Gorzod":
            self.gorzod_relevant = True
        if self.headquarters[0].get_name() == "Subject Omega-X62113":
            self.subject_omega_relevant = True
        if self.headquarters[0].get_name() == "Grigory Maksim":
            self.grigory_maksim_relevant = True
        if self.headquarters[0].get_name() == "Farsight":
            self.farsight_relevant = True
        if self.headquarters[0].get_name() == "Illuminor Szeras":
            self.illuminor_szeras_relevant = True
        if self.headquarters[0].get_name() == "Kaptin Bluddflagg":
            self.bluddflagg_relevant = True
        if self.headquarters[0].get_name() == "Castellan Crowe":
            self.castellan_crowe_relevant = True
            self.castellan_crowe_2_relevant = True
        self.deck = deck_list[1:]
        if self.headquarters[0].get_name() == "Vael the Gifted":
            self.vael_relevent = True
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.ritual_cards:
                    self.remove_card_from_game(self.deck[i])
                    del self.deck[i]
                    i = i - 1
                i = i + 1
        if self.warlord_faction == "Tyranids":
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.synapse_list:
                    self.allowed_units_rsn.remove(self.deck[i])
                    self.headquarters.append(copy.deepcopy(FindCard.find_card(self.deck[i], self.card_array,
                                                                              self.cards_dict,
                                                                              self.apoka_errata_cards,
                                                                              self.cards_that_have_errata)))
                    self.headquarters[1].name_owner = self.name_player
                    del self.deck[i]
                    i = i - 1
                i = i + 1
        self.shuffle_deck()
        self.deck_loaded = True
        self.cards_in_play[0] = planet_array
        self.resources = self.headquarters[0].get_starting_resources()
        preparation_cards_exist = False
        for i in range(len(self.preparation_cards)):
            if self.preparation_cards[i] in self.deck:
                preparation_cards_exist = True
        if not preparation_cards_exist:
            for i in range(self.headquarters[0].get_starting_cards()):
                self.draw_card()
        else:
            num_cards_left = self.headquarters[0].get_starting_cards()
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.preparation_cards:
                    self.cards.append(self.deck[i])
                    del self.deck[i]
                    num_cards_left = num_cards_left - 1
                    i = i - 1
                i = i + 1
            for i in range(num_cards_left):
                self.draw_card()
        if self.game.p1.deck_loaded and self.game.p2.deck_loaded and not self.game.sent_setup_info_already:
            self.game.sent_setup_info_already = True
            self.game.phase = "DEPLOY"
            self.game.start_mulligan()

    async def setup_player(self, raw_deck, planet_array):
        self.condition_player_main.acquire()
        deck_list = clean_received_deck(raw_deck)
        self.headquarters.append(copy.deepcopy(FindCard.find_card(deck_list[0], self.card_array, self.cards_dict,
                                                                  self.apoka_errata_cards, self.cards_that_have_errata
                                                                  )))
        self.warlord_faction = self.headquarters[0].get_faction()
        self.headquarters[0].name_owner = self.name_player
        if self.headquarters[0].get_name() == "Urien Rakarth":
            self.urien_relevant = True
        if self.headquarters[0].get_name() == "Gorzod":
            self.gorzod_relevant = True
        if self.headquarters[0].get_name() == "Subject Omega-X62113":
            self.subject_omega_relevant = True
        if self.headquarters[0].get_name() == "Grigory Maksim":
            self.grigory_maksim_relevant = True
        if self.headquarters[0].get_name() == "Farsight":
            self.farsight_relevant = True
        if self.headquarters[0].get_name() == "Illuminor Szeras":
            self.illuminor_szeras_relevant = True
        if self.headquarters[0].get_name() == "Kaptin Bluddflagg":
            self.bluddflagg_relevant = True
        if self.headquarters[0].get_name() == "Castellan Crowe":
            self.castellan_crowe_relevant = True
            self.castellan_crowe_2_relevant = True
        self.deck = deck_list[1:]
        if self.headquarters[0].get_name() == "Vael the Gifted":
            self.vael_relevent = True
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.ritual_cards:
                    self.remove_card_from_game(self.deck[i])
                    del self.deck[i]
                    i = i - 1
                i = i + 1
        if self.warlord_faction == "Tyranids":
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.synapse_list:
                    self.allowed_units_rsn.remove(self.deck[i])
                    self.headquarters.append(copy.deepcopy(FindCard.find_card(self.deck[i], self.card_array,
                                                                              self.cards_dict,
                                                                              self.apoka_errata_cards,
                                                                              self.cards_that_have_errata)))
                    self.headquarters[1].name_owner = self.name_player
                    del self.deck[i]
                    i = i - 1
                i = i + 1
        self.shuffle_deck()
        self.deck_loaded = True
        self.cards_in_play[0] = planet_array
        self.resources = self.headquarters[0].get_starting_resources()
        preparation_cards_exist = False
        for i in range(len(self.preparation_cards)):
            if self.preparation_cards[i] in self.deck:
                preparation_cards_exist = True
        if not preparation_cards_exist:
            for i in range(self.headquarters[0].get_starting_cards()):
                self.draw_card()
        else:
            num_cards_left = self.headquarters[0].get_starting_cards()
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.preparation_cards:
                    self.cards.append(self.deck[i])
                    del self.deck[i]
                    num_cards_left = num_cards_left - 1
                    i = i - 1
                i = i + 1
            for i in range(num_cards_left):
                self.draw_card()
        print(self.resources)
        print(self.deck)
        print(self.cards)
        self.print_headquarters()
        await self.conclude_setup_sends()
        self.condition_player_main.notify_all()
        self.condition_player_main.release()

    async def conclude_setup_sends(self):
        await self.send_removed_cards()
        await self.send_hand()
        for i in range(len(self.game.game_sockets)):
            await self.game.send_update_message("Setup of " + self.name_player + " finished.")
        await self.send_hq()
        await self.send_units_at_all_planets()
        await self.send_resources()
        if self.game.p1.deck_loaded and self.game.p2.deck_loaded and not self.game.sent_setup_info_already:
            self.game.sent_setup_info_already = True
            self.game.start_mulligan()
            await self.game.send_search()
            await self.game.send_info_box()
            self.game.phase = "DEPLOY"
            if self.game.apoka:
                await self.game.send_update_message("Apoka Errata is active")
            else:
                await self.game.send_update_message("No Errata is active")
            await self.game.send_update_message("The " + self.game.sector + " sector is active")
            await self.game.send_update_message(
                self.game.name_1 + " may mulligan their opening hand.")

    def resolve_electro_whip(self, planet_pos, unit_pos):
        if planet_pos == -2:
            self.headquarters[unit_pos].cannot_ready_phase = True
            return None
        self.cards_in_play[planet_pos + 1][unit_pos].cannot_ready_phase = True
        return None

    def remove_card_from_game(self, card_name, hidden="N"):
        self.cards_removed_from_game.append(card_name)
        self.cards_removed_from_game_hidden.append(hidden)

    def search_synapse_in_hq(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_card_type() == "Synapse":
                self.synapse_name = self.headquarters[i].get_name()
                return True
        return False

    def get_enemy_has_init_for_cards(self, planet_pos, unit_pos):
        if self.name_player == self.game.name_1:
            enemy_player = self.game.p2
        else:
            enemy_player = self.game.p1
        if self.game.last_planet_checked_for_battle != -1:
            if enemy_player.has_initiative_for_battle:
                return True
        elif self.game.player_with_initiative == enemy_player.name_player:
            return True
        if planet_pos == self.game.last_planet_checked_for_battle:
            if self.search_card_at_planet(planet_pos, "Corpulent Ork"):
                if not enemy_player.search_card_at_planet(planet_pos, "Corpulent Ork", ability_checking=False):
                    return True
        return False

    def add_attachment_to_planet(self, planet_pos, card):
        if card.get_limited():
            self.can_play_limited = False
        self.attachments_at_planet[planet_pos].append(copy.deepcopy(card))

    def get_can_play_limited(self):
        return self.can_play_limited

    def set_can_play_limited(self, new_val):
        self.can_play_limited = new_val

    async def send_hand(self, force=False):
        card_string = ""
        if self.cards:
            card_array = self.cards.copy()
            for i in range(len(card_array)):
                if card_array[i] in self.cards_that_have_errata:
                    card_array[i] = card_array[i] + "_apoka"
            if self.aiming_reticle_color is None:
                pass
            else:
                for i in range(len(card_array)):
                    if self.aiming_reticle_coords_hand == i or self.aiming_reticle_coords_hand_2 == i:
                        card_array[i] = card_array[i] + "|" + self.aiming_reticle_color
            card_string = "/".join(card_array)
            card_string = "GAME_INFO/HAND/" + str(self.number) + "/" + self.name_player + "/" + card_string
        else:
            card_string = "GAME_INFO/HAND/" + str(self.number) + "/" + self.name_player
        if card_string != self.last_hand_string or force:
            self.last_hand_string = card_string
            await self.game.send_update_message(card_string)

    def count_units_with_trait_at_planet(self, trait, i):
        copies = 0
        if i == -2:
            return copies
        for j in range(len(self.cards_in_play[i + 1])):
            if self.check_for_trait_given_pos(i, j, trait):
                copies += 1
        return copies

    def count_units_with_trait(self, trait):
        copies = 0
        for i in range(len(self.headquarters)):
            if self.check_for_trait_given_pos(-2, i, trait):
                copies += 1
        for i in range(7):
            copies += self.count_units_with_trait_at_planet(trait, i)
        return copies

    def search_triggered_interrupts_enemy_discard(self):
        interrupts = []
        if self.game.interrupts_discard_enemy_allowed:
            if self.search_hand_for_card("Scrying Pool"):
                interrupts.append("Scrying Pool")
            if self.search_hand_for_card("Vale Tenndrac"):
                interrupts.append("Vale Tenndrac")
            if self.search_hand_for_card("Blade of the Crimson Oath"):
                interrupts.append("Blade of the Crimson Oath")
            if self.search_hand_for_card("Shas'el Lyst"):
                interrupts.append("Shas'el Lyst")
            if self.search_hand_for_card("Hjorvath Coldstorm"):
                interrupts.append("Hjorvath Coldstorm")
        return interrupts

    def check_if_support_exists(self):
        for i in range(len(self.headquarters)):
            if self.get_card_type_given_pos(-2, i) == "Support":
                return True
        return False

    async def send_hq(self, force=False):
        joined_string = ""
        if self.headquarters:
            card_strings = []
            for i in range(len(self.headquarters)):
                current_card = self.headquarters[i]
                single_card_string = current_card.get_name()
                if current_card.actually_a_deepstrike:
                    single_card_string = current_card.deepstrike_card_name
                if single_card_string in self.cards_that_have_errata:
                    single_card_string += "_apoka"
                single_card_string = single_card_string + "|"
                if current_card.ready:
                    if current_card.check_for_a_trait("Pledge"):
                        single_card_string += "PR|"
                    else:
                        single_card_string += "R|"
                else:
                    if current_card.check_for_a_trait("Pledge"):
                        single_card_string += "PE|"
                    else:
                        single_card_string += "E|"
                card_type = current_card.get_card_type()
                if current_card.is_unit:
                    single_card_string += str(current_card.get_damage() + current_card.get_indirect_damage())
                elif current_card.get_card_type() == "Support":
                    single_card_string += str(current_card.get_damage())
                else:
                    single_card_string += "0"
                single_card_string += "|"
                if current_card.is_unit:
                    single_card_string += str(current_card.get_faith())
                elif current_card.get_name() == "Hive Ship Tendrils":
                    single_card_string += str(current_card.counter)
                elif current_card.get_name() == "Promethium Mine":
                    single_card_string += str(current_card.counter)
                elif current_card.get_name() == "The Phalanx":
                    single_card_string += str(current_card.counter)
                elif current_card.get_name() == "World Engine Beam":
                    single_card_string += str(current_card.counter)
                elif current_card.get_name() == "Vamii Industrial Complex":
                    single_card_string += str(current_card.counter)
                elif current_card.check_for_a_trait("Pledge"):
                    single_card_string += str(current_card.counter)
                else:
                    single_card_string += "0"
                single_card_string += "|"
                if card_type == "Warlord":
                    if current_card.get_bloodied():
                        single_card_string += "B|"
                    else:
                        single_card_string += "H|"
                elif current_card.actually_a_deepstrike:
                    single_card_string += "D|"
                else:
                    single_card_string += "H|"
                single_card_string += current_card.get_extra_info_string() + "|"
                if current_card.aiming_reticle_color is not None:
                    single_card_string += current_card.aiming_reticle_color
                attachments_list = current_card.get_attachments()
                for a in range(len(attachments_list)):
                    single_card_string += "|"
                    single_card_string += attachments_list[a].get_name()
                    if attachments_list[a].get_name() in self.cards_that_have_errata:
                        single_card_string += "_apoka"
                    single_card_string += "+"
                    if attachments_list[a].get_ready():
                        single_card_string += "R"
                    else:
                        single_card_string += "E"
                    single_card_string += "+"
                    if attachments_list[a].from_magus_harid:
                        single_card_string += "M+" + attachments_list[a].name_owner
                    else:
                        single_card_string += "R+"
                card_strings.append(single_card_string)
            for i in range(len(self.cards_in_reserve_hq)):
                current_card = self.cards_in_reserve_hq[i]
                single_card_string = current_card.get_name()
                if single_card_string in self.cards_that_have_errata:
                    single_card_string += "_apoka"
                single_card_string = single_card_string + "|"
                if current_card.ready:
                    single_card_string += "R|"
                else:
                    single_card_string += "E|"
                if current_card.is_unit:
                    single_card_string += str(current_card.get_damage() + current_card.get_indirect_damage())
                elif current_card.get_card_type() == "Support":
                    single_card_string += str(current_card.get_damage())
                else:
                    single_card_string += "0"
                single_card_string += "|"
                if current_card.is_unit:
                    single_card_string += str(current_card.get_faith())
                else:
                    single_card_string += "0"
                single_card_string += "|D|"
                single_card_string += current_card.get_extra_info_string() + "|"
                if current_card.aiming_reticle_color is not None:
                    single_card_string += current_card.aiming_reticle_color
                attachments_list = current_card.get_attachments()
                for a in range(len(attachments_list)):
                    single_card_string += "|"
                    single_card_string += attachments_list[a].get_name()
                    if attachments_list[a].get_name() in self.cards_that_have_errata:
                        single_card_string += "_apoka"
                    single_card_string += "+"
                    if attachments_list[a].get_ready():
                        single_card_string += "R"
                    else:
                        single_card_string += "E"
                    single_card_string += "+"
                    if attachments_list[a].from_magus_harid:
                        single_card_string += "M+" + attachments_list[a].name_owner
                    else:
                        single_card_string += "R+"
                card_strings.append(single_card_string)
            joined_string = "/".join(card_strings)
            joined_string = "GAME_INFO/HQ/" + str(self.number) + "/" \
                            + self.name_player + "/" + joined_string
        else:
            joined_string = "GAME_INFO/HQ/" + str(self.number) + "/" + self.name_player
        if self.last_hq_string != joined_string or force:
            self.last_hq_string = joined_string
            await self.game.send_update_message(joined_string)

    def check_for_trait_at_planet(self, planet_pos, trait):
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.check_for_trait_given_pos(planet_pos, i, trait):
                return True
        return False

    def discard_all_cards_in_reserve(self, planet_id):
        while self.cards_in_reserve[planet_id]:
            self.add_card_to_discard(self.cards_in_reserve[planet_id][0].get_name())
            del self.cards_in_reserve[planet_id][0]

    def get_card_type_in_reserve(self, planet_id, unit_id, in_play_card=False):
        if self.idden_base_active and not in_play_card:
            card_name = self.cards_in_play[planet_id + 1][unit_id].deepstrike_card_name
            card = self.game.preloaded_find_card(card_name)
            return card.get_card_type()
        return self.cards_in_reserve[planet_id][unit_id].get_card_type()

    def get_deepstrike_value_given_pos(self, planet_id, unit_id, in_play_card=False):
        if self.idden_base_active or in_play_card:
            card_name = self.cards_in_play[planet_id + 1][unit_id].deepstrike_card_name
            card = self.game.preloaded_find_card(card_name)
            ds_value = card.get_deepstrike_value()
            if ds_value == -1:
                return -1
            other_player = self.get_other_player()
            for i in range(len(other_player.cards_in_play[planet_id + 1])):
                if other_player.get_ability_given_pos(planet_id, i) == "Catachan Tracker":
                    ds_value += 2
            vanguarding_horror = False
            if planet_id != 0:
                if self.search_card_at_planet(planet_id - 1, "Vanguarding Horror"):
                    vanguarding_horror = True
            if not vanguarding_horror and planet_id != 6:
                if self.search_card_at_planet(planet_id + 1, "Vanguarding Horror"):
                    vanguarding_horror = True
            if vanguarding_horror:
                ds_value = ds_value - 1
            return ds_value
        ds_value = self.cards_in_reserve[planet_id][unit_id].get_deepstrike_value()
        if self.cards_in_reserve[planet_id][unit_id].get_card_type() == "Attachment":
            if self.farsight_relevant:
                ds_value = 0
        other_player = self.game.p1
        if other_player.name_player == self.name_player:
            other_player = self.game.p2
        for i in range(len(other_player.cards_in_play[planet_id + 1])):
            if other_player.get_ability_given_pos(planet_id, i) == "Catachan Tracker":
                ds_value += 2
        vanguarding_horror = False
        if planet_id != 0:
            if self.search_card_at_planet(planet_id - 1, "Vanguarding Horror"):
                vanguarding_horror = True
        if not vanguarding_horror and planet_id != 6:
            if self.search_card_at_planet(planet_id + 1, "Vanguarding Horror"):
                vanguarding_horror = True
        if vanguarding_horror:
            ds_value = ds_value - 1
        return ds_value

    def deepstrike_event(self, planet_id, unit_id, in_play_card=False):
        if not self.idden_base_active and not in_play_card:
            ability = self.cards_in_reserve[planet_id][unit_id].get_name()
        else:
            ability = self.cards_in_play[planet_id + 1][unit_id].deepstrike_card_name
        if ability == "The Prince's Might":
            self.the_princes_might_active[planet_id] = True
        if ability == "Unseen Strike":
            self.game.force_set_battle_initiative(self.name_player, self.number)
        if ability == "Concealing Darkness":
            self.concealing_darkness_active = True
        if ability == "Defensive Protocols":
            self.defensive_protocols_active = True
        if ability == "Tactical Withdrawal":
            self.game.create_reaction("Tactical Withdrawal", self.name_player, (int(self.number), planet_id, -1))
        if ability == "Run Down":
            self.game.create_reaction("Run Down", self.name_player, (int(self.number), planet_id, -1))
        if ability == "Burst Forth":
            self.game.create_reaction("Burst Forth", self.name_player, (int(self.number), planet_id, -1))
        self.add_card_to_discard(ability)
        self.after_any_deepstrike(planet_id)
        if not self.idden_base_active and not in_play_card:
            del self.cards_in_reserve[planet_id][unit_id]
        else:
            self.discard_attachments_from_card(planet_id, unit_id)
            del self.cards_in_play[planet_id + 1][unit_id]

    def after_any_deepstrike(self, planet_id):
        warlord_pla, warlord_pos = self.get_location_of_warlord()
        if self.get_ability_given_pos(warlord_pla, warlord_pos, bloodied_relevant=True) == "Epistolary Vezuel":
            self.game.create_reaction("Epistolary Vezuel", self.name_player,
                                      (int(self.number), warlord_pla, warlord_pos))
        if self.get_ability_given_pos(warlord_pla, warlord_pos, bloodied_relevant=True) == "Farsight":
            if not self.get_once_per_phase_used_given_pos(warlord_pla, warlord_pos):
                self.game.create_reaction("Farsight", self.name_player,
                                          (int(self.number), warlord_pla, warlord_pos))
        if self.search_attachments_at_pos(warlord_pla, warlord_pos, "Fulgaris"):
            self.game.create_reaction("Fulgaris", self.name_player,
                                      (int(self.number), warlord_pla, warlord_pos))
        for i in range(len(self.headquarters)):
            if self.get_ability_given_pos(-2, i) == "Deathstorm Drop Pod":
                self.game.create_reaction("Deathstorm Drop Pod", self.name_player,
                                          (int(self.number), planet_id, -1))
            if self.get_ability_given_pos(-2, i) == "Followers of Asuryan":
                self.game.create_reaction("Followers of Asuryan", self.name_player,
                                          (int(self.number), -2, i))

    def deepstrike_attachment_extras(self, planet_id):
        self.after_any_deepstrike(planet_id)

    def belial_deepstrike(self, planet_id):
        self.after_any_deepstrike(planet_id)

    def deepstrike_unit(self, planet_id, unit_id, in_play_card=False):
        damage = 0
        ready = True
        if not self.idden_base_active and not in_play_card:
            card = self.cards_in_reserve[planet_id][unit_id]
        else:
            card_name = self.cards_in_play[planet_id + 1][unit_id].deepstrike_card_name
            card = self.game.preloaded_find_card(card_name)
            damage = self.get_damage_given_pos(planet_id, unit_id)
            ready = self.get_ready_given_pos(planet_id, unit_id)
        if self.add_card_to_planet(card, planet_id, triggered_card_effect=False) != -1:
            self.after_any_deepstrike(planet_id)
            attachments = []
            if not self.idden_base_active and not in_play_card:
                del self.cards_in_reserve[planet_id][unit_id]
            else:
                attachments = self.cards_in_play[planet_id + 1][unit_id].get_attachments()
                del self.cards_in_play[planet_id + 1][unit_id]
            last_element_index = len(self.cards_in_play[planet_id + 1]) - 1
            self.cards_in_play[planet_id + 1][last_element_index].damage = damage
            self.cards_in_play[planet_id + 1][last_element_index].ready = ready
            for i in range(len(attachments)):
                if not self.attach_card(attachments[i], planet_id, last_element_index):
                    self.add_card_to_discard(attachments[i].get_name())
            ability = self.get_ability_given_pos(planet_id, last_element_index)
            if ability == "8th Company Assault Squad":
                self.game.create_reaction("8th Company Assault Squad", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Kamouflage Expert":
                self.game.create_reaction("Kamouflage Expert", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Thundering Wraith":
                self.game.create_reaction("Thundering Wraith", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Patient Infiltrator":
                if self.get_damage_given_pos(planet_id, last_element_index) > 0:
                    if not self.get_ready_given_pos(planet_id, last_element_index):
                        self.game.create_reaction("Patient Infiltrator", self.name_player,
                                                  (int(self.number), planet_id, last_element_index))
            if ability == "Tunneling Mawloc":
                self.game.create_reaction("Tunneling Mawloc", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Patron Saint":
                self.game.create_reaction("Patron Saint", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Connoisseur of Terror":
                self.game.create_reaction("Connoisseur of Terror", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Seething Mycetic Spore":
                self.game.create_reaction("Seething Mycetic Spore", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Slavering Mawloc":
                self.game.create_reaction("Slavering Mawloc", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Sicarian Infiltrator":
                self.game.create_reaction("Sicarian Infiltrator", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Scorpion Striker":
                self.game.create_reaction("Scorpion Striker", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Beastmaster Harvester":
                self.game.create_reaction("Beastmaster Harvester", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Deathwing Terminators":
                self.game.create_reaction("Deathwing Terminators", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Lictor Vine Lurker":
                self.game.create_reaction("Lictor Vine Lurker", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Mandrake Cutthroat":
                self.game.create_reaction("Mandrake Cutthroat", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Vezuel's Hunters":
                self.game.create_reaction("Vezuel's Hunters", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            if ability == "Sootblade Assashun":
                self.game.create_reaction("Sootblade Assashun", self.name_player,
                                          (int(self.number), planet_id, last_element_index))
            return last_element_index
        return -1

    async def send_units_at_planet(self, planet_id, force=False):
        if planet_id != -1:
            if planet_id == -2:
                await self.send_hq()
            else:
                if self.cards_in_play[planet_id + 1] or self.cards_in_reserve[planet_id]:
                    card_strings = []
                    for i in range(len(self.cards_in_play[planet_id + 1])):
                        current_card = self.cards_in_play[planet_id + 1][i]
                        single_card_string = current_card.get_name()
                        if current_card.actually_a_deepstrike:
                            single_card_string = current_card.deepstrike_card_name
                        if single_card_string in self.cards_that_have_errata:
                            single_card_string += "_apoka"
                        single_card_string = single_card_string + "|"
                        if current_card.ready:
                            single_card_string += "R|"
                        else:
                            single_card_string += "E|"
                        single_card_string += str(current_card.get_damage() + current_card.get_indirect_damage())
                        single_card_string += "|"
                        single_card_string += str(current_card.get_faith())
                        single_card_string += "|"
                        if current_card.actually_a_deepstrike:
                            single_card_string += "D"
                        elif current_card.get_card_type() == "Warlord":
                            if current_card.get_bloodied():
                                single_card_string += "B"
                            else:
                                single_card_string += "H"
                        else:
                            single_card_string += "H"
                        single_card_string += "|"
                        single_card_string += current_card.get_extra_info_string() + "|"
                        if current_card.aiming_reticle_color is not None:
                            single_card_string += current_card.aiming_reticle_color
                        attachments_list = current_card.get_attachments()
                        for a in range(len(attachments_list)):
                            single_card_string += "|"
                            single_card_string += attachments_list[a].get_name()
                            if attachments_list[a].get_name() in self.cards_that_have_errata:
                                single_card_string += "_apoka"
                            single_card_string += "+"
                            if attachments_list[a].get_ready():
                                single_card_string += "R"
                            else:
                                single_card_string += "E"
                            single_card_string += "+"
                            if attachments_list[a].from_magus_harid:
                                single_card_string += "M+" + attachments_list[a].name_owner
                            else:
                                single_card_string += "R+"
                        card_strings.append(single_card_string)
                    for i in range(len(self.cards_in_reserve[planet_id])):
                        current_card = self.cards_in_reserve[planet_id][i]
                        single_card_string = current_card.get_name()
                        if single_card_string in self.cards_that_have_errata:
                            single_card_string += "_apoka"
                        single_card_string = single_card_string + "|"
                        if current_card.ready:
                            single_card_string += "R|"
                        else:
                            single_card_string += "E|"
                        single_card_string += str(current_card.get_damage() + current_card.get_indirect_damage())
                        single_card_string += "|"
                        single_card_string += str(current_card.get_faith())
                        single_card_string += "|"
                        single_card_string += "D"
                        single_card_string += "|"
                        single_card_string += "None" + "|"
                        if current_card.aiming_reticle_color is not None:
                            single_card_string += current_card.aiming_reticle_color
                        attachments_list = current_card.get_attachments()
                        for a in range(len(attachments_list)):
                            single_card_string += "|"
                            single_card_string += attachments_list[a].get_name()
                            single_card_string += "+"
                            if attachments_list[a].get_ready():
                                single_card_string += "R"
                            else:
                                single_card_string += "E"
                        card_strings.append(single_card_string)
                    joined_string = "/".join(card_strings)
                    joined_string = "GAME_INFO/IN_PLAY/" + str(self.number) + "/" + str(planet_id) + "/"\
                                    + self.name_player + "/" + joined_string
                else:
                    joined_string = "GAME_INFO/IN_PLAY/" + str(self.number) +\
                                    "/" + str(planet_id) + "/" + self.name_player
                if self.last_planet_strings[planet_id] != joined_string or force:
                    self.last_planet_strings[planet_id] = joined_string
                    await self.game.send_update_message(joined_string)

    async def send_units_at_all_planets(self, force=False):
        for i in range(7):
            await self.send_units_at_planet(i, force=force)

    async def send_resources(self, force=False):
        joined_string = "GAME_INFO/RESOURCES/" + str(self.number) + "/" + str(self.resources)
        if joined_string != self.last_resources_string or force:
            self.last_resources_string = joined_string
            await self.game.send_update_message(joined_string)

    async def transform_indirect_into_damage(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                damage = self.headquarters[i].get_indirect_damage()
                if damage > 0:
                    self.assign_damage_to_pos(-2, i, damage, by_enemy_unit=False)
                    self.headquarters[i].reset_indirect_damage()
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_is_unit():
                    damage = self.cards_in_play[i + 1][j].get_indirect_damage()
                    print("Indirect damage:", damage)
                    if damage > 0:
                        self.assign_damage_to_pos(i, j, damage, by_enemy_unit=False)
                        self.cards_in_play[i + 1][j].reset_indirect_damage()

    def increase_sweep_given_pos_eor(self, planet_id, unit_id, value):
        if planet_id == -2:
            self.headquarters[unit_ud].sweep_eor += value
            return None
        self.cards_in_play[planet_id + 1][unit_id].sweep_eor += value
        return None

    def increase_sweep_given_pos_eop(self, planet_id, unit_id, value):
        if planet_id == -2:
            self.headquarters[unit_ud].sweep_eop += value
            return None
        self.cards_in_play[planet_id + 1][unit_id].sweep_eop += value
        return None

    def increase_retaliate_given_pos_eop(self, planet_id, unit_id, value):
        if planet_id == -2:
            self.headquarters[unit_ud].increase_retaliate_eop(value)
            return None
        self.cards_in_play[planet_id + 1][unit_id].increase_retaliate_eop(value)
        return None

    def check_bloodthirst(self, planet_id):
        return self.game.bloodthirst_active[planet_id]

    def get_retaliate_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_retaliate()
        retaliate = self.cards_in_play[planet_id + 1][unit_id].get_retaliate()
        if self.get_ability_given_pos(planet_id, unit_id) == "Fierce Purgator":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                retaliate += 3
        if self.get_ability_given_pos(planet_id, unit_id) == "Parched Neophyte":
            if self.check_bloodthirst(planet_id):
                retaliate += 3
        warlord_pla, warlord_pos = self.get_location_of_warlord()
        if self.get_ability_given_pos(warlord_pla, warlord_pos) == "Mephiston":
            retaliate += 1
        elif self.get_ability_given_pos(warlord_pla, warlord_pos) == "Mephiston BLOODIED":
            if warlord_pla == planet_id:
                retaliate += 1
        return retaliate

    async def send_victory_display(self):
        if self.victory_display:
            card_strings = []
            for i in range(len(self.victory_display)):
                card_strings.append(self.victory_display[i].get_name())
            joined_string = "/".join(card_strings)
            joined_string = "GAME_INFO/VICTORY_DISPLAY/" + str(self.number) + "/" + joined_string
            await self.game.send_update_message(joined_string)
        else:
            joined_string = "GAME_INFO/VICTORY_DISPLAY/" + str(self.number)
            await self.game.send_update_message(joined_string)
        total_icons = self.get_icons_on_captured()
        if total_icons[0] > 2 or total_icons[1] > 2 or total_icons[2] > 2:
            await self.game.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_player + "; sufficient icons on captured planets."
                                                    "----GAME END----"
            )
            await self.game.send_victory_proper(self.name_player, "icons on captured planets")

    async def send_removed_cards(self, force=False):
        joined_string = "GAME_INFO/REMOVED/" + str(self.number) + "/" + self.name_player
        if self.cards_removed_from_game:
            for i in range(len(self.cards_removed_from_game)):
                joined_string += "/" + self.cards_removed_from_game[i] + "|" + self.cards_removed_from_game_hidden[i]
        if joined_string != self.last_removed_string or force:
            self.last_removed_string = joined_string
            await self.game.send_update_message(joined_string)

    async def send_discard(self, force=False):
        joined_string = "GAME_INFO/DISCARD/" + str(self.number)
        if self.discard:
            for i in range(len(self.discard)):
                joined_string += "/" + self.discard[i] + "|"
                if self.aiming_reticle_coords_discard == i:
                    joined_string += self.aiming_reticle_color_discard
        if joined_string != self.last_discard_string or force:
            self.last_discard_string = joined_string
            await self.game.send_update_message(joined_string)

    def search_for_card_everywhere(self, card_name, ability=True, ready_relevant=False, must_own=False,
                                   limit_phase_rel=False, limit_round_rel=False, bloodied_relevant=False):
        for i in range(len(self.headquarters)):
            if self.get_ability_given_pos(-2, i, bloodied_relevant=bloodied_relevant) == card_name:
                if card_name == "Magus Harid":
                    for j in range(len(self.headquarters)):
                        if self.get_ability_given_pos(-2, j) == "Imperial Bastion":
                            if self.headquarters[i].once_per_round_used:
                                if not self.headquarters[j].once_per_round_used:
                                    return True
                if (not limit_phase_rel or not self.headquarters[i].once_per_phase_used) and \
                        (not limit_round_rel or not self.headquarters[i].once_per_round_used):
                    return True
            if self.search_attachments_at_pos(-2, i, card_name, ready_relevant=ready_relevant):
                return True
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.get_ability_given_pos(i, j, bloodied_relevant=bloodied_relevant) == card_name:
                    if card_name == "Magus Harid":
                        for k in range(len(self.headquarters)):
                            if self.get_ability_given_pos(-2, k) == "Imperial Bastion":
                                if self.cards_in_play[i + 1][j].once_per_round_used:
                                    if not self.cards_in_play[i + 1][j].once_per_round_used:
                                        return True
                    if (not limit_phase_rel or not self.cards_in_play[i + 1][j].once_per_phase_used) and \
                            (not limit_round_rel or not self.cards_in_play[i + 1][j].once_per_round_used):
                        return True
                if self.search_attachments_at_pos(i, j, card_name, ready_relevant=ready_relevant,
                                                  must_match_name=must_own):
                    return True
        return False

    def exhaust_card_in_hq_given_name(self, card_name):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_name() == card_name and self.headquarters[i].get_ready():
                self.exhaust_given_pos(-2, i)
                return True
        return False

    def sacrifice_card_in_hq_given_name(self, card_name):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_name() == card_name:
                self.sacrifice_card_in_hq(i)
                return True
        return False

    def move_to_top_of_discard(self, position):
        self.add_card_to_discard(self.discard.pop(position))

    def shuffle_card_in_discard_into_deck(self, position):
        self.deck.append(self.discard.pop(position))
        self.shuffle_deck()

    def mulligan_hand(self):
        num_cards = 0
        if self.search_hand_for_card("Singing Spear"):
            if not self.game.choices_available:
                self.game.create_interrupt("Singing Spear", self.name_player, (int(self.number), -1, -1))
        while self.cards:
            num_cards += 1
            self.deck.append(self.cards[0])
            del self.cards[0]
        self.shuffle_deck()
        preparation_cards_exist = False
        for i in range(len(self.preparation_cards)):
            if self.preparation_cards[i] in self.deck:
                preparation_cards_exist = True
        if not preparation_cards_exist:
            for i in range(num_cards):
                self.draw_card()
        else:
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.preparation_cards:
                    self.cards.append(self.deck[i])
                    del self.deck[i]
                    num_cards = num_cards - 1
                    i = i - 1
                i = i + 1
            for i in range(num_cards):
                self.draw_card()
        if self.search_card_in_hq("Wisdom of Biel-tan"):
            self.game.create_reaction("Wisdom of Biel-tan", self.name_player, (int(self.number), -1, -1))

    def get_headquarters(self):
        return self.headquarters

    def get_number(self):
        return self.number

    def get_name_player(self):
        return self.name_player

    def toggle_planet_in_play(self, planet_id):
        self.planets_in_play[planet_id] = not self.planets_in_play[planet_id]

    def toggle_turn(self):
        self.has_turn = not self.has_turn

    def get_turn(self):
        return self.has_turn

    def set_turn(self, new_turn):
        self.has_turn = new_turn

    def get_phase(self):
        return self.phase

    def set_phase(self, new_phase):
        self.phase = new_phase

    def get_top_card_removed(self):
        if not self.cards_removed_from_game:
            return None
        else:
            return self.cards_removed_from_game[-1]

    def get_top_card_discard(self):
        if not self.discard:
            return None
        else:
            return self.discard[-1]

    async def reveal_top_card_deck(self):
        if not self.deck:
            await self.game.send_update_message("No cards left!")
        else:
            card_name = self.deck[0]
            text = self.name_player + " reveals a " + card_name
            await self.game.send_update_message(text)

    def get_top_card_deck(self):
        if not self.deck:
            print("Deck is empty, you lose!")
            return None
        else:
            card = FindCard.find_card(self.deck[0], self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            return card

    def draw_card(self):
        if not self.deck:
            self.lost_due_to_deck = True
            print("Deck is empty, you lose!")
        else:
            self.cards.append(self.deck[0])
            del self.deck[0]

    def draw_card_at_location_deck(self, position):
        if not self.deck:
            print("Deck is empty, you lose!")
        else:
            if len(self.deck) > position:
                self.cards.append(self.deck[position])
                del self.deck[position]

    def play_card_to_battle_at_location_deck(self, planet_pos, deck_pos, card):
        if not self.deck:
            print("??? TRYING TO PLAY A CARD FROM DECK DESPITE DECK EMPTY ???")
        else:
            if len(self.deck) > deck_pos:
                if self.add_card_to_planet(card, planet_pos) != -1:
                    del self.deck[deck_pos]

    def discard_card_from_deck(self, deck_pos):
        if not self.deck:
            print("??? HOW DID YOU GET HERE ???")
        else:
            if len(self.deck) > deck_pos:
                self.add_card_to_discard(self.deck[deck_pos])
                del self.deck[deck_pos]

    def bottom_remaining_cards(self):
        if self.game.bottom_cards_after_search:
            if self.number_cards_to_search > len(self.deck):
                self.number_cards_to_search = len(self.deck) - 1
                if self.number_cards_to_search == -1:
                    self.number_cards_to_search = 0
            self.deck = self.deck[self.number_cards_to_search:] + self.deck[:self.number_cards_to_search]
        self.game.bottom_cards_after_search = True

    def spend_resources(self, amount):
        if amount > self.resources:
            return False
        else:
            if amount < 0:
                amount = 0
            self.resources = self.resources - amount
            return True

    def check_if_already_have_reaction(self, reaction_name):
        for i in range(len(self.game.reactions_needing_resolving)):
            if self.game.reactions_needing_resolving[i] == reaction_name:
                if self.game.player_who_resolves_reaction[i] == self.name_player:
                    return True
        return False

    def check_if_already_have_reaction_of_position(self, reaction_name, pla, pos):
        for i in range(len(self.game.reactions_needing_resolving)):
            if self.game.reactions_needing_resolving[i] == reaction_name:
                if self.game.player_who_resolves_reaction[i] == self.name_player:
                    num, og_pla, og_pos = self.game.positions_of_unit_triggering_reaction[i]
                    if num == int(self.number) and pla == og_pla and og_pos == pos:
                        return True
        return False

    def check_if_already_have_interrupt_of_position(self, interrupt_name, pla, pos):
        for i in range(len(self.game.interrupts_waiting_on_resolution)):
            if self.game.interrupts_waiting_on_resolution[i] == interrupt_name:
                if self.game.player_resolving_interrupts[i] == self.name_player:
                    num, og_pla, og_pos = self.game.positions_of_units_interrupting[i]
                    if num == int(self.number) and pla == og_pla and og_pos == pos:
                        return True
        return False

    def check_if_already_have_interrupt(self, interrupt_name):
        for i in range(len(self.game.interrupts_waiting_on_resolution)):
            if self.game.interrupts_waiting_on_resolution[i] == interrupt_name:
                if self.game.player_resolving_interrupts[i] == self.name_player:
                    return True
        return False

    def add_resources(self, amount, refund=False):
        if not refund:
            if not self.check_if_already_have_reaction("Dying Sun Marauder"):
                for i in range(len(self.headquarters)):
                    if self.get_ability_given_pos(-2, i) == "Dying Sun Marauder":
                        if not self.get_ready_given_pos(-2, i):
                            self.game.create_reaction("Dying Sun Marauder", self.name_player,
                                                      (int(self.number), -2, i))
                for i in range(7):
                    for j in range(len(self.cards_in_play[i + 1])):
                        if self.get_ability_given_pos(i, j) == "Dying Sun Marauder":
                            if not self.get_ready_given_pos(i, j):
                                self.game.create_reaction("Dying Sun Marauder", self.name_player,
                                                          (int(self.number), i, j))
        self.resources += amount

    def check_if_warlord(self, planet_id, unit_id):
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Warlord":
            return True
        return False

    def set_aiming_reticle_in_play(self, planet_id, unit_id, color="blue"):
        if planet_id == -2:
            self.headquarters[unit_id].aiming_reticle_color = color
        else:
            self.cards_in_play[planet_id + 1][unit_id].aiming_reticle_color = color

    def reset_aiming_reticle_in_play(self, planet_id, unit_id):
        if planet_id == -1 or unit_id == -1:
            return None
        if planet_id == -2:
            self.headquarters[unit_id].aiming_reticle_color = None
        else:
            self.cards_in_play[planet_id + 1][unit_id].aiming_reticle_color = None
        return None

    def discard_card_name_from_hand(self, card_name):
        for i in range(len(self.cards)):
            if self.cards[i] == card_name:
                self.discard_card_from_hand(i)
                return i
        return -1

    def ready_all_planet_attach(self):
        for i in range(7):
            self.ready_all_attached_at_planet(planet_pos=i)

    def ready_all_attached_at_planet(self, planet_pos):
        for i in range(len(self.attachments_at_planet[planet_pos])):
            if not self.attachments_at_planet[planet_pos][i].get_ready():
                self.attachments_at_planet[planet_pos][i].ready_card()

    def discard_card_from_hand(self, card_pos):
        if len(self.cards) > card_pos:
            self.add_card_to_discard(self.cards[card_pos])
            del self.cards[card_pos]

    def remove_card_from_hand(self, card_pos):
        del self.cards[card_pos]

    def remove_card_from_discard(self, card_pos):
        del self.discard[card_pos]

    def remove_card_name_from_discard(self, name):
        if name in self.discard:
            self.discard.remove(name)

    def remove_card_name_from_hand(self, name):
        if name in self.cards:
            self.cards.remove(name)

    def get_shields_given_pos(self, pos_in_hand, planet_pos=None, tank=False):
        shield_card_name = self.cards[pos_in_hand]
        card_object = FindCard.find_card(shield_card_name, self.card_array, self.cards_dict,
                                         self.apoka_errata_cards, self.cards_that_have_errata)
        shields = card_object.get_shields()
        if card_object.get_card_type() == "Support":
            if self.grigory_maksim_relevant:
                shields = 1
                if tank:
                    shields = 2
        if card_object.get_name() == "Humanity's Shield":
            shields = 2
        if card_object.get_name() == "The Phalanx":
            shields = self.phalanx_shield_value
        if card_object.get_name() == "Dal'yth Sept":
            if self.dalyth_sept_active:
                shields = 4
        if shields > 0:
            if card_object.get_faction() == "Tau":
                if planet_pos is not None:
                    if self.search_card_at_planet(planet_pos, "Fireblade Kais'vre"):
                        shields += 1
        return shields

    def get_damage_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_damage()
        return self.cards_in_play[planet_id + 1][unit_id].get_damage()

    def set_faith_given_pos(self, planet_id, unit_id, amount):
        if planet_id == -2:
            return self.headquarters[unit_id].set_faith(amount)
        return self.cards_in_play[planet_id + 1][unit_id].set_faith(amount)

    def set_damage_given_pos(self, planet_id, unit_id, amount):
        if planet_id == -2:
            return self.headquarters[unit_id].set_damage(amount)
        return self.cards_in_play[planet_id + 1][unit_id].set_damage(amount)

    def get_highest_cost_units(self):
        highest_cost = 0
        for i in range(len(self.headquarters)):
            if self.get_card_type_given_pos(-2, i) == "Army":
                cost = self.get_cost_given_pos(-2, i)
                if cost > highest_cost:
                    highest_cost = cost
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.get_card_type_given_pos(i, j) == "Army":
                    cost = self.get_cost_given_pos(i, j)
                    if cost > highest_cost:
                        highest_cost = cost
        return highest_cost

    def search_planet_attachments(self, planet_id, ability):
        for i in range(len(self.attachments_at_planet[planet_id])):
            if self.attachments_at_planet[planet_id][i].get_ability() == ability:
                return True
        return False

    def get_ranged_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ranged()
        if self.cards_in_play[planet_id + 1][unit_id].get_name() == "Guardsman":
            if self.search_planet_attachments(planet_id, "Planetary Defence Force"):
                return True
        if self.cards_in_play[planet_id + 1][unit_id].get_name() == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Termagant Spikers":
                    return True
        if self.search_attachments_at_pos(planet_id, unit_id, "Honorifica Imperialis"):
            if self.check_for_enemy_warlord(planet_id):
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Firstborn Battalion":
            if self.count_supports() > 2:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Vior'la Warrior Cadre":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.check_for_trait_given_pos(planet_id, i, "Ethereal"):
                    return True
        return self.cards_in_play[planet_id + 1][unit_id].get_ranged()

    def check_for_trait_given_pos(self, planet_id, unit_id, trait):
        if planet_id == -2:
            return self.headquarters[unit_id].check_for_a_trait(trait, self.etekh_trait)
        return self.cards_in_play[planet_id + 1][unit_id].check_for_a_trait(trait, self.etekh_trait)

    def make_warlord_hale_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            self.headquarters[unit_id].hale_warlord()
            name_card = self.headquarters[unit_id].get_name()
            if name_card == "Urien Rakarth":
                self.urien_relevant = True
            if name_card == "Gorzod":
                self.gorzod_relevant = True
            if name_card == "Subject Omega-X62113":
                self.subject_omega_relevant = True
            if name_card == "Grigory Maksim":
                self.grigory_maksim_relevant = True
            if name_card == "Illuminor Szeras":
                self.illuminor_szeras_relevant = True
            if name_card == "Kaptin Bluddflagg":
                self.bluddflagg_relevant = True
            if name_card == "Vael the Gifted":
                self.vael_relevent = True
            if name_card == "Castellan Crowe":
                self.castellan_crowe_2_relevant = True
            return None
        self.cards_in_play[planet_id + 1][unit_id].hale_warlord()
        name_card = self.cards_in_play[planet_id + 1][unit_id].get_name()
        if name_card == "Urien Rakarth":
            self.urien_relevant = True
        if name_card == "Gorzod":
            self.gorzod_relevant = True
        if name_card == "Subject Omega-X62113":
            self.subject_omega_relevant = True
        if name_card == "Grigory Maksim":
            self.grigory_maksim_relevant = True
        if name_card == "Illuminor Szeras":
            self.illuminor_szeras_relevant = True
        if name_card == "Kaptin Bluddflagg":
            self.bluddflagg_relevant = True
        if name_card == "Vael the Gifted":
            self.vael_relevent = True
        if name_card == "Castellan Crowe":
            self.castellan_crowe_2_relevant = True


    def bloody_warlord_given_pos(self, planet_id, unit_id):
        if planet_id != -2:
            self.cards_in_play[planet_id + 1][unit_id].bloody_warlord()
            self.cards_in_play[planet_id + 1][unit_id].ready = False
        else:
            self.headquarters[unit_id].bloody_warlord()
            self.headquarters[unit_id].ready = False
        self.urien_relevant = False
        self.gorzod_relevant = False
        self.subject_omega_relevant = False
        self.grigory_maksim_relevant = False
        self.illuminor_szeras_relevant = False
        self.bluddflagg_relevant = False
        self.vael_relevent = False
        self.castellan_crowe_2_relevant = False
        self.retreat_warlord()

    def shuffle_deck(self):
        shuffle(self.deck)

    def search_for_existing_relic(self):
        print("performing relic search")
        for i in range(len(self.headquarters)):
            if self.headquarters[i].check_for_a_trait("Relic"):
                if self.headquarters[i].name_owner == self.name_player:
                    return True
            for j in range(len(self.headquarters[i].get_attachments())):
                if self.headquarters[i].get_attachments()[j].check_for_a_trait("Relic"):
                    if self.headquarters[i].get_attachments()[j].name_owner == self.name_player:
                        return True
        print("not own hq")
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                if self.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait("Relic"):
                    if self.cards_in_play[planet_pos + 1][unit_pos].name_owner == self.name_player:
                        return True
                for attachment_pos in range(len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
                    if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]. \
                            check_for_a_trait("Relic"):
                        if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]. \
                                name_owner == self.name_player:
                            return True
        print("not own in play")
        if self.name_player == self.game.name_1:
            return self.game.p2.search_enemy_relic_in_own_cards()
        return self.game.p1.search_enemy_relic_in_own_cards()

    def search_enemy_relic_in_own_cards(self):
        name = self.game.name_1
        if name == self.name_player:
            name = self.game.name_2
        for i in range(len(self.headquarters)):
            if self.headquarters[i].check_for_a_trait("Relic"):
                if self.headquarters[i].name_owner == name:
                    return True
            for j in range(len(self.headquarters[i].get_attachments())):
                if self.headquarters[i].get_attachments()[j].check_for_a_trait("Relic"):
                    if self.headquarters[i].get_attachments()[j].name_owner == name:
                        return True
        print("not enemy hq")
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                if self.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait("Relic"):
                    if self.cards_in_play[planet_pos + 1][unit_pos].name_owner == name:
                        return True
                for attachment_pos in range(len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
                    if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]. \
                            check_for_a_trait("Relic"):
                        if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]. \
                                name_owner == name:
                            return True
        print("not enemy in play")
        return False

    def start_agras_preachings_deployment(self):
        for i in range(len(self.attachments_at_planet)):
            for j in range(len(self.attachments_at_planet[i])):
                if self.attachments_at_planet[i][j].shields == -1:
                    self.game.create_reaction("Agra's Preachings Deploy", self.name_player,
                                              (int(self.number), i, -1))

    def get_next_agras_preachings_name(self):
        for i in range(len(self.attachments_at_planet)):
            for j in range(len(self.attachments_at_planet[i])):
                if self.attachments_at_planet[i][j].shields == -1:
                    return self.attachments_at_planet[i][j].name
        return ""

    def delete_next_agras_preachings_name(self):
        for i in range(len(self.attachments_at_planet)):
            for j in range(len(self.attachments_at_planet[i])):
                if self.attachments_at_planet[i][j].shields == -1:
                    del self.attachments_at_planet[i][j]
                    return None
        return None

    def search_for_unique_card(self, name):
        print("performing uniques search")
        for i in range(len(self.headquarters)):
            if self.headquarters[i].name == name:
                return True
            for j in range(len(self.headquarters[i].get_attachments())):
                if self.headquarters[i].get_attachments()[j].name == name:
                    return True
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                if self.cards_in_play[planet_pos + 1][unit_pos].name == name:
                    return True
                for attachment_pos in range(len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
                    if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].name == name:
                        return True
        for i in range(len(self.attachments_at_planet)):
            for j in range(len(self.attachments_at_planet[i])):
                if self.attachments_at_planet[i][j].name == name:
                    return True
        return False

    def adjust_last_def_pos(self, planet_pos, unit_pos):
        num, pla, pos = self.game.last_defender_position
        if int(num) == int(self.number):
            if pla == planet_pos:
                if pos == unit_pos:
                    self.game.last_defender_position = (num, pla, -1)
                if pos > unit_pos:
                    pos -= 1
                    self.game.last_defender_position = (num, pla, pos)

    def controls_no_ranged_units(self):
        for i in range(len(self.headquarters)):
            if self.check_is_unit_at_pos(-2, i):
                if self.get_ranged_given_pos(-2, i):
                    return False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.get_ranged_given_pos(i, j):
                    return False
        return True

    def adjust_own_damage(self, planet_pos, unit_pos):
        i = 0
        while i < len(self.game.recently_damaged_units):
            num, pla, pos = self.game.recently_damaged_units[i]
            if num == int(self.number):
                if pla == planet_pos:
                    if pos > unit_pos:
                        pos -= 1
                        self.game.recently_damaged_units[i] = (num, pla, pos)
                    elif pos == unit_pos:
                        del self.game.recently_damaged_units[i]
                        del self.game.damage_taken_was_from_attack[i]
                        del self.game.positions_of_attacker_of_unit_that_took_damage[i]
                        del self.game.faction_of_attacker[i]
                        del self.game.card_names_that_caused_damage[i]
                        del self.game.on_kill_effects_of_attacker[i]
                        i = i - 1
            i = i + 1
        i = 0
        while i < len(self.game.amount_that_can_be_removed_by_shield):
            num, pla, pos = self.game.positions_of_units_to_take_damage[i]
            if num == int(self.number):
                if pla == planet_pos:
                    if pos > unit_pos:
                        pos -= 1
                        self.game.positions_of_units_to_take_damage[i] = (num, pla, pos)
                    elif pos == unit_pos:
                        if i == 0:
                            if not self.game.retaliate_used:
                                del self.game.damage_on_units_list_before_new_damage[i]
                                del self.game.damage_is_preventable[i]
                                del self.game.positions_of_units_to_take_damage[i]
                                del self.game.damage_can_be_shielded[i]
                                del self.game.positions_attackers_of_units_to_take_damage[i]
                                del self.game.card_names_triggering_damage[i]
                                del self.game.amount_that_can_be_removed_by_shield[i]
                                i = i - 1
                        else:
                            del self.game.damage_on_units_list_before_new_damage[i]
                            del self.game.damage_is_preventable[i]
                            del self.game.positions_of_units_to_take_damage[i]
                            del self.game.damage_can_be_shielded[i]
                            del self.game.positions_attackers_of_units_to_take_damage[i]
                            del self.game.card_names_triggering_damage[i]
                            del self.game.amount_that_can_be_removed_by_shield[i]
                            i = i - 1
            i += 1

    def adjust_own_reactions(self, planet_pos, unit_pos):
        i = 0
        while i < len(self.game.reactions_needing_resolving):
            num, pla, pos = self.game.positions_of_unit_triggering_reaction[i]
            if num == int(self.number):
                if pla == planet_pos:
                    if pos > unit_pos:
                        pos -= 1
                        self.game.positions_of_unit_triggering_reaction[i] = (num, pla, pos)
                    elif pos == unit_pos:
                        if i == 0:
                            if not self.game.already_resolving_reaction:
                                del self.game.reactions_needing_resolving[i]
                                del self.game.player_who_resolves_reaction[i]
                                del self.game.positions_of_unit_triggering_reaction[i]
                                del self.game.additional_reactions_info[i]
                                i = i - 1
                        else:
                            del self.game.reactions_needing_resolving[i]
                            del self.game.player_who_resolves_reaction[i]
                            del self.game.positions_of_unit_triggering_reaction[i]
                            del self.game.additional_reactions_info[i]
                            i = i - 1
            i += 1
        i = 0
        while i < len(self.game.delayed_reactions_needing_resolving):
            num, pla, pos = self.game.delayed_positions_of_unit_triggering_reaction[i]
            if num == int(self.number):
                if pla == planet_pos:
                    if pos > unit_pos:
                        pos -= 1
                        self.game.delayed_positions_of_unit_triggering_reaction[i] = (num, pla, pos)
                    elif pos == unit_pos:
                        del self.game.delayed_reactions_needing_resolving[i]
                        del self.game.delayed_player_who_resolves_reaction[i]
                        del self.game.delayed_positions_of_unit_triggering_reaction[i]
                        del self.game.delayed_additional_reactions_info[i]
                        i = i - 1
            i += 1

    def adjust_own_interrupts(self, planet_pos, unit_pos):
        i = 0
        while i < len(self.game.interrupts_waiting_on_resolution):
            num, pla, pos = self.game.positions_of_units_interrupting[i]
            if num == int(self.number):
                if pla == planet_pos:
                    if pos > unit_pos:
                        pos -= 1
                        self.game.positions_of_units_interrupting[i] = (num, pla, pos)
                    elif pos == unit_pos:
                        if i == 0:
                            pass
                        else:
                            del self.game.interrupts_waiting_on_resolution[i]
                            del self.game.positions_of_units_interrupting[i]
                            del self.game.player_resolving_interrupts[i]
                            del self.game.extra_interrupt_info[i]
                            i = i - 1
            i += 1

    def sort_hand(self):
        army_cards = []
        army_costs = []
        support_cards = []
        support_costs = []
        event_cards = []
        event_costs = []
        attachment_cards = []
        attachment_costs = []
        for i in range(len(self.cards)):
            card = self.game.preloaded_find_card(self.cards[i])
            card_type = card.get_card_type()
            name = card.get_name()
            cost = card.get_cost()
            if card_type == "Army":
                army_cards.append(name)
                army_costs.append(cost)
            if card_type == "Support":
                support_cards.append(name)
                support_costs.append(cost)
            if card_type == "Event":
                event_cards.append(name)
                event_costs.append(cost)
            if card_type == "Attachment":
                attachment_cards.append(name)
                attachment_costs.append(cost)
        army_cards = [x for _, x in sorted(zip(army_costs, army_cards))]
        support_cards = [x for _, x in sorted(zip(support_costs, support_cards))]
        attachment_cards = [x for _, x in sorted(zip(attachment_costs, attachment_cards))]
        event_cards = [x for _, x in sorted(zip(event_costs, event_cards))]
        self.cards = army_cards + support_cards + event_cards + attachment_cards

    def idden_base_detransform(self, force=False):
        for i in range(7):
            j = 0
            while j < len(self.cards_in_play[i + 1]):
                if self.cards_in_play[i + 1][j].actually_a_deepstrike and (not self.cards_in_play[i + 1][j].not_idden_base_src or force):
                    self.discard_attachments_from_card(i, j)
                    card = self.game.preloaded_find_card(self.cards_in_play[i + 1][j].deepstrike_card_name)
                    self.put_card_into_reserve(card, i, payment=False)
                    del self.cards_in_play[i + 1][j]
                    j = j - 1
                j = j + 1
        j = 0
        while j < len(self.headquarters):
            if self.headquarters[j].actually_a_deepstrike and (not self.headquarters[j].not_idden_base_src or force):
                self.discard_attachments_from_card(-2, j)
                card = self.game.preloaded_find_card(self.headquarters[j].deepstrike_card_name)
                self.put_card_into_reserve(card, -2, payment=False)
                del self.headquarters[j]
                j = j - 1
            j = j + 1

    def idden_base_transform(self):
        for i in range(7):
            while self.cards_in_reserve[i]:
                card = CardClasses.ArmyCard("Cardback", "I am a Deepstriked Card.", "",
                                            0, "Orks", "Common", 2, 2, 0, False)
                card.actually_a_deepstrike = True
                card.deepstrike_card_name = self.cards_in_reserve[i][0].get_name()
                card.name_owner = self.name_player
                self.cards_in_play[i + 1].append(card)
                del self.cards_in_reserve[i][0]
        while self.cards_in_reserve_hq:
            card = CardClasses.ArmyCard("Cardback", "I am a Deepstriked Card.", "",
                                        0, "Orks", "Common", 2, 2, 0, False)
            card.actually_a_deepstrike = True
            card.deepstrike_card_name = self.cards_in_reserve_hq[0].get_name()
            card.name_owner = self.name_player
            self.headquarters.append(card)
            del self.cards_in_reserve_hq[0]

    def add_to_hq(self, card_object):
        if card_object.get_unique():
            if self.search_for_unique_card(card_object.name):
                return False
        self.headquarters.append(copy.deepcopy(card_object))
        position = -2
        last_element_index = len(self.headquarters) - 1
        self.headquarters[last_element_index].name_owner = self.name_player
        other_player = self.get_other_player()
        if self.get_card_type_given_pos(-2, last_element_index) == "Army":
            if self.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(-2, last_element_index, 1, by_enemy_unit=False)
            enemy_player = self.game.p1
            if enemy_player.name_player == self.name_player:
                enemy_player = self.game.p2
            if enemy_player.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(-2, last_element_index, 1, by_enemy_unit=False)
        if self.check_is_unit_at_pos(-2, last_element_index):
            if other_player.search_for_card_everywhere("Magus Harid", bloodied_relevant=True, limit_round_rel=True):
                if not other_player.check_if_already_have_reaction("Magus Harid"):
                    self.game.create_reaction("Magus Harid", other_player.name_player, (int(other_player.number), -1, -1))
                self.headquarters[last_element_index].valid_target_magus_harid = True
        if self.get_ability_given_pos(-2, last_element_index) == "Augmented Warriors":
            self.assign_damage_to_pos(-2, last_element_index, 2, preventable=False, by_enemy_unit=False)
        elif self.headquarters[last_element_index].get_ability() == "Promethium Mine":
            self.headquarters[last_element_index].set_counter(4)
        if self.get_ability_given_pos(-2, last_element_index) == "Convoking Praetorians":
            self.game.create_reaction("Convoking Praetorians", self.name_player,
                                      (int(self.number), -2, last_element_index))
        if self.get_ability_given_pos(-2, last_element_index) == "Scavenging Kroot Rider":
            self.game.create_reaction("Scavenging Kroot Rider", self.name_player, (int(self.number), -2,
                                                                                   last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Raven Guard Legion":
            self.game.create_reaction("Raven Guard Legion", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(-2, last_element_index) == "Elusive Escort":
            self.game.create_reaction("Elusive Escort", self.name_player, (int(self.number), -2,
                                                                           last_element_index))
        if self.get_ability_given_pos(-2, last_element_index) == "Support Fleet":
            self.game.create_reaction("Support Fleet", self.name_player, (int(self.number), -2, last_element_index))
        if self.get_ability_given_pos(-2, last_element_index) == "Devoted Hospitaller":
            self.game.create_reaction("Devoted Hospitaller", self.name_player,
                                      (int(self.number), -2, last_element_index))
        if self.get_ability_given_pos(-2, last_element_index) == "Advocator of Blood":
            self.game.create_reaction("Advocator of Blood", self.name_player,
                                      (int(self.number), -2, last_element_index))
        if self.check_for_trait_given_pos(-2, last_element_index, "Khorne") and \
                self.get_card_type_given_pos(-2, last_element_index) == "Army":
            for i in range(len(self.headquarters)):
                if self.get_ability_given_pos(-2, i) == "Cult of Khorne":
                    self.game.create_reaction("Cult of Khorne", self.name_player,
                                              (int(self.number), -2, i))
        if self.get_card_type_given_pos(-2, last_element_index) == "Support":
            if self.search_card_in_hq("Citadel of Vamii"):
                self.game.create_reaction("Citadel of Vamii", self.name_player,
                                          (int(self.number), -2, last_element_index))
            if other_player.search_card_in_hq("Citadel of Vamii"):
                self.game.create_reaction("Citadel of Vamii", other_player.name_player,
                                          (int(self.number), -2, last_element_index))
        if self.get_ability_given_pos(-2, last_element_index) == "Court of the Stormlord":
            self.game.create_reaction("Court of the Stormlord", self.name_player,
                                      (int(self.number), -2, last_element_index))
        elif self.get_ability_given_pos(-2, last_element_index) == "Flayed Ones Revenants":
            self.game.create_interrupt("Flayed Ones Revenants", self.name_player,
                                       (int(self.number), -2, last_element_index))
        elif self.get_ability_given_pos(position, last_element_index) == "Awakened Geomancer":
            self.game.create_reaction("Awakened Geomancer", self.name_player, (int(self.number), position,
                                                                               last_element_index))
        elif self.headquarters[last_element_index].get_ability() == "Heretek Inventor":
            enemy_name = self.game.name_1
            if self.name_player == self.game.name_1:
                enemy_name = self.game.name_2
            self.game.create_reaction("Heretek Inventor", enemy_name,
                                      (int(self.number), -2, last_element_index))
        elif self.headquarters[last_element_index].get_ability() == "Coliseum Fighters":
            self.game.create_reaction("Coliseum Fighters", self.name_player,
                                      (int(self.number), -2, last_element_index))
        elif self.headquarters[last_element_index].get_ability() == "Swordwind Farseer":
            self.game.create_reaction("Swordwind Farseer", self.name_player,
                                      (int(self.number), -2, last_element_index))
        elif self.headquarters[last_element_index].get_ability() == "Inquisitor Caius Wroth":
            self.game.create_reaction("Inquisitor Caius Wroth", self.name_player,
                                      (int(self.number), -2, last_element_index))
        elif self.headquarters[last_element_index].get_ability() == "Coliseum Fighters":
            self.game.create_reaction("Coliseum Fighters", self.name_player,
                                      (int(self.number), -2, last_element_index))
        elif self.headquarters[last_element_index].get_ability() == "Earth Caste Technician":
            self.game.create_reaction("Earth Caste Technician", self.name_player,
                                      (int(self.number), -2, last_element_index))
        self.headquarters[last_element_index].card_id = self.game.current_card_id
        self.game.current_card_id += 1
        return True

    def print_headquarters(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].print_info()

    def play_card_if_support(self, position_hand, already_checked=False, card=None):
        if already_checked:
            played_card = self.play_card(-2, card=card)
            if played_card == "SUCCESS":
                return "SUCCESS/Support"
            return played_card
        card = FindCard.find_card(self.cards[position_hand], self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)
        if card.card_type == "Support":
            print("Need to play support card")
            played_card = self.play_card(-2, card=card)
            if played_card == "SUCCESS":
                return "SUCCESS/Support"
            return played_card
        return "SUCCESS/Not Support"

    def get_unique_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            return self.headquarters[unit_pos].get_unique()
        return self.cards_in_play[planet_pos + 1][unit_pos].get_unique()

    def get_has_faith_given_pos(self, planet_pos, unit_pos):
        if self.castellan_crowe_relevant:
            return True
        elif self.get_faith_given_pos(planet_pos, unit_pos) > 0:
            return True
        return False

    def get_faith_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            return self.headquarters[unit_pos].get_faith()
        return self.cards_in_play[planet_pos + 1][unit_pos].get_faith()

    def place_faith_given_pos(self, planet_pos, unit_pos, faith):
        self.increase_faith_given_pos(planet_pos, unit_pos, faith)

    def increase_faith_given_pos(self, planet_pos, unit_pos, faith):
        if planet_pos == -2:
            self.headquarters[unit_pos].increase_faith(faith)
            return None
        self.cards_in_play[planet_pos + 1][unit_pos].increase_faith(faith)
        return None

    def remove_faith_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            self.headquarters[unit_pos].remove_all_faith()
            return None
        self.cards_in_play[planet_pos + 1][unit_pos].remove_all_faith()
        return None

    def spend_faith_given_pos(self, planet_pos, unit_pos, faith):
        if planet_pos == -2:
            return self.headquarters[unit_pos].spend_faith(faith)
        return self.cards_in_play[planet_pos + 1][unit_pos].spend_faith(faith)

    def remove_all_faith_in_play(self):
        for i in range(len(self.headquarters)):
            if self.check_is_unit_at_pos(-2, i):
                if not self.search_attachments_at_pos(-2, i, "Servo-Harness"):
                    self.remove_faith_given_pos(-2, i)
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if not self.search_attachments_at_pos(i, j, "Servo-Harness"):
                    self.remove_faith_given_pos(i, j)

    def get_sweep_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            return self.headquarters[unit_pos].get_sweep()
        sweep_value = self.cards_in_play[planet_pos + 1][unit_pos].get_sweep()
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Raiding Kabal":
            if planet_pos != self.game.round_number:
                sweep_value += 1
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Kastelan Crusher":
            if self.get_has_faith_given_pos(planet_pos, unit_pos):
                sweep_value += 3
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.get_ability_given_pos(planet_pos, i) == "Great Unclean One":
                sweep_value += 2
        return sweep_value

    def get_card_in_hand(self, position_hand):
        card = FindCard.find_card(self.cards[position_hand], self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)
        return card

    def get_card_in_discard(self, position_discard):
        card = FindCard.find_card(self.discard[position_discard], self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)
        return card

    def get_discard(self):
        return self.discard

    def move_attachment_card(self, origin_planet, origin_position, origin_attachment_position,
                             destination_planet, destination_position):
        if origin_planet == -2:
            target_attachment = self.headquarters[origin_position].get_attachments()[origin_attachment_position]
        else:
            target_attachment = self.cards_in_play[origin_planet + 1][origin_position]. \
                get_attachments()[origin_attachment_position]
        # if destination_planet == -2:
        #     target_card = self.headquarters[destination_position]
        # else:
        #     target_card = self.cards_in_play[destination_planet + 1][destination_position]
        print("Moving attachment code")
        army_unit_as_attachment = False
        if target_attachment.get_ability() == "Gun Drones" or \
                target_attachment.get_ability() == "Shadowsun's Stealth Cadre" or \
                target_attachment.get_ability() == "Escort Drone":
            army_unit_as_attachment = True
        if self.attach_card(card=target_attachment, planet=destination_planet, position=destination_position,
                            not_own_attachment=False,
                            army_unit_as_attachment=army_unit_as_attachment):
            self.remove_attachment_from_pos(origin_planet, origin_position, origin_attachment_position)
            return True
        return False

    def destroy_attachment_from_pos(self, planet, position, attachment_position):
        self.remove_attachment_from_pos(planet, position, attachment_position, discard=True)

    def sacrifice_attachment_from_pos(self, planet, position, attachment_position):
        self.discard_attachment_at_pos(planet, position, attachment_position)

    def remove_attachment_from_pos(self, planet, position, attachment_position, discard=False):
        if planet == -2:
            card = self.headquarters[position]
            if discard:
                self.add_card_to_discard(card.get_attachments()[attachment_position].get_name())
            del card.get_attachments()[attachment_position]
        else:
            card = self.cards_in_play[planet + 1][position]
            if discard:
                self.add_card_to_discard(card.get_attachments()[attachment_position].get_name())
            del card.get_attachments()[attachment_position]

    def get_all_attachments_at_pos(self, planet, position):
        if planet == -2:
            return self.headquarters[position].get_attachments()
        return self.cards_in_play[planet + 1][position].get_attachments()

    def get_attachment_at_pos(self, planet, position, attachment_position):
        if planet == -2:
            return self.headquarters[position].get_attachments()[attachment_position]
        return self.cards_in_play[planet + 1][position].get_attachments()[attachment_position]

    def attach_card(self, card, planet, position, not_own_attachment=False, army_unit_as_attachment=False):
        if planet == -2:
            target_card = self.headquarters[position]
        else:
            target_card = self.cards_in_play[planet + 1][position]
        print("Adding attachment code")
        print(card.get_name())
        print(target_card.get_no_attachments())
        type_of_card = target_card.get_card_type()
        if army_unit_as_attachment:
            if type_of_card != "Army":
                print("Army units as attachments can only be attached to other army units")
                return False
            if target_card.get_no_attachments():
                print("Unit may not have attachments")
                return False
            if target_card.check_for_a_trait("Vehicle"):
                print("Vehicles may not have army units as attachments")
                return False
            name_owner = self.name_player
            if not_own_attachment:
                if self.number == "1":
                    name_owner = self.game.p2.name_player
                elif self.number == "2":
                    name_owner = self.game.p1.name_player
            target_card.add_attachment(card, name_owner=name_owner)
            self.game.queued_sound = "onplay"
            return True
        allowed_types = card.type_of_units_allowed_for_attachment
        if type_of_card not in allowed_types:
            print("Can't play to this card type.", type_of_card, allowed_types)
            return False
        if card.unit_must_match_faction:
            if card.get_faction() != target_card.get_faction():
                return False
        if card.required_traits not in target_card.get_traits():
            if card.get_name() == "Drone Defense System":
                if not target_card.check_for_a_trait("Pilot") and not target_card.check_for_a_trait("Vehicle"):
                    return False
            elif card.get_name() == "Missile Pod":
                if not target_card.check_for_a_trait("Pilot") and not target_card.check_for_a_trait("Vehicle"):
                    return False
            else:
                print("Wrong traits.")
                return False
        if card.get_ability() == "Raging Daemonhost":
            if "Vehicle" in target_card.get_traits() or "Daemon" in target_card.get_traits():
                return False
        if card.forbidden_traits in target_card.get_traits():
            return False
        if card.unit_must_be_unique:
            if not target_card.get_unique():
                print("Must be a unique unit, but is not")
                return False
        if card.limit_one_per_unit:
            attachments_active = target_card.get_attachments()
            for i in range(len(attachments_active)):
                if attachments_active[i].get_name() == card.get_name() and not attachments_active[i].from_magus_harid:
                    print("Limit one per unit")
                    return False
        if target_card.get_no_attachments():
            print("Unit may not have attachments")
            return False
        if card.check_for_a_trait("Wargear"):
            if not target_card.get_wargear_attachments_permitted():
                print("Unit may not have wargear")
                return False
        if card.get_name() == "The Shining Blade":
            if not target_card.get_mobile():
                return False
        if card.get_name() == "Flesh Hooks" and not card.from_magus_harid:
            if target_card.get_cost() > 2:
                return False
        name_owner = self.name_player
        if not_own_attachment:
            if self.number == "1":
                name_owner = self.game.p2.name_player
            elif self.number == "2":
                name_owner = self.game.p1.name_player
        target_card.add_attachment(card, name_owner=name_owner)
        if card.get_ability() == "Fusion Cascade Defiance":
            if planet != -2:
                self.game.create_reaction("Fusion Cascade Defiance", self.name_player,
                                          (int(self.number), planet, position))
        if not not_own_attachment:
            if planet != -2 and not card.check_for_a_trait("Drone"):
                for i in range(len(self.cards_in_play[planet + 1])):
                    if self.get_ability_given_pos(planet, i) == "Commander Bravestorm":
                        if not self.get_once_per_phase_used_given_pos(planet, i) or not self.game.apoka:
                            self.game.create_reaction("Commander Bravestorm", self.name_player,
                                                      (int(self.number), planet, i))
        self.game.queued_sound = "onplay"
        return True

    def enemy_holding_cell_check(self, card_name):
        if self.name_player == self.game.name_1:
            other_player = self.game.p2
        else:
            other_player = self.game.p1
        for i in range(len(other_player.headquarters)):
            if other_player.headquarters[i].get_ability() == "Holding Cell":
                for j in range(len(other_player.headquarters[i].get_attachments())):
                    if other_player.headquarters[i].get_attachments()[j].get_name() == card_name:
                        return True
        return False

    def play_attachment_card_to_in_play(self, card, planet, position, discounts=0, not_own_attachment=False,
                                        army_unit_as_attachment=False):
        if card.get_unique():
            if self.search_for_unique_card(card.name):
                return False
        if card.check_for_a_trait("Relic"):
            if self.search_for_existing_relic():
                return False
        if army_unit_as_attachment:
            if not_own_attachment:
                if self.attach_card(card, planet, position, not_own_attachment,
                                    army_unit_as_attachment=army_unit_as_attachment):
                    return True
                return False
            if self.get_ability_given_pos(planet, position) == "Junk Chucka Kommando":
                discounts += 1
            cost = card.get_cost() - discounts
            if cost < 0:
                cost = 0
            if self.spend_resources(cost):
                if self.attach_card(card, planet, position, not_own_attachment,
                                    army_unit_as_attachment=army_unit_as_attachment):
                    return True
                self.add_resources(cost, refund=True)
        else:
            if card.must_be_own_unit and not_own_attachment:
                print("Must be own unit, but is not")
                return False
            if card.must_be_enemy_unit and not not_own_attachment:
                print("Must be enemy unit, but is not")
                return False
            if not_own_attachment:
                if self.attach_card(card, planet, position, not_own_attachment):
                    return True
                return False
            if self.get_ability_given_pos(planet, position) == "Junk Chucka Kommando":
                discounts += 1
            cost = card.get_cost() - discounts
            if cost < 0:
                cost = 0
            if self.spend_resources(cost):
                if self.attach_card(card, planet, position, not_own_attachment):
                    return True
                self.add_resources(cost, refund=True)
        return False

    def get_name_enemy_player(self):
        name = self.name_player
        if self.name_player == self.game.name_1:
            name = self.game.name_2
        else:
            name = self.game.name_1
        return name

    def get_card_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            return self.headquarters[unit_pos]
        return self.cards_in_play[planet_pos + 1][unit_pos]

    def add_card_to_planet(self, card, position, sacrifice_end_of_phase=False, already_exhausted=False,
                           is_owner_of_card=True, triggered_card_effect=True):
        if position == -2:
            return self.add_to_hq(card)
        if card.get_unique():
            if self.search_for_unique_card(card.name):
                return -1
        if triggered_card_effect and not card.check_for_a_trait("Runt", etekh_trait=self.etekh_trait):
            resources_to_spend = self.game.imperial_blockades_active[position]
            if resources_to_spend:
                if not self.spend_resources(resources_to_spend):
                    self.game.queued_message = "Important Info: Imperial Blockade prevented a card from being added."
                    return -1
                else:
                    self.game.queued_message = "Important Info: " + str(resources_to_spend) + \
                                               " resources were spent due to Imperial Blockade."
        if card.get_card_type() == "Army" and self.game.phase == "COMBAT":
            if self.game.planet_array[position] == "Fenos":
                return -1
        self.cards_in_play[position + 1].append(copy.deepcopy(card))
        last_element_index = len(self.cards_in_play[position + 1]) - 1
        self.cards_in_play[position + 1][last_element_index].name_owner = self.name_player
        self.cards_in_play[position + 1][last_element_index].just_entered_play = True
        self.cards_in_play[position + 1][last_element_index].card_id = self.game.current_card_id
        self.game.current_card_id += 1
        other_player = self.get_other_player()
        if other_player.search_for_card_everywhere("Magus Harid", bloodied_relevant=True, limit_round_rel=True):
            if not other_player.check_if_already_have_reaction("Magus Harid"):
                self.game.create_reaction("Magus Harid", other_player.name_player, (int(other_player.number), -1, -1))
            self.cards_in_play[position + 1][last_element_index].valid_target_magus_harid = True
        if other_player.search_card_at_planet(position, "Eloquent Confessor"):
            if self.game.phase == "COMBAT":
                self.game.create_reaction("Eloquent Confessor", other_player.name_player,
                                          (int(self.number), position, last_element_index))
        if card.get_card_type() == "Army":
            if other_player.resources > 1:
                if other_player.search_hand_for_card("Catatonic Pain"):
                    self.game.create_reaction("Catatonic Pain", other_player.name_player,
                                              (int(self.number), position, last_element_index))
            for i in range(len(other_player.cards_in_play[position + 1])):
                if card.command > 1:
                    if other_player.get_ability_given_pos(position, i) == "Iron Hands Platoon":
                        self.game.create_reaction("Iron Hands Platoon", other_player.name_player,
                                                  (int(self.number), position, last_element_index))
                if other_player.resources > 0:
                    if other_player.get_unique_given_pos(position, i):
                        if not other_player.check_if_already_have_reaction("The Inevitable Decay"):
                            if "The Inevitable Decay" in other_player.cards:
                                self.game.create_reaction("The Inevitable Decay", other_player.name_player,
                                                          (int(self.number), -1, -1))
                            elif "The Inevitable Decay" in other_player.cards_removed_from_game:
                                warlord_pla, warlord_pos = other_player.get_location_of_warlord()
                                vael_relevant = False
                                if other_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                                        other_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                                    vael_relevant = True
                                elif other_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                                        and not other_player.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                                    vael_relevant = True
                                if vael_relevant:
                                    self.game.create_reaction("The Inevitable Decay", other_player.name_player,
                                                              (int(self.number), -1, -1))
        if position != 0:
            for i in range(len(other_player.cards_in_play[position])):
                if other_player.get_ability_given_pos(position - 1, i) == "Interceptor Squad":
                    if not other_player.get_once_per_phase_used_given_pos(position - 1, i):
                        if not other_player.check_if_already_have_reaction_of_position("Interceptor Squad",
                                                                                       position - 1, i):
                            self.game.create_reaction("Interceptor Squad", other_player.name_player,
                                                      (int(other_player.number), position - 1, i))
            for i in range(len(self.cards_in_play[position])):
                if self.get_ability_given_pos(position - 1, i) == "Interceptor Squad":
                    if not self.get_once_per_phase_used_given_pos(position - 1, i):
                        if not self.check_if_already_have_reaction_of_position("Interceptor Squad",
                                                                               position - 1, i):
                            self.game.create_reaction("Interceptor Squad", self.name_player,
                                                      (int(self.number), position - 1, i))
        if position != 6:
            for i in range(len(other_player.cards_in_play[position + 2])):
                if other_player.get_ability_given_pos(position + 1, i) == "Interceptor Squad":
                    if not other_player.get_once_per_phase_used_given_pos(position + 1, i):
                        if not other_player.check_if_already_have_reaction_of_position("Interceptor Squad",
                                                                                       position + 1, i):
                            self.game.create_reaction("Interceptor Squad", other_player.name_player,
                                                      (int(other_player.number), position + 1, i))
            for i in range(len(self.cards_in_play[position + 2])):
                if self.get_ability_given_pos(position + 1, i) == "Interceptor Squad":
                    if not self.get_once_per_phase_used_given_pos(position + 1, i):
                        if not self.check_if_already_have_reaction_of_position("Interceptor Squad",
                                                                               position + 1, i):
                            self.game.create_reaction("Interceptor Squad", self.name_player,
                                                      (int(self.number), position + 1, i))
        if not is_owner_of_card:
            self.cards_in_play[position + 1][last_element_index].name_owner = self.get_name_enemy_player()
        if self.get_card_type_given_pos(position, last_element_index) == "Army":
            if self.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(position, last_element_index, 1, by_enemy_unit=False)
            enemy_player = self.game.p1
            if enemy_player.name_player == self.name_player:
                enemy_player = self.game.p2
            if enemy_player.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(position, last_element_index, 1, by_enemy_unit=False)
            if enemy_player.contaminated_convoys:
                self.game.infest_planet(position, enemy_player)
                enemy_player.summon_token_at_planet("Termagant", position)
            if self.check_for_trait_given_pos(position, last_element_index, "Psyker"):
                for i in range(len(other_player.cards_in_play[position + 1])):
                    if other_player.get_ability_given_pos(position, i) == "Repurposed Pariah":
                        if not other_player.get_once_per_phase_used_given_pos(position, i):
                            self.game.create_reaction("Repurposed Pariah", other_player.name_player,
                                                      (int(other_player.number), position, i),
                                                      additional_info=(position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Augmented Warriors":
            self.assign_damage_to_pos(position, last_element_index, 2, preventable=False, by_enemy_unit=False)
        if self.get_ability_given_pos(position, last_element_index) == "Flayed Ones Revenants":
            self.game.create_interrupt("Flayed Ones Revenants", self.name_player,
                                       (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Frenzied Wulfen":
            self.game.create_reaction("Frenzied Wulfen", self.name_player, (int(self.number), position,
                                                                            last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "The Blinded Princess":
            self.game.create_reaction("The Blinded Princess", self.name_player, (int(self.number), position,
                                                                                 last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Scavenging Kroot Rider":
            self.game.create_reaction("Scavenging Kroot Rider", self.name_player, (int(self.number), position,
                                                                                   last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Gue'vesa Overseer":
            self.game.create_reaction("Gue'vesa Overseer", self.name_player, (int(self.number), position,
                                                                              last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Awakened Geomancer":
            self.game.create_reaction("Awakened Geomancer", self.name_player, (int(self.number), position,
                                                                               last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Goff Shokboyz":
            self.game.create_reaction("Goff Shokboyz", self.name_player, (int(self.number), position,
                                                                          last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Elusive Escort":
            self.game.create_reaction("Elusive Escort", self.name_player, (int(self.number), position,
                                                                           last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Raven Guard Legion":
            self.game.create_reaction("Raven Guard Legion", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Herald of the WAAGH!":
            if self.game.phase == "DEPLOY":
                self.game.create_reaction("Herald of the WAAGH!", self.name_player, (int(self.number), position,
                                                                                     last_element_index))
        if self.check_for_trait_given_pos(position, last_element_index, "Khorne") and \
                self.get_card_type_given_pos(position, last_element_index) == "Army":
            for i in range(len(self.headquarters)):
                if self.get_ability_given_pos(-2, i) == "Cult of Khorne":
                    self.game.create_reaction("Cult of Khorne", self.name_player,
                                              (int(self.number), -2, i))
        if self.game.last_planet_checked_for_battle == position:
            if other_player.search_hand_for_card("Wrathful Retribution"):
                if not other_player.check_if_already_have_reaction("Wrathful Retribution"):
                    self.game.create_reaction("Wrathful Retribution", other_player.name_player,
                                              (int(other_player.number), -1, -1))
                    cost_card_wrath = self.get_cost_given_pos(position, last_element_index)
                    if other_player.wrathful_retribution_value < cost_card_wrath:
                        other_player.wrathful_retribution_value = cost_card_wrath
        if sacrifice_end_of_phase:
            self.cards_in_play[position + 1][last_element_index].set_sacrifice_end_of_phase(True)
        if self.cards_in_play[position + 1][last_element_index].get_ability() == "Heretek Inventor":
            enemy_name = self.game.name_1
            if self.name_player == self.game.name_1:
                enemy_name = self.game.name_2
            self.game.create_reaction("Heretek Inventor", enemy_name,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Griffon Escort":
            self.game.create_reaction("Griffon Escort", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Devoted Hospitaller":
            self.game.create_reaction("Devoted Hospitaller", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Advocator of Blood":
            self.game.create_reaction("Advocator of Blood", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Court of the Stormlord":
            self.game.create_reaction("Court of the Stormlord", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Convoking Praetorians":
            self.game.create_reaction("Convoking Praetorians", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.get_ability_given_pos(position, last_element_index) == "Spreading Genestealer Brood":
            self.game.create_reaction("Spreading Genestealer Brood", self.name_player,
                                      (int(self.number), position, last_element_index))
        if self.cards_in_play[position + 1][last_element_index].get_ability() == "Swordwind Farseer":
            self.game.create_reaction("Swordwind Farseer", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Mighty Wraithknight":
            self.game.create_reaction("Mighty Wraithknight", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Veteran Barbrus":
            self.game.create_reaction("Veteran Barbrus", self.name_player, (int(self.number), position,
                                                                            last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Vale Tenndrac":
            self.game.create_reaction("Vale Tenndrac", self.name_player, (int(self.number), position,
                                                                          last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Standard Bearer":
            self.game.create_reaction("Standard Bearer", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Coliseum Fighters":
            self.game.create_reaction("Coliseum Fighters", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Sicarius's Chosen":
            self.game.create_reaction("Sicarius's Chosen", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Weirdboy Maniak":
            self.game.create_reaction("Weirdboy Maniak", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Inquisitor Caius Wroth":
            self.game.create_reaction("Inquisitor Caius Wroth", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Earth Caste Technician":
            self.game.create_reaction("Earth Caste Technician", self.name_player,
                                      (int(self.number), position, last_element_index))
        if card.check_for_a_trait("Kabalite", self.etekh_trait) or card.check_for_a_trait("Raider", self.etekh_trait):
            if self.game.get_red_icon(position):
                if self.search_for_card_everywhere("Archon Salaine Morn", limit_phase_rel=True):
                    self.game.create_reaction("Archon Salaine Morn", self.name_player, (int(self.number), -1, -1))
        if card.check_for_a_trait("Kabalite", self.etekh_trait):
            for i in range(len(self.cards_in_play[position + 1])):
                if self.get_ability_given_pos(position, i) == "Kabalite Harriers":
                    self.game.create_reaction("Kabalite Harriers", self.name_player,
                                              (int(self.number), position, i))
        if already_exhausted:
            self.cards_in_play[position + 1][last_element_index].exhaust_card()
        return last_element_index

    def get_once_per_game_used_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_once_per_game_used()
        return self.cards_in_play[planet_id + 1][unit_id].get_once_per_game_used()

    def drammask_nane_check(self):
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.get_ability_given_pos(i, j) == "Drammask Nane":
                    self.game.create_reaction("Drammask Nane", self.name_player,
                                              (int(self.number), i, j))

    def return_cards_to_hand_eor(self):
        i = 0
        while i < len(self.headquarters):
            if self.headquarters[i].return_to_hand_eor:
                self.return_card_to_hand(-2, i, return_attachments=False)
                i = i - 1
            i = i + 1
        for i in range(7):
            j = 0
            while j < len(self.cards_in_play[i + 1]):
                if self.cards_in_play[i + 1][j].return_to_hand_eor:
                    self.return_card_to_hand(i, j, return_attachments=False)
                    j = j - 1
                j = j + 1

    def get_once_per_phase_used_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_once_per_phase_used()
        return self.cards_in_play[planet_id + 1][unit_id].get_once_per_phase_used()

    def get_once_per_round_used_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_once_per_round_used()
        return self.cards_in_play[planet_id + 1][unit_id].get_once_per_round_used()

    def set_once_per_game_used_given_pos(self, planet_id, unit_id, new_val):
        if planet_id == -2:
            self.headquarters[unit_id].set_once_per_game_used(new_val)
            return None
        self.cards_in_play[planet_id + 1][unit_id].set_once_per_game_used(new_val)
        return None

    def set_once_per_phase_used_given_pos(self, planet_id, unit_id, new_val=True):
        if planet_id == -2:
            self.headquarters[unit_id].set_once_per_phase_used(new_val)
            return None
        self.cards_in_play[planet_id + 1][unit_id].set_once_per_phase_used(new_val)
        return None

    def set_once_per_round_used_given_pos(self, planet_id, unit_id, new_val):
        if planet_id == -2:
            self.headquarters[unit_id].set_once_per_round_used(new_val)
            return None
        self.cards_in_play[planet_id + 1][unit_id].set_once_per_round_used(new_val)
        return None

    def get_cost_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            if self.get_ability_given_pos(planet_id, unit_id) == "Citadel of Vamii" or \
                    self.get_ability_given_pos(planet_id, unit_id) == "Citadel of Vamii":
                return 4
            return self.headquarters[unit_id].get_cost()
        return self.cards_in_play[planet_id + 1][unit_id].get_cost()

    def reset_resolving_attack_attribute_own(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].resolving_attack = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].resolving_attack = False

    def set_once_per_phase_used_of_att_name(self, planet_pos, unit_pos, name_attachment, value):
        if planet_pos == -2:
            for i in range(len(self.headquarters[unit_pos].get_attachments())):
                if self.headquarters[unit_pos].get_attachments()[i].get_name() == name_attachment:
                    self.headquarters[unit_pos].get_attachments()[i].set_once_per_phase_used(value)
                    return True
            return False
        for i in range(len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_name() == name_attachment:
                self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].set_once_per_phase_used(value)
                return True
        return False

    async def reveal_hand(self):
        string_sent = "; ".join(self.cards)
        string_sent = self.name_player + " reveals their hand: " + string_sent
        await self.game.send_update_message(string_sent)

    def torture_event_played(self, name=""):
        warlord_planet, warlord_pos = self.get_location_of_warlord()
        if self.search_attachments_at_pos(warlord_planet, warlord_pos, "Ichor Gauntlet"):
            if self.get_ready_given_pos(warlord_planet, warlord_pos):
                self.game.create_reaction("Ichor Gauntlet", self.name_player, (int(self.number), -1, -1))
                self.ichor_gauntlet_target = name
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Uber Grotesque":
                if not self.headquarters[i].once_per_phase_used:
                    self.game.create_reaction("Uber Grotesque", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Crucible of Malediction":
                if self.headquarters[i].get_ready():
                    self.game.create_reaction("Crucible of Malediction", self.name_player,
                                              (int(self.number), -2, i))
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == "Uber Grotesque":
                    if not self.cards_in_play[i + 1][j].once_per_phase_used:
                        self.game.create_reaction("Uber Grotesque", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Arrogant Haemonculus":
                    self.game.create_reaction("Arrogant Haemonculus", self.name_player, (int(self.number), i, j))

    def count_tortures_in_discard(self):
        count = 0
        for i in range(len(self.discard)):
            card = FindCard.find_card(self.discard[i], self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            if card.check_for_a_trait("Torture"):
                count += 1
        return count

    async def dark_eldar_event_played(self):
        self.reset_reaction_beasthunter_wyches()
        pain_crafter = False
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Beasthunter Wyches":
                self.game.create_reaction("Beasthunter Wyches", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Pain Crafter":
                if self.get_ready_given_pos(-2, i):
                    if not self.get_once_per_phase_used_given_pos(-2, i):
                        pain_crafter = True
            for attach in self.headquarters[i].get_attachments():
                if attach.get_ability() == "Hypex Injector" and attach.name_owner == self.name_player:
                    self.game.create_reaction("Hypex Injector", self.name_player, (int(self.number), -2, i))
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == "Beasthunter Wyches":
                    self.game.create_reaction("Beasthunter Wyches", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Pain Crafter":
                    if self.get_ready_given_pos(i, j):
                        if not self.get_once_per_phase_used_given_pos(i, j):
                            pain_crafter = True
                for attach in self.cards_in_play[i + 1][j].get_attachments():
                    if attach.get_ability() == "Hypex Injector" and attach.name_owner == self.name_player:
                        self.game.create_reaction("Hypex Injector", self.name_player, (int(self.number), i, j))
        if pain_crafter:
            self.game.create_reaction("Pain Crafter", self.name_player, (int(self.number), -1, -1))
        other_player = self.game.p1
        if other_player.name_player == self.name_player:
            other_player = self.game.p2
        for i in range(len(other_player.headquarters)):
            for attach in other_player.headquarters[i].get_attachments():
                if attach.get_ability() == "Hypex Injector" and attach.name_owner == self.name_player:
                    self.game.create_reaction("Hypex Injector", self.name_player, (int(other_player.number), -2, i))
        for i in range(7):
            for j in range(len(other_player.cards_in_play[i + 1])):
                for attach in other_player.cards_in_play[i + 1][j].get_attachments():
                    if attach.get_ability() == "Hypex Injector" and attach.name_owner == self.name_player:
                        self.game.create_reaction("Hypex Injector", self.name_player, (int(other_player.number), i, j))

    def put_card_in_hand_into_hq(self, hand_pos, unit_only=True):
        card = copy.deepcopy(FindCard.find_card(self.cards[hand_pos], self.card_array, self.cards_dict,
                                                self.apoka_errata_cards, self.cards_that_have_errata))
        if unit_only:
            if card.get_card_type() != "Army":
                return False
        self.add_to_hq(card)
        del self.cards[hand_pos]
        return True

    def play_card(self, position, card=None, position_hand=None, discounts=0, damage_to_take=0,
                  is_owner_of_card=True):
        damage_on_play = damage_to_take
        if position_hand is not None:
            return "ERROR/play_card function called incorrectly", -1
        if card is None:
            return "ERROR/play_card function called incorrectly", -1
        if card is not None:
            if card.get_card_type() == "Support":
                warlord_pla, warlord_pos = self.get_location_of_warlord()
                if self.get_ability_given_pos(warlord_pla, warlord_pos) == "Chapter Champion Varn" or \
                        self.get_ability_given_pos(warlord_pla, warlord_pos) == "Chapter Champion Varn BLOODIED":
                    if not self.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                        discounts += 1
                        self.set_once_per_round_used_given_pos(warlord_pla, warlord_pos, True)
            cost = card.get_cost() - discounts
            other_player = self.get_other_player()
            if self.bluddflagg_relevant or other_player.bluddflagg_relevant:
                if not self.bluddflagg_used:
                    position = -2
            if position == -2:
                print("Play card to HQ")
                print(card.get_limited(), self.can_play_limited)
                if card.get_card_type() == "Support":
                    for i in range(len(self.headquarters)):
                        if self.get_ability_given_pos(-2, i) == "Orbital Relay":
                            cost = cost - 1
                cost = max(cost, 0)
                if card.get_limited():
                    if self.can_play_limited:
                        if self.spend_resources(cost):
                            if self.add_to_hq(card):
                                self.set_can_play_limited(False)
                                location_of_unit = len(self.headquarters) - 1
                                if card.get_card_type() == "Army":
                                    self.bluddflagg_used = True
                                    if damage_to_take > 0:
                                        if self.game.bigga_is_betta_active:
                                            while damage_on_play > 0:
                                                self.assign_damage_to_pos(position, location_of_unit, 1,
                                                                          by_enemy_unit=False)
                                                damage_on_play -= 1
                                        else:
                                            self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                                print("Played card to HQ")
                                return "SUCCESS", -1
                            self.add_resources(cost, refund=True)
                            return "FAIL/Unique already in play", -1
                    else:
                        return "FAIL/Limited already played", -1
                else:
                    if card.get_ability() == "Devoted Hospitaller":
                        if self.check_if_control_trait("Commissar"):
                            return "FAIL/Controls Commissar and is Devoted Hospitaller", -1
                    if self.spend_resources(cost):
                        if self.add_to_hq(card):
                            location_of_unit = len(self.headquarters) - 1
                            print("Played card to HQ")
                            if self.check_for_trait_given_pos(position, location_of_unit, "Vehicle"):
                                if self.search_for_card_everywhere("Forge Master Dominus", bloodied_relevant=True):
                                    self.game.create_reaction("Forge Master Dominus", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                                elif self.search_for_card_everywhere("Forge Master Dominus BLOODIED",
                                                                     bloodied_relevant=True):
                                    self.game.create_reaction("Forge Master Dominus BLD", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                                if self.search_card_in_hq("Dominus' Forge"):
                                    self.game.create_reaction("Dominus' Forge", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Murder of Razorwings":
                                self.game.create_reaction("Murder of Razorwings", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Mobilize the Chapter":
                                self.game.create_reaction("Mobilize the Chapter Initiation", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Shadowed Thorns Venom":
                                self.game.create_reaction("Shadowed Thorns Venom", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Munitorum Support":
                                self.game.create_reaction("Munitorum Support", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Triarch Stalkers Procession":
                                other_player.draw_card()
                                other_player.draw_card()
                            if card.check_for_a_trait("Torture"):
                                for i in range(7):
                                    for j in range(len(self.cards_in_play[i + 1])):
                                        if self.get_ability_given_pos(i, j) == "Arrogant Haemonculus":
                                            self.game.create_reaction("Arrogant Haemonculus", self.name_player,
                                                                      (int(self.number), i, j))
                            if card.get_ability() == "Bork'an Sept":
                                self.game.create_reaction("Bork'an Sept", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Novokh Dynasty":
                                self.game.create_reaction("Novokh Dynasty Burying", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "WAAAGH! Ungskar":
                                self.game.create_reaction("WAAAGH! Ungskar", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "The Broken Sigil":
                                self.game.create_reaction("The Broken Sigil", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "The Flayed Mask":
                                self.game.create_reaction("The Flayed Mask", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Hive Fleet Leviathan":
                                self.game.create_reaction("Hive Fleet Leviathan", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Dark Allegiance":
                                self.game.create_reaction("Dark Allegiance Trait", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Patron Saint":
                                self.game.create_reaction("Patron Saint", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "First Line Rhinos":
                                self.game.create_reaction("First Line Rhinos", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if not card.check_for_a_trait("Elite") and card.get_card_type() == "Army":
                                if self.search_card_in_hq("Eldritch Council", ready_relevant=True):
                                    self.game.create_reaction("Eldritch Council", self.name_player,
                                                              (int(self.number), -1, -1))
                                    self.game.eldritch_council_value = card.get_cost()
                            if card.get_card_type() == "Army":
                                self.bluddflagg_used = True
                                if card.get_faction() != "Necrons":
                                    if self.search_card_in_hq("Sautekh Dynasty", ready_relevant=True):
                                        self.game.create_reaction("Sautekh Dynasty", self.name_player,
                                                                  (int(self.number), position, location_of_unit))
                                if damage_to_take > 0:
                                    if self.game.bigga_is_betta_active:
                                        while damage_on_play > 0:
                                            self.assign_damage_to_pos(position, location_of_unit, 1,
                                                                      by_enemy_unit=False)
                                            damage_on_play -= 1
                                    else:
                                        self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                                if card.get_has_hive_mind():
                                    for i in range(len(self.headquarters)):
                                        if self.headquarters[i].get_ability() == "Hive Fleet Kraken":
                                            self.game.create_reaction("Hive Fleet Kraken", self.name_player,
                                                                      (int(self.number), -2, i))
                            return "SUCCESS", -1
                        self.add_resources(cost, refund=True)
                        return "Fail/Unique already in play", -1
                print("Insufficient resources")
                return "FAIL/Insufficient resources", -1
            else:
                if card.get_ability() == "Devoted Hospitaller":
                    if self.check_if_control_trait("Commissar"):
                        return "FAIL/Controls Commissar and is Devoted Hospitaller", -1
                cost = card.get_cost() - discounts
                if card.get_limited():
                    if self.can_play_limited and not self.enemy_holding_cell_check(card.get_name()):
                        if self.spend_resources(cost):
                            if self.add_card_to_planet(card, position, is_owner_of_card=is_owner_of_card,
                                                       triggered_card_effect=False) != -1:
                                self.set_can_play_limited(False)
                                print("Played card to planet", position)
                                location_of_unit = len(self.cards_in_play[position + 1]) - 1
                                if damage_to_take > 0:
                                    if self.game.bigga_is_betta_active:
                                        while damage_on_play > 0:
                                            self.assign_damage_to_pos(position, location_of_unit, 1,
                                                                      by_enemy_unit=False)
                                            damage_on_play -= 1
                                    else:
                                        self.assign_damage_to_pos(position, location_of_unit, damage_to_take,
                                                                  by_enemy_unit=False)
                                return "SUCCESS", location_of_unit
                            self.add_resources(cost, refund=True)
                            return "FAIL/Unique already in play", -1
                    else:
                        return "FAIL/Limited already played", -1
                elif not self.enemy_holding_cell_check(card.get_name()):
                    if self.spend_resources(cost):
                        if self.add_card_to_planet(card, position, is_owner_of_card=is_owner_of_card,
                                                   triggered_card_effect=False) != -1:
                            location_of_unit = len(self.cards_in_play[position + 1]) - 1
                            if damage_to_take > 0:
                                if self.game.bigga_is_betta_active:
                                    while damage_on_play > 0:
                                        self.assign_damage_to_pos(position, location_of_unit, 1,
                                                                  by_enemy_unit=False)
                                        damage_on_play -= 1
                                else:
                                    self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                            other_player = self.game.p1
                            if other_player.name_player == self.name_player:
                                other_player = self.game.p2
                            if card.get_ability() == "Murder of Razorwings":
                                self.game.create_reaction("Murder of Razorwings", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if self.check_for_trait_given_pos(position, location_of_unit, "Vehicle"):
                                if self.search_for_card_everywhere("Forge Master Dominus", bloodied_relevant=True):
                                    self.game.create_reaction("Forge Master Dominus", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                                elif self.search_for_card_everywhere("Forge Master Dominus BLOODIED",
                                                                     bloodied_relevant=True):
                                    self.game.create_reaction("Forge Master Dominus BLD", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                                if self.search_card_in_hq("Dominus' Forge"):
                                    self.game.create_reaction("Dominus' Forge", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Patron Saint":
                                self.game.create_reaction("Patron Saint", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Imperial Fists Siege Force":
                                self.game.create_reaction("Imperial Fists Siege Force", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Hydrae Stalker":
                                self.game.create_reaction("Hydrae Stalker", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Imperial Fists Devastators":
                                if self.game.get_blue_icon(position):
                                    self.game.create_reaction("Imperial Fists Devastators", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if card.get_faction() != "Necrons":
                                if self.search_card_in_hq("Sautekh Dynasty", ready_relevant=True):
                                    self.game.create_reaction("Sautekh Dynasty", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if card.get_ability() == "First Line Rhinos":
                                self.game.create_reaction("First Line Rhinos", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Triarch Stalkers Procession":
                                other_player.draw_card()
                                other_player.draw_card()
                            if card.get_ability() == "Scheming Warlock":
                                self.game.create_reaction("Scheming Warlock", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Brotherhood Justicar":
                                self.game.create_reaction("Brotherhood Justicar", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Luring Troupe":
                                self.game.create_reaction("Luring Troupe", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "The Webway Witch":
                                self.game.create_reaction("The Webway Witch", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Scything Hormagaunts"\
                                    and not self.game.infested_planets[position]:
                                self.game.create_reaction("Scything Hormagaunts", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Emergent Cultists":
                                self.game.create_reaction("Emergent Cultists", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Klaivex Warleader":
                                if self.game.phase == "COMBAT":
                                    self.game.create_reaction("Klaivex Warleader", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Aun'ui Prelate":
                                self.game.create_reaction("Aun'ui Prelate", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Doom Scythe Invader":
                                self.game.create_reaction("Doom Scythe Invader", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Genestealer Brood":
                                self.game.create_reaction("Genestealer Brood", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Kith's Khymeramasters":
                                self.game.create_reaction("Kith's Khymeramasters", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Space Wolves Predator":
                                self.game.create_reaction("Space Wolves Predator", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Kommando Sneakaz":
                                self.game.create_reaction("Kommando Sneakaz", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Prophetic Farseer":
                                self.game.create_reaction("Prophetic Farseer", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Prototype Crisis Suit":
                                self.game.create_reaction("Prototype Crisis Suit", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Invasive Genestealers":
                                self.game.create_reaction("Invasive Genestealers", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Shadowed Thorns Venom":
                                self.game.create_reaction("Shadowed Thorns Venom", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Kroot Hunter":
                                if self.game.get_red_icon(position):
                                    self.game.create_reaction("Kroot Hunter", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if card.check_for_a_trait("Scout", self.etekh_trait) \
                                    and card.get_faction() != "Necrons":
                                for i in range(7):
                                    for j in range(len(self.cards_in_play[i + 1])):
                                        if self.cards_in_play[i + 1][j].get_ability() == "Tomb Blade Squadron":
                                            if "Tomb Blade Squadron" not in self.game.reactions_needing_resolving:
                                                self.game.create_reaction("Tomb Blade Squadron", self.name_player,
                                                                          (int(self.number), -1, -1))
                                for i in range(len(self.headquarters)):
                                    if self.headquarters[i].get_ability() == "Tomb Blade Squadron":
                                        if "Tomb Blade Squadron" not in self.game.reactions_needing_resolving:
                                            self.game.create_reaction("Tomb Blade Squadron", self.name_player,
                                                                      (int(self.number), -1, -1))
                            if card.check_for_a_trait("Elite"):
                                for i in range(len(self.headquarters)):
                                    if self.get_ability_given_pos(-2, i) == "Turbulent Rift":
                                        self.game.create_reaction("Turbulent Rift", self.name_player,
                                                                  (int(self.number), position, location_of_unit))
                                    if self.get_ability_given_pos(-2, i) == "Loamy Broodhive":
                                        if self.get_ready_given_pos(-2, i):
                                            self.game.create_reaction("Loamy Broodhive", self.name_player,
                                                                      (int(self.number), position, location_of_unit))
                            if not card.check_for_a_trait("Elite") and card.get_card_type() == "Army":
                                if self.search_card_in_hq("Eldritch Council", ready_relevant=True):
                                    self.game.create_reaction("Eldritch Council", self.name_player,
                                                              (int(self.number), -1, -1))
                                    self.game.eldritch_council_value = card.get_cost()
                            if card.check_for_a_trait("Daemon", self.etekh_trait):
                                for i in range(len(self.headquarters)):
                                    if self.get_ability_given_pos(-2, i) == "Tower of Worship":
                                        self.game.create_reaction("Tower of Worship", self.name_player,
                                                                  (int(self.number), -2, i))
                            if card.check_for_a_trait("Nurgle", self.etekh_trait):
                                for i in range(len(self.cards_in_play[position + 1])):
                                    if self.get_ability_given_pos(position, i) == "Death Guard Preachers":
                                        if not self.get_once_per_phase_used_given_pos(position, i):
                                            if not self.check_if_already_have_reaction_of_position(
                                                    "Death Guard Preachers", position, i):
                                                self.game.create_reaction("Death Guard Preachers", self.name_player,
                                                                          (int(self.number), position, i))
                            if card.get_faction() != "Necrons":
                                if self.count_units_of_faction(card.get_faction()) == 1:
                                    for i in range(len(self.headquarters)):
                                        if self.headquarters[i].get_ability() == "Sautekh Complex":
                                            self.game.create_reaction("Sautekh Complex", self.name_player,
                                                                      (int(self.number), -2, i))
                            if card.get_faction() != "Tau":
                                for i in range(len(self.cards_in_play[position + 1])):
                                    if self.get_ability_given_pos(position, i) == "Exploratory Drone":
                                        self.game.create_reaction("Exploratory Drone", self.name_player,
                                                                  (int(self.number), position, i))
                                other_player = self.game.p1
                                if other_player.name_player == self.name_player:
                                    other_player = self.game.p2
                                for i in range(len(other_player.cards_in_play[position + 1])):
                                    if other_player.get_ability_given_pos(position, i) == "Exploratory Drone":
                                        self.game.create_reaction("Exploratory Drone", other_player.name_player,
                                                                  (int(other_player.number), position, i))
                            other_player = self.get_other_player()
                            syren_ok = False
                            for i in range(len(other_player.cards_in_play[position + 1])):
                                if other_player.get_ability_given_pos(position, i) == "Syren Zythlex":
                                    if self.game.apoka:
                                        if not other_player.get_once_per_phase_used_given_pos(position, i):
                                            syren_ok = True
                                            other_player.set_once_per_phase_used_given_pos(position, i, True)
                                    else:
                                        syren_ok = True
                            if card.get_has_hive_mind():
                                for i in range(len(self.headquarters)):
                                    if self.headquarters[i].get_ability() == "Hive Fleet Kraken":
                                        self.game.create_reaction("Hive Fleet Kraken", self.name_player,
                                                                  (int(self.number), -2, i))
                            for i in range(len(other_player.attachments_at_planet[position])):
                                if other_player.attachments_at_planet[position][i].get_ability() == "Vanguard Pack":
                                    self.game.create_reaction("Vanguard Pack", other_player.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if self.game.deploy_exhausted:
                                self.exhaust_given_pos(position, location_of_unit)
                                self.game.deploy_exhausted = False
                            elif syren_ok:
                                name = self.name_player
                                if name == self.game.name_1:
                                    name = self.game.name_2
                                else:
                                    name = self.game.name_1
                                self.game.create_reaction("Syren Zythlex", name,
                                                          (int(self.number), position, location_of_unit))
                            return "SUCCESS", location_of_unit
                        self.add_resources(cost, refund=True)
                        return "FAIL/Unique already in play", -1
                print("Insufficient resources")
                return "FAIL/Insufficient resources", -1
        return "FAIL/Invalid card", -1

    def count_units_of_faction(self, faction):
        count = 0
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_faction() == faction and self.headquarters[i].get_is_unit():
                count += 1
        for planet in range(7):
            for i in range(len(self.cards_in_play[planet + 1])):
                if self.cards_in_play[planet + 1][i].get_faction() == faction and \
                        self.cards_in_play[planet + 1][i].get_is_unit():
                    count += 1
        return count

    def reset_resolving_attacks_everywhere(self):
        i = 0
        while i < len(self.headquarters):
            self.headquarters[i].resolving_attack = False
            if self.headquarters[i].get_ability() == "Tomb Blade Diversionist":
                self.headquarters[i].misc_ability_used = False
            i += 1
        for i in range(7):
            j = 0
            while j < len(self.cards_in_play[i + 1]):
                self.cards_in_play[i + 1][j].resolving_attack = False
                if self.cards_in_play[i + 1][j].get_ability() == "Tomb Blade Diversionist":
                    self.cards_in_play[i + 1][j].misc_ability_used = False
                j = j + 1

    def ethereal_movement_resolution(self):
        i = 0
        while i < len(self.headquarters):
            self.headquarters[i].ethereal_movement_active = False
            i += 1
        for i in range(7):
            j = 0
            while j < len(self.cards_in_play[i + 1]):
                if self.cards_in_play[i + 1][j].ethereal_movement_active:
                    self.cards_in_play[i + 1][j].ethereal_movement_active = False
                    if self.search_card_in_hq("Slumbering Gardens", ready_relevant=True):
                        self.game.create_interrupt("Slumbering Gardens Special", self.name_player,
                                                   (int(self.number), i, j))
                    else:
                        self.move_unit_at_planet_to_hq(i, j)
                        j = j - 1
                j = j + 1

    def reset_card_name_misc_ability(self, card_name):
        if card_name == "Follower of Gork":
            for i in range(len(self.headquarters)):
                self.headquarters[i].follower_of_gork_available = False
            for i in range(7):
                for j in range(len(self.cards_in_play[i + 1])):
                    self.cards_in_play[i + 1][j].follower_of_gork_available = False
            return None
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == card_name:
                self.headquarters[i].misc_ability_used = False
            for j in range(len(self.headquarters[i].get_attachments())):
                if self.headquarters[i].get_attachments()[j].get_ability() == card_name:
                    self.headquarters[i].get_attachments()[j].misc_ability_used = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == card_name:
                    self.cards_in_play[i + 1][j].misc_ability_used = False
                for k in range(len(self.cards_in_play[i + 1][j].get_attachments())):
                    if self.cards_in_play[i + 1][j].get_attachments()[k].get_ability() == card_name:
                        self.cards_in_play[i + 1][j].get_attachments()[k].misc_ability_used = False

    def return_attachment_to_hand(self, planet_pos, unit_pos, attachment_pos):
        other_player = self.get_other_player()
        if planet_pos == -2:
            card_name = self.headquarters[unit_pos].get_attachments()[attachment_pos].get_name()
            name_owner = self.headquarters[unit_pos].get_attachments()[attachment_pos].name_owner
            if name_owner == self.name_player:
                self.cards.append(card_name)
            else:
                other_player.cards.append(card_name)
            del self.headquarters[unit_pos].get_attachments()[attachment_pos]
            return None
        card_name = self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_name()
        name_owner = self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].name_owner
        if name_owner == self.name_player:
            self.cards.append(card_name)
        else:
            other_player.cards.append(card_name)
        del self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
        return None

    def return_attachments_on_card_to_hand(self, planet_pos, unit_pos):
        if planet_pos == -2:
            while len(self.headquarters[unit_pos].get_attachments()):
                self.return_attachment_to_hand(planet_pos, unit_pos, 0)
            return None
        while len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()):
            self.return_attachment_to_hand(planet_pos, unit_pos, 0)
        return None

    def return_card_to_hand(self, planet_pos, unit_pos, return_attachments=False):
        if planet_pos == -2:
            if self.headquarters[unit_pos].name_owner == self.name_player:
                self.cards.append(self.headquarters[unit_pos].get_name())
            else:
                ret_player = self.game.p1
                if self.game.name_1 == self.name_player:
                    ret_player = self.game.p2
                ret_player.cards.append(self.headquarters[unit_pos].get_name())
            if not return_attachments:
                self.discard_attachments_from_card(planet_pos, unit_pos)
            else:
                self.return_attachments_on_card_to_hand(planet_pos, unit_pos)
            self.remove_card_from_hq(unit_pos)
            return None
        if self.cards_in_play[planet_pos + 1][unit_pos].name_owner == self.name_player:
            self.cards.append(self.cards_in_play[planet_pos + 1][unit_pos].get_name())
        else:
            ret_player = self.game.p1
            if self.game.name_1 == self.name_player:
                ret_player = self.game.p2
            ret_player.cards.append(self.cards_in_play[planet_pos + 1][unit_pos].get_name())
        if not return_attachments:
            self.discard_attachments_from_card(planet_pos, unit_pos)
        else:
            self.return_attachments_on_card_to_hand(planet_pos, unit_pos)
        self.remove_card_from_play(planet_pos, unit_pos)
        return None

    def discard_card_at_random(self):
        if self.cards:
            pos = random.randint(0, len(self.cards) - 1)
            self.discard_card_from_hand(pos)

    def reset_movement_trackers(self):
        self.reset_defense_batteries()
        for i in range(len(self.headquarters)):
            self.headquarters[i].card_moved_recently = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].card_moved_recently = False

    def clear_aiming_reticle_actioned_card(self):
        pla, pos = self.game.position_of_actioned_card
        self.reset_aiming_reticle_in_play(pla, pos)

    def reset_defense_batteries(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].valid_defense_battery_target = False
        for i in range(7):
            for j in range(len(self.attachments_at_planet[i])):
                self.attachments_at_planet[i][j].defense_battery_activated = False
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].valid_defense_battery_target = False

    def move_unit_to_planet(self, origin_planet, origin_position, destination, force=False, card_effect=True):
        if origin_planet == -2:
            headquarters_list = self.headquarters
            other_player = self.get_other_player()
            if card_effect:
                if self.game.imperial_blockades_active[destination] > 0:
                    resources_to_spend = self.game.imperial_blockades_active[destination]
                    if not self.spend_resources(resources_to_spend):
                        self.game.queued_message = "Important Info: Imperial Blockade prevented the move."
                        return False
                    else:
                        self.game.queued_message = "Important Info: " + str(resources_to_spend) + \
                                                   " resources were spent due to Imperial Blockade."
            self.headquarters[origin_position].card_moved_recently = True
            if self.headquarters[origin_position].get_card_type() == "Army":
                if self.defense_battery_check(destination):
                    self.headquarters[origin_position].valid_defense_battery_target = True
            if self.headquarters[origin_position].get_card_type() == "Army":
                for i in range(len(other_player.cards_in_play[destination + 1])):
                    if other_player.resources > 0:
                        if other_player.get_unique_given_pos(destination, i):
                            if not other_player.check_if_already_have_reaction("The Inevitable Decay"):
                                if "The Inevitable Decay" in other_player.cards:
                                    self.game.create_reaction("The Inevitable Decay", other_player.name_player,
                                                              (int(self.number), -1, -1))
                                elif "The Inevitable Decay" in other_player.cards_removed_from_game:
                                    warlord_pla, warlord_pos = other_player.get_location_of_warlord()
                                    vael_relevant = False
                                    if other_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                                            other_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                                        vael_relevant = True
                                    elif other_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                                            and not other_player.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                                        vael_relevant = True
                                    if vael_relevant:
                                        self.game.create_reaction("The Inevitable Decay", other_player.name_player,
                                                                  (int(self.number), -1, -1))
            for i in range(len(other_player.cards_in_play[destination + 1])):
                if other_player.get_ability_given_pos(destination, i) == "Hydra Flak Tank":
                    if not other_player.get_once_per_phase_used_given_pos(destination, i):
                        already_reacted = False
                        self.headquarters[origin_position].valid_defense_battery_target = True
                        for j in range(len(self.game.reactions_needing_resolving)):
                            if self.game.reactions_needing_resolving[j] == "Hydra Flak Tank":
                                if self.game.positions_of_unit_triggering_reaction[j] == (int(other_player.number),
                                                                                          destination, i):
                                    if self.game.player_who_resolves_reaction[j] == other_player.name_player:
                                        already_reacted = True
                        if not already_reacted:
                            self.game.create_reaction("Hydra Flak Tank", other_player.name_player,
                                                      (int(other_player.number), destination, i))
            if destination != 0:
                for i in range(len(other_player.cards_in_play[destination])):
                    if other_player.get_ability_given_pos(destination - 1, i) == "Mars Pattern Hellhound":
                        if not other_player.check_if_already_have_reaction_of_position("Mars Pattern Hellhound",
                                                                                       destination - 1, i):
                            self.game.create_reaction("Mars Pattern Hellhound", other_player.name_player,
                                                      (int(other_player.number), destination - 1, i))
            if destination != 6:
                for i in range(len(other_player.cards_in_play[destination + 2])):
                    if other_player.get_ability_given_pos(destination + 1, i) == "Mars Pattern Hellhound":
                        if not other_player.check_if_already_have_reaction_of_position("Mars Pattern Hellhound",
                                                                                       destination + 1, i):
                            self.game.create_reaction("Mars Pattern Hellhound", other_player.name_player,
                                                      (int(other_player.number), destination + 1, i))
            self.cards_in_play[destination + 1].append(copy.deepcopy(headquarters_list[origin_position]))
            new_pos = len(self.cards_in_play[destination + 1]) - 1
            self.cards_in_play[destination + 1][new_pos].valid_kugath_nurgling_target = True
            self.game.just_moved_units = True
            if self.game.last_planet_checked_for_battle == destination:
                if other_player.search_hand_for_card("Wrathful Retribution"):
                    if not other_player.check_if_already_have_reaction("Wrathful Retribution"):
                        self.game.create_reaction("Wrathful Retribution", other_player.name_player,
                                                  (int(other_player.number), -1, -1))
                        cost_card_wrath = self.get_cost_given_pos(destination, new_pos)
                        if other_player.wrathful_retribution_value < cost_card_wrath:
                            other_player.wrathful_retribution_value = cost_card_wrath
            if self.check_for_trait_given_pos(destination, new_pos, "Vostroya"):
                if self.search_card_in_hq("Convent Prioris Advisor"):
                    self.game.create_reaction("Convent Prioris Advisor", self.name_player,
                                              (int(self.number), destination, new_pos))
            if self.get_ability_given_pos(destination, new_pos) == "Sacred Rose Immolator":
                if not self.get_once_per_round_used_given_pos(destination, new_pos):
                    self.game.create_reaction("Sacred Rose Immolator", self.name_player,
                                              (int(self.number), destination, new_pos))
                elif self.get_once_per_round_used_given_pos(destination, new_pos) < 2:
                    self.game.create_reaction("Sacred Rose Immolator", self.name_player,
                                              (int(self.number), destination, new_pos))
            if self.get_ability_given_pos(destination, new_pos) == "Quartermasters":
                if self.get_damage_given_pos(destination, new_pos) > 0:
                    self.game.create_reaction("Quartermasters", self.name_player,
                                              (int(self.number), destination, new_pos))
            if self.cards_in_play[destination + 1][new_pos].get_faction() == "Eldar":
                if self.search_card_in_hq("Alaitoc Shrine", ready_relevant=True):
                    alaitoc_shrine_already_present = False
                    for i in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[i] == "Alaitoc Shrine":
                            alaitoc_shrine_already_present = True
                    if not alaitoc_shrine_already_present:
                        self.game.create_reaction("Alaitoc Shrine", self.name_player,
                                                  (int(self.number), -1, -1))
                        self.game.allowed_units_alaitoc_shrine.append([int(self.number), destination, new_pos])
            for i in range(len(self.cards_in_play[destination + 1])):
                if self.game.phase != "COMMAND":
                    if self.get_ability_given_pos(destination, i) == "Acquisition Phalanx":
                        self.game.create_reaction("Acquisition Phalanx", self.name_player,
                                                  (int(self.number), destination, i))
            if self.game.phase == "COMBAT":
                if self.search_attachments_at_pos(destination, new_pos, "Third Eye of Trazyn", ready_relevant=True):
                    self.game.create_reaction("Third Eye of Trazyn", self.name_player,
                                              (int(self.number), destination, new_pos))
                if other_player.search_card_at_planet(destination, "Eloquent Confessor"):
                    if self.game.phase == "COMBAT":
                        self.game.create_reaction("Eloquent Confessor", other_player.name_player,
                                                  (int(other_player.number), destination, new_pos))
            self.remove_card_from_hq(origin_position)
            return True
        else:
            other_player = self.get_other_player()
            if self.cards_in_play[origin_planet + 1][origin_position].get_card_type() == "Army":
                if other_player.search_card_at_planet(origin_planet, "Strangleweb Termagant", ready_relevant=True) \
                        and not force:
                    self.game.choices_available = ["No Interrupt", "Strangleweb Termagant"]
                    self.game.name_player_making_choices = other_player.name_player
                    self.game.choice_context = "Interrupt Enemy Movement Effect?"
                    self.game.resolving_search_box = True
                    self.game.queued_moves.append((int(self.number), origin_planet,
                                                   origin_position, destination))
                    return False
            if card_effect:
                if self.game.imperial_blockades_active[destination] > 0:
                    resources_to_spend = self.game.imperial_blockades_active[destination]
                    if not self.spend_resources(resources_to_spend):
                        self.game.queued_message = "Important Info: Imperial Blockade prevented the move."
                        return False
                    else:
                        self.game.queued_message = "Important Info: " + str(resources_to_spend) + \
                                                   " resources were spent due to Imperial Blockade."
            self.cards_in_play[origin_planet + 1][origin_position].card_moved_recently = True
            if self.cards_in_play[origin_planet + 1][origin_position].get_card_type() == "Army":
                if self.defense_battery_check(origin_planet) or self.defense_battery_check(destination):
                    self.cards_in_play[origin_planet + 1][origin_position].valid_defense_battery_target = True
            for i in range(len(other_player.cards_in_play[destination + 1])):
                if other_player.get_ability_given_pos(destination, i) == "Hydra Flak Tank":
                    if not other_player.get_once_per_phase_used_given_pos(destination, i):
                        already_reacted = False
                        self.cards_in_play[origin_planet + 1][origin_position].valid_defense_battery_target = True
                        for j in range(len(self.game.reactions_needing_resolving)):
                            if self.game.reactions_needing_resolving[j] == "Hydra Flak Tank":
                                if self.game.positions_of_unit_triggering_reaction[j] == (int(other_player.number),
                                                                                          destination, i):
                                    if self.game.player_who_resolves_reaction[j] == other_player.name_player:
                                        already_reacted = True
                        if not already_reacted:
                            self.game.create_reaction("Hydra Flak Tank", other_player.name_player,
                                                      (int(other_player.number), destination, i))
            if destination != 0:
                for i in range(len(other_player.cards_in_play[destination])):
                    if other_player.get_ability_given_pos(destination - 1, i) == "Mars Pattern Hellhound":
                        if not other_player.check_if_already_have_reaction_of_position("Mars Pattern Hellhound",
                                                                                       destination - 1, i):
                            self.game.create_reaction("Mars Pattern Hellhound", other_player.name_player,
                                                      (int(other_player.number), destination - 1, i))
            if destination != 6:
                for i in range(len(other_player.cards_in_play[destination + 2])):
                    if other_player.get_ability_given_pos(destination + 1, i) == "Mars Pattern Hellhound":
                        if not other_player.check_if_already_have_reaction_of_position("Mars Pattern Hellhound",
                                                                                       destination + 1, i):
                            self.game.create_reaction("Mars Pattern Hellhound", other_player.name_player,
                                                      (int(other_player.number), destination + 1, i))
            for i in range(len(other_player.cards_in_play[origin_planet + 1])):
                if other_player.get_ability_given_pos(origin_planet, i) == "Hydra Flak Tank":
                    if not other_player.get_once_per_phase_used_given_pos(origin_planet, i):
                        already_reacted = False
                        self.headquarters[origin_position].valid_defense_battery_target = True
                        for j in range(len(self.game.reactions_needing_resolving)):
                            if self.game.reactions_needing_resolving[j] == "Hydra Flak Tank":
                                if self.game.positions_of_unit_triggering_reaction[j] == (int(other_player.number),
                                                                                          origin_planet, i):
                                    if self.game.player_who_resolves_reaction[j] == other_player.name_player:
                                        already_reacted = True
                        if not already_reacted:
                            self.game.create_reaction("Hydra Flak Tank", other_player.name_player,
                                                      (int(other_player.number), origin_planet, i))
            if self.cards_in_play[origin_planet + 1][origin_position].get_card_type() != "Warlord":
                for i in range(len(other_player.cards_in_play[destination + 1])):
                    for j in range(len(other_player.cards_in_play[destination + 1][i].attachments)):
                        if other_player.cards_in_play[destination + 1][i].attachments[j].\
                                get_ability() == "Sanctified Bolter":
                            self.game.create_reaction("Sanctified Bolter", other_player.name_player,
                                                      (int(other_player.number), destination, i))
            self.cards_in_play[destination + 1].append(copy.deepcopy(self.cards_in_play[origin_planet + 1]
                                                                     [origin_position]))
            new_pos = len(self.cards_in_play[destination + 1]) - 1
            last_element_index = new_pos
            self.cards_in_play[destination + 1][new_pos].valid_kugath_nurgling_target = True
            self.game.just_moved_units = True
            self.remove_card_from_play(origin_planet, origin_position)
            for i in range(len(self.headquarters)):
                if i != last_element_index:
                    if self.get_ability_given_pos(-2, i) == "Frontline Counsellor":
                        if not self.get_once_per_phase_used_given_pos(-2, i):
                            if not self.check_if_already_have_interrupt_of_position("Frontline Counsellor",
                                                                                    self.name_player,
                                                                                    (int(self.number), -2, i)):
                                self.game.create_interrupt("Frontline Counsellor", self.name_player,
                                                           (int(self.number), -2, i), extra_info=origin_planet)
            for i in range(7):
                if i != origin_planet:
                    for j in range(len(self.cards_in_play[i + 1])):
                        if j != last_element_index or i != destination:
                            if self.get_ability_given_pos(i, j) == "Frontline Counsellor":
                                if not self.get_once_per_phase_used_given_pos(i, j):
                                    if not self.check_if_already_have_interrupt_of_position("Frontline Counsellor",
                                                                                            self.name_player,
                                                                                            (int(self.number), i, j)):
                                        self.game.create_interrupt("Frontline Counsellor", self.name_player,
                                                                   (int(self.number), i, j), extra_info=origin_planet)
            if self.game.last_planet_checked_for_battle == destination:
                if other_player.search_hand_for_card("Wrathful Retribution"):
                    if not other_player.check_if_already_have_reaction("Wrathful Retribution"):
                        self.game.create_reaction("Wrathful Retribution", other_player.name_player,
                                                  (int(other_player.number), -1, -1))
                        cost_card_wrath = self.get_cost_given_pos(destination, new_pos)
                        if other_player.wrathful_retribution_value < cost_card_wrath:
                            other_player.wrathful_retribution_value = cost_card_wrath
            if other_player.search_hand_for_card("Calibration Error"):
                if self.get_card_type_given_pos(destination, new_pos) != "Warlord":
                    if self.get_ready_given_pos(destination, new_pos):
                        cost = 2
                        if other_player.urien_relevant:
                            cost += 1
                        if other_player.resources >= cost:
                            if not other_player.check_if_already_have_reaction("Calibration Error"):
                                self.game.create_reaction("Calibration Error", other_player.name_player,
                                                          (int(other_player.number), destination, new_pos))
            if self.search_hand_for_card("Cry of the Wind"):
                already_cry = False
                self.cards_in_play[destination + 1][new_pos].valid_target_ashen_banner = True
                for i in range(len(self.game.reactions_needing_resolving)):
                    if self.game.reactions_needing_resolving[i] == "Cry of the Wind":
                        if self.game.player_who_resolves_reaction[i] == self.name_player:
                            already_cry = True
                if not already_cry:
                    self.game.create_reaction("Cry of the Wind", self.name_player, (int(self.number), -1, -1))
            for i in range(len(self.cards_in_play[destination + 1])):
                if self.get_ability_given_pos(destination, i) == "Acquisition Phalanx":
                    self.game.create_reaction("Acquisition Phalanx", self.name_player,
                                              (int(self.number), destination, i))
            if self.game.phase == "COMBAT":
                if self.search_card_in_hq("Deathly Web Shrine", ready_relevant=True):
                    self.game.create_reaction("Deathly Web Shrine", self.name_player,
                                              (int(self.number), destination, -1))
                if self.search_attachments_at_pos(destination, new_pos, "Third Eye of Trazyn"):
                    self.game.create_reaction("Third Eye of Trazyn", self.name_player,
                                              (int(self.number), destination, new_pos))
                if other_player.search_card_at_planet(destination, "Eloquent Confessor"):
                    if self.game.phase == "COMBAT":
                        self.game.create_reaction("Eloquent Confessor", other_player.name_player,
                                                  (int(other_player.number), destination, new_pos))
            self.cards_in_play[destination + 1][new_pos].valid_target_ashen_banner = True
            if self.search_card_in_hq("Banner of the Ashen Sky", ready_relevant=True):
                already_banner = False
                for i in range(len(self.game.reactions_needing_resolving)):
                    if self.game.reactions_needing_resolving[i] == "Banner of the Ashen Sky":
                        if self.game.player_who_resolves_reaction[i] == self.name_player:
                            already_banner = True
                if not already_banner:
                    self.game.create_reaction("Banner of the Ashen Sky", self.name_player,
                                              (int(self.number), -1, -1))
            if self.cards_in_play[destination + 1][new_pos].get_ability() == "Piranha Hunter":
                self.game.create_reaction("Piranha Hunter", self.name_player, (int(self.number), destination, new_pos))
            if self.get_ability_given_pos(destination, new_pos) == "Sacred Rose Immolator":
                if not self.get_once_per_round_used_given_pos(destination, new_pos):
                    self.game.create_reaction("Sacred Rose Immolator", self.name_player,
                                              (int(self.number), destination, new_pos))
                elif self.get_once_per_round_used_given_pos(destination, new_pos) < 2:
                    self.game.create_reaction("Sacred Rose Immolator", self.name_player,
                                              (int(self.number), destination, new_pos))
            for i in range(len(self.cards_in_play[origin_planet + 1])):
                if self.get_ability_given_pos(origin_planet, i) == "Wildrider Vyper":
                    self.game.create_reaction("Wildrider Vyper", self.name_player,
                                              (int(self.number), origin_planet, i))
            other_player = self.get_other_player()
            for i in range(len(other_player.cards_in_play[origin_planet + 1])):
                if other_player.get_ability_given_pos(origin_planet, i) == "Wildrider Vyper":
                    self.game.create_reaction("Wildrider Vyper", other_player.name_player,
                                              (int(other_player.number), origin_planet, i))
            if self.get_card_type_given_pos(destination, new_pos) == "Army":
                for i in range(len(other_player.cards_in_play[destination + 1])):
                    if other_player.resources > 0:
                        if other_player.get_unique_given_pos(destination, i):
                            if not other_player.check_if_already_have_reaction("The Inevitable Decay"):
                                if "The Inevitable Decay" in other_player.cards:
                                    self.game.create_reaction("The Inevitable Decay", other_player.name_player,
                                                              (int(self.number), -1, -1))
                                elif "The Inevitable Decay" in other_player.cards_removed_from_game:
                                    warlord_pla, warlord_pos = other_player.get_location_of_warlord()
                                    vael_relevant = False
                                    if other_player.get_ability_given_pos(warlord_pla,
                                                                          warlord_pos) == "Vael the Gifted" and not \
                                            other_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                                        vael_relevant = True
                                    elif other_player.get_ability_given_pos(warlord_pla,
                                                                            warlord_pos) == "Vael the Gifted BLOODIED" \
                                            and not other_player.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                                        vael_relevant = True
                                    if vael_relevant:
                                        self.game.create_reaction("The Inevitable Decay", other_player.name_player,
                                                                  (int(self.number), -1, -1))
        if self.cards_in_play[destination + 1][new_pos].get_ability() == "Venomous Fiend":
            self.game.create_reaction("Venomous Fiend", self.name_player, (int(self.number), destination, new_pos))
        return True

    def commit_warlord_to_planet_from_planet(self, origin_planet, dest_planet):
        self.warlord_commit_location = dest_planet
        if origin_planet == -2:
            self.commit_warlord_to_planet(dest_planet, only_warlord=True)
        i = 0
        warlord_committed = False
        while i < len(self.cards_in_play[origin_planet + 1]) and not warlord_committed:
            if self.cards_in_play[origin_planet + 1][i].get_card_type() == "Warlord":
                warlord_committed = True
                summon_khymera = False
                if self.cards_in_play[origin_planet + 1][i].get_ability() == "Packmaster Kith":
                    summon_khymera = True
                if self.cards_in_play[origin_planet + 1][i].get_ability(bloodied_relevant=True) == "Eldorath Starbane":
                    self.game.create_reaction("Eldorath Starbane", self.name_player,
                                              [int(self.number), dest_planet, -1])
                if self.cards_in_play[origin_planet + 1][i].get_ability(bloodied_relevant=True) == "Ragnar Blackmane":
                    if not self.check_if_already_have_reaction("Ragnar Blackmane"):
                        self.game.create_reaction("Ragnar Blackmane", self.name_player,
                                                  [int(self.number), dest_planet, -1])
                self.move_unit_to_planet(origin_planet, i, dest_planet)
                for j in range(len(self.headquarters)):
                    if self.get_ability_given_pos(-2, j) == "Heralding Cherubim":
                        self.game.create_reaction("Heralding Cherubim", self.name_player,
                                                  (int(self.number), -2, j))
                for j in range(7):
                    for k in range(len(self.cards_in_play[j + 1])):
                        if self.get_ability_given_pos(j, k) == "Heralding Cherubim":
                            self.game.create_reaction("Heralding Cherubim", self.name_player,
                                                      (int(self.number), j, k))
                    if j != dest_planet:
                        for k in range(len(self.cards_in_play[j + 1])):
                            if self.get_ability_given_pos(j, k) == "Blackmane Sentinel":
                                self.game.create_reaction("Blackmane Sentinel", self.name_player,
                                                          (int(self.number), j, k))
                if summon_khymera:
                    self.summon_token_at_planet("Khymera", dest_planet)
                other_player = self.get_other_player()
                self.resolve_additional_warlord_after_commit_effects(dest_planet)
                other_player.resolve_enemy_warlord_committed_to_planet(dest_planet)
            i += 1

    def move_synapse_to_hq(self):
        for i in range(7):
            j = 0
            hard_stop = 100
            while j < len(self.cards_in_play[i + 1]) and hard_stop > 0:
                if self.cards_in_play[i + 1][j].get_card_type() == "Synapse":
                    self.move_unit_at_planet_to_hq(i, j)
                    j = j - 1
                j = j + 1
                hard_stop = hard_stop - 1
        return None

    def check_yvraine_battle(self, planet):
        for i in range(len(self.cards_in_play[planet + 1])):
            if self.cards_in_play[planet + 1][i].yvraine_active:
                return True
        return False
    def check_savage_warrior_prime_present(self, planet):
        for i in range(len(self.cards_in_play[planet + 1])):
            if self.cards_in_play[planet + 1][i].get_ability() == "Savage Warrior Prime":
                return True
        return False

    def ranged_skirmish_ends_triggers(self, planet_pos):
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.get_ability_given_pos(planet_pos, i) == "Sniper Drone Team":
                if not self.get_ready_given_pos(planet_pos, i):
                    self.game.create_reaction("Sniper Drone Team", self.name_player,
                                              (int(self.number), planet_pos, i))
        if planet_pos != 0:
            for i in range(len(self.cards_in_play[planet_pos])):
                if self.get_ability_given_pos(planet_pos - 1, i) == "Siege Regiment Manticore":
                    if self.get_ready_given_pos(planet_pos - 1, i):
                        self.game.create_reaction("Siege Regiment Manticore", self.name_player,
                                                  (int(self.number), planet_pos - 1, i))
        if planet_pos != 6:
            for i in range(len(self.cards_in_play[planet_pos + 2])):
                if self.get_ability_given_pos(planet_pos + 1, i) == "Siege Regiment Manticore":
                    if self.get_ready_given_pos(planet_pos + 1, i):
                        self.game.create_reaction("Siege Regiment Manticore", self.name_player,
                                                  (int(self.number), planet_pos + 1, i))

    def phoenix_attack_fighter_triggers(self, planets_list):
        for planet_pos in planets_list:
            for i in range(len(self.cards_in_play[planet_pos + 1])):
                if self.get_ability_given_pos(planet_pos, i) == "Phoenix Attack Fighter":
                    self.game.create_reaction("Phoenix Attack Fighter", self.name_player,
                                              (int(self.number), planet_pos, i))

    def create_warlord_committed_to_planet_reactions(self, planets_list):
        for i in range(len(planets_list)):
            planet_pos = planets_list[i]
            for j in range(len(self.cards_in_play[planet_pos + 1])):
                if self.get_ability_given_pos(planet_pos, j) == "Tenacious Novice Squad":
                    self.game.create_reaction("Tenacious Novice Squad", self.name_player,
                                              (int(self.number), planet_pos, j))
                if self.get_ability_given_pos(planet_pos, j, bloodied_relevant=True) == "Ragnar Blackmane":
                    if not self.check_if_already_have_reaction("Ragnar Blackmane"):
                        self.game.create_reaction("Ragnar Blackmane", self.name_player,
                                                  (int(self.number), planet_pos, j))
                if self.get_ability_given_pos(planet_pos, j) == "Sanctified Aggressor":
                    num_warlords = 0
                    for k in range(len(planets_list)):
                        if planets_list[i] == planet_pos:
                            num_warlords += 1
                    if num_warlords > 1:
                        if not self.check_if_already_have_reaction_of_position("Sanctified Aggressor", planet_pos, j):
                            self.game.create_reaction("Sanctified Aggressor", self.name_player,
                                                      (int(self.number), planet_pos, j))

    def commit_synapse_to_planet(self):
        if self.synapse_commit_location != -1:
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_card_type() == "Synapse" and self.headquarters[i].from_deck:
                    if self.headquarters[i].get_ability() == "Gravid Tervigon":
                        self.game.create_reaction("Gravid Tervigon", self.name_player,
                                                  (int(self.number), self.synapse_commit_location, -1))
                    if self.headquarters[i].get_ability() == "Venomthrope Polluter":
                        self.game.create_reaction("Venomthrope Polluter", self.name_player,
                                                  (int(self.number), self.synapse_commit_location, -1))
                    self.move_unit_to_planet(-2, i, self.synapse_commit_location, card_effect=False)
                    for j in range(len(self.headquarters)):
                        if self.headquarters[j].get_ability() == "Synaptic Link":
                            self.game.create_reaction("Synaptic Link", self.name_player, (int(self.number), -1, -1))
                    return None
        return None

    def ready_unit_by_name(self, name, planet):
        for i in range(len(self.cards_in_play[planet + 1])):
            if self.cards_in_play[planet + 1][i].get_ability() == name:
                self.ready_given_pos(planet, i)
                return True
        return False

    def commit_warlord_to_planet(self, planet_pos=None, only_warlord=False):
        headquarters_list = self.get_headquarters()
        if planet_pos is None:
            planet_pos = self.warlord_commit_location + 1
        if (planet_pos - 1) == self.sautekh_royal_crypt:
            other_player = self.get_other_player()
            self.game.create_reaction("Sautekh Royal Crypt Damage", other_player.name_player,
                                      (int(other_player.number), planet_pos - 1, -1))
        self.sautekh_royal_crypt = -1
        if only_warlord:
            for i in range(len(headquarters_list)):
                if headquarters_list[i].get_card_type() == "Warlord":
                    print(headquarters_list[i].get_name())
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Packmaster Kith":
                        self.game.create_reaction("Packmaster Kith", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Eldorath Starbane":
                        self.game.create_reaction("Eldorath Starbane", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Commander Shadowsun":
                        self.game.create_reaction("Commander Shadowsun", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Old Zogwort":
                        self.game.create_reaction("Old Zogwort", self.name_player,
                                                  (int(self.number), planet_pos - 1, i))
                    self.move_unit_to_planet(-2, i, planet_pos - 1)
                    for j in range(len(self.headquarters)):
                        if self.get_ability_given_pos(-2, j) == "Heralding Cherubim":
                            self.game.create_reaction("Heralding Cherubim", self.name_player,
                                                      (int(self.number), -2, j))
                    for j in range(7):
                        for k in range(len(self.cards_in_play[j + 1])):
                            if self.get_ability_given_pos(j, k) == "Heralding Cherubim":
                                self.game.create_reaction("Heralding Cherubim", self.name_player,
                                                          (int(self.number), j, k))
                        if j != planet_pos - 1:
                            for k in range(len(self.cards_in_play[j + 1])):
                                if self.get_ability_given_pos(j, k) == "Blackmane Sentinel":
                                    self.game.create_reaction("Blackmane Sentinel", self.name_player,
                                                              (int(self.number), j, k))
                    return True
            return False
        else:
            gardis_planets = ["Anshan", "Beckel", "Erida", "Excellor", "Jalayerid",
                              "Jaricho", "Munos", "Navida Prime", "Nectavus XI", "Vargus"]
            if self.game.planet_array[planet_pos - 1] in gardis_planets:
                self.game.create_reaction(self.game.planet_array[planet_pos - 1] + " Commit",
                                          self.name_player, (int(self.number), planet_pos - 1, -1))
            i = 0
            while i < len(headquarters_list):
                card_type = headquarters_list[i].get_card_type()
                if card_type == "Warlord" or card_type == "Army" or card_type == "Token":
                    print(headquarters_list[i].get_name())
                    if card_type != "Warlord":
                        headquarters_list[i].exhaust_card()
                        if headquarters_list[i].get_ability() == "Experimental Devilfish":
                            self.game.create_reaction("Experimental Devilfish", self.name_player,
                                                      (int(self.number), planet_pos - 1, -1))
                            self.game.player_who_resolves_reaction.append(self.name_player)
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Old Zogwort":
                        self.game.create_reaction("Old Zogwort", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability() == "Tras the Corrupter" or \
                            headquarters_list[i].get_ability() == "Tras the Corrupter BLOODIED":
                        self.game.create_reaction("Tras the Corrupter", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if self.search_attachments_at_pos(-2, i, "The Blade of Antwyr"):
                        self.game.create_reaction("The Blade of Antwyr", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Commander Starblaze":
                        self.game.create_reaction("Commander Starblaze", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Yvraine":
                        self.game.create_reaction("Yvraine", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "The Swarmlord":
                        self.game.create_reaction("The Swarmlord", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Packmaster Kith":
                        self.game.create_reaction("Packmaster Kith", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Eldorath Starbane":
                        self.game.create_reaction("Eldorath Starbane", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Commander Shadowsun":
                        self.game.create_reaction("Commander Shadowsun", self.name_player,
                                                  (int(self.number), planet_pos - 1, -1))
                    self.move_unit_to_planet(-2, i, planet_pos - 1, card_effect=False)
                    last_element_index = len(self.cards_in_play[planet_pos]) - 1
                    if self.get_ability_given_pos(planet_pos - 1, last_element_index) == "Ardent Auxiliaries":
                        self.game.create_reaction("Ardent Auxiliaries", self.name_player,
                                                  (int(self.number), planet_pos - 1, last_element_index))
                    if card_type == "Warlord":
                        if self.search_hand_for_card("Tides of Chaos"):
                            if self.resources > 0:
                                self.game.create_reaction("Tides of Chaos", self.name_player,
                                                          (int(self.number), -1, -1))
                        for j in range(7):
                            if j != planet_pos - 1:
                                for k in range(len(self.cards_in_play[j + 1])):
                                    if self.get_ability_given_pos(j, k) == "Blackmane Sentinel":
                                        self.game.create_reaction("Blackmane Sentinel", self.name_player,
                                                                  (int(self.number), j, k))
                    i -= 1
                i += 1
        return None

    def get_unstoppable_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_unstoppable()
        return self.cards_in_play[planet_id + 1][unit_id].get_unstoppable()

    def get_command_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_command()
        command = self.cards_in_play[planet_id + 1][unit_id].get_command()
        if self.cards_in_play[planet_id + 1][unit_id].command == 0:
            if self.search_card_in_hq("Administratum Office"):
                command += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Fire Warrior Grenadiers":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.check_for_trait_given_pos(planet_id, i, "Ethereal"):
                    command += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Iron Hands Techmarine":
            command += self.game.request_number_of_enemy_units_at_planet(self.number, planet_id)
        if self.get_ability_given_pos(planet_id, unit_id) == "Prognosticator":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                command += 1
        if self.get_ability_given_pos(planet_id, unit_id) == "Advocator of Blood":
            warlord_bloodied = False
            warlord_pla, warlord_pos = self.get_location_of_warlord()
            if warlord_pla == -2:
                if self.headquarters[warlord_pos].get_bloodied():
                    warlord_bloodied = True
            elif warlord_pla != -1:
                if self.cards_in_play[warlord_pla + 1][warlord_pos].get_bloodied():
                    warlord_bloodied = True
            if not warlord_bloodied:
                other_player = self.get_other_player()
                warlord_pla, warlord_pos = other_player.get_location_of_warlord()
                if warlord_pla == -2:
                    if other_player.headquarters[warlord_pos].get_bloodied():
                        warlord_bloodied = True
                elif warlord_pla != -1:
                    if other_player.cards_in_play[warlord_pla + 1][warlord_pos].get_bloodied():
                        warlord_bloodied = True
            if warlord_bloodied:
                command += 1
        if self.get_ability_given_pos(planet_id, unit_id) == "3rd Company Tactical Squad":
            if not self.check_if_support_exists():
                command += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Improbable Runt Machine":
            command += min(len(self.cards_in_play[planet_id + 1][unit_id].get_attachments()), 3)
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Goff Brawlers":
            if self.warlord_faction != "Orks":
                command += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_name() == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Brood Warriors":
                    command += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Warriors of Gidrim":
            if self.count_non_necron_factions() > 1:
                command += 1
        if self.get_faction_given_pos(planet_id, unit_id) == "Orks":
            if self.get_card_type_given_pos(planet_id, unit_id) == "Army":
                if self.search_card_in_hq("Painboy Tent"):
                    command += 1
        if self.get_card_type_given_pos(planet_id, unit_id) == "Army":
            if self.search_card_at_planet(planet_id, "Great Iron Gob"):
                command += 1
        return command

    def count_command_at_planet(self, planet_id, fbk=False, actual_cs=False):
        counted_command = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.get_ready_given_pos(planet_id, i) or self.war_of_ideas_active:
                count_unit_command = True
                if fbk:
                    if self.get_card_type_given_pos(planet_id, i) == "Army":
                        if self.get_cost_given_pos(planet_id, i) < 3:
                            count_unit_command = False
                if count_unit_command:
                    counted_command += self.get_command_given_pos(planet_id, i)
        if actual_cs:
            self.war_of_ideas_active = False
            if self.cards_in_reserve[planet_id]:
                if self.search_card_in_hq("Beleaguered Garrison"):
                    counted_command += len(self.cards_in_reserve[planet_id])
        return counted_command

    def count_tyranid_units_at_planet(self, planet_id):
        unit_count = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.cards_in_play[planet_id + 1][i].get_faction() == "Tyranids":
                unit_count += 1
        return unit_count

    def count_units_at_planet(self, planet_id):
        return len(self.cards_in_play[planet_id + 1])

    def count_units_in_play_all(self):
        unit_count = 0
        for i in range(7):
            unit_count += len(self.cards_in_play[i + 1])
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_card_type() != "Support":
                unit_count += 1
        return unit_count

    def get_bonus_winnings_at_planet(self, planet_id):
        extra_resources = 0
        extra_cards = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            extra_resources += self.cards_in_play[planet_id + 1][i].get_additional_resources_command_struggle()
            extra_cards += self.cards_in_play[planet_id + 1][i].get_additional_cards_command_struggle()
            if self.game.get_blue_icon(planet_id):
                if self.get_ability_given_pos(planet_id, i) == "Seer of Deceit":
                    extra_cards += 1
                if self.get_ability_given_pos(planet_id, i) == "Reliquary Techmarine":
                    extra_cards += 1
            if self.game.get_red_icon(planet_id):
                if self.get_ability_given_pos(planet_id, i) == "Skrap Nabba":
                    extra_resources += 2
                if self.get_ability_given_pos(planet_id, i) == "Sae'lum Pioneer":
                    extra_resources += 2
                if self.get_ability_given_pos(planet_id, i) == "Flayed Skull Slaver":
                    extra_resources += 2
            if self.game.infested_planets[planet_id]:
                if self.get_ability_given_pos(planet_id, i) == "Genestealer Harvesters":
                    extra_resources += 1
                    extra_cards += 1
        return extra_resources, extra_cards

    def find_warlord_planet(self):
        for i in range(7):
            if self.check_for_warlord(i):
                return i
        return -1

    def check_for_warlord(self, planet_id, card_effect=False, searching_name=""):
        if planet_id == -2:
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_card_type() == "Warlord":
                    return 1
            return 0
        if not self.cards_in_play[planet_id + 1]:
            pass
        else:
            for j in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][j].get_card_type() == "Warlord":
                    return 1
                if card_effect:
                    if searching_name in self.cards_in_play[planet_id + 1][j].hit_by_frenzied_wulfen_names:
                        return 1
        return 0

    def check_ready_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ready()

    def get_flying_given_pos(self, planet_id, unit_id):
        rokkitboy_present = self.game.request_search_for_enemy_card_at_planet(self.number, planet_id, "Rokkitboy")
        if rokkitboy_present:
            return False
        if self.get_ability_given_pos(planet_id, unit_id) == "Air Caste Courier":
            if self.warlord_faction != "Tau":
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Vengeful Seraphim":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                return True
        if self.get_name_given_pos(planet_id, unit_id) == "Termagant":
            if self.search_card_at_planet(planet_id, "Soaring Gargoyles"):
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Frenzied Bloodthirster":
            if self.game.bloodthirst_active[planet_id]:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Blitza-Bommer":
            if self.get_ready_given_pos(planet_id, unit_id):
                return True
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, "Adherent Outcast") and \
                    self.check_is_unit_at_pos(planet_id, unit_id):
                return True
        return self.cards_in_play[planet_id + 1][unit_id].get_flying()

    def set_blanked_given_pos(self, planet_id, unit_id, exp="EOP"):
        if planet_id == -2:
            self.headquarters[unit_id].set_blanked(True, exp=exp)
            return None
        self.cards_in_play[planet_id + 1][unit_id].set_blanked(True, exp=exp)
        return None

    def reset_all_blanked_eor(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].reset_blanked_eor()
            self.headquarters[i].reset_blanked_eor2()
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].reset_blanked_eor()
                self.cards_in_play[planet_pos + 1][unit_pos].reset_blanked_eor2()

    def reset_all_blanked_eop(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].reset_blanked_eop()
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].reset_blanked_eop()

    def check_for_enemy_warlord(self, planet_id, card_effect=False, searching_name=""):
        if self.number == "1":
            enemy_player = self.game.p2
        else:
            enemy_player = self.game.p1
        if enemy_player.check_for_warlord(planet_id, card_effect, searching_name):
            return True
        return False

    def get_armorbane_given_pos(self, planet_id, unit_id, enemy_unit_damage=0):
        warlord_pla, warlord_pos = self.get_location_of_warlord()
        if warlord_pla == planet_id:
            if self.search_attachments_at_pos(warlord_pla, warlord_pos, "Cloak of Shade"):
                return False
        other_player = self.get_other_player()
        warlord_pla, warlord_pos = other_player.get_location_of_warlord()
        if warlord_pla == planet_id:
            if other_player.search_attachments_at_pos(warlord_pla, warlord_pos, "Cloak of Shade"):
                return False
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Praetorian Ancient":
            if self.count_units_in_discard() > 5:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Treacherous Lhamaean":
            if self.warlord_faction != "Dark Eldar":
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Dominion Eugenia":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Frenzied Bloodthirster":
            if self.game.bloodthirst_active[planet_id]:
                return True
        if planet_id != -2:
            if self.get_faction_given_pos(planet_id, unit_id) == "Tau":
                if self.search_card_at_planet(planet_id, "Aun'shi", bloodied_relevant=True):
                    return True
            if self.search_attachments_at_pos(planet_id, unit_id, "Honorifica Imperialis"):
                if self.check_for_enemy_warlord(planet_id):
                    return True
        if self.get_name_given_pos(planet_id, unit_id) == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.get_ability_given_pos(planet_id, i) == "Caustic Tyrannofex":
                    if self.cards_in_play[planet_id + 1][i].misc_ability_used:
                        return True
        if enemy_unit_damage > 0:
            if self.check_for_trait_given_pos(planet_id, unit_id, "Elite") and \
                    self.check_is_unit_at_pos(planet_id, unit_id):
                if self.search_card_at_planet(planet_id, "Supplicant of Pain"):
                    return True
        return self.cards_in_play[planet_id + 1][unit_id].get_armorbane()

    def get_ignores_flying_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ignores_flying()

    def get_faction_given_pos(self, planet_id, unit_id):
        if self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
            if self.search_card_in_hq("Kustomisation Station"):
                return "Orks"
        if planet_id == -2:
            if self.get_card_type_given_pos(planet_id, unit_id) == "Army":
                if self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
                    if self.search_card_in_hq("Kustomisation Station"):
                        return "Orks"
            return self.headquarters[unit_id].get_faction()
        return self.cards_in_play[planet_id + 1][unit_id].get_faction()

    def get_name_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_name()
        return self.cards_in_play[planet_id + 1][unit_id].get_name()

    def get_has_hive_mind_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_has_hive_mind()
        return self.cards_in_play[planet_id + 1][unit_id].get_has_hive_mind()

    def get_ability_given_pos(self, planet_id, unit_id, bloodied_relevant=False):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ability(bloodied_relevant=bloodied_relevant)
        return self.cards_in_play[planet_id + 1][unit_id].get_ability(bloodied_relevant=bloodied_relevant)

    def get_traits_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_traits()
        return self.cards_in_play[planet_id + 1][unit_id].get_traits()

    def get_ready_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ready()
        return self.cards_in_play[planet_id + 1][unit_id].get_ready()

    def get_ambush_of_card(self, card):
        if card.get_ability() == "Standard Bearer":
            if self.warlord_faction != "Astra Militarum":
                return True
        if card.check_for_a_trait("Genestealer", self.etekh_trait):
            if self.subject_omega_relevant:
                return True
        if card.get_faction() == "Eldar":
            if card.get_is_unit():
                if self.concealing_darkness_active:
                    return True
        if self.followers_of_asuryan_relevant:
            if card.get_is_unit():
                if card.get_cost() < 4:
                    return True
        return card.get_ambush()

    def count_supports(self):
        count = 0
        for i in range(len(self.headquarters)):
            if self.get_card_type_given_pos(-2, i) == "Support":
                count += 1
        return count

    def get_mobile_given_pos(self, planet_id, unit_id):
        if self.get_ability_given_pos(planet_id, unit_id) == "Ravenwing Escort":
            if self.warlord_faction != "Space Marines":
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Venomous Fiend":
            if self.warlord_faction != "Chaos":
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Firstborn Battalion":
            if self.count_supports() > 2:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Interceptor Squad":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                return True
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, unit_id, "Herald of the Tau'va"):
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Conjuring Warmaster":
            if self.check_for_warlord(planet_id, card_effect=True, searching_name=self.name_player):
                return True
        if planet_id == -2:
            return self.headquarters[unit_id].get_mobile()
        return self.cards_in_play[planet_id + 1][unit_id].get_mobile()

    def get_available_mobile_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_available_mobile()

    def set_available_mobile_given_pos(self, planet_id, unit_id, new_val):
        if planet_id == -2:
            self.headquarters[unit_id].set_available_mobile(new_val)
            return None
        self.cards_in_play[planet_id + 1][unit_id].set_available_mobile(new_val)
        return None

    def set_available_mobile_all(self, new_val):
        for i in range(len(self.headquarters)):
            self.set_available_mobile_given_pos(-2, i, new_val)
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.set_available_mobile_given_pos(planet_pos, unit_pos, new_val)

    def search_cards_for_available_mobile(self):
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                if self.get_mobile_given_pos(planet_pos, unit_pos):
                    if self.get_available_mobile_given_pos(planet_pos, unit_pos):
                        return True
        return False

    def search_card_at_planet(self, planet_id, name_of_card, bloodied_relevant=False, ability_checking=True,
                              ready_relevant=False, once_per_phase_relevant=False):
        if planet_id == -2:
            return False
        if not ability_checking:
            for i in range(len(self.cards_in_play[planet_id + 1])):
                current_name = self.cards_in_play[planet_id + 1][i].get_name()
                if self.cards_in_play[planet_id + 1][i].get_name() == name_of_card:
                    if not bloodied_relevant:
                        return True
                    if self.cards_in_play[planet_id + 1][i].get_bloodied():
                        return False
                    return True
                if self.search_attachments_at_pos(planet_id, i, name_of_card):
                    return True
            return False
        for i in range(len(self.cards_in_play[planet_id + 1])):
            current_name = self.cards_in_play[planet_id + 1][i].get_ability()
            if current_name == name_of_card:
                if not ready_relevant or self.get_ready_given_pos(planet_id, i):
                    if not bloodied_relevant:
                        return True
                    if self.cards_in_play[planet_id + 1][i].get_bloodied():
                        return False
                    if not once_per_phase_relevant or not self.get_once_per_phase_used_given_pos(planet_id, i):
                        return True
                    return True
            if self.search_attachments_at_pos(planet_id, i, name_of_card):
                return True
        return False

    def get_dw_term_active(self, planet_pos, unit_pos):
        if planet_pos == -2:
            return self.headquarters[unit_pos].misc_ability_used
        return self.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used

    def get_immune_to_enemy_card_abilities(self, planet_pos, unit_pos):
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Deathwing Terminators":
            if self.get_dw_term_active(planet_pos, unit_pos):
                return True
        if self.get_ability_given_pos(planet_pos, unit_pos) == "23rd Mechanised Battalion":
            return True
        if planet_pos != -2:
            if not self.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait("Vehicle"):
                for i in range(len(self.cards_in_play[planet_pos + 1])):
                    if self.get_ability_given_pos(planet_pos, i) == "Land Raider":
                        return True
            if self.search_card_at_planet(planet_pos, "Shas'el Lyst", ready_relevant=True):
                other_player = self.get_other_player()
                if other_player.spend_resources(1):
                    self.game.queued_message = "Important info: Shas'el Lyst made " + other_player.name_player + \
                                               " spend 1 resource!"
                else:
                    return True
        return False

    def get_immune_to_enemy_events(self, planet_pos, unit_pos, power=False):
        if not self.check_is_unit_at_pos(planet_pos, unit_pos):
            return False
        if self.search_attachments_at_pos(planet_pos, unit_pos, "Lucky Warpaint"):
            return True
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Stalwart Ogryn":
            return True
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Frenzied Bloodthirster" and power:
            return True
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Amalgamated Devotee":
            if len(self.get_all_attachments_at_pos(planet_pos, unit_pos)) > 1:
                return True
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Champion of Khorne":
            if self.game.bloodthirst_active[planet_pos]:
                return True
        if self.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
            if self.search_card_at_planet(planet_pos, "Vostroyan Officer"):
                return True
        return False

    def search_card_in_hq(self, name_of_card, bloodied_relevant=False, ability_checking=True, ready_relevant=False):
        for i in range(len(self.headquarters)):
            current_name = self.headquarters[i].get_ability()
            if current_name == name_of_card:
                if current_name == "Holding Cell":
                    if len(self.headquarters[i].get_attachments()) == 0:
                        return True
                else:
                    if bloodied_relevant:
                        if self.headquarters[i].get_bloodied():
                            return False
                        else:
                            return True
                    if ready_relevant:
                        if self.headquarters[i].get_ready():
                            return True
                    else:
                        return True
        return False

    def search_hq_for_discounts(self, faction_of_card, traits, is_attachment=False, planet_chosen=None, name_of_card=""):
        discounts_available = 0
        if is_attachment:
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_ability() == "Ambush Platform":
                    discounts_available += 1
            return discounts_available
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_applies_discounts():
                print("applies")
                if self.headquarters[i].get_is_faction_limited_unique_discounter():
                    print("is fac lim uni dis")
                    if self.headquarters[i].get_faction() == faction_of_card:
                        print("faction ok")
                        if self.headquarters[i].get_ready():
                            print("ready")
                            self.set_aiming_reticle_in_play(-2, i, "green")
                            discounts_available += self.headquarters[i].get_discount_amount()
                elif self.headquarters[i].get_ability() == "Parasitic Scarabs":
                    if faction_of_card == "Necrons":
                        discounts_available += 1
                        self.set_aiming_reticle_in_play(-2, i, "green")
                elif self.headquarters[i].get_ability() == "Digestion Pool":
                    if self.headquarters[i].get_ready():
                        if planet_chosen is not None:
                            if self.game.infested_planets[planet_chosen]:
                                discounts_available += 2
                                self.set_aiming_reticle_in_play(-2, i, "green")
                elif self.headquarters[i].get_ability() == "STC Fragment":
                    if self.headquarters[i].get_ready():
                        if "Elite" in traits:
                            discounts_available += 2
                            self.set_aiming_reticle_in_play(-2, i, "green")
                elif self.headquarters[i].get_ability() == "Bonesinger Choir":
                    if faction_of_card == "Eldar":
                        if "Vehicle" in traits or "Drone" in traits:
                            discounts_available += 2
                            self.set_aiming_reticle_in_play(-2, i, "green")
            if "Daemon" in traits:
                if self.headquarters[i].get_ability() == "Cultist":
                    discounts_available += 1
                    if name_of_card == "Venomcrawler":
                        discounts_available += 1
                    self.set_aiming_reticle_in_play(-2, i, "green")
                    if "Elite" in traits:
                        discounts_available += self.count_copies_in_play("Master Warpsmith", ability=True)
                elif self.headquarters[i].get_ability() == "Splintered Path Acolyte":
                    discounts_available += 2
                    self.set_aiming_reticle_in_play(-2, i, "green")
            if faction_of_card != "Tau":
                if self.headquarters[i].get_ability() == "Sae'lum Enclave":
                    if self.get_ready_given_pos(-2, i):
                        discounts_available += 2
                        self.set_aiming_reticle_in_play(-2, i, "green")
            if self.headquarters[i].get_ability() == "Prophets of Flesh":
                if "Abomination" in traits or "Scholar" in traits:
                    if self.get_ready_given_pos(-2, i):
                        discounts_available += 1
                        self.set_aiming_reticle_in_play(-2, i, "green")
            if "Ecclesiarchy" in traits:
                if self.search_attachments_at_pos(-2, i, "Banner of the Sacred Rose", ready_relevant=True):
                    other_player = self.get_other_player()
                    icons = other_player.get_icons_on_captured()
                    discounts_available += icons[2] + 1
                    self.set_aiming_reticle_in_play(-2, i, "green")
        return discounts_available

    def search_planet_for_discounts(self, planet_pos, traits, faction_of_card, name_of_card=""):
        discounts_available = 0
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if "Ecclesiarchy" in traits:
                if self.search_attachments_at_pos(planet_pos, i, "Banner of the Sacred Rose", ready_relevant=True):
                    other_player = self.get_other_player()
                    icons = other_player.get_icons_on_captured()
                    discounts_available += icons[2] + 1
                    self.set_aiming_reticle_in_play(planet_pos, i, "green")
            if "Daemon" in traits:
                if self.cards_in_play[planet_pos + 1][i].get_ability() == "Cultist":
                    discounts_available += 1
                    if name_of_card == "Venomcrawler":
                        discounts_available += 1
                    self.set_aiming_reticle_in_play(planet_pos, i, "green")
                    if "Elite" in traits:
                        discounts_available += self.count_copies_in_play("Master Warpsmith", ability=True)
                elif self.cards_in_play[planet_pos + 1][i].get_ability() == "Splintered Path Acolyte":
                    discounts_available += 2
                    self.set_aiming_reticle_in_play(planet_pos, i, "green")
            elif self.cards_in_play[planet_pos + 1][i].get_ability() == "Parasitic Scarabs":
                if faction_of_card == "Necrons":
                    discounts_available += 1
                    self.set_aiming_reticle_in_play(planet_pos, i, "green")
        return discounts_available

    def reset_all_aiming_reticles_play_hq(self):
        for i in range(len(self.headquarters)):
            self.reset_aiming_reticle_in_play(-2, i)
        for j in range(7):
            for i in range(len(self.cards_in_play[j + 1])):
                self.reset_aiming_reticle_in_play(j, i)

    def search_all_planets_for_discounts(self, traits, faction_of_card, name_of_card=""):
        discounts_available = 0
        for i in range(7):
            discounts_available += self.search_planet_for_discounts(i, traits, faction_of_card,
                                                                    name_of_card=name_of_card)
        return discounts_available

    def search_same_planet_for_discounts(self, faction_of_card, planet_pos):
        discounts_available = 0
        automatic_discounts = 0
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.cards_in_play[planet_pos + 1][i].get_ability() == "Crushface":
                if faction_of_card == "Orks":
                    self.set_aiming_reticle_in_play(planet_pos, i, "green")
                    discounts_available += 1
                    automatic_discounts += 1
        return discounts_available, automatic_discounts

    def valid_nullify_unit(self, planet_pos, unit_pos):
        if planet_pos == -2:
            if self.headquarters[unit_pos].get_faction() == "Eldar" and self.headquarters[unit_pos].get_is_unit() and \
                    self.headquarters[unit_pos].get_unique() and self.headquarters[unit_pos].get_ready():
                return True
            return False
        if self.cards_in_play[planet_pos + 1][unit_pos].get_faction() == "Eldar" and \
                self.cards_in_play[planet_pos + 1][unit_pos].get_is_unit() and \
                self.cards_in_play[planet_pos + 1][unit_pos].get_unique() and \
                self.cards_in_play[planet_pos + 1][unit_pos].get_ready():
            return True
        return False

    def nullify_check(self):
        print("---\nNullify Check!\n---")
        if self.hit_by_gorgul:
            return False
        other_player = self.get_other_player()
        if other_player.vael_relevent:
            return False
        num_nullifies = 0
        if self.castellan_crowe_relevant:
            if "Psychic Ward" in self.cards:
                return True
            return False
        if self.urien_relevant:
            if self.resources < 1:
                return False
        for i in range(len(self.cards)):
            if self.cards[i] == "Nullify":
                num_nullifies += 1
        if num_nullifies > self.num_nullify_played:
            for i in range(len(self.headquarters)):
                if self.valid_nullify_unit(-2, i):
                    return True
            for planet_pos in range(7):
                for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                    if self.valid_nullify_unit(planet_pos, unit_pos):
                        return True
        return False

    def intercept_check(self):
        possible_interrupts = []
        if self.game.intercept_enabled:
            if self.search_card_in_hq("Intercept", ready_relevant=True):
                possible_interrupts.append("Intercept")
        return possible_interrupts

    def storm_of_silence_check(self):
        if self.resources > 1:
            if self.search_hand_for_card("Storm of Silence"):
                return True
        return False

    def interrupt_cancel_target_check(self, planet_pos, unit_pos, context="", move_from_planet=False,
                                      targeting_support=False, intercept_possible=False, event=False):
        possible_interrupts = []
        vael = False
        if event:
            other_player = self.get_other_player()
            vael = other_player.vael_relevent
        if targeting_support:
            if self.game.colony_shield_generator_enabled:
                if self.get_ability_given_pos(planet_pos, unit_pos) != "Colony Shield Generator":
                    if self.search_card_in_hq("Colony Shield Generator", ready_relevant=True):
                        possible_interrupts.append("Colony Shield Generator")
        else:
            if context == "Searing Brand" and not vael:
                if self.game.searing_brand_cancel_enabled:
                    if len(self.cards) > 1:
                        possible_interrupts.append("Searing Brand")
            if move_from_planet and not vael:
                if self.game.slumbering_gardens_enabled:
                    if self.search_card_in_hq("Slumbering Gardens", ready_relevant=True):
                        possible_interrupts.append("Slumbering Gardens")
            if intercept_possible:
                if self.game.intercept_enabled:
                    if self.search_card_in_hq("Intercept", ready_relevant=True):
                        possible_interrupts.append("Intercept")
            if self.game.storm_of_silence_enabled and not vael:
                if self.storm_of_silence_check():
                    possible_interrupts.append("Storm of Silence")
            if self.game.communications_relay_enabled and not vael:
                if self.communications_relay_check(planet_pos, unit_pos):
                    possible_interrupts.append("Communications Relay")
            if self.game.backlash_enabled and not vael:
                if self.backlash_check(planet_pos, unit_pos):
                    possible_interrupts.append("Backlash")
            if planet_pos != -2:
                if self.game.communications_relay_enabled and not vael:
                    if self.cards_in_play[planet_pos + 1][unit_pos].immortal_loyalist_ok:
                        self.cards_in_play[planet_pos + 1][unit_pos].immortal_loyalist_ok = False
                        if self.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                            if self.search_card_at_planet(planet_pos, "Immortal Loyalist"):
                                possible_interrupts.append("Immortal Loyalist")
                    for i in range(len(self.cards_in_play[planet_pos + 1])):
                        if self.get_ability_given_pos(planet_pos, i, bloodied_relevant=True) == "Jain Zar":
                            if not self.cards_in_play[planet_pos + 1][i].once_per_round_used:
                                possible_interrupts.append("Jain Zar")
        return possible_interrupts

    def backlash_check(self, planet_pos, unit_pos):
        print("---\nBacklash Check!\n---")
        backlash_permitted = False
        if planet_pos == -2:
            if self.headquarters[unit_pos].get_is_unit():
                if self.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    backlash_permitted = True
        elif self.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
            if self.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                backlash_permitted = True
        if backlash_permitted:
            if self.resources > 0:
                if self.urien_relevant:
                    if self.resources < 2:
                        return False
                if self.search_hand_for_card("Backlash"):
                    return True
        return False

    def communications_relay_check(self, planet_pos, unit_pos):
        print("---\nCommunications Relay Check!\n---")
        communications_permitted = False
        if planet_pos == -2:
            if self.headquarters[unit_pos].get_is_unit():
                if self.headquarters[unit_pos].get_attachments():
                    communications_permitted = True
        elif self.cards_in_play[planet_pos + 1][unit_pos].get_attachments():
            communications_permitted = True
        if communications_permitted:
            if self.search_card_in_hq("Communications Relay", ready_relevant=True):
                return True
        return False

    def foretell_check(self):
        if self.foretell_permitted:
            if self.urien_relevant:
                if self.resources < 1:
                    return False
            war_plan, war_pos = self.get_location_of_warlord()
            if self.get_ready_given_pos(war_plan, war_pos):
                if self.search_hand_for_card("Foretell"):
                    return True
        return False

    def spend_foretell(self):
        war_plan, war_pos = self.get_location_of_warlord()
        self.exhaust_given_pos(war_plan, war_pos)
        self.discard_card_name_from_hand("Foretell")
        if self.urien_relevant:
            self.spend_resources(1)
        if self.search_hand_for_card("Banshee Assault Squad"):
            self.game.create_reaction("Banshee Assault Squad", self.name_player, (int(self.number), -1, -1))

    def search_hand_for_card(self, card_name):
        for i in range(len(self.cards)):
            if self.cards[i] == card_name:
                return True
        return False

    def get_card_type_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            return self.headquarters[unit_pos].get_card_type()
        return self.cards_in_play[planet_pos + 1][unit_pos].get_card_type()

    def search_hand_for_discounts(self, faction_of_card, traits=""):
        discounts_available = 0
        for i in range(len(self.cards)):
            if self.cards[i] == "Bigga Is Betta":
                if faction_of_card == "Orks":
                    discounts_available += 2
        if "Drone" not in traits:
            if not self.optimized_landing_used:
                if self.search_hand_for_card("Optimized Landing"):
                    discounts_available += min(2, self.count_attachments_controlled())
        return discounts_available

    def search_attachments_at_pos(self, planet_pos, unit_pos, card_abil, ready_relevant=False, must_match_name=False):
        if planet_pos == -2:
            for i in range(len(self.headquarters[unit_pos].get_attachments())):
                if self.headquarters[unit_pos].get_attachments()[i].get_ability() == card_abil and not \
                        self.headquarters[unit_pos].get_attachments()[i].from_magus_harid:
                    if not must_match_name or \
                            self.headquarters[unit_pos].get_attachments()[i].name_owner == self.name_player:
                        if not ready_relevant:
                            return True
                        if self.headquarters[unit_pos].get_attachments()[i].get_ready():
                            return True
            return False
        for i in range(len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_ability() == card_abil:
                if not must_match_name or self.cards_in_play[planet_pos + 1][unit_pos] \
                        .get_attachments()[i].name_owner == self.name_player:
                    if not ready_relevant:
                        return True
                    if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_ready():
                        return True
        return False

    def perform_discount_at_pos_hq_attachment(self, pos, att_pos, faction_of_card, traits, target_planet=None):
        discount = 0
        if self.headquarters[pos].aiming_reticle_color == "green":
            if self.headquarters[pos].get_attachments()[att_pos].get_ability() == "Banner of the Sacred Rose":
                if "Ecclesiarchy" in traits:
                    if self.headquarters[pos].get_attachments()[att_pos].get_ready():
                        self.headquarters[pos].get_attachments()[att_pos].exhaust_card()
                        other_player = self.get_other_player()
                        icons = other_player.get_icons_on_captured()
                        discount += icons[2] + 1
        return discount

    def perform_discount_at_pos_in_play_attachment(self, planet_pos, unit_pos, att_pos, traits):
        discount = 0
        if self.cards_in_play[planet_pos + 1][unit_pos].aiming_reticle_color == "green":
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[
                    att_pos].get_ability() == "Banner of the Sacred Rose":
                if "Ecclesiarchy" in traits:
                    if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[att_pos].get_ready():
                        self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[att_pos].exhaust_card()
                        other_player = self.get_other_player()
                        icons = other_player.get_icons_on_captured()
                        discount += icons[2] + 1
        return discount

    def perform_discount_at_pos_hq(self, pos, faction_of_card, traits, target_planet=None, name_of_card=""):
        discount = 0
        if self.headquarters[pos].get_applies_discounts():
            if self.headquarters[pos].get_is_faction_limited_unique_discounter():
                if self.headquarters[pos].get_faction() == faction_of_card:
                    if self.headquarters[pos].get_ready():
                        self.headquarters[pos].exhaust_card()
                        discount += self.headquarters[pos].get_discount_amount()
            elif self.headquarters[pos].get_ability() == "Digestion Pool":
                if self.headquarters[pos].get_ready():
                    if target_planet is not None:
                        if self.game.infested_planets[target_planet]:
                            discount += 2
                            self.exhaust_given_pos(-2, pos)
        if self.headquarters[pos].get_ability() == "Gorzod":
            if self.headquarters[pos].aiming_reticle_color == "green":
                discount += 1
                self.reset_aiming_reticle_in_play(-2, pos)
        if self.headquarters[pos].get_ability() == "Parasitic Scarabs":
            if self.headquarters[pos].aiming_reticle_color == "green":
                discount += 1
                self.reset_aiming_reticle_in_play(-2, pos)
                self.assign_damage_to_pos(-2, pos, 1, by_enemy_unit=False)
                self.game.damage_for_unit_to_take_on_play.append(1)
                self.discard_top_card_deck()
        if self.headquarters[pos].get_ability() == "Sae'lum Enclave":
            if self.headquarters[pos].aiming_reticle_color == "green":
                self.exhaust_given_pos(-2, pos)
                discount += 2
                self.reset_aiming_reticle_in_play(-2, pos)
        if self.headquarters[pos].get_ability() == "Prophets of Flesh":
            if self.headquarters[pos].aiming_reticle_color == "green":
                self.exhaust_given_pos(-2, pos)
                discount += 1
                self.reset_aiming_reticle_in_play(-2, pos)
        if "Elite" in traits:
            if self.headquarters[pos].get_ability() == "STC Fragment":
                if self.headquarters[pos].get_ready():
                    self.exhaust_given_pos(-2, pos)
                    discount += 2
                    if self.game.apoka:
                        self.game.deploy_exhausted = True
        if self.headquarters[pos].get_ability() == "Bonesinger Choir":
            if self.headquarters[pos].aiming_reticle_color == "green":
                self.exhaust_given_pos(-2, pos)
                discount += 2
                self.reset_aiming_reticle_in_play(-2, pos)
        if "Daemon" in traits:
            if self.headquarters[pos].get_ability() == "Cultist":
                if self.sacrifice_card_in_hq(pos):
                    discount += 1
                    if name_of_card == "Venomcrawler":
                        discount += 1
            elif self.headquarters[pos].get_ability() == "Splintered Path Acolyte":
                discount += 2
                self.sacrifice_card_in_hq(pos)
        return discount

    def increase_eor_value(self, eor_name, value, planet_pos, unit_pos):
        if planet_pos == -2:
            if "Area Effect" in eor_name:
                self.headquarters[unit_pos].area_effect_eor += value
            elif eor_name == "Armorbane":
                self.headquarters[unit_pos].armorbane_eor = True
            elif eor_name == "Mobile":
                self.headquarters[unit_pos].mobile_eor = True
            return None
        if "Area Effect" in eor_name:
            self.cards_in_play[planet_pos + 1][unit_pos].area_effect_eor += value
        elif eor_name == "Armorbane":
            self.cards_in_play[planet_pos + 1][unit_pos].armorbane_eor = True
        elif eor_name == "Mobile":
            self.cards_in_play[planet_pos + 1][unit_pos].mobile_eor = True
        return None

    def round_ends_reset_values(self):
        self.reset_all_blanked_eor()
        for i in range(len(self.headquarters)):
            self.headquarters[i].set_once_per_round_used(False)
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].used_techmarine_ids = []
                for j in range(len(self.headquarters[i].get_attachments())):
                    self.headquarters[i].get_attachments()[j].set_once_per_round_used(False)
                self.headquarters[i].area_effect_eor = 0
                self.headquarters[i].brutal_eor = False
                self.headquarters[i].flying_eor = False
                self.headquarters[i].armorbane_eor = False
                self.headquarters[i].positive_hp_until_eor = 0
                self.headquarters[i].sweep_eor = 0
                self.headquarters[i].yvraine_active = False
                self.headquarters[i].retaliate_eor = 0
                self.headquarters[i].extra_attack_until_end_of_round = 0
                self.headquarters[i].mobile_eor = False
                self.headquarters[i].ranged_eor = False
                self.headquarters[i].extra_traits_eor = ""
                self.headquarters[i].embarked_squads_active = False
                if self.get_name_given_pos(-2, i) == "Caustic Tyrannofex":
                    self.headquarters[i].misc_ability_used = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].set_once_per_round_used(False)
                self.cards_in_play[i + 1][j].used_techmarine_ids = []
                for k in range(len(self.cards_in_play[i + 1][j].get_attachments())):
                    self.cards_in_play[i + 1][j].get_attachments()[k].set_once_per_round_used(False)
                self.cards_in_play[i + 1][j].area_effect_eor = 0
                self.cards_in_play[i + 1][j].brutal_eor = False
                self.cards_in_play[i + 1][j].flying_eor = False
                self.cards_in_play[i + 1][j].armorbane_eor = False
                self.cards_in_play[i + 1][j].positive_hp_until_eor = 0
                self.cards_in_play[i + 1][j].extra_attack_until_end_of_round = 0
                self.cards_in_play[i + 1][j].sweep_eor = 0
                self.cards_in_play[i + 1][j].yvraine_active = False
                self.cards_in_play[i + 1][j].retaliate_eor = 0
                self.cards_in_play[i + 1][j].mobile_eor = False
                self.cards_in_play[i + 1][j].ranged_eor = False
                self.cards_in_play[i + 1][j].extra_traits_eor = ""
                self.cards_in_play[i + 1][j].embarked_squads_active = False
                if self.get_name_given_pos(i, j) == "Caustic Tyrannofex":
                    self.cards_in_play[i + 1][j].misc_ability_used = False

    def check_is_unit_at_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            if self.headquarters[unit_pos].get_is_unit():
                return True
            return False
        if self.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
            return True
        return False

    def increase_health_of_unit_at_pos(self, planet_pos, unit_pos, amount, expiration="EOB"):
        if planet_pos == -2:
            if expiration == "EOP":
                self.headquarters[unit_pos].increase_extra_health_until_end_of_phase(amount)
            elif expiration == "EOR":
                self.headquarters[unit_pos].increase_extra_health_until_end_of_round(amount)
            elif expiration == "EOG":
                self.headquarters[unit_pos].increase_extra_health_until_end_of_game(amount)
            return None
        if expiration == "EOP":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_health_until_end_of_phase(amount)
        elif expiration == "EOR":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_health_until_end_of_round(amount)
        elif expiration == "EOG":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_health_until_end_of_game(amount)
        return None

    def increase_attack_of_unit_at_pos(self, planet_pos, unit_pos, amount, expiration="EOB"):
        if planet_pos == -2:
            if expiration == "EOB":
                self.headquarters[unit_pos].increase_extra_attack_until_end_of_battle(amount)
            elif expiration == "NEXT":
                self.headquarters[unit_pos].increase_extra_attack_until_next_attack(amount)
            elif expiration == "EOP":
                self.headquarters[unit_pos].increase_extra_attack_until_end_of_phase(amount)
            elif expiration == "EOG":
                self.headquarters[unit_pos].increase_extra_attack_until_end_of_game(amount)
            elif expiration == "EOR":
                self.headquarters[unit_pos].increase_extra_attack_until_end_of_round(amount)
            return None
        if expiration == "EOB":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_end_of_battle(amount)
        elif expiration == "NEXT":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_next_attack(amount)
        elif expiration == "EOP":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_end_of_phase(amount)
        elif expiration == "EOG":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_end_of_game(amount)
        elif expiration == "EOR":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_end_of_round(amount)
        return None

    def increase_attack_of_all_units_at_hq(self, amount, required_faction=None, expiration="EOB"):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                if required_faction is None:
                    self.increase_attack_of_unit_at_pos(-2, i, amount, expiration)
                elif required_faction == self.headquarters[i].get_faction():
                    self.increase_attack_of_unit_at_pos(-2, i, amount, expiration)

    def increase_attack_of_all_units_at_planet(self, amount, planet_pos, required_faction=None, expiration="EOB"):
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.cards_in_play[planet_pos + 1][i].get_is_unit():
                if required_faction is None:
                    self.increase_attack_of_unit_at_pos(planet_pos, i, amount, expiration)
                elif required_faction == self.cards_in_play[planet_pos + 1][i].get_faction():
                    self.increase_attack_of_unit_at_pos(planet_pos, i, amount, expiration)

    def increase_attack_of_all_units_at_all_planets(self, amount, required_faction=None, expiration="EOB"):
        for planet_pos in range(7):
            self.increase_attack_of_all_units_at_planet(amount, planet_pos, required_faction, expiration)

    def increase_attack_of_all_units_in_play(self, amount, required_faction=None, expiration="EOB"):
        self.increase_attack_of_all_units_at_hq(amount, required_faction, expiration)
        self.increase_attack_of_all_units_at_all_planets(amount, required_faction, expiration)

    def reset_reaction_beasthunter_wyches(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Beasthunter Wyches":
                self.headquarters[i].set_reaction_availabe(True)
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Beasthunter Wyches":
                    self.cards_in_play[planet_pos + 1][unit_pos].set_reaction_available(True)

    def reset_extra_attack_eob(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].reset_extra_attack_until_end_of_battle()
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].reset_extra_attack_until_end_of_battle()

    def reset_extra_health_eob(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].reset_extra_health_until_end_of_battle()
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].reset_extra_health_until_end_of_battle()

    def reset_extra_attack_until_next_attack_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            if self.headquarters[unit_pos].get_is_unit():
                self.headquarters[unit_pos].reset_extra_attack_until_next_attack()
            return None
        if self.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
            self.cards_in_play[planet_pos + 1][unit_pos].reset_extra_attack_until_next_attack()
        return None

    def sacrifice_check_eop(self):
        sacrificed_locations = [False, False, False, False, False, False, False, False]
        i = 0
        while i < len(self.headquarters):
            if self.headquarters[i].get_sacrifice_end_of_phase():
                if self.sacrifice_card_in_hq(i):
                    sacrificed_locations[0] = True
                    i = i - 1
            elif self.headquarters[i].quick_construct:
                if self.sacrifice_card_in_hq(i):
                    sacrificed_locations[0] = True
                    i = i - 1
                    self.draw_card()
            elif self.headquarters[i].saint_celestine_active:
                if self.sacrifice_card_in_hq(i):
                    sacrificed_locations[0] = True
                    i = i - 1
                    self.draw_card()
            i = i + 1
        for planet_pos in range(7):
            unit_pos = 0
            while unit_pos < len(self.cards_in_play[planet_pos + 1]):
                if self.cards_in_play[planet_pos + 1][unit_pos].get_sacrifice_end_of_phase():
                    if self.sacrifice_card_in_play(planet_pos, unit_pos):
                        sacrificed_locations[planet_pos + 1] = True
                        unit_pos = unit_pos - 1
                elif self.cards_in_play[planet_pos + 1][unit_pos].saint_celestine_active:
                    if self.sacrifice_card_in_play(planet_pos, unit_pos):
                        sacrificed_locations[planet_pos + 1] = True
                        unit_pos = unit_pos - 1
                        self.draw_card()
                unit_pos += 1
        return sacrificed_locations

    def clear_effects_end_of_cs(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].hit_by_superiority = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_is_unit():
                    self.cards_in_play[i + 1][j].hit_by_superiority = False

    def reset_extra_abilities_eop(self):
        self.dark_possession_active = False
        self.the_princes_might_active = [False, False, False, False, False, False, False]
        self.concealing_darkness_active = False
        for i in range(len(self.headquarters)):
            if self.game.phase == "DEPLOY":
                self.headquarters[i].cannot_ready_hq_phase = False
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].hit_by_which_salamanders = []
                if self.headquarters[i].get_name() != "Kairos Fateweaver" or self.game.phase == "DEPLOY":
                    self.headquarters[i].new_ability = ""
                self.headquarters[i].reset_ranged()
                self.headquarters[i].reset_all_eop()
                if self.game.phase == "COMBAT":
                    self.headquarters[i].command_until_combat = 0
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                if self.game.phase == "DEPLOY":
                    self.cards_in_play[planet_pos + 1][unit_pos].cannot_ready_hq_phase = False
                self.cards_in_play[planet_pos + 1][unit_pos].reset_ranged()
                self.cards_in_play[planet_pos + 1][unit_pos].reset_all_eop()
                if self.cards_in_play[planet_pos + 1][unit_pos].get_name() != "Kairos Fateweaver" or self.game.phase == "DEPLOY":
                    self.cards_in_play[planet_pos + 1][unit_pos].new_ability = ""
                self.cards_in_play[planet_pos + 1][unit_pos].hit_by_which_salamanders = []
                if self.game.phase == "COMBAT":
                    self.cards_in_play[planet_pos + 1][unit_pos].command_until_combat = 0

    def reset_extra_attack_eop(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].reset_extra_attack_until_end_of_phase()
                self.headquarters[i].reset_extra_attack_until_next_attack()
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].reset_extra_attack_until_end_of_phase()
                self.cards_in_play[planet_pos + 1][unit_pos].reset_extra_attack_until_next_attack()

    def refresh_once_per_phase_abilities(self):
        self.webway_witch = -1
        for i in range(len(self.headquarters)):
            self.headquarters[i].set_once_per_phase_used(False)
            self.headquarters[i].world_engine_owner = False
            self.headquarters[i].world_engine_enemy = False
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].set_once_per_phase_used(False)
                self.cards_in_play[planet_pos + 1][unit_pos].world_engine_owner = False
                self.cards_in_play[planet_pos + 1][unit_pos].world_engine_enemy = False

    def perform_discount_at_pos_hand(self, pos, faction_of_card, traits):
        discount = 0
        damage = 0
        if self.cards[pos] == "Bigga Is Betta":
            if faction_of_card == "Orks":
                discount += 2
                damage += 1
        if self.cards[pos] == "Optimized Landing":
            if "Drone" not in traits:
                if not self.optimized_landing_used:
                    discount += min(2, self.count_attachments_controlled())
        return discount, damage

    def perform_discount_at_pos_in_play(self, planet_pos, unit_pos, traits, name_of_card=""):
        discount = 0
        if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Crushface":
            if self.cards_in_play[planet_pos + 1][unit_pos].aiming_reticle_color == "green":
                self.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                discount += 1
        if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Gorzod":
            if self.cards_in_play[planet_pos + 1][unit_pos].aiming_reticle_color == "green":
                self.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                discount += 1
        if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Parasitic Scarabs":
            if self.cards_in_play[planet_pos + 1][unit_pos].aiming_reticle_color == "green":
                discount += 1
                self.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                self.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                self.game.damage_for_unit_to_take_on_play.append(1)
                self.discard_top_card_deck()
        if "Daemon" in traits:
            if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Cultist":
                if self.sacrifice_card_in_play(planet_pos, unit_pos):
                    discount += 1
                    if name_of_card == "Venomcrawler":
                        discount += 1
            elif self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Splintered Path Acolyte":
                discount += 2
                self.sacrifice_card_in_play(planet_pos, unit_pos)
        return discount

    def exhaust_given_pos(self, planet_id, unit_id, card_effect=False):
        if planet_id == -2:
            previous_state = self.headquarters[unit_id].get_ready()
            self.headquarters[unit_id].exhaust_card()
            new_state = self.headquarters[unit_id].get_ready()
            if previous_state and not new_state:
                if self.get_ability_given_pos(planet_id, unit_id) == "Exalted Celestians":
                    self.game.create_reaction("Exalted Celestians", self.name_player,
                                              (int(self.number), planet_id, unit_id))
                for i in range(len(self.headquarters[unit_id].get_attachments())):
                    if self.headquarters[unit_id].get_attachments()[i].get_ability() == "Dire Mutation":
                        self.assign_damage_to_pos(-2, unit_id, 1, by_enemy_unit=False)
            return None
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, "Disciple of Excess") and card_effect:
                return None
        previous_state = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        self.cards_in_play[planet_id + 1][unit_id].exhaust_card()
        new_state = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        if previous_state and not new_state:
            if self.get_ability_given_pos(planet_id, unit_id) == "Exalted Celestians":
                self.game.create_reaction("Exalted Celestians", self.name_player,
                                          (int(self.number), planet_id, unit_id))
            for i in range(len(self.cards_in_play[planet_id + 1][unit_id].get_attachments())):
                if self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].get_ability() == "Dire Mutation":
                    self.assign_damage_to_pos(planet_id, unit_id, 1, by_enemy_unit=False)
        return None

    def get_area_effect_given_pos(self, planet_id, unit_id):
        if self.search_card_at_planet(planet_id, "Zen Xi Aonia"):
            return 0
        else:
            other_player = self.get_other_player()
            if other_player.search_card_at_planet(planet_id, "Zen Xi Aonia"):
                return 0
        area_effect = self.cards_in_play[planet_id + 1][unit_id].get_area_effect()
        if self.cards_in_play[planet_id + 1][unit_id].get_name() == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Biovore Spore Launcher":
                    area_effect += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Doomsday Ark":
            area_effect += self.count_non_necron_factions()
        if self.get_ability_given_pos(planet_id, unit_id) == "Nightshade Interceptor":
            if self.warlord_faction != "Eldar":
                area_effect += 2
        return area_effect

    def optimized_protocol_check(self):
        if self.search_hand_for_card("Optimized Protocol"):
            return True
        elif self.search_for_card_everywhere("Harbinger of Eternity") \
                and self.search_discard_for_card("Optimized Protocol"):
            return True
        return False

    def surrogate_host_check(self):
        if self.search_hand_for_card("Surrogate Host"):
            return True
        elif self.search_for_card_everywhere("Harbinger of Eternity") \
                and self.search_discard_for_card("Surrogate Host"):
            return True
        return False

    def necrodermis_check(self):
        if self.search_hand_for_card("Necrodermis"):
            return True
        elif self.search_for_card_everywhere("Harbinger of Eternity") \
                and self.search_discard_for_card("Necrodermis"):
            return True
        return False

    def get_resources(self):
        return self.resources

    def resolve_additional_warlord_after_commit_effects(self, planet_pos):
        other_player = self.get_other_player()
        if other_player.check_for_warlord(planet_pos, card_effect=True, searching_name=self.name_player):
            if self.search_hand_for_card("Primal Howl"):
                if not self.primal_howl_used:
                    self.game.create_reaction("Primal Howl", self.name_player, (self.number, -1, -1))

    def resolve_enemy_warlord_committed_to_planet(self, planet_pos):
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            for j in range(len(self.cards_in_play[planet_pos + 1][i].get_attachments())):
                if self.cards_in_play[planet_pos + 1][i].get_attachments()[j].get_ability() == "Blacksun Filter":
                    owner = self.cards_in_play[planet_pos + 1][i].get_attachments()[j].name_owner
                    self.game.create_reaction("Blacksun Filter", owner, (int(self.number), planet_pos, i))
            if self.cards_in_play[planet_pos + 1][i].get_ability() == "Blood Claw Pack":
                if self.get_ready_given_pos(planet_pos, i):
                    self.game.create_reaction("Blood Claw Pack", self.name_player,
                                              (int(self.number), planet_pos, i))
        if len(self.cards_in_play[planet_pos + 1]) == 1:
            if planet_pos != 0:
                for i in range(len(self.cards_in_play[planet_pos])):
                    if self.get_ability_given_pos(planet_pos - 1, i) == "Thunderwolf Cavalry":
                        if not self.check_if_already_have_reaction("Thunderwolf Cavalry"):
                            self.game.create_reaction("Thunderwolf Cavalry", self.name_player,
                                                      (int(self.number), planet_pos, -1))
            if planet_pos != 6:
                for i in range(len(self.cards_in_play[planet_pos + 2])):
                    if self.get_ability_given_pos(planet_pos + 1, i) == "Thunderwolf Cavalry":
                        if not self.check_if_already_have_reaction("Thunderwolf Cavalry"):
                            self.game.create_reaction("Thunderwolf Cavalry", self.name_player,
                                                      (int(self.number), planet_pos, -1))


    def does_own_interrupt_exist(self, reaction_name):
        for i in range(len(self.game.interrupts_waiting_on_resolution)):
            if self.game.interrupts_waiting_on_resolution[i] == reaction_name:
                if self.game.player_resolving_interrupts[i] == self.name_player:
                    return True
        return False

    def does_own_positioned_reaction_exist(self, reaction_name, planet_pos, unit_pos):
        for i in range(len(self.game.reactions_needing_resolving)):
            if self.game.reactions_needing_resolving[i] == reaction_name:
                if self.game.player_who_resolves_reaction[i] == self.name_player:
                    if self.game.positions_of_unit_triggering_reaction[i] == (int(self.number), planet_pos, unit_pos):
                        return True
        return False

    def does_own_reaction_exist(self, reaction_name):
        for i in range(len(self.game.reactions_needing_resolving)):
            if self.game.reactions_needing_resolving[i] == reaction_name:
                if self.game.player_who_resolves_reaction[i] == self.name_player:
                    return True
        return False

    def get_brutal_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return False
        card = self.cards_in_play[planet_id + 1][unit_id]
        if card.get_blanked():
            return False
        if card.get_ability() != "Nazdreg":
            nazdreg_check = self.search_card_at_planet(planet_id, "Nazdreg", bloodied_relevant=True)
            if nazdreg_check:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Frenzied Bloodthirster":
            if self.game.bloodthirst_active[planet_id]:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Champion of Khorne":
            if self.game.bloodthirst_active[planet_id]:
                return True
        if self.search_attachments_at_pos(planet_id, unit_id, "Khornate Chain Axe"):
            if self.game.bloodthirst_active[planet_id]:
                return True
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, "Focal Warrior"):
                return True
        return card.get_brutal()

    def get_attack_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            card = self.headquarters[unit_id]
            attack_value = card.get_attack()
            if card.get_ability() == "Praetorian Ancient":
                if self.count_units_in_discard() > 5:
                    attack_value += 2
            if card.get_ability() == "Cowardly Squig":
                attack_value = self.get_health_given_pos(planet_id, unit_id) -\
                               self.get_damage_given_pos(planet_id, unit_id)
                return attack_value
            if card.get_ability() == "Eloquent Confessor":
                if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                    attack_value += 1
            if card.get_ability() == "Cultist":
                if self.search_for_card_everywhere("Sivarla Soulbinder"):
                    attack_value += 1
            if card.get_ability() == "BLANKED" and card.get_traits() == "":
                if self.search_for_card_everywhere("Forge Master Dominus", bloodied_relevant=True):
                    attack_value += 1
            if card.get_ability() == "Neurotic Obliterator":
                attack_value += len(card.get_attachments())
            if card.get_ability() == "Amalgamated Devotee":
                attack_value += len(card.get_attachments())
            if card.get_ability() == "Pyrrhian Eternals":
                attack_value += self.discard.count("Pyrrhian Eternals")
            if self.get_ability_given_pos(planet_id, unit_id) == "Tenacious Novice Squad":
                if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                    attack_value += 1
            if card.get_ability() == "Shard of the Deceiver":
                attack_value += len(self.discard)
            if card.get_ability() == "Improbable Runt Machine":
                attack_value += min(len(card.get_attachments()), 3)
            if card.get_ability() == "Destroyer Cultist":
                attack_value += self.count_non_necron_factions()
            if card.get_ability() == "Phantasmatic Masque":
                attack_value += self.get_health_given_pos(planet_id, unit_id) - \
                                self.get_damage_given_pos(planet_id, unit_id)
            if card.get_ability() == "Virulent Plague Squad":
                attack_value = attack_value + self.game.request_number_of_enemy_units_in_discard(str(self.number))
            return attack_value
        card = self.cards_in_play[planet_id + 1][unit_id]
        if card.attack_set_eop != -1:
            return card.attack_set_eop
        other_player = self.game.p1
        if other_player.name_player == self.name_player:
            other_player = self.game.p2
        attack_value = card.get_attack()
        ability = self.get_ability_given_pos(planet_id, unit_id)
        if card.get_name() == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Strangler Brood":
                    attack_value += 1
        if card.get_card_type() == "Warlord":
            found_praetorian_shadow = False
            if self.game.planet_array[planet_id] == "Chiros The Great Bazaar":
                attack_value += 1
            if self.search_card_at_planet(planet_id, "Praetorian Shadow"):
                found_praetorian_shadow = True
            if not found_praetorian_shadow and planet_id != 0:
                if self.search_card_at_planet(planet_id - 1, "Praetorian Shadow"):
                    found_praetorian_shadow = True
            if not found_praetorian_shadow and planet_id != 6:
                if self.search_card_at_planet(planet_id + 1, "Praetorian Shadow"):
                    found_praetorian_shadow = True
            if found_praetorian_shadow:
                attack_value += 1
        elif card.get_card_type() in ["Army", "Token"]:
            for i in range(len(other_player.cards_in_play[planet_id + 1])):
                if other_player.get_ready_given_pos(planet_id, i):
                    if other_player.search_attachments_at_pos(planet_id, i, "Imposing Presence"):
                        attack_value = attack_value - 1
        if ability == "Cowardly Squig":
            attack_value = self.get_health_given_pos(planet_id, unit_id) - \
                           self.get_damage_given_pos(planet_id, unit_id)
            return attack_value
        if ability == "Repurposed Pariah":
            attack_value += self.count_units_with_trait_at_planet("Psyker", planet_id)
        if ability == "Immature Squig":
            for j in range(len(self.cards_in_play[planet_id + 1])):
                if j != unit_id:
                    if self.check_for_trait_given_pos(planet_id, j, "Squig"):
                        attack_value += 1
        if ability == "Shard of the Deceiver":
            attack_value += len(self.discard)
        if ability != "Knight Paladin Voris":
            if self.search_card_at_planet(planet_id, "Knight Paladin Voris"):
                attack_value += 1
        if ability == "BLANKED" and card.get_traits() == "":
            if self.search_for_card_everywhere("Forge Master Dominus", bloodied_relevant=True):
                attack_value += 1
        if ability == "Ireful Vanguard":
            warlord_pla, warlord_pos = self.get_location_of_warlord()
            if self.get_bloodied_given_pos(warlord_pla, warlord_pos):
                attack_value += 1
            else:
                other_player = self.get_other_player()
                warlord_pla, warlord_pos = other_player.get_location_of_warlord()
                if other_player.get_bloodied_given_pos(warlord_pla, warlord_pos):
                    attack_value += 1
        if ability == "Holy Battery":
            if self.search_faith_at_planet(planet_id):
                attack_value += 1
        if ability == "Cultist":
            if self.search_for_card_everywhere("Sivarla Soulbinder"):
                attack_value += 1
        if ability == "Neurotic Obliterator":
            attack_value += len(card.get_attachments())
        if ability == "Amalgamated Devotee":
            attack_value += len(card.get_attachments())
        if ability == "Kabal of the Ebon Law":
            if planet_id != self.game.round_number:
                attack_value += 1
        if ability == "Tenacious Novice Squad":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                attack_value += 1
        if ability == "Aurora Predator":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                attack_value += 3
        if ability == "Eloquent Confessor":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                attack_value += 1
        if ability == "Hjorvath Coldstorm":
            if self.check_for_enemy_warlord(planet_id, True, self.name_player):
                attack_value = attack_value - 2
        if ability == "Galvax the Bloated":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.check_for_trait_given_pos(planet_id, i, "Cultist"):
                    attack_value += 1
        if ability == "Phantasmatic Masque":
            attack_value += self.get_health_given_pos(planet_id, unit_id) - \
                            self.get_damage_given_pos(planet_id, unit_id)
        if self.check_for_trait_given_pos(planet_id, unit_id, "Sautekh"):
            for i in range(len(self.attachments_at_planet[planet_id])):
                if self.attachments_at_planet[planet_id][i].get_ability() == "Supreme Strategist":
                    attack_value += 1
        if self.get_cost_given_pos(planet_id, unit_id) > 2:
            for i in range(len(self.attachments_at_planet[planet_id])):
                if self.attachments_at_planet[planet_id][i].get_ability() == "Close Quarters Doctrine":
                    attack_value = attack_value - 1
            for i in range(len(other_player.attachments_at_planet[planet_id])):
                if other_player.attachments_at_planet[planet_id][i].get_ability() == "Close Quarters Doctrine":
                    attack_value = attack_value - 1
        if self.check_for_trait_given_pos(planet_id, unit_id, "Vostroya"):
            if self.search_card_in_hq("Cardinal Agra Decree"):
                if self.check_if_control_faith():
                    attack_value += 1
        if card.get_faction() != "Necrons" and card.check_for_a_trait("Warrior"):
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Immortal Vanguard":
                    attack_value += 1
        if ability == "Improbable Runt Machine":
            attack_value += min(len(card.get_attachments()), 3)
        if ability == "Praetorian Ancient":
            if self.count_units_in_discard() > 5:
                attack_value += 2
        if ability == "Pyrrhian Eternals":
            attack_value += self.discard.count("Pyrrhian Eternals")
        if ability == "Destroyer Cultist":
            attack_value += self.count_non_necron_factions()
        if ability != "Colonel Straken":
            straken_check = self.search_card_at_planet(planet_id, "Colonel Straken", bloodied_relevant=True)
            if straken_check:
                if card.check_for_a_trait("Soldier") or card.check_for_a_trait("Warrior"):
                    attack_value += 1
        if self.check_for_trait_given_pos(planet_id, unit_id, "Warrior"):
            if self.search_card_at_planet(planet_id, "Talyesin Fharenal"):
                if self.check_if_trait_at_planet(planet_id, "Psyker"):
                    attack_value += 1
        elif self.check_for_trait_given_pos(planet_id, unit_id, "Psyker"):
            if self.search_card_at_planet(planet_id, "Talyesin Fharenal"):
                if self.check_if_trait_at_planet(planet_id, "Warrior"):
                    attack_value += 1
        if ability == "Auxiliary Overseer":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.get_faction_given_pos(planet_id, i) != "Tau":
                    attack_value += 1
        if ability == "Goff Boyz":
            if self.game.round_number == planet_id:
                attack_value = attack_value + 3
        if ability in self.plus_two_atk_if_warlord:
            if self.check_for_warlord(planet_id, True, self.name_player):
                attack_value += 2
            else:
                if self.number == "1":
                    if self.game.p2.check_for_warlord(planet_id, True, self.name_player):
                        attack_value += 2
                elif self.number == "2":
                    if self.game.p1.check_for_warlord(planet_id, True, self.name_player):
                        attack_value += 2
        if ability == "Baharroth's Hawks":
            if self.check_for_warlord(planet_id, True, self.name_player):
                attack_value += 3
        if self.get_faction_given_pos(planet_id, unit_id) == "Orks" and \
                self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
            if self.search_card_in_hq("Kustomisation Station"):
                attack_value += 1
        if self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
            if self.search_card_at_planet(planet_id, "Baddfrag"):
                attack_value += 1
        if self.get_faction_given_pos(planet_id, unit_id) == "Astra Militarum" and \
                self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
            if self.get_has_faith_given_pos(planet_id, unit_id):
                if self.search_card_in_hq("Dominus' Forge"):
                    attack_value += 1
        if ability == "Gorzod's Wagons":
            if self.get_enemy_has_init_for_cards(planet_id, unit_id):
                attack_value += 2
        if ability == "Fire Warrior Grenadiers":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.check_for_trait_given_pos(planet_id, i, "Ethereal"):
                    attack_value += 2
        if ability == "Sacaellum Shrine Guard" or ability == "Saim-Hann Kinsman":
            if self.game.get_green_icon(planet_id):
                attack_value += 1
        if ability == "Virulent Plague Squad":
            attack_value = attack_value + self.game.request_number_of_enemy_units_in_discard(str(self.number))
        if ability == "Infantry Conscripts":
            support_count = 0
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_card_type() == "Support":
                    support_count += 1
            attack_value += support_count * 2
        attachments = card.get_attachments()
        condition_present = False
        for i in range(len(attachments)):
            if attachments[i].get_ability() == "Adaptative Thorax Swarm" and not attachments[i].from_magus_harid:
                if attachments[i].name_owner == self.name_player:
                    attack_value += len(self.victory_display)
                else:
                    other_player = self.get_other_player()
                    attack_value += len(other_player.victory_display)
            if attachments[i].check_for_a_trait("Condition"):
                condition_present = True
            if attachments[i].get_ability() == "Agonizer of Bren":
                attack_value += self.count_copies_in_play("Khymera")
            if attachments[i].get_ability() == "Necklace of Teef":
                attack_value += attachments[i].get_counter()
            if attachments[i].get_ability() == "Speed Freakz Warpaint":
                if self.get_enemy_has_init_for_cards(planet_id, unit_id):
                    attack_value += 3
            if attachments[i].get_ability() == "Medallion of Betrayal":
                if self.check_for_trait_given_pos(planet_id, unit_id, "Cultist"):
                    attack_value += 1
            if attachments[i].get_ability() == "Noxious Fleshborer" and not attachments[i].from_magus_harid:
                if self.game.infested_planets[planet_id]:
                    attack_value += 1
            if attachments[i].get_ability() == "Frostfang":
                if self.number == "1":
                    if self.game.p2.check_for_warlord(planet_id, True, self.name_player):
                        attack_value += 2
                elif self.number == "2":
                    if self.game.p1.check_for_warlord(planet_id, True, self.name_player):
                        attack_value += 2
            if attachments[i].get_ability() == "Imperial Power Fist":
                if len(self.cards_in_play[planet_id + 1]) > 1:
                    other_ready_unit_present = False
                    for j in range(len(self.cards_in_play[planet_id + 1])):
                        if j != unit_id:
                            if self.get_ready_given_pos(planet_id, j):
                                other_ready_unit_present = True
                    if not other_ready_unit_present:
                        attack_value += 5
        if condition_present:
            for i in range(len(other_player.cards_in_play[planet_id + 1])):
                if other_player.get_ability_given_pos(planet_id, i) == "Swarming Rippers":
                    attack_value = attack_value - 1
        if self.get_faction_given_pos(planet_id, unit_id) == "Astra Militarum":
            if self.get_ability_given_pos(planet_id, unit_id) != "Broderick Worr":
                if self.game.get_green_icon(planet_id):
                    if self.search_for_card_everywhere("Broderick Worr"):
                        attack_value += 1
        if card.get_faction() == "Tau":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if i != unit_id:
                    if self.search_attachments_at_pos(planet_id, i, "Honor Blade"):
                        attack_value += 1
        if self.get_brutal_given_pos(planet_id, unit_id):
            attack_value = attack_value + card.get_damage()
        return attack_value

    def get_most_termagants_at_single_planet(self):
        num_copies = 0
        current_num = 0
        for i in range(7):
            current_num = self.count_copies_at_planet(i, "Termagant")
            if current_num > num_copies:
                num_copies = current_num
        return num_copies

    def count_copies_in_play(self, card_name, ability=False):
        num_copies = 0
        for i in range(7):
            num_copies += self.count_copies_at_planet(planet_num=i, card_name=card_name, ability=ability)
        num_copies += self.count_copies_at_hq(card_name, ability=ability)
        return num_copies

    def count_copies_at_planet(self, planet_num, card_name, ability=False):
        num_copies = 0
        for i in range(len(self.cards_in_play[planet_num + 1])):
            if ability:
                if self.cards_in_play[planet_num + 1][i].get_ability() == card_name:
                    num_copies += 1
            elif self.cards_in_play[planet_num + 1][i].get_name() == card_name:
                num_copies += 1
        return num_copies

    def count_units_in_discard(self):
        count = 0
        for i in range(len(self.discard)):
            card = FindCard.find_card(self.discard[i], self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            if card.get_card_type() == "Army":
                count = count + 1
        return count

    def count_copies_at_hq(self, card_name, ability=False):
        num_copies = 0
        for i in range(len(self.headquarters)):
            if ability:
                if self.headquarters[i].get_ability() == card_name:
                    num_copies += 1
            elif self.headquarters[i].get_name() == card_name:
                num_copies += 1
        return num_copies

    def search_ready_unique_unit(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit() and self.headquarters[i].get_ready() and \
                    self.headquarters[i].get_unique():
                return True
        for j in range(7):
            for k in range(len(self.cards_in_play[j + 1])):
                if self.cards_in_play[j + 1][k].get_ready() and self.cards_in_play[j + 1][k].get_unique():
                    return True
        return False

    def set_vow_of_honor(self, planet_pos, unit_pos, value):
        if planet_pos == -2:
            self.headquarters[unit_pos].valid_target_vow_of_honor = value
            return None
        self.cards_in_play[planet_pos + 1][unit_pos].valid_target_vow_of_honor = value
        return None

    def assign_damage_to_pos(self, planet_id, unit_id, damage, can_shield=True, att_pos=None, is_reassign=False,
                             context="", preventable=True, shadow_field_possible=False, rickety_warbuggy=False,
                             by_enemy_unit=True):
        other_player = self.get_other_player()
        if planet_id == -2:
            return self.assign_damage_to_pos_hq(unit_id, damage, can_shield=can_shield)
        if shadow_field_possible:
            if self.search_attachments_at_pos(planet_id, unit_id, "Shadow Field"):
                return False, 0
            if self.check_for_trait_given_pos(planet_id, unit_id, "Daemon"):
                if self.the_princes_might_active[planet_id]:
                    return False, 0
        if att_pos is None:
            if self.get_ability_given_pos(planet_id, unit_id) == "Exalted Celestians":
                if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                    return False, 0
        if rickety_warbuggy:
            if self.get_ability_given_pos(planet_id, unit_id) == "Rickety Warbuggy":
                if self.get_enemy_has_init_for_cards(planet_id, unit_id):
                    any_non_warbuggies = False
                    for i in range(len(self.cards_in_play[planet_id + 1])):
                        if self.get_card_type_given_pos(planet_id, i) == "Army":
                            if self.get_name_given_pos(planet_id, i) != "Rickety Warbuggy":
                                any_non_warbuggies = True
                    if any_non_warbuggies:
                        return False, 0
        prior_damage = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        zara_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_id,
                                                                       "Zarathur, High Sorcerer",
                                                                       bloodied_relevant=True)
        bodyguard_damage_list = []
        for i in range(len(self.cards_in_play[planet_id + 1][unit_id].get_attachments())):
            if self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].get_ability() == "Until Justice is Done":
                damage += 1
        if damage > 0:
            for i in range(len(self.cards_in_play[planet_id + 1][unit_id].get_attachments())):
                if self.cards_in_play[planet_id + 1][unit_id].get_attachments()[
                        i].get_ability() == "Flickering Holosuit":
                    if self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].get_ready():
                        self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].exhaust_card()
                        damage = damage - 2
                    else:
                        self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].ready_card()
        og_damage = damage
        too_many_bodyguards = False
        if att_pos is not None:
            if damage > 0:
                if "Until Justice is Done" in self.cards:
                    if self.check_for_trait_given_pos(planet_id, unit_id, "Ecclesiarchy"):
                        self.game.create_reaction("Until Justice is Done", self.name_player, att_pos)
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if i != unit_id:
                    print("Get attachments")
                    for j in range(len(self.cards_in_play[planet_id + 1][i].get_attachments())):
                        print("Bodyguard check")
                        if self.cards_in_play[planet_id + 1][i].get_attachments()[j].get_ability() == "Bodyguard":
                            print("Bodyguard found")
                            if damage > 0:
                                damage = damage - 1
                                bodyguard_damage_list.append(i)
                            elif damage <= 0:
                                bodyguard_damage_list.append(i)
                                too_many_bodyguards = True
        if too_many_bodyguards:
            too_many_bodyguards = False
            unique_bodyguards = []
            for i in range(len(bodyguard_damage_list)):
                already_bodyguard = False
                for j in range(len(unique_bodyguards)):
                    if bodyguard_damage_list[i] == unique_bodyguards[j]:
                        already_bodyguard = True
                if not already_bodyguard:
                    unique_bodyguards.append(bodyguard_damage_list[i])
            if len(unique_bodyguards) > 1:
                too_many_bodyguards = True
            self.game.num_bodyguards = len(unique_bodyguards)
        if too_many_bodyguards:
            self.game.body_guard_positions = bodyguard_damage_list
            self.game.name_player_manual_bodyguard = self.name_player
            self.game.manual_bodyguard_resolution = True
            self.game.planet_bodyguard = planet_id
            self.game.damage_bodyguard = og_damage
            return False, len(bodyguard_damage_list)
        if zara_check and damage > 0:
            if not other_player.hit_by_gorgul:
                damage += 1
        if self.search_attachments_at_pos(planet_id, unit_id, "Heavy Marker Drone"):
            damage = damage * 2
        if damage > 3:
            if self.search_attachments_at_pos(planet_id, unit_id, "Armour of Saint Katherine"):
                damage = 3
        damage_on_card_before = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        if damage < 0:
            damage = 0
        self.cards_in_play[planet_id + 1][unit_id].damage_card(self, damage, can_shield)
        damage_on_card_after = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        total_damage_that_can_be_blocked = damage_on_card_after - prior_damage
        self.cards_in_play[planet_id + 1][unit_id].recently_assigned_damage = True
        if total_damage_that_can_be_blocked > 0:
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                for i in range(len(self.headquarters)):
                    if self.get_ability_given_pos(-2, i) == "Prognosticator":
                        if not self.get_once_per_round_used_given_pos(-2, i):
                            if not self.check_if_already_have_interrupt_of_position("Prognosticator", -2, i):
                                self.game.create_interrupt("Prognosticator", self.name_player,
                                                           (int(self.number), -2, i))
                for i in range(7):
                    for j in range(len(self.cards_in_play[i + 1])):
                        if self.get_ability_given_pos(i, j) == "Prognosticator":
                            if not self.get_once_per_round_used_given_pos(i, j):
                                if not self.check_if_already_have_interrupt_of_position("Prognosticator", i, j):
                                    self.game.create_interrupt("Prognosticator", self.name_player,
                                                               (int(self.number), i, j))
            if self.get_unstoppable_given_pos(planet_id, unit_id):
                if not self.cards_in_play[planet_id + 1][unit_id].once_per_round_used:
                    self.cards_in_play[planet_id + 1][unit_id].once_per_round_used = True
                    if preventable:
                        self.cards_in_play[planet_id + 1][unit_id].set_damage(damage_on_card_after - 1)
                        total_damage_that_can_be_blocked = total_damage_that_can_be_blocked - 1
                        damage_on_card_after = damage_on_card_after - 1
                        if self.get_ability_given_pos(planet_id, unit_id) == "Righteous Initiate":
                            self.cards_in_play[planet_id + 1][unit_id].extra_attack_until_end_of_phase += 2
                        if self.get_ability_given_pos(planet_id, unit_id) == "Brotherhood Justicar":
                            self.increase_faith_given_pos(planet_id, unit_id, 1)
                        if self.get_ability_given_pos(planet_id, unit_id) == "Dutiful Castellan":
                            self.game.create_reaction("Dutiful Castellan", self.name_player,
                                                      (int(self.number), planet_id, unit_id))
                        if self.get_ability_given_pos(planet_id, unit_id) == "Sword Brethren Dreadnought":
                            self.game.create_reaction("Sword Brethren Dreadnought", self.name_player,
                                                      (int(self.number), planet_id, unit_id))
                        if self.get_ability_given_pos(planet_id, unit_id) == "Steadfast Sword Brethren":
                            self.game.create_reaction("Steadfast Sword Brethren", self.name_player,
                                                      (int(self.number), planet_id, unit_id))
                        if self.get_ability_given_pos(planet_id, unit_id) == "Wrathful Dreadnought":
                            self.game.create_reaction("Wrathful Dreadnought", self.name_player,
                                                      (int(self.number), planet_id, unit_id))
                        if self.get_ability_given_pos(planet_id, unit_id) == "Fighting Company Daras":
                            self.increase_retaliate_given_pos_eop(planet_id, unit_id, 2)
                        if self.get_ability_given_pos(planet_id, unit_id) == "Reclusiam Templars":
                            self.ready_given_pos(planet_id, unit_id)
            for i in range(len(self.cards_in_play[planet_id + 1][unit_id].get_attachments())):
                if self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].\
                        get_ability() == "Ancient Crozius Arcanum":
                    if not self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].once_per_round_used:
                        self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].once_per_round_used = True
                        if damage_on_card_before > 0:
                            self.remove_damage_from_pos(planet_id, unit_id, 1, healing=True)
                            damage_on_card_before = damage_on_card_before - 1
                            damage_on_card_after = damage_on_card_after - 1
                        if total_damage_that_can_be_blocked > 0:
                            self.cards_in_play[planet_id + 1][unit_id].set_damage(damage_on_card_after - 1)
                            total_damage_that_can_be_blocked = total_damage_that_can_be_blocked - 1
                            damage_on_card_after = damage_on_card_after - 1
        for i in range(len(bodyguard_damage_list)):
            self.assign_damage_to_pos(planet_id, bodyguard_damage_list[i], 1, is_reassign=True, can_shield=False)
        if damage_on_card_after > damage_on_card_before:
            if att_pos is not None:
                for i in range(len(other_player.cards_in_play[planet_id + 1])):
                    if other_player.search_attachments_at_pos(planet_id, i, "Data Analyzer"):
                        self.game.create_interrupt("Data Analyzer Aggressive", other_player.name_player,
                                                   (int(self.number), planet_id, unit_id))
            if self.get_card_type_given_pos(planet_id, unit_id) == "Warlord":
                if self.check_if_card_is_destroyed(planet_id, unit_id):
                    if not self.check_if_already_have_interrupt("Cajivak the Hateful"):
                        if self.search_hand_for_card("Cajivak the Hateful"):
                            self.game.create_interrupt("Cajivak the Hateful", self.name_player,
                                                       (int(self.number), -1, -1))
            if by_enemy_unit and not is_reassign:
                for i in range(len(self.cards_in_play[planet_id + 1])):
                    if self.get_ability_given_pos(planet_id, i) == "Avenging Squad":
                        if i != unit_id:
                            self.game.create_reaction("Avenging Squad", self.name_player,
                                                      (int(self.number), planet_id, i))
            if not self.game.positions_of_units_to_take_damage:
                self.set_aiming_reticle_in_play(planet_id, unit_id, "red")
            else:
                self.set_aiming_reticle_in_play(planet_id, unit_id, "blue")
            self.game.damage_on_units_list_before_new_damage.append(prior_damage)
            self.game.damage_is_preventable.append(preventable)
            self.game.positions_of_units_to_take_damage.append((int(self.number), planet_id, unit_id))
            self.game.damage_can_be_shielded.append(can_shield)
            self.game.positions_attackers_of_units_to_take_damage.append(att_pos)
            self.game.card_names_triggering_damage.append(context)
            self.game.amount_that_can_be_removed_by_shield.append(total_damage_that_can_be_blocked)
            return True, len(bodyguard_damage_list)
        return False, len(bodyguard_damage_list)

    def discard_attachment_name_from_card(self, planet_pos, unit_pos, name):
        i = 0
        if planet_pos == -2:
            while i < len(self.headquarters[unit_pos].get_attachments()):
                if self.headquarters[unit_pos].get_attachments()[i].get_name() == name:
                    if self.headquarters[unit_pos].get_attachments()[i].name_owner == self.game.name_1:
                        self.game.p1.add_card_to_discard(self.headquarters[unit_pos].get_attachments()[0].get_name())
                    else:
                        self.game.p2.add_card_to_discard(self.headquarters[unit_pos].get_attachments()[0].get_name())
                    del self.headquarters[unit_pos].get_attachments()[i]
                    i = i - 1
                i = i + 1
            return None
        while i < len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()):
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_name() == name:
                if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].name_owner ==\
                        self.game.name_1:
                    self.game.p1.add_card_to_discard(
                        self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_name())
                else:
                    self.game.p2.add_card_to_discard(
                        self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_name())
                del self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i]
                i = i - 1
            i = i + 1
        return None

    def discard_attachment_at_pos(self, planet_pos, unit_pos, attachment_pos):
        if planet_pos == -2:
            name_attachment = self.headquarters[unit_pos].get_attachments()[attachment_pos].get_name()
            name_owner = self.headquarters[unit_pos].get_attachments()[attachment_pos].name_owner
            if name_owner == self.game.name_1:
                self.game.p1.add_card_to_discard(name_attachment)
            else:
                self.game.p2.add_card_to_discard(name_attachment)
            if name_attachment == "Savage Parasite":
                self.game.create_interrupt("Savage Parasite", name_owner, (int(self.number), -1, -1))
            del self.headquarters[unit_pos].get_attachments()[attachment_pos]
            return None
        name_attachment = self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_name()
        name_owner = self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].name_owner
        if name_owner == self.game.name_1:
            if self.game.p1.search_card_at_planet(planet_pos, "Fairly 'Quipped Kommando"):
                self.game.create_interrupt("Fairly 'Quipped Kommando", self.game.p1.name_player,
                                           (1, -1, -1), extra_info=name_attachment)
            self.game.p1.add_card_to_discard(name_attachment)
        else:
            if self.game.p2.search_card_at_planet(planet_pos, "Fairly 'Quipped Kommando"):
                self.game.create_interrupt("Fairly 'Quipped Kommando", self.game.p2.name_player,
                                           (2, -1, -1), extra_info=name_attachment)
            self.game.p2.add_card_to_discard(name_attachment)
        if name_attachment == "Savage Parasite":
            self.game.create_interrupt("Savage Parasite", name_owner, (int(self.number), -1, -1))
        if name_attachment == "Fusion Cascade Defiance":
            self.game.create_reaction("Fusion Cascade Defiance", name_owner,
                                      (int(self.number), planet_pos, -1))
        del self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
        return None

    def count_attachments_controlled(self):
        attachments_count = 0
        for i in range(len(self.headquarters)):
            for j in range(len(self.headquarters[i].get_attachments())):
                if self.headquarters[i].get_attachments()[j].name_owner == self.name_player:
                    attachments_count += 1
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                for k in range(len(self.cards_in_play[i + 1][j].get_attachments())):
                    if self.cards_in_play[i + 1][j].get_attachments()[k].name_owner == self.name_player:
                        attachments_count += 1
        other_player = self.get_other_player()
        for i in range(len(other_player.headquarters)):
            for j in range(len(other_player.headquarters[i].get_attachments())):
                if other_player.headquarters[i].get_attachments()[j].name_owner == self.name_player:
                    attachments_count += 1
        for i in range(7):
            for j in range(len(other_player.cards_in_play[i + 1])):
                for k in range(len(other_player.cards_in_play[i + 1][j].get_attachments())):
                    if other_player.cards_in_play[i + 1][j].get_attachments()[k].name_owner == self.name_player:
                        attachments_count += 1
        return attachments_count

    def discard_attachments_from_card(self, planet_pos, unit_pos):
        if planet_pos == -2:
            while self.headquarters[unit_pos].get_attachments():
                self.discard_attachment_at_pos(planet_pos, unit_pos, 0)
            return None
        while self.cards_in_play[planet_pos + 1][unit_pos].get_attachments():
            self.discard_attachment_at_pos(planet_pos, unit_pos, 0)
        return None

    def increase_indirect_damage_at_pos(self, planet_pos, card_pos, amount):
        if planet_pos == -2:
            if self.headquarters[card_pos].get_is_unit():
                if self.get_health_given_pos(planet_pos, card_pos) <= \
                        self.headquarters[card_pos].get_indirect_and_direct_damage():
                    return False
                self.headquarters[card_pos].increase_not_yet_assigned_damage(amount)
                self.indirect_damage_applied += 1
                return True
            return False
        if self.cards_in_play[planet_pos + 1][card_pos].get_is_unit():
            if self.get_health_given_pos(planet_pos, card_pos) <= \
                    self.cards_in_play[planet_pos + 1][card_pos].get_indirect_and_direct_damage():
                return False
            self.cards_in_play[planet_pos + 1][card_pos].increase_not_yet_assigned_damage(amount)
            self.indirect_damage_applied += 1
            return True
        return False

    def exhaust_attachment_name_pos(self, planet_pos, unit_pos, name):
        if planet_pos == -2:
            self.headquarters[unit_pos].exhaust_first_attachment_name(name)
            return None
        self.cards_in_play[planet_pos + 1][unit_pos].exhaust_first_attachment_name(name)
        return None

    def assign_damage_to_pos_hq(self, unit_id, damage, can_shield=True, context="", preventable=True):
        if self.get_ability_given_pos(-2, unit_id) == "Exalted Celestians":
            if self.get_has_faith_given_pos(-2, unit_id) > 0:
                return False
        if damage > 0:
            for i in range(len(self.headquarters[unit_id].get_attachments())):
                if self.headquarters[unit_id].get_attachments()[i].get_ability() == "Flickering Holosuit":
                    if self.headquarters[unit_id].get_attachments()[i].get_ready():
                        self.headquarters[unit_id].get_attachments()[i].exhaust_card()
                        damage = damage - 2
                    else:
                        self.headquarters[unit_id].get_attachments()[i].ready_card()
        prior_damage = self.headquarters[unit_id].get_damage()
        damage_too_great = self.headquarters[unit_id].damage_card(self, damage, can_shield)
        afterwards_damage = self.headquarters[unit_id].get_damage()
        total_that_can_be_blocked = afterwards_damage - prior_damage
        if total_that_can_be_blocked > 0:
            if self.get_unstoppable_given_pos(-2, unit_id):
                if not self.headquarters[unit_id].once_per_round_used:
                    self.headquarters[unit_id].once_per_round_used = True
                    self.headquarters[unit_id].set_damage(afterwards_damage - 1)
                    total_that_can_be_blocked = total_that_can_be_blocked - 1
                    afterwards_damage = afterwards_damage - 1
                    if self.get_ability_given_pos(-2, unit_id) == "Righteous Initiate":
                        self.headquarters[unit_id].extra_attack_until_end_of_phase += 2
                    if self.get_ability_given_pos(-2, unit_id) == "Steadfast Sword Brethren":
                        self.game.create_reaction("Steadfast Sword Brethren", self.name_player,
                                                  (int(self.number), -2, unit_id))
                    if self.get_ability_given_pos(-2, unit_id) == "Brotherhood Justicar":
                        self.increase_faith_given_pos(-2, unit_id, 1)
                    if self.get_ability_given_pos(-2, unit_id) == "Wrathful Dreadnought":
                        self.game.create_reaction("Wrathful Dreadnought", self.name_player,
                                                  (int(self.number), -2, unit_id))
                    if self.get_ability_given_pos(-2, unit_id) == "Fighting Company Daras":
                        self.increase_retaliate_given_pos_eop(-2, unit_id, 2)
        if total_that_can_be_blocked > 0:
            if self.get_card_type_given_pos(-2, unit_id) == "Warlord":
                if self.check_if_card_is_destroyed(-2, unit_id):
                    if not self.check_if_already_have_interrupt("Cajivak the Hateful"):
                        if self.search_hand_for_card("Cajivak the Hateful"):
                            self.game.create_interrupt("Cajivak the Hateful", self.name_player,
                                                       (int(self.number), -1, -1))
            if not self.game.positions_of_units_to_take_damage:
                self.set_aiming_reticle_in_play(-2, unit_id, "red")
            else:
                self.set_aiming_reticle_in_play(-2, unit_id, "blue")
            self.game.damage_on_units_list_before_new_damage.append(prior_damage)
            self.game.damage_is_preventable.append(preventable)
            self.game.positions_of_units_to_take_damage.append((int(self.number), -2, unit_id))
            self.game.damage_can_be_shielded.append(can_shield)
            self.game.positions_attackers_of_units_to_take_damage.append(None)
            self.game.card_names_triggering_damage.append(context)
            self.game.amount_that_can_be_removed_by_shield.append(total_that_can_be_blocked)
        return damage_too_great

    def search_discard_for_card(self, card_name):
        if card_name in self.discard:
            return True
        return False

    def suffer_area_effect(self, planet_id, amount, faction="", shadow_field_possible=False, rickety_warbuggy=False,
                           actual_area_effect=False):
        for i in range(len(self.cards_in_play[planet_id + 1])):
            genestealer_hybrids_relevant = False
            if actual_area_effect:
                if self.search_card_in_hq("Hive Fleet Leviathan"):
                    amount = min(1, amount)
                for j in range(len(self.cards_in_play[planet_id + 1])):
                    if self.get_ability_given_pos(planet_id, j) == "Genestealer Hybrids" and i != j:
                        genestealer_hybrids_relevant = True
            if not genestealer_hybrids_relevant:
                if self.get_ability_given_pos(planet_id, i) not in self.game.units_immune_to_aoe:
                    self.assign_damage_to_pos(planet_id, i, amount, context=faction,
                                              shadow_field_possible=shadow_field_possible,
                                              rickety_warbuggy=rickety_warbuggy)

    def suffer_area_effect_at_hq(self, amount):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_card_type() != "Support":
                self.assign_damage_to_pos_hq(i, amount)

    def get_number_of_units_at_planet(self, planet_id):
        return len(self.cards_in_play[planet_id + 1])

    def check_if_trait_at_planet(self, planet_id, trait):
        if planet_id == -2:
            for i in range(len(self.headquarters)):
                if self.check_for_trait_given_pos(-2, i, trait):
                    return True
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.check_for_trait_given_pos(planet_id, i, trait):
                return True
        return False

    def check_if_control_trait(self, trait):
        if self.check_if_trait_at_planet(-2, trait):
            return True
        for i in range(7):
            if self.check_if_trait_at_planet(i, trait):
                return True
        return False

    def get_other_player(self):
        other_player = self.game.p1
        if other_player.name_player == self.name_player:
            other_player = self.game.p2
        return other_player

    def get_bloodied_given_pos(self, planet_id, unit_id):
        if self.get_card_type_given_pos(planet_id, unit_id) != "Warlord":
            return False
        if planet_id == -2:
            return self.headquarters[unit_id].get_bloodied()
        return self.cards_in_play[planet_id + 1][unit_id]

    def get_health_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            health = self.headquarters[unit_id].get_health()
            if self.headquarters[unit_id].attack == 0:
                if self.search_card_in_hq("Wraithbone Armour"):
                    health += 1
            ability = self.get_ability_given_pos(planet_id, unit_id)
            if self.get_card_type_given_pos(planet_id, unit_id) == "Warlord":
                for i in range(len(self.victory_display)):
                    if self.victory_display[i].get_name() == "Daemon World Ivandis":
                        health += 2
                if self.search_card_in_hq("Ghosts of Cegorach"):
                    if self.check_if_all_units_have_trait("Harlequin"):
                        health += 3
            if ability == "BLANKED" and self.get_traits_given_pos(planet_id, unit_id) == "":
                if self.search_for_card_everywhere("Forge Master Dominus", bloodied_relevant=True):
                    health += 1
            if self.headquarters[unit_id].health_set_eop != -1:
                return self.headquarters[unit_id].health_set_eop
            if self.get_faction_given_pos(-2, unit_id) == "Orks":
                if self.get_card_type_given_pos(-2, unit_id) != "Token":
                    if self.search_card_in_hq("Mork's Great Heap"):
                        health += 1
            if ability == "Charging Juggernaut":
                if self.headquarters[unit_id].get_attachments():
                    health += 1
            if ability == "Lychguard Sentinel":
                if self.count_units_in_discard() > 5:
                    health += 4
            if ability == "Neurotic Obliterator":
                health += len(self.headquarters[unit_id].get_attachments())
            if ability == "Amalgamated Devotee":
                health += 2 * len(self.headquarters[unit_id].get_attachments())
            if ability == "Improbable Runt Machine":
                health += min(len(self.headquarters[unit_id].get_attachments()), 3)
            if ability == "Tenacious Novice Squad":
                if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                    health += 1
            if ability == "Ireful Vanguard":
                warlord_pla, warlord_pos = self.get_location_of_warlord()
                if self.get_bloodied_given_pos(warlord_pla, warlord_pos):
                    health += 1
                else:
                    other_player = self.get_other_player()
                    warlord_pla, warlord_pos = other_player.get_location_of_warlord()
                    if other_player.get_bloodied_given_pos(warlord_pla, warlord_pos):
                        health += 1
            if ability == "Fairly 'Quipped Kommando":
                health += len(self.headquarters[unit_id].get_attachments())
            if ability == "Cultist":
                if self.search_for_card_everywhere("Sivarla Soulbinder"):
                    health += 1
            if ability == "Pyrrhian Eternals":
                health += self.discard.count("Pyrrhian Eternals")
            if ability == "Shard of the Deceiver":
                health += len(self.discard)
            for i in range(len(self.headquarters[unit_id].get_attachments())):
                attachment = self.headquarters[unit_id].get_attachments()[i]
                if attachment.get_ability() == "Adaptative Thorax Swarm":
                    if attachment.name_owner == self.name_player:
                        health += len(self.victory_display)
                    else:
                        other_player = self.get_other_player()
                        health += len(other_player.victory_display)
                if attachment.get_ability() == "Medallion of Betrayal":
                    if self.check_for_trait_given_pos(planet_id, unit_id, "Cultist"):
                        health += 1
            return health
        health = self.cards_in_play[planet_id + 1][unit_id].get_health()
        if self.cards_in_play[planet_id + 1][unit_id].attack == 0:
            if self.search_card_in_hq("Wraithbone Armour"):
                health += 1
        ability = self.get_ability_given_pos(planet_id, unit_id)
        if self.get_card_type_given_pos(planet_id, unit_id) == "Warlord":
            for i in range(len(self.victory_display)):
                if self.victory_display[i].get_name() == "Daemon World Ivandis":
                    health += 2
            if self.search_card_in_hq("Ghosts of Cegorach"):
                if self.check_if_all_units_have_trait("Harlequin"):
                    health += 3
        if self.cards_in_play[planet_id + 1][unit_id].health_set_eop != -1:
            return self.cards_in_play[planet_id + 1][unit_id].health_set_eop
        card = self.cards_in_play[planet_id + 1][unit_id]
        if self.get_faction_given_pos(planet_id, unit_id) == "Orks" and \
                self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
            if self.search_card_in_hq("Kustomisation Station"):
                health += 1
        if card.get_has_hive_mind():
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_ability() == "Hive Fleet Kraken":
                    if self.headquarters[i].counter > 3:
                        if self.check_for_warlord(planet_id):
                            health += 1
                        elif self.search_synapse_at_planet(planet_id):
                            health += 1
        if ability == "BLANKED" and self.get_traits_given_pos(planet_id, unit_id) == "":
            if self.search_for_card_everywhere("Forge Master Dominus", bloodied_relevant=True):
                health += 1
        if ability == "Ireful Vanguard":
            warlord_pla, warlord_pos = self.get_location_of_warlord()
            if self.get_bloodied_given_pos(warlord_pla, warlord_pos):
                health += 1
            else:
                other_player = self.get_other_player()
                warlord_pla, warlord_pos = other_player.get_location_of_warlord()
                if other_player.get_bloodied_given_pos(warlord_pla, warlord_pos):
                    health += 1
        if ability != "Knight Paladin Voris":
            if self.search_card_at_planet(planet_id, "Knight Paladin Voris"):
                health += 1
        if ability == "Repurposed Pariah":
            health += self.count_units_with_trait_at_planet("Psyker", planet_id)
        if ability == "Galvax the Bloated":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.check_for_trait_given_pos(planet_id, i, "Cultist"):
                    health += 1
        if ability == "Fairly 'Quipped Kommando":
            health += len(self.cards_in_play[planet_id + 1][unit_id].get_attachments())
        if card.get_faction() == "Orks" and card.get_card_type() != "Token":
            if self.search_card_in_hq("Mork's Great Heap"):
                health += 1
        if ability == "Improbable Runt Machine":
            health += min(len(card.get_attachments()), 3)
        if ability == "Cultist":
            if self.search_for_card_everywhere("Sivarla Soulbinder"):
                health += 1
        if ability == "Charging Juggernaut":
            if card.get_attachments():
                health += 1
        if card.get_card_type() == "Warlord":
            if self.game.round_number == planet_id:
                if self.search_card_in_hq("Order of the Crimson Oath"):
                    health += 2
        if ability == "Neurotic Obliterator":
            health += len(card.get_attachments())
        if ability == "Amalgamated Devotee":
            health += 2 * len(card.get_attachments())
        if ability == "Hjorvath Coldstorm":
            if self.check_for_enemy_warlord(planet_id, True, self.name_player):
                health = health - 2
        if ability == "Tenacious Novice Squad":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                health += 1
        if ability == "Sacaellum Shrine Guard" or ability == "Saim-Hann Kinsman":
            if self.game.get_green_icon(planet_id):
                health += 1
        if self.game.infested_planets[planet_id]:
            if ability == "Emergent Cultists":
                health += 1
        if ability == "Shard of the Deceiver":
            health += len(self.discard)
        if self.check_for_trait_given_pos(planet_id, unit_id, "Warrior"):
            if self.search_card_at_planet(planet_id, "Talyesin Fharenal"):
                health += 1
        elif self.check_for_trait_given_pos(planet_id, unit_id, "Psyker"):
            if self.search_card_at_planet(planet_id, "Talyesin Fharenal"):
                health += 1
        if card.get_card_type() == "Army":
            if self.search_card_in_hq("Reign of Solemnace"):
                warlord_pla, warlord_pos = self.get_location_of_warlord()
                if warlord_pla == planet_id:
                    health += 1
            if self.game.infested_planets[planet_id]:
                if self.search_for_card_everywhere("Aberrant Alpha"):
                    health += 1
        if ability == "Ramshackle Trukk":
            if self.get_enemy_has_init_for_cards(planet_id, unit_id):
                health += 4
        if ability == "Goliath Rockgrinder":
            if self.game.infested_planets[planet_id]:
                health += 2
        if card.get_faction() != "Necrons" and card.check_for_a_trait("Warrior"):
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Immortal Vanguard":
                    health += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_name() == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Swarm Guard":
                    health += 2
        if ability == "Pyrrhian Eternals":
            health += self.discard.count("Pyrrhian Eternals")
        if ability == "Lychguard Sentinel":
            if self.count_units_in_discard() > 5:
                health += 4
        if ability == "Ymgarl Genestealer":
            if self.search_synapse_at_planet(planet_id):
                health += 2
            else:
                if self.number == "1":
                    if self.game.p2.search_synapse_at_planet(planet_id):
                        health += 2
                elif self.number == "2":
                    if self.game.p1.search_synapse_at_planet(planet_id):
                        health += 2
        if ability == "Armored Fist Squad":
            if self.check_for_warlord(planet_id, True, self.name_player) or \
                    self.check_for_enemy_warlord(planet_id, True, self.name_player):
                health += 2
        if self.get_card_type_given_pos(planet_id, unit_id) == "Army":
            if self.get_cost_given_pos(planet_id, unit_id) < 3:
                hunt_count = self.count_copies_at_planet(planet_id, "Hunting Acanthrites", ability=True)
                other_player = self.game.p1
                if other_player.name_player == self.name_player:
                    other_player = self.game.p2
                hunt_count += other_player.count_copies_at_planet(planet_id, "Hunting Acanthrites", ability=True)
                health = health - hunt_count
        attachments = self.cards_in_play[planet_id + 1][unit_id].get_attachments()
        for i in range(len(attachments)):
            if attachments[i].get_ability() == "Adaptative Thorax Swarm" and not attachments[i].from_magus_harid:
                if attachments[i].name_owner == self.name_player:
                    health += len(self.victory_display)
                else:
                    other_player = self.get_other_player()
                    health += len(other_player.victory_display)
            if attachments[i].get_ability() == "Noxious Fleshborer" and not attachments[i].from_magus_harid:
                if self.game.infested_planets[planet_id]:
                    health += 1
            if attachments[i].get_ability() == "Medallion of Betrayal":
                if self.check_for_trait_given_pos(planet_id, unit_id, "Cultist"):
                    health += 1
            if attachments[i].get_ability() == "Frostfang":
                if self.number == "1":
                    if self.game.p2.check_for_warlord(planet_id, True, self.name_player):
                        health += 2
                elif self.number == "2":
                    if self.game.p1.check_for_warlord(planet_id, True, self.name_player):
                        health += 2
        return health

    def search_synapse_at_planet(self, planet_pos):
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.cards_in_play[planet_pos + 1][i].get_card_type() == "Synapse":
                return True
        return False

    def check_damage_too_great_given_pos(self, planet_id, unit_id):
        if self.get_health_given_pos(planet_id, unit_id) > self.get_damage_given_pos(planet_id, unit_id):
            return 1
        return 0

    def check_if_control_faith(self):
        for i in range(len(self.headquarters)):
            if self.get_faith_given_pos(-2, i) > 0:
                return True
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.get_faith_given_pos(i, j) > 0:
                    return True
        return False

    def check_if_card_is_destroyed(self, planet_id, unit_id):
        if planet_id == -2:
            if self.headquarters[unit_id].get_card_type() == "Support":
                return False
            if self.get_ability_given_pos(planet_id, unit_id) == "Saint Erika":
                if not self.check_if_control_faith():
                    return True
            return not self.check_damage_too_great_given_pos(planet_id, unit_id)
        if self.get_ability_given_pos(planet_id, unit_id) == "Saint Erika":
            if not self.check_if_control_faith():
                return True
        return not self.check_damage_too_great_given_pos(planet_id, unit_id)

    def resolve_moved_damage_to_pos(self, planet_id, unit_id, amount):
        self.increase_damage_at_pos(planet_id, unit_id, amount)
        if self.get_card_type_given_pos(planet_id, unit_id) == "Warlord":
            if self.check_if_card_is_destroyed(planet_id, unit_id):
                if self.search_hand_for_card("Cajivak the Hateful"):
                    if not self.check_if_already_have_interrupt("Cajivak the Hateful"):
                        self.game.create_interrupt("Cajivak the Hateful", self.name_player,
                                                   (int(self.number), -1, -1))

    def increase_damage_at_pos(self, planet_id, unit_id, amount):
        if planet_id == -2:
            self.headquarters[unit_id].increase_damage(amount)
            return None
        self.cards_in_play[planet_id + 1][unit_id].increase_damage(amount)
        return None

    def remove_damage_from_pos(self, planet_id, unit_id, amount, healing=False):
        if healing:
            if self.search_card_at_planet(planet_id, "Hot-Shot Laspistol"):
                return None
            enemy_player = self.game.p1
            if enemy_player.name_player == self.name_player:
                enemy_player = self.game.p2
            if enemy_player.search_card_at_planet(planet_id, "Hot-Shot Laspistol"):
                return None
            if self.search_attachments_at_pos(planet_id, unit_id, "Great Scything Talons"):
                self.game.create_reaction("Great Scything Talons", self.name_player,
                                          (int(self.number), planet_id, unit_id))
                self.game.great_scything_talons_value = amount
            if self.illuminor_szeras_relevant:
                if self.get_faction_given_pos(planet_id, unit_id) == "Necrons":
                    if self.get_card_type_given_pos(planet_id, unit_id) == "Army":
                        self.game.create_reaction("Illuminor Szeras", self.name_player, (int(self.number), -1, -1))
        if planet_id == -2:
            self.headquarters[unit_id].remove_damage(amount)
        else:
            self.cards_in_play[planet_id + 1][unit_id].remove_damage(amount)

    def reset_eocr_values(self):
        self.reset_card_name_misc_ability("Trap Laying Hunter")
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].reset_own_eocr_values()
                if self.get_ability_given_pos(-2, i) == "Deathwing Terminators":
                    self.headquarters[i].misc_ability_used = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].reset_own_eocr_values()
                if self.get_ability_given_pos(i, j) == "Deathwing Terminators":
                    self.cards_in_play[i + 1][j].misc_ability_used = False

    def count_non_necron_factions(self):
        faction_list = []
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_faction() != "Necrons" and self.headquarters[i].get_faction() != "Neutral":
                if self.headquarters[i].get_faction() not in faction_list:
                    faction_list.append(self.headquarters[i].get_faction())
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_faction() != "Necrons" and \
                        self.cards_in_play[i + 1][j].get_faction() != "Neutral":
                    if self.cards_in_play[i + 1][j].get_faction() not in faction_list:
                        faction_list.append(self.cards_in_play[i + 1][j].get_faction())
        return len(faction_list)

    def apply_negative_health_eop(self, planet_pos, unit_pos, value):
        if planet_pos == -2:
            self.headquarters[unit_pos].negative_hp_until_eop += value
            return None
        self.cards_in_play[planet_pos + 1][unit_pos].negative_hp_until_eop += value
        return None

    def check_if_all_units_have_trait(self, trait):
        for i in range(len(self.headquarters)):
            if self.check_is_unit_at_pos(-2, i):
                if not self.check_for_trait_given_pos(-2, i, trait):
                    return False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if not self.check_for_trait_given_pos(i, j, trait):
                    return False
        return True

    def check_if_faction_given_pos(self, planet_pos, unit_pos, faction):
        if self.get_faction_given_pos(planet_pos, unit_pos) == faction:
            return True
        elif faction == "Astra Militarum" and \
                self.get_ability_given_pos(planet_pos, unit_pos) == "Gue'vesa Overseer" or \
                (self.game.apoka and self.get_ability_given_pos(planet_pos, unit_pos) == "Ardent Auxiliaries"):
            return True
        return False

    def perform_own_reactions_on_phase_change(self, phase):
        # Forced reactions first
        zog_wort = False
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Old Zogwort":
                if phase == "HEADQUARTERS":
                    zog_wort = True
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == "Old Zogwort":
                    if phase == "HEADQUARTERS":
                        zog_wort = True
        if zog_wort:
            i = 0
            while i < len(self.headquarters):
                if self.headquarters[i].get_name() == "Snotlings":
                    self.destroy_card_in_hq(i)
                    i = i - 1
                i = i + 1
            i = 0
            while i < 7:
                j = 0
                while j < len(self.cards_in_play[i + 1]):
                    if self.cards_in_play[i + 1][j].get_name() == "Snotlings":
                        self.destroy_card_in_play(i, j)
                        j = j - 1
                    j = j + 1
                i = i + 1
        if self.unstoppable_tide_value > 0:
            self.game.create_reaction("Unstoppable Tide", self.name_player, (int(self.number), -1, -1))
        if phase == "HEADQUARTERS":
            warlord_pla, warlord_pos = self.get_location_of_warlord()
            if self.search_attachments_at_pos(warlord_pla, warlord_pos, "Servo-Harness"):
                self.game.create_reaction("Servo-Harness", self.name_player, (int(self.number), -1, -1))
        if phase == "DEPLOY":
            if self.erekiels_queued > 0:
                for i in range(self.erekiels_queued):
                    self.game.create_reaction("Erekiel Next", self.name_player, (int(self.number), -1, -1))
                self.erekiels_queued = 0
            for i in range(len(self.victory_display)):
                if self.victory_display[i].get_name() == "Josoon":
                    self.add_resources(1)
        if self.search_hand_for_card("Hunter's Ploy"):
            if phase == "HEADQUARTERS":
                self.game.create_reaction("Hunter's Ploy", self.name_player, (int(self.number), -1, -1))
        if self.search_hand_for_card("Contaminated Convoys") and self.resources > 0:
            self.game.create_reaction("Contaminated Convoys", self.name_player, (int(self.number), -1, -1))
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Spore Chimney":
                if phase == "HEADQUARTERS":
                    self.game.create_reaction("Spore Chimney", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Palace of Slaanesh":
                if phase == "HEADQUARTERS":
                    self.game.create_reaction("Palace of Slaanesh", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Promethium Mine":
                if phase == "DEPLOY" and self.headquarters[i].counter:
                    self.game.create_reaction("Promethium Mine", self.name_player, (int(self.number), -2, i))
            if self.get_ability_given_pos(-2, i) == "Mobilize the Chapter":
                if phase == "COMBAT":
                    self.game.create_reaction("Mobilize the Chapter", self.name_player, (int(self.number), -2, i))
            if self.get_ability_given_pos(-2, i) == "Myriad Excesses":
                if phase == "COMMAND":
                    self.game.create_reaction("Myriad Excesses", self.name_player, (int(self.number), -2, i))
            if self.get_ability_given_pos(-2, i) == "Vior'la Sept":
                if phase == "COMBAT":
                    self.game.create_reaction("Vior'la Sept", self.name_player, (int(self.number), -2, i))
            if self.get_ability_given_pos(-2, i) == "Dark Allegiance":
                if phase == "DEPLOY":
                    if self.check_if_all_units_have_trait(self.headquarters[i].misc_string):
                        self.game.create_reaction("Dark Allegiance", self.name_player, (int(self.number), -2, i))
            if self.get_ability_given_pos(-2, i) == "Vamii Industrial Complex":
                if phase == "COMBAT":
                    self.game.create_reaction("Vamii Industrial Complex", self.name_player, (int(self.number), -2, i))
            if self.get_ability_given_pos(-2, i) == "Maynarkh Dynasty":
                if phase == "DEPLOY":
                    self.game.create_reaction("Maynarkh Dynasty", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Shard of the Deceiver":
                self.game.create_reaction("Shard of the Deceiver", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Weight of the Aeons":
                if self.get_ready_given_pos(-2, i):
                    self.game.create_reaction("Weight of the Aeons", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Masters of the Webway":
                if phase == "DEPLOY":
                    self.game.create_reaction("Masters of the Webway", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Support Fleet":
                if phase == "DEPLOY":
                    if self.headquarters[i].attachments:
                        self.game.create_reaction("Support Fleet Transfer", self.name_player,
                                                  (int(self.number), -2, i))
            if self.get_ability_given_pos(-2, i, bloodied_relevant=True) == "Aun'Len":
                if phase == "COMMAND":
                    self.game.create_reaction("Aun'Len", self.name_player,
                                              (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Obedience":
                if self.get_ready_given_pos(-2, i):
                    self.game.create_reaction("Obedience", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Willing Submission":
                if phase == "DEPLOY":
                    self.game.create_reaction("Willing Submission", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Deathmark Assassins":
                if phase == "COMBAT":
                    self.game.create_reaction("Deathmark Assassins", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Warlock Destructor":
                if phase == "DEPLOY":
                    self.game.create_reaction("Warlock Destructor", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Charging Juggernaut":
                if phase == "DEPLOY":
                    self.game.create_reaction("Charging Juggernaut", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Blood Rain Tempest":
                if phase == "COMBAT":
                    self.game.create_reaction("Blood Rain Tempest", self.name_player, (int(self.number), -2, i))
            for j in range(len(self.headquarters[i].get_attachments())):
                if phase == "COMBAT":
                    if self.headquarters[i].get_attachments()[j].get_ability() == "Parasitic Infection" and not \
                            self.headquarters[i].get_attachments()[j].from_magus_harid:
                        name_owner = self.headquarters[i].get_attachments()[j].name_owner
                        self.game.create_reaction("Parasitic Infection", name_owner, (int(self.number), -2, i))
                    if self.headquarters[i].get_attachments()[j].get_ability() == "Savage Parasite" and not \
                            self.headquarters[i].get_attachments()[j].from_magus_harid:
                        name_owner = self.headquarters[i].get_attachments()[j].name_owner
                        self.game.create_reaction("Savage Parasite", name_owner, (int(self.number), -2, i))
                if self.headquarters[i].get_attachments()[j].get_ability() == "Royal Phylactery":
                    if self.headquarters[i].get_damage() > 0:
                        owner = self.headquarters[i].get_attachments()[j].name_owner
                        self.game.create_reaction("Royal Phylactery", owner, (int(self.number), -2, i))
        for i in range(7):
            for j in range(len(self.attachments_at_planet[i])):
                if self.attachments_at_planet[i][j].get_ability() == "Supreme Strategist":
                    if phase == "DEPLOY":
                        self.game.create_reaction("Supreme Strategist", self.name_player, (int(self.number), i, j))
                if self.attachments_at_planet[i][j].get_ability() == "Trapped Objective":
                    if phase == "COMBAT":
                        self.game.create_reaction("Trapped Objective", self.name_player, (int(self.number), i, -1))
            for j in range(len(self.cards_in_reserve[i])):
                if self.cards_in_reserve[i][j].get_ability() == "Snagbrat's Scouts":
                    if phase == "COMMAND":
                        if self.resources > 0:
                            if not self.check_if_already_have_reaction("Snagbrat's Scouts"):
                                self.game.create_reaction("Snagbrat's Scouts", self.name_player,
                                                          (int(self.number), -1, -1))
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == "Warlock Destructor":
                    if phase == "DEPLOY":
                        self.game.create_reaction("Warlock Destructor", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Charging Juggernaut":
                    if phase == "DEPLOY":
                        self.game.create_reaction("Charging Juggernaut", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Shard of the Deceiver":
                    self.game.create_reaction("Shard of the Deceiver", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Drifting Spore Mines":
                    if phase == "COMBAT":
                        self.game.create_reaction("Drifting Spore Mines", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Seer Adept":
                    if phase == "COMMAND":
                        enemy_player = self.game.p1
                        if enemy_player.name_player == self.name_player:
                            enemy_player = self.game.p2
                        if enemy_player.cards_in_reserve[i]:
                            self.game.create_reaction("Seer Adept", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Blazing Zoanthrope":
                    if phase == "COMBAT":
                        self.game.create_reaction("Blazing Zoanthrope", self.name_player,
                                                  (int(self.number), i, j))
                if self.get_ability_given_pos(i, j) == "Squiggoth Brute":
                    if phase == "COMBAT":
                        self.game.create_reaction("Squiggoth Brute", self.name_player, (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Deathmark Assassins":
                    if phase == "COMBAT":
                        self.game.create_reaction("Deathmark Assassins", self.name_player,
                                                  (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Nahumekh":
                    if phase == "COMBAT":
                        self.nahumekh_value = self.count_non_necron_factions()
                        if self.nahumekh_value > 0:
                            self.game.create_reaction("Nahumekh", self.name_player,
                                                      (int(self.number), i, j))
                if self.cards_in_play[i + 1][j].get_ability() == "Gleeful Plague Beast":
                    if phase == "COMBAT":
                        self.suffer_area_effect(i, 1)
                        if self.name_player == self.game.name_1:
                            self.game.p2.suffer_area_effect(i, 1, rickety_warbuggy=True)
                        else:
                            self.game.p1.suffer_area_effect(i, 1, rickety_warbuggy=True)
                for k in range(len(self.cards_in_play[i + 1][j].get_attachments())):
                    if phase == "COMBAT":
                        if self.cards_in_play[i + 1][j].get_attachments()[k].get_ability() == "Parasitic Infection" \
                                and not self.cards_in_play[i + 1][j].get_attachments()[k].from_magus_harid:
                            name_owner = self.cards_in_play[i + 1][j].get_attachments()[k].name_owner
                            self.game.create_reaction("Parasitic Infection", name_owner, (int(self.number), i, j))
                        if self.cards_in_play[i + 1][j].get_attachments()[k].get_ability() == "Savage Parasite" \
                                and not self.cards_in_play[i + 1][j].get_attachments()[k].from_magus_harid:
                            name_owner = self.cards_in_play[i + 1][j].get_attachments()[k].name_owner
                            self.game.create_reaction("Savage Parasite", name_owner, (int(self.number), i, j))
                    if self.cards_in_play[i + 1][j].get_attachments()[k].get_ability() == "Royal Phylactery":
                        if self.cards_in_play[i + 1][j].get_damage() > 0:
                            owner = self.cards_in_play[i + 1][j].get_attachments()[k].name_owner
                            self.game.create_reaction("Royal Phylactery", owner, (int(self.number), i, j))

    def sacrifice_card_in_hq(self, card_pos):
        if self.headquarters[card_pos].get_card_type() == "Warlord":
            return False
        if self.headquarters[card_pos].get_name() == "Cultist":
            if self.search_card_in_hq("Myriad Excesses"):
                return False
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_ability() == "Master Warpsmith":
                    if self.game.card_to_deploy is not None:
                        if self.game.card_to_deploy.check_for_a_trait("Elite"):
                            self.game.discounts_applied += 1
                        else:
                            self.master_warpsmith_count += 1
                    else:
                        self.master_warpsmith_count += 1
            for i in range(7):
                for j in range(len(self.cards_in_play[i + 1])):
                    if self.get_ability_given_pos(i, j) == "Master Warpsmith":
                        if self.game.card_to_deploy is not None:
                            if self.game.card_to_deploy.check_for_a_trait("Elite"):
                                self.game.discounts_applied += 1
                            else:
                                self.master_warpsmith_count += 1
                        else:
                            self.master_warpsmith_count += 1
        self.add_card_in_hq_to_discard(card_pos)
        return True

    def sacrifice_card_in_play(self, planet_num, card_pos):
        if planet_num == -2:
            return self.sacrifice_card_in_hq(card_pos)
        if self.cards_in_play[planet_num + 1][card_pos].get_card_type() == "Warlord":
            return False
        if self.cards_in_play[planet_num + 1][card_pos].get_card_type() != "Token":
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_ability() == "Formosan Black Ship":
                    if self.headquarters[i].get_ready():
                        self.game.create_reaction("Formosan Black Ship", self.name_player,
                                                  (int(self.number), -2, -1))
                        self.last_planet_sacrifice = planet_num
        if self.cards_in_play[planet_num + 1][card_pos].get_name() == "Cultist":
            if self.search_card_in_hq("Myriad Excesses"):
                return False
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_ability() == "Master Warpsmith":
                    if self.game.card_to_deploy is not None:
                        if self.game.card_to_deploy.check_for_a_trait("Elite"):
                            self.game.discounts_applied += 1
                        else:
                            self.master_warpsmith_count += 1
                    else:
                        self.master_warpsmith_count += 1
            for i in range(7):
                for j in range(len(self.cards_in_play[i + 1])):
                    if self.get_ability_given_pos(i, j) == "Master Warpsmith":
                        if self.game.card_to_deploy is not None:
                            if self.game.card_to_deploy.check_for_a_trait("Elite"):
                                self.game.discounts_applied += 1
                            else:
                                self.master_warpsmith_count += 1
                        else:
                            self.master_warpsmith_count += 1
        self.add_card_in_play_to_discard(planet_num, card_pos)
        return True

    def destroy_card_in_hq(self, card_pos):
        self.search_for_preemptive_destroy_interrupts()
        if self.headquarters[card_pos].get_card_type() == "Warlord":
            if self.headquarters[card_pos].get_name() == "Termagant":
                self.add_card_in_hq_to_discard(card_pos)
                self.warlord_just_got_destroyed = True
            if self.headquarters[card_pos].get_name() == "Grand Master Belial" and \
                    self.headquarters[card_pos].get_card_type() == "Warlord":
                self.add_card_in_hq_to_discard(card_pos)
                self.warlord_just_got_destroyed = True
            elif not self.headquarters[card_pos].get_bloodied():
                self.bloody_warlord_given_pos(-2, card_pos)
            else:
                if self.get_ability_given_pos(-2, card_pos) == "Magus Harid" and not self.hit_by_gorgul:
                    self.game.create_interrupt("Magus Harid: Final Form", self.name_player,
                                               (int(self.number), -1, -1))
                    self.add_card_in_hq_to_discard(card_pos)
                elif self.search_all_deepstrikes("Grand Master Belial"):
                    self.game.create_interrupt("Grand Master Belial", self.name_player,
                                               (int(self.number), -1, -1))
                    self.add_card_in_hq_to_discard(card_pos)
                else:
                    self.add_card_in_hq_to_discard(card_pos)
                    self.warlord_just_got_destroyed = True
        else:
            if self.headquarters[card_pos].get_ability() == "Carnivore Pack":
                self.add_resources(3)
            if self.headquarters[card_pos].get_ability() == "Shrouded Harlequin":
                self.game.create_reaction("Shrouded Harlequin", self.name_player,
                                          (int(self.number), -1, -1))
            if self.get_ability_given_pos(-2, card_pos) == "Mucolid Spores":
                self.game.create_interrupt("Mucolid Spores", self.name_player, (int(self.number), -1, -1))
            if self.get_faction_given_pos(-2, card_pos) == "Space Marines" \
                    and self.check_is_unit_at_pos(-2, card_pos):
                already_apoth = False
                for i in range(len(self.game.reactions_needing_resolving)):
                    if self.game.reactions_needing_resolving[i] == "Secluded Apothecarion":
                        if self.game.player_who_resolves_reaction[i] == self.name_player:
                            already_apoth = True
                if not already_apoth:
                    for i in range(len(self.headquarters)):
                        if self.get_ability_given_pos(-2, i) == "Secluded Apothecarion":
                            if self.get_ready_given_pos(-2, i):
                                self.game.create_reaction("Secluded Apothecarion", self.name_player,
                                                          (int(self.number), -2, i))
            if self.check_for_trait_given_pos(-2, card_pos, "Vehicle"):
                if not self.does_own_interrupt_exist("Death Serves the Emperor"):
                    if self.search_hand_for_card("Death Serves the Emperor"):
                        if not self.death_serves_used or self.game.apoka:
                            self.game.create_interrupt("Death Serves the Emperor", self.name_player,
                                                       (int(self.number), -1, -1))
                            cost = self.get_cost_given_pos(-2, card_pos)
                            if cost > self.highest_death_serves_value:
                                self.highest_death_serves_value = cost
            if self.check_for_trait_given_pos(-2, card_pos, "Dark Angels"):
                if self.search_card_in_hq("Standard of Devastation"):
                    self.game.create_reaction("Standard of Devastation", self.name_player,
                                              (int(self.number), -1, -1))
            self.cards_recently_destroyed.append(self.headquarters[card_pos].get_name())
            self.add_card_in_hq_to_discard(card_pos)
            self.game.queued_sound = "destroy"

    def destroy_all_cards_in_hq(self, ignore_uniques=True, units_only=True, enemy_event=False):
        i = 0
        while i < len(self.headquarters):
            card_type = self.headquarters[i].get_card_type()
            if ignore_uniques and units_only:
                if not self.headquarters[i].get_unique() and (card_type == "Army" or card_type == "Token"):
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i, power=True):
                        if self.get_ability_given_pos(-2, i) == "Flayed Ones Revenants":
                            self.create_reaction("Flayed Ones Revenants", secondary_player.name_player,
                                                 (int(secondary_player.number), -2, -1))
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            elif ignore_uniques and not units_only:
                if not self.headquarters[i].get_unique():
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i, power=True):
                        if self.get_ability_given_pos(-2, i) == "Flayed Ones Revenants":
                            self.create_reaction("Flayed Ones Revenants", secondary_player.name_player,
                                                 (int(secondary_player.number), -2, -1))
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            elif not ignore_uniques and units_only:
                if card_type == "Army" or card_type == "Token":
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i, power=True):
                        if self.get_ability_given_pos(-2, i) == "Flayed Ones Revenants":
                            self.create_reaction("Flayed Ones Revenants", secondary_player.name_player,
                                                 (int(secondary_player.number), -2, -1))
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            else:
                if not enemy_event:
                    self.destroy_card_in_hq(i)
                    i = i - 1
                elif not self.get_immune_to_enemy_events(-2, i, power=True):
                    if self.get_ability_given_pos(-2, i) == "Flayed Ones Revenants":
                        self.create_reaction("Flayed Ones Revenants", secondary_player.name_player,
                                             (int(secondary_player.number), -2, -1))
                    self.destroy_card_in_hq(i)
                    i = i - 1
                i = i + 1

    def discard_top_card_deck(self):
        if self.deck:
            self.add_card_to_discard(self.deck[0])
            del self.deck[0]
            return True
        return False

    def get_card_top_discard(self):
        if self.discard:
            card_name = self.discard[-1]
            card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            return card
        return None

    def get_planet_of_warlord(self):
        if self.check_for_warlord(-2) == 1:
            return -2
        for i in range(7):
            if self.check_for_warlord(i) == 1:
                return i
        return -1

    def get_location_of_warlord(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_card_type() == "Warlord":
                return -2, i
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_card_type() == "Warlord":
                    return i, j
        return -1, -1

    def resolve_battle_begins(self, planet_num):
        self.looted_skrap_active = False
        if planet_num != 0:
            for i in range(len(self.cards_in_play[planet_num])):
                if self.get_ability_given_pos(planet_num - 1, i) == "Champion of Khorne":
                    self.game.create_reaction("Champion of Khorne", self.name_player,
                                              (int(self.number), planet_num - 1, i))
        if planet_num != 6:
            for i in range(len(self.cards_in_play[planet_num + 2])):
                if self.get_ability_given_pos(planet_num + 1, i) == "Champion of Khorne":
                    self.game.create_reaction("Champion of Khorne", self.name_player,
                                              (int(self.number), planet_num + 1, i))
        for i in range(len(self.cards_in_play[planet_num + 1])):
            if self.search_attachments_at_pos(planet_num, i, "Fenrisian Wolf", must_match_name=True):
                if self.get_ready_given_pos(planet_num, i):
                    self.game.create_reaction("Fenrisian Wolf", self.name_player, (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Kroot Guerrilla":
                self.game.create_reaction("Kroot Guerrilla", self.name_player, (int(self.number), planet_num, i))
            if self.get_lumbering_given_pos(planet_num, i):
                self.exhaust_given_pos(planet_num, i, card_effect=True)
            if self.get_ability_given_pos(planet_num, i) == "Da Swoopy":
                self.game.create_reaction("Da Swoopy", self.name_player, (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Kabal of the Ebon Law":
                self.game.create_reaction("Kabal of the Ebon Law", self.name_player, (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Yvraine's Entourage":
                self.game.create_reaction("Yvraine's Entourage", self.name_player, (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Cegorach's Jesters":
                self.game.create_reaction("Cegorach's Jesters", self.name_player, (int(self.number), planet_num, i))

    def get_lumbering_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_lumbering()
        if self.search_attachments_at_pos(planet_id, unit_id, "Centurion Warsuit"):
            return True
        return self.cards_in_play[planet_id + 1][unit_id].get_lumbering()

    def resolve_combat_round_begins(self, planet_num):
        if not self.check_for_warlord(planet_num):
            if "Miraculous Intervention" in self.cards:
                self.game.create_reaction("Miraculous Intervention", self.name_player, (int(self.number), -1, -1))
        for i in range(len(self.headquarters)):
            self.headquarters[i].once_per_combat_round_used = False
            if self.headquarters[i].get_ability() == "Holy Fusillade":
                if self.headquarters[i].get_ready():
                    if not self.game.ranged_skirmish_active:
                        self.game.create_reaction("Holy Fusillade", self.name_player, (int(self.number), -2, i))
        for i in range(len(self.cards_in_play[planet_num + 1])):
            self.cards_in_play[planet_num + 1][i].once_per_combat_round_used = False
            if self.cards_in_play[planet_num + 1][i].get_ability() == "Termagant Horde":
                self.game.create_reaction("Termagant Horde", self.name_player, (int(self.number), planet_num, i))
            if self.cards_in_play[planet_num + 1][i].get_ability() == "Storming Librarian":
                self.game.create_reaction("Storming Librarian", self.name_player, (int(self.number), planet_num, i))
            if self.cards_in_play[planet_num + 1][i].get_ability() == "Crush of Sky-Slashers":
                self.game.create_reaction("Crush of Sky-Slashers", self.name_player, (int(self.number), planet_num, i))
            if self.cards_in_play[planet_num + 1][i].get_ability() == "Shard of the Deceiver":
                self.game.create_reaction("Shard of the Deceiver", self.name_player, (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Sathariel the Invokator":
                self.game.create_reaction("Sathariel the Invokator", self.name_player,
                                          (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Devoted Enginseer":
                if self.get_ready_given_pos(planet_num, i):
                    self.game.create_reaction("Devoted Enginseer", self.name_player,
                                              (int(self.number), planet_num, i))
            for j in range(len(self.cards_in_play[planet_num + 1][i].get_attachments())):
                if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability() == "Royal Phylactery":
                    if self.cards_in_play[planet_num + 1][i].get_damage() > 0:
                        owner = self.cards_in_play[planet_num + 1][i].get_attachments()[j].name_owner
                        self.game.create_reaction("Royal Phylactery", owner, (int(self.number), planet_num, i))
                if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability() == "Resurrection Orb":
                    self.game.create_reaction("Resurrection Orb", self.name_player,
                                              (int(self.number), planet_num, i))
                if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability() == "Cloud of Flies":
                    self.game.create_reaction("Cloud of Flies", self.name_player,
                                              (int(self.number), planet_num, i))
                if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability() == "Necklace of Teef":
                    self.game.create_reaction("Necklace of Teef", self.name_player,
                                              (int(self.number), planet_num, i))

    def add_card_to_discard(self, card_name):
        if card_name not in ["Snotlings", "Guardsman", "Cultist", "Khymera", "Termagant"]:
            self.discard.append(card_name)
            card = self.game.preloaded_find_card(card_name)
            self.cards_recently_discarded.append(card_name)
            if card.get_card_type() == "Attachment":
                if not card.planet_attachment:
                    for i in range(7):
                        for j in range(len(self.cards_in_reserve[i])):
                            if not self.check_if_already_have_reaction("Impulsive Loota"):
                                if self.cards_in_reserve[i][j].get_ability() == "Impulsive Loota":
                                    self.game.create_reaction("Impulsive Loota Reserve", self.name_player,
                                                              (int(self.number), -1, -1))
                        for j in range(len(self.cards_in_play[i + 1])):
                            if not self.check_if_already_have_reaction("Impulsive Loota"):
                                if self.cards_in_play[i + 1][j].actually_a_deepstrike:
                                    if self.cards_in_play[i + 1][j].deepstrike_card_name == "Impulsive Loota":
                                        self.game.create_reaction("Impulsive Loota In Play", self.name_player,
                                                                  (int(self.number), -1, -1))
            if card.get_card_type() == "Army":
                for i in range(len(self.headquarters)):
                    if self.get_ability_given_pos(-2, i) == "Unearthed Crypt":
                        if self.get_ready_given_pos(-2, i):
                            self.game.create_interrupt("Unearthed Crypt", self.name_player, (int(self.number), -2, i))
            if card_name == "Cardinal Agra Decree":
                self.game.create_interrupt("Cardinal Agra Decree", self.name_player, (int(self.number), -1, -1))
            if card_name == "Medallion of Betrayal":
                if not self.check_if_already_have_reaction("Medallion of Betrayal"):
                    self.game.create_reaction("Medallion of Betrayal", self.name_player, (int(self.number), -1, -1))

    def search_for_preemptive_destroy_interrupts(self):
        for i in range(len(self.headquarters)):
            if self.check_if_card_is_destroyed(-2, i):
                if self.search_attachments_at_pos(-2, i, "Ulthwe Spirit Stone"):
                    self.game.create_interrupt("Ulthwe Spirit Stone", self.name_player, (int(self.number), -2, i))
                if self.get_ability_given_pos(-2, i, bloodied_relevant=True) == "Trazyn the Infinite"\
                        and not self.headquarters[i].misc_ability_used:
                    self.game.create_interrupt("Trazyn the Infinite", self.name_player, (int(self.number), -2, i))
                if self.get_card_type_given_pos(-2, i) == "Warlord":
                    if self.headquarters[i].get_bloodied():
                        if self.get_ability_given_pos(-2, i) == "Saint Celestine" and not \
                                self.hit_by_gorgul and not self.get_once_per_game_used_given_pos(-2, i):
                            self.game.create_interrupt("Saint Celestine: Rebirth", self.name_player,
                                                       (int(self.number), -2, i))
                        elif self.game.last_planet_checked_for_battle != -1 and self.necrodermis_allowed:
                            if self.necrodermis_check():
                                self.game.create_interrupt("Necrodermis", self.name_player,
                                                           (int(self.number), -2, i))
                                self.necrodermis_allowed = False
                            # elif self.search_for_card_everywhere("Harbinger of Eternity"):
                            #     if "Necrodermis" in self.discard:
                            #         self.game.create_interrupt("Necrodermis", self.name_player,
                            #                                    (int(self.number), -2, i))
                            #         self.necrodermis_allowed = False

        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.check_if_card_is_destroyed(i, j):
                    if self.search_attachments_at_pos(i, j, "Ulthwe Spirit Stone"):
                        self.game.create_interrupt("Ulthwe Spirit Stone", self.name_player, (int(self.number), i, j))
                    if self.get_ability_given_pos(i, j, bloodied_relevant=True) == "Trazyn the Infinite"\
                            and not self.cards_in_play[i + 1][j].misc_ability_used:
                        self.game.create_interrupt("Trazyn the Infinite", self.name_player, (int(self.number), i, j))
                    if self.get_card_type_given_pos(i, j) == "Warlord":
                        if self.cards_in_play[i + 1][j].get_bloodied():
                            if self.get_ability_given_pos(i, j) == "Saint Celestine" and not \
                                    self.hit_by_gorgul and not self.get_once_per_game_used_given_pos(i, j):
                                self.game.create_interrupt("Saint Celestine: Rebirth", self.name_player,
                                                           (int(self.number), i, j))
                            elif self.game.last_planet_checked_for_battle != -1 and self.necrodermis_allowed:
                                if self.necrodermis_check():
                                    self.game.create_interrupt("Necrodermis", self.name_player,
                                                               (int(self.number), i, j))
                                    self.necrodermis_allowed = False
                                # elif self.search_for_card_everywhere("Harbinger of Eternity"):
                                #     if "Necrodermis" in self.discard:
                                #         self.game.create_interrupt("Necrodermis", self.name_player,
                                #                                    (int(self.number), i, j))
                                #         self.necrodermis_allowed = False
                    if self.get_ability_given_pos(i, j) == "Icy Trygon"\
                            and not self.cards_in_play[i + 1][j].misc_ability_used:
                        self.cards_in_play[i + 1][j].misc_ability_used = True
                        self.game.create_interrupt("Icy Trygon", self.name_player, (int(self.number), i, j))
                    if self.get_faction_given_pos(i, j) == "Astra Militarum":
                        if not self.check_if_already_have_interrupt("Blood of Martyrs"):
                            for hq_pos in range(len(self.headquarters)):
                                if self.get_ability_given_pos(-2, hq_pos) == "Blood of Martyrs":
                                    if self.get_ready_given_pos(-2, hq_pos):
                                        self.game.create_interrupt("Blood of Martyrs", self.name_player,
                                                                   (int(self.number), -1, -1))
                    if self.get_ability_given_pos(i, j) == "Growing Tide"\
                            and not self.cards_in_play[i + 1][j].misc_ability_used:
                        if i == self.game.round_number:
                            self.cards_in_play[i + 1][j].misc_ability_used = True
                            self.game.create_interrupt("Growing Tide", self.name_player, (int(self.number), i, j))

    def check_for_cards_in_reserve(self, planet_pos):
        if self.cards_in_reserve[planet_pos]:
            return True
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.cards_in_play[planet_pos + 1][i].actually_a_deepstrike:
                return True
        return False

    def search_all_deepstrikes(self, card_name):
        for i in range(7):
            for j in range(len(self.cards_in_reserve[i])):
                if self.cards_in_reserve[i][j].get_ability() == card_name:
                    return True
        return False

    def destroy_card_in_play(self, planet_num, card_pos):
        if planet_num == -2:
            self.destroy_card_in_hq(card_pos)
            return None
        if self.cards_in_play[planet_num + 1][card_pos].get_card_type() == "Warlord":
            if self.cards_in_play[planet_num + 1][card_pos].get_name() == "Termagant":
                self.add_card_in_play_to_discard(planet_num, card_pos)
                self.warlord_just_got_destroyed = True
            if self.cards_in_play[planet_num + 1][card_pos].get_name() == "Grand Master Belial" and \
                    self.cards_in_play[planet_num + 1][card_pos].get_card_type() == "Warlord":
                self.add_card_in_play_to_discard(planet_num, card_pos)
                self.warlord_just_got_destroyed = True
            elif not self.cards_in_play[planet_num + 1][card_pos].get_bloodied():
                self.bloody_warlord_given_pos(planet_num, card_pos)
                self.warlord_just_got_bloodied = True
            else:
                if self.get_ability_given_pos(planet_num, card_pos) == "Magus Harid" and not self.hit_by_gorgul:
                    self.game.create_interrupt("Magus Harid: Final Form", self.name_player,
                                               (int(self.number), -1, -1))
                    self.add_card_in_play_to_discard(planet_num, card_pos)
                elif self.search_all_deepstrikes("Grand Master Belial"):
                    self.game.create_interrupt("Grand Master Belial", self.name_player,
                                               (int(self.number), -1, -1))
                    self.add_card_in_play_to_discard(planet_num, card_pos)
                else:
                    self.add_card_in_play_to_discard(planet_num, card_pos)
                    self.warlord_just_got_destroyed = True
        else:
            other_player = self.get_other_player()
            if other_player.looted_skrap_active:
                if planet_num == other_player.looted_skrap_planet:
                    if other_player.looted_skrap_count > 0:
                        other_player.add_resources(1)
                        other_player.looted_skrap_count = other_player.looted_skrap_count - 1
            if other_player.search_hand_for_card("Berzerker Warriors"):
                if not other_player.check_if_already_have_reaction("Berzerker Warriors"):
                    self.game.create_interrupt("Berzerker Warriors", other_player.name_player,
                                               (int(other_player.number), -1, -1))
            if self.get_card_type_given_pos(planet_num, card_pos) == "Army":
                for i in range(len(other_player.cards_in_play[planet_num + 1])):
                    if other_player.get_ability_given_pos(planet_num, i) == "Mindless Pain Addict":
                        self.game.create_reaction("Mindless Pain Addict", self.name_player,
                                                  (int(other_player.number), planet_num, i))
                if self.get_faction_given_pos(planet_num, card_pos) == "Space Marines":
                    for i in range(len(self.cards_in_play[planet_num + 1])):
                        if self.get_ability_given_pos(planet_num, i) == "Imperial Fists Apothecary":
                            if not self.get_once_per_phase_used_given_pos(planet_num, i):
                                if not self.check_if_already_have_reaction_of_position(
                                        "Imperial Fists Apothecary", planet_num, i):
                                    self.game.create_reaction("Imperial Fists Apothecary", self.name_player,
                                                              (int(self.number), planet_num, i))
            if self.get_card_type_given_pos(planet_num, card_pos) != "Warlord":
                if self.get_faction_given_pos(planet_num, card_pos) == other_player.enslaved_faction:
                    for i in range(len(other_player.cards_in_play[planet_num + 1])):
                        if other_player.get_ability_given_pos(planet_num, i) == "Lokhust Destroyer":
                            if not other_player.get_once_per_phase_used_given_pos(planet_num, i):
                                if not other_player.check_if_already_have_reaction_of_position("Lokhust Destroyer",
                                                                                               planet_num, i):
                                    if not other_player.get_ready_given_pos(planet_num, i):
                                        self.game.create_reaction("Lokhust Destroyer", other_player.name_player,
                                                                  (int(other_player.number), planet_num, i))
            if self.cards_in_play[planet_num + 1][card_pos].get_name() == "Termagant":
                for i in range(len(self.cards_in_play[planet_num + 1])):
                    if self.cards_in_play[planet_num + 1][i].get_ability() == "Termagant Sentry":
                        already_termagant_sentry = False
                        for j in range(len(self.game.reactions_needing_resolving)):
                            if self.game.reactions_needing_resolving[j] == "Termagant Sentry":
                                if self.game.player_who_resolves_reaction[j] == self.name_player:
                                    already_termagant_sentry = True
                        if not already_termagant_sentry:
                            self.game.create_reaction("Termagant Sentry", self.name_player,
                                                      (int(self.number), planet_num, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_name() == "Snotlings":
                self.enemy_has_wyrdboy_stikk = False
                already_weirdboy_stikk = False
                if self.search_for_card_everywhere("Wyrdboy Stikk", ready_relevant=True):
                    for i in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[i] == "Wyrdboy Stikk":
                            if self.game.player_who_resolves_reaction[i] == self.name_player:
                                already_weirdboy_stikk = True
                    if not already_weirdboy_stikk:
                        self.game.create_reaction("Wyrdboy Stikk", self.name_player,
                                                  (int(self.number), -1, -1))
                else:
                    found_stikk = False
                    for i in range(len(other_player.headquarters)):
                        if other_player.headquarters[i].get_is_unit():
                            for j in range(len(other_player.headquarters[i].get_attachments())):
                                attach = other_player.headquarters[i].get_attachments()[j]
                                if attach.get_ability() == "Wyrdboy Stikk":
                                    if attach.get_ready() and attach.name_owner == self.name_player:
                                        found_stikk = True
                                        self.enemy_has_wyrdboy_stikk = True
                    for h in range(7):
                        for i in range(len(other_player.cards_in_play[h + 1])):
                            if other_player.cards_in_play[h + 1][i].get_is_unit():
                                for j in range(len(other_player.cards_in_play[h + 1][i].get_attachments())):
                                    attach = other_player.cards_in_play[h + 1][i].get_attachments()[j]
                                    if attach.get_ability() == "Wyrdboy Stikk":
                                        if attach.get_ready() and attach.name_owner == self.name_player:
                                            found_stikk = True
                                            self.enemy_has_wyrdboy_stikk = True
                    if found_stikk:
                        for k in range(len(self.game.reactions_needing_resolving)):
                            if self.game.reactions_needing_resolving[k] == "Wyrdboy Stikk":
                                if self.game.player_who_resolves_reaction[k] == self.name_player:
                                    already_weirdboy_stikk = True
                        if not already_weirdboy_stikk:
                            self.game.create_reaction("Wyrdboy Stikk", self.name_player,
                                                      (int(self.number), -1, -1))
            if self.check_for_trait_given_pos(planet_num, card_pos, "Elite"):
                if not self.does_own_reaction_exist("Invasion Site"):
                    if self.search_card_in_hq("Invasion Site"):
                        self.game.create_reaction("Invasion Site", self.name_player,
                                                  (int(self.number), -1, -1))
                        cost = self.get_cost_given_pos(planet_num, card_pos)
                        if cost > self.highest_cost_invasion_site:
                            self.highest_cost_invasion_site = cost
            if self.check_for_trait_given_pos(planet_num, card_pos, "Ecclesiarchy"):
                for i in range(len(self.cards_in_play[planet_num + 1])):
                    if self.get_ability_given_pos(planet_num, i) == "Vengeful Seraphim":
                        if not self.get_once_per_phase_used_given_pos(planet_num, i):
                            if not self.does_own_positioned_reaction_exist("Vengeful Seraphim", planet_num, i):
                                self.game.create_reaction("Vengeful Seraphim", self.name_player,
                                                          (int(self.number), planet_num, i))
            if self.check_for_trait_given_pos(planet_num, card_pos, "Dark Angels"):
                if self.search_card_in_hq("Standard of Devastation"):
                    self.game.create_reaction("Standard of Devastation", self.name_player,
                                              (int(self.number), -1, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_has_deepstrike():
                if self.search_card_in_hq("Klan Totem", ready_relevant=True):
                    if not self.check_if_already_have_reaction("Klan Totem"):
                        self.game.create_reaction("Klan Totem", self.name_player, (int(self.number), -1, -1))
            if self.check_for_trait_given_pos(planet_num, card_pos, "Vehicle"):
                if not self.does_own_interrupt_exist("Death Serves the Emperor"):
                    if self.search_hand_for_card("Death Serves the Emperor"):
                        if not self.death_serves_used or self.game.apoka:
                            self.game.create_interrupt("Death Serves the Emperor", self.name_player,
                                                       (int(self.number), -1, -1))
                            cost = self.get_cost_given_pos(planet_num, card_pos)
                            if cost > self.highest_death_serves_value:
                                self.highest_death_serves_value = cost
                if not self.does_own_reaction_exist("The Bloodrunna"):
                    for i in range(len(self.cards_in_play[planet_num + 1])):
                        if i != card_pos:
                            for j in range(len(self.cards_in_play[planet_num + 1][i].get_attachments())):
                                if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability()\
                                        == "The Bloodrunna":
                                    if not self.cards_in_play[planet_num + 1][i].\
                                            get_attachments()[j].once_per_phase_used:
                                        self.game.create_reaction("The Bloodrunna", self.name_player,
                                                                  (int(self.number), planet_num, i))
                if not other_player.does_own_reaction_exist("The Bloodrunna"):
                    for i in range(len(other_player.cards_in_play[planet_num + 1])):
                        for j in range(len(other_player.cards_in_play[planet_num + 1][i].get_attachments())):
                            if other_player.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability()\
                                    == "The Bloodrunna":
                                if not other_player.cards_in_play[planet_num + 1][i].\
                                        get_attachments()[j].once_per_phase_used:
                                    self.game.create_reaction("The Bloodrunna", other_player.name_player,
                                                              (int(other_player.number), planet_num, i))
            cato_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_num,
                                                                           "Captain Cato Sicarius",
                                                                           bloodied_relevant=True)
            if cato_check:
                self.game.create_reaction("Captain Cato Sicarius", other_player.name_player,
                                          (int(other_player.number), -1, -1))
            xavaes_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_num,
                                                                             "Xavaes Split-Tongue")
            if xavaes_check:
                self.game.create_reaction("Xavaes Split-Tongue", other_player.name_player,
                                          (int(other_player.number), -1, -1))
            if self.get_card_type_given_pos(planet_num, card_pos) == "Army":
                for i in range(len(self.cards_in_play[planet_num + 1])):
                    if self.get_ability_given_pos(planet_num, i) == "Shrieking Exarch":
                        if not self.game.apoka:
                            self.game.create_reaction("Shrieking Exarch", self.name_player,
                                                      (int(self.number), planet_num, i))
                        elif not self.check_if_already_have_reaction_of_position("Shrieking Exarch", planet_num, i):
                            if not self.get_once_per_phase_used_given_pos(planet_num, i):
                                self.game.create_reaction("Shrieking Exarch", self.name_player,
                                                          (int(self.number), planet_num, i))
                for i in range(len(other_player.cards_in_play[planet_num + 1])):
                    if other_player.get_ability_given_pos(planet_num, i) == "Shrieking Exarch":
                        if not self.game.apoka:
                            self.game.create_reaction("Shrieking Exarch", other_player.name_player,
                                                      (int(other_player.number), planet_num, i))
                        elif not other_player.check_if_already_have_reaction_of_position(
                                "Shrieking Exarch", planet_num, i):
                            if not other_player.get_once_per_phase_used_given_pos(planet_num, i):
                                self.game.create_reaction("Shrieking Exarch", other_player.name_player,
                                                          (int(other_player.number), planet_num, i))
                    if other_player.get_ability_given_pos(planet_num, i, bloodied_relevant=True) == "Vha'shaelhur":
                        if other_player.cards_in_play[planet_num + 1][i].resolving_attack:
                            if not other_player.check_if_already_have_reaction("Vha'shaelhur"):
                                self.game.create_reaction("Vha'shaelhur", other_player.name_player,
                                                          (int(other_player.number), planet_num, i))
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Carnivore Pack":
                self.game.create_reaction("Carnivore Pack", self.name_player,
                                          (int(self.number), -1, -1))
            if self.get_ability_given_pos(planet_num, card_pos) == "Mucolid Spores":
                self.game.create_interrupt("Mucolid Spores", self.name_player, (int(self.number), -1, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Big Shoota Battlewagon":
                self.game.create_reaction("Big Shoota Battlewagon", self.name_player,
                                          (int(self.number), planet_num, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Dark Angels Purifier":
                self.game.create_interrupt("Dark Angels Purifier", self.name_player,
                                           (int(self.number), planet_num, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Shrouded Harlequin":
                self.game.create_reaction("Shrouded Harlequin", self.name_player,
                                          (int(self.number), -1, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "The Dawnsinger":
                self.game.create_reaction("The Dawnsinger", self.name_player,
                                          (int(self.number), -1, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Canoptek Scarab Swarm":
                self.game.create_reaction("Canoptek Scarab Swarm", self.name_player,
                                          (int(self.number), -1, -1))
            if self.surrogate_host_check():
                warlord_pla, warlord_pos = self.get_location_of_warlord()
                if warlord_pla != planet_num:
                    self.valid_surrogate_host[planet_num] = True
                    if not self.check_if_already_have_interrupt("Surrogate Host"):
                        self.game.create_interrupt("Surrogate Host", self.name_player,
                                                   (int(self.number), -1, -1))
            if self.get_faction_given_pos(planet_num, card_pos) == "Space Marines":
                already_apoth = False
                for i in range(len(self.game.reactions_needing_resolving)):
                    if self.game.reactions_needing_resolving[i] == "Secluded Apothecarion":
                        if self.game.player_who_resolves_reaction[i] == self.name_player:
                            already_apoth = True
                if not already_apoth:
                    for i in range(len(self.headquarters)):
                        if self.get_ability_given_pos(-2, i) == "Secluded Apothecarion":
                            if self.get_ready_given_pos(-2, i):
                                self.game.create_reaction("Secluded Apothecarion", self.name_player,
                                                          (int(self.number), -2, i))
            self.cards_recently_destroyed.append(self.cards_in_play[planet_num + 1][card_pos].get_name())
            self.add_card_in_play_to_discard(planet_num, card_pos)
            self.game.queued_sound = "destroy"

    def exhaust_all_cards_of_ability(self, card_name):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == card_name:
                self.exhaust_given_pos(-2, i)
            for k in range(len(self.headquarters[i].get_attachments())):
                if self.headquarters[i].get_attachments()[k].get_ability() == card_name:
                    self.headquarters[i].get_attachments()[k].exhaust_card()
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == card_name:
                    self.exhaust_given_pos(i, j)
                for k in range(len(self.cards_in_play[i + 1][j].get_attachments())):
                    if self.cards_in_play[i + 1][j].get_attachments()[k].get_ability() == card_name:
                        self.cards_in_play[i + 1][j].get_attachments()[k].exhaust_card()

    def destroy_all_cards_at_planet(self, planet_num, ignore_uniques=True, enemy_event=True):
        i = 0
        while i < len(self.cards_in_play[planet_num + 1]):
            if ignore_uniques:
                if not self.cards_in_play[planet_num + 1][i].get_unique():
                    if not enemy_event:
                        self.destroy_card_in_play(planet_num, i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(planet_num, i):
                        if self.get_ability_given_pos(planet_num, i) == "Flayed Ones Revenants":
                            self.game.create_reaction("Flayed Ones Revenants", self.name_player,
                                                      (int(self.number), planet_num, -1))
                        self.destroy_card_in_play(planet_num, i)
                        i = i - 1
                i = i + 1
            else:
                self.destroy_card_in_play(planet_num, i)

    def summon_token_at_planet(self, token_name, planet_num, already_exhausted=False):
        card = FindCard.find_card(token_name, self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)
        if card.get_name() != "FINAL CARD":
            limit = 10
            if card.get_name() == "Cultist":
                if self.search_for_card_everywhere("Sivarla Soulbinder"):
                    limit = 2
            if self.count_copies_in_play(card.get_name()) < limit:
                self.add_card_to_planet(card, planet_num, already_exhausted=already_exhausted)

    def summon_token_at_hq(self, token_name, amount=1):
        card = FindCard.find_card(token_name, self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)
        if card.get_name() != "FINAL CARD":
            limit = 10
            if card.get_name() == "Cultist":
                if self.search_for_card_everywhere("Sivarla Soulbinder"):
                    limit = 2
            for _ in range(amount):
                if self.count_copies_in_play(card.get_name()) < limit:
                    self.add_to_hq(card)

    def remove_card_from_play(self, planet_num, card_pos):
        del self.cards_in_play[planet_num + 1][card_pos]
        self.adjust_own_reactions(planet_num, card_pos)
        self.adjust_own_interrupts(planet_num, card_pos)
        self.adjust_last_def_pos(planet_num, card_pos)
        self.adjust_own_damage(planet_num, card_pos)

    def remove_card_from_hq(self, card_pos):
        del self.headquarters[card_pos]
        self.adjust_own_reactions(-2, card_pos)
        self.adjust_own_interrupts(-2, card_pos)
        self.adjust_last_def_pos(-2, card_pos)

    def add_card_in_play_to_discard(self, planet_num, card_pos):
        if planet_num == -2:
            self.add_card_in_hq_to_discard(card_pos)
            return None
        self.game.reactions_on_destruction_permitted = True
        other_player = self.game.p1
        if other_player.name_player == self.name_player:
            other_player = self.game.p2
        card = self.cards_in_play[planet_num + 1][card_pos]
        card_name = card.get_name()
        if card.actually_a_deepstrike:
            card_name = card.deepstrike_card_name
        if card.get_card_type() == "Army":
            for i in range(len(self.cards_in_play[planet_num + 1])):
                if self.get_ability_given_pos(planet_num, i) == "Cadian Mortar Squad":
                    if not self.check_if_already_have_reaction_of_position("Cadian Mortar Squad", planet_num, i):
                        self.game.create_reaction("Cadian Mortar Squad", self.name_player,
                                                  (int(self.number), planet_num, i))
                for j in range(len(self.cards_in_play[planet_num + 1][i].get_attachments())):
                    if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability() \
                            == "Commissarial Bolt Pistol":
                        self.game.create_reaction("Commissarial Bolt Pistol", self.name_player,
                                                  (int(self.number), planet_num, i))
            if self.get_faction_given_pos(planet_num, card_pos) == "Astra Militarum":
                if not self.check_for_trait_given_pos(planet_num, card_pos, "Elysia") and not \
                        self.check_for_trait_given_pos(planet_num, card_pos, "Saint"):
                    for i in range(len(self.cards_in_play[planet_num + 1])):
                        if self.get_ability_given_pos(planet_num, i) == "Saint Erika":
                            self.game.create_reaction("Saint Erika", self.name_player,
                                                      (int(self.number), planet_num, i))
            if self.check_for_trait_given_pos(planet_num, card_pos, "Harlequin"):
                if self.search_hand_for_card("The Dance Without End") and self.resources > 0:
                    if not self.check_if_already_have_reaction("The Dance Without End"):
                        self.game.create_reaction("The Dance Without End", self.name_player,
                                                  (int(self.number), planet_num, -1))
        if card.get_card_type() != "Token":
            if self.search_planet_attachments(planet_num, "Fungal Infestation"):
                self.game.create_reaction("Fungal Infestation", self.name_player, (int(self.number), planet_num, -1))
        for i in range(len(card.get_attachments())):
            owner = card.get_attachments()[i].name_owner
            if card.get_attachments()[i].get_ability() == "Straken's Cunning":
                self.game.create_reaction("Straken's Cunning", owner, (int(self.number), -1, -1))
            if card.get_attachments()[i].get_ability() == "Escort Drone":
                self.game.create_interrupt("Escort Drone", owner, (int(self.number), planet_num, -1))
            if card.get_attachments()[i].get_ability() == "The Shadow Suit":
                self.game.create_interrupt("The Shadow Suit", owner, (int(self.number), -1, -1))
            if card.get_attachments()[i].get_ability() == "M35 Galaxy Lasgun":
                self.game.create_interrupt("M35 Galaxy Lasgun", owner, (int(self.number), -1, -1))
            if card.get_attachments()[i].get_ability() == "Mark of Slaanesh":
                self.game.create_interrupt("Mark of Slaanesh", owner, (int(self.number), planet_num, -1))
            if card.get_attachments()[i].get_ability() == "Transcendent Blessing":
                self.game.create_interrupt("Transcendent Blessing", owner, (int(self.number), planet_num, -1))
            if card.get_attachments()[i].get_ability() == "Banner of the Cult" \
                    and not card.get_attachments()[i].from_magus_harid:
                self.game.create_interrupt("Banner of the Cult", owner, (int(self.number), planet_num, -1))
            if card.get_attachments()[i].from_front_line_rhinos:
                self.game.create_interrupt("First Line Rhinos", owner, (int(self.number), planet_num, -1),
                                           extra_info=card.get_attachments()[i].get_name())
            if card.get_attachments()[i].from_magus_harid:
                att_card_type = card.get_attachments()[i].get_card_type()
                if att_card_type == "Army" or att_card_type == "Attachment":
                    if owner == other_player.name_player:
                        other_player.magus_harid_waiting_cards.append(card.get_attachments()[i].get_name())
                        self.game.create_interrupt("Magus Harid", other_player.name_player,
                                                   (int(other_player.number), planet_num, -1))
                    else:
                        self.magus_harid_waiting_cards.append(card.get_attachments()[i].get_name())
                        self.game.create_interrupt("Magus Harid", self.name_player,
                                                   (int(self.number), planet_num, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Straken's Command Squad":
            self.game.create_reaction("Straken's Command Squad", self.name_player, (int(self.number), planet_num, -1))
        if self.get_ability_given_pos(planet_num, card_pos) == "Krieg Armoured Regiment":
            self.game.create_reaction("Krieg Armoured Regiment", self.name_player, (int(self.number), planet_num, -1))
        if self.get_faction_given_pos(planet_num, card_pos) == "Necrons":
            if self.search_card_in_hq("Endless Legions", ready_relevant=True):
                self.game.create_reaction("Endless Legions", self.name_player,
                                          (int(self.number), -1, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Elusive Escort":
            temp_card_name = self.cards_in_play[planet_num + 1][card_pos].misc_string
            if temp_card_name:
                if temp_card_name in self.cards_removed_from_game:
                    self.cards_removed_from_game.remove(temp_card_name)
                    del self.cards_removed_from_game_hidden[0]
                    self.cards.append(temp_card_name)
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Interrogator Acolyte":
            self.game.create_interrupt("Interrogator Acolyte", self.name_player, (int(self.number), planet_num, -1))
        if self.get_ability_given_pos(planet_num, card_pos) == "Kabalite Halfborn":
            self.game.create_reaction("Kabalite Halfborn", self.name_player, (int(self.number), -1, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "The Sun Prince":
            self.game.create_interrupt("The Sun Prince", self.name_player, (int(self.number), planet_num, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Vanguard Soldiers":
            self.game.create_interrupt("Vanguard Soldiers", self.name_player, (int(self.number), planet_num, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Raging Daemonhost":
            self.game.create_interrupt("Raging Daemonhost", self.name_player, (int(self.number), planet_num, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Growing Tide":
            if self.game.round_number == planet_num:
                self.game.create_interrupt("Growing Tide", self.name_player, (int(self.number), planet_num, -1))
        condition_present = False
        for i in range(len(card.get_attachments())):
            if card.get_attachments()[i].get_ability() == "Mark of Chaos":
                owner = card.get_attachments()[i].name_owner
                self.game.create_reaction("Mark of Chaos", owner, (int(self.number), planet_num, -1))
            if card.get_attachments()[i].check_for_a_trait("Condition"):
                condition_present = True
        if condition_present:
            if not self.game.infested_planets[planet_num]:
                if other_player.search_card_in_hq("Prey on the Weak", ready_relevant=True):
                    other_player.valid_prey_on_the_weak[planet_num] = True
                    if not other_player.check_if_already_have_interrupt("Prey on the Weak"):
                        self.game.create_interrupt("Prey on the Weak", other_player.name_player,
                                                   (int(other_player.number), -1, -1))
        if card.check_for_a_trait("Warrior") or card.check_for_a_trait("Soldier"):
            for i in range(len(self.cards)):
                if self.cards[i] == "Elysian Assault Team":
                    already_queued_elysian_assault_team = False
                    for j in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[j] == "Elysian Assault Team":
                            if self.game.player_who_resolves_reaction[j] == self.name_player:
                                already_queued_elysian_assault_team = True
                    if not already_queued_elysian_assault_team:
                        self.game.create_reaction("Elysian Assault Team", self.name_player,
                                                  (int(self.number), planet_num, -1))
        if card.check_for_a_trait("Vehicle"):
            for i in range(len(self.headquarters)):
                if self.get_ability_given_pos(-2, i) == "Truck Wreck Launcha":
                    self.game.create_interrupt("Truck Wreck Launcha", self.name_player,
                                               (int(self.number), -2, i), extra_info=planet_num)
        if self.get_ability_given_pos(planet_num, card_pos) == "Coteaz's Henchmen":
            self.game.create_reaction("Coteaz's Henchmen", self.name_player,
                                      (int(self.number), -1, -1))
        if card.check_for_a_trait("Cultist"):
            for i in range(len(self.cards_in_play[planet_num + 1])):
                if self.get_ability_given_pos(planet_num, i) == "Galvax the Bloated":
                    self.game.create_reaction("Galvax the Bloated", self.name_player, (int(self.number), planet_num, i))
        if card.check_for_a_trait("Cultist") or card.check_for_a_trait("Daemon"):
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_ability() == "Murder Cogitator":
                    if self.headquarters[i].get_ready():
                        already_using_murder_cogitator = False
                        for j in range(len(self.game.reactions_needing_resolving)):
                            if self.game.reactions_needing_resolving[j] == "Murder Cogitator":
                                if self.game.player_who_resolves_reaction[j] == self.name_player:
                                    already_using_murder_cogitator = True
                        if not already_using_murder_cogitator:
                            self.game.create_reaction("Murder Cogitator", self.name_player, (int(self.number), -1, -1))
        if other_player.search_card_in_hq("Cato's Stronghold", ready_relevant=True):
            self.game.create_reaction("Cato's Stronghold", other_player.name_player, (int(other_player.number), -1, -1))
        if card.get_ability() == "Enginseer Augur":
            self.game.create_reaction("Enginseer Augur", self.name_player, (int(self.number), -1, -1))
        if card.get_ability() == "3rd Company Tactical Squad":
            self.game.create_interrupt("3rd Company Tactical Squad", self.name_player, (int(self.number), -1, -1))
        if card.get_ability() == "Shok Troopa":
            self.game.create_interrupt("Shok Troopa", self.name_player, (int(self.number), planet_num, -1))
        if card.get_card_type() != "Token":
            if card.name_owner == self.name_player:
                self.add_card_to_discard(card_name)
                self.cards_recently_discarded.append(card_name)
            else:
                dis_player = self.game.p1
                if self.game.name_1 == self.name_player:
                    dis_player = self.game.p2
                dis_player.add_card_to_discard(card_name)
        if card.get_card_type() == "Army":
            if self.check_for_trait_given_pos(planet_num, card_pos, "Ecclesiarchy") or \
                    self.check_for_trait_given_pos(planet_num, card_pos, "Grey Knights"):
                for i in range(len(self.headquarters)):
                    if self.get_ability_given_pos(-2, i) == "Zealous Cantus":
                        self.game.create_reaction("Zealous Cantus", self.name_player, (int(self.number), -2, i))
                for i in range(7):
                    for j in range(len(self.cards_in_play[i + 1])):
                        if self.get_ability_given_pos(i, j) == "Zealous Cantus":
                            self.game.create_reaction("Zealous Cantus", self.name_player, (int(self.number), i, j))
            if self.check_for_warlord(planet_num):
                self.stored_targets_the_emperor_protects.append(card_name)
            if self.check_for_trait_given_pos(planet_num, card_pos, "Transport"):
                if self.get_faction_given_pos(planet_num, card_pos) == "Astra Militarum":
                    if self.search_for_card_everywhere("Commissar Somiel"):
                        self.game.create_reaction("Commissar Somiel", self.name_player, (int(self.number), -1, -1))

        if card.has_hive_mind:
            for i in range(len(self.headquarters)):
                if self.get_ability_given_pos(-2, i) == "Hive Ship Tendrils":
                    self.game.create_reaction("Hive Ship Tendrils", self.name_player, (self.number, -2, i))
        self.discard_attachments_from_card(planet_num, card_pos)
        self.remove_card_from_play(planet_num, card_pos)

    def search_faith_at_planet(self, planet_pos):
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.get_faith_given_pos(planet_pos, i) > 0:
                return True
        return False

    def add_card_in_hq_to_discard(self, card_pos):
        self.game.reactions_on_destruction_permitted = True
        card = self.headquarters[card_pos]
        card_name = card.get_name()
        if card.actually_a_deepstrike:
            card_name = card.deepstrike_card_name
        planet_num = -2
        if card.get_is_unit():
            if card.check_for_a_trait("Cultist") or card.check_for_a_trait("Daemon"):
                for i in range(len(self.headquarters)):
                    if self.headquarters[i].get_ability() == "Murder Cogitator":
                        if self.headquarters[i].get_ready():
                            already_using_murder_cogitator = False
                            for j in range(len(self.game.reactions_needing_resolving)):
                                if self.game.reactions_needing_resolving[j] == "Murder Cogitator":
                                    already_using_murder_cogitator = True
                            if not already_using_murder_cogitator:
                                self.game.create_reaction("Murder Cogitator", self.name_player,
                                                          (int(self.number), -2, -1))
            if self.check_for_trait_given_pos(-2, card_pos, "Transport"):
                if self.get_faction_given_pos(-2, card_pos) == "Astra Militarum":
                    if self.search_for_card_everywhere("Commissar Somiel"):
                        self.game.create_reaction("Commissar Somiel", self.name_player, (int(self.number), -1, -1))
            for i in range(len(card.get_attachments())):
                owner = card.get_attachments()[i].name_owner
                if card.get_attachments()[i].get_ability() == "Straken's Cunning":
                    self.game.create_reaction("Straken's Cunning", owner, (int(self.number), -1, -1))
                if card.get_attachments()[i].get_ability() == "Transcendent Blessing":
                    self.game.create_interrupt("Transcendent Blessing", owner, (int(self.number), -1, -1))
                if card.get_attachments()[i].get_ability() == "Escort Drone":
                    self.game.create_interrupt("Escort Drone", owner, (int(self.number), -2, -1))
                if card.get_attachments()[i].get_ability() == "The Shadow Suit":
                    self.game.create_interrupt("The Shadow Suit", owner, (int(self.number), -1, -1))
                if card.get_attachments()[i].get_ability() == "M35 Galaxy Lasgun":
                    self.game.create_interrupt("M35 Galaxy Lasgun", owner, (int(self.number), -1, -1))
        if card.get_card_type() == "Army":
            if self.check_for_trait_given_pos(-2, card_pos, "Ecclesiarchy") or \
                    self.check_for_trait_given_pos(-2, card_pos, "Grey Knights"):
                for i in range(len(self.headquarters)):
                    if self.get_ability_given_pos(-2, i) == "Zealous Cantus":
                        self.game.create_reaction("Zealous Cantus", self.name_player, (int(self.number), -2, i))
                for i in range(7):
                    for j in range(len(self.cards_in_play[i + 1])):
                        if self.get_ability_given_pos(i, j) == "Zealous Cantus":
                            self.game.create_reaction("Zealous Cantus", self.name_player, (int(self.number), i, j))
        if card.get_ability() == "Enginseer Augur":
            self.game.create_reaction("Enginseer Augur", self.name_player, (int(self.number), -1, -1))
        if card.get_ability() == "3rd Company Tactical Squad":
            self.game.create_interrupt("3rd Company Tactical Squad", self.name_player, (int(self.number), -1, -1))
        if card.get_ability() == "Kabalite Halfborn":
            self.game.create_reaction("Kabalite Halfborn", self.name_player, (int(self.number), -1, -1))
        if self.get_ability_given_pos(-2, card_pos) == "Coteaz's Henchmen":
            self.game.create_reaction("Coteaz's Henchmen", self.name_player, (int(self.number), -1, -1))
        if self.get_ability_given_pos(-2, card_pos) == "Elusive Escort":
            temp_card_name = self.headquarters[card_pos].misc_string
            if temp_card_name:
                if temp_card_name in self.cards_removed_from_game:
                    self.cards_removed_from_game.remove(temp_card_name)
                    del self.cards_removed_from_game_hidden[0]
                    self.cards.append(temp_card_name)
        if card.get_ability() == "Interrogator Acolyte":
            self.game.create_interrupt("Interrogator Acolyte", self.name_player, (int(self.number), -2, -1))
        if card.get_ability() == "Vanguard Soldiers":
            self.game.create_interrupt("Vanguard Soldiers", self.name_player, (int(self.number), -2, -1))
        if self.get_faction_given_pos(-2, card_pos) == "Necrons":
            if self.search_card_in_hq("Endless Legions", ready_relevant=True):
                self.game.create_reaction("Endless Legions", self.name_player,
                                          (int(self.number), -1, -1))
        if card.get_card_type() == "Support":
            for i in range(len(self.headquarters)):
                if self.get_ability_given_pos(-2, i) == "Fortress of Mangeras":
                    self.game.create_reaction("Fortress of Mangeras", self.name_player,
                                              (int(self.number), -2, i))
        if card.get_card_type() != "Token":
            if card.name_owner == self.name_player:
                self.add_card_to_discard(card_name)
                self.cards_recently_discarded.append(card_name)
            else:
                dis_player = self.game.p1
                if self.game.name_1 == self.name_player:
                    dis_player = self.game.p2
                dis_player.add_card_to_discard(card_name)
        if card.has_hive_mind:
            for i in range(len(self.headquarters)):
                if self.get_ability_given_pos(-2, i) == "Hive Ship Tendrils":
                    self.game.create_reaction("Hive Ship Tendrils", self.name_player, (self.number, -2, i))
        self.discard_attachments_from_card(-2, card_pos)
        self.remove_card_from_hq(card_pos)

    def retreat_warlord(self):
        for i in range(len(self.cards_in_play[0])):
            if not self.cards_in_play[i + 1]:
                pass
            else:
                j = 0
                while j < len(self.cards_in_play[i + 1]):
                    if self.cards_in_play[i + 1][j].get_card_type() == "Warlord":
                        self.move_unit_at_planet_to_hq(i, j)
                        return None
                    j = j + 1
        return None

    def move_unit_at_planet_to_hq(self, planet_id, unit_id):
        print("calling move unit to planet")
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Army":
            if self.defense_battery_check(planet_id):
                self.cards_in_play[planet_id + 1][unit_id].valid_defense_battery_target = True
        other_player = self.get_other_player()
        for i in range(len(other_player.cards_in_play[planet_id + 1])):
            if other_player.get_ability_given_pos(planet_id, i) == "Hydra Flak Tank":
                if not other_player.get_once_per_phase_used_given_pos(planet_id, i):
                    already_reacted = False
                    self.cards_in_play[planet_id + 1][unit_id].valid_defense_battery_target = True
                    for j in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[j] == "Hydra Flak Tank":
                            if self.game.positions_of_unit_triggering_reaction[j] == (int(other_player.number),
                                                                                      planet_id, i):
                                if self.game.player_who_resolves_reaction[j] == other_player.name_player:
                                    already_reacted = True
                    if not already_reacted:
                        self.game.create_reaction("Hydra Flak Tank", other_player.name_player,
                                                  (int(other_player.number), planet_id, i))
        already_homing_beacon = False
        for i in range(len(self.game.reactions_needing_resolving)):
            if self.game.reactions_needing_resolving[0] == "Homing Beacon":
                if self.game.player_who_resolves_reaction[0] == self.name_player:
                    already_homing_beacon = True
        if not already_homing_beacon:
            for i in range(len(self.headquarters)):
                if self.get_ability_given_pos(-2, i) == "Homing Beacon":
                    if self.get_ready_given_pos(-2, i):
                        self.game.create_reaction("Homing Beacon", self.name_player, (int(self.number), -2, i))
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        self.remove_card_from_play(planet_id, unit_id)
        last_element_index = len(self.headquarters) - 1
        for i in range(len(self.headquarters)):
            if i != last_element_index:
                if self.get_ability_given_pos(-2, i) == "Frontline Counsellor":
                    if not self.get_once_per_phase_used_given_pos(-2, i):
                        if not self.check_if_already_have_interrupt_of_position("Frontline Counsellor", self.name_player,
                                                                                (int(self.number), -2, i)):
                            self.game.create_interrupt("Frontline Counsellor", self.name_player,
                                                       (int(self.number), -2, i), extra_info=planet_id)
        for i in range(7):
            if i != planet_id:
                for j in range(len(self.cards_in_play[i + 1])):
                    if self.get_ability_given_pos(i, j) == "Frontline Counsellor":
                        if not self.get_once_per_phase_used_given_pos(i, j):
                            if not self.check_if_already_have_interrupt_of_position("Frontline Counsellor",
                                                                                    self.name_player,
                                                                                    (int(self.number), i, j)):
                                self.game.create_interrupt("Frontline Counsellor", self.name_player,
                                                           (int(self.number), i, j), extra_info=planet_id)
        if self.get_ability_given_pos(-2, last_element_index) == "Growing Tide":
            if planet_id == self.game.round_number:
                self.game.create_interrupt("Growing Tide", self.name_player,
                                           (int(self.number), -2, last_element_index))
        return True

    def resolve_combat_round_ends_effects(self, planet_id):
        can_forward_barracks = False
        self.mork_blessings_count = 0
        self.defensive_protocols_active = False
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.get_ability_given_pos(planet_id, i) == "Anxious Infantry Platoon":
                self.game.create_reaction("Anxious Infantry Platoon", self.name_player,
                                          (int(self.number), planet_id, i))
            if self.get_ability_given_pos(planet_id, i) == "23rd Mechanised Battalion":
                if self.game.combat_round_number == 3:
                    self.game.create_reaction("23rd Mechanised Battalion", self.name_player,
                                              (int(self.number), planet_id, i))
            if self.get_faction_given_pos(planet_id, i) == "Astra Militarum":
                can_forward_barracks = True
        if can_forward_barracks:
            if self.search_card_in_hq("Forward Barracks"):
                self.game.create_reaction("Forward Barracks", self.name_player, (int(self.number), planet_id, -1))
        if self.search_planet_attachments(planet_id, "Planetary Defence Force"):
            self.game.create_reaction("Planetary Defence Force", self.name_player, (int(self.number), planet_id, -1))
        if self.game.get_green_icon(planet_id):
            for i in range(7):
                if i != planet_id:
                    for j in range(len(self.cards_in_play[i + 1])):
                        if self.cards_in_play[i + 1][j].get_ability() == "Taurox APC":
                            self.game.create_reaction("Taurox APC", self.name_player,
                                                      (int(self.number), i, j))

    def special_get_card_type_given_pos(self, sent_in_value):
        if sent_in_value is None:
            return ""
        _, planet_pos, unit_pos = sent_in_value
        return self.get_card_type_given_pos(planet_pos, unit_pos)

    def search_ready_card_at_planet(self, planet_pos):
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if self.get_ready_given_pos(planet_pos, i):
                return True
        return False

    def search_card_type_at_planet(self, planet_id, card_type):
        if planet_id == -2:
            return False
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.get_card_type_given_pos(planet_id, i) == card_type:
                return True
        return False

    def rout_unit(self, planet_id, unit_id):
        if planet_id == -2:
            return False
        if self.get_ability_given_pos(planet_id, unit_id) == "Heavy Flamer Retributor":
            if self.get_has_faith_given_pos(planet_id, unit_id) > 0:
                return False
        if self.get_ability_given_pos(planet_id, unit_id) == "Mars Pattern Hellhound":
            if self.search_card_type_at_planet(planet_id, "Token"):
                return False
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, "Disciple of Excess"):
                return False
        if self.get_ability_given_pos(planet_id, unit_id) == "Charging Juggernaut":
            if self.get_all_attachments_at_pos(planet_id, unit_id):
                if self.game.combat_round_number < 2:
                    return False
        if self.get_ability_given_pos(planet_id, unit_id) == "Mindless Pain Addict":
            return False
        if self.game.imperial_blockades_active[planet_id] > 0:
            other_player = self.get_other_player()
            resources_to_spend = self.game.imperial_blockades_active[planet_id]
            if not other_player.spend_resources(resources_to_spend):
                self.game.queued_message = "Important Info: Imperial Blockade prevented the Rout."
                return False
            else:
                self.game.queued_message = "Important Info: " + str(resources_to_spend) + \
                                           " resources were spent due to Imperial Blockade."
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Army":
            if self.get_faction_given_pos(planet_id, unit_id) == "Astra Militarum":
                every_worr_check = self.search_for_card_everywhere("Broderick Worr")
                if every_worr_check:
                    if self.game.get_green_icon(planet_id):
                        return False
            if self.defense_battery_check(planet_id):
                self.cards_in_play[planet_id + 1][unit_id].valid_defense_battery_target = True
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        self.adjust_own_reactions(planet_id, unit_id)
        self.adjust_own_interrupts(planet_id, unit_id)
        last_element_hq = len(self.headquarters) - 1
        self.exhaust_given_pos(-2, last_element_hq)
        del self.cards_in_play[planet_id + 1][unit_id]
        if self.search_hand_for_card("Shas'el Lyst"):
            self.game.create_interrupt("Shas'el Lyst", self.name_player, (int(self.number), -1, -1))
        return True

    def get_keywords_given_pos(self, planet_pos, unit_pos, printed=True):
        keywords = []
        if planet_pos == -2:
            return keywords
        if printed:
            if self.cards_in_play[planet_pos + 1][unit_pos].by_base_brutal:
                keywords.append("Brutal")
            if self.cards_in_play[planet_pos + 1][unit_pos].by_base_flying:
                keywords.append("Flying")
            if self.cards_in_play[planet_pos + 1][unit_pos].by_base_armorbane:
                keywords.append("Armorbane")
            if self.cards_in_play[planet_pos + 1][unit_pos].by_base_mobile:
                keywords.append("Mobile")
            if self.cards_in_play[planet_pos + 1][unit_pos].by_base_area_effect > 0:
                keywords.append("Area Effect")
                self.game.stored_area_effect_value = self.cards_in_play[planet_pos + 1][unit_pos].by_base_area_effect
            if self.cards_in_play[planet_pos + 1][unit_pos].by_base_ranged:
                keywords.append("Ranged")
        else:
            if self.get_brutal_given_pos(planet_pos, unit_pos):
                keywords.append("Brutal")
            if self.get_flying_given_pos(planet_pos, unit_pos):
                keywords.append("Flying")
            if self.get_armorbane_given_pos(planet_pos, unit_pos):
                keywords.append("Armorbane")
            if self.get_retaliate_given_pos(planet_pos, unit_pos) > 0:
                keywords.append("Retaliate")
            if self.get_area_effect_given_pos(planet_pos, unit_pos) > 0:
                keywords.append("Area Effect")
            if self.get_sweep_given_pos(planet_pos, unit_pos) > 0:
                kewords.append("Sweep")
            if self.get_ranged_given_pos(planet_pos, unit_pos):
                keywords.append("Ranged")
            if self.get_lumbering_given_pos(planet_pos, unit_pos):
                keywords.append("Lumbering")
            if self.cards_in_play[planet_pos + 1][unit_pos].get_ambush():
                keywords.append("Ambush")
            if self.get_mobile_given_pos(planet_pos, unit_pos):
                keywords.append("Mobile")
        return keywords

    def reset_can_retreat_values(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].can_retreat = True
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].can_retreat = True

    def defense_battery_check(self, planet_id):
        if self.number == "1":
            enemy_player = self.game.p2
        else:
            enemy_player = self.game.p1
        for i in range(len(enemy_player.attachments_at_planet[planet_id])):
            if enemy_player.attachments_at_planet[planet_id][i].get_name() == "Defense Battery":
                if enemy_player.attachments_at_planet[planet_id][i].get_ready():
                    enemy_player.attachments_at_planet[planet_id][i].defense_battery_activated = True
                    already_defense_battery = False
                    for k in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[k] == "Defense Battery":
                            if self.game.player_who_resolves_reaction[k] == enemy_player.name_player:
                                already_defense_battery = True
                    if not already_defense_battery:
                        self.game.create_reaction("Defense Battery", enemy_player.name_player,
                                                  (int(self.number), planet_id, -1))
                    return True
        return False

    def retreat_unit(self, planet_id, unit_id, exhaust=False):
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Army":
            if self.get_ability_given_pos(planet_id, unit_id) == "Growing Tide":
                return False
            if self.get_ability_given_pos(planet_id, unit_id) == "Mindless Pain Addict":
                return False
            own_umbral_check = self.search_card_at_planet(planet_id, "Umbral Preacher")
            enemy_umbral_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_id,
                                                                                   "Umbral Preacher")
            if own_umbral_check or enemy_umbral_check:
                return False
            if self.get_faction_given_pos(planet_id, unit_id) == "Astra Militarum":
                every_worr_check = self.search_for_card_everywhere("Broderick Worr")
                if every_worr_check:
                    if self.game.get_green_icon(planet_id):
                        return False
            own_worr_check = self.search_card_at_planet(planet_id, "Broderick Worr", bloodied_relevant=True)
            enemy_worr_check = self.game.request_search_for_enemy_card_at_planet(
                self.number, planet_id, "Broderick Worr", bloodied_relevant=True)
            if own_worr_check or enemy_worr_check:
                self.destroy_card_in_play(planet_id, unit_id)
                return False
        if not self.cards_in_play[planet_id + 1][unit_id].can_retreat:
            return False
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Army":
            if self.defense_battery_check(planet_id):
                self.cards_in_play[planet_id + 1][unit_id].valid_defense_battery_target = True
        mork_count = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.get_ability_given_pos(planet_id, i) == "Morkai Rune Priest":
                mork_count += 1
        if self.get_ability_given_pos(planet_id, unit_id) == "Armored Fist Squad":
            self.game.create_interrupt("Armored Fist Squad", self.name_player,
                                       (int(self.number), planet_id, -1))
        if self.cards_in_play[planet_id + 1][unit_id].embarked_squads_active:
            self.game.create_interrupt("Embarked Squads", self.name_player,
                                       (int(self.number), planet_id, -1))
        if self.number == "1":
            enemy_player = self.game.p2
        else:
            enemy_player = self.game.p1
        for i in range(len(enemy_player.cards_in_play[planet_id + 1])):
            if enemy_player.get_ability_given_pos(planet_id, i) == "Morkai Rune Priest":
                mork_count += 1
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        last_element_hq = len(self.headquarters) - 1
        if self.headquarters[last_element_hq].check_for_a_trait("Space Wolves", self.etekh_trait):
            mork_count = 0
        for i in range(mork_count):
            self.assign_damage_to_pos(-2, last_element_hq, 1, context="Morkai Rune Priest", rickety_warbuggy=True)
        if exhaust:
            self.exhaust_given_pos(-2, last_element_hq)
        self.adjust_own_reactions(planet_id, unit_id)
        self.adjust_own_interrupts(planet_id, unit_id)
        del self.cards_in_play[planet_id + 1][unit_id]
        return True

    def ready_all_in_headquarters(self):
        for i in range(len(self.headquarters)):
            self.ready_given_pos(-2, i)
            if self.game.phase == "HEADQUARTERS":
                for j in range(len(self.headquarters[i].get_attachments())):
                    self.headquarters[i].get_attachments()[j].ready_card()

    def ready_all_in_play(self):
        for i in range(len(self.cards_in_play[0])):
            self.ready_all_at_planet(i)
        self.ready_all_in_headquarters()

    def ready_all_at_planet(self, planet_id):
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.game.phase != "COMBAT":
                self.ready_given_pos(planet_id, i)
            elif not self.search_attachments_at_pos(planet_id, i, "Huge Chain-Choppa"):
                self.ready_given_pos(planet_id, i)
            if self.game.phase == "HEADQUARTERS":
                for j in range(len(self.cards_in_play[planet_id + 1][i].get_attachments())):
                    self.cards_in_play[planet_id + 1][i].get_attachments()[j].ready_card()

    def refresh_all_once_per_round(self):
        for i in range(len(self.headquarters)):
            self.set_once_per_round_used_given_pos(-2, i, True)
        for j in range(7):
            for i in range(len(self.cards_in_play[j + 1])):
                self.set_once_per_round_used_given_pos(j, i, True)

    def ready_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            if self.headquarters[unit_id].cannot_ready_hq_phase and self.game.phase == "HEADQUARTERS":
                return None
            if self.headquarters[unit_id].cannot_ready_phase:
                return None
            was_ready = self.headquarters[unit_id].get_ready()
            self.headquarters[unit_id].ready_card()
            is_ready = self.headquarters[unit_id].get_ready()
            print(was_ready, is_ready)
            if not was_ready and is_ready:
                print("check if old one eye")
                if self.headquarters[unit_id].get_ability(bloodied_relevant=True) == "Old One Eye":
                    print("is old one")
                    if not self.headquarters[unit_id].get_once_per_round_used():
                        if self.headquarters[unit_id].get_damage() > 0:
                            self.game.create_reaction("Old One Eye", self.name_player,
                                                      (int(self.number), planet_id, unit_id))
                if self.get_ability_given_pos(planet_id, unit_id) == "Salamander Flamer Squad":
                    self.game.create_reaction("Salamander Flamer Squad", self.name_player,
                                              (int(self.number), planet_id, unit_id))
            return None
        if self.cards_in_play[planet_id + 1][unit_id].cannot_ready_hq_phase and self.game.phase == "HEADQUARTERS":
            return None
        if self.cards_in_play[planet_id + 1][unit_id].cannot_ready_phase:
            return None
        was_ready = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        self.cards_in_play[planet_id + 1][unit_id].ready_card()
        is_ready = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        if not was_ready and is_ready:
            if self.cards_in_play[planet_id + 1][unit_id].get_ability(bloodied_relevant=True) == "Old One Eye":
                if not self.cards_in_play[planet_id + 1][unit_id].get_once_per_round_used():
                    if self.cards_in_play[planet_id + 1][unit_id].get_damage() > 0:
                        self.game.create_reaction("Old One Eye", self.name_player,
                                                  (int(self.number), planet_id, unit_id))
            if self.get_ability_given_pos(planet_id, unit_id) == "Blitza-Bommer":
                self.game.create_reaction("Blitza-Bommer", self.name_player,
                                          (int(self.number), planet_id, unit_id))
            if self.get_ability_given_pos(planet_id, unit_id) == "Salamander Flamer Squad":
                self.game.create_reaction("Salamander Flamer Squad", self.name_player,
                                          (int(self.number), planet_id, unit_id))
            if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Goff Brawlers":
                self.game.create_reaction("Goff Brawlers", self.name_player, (int(self.number), planet_id, unit_id))
        return None

    def check_if_units_present(self, planet_id):
        if not self.cards_in_play[planet_id + 1]:
            return 0
        return 1

    def retreat_all_at_planet(self, planet_id):
        while self.cards_in_play[planet_id + 1]:
            self.retreat_unit(planet_id, 0)

    def move_all_at_planet_to_hq(self, planet_id):
        while self.cards_in_play[planet_id + 1]:
            self.move_unit_at_planet_to_hq(planet_id, 0)

    def discard_planet_attachments(self, planet_id):
        while self.attachments_at_planet[planet_id]:
            ability = self.attachments_at_planet[planet_id][0].get_ability()
            del self.attachments_at_planet[planet_id][0]
            self.add_card_to_discard(ability)

    def capture_planet(self, planet_id, planet_cards):
        planet_name = self.game.original_planet_array[planet_id]
        print("Attempting to capture planet.")
        print("Planet to capture:", planet_name)
        other_player = self.get_other_player()
        self.discard_planet_attachments(planet_id)
        other_player.discard_planet_attachments(planet_id)
        print(planet_id)
        if self.broken_sigil_planet == planet_id:
            if self.broken_sigil_effect:
                self.game.create_interrupt("The Broken Sigil " + self.broken_sigil_effect, self.name_player,
                                           (int(self.number), -1, -1))
        if other_player.broken_sigil_planet == planet_id:
            if other_player.broken_sigil_effect:
                self.game.create_interrupt("The Broken Sigil " + other_player.broken_sigil_effect, self.name_player,
                                           (int(self.number), -1, -1))
        if other_player.search_hand_for_card("Erupting Aberrants"):
            self.game.create_reaction("Erupting Aberrants", other_player.name_player,
                                      (int(other_player.number), -1, -1))
        for i in range(len(self.headquarters)):
            if self.get_ability_given_pos(-2, i) == "Hive Fleet Behemoth":
                self.game.create_reaction("Hive Fleet Behemoth", self.name_player, (int(self.number), -2, i))
        for i in range(len(other_player.headquarters)):
            if other_player.get_ability_given_pos(-2, i) == "Dal'yth Sept":
                self.game.create_reaction("Dal'yth Sept", other_player.name_player,
                                          (int(other_player.number), -2, i))
            if other_player.get_ability_given_pos(-2, i) == "The Phalanx":
                self.game.create_reaction("The Phalanx", other_player.name_player,
                                          (int(other_player.number), -2, i))
        for letter in planet_name:
            if letter == "_":
                planet_name = planet_name.replace(letter, " ")
        if self.game.grand_plan_active:
            self.game.grand_plan_active = False
            self.game.grand_plan_queued.append(
                (planet_name, self.game.round_number + 2, int(self.number),
                 self.game.p1.played_grand_plan, self.game.p2.played_grand_plan)
            )
            self.game.p1.played_grand_plan = False
            self.game.p2.played_grand_plan = False
            return 0
        if self.flayed_mask_active:
            self.flayed_mask_active = False
            return 0
        i = 0
        while planet_cards[i].get_name() != "FINAL CARD":
            print(planet_cards[i].get_name(), planet_name)
            if planet_cards[i].get_name() == planet_name:
                self.victory_display.append(planet_cards[i])
                self.print_victory_display()
                self.print_icons_on_captured()
                return 0
            else:
                i += 1
        return -1

    def print_victory_display(self):
        print("Cards in victory display:")
        for i in range(len(self.victory_display)):
            print(self.victory_display[i].get_name())

    def get_icons_on_captured(self):
        total_icons = [0, 0, 0]
        for i in range(len(self.victory_display)):
            if self.victory_display[i].get_red():
                total_icons[0] += 1
            if self.victory_display[i].get_blue():
                total_icons[1] += 1
            if self.victory_display[i].get_green():
                total_icons[2] += 1
        return total_icons

    def print_icons_on_captured(self):
        total_icons = [0, 0, 0]
        for i in range(len(self.victory_display)):
            if self.victory_display[i].get_red():
                total_icons[0] += 1
            if self.victory_display[i].get_blue():
                total_icons[1] += 1
            if self.victory_display[i].get_green():
                total_icons[2] += 1
        print("Total Icons:", total_icons)
