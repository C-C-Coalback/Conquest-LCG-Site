from django.urls import path

from . import consumers

websocket_decks_urlpatterns = [
    path("ws/decks/", consumers.DecksConsumer.as_asgi()),
]