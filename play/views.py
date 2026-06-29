from django.shortcuts import render
from django.http import JsonResponse
from .consumers import get_lobbies, get_active_games
import os
import socket
import update_settings

def _is_redis_connection_available():
    redis_host = os.environ.get("CHANNEL_REDIS_HOST", "127.0.0.1")
    redis_port = int(os.environ.get("CHANNEL_REDIS_PORT", "6379"))
    try:
        with socket.create_connection((redis_host, redis_port), timeout=0.25):
            return True
    except OSError:
        return False


def lobby(request):
    show_admin_redis_warning = bool(
        request.user.is_authenticated and request.user.is_superuser and not _is_redis_connection_available()
    )
    return render(
        request,
        "play/lobby.html",
        {"show_admin_redis_warning": show_admin_redis_warning}
    )


BACKGROUND_IMAGE_MAP = {
    "Imperial Aquila": "ImperialAquila.jpg",
    "Heldrakes": "Heldrakes.jpg",
    "Box Art": "Box_Art.jpg",
    "Death Guard": "Death_Guard.jpg",
    "Necrons Awakening": "Necrons_Awakening.jpg",
    "Chaos v Orks": "Chaos_v_Orks.jpg",
    "Tyranids v Tau": "Tyranids_v_Tau.jpg",
}
DEFAULT_BACKGROUND_URL = "/static/images/ImperialAquila.jpg"
VALID_BACKGROUND_URLS = {
    "/static/images/" + filename for filename in BACKGROUND_IMAGE_MAP.values()
}


def resolve_background_url(saved_background_value):
    if saved_background_value is None:
        return DEFAULT_BACKGROUND_URL
    value = str(saved_background_value).strip()
    if not value:
        return DEFAULT_BACKGROUND_URL
    if value in BACKGROUND_IMAGE_MAP:
        return "/static/images/" + BACKGROUND_IMAGE_MAP[value]
    if value in VALID_BACKGROUND_URLS:
        return value
    if value.startswith("/static/images/"):
        if value in VALID_BACKGROUND_URLS:
            return value
        if not value.lower().endswith(".jpg") and (value + ".jpg") in VALID_BACKGROUND_URLS:
            return value + ".jpg"
        return DEFAULT_BACKGROUND_URL
    if value.startswith("images/"):
        value = value[len("images/"):]
    if value.startswith("/images/"):
        value = value[len("/images/"):]
    value = value.lstrip("/")
    if value and not value.lower().endswith(".jpg"):
        value = value + ".jpg"
    candidate = "/static/images/" + value
    if candidate in VALID_BACKGROUND_URLS:
        return candidate
    normalized = value.lower().replace("_", " ").replace(".jpg", "").strip()
    for setting_name, filename in BACKGROUND_IMAGE_MAP.items():
        if normalized == setting_name.lower():
            return "/static/images/" + filename
    return DEFAULT_BACKGROUND_URL


def game(request, game_id):
    active_games = get_active_games()
    is_second_player = False
    for i in range(len(active_games)):
        if active_games[i].game_id == game_id:
            if request.user.username == active_games[i].p2.name_player:
                is_second_player = True
    cardback_1 = "Cardback"
    cardback_2 = "Cardback"
    username = request.user.username
    background = DEFAULT_BACKGROUND_URL
    data = update_settings.get_user_settings(username)
    volume = float(data["volume"])
    background = resolve_background_url(data.get("background"))
    for i in range(len(active_games)):
        if active_games[i].game_id == game_id:
            cardback_1 = active_games[i].p1.cardback_name
            cardback_2 = active_games[i].p2.cardback_name
    return render(request, "play/play.html", {"game_id": game_id, "is_p2": is_second_player,
                                              "cardback_1": cardback_1, "cardback_2": cardback_2,
                                              "background": background, "volume": volume})


def discord_bot(request):
    active_lobbies, spec_lobbies = get_lobbies()
    sent_lobby_first_players = []
    sent_lobby_second_players = []
    sent_lobby_errata = []
    for i in range(len(active_lobbies[2])):
        if active_lobbies[2][i] == "Public":
            sent_lobby_first_players.append(active_lobbies[0][i])
            sent_lobby_second_players.append(active_lobbies[1][i])
            sent_lobby_errata.append(active_lobbies[3][i])
    data = {"firstPlayers": sent_lobby_first_players,
            "secondPlayers": sent_lobby_second_players, "errata": sent_lobby_errata}
    return JsonResponse(data)
