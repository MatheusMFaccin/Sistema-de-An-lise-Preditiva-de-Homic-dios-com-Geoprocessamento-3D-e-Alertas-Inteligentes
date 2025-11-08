from django.urls import path
from .views import cadastro

urlpatterns = [
    path('contato/', cadastro, name='contato'),
]
