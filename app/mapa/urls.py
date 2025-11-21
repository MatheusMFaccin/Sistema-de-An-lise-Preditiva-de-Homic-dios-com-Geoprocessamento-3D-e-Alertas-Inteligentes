from django.urls import path
from .views import mapa

urlpatterns = [
    path('mapa/', mapa, name='mapa'),
]
