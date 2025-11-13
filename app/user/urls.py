from django.urls import path
from .views import cadastro

urlpatterns = [
    path('mapa/', cadastro, name='mapa'),
]
