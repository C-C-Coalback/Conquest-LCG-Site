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
        self.aiming_reticle_color = "blue"
        self.aiming_reticle_coords_hand = None
        self.aiming_reticle_coords_hand_2 = None
        self.can_play_limited = True
        self.number_cards_to_search = 0
        self.mobile_resolved = True
        self.indirect_damage_applied = 0
        self.total_indirect_damage = 0
        self.cards_recently_discarded = []
        self.stored_cards_recently_discarded = []
        self.cards_recently_destroyed = []
        self.stored_cards_recently_destroyed = []
        self.num_nullify_played = 0

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
                    if self.aiming_reticle_coords_hand == i or self.aiming_reticle_coords_hand_2 == i:
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
                    print("Adding attachments")
                    print(attachments_list[a].get_name())
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
            print(joined_string)
            await self.game.game_sockets[0].receive_game_update(joined_string)
        else:
            joined_string = "GAME_INFO/HQ/" + str(self.number)
            await self.game.game_sockets[0].receive_game_update(joined_string)

    async def send_units_at_planet(self, planet_id):
        if planet_id != -1:
            if planet_id == -2:
                await self.send_hq()
            else:
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
                            print("Adding attachments")
                            print(attachments_list[a].get_name())
                            single_card_string += "|"
                            single_card_string += attachments_list[a].get_name()
                            single_card_string += "+"
                            if attachments_list[a].get_ready():
                                single_card_string += "R"
                            else:
                                single_card_string += "E"
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
                await self.send_hq()
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
                    await self.send_units_at_planet(i)

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

    def exhaust_card_in_hq_given_name(self, card_name):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_name() == card_name and self.headquarters[i].get_ready():
                self.exhaust_given_pos(-2, i)
                return True
        return False

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
            await self.game.game_sockets[0].receive_game_update("No cards left!")
        else:
            card_name = self.deck[0]
            text = self.name_player + " reveals a " + card_name
            await self.game.game_sockets[0].receive_game_update(text)

    def get_top_card_deck(self):
        if not self.deck:
            print("Deck is empty, you lose!")
            return None
        else:
            card = FindCard.find_card(self.deck[0], self.card_array)
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

    def add_resources(self, amount):
        self.resources += amount

    def check_if_warlord(self, planet_id, unit_id):
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Warlord":
            return True
        return False

    def set_aiming_reticle_in_play(self, planet_id, unit_id, color):
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

    def get_shields_given_pos(self, pos_in_hand, planet_pos=None):
        shield_card_name = self.cards[pos_in_hand]
        card_object = FindCard.find_card(shield_card_name, self.card_array)
        shields = card_object.get_shields()
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

    def get_ranged_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ranged()

    def check_for_trait_given_pos(self, planet_id, unit_id, trait):
        return self.cards_in_play[planet_id + 1][unit_id].check_for_a_trait(trait)

    def bloody_warlord_given_pos(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].bloody_warlord()
        self.retreat_warlord()

    def shuffle_deck(self):
        shuffle(self.deck)

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
        return False

    def add_to_hq(self, card_object):
        if card_object.get_unique():
            if self.search_for_unique_card(card_object.name):
                return False
        self.headquarters.append(copy.deepcopy(card_object))
        last_element_index = len(self.headquarters) - 1
        if self.headquarters[last_element_index].get_ability() == "Promethium Mine":
            self.headquarters[last_element_index].set_counter(4)
        elif self.headquarters[last_element_index].get_ability() == "Swordwind Farseer":
            self.game.reactions_needing_resolving.append("Swordwind Farseer")
            self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
            self.game.player_who_resolves_reaction.append(self.name_player)
        elif self.headquarters[last_element_index].get_ability() == "Coliseum Fighters":
            i = len(self.discard) - 1
            while i > -1:
                card = FindCard.find_card(self.discard[i], self.card_array)
                if card.get_card_type() == "Event":
                    self.cards.append(card.get_name())
                    del self.discard[i]
                    return None
                i = i - 1
        elif self.headquarters[last_element_index].get_ability() == "Earth Caste Technician":
            self.game.reactions_needing_resolving.append("Earth Caste Technician")
            self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
            self.game.player_who_resolves_reaction.append(self.name_player)
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

    def get_card_in_discard(self, position_discard):
        card = FindCard.find_card(self.discard[position_discard], self.card_array)
        return card

    def get_discard(self):
        return self.discard

    def move_attachment_card(self, origin_planet, origin_position, origin_attachment_position,
                             destination_planet, destination_position):
        if origin_planet == -2:
            target_attachment = self.headquarters[origin_position].get_attachments()[origin_attachment_position]
        else:
            target_attachment = self.cards_in_play[origin_planet + 1][origin_position].\
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
                            army_unit_as_attachment=army_unit_as_attachment):
            self.remove_attachment_from_pos(origin_planet, origin_position, origin_attachment_position)
            return True
        return False

    def destroy_attachment_from_pos(self, planet, position, attachment_position):
        self.remove_attachment_from_pos(planet, position, attachment_position, discard=True)

    def remove_attachment_from_pos(self, planet, position, attachment_position, discard=False):
        if planet == -2:
            card = self.headquarters[position]
            if discard:
                self.discard.append(card.get_name())
            del card.get_attachments()[attachment_position]
        else:
            card = self.cards_in_play[planet + 1][position]
            if discard:
                self.discard.append(card.get_name())
            del card.get_attachments()[attachment_position]

    def attach_card(self, card, planet, position, army_unit_as_attachment=False):
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
            target_card.add_attachment(card)
            return True
        allowed_types = card.type_of_units_allowed_for_attachment
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

    def play_attachment_card_to_in_play(self, card, planet, position, discounts=0, not_own_attachment=False,
                                        army_unit_as_attachment=False):
        if card.get_unique():
            if self.search_for_unique_card(card.name):
                return False
        if army_unit_as_attachment:
            if not_own_attachment:
                if self.attach_card(card, planet, position, army_unit_as_attachment=army_unit_as_attachment):
                    return True
                return False
            cost = card.get_cost() - discounts
            if self.spend_resources(cost):
                if self.attach_card(card, planet, position, army_unit_as_attachment=army_unit_as_attachment):
                    return True
                self.add_resources(cost)
        else:
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

    def add_card_to_planet(self, card, position, sacrifice_end_of_phase=False):
        if card.get_unique():
            if self.search_for_unique_card(card.name):
                return -1
        self.cards_in_play[position + 1].append(copy.deepcopy(card))
        last_element_index = len(self.cards_in_play[position + 1]) - 1
        if sacrifice_end_of_phase:
            self.cards_in_play[position + 1][last_element_index].set_sacrifice_end_of_phase(True)
        if self.cards_in_play[position + 1][last_element_index].get_ability() == "Swordwind Farseer":
            if len(self.deck) > 5:
                self.number_cards_to_search = 6
                self.game.cards_in_search_box = self.deck[0:self.number_cards_to_search]
                self.game.name_player_who_is_searching = self.name_player
                self.game.number_who_is_searching = str(self.number)
                self.game.what_to_do_with_searched_card = "DRAW"
                self.game.traits_of_searched_card = None
                self.game.card_type_of_searched_card = None
                self.game.faction_of_searched_card = None
                self.game.no_restrictions_on_chosen_card = True
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Coliseum Fighters":
            i = len(self.discard) - 1
            while i > -1:
                card = FindCard.find_card(self.discard[i], self.card_array)
                if card.get_card_type() == "Event":
                    self.cards.append(card.get_name())
                    del self.discard[i]
                    return None
                i = i - 1
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Sicarius's Chosen":
            self.game.reactions_needing_resolving.append("Sicarius's Chosen")
            self.game.positions_of_unit_triggering_reaction.append([int(self.number), position, last_element_index])
            self.game.player_who_resolves_reaction.append(self.name_player)
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Weirdboy Maniak":
            no_units_damaged = True
            for i in range(len(self.cards_in_play[position + 1]) - 1):
                if no_units_damaged:
                    self.set_aiming_reticle_in_play(position, i, "red")
                    no_units_damaged = False
                else:
                    self.set_aiming_reticle_in_play(position, i, "blue")
                self.assign_damage_to_pos(position, i, 1)
            if int(self.number) == 1:
                for i in range(len(self.game.p2.cards_in_play[position + 1])):
                    if no_units_damaged:
                        self.game.p2.set_aiming_reticle_in_play(position, i, "red")
                        no_units_damaged = False
                    else:
                        self.game.p2.set_aiming_reticle_in_play(position, i, "blue")
                    self.game.p2.assign_damage_to_pos(position, i, 1)
            else:
                for i in range(len(self.game.p1.cards_in_play[position + 1])):
                    if no_units_damaged:
                        self.game.p1.set_aiming_reticle_in_play(position, i, "red")
                        no_units_damaged = False
                    else:
                        self.game.p1.set_aiming_reticle_in_play(position, i, "blue")
                    self.game.p1.assign_damage_to_pos(position, i, 1)
        elif self.cards_in_play[position + 1][last_element_index].get_ability() == "Earth Caste Technician":
            if len(self.deck) > 5:
                self.number_cards_to_search = 6
                self.game.cards_in_search_box = self.deck[0:self.number_cards_to_search]
                self.game.name_player_who_is_searching = self.name_player
                self.game.number_who_is_searching = str(self.number)
                self.game.what_to_do_with_searched_card = "DRAW"
                self.game.traits_of_searched_card = "Drone"
                self.game.card_type_of_searched_card = "Attachment"
                self.game.faction_of_searched_card = None
                self.game.no_restrictions_on_chosen_card = False
        return last_element_index

    async def dark_eldar_event_played(self):
        self.reset_reaction_beasthunter_wyches()
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_ability() == "Beasthunter Wyches":
                self.game.reactions_needing_resolving.append("Beasthunter Wyches")
                self.game.positions_of_unit_triggering_reaction.append([int(self.number), -2, i])
                self.player_who_resolves_reaction.append(self.name_player)
            for attach in self.headquarters[i].get_attachments():
                found_any = False
                if attach.get_ability() == "Hypex Injector":
                    self.ready_given_pos(-2, i)
                    found_any = True
                if found_any:
                    await self.send_hq()
        for i in range(7):
            for j in range(len(self.cards_in_play[i + 1])):
                if self.cards_in_play[i + 1][j].get_ability() == "Beasthunter Wyches":
                    self.game.reactions_needing_resolving.append("Beasthunter Wyches")
                    self.game.positions_of_unit_triggering_reaction.append([int(self.number), i, j])
                    self.game.player_who_resolves_reaction.append(self.name_player)
                for attach in self.cards_in_play[i + 1][j].get_attachments():
                    found_any = False
                    if attach.get_ability() == "Hypex Injector":
                        self.ready_given_pos(i, j)
                        found_any = True
                    if found_any:
                        await self.send_units_at_planet(i)

    def put_card_in_hand_into_hq(self, hand_pos, unit_only=True):
        card = copy.deepcopy(FindCard.find_card(self.cards[hand_pos], self.card_array))
        if unit_only:
            if card.get_card_type() != "Army":
                return False
        self.headquarters.append(card)
        del self.cards[hand_pos]
        return True

    def play_card(self, position, card=None, position_hand=None, discounts=0, damage_to_take=0):
        damage_on_play = damage_to_take
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
                            if self.add_to_hq(card):
                                self.cards.remove(card.get_name())
                                self.set_can_play_limited(False)
                                print("Played card to HQ")
                                return "SUCCESS", -1
                            self.add_resources(cost)
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
                        self.add_resources(cost)
                        return "Fail/Unique already in play", -1
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
                                if self.add_card_to_planet(card, position) != -1:
                                    self.cards.remove(card.get_name())
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
                                self.add_resources(cost)
                                return "FAIL/Unique already in play", -1
                        else:
                            return "FAIL/Limited already played", -1
                    else:
                        if self.spend_resources(cost):
                            if self.add_card_to_planet(card, position) != -1:
                                self.cards.remove(card.get_name())
                                print("Played card to planet", position)
                                print(card.get_ability())
                                location_of_unit = len(self.cards_in_play[position + 1]) - 1
                                if damage_to_take > 0:
                                    if self.game.bigga_is_betta_active:
                                        while damage_on_play > 0:
                                            self.assign_damage_to_pos(position, location_of_unit, 1)
                                            damage_on_play -= 1
                                    else:
                                        self.assign_damage_to_pos(position, location_of_unit, damage_to_take)
                                if card.get_ability() == "Murder of Razorwings":
                                    self.game.discard_card_at_random_from_opponent(self.number)
                                if card.get_ability() == "Kith's Khymeramasters":
                                    self.summon_token_at_planet("Khymera", position)
                                return "SUCCESS", location_of_unit
                            self.add_resources(cost)
                            return "FAIL/Unique already in play", -1
                    print("Insufficient resources")
                    return "FAIL/Insufficient resources", -1
        return "FAIL/Invalid card", -1

    def return_card_to_hand(self, planet_pos, unit_pos):
        if planet_pos == -2:
            self.cards.append(self.headquarters[unit_pos].get_name())
            self.remove_card_from_hq(unit_pos)
            return None
        self.cards.append(self.cards_in_play[planet_pos + 1][unit_pos].get_name())
        self.remove_card_from_play(planet_pos, unit_pos)
        return None

    def discard_card_at_random(self):
        print("")
        if self.cards:
            pos = random.randint(1, len(self.cards) - 1)
            print(pos)
            self.discard_card_from_hand(pos)

    def move_unit_to_planet(self, origin_planet, origin_position, destination):
        if origin_planet == -2:
            headquarters_list = self.headquarters
            self.cards_in_play[destination + 1].append(copy.deepcopy(headquarters_list[origin_position]))
            new_pos = len(self.cards_in_play[destination + 1]) - 1
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
            self.cards_in_play[destination + 1].append(copy.deepcopy(self.cards_in_play[origin_planet + 1]
                                                                     [origin_position]))
            self.remove_card_from_play(origin_planet, origin_position)

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
                if self.cards_in_play[origin_planet + 1][i].get_ability() == "Eldorath Starbane":
                    self.game.reactions_needing_resolving.append("Eldorath Starbane")
                    self.game.positions_of_unit_triggering_reaction.append([int(self.number), dest_planet, -1])
                    self.game.player_who_resolves_reaction.append(self.name_player)
                self.move_unit_to_planet(origin_planet, i, dest_planet)
                if summon_khymera:
                    self.summon_token_at_planet("Khymera", dest_planet)
            i += 1

    def commit_warlord_to_planet(self, planet_pos=None, only_warlord=False):
        headquarters_list = self.get_headquarters()
        if planet_pos is None:
            planet_pos = self.warlord_commit_location + 1
        if only_warlord:
            for i in range(len(headquarters_list)):
                if headquarters_list[i].get_card_type() == "Warlord":
                    print(headquarters_list[i].get_name())
                    summon_khymera = False
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Packmaster Kith":
                        summon_khymera = True
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Eldorath Starbane":
                        self.game.reactions_needing_resolving.append("Eldorath Starbane")
                        self.game.positions_of_unit_triggering_reaction.append([int(self.number), planet_pos - 1, -1])
                        self.game.player_who_resolves_reaction.append(self.name_player)
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Commander Shadowsun":
                        self.game.reactions_needing_resolving.append("Commander Shadowsun")
                        self.game.positions_of_unit_triggering_reaction.append([int(self.number), planet_pos - 1, -1])
                        self.game.player_who_resolves_reaction.append(self.name_player)
                    self.move_unit_to_planet(-2, i, planet_pos - 1)
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
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Packmaster Kith":
                        summon_khymera = True
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Eldorath Starbane":
                        self.game.reactions_needing_resolving.append("Eldorath Starbane")
                        self.game.positions_of_unit_triggering_reaction.append([int(self.number), planet_pos - 1, -1])
                        self.game.player_who_resolves_reaction.append(self.name_player)
                    if headquarters_list[i].get_ability(bloodied_relevant=True) == "Commander Shadowsun":
                        self.game.reactions_needing_resolving.append("Commander Shadowsun")
                        self.game.positions_of_unit_triggering_reaction.append([int(self.number), planet_pos - 1, -1])
                        self.game.player_who_resolves_reaction.append(self.name_player)
                    self.move_unit_to_planet(-2, i, planet_pos - 1)
                    if summon_khymera:
                        self.summon_token_at_planet("Khymera", planet_pos - 1)
                    i -= 1
                i += 1
        return None

    def count_command_at_planet(self, planet_id):
        counted_command = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            if self.get_ready_given_pos(planet_id, i):
                counted_command += self.cards_in_play[planet_id + 1][i].get_command()
                if self.cards_in_play[planet_id + 1][i].get_ability() == "Iron Hands Techmarine":
                    counted_command += self.game.request_number_of_enemy_units_at_planet(self.number, planet_id)
        return counted_command

    def count_units_in_play_all(self):
        unit_count = 0
        for i in range(7):
            unit_count += len(self.cards_in_play[i])
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

    def get_armorbane_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_armorbane()

    def get_ignores_flying_given_pos(self, planet_id, unit_id):
        return self.cards_in_play[planet_id + 1][unit_id].get_ignores_flying()

    def get_faction_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_faction()
        return self.cards_in_play[planet_id + 1][unit_id].get_faction()

    def get_ability_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ability()
        return self.cards_in_play[planet_id + 1][unit_id].get_ability()

    def get_ready_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            return self.headquarters[unit_id].get_ready()
        return self.cards_in_play[planet_id + 1][unit_id].get_ready()

    def get_ambush_of_card(self, card):
        return card.get_ambush()

    def get_mobile_given_pos(self, planet_id, unit_id):
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

    def get_immune_to_enemy_card_abilities(self, planet_pos, unit_pos):
        if not self.cards_in_play[planet_pos + 1][unit_pos].check_for_a_trait("Vehicle"):
            for i in range(len(self.cards_in_play[planet_pos + 1])):
                if self.get_ability_given_pos(planet_pos, i) == "Land Raider":
                    return True
        return False

    def get_immune_to_enemy_events(self, planet_pos, unit_pos):
        if planet_pos == -2:
            if self.headquarters[unit_pos].get_ability() == "Stalwart Ogryn":
                return True
            return False
        if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Stalwart Ogryn":
            return True
        return False

    def search_card_in_hq(self, name_of_card, bloodied_relevant=False, ability_checking=True, ready_relevant=False):
        for i in range(len(self.headquarters)):
            current_name = self.headquarters[i].get_ability()
            print(current_name, name_of_card)
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

    def search_hq_for_discounts(self, faction_of_card, traits, is_attachment=False):
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
                            discounts_available += self.headquarters[i].get_discount_amount()
            if "Daemon" in traits:
                if self.headquarters[i].get_ability() == "Cultist":
                    discounts_available += 1
                elif self.headquarters[i].get_ability() == "Splintered Path Acolyte":
                    discounts_available += 2

        return discounts_available

    def search_planet_for_discounts(self, planet_pos, traits):
        discounts_available = 0
        for i in range(len(self.cards_in_play[planet_pos + 1])):
            if "Daemon" in traits:
                if self.cards_in_play[planet_pos + 1][i].get_ability() == "Cultist":
                    discounts_available += 1
                elif self.cards_in_play[planet_pos + 1][i].get_ability() == "Splintered Path Acolyte":
                    discounts_available += 2
        return discounts_available

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
        num_nullifies = 0
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

    def search_hand_for_card(self, card_name):
        print("Looking for", card_name)
        for i in range(len(self.cards)):
            print(self.cards[i])
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

    def search_attachments_at_pos(self, planet_pos, unit_pos, card_abil):
        for i in range(len(self.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
            if self.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[i].get_ability() == card_abil:
                return True
        return False

    def perform_discount_at_pos_hq(self, pos, faction_of_card, traits):
        discount = 0
        if self.headquarters[pos].get_applies_discounts():
            if self.headquarters[pos].get_is_faction_limited_unique_discounter():
                if self.headquarters[pos].get_faction() == faction_of_card:
                    if self.headquarters[pos].get_ready():
                        self.headquarters[pos].exhaust_card()
                        discount += self.headquarters[pos].get_discount_amount()
        if "Daemon" in traits:
            if self.headquarters[pos].get_ability() == "Cultist":
                discount += 1
                self.sacrifice_card_in_hq(pos)
            elif self.headquarters[pos].get_ability() == "Splintered Path Acolyte":
                discount += 2
                self.sacrifice_card_in_hq(pos)
        return discount

    def check_is_unit_at_pos(self, planet_pos, unit_pos):
        if planet_pos == -2:
            if self.headquarters[unit_pos].get_is_unit():
                return True
            return False
        if self.cards_in_play[planet_pos + 1][unit_pos].get_is_unit():
            return True
        return False

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

    def reset_extra_abilities_eop(self):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_is_unit():
                self.headquarters[i].reset_ranged()
        for planet_pos in range(7):
            for unit_pos in range(len(self.cards_in_play[planet_pos + 1])):
                self.cards_in_play[planet_pos + 1][unit_pos].reset_ranged()

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
        if "Daemon" in traits:
            if self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Cultist":
                discount += 1
                self.sacrifice_card_in_play(planet_pos, unit_pos)
            elif self.cards_in_play[planet_pos + 1][unit_pos].get_ability() == "Splintered Path Acolyte":
                discount += 2
                self.sacrifice_card_in_play(planet_pos, unit_pos)
        return discount

    def exhaust_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            previous_state = self.headquarters[unit_id].get_ready()
            self.headquarters[unit_id].exhaust_card()
            new_state = self.headquarters[unit_id].get_ready()
            if previous_state and not new_state:
                for i in range(len(self.headquarters[unit_id].get_attachments())):
                    if self.headquarters[unit_id].get_attachments()[i].get_ability() == "Dire Mutation":
                        self.assign_damage_to_pos(-2, unit_id, 1)
            return None
        previous_state = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        self.cards_in_play[planet_id + 1][unit_id].exhaust_card()
        new_state = self.cards_in_play[planet_id + 1][unit_id].get_ready()
        if previous_state and not new_state:
            for i in range(len(self.cards_in_play[planet_id + 1][unit_id].get_attachments())):
                if self.cards_in_play[planet_id + 1][unit_id].get_attachments()[i].get_ability() == "Dire Mutation":
                    self.assign_damage_to_pos(planet_id, unit_id, 1)
        return None

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
        card.reset_brutal()
        attack_value += card.get_extra_attack_until_end_of_battle()
        attack_value += card.get_extra_attack_until_next_attack()
        attack_value += card.get_extra_attack_until_end_of_phase()
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

    def count_units_in_discard(self):
        count = 0
        for i in range(len(self.discard)):
            card = FindCard.find_card(self.discard[i], self.card_array)
            if card.get_card_type() == "Army":
                count = count + 1
        return count

    def count_copies_at_hq(self, card_name):
        num_copies = 0
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_name() == card_name:
                num_copies += 1
        return num_copies

    def assign_damage_to_pos(self, planet_id, unit_id, damage, can_shield=True, att_pos=None):
        if planet_id == -2:
            return self.assign_damage_to_pos_hq(unit_id, damage, can_shield)
        prior_damage = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        self.game.damage_on_units_list_before_new_damage.append(prior_damage)
        zara_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_id,
                                                                       "Zarathur, High Sorcerer",
                                                                       bloodied_relevant=True)
        if zara_check:
            damage += 1
        bodyguard_damage_list = []
        if att_pos is not None:
            for i in range(len(self.cards_in_play[planet_id + 1])):
                if i != unit_id:
                    if self.search_attachments_at_pos(planet_id, i, "Bodyguard"):
                        if damage > 0:
                            damage = damage - 1
                            bodyguard_damage_list.append(i)
        damage_on_card_before = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        damage_too_great = self.cards_in_play[planet_id + 1][unit_id].damage_card(self, damage, can_shield)
        damage_on_card_after = self.cards_in_play[planet_id + 1][unit_id].get_damage()
        total_damage_that_can_be_blocked = damage_on_card_after - prior_damage
        for i in range(len(bodyguard_damage_list)):
            self.assign_damage_to_pos(planet_id, bodyguard_damage_list[i], 1)
        if damage_on_card_after > damage_on_card_before:
            self.game.positions_of_units_to_take_damage.append((int(self.number), planet_id, unit_id))
            self.game.damage_can_be_shielded.append(can_shield)
            self.game.positions_attackers_of_units_to_take_damage.append(att_pos)
            self.game.amount_that_can_be_removed_by_shield.append(total_damage_that_can_be_blocked)
        return damage_too_great

    def increase_indirect_damage_at_pos(self, planet_pos, card_pos, amount):
        if planet_pos == -2:
            if self.headquarters[card_pos].get_is_unit():
                self.headquarters[card_pos].increase_not_yet_assigned_damage(amount)
                self.indirect_damage_applied += 1
                return True
            return False
        if self.cards_in_play[planet_pos + 1][card_pos].get_is_unit():
            self.cards_in_play[planet_pos + 1][card_pos].increase_not_yet_assigned_damage(amount)
            self.indirect_damage_applied += 1
            return True
        return False

    def assign_damage_to_pos_hq(self, unit_id, damage, can_shield=True):
        prior_damage = self.headquarters[unit_id].get_damage()
        self.game.damage_on_units_list_before_new_damage.append(prior_damage)
        damage_too_great = self.headquarters[unit_id].damage_card(self, damage, can_shield)
        afterwards_damage = self.headquarters[unit_id].get_damage()
        total_that_can_be_blocked = afterwards_damage - prior_damage
        self.game.positions_of_units_to_take_damage.append((int(self.number), -2, unit_id))
        self.game.damage_can_be_shielded.append(can_shield)
        self.game.positions_attackers_of_units_to_take_damage.append(None)
        self.game.amount_that_can_be_removed_by_shield.append()
        return damage_too_great

    def suffer_area_effect(self, planet_id, amount):
        for i in range(len(self.cards_in_play[planet_id + 1])):
            self.assign_damage_to_pos(planet_id, i, amount)

    def suffer_area_effect_at_hq(self, amount):
        for i in range(len(self.headquarters)):
            if self.headquarters[i].get_card_type() != "Support":
                self.assign_damage_to_pos_hq(i, amount)

    def get_number_of_units_at_planet(self, planet_id):
        return len(self.cards_in_play[planet_id + 1])

    def check_if_card_is_destroyed(self, planet_id, unit_id):
        if planet_id == -2:
            if self.headquarters[unit_id].get_card_type() == "Support":
                return False
            return not self.headquarters[unit_id].check_health()
        return not self.cards_in_play[planet_id + 1][unit_id].check_health()

    def remove_damage_from_pos(self, planet_id, unit_id, amount):
        if planet_id == -2:
            self.headquarters[unit_id].remove_damage(amount)
        else:
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
            if self.headquarters[card_pos].get_ability() == "Shrouded Harlequin":
                self.game.reactions_needing_resolving.append("Shrouded Harlequin")
                self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
                self.game.player_who_resolves_reaction.append(self.name_player)
            self.cards_recently_destroyed.append(self.headquarters[card_pos].get_name())
            self.add_card_in_hq_to_discard(card_pos)

    def destroy_all_cards_in_hq(self, ignore_uniques=True, units_only=True, enemy_event=False):
        i = 0
        while i < len(self.headquarters):
            card_type = self.headquarters[i].get_card_type()
            if ignore_uniques and units_only:
                if not self.headquarters[i].get_unique() and (card_type == "Army" or card_type == "Token"):
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i):
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            elif ignore_uniques and not units_only:
                if not self.headquarters[i].get_unique():
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i):
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            elif not ignore_uniques and units_only:
                if card_type == "Army" or card_type == "Token":
                    if not enemy_event:
                        self.destroy_card_in_hq(i)
                        i = i - 1
                    elif not self.get_immune_to_enemy_events(-2, i):
                        self.destroy_card_in_hq(i)
                        i = i - 1
                i = i + 1
            else:
                if not enemy_event:
                    self.destroy_card_in_hq(i)
                    i = i - 1
                elif not self.get_immune_to_enemy_events(-2, i):
                    self.destroy_card_in_hq(i)
                    i = i - 1
                i = i + 1

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
                self.game.resources_need_sending_outside_normal_sends = True
            xavaes_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_num,
                                                                             "Xavaes Split-Tongue")
            if xavaes_check:
                self.game.summon_enemy_token_at_hq(self.number, "Cultist", 1)
                self.game.hqs_need_sending_outside_normal_sends = True
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Carnivore Pack":
                self.add_resources(3)
            if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Shrouded Harlequin":
                self.game.reactions_needing_resolving.append("Shrouded Harlequin")
                self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
                self.game.player_who_resolves_reaction.append(self.name_player)
            self.cards_recently_destroyed.append(self.cards_in_play[planet_num + 1][card_pos].get_name())
            self.add_card_in_play_to_discard(planet_num, card_pos)

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
        if card.get_card_type() == "Army":
            for i in range(len(self.cards_in_play[planet_num + 1])):
                if self.cards_in_play[planet_num + 1][i].get_ability() == "Cadian Mortar Squad":
                    self.ready_given_pos(planet_num, i)
        for i in range(len(card.get_attachments())):
            if card.get_attachments()[i].get_ability() == "Straken's Cunning":
                self.draw_card()
                self.draw_card()
                self.draw_card()
                self.game.cards_need_sending_outside_normal_sends = True
        if self.cards_in_play[planet_num + 1][card_pos].get_ability() == "Straken's Command Squad":
            self.summon_token_at_planet("Guardsman", planet_num)
        if self.search_attachments_at_pos(planet_num, card_pos, "Mark of Chaos"):
            self.game.reactions_needing_resolving.append("Mark of Chaos")
            self.game.positions_of_unit_triggering_reaction.append([int(self.number), planet_num, card_pos])
            self.game.player_who_resolves_reaction.append(self.name_player)
        if card.check_for_a_trait("Warrior") or card.check_for_a_trait("Soldier"):
            for i in range(len(self.cards)):
                if self.cards[i] == "Elysian Assault Team":
                    already_queued_elysian_assault_team = False
                    for j in range(len(self.game.reactions_needing_resolving)):
                        if self.game.reactions_needing_resolving[j] == "Elysian Assault Team":
                            if self.game.player_who_resolves_reaction[j] == self.name_player:
                                already_queued_elysian_assault_team = True
                    if not already_queued_elysian_assault_team:
                        self.game.reactions_needing_resolving.append("Elysian Assault Team")
                        self.game.positions_of_unit_triggering_reaction.append([int(self.number), planet_num, -1])
                        self.game.player_who_resolves_reaction.append(self.name_player)
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
                            self.game.reactions_needing_resolving.append("Murder Cogitator")
                            self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
                            self.game.player_who_resolves_reaction.append(self.name_player)
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
            self.game.reactions_needing_resolving.append("Enginseer Augur")
            self.game.player_who_resolves_reaction.append(self.name_player)
            self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
        self.discard.append(card_name)
        self.cards_recently_discarded.append(card_name)
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
                                self.game.reactions_needing_resolving.append("Murder Cogitator")
                                self.game.positions_of_unit_triggering_reaction.append([int(self.number), -1, -1])
                                self.game.player_who_resolves_reaction.append(self.name_player)
        if card.get_ability() == "Enginseer Augur":
            self.game.reactions_needing_resolving.append("Enginseer Augur")
            self.game.player_who_resolves_reaction.append(self.name_player)
            self.game.positions_of_unit_triggering_reaction.append(int(self.number), -1, -1)
        self.discard.append(card_name)
        self.cards_recently_discarded.append(card_name)
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

    def move_unit_at_planet_to_hq(self, planet_id, unit_id):
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        del self.cards_in_play[planet_id + 1][unit_id]
        return True

    def rout_unit(self, planet_id, unit_id):
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        last_element_hq = len(self.headquarters) - 1
        self.exhaust_given_pos(-2, last_element_hq)
        del self.cards_in_play[planet_id + 1][unit_id]
        return True

    def retreat_unit(self, planet_id, unit_id, exhaust=False):
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Army":
            own_umbral_check = self.search_card_at_planet(planet_id, "Umbral Preacher")
            enemy_umbral_check = self.game.request_search_for_enemy_card_at_planet(self.number, planet_id,
                                                                                   "Umbral Preacher")
            if own_umbral_check or enemy_umbral_check:
                return False
        self.headquarters.append(copy.deepcopy(self.cards_in_play[planet_id + 1][unit_id]))
        last_element_hq = len(self.headquarters) - 1
        if exhaust:
            self.exhaust_given_pos(-2, last_element_hq)
        del self.cards_in_play[planet_id + 1][unit_id]
        return True

    def ready_all_in_headquarters(self):
        for i in range(len(self.headquarters)):
            self.headquarters[i].ready_card()
            if self.game.phase == "HEADQUARTERS":
                for j in range(len(self.headquarters[i].get_attachments())):
                    self.headquarters[i].get_attachments()[j].ready_card()

    def ready_all_in_play(self):
        for i in range(len(self.cards_in_play[0])):
            self.ready_all_at_planet(i)
        self.ready_all_in_headquarters()

    def ready_all_at_planet(self, planet_id):
        for i in range(len(self.cards_in_play[planet_id + 1])):
            self.ready_given_pos(planet_id, i)
            if self.game.phase == "HEADQUARTERS":
                for j in range(len(self.cards_in_play[planet_id + 1][i].get_attachments())):
                    self.cards_in_play[planet_id + 1][i].get_attachments()[j].ready_card()

    def ready_given_pos(self, planet_id, unit_id):
        if planet_id == -2:
            self.headquarters[unit_id].ready_card()
            return None
        self.cards_in_play[planet_id + 1][unit_id].ready_card()
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
