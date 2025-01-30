import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from .gamecode import GameClass
import os
from .gamecode import Initfunctions


card_array = Initfunctions.init_player_cards()
planet_array = Initfunctions.init_planet_cards()

active_lobbies = [[], []]
active_games = []


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global active_lobbies
        self.room_name = "lobby"
        self.room_group_name = "lobby"
        self.user = self.scope["user"]
        self.name = self.user.username
        print(self.name)
        print("got to lobby consumer")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        for i in range(len(active_lobbies[0])):
            message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i]
            await self.chat_message({"type": "chat.message", "message": message})

    async def receive(self, text_data):
        global active_lobbies
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)
        if message == "Create lobby":
            print("code to create lobby for:", self.name)
            if self.name == "":
                print("Must be logged in to create a lobby.")
                await self.chat_message({"type": "chat.message", "message": "Logged out"})
                return None
            for i in range(len(active_lobbies[0])):
                if active_lobbies[0][i] == self.name or active_lobbies[1][i] == self.name:
                    print("User is already in a lobby.")
                    await self.chat_message({"type": "chat.message", "message": "Already in lobby"})
                    return None
            active_lobbies[0].append(self.name)
            active_lobbies[1].append("")
            print(active_lobbies)
            length = len(active_lobbies[0])
            message += "/" + active_lobbies[0][length - 1] + "/" + active_lobbies[1][length - 1]
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )
        if message == "Remove lobby":
            i = 0
            while i < len(active_lobbies[0]):
                if active_lobbies[0][i] == self.name:
                    del active_lobbies[0][i]
                    del active_lobbies[1][i]
                    i += -1
                i += 1
            print(active_lobbies)
            message = "Delete lobby"
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )
            for i in range(len(active_lobbies[0])):
                message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i]
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
        message = message.split(sep="/")
        if len(message) > 1:
            if message[0] == "Join lobby":
                print("code to join lobby")
                print(message[1])
                for i in range(len(active_lobbies[0])):
                    if active_lobbies[0][i] == message[1]:
                        active_lobbies[1][i] = self.name
                print(active_lobbies)
                message = "Delete lobby"
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i]
                    await self.channel_layer.group_send(
                        self.room_group_name, {"type": "chat.message", "message": message}
                    )
            if message[0] == "Start game":
                print("Code to start game")
                game_id = ''.join(
                    random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
                print(game_id)
                first_name = ""
                second_name = ""
                for i in range(len(active_lobbies[0])):
                    if active_lobbies[0][i] == self.name:
                        first_name = active_lobbies[0][i]
                        second_name = active_lobbies[1][i]
                message = "Move to game/" + game_id + "/" + first_name + "/" + second_name
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                i = 0
                while i < len(active_lobbies[0]):
                    if active_lobbies[0][i] == self.name:
                        del active_lobbies[0][i]
                        del active_lobbies[1][i]
                        i += -1
                    i += 1
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i]
                    await self.channel_layer.group_send(
                        self.room_group_name, {"type": "chat.message", "message": message}
                    )

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


chat_messages = [[], []]


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global active_games

        print("got to game consumer")
        self.room_name = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = f"play_{self.room_name}"
        self.user = self.scope["user"]
        self.name = self.user.username
        print("username:", self.user.username, ".")
        if self.name == "":
            self.name = "Anonymous"
        room_already_exists = False
        game_id_if_exists = -1
        self.game_position = 0
        for i in range(len(active_games)):
            if active_games[i].game_id == self.room_name:
                room_already_exists = True
                game_id_if_exists = i
                self.game_position = i
        if not room_already_exists:
            active_games.append(GameClass.Game("1", "Example", "alex", card_array))
            active_games[len(active_games) - 1].game_sockets.append(self)
            self.game_position = len(active_games) - 1
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(self.room_name)
        for i in range(len(chat_messages[0])):
            if chat_messages[0][i] == self.room_name:
                await self.send(text_data=json.dumps({"message": chat_messages[1][i]}))
        if room_already_exists:
            await active_games[game_id_if_exists].joined_requests_graphics()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def receive_game_update(self, text_update):
        print("game update received: ", text_update)
        split_text = text_update.split("/")
        if split_text[0] == "GAME_INFO":
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": text_update}
            )
        else:
            text_update = "server: " + text_update
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": text_update}
            )

    async def receive(self, text_data):
        global active_games
        global chat_messages
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)
        message = message.split("/")
        if message[0] == "CHAT_MESSAGE" and len(message) > 1:
            if message[1] == "PLANETS":
                print("Need to load planets")
                for i in range(len(active_games)):
                    if active_games[i].game_id == self.room_name:
                        await active_games[i].send_planet_array()
            elif (message[1] == "LOAD DECK" or message[1] == "LOADDECK") and len(message) > 2:
                deck_name = message[2]
                print(deck_name)
                path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + self.user.username + "/" + deck_name
                print(path_to_player_decks)
                if os.path.exists(path_to_player_decks):
                    print("Success")
                    with open(path_to_player_decks, 'r') as f:
                        deck_content = f.read()
                    print(deck_content)
                    for i in range(len(active_games)):
                        if active_games[i].game_id == self.room_name:
                            print("In correct room")
                            if active_games[i].name_1 == self.name:
                                print("Need to load player one's deck")
                                if not active_games[i].p1.deck_loaded:
                                    await active_games[i].p1.setup_player(deck_content, active_games[i].planet_array)
                            elif active_games[i].name_2 == self.name:
                                print("Need to load player two's deck")
                                if not active_games[i].p2.deck_loaded:
                                    await active_games[i].p2.setup_player(deck_content, active_games[i].planet_array)
            elif message[1] == "DRAW" and len(message) > 2:
                if message[2] == "1":
                    active_games[self.game_position].p1.draw_card()
                    await active_games[self.game_position].p1.send_hand()
                elif message[2] == "2":
                    active_games[self.game_position].p2.draw_card()
                    await active_games[self.game_position].p2.send_hand()
            else:
                message = self.name + ": " + message[1]
                print("receive:", message)
                chat_messages[0].append(self.room_name)
                chat_messages[1].append(message)
                print(chat_messages)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
