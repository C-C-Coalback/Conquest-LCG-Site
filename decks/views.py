from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse
from .consumers import get_card_names, deck_check_and_save
import requests
from django.views.decorators.csrf import csrf_exempt


def decks(request):
    card_names = get_card_names(request.user.username)
    return render(request, "decks.html", {"auto_complete": card_names, "load_latest": False})


def decks_latest(request):
    card_names = get_card_names(request.user.username)
    return render(request, "decks.html", {"auto_complete": card_names, "load_latest": True})


def decks_import(request):
    return render(request, "decks_import.html")


@csrf_exempt
def ajax_import(request):
    conquestdb_url = "http://conquestdb.com/"
    deck_key = request.POST.get('deck_key')
    conquestdb_url = conquestdb_url + "api/iridial/" + deck_key + "/"
    try:
        response = requests.get(conquestdb_url)
        response = response.json()
        flag = response["message"]
        if flag == "DECK FOUND":
            deck_content = response["deck_content"]
            data_from_check = deck_check_and_save(request.user.username, deck_content)
            if data_from_check["will_send"] or data_from_check["deck_exists"]:
                return JsonResponse({'message': 'Found and saved deck'})
            return JsonResponse({'message': 'Found deck, but invalid - ' + data_from_check["message"].replace("Feedback/", "")})
        else:
            return JsonResponse({'message': 'Failed to find a deck of the given key'})
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'could not reach ConquestDB'})
