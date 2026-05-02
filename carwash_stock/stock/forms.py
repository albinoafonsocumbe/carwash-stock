from django import forms
from products.models import Product
from .models import StockMovement


class StockEntryForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        label='Produto',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    quantidade = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01,
        label='Quantidade',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['produto'].queryset = Product.objects.filter(owner=user).order_by('nome')

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is not None and quantidade <= 0:
            raise forms.ValidationError('A quantidade deve ser um valor positivo.')
        return quantidade


class StockExitForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        label='Produto',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    quantidade = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01,
        label='Quantidade',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['produto'].queryset = Product.objects.filter(owner=user).order_by('nome')

    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get('produto')
        quantidade = cleaned_data.get('quantidade')
        if produto and quantidade is not None:
            if quantidade <= 0:
                self.add_error('quantidade', 'A quantidade deve ser um valor positivo.')
            elif quantidade > produto.quantidade:
                self.add_error('quantidade', f'Stock insuficiente. Disponivel: {produto.quantidade} {produto.unidade}.')
        return cleaned_data
