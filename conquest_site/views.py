from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from PIL import Image
import os


def simple_upload(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            files = request.FILES['file']
            print('got here')
            cwd = os.getcwd()
            destination = cwd + "/staticfiles/images/ProfilePictures/"
            destination = destination + username + ".jpg"
            print(destination)
            file_data = files.read()
            print(len(file_data))
            img = Image.open(files)
            img.save(destination)
        return redirect("/")

