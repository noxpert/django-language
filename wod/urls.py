from django.urls import path

from . import views

urlpatterns = [
    path("", views.random_word, name="random_word"),
]
