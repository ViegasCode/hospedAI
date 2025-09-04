from django.db import models

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Quarto(models.Model):
    TIPO_CHOICES = [
        ("Standard", "Standard"),
        ("Luxo", "Luxo"),
        ("Suite", "Suite"),
    ]

    numero = models.PositiveIntegerField(unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    capacidade = models.PositiveIntegerField(default=2)
    ativo = models.BooleanField(default=True)
    tarifa = models.DecimalField(max_digits=8, decimal_places=2)
    servicos = models.ManyToManyField('Servico', blank=True)
    ocupado = models.BooleanField(default=False)  # indica se o quarto está ocupado

    def __str__(self):
        return f"{self.tipo.capitalize()} - Quarto {self.numero}"

    def esta_disponivel(self):
        """
        Verifica se o quarto está disponível.
        Sem depender do modelo Reserva.
        """
        return self.ativo and not self.ocupado


class FotoQuarto(models.Model):
    quarto = models.ForeignKey(Quarto, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='quartos/')
    descricao = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Foto do {self.quarto}"
