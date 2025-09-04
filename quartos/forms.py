from django import forms
from .models import Quarto, FotoQuarto

class QuartoForm(forms.ModelForm):
    class Meta:
        model = Quarto
        fields = ['numero', 'tipo', 'capacidade', 'tarifa', 'ativo', 'servicos']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 101'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'capacidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2'}),
            'tarifa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 250.00'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'servicos': forms.CheckboxSelectMultiple(),
        }

class FotoQuartoForm(forms.ModelForm):
    class Meta:
        model = FotoQuarto
        fields = ['quarto', 'imagem', 'descricao']
