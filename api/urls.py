from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_bot_room/", views.create_bot_room, name="create_bot_room"),
    path("send_deck_text/", views.receive_raw_deck_text, name="receive_raw_deck_text"),
    path("request_deck/", views.request_deck_text_given_name, name="request_deck_text_given_name"),
]
