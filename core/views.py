# core/views.py
from django.shortcuts import render
from django.utils.timezone import now

# core/views.py
from django.shortcuts import render
from django.apps import apps
from django.utils import timezone

def home(request):
    # Carrega os models de forma segura (evita import circular / None)
    Reserva = apps.get_model('reservas', 'Reserva')
    Quarto = apps.get_model('quartos', 'Quarto')

    # Se por algum motivo não encontrou, mostra fallback amigável
    if Reserva is None or Quarto is None:
        return render(request, 'core/home.html', {
            'ultimas_reservas': [],
            'stats': {'total_quartos': 0, 'ocupados_hoje': 0, 'livres_hoje': 0},
            'hoje': timezone.now().date(),
        })

    hoje = timezone.now().date()

    # Estatísticas simples
    total_quartos = Quarto.objects.filter(ativo=True).count()
    ocupados_hoje = Reserva.objects.filter(
        data_entrada__date__lte=hoje,
        data_saida__date__gte=hoje,
        status__in=['pendente', 'confirmada'],
    ).count()
    livres_hoje = max(total_quartos - ocupados_hoje, 0)

    # Últimas reservas (ordena por id para não depender de campo de criação)
    ultimas = (Reserva.objects
               .select_related('quarto')
               .order_by('-id')[:5])

    context = {
        'ultimas_reservas': ultimas,
        'stats': {
            'total_quartos': total_quartos,
            'ocupados_hoje': ocupados_hoje,
            'livres_hoje': livres_hoje,
        },
        'hoje': hoje,
    }
    return render(request, 'core/home.html', context)
