from django.contrib import admin
from .models import Reserva  # certifique-se que é .models, não core.models

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nome_cliente', 'tipo_quarto', 'data_entrada', 'data_saida', 'status')
    list_filter = ('tipo_quarto', 'status')
    search_fields = ('nome_cliente', 'email', 'telefone')
