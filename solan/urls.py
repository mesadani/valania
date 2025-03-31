# myapp/urls.py
from django.urls import path
from .views import wallet_info, connect

urlpatterns = [
    path('connect', connect, name='connect'),  # Ruta para acceder al HTML (index.html)
    path('wallet_info/', wallet_info, name='wallet_info'),  # Ruta para la API de la wallet
]
