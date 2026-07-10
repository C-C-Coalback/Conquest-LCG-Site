from django.shortcuts import render
from django.http import JsonResponse
from .consumers import get_lobbies, get_active_games
import os
import update_settings


def lobby(request):
    return render(request, "play/lobby.html")


valid_backgrounds = ["/static/images/ImperialAquila.jpg", "/static/images/Heldrakes.jpg", "/static/images/Box_Art.jpg",
                     "/static/images/Death_Guard.jpg", "/static/images/Necrons_Awakening.jpg",
                     "/static/images/Chaos_v_Orks.jpg", "/static/images/Tyranids_v_Tau.jpg"]


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
    background = "images/ImperialAquila.jpg"
    data = update_settings.get_user_settings(username)
    volume = float(data["volume"])
    background = "images/" + data["background"]
    if background not in valid_backgrounds:
        background = valid_backgrounds[0]
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
    for i in range(len(active_lobbies)):
        if active_lobbies[i][2] == "Public":
            sent_lobby_first_players.append(active_lobbies[i][0])
            sent_lobby_second_players.append(active_lobbies[i][1])
            sent_lobby_errata.append(active_lobbies[i][3])
    data = {"firstPlayers": sent_lobby_first_players,
            "secondPlayers": sent_lobby_second_players, "errata": sent_lobby_errata}
    return JsonResponse(data)
