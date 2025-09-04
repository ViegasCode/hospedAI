from django.contrib import admin
from .models import Quarto, Servico, FotoQuarto

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')

@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'capacidade', 'tarifa', 'ativo')
    list_filter = ('tipo', 'ativo')
    search_fields = ('numero',)

@admin.register(FotoQuarto)
class FotoQuartoAdmin(admin.ModelAdmin):
    list_display = ('quarto', 'descricao')
