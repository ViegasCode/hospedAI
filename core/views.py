# core/views.py
from django.shortcuts import render
from django.utils.timezone import now

try:
    from quartos.models import Quarto
    from reservas.models import Reserva
except Exception:
    # Se quiser rodar sem apps por um momento
    Quarto = None
    Reserva = None

def home(request):
    hoje = now().date()

    total_quartos = Quarto.objects.filter(ativo=True).count() if Quarto else 0

    reservas_ativas_hoje = Reserva.objects.filter(
        data_entrada__date__lte=hoje,
        data_saida__date__gt=hoje,
        status__in=["pendente", "confirmada"]
    ).select_related("quarto") if Reserva else []

    ocupados_hoje = reservas_ativas_hoje.count() if Reserva else 0
    livres_hoje = max(total_quartos - ocupados_hoje, 0)

    checkins_hoje = Reserva.objects.filter(
        data_entrada__date=hoje,
        status__in=["pendente", "confirmada"]
    ).count() if Reserva else 0

    checkouts_hoje = Reserva.objects.filter(
        data_saida__date=hoje,
        status__in=["pendente", "confirmada"]
    ).count() if Reserva else 0

    ultimas_reservas = Reserva.objects.select_related("quarto").order_by("-data_entrada")[:5]

    contexto = {
        "total_quartos": total_quartos,
        "ocupados_hoje": ocupados_hoje,
        "livres_hoje": livres_hoje,
        "checkins_hoje": checkins_hoje,
        "checkouts_hoje": checkouts_hoje,
        "tem_quartos": total_quartos > 0,
        "tem_reservas_hoje": ocupados_hoje > 0 or checkins_hoje > 0 or checkouts_hoje > 0,
        "ultimas_reservas": ultimas_reservas,
    }
    return render(request, "core/home.html", contexto)
