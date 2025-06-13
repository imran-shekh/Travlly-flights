from django.urls import path
from .views import search_flights
from . import views

urlpatterns = [
    path('', views.search_flights, name='search_flights'),
]
