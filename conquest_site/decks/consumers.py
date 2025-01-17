import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from .deckscode import CardClasses, Initfunctions, FindCard
cards_array = Initfunctions.init_player_cards()
# cards_array[10].print_info()
planet_cards_array = Initfunctions.init_planet_cards()
# planet_cards_array[5].print_info()

card_object = FindCard.find_card("Error", cards_array)
card_object.print_info()


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
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)
        await self.send(text_data=json.dumps({"message": message}))


    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))