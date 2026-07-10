from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("auth-token/", obtain_auth_token),
    path("create_bot_room/", views.create_bot_room, name="create_bot_room"),
    path("send_deck_text/", views.receive_raw_deck_text, name="receive_raw_deck_text"),
    path("request_deck/", views.request_deck_text_given_name, name="request_deck_text_given_name"),
]
