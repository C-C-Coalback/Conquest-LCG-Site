import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from .deckscode import CardClasses, Initfunctions, FindCard
cards_array = Initfunctions.init_player_cards()
planet_cards_array = Initfunctions.init_planet_cards()


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

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))