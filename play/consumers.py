import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from .gamecode import GameClass
import os
from .gamecode import Initfunctions, FindCard
import threading

card_array = Initfunctions.init_player_cards()
planet_array = Initfunctions.init_planet_cards()

active_lobbies = [[], []]
active_games = []

condition_lobby = threading.Condition()

condition_games = threading.Condition()


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global active_lobbies
        global condition_lobby
        self.room_name = "lobby"
        self.room_group_name = "lobby"
        self.user = self.scope["user"]
        self.name = self.user.username
        print(self.name)
        print("got to lobby consumer")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        condition_lobby.acquire()

        await self.accept()
        for i in range(len(active_lobbies[0])):
            message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i]
            await self.chat_message({"type": "chat.message", "message": message})
        condition_lobby.notify_all()
        condition_lobby.release()

    async def receive(self, text_data): # noqa
        global active_lobbies
        global active_games
        global condition_lobby
        global condition_games
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)
        condition_lobby.acquire()
        condition_games.acquire()
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
                game_id = self.create_game(first_name, second_name, game_id)
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
        condition_lobby.notify_all()
        condition_lobby.release()
        condition_games.notify_all()
        condition_games.release()

    async def chat_message(self, event):
        message = event["message"]
        print("send:", message)
        # Send message to WebSocket
        # FIXME: Disconnect() method of WebSocketConsumer not being called
        # FIXME: https://github.com/django/channels/issues/1466
        # FIXME: Needs Django Channels dev team to fix this issue
        try:
            await self.send(text_data=json.dumps({"message": message}))
        except autobahn.exception.Disconnected:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    def create_game(self, name_1, name_2, game_id):
        global active_games
        global card_array
        global planet_array
        for i in range(len(active_games)):
            if active_games[i].game_id == game_id:
                new_game_id = game_id + random.choice('0123456789ABCDEF')
                return self.create_game(name_1, name_2, new_game_id)
        active_games.append(GameClass.Game(game_id, name_1, name_2, card_array, planet_array))
        return game_id



chat_messages = [[], []]


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global active_games
        global card_array
        global planet_array
        global condition_games

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
        condition_games.acquire()
        for i in range(len(active_games)):
            if active_games[i].game_id == self.room_name:
                room_already_exists = True
                game_id_if_exists = i
                self.game_position = i
        if room_already_exists:
            if not active_games[game_id_if_exists].game_sockets:
                active_games[game_id_if_exists].game_sockets.append(self)
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(self.room_name)
        for i in range(len(chat_messages[0])):
            if chat_messages[0][i] == self.room_name:
                await self.send(text_data=json.dumps({"message": chat_messages[1][i]}))
        if room_already_exists:
            await active_games[game_id_if_exists].joined_requests_graphics(self.name)
        condition_games.notify_all()
        condition_games.release()

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

    async def receive(self, text_data): # noqa
        global active_games
        global chat_messages
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)
        message = message.split("/")
        condition_games.acquire()
        if message[0] == "BUTTON PRESSED":
            current_game_id = -1
            for i in range(len(active_games)):
                if active_games[i].game_id == self.room_name:
                    print("Found room")
                    current_game_id = i
            if current_game_id != -1:
                await active_games[current_game_id].update_game_event(self.name, message[1:])
        if message[0] == "CHAT_MESSAGE" and len(message) > 1:
            del message[0]
            if message[0] == "" and len(message) > 1:
                if message[1] == "planets":
                    print("Need to load planets")
                    for i in range(len(active_games)):
                        if active_games[i].game_id == self.room_name:
                            await active_games[i].send_planet_array()
                elif message[1] == "force-quit-reactions":
                    await self.receive_game_update("FORCEFULLY QUITTING REACTIONS")
                    active_games[self.game_position].reset_reactions_data()
                    await active_games[self.game_position].send_info_box()
                elif message[1] == "force-quit-effects":
                    await self.receive_game_update("FORCEFULLY QUITTING REACTIONS")
                    active_games[self.game_position].reset_effects_data()
                    await active_games[self.game_position].send_info_box()
                elif message[1] == "force-quit-damage":
                    await self.receive_game_update("FORCEFULLY QUITTING DAMAGE")
                    active_games[self.game_position].reset_damage_data()
                    await active_games[self.game_position].send_info_box()
                elif message[1] == "force-quit-action":
                    await self.receive_game_update("FORCEFULLY QUITTING ACTION")
                    active_games[self.game_position].reset_action_data()
                    await active_games[self.game_position].send_info_box()
                elif (message[1] == "loaddeck" or message[1] == "LOADDECK") and len(message) > 2:
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
                elif message[1] == "addcard" and len(message) > 3:
                    card_name = message[3]
                    card = FindCard.find_card(card_name, active_games[self.game_position].card_array)
                    if card.get_shields() != "FINAL CARD":
                        if message[2] == "1":
                            active_games[self.game_position].p1.cards.append(card_name)
                            await active_games[self.game_position].p1.send_hand()
                        elif message[2] == "2":
                            active_games[self.game_position].p2.cards.append(card_name)
                            await active_games[self.game_position].p2.send_hand()
                elif message[1] == "draw" and len(message) > 2:
                    if message[2] == "1":
                        num_times = 1
                        if len(message) == 4:
                            try:
                                num_times = int(message[3])
                            except:
                                pass
                        if num_times > 50:
                            num_times = 50
                        for i in range(num_times):
                            active_games[self.game_position].p1.draw_card()
                        await active_games[self.game_position].p1.send_hand()
                    elif message[2] == "2":
                        num_times = 1
                        if len(message) == 4:
                            try:
                                num_times = int(message[3])
                            except:
                                pass
                        if num_times > 50:
                            num_times = 50
                        for i in range(num_times):
                            active_games[self.game_position].p2.draw_card()
                        await active_games[self.game_position].p2.send_hand()
                elif message[1] == "discard" and len(message) > 3:
                    hand_pos = int(message[3])
                    if message[2] == "1":
                        active_games[self.game_position].p1.discard_card_from_hand(hand_pos)
                        await active_games[self.game_position].p1.send_hand()
                        await active_games[self.game_position].p1.send_discard()
                    elif message[2] == "2":
                        active_games[self.game_position].p2.discard_card_from_hand(hand_pos)
                        await active_games[self.game_position].p2.send_hand()
                        await active_games[self.game_position].p2.send_discard()
                elif message[1] == "clear-reticle" and len(message) > 3:
                    unit_position = message[2:]
                    if active_games[self.game_position].validate_received_game_string(unit_position):
                        try:
                            if unit_position[1] == "1":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p1.reset_aiming_reticle_in_play(
                                        -2, int(unit_position[2]))
                                    await active_games[self.game_position].p1.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p1.reset_aiming_reticle_in_play(
                                        int(unit_position[2]), int(unit_position[3]))
                                    await active_games[self.game_position].p1.send_units_at_planet(
                                        int(unit_position[2]))
                            elif unit_position[1] == "2":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p2.reset_aiming_reticle_in_play(
                                        -2, int(unit_position[2]))
                                    await active_games[self.game_position].p2.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p2.reset_aiming_reticle_in_play(
                                        int(unit_position[2]), int(unit_position[3]))
                                    await active_games[self.game_position].p2.send_units_at_planet(
                                        int(unit_position[2]))
                        except:
                            await self.channel_layer.group_send(
                                self.room_group_name, {"type": "chat.message", "message": "Incorrect clear usage"}
                            )
                elif message[1] == "ready-card" and len(message) > 3:
                    unit_position = message[2:]
                    if active_games[self.game_position].validate_received_game_string(unit_position):
                        try:
                            if unit_position[1] == "1":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p1.ready_given_pos(-2, int(unit_position[2]))
                                    await active_games[self.game_position].p1.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p1.ready_given_pos(int(unit_position[2]),
                                                                                        int(unit_position[3]))
                                    await active_games[self.game_position].p1.send_units_at_planet(
                                        int(unit_position[2]))
                            elif unit_position[1] == "2":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p2.ready_given_pos(-2, int(unit_position[2]))
                                    await active_games[self.game_position].p2.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p2.ready_given_pos(int(unit_position[2]),
                                                                                        int(unit_position[3]))
                                    await active_games[self.game_position].p2.send_units_at_planet(
                                        int(unit_position[2]))
                        except:
                            await self.channel_layer.group_send(
                                self.room_group_name, {"type": "chat.message", "message": "Incorrect ready usage"}
                            )
                elif message[1] == "exhaust-card" and len(message) > 3:
                    unit_position = message[2:]
                    if active_games[self.game_position].validate_received_game_string(unit_position):
                        try:
                            if unit_position[1] == "1":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p1.exhaust_given_pos(-2, int(unit_position[2]))
                                    await active_games[self.game_position].p1.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p1.exhaust_given_pos(int(unit_position[2]),
                                                                                        int(unit_position[3]))
                                    await active_games[self.game_position].p1.send_units_at_planet(
                                        int(unit_position[2]))
                            elif unit_position[1] == "2":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p2.exhaust_given_pos(-2, int(unit_position[2]))
                                    await active_games[self.game_position].p2.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p2.exhaust_given_pos(int(unit_position[2]),
                                                                                        int(unit_position[3]))
                                    await active_games[self.game_position].p2.send_units_at_planet(
                                        int(unit_position[2]))
                        except:
                            await self.channel_layer.group_send(
                                self.room_group_name, {"type": "chat.message", "message": "Incorrect exhaust usage"}
                            )
                elif message[1] == "set-damage" and len(message) > 3:
                    unit_position = message[2:]
                    unit_position = unit_position[:-1]
                    damage = message[-1]
                    print(unit_position, damage)
                    if active_games[self.game_position].validate_received_game_string(unit_position):
                        try:
                            damage = int(damage)
                            if unit_position[1] == "1":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p1.set_damage_given_pos(
                                        -2, int(unit_position[2]), damage)
                                    await active_games[self.game_position].p1.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p1.set_damage_given_pos(
                                        int(unit_position[2]), int(unit_position[3]), damage)
                                    await active_games[self.game_position].p1.send_units_at_planet(
                                        int(unit_position[2]))
                            elif unit_position[2] == "2":
                                if unit_position[0] == "HQ":
                                    active_games[self.game_position].p2.set_damage_given_pos(
                                        -2, int(unit_position[2]), damage)
                                    await active_games[self.game_position].p2.send_hq()
                                elif unit_position[0] == "IN_PLAY":
                                    active_games[self.game_position].p2.set_damage_given_pos(
                                        int(unit_position[2]), int(unit_position[3]), damage)
                                    await active_games[self.game_position].p2.send_units_at_planet(
                                        int(unit_position[2]))
                        except:
                            await self.channel_layer.group_send(
                                self.room_group_name, {"type": "chat.message", "message": "Incorrect SET-DAMAGE usage"}
                            )
            else:
                message = self.name + ": " + message[0]
                print("receive:", message)
                chat_messages[0].append(self.room_name)
                chat_messages[1].append(message)
                print(chat_messages)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
        condition_games.notify_all()
        condition_games.release()
