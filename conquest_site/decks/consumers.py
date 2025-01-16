import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer


class DecksConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "lobby"
        self.room_group_name = "lobby"
        self.user = self.scope["user"]
        self.name = self.user.username
        print("got to decks consumer")
