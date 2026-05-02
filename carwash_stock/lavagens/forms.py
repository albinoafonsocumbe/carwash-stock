from django import forms
from .models import Lavagem, TipoLavagem


class LavagemForm(forms.ModelForm):
    class Meta:
        model = Lavagem
        fields = ['matricula', 'tipo_lavagem', 'funcionario', 'valor_cobrado', 'foto', 'observacoes']
        labels = {
            'matricula': 'Matricula do Veiculo',
            'tipo_lavagem': 'Tipo de Lavagem',
            'funcionario': 'Funcionario Responsavel',
            'valor_cobrado': 'Valor Cobrado (MZN)',
            'foto': 'Foto do Veiculo',
            'observacoes': 'Observacoes',
        }
        widgets = {
            'matricula': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: ABC-1234',
                'style': 'text-transform:uppercase;font-weight:700;letter-spacing:.05em;'
            }),
            'tipo_lavagem': forms.Select(attrs={'class': 'form-select'}),
            'funcionario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do funcionario'}),
            'valor_cobrado': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observacoes adicionais...'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['tipo_lavagem'].queryset = TipoLavagem.objects.filter(is_active=True, owner=user)
        else:
            self.fields['tipo_lavagem'].queryset = TipoLavagem.objects.filter(is_active=True)
        self.fields['funcionario'].required = False
        self.fields['observacoes'].required = False

    def clean_matricula(self):
        return self.cleaned_data.get('matricula', '').upper().strip()


class TipoLavagemForm(forms.ModelForm):
    class Meta:
        model = TipoLavagem
        fields = ['nome', 'descricao', 'preco', 'duracao_minutos', 'is_active']
        labels = {
            'nome': 'Nome do Serviço',
            'descricao': 'Descrição',
            'preco': 'Preço (MZN)',
            'duracao_minutos': 'Duração (minutos)',
            'is_active': 'Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'duracao_minutos': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
