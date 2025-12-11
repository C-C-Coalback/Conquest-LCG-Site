from django.shortcuts import render
from django.http import JsonResponse
from .consumers import get_lobbies


def lobby(request):
    return render(request, "play/lobby.html")


def game(request, game_id):
    return render(request, "play/play.html", {"game_id": game_id})


def discord_bot(request):
    active_lobbies, spec_lobbies = get_lobbies()
    lobbies_count = 0
    sent_lobby_first_players = []
    sent_lobby_second_players = []
    sent_lobby_errata = []
    for i in range(len(active_lobbies[2])):
        if active_lobbies[2][i] == "Public":
            lobbies_count += 1
            sent_lobby_first_players.append(active_lobbies[0][i])
            sent_lobby_second_players.append(active_lobbies[1][i])
            sent_lobby_errata.append(active_lobbies[3][i])
    data = {"lobbiesCount": len(active_lobbies[0]), "firstPlayers": sent_lobby_first_players,
            "secondPlayers": sent_lobby_second_players, "errata": sent_lobby_errata}
    return JsonResponse(data)
