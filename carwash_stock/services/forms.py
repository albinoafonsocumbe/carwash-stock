from django import forms
from django.forms import inlineformset_factory

from .models import Service, ServiceProduct
from products.models import Product


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nome', 'descricao', 'preco', 'tempo_estimado', 'foto', 'ativo']
        labels = {
            'nome': 'Nome do Serviço',
            'descricao': 'Descrição',
            'preco': 'Preço (MZN)',
            'tempo_estimado': 'Tempo Estimado (minutos)',
            'foto': 'Foto do Serviço',
            'ativo': 'Serviço Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Lavagem Completa Premium'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva o que inclui este serviço...'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'tempo_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '30'
            }),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()
        qs = Service.objects.filter(nome__iexact=nome)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe um serviço com este nome.')
        return nome

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco < 0:
            raise forms.ValidationError('O preço não pode ser negativo.')
        return preco


class ServiceProductForm(forms.ModelForm):
    class Meta:
        model = ServiceProduct
        fields = ['produto', 'quantidade_usada']
        labels = {
            'produto': 'Produto',
            'quantidade_usada': 'Quantidade por Execução',
        }
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_usada': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}
            ),
        }

    def clean_quantidade_usada(self):
        qty = self.cleaned_data.get('quantidade_usada')
        if qty is not None and qty <= 0:
            raise forms.ValidationError('A quantidade deve ser positiva.')
        return qty


ServiceProductFormSet = inlineformset_factory(
    Service,
    ServiceProduct,
    form=ServiceProductForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class ServiceExecutionForm(forms.Form):
    quantidade_execucoes = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Número de Execuções',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
    )
