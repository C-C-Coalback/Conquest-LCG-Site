from django.urls import path
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    path("", views.decks, name="decks"),
]
