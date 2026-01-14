from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from PIL import Image
import os


def settings_page(request):
    zoom = 1.0
    cardback_name = "Default"
    background_name = "Imperial Aquila"
    if request.user.is_authenticated:
        username = request.user.username
        cwd = os.getcwd()
        settings_file = os.path.join(cwd, "user_preferences_storage/" + username + ".txt")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    extracted_text = f.read()
                    split_text = extracted_text.split(sep="\n")
                    zoom = float(split_text[0])
                    cardback_name = split_text[1]
                    if cardback_name == "Cardback":
                        cardback_name = "Default"
                    cardback_name = cardback_name.replace("_Cardback", "")
                    cardback_name = cardback_name.replace("_", " ")
                    background_name = split_text[2]
            except:
                pass
    return render(request, "settings.html", {"zoom": zoom, "cardback": cardback_name, "background": background_name})


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

