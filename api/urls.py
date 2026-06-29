from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("skills/", views.skills, name="skills"),
    path("skills/<path:skill_id>/", views.skill_detail, name="skill_detail"),
    path("lobbies/", views.lobbies, name="lobbies"),
    path("join_lobby/", views.join_lobby, name="join_lobby"),
    path("games/", views.games, name="games"),
    path("game/<str:game_id>/agent_state/", views.agent_state, name="agent_state"),
    path("game/<str:game_id>/agent_action/", views.agent_action, name="agent_action"),
    path("game/<str:game_id>/agent_command/", views.agent_command, name="agent_command"),
    path("games/<str:game_id>/webhooks/", views.webhook_subscriptions, name="webhook_subscriptions"),
    path("create_bot_room/", views.create_bot_room, name="create_bot_room"),
    path("send_deck_text/", views.receive_raw_deck_text, name="receive_raw_deck_text"),
    path("request_deck/", views.request_deck_text_given_name, name="request_deck_text_given_name"),
]
