from django.shortcuts import render


def lobby(request):
    return render(request, "play/lobby.html")


def game(request, game_id):
    return render(request, "play/play.html", {"game_id": game_id})
