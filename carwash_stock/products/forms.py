from django import forms
from .models import Product
from .categories import CATEGORIAS, get_categorias_choices


class CategoryFilterForm(forms.Form):
    """Formulário de filtro por categoria na listagem de produtos."""
    categoria = forms.ChoiceField(
        choices=get_categorias_choices,
        required=False,
        label='Categoria',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class ProductForm(forms.ModelForm):
    """Formulário de criação/edição de produto."""

    class Meta:
        model = Product
        fields = ['nome', 'unidade', 'quantidade', 'preco', 'nivel_minimo']
        labels = {
            'nome': 'Nome do Produto',
            'unidade': 'Unidade de Medida',
            'quantidade': 'Quantidade em Stock',
            'preco': 'Preco Unitario (MZN)',
            'nivel_minimo': 'Nivel Minimo de Alerta',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Champo Auto'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: L, kg, un'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'nivel_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError('A quantidade não pode ser negativa.')
        return quantidade

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco < 0:
            raise forms.ValidationError('O preço não pode ser negativo.')
        return preco

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()
        if not nome:
            raise forms.ValidationError('O nome do produto é obrigatório.')
        # Verificar unicidade (excluindo o próprio produto em edição)
        qs = Product.objects.filter(nome__iexact=nome)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe um produto com este nome.')
        return nome
