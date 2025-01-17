import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from .deckscode import CardClasses, Initfunctions, FindCard

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
    current_index += 1
    skippers = ["Support", "Attachment", "Event", "Synapse"]
    while deck[current_index] != "Planet" and current_index < len(deck):
        if len(deck[current_index]) > 3:
            current_name = deck[current_index][3:]
            current_amount = deck[current_index][0]
            if int(current_amount) > 3:
                print("Too many copies")
                return "Too many copies"
            card_result = FindCard.find_card(current_name, cards_array)
            if card_result.get_name() != current_name:
                print("Card not found in database", current_name)
                return "Card not found in database"
            if card_result.get_card_type() == "Signature":
                print("Signature card found")
                return "Signature card found"
            faction_check_passed = False
            if card_result.get_faction() == factions[0]:
                faction_check_passed = True
            elif card_result.get_faction() == factions[1] and card_result.get_loyalty() == "Common":
                faction_check_passed = True
            elif card_result.get_faction() == "Neutral":
                faction_check_passed = True
            if not faction_check_passed:
                print("Faction check not passed", factions[0], factions[1], card_result.get_faction())
                return "Faction check not passed"
        current_index += 1
        while deck[current_index] in skippers:
            current_index += 1
    print("No issues")
    return "No issues"


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

    async def receive(self, text_data):
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
                if card_object.get_name() == "Nazdreg":
                    for i in range(4):
                        await self.send(text_data=json.dumps({"message": "SS/Nazdreg's Flash Gitz"}))
                    await self.send(text_data=json.dumps({"message": "SS/Bigga is Betta"}))
                    await self.send(text_data=json.dumps({"message": "SS/Bigga is Betta"}))
                    await self.send(text_data=json.dumps({"message": "SS/Kraktoof Hall"}))
                    await self.send(text_data=json.dumps({"message": "SS/Cybork Body"}))
                if card_object.get_name() == "Zarathur, High Sorcerer":
                    for i in range(4):
                        await self.send(text_data=json.dumps({"message": "SS/Zarathur's Flamers"}))
                    await self.send(text_data=json.dumps({"message": "SS/Infernal Gateway"}))
                    await self.send(text_data=json.dumps({"message": "SS/Infernal Gateway"}))
                    await self.send(text_data=json.dumps({"message": "SS/Shrine of Warpflame"}))
                    await self.send(text_data=json.dumps({"message": "SS/Mark of Chaos"}))

        elif len(split_message) == 2:
            if split_message[0] == "Name":
                print("Need to set name to: ", split_message[1])
                await self.send(text_data=json.dumps({"message": message}))
            elif split_message[0] == "Ally":
                print("Trying to set ally faction to:", split_message[1])
                changed_ally = False
                if self.main_faction == "Chaos" and split_message[1] == "Orks":
                    self.ally_faction = "Orks"
                    changed_ally = True
                elif self.main_faction == "Orks" and split_message[1] == "Chaos":
                    self.ally_faction = "Chaos"
                    changed_ally = True
                print(self.main_faction, self.ally_faction)
                if changed_ally:
                    await self.send(text_data=json.dumps({"message": message}))
            elif split_message[0] == "SEND DECK":
                message_to_send = ""
                deck = clean_sent_deck(split_message[1])
                print(deck)
                remaining_signature_squad = []
                if len(deck) > 5:
                    print("Size should be fine")
                    warlord_card = FindCard.find_card(deck[1], cards_array)
                    if warlord_card.get_card_type() != "Warlord":
                        print("Card in Warlord position is not a warlord.")
                    if warlord_card.get_name() == "Nazdreg":
                        remaining_signature_squad = ['1x Cybork Body', '1x Kraktoof Hall',
                                                     '2x Bigga Is Betta', "4x Nazdreg's Flash Gitz"]
                    factions = deck[2].split(sep=" (")
                    if len(factions) == 2:
                        factions[1] = factions[1][:-1]
                    print(factions)
                    warlord_matches = True
                    if factions[0] != warlord_card.get_faction():
                        print("Faction chosen does not match the warlord.")
                        warlord_matches = False
                    if len(factions) == 1 and warlord_matches:
                        message_to_send = deck_validation(deck, remaining_signature_squad, factions)
                    if len(factions) == 2 and warlord_matches:
                        if factions[0] == factions[1]:
                            print("Main faction and ally faction can not be the same.")
                        if (factions[0] == "Orks" and factions[1] == "Chaos") or (
                                factions[0] == "Chaos" and factions[1] == factions[0]):
                            message_to_send = deck_validation(deck, remaining_signature_squad, factions)

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
