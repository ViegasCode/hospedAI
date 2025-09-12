from __future__ import annotations

import calendar
# reservas/views_api_reservas.py

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
# reservas/views.py (apenas os trechos relevantes)
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.decorators import api_view
from rest_framework.response import Response
from quartos.models import Quarto
from reservas.models import Reserva

STATUS_CONSIDERADOS = ["pendente", "confirmada"]

def intervalo_do_dia(d):
    tz = timezone.get_current_timezone()
    inicio = make_aware(datetime.combine(d, time.min), tz)
    fim = make_aware(datetime.combine(d, time.max), tz)
    return inicio, fim

@api_view(["GET"])
def calendario_dashboard(request):
    data_entrada = request.GET.get("data_entrada")
    data_saida = request.GET.get("data_saida")
    if not data_entrada or not data_saida:
        return Response({"error": "Forneça data_entrada e data_saida"}, status=400)

    d1 = date.fromisoformat(data_entrada)
    d2 = date.fromisoformat(data_saida)

    total_quartos = Quarto.objects.filter(ativo=True).count()

    calendario = []
    dia = d1
    while dia <= d2:
        ini, fim = intervalo_do_dia(dia)
        reservas_overlap = Reserva.objects.filter(
            status__in=STATUS_CONSIDERADOS,
            data_entrada__lte=fim,
            data_saida__gte=ini,
        )
        ocupados = reservas_overlap.values("quarto_id").distinct().count()
        livres = max(total_quartos - ocupados, 0)
        calendario.append({
            "day": dia.day,
            "date": dia.isoformat(),
            "free": livres,
            "occupied": ocupados,
        })
        dia += timedelta(days=1)

    # Dashboard do dia atual — mesma regra!
    hoje = timezone.localdate()
    ini_h, fim_h = intervalo_do_dia(hoje)
    reservas_hoje = Reserva.objects.filter(
        status__in=STATUS_CONSIDERADOS,
        data_entrada__lte=fim_h,
        data_saida__gte=ini_h,
    )
    ocupados_hoje = reservas_hoje.values("quarto_id").distinct().count()
    checkins = Reserva.objects.filter(
        status__in=STATUS_CONSIDERADOS,
        data_entrada__gte=ini_h, data_entrada__lte=fim_h
    ).count()
    checkouts = Reserva.objects.filter(
        status__in=STATUS_CONSIDERADOS,
        data_saida__gte=ini_h, data_saida__lte=fim_h
    ).count()

    return Response({
        "total_quartos": total_quartos,
        "calendario": calendario,
        "dashboard": {
            "livres": max(total_quartos - ocupados_hoje, 0),
            "ocupados": ocupados_hoje,
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


# reservas/views.py
from datetime import date, timedelta
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.utils.timezone import now
from quartos.models import Quarto
from .models import Reserva

def calendario_api(request):
    """
    JSON: disponibilidade diária no intervalo [data_entrada, data_saida]
    Cada item: {"day": 12, "date": "2025-09-12", "free": 3}
    E também um dashboard simples do dia de hoje.
    """
    di = parse_date(request.GET.get('data_entrada'))
    ds = parse_date(request.GET.get('data_saida'))

    # defaults: mês corrente se não vier filtro
    hoje = date.today()
    if not di:
        di = hoje.replace(day=1)
    if not ds:
        # último dia do mês de di
        first_next_month = (di.replace(day=28) + timedelta(days=4)).replace(day=1)
        ds = first_next_month - timedelta(days=1)

    total_quartos = Quarto.objects.filter(ativo=True).count()

    calendario = []
    d = di
    while d <= ds:
        # reservas que pegam o dia d (comparando só a data)
        ocupados_qs = Reserva.objects.filter(
            status__in=['pendente', 'confirmada'],
            data_entrada__date__lte=d,
            data_saida__date__gt=d
        ).values_list('quarto_id', flat=True).distinct()

        ocupados = len(set(ocupados_qs))
        livres = max(total_quartos - ocupados, 0)

        calendario.append({
            "day": d.day,
            "date": d.isoformat(),
            "free": livres,
        })
        d += timedelta(days=1)

    # Dashboard de hoje
    hoje_d = now().date()
    ocupados_hoje = Reserva.objects.filter(
        status__in=['pendente', 'confirmada'],
        data_entrada__date__lte=hoje_d,
        data_saida__date__gt=hoje_d
    ).values_list('quarto_id', flat=True).distinct()
    ocupados_hoje_ct = len(set(ocupados_hoje))
    livres_hoje_ct = max(total_quartos - ocupados_hoje_ct, 0)

    checkins_hoje = Reserva.objects.filter(
        status__in=['pendente', 'confirmada'],
        data_entrada__date=hoje_d
    ).count()
    checkouts_hoje = Reserva.objects.filter(
        status__in=['pendente', 'confirmada'],
        data_saida__date=hoje_d
    ).count()

    return JsonResponse({
        "total_quartos": total_quartos,
        "calendario": calendario,
        "dashboard": {
            "livres": livres_hoje_ct,
            "ocupados": ocupados_hoje_ct,
            "checkins": checkins_hoje,
            "checkouts": checkouts_hoje
        }
    })

from django.http import JsonResponse
from django.utils.timezone import make_aware
from datetime import datetime
from reservas.models import Reserva
from quartos.models import Quarto

def detalhes_dia(request):
    """
    Retorna listas para as três colunas (livres, ocupados, check-ins) de um dia específico.
    GET ?dia=YYYY-MM-DD
    """
    dia = request.GET.get("dia")
    if not dia:
        return JsonResponse({"error": "Informe ?dia=YYYY-MM-DD"}, status=400)

    start = make_aware(datetime.fromisoformat(dia + "T00:00:00"))
    end   = make_aware(datetime.fromisoformat(dia + "T23:59:59"))

    reservas_dia = Reserva.objects.filter(
        status__in=["pendente", "confirmada"],
        data_entrada__lte=end,
        data_saida__gte=start
    ).select_related("quarto")

    ocupados = [
        {
            "room": f"{r.quarto.tipo} {r.quarto.numero}",
            "checkout": r.data_saida.strftime("%d/%m"),
            "cliente": r.nome_cliente,
        }
        for r in reservas_dia
    ]

    livres_qs = Quarto.objects.filter(ativo=True).exclude(
        id__in=reservas_dia.values_list("quarto_id", flat=True)
    )
    livres = [{"room": f"{q.tipo} {q.numero}", "checkout": "-"} for q in livres_qs]

    checkins = [
        {
            "room": f"{r.quarto.tipo} {r.quarto.numero}",
            "checkout": r.data_saida.strftime("%d/%m"),
            "cliente": r.nome_cliente,
        }
        for r in Reserva.objects.filter(
            status__in=["pendente", "confirmada"], data_entrada__date=start.date()
        ).select_related("quarto")
    ]

    return JsonResponse({"free": livres, "occupied": ocupados, "checkins": checkins})

# reservas/views.py
from datetime import datetime
import calendar

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from reservas.models import Reserva
from quartos.models import Quarto



def _month_bounds(ano: int, mes: int):
    """(início_aware, fim_aware, dias_no_mes) para o mês."""
    first_day = datetime(ano, mes, 1, 0, 0, 0)
    last_day_num = calendar.monthrange(ano, mes)[1]
    last_moment = datetime(ano, mes, last_day_num, 23, 59, 59, 999999)

    if timezone.is_naive(first_day):
        first_day = timezone.make_aware(first_day)
    if timezone.is_naive(last_moment):
        last_moment = timezone.make_aware(last_moment)
    return first_day, last_moment, last_day_num


def _iso_local(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    dt = timezone.localtime(dt)
    return dt.replace(microsecond=0).isoformat()


import calendar
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from quartos.models import Quarto
from reservas.models import Reserva

def gantt_page(request):
    # Renderiza o template React/JSX que você já está usando
    return render(request, "reservas/gantt.html")

def gantt_api(request):
    """
    Retorna JSON no formato:
    {
      "ano": 2025, "mes": 9, "dias": 30,
      "quartos": [
        {"id": 1, "label": "101 · Standard", "reservas":[
           {"id": 55, "start": "2025-09-01T12:00:00-03:00", "end": "2025-09-03T12:00:00-03:00",
            "cliente": "João Silva", "status": "confirmada"}
        ]}
      ]
    }
    """
    # ano/mes vindos do front; default = mês atual
    try:
        ano = int(request.GET.get("ano") or datetime.now().year)
        mes = int(request.GET.get("mes") or datetime.now().month)
    except ValueError:
        now = datetime.now()
        ano, mes = now.year, now.month

    # limites do mês (timezone-aware)
    tz = timezone.get_current_timezone()
    mes_inicio = timezone.make_aware(datetime(ano, mes, 1, 0, 0, 0), tz)
    if mes == 12:
        mes_fim = timezone.make_aware(datetime(ano + 1, 1, 1, 0, 0, 0), tz)
    else:
        mes_fim = timezone.make_aware(datetime(ano, mes + 1, 1, 0, 0, 0), tz)

    # número de dias
    dias = calendar.monthrange(ano, mes)[1]

    # quartos ativos
    quartos_qs = Quarto.objects.filter(ativo=True).order_by("numero", "id")

    quartos_payload = []
    for q in quartos_qs:
        label = f"{q.numero} · {q.tipo}" if getattr(q, "numero", None) else (q.tipo or f"Quarto {q.id}")

        # reservas que INTERSECTAM o mês
        reservas_qs = Reserva.objects.filter(
            quarto=q,
            data_entrada__lt=mes_fim,
            data_saida__gt=mes_inicio,
            status__in=["pendente", "confirmada"]  # ajuste se usar outros status
        ).order_by("data_entrada")

        reservas_payload = []
        for r in reservas_qs:
            # isoformat com timezone
            start_iso = r.data_entrada.isoformat()
            end_iso = r.data_saida.isoformat()
            reservas_payload.append({
                "id": r.id,
                "start": start_iso,
                "end": end_iso,
                "cliente": getattr(r, "nome_cliente", "") or "",
                "status": (r.status or "confirmada").lower(),
            })

        quartos_payload.append({
            "id": q.id,
            "label": label,
            "reservas": reservas_payload,
        })

    payload = {
        "ano": ano,
        "mes": mes,
        "dias": dias,
        "quartos": quartos_payload,
    }
    return JsonResponse(payload, safe=True)
from datetime import date, datetime, timedelta
from django.http import JsonResponse
from django.utils.timezone import make_aware, is_aware, get_current_timezone
from reservas.models import Reserva
from quartos.models import Quarto

def _to_naive_date(s):
    # espera 'YYYY-MM-DD'
    return datetime.strptime(s, "%Y-%m-%d").date()

# reservas/views.py
from datetime import datetime, timedelta, time
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from quartos.models import Quarto
from reservas.models import Reserva

def _aware(dt: datetime) -> datetime:
    """Garante datetime timezone-aware conforme settings.USE_TZ."""
    if settings.USE_TZ and timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt

# reservas/views.py
from datetime import datetime, timedelta, time
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from quartos.models import Quarto
from reservas.models import Reserva

# reservas/views.py
from datetime import datetime, timedelta, time
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from quartos.models import Quarto
from reservas.models import Reserva

def _aware(dt: datetime) -> datetime:
    """Garante datetime timezone-aware conforme settings.USE_TZ."""
    if settings.USE_TZ and timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt

def gantt_window(request):
    """
    /reservas/api/gantt_window/?start=YYYY-MM-DD&days=30|60|90
    Retorna:
    {
      "window_start": "YYYY-MM-DD",
      "window_days": N,
      "quartos": [{
         "id": int, "label": "N · Tipo",
         "reservas": [{
            "id": int, "start": ISO8601, "end": ISO8601, "cliente": str, "status": str
         }]
      }, ...]
    }
    """
    # 1) parâmetros
    start_str = request.GET.get("start")
    days_str  = request.GET.get("days", "30")
    if not start_str:
        # default: 1º dia do mês atual
        today = timezone.localdate()
        start_str = today.replace(day=1).isoformat()

    try:
        days = max(1, min(90, int(days_str)))
    except ValueError:
        days = 30

    # 2) janela [start, end)
    #    start é meia-noite local do dia informado; end é exclusivo
    start_date = datetime.fromisoformat(start_str).date()
    start_dt = _aware(datetime.combine(start_date, time.min))
    end_dt   = start_dt + timedelta(days=days)

    # 3) busca quartos (todos, mesmo sem reserva)
    quartos_qs = Quarto.objects.all().order_by("id")  # troque para .order_by("numero") se preferir
    # 4) busca reservas QUE INTERSECTAM a janela (não apenas “no mês”)
    reservas_qs = (
        Reserva.objects
        .filter(status__in=["pendente", "confirmada", "cancelada"])
        .filter(data_entrada__lt=end_dt, data_saida__gt=start_dt)  # overlap verdadeira
        .select_related("quarto")
        .order_by("data_entrada")
    )

    # 5) indexa reservas por quarto
    by_quarto = {}
    for r in reservas_qs:
        by_quarto.setdefault(r.quarto_id, []).append({
            "id": r.id,
            "start": r.data_entrada.isoformat(),   # sem truncar!
            "end": r.data_saida.isoformat(),
            "cliente": r.nome_cliente or "",
            "status": r.status or "confirmada",
        })

    # 6) monta payload
    payload = {
        "window_start": start_date.isoformat(),
        "window_days": days,
        "quartos": []
    }

    for q in quartos_qs:
        label = f"{q.numero} · {q.tipo}" if getattr(q, "numero", None) else f"{q.id} · {q.tipo}"
        payload["quartos"].append({
            "id": q.id,
            "label": label,
            "reservas": by_quarto.get(q.id, [])
        })

    return JsonResponse(payload)


from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware, is_naive
import json

from .models import Reserva

from datetime import date, datetime, timedelta
from django.http import JsonResponse
from django.utils.timezone import make_aware, is_aware, get_current_timezone
from reservas.models import Reserva
from quartos.models import Quarto

def _to_naive_date(s):
    # espera 'YYYY-MM-DD'
    return datetime.strptime(s, "%Y-%m-%d").date()

def gantt_window_api(request):
    """
    GET /reservas/api/gantt_window/?start=YYYY-MM-DD&days=90
    Janela deslizante para o Gantt (mostra reservas que INTERSECTAM a janela).
    """
    tz = get_current_timezone()

    # parâmetros
    start_param = request.GET.get("start")
    days_param = request.GET.get("days")

    if start_param:
        window_start = _to_naive_date(start_param)
    else:
        # padrão: primeiro dia do mês corrente
        today = date.today()
        window_start = date(today.year, today.month, 1)

    window_days = int(days_param) if days_param else 90
    if window_days < 1:
        window_days = 90

    window_end_exclusive = window_start + timedelta(days=window_days)  # fim EXCLUSIVO

    # quartos (todos, inclusive sem reservas)
    quartos_qs = Quarto.objects.filter(ativo=True).order_by("numero", "id")

    # reservas que tocam a janela
    reservas_qs = Reserva.objects.filter(
        data_saida__date__gte=window_start,     # termina depois do início
        data_entrada__date__lt=window_end_exclusive  # começa antes do fim
    ).select_related("quarto")

    # indexar reservas por quarto
    by_quarto = {}
    for r in reservas_qs:
        qid = r.quarto_id if r.quarto_id else None
        if not qid:
            continue
        by_quarto.setdefault(qid, []).append(r)

    # quebras de mês (para o header)
    month_breaks = []
    cur = window_start
    last_label = None
    for i in range(window_days):
        d = window_start + timedelta(days=i)
        if d.day == 1 or i == 0:
            label = d.strftime("%b/%Y")  # ex.: Sep/2025
            month_breaks.append({"label": label, "offset": i})
            last_label = label

    # montar payload
    payload = {
        "window_start": window_start.isoformat(),
        "window_days": window_days,
        "month_breaks": month_breaks,
        "quartos": []
    }

    for q in quartos_qs:
        reservas_out = []
        for r in by_quarto.get(q.id, []):
            # datas aware -> isoformat
            dt_in = r.data_entrada if is_aware(r.data_entrada) else make_aware(r.data_entrada, tz)
            dt_out = r.data_saida if is_aware(r.data_saida) else make_aware(r.data_saida, tz)

            starts_before = dt_in.date() < window_start
            ends_after = dt_out.date() >= window_end_exclusive

            reservas_out.append({
                "id": r.id,
                "start": dt_in.isoformat(),
                "end": dt_out.isoformat(),
                "cliente": r.nome_cliente or "",
                "status": r.status or "confirmada",
                "starts_before_window": starts_before,
                "ends_after_window": ends_after,
            })

        label = f"{q.numero} · {q.tipo}" if getattr(q, "tipo", None) else f"{q.numero}"
        payload["quartos"].append({
            "id": q.id,
            "label": label,
            "reservas": reservas_out,
        })

    return JsonResponse(payload)


import json
from typing import Any, Dict

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404

from quartos.models import Quarto
from .models import Reserva


def _json(request: HttpRequest) -> Dict[str, Any]:
    try:
        body = request.body.decode("utf-8") if isinstance(request.body, (bytes, bytearray)) else request.body
        return json.loads(body or "{}")
    except Exception:
        return {}

def _to_aware(dt_str: str | None):
    """Converte ISO string para datetime c/ timezone. Aceita naive/aware."""
    if not dt_str:
        return None
    dt = parse_datetime(dt_str)
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt

def _reserva_to_dict(res: Reserva) -> Dict[str, Any]:
    """Forma usada em várias respostas JSON."""
    return {
        "id": res.id,
        "quarto": res.quarto_id,
        "tipo_quarto": res.tipo_quarto,
        "nome_cliente": res.nome_cliente,
        "email": res.email,
        "telefone": res.telefone,
        "status": res.status,
        "data_entrada": res.data_entrada.isoformat(),
        "data_saida": res.data_saida.isoformat(),
        # aliases úteis ao front do Gantt
        "cliente": res.nome_cliente,
        "start": res.data_entrada.isoformat(),
        "end": res.data_saida.isoformat(),
        "label_quarto": f"{res.quarto.numero} · {res.quarto.tipo}" if res.quarto_id else None,
    }

def _validate_status(val: str | None) -> str:
    allowed = {"pendente", "confirmada", "cancelada"}
    v = (val or "pendente").lower()
    if v not in allowed:
        raise ValueError(f"status inválido: {v}")
    return v

def _infer_tipo_quarto_from_quarto(quarto: Quarto) -> str:
    # seus choices de Reserva são: "standard", "luxo", "suite"
    return (quarto.tipo or "").lower()

@require_http_methods(["POST"])
# use UMA das duas linhas abaixo:
# 1) Se você já está enviando o csrftoken do template -> deixe csrf_protect
@csrf_protect
# 2) Se tiver erro de CSRF durante o deploy, troque para @csrf_exempt temporariamente
# @csrf_exempt
def reservas_create_api(request: HttpRequest):
    """
    POST /reservas/api/reservas/
    Payload esperado (JSON):
    {
      "quarto": 7,
      "nome_cliente": "...", "email": "...", "telefone": "...",
      "status": "confirmada" | "pendente" | "cancelada",
      "data_entrada": "2025-09-02T17:00:00Z",
      "data_saida":   "2025-09-05T15:00:00Z",
      "tipo_quarto": "standard|luxo|suite"  (opcional; será inferido do Quarto se ausente)
    }
    """
    data = _json(request)

    # Campos obrigatórios básicos
    quarto_id = data.get("quarto")
    if not quarto_id:
        return JsonResponse({"error": "Campo 'quarto' é obrigatório."}, status=400)

    quarto = get_object_or_404(Quarto, pk=quarto_id)

    nome_cliente = (data.get("nome_cliente") or "").strip()
    email = (data.get("email") or "").strip()
    telefone = (data.get("telefone") or "").strip()
    if not nome_cliente:
        return JsonResponse({"error": "Campo 'nome_cliente' é obrigatório."}, status=400)

    dt_in = _to_aware(data.get("data_entrada"))
    dt_out = _to_aware(data.get("data_saida"))
    if not dt_in or not dt_out:
        return JsonResponse({"error": "Data/hora de entrada e saída são obrigatórias (ISO)."}, status=400)
    if dt_out <= dt_in:
        return JsonResponse({"error": "data_saida deve ser maior que data_entrada."}, status=400)

    try:
        status = _validate_status(data.get("status"))
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    tipo_quarto = (data.get("tipo_quarto") or "").strip().lower()
    if not tipo_quarto:
        tipo_quarto = _infer_tipo_quarto_from_quarto(quarto)

    # (Opcional) checar conflito simples de ocupação aqui se quiser…

    res = Reserva.objects.create(
        nome_cliente=nome_cliente,
        email=email,
        telefone=telefone,
        tipo_quarto=tipo_quarto,
        data_entrada=dt_in,
        data_saida=dt_out,
        status=status,
        quarto=quarto,
    )

    return JsonResponse(_reserva_to_dict(res), status=201)


from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone

@require_http_methods(["PATCH", "PUT"])
@csrf_exempt  # se preferir CSRF, troque para @csrf_protect e garanta o X-CSRFToken no fetch
def reserva_update_api(request, pk: int):
    res = get_object_or_404(Reserva, pk=pk)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # status
    st = payload.get("status")
    if st in {"pendente", "confirmada", "cancelada"}:
        res.status = st

    # datas — aceita data_entrada/data_saida OU start/end
    start_iso = payload.get("data_entrada") or payload.get("start")
    end_iso   = payload.get("data_saida")   or payload.get("end")

    def _aware(dt_str):
        if not dt_str: return None
        dt = parse_datetime(dt_str)
        if dt is None: return None
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    if start_iso or end_iso:
        dt_in  = _aware(start_iso) or res.data_entrada
        dt_out = _aware(end_iso)   or res.data_saida
        if dt_out <= dt_in:
            return JsonResponse({"error":"data_saida deve ser maior que data_entrada."}, status=400)
        res.data_entrada = dt_in
        res.data_saida   = dt_out

    # mudar quarto (opcional)
    if "quarto" in payload and payload["quarto"]:
        q = get_object_or_404(Quarto, pk=payload["quarto"])
        res.quarto = q
        res.tipo_quarto = (q.tipo or "").lower()

    res.save()

    return JsonResponse({
        "id": res.id,
        "quarto": res.quarto_id,
        "status": res.status,
        "nome_cliente": res.nome_cliente,
        "data_entrada": res.data_entrada.isoformat(),
        "data_saida": res.data_saida.isoformat(),
    })

