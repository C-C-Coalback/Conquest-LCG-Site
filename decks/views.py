from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


def decks(request):
    template = loader.get_template('decks.html')
    return HttpResponse(template.render())
