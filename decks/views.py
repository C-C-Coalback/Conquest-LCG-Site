from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .consumers import get_card_names


def decks(request):
    card_names = get_card_names(request.user.username)
    print("card names", card_names)
    return render(request, "decks.html", {"auto_complete": card_names})
