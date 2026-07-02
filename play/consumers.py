import json
import random
import string
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from .gamecode import GameClass
import os
from .gamecode import Initfunctions
import threading
import traceback
import datetime
from django.contrib.auth.models import User
from django.db.utils import OperationalError, ProgrammingError
import update_settings
from . import turn_notifier


RUNTIME_STATE_PERSIST_ENABLED = False
ban_list_apoka = [
    "Bonesinger Choir", "Squiggoth Brute", "Corrupted Teleportarium", "Gun Drones", "Archon's Palace",
    "Land Speeder Vengeance", "Sowing Chaos", "Smasha Gun Battery", "The Prince's Might", "Purveyor of Hubris", "Doom",
    "Exterminatus", "Mind Shackle Scarab", "Crypt of Saint Camila", "Warpstorm"
]
card_array = Initfunctions.init_player_cards()
ffg_only_cards_list = Initfunctions.init_ffg_only_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]
planet_array = Initfunctions.init_planet_cards()
apoka_errata_cards_array = Initfunctions.init_apoka_errata_cards()
blackstone_errata_cards_array = Initfunctions.init_blackstone_errata_cards()

active_lobbies = [[], [], [], [], [], [], [], [], [], []]
spectator_games = []  # Format: (p_one_name, p_two_name, game_id, end_time)
active_games = []
players_in_lobby = []

condition_lobby = threading.Condition()

condition_games = threading.Condition()


def get_users():
    try:
        usernames = list(User.objects.values_list("username", flat=True))
    except (OperationalError, ProgrammingError):
        return
    with open(os.getcwd() + "/users_list.txt", "w") as user_file:
        user_file.write("\n".join(usernames))


get_users()

_runtime_state_lock = threading.RLock()
_runtime_state_loaded = False
_runtime_state_loading = False
_runtime_state_version = 1
_cleaned_play_room_groups = set()
_cleaned_play_room_groups_lock = threading.RLock()


def _maybe_clear_stale_play_room_group(channel_layer, room_group_name):
    if channel_layer is None or not room_group_name or not room_group_name.startswith("play_"):
        return
    if channel_layer.__class__.__name__ != "RedisChannelLayer":
        return
    with _cleaned_play_room_groups_lock:
        if room_group_name in _cleaned_play_room_groups:
            return
        _cleaned_play_room_groups.add(room_group_name)
    try:
        import redis
        redis_host = os.environ.get("CHANNEL_REDIS_HOST", "127.0.0.1")
        redis_port = int(os.environ.get("CHANNEL_REDIS_PORT", "6379"))
        redis_prefix = getattr(channel_layer, "prefix", "asgi")
        if isinstance(redis_prefix, bytes):
            redis_prefix = redis_prefix.decode("utf-8")
        redis_group_key = f"{redis_prefix}:group:{room_group_name}"
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            socket_connect_timeout=0.25,
            socket_timeout=0.25,
        )
        redis_client.delete(redis_group_key)
    except Exception:
        pass


def _write_runtime_error(trace_text):
    try:
        with open("errorslog.txt", "a") as f:
            f.write(trace_text)
    except Exception:
        pass


def _get_runtime_state_file_path():
    cwd = os.getcwd()
    stored_game_data_dir = os.path.join(cwd, "saved_games")
    if not os.path.exists(stored_game_data_dir):
        os.mkdir(stored_game_data_dir)
    return os.path.join(stored_game_data_dir, "active_games_state.json")


def _find_active_game_by_id(game_id):
    for i in range(len(active_games)):
        if active_games[i].game_id == game_id:
            return active_games[i]
    return None


def _game_is_finished(game):
    if game is None:
        return True
    if game.game_is_complete:
        return True
    try:
        if game.p1.is_the_winner or game.p2.is_the_winner:
            return True
    except Exception:
        pass
    return False


def _infer_first_to_load_from_moves(moves_as_mono_string, name_1, name_2):
    if not moves_as_mono_string:
        return name_1
    for line in moves_as_mono_string.splitlines():
        if "|||" not in line:
            continue
        name_user, move_details = line.split("|||", 1)
        if move_details.startswith("/loaddeck"):
            return name_user
        if "loaddeckbot" in move_details:
            split_move = move_details.split("/")
            if len(split_move) > 2:
                return split_move[2]
            return name_user
    return name_1 if name_1 else name_2


def _replay_game_events_from_mono_string(game, moves_as_mono_string):
    if not moves_as_mono_string:
        return
    moves_list = [line for line in moves_as_mono_string.splitlines() if line]
    for move_string in moves_list:
        if "|||" not in move_string:
            continue
        name_user, move_details = move_string.split(sep="|||", maxsplit=1)
        move_details_split = move_details.split(sep="/")
        if move_details.startswith("/"):
            if len(move_details_split) > 1 and move_details_split[1] == "savegame":
                continue
            async_to_sync(game.resolve_chat_message)(name_user, move_details_split)
        elif move_details_split[0] == "SpecialAction":
            if len(move_details_split) <= 1:
                continue
            if move_details_split[1] in ["pass-P1", "pass-P2"]:
                continue
            async_to_sync(game.update_game_event)(name_user, ["action-button"], same_thread=True)
            async_to_sync(game.update_game_event)(name_user, move_details_split[1:])
        elif move_details_split[0] == "REARRANGE_HAND":
            if len(move_details_split) < 3:
                continue
            if name_user == game.name_1:
                game.p1.reorder_card_in_hand(int(move_details_split[1]), int(move_details_split[2]))
            elif name_user == game.name_2:
                game.p2.reorder_card_in_hand(int(move_details_split[1]), int(move_details_split[2]))
        else:
            async_to_sync(game.update_game_event)(name_user, move_details_split)


def _serialize_current_runtime_state():
    serialized_games = []
    for i in range(len(active_games)):
        game = active_games[i]
        if _game_is_finished(game):
            continue
        errata = "No Errata"
        if game.apoka:
            errata = "Apoka"
        elif game.blackstone:
            errata = "Blackstone"
        deck_1_text = ""
        deck_2_text = ""
        try:
            deck_1_text = game.p1.deck_string
        except Exception:
            pass
        try:
            deck_2_text = game.p2.deck_string
        except Exception:
            pass
        game_events_as_mono_string = getattr(game, "game_events_as_mono_string", "")
        serialized_games.append({
            "game_id": game.game_id,
            "name_1": game.name_1,
            "name_2": game.name_2,
            "errata": errata,
            "sector": game.sector,
            "random_seed": game.random_seed,
            "deck_1_text": deck_1_text,
            "deck_2_text": deck_2_text,
            "first_to_load": _infer_first_to_load_from_moves(game_events_as_mono_string, game.name_1, game.name_2),
            "game_events_as_mono_string": game_events_as_mono_string,
            "bot_is_present": bool(game.bot_is_present),
        })
    serialized_spectators = []
    for i in range(len(spectator_games)):
        try:
            player_1, player_2, game_id, end_time = spectator_games[i]
            if hasattr(end_time, "isoformat"):
                end_time = end_time.isoformat()
            serialized_spectators.append({
                "player_1": player_1,
                "player_2": player_2,
                "game_id": game_id,
                "end_time": end_time,
            })
        except Exception:
            continue
    return {
        "version": _runtime_state_version,
        "saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "active_games": serialized_games,
        "spectator_games": serialized_spectators,
    }


def persist_runtime_state():
    global RUNTIME_STATE_PERSIST_ENABLED
    if RUNTIME_STATE_PERSIST_ENABLED:
        _ensure_runtime_state_loaded()
        _ensure_lobby_id_column()
        with _runtime_state_lock:
            try:
                runtime_state = _serialize_current_runtime_state()
                target_file = _get_runtime_state_file_path()
                temp_file = target_file + ".tmp"
                with open(temp_file, "w") as f:
                    json.dump(runtime_state, f)
                os.replace(temp_file, target_file)
            except Exception:
                _write_runtime_error(traceback.format_exc())


def _restore_runtime_state_from_disk():
    global active_games
    global spectator_games
    runtime_file = _get_runtime_state_file_path()
    if not os.path.exists(runtime_file):
        return
    try:
        with open(runtime_file, "r") as f:
            data = json.load(f)
    except Exception:
        _write_runtime_error(traceback.format_exc())
        return
    if not isinstance(data, dict):
        return
    restored_games = []
    restored_game_ids = set()
    serialized_games = data.get("active_games", [])
    if not isinstance(serialized_games, list):
        serialized_games = []
    for i in range(len(serialized_games)):
        game_data = serialized_games[i]
        if not isinstance(game_data, dict):
            continue
        game_id = str(game_data.get("game_id", "")).strip()
        name_1 = str(game_data.get("name_1", "")).strip()
        name_2 = str(game_data.get("name_2", "")).strip()
        if not game_id or not name_1 or not name_2:
            continue
        if game_id in restored_game_ids:
            continue
        errata = str(game_data.get("errata", "No Errata"))
        sector = str(game_data.get("sector", "Traxis"))
        random_seed = game_data.get("random_seed")
        deck_1_text = str(game_data.get("deck_1_text", ""))
        deck_2_text = str(game_data.get("deck_2_text", ""))
        first_to_load = str(game_data.get("first_to_load", ""))
        game_events_as_mono_string = str(game_data.get("game_events_as_mono_string", ""))
        if not first_to_load:
            first_to_load = _infer_first_to_load_from_moves(game_events_as_mono_string, name_1, name_2)
        card_errata = []
        banned_cards = []
        if errata == "Apoka":
            card_errata = apoka_errata_cards_array
            banned_cards = ban_list_apoka
        elif errata == "Blackstone":
            card_errata = blackstone_errata_cards_array
        try:
            game = GameClass.Game(
                game_id,
                name_1,
                name_2,
                card_array,
                planet_array,
                cards_dict,
                errata,
                card_errata,
                sector=sector,
                random_seed=random_seed,
                raw_deck_text_1=deck_1_text,
                raw_deck_text_2=deck_2_text,
                first_to_load=first_to_load,
                bot_is_present=bool(game_data.get("bot_is_present", False)),
                banned_cards=banned_cards
            )
            _replay_game_events_from_mono_string(game, game_events_as_mono_string)
            game.game_events_as_mono_string = game_events_as_mono_string
            if not _game_is_finished(game):
                restored_games.append(game)
                restored_game_ids.add(game_id)
        except Exception:
            _write_runtime_error(traceback.format_exc())
            continue
    active_games.clear()
    active_games.extend(restored_games)
    restored_spectator_games = []
    serialized_spectator_games = data.get("spectator_games", [])
    if not isinstance(serialized_spectator_games, list):
        serialized_spectator_games = []
    for i in range(len(serialized_spectator_games)):
        entry = serialized_spectator_games[i]
        if not isinstance(entry, dict):
            continue
        game_id = str(entry.get("game_id", "")).strip()
        if game_id not in restored_game_ids:
            continue
        end_time = entry.get("end_time")
        if isinstance(end_time, str):
            try:
                end_time = datetime.datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                if end_time.tzinfo is not None:
                    end_time = end_time.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            except Exception:
                end_time = datetime.datetime.now()
        if not isinstance(end_time, datetime.datetime):
            end_time = datetime.datetime.now()
        restored_spectator_games.append(
            (
                str(entry.get("player_1", "")),
                str(entry.get("player_2", "")),
                game_id,
                end_time
            )
        )
    spectator_games.clear()
    spectator_games.extend(restored_spectator_games)


def _ensure_runtime_state_loaded():
    global _runtime_state_loaded
    global _runtime_state_loading
    if _runtime_state_loaded:
        return
    if _runtime_state_loading:
        return
    _runtime_state_loading = True
    with _runtime_state_lock:
        try:
            if _runtime_state_loaded:
                return
            if active_games:
                _runtime_state_loaded = True
                return
            _restore_runtime_state_from_disk()
            _runtime_state_loaded = True
        except Exception:
            _write_runtime_error(traceback.format_exc())
        finally:
            _runtime_state_loading = False


def prune_spectator_games():
    global spectator_games
    _ensure_runtime_state_loaded()
    current_time = datetime.datetime.now()
    i = 0
    removed_game = False
    while i < len(spectator_games):
        remove_game = False
        if spectator_games[i][3] < current_time:
            remove_game = True
        else:
            game = _find_active_game_by_id(spectator_games[i][2])
            if _game_is_finished(game):
                remove_game = True
        if remove_game:
            del spectator_games[i]
            i = i - 1
            removed_game = True
        i = i + 1
    if removed_game:
        persist_runtime_state()


def get_lobbies():
    _ensure_runtime_state_loaded()
    _ensure_lobby_id_column()
    prune_spectator_games()
    return active_lobbies, spectator_games


def get_active_games():
    _ensure_runtime_state_loaded()
    return active_games


def _generate_unique_lobby_id():
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    known_ids = set()
    if len(active_lobbies) > 9:
        for i in range(len(active_lobbies[9])):
            lobby_id = str(active_lobbies[9][i]).strip()
            if lobby_id:
                known_ids.add(lobby_id)
    for i in range(len(active_games)):
        known_ids.add(active_games[i].game_id)
    while True:
        generated_id = ''.join(random.choice(characters) for _ in range(16))
        if generated_id not in known_ids:
            return generated_id


def _ensure_lobby_id_column():
    if len(active_lobbies) < 10:
        active_lobbies.append([])
    while len(active_lobbies[9]) < len(active_lobbies[0]):
        active_lobbies[9].append(_generate_unique_lobby_id())


def _build_lobby_create_message(index):
    _ensure_lobby_id_column()
    return "Create lobby/" + active_lobbies[0][index] + "/" + active_lobbies[1][index] + "/" + \
           active_lobbies[2][index] + "/" + active_lobbies[3][index] + "/" + active_lobbies[4][index] + "/" + \
           active_lobbies[7][index] + "/" + active_lobbies[8][index] + "/" + active_lobbies[9][index]


def _remove_lobby_at_index(index):
    for i in range(len(active_lobbies)):
        del active_lobbies[i][index]


def _find_lobby_index_by_identifier(identifier):
    _ensure_lobby_id_column()
    identifier = str(identifier).strip()
    if not identifier:
        return -1
    for i in range(len(active_lobbies[0])):
        if active_lobbies[9][i] == identifier:
            return i
        if active_lobbies[0][i] == identifier:
            return i
    return -1

def _serialize_lobby_row(index):
    _ensure_lobby_id_column()
    return {
        "host_player": active_lobbies[0][index],
        "guest_player": active_lobbies[1][index],
        "visibility": active_lobbies[2][index],
        "errata": active_lobbies[3][index],
        "sector": active_lobbies[4][index],
        "host_deck": active_lobbies[5][index],
        "guest_deck": active_lobbies[6][index],
        "created_at": active_lobbies[7][index],
        "first_player_decider": active_lobbies[8][index],
        "lobby_id": active_lobbies[9][index],
    }


def _broadcast_lobby_state_update():
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    messages = ["Delete lobby"]
    condition_lobby.acquire()
    try:
        _ensure_lobby_id_column()
        for i in range(len(active_lobbies[0])):
            messages.append(_build_lobby_create_message(i))
    finally:
        condition_lobby.release()
    try:
        for message in messages:
            async_to_sync(channel_layer.group_send)(
                "lobby", {"type": "chat.message", "message": message}
            )
    except Exception:
        _write_runtime_error(traceback.format_exc())


def join_lobby_for_player(host_player, guest_player, guest_deck="", lobby_id=""):
    _ensure_runtime_state_loaded()
    _ensure_lobby_id_column()
    host_player = str(host_player).strip()
    guest_player = str(guest_player).strip()
    guest_deck = str(guest_deck).strip()
    lobby_id = str(lobby_id).strip()
    if not host_player and not lobby_id:
        return {"status": "error", "error": "Missing required field: lobby_id (or host_player)", "http_status": 400}
    if not guest_player:
        return {"status": "error", "error": "Missing required field: guest_player", "http_status": 400}
    if host_player == guest_player:
        return {"status": "error", "error": "Host and guest players must be different", "http_status": 400}
    updated_lobby = None
    should_broadcast = False
    condition_lobby.acquire()
    try:
        target_lobby_index = -1
        if lobby_id:
            target_lobby_index = _find_lobby_index_by_identifier(lobby_id)
        if target_lobby_index == -1 and host_player:
            for i in range(len(active_lobbies[0])):
                if active_lobbies[0][i] == host_player:
                    target_lobby_index = i
                    break
        if target_lobby_index == -1:
            return {
                "status": "error",
                "error": "Lobby not found",
                "http_status": 404,
                "host_player": host_player,
                "lobby_id": lobby_id
            }
        if active_lobbies[2][target_lobby_index] == "Private":
            return {
                "status": "error",
                "error": "Lobby is private and cannot be joined through the public REST endpoint",
                "http_status": 403,
                "host_player": active_lobbies[0][target_lobby_index],
                "lobby_id": active_lobbies[9][target_lobby_index]
            }
        current_guest = active_lobbies[1][target_lobby_index]
        if current_guest and current_guest != guest_player:
            return {
                "status": "error",
                "error": "Lobby already has a guest",
                "http_status": 409,
                "host_player": active_lobbies[0][target_lobby_index],
                "lobby_id": active_lobbies[9][target_lobby_index],
                "guest_player": current_guest
            }
        if current_guest != guest_player:
            active_lobbies[1][target_lobby_index] = guest_player
            should_broadcast = True
        if guest_deck and active_lobbies[6][target_lobby_index] != guest_deck:
            active_lobbies[6][target_lobby_index] = guest_deck
            should_broadcast = True
        updated_lobby = _serialize_lobby_row(target_lobby_index)
        if should_broadcast:
            condition_lobby.notify_all()
    finally:
        condition_lobby.release()
    if should_broadcast:
        _broadcast_lobby_state_update()
    resolved_host_player = host_player
    if updated_lobby is not None and not resolved_host_player:
        resolved_host_player = updated_lobby["host_player"]
    return {
        "status": "success",
        "host_player": resolved_host_player,
        "guest_player": guest_player,
        "lobby_id": updated_lobby["lobby_id"] if updated_lobby else lobby_id,
        "lobby": updated_lobby,
        "http_status": 200
    }


def create_bot_game(name_bot_1, name_bot_2, game_id, errata="No Errata", sector="Traxis Sector", deck_1="", deck_2="", private=False):
    global spectator_games
    _ensure_runtime_state_loaded()
    game_id = create_game(name_bot_1, name_bot_2, game_id, errata, sector=sector, deck_1=deck_1, deck_2=deck_2, bots_present=True)
    current_time = datetime.datetime.now()
    time_change = datetime.timedelta(minutes=14400)
    end_time = current_time + time_change
    if not private:
        spectator_games.append((name_bot_1, name_bot_2, game_id, end_time))
        persist_runtime_state()
    return game_id


def create_game(name_1, name_2, game_id, errata, sector="Traxis", deck_1="", deck_2="", bots_present=False):
    global active_games
    global card_array
    global planet_array
    global cards_dict
    global apoka_errata_cards_array
    _ensure_runtime_state_loaded()
    for i in range(len(active_games)):
        if active_games[i].game_id == game_id:
            new_game_id = game_id + random.choice('0123456789ABCDEF')
            return create_game(name_1, name_2, new_game_id, errata, sector=sector, deck_1=deck_1, deck_2=deck_2,
                               bots_present=bots_present)
    card_errata = []
    banned_cards = []
    if errata == "Apoka":
        card_errata = apoka_errata_cards_array
        banned_cards = ban_list_apoka
    elif errata == "Blackstone":
        card_errata = blackstone_errata_cards_array
    active_games.append(GameClass.Game(game_id, name_1, name_2, card_array, planet_array, cards_dict,
                                       errata, card_errata, sector=sector, deck_1=deck_1, deck_2=deck_2,
                                       bot_is_present=bots_present, banned_cards=banned_cards))
    persist_runtime_state()
    return game_id

_ensure_runtime_state_loaded()


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
        _ensure_runtime_state_loaded()
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
            message = _build_lobby_create_message(i)
            await self.chat_message({"type": "chat.message", "message": message})
        print("CURRENT SPEC")
        print(spectator_games)
        prune_spectator_games()
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
        _ensure_runtime_state_loaded()
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        split_message = message.split(sep="/")
        print("receive:", message)
        condition_lobby.acquire()
        condition_games.acquire()
        _ensure_lobby_id_column()
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
            _ensure_lobby_id_column()
            print(active_lobbies)
            le = len(active_lobbies[0]) - 1
            message = _build_lobby_create_message(le)
            print(message)
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )
        if message == "Remove lobby":
            i = 0
            while i < len(active_lobbies[0]):
                if active_lobbies[0][i] == self.name:
                    _remove_lobby_at_index(i)
                    i += -1
                i += 1
            print(active_lobbies)
            message = "Delete lobby"
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )
            for i in range(len(active_lobbies[0])):
                message = _build_lobby_create_message(i)
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
        message = message.split(sep="/")
        if len(message) > 1:
            if message[0] == "Join lobby":
                target_lobby_index = _find_lobby_index_by_identifier(message[1])
                if target_lobby_index != -1:
                    active_lobbies[1][target_lobby_index] = self.name
                    if len(split_message) > 2:
                        active_lobbies[6][target_lobby_index] = split_message[2]
                message = "Delete lobby"
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = _build_lobby_create_message(i)
                    await self.channel_layer.group_send(
                        self.room_group_name, {"type": "chat.message", "message": message}
                    )
            if message[0] == "Leave lobby":
                target_lobby_index = _find_lobby_index_by_identifier(message[1])
                if target_lobby_index != -1 and active_lobbies[1][target_lobby_index] == self.name:
                    active_lobbies[1][target_lobby_index] = ""
                message = "Delete lobby"
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = _build_lobby_create_message(i)
                    await self.channel_layer.group_send(
                        self.room_group_name, {"type": "chat.message", "message": message}
                    )
            if message[0] == "Start game":
                print("Code to start game")
                requested_lobby_identifier = ""
                if len(message) > 1:
                    requested_lobby_identifier = message[1]
                first_name = ""
                second_name = ""
                game_num = -1
                for i in range(len(active_lobbies[0])):
                    if active_lobbies[0][i] == self.name and (
                        not requested_lobby_identifier or
                        active_lobbies[0][i] == requested_lobby_identifier or
                        active_lobbies[9][i] == requested_lobby_identifier
                    ):
                        first_name = active_lobbies[0][i]
                        second_name = active_lobbies[1][i]
                        game_num = i
                        break
                if game_num == -1:
                    print("No matching lobby found for start game request.")
                    condition_lobby.notify_all()
                    condition_lobby.release()
                    condition_games.notify_all()
                    condition_games.release()
                    return None
                game_id = active_lobbies[9][game_num]
                print(game_id)
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
                prune_spectator_games()
                persist_runtime_state()
                message = "Move to game/" + game_id + "/" + first_name + "/" + second_name
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                i = 0
                while i < len(active_lobbies[0]):
                    if active_lobbies[0][i] == self.name:
                        _remove_lobby_at_index(i)
                        i += -1
                    i += 1
                message = "Delete lobby"
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat.message", "message": message}
                )
                for i in range(len(active_lobbies[0])):
                    message = _build_lobby_create_message(i)
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
        except:
            try:
                await self.close()
            except:
                pass

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
        _ensure_runtime_state_loaded()

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
        _maybe_clear_stale_play_room_group(self.channel_layer, self.room_group_name)
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
                data = update_settings.get_user_settings(self.name)
                choices_box_h = data["choices_box_h"]
                choices_box_v = data["choices_box_v"]
                info_box_h = data["info_box_h"]
                info_box_v = data["info_box_v"]
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
        _ensure_runtime_state_loaded()
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)
        message = message.split("/")
        condition_games.acquire()
        game_state_changed = False
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
                    try:
                        turn_notifier.maybe_notify_turn_changed(active_games[current_game_id])
                    except Exception:
                        pass
                    game_state_changed = True
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
                    if message[2] == "SPECIAL_ACTION":
                        game_relevant_string = message[1] + "|||" + "/".join(message[3:])
                        active_games[current_game_id].game_events_as_mono_string += message[1] + "|||action-button" + "\n"
                        active_games[current_game_id].game_events_as_mono_string += game_relevant_string + "\n"
                        await active_games[current_game_id].update_game_event(message[1], ["action-button"],
                                                                              same_thread=True)
                        await active_games[current_game_id].update_game_event(message[1], message[3:])
                    else:
                        game_relevant_string = message[1] + "|||" + "/".join(message[2:])
                        active_games[current_game_id].game_events_as_mono_string += game_relevant_string + "\n"
                        await active_games[current_game_id].update_game_event(message[1], message[2:])
                    try:
                        turn_notifier.maybe_notify_turn_changed(active_games[current_game_id])
                    except Exception:
                        pass
                    game_state_changed = True
                except:
                    try:
                        with open("errorslog.txt", "a") as f:
                            f.write(traceback.format_exc())
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "savegame"])
                    except:
                        pass
                    await self.receive_game_update(
                        "An error has occurred on the server side. Your game may become unstable or unplayable."
                    )
        elif message[0] == "CONTEXT_MENU" and len(message) > 1:
            current_game_id = -1
            for i in range(len(active_games)):
                if active_games[i].game_id == self.room_name:
                    print("Found room")
                    current_game_id = i
            if current_game_id != -1:
                if active_games[current_game_id].safety_check():
                    command_used = message[1]
                    position_card = message[2:]
                    print(command_used)
                    print(position_card)
                    if command_used == "Ready":
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "ready-card"])
                        await active_games[current_game_id].update_game_event(self.name, position_card)
                    elif command_used == "Exhaust":
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "exhaust-card"])
                        await active_games[current_game_id].update_game_event(self.name, position_card)
                    elif command_used == "Discard":
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "discard"])
                        await active_games[current_game_id].update_game_event(self.name, position_card)
                    elif command_used == "Return":
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "return"])
                        await active_games[current_game_id].update_game_event(self.name, position_card)
                    elif command_used == "Remove":
                        if message[2] == "IN_DISCARD":
                            await active_games[current_game_id].resolve_chat_message(self.name, ["", "remove-discard", message[3], message[4]])
                        elif message[2] == "REMOVED":
                            await active_games[current_game_id].resolve_chat_message(self.name, ["", "fully-remove", message[3], message[4]])
                    elif command_used == "Destroy":
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "destroy"])
                        await active_games[current_game_id].update_game_event(self.name, position_card)
                    elif command_used == "Infest":
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "infest", message[3]])
                    elif command_used == "Clear Infestation":
                        await active_games[current_game_id].resolve_chat_message(self.name, ["", "clear-infestation", message[3]])
                    elif command_used == "Deal 1 Damage":
                        complete_message = ["", "assign-damage", position_card[1]]
                        if position_card[0] == "HQ":
                            complete_message.append("-2")
                            complete_message.append(position_card[2])
                        else:
                            complete_message.append(position_card[2])
                            complete_message.append(position_card[3])
                        complete_message.append("1")
                        await active_games[current_game_id].resolve_chat_message(self.name, complete_message)
                    elif command_used == "Remove 1 Damage":
                        complete_message = ["", "remove-damage", position_card[1]]
                        if position_card[0] == "HQ":
                            complete_message.append("-2")
                            complete_message.append(position_card[2])
                        else:
                            complete_message.append(position_card[2])
                            complete_message.append(position_card[3])
                        complete_message.append("1")
                        await active_games[current_game_id].resolve_chat_message(self.name, complete_message)
                    game_state_changed = True
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
                    await active_games[current_game_id].update_game_event_combat_turn_special_action(message[1], message[2:])
                    game_state_changed = True
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
                        game_state_changed = True
                    else:
                        await active_games[self.game_position].resolve_chat_message(self.name, message)
                        game_state_changed = True
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
                                            if "loaddeckbot" in replay_details_split[i + 1]:
                                                first_to_load_deck = p1_name
                                            elif p1_name == replay_details_split[i + 1].split(sep="|||")[0]:
                                                first_to_load_deck = p1_name
                                            else:
                                                first_to_load_deck = p2_name
                                print("First to load", first_to_load_deck)
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
                                game_state_changed = True
                        else:
                            await self.channel_layer.group_send(
                                self.room_group_name, {"type": "chat.message", "message": "Game does not exist"}
                            )
                    else:
                        await active_games[self.game_position].resolve_chat_message(self.name, message)
                        game_state_changed = True
                else:
                    await active_games[self.game_position].resolve_chat_message(self.name, message)
                    game_state_changed = True
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
                        game_state_changed = True
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
                update_settings.update_settings(self.name, choices_box_h=message[1], choices_box_v=message[2])
        elif message[0] == "UPDATE_INFO_BOX_LOCATION" and len(message) == 3:
            if self.name != "Anonymous":
                update_settings.update_settings(self.name, info_box_h=message[1], info_box_v=message[2])
        if game_state_changed:
            persist_runtime_state()
        condition_games.notify_all()
        condition_games.release()
