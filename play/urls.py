from django.urls import path

from . import views

urlpatterns = [
    path("", views.lobby, name="lobby"),
    path("api/discord_bot/", views.discord_bot, name="discord_bot"),
    path("<str:game_id>/", views.game, name="game"),
]
