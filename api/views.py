import json
from django.http import JsonResponse
from play.consumers import create_bot_game
import os
from django.views.decorators.csrf import csrf_exempt


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
            errata = "No Errata"
            sector = "Traxis Sector"
            deck_1 = ""
            deck_2 = ""

            cwd = os.getcwd()
            print(cwd)
            content_file = cwd + "/decks/default_decks/CatoCore"
            with open(content_file, "r") as f:
                deck_1 = f.read()
                deck_2 = deck_1
            game_id = create_bot_game(bot_name_1, bot_name_2, game_id, errata, sector, deck_1, deck_2)
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
