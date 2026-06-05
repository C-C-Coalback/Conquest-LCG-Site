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
