from django.urls import path

from . import views

app_name = "matching"

urlpatterns = [
    path("", views.matching_exercise, name="exercise"),
    path("check/", views.check_matches, name="check"),
]
