from django.urls import re_path, path

from . import consumers

websocket_play_urlpatterns = [
    path("ws/play/", consumers.LobbyConsumer.as_asgi()),
    re_path(r"ws/play/(?P<game_id>\w+)/$", consumers.GameConsumer.as_asgi()),
]
