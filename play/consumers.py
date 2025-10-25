import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from .gamecode import GameClass
import os
from .gamecode import Initfunctions, FindCard
import threading
import traceback
import datetime


card_array = Initfunctions.init_player_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()

active_lobbies = [[], [], [], [], []]
spectator_games = []  # Format: (p_one_name, p_two_name, game_id, end_time)
active_games = []

condition_lobby = threading.Condition()

condition_games = threading.Condition()


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global active_lobbies
        global condition_lobby
        global spectator_games
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
            message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i] + "/" \
                      + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i]
            await self.chat_message({"type": "chat.message", "message": message})
        i = 0
        print("CURRENT SPEC")
        print(spectator_games)
        while i < len(spectator_games):
            if spectator_games[i][3] < datetime.datetime.now():
                del spectator_games[i]
                i = i - 1
            i = i + 1
        message = "Delete spec"
        print("CURRENT SPEC")
        print(spectator_games)
        await self.chat_message({"type": "chat.message", "message": message})
        for i in range(len(spectator_games)):
            message = "Create spec/" + spectator_games[i][0] + "/" + spectator_games[i][1] + "/" + spectator_games[i][2]
            await self.chat_message({"type": "chat.message", "message": message})
        condition_lobby.notify_all()
        condition_lobby.release()

    async def receive(self, text_data): # noqa
        global active_lobbies
        global active_games
        global condition_lobby
        global condition_games
        global spectator_games
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        split_message = message.split(sep="/")
        print("receive:", message)
        condition_lobby.acquire()
        condition_games.acquire()
        if split_message[0] == "Create lobby":
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
            if split_message[1] == "false":
                active_lobbies[2].append("Public")
            else:
                active_lobbies[2].append("Private")
            if split_message[2] == "false":
                active_lobbies[3].append("No Errata")
            else:
                active_lobbies[3].append("Apoka")
            active_lobbies[4].append(split_message[3])
            print(active_lobbies)
            le = len(active_lobbies[0]) - 1
            split_message[0] += "/" + active_lobbies[0][le] + "/" + active_lobbies[1][le] + \
                                "/" + active_lobbies[2][le] + "/" + active_lobbies[3][le] + \
                                "/" + active_lobbies[4][le]
            print(split_message[0])
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": split_message[0]}
            )
        if message == "Remove lobby":
            i = 0
            while i < len(active_lobbies[0]):
                if active_lobbies[0][i] == self.name:
                    del active_lobbies[0][i]
                    del active_lobbies[1][i]
                    del active_lobbies[2][i]
                    del active_lobbies[3][i]
                    del active_lobbies[4][i]
                    i += -1
                i += 1
            print(active_lobbies)
            message = "Delete lobby"
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )
            for i in range(len(active_lobbies[0])):
                message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i] + "/"\
                          + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i]
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
        message = message.split(sep="/")
        if len(message) > 1:
            if message[0] == "Join lobby":
                for i in range(len(active_lobbies[0])):
                    if active_lobbies[0][i] == message[1]:
                        active_lobbies[1][i] = self.name
                message = "Delete lobby"
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i] + "/" \
                              + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i]
                    await self.channel_layer.group_send(
                        self.room_group_name, {"type": "chat.message", "message": message}
                    )
            if message[0] == "Leave lobby":
                for i in range(len(active_lobbies[0])):
                    if active_lobbies[0][i] == message[1]:
                        active_lobbies[1][i] = ""
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
                game_num = -1
                for i in range(len(active_lobbies[0])):
                    if active_lobbies[0][i] == self.name:
                        first_name = active_lobbies[0][i]
                        second_name = active_lobbies[1][i]
                        game_num = i
                apoka = False
                if active_lobbies[3][game_num] == "Apoka":
                    apoka = True
                sector = active_lobbies[4][game_num]
                game_id = self.create_game(first_name, second_name, game_id, apoka, sector=sector)
                if active_lobbies[2][game_num] == "Public":
                    current_time = datetime.datetime.now()
                    time_change = datetime.timedelta(minutes=1440)
                    end_time = current_time + time_change
                    spectator_games.append((first_name, second_name, game_id, end_time))
                    print("End game time:")
                    print(end_time)
                message = "Move to game/" + game_id + "/" + first_name + "/" + second_name
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                i = 0
                while i < len(active_lobbies[0]):
                    if active_lobbies[0][i] == self.name:
                        del active_lobbies[0][i]
                        del active_lobbies[1][i]
                        del active_lobbies[2][i]
                        del active_lobbies[3][i]
                        del active_lobbies[4][i]
                        i += -1
                    i += 1
                for i in range(len(active_lobbies[0])):
                    message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i] + "/" \
                              + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i]
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

    def create_game(self, name_1, name_2, game_id, apoka, sector="Traxis"):
        global active_games
        global card_array
        global planet_array
        global cards_dict
        global apoka_errata_cards_array
        for i in range(len(active_games)):
            if active_games[i].game_id == game_id:
                new_game_id = game_id + random.choice('0123456789ABCDEF')
                return self.create_game(name_1, name_2, new_game_id, apoka, sector=sector)
        card_errata = []
        if apoka:
            card_errata = apoka_errata_cards_array
        active_games.append(GameClass.Game(game_id, name_1, name_2, card_array, planet_array, cards_dict,
                                           apoka, card_errata, sector=sector))
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
            await self.receive_game_update(self.name + " joined the lobby")
        condition_games.notify_all()
        condition_games.release()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.receive_game_update(self.name + " left the lobby")

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
                try:
                    await active_games[current_game_id].update_game_event(self.name, message[1:])
                except:
                    try:
                        with open("errorslog.txt", "a") as f:
                            f.write(traceback.format_exc())
                    except:
                        pass
                    await self.receive_game_update(
                        "An error has occurred on the server side. Your game may become unstable or unplayable."
                    )
        if message[0] == "CHAT_MESSAGE" and len(message) > 1:
            del message[0]
            try:
                if message[0] == "" and len(message) > 1:
                    if message[1] != "loaddeck":
                        await self.receive_game_update(
                            self.name + " is using a command: " + "/".join(message)
                        )
                    if (message[1] == "loaddeck" or message[1] == "LOADDECK") and len(message) > 2:
                        deck_name = message[2]
                        print(deck_name)
                        path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + \
                            self.user.username + "/" + deck_name
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
                                            await active_games[i].p1.setup_player(deck_content,
                                                                                  active_games[i].planet_array)
                                    elif active_games[i].name_2 == self.name:
                                        print("Need to load player two's deck")
                                        if not active_games[i].p2.deck_loaded:
                                            await active_games[i].p2.setup_player(deck_content,
                                                                                  active_games[i].planet_array)
                    elif message[1] == "Error":
                        raise ValueError
                    elif message[1] == "force-quit-reactions":
                        await self.receive_game_update("FORCEFULLY QUITTING REACTIONS")
                        active_games[self.game_position].reset_reactions_data()
                        await active_games[self.game_position].send_info_box()
                    elif message[1] == "force-quit-effects":
                        await self.receive_game_update("FORCEFULLY QUITTING EFFECTS")
                        active_games[self.game_position].reset_effects_data()
                        await active_games[self.game_position].send_info_box()
                    elif message[1] == "force-quit-damage":
                        await self.receive_game_update("FORCEFULLY QUITTING DAMAGE")
                        active_games[self.game_position].reset_damage_data()
                        await active_games[self.game_position].send_info_box()
                    elif message[1] == "force-quit-action":
                        await self.receive_game_update("FORCEFULLY QUITTING ACTION")
                        active_games[self.game_position].reset_action_data()
                        active_games[self.game_position].action_cleanup()
                        await active_games[self.game_position].send_info_box()
                    elif message[1] == "force-quit-moves":
                        await self.receive_game_update("FORCEFULLY QUITTING MOVES")
                        active_games[self.game_position].queued_moves = []
                        if active_games[self.game_position].choice_context == "Interrupt Enemy Movement Effect?":
                            active_games[self.game_position].reset_choices_available()
                        await active_games[self.game_position].send_info_box()
                    elif message[1] == "debug-reactions":
                        sent_string = "Current Reaction Info: "
                        sent_string += active_games[self.game_position].name_1
                        sent_string += ": "
                        for i in range(len(active_games[self.game_position].reactions_needing_resolving)):
                            if active_games[self.game_position].player_who_resolves_reaction[i] \
                                    == active_games[self.game_position].name_1:
                                sent_string += active_games[self.game_position].reactions_needing_resolving[i]
                                sent_string += ", "
                        sent_string += ". "
                        sent_string += active_games[self.game_position].name_2
                        sent_string += ": "
                        for i in range(len(active_games[self.game_position].reactions_needing_resolving)):
                            if active_games[self.game_position].player_who_resolves_reaction[i] \
                                    == active_games[self.game_position].name_2:
                                sent_string += active_games[self.game_position].reactions_needing_resolving[i]
                                sent_string += ", "
                        sent_string += "."
                        await self.receive_game_update(
                            sent_string
                        )
                    elif message[1] == "debug-interrupts":
                        sent_string = "Current Interrupt Info: "
                        sent_string += active_games[self.game_position].name_1
                        sent_string += ": "
                        for i in range(len(active_games[self.game_position].interrupts_waiting_on_resolution)):
                            if active_games[self.game_position].player_resolving_interrupts[i] \
                                    == active_games[self.game_position].name_1:
                                sent_string += active_games[self.game_position].interrupts_waiting_on_resolution[i]
                                sent_string += ", "
                        sent_string += ". "
                        sent_string += active_games[self.game_position].name_2
                        sent_string += ": "
                        for i in range(len(active_games[self.game_position].interrupts_waiting_on_resolution)):
                            if active_games[self.game_position].player_resolving_interrupts[i] \
                                    == active_games[self.game_position].name_2:
                                sent_string += active_games[self.game_position].interrupts_waiting_on_resolution[i]
                                sent_string += ", "
                        sent_string += "."
                        await self.receive_game_update(
                            sent_string
                        )
                    elif not active_games[self.game_position].safety_check():
                        await self.receive_game_update(
                            "Command prevented; game is in an unsafe state."
                        )
                    elif message[1] == "shuffle-deck" and len(message) == 3:
                        if message[2] == "1":
                            active_games[self.game_position].p1.shuffle_deck()
                            await active_games[self.game_position].send_decks()
                        elif message[2] == "2":
                            active_games[self.game_position].p2.shuffle_deck()
                            await active_games[self.game_position].send_decks()
                    elif message[1] == "rearrange-deck" and len(message) == 4:
                        try:
                            print("got here")
                            if not active_games[self.game_position].rearranging_deck:
                                print("not rearranging")
                                amount = int(message[3])
                                if message[2] == "1":
                                    if amount > 0:
                                        active_games[self.game_position].rearranging_deck = True
                                        active_games[self.game_position].name_player_rearranging_deck = \
                                            active_games[self.game_position].name_1
                                        active_games[self.game_position].deck_part_being_rearranged = \
                                            active_games[self.game_position].p1.deck[:amount]
                                        active_games[self.game_position].deck_part_being_rearranged.append("FINISH")
                                        active_games[self.game_position].number_cards_to_rearrange = amount
                                        await active_games[self.game_position].send_search()
                                        await active_games[self.game_position].send_info_box()
                                elif message[2] == "2":
                                    if amount > 0:
                                        active_games[self.game_position].rearranging_deck = True
                                        active_games[self.game_position].name_player_rearranging_deck = \
                                            active_games[self.game_position].name_2
                                        active_games[self.game_position].deck_part_being_rearranged = \
                                            active_games[self.game_position].p2.deck[:amount]
                                        active_games[self.game_position].deck_part_being_rearranged.append("FINISH")
                                        active_games[self.game_position].number_cards_to_rearrange = amount
                                        await active_games[self.game_position].send_search()
                                        await active_games[self.game_position].send_info_box()
                        except Exception as e:
                            print(e)
                    elif message[1] == "stop-rearrange-deck":
                        active_games[self.game_position].stop_rearranging_deck()
                        await active_games[self.game_position].send_search()
                        await active_games[self.game_position].send_info_box()
                    elif message[1] == "cards-deck" and len(message) == 3:
                        if message[2] == "1":
                            amount = len(active_games[self.game_position].p1.deck)
                            await self.receive_game_update(
                                "Num cards in P1's deck: " + str(amount)
                            )
                        elif message[2] == "2":
                            amount = len(active_games[self.game_position].p2.deck)
                            await self.receive_game_update(
                                "Num cards in P2's deck: " + str(amount)
                            )
                    elif message[1] == "show-discard" and len(message) == 3:
                        if message[2] == "1":
                            discard = active_games[self.game_position].p1.discard
                            new_message = ", ".join(discard)
                            await self.receive_game_update(
                                "Current discard of P1 is: " + new_message
                            )
                        elif message[2] == "2":
                            discard = active_games[self.game_position].p2.discard
                            new_message = ", ".join(discard)
                            await self.receive_game_update(
                                "Current discard of P2 is: " + new_message
                            )
                    elif message[1] == "set-resources" and len(message) == 4:
                        player_num = message[2]
                        resources = int(message[3])
                        if player_num == "1":
                            active_games[self.game_position].p1.resources = resources
                            await active_games[self.game_position].p1.send_resources()
                        elif player_num == "2":
                            active_games[self.game_position].p2.resources = resources
                            await active_games[self.game_position].p2.send_resources()
                    elif message[1] == "addcard" and len(message) > 3:
                        card_name = message[3]
                        card = FindCard.find_card(card_name, active_games[self.game_position].card_array,
                                                  active_games[self.game_position].cards_dict,
                                                  active_games[self.game_position].apoka_errata_cards,
                                                  active_games[self.game_position].cards_that_have_errata)
                        if card.get_shields() != -1:
                            if message[2] == "1":
                                active_games[self.game_position].p1.cards.append(card.get_name())
                                await active_games[self.game_position].p1.send_hand()
                            elif message[2] == "2":
                                active_games[self.game_position].p2.cards.append(card.get_name())
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
                            await active_games[self.game_position].send_decks()
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
                            await active_games[self.game_position].send_decks()
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
                    elif message[1] == "fully-remove" and len(message) > 3:
                        hand_pos = int(message[3])
                        if message[2] == "1":
                            del active_games[self.game_position].p1.cards_removed_from_game[hand_pos]
                            del active_games[self.game_position].p1.cards_removed_from_game_hidden[hand_pos]
                            await active_games[self.game_position].p1.send_removed_cards()
                        elif message[2] == "2":
                            del active_games[self.game_position].p2.cards_removed_from_game[hand_pos]
                            del active_games[self.game_position].p2.cards_removed_from_game_hidden[hand_pos]
                            await active_games[self.game_position].p2.send_removed_cards()
                    elif message[1] == "remove-discard" and len(message) > 3:
                        hand_pos = int(message[3])
                        if message[2] == "1":
                            card_name = active_games[self.game_position].p1.discard[hand_pos]
                            active_games[self.game_position].p1.remove_card_from_game(card_name)
                            del active_games[self.game_position].p1.discard[hand_pos]
                            await active_games[self.game_position].p1.send_discard()
                            await active_games[self.game_position].p1.send_removed_cards()
                        elif message[2] == "2":
                            card_name = active_games[self.game_position].p2.discard[hand_pos]
                            active_games[self.game_position].p2.remove_card_from_game(card_name)
                            del active_games[self.game_position].p2.discard[hand_pos]
                            await active_games[self.game_position].p2.send_discard()
                            await active_games[self.game_position].p2.send_removed_cards()
                    elif message[1] == "remove-hand" and len(message) > 3:
                        hand_pos = int(message[3])
                        if message[2] == "1":
                            card_name = active_games[self.game_position].p1.cards[hand_pos]
                            active_games[self.game_position].p1.remove_card_from_game(card_name)
                            del active_games[self.game_position].p1.cards[hand_pos]
                            await active_games[self.game_position].p1.send_hand()
                            await active_games[self.game_position].p1.send_removed_cards()
                        elif message[2] == "2":
                            card_name = active_games[self.game_position].p2.cards[hand_pos]
                            active_games[self.game_position].p2.remove_card_from_game(card_name)
                            del active_games[self.game_position].p2.cards[hand_pos]
                            await active_games[self.game_position].p2.send_hand()
                            await active_games[self.game_position].p2.send_removed_cards()
                    elif message[1] == "clear-reticle" and len(message) > 3:
                        num_player = message[2]
                        planet_pos = int(message[3])
                        unit_pos = int(message[4])
                        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
                        if message[3] == "-2":
                            unit_position = ["HQ", message[2], message[4]]
                        if active_games[self.game_position].validate_received_game_string(unit_position):
                            try:
                                if num_player == "1":
                                    active_games[self.game_position].p1.reset_aiming_reticle_in_play(
                                        planet_pos, unit_pos)
                                    await active_games[self.game_position].p1.send_units_at_planet(planet_pos)
                                elif unit_position[1] == "2":
                                    active_games[self.game_position].p2.reset_aiming_reticle_in_play(
                                        planet_pos, unit_pos)
                                    await active_games[self.game_position].p2.send_units_at_planet(planet_pos)
                            except:
                                await self.channel_layer.group_send(
                                    self.room_group_name, {"type": "chat.message", "message": "server: "
                                                                                              "Incorrect clear usage"}
                                )
                    elif message[1] == "infest-planet" and len(message) > 2:
                        planet_pos = int(message[2])
                        active_games[self.game_position].infested_planets[planet_pos] = True
                        await active_games[self.game_position].send_planet_array()
                    elif message[1] == "clear-infestation" and len(message) > 2:
                        planet_pos = int(message[2])
                        active_games[self.game_position].infested_planets[planet_pos] = False
                        await active_games[self.game_position].send_planet_array()
                    elif message[1] == "ready-card" and len(message) > 3:
                        num_player = message[2]
                        planet_pos = int(message[3])
                        unit_pos = int(message[4])
                        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
                        if message[3] == "-2":
                            unit_position = ["HQ", message[2], message[4]]
                        if active_games[self.game_position].validate_received_game_string(unit_position):
                            try:
                                if num_player == "1":
                                    active_games[self.game_position].p1.ready_given_pos(planet_pos, unit_pos)
                                    await active_games[self.game_position].p1.send_units_at_planet(planet_pos)
                                elif unit_position[1] == "2":
                                    active_games[self.game_position].p2.ready_given_pos(planet_pos, unit_pos)
                                    await active_games[self.game_position].p2.send_units_at_planet(planet_pos)
                            except:
                                await self.channel_layer.group_send(
                                    self.room_group_name, {"type": "chat.message", "message": "server: "
                                                                                              "Incorrect ready usage"}
                                )
                    elif message[1] == "exhaust-card" and len(message) > 3:
                        num_player = message[2]
                        planet_pos = int(message[3])
                        unit_pos = int(message[4])
                        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
                        if message[3] == "-2":
                            unit_position = ["HQ", message[2], message[4]]
                        if active_games[self.game_position].validate_received_game_string(unit_position):
                            try:
                                if num_player == "1":
                                    active_games[self.game_position].p1.exhaust_given_pos(planet_pos, unit_pos)
                                    await active_games[self.game_position].p1.send_units_at_planet(planet_pos)
                                elif unit_position[1] == "2":
                                    active_games[self.game_position].p2.exhaust_given_pos(planet_pos, unit_pos)
                                    await active_games[self.game_position].p2.send_units_at_planet(planet_pos)
                            except:
                                await self.channel_layer.group_send(
                                    self.room_group_name, {"type": "chat.message", "message": "server: "
                                                                                              "Incorrect exhaust usage"}
                                )
                    elif message[1] == "move-unit" and len(message) > 4:
                        num_player = message[2]
                        planet_pos = int(message[3])
                        unit_pos = int(message[4])
                        destination = int(message[5])
                        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
                        if message[3] == "-2":
                            unit_position = ["HQ", message[2], message[4]]
                        if active_games[self.game_position].validate_received_game_string(unit_position):
                            try:
                                if (active_games[self.game_position].planets_in_play_array[destination]
                                        and 0 <= destination <= 6) or destination == -2:
                                    if num_player == "1":
                                        if active_games[self.game_position].p1.check_is_unit_at_pos(
                                                planet_pos, unit_pos):
                                            if destination == -2:
                                                active_games[self.game_position].p1.move_unit_at_planet_to_hq(
                                                    planet_pos, unit_pos)
                                            else:
                                                active_games[self.game_position].p1.move_unit_to_planet(
                                                    planet_pos, unit_pos, destination)
                                            await active_games[self.game_position].p1.send_units_at_planet(planet_pos)
                                            await active_games[self.game_position].p1.send_units_at_planet(destination)
                                    elif unit_position[1] == "2":
                                        if active_games[self.game_position].p2.check_is_unit_at_pos(
                                                planet_pos, unit_pos):
                                            if destination == -2:
                                                active_games[self.game_position].p2.move_unit_at_planet_to_hq(
                                                    planet_pos, unit_pos)
                                            else:
                                                active_games[self.game_position].p2.move_unit_to_planet(
                                                    planet_pos, unit_pos, destination)
                                            await active_games[self.game_position].p2.send_units_at_planet(planet_pos)
                                            await active_games[self.game_position].p2.send_units_at_planet(destination)
                            except:
                                await self.channel_layer.group_send(
                                    self.room_group_name, {"type": "chat.message",
                                                           "message": "server: Incorrect set-faith usage"}
                                )
                    elif message[1] == "set-faith" and len(message) > 4:
                        num_player = message[2]
                        planet_pos = int(message[3])
                        unit_pos = int(message[4])
                        faith = int(message[5])
                        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
                        if message[3] == "-2":
                            unit_position = ["HQ", message[2], message[4]]
                        if active_games[self.game_position].validate_received_game_string(unit_position):
                            try:
                                if num_player == "1":
                                    active_games[self.game_position].p1.set_faith_given_pos(planet_pos, unit_pos, faith)
                                    await active_games[self.game_position].p1.send_units_at_planet(planet_pos)
                                elif unit_position[1] == "2":
                                    active_games[self.game_position].p2.set_faith_given_pos(planet_pos, unit_pos, faith)
                                    await active_games[self.game_position].p2.send_units_at_planet(planet_pos)
                            except:
                                await self.channel_layer.group_send(
                                    self.room_group_name, {"type": "chat.message",
                                                           "message": "server: Incorrect set-faith usage"}
                                )
                    elif message[1] == "set-damage" and len(message) > 4:
                        num_player = message[2]
                        planet_pos = int(message[3])
                        unit_pos = int(message[4])
                        damage = int(message[5])
                        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
                        if message[3] == "-2":
                            unit_position = ["HQ", message[2], message[4]]
                        if active_games[self.game_position].validate_received_game_string(unit_position):
                            try:
                                if num_player == "1":
                                    active_games[self.game_position].p1.set_damage_given_pos(
                                        planet_pos, unit_pos, damage)
                                    await active_games[self.game_position].p1.send_units_at_planet(planet_pos)
                                elif unit_position[1] == "2":
                                    active_games[self.game_position].p2.set_damage_given_pos(
                                        planet_pos, unit_pos, damage)
                                    await active_games[self.game_position].p2.send_units_at_planet(planet_pos)
                            except:
                                await self.channel_layer.group_send(
                                    self.room_group_name, {"type": "chat.message",
                                                           "message": "server: Incorrect set-damage usage"}
                                )
                    elif message[1] == "assign-damage" and len(message) > 4:
                        num_player = message[2]
                        planet_pos = int(message[3])
                        unit_pos = int(message[4])
                        damage = int(message[5])
                        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
                        if message[3] == "-2":
                            unit_position = ["HQ", message[2], message[4]]
                        if active_games[self.game_position].validate_received_game_string(unit_position):
                            try:
                                if num_player == "1":
                                    if active_games[self.game_position].p1.check_is_unit_at_pos(
                                            planet_pos, unit_pos):
                                        active_games[self.game_position].p1.assign_damage_to_pos(
                                            planet_pos, unit_pos, damage, by_enemy_unit=False)
                                        await active_games[self.game_position].p1.send_units_at_planet(planet_pos)
                                elif unit_position[1] == "2":
                                    if active_games[self.game_position].p2.check_is_unit_at_pos(
                                            planet_pos, unit_pos):
                                        active_games[self.game_position].p2.assign_damage_to_pos(
                                            planet_pos, unit_pos, damage, by_enemy_unit=False)
                                        await active_games[self.game_position].p2.send_units_at_planet(planet_pos)
                            except:
                                await self.channel_layer.group_send(
                                    self.room_group_name, {"type": "chat.message",
                                                           "message": "server: Incorrect set-damage usage"}
                                )
                else:
                    message = self.name + ": " + "/".join(message)
                    print("receive:", message)
                    chat_messages[0].append(self.room_name)
                    chat_messages[1].append(message)
                    print(chat_messages)

                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name, {"type": "chat.message", "message": message}
                    )
            except:
                try:
                    with open("errorslog.txt", "a") as f:
                        f.write(traceback.format_exc())
                except:
                    pass
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": "server: "
                                                                              "Something went wrong during command"}
                )
        condition_games.notify_all()
        condition_games.release()
