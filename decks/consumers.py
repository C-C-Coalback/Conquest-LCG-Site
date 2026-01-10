import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .deckscode import Initfunctions, FindCard
import os
import copy

cards_array = Initfunctions.init_player_cards()
blackstone_array = Initfunctions.init_blackstone_player_cards()
card_names = "CARD_NAMES"
card_names_with_bp = "CARD_NAMES"
authorised_blackstone_users = ["Coalback", "alex", "Echo", "i0Predator0i"]
non_signature_rituals = []
cards_dict = {}
blackstone_dict = {}
for key in range(len(blackstone_array)):
    blackstone_dict[blackstone_array[key].name] = blackstone_array[key]
for key in range(len(cards_array)):
    cards_dict[cards_array[key].name] = cards_array[key]
    card_names_with_bp += "/" + cards_array[key].name
    if cards_array[key].check_for_a_trait("Ritual") and cards_array[key].get_loyalty() != "Signature":
        non_signature_rituals.append(cards_array[key].name)
    if cards_array[key].name not in blackstone_dict:
        card_names += "/" + cards_array[key].name
planet_cards_array = Initfunctions.init_planet_cards()


def clean_sent_deck(deck_message):
    print("Code to test if deck is ok")
    deck_sections = deck_message.split(sep="------------------"
                                           "----------------------------------------------------")
    print(deck_sections)
    individual_parts = []
    for i in range(len(deck_sections)):
        individual_parts += deck_sections[i].split(sep="\n")
    individual_parts = [x for x in individual_parts if x]
    return individual_parts


def second_part_deck_validation(deck):
    global cards_array
    global cards_dict
    print("Size should be fine")
    name = deck[0]
    res = name != '' and all(c.isalnum() or c.isspace() for c in name)
    if len(name) > 27:
        return "Name too long"
    elif not res:
        return "Name contains non-alphanumeric characters"
    warlord_card = FindCard.find_card(deck[1], cards_array, cards_dict)
    if warlord_card.get_card_type() != "Warlord":
        print("Card in Warlord position is not a warlord")
        return "Card in Warlord position is not a warlord"
    remaining_signature_squad = copy.deepcopy(warlord_card.get_signature_squad())
    print("Warlord name: ", warlord_card.get_name())
    print("Remaining signature squad list: ", remaining_signature_squad)
    factions = deck[2].split(sep=" (")
    if len(factions) == 2:
        factions[1] = factions[1][:-1]
    print(factions)
    warlord_matches = True
    if factions[0] != warlord_card.get_faction():
        print("Faction chosen does not match the warlord")
        return "Warlord does not match main faction"
    if len(factions) == 1 and warlord_matches:
        factions.append("None")
        return deck_validation(deck, remaining_signature_squad, factions, warlord_card.get_name())
    if len(factions) == 2 and warlord_matches:
        if factions[0] == factions[1]:
            print("Main faction and ally faction can not be the same")
            return "Main faction and ally faction can not be the same"
        alignment_wheel = ["Astra Militarum", "Space Marines", "Tau", "Eldar",
                           "Dark Eldar", "Chaos", "Orks"]
        position_main_faction = -1
        for i in range(len(alignment_wheel)):
            if alignment_wheel[i] == factions[0]:
                position_main_faction = i
        if position_main_faction != -1:
            ally_pos_1 = (position_main_faction + 1) % 7
            ally_pos_2 = (position_main_faction - 1) % 7
            if (factions[1] == alignment_wheel[ally_pos_1] or factions[1] == alignment_wheel[ally_pos_2]) \
                    and warlord_card.get_name() != "Farseer Tadheris" and \
                    warlord_card.get_name() != "Commander Starblaze":
                return deck_validation(deck, remaining_signature_squad, factions, warlord=warlord_card.get_name())
            elif factions[1] == "Astra Militarum" and warlord_card.get_name() == "Commander Starblaze":
                return deck_validation(deck, remaining_signature_squad, factions, "Commander Starblaze")
            elif warlord_card.get_name() == "Farseer Tadheris":
                if factions[1] == "Space Marines" or factions[1] == "Orks":
                    return deck_validation(deck, remaining_signature_squad, factions, "Farseer Tadheris")
        return "Issue with faction matching."
    return "Unknown issue"


def deck_validation(deck, remaining_signature_squad, factions, warlord=""):
    global cards_array
    global cards_dict
    print("Can continue")
    current_index = 4
    if len(factions) == 1:
        factions.append("")
    holy_crusade_relevant = False
    has_non_sig_ritual = False
    if deck[3] != "Signature Squad":
        current_name = deck[3]
        card_result = FindCard.find_card(current_name, cards_array, cards_dict)
        current_index = 5
        if card_result.get_name() == "Holy Crusade":
            holy_crusade_relevant = True
        if card_result.get_faction() == factions[0]:
            print("Pledge ok")
        elif card_result.get_faction() == factions[1] and card_result.get_loyalty() == "Common":
            print("Pledge ok")
        else:
            return "Unexpected card in pledge area: " + current_name
    while deck[current_index] != "Army":
        if deck[current_index] in remaining_signature_squad:
            print("Found a match")
            try:
                remaining_signature_squad.remove(deck[current_index])
            except ValueError:
                print("How?")
            print(remaining_signature_squad)
        else:
            print("No match")
            return "Unexpected Card in Signature Squad: " + deck[current_index]
        current_index += 1
    if len(remaining_signature_squad) > 0:
        return "Missing something from signature squad"
    synapse_needed = False
    has_synapse = False
    if factions[0] == "Tyranids":
        synapse_needed = True
    current_index += 1
    card_count = 0
    skippers = ["Support", "Attachment", "Event", "Synapse"]
    while deck[current_index] != "Planet" and current_index < len(deck):
        if len(deck[current_index]) > 3:
            current_name = deck[current_index][3:]
            current_amount = deck[current_index][0]
            try:
                card_count += int(current_amount)
                max_copies = 3
                if current_name == "Immature Squig":
                    max_copies = 6
                if current_name in non_signature_rituals:
                    max_copies = 1
                    if has_non_sig_ritual:
                        return "Too many non-signature Ritual cards."
                    has_non_sig_ritual = True
                if int(current_amount) > max_copies:
                    print("Too many copies")
                    return "Too many copies: " + current_name + " (max " + str(current_amount) + ")"
            except ValueError:
                return "Number missing"
            card_result = FindCard.find_card(current_name, cards_array, cards_dict)
            if holy_crusade_relevant:
                if not card_result.check_for_a_trait("Ecclesiarchy"):
                    return "Non-Ecclesiarchy unit found: " + current_name
            if card_result.check_for_a_trait("Pledge"):
                return "Pledge card found outside of pledge area: " + current_name
            if card_result.get_name() != current_name:
                print("Card not found in database", current_name)
                return "Card not found in database: " + current_name
            if card_result.get_loyalty() == "Signature":
                print("Signature card found")
                return "Signature card found: " + current_name
            if card_result.get_card_type() == "Synapse":
                if synapse_needed:
                    if has_synapse:
                        return "Too many Synapse units given"
                    else:
                        if current_amount != "1":
                            return "Wrong number for synapse unit"
                        has_synapse = True
                else:
                    return "Synapse units not allowed in this deck"
            faction_check_passed = False
            if card_result.get_faction() == factions[0]:
                faction_check_passed = True
            elif card_result.get_faction() == factions[1] and card_result.get_loyalty() == "Common":
                faction_check_passed = True
                if warlord == "Yvraine":
                    if card_result.get_faction() == "Chaos":
                        if card_result.check_for_a_trait("Elite"):
                            faction_check_passed = False
            elif factions[0] == "Necrons" and card_result.get_faction() != "Tyranids" and \
                    card_result.get_loyalty() == "Common" and card_result.get_card_type() == "Army":
                faction_check_passed = True
            elif card_result.get_faction() == "Neutral":
                if factions[0] == "Tyranids" and card_result.get_card_type() == "Army":
                    return "Tyranids may not have Neutral Army Units in their deck"
                faction_check_passed = True
            elif warlord == "Gorzod":
                if card_result.get_faction() == "Astra Militarum" or card_result.get_faction() == "Space Marines":
                    if card_result.get_card_type() == "Army" and card_result.get_loyalty() == "Common":
                        if card_result.check_for_a_trait("Vehicle"):
                            faction_check_passed = True
            if not faction_check_passed:
                print("Faction check not passed", factions[0], factions[1], card_result.get_faction())
                return "Faction check not passed (Main, Ally, Card): "\
                       + factions[0] + factions[1] + card_result.get_faction()
        current_index += 1
        while deck[current_index] in skippers:
            current_index += 1
    if synapse_needed and not has_synapse:
        return "No Synapse Unit Given"
    if card_count < 42:
        print("Too few cards")
        return "Too few cards: " + str(card_count)
    print("No issues")
    return "SUCCESS"


class DecksConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "decks"
        self.room_group_name = "decks"
        self.user = self.scope["user"]
        self.name = self.user.username
        self.main_faction = ""
        self.ally_faction = ""
        self.warlord = ""
        print("got to decks consumer")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(self.room_name)
        print(self.name)
        await self.send_stored_decks()
        message = card_names
        if self.user.username in authorised_blackstone_users:
            message = card_names_with_bp
        await self.send(text_data=json.dumps({"message": message}))

    async def send_stored_decks(self):
        if not os.path.isdir("decks/DeckStorage/" + self.name):
            print("Path does not exist")
        elif self.name == "":
            print("Not logged in")
        else:
            for filename in os.listdir("decks/DeckStorage/" + self.name):
                await self.send_deck(filename)

    async def send_deck(self, filename):
        username = self.name
        if not self.name:
            username = "Anonymous"
        else:
            target_deck_dir = os.getcwd() + "/decks/DeckStorage/" + username + "/" + filename
            with open(target_deck_dir, "r") as file:
                content = file.readlines()
            print("Name:", content[0].replace('\n', ''))
            print("Warlord:", content[2].replace('\n', ''))
            message = "saved_deck/" + content[0].replace('\n', '') + "/" + content[2].replace('\n', '')
            await self.send(text_data=json.dumps({"message": message}))

    async def receive(self, text_data): # noqa
        global cards_array
        global cards_dict
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)
        split_message = message.split(sep="/")
        if len(split_message) == 1:
            card_object = FindCard.find_card(message, cards_array, cards_dict)
            if card_object.get_name() != "FINAL CARD":
                card_type = card_object.get_card_type()
                card_loyalty = card_object.get_loyalty()
                message = card_type + "/" + message
                if card_type == "Warlord":
                    message = message + "/" + card_object.get_faction()
                    self.main_faction = card_object.get_faction()
                    self.warlord = card_object.get_name()
                if card_loyalty != "Signature" or card_type == "Warlord":
                    if card_object.check_for_a_trait("Pledge"):
                        message = "Pledge/" + card_object.get_name()
                        print("New message", message)
                        if self.main_faction == card_object.get_faction():
                            print("sending")
                            await self.send(text_data=json.dumps({"message": message}))
                        elif self.ally_faction == card_object.get_faction() and card_loyalty == "Common":
                            print("sending")
                            await self.send(text_data=json.dumps({"message": message}))
                    elif self.main_faction == card_object.get_faction():
                        await self.send(text_data=json.dumps({"message": message}))
                    elif self.ally_faction == card_object.get_faction() and card_loyalty == "Common":
                        if self.warlord == "Yvraine":
                            if card_object.get_faction() == "Chaos" and card_object.check_for_a_trait("Elite"):
                                pass
                            else:
                                await self.send(text_data=json.dumps({"message": message}))
                        else:
                            await self.send(text_data=json.dumps({"message": message}))
                    elif self.main_faction == "Necrons" and card_object.get_faction() != "Tyranids" and\
                            card_loyalty == "Common" and card_type == "Army":
                        await self.send(text_data=json.dumps({"message": message}))
                    elif card_object.get_faction() == "Neutral":
                        if self.main_faction != "Tyranids":
                            await self.send(text_data=json.dumps({"message": message}))
                        elif card_type != "Army":
                            await self.send(text_data=json.dumps({"message": message}))
                    elif self.warlord == "Gorzod":
                        if card_object.get_card_type() == "Army":
                            if card_object.get_faction() == "Space Marines" \
                                    or card_object.get_faction() == "Astra Militarum":
                                if card_object.check_for_a_trait("Vehicle"):
                                    if card_loyalty == "Common":
                                        await self.send(text_data=json.dumps({"message": message}))
                if card_type == "Warlord":
                    sig_squad = card_object.signature_squad
                    for i in range(len(sig_squad)):
                        num_copies = int(sig_squad[i][0])
                        card_name = sig_squad[i][3:]
                        for _ in range(num_copies):
                            await self.send(text_data=json.dumps({"message": "SS/" + card_name}))
        elif len(split_message) == 2:
            if split_message[0] == "Name":
                s = split_message[1]
                res = s != '' and all(c.isalnum() or c.isspace() for c in s)
                if len(split_message[1]) > 27:
                    message = "Feedback/Name too long"
                elif not res:
                    message = "Feedback/Name contains non-alphanumeric characters"
                else:
                    print("Need to set name to: ", split_message[1])
                await self.send(text_data=json.dumps({"message": message}))
            elif split_message[0] == "Ally":
                print("Trying to set ally faction to:", split_message[1])
                changed_ally = False
                alignment_wheel = ["Astra Militarum", "Space Marines", "Tau", "Eldar",
                                   "Dark Eldar", "Chaos", "Orks"]
                position_main_faction = -1
                for i in range(len(alignment_wheel)):
                    if alignment_wheel[i] == self.main_faction:
                        position_main_faction = i
                if position_main_faction != -1:
                    ally_pos_1 = (position_main_faction + 1) % 7
                    ally_pos_2 = (position_main_faction - 1) % 7
                    if self.warlord == "Commander Starblaze":
                        if split_message[1] == "Astra Militarum":
                            self.ally_faction = split_message[1]
                            changed_ally = True
                    elif self.warlord == "Farseer Tadheris":
                        if split_message[1] == "Space Marines" or split_message[1] == "Orks":
                            self.ally_faction = split_message[1]
                            changed_ally = True
                    elif self.warlord == "Gorzod":
                        if split_message[1] == "":
                            self.ally_faction = ""
                            changed_ally = True
                    elif split_message[1] == alignment_wheel[ally_pos_1] \
                            or split_message[1] == alignment_wheel[ally_pos_2]:
                        self.ally_faction = split_message[1]
                        changed_ally = True
                print(self.main_faction, self.ally_faction)
                if self.main_faction == "Tyranids" or self.main_faction == "Necrons":
                    if split_message[1] == "":
                        changed_ally = True
                if changed_ally:
                    await self.send(text_data=json.dumps({"message": message}))
            elif split_message[0] == "DELETE DECK":
                deck_name = split_message[1]
                if os.path.isdir("decks/DeckStorage/" + self.name):
                    path_to_deck = os.getcwd() + "/decks/DeckStorage/" + self.name + "/" + deck_name
                    if os.path.exists(path_to_deck):
                        os.remove(path_to_deck)
            elif split_message[0] == "LOAD DECK":
                deck_name = split_message[1]
                if os.path.isdir("decks/DeckStorage/" + self.name):
                    path_to_deck = os.getcwd() + "/decks/DeckStorage/" + self.name + "/" + deck_name
                    if os.path.exists(path_to_deck):
                        with open(path_to_deck, 'r') as f:
                            deck_content = f.read()
                        deck_list_content = deck_content.split(sep="\n")
                        message = "Load deck/" + deck_content
                        deck_name = "Name/" + deck_list_content[0]
                        await self.send(text_data=json.dumps({"message": deck_name}))
                        warlord = "Warlord/" + deck_list_content[2]
                        await self.send(text_data=json.dumps({"message": warlord}))
                        factions = deck_list_content[3]
                        factions = factions.split(sep=" (")
                        pledge = deck_list_content[4]
                        num_to_delete = 4
                        if pledge != "----------------------------------------------------------------------"\
                                and pledge:
                            print("pledge: ", pledge)
                            pledge = "Pledge/" + pledge
                            num_to_delete = 5
                            await self.send(text_data=json.dumps({"message": pledge}))
                        for i in range(len(factions)):
                            factions[i] = factions[i].replace(")", "")
                            if i == 0:
                                self.main_faction = factions[i]
                                if len(factions) == 1:
                                    ally = "SetAlly/"
                                    await self.send(text_data=json.dumps({"message": ally}))
                            elif i == 1:
                                self.ally_faction = factions[i]
                                ally = "SetAlly/" + factions[i]
                                await self.send(text_data=json.dumps({"message": ally}))
                        await self.send(text_data=json.dumps({"message": "Ally"}))
                        for i in range(num_to_delete):
                            del deck_list_content[0]
                        i = 0
                        while i < len(deck_list_content):
                            if deck_list_content[i] in ["-----------------------------------"
                                                        "-----------------------------------", ""]:
                                del deck_list_content[i]
                                i = i - 1
                            i = i + 1
                        current_header = "SS"
                        for i in range(len(deck_list_content)):
                            if deck_list_content[i] in ["Signature Squad", "Army", "Support",
                                                        "Synapse", "Attachment", "Event", "Planet"]:
                                current_header = deck_list_content[i]
                                if current_header == "Signature Squad":
                                    current_header = "SS"
                            else:
                                number_of_cards = deck_list_content[i][0]
                                card_name = deck_list_content[i][3:]
                                for _ in range(int(number_of_cards)):
                                    item_sent = current_header + "/" + card_name
                                    await self.send(text_data=json.dumps({"message": item_sent}))
                        # print("Sending: ", deck_name, warlord, factions, sep="\n")
                        # await self.send(text_data=json.dumps({"message": message}))
            elif split_message[0] == "SEND DECK":
                message_to_send = ""
                split_message[1] = split_message[1].replace("\"Subject: &Omega;-X62113\"", "")
                split_message[1] = split_message[1].replace("idden Base", "'idden Base")
                split_message[1] = split_message[1].replace("\"", "")
                true_split_message = split_message[1].split(sep="\n")
                while true_split_message:
                    if true_split_message[0].strip():
                        break
                    del true_split_message[0]
                split_message[1] = "\n".join(true_split_message)
                deck = clean_sent_deck(split_message[1])
                deck_name = deck[0]
                if len(deck) > 5:
                    if "{AUTOMAIN}" in deck[2]:
                        warlord = FindCard.find_card(deck[1], cards_array, cards_dict)
                        deck[2] = deck[2].replace("{AUTOMAIN}", warlord.get_faction())
                        split_message[1] = split_message[1].replace("{AUTOMAIN}", warlord.get_faction())
                    message_to_send = second_part_deck_validation(deck)
                if message_to_send == "SUCCESS":
                    print("Need to save deck")
                    print(os.path.dirname(os.path.realpath(__file__)))
                    print(os.getcwd())
                    username = self.name
                    if not self.name:
                        username = "Anonymous"
                    print("username:", username)
                    target_user_dir = os.getcwd() + "/decks/DeckStorage/" + username
                    target_deck_dir = os.getcwd() + "/decks/DeckStorage/" + username + "/" + deck_name
                    print(target_user_dir)
                    print(target_deck_dir)
                    if not os.path.isdir(target_user_dir):
                        print("Path does not exist")
                        os.mkdir(target_user_dir)
                    will_send = False
                    if not os.path.exists(target_deck_dir):
                        will_send = True
                    with open(target_deck_dir, "w") as file:
                        file.write(split_message[1])
                    if will_send:
                        await self.send_deck(deck_name)
                message_to_send = "Feedback/" + message_to_send
                message = message_to_send
                await self.send(text_data=json.dumps({"message": message}))

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
