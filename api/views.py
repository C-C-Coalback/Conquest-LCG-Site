import json
from django.http import JsonResponse
from play.consumers import create_bot_game
import os
from django.views.decorators.csrf import csrf_exempt
from decks.consumers import deck_check_and_save


def index(request):
    return JsonResponse({"status": "error"})

@csrf_exempt
def create_bot_room(request):
    print(request.method)
    if request.method == "POST":
        try:
            data = request.POST.dict()
            print(data)
            bot_name_1 = data["name1"]
            bot_name_2 = data["name2"]
            game_id = data["id"]
            private = data["private"]
            errata = "No Errata"
            sector = "Traxis Sector"
            print(private)
            if private == "False":
                private = False
            else:
                private = True
            print(type(private))
            game_id = create_bot_game(bot_name_1, bot_name_2, game_id, errata, sector, private=private)
            response = {
                'status': 'success',
                "id": game_id
            }
        except json.JSONDecodeError:
            response = {
                'status': 'error',
                'error': 'Incorrect JSON usage'
            }
        except:
            response = {
                'status': 'error',
                'error': "server error 500"
            }
    else:
        response = {
            'status': 'error',
            'error': 'Only POST requests allowed'
        }
    return JsonResponse(response)


@csrf_exempt
def receive_raw_deck_text(request):
    if request.method != "POST":
        response = {
            "status": "error",
            "error": "Not POST request"
        }
        return JsonResponse(response)
    data = request.POST.dict()
    try:
        bot_name = data["name"]
        deck = data["deck_text"]
        print(deck)
        result_of_saving = deck_check_and_save(bot_name, deck)
        response = {
            "status": result_of_saving["message"]
        }
    except KeyError as e:
        response = {
            "status": "error",
            "error": f"Missing required field: {str(e)}"
        }
    except Exception as e:
        response = {
            "status": "error",
            "error": "server error 500",
            "details": str(e)
        }
    return JsonResponse(response)


@csrf_exempt
def request_deck_text_given_name(request):
    if request.method != "POST":
        response = {
            "status": "error",
            "error": "Not POST request"
        }
        return JsonResponse(response)
    data = request.POST.dict()
    try:
        bot_name = data["name"]
        deck_name = data["deck_name"]
        target_deck_dir = os.getcwd() + "/decks/DeckStorage/" + bot_name + "/" + deck_name
        if not os.path.exists(target_deck_dir):
            response = {
                "status": "error",
                "error": "Deck does not exist"
            }
        else:
            with open(target_deck_dir, "r") as file:
                deck_text = file.read()
            response = {
                "status": "success",
                "deck_text": deck_text
            }
    except KeyError as e:
        response = {
            "status": "error",
            "error": f"Missing required field: {str(e)}"
        }
    except Exception as e:
        response = {
            "status": "error",
            "error": "server error 500",
            "details": str(e)
        }
    return JsonResponse(response)
