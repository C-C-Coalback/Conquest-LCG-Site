from django.shortcuts import render
from django.http import JsonResponse
from .consumers import get_lobbies, get_active_games


def lobby(request):
    return render(request, "play/lobby.html")


def game(request, game_id):
    _, spec_lobbies = get_lobbies()
    is_second_player = False
    for i in range(len(spec_lobbies)):
        if spec_lobbies[i][2] == game_id:
            if request.user.username == spec_lobbies[i][1]:
                is_second_player = True
    active_games = get_active_games()
    cardback_1 = "Cardback"
    cardback_2 = "Cardback"
    for i in range(len(active_games)):
        if active_games[i].game_id == game_id:
            cardback_1 = active_games[i].p1.cardback_name
            cardback_2 = active_games[i].p2.cardback_name
    return render(request, "play/play.html", {"game_id": game_id, "is_p2": is_second_player,
                                              "cardback_1": cardback_1, "cardback_2": cardback_2})


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
