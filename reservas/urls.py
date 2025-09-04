from django.urls import path
from . import views

urlpatterns = [
    path("nova_reserva/", views.nova_reserva, name="nova_reserva"),
    # path("calendario/", views.calendario_quartos, name="calendario_quartos"),
    path("api/reservas/", views.reservas_json, name="reservas_json"),  # nova rota
    path("calendario/", views.calendario_dashboard, name="calendario_dashboard"),
    path("calendario2/", views.calendario_quarto2, name="calendario_quarto2"),
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
]
