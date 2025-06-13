from . import FindCard
import random
from random import shuffle
import copy
import threading


def clean_received_deck(raw_deck):
    split_deck = raw_deck.split("----------------------------------------------------------------------")
    split_deck = "\n".join(split_deck)
    split_deck = split_deck.split("\n")
    split_deck = [x for x in split_deck if x]
    del split_deck[0]
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
    print(deck_as_single_cards)
    return deck_as_single_cards


class Player:
    def __init__(self, name, number, card_array, cards_dict, game):
        self.game = game
        self.card_array = card_array
        self.cards_dict = cards_dict
        self.number = str(number)
        self.name_player = name
        self.position_activated = []
        self.has_initiative = True
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
        self.mulligan_done = False
        self.synapse_list = ["Savage Warrior Prime", "Blazing Zoanthrope", "Gravid Tervigon",
                             "Stalking Lictor", "Venomthrope Polluter", "Keening Maleceptor"]
        self.tyranid_warlord_list = ["Old One Eye", "The Swarmlord"]
        self.synapse_name = ""
        self.warlord_faction = ""
        self.consumption_sacs_list = [True, True, True, True, True, True, True]
        self.dark_possession_active = False
        self.force_due_to_dark_possession = False
        self.pos_card_dark_possession = -1
        self.dark_possession_remove_after_play = False
        self.enslaved_faction = ""
        self.chosen_enslaved_faction = False
        self.nahumekh_value = 0
        self.last_hand_string = ""
        self.last_hq_string = ""
        self.last_planet_strings = ["", "", "", "", "", "", ""]
        self.last_resources_string = ""
        self.last_discard_string = ""
        self.used_reanimation_protocol = False
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
        self.illuminor_szeras_relevant = False
        self.ichor_gauntlet_target = ""
        self.permitted_commit_locs_warlord = [True, True, True, True, True, True, True]
        self.illegal_commits_warlord = 0
        self.illegal_commits_synapse = 0
        self.primal_howl_used = False
        self.discard_inquis_caius_wroth = False
        self.enemy_has_wyrdboy_stikk = False
        self.accept_any_challenge_used = False
        self.rok_bombardment_active = []
        self.master_warpsmith_count = 0
        self.gut_and_pillage_used = False
        self.valid_planets_berzerker_warriors = [False, False, False, False, False, False, False]
        self.war_of_ideas_active = False
        self.cards_in_reserve = [[], [], [], [], [], [], []]
        self.the_princes_might_active = [False, False, False, False, False, False, False]
        self.hit_by_gorgul = False
        self.concealing_darkness_active = False
        self.defensive_protocols_active = False
        self.death_serves_used = False
        self.highest_death_serves_value = 0
        self.highest_cost_invasion_site = 0

    def put_card_into_reserve(self, card, planet_pos):
        if self.spend_resources(1):
            self.cards_in_reserve[planet_pos].append(copy.deepcopy(card))
            return True
        return False

    async def setup_player(self, raw_deck, planet_array):
        self.condition_player_main.acquire()
        deck_list = clean_received_deck(raw_deck)
        self.headquarters.append(copy.deepcopy(FindCard.find_card(deck_list[0], self.card_array, self.cards_dict)))
        self.warlord_faction = self.headquarters[0].get_faction()
        if self.headquarters[0].get_name() == "Urien Rakarth":
            self.urien_relevant = True
        if self.headquarters[0].get_name() == "Gorzod":
            self.gorzod_relevant = True
        if self.headquarters[0].get_name() == "Subject Omega-X62113":
            self.subject_omega_relevant = True
        if self.headquarters[0].get_name() == "Grigory Maksim":
            self.grigory_maksim_relevant = True
        if self.headquarters[0].get_name() == "Illuminor Szeras":
            self.illuminor_szeras_relevant = True
        self.deck = deck_list[1:]
        if self.warlord_faction == "Tyranids":
            i = 0
            while i < len(self.deck):
                if self.deck[i] in self.synapse_list:
                    self.headquarters.append(copy.deepcopy(FindCard.find_card(self.deck[i], self.card_array,
                                                                              self.cards_dict)))
                    del self.deck[i]
                i = i + 1
        self.shuffle_deck()
        self.deck_loaded = True
        self.cards_in_play[0] = planet_array
        self.resources = self.headquarters[0].get_starting_resources()
        for i in range(self.headquarters[0].get_starting_cards()):
            self.draw_card()
        print(self.resources)
        print(self.deck)
        print(self.cards_in_play)
        print(self.cards)
        self.print_headquarters()
        await self.send_hand()
        for i in range(len(self.game.game_sockets)):
            await self.game.send_update_message("Setup of " + self.name_player + " finished.")
        await self.send_hq()
        await self.send_units_at_all_planets()
        await self.send_resources()
        if self.game.p1.deck_loaded and self.game.p2.deck_loaded:
            await self.game.start_mulligan()
            await self.game.send_search()
            await self.game.send_info_box()
            self.game.phase = "DEPLOY"
            await self.game.send_update_message(
                self.game.name_1 + " may mulligan their opening hand.")
        self.condition_player_main.notify_all()
        self.condition_player_main.release()

    def resolve_electro_whip(self, planet_pos, unit_pos):
        if planet_pos == -2:
            self.headquarters[unit_pos].cannot_ready_phase = True
            return None
        self.cards_in_play[planet_pos + 1][unit_pos].cannot_ready_phase = True
        return None

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
        if enemy_player.has_initiative:
            return True
        if planet_pos == self.game.last_planet_checked_for_battle:
            if self.search_card_at_planet(planet_pos, "Corpulent Ork"):
                if not enemy_player.search_card_at_planet(planet_pos, "Corpulent Ork", ability_checking=False):
                    return True
        return False

    def add_attachment_to_planet(self, planet_pos, card):
        self.attachments_at_planet[planet_pos].append(copy.deepcopy(card))

    def get_can_play_limited(self):
        return self.can_play_limited

    def set_can_play_limited(self, new_val):
        self.can_play_limited = new_val

    async def send_hand(self, force=False):
        card_string = ""
        if self.cards:
            card_array = self.cards.copy()
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

    async def send_hq(self, force=False):
        joined_string = ""
        if self.headquarters:
            card_strings = []
            for i in range(len(self.headquarters)):
                current_card = self.headquarters[i]
                single_card_string = current_card.get_name()
                single_card_string = single_card_string + "|"
                if current_card.ready:
                    single_card_string += "R|"
                else:
                    single_card_string += "E|"
                card_type = current_card.get_card_type()
                if card_type == "Warlord" or card_type == "Army" or card_type == "Token":
                    single_card_string += str(current_card.get_damage() + current_card.get_indirect_damage())
                else:
                    single_card_string += "0"
                single_card_string += "|"
                if card_type == "Warlord":
                    if current_card.get_bloodied():
                        single_card_string += "B|"
                    else:
                        single_card_string += "H|"
                else:
                    single_card_string += "H|"
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
            joined_string = "GAME_INFO/HQ/" + str(self.number) + "/" + joined_string
        else:
            joined_string = "GAME_INFO/HQ/" + str(self.number)
        if self.last_hq_string != joined_string or force:
            self.last_hq_string = joined_string
            await self.game.send_update_message(joined_string)

    def discard_all_cards_in_reserve(self, planet_id):
        while self.cards_in_reserve[planet_id]:
            self.discard.append(self.cards_in_reserve[planet_id][0].get_name())
            del self.cards_in_reserve[planet_id][0]

    def get_card_type_in_reserve(self, planet_id, unit_id):
        return self.cards_in_reserve[planet_id][unit_id].get_card_type()

    def get_deepstrike_value_given_pos(self, planet_id, unit_id):
        ds_value = self.cards_in_reserve[planet_id][unit_id].get_deepstrike_value()
        other_player = self.game.p1
        if other_player.name_player == self.name_player:
            other_player = self.game.p2
        for i in range(len(other_player.cards_in_play[planet_id + 1])):
            if other_player.get_ability_given_pos(planet_id, i) == "Catachan Tracker":
                ds_value += 2
        return ds_value

    def deepstrike_event(self, planet_id, unit_id):
        ability = self.cards_in_reserve[planet_id][unit_id].get_name()
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
        self.discard.append(ability)
        self.after_any_deepstrike(planet_id)
        del self.cards_in_reserve[planet_id][unit_id]

    def after_any_deepstrike(self, planet_id):
        warlord_pla, warlord_pos = self.get_location_of_warlord()
        if self.get_ability_given_pos(warlord_pla, warlord_pos, bloodied_relevant=True) == "Epistolary Vezuel":
            self.game.create_reaction("Epistolary Vezuel", self.name_player,
                                      (int(self.number), warlord_pla, warlord_pos))
        if self.search_attachments_at_pos(warlord_pla, warlord_pos, "Fulgaris"):
            self.game.create_reaction("Fulgaris", self.name_player,
                                      (int(self.number), warlord_pla, warlord_pos))
        for i in range(len(self.headquarters)):
            if self.get_ability_given_pos(-2, i) == "Deathstorm Drop Pod":
                self.game.create_reaction("Deathstorm Drop Pod", self.name_player,
                                          (int(self.number), planet_id, -1))

    def deepstrike_attachment_extras(self, planet_id):
        self.after_any_deepstrike(planet_id)

    def deepstrike_unit(self, planet_id, unit_id):
        card = self.cards_in_reserve[planet_id][unit_id]
        self.add_card_to_planet(card, planet_id)
        self.after_any_deepstrike(planet_id)
        del self.cards_in_reserve[planet_id][unit_id]
        last_element_index = len(self.cards_in_play[planet_id + 1]) - 1
        ability = self.get_ability_given_pos(planet_id, last_element_index)
        if ability == "8th Company Assault Squad":
            self.game.create_reaction("8th Company Assault Squad", self.name_player,
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
                        single_card_string = single_card_string + "|"
                        if current_card.ready:
                            single_card_string += "R|"
                        else:
                            single_card_string += "E|"
                        single_card_string += str(current_card.get_damage() + current_card.get_indirect_damage())
                        single_card_string += "|"
                        if current_card.get_card_type() == "Warlord":
                            if current_card.get_bloodied():
                                single_card_string += "B"
                            else:
                                single_card_string += "H"
                        else:
                            single_card_string += "H"
                        single_card_string += "|"
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
                    for i in range(len(self.cards_in_reserve[planet_id])):
                        current_card = self.cards_in_reserve[planet_id][i]
                        single_card_string = current_card.get_name()
                        single_card_string = single_card_string + "|"
                        if current_card.ready:
                            single_card_string += "R|"
                        else:
                            single_card_string += "E|"
                        single_card_string += str(current_card.get_damage() + current_card.get_indirect_damage())
                        single_card_string += "|"
                        single_card_string += "D"
                        single_card_string += "|"
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
                    self.assign_damage_to_pos(-2, i, damage)
                    self.headquarters[i].reset_indirect_damage()
                    self.set_aiming_reticle_in_play(-2, i, "blue")
                    if self.game.first_card_damaged:
                        self.game.first_card_damaged = False
                        self.set_aiming_reticle_in_play(-2, i, "red")
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_is_unit():
                    damage = self.cards_in_play[i + 1][j].get_indirect_damage()
                    print("Indirect damage:", damage)
                    if damage > 0:
                        self.assign_damage_to_pos(i, j, damage)
                        self.cards_in_play[i + 1][j].reset_indirect_damage()
                        self.set_aiming_reticle_in_play(i, j, "blue")
                        if self.game.first_card_damaged:
                            self.game.first_card_damaged = False
                            self.set_aiming_reticle_in_play(i, j, "red")

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

    async def send_discard(self, force=False):
        joined_string = "GAME_INFO/DISCARD/" + str(self.number)
        top_card = self.get_top_card_discard()
        if self.discard:
            for i in range(len(self.discard)):
                joined_string += "/" + self.discard[i] + "|"
                if self.aiming_reticle_coords_discard == i:
                    joined_string += self.aiming_reticle_color_discard
        if joined_string != self.last_discard_string or force:
            self.last_discard_string = joined_string
            await self.game.send_update_message(joined_string)

    def search_for_card_everywhere(self, card_name, ability=True, ready_relevant=False, must_own=False,
                                   limit_phase_rel=False):
        for i in range(len(self.headquarters)):
            if self.get_ability_given_pos(-2, i) == card_name:
                if not limit_phase_rel or not self.headquarters[i].once_per_phase_used:
                    return True
            if self.search_attachments_at_pos(-2, i, card_name, ready_relevant=ready_relevant):
                return True
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.get_ability_given_pos(i, j) == card_name:
                    if not limit_phase_rel or not self.cards_in_play[i + 1][j].once_per_phase_used:
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

    def move_to_top_of_discard(self, position):
        self.discard.append(self.discard.pop(position))

    def shuffle_card_in_discard_into_deck(self, position):
        self.deck.append(self.discard.pop(position))
        self.shuffle_deck()

    def mulligan_hand(self):
        num_cards = 0
        while self.cards:
            num_cards += 1
            self.deck.append(self.cards[0])
            del self.cards[0]
        self.shuffle_deck()
        for i in range(num_cards):
            self.draw_card()

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
            card = FindCard.find_card(self.deck[0], self.card_array, self.cards_dict)
            return card

    def draw_card(self):
        if not self.deck:
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
                self.discard.append(self.deck[deck_pos])
                del self.deck[deck_pos]

    def bottom_remaining_cards(self):
        if self.game.bottom_cards_after_search:
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

    def discard_card_from_hand(self, card_pos):
        if len(self.cards) > card_pos:
            self.discard.append(self.cards[card_pos])
            del self.cards[card_pos]

    def remove_card_from_hand(self, card_pos):
        del self.cards[card_pos]

    def remove_card_name_from_hand(self, name):
        if name in self.cards:
            self.cards.remove(name)

    def get_shields_given_pos(self, pos_in_hand, planet_pos=None, tank=False):
        shield_card_name = self.cards[pos_in_hand]
        card_object = FindCard.find_card(shield_card_name, self.card_array, self.cards_dict)
        shields = card_object.get_shields()
        if card_object.get_card_type() == "Support":
            if self.grigory_maksim_relevant:
                shields = 1
                if tank:
                    shields = 2
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

    def get_ranged_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ranged()
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
            return self.headquarters[unit_id].check_for_a_trait(trait)
        return self.cards_in_play[planet_id + 1][unit_id].check_for_a_trait(trait)

    def bloody_warlord_given_pos(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].bloody_warlord()
        self.urien_relevant = False
        self.gorzod_relevant = False
        self.subject_omega_relevant = False
        self.grigory_maksim_relevant = False
        self.illuminor_szeras_relevant = False
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
                                i = i - 1
                        else:
                            del self.game.reactions_needing_resolving[i]
                            del self.game.player_who_resolves_reaction[i]
                            del self.game.positions_of_unit_triggering_reaction[i]
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
                            i = i - 1
            i += 1

    def add_to_hq(self, card_object):
        if card_object.get_unique():
            if self.search_for_unique_card(card_object.name):
                return False
        self.headquarters.append(copy.deepcopy(card_object))
        last_element_index = len(self.headquarters) - 1
        self.headquarters[last_element_index].name_owner = self.name_player
        if self.get_card_type_given_pos(-2, last_element_index) == "Army":
            if self.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(-2, last_element_index, 1)
            enemy_player = self.game.p1
            if enemy_player.name_player == self.name_player:
                enemy_player = self.game.p2
            if enemy_player.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(-2, last_element_index, 1)
        if self.get_ability_given_pos(-2, last_element_index) == "Augmented Warriors":
            self.assign_damage_to_pos(-2, last_element_index, 2, preventable=False)
        elif self.headquarters[last_element_index].get_ability() == "Promethium Mine":
            self.headquarters[last_element_index].set_counter(4)
        elif self.headquarters[last_element_index].get_ability() == "Salamander Flamer Squad":
            self.headquarters[last_element_index].salamanders_flamers_id_number = self.game.current_flamers_id
            self.game.current_flamers_id += 1
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
            i = len(self.discard) - 1
            found = False
            while i > -1 and not found:
                card = FindCard.find_card(self.discard[i], self.card_array, self.cards_dict)
                if card.get_card_type() == "Event":
                    self.cards.append(card.get_name())
                    del self.discard[i]
                    found = True
                i = i - 1
        elif self.headquarters[last_element_index].get_ability() == "Earth Caste Technician":
            self.game.create_reaction("Earth Caste Technician", self.name_player,
                                      (int(self.number), -2, last_element_index))
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
        card = FindCard.find_card(self.cards[position_hand], self.card_array, self.cards_dict)
        if card.card_type == "Support":
            print("Need to play support card")
            played_card = self.play_card(-2, card=card)
            if played_card == "SUCCESS":
                return "SUCCESS/Support"
            return played_card
        return "SUCCESS/Not Support"

    def get_card_in_hand(self, position_hand):
        card = FindCard.find_card(self.cards[position_hand], self.card_array, self.cards_dict)
        return card

    def get_card_in_discard(self, position_discard):
        card = FindCard.find_card(self.discard[position_discard], self.card_array, self.cards_dict)
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
        if destination_planet == -2:
            target_card = self.headquarters[destination_position]
        else:
            target_card = self.cards_in_play[destination_planet + 1][destination_position]
        print("Moving attachment code")
        army_unit_as_attachment = False
        if target_attachment.get_ability() == "Gun Drones" or \
                target_attachment.get_ability() == "Shadowsun's Stealth Cadre":
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
        self.remove_attachment_from_pos(planet, position, attachment_position, discard=True)

    def remove_attachment_from_pos(self, planet, position, attachment_position, discard=False):
        if planet == -2:
            card = self.headquarters[position]
            if discard:
                self.discard.append(card.get_attachments()[attachment_position].get_name())
            del card.get_attachments()[attachment_position]
        else:
            card = self.cards_in_play[planet + 1][position]
            if discard:
                self.discard.append(card.get_attachments()[attachment_position].get_name())
            del card.get_attachments()[attachment_position]

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
            return True
        allowed_types = card.type_of_units_allowed_for_attachment
        if type_of_card not in allowed_types:
            print("Can't play to this card type.", type_of_card, allowed_types)
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
        if card.forbidden_traits in target_card.get_traits():
            return False
        if card.unit_must_be_unique:
            if not target_card.get_unique():
                print("Must be a unique unit, but is not")
                return False
        if card.limit_one_per_unit:
            attachments_active = target_card.get_attachments()
            for i in range(len(attachments_active)):
                if attachments_active[i].get_name() == card.get_name():
                    print("Limit one per unit")
                    return False
        if target_card.get_no_attachments():
            print("Unit may not have attachments")
            return False
        if card.check_for_a_trait("Wargear."):
            if not target_card.get_wargear_attachments_permitted():
                print("Unit may not have wargear")
                return False
        if card.get_name() == "The Shining Blade":
            if not target_card.get_mobile():
                return False
        if card.get_name() == "Flesh Hooks":
            if target_card.get_cost() > 2:
                return False
        name_owner = self.name_player
        if not_own_attachment:
            if self.number == "1":
                name_owner = self.game.p2.name_player
            elif self.number == "2":
                name_owner = self.game.p1.name_player
        target_card.add_attachment(card, name_owner=name_owner)
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
            cost = card.get_cost() - discounts
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
            cost = card.get_cost() - discounts
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
                           is_owner_of_card=True):
        if card.get_unique():
            if self.search_for_unique_card(card.name):
                return -1
        self.cards_in_play[position + 1].append(copy.deepcopy(card))
        last_element_index = len(self.cards_in_play[position + 1]) - 1
        self.cards_in_play[position + 1][last_element_index].name_owner = self.name_player
        if not is_owner_of_card:
            self.cards_in_play[position + 1][last_element_index].name_owner = self.get_name_enemy_player()
        if self.get_card_type_given_pos(position, last_element_index) == "Army":
            if self.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(position, last_element_index, 1)
            enemy_player = self.game.p1
            if enemy_player.name_player == self.name_player:
                enemy_player = self.game.p2
            if enemy_player.search_card_in_hq("Dissection Chamber"):
                self.assign_damage_to_pos(position, last_element_index, 1)
        if self.get_ability_given_pos(position, last_element_index) == "Augmented Warriors":
            self.assign_damage_to_pos(position, last_element_index, 2, preventable=False)
        if self.cards_in_play[position + 1][last_element_index].get_ability() == "Salamander Flamer Squad":
            self.cards_in_play[position + 1][last_element_index].salamanders_flamers_id_number =\
                self.game.current_flamers_id
            self.game.current_flamers_id += 1
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
        if self.cards_in_play[position + 1][last_element_index].get_ability() == "Swordwind Farseer":
            self.game.create_reaction("Swordwind Farseer", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Mighty Wraithknight":
            self.game.create_reaction("Mighty Wraithknight", self.name_player,
                                      (int(self.number), position, last_element_index))
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Veteran Barbrus":
            self.game.create_reaction("Veteran Barbrus", self.name_player, (int(self.number), position,
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
        if card.check_for_a_trait("Kabalite") or card.check_for_a_trait("Raider"):
            if self.game.get_red_icon(position):
                if self.search_for_card_everywhere("Archon Salaine Morn", limit_phase_rel=True):
                    self.game.create_reaction("Archon Salaine Morn", self.name_player, (int(self.number), -1, -1))
        if card.check_for_a_trait("Kabalite"):
            for i in range(len(self.cards_in_play[position + 1])):
                if self.get_ability_given_pos(position, i) == "Kabalite Harriers":
                    self.game.create_reaction("Kabalite Harriers", self.name_player,
                                              (int(self.number), position, i))
        if already_exhausted:
            self.cards_in_play[position + 1][last_element_index].exhaust_card()
        return last_element_index

    def get_once_per_phase_used_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_once_per_phase_used()
        return self.cards_in_play[planet_id + 1][unit_id].get_once_per_phase_used()

    def set_once_per_phase_used_given_pos(self, planet_id, unit_id, new_val):
        if planet_id == -2:
            self.headquarters[unit_id].set_once_per_phase_used(new_val)
            return None
        self.cards_in_play[planet_id + 1][unit_id].set_once_per_phase_used(new_val)
        return None

    def get_cost_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_cost()
        return self.cards_in_play[planet_id + 1][unit_id].get_cost()

    def reset_resolving_attack_attribute_own(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].resolving_attack = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].resolving_attack = False

    def get_on_kill_effects_of_attacker(self, planet_pos, unit_pos, def_pla, def_pos):
        print("\nGetting on kill effects\n")
        if self.name_player == self.game.name_1:
            other_player = self.game.p2
        else:
            other_player = self.game.p1
        on_kill_effects = []
        if planet_pos == -2:
            return on_kill_effects
        if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Patrolling Wraith":
            on_kill_effects.append("Patrolling Wraith")
        if self.get_ability_given_pos(planet_pos, unit_pos) == "Salvaged Battlewagon":
            on_kill_effects.append("Salvaged Battlewagon")
        for i in range(len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_ability() == "Bone Sabres":
                on_kill_effects.append("Bone Sabres")
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_ability() == "Kroot Hunting Rifle":
                on_kill_effects.append("Kroot Hunting Rifle")
        if other_player.get_card_type_given_pos(def_pla, def_pos) == "Army":
            if self.search_card_in_hq("Holding Cell"):
                on_kill_effects.append("Holding Cell")
            if self.check_for_trait_given_pos(planet_pos, unit_pos, "Genestealer"):
                if other_player.get_cost_given_pos(def_pla, def_pos) < 4:
                    if self.resources > 1 and self.search_hand_for_card("Gene Implantation"):
                        on_kill_effects.append("Gene Implantation")
            if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Ravenous Haruspex":
                if not self.cards_in_play[planet_pos + 1][unit_pos].get_once_per_phase_used():
                    on_kill_effects.append("Ravenous Haruspex")
                    self.game.ravenous_haruspex_gain = other_player.get_cost_given_pos(def_pla, def_pos)
            if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Striking Ravener":
                on_kill_effects.append("Striking Ravener")
            if self.get_ability_given_pos(planet_pos, unit_pos) == "Fire Prism":
                on_kill_effects.append("Fire Prism")
        return on_kill_effects

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

    def count_tortures_in_discard(self):
        count = 0
        for i in range(len(self.discard)):
            card = FindCard.find_card(self.discard[i], self.card_array, self.cards_dict)
            if card.check_for_a_trait("Torture"):
                count += 1
        return count

    async def dark_eldar_event_played(self):
        self.reset_reaction_beasthunter_wyches()
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Beasthunter Wyches":
                self.game.create_reaction("Beasthunter Wyches", self.name_player, (int(self.number), -2, i))
            for attach in self.headquarters[i].get_attachments():
                if attach.get_ability() == "Hypex Injector" and attach.name_owner == self.name_player:
                    self.game.create_reaction("Hypex Injector", self.name_player, (int(self.number), -2, i))
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == "Beasthunter Wyches":
                    self.game.create_reaction("Beasthunter Wyches", self.name_player, (int(self.number), i, j))
                for attach in self.cards_in_play[i + 1][j].get_attachments():
                    if attach.get_ability() == "Hypex Injector" and attach.name_owner == self.name_player:
                        self.game.create_reaction("Hypex Injector", self.name_player, (int(self.number), i, j))
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
        card = copy.deepcopy(FindCard.find_card(self.cards[hand_pos], self.card_array, self.cards_dict))
        if unit_only:
            if card.get_card_type() != "Army":
                return False
        self.headquarters.append(card)
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
            cost = card.get_cost() - discounts
            if position == -2:
                print("Play card to HQ")
                print(card.get_limited(), self.can_play_limited)
                if card.get_limited():
                    if self.can_play_limited:
                        if self.spend_resources(cost):
                            if self.add_to_hq(card):
                                self.cards.remove(card.get_name())
                                self.set_can_play_limited(False)
                                print("Played card to HQ")
                                return "SUCCESS", -1
                            self.add_resources(cost, refund=True)
                            return "FAIL/Unique already in play", -1
                    else:
                        return "FAIL/Limited already played", -1
                else:
                    if self.spend_resources(cost):
                        if self.add_to_hq(card):
                            self.cards.remove(card.get_name())
                            print("Played card to HQ")
                            if card.get_ability() == "Murder of Razorwings":
                                self.game.discard_card_at_random_from_opponent(self.number)
                            return "SUCCESS", -1
                        self.add_resources(cost, refund=True)
                        return "Fail/Unique already in play", -1
                print("Insufficient resources")
                return "FAIL/Insufficient resources", -1
            else:
                cost = card.get_cost() - discounts
                if card.get_limited():
                    if self.can_play_limited and not self.enemy_holding_cell_check(card.get_name()):
                        if self.spend_resources(cost):
                            if self.add_card_to_planet(card, position, is_owner_of_card=is_owner_of_card) != -1:
                                self.set_can_play_limited(False)
                                print("Played card to planet", position)
                                location_of_unit = len(self.cards_in_play[position + 1]) - 1
                                if damage_to_take > 0:
                                    if self.game.bigga_is_betta_active:
                                        while damage_on_play > 0:
                                            self.assign_damage_to_pos(position, location_of_unit, 1)
                                            damage_on_play -= 1
                                    else:
                                        self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                                return "SUCCESS", location_of_unit
                            self.add_resources(cost, refund=True)
                            return "FAIL/Unique already in play", -1
                    else:
                        return "FAIL/Limited already played", -1
                elif not self.enemy_holding_cell_check(card.get_name()):
                    if self.spend_resources(cost):
                        if self.add_card_to_planet(card, position, is_owner_of_card=is_owner_of_card) != -1:
                            location_of_unit = len(self.cards_in_play[position + 1]) - 1
                            if damage_to_take > 0:
                                if self.game.bigga_is_betta_active:
                                    while damage_on_play > 0:
                                        self.assign_damage_to_pos(position, location_of_unit, 1)
                                        damage_on_play -= 1
                                else:
                                    self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                            if card.get_ability() == "Murder of Razorwings":
                                self.game.create_reaction("Murder of Razorwings", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Imperial Fists Siege Force":
                                self.game.create_reaction("Imperial Fists Siege Force", self.name_player,
                                                          (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Imperial Fists Devastators":
                                if self.game.get_blue_icon(position):
                                    self.game.create_reaction("Imperial Fists Devastators", self.name_player,
                                                              (int(self.number), position, location_of_unit))
                            if card.get_ability() == "Scything Hormagaunts":
                                self.game.create_reaction("Scything Hormagaunts", self.name_player,
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
                            if card.check_for_a_trait("Scout") and card.get_faction() != "Necrons":
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
                                        if self.get_ready_given_pos(-2, i):
                                            self.game.create_reaction("Turbulent Rift", self.name_player,
                                                                      (int(self.number), position, location_of_unit))
                                    if self.get_ability_given_pos(-2, i) == "Loamy Broodhive":
                                        if self.get_ready_given_pos(-2, i):
                                            self.game.create_reaction("Loamy Broodhive", self.name_player,
                                                                      (int(self.number), position, location_of_unit))
                            if card.check_for_a_trait("Daemon"):
                                for i in range(len(self.headquarters)):
                                    if self.get_ability_given_pos(-2, i) == "Tower of Worship":
                                        self.game.create_reaction("Tower of Worship", self.name_player,
                                                                  (int(self.number), -2, i))
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
                            if self.game.request_search_for_enemy_card_at_planet(self.number, position,
                                                                                 "Syren Zythlex"):
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
            i += 1
        for i in range(7):
            j = 0
            while j < len(self.cards_in_play[i + 1]):
                self.cards_in_play[i + 1][j].resolving_attack = False
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
                    self.move_unit_at_planet_to_hq(i, j)
                    j = j - 1
                j = j + 1

    def reset_card_name_misc_ability(self, card_name):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == card_name:
                self.headquarters[i].misc_ability_used = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == card_name:
                    self.cards_in_play[i + 1][j].misc_ability_used = False

    def return_card_to_hand(self, planet_pos, unit_pos):
        if planet_pos == -2:
            if self.headquarters[unit_pos].name_owner == self.name_player:
                self.cards.append(self.headquarters[unit_pos].get_name())
            else:
                ret_player = self.game.p1
                if self.game.name_1 == self.name_player:
                    ret_player = self.game.p2
                ret_player.cards.append(self.headquarters[unit_pos].get_name())
            self.discard_attachments_from_card(planet_pos, unit_pos)
            self.remove_card_from_hq(unit_pos)
            return None
        if self.cards_in_play[planet_pos + 1][unit_pos].name_owner == self.name_player:
            self.cards.append(self.cards_in_play[planet_pos + 1][unit_pos].get_name())
        else:
            ret_player = self.game.p1
            if self.game.name_1 == self.name_player:
                ret_player = self.game.p2
            ret_player.cards.append(self.cards_in_play[planet_pos + 1][unit_pos].get_name())
        self.discard_attachments_from_card(planet_pos, unit_pos)
        self.remove_card_from_play(planet_pos, unit_pos)
        return None

    def discard_card_at_random(self):
        print("")
        if self.cards:
            pos = random.randint(1, len(self.cards) - 1)
            print(pos)
            self.discard_card_from_hand(pos)

    def reset_defense_batteries(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].valid_defense_battery_target = False
        for i in range(7):
            for j in range(len(self.attachments_at_planet[i])):
                self.attachments_at_planet[i][j].defense_battery_activated = False
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].valid_defense_battery_target = False

    def move_unit_to_planet(self, origin_planet, origin_position, destination):
        if origin_planet == -2:
            headquarters_list = self.headquarters
            if self.headquarters[origin_position].get_card_type() == "Army":
                if self.defense_battery_check(destination):
                    self.headquarters[origin_position].valid_defense_battery_target = True
            self.cards_in_play[destination + 1].append(copy.deepcopy(headquarters_list[origin_position]))
            new_pos = len(self.cards_in_play[destination + 1]) - 1
            self.cards_in_play[destination + 1][new_pos].valid_kugath_nurgling_target = True
            self.game.just_moved_units = True
            if self.cards_in_play[destination + 1][new_pos].get_faction() == "Eldar":
                if self.search_card_in_hq("Alaitoc Shrine", ready_relevant=True):
                    alaitoc_shrine_already_present = False
                    for i in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[i] == "Alaitoc Shrine":
                            alaitoc_shrine_already_present = True
                    if not alaitoc_shrine_already_present:
                        self.game.reactions_needing_resolving.append("Alaitoc Shrine")
                        self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
                        self.game.player_who_resolves_reaction.append(self.name_player)
                        self.game.allowed_units_alaitoc_shrine.append([int(self.number), destination, new_pos])
            self.remove_card_from_hq(origin_position)
        else:
            if self.cards_in_play[origin_planet + 1][origin_position].get_card_type() == "Army":
                if self.defense_battery_check(origin_planet) or self.defense_battery_check(destination):
                    self.cards_in_play[origin_planet + 1][origin_position].valid_defense_battery_target = True
            self.cards_in_play[destination + 1].append(copy.deepcopy(self.cards_in_play[origin_planet + 1]
                                                                     [origin_position]))
            new_pos = len(self.cards_in_play[destination + 1]) - 1
            self.cards_in_play[destination + 1][new_pos].valid_kugath_nurgling_target = True
            self.game.just_moved_units = True
            self.remove_card_from_play(origin_planet, origin_position)
            if self.search_hand_for_card("Cry of the Wind"):
                already_cry = False
                self.cards_in_play[destination + 1][new_pos].valid_target_ashen_banner = True
                for i in range(len(self.game.reactions_needing_resolving)):
                    if self.game.reactions_needing_resolving[i] == "Cry of the Wind":
                        if self.game.player_who_resolves_reaction[i] == self.name_player:
                            already_cry = True
                if not already_cry:
                    self.game.create_reaction("Cry of the Wind", self.name_player, (int(self.number), -1, -1))
            if self.game.phase == "COMBAT":
                if self.search_card_in_hq("Deathly Web Shrine", ready_relevant=True):
                    self.game.create_reaction("Deathly Web Shrine", self.name_player,
                                              (int(self.number), destination, -1))
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
            for i in range(len(self.cards_in_play[origin_planet + 1])):
                if self.get_ability_given_pos(origin_planet, i) == "Wildrider Vyper":
                    self.game.create_reaction("Wildrider Vyper", self.name_player,
                                              (int(self.number), origin_planet, i))
            other_player = self.game.p1
            if other_player.name_player == self.name_player:
                other_player = self.game.p2
            for i in range(len(other_player.cards_in_play[origin_planet + 1])):
                if other_player.get_ability_given_pos(origin_planet, i) == "Wildrider Vyper":
                    self.game.create_reaction("Wildrider Vyper", other_player.name_player,
                                              (int(other_player.number), origin_planet, i))
        if self.cards_in_play[destination + 1][new_pos].get_ability() == "Venomous Fiend":
            self.game.create_reaction("Venomous Fiend", self.name_player, (int(self.number), destination, new_pos))

    def commit_warlord_to_planet_from_planet(self, origin_planet, dest_planet):
        self.warlord_commit_location = dest_planet
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
                    self.game.create_reaction("Ragnar Blackmane", self.name_player,
                                              [int(self.number), dest_planet, -1])
                self.move_unit_to_planet(origin_planet, i, dest_planet)
                for j in range(7):
                    if j != dest_planet:
                        for k in range(len(self.cards_in_play[j + 1])):
                            if self.get_ability_given_pos(j, k) == "Blackmane Sentinel":
                                self.game.create_reaction("Blackmane Sentinel", self.name_player,
                                                          (int(self.number), j, k))
                if summon_khymera:
                    self.summon_token_at_planet("Khymera", dest_planet)
                if self.number == "1":
                    self.game.p2.resolve_enemy_warlord_committed_to_planet(dest_planet)
                else:
                    self.game.p1.resolve_enemy_warlord_committed_to_planet(dest_planet)
            i += 1

    def move_synapse_to_hq(self):
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_card_type() == "Synapse":
                    self.move_unit_at_planet_to_hq(i, j)
                    return None
        return None

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

    def phoenix_attack_fighter_triggers(self, planets_list):
        for planet_pos in planets_list:
            for i in range(len(self.cards_in_play[planet_pos + 1])):
                if self.get_ability_given_pos(planet_pos, i) == "Phoenix Attack Fighter":
                    self.game.create_reaction("Phoenix Attack Fighter", self.name_player,
                                              (int(self.number), planet_pos, i))

    def commit_synapse_to_planet(self):
        if self.synapse_commit_location != -1:
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_card_type() == "Synapse":
                    if self.headquarters[i].get_ability() == "Gravid Tervigon":
                        self.game.create_reaction("Gravid Tervigon", self.name_player,
                                                  (int(self.number), self.synapse_commit_location, -1))
                    if self.headquarters[i].get_ability() == "Venomthrope Polluter":
                        self.game.create_reaction("Venomthrope Polluter", self.name_player,
                                                  (int(self.number), self.synapse_commit_location, -1))
                    self.move_unit_to_planet(-2, i, self.synapse_commit_location)
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
                    for j in range(7):
                        if j != planet_pos - 1:
                            for k in range(len(self.cards_in_play[j + 1])):
                                if self.get_ability_given_pos(j, k) == "Blackmane Sentinel":
                                    self.game.create_reaction("Blackmane Sentinel", self.name_player,
                                                              (int(self.number), j, k))
                    return True
            return False
        else:
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
                        if headquarters_list[i].get_ability() == "Ardent Auxiliaries":
                            self.game.create_reaction("Ardent Auxiliaries", self.name_player,
                                                      (int(self.number), planet_pos - 1, -1))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Old Zogwort":
                        self.game.create_reaction("Old Zogwort", self.name_player,
                                                  (int(self.number), planet_pos - 1, i))
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Commander Starblaze":
                        self.game.create_reaction("Commander Starblaze", self.name_player,
                                                  (int(self.number), planet_pos - 1, i))
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
                    self.move_unit_to_planet(-2, i, planet_pos - 1)
                    for j in range(7):
                        if j != planet_pos - 1:
                            for k in range(len(self.cards_in_play[j + 1])):
                                if self.get_ability_given_pos(j, k) == "Blackmane Sentinel":
                                    self.game.create_reaction("Blackmane Sentinel", self.name_player,
                                                              (int(self.number), j, k))
                    i -= 1
                i += 1
        return None

    def get_command_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_command()
        command = self.cards_in_play[planet_id + 1][unit_id].get_command()
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Fire Warrior Grenadiers":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].check_for_a_trait("Ethereal"):
                    command += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Iron Hands Techmarine":
            command += self.game.request_number_of_enemy_units_at_planet(self.number, planet_id)
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

    def check_for_warlord(self, planet_id):
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

    def reset_all_blanked_eop(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].reset_blanked_eop()
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].reset_blanked_eop()

    def check_for_enemy_warlord(self, planet_id):
        if self.number == "1":
            enemy_player = self.game.p2
        else:
            enemy_player = self.game.p1
        if enemy_player.check_for_warlord(planet_id):
            return True
        return False

    def get_armorbane_given_pos(self, planet_id, unit_id, enemy_unit_damage=0):
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Praetorian Ancient":
            if self.count_units_in_discard() > 5:
                return True
        if self.get_ability_given_pos(planet_id, unit_id) == "Treacherous Lhamaean":
            if self.warlord_faction != "Dark Eldar":
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
            return self.headquarters[unit_id].get_faction()
        return self.cards_in_play[planet_id + 1][unit_id].get_faction()

    def get_name_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_name()
        return self.cards_in_play[planet_id + 1][unit_id].get_name()

    def get_has_hive_mind_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].has_hive_mind
        return self.cards_in_play[planet_id + 1][unit_id].has_hive_mind

    def get_ability_given_pos(self, planet_id, unit_id, bloodied_relevant=False):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ability(bloodied_relevant=bloodied_relevant)
        return self.cards_in_play[planet_id + 1][unit_id].get_ability(bloodied_relevant=bloodied_relevant)

    def get_ready_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ready()
        return self.cards_in_play[planet_id + 1][unit_id].get_ready()

    def get_ambush_of_card(self, card):
        if card.get_ability() == "Standard Bearer":
            if self.warlord_faction != "Astra Militarum":
                return True
        if card.check_for_a_trait("Genestealer"):
            if self.subject_omega_relevant:
                return True
        if card.get_faction() == "Eldar":
            if card.get_is_unit():
                if self.concealing_darkness_active:
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
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, unit_id, "Herald of the Tau'va"):
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
                              ready_relevant=False):
        if not ability_checking:
            for i in range(len(self.cards_in_play[planet_id + 1])):
                current_name = self.cards_in_play[planet_id + 1][i].get_name()
                print(current_name, name_of_card)
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
            print(current_name, name_of_card)
            if current_name == name_of_card:
                if not ready_relevant or self.get_ready_given_pos(planet_id, i):
                    if not bloodied_relevant:
                        return True
                    if self.cards_in_play[planet_id + 1][i].get_bloodied():
                        return False
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
        if not self.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait("Vehicle"):
            for i in range(len(self.cards_in_play[planet_pos + 1])):
                if self.get_ability_given_pos(planet_pos, i) == "Land Raider":
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
        if self.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
            if self.search_card_at_planet(planet_pos, "Vostroyan Officer"):
                return True
        return False

    def search_card_in_hq(self, name_of_card, bloodied_relevant=False, ability_checking=True, ready_relevant=False):
        for i in range(len(self.headquarters)):
            current_name = self.headquarters[i].get_ability()
            if current_name == name_of_card:
                if not bloodied_relevant:
                    if ready_relevant:
                        return self.headquarters[i].get_ready()
                    return True
                if self.headquarters[i].get_bloodied():
                    return False
                if ready_relevant:
                    return self.headquarters[i].get_ready()
                return True
        return False

    def search_hq_for_discounts(self, faction_of_card, traits, is_attachment=False, planet_chosen=None):
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
        return discounts_available

    def search_planet_for_discounts(self, planet_pos, traits):
        discounts_available = 0
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if "Daemon" in traits:
                if self.cards_in_play[planet_pos + 1][i].get_ability() == "Cultist":
                    discounts_available += 1
                    self.set_aiming_reticle_in_play(planet_pos, i, "green")
                    if "Elite" in traits:
                        discounts_available += self.count_copies_in_play("Master Warpsmith", ability=True)
                elif self.cards_in_play[planet_pos + 1][i].get_ability() == "Splintered Path Acolyte":
                    discounts_available += 2
                    self.set_aiming_reticle_in_play(planet_pos, i, "green")
        return discounts_available

    def reset_all_aiming_reticles_play_hq(self):
        for i in range(len(self.headquarters)):
            self.reset_aiming_reticle_in_play(-2, i)
        for j in range(7):
            for i in range(len(self.cards_in_play[j + 1])):
                self.reset_aiming_reticle_in_play(j, i)

    def search_all_planets_for_discounts(self, traits):
        discounts_available = 0
        for i in range(7):
            discounts_available += self.search_planet_for_discounts(i, traits)
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
        num_nullifies = 0
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
        if self.search_card_in_hq("Intercept", ready_relevant=True):
            possible_interrupts.append("Intercept")
        return possible_interrupts

    def storm_of_silence_check(self):
        if self.resources > 1:
            if self.search_hand_for_card("Storm of Silence"):
                return True
        return False

    def interrupt_cancel_target_check(self, planet_pos, unit_pos, context="", move_from_planet=False,
                                      targeting_support=False, intercept_possible=False):
        possible_interrupts = []
        if targeting_support:
            if self.game.colony_shield_generator_enabled:
                if self.get_ability_given_pos(planet_pos, unit_pos) != "Colony Shield Generator":
                    if self.search_card_in_hq("Colony Shield Generator", ready_relevant=True):
                        possible_interrupts.append("Colony Shield Generator")
        else:
            if context == "Searing Brand":
                if self.game.searing_brand_cancel_enabled:
                    if len(self.cards) > 1:
                        possible_interrupts.append("Searing Brand")
            if move_from_planet:
                if self.game.slumbering_gardens_enabled:
                    if self.search_card_in_hq("Slumbering Gardens", ready_relevant=True):
                        possible_interrupts.append("Slumbering Gardens")
            if intercept_possible:
                possible_interrupts + self.intercept_check()
            if self.game.storm_of_silence_enabled:
                if self.storm_of_silence_check():
                    possible_interrupts.append("Storm of Silence")
            if self.game.communications_relay_enabled:
                if self.communications_relay_check(planet_pos, unit_pos):
                    possible_interrupts.append("Communications Relay")
            if self.game.backlash_enabled:
                if self.backlash_check(planet_pos, unit_pos):
                    possible_interrupts.append("Backlash")
            if planet_pos != -2:
                if self.game.communications_relay_enabled:
                    if self.cards_in_play[planet_pos + 1][unit_pos].immortal_loyalist_ok:
                        self.cards_in_play[planet_pos + 1][unit_pos].immortal_loyalist_ok = False
                        if self.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                            if self.search_card_at_planet(planet_pos, "Immortal Loyalist"):
                                possible_interrupts.append("Immortal Loyalist")
                    for i in range(len(self.cards_in_play[planet_pos + 1])):
                        if self.get_ability_given_pos(planet_pos, i, bloodied_relevant=True) == "Jain Zar":
                            if not self.cards_in_play[planet_pos + 1][unit_pos].once_per_round_used:
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

    def search_hand_for_card(self, card_name):
        for i in range(len(self.cards)):
            if self.cards[i] == card_name:
                return True
        return False

    def get_card_type_given_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            return self.headquarters[unit_pos].get_card_type()
        return self.cards_in_play[planet_pos + 1][unit_pos].get_card_type()

    def search_hand_for_discounts(self, faction_of_card):
        discounts_available = 0
        for i in range(len(self.cards)):
            if self.cards[i] == "Bigga Is Betta":
                if faction_of_card == "Orks":
                    discounts_available += 2
        return discounts_available

    def search_attachments_at_pos(self, planet_pos, unit_pos, card_abil, ready_relevant=False, must_match_name=False):
        if planet_pos == -2:
            for i in range(len(self.headquarters[unit_pos].get_attachments())):
                if self.headquarters[unit_pos].get_attachments()[i].get_ability() == card_abil:
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

    def perform_discount_at_pos_hq(self, pos, faction_of_card, traits, target_planet=None):
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
        if self.headquarters[pos].get_ability() == "Sae'lum Enclave":
            if self.headquarters[pos].aiming_reticle_color == "green":
                self.exhaust_given_pos(-2, pos)
                discount += 2
                self.reset_aiming_reticle_in_play(-2, pos)
        if "Elite" in traits:
            if self.headquarters[pos].get_ability() == "STC Fragment":
                if self.headquarters[pos].get_ready():
                    self.exhaust_given_pos(-2, pos)
                    discount += 2
        if self.headquarters[pos].get_ability() == "Bonesinger Choir":
            if self.headquarters[pos].aiming_reticle_color == "green":
                self.exhaust_given_pos(-2, pos)
                discount += 2
                self.reset_aiming_reticle_in_play(-2, pos)
        if "Daemon" in traits:
            if self.headquarters[pos].get_ability() == "Cultist":
                discount += 1
                self.sacrifice_card_in_hq(pos)
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
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].set_once_per_round_used(False)
                self.headquarters[i].techmarine_aspirant_available = True
                for j in range(len(self.headquarters[i].get_attachments())):
                    self.headquarters[i].get_attachments()[j].set_once_per_round_used(False)
                self.headquarters[i].area_effect_eor = 0
                self.headquarters[i].armorbane_eor = False
                self.headquarters[i].mobile_eor = False
                if self.get_name_given_pos(-2, i) == "Caustic Tyrannofex":
                    self.headquarters[i].misc_ability_used = False
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                self.cards_in_play[i + 1][j].set_once_per_round_used(False)
                self.cards_in_play[i + 1][j].techmarine_aspirant_available = True
                for k in range(len(self.cards_in_play[i + 1][j].get_attachments())):
                    self.cards_in_play[i + 1][j].get_attachments()[k].set_once_per_round_used(False)
                self.cards_in_play[i + 1][j].area_effect_eor = 0
                self.cards_in_play[i + 1][j].armorbane_eor = False
                self.cards_in_play[i + 1][j].mobile_eor = False
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
            return None
        if expiration == "EOP":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_health_until_end_of_phase(amount)

    def increase_attack_of_unit_at_pos(self, planet_pos, unit_pos, amount, expiration="EOB"):
        if planet_pos == -2:
            if expiration == "EOB":
                self.headquarters[unit_pos].increase_extra_attack_until_end_of_battle(amount)
            elif expiration == "NEXT":
                self.headquarters[unit_pos].increase_extra_attack_until_next_attack(amount)
            elif expiration == "EOP":
                self.headquarters[unit_pos].increase_extra_attack_until_end_of_phase(amount)
            return None
        if expiration == "EOB":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_end_of_battle(amount)
        elif expiration == "NEXT":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_next_attack(amount)
        elif expiration == "EOP":
            self.cards_in_play[planet_pos + 1][unit_pos].increase_extra_attack_until_end_of_phase(amount)
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
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_sacrifice_end_of_phase():
                self.sacrifice_card_in_hq(i)
                sacrificed_locations[0] = True
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                if self.cards_in_play[planet_pos + 1][unit_pos].get_sacrifice_end_of_phase():
                    self.sacrifice_card_in_play(planet_pos, unit_pos)
                    sacrificed_locations[planet_pos + 1] = True
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
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].negative_hp_until_eop = 0
                self.headquarters[i].hit_by_which_salamanders = []
                self.headquarters[i].extra_command_eop = 0
                self.headquarters[i].positive_hp_until_eop = 0
                self.headquarters[i].reset_ranged()
                self.headquarters[i].area_effect_eop = 0
                self.headquarters[i].armorbane_eop = False
                self.headquarters[i].lost_ranged_eop = False
                self.headquarters[i].ranged_eop = False
                self.headquarters[i].mobile_eop = False
                self.headquarters[i].flying_eop = False
                self.headquarters[i].attack_set_eop = -1
                self.headquarters[i].brutal_eop = False
                self.headquarters[i].extra_traits_eop = ""
                self.headquarters[i].lost_keywords_eop = False
                self.headquarters[i].cannot_ready_phase = False
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].lost_keywords_eop = False
                self.cards_in_play[planet_pos + 1][unit_pos].negative_hp_until_eop = 0
                self.cards_in_play[planet_pos + 1][unit_pos].positive_hp_until_eop = 0
                self.cards_in_play[planet_pos + 1][unit_pos].reset_ranged()
                self.cards_in_play[planet_pos + 1][unit_pos].area_effect_eop = 0
                self.cards_in_play[planet_pos + 1][unit_pos].extra_command_eop = 0
                self.cards_in_play[planet_pos + 1][unit_pos].armorbane_eop = False
                self.cards_in_play[planet_pos + 1][unit_pos].brutal_eop = False
                self.cards_in_play[planet_pos + 1][unit_pos].lost_ranged_eop = False
                self.cards_in_play[planet_pos + 1][unit_pos].hit_by_which_salamanders = []
                self.cards_in_play[planet_pos + 1][unit_pos].ranged_eop = False
                self.cards_in_play[planet_pos + 1][unit_pos].mobile_eop = False
                self.cards_in_play[planet_pos + 1][unit_pos].flying_eop = False
                self.cards_in_play[planet_pos + 1][unit_pos].attack_set_eop = -1
                self.cards_in_play[planet_pos + 1][unit_pos].extra_traits_eop = ""
                self.cards_in_play[planet_pos + 1][unit_pos].cannot_ready_phase = False

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
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].set_once_per_phase_used(False)
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].set_once_per_phase_used(False)

    def perform_discount_at_pos_hand(self, pos, faction_of_card):
        discount = 0
        damage = 0
        if self.cards[pos] == "Bigga Is Betta":
            if faction_of_card == "Orks":
                discount += 2
                damage += 1
        return discount, damage

    def perform_discount_at_pos_in_play(self, planet_pos, unit_pos, traits):
        discount = 0
        if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Crushface":
            if self.cards_in_play[planet_pos + 1][unit_pos].aiming_reticle_color == "green":
                self.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                discount += 1
        if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Gorzod":
            if self.cards_in_play[planet_pos + 1][unit_pos].aiming_reticle_color == "green":
                self.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                discount += 1
        if "Daemon" in traits:
            if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Cultist":
                discount += 1
                self.sacrifice_card_in_play(planet_pos, unit_pos)
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
                for i in range(len(self.headquarters[unit_id].get_attachments())):
                    if self.headquarters[unit_id].get_attachments()[i].get_ability() == "Dire Mutation":
                        self.assign_damage_to_pos(-2, unit_id, 1)
            return None
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, "Disciple of Excess"):
                return None
        previous_state = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        self.cards_in_play[planet_id + 1][unit_id].exhaust_card()
        new_state = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        if previous_state and not new_state:
            for i in range(len(self.cards_in_play[planet_id + 1][unit_id].get_attachments())):
                if self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].get_ability() == "Dire Mutation":
                    self.assign_damage_to_pos(planet_id, unit_id, 1)
        return None

    def get_area_effect_given_pos(self, planet_id, unit_id):
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

    def resolve_enemy_warlord_committed_to_planet(self, planet_pos):
        if self.check_for_warlord(planet_pos):
            if self.search_hand_for_card("Primal Howl"):
                if not self.primal_howl_used:
                    self.primal_howl_used = True
                    self.game.create_reaction("Primal Howl", self.name_player, (self.number, -1, -1))
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            for j in range(len(self.cards_in_play[planet_pos + 1][i].get_attachments())):
                if self.cards_in_play[planet_pos + 1][i].get_attachments()[j].get_ability() == "Blacksun Filter":
                    owner = self.cards_in_play[planet_pos + 1][i].get_attachments()[j].name_owner
                    self.game.create_reaction("Blacksun Filter", owner, (int(self.number), planet_pos, i))
            if self.cards_in_play[planet_pos + 1][i].get_ability(bloodied_relevant=True) == "Ragnar Blackmane":
                # Need an extra check that the ability has not already fired this phase.
                self.game.create_reaction("Ragnar Blackmane", self.name_player,
                                          (int(self.number), planet_pos, i))
            if self.cards_in_play[planet_pos + 1][i].get_ability() == "Blood Claw Pack":
                if self.get_ready_given_pos(planet_pos, i):
                    self.game.create_reaction("Blood Claw Pack", self.name_player,
                                              (int(self.number), planet_pos, i))

    def does_own_interrupt_exist(self, reaction_name):
        for i in range(len(self.game.interrupts_waiting_on_resolution)):
            if self.game.interrupts_waiting_on_resolution[i] == reaction_name:
                if self.game.player_resolving_interrupts[i] == self.name_player:
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
            if card.get_ability() == "Pyrrhian Eternals":
                attack_value += self.discard.count("Pyrrhian Eternals")
            if card.get_ability() == "Destroyer Cultist":
                attack_value += self.count_non_necron_factions()
            if card.get_ability() == "Virulent Plague Squad":
                attack_value = attack_value + self.game.request_number_of_enemy_units_in_discard(str(self.number))
            return attack_value
        card = self.cards_in_play[planet_id + 1][unit_id]
        if card.attack_set_eop != -1:
            return card.attack_set_eop
        attack_value = card.get_attack()
        if card.get_name() == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Strangler Brood":
                    attack_value += 1
        if card.get_faction() != "Necrons" and card.check_for_a_trait("Warrior"):
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Immortal Vanguard":
                    attack_value += 1
        if card.get_ability() == "Praetorian Ancient":
            if self.count_units_in_discard() > 5:
                attack_value += 2
        if card.get_ability() == "Pyrrhian Eternals":
            attack_value += self.discard.count("Pyrrhian Eternals")
        if card.get_ability() == "Destroyer Cultist":
            attack_value += self.count_non_necron_factions()
        if card.get_ability() != "Colonel Straken":
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
        if card.get_ability() == "Auxiliary Overseer":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.get_faction_given_pos(planet_id, i) != "Tau":
                    attack_value += 1
        if card.get_ability() == "Goff Boyz":
            if self.game.round_number == planet_id:
                attack_value = attack_value + 3
        if card.get_ability() in self.plus_two_atk_if_warlord:
            if self.check_for_warlord(planet_id):
                attack_value += 2
            else:
                if self.number == "1":
                    if self.game.p2.check_for_warlord(planet_id):
                        attack_value += 2
                elif self.number == "2":
                    if self.game.p1.check_for_warlord(planet_id):
                        attack_value += 2
        if card.get_ability() == "Baharroth's Hawks":
            if self.check_for_warlord(planet_id):
                attack_value += 3
        if self.get_faction_given_pos(planet_id, unit_id) == "Orks" and \
                self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
            if self.search_card_in_hq("Kustomisation Station"):
                attack_value += 1
        if card.get_ability() == "Gorzod's Wagons":
            if self.get_enemy_has_init_for_cards(planet_id, unit_id):
                attack_value += 2
        if card.get_ability() == "Fire Warrior Grenadiers":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].check_for_a_trait("Ethereal"):
                    attack_value += 2
        if card.get_ability() == "Sacaellum Shrine Guard" or card.get_ability() == "Saim-Hann Kinsman":
            if self.game.get_green_icon(planet_id):
                attack_value += 1
        if card.get_ability() == "Virulent Plague Squad":
            attack_value = attack_value + self.game.request_number_of_enemy_units_in_discard(str(self.number))
        if card.get_ability() == "Infantry Conscripts":
            support_count = 0
            for i in range(len(self.headquarters)):
                if self.headquarters[i].get_card_type() == "Support":
                    support_count += 1
            attack_value += support_count * 2
        attachments = card.get_attachments()
        for i in range(len(attachments)):
            if attachments[i].get_ability() == "Agonizer of Bren":
                attack_value += self.count_copies_in_play("Khymera")
            if attachments[i].get_ability() == "Noxious Fleshborer":
                if self.game.infested_planets[planet_id]:
                    attack_value += 1
            if attachments[i].get_ability() == "Frostfang":
                if self.number == "1":
                    if self.game.p2.check_for_warlord(planet_id):
                        attack_value += 2
                elif self.number == "2":
                    if self.game.p1.check_for_warlord(planet_id):
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
            card = FindCard.find_card(self.discard[i], self.card_array, self.cards_dict)
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
                             context="", preventable=True, shadow_field_possible=False, rickety_warbuggy=False):
        if planet_id == -2:
            return self.assign_damage_to_pos_hq(unit_id, damage, can_shield)
        if shadow_field_possible:
            if self.search_attachments_at_pos(planet_id, unit_id, "Shadow Field"):
                return False, 0
            if self.check_for_trait_given_pos(planet_id, unit_id, "Daemon"):
                if self.the_princes_might_active[planet_id]:
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
        og_damage = damage
        too_many_bodyguards = False
        if att_pos is not None:
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
            other_player = self.game.p1
            if other_player.name_player == self.name_player:
                other_player = self.game.p2
            if not other_player.hit_by_gorgul:
                damage += 1
        if self.search_attachments_at_pos(planet_id, unit_id, "Heavy Marker Drone"):
            damage = damage * 2
        damage_on_card_before = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        self.cards_in_play[planet_id + 1][unit_id].damage_card(self, damage, can_shield)
        damage_on_card_after = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        total_damage_that_can_be_blocked = damage_on_card_after - prior_damage
        if total_damage_that_can_be_blocked > 0:
            if self.cards_in_play[planet_id + 1][unit_id].get_unstoppable():
                if not self.cards_in_play[planet_id + 1][unit_id].once_per_round_used:
                    self.cards_in_play[planet_id + 1][unit_id].once_per_round_used = True
                    self.cards_in_play[planet_id + 1][unit_id].set_damage(damage_on_card_after - 1)
                    total_damage_that_can_be_blocked = total_damage_that_can_be_blocked - 1
                    damage_on_card_after = damage_on_card_after - 1
                    if self.get_ability_given_pos(planet_id, unit_id) == "Righteous Initiate":
                        self.cards_in_play[planet_id + 1][unit_id].extra_attack_until_end_of_phase += 2
                    if self.get_ability_given_pos(planet_id, unit_id) == "Sword Brethren Dreadnought":
                        self.game.create_reaction("Sword Brethren Dreadnought", self.name_player,
                                                  (int(self.number), planet_id, unit_id))
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
            if i == 0 or bodyguard_damage_list[i] == bodyguard_damage_list[0]:
                self.set_aiming_reticle_in_play(planet_id, bodyguard_damage_list[i], "red")
            else:
                self.set_aiming_reticle_in_play(planet_id, bodyguard_damage_list[i], "blue")
        if damage_on_card_after > damage_on_card_before:
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
                        self.game.p1.discard.append(self.headquarters[unit_pos].get_attachments()[0].get_name())
                    else:
                        self.game.p2.discard.append(self.headquarters[unit_pos].get_attachments()[0].get_name())
                    del self.headquarters[unit_pos].get_attachments()[i]
                    i = i - 1
                i = i + 1
            return None
        while i < len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()):
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_name() == name:
                if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].name_owner ==\
                        self.game.name_1:
                    self.game.p1.discard.append(
                        self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_name())
                else:
                    self.game.p2.discard.append(
                        self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_name())
                del self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i]
                i = i - 1
            i = i + 1
        return None

    def discard_attachments_from_card(self, planet_pos, unit_pos):
        if planet_pos == -2:
            while self.headquarters[unit_pos].get_attachments():
                if self.headquarters[unit_pos].get_attachments()[0].name_owner == self.game.name_1:
                    self.game.p1.discard.append(self.headquarters[unit_pos].get_attachments()[0].get_name())
                else:
                    self.game.p2.discard.append(self.headquarters[unit_pos].get_attachments()[0].get_name())
                del self.headquarters[unit_pos].get_attachments()[0]
            return None
        while self.cards_in_play[planet_pos + 1][unit_pos].get_attachments():
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[0].name_owner == self.game.name_1:
                self.game.p1.discard.append(
                    self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[0].get_name())
            else:
                self.game.p2.discard.append(
                    self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[0].get_name())
            del self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[0]
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
        prior_damage = self.headquarters[unit_id].get_damage()
        damage_too_great = self.headquarters[unit_id].damage_card(self, damage, can_shield)
        afterwards_damage = self.headquarters[unit_id].get_damage()
        total_that_can_be_blocked = afterwards_damage - prior_damage
        if total_that_can_be_blocked > 0:
            if self.headquarters[unit_id].get_unstoppable():
                if not self.headquarters[unit_id].once_per_round_used:
                    self.headquarters[unit_id].once_per_round_used = True
                    self.headquarters[unit_id].set_damage(afterwards_damage - 1)
                    total_that_can_be_blocked = total_that_can_be_blocked - 1
                    afterwards_damage = afterwards_damage - 1
                    if self.get_ability_given_pos(-2, unit_id) == "Righteous Initiate":
                        self.headquarters[unit_id].extra_attack_until_end_of_phase += 2
        if total_that_can_be_blocked > 0:
            self.game.damage_on_units_list_before_new_damage.append(prior_damage)
            self.game.damage_is_preventable.append(preventable)
            self.game.positions_of_units_to_take_damage.append((int(self.number), -2, unit_id))
            self.game.damage_can_be_shielded.append(can_shield)
            self.game.positions_attackers_of_units_to_take_damage.append(None)
            self.game.card_names_triggering_damage.append(context)
            self.game.amount_that_can_be_removed_by_shield.append(total_that_can_be_blocked)
        return damage_too_great

    def suffer_area_effect(self, planet_id, amount, faction="", shadow_field_possible=False, rickety_warbuggy=False):
        for i in range(len(self.cards_in_play[planet_id + 1])):
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
            return False
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.check_for_trait_given_pos(planet_id, i, trait):
                return True
        return False

    def get_health_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            health = self.headquarters[unit_id].get_health()
            if self.get_faction_given_pos(-2, unit_id) == "Orks":
                if self.get_card_type_given_pos(-2, unit_id) != "Token":
                    if self.search_card_in_hq("Mork's Great Heap"):
                        health += 1
            if self.headquarters[unit_id].get_ability() == "Lychguard Sentinel":
                if self.count_units_in_discard() > 5:
                    health += 4
            return health
        health = self.cards_in_play[planet_id + 1][unit_id].get_health()
        card = self.cards_in_play[planet_id + 1][unit_id]
        if self.get_faction_given_pos(planet_id, unit_id) == "Orks" and \
                self.check_for_trait_given_pos(planet_id, unit_id, "Vehicle"):
            if self.search_card_in_hq("Kustomisation Station"):
                health += 1
        if card.get_faction() == "Orks" and card.get_card_type() != "Token":
            if self.search_card_in_hq("Mork's Great Heap"):
                health += 1
        if card.get_ability() == "Sacaellum Shrine Guard" or card.get_ability() == "Saim-Hann Kinsman":
            if self.game.get_green_icon(planet_id):
                health += 1
        if self.check_for_trait_given_pos(planet_id, unit_id, "Warrior"):
            if self.search_card_at_planet(planet_id, "Talyesin Fharenal"):
                health += 1
        elif self.check_for_trait_given_pos(planet_id, unit_id, "Psyker"):
            if self.search_card_at_planet(planet_id, "Talyesin Fharenal"):
                health += 1
        if card.get_ability() == "Ramshackle Trukk":
            if self.get_enemy_has_init_for_cards(planet_id, unit_id):
                health += 4
        if card.get_faction() != "Necrons" and card.check_for_a_trait("Warrior"):
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Immortal Vanguard":
                    health += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_name() == "Termagant":
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Swarm Guard":
                    health += 2
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Pyrrhian Eternals":
            health += self.discard.count("Pyrrhian Eternals")
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Lychguard Sentinel":
            if self.count_units_in_discard() > 5:
                health += 4
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Ymgarl Genestealer":
            if self.search_synapse_at_planet(planet_id):
                health += 2
            else:
                if self.number == "1":
                    if self.game.p2.search_synapse_at_planet(planet_id):
                        health += 2
                elif self.number == "2":
                    if self.game.p1.search_synapse_at_planet(planet_id):
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
            if attachments[i].get_ability() == "Noxious Fleshborer":
                if self.game.infested_planets[planet_id]:
                    health += 1
            if attachments[i].get_ability() == "Frostfang":
                if self.number == "1":
                    if self.game.p2.check_for_warlord(planet_id):
                        health += 2
                elif self.number == "2":
                    if self.game.p1.check_for_warlord(planet_id):
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

    def check_if_card_is_destroyed(self, planet_id, unit_id):
        if planet_id == -2:
            if self.headquarters[unit_id].get_card_type() == "Support":
                return False
            return not self.check_damage_too_great_given_pos(planet_id, unit_id)
        return not self.check_damage_too_great_given_pos(planet_id, unit_id)

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
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Spore Chimney":
                if phase == "HEADQUARTERS":
                    self.game.create_reaction("Spore Chimney", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Weight of the Aeons":
                if self.get_ready_given_pos(-2, i):
                    self.game.create_reaction("Weight of the Aeons", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Obedience":
                if self.get_ready_given_pos(-2, i):
                    self.game.create_reaction("Obedience", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Deathmark Assassins":
                if phase == "COMBAT":
                    self.game.create_reaction("Deathmark Assassins", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Warlock Destructor":
                if phase == "DEPLOY":
                    self.game.create_reaction("Warlock Destructor", self.name_player, (int(self.number), -2, i))
            if self.headquarters[i].get_ability() == "Blood Rain Tempest":
                if phase == "COMBAT":
                    self.game.create_reaction("Blood Rain Tempest", self.name_player, (int(self.number), -2, i))
            for j in range(len(self.headquarters[i].get_attachments())):
                if phase == "COMBAT":
                    if self.headquarters[i].get_attachments()[j].get_ability() == "Parasitic Infection":
                        name_owner = self.headquarters[i].get_attachments()[j].name_owner
                        self.game.create_reaction("Parasitic Infection", name_owner, (int(self.number), -2, i))
                    if self.headquarters[i].get_attachments()[j].get_ability() == "Royal Phylactery":
                        if self.headquarters[i].get_damage() > 0:
                            owner = self.headquarters[i].get_attachments()[j].name_owner
                            self.game.create_reaction("Royal Phylactery", owner, (int(self.number), -2, i))

        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == "Warlock Destructor":
                    if phase == "DEPLOY":
                        self.game.create_reaction("Warlock Destructor", self.name_player, (int(self.number), i, j))
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
                        if self.cards_in_play[i + 1][j].get_attachments()[k].get_ability() == "Parasitic Infection":
                            name_owner = self.cards_in_play[i + 1][j].get_attachments()[k].name_owner
                            self.game.create_reaction("Parasitic Infection", name_owner, (int(self.number), i, j))
                    if self.cards_in_play[i + 1][j].get_attachments()[k].get_ability() == "Royal Phylactery":
                        if self.cards_in_play[i + 1][j].get_damage() > 0:
                            owner = self.cards_in_play[i + 1][j].get_attachments()[k].name_owner
                            self.game.create_reaction("Royal Phylactery", owner, (int(self.number), i, j))

    def sacrifice_card_in_hq(self, card_pos):
        if self.headquarters[card_pos].get_card_type() == "Warlord":
            return False
        if self.headquarters[card_pos].get_name() == "Cultist":
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
        if self.headquarters[card_pos].get_card_type() == "Warlord":
            if not self.headquarters[card_pos].get_bloodied():
                self.headquarters[card_pos].bloody_warlord()
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
                        if not self.death_serves_used:
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
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            elif ignore_uniques and not units_only:
                if not self.headquarters[i].get_unique():
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i, power=True):
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            elif not ignore_uniques and units_only:
                if card_type == "Army" or card_type == "Token":
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i, power=True):
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            else:
                if not enemy_event:
                    self.destroy_card_in_hq(i)
                    i = i - 1
                elif not self.get_immune_to_enemy_events(-2, i, power=True):
                    self.destroy_card_in_hq(i)
                    i = i - 1
                i = i + 1

    def discard_top_card_deck(self):
        if self.deck:
            self.discard.append(self.deck[0])
            del self.deck[0]
            return True
        return False

    def get_card_top_discard(self):
        if self.discard:
            card_name = self.discard[-1]
            card = FindCard.find_card(card_name, self.card_array, self.cards_dict)
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
        for i in range(len(self.cards_in_play[planet_num + 1])):
            if self.search_attachments_at_pos(planet_num, i, "Fenrisian Wolf", must_match_name=True):
                if self.get_ready_given_pos(planet_num, i):
                    self.game.create_reaction("Fenrisian Wolf", self.name_player, (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Kroot Guerrilla":
                self.game.create_reaction("Kroot Guerrilla", self.name_player, (int(self.number), planet_num, i))

    def resolve_combat_round_begins(self, planet_num):
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
            if self.cards_in_play[planet_num + 1][i].get_ability() == "Crush of Sky-Slashers":
                self.game.create_reaction("Crush of Sky-Slashers", self.name_player, (int(self.number), planet_num, i))
            if self.get_ability_given_pos(planet_num, i) == "Sathariel the Invokator":
                self.game.create_reaction("Sathariel the Invokator", self.name_player,
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

    def search_for_preemptive_destroy_interrupts(self):
        for i in range(len(self.headquarters)):
            if self.check_if_card_is_destroyed(-2, i):
                if self.search_attachments_at_pos(-2, i, "Ulthwe Spirit Stone"):
                    self.game.create_interrupt("Ulthwe Spirit Stone", self.name_player, (int(self.number), -2, i))
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.check_if_card_is_destroyed(i, j):
                    if self.search_attachments_at_pos(i, j, "Ulthwe Spirit Stone"):
                        self.game.create_interrupt("Ulthwe Spirit Stone", self.name_player, (int(self.number), i, j))

    def destroy_card_in_play(self, planet_num, card_pos):
        if planet_num == -2:
            self.destroy_card_in_hq(card_pos)
            return None
        if self.cards_in_play[planet_num + 1][card_pos].get_card_type() == "Warlord":
            if not self.cards_in_play[planet_num + 1][card_pos].get_bloodied():
                self.bloody_warlord_given_pos(planet_num, card_pos)
                self.warlord_just_got_bloodied = True
            else:
                self.add_card_in_play_to_discard(planet_num, card_pos)
                self.warlord_just_got_destroyed = True
        else:
            other_player = self.game.p1
            if other_player.name_player == self.name_player:
                other_player = self.game.p2
            if other_player.search_hand_for_card("Berzerker Warriors"):
                if not other_player.check_if_already_have_reaction("Berzerker Warriors"):
                    self.game.create_interrupt("Berzerker Warriors", other_player.name_player,
                                               (int(other_player.number), -1, -1))
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
            if self.check_for_trait_given_pos(planet_num, card_pos, "Dark Angels"):
                if self.search_card_in_hq("Standard of Devastation"):
                    self.game.create_reaction("Standard of Devastation", self.name_player,
                                              (int(self.number), -1, -1))
            if self.check_for_trait_given_pos(planet_num, card_pos, "Vehicle"):
                if not self.does_own_interrupt_exist("Death Serves the Emperor"):
                    if self.search_hand_for_card("Death Serves the Emperor"):
                        if not self.death_serves_used:
                            self.game.create_interrupt("Death Serves the Emperor", self.name_player,
                                                       (int(self.number), -1, -1))
                            cost = self.get_cost_given_pos(planet_num, card_pos)
                            if cost > self.highest_death_serves_value:
                                self.highest_death_serves_value = cost
                if not self.does_own_reaction_exist("The Bloodrunna"):
                    for i in range(len(self.cards_in_play[planet_num + 1])):
                        if i != card_pos:
                            for j in range(len(self.cards_in_play[planet_num + 1][i].get_attachments())):
                                if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability():
                                    if not self.cards_in_play[planet_num + 1][i].\
                                            get_attachments()[j].once_per_phase_used:
                                        self.game.create_reaction("The Bloodrunna", self.name_player,
                                                                  (int(self.number), planet_num, i))
                if not other_player.does_own_reaction_exist("The Bloodrunna"):
                    for i in range(len(other_player.cards_in_play[planet_num + 1])):
                        for j in range(len(other_player.cards_in_play[planet_num + 1][i].get_attachments())):
                            if other_player.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability():
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
                        self.game.create_reaction("Shrieking Exarch", self.name_player,
                                                  (int(self.number), planet_num, i))
                for i in range(len(other_player.cards_in_play[planet_num + 1])):
                    if other_player.get_ability_given_pos(planet_num, i) == "Shrieking Exarch":
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
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Shrouded Harlequin":
                self.game.create_reaction("Shrouded Harlequin", self.name_player,
                                          (int(self.number), -1, -1))
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Canoptek Scarab Swarm":
                self.game.create_reaction("Canoptek Scarab Swarm", self.name_player,
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
                        self.destroy_card_in_play(planet_num, i)
                        i = i - 1
                i = i + 1
            else:
                self.destroy_card_in_play(planet_num, i)

    def summon_token_at_planet(self, token_name, planet_num):
        card = FindCard.find_card(token_name, self.card_array, self.cards_dict)
        if card.get_name() != "FINAL CARD":
            if self.count_copies_in_play(card.get_name()) < 10:
                self.add_card_to_planet(card, planet_num)

    def summon_token_at_hq(self, token_name, amount=1):
        card = FindCard.find_card(token_name, self.card_array, self.cards_dict)
        if card.get_name() != "FINAL CARD":
            for _ in range(amount):
                if self.count_copies_in_play(card.get_name()) < 10:
                    self.add_to_hq(card)

    def remove_card_from_play(self, planet_num, card_pos):
        # card_object = self.cards_in_play[planet_num + 1][card_pos]
        # self.discard_object(card_object)
        del self.cards_in_play[planet_num + 1][card_pos]
        self.adjust_own_reactions(planet_num, card_pos)
        self.adjust_own_interrupts(planet_num, card_pos)
        self.adjust_last_def_pos(planet_num, card_pos)

    def remove_card_from_hq(self, card_pos):
        del self.headquarters[card_pos]
        self.adjust_own_reactions(-2, card_pos)
        self.adjust_own_interrupts(-2, card_pos)
        self.adjust_last_def_pos(-2, card_pos)

    def add_card_in_play_to_discard(self, planet_num, card_pos):
        if planet_num == -2:
            self.add_card_in_hq_to_discard(card_pos)
            return None
        card = self.cards_in_play[planet_num + 1][card_pos]
        card_name = card.get_name()
        if card.get_card_type() == "Army":
            for i in range(len(self.cards_in_play[planet_num + 1])):
                if self.cards_in_play[planet_num + 1][i].get_ability() == "Cadian Mortar Squad":
                    already_cadian_mortar_squad = False
                    for j in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[j] == "Cadian Mortar Squad":
                            if self.game.player_who_resolves_reaction[j] == self.name_player:
                                already_cadian_mortar_squad = True
                    if not already_cadian_mortar_squad:
                        self.game.create_reaction("Cadian Mortar Squad", self.name_player, (int(self.number),
                                                                                            planet_num, -1))
                for j in range(len(self.cards_in_play[planet_num + 1][i].get_attachments())):
                    if self.cards_in_play[planet_num + 1][i].get_attachments()[j].get_ability() \
                            == "Commissarial Bolt Pistol":
                        self.game.create_reaction("Commissarial Bolt Pistol", self.name_player,
                                                  (int(self.number), planet_num, i))
                        print("created bolt pistol react")
        for i in range(len(card.get_attachments())):
            owner = card.get_attachments()[i].name_owner
            if card.get_attachments()[i].get_ability() == "Straken's Cunning":
                self.game.create_reaction("Straken's Cunning", owner, (int(self.number), -1, -1))
            if card.get_attachments()[i].get_ability() == "M35 Galaxy Lasgun":
                self.game.create_interrupt("M35 Galaxy Lasgun", owner, (int(self.number), -1, -1))
            if card.get_attachments()[i].get_ability() == "Mark of Slaanesh":
                self.game.create_interrupt("Mark of Slaanesh", owner, (int(self.number), planet_num, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Straken's Command Squad":
            self.game.create_reaction("Straken's Command Squad", self.name_player, (int(self.number), planet_num, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Interrogator Acolyte":
            self.game.create_interrupt("Interrogator Acolyte", self.name_player, (int(self.number), planet_num, -1))
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Vanguard Soldiers":
            self.game.create_interrupt("Vanguard Soldiers", self.name_player, (int(self.number), planet_num, -1))
        for i in range(len(card.get_attachments())):
            if card.get_attachments()[i].get_ability() == "Mark of Chaos":
                owner = card.get_attachments()[i].name_owner
                self.game.create_reaction("Mark of Chaos", owner, (int(self.number), planet_num, -1))
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
        if self.get_ability_given_pos(planet_num, card_pos) == "Coteaz's Henchmen":
            self.game.create_reaction("Coteaz's Henchmen", self.name_player,
                                      (int(self.number), -1, -1))
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
        if self.game.request_search_for_enemy_card_at_planet(self.number, -2, "Cato's Stronghold", ready_relevant=True):
            self.game.reactions_needing_resolving.append("Cato's Stronghold")
            self.game.allowed_planets_cato_stronghold.append(planet_num)
            if self.number == "1":
                self.game.positions_of_unit_triggering_reaction.append([2, -1, -1])
                self.game.player_who_resolves_reaction.append(self.game.name_2)
            else:
                self.game.positions_of_unit_triggering_reaction.append([1, -1, -1])
                self.game.player_who_resolves_reaction.append(self.game.name_1)
        if card.get_ability() == "Enginseer Augur":
            self.game.create_reaction("Enginseer Augur", self.name_player, (int(self.number), -1, -1))
        if card.get_card_type() != "Token":
            if card.name_owner == self.name_player:
                self.discard.append(card_name)
                self.cards_recently_discarded.append(card_name)
            else:
                dis_player = self.game.p1
                if self.game.name_1 == self.name_player:
                    dis_player = self.game.p2
                dis_player.discard.append(card_name)
        if card.get_card_type() == "Army":
            if self.check_for_warlord(planet_num):
                self.stored_targets_the_emperor_protects.append(card_name)
        self.discard_attachments_from_card(planet_num, card_pos)
        self.remove_card_from_play(planet_num, card_pos)

    def add_card_in_hq_to_discard(self, card_pos):
        card = self.headquarters[card_pos]
        card_name = card.get_name()
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
            for i in range(len(card.get_attachments())):
                if card.get_attachments()[i].get_ability() == "Straken's Cunning":
                    owner = card.get_attachments()[i].name_owner
                    self.game.create_reaction("Straken's Cunning", owner, (int(self.number), -1, -1))
        if card.get_ability() == "Enginseer Augur":
            self.game.create_reaction("Enginseer Augur", self.name_player, (int(self.number), -1, -1))
        if card.get_ability() == "Kabalite Halfborn":
            self.game.create_reaction("Kabalite Halfborn", self.name_player, (int(self.number), -1, -1))
        if self.get_ability_given_pos(-2, card_pos) == "Coteaz's Henchmen":
            self.game.create_reaction("Coteaz's Henchmen", self.name_player, (int(self.number), -1, -1))
        if card.get_ability() == "Interrogator Acolyte":
            self.game.create_interrupt("Interrogator Acolyte", self.name_player, (int(self.number), -2, -1))
        if card.get_ability() == "Vanguard Soldiers":
            self.game.create_interrupt("Vanguard Soldiers", self.name_player, (int(self.number), -2, -1))
        if card.get_card_type() != "Token":
            if card.name_owner == self.name_player:
                self.discard.append(card_name)
                self.cards_recently_discarded.append(card_name)
            else:
                dis_player = self.game.p1
                if self.game.name_1 == self.name_player:
                    dis_player = self.game.p2
                dis_player.discard.append(card_name)
        self.discard_attachments_from_card(-2, card_pos)
        self.remove_card_from_hq(card_pos)

    def retreat_warlord(self):
        for i in range(len(self.cards_in_play[0])):
            if not self.cards_in_play[i + 1]:
                pass
            else:
                j = 0
                while j < len(self.cards_in_play[i + 1]):
                    print("TEST", self.cards_in_play[0][i], "planet", i)
                    print(self.cards_in_play[0])
                    print(len(self.cards_in_play[i + 1]))
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
        return True

    def resolve_combat_round_ends_effects(self, planet_id):
        can_forward_barracks = False
        self.defensive_protocols_active = False
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.get_ability_given_pos(planet_id, i) == "Anxious Infantry Platoon":
                self.game.create_reaction("Anxious Infantry Platoon", self.name_player,
                                          (int(self.number), planet_id, i))
            if self.get_faction_given_pos(planet_id, i) == "Astra Militarum":
                can_forward_barracks = True
        if can_forward_barracks:
            if self.search_card_in_hq("Forward Barracks"):
                self.game.create_reaction("Forward Barracks", self.name_player, (int(self.number), planet_id, -1))
        if self.game.get_green_icon(planet_id):
            for i in range(7):
                if i != planet_id:
                    for j in range(len(self.cards_in_play[i + 1])):
                        if self.cards_in_play[i + 1][j].get_ability() == "Taurox APC":
                            self.game.create_reaction("Taurox APC", self.name_player,
                                                      (int(self.number), i, j))

    def rout_unit(self, planet_id, unit_id):
        if self.check_for_trait_given_pos(planet_id, unit_id, "Elite"):
            if self.search_card_at_planet(planet_id, "Disciple of Excess"):
                return False
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
        return True

    def get_keywords_given_pos(self, planet_pos, unit_pos):
        keywords = []
        if planet_pos == -2:
            return keywords
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
        if self.number == "1":
            enemy_player = self.game.p2
        else:
            enemy_player = self.game.p1
        for i in range(len(enemy_player.cards_in_play[planet_id + 1])):
            if enemy_player.get_ability_given_pos(planet_id, i) == "Morkai Rune Priest":
                mork_count += 1
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        last_element_hq = len(self.headquarters) - 1
        if self.headquarters[last_element_hq].check_for_a_trait("Space Wolves"):
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

    def set_once_per_round_used_given_pos(self, planet_id, unit_id, new_val):
        if planet_id == -2:
            self.headquarters[unit_id].set_once_per_round_used(new_val)
            return None
        self.cards_in_play[planet_id + 1][unit_id].set_once_per_round_used(new_val)
        return None

    def refresh_all_once_per_round(self):
        for i in range(len(self.headquarters)):
            self.set_once_per_round_used_given_pos(-2, i, True)
        for j in range(7):
            for i in range(len(self.cards_in_play[j + 1])):
                self.set_once_per_round_used_given_pos(j, i, True)

    def ready_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
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
        print("Checking for cards at:", self.cards_in_play[0][planet_id])
        if not self.cards_in_play[planet_id + 1]:
            print("No cards present.")
            return 0
        print("Cards present.")
        return 1

    def retreat_all_at_planet(self, planet_id):
        while self.cards_in_play[planet_id + 1]:
            self.retreat_unit(planet_id, 0)

    def move_all_at_planet_to_hq(self, planet_id):
        while self.cards_in_play[planet_id + 1]:
            self.move_unit_at_planet_to_hq(planet_id, 0)

    def capture_planet(self, planet_id, planet_cards):
        planet_name = self.cards_in_play[0][planet_id]
        print("Attempting to capture planet.")
        print("Planet to capture:", planet_name)
        i = 0
        for letter in planet_name:
            if letter == "_":
                planet_name = planet_name.replace(letter, " ")
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
