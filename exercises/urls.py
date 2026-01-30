from django.urls import path

from . import views

app_name = "exercises"

urlpatterns = [
    path("matching/", views.matching_exercise, name="matching"),
    path("matching/check/", views.check_matches, name="matching_check"),
    path("spelling/", views.spelling_exercise, name="spelling"),
    path("spelling/check/", views.check_spelling, name="spelling_check"),
]
