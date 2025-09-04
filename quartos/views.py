from django.shortcuts import render, redirect
from .models import Quarto
from datetime import datetime
from .forms import QuartoForm
from .models import FotoQuarto

def listar_quartos(request):
    data_entrada = request.GET.get('data_entrada')
    data_saida = request.GET.get('data_saida')

    quartos = Quarto.objects.filter(ativo=True)

    try:
        if data_entrada and data_saida:
            data_entrada = datetime.strptime(data_entrada, "%Y-%m-%d").date()
            data_saida = datetime.strptime(data_saida, "%Y-%m-%d").date()
        else:
            data_entrada = data_saida = None
    except:
        data_entrada = data_saida = None

    # Filtra quartos disponíveis

    if data_entrada and data_saida:
        quartos = [q for q in quartos if q.esta_disponivel(data_entrada, data_saida)]

    context = {
        'quartos': quartos,
    }

    return render(request, 'quartos/listar_quartos.html', context)

def criar_quarto(request):
    if request.method == 'POST':
        form = QuartoForm(request.POST)
        if form.is_valid():
            quarto = form.save()
            # Salvar múltiplas fotos
            for img in request.FILES.getlist('fotos'):
                FotoQuarto.objects.create(quarto=quarto, imagem=img)
            return redirect('criar_quarto')  # volta para o formulário ou ajuste para outra página
    else:
        form = QuartoForm()
    return render(request, 'quartos/criar_quartos.html', {'form': form})