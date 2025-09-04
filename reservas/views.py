import calendar

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from reservas.models import Reserva
from quartos.models import Quarto
import datetime
from datetime import datetime, timedelta
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.shortcuts import render
from reservas.models import Reserva
from quartos.models import Quarto
import calendar

import calendar
from datetime import date, datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from reservas.models import Reserva
from quartos.models import Quarto
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now

def listar_quartos(request):
    data_entrada = request.GET.get('data_entrada')
    data_saida = request.GET.get('data_saida')

    quartos = Quarto.objects.all()

    if data_entrada and data_saida:
        # Converter para datetime.date
        data_entrada_obj = date.fromisoformat(data_entrada)
        data_saida_obj = date.fromisoformat(data_saida)

        # Filtra quartos já reservados
        quartos_reservados = Reserva.objects.filter(
            status__in=['confirmada', 'pendente'],
            data_entrada__lte=data_saida_obj,
            data_saida__gte=data_entrada_obj
        ).values_list('quarto_id', flat=True)

        quartos = quartos.exclude(id__in=quartos_reservados)

    context = {
        'quartos': quartos,
        'request': request,
    }
    return render(request, 'reservas/listar_quartos.html', context)

# ============================
# Listar quartos disponíveis
# ============================
def nova_reserva(request):
    if request.method == "POST":
        nome = request.POST.get('nome_cliente')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        tipo_quarto = request.POST.get('tipo_quarto')
        quarto_id = request.POST.get('quarto')
        data_entrada = request.POST.get('data_entrada')
        hora_entrada = request.POST.get('hora_entrada')
        data_saida = request.POST.get('data_saida')
        hora_saida = request.POST.get('hora_saida')

        quarto = Quarto.objects.get(id=quarto_id)

        # Combina data + hora
        dt_entrada = timezone.make_aware(datetime.fromisoformat(f"{data_entrada}T{hora_entrada}"))
        dt_saida = timezone.make_aware(datetime.fromisoformat(f"{data_saida}T{hora_saida}"))

        reserva = Reserva.objects.create(
            nome_cliente=nome,
            email=email,
            telefone=telefone,
            tipo_quarto=tipo_quarto,
            quarto=quarto,
            data_entrada=dt_entrada,
            data_saida=dt_saida,
            status="pendente"
        )

        # Mensagem de sucesso
        messages.success(request, f"Reserva de {reserva.nome_cliente} criada com sucesso!")

        return redirect(reverse('listar_quartos'))

    quartos = Quarto.objects.all()
    context = {
        'quartos': quartos
    }
    return render(request, 'reservas/nova_reserva.html', context)


# ============================
# Criar nova reserva
# ============================
def calendario_quartos(request):
    hoje = date.today()
    mes = hoje.month
    ano = hoje.year

    quartos = Quarto.objects.all()

    # Dias do mês
    dias_mes = [date(ano, mes, d) for d in range(1, calendar.monthrange(ano, mes)[1]+1)]
    inicio_mes = timezone.make_aware(datetime(ano, mes, 1, 0, 0))
    fim_mes = timezone.make_aware(datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59))

    calendario = []

    for quarto in quartos:
        reservas_quarto = []
        reservas = Reserva.objects.filter(
            quarto=quarto,
            data_saida__gte=inicio_mes,
            data_entrada__lte=fim_mes
        )

        for reserva in reservas:
            # Ajusta para o mês
            start = max(reserva.data_entrada, inicio_mes)
            end = min(reserva.data_saida, fim_mes)

            total_segundos = (fim_mes - inicio_mes).total_seconds()
            left = (start - inicio_mes).total_seconds() / total_segundos * 100
            width = (end - start).total_seconds() / total_segundos * 100

            reservas_quarto.append({
                'nome': reserva.nome_cliente.split()[0],
                'left': left,
                'width': width
            })

        calendario.append({
            'quarto': quarto,
            'reservas': reservas_quarto
        })

    context = {
        'calendario': calendario,
        'dias_mes': dias_mes,
        'mes': mes,
        'ano': ano
    }
    return render(request, 'reservas/calendario_quartos.html', context)


# ============================
# Calendário de quartos
# ============================


from django.utils import timezone

from django.http import JsonResponse

from django.http import JsonResponse
from reservas.models import Reserva

def reservas_json(request):
    reservas = Reserva.objects.all()
    events = []

    cores = {
        "standard": "#007bff",
        "luxo": "#28a745",
        "suite": "#dc3545",
    }

    for reserva in reservas:
        tipo = reserva.tipo_quarto if reserva.tipo_quarto else "Sem tipo"
        cor = cores.get(tipo, "#ffc107")

        events.append({
            "id": reserva.id,
            "title": f"{reserva.nome_cliente} ({tipo})",
            "start": reserva.data_entrada.isoformat(),
            "end": reserva.data_saida.isoformat(),
            "backgroundColor": cor,
            "borderColor": cor,
        })

    return JsonResponse(events, safe=False)

@api_view(["GET"])
def calendario_dashboard(request):
    """
    Retorna dados de ocupação por dia + dashboard diário
    """
    data_entrada = request.GET.get("data_entrada")
    data_saida = request.GET.get("data_saida")

    if not data_entrada or not data_saida:
        return Response({"error": "Forneça data_entrada e data_saida"}, status=400)

    # Quartos
    total_quartos = Quarto.objects.count()

    # Reservas nesse período
    reservas = Reserva.objects.filter(
        data_saida__gte=data_entrada,
        data_entrada__lte=data_saida,
        status__in=["pendente", "confirmada"]
    )

    # Disponibilidade por dia
    from datetime import date, timedelta
    d1 = date.fromisoformat(data_entrada)
    d2 = date.fromisoformat(data_saida)
    dias = (d2 - d1).days + 1

    calendario = []
    for i in range(dias):
        dia = d1 + timedelta(days=i)
        ocupados = reservas.filter(data_entrada__lte=dia, data_saida__gte=dia).count()
        livres = total_quartos - ocupados
        calendario.append({
            "day": dia.day,
            "date": dia.isoformat(),
            "free": livres,
            "occupied": ocupados,
        })

    # Dashboard do dia atual
    hoje = now().date()
    checkins = reservas.filter(data_entrada=hoje).count()
    checkouts = reservas.filter(data_saida=hoje).count()

    return Response({
        "total_quartos": total_quartos,
        "calendario": calendario,
        "dashboard": {
            "livres": total_quartos - reservas.filter(data_entrada__lte=hoje, data_saida__gte=hoje).count(),
            "ocupados": reservas.filter(data_entrada__lte=hoje, data_saida__gte=hoje).count(),
            "checkins": checkins,
            "checkouts": checkouts,
        },
    })

def calendario_quarto2(request):
    return render(request, "reservas/calendario_quarto2.html")

from django.http import JsonResponse
from django.utils.timezone import now
from datetime import datetime, timedelta
from quartos.models import Quarto
from .models import Reserva

def get_calendar_and_dashboard(request):
    """
    Retorna dados combinados para o frontend:
    - Calendário mensal: quartos livres / total
    - Dashboard: livres, ocupados, check-ins, check-outs
    - Kanban: distribuição de quartos por status
    """
    today = datetime.today()
    total_quartos = Quarto.objects.filter(ativo=True).count()
    month_days = 30  # ou calcular o número de dias do mês atual

    # Construindo dados do calendário
    calendar_data = []
    for day_num in range(1, month_days + 1):
        day_date = today.replace(day=day_num)
        # Reservas ativas no dia
        reservas_no_dia = Reserva.objects.filter(
            status__in=["pendente", "confirmada"],
            data_entrada__lte=day_date,
            data_saida__gte=day_date
        ).values_list('quarto_id', flat=True)

        quartos_livres = Quarto.objects.filter(ativo=True).exclude(id__in=reservas_no_dia).count()

        calendar_data.append({
            "day": day_num,
            "free": quartos_livres,
            "total": total_quartos
        })

    # Detalhes do dia atual
    reservas_hoje = Reserva.objects.filter(
        status__in=["pendente", "confirmada"],
        data_entrada__lte=today,
        data_saida__gte=today
    )

    quartos_livres_hoje = Quarto.objects.filter(ativo=True).exclude(id__in=reservas_hoje.values_list('quarto_id', flat=True))

    today_details = {
        "free": [{"room": f"{q.tipo} {q.numero}", "checkout": "—"} for q in quartos_livres_hoje],
        "occupied": [{"room": f"{r.quarto.tipo} {r.quarto.numero}", "checkout": r.data_saida.strftime("%d/%m")} for r in reservas_hoje],
        "checkins": [{"room": f"{r.quarto.tipo} {r.quarto.numero}", "checkout": r.data_saida.strftime("%d/%m")}
                     for r in Reserva.objects.filter(status__in=["pendente", "confirmada"], data_entrada__date=today.date())]
    }

    # Kanban simples por status
    kanban_data = {
        "Livre": [f"{q.tipo} {q.numero}" for q in quartos_livres_hoje],
        "Ocupado": [f"{r.quarto.tipo} {r.quarto.numero} - {r.nome_cliente}" for r in reservas_hoje],
        "Pendente": [f"{r.quarto.tipo} {r.quarto.numero} - {r.nome_cliente}" for r in Reserva.objects.filter(status="pendente")],
        "Check-out hoje": [f"{r.quarto.tipo} {r.quarto.numero} - {r.nome_cliente}"
                           for r in Reserva.objects.filter(status__in=["pendente","confirmada"], data_saida__date=today.date())]
    }

    return JsonResponse({
        "calendar": calendar_data,
        "today": today_details,
        "kanban": kanban_data
    })

def dashboard_api(request):
    # Total de quartos ativos
    quartos = Quarto.objects.filter(ativo=True)
    total_quartos = quartos.count()

    # Data de hoje
    hoje = timezone.now().date()

    # Lista de quartos por dia (para o calendário)
    month_days = 30  # assumindo 30 dias para simplificação
    calendar = []
    for i in range(1, month_days + 1):
        dia = hoje.replace(day=i) if i <= 28 else hoje  # evitar erro em meses curtos
        reservas_dia = Reserva.objects.filter(
            data_entrada__date__lte=dia,
            data_saida__date__gt=dia,
            status='confirmada'
        )
        ocupados = reservas_dia.count()
        livres = total_quartos - ocupados
        calendar.append({'day': i, 'free': livres, 'total': total_quartos})

    # Detalhes do dia de hoje
    reservas_hoje = Reserva.objects.filter(
        data_entrada__date__lte=hoje,
        data_saida__date__gt=hoje,
        status='confirmada'
    )

    free_quartos = [q for q in quartos if not reservas_hoje.filter(quarto=q).exists()]
    occupied_quartos = [r.quarto for r in reservas_hoje]

    checkins_hoje = Reserva.objects.filter(
        data_entrada__date=hoje,
        status='confirmada'
    )

    # Monta a resposta JSON
    data = {
        'calendar': calendar,
        'today': {
            'free': [{'room': f"{q.tipo} {q.numero}", 'checkout': '-'} for q in free_quartos],
            'occupied': [{'room': f"{q.tipo} {q.numero}", 'checkout': r.data_saida.strftime('%d/%m')} for r, q in zip(reservas_hoje, occupied_quartos)],
            'checkins': [{'room': f"{r.quarto.tipo} {r.quarto.numero}", 'checkout': r.data_saida.strftime('%d/%m')} for r in checkins_hoje],
        },
        'kanban': [
            {'title': 'Livre', 'items': [f"{q.tipo} {q.numero}" for q in free_quartos]},
            {'title': 'Ocupado', 'items': [f"{r.quarto.tipo} {r.quarto.numero}" for r in reservas_hoje]},
            {'title': 'Check-in Hoje', 'items': [f"{r.quarto.tipo} {r.quarto.numero}" for r in checkins_hoje]},
            {'title': 'Check-out Hoje', 'items': [f"{r.quarto.tipo} {r.quarto.numero}" for r in reservas_hoje if r.data_saida.date() == hoje]},
        ]
    }

    return JsonResponse(data)