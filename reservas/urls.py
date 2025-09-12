from django.urls import path
from . import views

urlpatterns = [
    path("nova_reserva/", views.nova_reserva, name="nova_reserva"),
    path("calendario-ui/", views.calendario_quarto2, name="calendario_quartos"),
    path("api/reservas/", views.reservas_create_api, name="reservas_create_api"),# nova rota
    #("calendario/", views.calendario_dashboard, name="calendario_dashboard"),
    path("calendario2/", views.calendario_quarto2, name="calendario_quarto2"),
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    path("nova_reserva/", views.nova_reserva, name="nova_reserva"),
    # Página (HTML) que vai usar seu template de calendário
    path("calendario/", views.calendario_quarto2, name="calendario_quartos"),
    # API JSON consumida pelo template
    path("api/calendario/", views.calendario_api, name="calendario_api"),
    # (opcionais/legados)
    path("reservas_json/", views.reservas_json, name="reservas_json"),
    path("api/detalhes/", views.detalhes_dia, name="detalhes_dia"),  # <--- NOVO
    path("api/gantt/", views.gantt_api, name="gantt_api"),
    path("gantt/", views.gantt_page, name="gantt_page"),
    path('api/gantt_window/', views.gantt_window_api, name='gantt_window_api'),
    path("api/reservas/<int:pk>/", views.reserva_update_api, name="reserva_update_api"),
]
