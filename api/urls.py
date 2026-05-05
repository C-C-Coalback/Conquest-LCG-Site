from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_bot_room/", views.create_bot_room, name="create_bot_room"),
]
