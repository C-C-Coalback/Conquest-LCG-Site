from django.urls import path

from . import views

urlpatterns = [
    path("", views.lobby, name="lobby"),
    path("<str:game_id>/", views.game, name="game"),
]
