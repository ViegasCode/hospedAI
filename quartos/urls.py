from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_quartos, name='listar_quartos'),
path('criar/', views.criar_quarto, name='criar_quarto'),
]
