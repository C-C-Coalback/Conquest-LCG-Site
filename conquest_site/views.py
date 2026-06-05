from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from PIL import Image
import os
import update_settings


def settings_page(request):
    zoom = 1.0
    volume = 1.0
    cardback_name = "Default"
    background_name = "Imperial Aquila"
    if request.user.is_authenticated:
        username = request.user.username
        data = update_settings.get_user_settings(username)
        zoom = float(data["zoom"])
        volume = float(data["volume"])
        cardback_name = data["cardback"]
        background_name = data["background"]
    print(cardback_name)
    print(background_name)
    return render(request, "settings.html", {"zoom": zoom, "cardback": cardback_name, "background": background_name, "volume": volume})


def simple_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        if request.user.is_authenticated:
            username = request.user.username
            files = request.FILES['file']
            print('got here')
            cwd = os.getcwd()
            destination = cwd + "/media/"
            destination = destination + username + ".jpg"
            if os.path.exists(destination):
                os.remove(destination)
            destination = username + ".jpg"
            print(destination)
            file_data = files.read()
            print(len(file_data))
            fs = FileSystemStorage()
            file_name = fs.save(destination, files)
            # img = Image.open(files)
            # img.save(destination)
    return redirect("/")

