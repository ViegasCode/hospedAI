# core/views.py
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.utils.timezone import make_aware
from reservas.models import Reserva
from quartos.models import Quarto

STATUS_CONSIDERADOS = ["pendente", "confirmada"]  # mantenha igual ao calendário

def intervalo_do_dia(d):
    """Retorna (início_aware, fim_aware) do dia 'd' (date)."""
    tz = timezone.get_current_timezone()
    inicio = make_aware(datetime.combine(d, time.min), tz)
    fim = make_aware(datetime.combine(d, time.max), tz)
    return inicio, fim

def home(request):
    hoje_date = timezone.localdate()
    ini, fim = intervalo_do_dia(hoje_date)

    # Quartos ativos
    total_quartos = Quarto.objects.filter(ativo=True).count()

    # Reservas que OVERLAP com o dia de hoje
    reservas_hoje = Reserva.objects.filter(
        status__in=STATUS_CONSIDERADOS,
        data_entrada__lte=fim,
        data_saida__gte=ini,
    )

    ocupados_hoje = reservas_hoje.values("quarto_id").distinct().count()
    livres_hoje = max(total_quartos - ocupados_hoje, 0)

    checkins_hoje = Reserva.objects.filter(
        status__in=STATUS_CONSIDERADOS,
        data_entrada__gte=ini,
        data_entrada__lte=fim,
    ).count()

    checkouts_hoje = Reserva.objects.filter(
        status__in=STATUS_CONSIDERADOS,
        data_saida__gte=ini,
        data_saida__lte=fim,
    ).count()

    # Últimas reservas (para cards/lista na home)
    ultimas_reservas = (Reserva.objects
                        .filter(status__in=STATUS_CONSIDERADOS)
                        .select_related("quarto")
                        .order_by("-data_entrada")[:8])

    ctx = {
        "totais": {
            "quartos_ativos": total_quartos,
            "ocupados_hoje": ocupados_hoje,
            "livres_hoje": livres_hoje,
            "checkins_hoje": checkins_hoje,
            "checkouts_hoje": checkouts_hoje,
        },
        "ultimas_reservas": ultimas_reservas,
    }
    return render(request, "core/home.html", ctx)
