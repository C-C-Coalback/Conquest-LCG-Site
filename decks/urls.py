from django.urls import path
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    path("", views.decks, name="decks"),
    path("load_latest/", views.decks_latest, name="decks_latest"),
    path("import/", views.decks_import, name="decks_import"),
    path("ajax_import/", views.ajax_import, name="ajax_import")
]
