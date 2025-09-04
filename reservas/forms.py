from django import forms
from django.forms import DateInput
from .models import Reserva
from quartos.models import Quarto

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["nome_cliente", "email", "telefone", "quarto", "data_entrada", "data_saida"]
        widgets = {
            'data_entrada': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_saida': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quarto = cleaned_data.get("quarto")
        data_entrada = cleaned_data.get("data_entrada")
        data_saida = cleaned_data.get("data_saida")

        if quarto and data_entrada and data_saida:
            from quartos.models import Quarto
            if not quarto.esta_disponivel(data_entrada, data_saida):
                raise forms.ValidationError(
                    f"O quarto {quarto.tipo} - {quarto.numero} não está disponível nesse período."
                )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        data_entrada = kwargs.pop('data_entrada', None)
        data_saida = kwargs.pop('data_saida', None)
        super().__init__(*args, **kwargs)

        # Filtra apenas quartos ativos e disponíveis
        quartos = Quarto.objects.filter(ativo=True)
        if data_entrada and data_saida:
            quartos = [q for q in quartos if q.esta_disponivel(data_entrada, data_saida)]

        self.fields['quarto'].queryset = quartos
        self.fields['quarto'].widget.attrs.update({'class': 'form-control'})
