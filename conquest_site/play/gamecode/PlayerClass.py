from . import FindCard
from random import shuffle
import copy


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
        self.number = number
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

    async def setup_player(self, raw_deck, planet_array):
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

    async def send_hand(self):
        if self.cards:
            card_string = "/".join(self.cards)
            card_string = "GAME_INFO/HAND/" + str(self.number) + "/" + self.name_player + "/" + card_string
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
                single_card_string += str(0)
                single_card_string += "|"
                if current_card.get_card_type() == "Warlord":
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
                single_card_string += str(0)
                single_card_string += "|"
                if current_card.get_card_type() == "Warlord":
                    if current_card.get_bloodied():
                        single_card_string += "B|"
                    else:
                        single_card_string += "H|"
                card_strings.append(single_card_string)
            joined_string = "/".join(card_strings)
            joined_string = "GAME_INFO/IN_PLAY/" + str(self.number) + "/" + str(planet_id) + "/" + joined_string
            print(joined_string)
            await self.game.game_sockets[0].receive_game_update(joined_string)
        else:
            print("Empty")

    async def send_units_at_all_planets(self):
        for i in range(7):
            await self.send_units_at_planet(i)

    async def send_resources(self):
        joined_string = "GAME_INFO/RESOURCES/" + str(self.number) + "/" + str(self.resources)
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
            return "NONE"
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
            self.resources = self.resources - amount
            return True

    def add_resources(self, amount):
        self.resources += amount

    def check_if_warlord(self, planet_id, unit_id):
        if self.cards_in_play[planet_id + 1][unit_id].get_card_type() == "Warlord":
            return True
        return False

    def discard_card_from_hand(self, card_pos):
        self.discard.append(self.cards[card_pos])
        del self.cards[card_pos]

    def get_shields_given_pos(self, pos_in_hand):
        shield_card_name = self.cards[pos_in_hand]
        card_object = FindCard.find_card(shield_card_name, self.card_array)
        return card_object.get_shields()

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

    def play_card_if_support(self, position_hand):
        card = FindCard.find_card(self.cards[position_hand], self.card_array)
        if card.card_type == "Support":
            print("Need to play support card")
            played_card = self.play_card(-2, card=card)
            return "SUCCESS/Support"
        return "SUCCESS/Not Support"

    def add_card_to_planet(self, card, position):
        self.cards_in_play[position + 1].append(copy.deepcopy(card))

    def play_card(self, position, card=None, position_hand=None):
        if card is None and position_hand is None:
            return "ERROR/play_card function called incorrectly"
        if card is not None and position_hand is not None:
            return "ERROR/play_card function called incorrectly"
        if card is not None:
            if position == -2:
                print("Play card to HQ")
                if self.spend_resources(card.get_cost()):
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
                    if self.spend_resources(card.get_cost()):
                        self.add_card_to_planet(card, position)
                        self.cards.remove(card.get_name())
                        print("Played card to planet", position)
                        return "SUCCESS"
                    print("Insufficient resources")
                    return "FAIL/Insufficient resources"
        return "FAIL/Invalid card"

    def commit_warlord_to_planet(self, planet_pos=None):
        headquarters_list = self.get_headquarters()
        if planet_pos is None:
            planet_pos = self.warlord_commit_location + 1
        for i in range(len(headquarters_list)):
            if headquarters_list[i].get_card_type() == "Warlord":
                print(headquarters_list[i].get_name())
                self.cards_in_play[planet_pos].append(copy.deepcopy(headquarters_list[i]))
                self.headquarters.remove(headquarters_list[i])
                return True

    def count_command_at_planet(self, planet_id):
        counted_command = 0
        for i in range(len(self.cards_in_play[planet_id + 1])):
            counted_command += self.cards_in_play[planet_id + 1][i].get_command()
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

    def check_if_units_present(self, planet_id):
        print("Checking for cards at:", self.cards_in_play[0][planet_id])
        if not self.cards_in_play[planet_id + 1]:
            print("No cards present.")
            return 0
        print("Cards present.")
        return 1

    def get_cards_in_play(self):
        return self.cards_in_play

    def assign_damage_to_pos(self, planet_id, unit_id, damage, can_shield=True):
        damage_too_great = self.cards_in_play[planet_id + 1][unit_id].damage_card(self, damage, can_shield)
        return damage_too_great

    def get_attack_given_pos(self, planet_id, unit_id):
        attack_value = self.cards_in_play[planet_id + 1][unit_id].get_attack()
        # if self.search_card_at_planet("Nazdreg", planet_id) != -1:
        #     if self.cards_in_play[planet_id + 1][unit_id].get_name() != "Nazdreg":
        #         self.cards_in_play[planet_id + 1][unit_id].set_brutal(True)
        # if self.cards_in_play[planet_id + 1][unit_id].get_name() == "Goff Boyz":
        #     attack_value = attack_value + 3
        if self.cards_in_play[planet_id + 1][unit_id].get_brutal():
            attack_value = attack_value + self.cards_in_play[planet_id + 1][unit_id].get_damage()
        self.cards_in_play[planet_id + 1][unit_id].reset_brutal()
        attack_value += self.cards_in_play[planet_id + 1][unit_id].get_extra_attack_until_end_of_battle()
        return attack_value



    def exhaust_given_pos(self, planet_id, unit_id):
        self.cards_in_play[planet_id + 1][unit_id].exhaust_card()

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

    def retreat_all_at_planet(self, planet_id):
        while self.cards_in_play[planet_id + 1]:
            self.retreat_unit(planet_id, 0)
        self.print_cards_at_planet(planet_id + 1)

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

    def remove_card_from_play(self, planet_num, card_pos):
        # card_object = self.cards_in_play[planet_num + 1][card_pos]
        # self.discard_object(card_object)
        del self.cards_in_play[planet_num + 1][card_pos]

    def add_card_in_play_to_discard(self, planet_num, card_pos):
        card_name = self.cards_in_play[planet_num + 1][card_pos].get_name()
        self.discard.append(card_name)
        self.remove_card_from_play(planet_num, card_pos)

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
