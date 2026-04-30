from django.urls import path

from . import views

urlpatterns = [
    path("/create_bot_room/<str:room_name>", views.create_bot_room, name="create_bot_room"),
]
