from django.urls import path

from .views import SignUpView
from . import views


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("update_settings/", views.change_settings, name="change_settings"),
    path("delete_profile/", views.delete_profile, name="delete_profile"),
]
