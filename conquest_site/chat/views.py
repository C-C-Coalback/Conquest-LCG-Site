from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


def chat(request):
    template = loader.get_template('chat.html')
    return HttpResponse(template.render())
