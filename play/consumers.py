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
import copy
from django.contrib.auth.models import User


ban_list_apoka = [
    "Bonesinger Choir", "Squiggoth Brute", "Corrupted Teleportarium", "Gun Drones", "Archon's Palace",
    "Land Speeder Vengeance", "Sowing Chaos", "Smasha Gun Battery", "The Prince's Might", "Purveyor of Hubris", "Doom",
    "Exterminatus", "Mind Shackle Scarab", "Crypt of Saint Camila", "Warp Storm"
]
card_array = Initfunctions.init_player_cards()
ffg_only_cards_list = Initfunctions.init_ffg_only_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()
blackstone_errata_cards_array = Initfunctions.init_blackstone_errata_cards()

active_lobbies = [[], [], [], [], [], [], [], [], []]
spectator_games = []  # Format: (p_one_name, p_two_name, game_id, end_time)
active_games = []
players_in_lobby = []

condition_lobby = threading.Condition()

condition_games = threading.Condition()


def get_users():
    all_users = User.objects.values()
    usernames = []
    for i in range(len(all_users)):
        usernames.append((all_users[i]['username']))
    with open(os.getcwd() + "/users_list.txt", "w") as user_file:
        user_file.write("\n".join(usernames))


get_users()


def get_lobbies():
    return active_lobbies, spectator_games


def get_active_games():
    return active_games


def create_bot_game(name_bot_1, name_bot_2, game_id, errata="No Errata", sector="Traxis Sector", deck_1="", deck_2=""):
    global spectator_games
    game_id = create_game(name_bot_1, name_bot_2, game_id, errata, sector=sector, deck_1=deck_1, deck_2=deck_2, bots_present=True)
    current_time = datetime.datetime.now()
    time_change = datetime.timedelta(minutes=14400)
    end_time = current_time + time_change
    spectator_games.append((name_bot_1, name_bot_2, game_id, end_time))
    return game_id


def create_game(name_1, name_2, game_id, errata, sector="Traxis", deck_1="", deck_2="", bots_present=False):
    global active_games
    global card_array
    global planet_array
    global cards_dict
    global apoka_errata_cards_array
    for i in range(len(active_games)):
        if active_games[i].game_id == game_id:
            new_game_id = game_id + random.choice('0123456789ABCDEF')
            return create_game(name_1, name_2, new_game_id, errata, sector=sector, deck_1=deck_1, deck_2=deck_2,
                               bots_present=bots_present)
    card_errata = []
    if errata == "Apoka":
        card_errata = apoka_errata_cards_array
    elif errata == "Blackstone":
        card_errata = blackstone_errata_cards_array
    active_games.append(GameClass.Game(game_id, name_1, name_2, card_array, planet_array, cards_dict,
                                       errata, card_errata, sector=sector, deck_1=deck_1, deck_2=deck_2,
                                       bot_is_present=bots_present))
    return game_id


def check_legality(deck_list, legality):
    deck_list = list(filter(("----------------------------------------------------------------------").__ne__, deck_list))
    deck_list = list(filter(None, deck_list))
    warlord_name = deck_list[1]
    if legality == "FFG":
        if warlord_name not in ffg_only_cards_list:
            return False
        print(deck_list[3])
        if deck_list[3] != "Signature Squad":
            return False
        for i in range(3, len(deck_list)):
            if deck_list[i] not in ["Signature Squad", "Army", "Support", "Event", "Attachment", "Synapse", "Planet"]:
                card_name = deck_list[i][3:]
                if card_name not in ffg_only_cards_list:
                    print(card_name)
                    return False
    elif legality == "Apoka":
        start_index = 3
        if deck_list[start_index] != "Signature Squad":
            start_index = 4
        for i in range(start_index, len(deck_list)):
            if deck_list[i] not in ["Signature Squad", "Army", "Support", "Event", "Attachment", "Synapse", "Planet"]:
                card_name = deck_list[i][3:]
                if card_name in ban_list_apoka:
                    print(card_name)
                    return False
    return True


def convert_name_to_img_src(card_name):
    card_name = card_name.replace("\"", "")
    card_name = card_name.replace(" ", "_")
    card_name = card_name.replace(":", "")
    card_name = card_name.replace("'idden_Base", "idden_Base")
    return card_name


def get_decks_user(username, start_index, end_index, required_faction="", legality=""):
    if not username:
        return []
    decks_stored = []
    path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + username + "/"
    if os.path.isdir(path_to_player_decks):
        for deck_name in os.listdir(path_to_player_decks):
            content_file = path_to_player_decks + deck_name
            with open(content_file, "r") as f:
                content = f.read()
                split_content = content.split(sep="\n")
                warlord_name = split_content[2]
                faction = split_content[3]
                faction = faction.split(sep=" (")[0]
                if not required_faction or faction == required_faction:
                    if legality == "" or legality == "All":
                        decks_stored.append((deck_name, convert_name_to_img_src(warlord_name), faction))
                    else:
                        if check_legality(split_content, legality):
                            decks_stored.append((deck_name, convert_name_to_img_src(warlord_name), faction))
    decks_stored = sorted(decks_stored, key=lambda x: x[0])
    end_index = min(end_index, len(decks_stored))
    start_index = min(start_index, len(decks_stored))
    decks_stored = decks_stored[start_index: end_index]
    return decks_stored


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global active_lobbies
        global condition_lobby
        global spectator_games
        global players_in_lobby
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
                      + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i] +\
                      "/" + active_lobbies[7][i] + "/" + active_lobbies[8][i]
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
        decks_user = get_decks_user(self.user.username, 0, 5)
        for i in range(len(decks_user)):
            deck_name = decks_user[i][0]
            warlord_name = decks_user[i][1]
            message = "Send Deck/" + self.user.username + "/" + deck_name + "/" + warlord_name + "/"
            await self.chat_message({"type": "chat.message", "message": message})
        user_name = self.user.username
        if user_name == "":
            user_name = "Anonymous"
        if user_name not in players_in_lobby:
            players_in_lobby.append(user_name)
        message = "players_in_lobby/" + "|".join(players_in_lobby)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )
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
        if split_message[0] == "Select Deck":
            for i in range(len(active_lobbies[0])):
                if active_lobbies[0][i] == self.name:
                    active_lobbies[5][i] = split_message[1]
                if active_lobbies[1][i] == self.name:
                    active_lobbies[6][i] = split_message[1]
        if split_message[0] == "Load More":
            value = int(split_message[1])
            required_faction = split_message[2]
            legality = split_message[3]
            decks_user = get_decks_user(self.user.username, value, value + 5, required_faction, legality)
            for i in range(len(decks_user)):
                deck_name = decks_user[i][0]
                warlord_name = decks_user[i][1]
                message = "Send Deck/" + self.user.username + "/" + deck_name + "/" + warlord_name + "/"
                await self.chat_message({"type": "chat.message", "message": message})
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
            if split_message[2] == "None":
                active_lobbies[3].append("No Errata")
            elif split_message[2] == "Apoka":
                active_lobbies[3].append("Apoka")
            else:
                active_lobbies[3].append("Blackstone")
            active_lobbies[4].append(split_message[3])
            active_lobbies[5].append(split_message[4])
            active_lobbies[6].append("")
            active_lobbies[7].append(datetime.datetime.today().strftime("%I:%M%p, %B %d, %Y"))
            active_lobbies[8].append(split_message[5])
            print(active_lobbies)
            le = len(active_lobbies[0]) - 1
            split_message[0] += "/" + active_lobbies[0][le] + "/" + active_lobbies[1][le] + \
                                "/" + active_lobbies[2][le] + "/" + active_lobbies[3][le] + \
                                "/" + active_lobbies[4][le] + "/" + active_lobbies[7][le] + \
                                "/" + active_lobbies[8][le]
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
                    del active_lobbies[5][i]
                    del active_lobbies[6][i]
                    del active_lobbies[7][i]
                    del active_lobbies[8][i]
                    i += -1
                i += 1
            print(active_lobbies)
            message = "Delete lobby"
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )
            for i in range(len(active_lobbies[0])):
                message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i] + "/"\
                          + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i] + \
                          "/" + active_lobbies[7][i]
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
        message = message.split(sep="/")
        if len(message) > 1:
            if message[0] == "Join lobby":
                for i in range(len(active_lobbies[0])):
                    if active_lobbies[0][i] == message[1]:
                        active_lobbies[1][i] = self.name
                        active_lobbies[6][i] = split_message[2]
                message = "Delete lobby"
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i] + "/" \
                              + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i] + \
                              "/" + active_lobbies[7][i] + "/" + active_lobbies[8][i]
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
                errata = active_lobbies[3][game_num]
                sector = active_lobbies[4][game_num]
                deck_1 = active_lobbies[5][game_num]
                deck_2 = active_lobbies[6][game_num]
                first_player = first_name
                second_player = second_name
                decider_first_player = active_lobbies[8][game_num]
                if decider_first_player == "Random":
                    first_player = random.choice([first_name, second_name])
                    if first_player == first_name:
                        second_player = second_name
                    else:
                        second_player = first_name
                        temp = deck_1
                        deck_1 = deck_2
                        deck_2 = temp
                elif decider_first_player == "Yourself":
                    pass
                else:
                    first_player = second_name
                    second_player = first_name
                    temp = deck_1
                    deck_1 = deck_2
                    deck_2 = temp
                game_id = create_game(first_player, second_player, game_id, errata, sector=sector,
                                      deck_1=deck_1, deck_2=deck_2)
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
                        del active_lobbies[5][i]
                        del active_lobbies[6][i]
                        del active_lobbies[7][i]
                        del active_lobbies[8][i]
                        i += -1
                    i += 1
                message = "Delete lobby"
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = "Create lobby/" + active_lobbies[0][i] + "/" + active_lobbies[1][i] + "/" \
                              + active_lobbies[2][i] + "/" + active_lobbies[3][i] + "/" + active_lobbies[4][i] + \
                              "/" + active_lobbies[7][i] + "/" + active_lobbies[8][i]
                    await self.channel_layer.group_send(
                        self.room_group_name, {"type": "chat.message", "message": message}
                    )
                message = "Delete spec"
                print("CURRENT SPEC")
                print(spectator_games)
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(spectator_games)):
                    message = "Create spec/" + spectator_games[i][0] + "/" + spectator_games[i][1] + "/" + \
                              spectator_games[i][2]
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
        global players_in_lobby
        try:
            user_name = self.user.username
            if self.user.username == "":
                user_name = "Anonymous"
            if user_name in players_in_lobby:
                players_in_lobby.remove(user_name)
        except Exception as e:
            print(e)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        message = "players_in_lobby/" + "|".join(players_in_lobby)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )


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
        if room_already_exists:
            for i in range(len(active_games[game_id_if_exists].chat_messages)):
                await self.send(text_data=json.dumps({"message": active_games[game_id_if_exists].chat_messages[i]}))
        if room_already_exists:
            await active_games[game_id_if_exists].joined_requests_graphics(self.name)
            await self.receive_game_update(self.name + " joined the lobby")
            if self.name != "Anonymous":
                pref_path = "user_preferences_storage/" + self.name + ".txt"
                if os.path.exists(pref_path):
                    with open(pref_path, "r") as f:
                        contents = f.read()
                        content_split = contents.split(sep="\n")
                        if len(content_split) > 6:
                            choices_box_h = content_split[3]
                            choices_box_v = content_split[4]
                            info_box_h = content_split[5]
                            info_box_v = content_split[6]
                            await self.receive_game_update(
                                "GAME_INFO/SET_BOX_LOCATIONS/" + self.name + "/" + choices_box_h + "/" + choices_box_v + "/" +
                                info_box_h + "/" + info_box_v
                            )
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

    async def broadcast_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

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
        print(text_data)
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
                    game_relevant_string = self.name + "|||" + "/".join(message[1:])
                    active_games[current_game_id].game_events_as_mono_string += game_relevant_string + "\n"
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
        elif message[0] == "AUTOMATED_CHOICE" and len(message) > 1:
            current_game_id = -1
            for i in range(len(active_games)):
                if active_games[i].game_id == self.room_name:
                    print("Found room")
                    current_game_id = i
            if current_game_id != -1:
                try:
                    game_relevant_string = message[1] + "|||" + "/".join(message[2:])
                    active_games[current_game_id].game_events_as_mono_string += game_relevant_string + "\n"
                    await active_games[current_game_id].update_game_event(message[1], message[2:])
                except:
                    try:
                        with open("errorslog.txt", "a") as f:
                            f.write(traceback.format_exc())
                    except:
                        pass
                    await self.receive_game_update(
                        "An error has occurred on the server side. Your game may become unstable or unplayable."
                    )
        elif message[0] == "AUTOMATED_SPECIAL_ACTION_CHOICE" and len(message) > 1:
            current_game_id = -1
            for i in range(len(active_games)):
                if active_games[i].game_id == self.room_name:
                    print("Found room")
                    current_game_id = i
            if current_game_id != -1:
                try:
                    game_relevant_string = message[1] + "|||SpecialAction/" + "/".join(message[2:])
                    active_games[current_game_id].game_events_as_mono_string += game_relevant_string + "\n"
                    if message[2] == "pass-P1":
                        if message[1] == active_games[current_game_id].name_1:
                            active_games[current_game_id].automated_1_has_passed_action = True
                        elif message[1] == active_games[current_game_id].name_2:
                            active_games[current_game_id].automated_2_has_passed_action = True
                        await active_games[current_game_id].update_automated_info()
                        await active_games[current_game_id].send_automated_info()
                        print("automated player special action states")
                        print(active_games[current_game_id].automated_1_has_passed_action)
                        print(active_games[current_game_id].automated_2_has_passed_action)
                    else:
                        await active_games[current_game_id].update_game_event(message[1], ["action-button"], same_thread=True)
                        active_games[current_game_id].automated_1_has_passed_action = False
                        active_games[current_game_id].automated_2_has_passed_action = False
                        await active_games[current_game_id].update_game_event(message[1], message[2:])
                except:
                    try:
                        with open("errorslog.txt", "a") as f:
                            f.write(traceback.format_exc())
                    except:
                        pass
                    await self.receive_game_update(
                        "An error has occurred on the server side. Your game may become unstable or unplayable."
                    )
        elif message[0] == "CHAT_MESSAGE" and len(message) > 1:
            del message[0]
            try:
                print(message)
                if len(message) == 2:
                    if message[0] == "" and message[1] == "reset-game" and active_games[self.game_position].bot_is_present:
                        game_id = active_games[self.game_position].game_id
                        player_one_name = active_games[self.game_position].name_1
                        player_two_name = active_games[self.game_position].name_2
                        card_array_game = active_games[self.game_position].card_array
                        cards_dict_game = active_games[self.game_position].cards_dict
                        planet_array_game = active_games[self.game_position].planet_cards_array
                        errata = "No Errata"
                        if active_games[self.game_position].apoka:
                            errata = "Apoka"
                        elif active_games[self.game_position].blackstone:
                            errata = "Blackstone"
                        apoka_errata_cards_game = active_games[self.game_position].apoka_errata_cards
                        game = GameClass.Game(game_id, player_one_name, player_two_name, card_array_game,
                                              planet_array_game, cards_dict_game, errata,
                                              apoka_errata_cards_game)
                        game.game_sockets.append(self)
                        game.bot_is_present = True
                        active_games[self.game_position] = game
                        await game.send_everything()
                    else:
                        await active_games[self.game_position].resolve_chat_message(self.name, message)
                elif len(message) == 3:
                    if message[0] == "" and message[1] == "Load-Game" and active_games[self.game_position].phase == "SETUP":
                        game_id = message[2]
                        cwd = os.getcwd()
                        stored_game_data_dir = os.path.join(cwd, "saved_games")
                        if not os.path.exists(stored_game_data_dir):
                            os.mkdir(stored_game_data_dir)
                        target_save_file = os.path.join(stored_game_data_dir, game_id) + ".txt"
                        if os.path.exists(target_save_file):
                            with open(target_save_file, "r") as f:
                                file_content = f.read()
                                position_start_p1_deck = file_content.find("-----\nDECK P1\n-----")
                                position_start_p2_deck = file_content.find("-----\nDECK P2\n-----")
                                position_game_details = file_content.find("-----GAME DETAILS-----")
                                position_p1_details = file_content.find("-----\nP1 DETAILS\n-----")
                                position_p2_details = file_content.find("-----\nP2 DETAILS\n-----")
                                replay_details = file_content.find("-----\nREPLAY DETAILS\n-----")
                                stored_p1_deck_text = file_content[position_start_p1_deck + len("-----\nDECK P1\n-----") + 1:position_start_p2_deck]
                                print(stored_p1_deck_text)
                                stored_p2_deck_text = file_content[position_start_p2_deck + len("-----\nDECK P1\n-----") + 1:position_game_details]
                                print(stored_p2_deck_text)
                                game_details_text = file_content[position_game_details:position_p1_details]
                                game_details_split = game_details_text.split(sep="\n")
                                errata = "No Errata"
                                sector = "Traxis"
                                for i in range(len(game_details_split)):
                                    if "ERRATA" in game_details_split[i] and "WINNER" not in game_details_split[i]:
                                        errata = game_details_split[i].split(sep="\t")[1].capitalize()
                                    if "SECTOR" in game_details_split[i] and "WINNER" not in game_details_split[i]:
                                        sector = game_details_split[i].split(sep="\t")[1]
                                if errata == "None":
                                    errata = "No Errata"
                                print(errata)
                                p1_details_text = file_content[position_p1_details:position_p2_details]
                                p1_details_split = p1_details_text.split(sep="\n")
                                p1_name = "Dummy"
                                for i in range(len(p1_details_split)):
                                    if "NAME" in p1_details_split[i]:
                                        p1_name = p1_details_split[i].split(sep="\t")[1]
                                p2_details_text = file_content[position_p2_details:replay_details]
                                p2_details_split = p2_details_text.split(sep="\n")
                                p2_name = "Dummy"
                                for i in range(len(p2_details_split)):
                                    if "NAME" in p2_details_split[i]:
                                        p2_name = p2_details_split[i].split(sep="\t")[1]
                                print(p1_name, p2_name)
                                replay_text = file_content[replay_details:]
                                replay_details_split = replay_text.split(sep="\n")
                                random_seed = 11037
                                move_details_started = False
                                moves_list = []
                                first_to_load_deck = ""
                                for i in range(len(replay_details_split)):
                                    if "RANDOM SEED" in replay_details_split[i] and "|" not in replay_details_split[i]:
                                        random_seed = int(replay_details_split[i].split(sep="\t")[1])
                                    if move_details_started:
                                        if replay_details_split[i]:
                                            moves_list.append(replay_details_split[i])
                                    if "MOVE DETAILS:" in replay_details_split[i]:
                                        move_details_started = True
                                        if not first_to_load_deck:
                                            if p1_name == replay_details_split[i + 1].split(sep="|||")[0]:
                                                first_to_load_deck = p1_name
                                            else:
                                                first_to_load_deck = p2_name
                                print(random_seed)
                                print(moves_list)
                                card_errata = []
                                if errata == "Apoka":
                                    card_errata = apoka_errata_cards_array
                                elif errata == "Blackstone":
                                    card_errata = blackstone_errata_cards_array
                                active_games[self.game_position] = GameClass.Game(
                                    self.room_name, p1_name, p2_name, card_array, planet_array, cards_dict, errata,
                                    card_errata, sector=sector, raw_deck_text_1=stored_p1_deck_text,
                                    raw_deck_text_2=stored_p2_deck_text, random_seed=random_seed,
                                    first_to_load=first_to_load_deck
                                )
                                active_games[self.game_position].game_sockets.append(self)
                                active_games[self.game_position].saved_moves = moves_list
                                active_games[self.game_position].saved_move_id = 0
                                await active_games[self.game_position].update_game_event("", [])
                        else:
                            await self.channel_layer.group_send(
                                self.room_group_name, {"type": "chat.message", "message": "Game does not exist"}
                            )
                    else:
                        await active_games[self.game_position].resolve_chat_message(self.name, message)
                else:
                    await active_games[self.game_position].resolve_chat_message(self.name, message)
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
        elif message[0] == "REARRANGE_HAND":
            current_game_id = -1
            for i in range(len(active_games)):
                if active_games[i].game_id == self.room_name:
                    print("Found room")
                    current_game_id = i
            if current_game_id != -1:
                if self.name == active_games[current_game_id].name_1 or self.name == active_games[current_game_id].name_2:
                    if active_games[current_game_id].safety_check():
                        if self.name == active_games[current_game_id].name_1:
                            active_games[current_game_id].p1.reorder_card_in_hand(int(message[1]), int(message[2]))
                            active_games[current_game_id].game_events_as_mono_string += self.name + "|||REARRANGE_HAND/" + message[1] + "/" + message[2] + "\n"
                            await active_games[current_game_id].p1.send_hand()
                        else:
                            active_games[current_game_id].p2.reorder_card_in_hand(int(message[1]), int(message[2]))
                            active_games[current_game_id].game_events_as_mono_string += self.name + "|||REARRANGE_HAND/" + message[1] + "/" + message[2] + "\n"
                            await active_games[current_game_id].p2.send_hand()
                    else:
                        await active_games[current_game_id].send_mistarget_message(
                            self.name, "Cannot Rearrange", "Rearranging your hand is not permitted right now. "
                                                           "Please wait for the current effect to resolve."
                        )
                        if self.name == active_games[current_game_id].name_1:
                            await active_games[current_game_id].p1.send_hand(force=True)
                        elif self.name == active_games[current_game_id].name_2:
                            await active_games[current_game_id].p2.send_hand(force=True)

        elif message[0] == "UPDATE_CHOICE_BOX_LOCATION" and len(message) == 3:
            if self.name != "Anonymous":
                pref_path = "user_preferences_storage/" + self.name + ".txt"
                if os.path.exists(pref_path):
                    with open(pref_path, "r") as f:
                        contents = f.read()
                        content_split = contents.split(sep="\n")
                        while len(content_split) < 7:
                            content_split.append("-1")
                        content_split[3] = message[1]
                        content_split[4] = message[2]
                        contents = "\n".join(content_split)
                    with open(pref_path, "w") as f:
                        f.write(contents)
        elif message[0] == "UPDATE_INFO_BOX_LOCATION" and len(message) == 3:
            if self.name != "Anonymous":
                pref_path = "user_preferences_storage/" + self.name + ".txt"
                if os.path.exists(pref_path):
                    with open(pref_path, "r") as f:
                        contents = f.read()
                        content_split = contents.split(sep="\n")
                        while len(content_split) < 7:
                            content_split.append("-1")
                        content_split[5] = message[1]
                        content_split[6] = message[2]
                        contents = "\n".join(content_split)
                    with open(pref_path, "w") as f:
                        f.write(contents)
        condition_games.notify_all()
        condition_games.release()
