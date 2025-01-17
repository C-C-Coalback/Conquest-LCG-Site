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
                await self.send(text_data=json.dumps({"message": message}))
        elif len(split_message) == 2:
            if split_message[0] == "Name":
                print("Need to set name to: ", split_message[1])
                await self.send(text_data=json.dumps({"message": message}))

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))