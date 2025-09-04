from django.db import models
from django.utils import timezone
from quartos.models import Quarto  # importa o Quarto real


class Reserva(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    nome_cliente = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    tipo_quarto = models.CharField(max_length=50, choices=[
        ("standard", "Standard"),
        ("luxo", "Luxo"),
        ("suite", "Suite"),
    ])

    data_entrada = models.DateTimeField()  # agora inclui hora
    data_saida = models.DateTimeField()  # agora inclui hora
    criado_em = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")

    # ForeignKey para o Quarto real
    quarto = models.ForeignKey(Quarto, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.nome_cliente} - {self.quarto} ({self.data_entrada} -> {self.data_saida})"
