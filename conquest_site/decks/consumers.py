import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from .deckscode import CardClasses, Initfunctions, FindCard
import os

cards_array = Initfunctions.init_player_cards()
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
    remaining_signature_squad = []
    print("Size should be fine")
    warlord_card = FindCard.find_card(deck[1], cards_array)
    if warlord_card.get_card_type() != "Warlord":
        print("Card in Warlord position is not a warlord")
        return "Card in Warlord position is not a warlord"
    if warlord_card.get_name() == "Nazdreg":
        remaining_signature_squad = ['1x Cybork Body', '1x Kraktoof Hall',
                                     '2x Bigga Is Betta', "4x Nazdreg's Flash Gitz"]
    if warlord_card.get_name() == "Zarathur, High Sorcerer":
        remaining_signature_squad = ['1x Mark of Chaos', '1x Shrine of Warpflame',
                                     '2x Infernal Gateway', "4x Zarathur's Flamers"]
    factions = deck[2].split(sep=" (")
    if len(factions) == 2:
        factions[1] = factions[1][:-1]
    print(factions)
    warlord_matches = True
    if factions[0] != warlord_card.get_faction():
        print("Faction chosen does not match the warlord")
        return "Warlord does not match main faction"
    if len(factions) == 1 and warlord_matches:
        return deck_validation(deck, remaining_signature_squad, factions)
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
            if factions[1] == alignment_wheel[ally_pos_1] \
                    or factions[1] == alignment_wheel[ally_pos_2]:
                return deck_validation(deck, remaining_signature_squad, factions)
        return "Issue with faction matching."
    return "Unknown issue"


def deck_validation(deck, remaining_signature_squad, factions):
    global cards_array
    print("Can continue")
    current_index = 4
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
            return "Unexpected Card in Signature Squad"
        current_index += 1
    if len(remaining_signature_squad) > 0:
        return "Missing something from signature squad"
    current_index += 1
    card_count = 0
    skippers = ["Support", "Attachment", "Event", "Synapse"]
    while deck[current_index] != "Planet" and current_index < len(deck):
        if len(deck[current_index]) > 3:
            current_name = deck[current_index][3:]
            current_amount = deck[current_index][0]
            try:
                card_count += int(current_amount)
                if int(current_amount) > 3:
                    print("Too many copies")
                    return "Too many copies: " + current_name
            except ValueError:
                return "Number missing"
            card_result = FindCard.find_card(current_name, cards_array)
            if card_result.get_name() != current_name:
                print("Card not found in database", current_name)
                return "Card not found in database: " + current_name
            if card_result.get_loyalty() == "Signature":
                print("Signature card found")
                return "Signature card found: " + current_name
            faction_check_passed = False
            if card_result.get_faction() == factions[0]:
                faction_check_passed = True
            elif card_result.get_faction() == factions[1] and card_result.get_loyalty() == "Common":
                faction_check_passed = True
            elif card_result.get_faction() == "Neutral":
                faction_check_passed = True
            if not faction_check_passed:
                print("Faction check not passed", factions[0], factions[1], card_result.get_faction())
                return "Faction check not passed (Main, Ally, Card): "\
                       + factions[0] + factions[1] + card_result.get_faction()
        current_index += 1
        while deck[current_index] in skippers:
            current_index += 1
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
        print("got to decks consumer")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(self.room_name)
        print(self.name)

    async def receive(self, text_data): # noqa
        global cards_array
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)
        split_message = message.split(sep="/")
        if len(split_message) == 1:
            card_object = FindCard.find_card(message, cards_array)
            if card_object.get_name() != "FINAL CARD":
                card_type = card_object.get_card_type()
                card_loyalty = card_object.get_loyalty()
                message = card_type + "/" + message
                if card_type == "Warlord":
                    message = message + "/" + card_object.get_faction()
                    self.main_faction = card_object.get_faction()
                if card_loyalty != "Signature" or card_type == "Warlord":
                    if self.main_faction == card_object.get_faction():
                        await self.send(text_data=json.dumps({"message": message}))
                    if self.ally_faction == card_object.get_faction() and card_loyalty == "Common":
                        await self.send(text_data=json.dumps({"message": message}))
                    if card_object.get_faction() == "Neutral":
                        await self.send(text_data=json.dumps({"message": message}))
                if card_object.get_name() == "Nazdreg":
                    for i in range(4):
                        await self.send(text_data=json.dumps({"message": "SS/Nazdreg's Flash Gitz"}))
                    await self.send(text_data=json.dumps({"message": "SS/Bigga Is Betta"}))
                    await self.send(text_data=json.dumps({"message": "SS/Bigga Is Betta"}))
                    await self.send(text_data=json.dumps({"message": "SS/Kraktoof Hall"}))
                    await self.send(text_data=json.dumps({"message": "SS/Cybork Body"}))
                if card_object.get_name() == "Zarathur, High Sorcerer":
                    for i in range(4):
                        await self.send(text_data=json.dumps({"message": "SS/Zarathur's Flamers"}))
                    await self.send(text_data=json.dumps({"message": "SS/Infernal Gateway"}))
                    await self.send(text_data=json.dumps({"message": "SS/Infernal Gateway"}))
                    await self.send(text_data=json.dumps({"message": "SS/Shrine of Warpflame"}))
                    await self.send(text_data=json.dumps({"message": "SS/Mark of Chaos"}))
                if card_object.get_name() == "Captain Cato Sicarius":
                    for i in range(4):
                        await self.send(text_data=json.dumps({"message": "SS/Sicarius's Chosen"}))
                    await self.send(text_data=json.dumps({"message": "SS/The Fury of Sicarius"}))
                    await self.send(text_data=json.dumps({"message": "SS/The Fury of Sicarius"}))
                    await self.send(text_data=json.dumps({"message": "SS/Cato's Stronghold"}))
                    await self.send(text_data=json.dumps({"message": "SS/Tallassarian Tempest Blade"}))

        elif len(split_message) == 2:
            if split_message[0] == "Name":
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
                    if split_message[1] == alignment_wheel[ally_pos_1] \
                            or split_message[1] == alignment_wheel[ally_pos_2]:
                        self.ally_faction = split_message[1]
                        changed_ally = True
                print(self.main_faction, self.ally_faction)
                if changed_ally:
                    await self.send(text_data=json.dumps({"message": message}))
            elif split_message[0] == "SEND DECK":
                message_to_send = ""
                deck = clean_sent_deck(split_message[1])
                print(deck)
                deck_name = deck[0]
                if len(deck) > 5:
                    message_to_send = second_part_deck_validation(deck)
                if message_to_send == "SUCCESS":
                    print("Need to save deck")
                    print(os.path.dirname(os.path.realpath(__file__)))
                    print(os.getcwd())
                    if not os.path.isdir("decks/DeckStorage/" + self.name):
                        print("Path does not exist")
                        os.mkdir("decks/DeckStorage/" + self.name)
                    with open("decks/DeckStorage/" + self.name + "/" + deck_name, "w") as file:
                        file.write(split_message[1])
                message_to_send = "Feedback/" + message_to_send
                message = message_to_send
                await self.send(text_data=json.dumps({"message": message}))

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
