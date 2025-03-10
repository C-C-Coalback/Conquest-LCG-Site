from . import FindCard
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
    def __init__(self, name, number, card_array, game):
        self.game = game
        self.card_array = card_array
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
        self.warlord_commit_location = -1
        self.warlord_just_got_bloodied = False
        self.condition_player_main = threading.Condition()
        self.condition_player_sub = threading.Condition()
        self.aiming_reticle_color = None
        self.aiming_reticle_coords_hand = None
        self.can_play_limited = True

    async def setup_player(self, raw_deck, planet_array):
        self.condition_player_main.acquire()
        deck_list = clean_received_deck(raw_deck)
        self.headquarters.append(FindCard.find_card(deck_list[0], self.card_array))
        self.deck = deck_list[1:]
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
            await self.game.game_sockets[i].receive_game_update("Setup of " + self.name_player + " finished.")
        await self.send_hq()
        await self.send_units_at_all_planets()
        await self.send_resources()
        self.condition_player_main.notify_all()
        self.condition_player_main.release()

    def get_can_play_limited(self):
        return self.can_play_limited

    def set_can_play_limited(self, new_val):
        self.can_play_limited = new_val

    async def send_hand(self):
        if self.cards:
            card_array = self.cards.copy()
            if self.aiming_reticle_color is None:
                pass
            else:
                for i in range(len(card_array)):
                    if self.aiming_reticle_coords_hand == i:
                        card_array[i] = card_array[i] + "|" + self.aiming_reticle_color
            card_string = "/".join(card_array)
            card_string = "GAME_INFO/HAND/" + str(self.number) + "/" + self.name_player + "/" + card_string
            await self.game.game_sockets[0].receive_game_update(card_string)
        else:
            card_string = "GAME_INFO/HAND/" + str(self.number) + "/" + self.name_player
            await self.game.game_sockets[0].receive_game_update(card_string)

    async def send_hq(self):
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
                    single_card_string += str(current_card.get_damage())
                else:
                    single_card_string += "0"
                single_card_string += "|"
                if card_type == "Warlord":
                    if current_card.get_bloodied():
                        single_card_string += "B|"
                    else:
                        single_card_string += "H|"
                card_strings.append(single_card_string)
            joined_string = "/".join(card_strings)
            joined_string = "GAME_INFO/HQ/" + str(self.number) + "/" + joined_string
            print(joined_string)
            await self.game.game_sockets[0].receive_game_update(joined_string)
        else:
            joined_string = "GAME_INFO/HQ/" + str(self.number)
            await self.game.game_sockets[0].receive_game_update(joined_string)

    async def send_units_at_planet(self, planet_id):
        if self.cards_in_play[planet_id + 1]:
            print("Need to send units")
            card_strings = []
            for i in range(len(self.cards_in_play[planet_id + 1])):
                current_card = self.cards_in_play[planet_id + 1][i]
                single_card_string = current_card.get_name()
                single_card_string = single_card_string + "|"
                if current_card.ready:
                    single_card_string += "R|"
                else:
                    single_card_string += "E|"
                single_card_string += str(current_card.get_damage())
                single_card_string += "|"
                if current_card.get_card_type() == "Warlord":
                    if current_card.get_bloodied():
                        single_card_string += "B"
                    else:
                        single_card_string += "H"
                else:
                    single_card_string += "H"
                if current_card.aiming_reticle_color is None:
                    pass
                else:
                    single_card_string += "|"
                    single_card_string += current_card.aiming_reticle_color
                card_strings.append(single_card_string)
            joined_string = "/".join(card_strings)
            joined_string = "GAME_INFO/IN_PLAY/" + str(self.number) + "/" + str(planet_id) + "/" + joined_string
            print(joined_string)
            await self.game.game_sockets[0].receive_game_update(joined_string)
        else:
            joined_string = "GAME_INFO/IN_PLAY/" + str(self.number) + "/" + str(planet_id)
            await self.game.game_sockets[0].receive_game_update(joined_string)

    async def send_units_at_all_planets(self):
        for i in range(7):
            await self.send_units_at_planet(i)

    async def send_resources(self):
        joined_string = "GAME_INFO/RESOURCES/" + str(self.number) + "/" + str(self.resources)
        await self.game.game_sockets[0].receive_game_update(joined_string)

    async def send_victory_display(self):
        if self.victory_display:
            card_strings = []
            for i in range(len(self.victory_display)):
                card_strings.append(self.victory_display[i].get_name())
            joined_string = "/".join(card_strings)
            joined_string = "GAME_INFO/VICTORY_DISPLAY/" + str(self.number) + "/" + joined_string
            print(joined_string)
            await self.game.game_sockets[0].receive_game_update(joined_string)
        else:
            joined_string = "GAME_INFO/VICTORY_DISPLAY/" + str(self.number)
            await self.game.game_sockets[0].receive_game_update(joined_string)

    async def send_discard(self):
        top_card = self.get_top_card_discard()
        if top_card is None:
            joined_string = "GAME_INFO/DISCARD/" + str(self.number)
            await self.game.game_sockets[0].receive_game_update(joined_string)
        else:
            joined_string = "GAME_INFO/DISCARD/" + str(self.number) + "/" + top_card
            await self.game.game_sockets[0].receive_game_update(joined_string)

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

    def draw_card(self):
        if not self.deck:
            print("Deck is empty, you lose!")
        else:
            self.cards.append(self.deck[0])
            del self.deck[0]

    def spend_resources(self, amount):
        if amount > self.resources:
            return False
        else:
            if amount < 0:
                amount = 0
            self.resources = self.resources - amount
            return True

    def add_resources(self, amount):
        self.resources += amount

    def check_if_warlord(self, planet_id, unit_id):
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Warlord":
            return True
        return False

    def set_aiming_reticle_in_play(self, planet_id, unit_id, color):
        self.cards_in_play[planet_id + 1][unit_id].aiming_reticle_color = color

    def reset_aiming_reticle_in_play(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].aiming_reticle_color = None

    def discard_card_from_hand(self, card_pos):
        self.discard.append(self.cards[card_pos])
        del self.cards[card_pos]

    def get_shields_given_pos(self, pos_in_hand):
        shield_card_name = self.cards[pos_in_hand]
        card_object = FindCard.find_card(shield_card_name, self.card_array)
        return card_object.get_shields()

    def get_damage_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_damage()

    def set_damage_given_pos(self, planet_id, unit_id, amount):
        return self.cards_in_play[planet_id + 1][unit_id].set_damage(amount)

    def get_ranged_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ranged()

    def bloody_warlord_given_pos(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].bloody_warlord()
        self.retreat_warlord()

    def shuffle_deck(self):
        shuffle(self.deck)

    def add_to_hq(self, card_object):
        self.headquarters.append(copy.deepcopy(card_object))

    def print_headquarters(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].print_info()

    def play_card_if_support(self, position_hand, already_checked=False, card=None):
        if already_checked:
            played_card = self.play_card(-2, card=card)
            if played_card == "SUCCESS":
                return "SUCCESS/Support"
            return played_card
        card = FindCard.find_card(self.cards[position_hand], self.card_array)
        if card.card_type == "Support":
            print("Need to play support card")
            played_card = self.play_card(-2, card=card)
            if played_card == "SUCCESS":
                return "SUCCESS/Support"
            return played_card
        return "SUCCESS/Not Support"

    def get_card_in_hand(self, position_hand):
        card = FindCard.find_card(self.cards[position_hand], self.card_array)
        return card

    def add_card_to_planet(self, card, position):
        self.cards_in_play[position + 1].append(copy.deepcopy(card))

    def play_card(self, position, card=None, position_hand=None, discounts=0):
        if card is None and position_hand is None:
            return "ERROR/play_card function called incorrectly"
        if card is not None and position_hand is not None:
            return "ERROR/play_card function called incorrectly"
        if card is not None:
            cost = card.get_cost() - discounts
            if position == -2:
                print("Play card to HQ")
                print(card.get_limited(), self.can_play_limited)
                if card.get_limited():
                    if self.can_play_limited:
                        if self.spend_resources(cost):
                            self.add_to_hq(card)
                            self.cards.remove(card.get_name())
                            self.set_can_play_limited(False)
                            print("Played card to HQ")
                            return "SUCCESS"
                    else:
                        return "FAIL/Limited already played"
                else:
                    if self.spend_resources(cost):
                        self.add_to_hq(card)
                        self.cards.remove(card.get_name())
                        print("Played card to HQ")
                        return "SUCCESS"
                print("Insufficient resources")
                return "FAIL/Insufficient resources"
        if position_hand is not None:
            if position_hand != -1:
                if -1 < position < 7:
                    card = FindCard.find_card(self.cards[position_hand], self.card_array)
                    cost = card.get_cost() - discounts
                    if card.get_limited():
                        if self.can_play_limited:
                            if self.spend_resources(cost):
                                self.add_card_to_planet(card, position)
                                self.cards.remove(card.get_name())
                                self.set_can_play_limited(False)
                                print("Played card to planet", position)
                                return "SUCCESS"
                        else:
                            return "FAIL/Limited already played"
                    else:
                        if self.spend_resources(cost):
                            self.add_card_to_planet(card, position)
                            self.cards.remove(card.get_name())
                            print("Played card to planet", position)
                            return "SUCCESS"
                    print("Insufficient resources")
                    return "FAIL/Insufficient resources"
        return "FAIL/Invalid card"

    def commit_warlord_to_planet(self, planet_pos=None, only_warlord=False):
        headquarters_list = self.get_headquarters()
        if planet_pos is None:
            planet_pos = self.warlord_commit_location + 1
        if only_warlord:
            for i in range(len(headquarters_list)):
                if headquarters_list[i].get_card_type() == "Warlord":
                    print(headquarters_list[i].get_name())
                    summon_khymera = False
                    if headquarters_list[i].get_ability() == "Packmaster Kith":
                        summon_khymera = True
                    self.cards_in_play[planet_pos].append(copy.deepcopy(headquarters_list[i]))
                    self.headquarters.remove(headquarters_list[i])
                    if summon_khymera:
                        self.summon_token_at_planet("Khymera", planet_pos - 1)
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
                            headquarters_list[i].ready_card()
                    summon_khymera = False
                    if headquarters_list[i].get_ability() == "Packmaster Kith":
                        summon_khymera = True
                    self.cards_in_play[planet_pos].append(copy.deepcopy(headquarters_list[i]))
                    self.headquarters.remove(headquarters_list[i])
                    if summon_khymera:
                        self.summon_token_at_planet("Khymera", planet_pos - 1)
                    i -= 1
                i += 1
        return None

    def count_command_at_planet(self, planet_id):
        counted_command = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            counted_command += self.cards_in_play[planet_id + 1][i].get_command()
            if self.cards_in_play[planet_id + 1][i].get_ability() == "Iron Hands Techmarine":
                counted_command += self.game.request_number_of_enemy_units_at_planet(self.number, planet_id)
        return counted_command

    def check_for_warlord(self, planet_id):
        print("Looking for warlord at:", self.cards_in_play[0][planet_id])
        if not self.cards_in_play[planet_id + 1]:
            pass
        else:
            for j in range(len(self.cards_in_play[planet_id + 1])):
                print("Card is:", self.cards_in_play[planet_id + 1][j].get_name())
                print("Check if card is a warlord.")
                if self.cards_in_play[planet_id + 1][j].get_card_type() == "Warlord":
                    print("Card is a Warlord")
                    return 1
                else:
                    print("Card is not a Warlord")
        print("Warlord is not present")
        return 0

    def check_ready_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ready()

    def get_flying_given_pos(self, planet_id, unit_id):
        rokkitboy_present = self.game.request_search_for_enemy_card_at_planet(self.number, planet_id, "Rokkitboy")
        if rokkitboy_present:
            return False
        return self.cards_in_play[planet_id + 1][unit_id].get_flying()

    def get_armorbane_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_armorbane()

    def search_card_at_planet(self, planet_id, name_of_card, bloodied_relevant=False, ability_checking=True):
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
            return False
        for i in range(len(self.cards_in_play[planet_id + 1])):
            current_name = self.cards_in_play[planet_id + 1][i].get_ability()
            print(current_name, name_of_card)
            if current_name == name_of_card:
                if not bloodied_relevant:
                    return True
                if self.cards_in_play[planet_id + 1][i].get_bloodied():
                    return False
                return True
        return False

    def search_card_in_hq(self, name_of_card, bloodied_relevant=False, ability_checking=True):
        for i in range(len(self.headquarters)):
            current_name = self.headquarters[i].get_ability()
            print(current_name, name_of_card)
            if current_name == name_of_card:
                if not bloodied_relevant:
                    return True
                if self.headquarters[i].get_bloodied():
                    return False
                return True
        return False

    def search_hq_for_discounts(self, faction_of_card):
        discounts_available = 0
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_applies_discounts():
                if self.headquarters[i].get_is_faction_limited_unique_discounter():
                    if self.headquarters[i].get_faction() == faction_of_card:
                        if self.headquarters[i].get_ready():
                            discounts_available += self.headquarters[i].get_discount_amount()

        return discounts_available

    def perform_discount_at_pos_hq(self, pos, faction_of_card):
        discount = 0
        if self.headquarters[pos].get_applies_discounts():
            if self.headquarters[pos].get_is_faction_limited_unique_discounter():
                if self.headquarters[pos].get_faction() == faction_of_card:
                    if self.headquarters[pos].get_ready():
                        self.headquarters[pos].exhaust_card()
                        discount += self.headquarters[pos].get_discount_amount()
        return discount

    def exhaust_given_pos(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].exhaust_card()

    def get_attack_given_pos(self, planet_id, unit_id):
        attack_value = self.cards_in_play[planet_id + 1][unit_id].get_attack()
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() != "Nazdreg":
            nazdreg_check = self.search_card_at_planet(planet_id, "Nazdreg", bloodied_relevant=True)
            if nazdreg_check:
                self.cards_in_play[planet_id + 1][unit_id].set_brutal(True)
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() != "Colonel Straken":
            straken_check = self.search_card_at_planet(planet_id, "Colonel Straken", bloodied_relevant=True)
            if straken_check:
                if self.cards_in_play[planet_id + 1][unit_id].check_for_a_trait("Soldier") or \
                        self.cards_in_play[planet_id + 1][unit_id].check_for_a_trait("Warrior"):
                    attack_value += 1
        if self.cards_in_play[planet_id + 1][unit_id].get_ability() == "Goff Boyz":
            if self.game.round_number == planet_id:
                attack_value = attack_value + 3
        if self.cards_in_play[planet_id + 1][unit_id].get_brutal():
            attack_value = attack_value + self.cards_in_play[planet_id + 1][unit_id].get_damage()
        self.cards_in_play[planet_id + 1][unit_id].reset_brutal()
        attack_value += self.cards_in_play[planet_id + 1][unit_id].get_extra_attack_until_end_of_battle()
        return attack_value

    def assign_damage_to_pos(self, planet_id, unit_id, damage, can_shield=True):
        zara_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_id,
                                                                       "Zarathur, High Sorcerer",
                                                                       bloodied_relevant=True)
        if zara_check:
            damage += 1
        damage_too_great = self.cards_in_play[planet_id + 1][unit_id].damage_card(self, damage, can_shield)
        return damage_too_great

    def suffer_area_effect(self, planet_id, amount):
        for i in range(len(self.cards_in_play[planet_id + 1])):
            self.assign_damage_to_pos(planet_id, i, amount)

    def get_number_of_units_at_planet(self, planet_id):
        return len(self.cards_in_play[planet_id + 1])

    def check_if_card_is_destroyed(self, planet_id, unit_id):
        return not self.cards_in_play[planet_id + 1][unit_id].check_health()

    def remove_damage_from_pos(self, planet_id, unit_id, amount):
        self.cards_in_play[planet_id + 1][unit_id].remove_damage(amount)

    def destroy_card_in_play(self, planet_num, card_pos):
        if self.cards_in_play[planet_num + 1][card_pos].get_card_type() == "Warlord":
            if not self.cards_in_play[planet_num + 1][card_pos].get_bloodied():
                self.bloody_warlord_given_pos(planet_num, card_pos)
                self.warlord_just_got_bloodied = True
            else:
                self.add_card_in_play_to_discard(planet_num, card_pos)
        else:
            cato_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_num,
                                                                           "Captain Cato Sicarius",
                                                                           bloodied_relevant=True)
            if cato_check:
                self.game.add_resources_to_opponent(self.number, 1)
            self.add_card_in_play_to_discard(planet_num, card_pos)

    def destroy_all_cards_at_planet(self, planet_num, ignore_uniques=True):
        i = 0
        while i < len(self.cards_in_play[planet_num + 1]):
            if ignore_uniques:
                if not self.cards_in_play[planet_num + 1][i].get_unique():
                    self.destroy_card_in_play(planet_num, i)
                    i = i - 1
                i = i + 1
            else:
                self.destroy_card_in_play(planet_num, i)

    def summon_token_at_planet(self, token_name, planet_num):
        card = FindCard.find_card(token_name, self.card_array)
        if card.get_name() != "FINAL CARD":
            self.add_card_to_planet(card, planet_num)

    def summon_token_at_hq(self, token_name, amount=1):
        card = FindCard.find_card(token_name, self.card_array)
        if card.get_name() != "FINAL CARD":
            for _ in range(amount):
                self.add_to_hq(card)

    def remove_card_from_play(self, planet_num, card_pos):
        # card_object = self.cards_in_play[planet_num + 1][card_pos]
        # self.discard_object(card_object)
        del self.cards_in_play[planet_num + 1][card_pos]

    def add_card_in_play_to_discard(self, planet_num, card_pos):
        card_name = self.cards_in_play[planet_num + 1][card_pos].get_name()
        self.discard.append(card_name)
        self.remove_card_from_play(planet_num, card_pos)

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
                        self.retreat_unit(i, j)
                        j = j - 1
                    j = j + 1

    def retreat_unit(self, planet_id, unit_id):
        # print("Name of card:", self.cards_in_play[planet_id + 1][unit_id].get_name())
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        del self.cards_in_play[planet_id + 1][unit_id]

    def ready_all_in_headquarters(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].ready_card()

    def ready_all_in_play(self):
        for i in range(len(self.cards_in_play[0])):
            self.ready_all_at_planet(i)
        self.ready_all_in_headquarters()

    def ready_all_at_planet(self, planet_id):
        for i in range(len(self.cards_in_play[planet_id + 1])):
            self.ready_given_pos(planet_id, i)

    def ready_given_pos(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].ready_card()

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


"""
    def play_card(self, position, card):
        if position is None:
            if self.spend_resources(card.get_cost()):
                self.add_to_hq(card)
                self.cards.remove(card.get_name())
                print("Played card to HQ")
                return "SUCCESS"
            print("Insufficient resources")
            self.c.notify_all()
            self.c.release()
            return "FAIL"
        if not self.planets_in_play[position]:
            self.c.notify_all()
            self.c.release()
            return "FAIL"
        if self.spend_resources(card.get_cost()):
            self.cards_in_play[position + 1].append(copy.deepcopy(card))
            self.cards.remove(card.get_name())
            self.c.notify_all()
            self.c.release()
            return "SUCCESS"
        print("Insufficient resources")
        self.c.notify_all()
        self.c.release()
        return "FAIL" """

"""
    

    

    def get_cards_in_play(self):
        return self.cards_in_play

    def retreat_combat_window(self, planet_id):
        self.position_activated = []
        while True:
            pygame.time.wait(500)
            self.c.acquire()
            self.c.notify_all()
            current_active = self.position_activated
            self.c.release()
            self.set_turn(True)
            self.extra_text = "Retreat window"
            print(current_active)
            if len(current_active) == 1:
                if current_active[0] == "PASS":
                    self.set_turn(False)
                    return True
            if len(current_active) == 4:
                if current_active[1] == "PLAY":
                    if int(current_active[0][1]) == self.get_number():
                        print("Correct player and is in play. Advancing.")
                        pos_planet = int(current_active[2])
                        if pos_planet == planet_id:
                            print("Correct planet.")
                            pos_unit = int(current_active[3])
                            if len(self.get_cards_in_play()[planet_id + 1]) > pos_unit:
                                print("Valid unit.")
                                self.exhaust_given_pos(planet_id, pos_unit)
                                self.retreat_unit(planet_id, pos_unit)
                                self.position_activated = []



    def capture_planet(self, planet_id):
        planet_name = self.cards_in_play[0][planet_id]
        print("Attempting to capture planet.")
        print("Planet to capture:", planet_name)
        planet_cards = UseInits.planet_array
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

    def take_deploy_turn(self):
        self.position_activated = []
        self.set_turn(True)
        self.extra_text = "Deploy turn"
        while True:
            pygame.time.wait(500)
            self.c.acquire()
            self.c.notify_all()
            current_active = self.position_activated
            self.c.release()
            if len(current_active) > 0:
                if current_active[0] == "PASS":
                    print("PASS NEEDED")
                    self.set_turn(False)
                    return True
                if len(current_active) > 1:
                    print("GOT HERE + :", current_active)
                    if current_active[1] == "Hand" and int((current_active[0])[1]) == self.number:
                        if int(current_active[2]) < len(self.cards):
                            print("Card needs to be deployed")
                            print("Position of card: Player", current_active[0], "Hand pos:", current_active[2])
                            self.bonus_boxes = "Hand/" + current_active[0] + "/" + current_active[2] + "/green"
                            self.c.acquire()
                            self.c.notify_all()
                            self.position_activated = []
                            self.c.notify_all()
                            self.c.release()
                            card_object = FindCard.find_card(self.cards[int(current_active[2])])
                            if card_object.get_card_type() == "Army":
                                print("Card is an army unit")
                                self.extra_text = "Choose planet"
                                ret_val = self.select_planet_to_play_card(card_object)
                                self.bonus_boxes = ""
                                if ret_val != "PASS" and ret_val != "FAIL":
                                    print("Successfully played card")
                                    self.set_turn(False)
                                    return False
                                print("Cancelling playing the card.")
                            if card_object.get_card_type() == "Support":
                                print("Card is a support")
                                ret_val = self.play_card(None, card_object)
                                self.bonus_boxes = ""
                                if ret_val != "PASS" and ret_val != "FAIL":
                                    print("Successfully played card")
                                    self.set_turn(False)
                                    return False
                                print("Cancelling playing the card.")

    def select_planet_to_play_card(self, card):
        while True:
            pygame.time.wait(125)
            current_active = self.position_activated
            if len(current_active) > 0:
                if current_active[0] == "PASS":
                    return "PASS"
                if current_active[0] == "Planet":
                    int_planet = int(current_active[1])
                    print("position of planet to deploy unit:", int_planet)
                    return self.play_card(int_planet, card)

    def commit_warlord_step(self):
        self.position_activated = []
        self.set_turn(True)
        while True:
            pygame.time.wait(125)
            self.c.acquire()
            self.c.notify_all()
            current_active = self.position_activated
            self.c.release()
            self.set_turn(True)
            self.extra_text = "Commit Warlord"
            if len(current_active) > 0:
                if current_active[0] == "Planet":
                    int_planet = int(current_active[1])
                    print("position of planet to commit warlord:", int_planet)
                    self.commit_warlord_to_planet(int_planet + 1)
                    self.set_turn(False)
                    return True

    def commit_warlord_to_planet(self, planet_pos):
        headquarters_list = self.get_headquarters()
        for i in range(len(headquarters_list)):
            if headquarters_list[i].get_card_type() == "Warlord":
                print(headquarters_list[i].get_name())
                self.cards_in_play[planet_pos].append(copy.deepcopy(headquarters_list[i]))
                self.headquarters.remove(headquarters_list[i])
                return True
                # self.commit_units_to_planet(planet_id)

    def count_command_at_planet(self, planet_id):
        command = 0
        for i in range(len(self.cards_in_play[planet_id])):
            print(self.cards_in_play[planet_id][i].get_command())
            if self.cards_in_play[planet_id][i].get_ready():
                command += self.cards_in_play[planet_id][i].get_command()
        return command

    

    def get_planet_name_given_position(self, planet_id):
        return self.cards_in_play[0][planet_id]

    def print_cards_at_planet(self, planet_id):
        for j in range(len(self.cards_in_play[planet_id + 1])):
            print(self.cards_in_play[planet_id + 1][j].get_name())

    def print_position_active(self):
        while True:
            t = input("")
            if t == "STOP":
                break
            print("Player", self.number, "active position:", self.position_activated)

    def toggle_initiative(self):
        self.has_initiative = not self.has_initiative

    def get_initiative(self):
        return self.has_initiative

    def get_active_position(self):
        return self.position_activated

    def set_active_position(self, new_val):
        self.position_activated = new_val

    def get_resources(self):
        return self.resources

    def get_planets_in_play_for_message(self):
        message = "#"
        for i in range(7):
            message += self.cards_in_play[0][i]
            if i != 6:
                message += "/"
        message += "#"
        for i in range(7):
            message += str(self.planets_in_play[i])
            if i != 6:
                message += "/"
        return message

    def get_hand_for_message(self):
        message = "#"
        for i in range(len(self.cards)):
            message += self.cards[i]
            if i != len(self.cards) - 1:
                message += "/"
        return message

    def get_hq_for_message(self):
        message = "#"
        if len(self.headquarters) == 0:
            message += "NONE"
        for i in range(len(self.headquarters)):
            message += self.headquarters[i].get_name()
            c_t = self.headquarters[i].get_card_type()
            message += "("
            if c_t == "Warlord":
                if self.headquarters[i].get_bloodied_state():
                    message += "B"
                else:
                    message += "H"
            else:
                message += "H"
            message += "!"
            if self.headquarters[i].get_ready():
                message += "R"
            else:
                message += "E"
            message += "!"
            damage = 0
            if c_t == "Warlord" or c_t == "Army" or c_t == "Token":
                damage += self.headquarters[i].get_damage()
            message += str(damage) + ")"
            if i != len(self.headquarters) - 1:
                message += "/"
        return message

    def increment_round_number(self):
        self.round_number += 1

    def get_victory_display_for_message(self):
        if len(self.victory_display) == 0:
            return "NONE"
        message = ""
        for i in range(len(self.victory_display)):
            message += self.victory_display[i].get_name()
            if i != len(self.victory_display) - 1:
                message += "/"
        return message

    def get_all_planets_for_message(self):
        message = ""
        planet_num = 1
        while planet_num < 8:
            message += self.get_one_planet_for_message(planet_num)
            planet_num += 1
        return message

    def get_one_planet_for_message(self, planet_pos):
        message = "#"
        if len(self.cards_in_play[planet_pos]) == 0:
            message += "NONE"
        for i in range(len(self.cards_in_play[planet_pos])):
            message += self.cards_in_play[planet_pos][i].get_name()
            c_t = self.cards_in_play[planet_pos][i].get_card_type()
            message += "("
            if c_t == "Warlord":
                if self.cards_in_play[planet_pos][i].get_bloodied_state():
                    message += "B"
                else:
                    message += "H"
            else:
                message += "H"
            message += "!"
            if self.cards_in_play[planet_pos][i].get_ready():
                message += "R"
            else:
                message += "E"
            message += "!"
            damage = 0
            # if c_t == "Warlord" or c_t == "Army" or c_t == "Token":
            damage += self.cards_in_play[planet_pos][i].get_damage()
            message += str(damage) + ")"
            if i != len(self.cards_in_play[planet_pos]) - 1:
                message += "/"
        return message

"""
