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
        self.number_cards_to_search = 0

    async def setup_player(self, raw_deck, planet_array):
        self.condition_player_main.acquire()
        deck_list = clean_received_deck(raw_deck)
        self.headquarters.append(copy.deepcopy(FindCard.find_card(deck_list[0], self.card_array)))
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
                else:
                    single_card_string += "H|"
                if current_card.aiming_reticle_color is not None:
                    single_card_string += current_card.aiming_reticle_color
                attachments_list = current_card.get_attachments()
                for a in range(len(attachments_list)):
                    print("Adding attachments")
                    print(attachments_list[a].get_name())
                    single_card_string += "|"
                    single_card_string += attachments_list[a].get_name()
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
                single_card_string += "|"
                if current_card.aiming_reticle_color is not None:
                    single_card_string += current_card.aiming_reticle_color
                attachments_list = current_card.get_attachments()
                for a in range(len(attachments_list)):
                    print("Adding attachments")
                    print(attachments_list[a].get_name())
                    single_card_string += "|"
                    single_card_string += attachments_list[a].get_name()
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

    def draw_card_at_location_deck(self, position):
        if not self.deck:
            print("Deck is empty, you lose!")
        else:
            if len(self.deck) > position:
                self.cards.append(self.deck[position])
                del self.deck[position]

    def bottom_remaining_cards(self):
        self.deck = self.deck[self.number_cards_to_search:] + self.deck[:self.number_cards_to_search]

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

    def remove_card_from_hand(self, card_pos):
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
        last_element_index = len(self.headquarters) - 1
        if self.headquarters[last_element_index].get_ability() == "Promethium Mine":
            self.headquarters[last_element_index].set_counter(4)
        elif self.headquarters[last_element_index].get_ability() == "Swordwind Farseer":
            if len(self.deck) > 5:
                self.number_cards_to_search = 6
                self.game.cards_in_search_box = self.deck[0:self.number_cards_to_search]
                self.game.name_player_who_is_searching = self.name_player
                self.game.number_who_is_searching = str(self.number)

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

    def attach_card(self, card, planet, position):
        if planet == -2:
            target_card = self.headquarters[position]
        else:
            target_card = self.cards_in_play[planet + 1][position]
        print("Adding attachment code")
        print(card.get_name())
        print(target_card.get_no_attachments())
        allowed_types = card.type_of_units_allowed_for_attachment
        type_of_card = target_card.get_card_type()
        if type_of_card not in allowed_types:
            print("Can't play to this card type.", type_of_card, allowed_types)
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
        target_card.add_attachment(card)
        return True

    def play_attachment_card_to_in_play(self, card, planet, position, discounts=0, not_own_attachment=False):
        if card.must_be_own_unit and not_own_attachment:
            print("Must be own unit, but is not")
            return False
        if card.must_be_enemy_unit and not not_own_attachment:
            print("Must be enemy unit, but is not")
            return False
        if not_own_attachment:
            if self.attach_card(card, planet, position):
                return True
            return False
        cost = card.get_cost() - discounts
        if self.spend_resources(cost):
            if self.attach_card(card, planet, position):
                return True
            self.add_resources(cost)
        return False

    def add_card_to_planet(self, card, position):
        self.cards_in_play[position + 1].append(copy.deepcopy(card))
        last_element_index = len(self.cards_in_play[position + 1]) - 1
        if self.cards_in_play[position + 1][last_element_index].get_ability() == "Swordwind Farseer":
            if len(self.deck) > 5:
                self.number_cards_to_search = 6
                self.game.cards_in_search_box = self.deck[0:self.number_cards_to_search]
                self.game.name_player_who_is_searching = self.name_player
                self.game.number_who_is_searching = str(self.number)

    def play_card(self, position, card=None, position_hand=None, discounts=0, damage_to_take=0):
        if card is None and position_hand is None:
            return "ERROR/play_card function called incorrectly", -1
        if card is not None and position_hand is not None:
            return "ERROR/play_card function called incorrectly", -1
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
                            return "SUCCESS", -1
                    else:
                        return "FAIL/Limited already played", -1
                else:
                    if self.spend_resources(cost):
                        self.add_to_hq(card)
                        self.cards.remove(card.get_name())
                        print("Played card to HQ")
                        if card.get_ability() == "Murder of Razorwings":
                            self.game.discard_card_at_random_from_opponent(self.number)
                        return "SUCCESS", -1
                print("Insufficient resources")
                return "FAIL/Insufficient resources", -1
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
                                location_of_unit = len(self.cards_in_play[position + 1]) - 1
                                if damage_to_take > 0:
                                    self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                                return "SUCCESS", location_of_unit
                        else:
                            return "FAIL/Limited already played", -1
                    else:
                        if self.spend_resources(cost):
                            self.add_card_to_planet(card, position)
                            self.cards.remove(card.get_name())
                            print("Played card to planet", position)
                            print(card.get_ability())
                            location_of_unit = len(self.cards_in_play[position + 1]) - 1
                            if damage_to_take > 0:
                                self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                            if card.get_ability() == "Murder of Razorwings":
                                self.game.discard_card_at_random_from_opponent(self.number)
                            if card.get_ability() == "Kith's Khymeramasters":
                                self.summon_token_at_planet("Khymera", position)
                            return "SUCCESS", location_of_unit
                    print("Insufficient resources")
                    return "FAIL/Insufficient resources", -1
        return "FAIL/Invalid card", -1

    def discard_card_at_random(self):
        print("")
        if self.cards:
            pos = random.randint(1, len(self.cards) - 1)
            print(pos)
            self.discard_card_from_hand(pos)

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

    def get_bonus_winnings_at_planet(self, planet_id):
        extra_resources = 0
        extra_cards = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            extra_resources += self.cards_in_play[planet_id + 1][i].get_additional_resources_command_struggle()
            extra_cards += self.cards_in_play[planet_id + 1][i].get_additional_cards_command_struggle()
        return extra_resources, extra_cards

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

    def get_ignores_flying_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ignores_flying()

    def get_ability_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ability()

    def get_ready_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ready()

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

    def search_hand_for_discounts(self, faction_of_card):
        discounts_available = 0
        for i in range(len(self.cards)):
            if self.cards[i] == "Bigga Is Betta":
                if faction_of_card == "Orks":
                    discounts_available += 2
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

    def perform_discount_at_pos_hand(self, pos, faction_of_card):
        discount = 0
        damage = 0
        if self.cards[pos] == "Bigga Is Betta":
            if faction_of_card == "Orks":
                discount += 2
                damage += 1
        return discount, damage

    def exhaust_given_pos(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].exhaust_card()

    def get_attack_given_pos(self, planet_id, unit_id):
        card = self.cards_in_play[planet_id + 1][unit_id]
        attack_value = card.get_attack()
        if card.get_ability() != "Nazdreg":
            nazdreg_check = self.search_card_at_planet(planet_id, "Nazdreg", bloodied_relevant=True)
            if nazdreg_check:
                card.set_brutal(True)
        if card.get_ability() != "Colonel Straken":
            straken_check = self.search_card_at_planet(planet_id, "Colonel Straken", bloodied_relevant=True)
            if straken_check:
                if card.check_for_a_trait("Soldier") or card.check_for_a_trait("Warrior"):
                    attack_value += 1
        if card.get_ability() == "Goff Boyz":
            if self.game.round_number == planet_id:
                attack_value = attack_value + 3
        if card.get_brutal():
            attack_value = attack_value + card.get_damage()
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
        card.reset_brutal()
        attack_value += card.get_extra_attack_until_end_of_battle()
        return attack_value

    def count_copies_in_play(self, card_name):
        num_copies = 0
        for i in range(7):
            num_copies += self.count_copies_at_planet(planet_num=i, card_name=card_name)
        num_copies += self.count_copies_at_hq(card_name)
        return num_copies

    def count_copies_at_planet(self, planet_num, card_name):
        num_copies = 0
        for i in range(len(self.cards_in_play[planet_num + 1])):
            if self.cards_in_play[planet_num + 1][i].get_name() == card_name:
                num_copies += 1
        return num_copies

    def count_copies_at_hq(self, card_name):
        num_copies = 0
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_name() == card_name:
                num_copies += 1
        return num_copies

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

    def sacrifice_card_in_hq(self, card_pos):
        if self.headquarters[card_pos].get_card_type() == "Warlord":
            return False
        self.add_card_in_hq_to_discard(card_pos)
        return True

    def sacrifice_card_in_play(self, planet_num, card_pos):
        if self.cards_in_play[planet_num + 1][card_pos].get_card_type() == "Warlord":
            return False
        self.add_card_in_play_to_discard(planet_num, card_pos)
        return True

    def destroy_card_in_hq(self, card_pos):
        if self.headquarters[card_pos].get_card_type() == "Warlord":
            if not self.headquarters[card_pos].get_bloodied():
                self.headquarters[card_pos].bloody_warlord()
            else:
                self.add_card_in_hq_to_discard(card_pos)
        else:
            if self.headquarters[card_pos].get_ability() == "Carnivore Pack":
                self.add_resources(3)
            self.add_card_in_hq_to_discard(card_pos)

    def destroy_all_cards_in_hq(self, ignore_uniques=True, units_only=True):
        i = 0
        while i < len(self.headquarters):
            card_type = self.headquarters[i].get_card_type()
            if ignore_uniques and units_only:
                if not self.headquarters[i].get_unique() and (card_type == "Army" or card_type == "Token"):
                    self.destroy_card_in_hq(i)
                    i = i - 1
                i = i + 1
            elif ignore_uniques and not units_only:
                if not self.headquarters[i].get_unique():
                    self.destroy_card_in_hq(i)
                    i = i - 1
                i = i + 1
            elif not ignore_uniques and units_only:
                if card_type == "Army" or card_type == "Token":
                    self.destroy_card_in_hq(i)
                    i = i - 1
                i = i + 1
            else:
                self.destroy_card_in_hq(i)

    def destroy_card_in_play(self, planet_num, card_pos):
        if self.cards_in_play[planet_num + 1][card_pos].get_card_type() == "Warlord":
            if not self.cards_in_play[planet_num + 1][card_pos].get_bloodied():
                self.bloody_warlord_given_pos(planet_num, card_pos)
                self.warlord_just_got_bloodied = True
            else:
                if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Carnivore Pack":
                    self.add_resources(3)
                self.add_card_in_play_to_discard(planet_num, card_pos)
        else:
            cato_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_num,
                                                                           "Captain Cato Sicarius",
                                                                           bloodied_relevant=True)
            if cato_check:
                self.game.add_resources_to_opponent(self.number, 1)
                self.game.resources_need_sending_outside_normal_sends = True
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Straken's Command Squad":
                self.summon_token_at_planet("Guardsman", planet_num)
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

    def remove_card_from_hq(self, card_pos):
        del self.headquarters[card_pos]

    def add_card_in_play_to_discard(self, planet_num, card_pos):
        card = self.cards_in_play[planet_num + 1][card_pos]
        card_name = card.get_name()
        for i in range(len(card.get_attachments())):
            if card.get_attachments()[i].get_ability() == "Straken's Cunning":
                self.draw_card()
                self.draw_card()
                self.draw_card()
                self.game.cards_need_sending_outside_normal_sends = True
        self.discard.append(card_name)
        self.remove_card_from_play(planet_num, card_pos)

    def add_card_in_hq_to_discard(self, card_pos):
        card_name = self.headquarters[card_pos].get_name()
        card = self.headquarters[card_pos]
        card_name = card.get_name()
        for i in range(len(card.get_attachments())):
            if card.get_attachments()[i].get_ability() == "Straken's Cunning":
                self.draw_card()
                self.draw_card()
                self.draw_card()
                self.game.cards_need_sending_outside_normal_sends = True
        self.discard.append(card_name)
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
