from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from accounts.mixins import AdminRequiredMixin
from .models import Lavagem, TipoLavagem
from .forms import LavagemForm, TipoLavagemForm


class LavagemDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'lavagens/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.utils import timezone
        hoje = timezone.now().date()

        ctx['total_lavagens'] = Lavagem.objects.count()
        ctx['lavagens_hoje'] = Lavagem.objects.filter(data__date=hoje).count()
        ctx['receita_hoje'] = Lavagem.objects.filter(data__date=hoje).aggregate(
            t=Sum('valor_cobrado'))['t'] or 0
        ctx['receita_total'] = Lavagem.objects.aggregate(t=Sum('valor_cobrado'))['t'] or 0
        ctx['ultimas_lavagens'] = Lavagem.objects.select_related('tipo_lavagem').order_by('-data')[:10]
        ctx['tipos_lavagem'] = TipoLavagem.objects.filter(is_active=True)

        # Top serviços
        ctx['top_servicos'] = TipoLavagem.objects.annotate(
            total=Count('lavagem')
        ).order_by('-total')[:5]

        return ctx


class LavagemListView(LoginRequiredMixin, ListView):
    model = Lavagem
    template_name = 'lavagens/list.html'
    context_object_name = 'lavagens'
    paginate_by = 20

    def get_queryset(self):
        qs = Lavagem.objects.filter(owner=self.request.user).select_related('tipo_lavagem').order_by('-data')
        q = self.request.GET.get('q', '').strip()
        tipo = self.request.GET.get('tipo', '')
        if q:
            qs = qs.filter(matricula__icontains=q)
        if tipo:
            qs = qs.filter(tipo_lavagem_id=tipo)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['tipo_sel'] = self.request.GET.get('tipo', '')
        ctx['tipos'] = TipoLavagem.objects.filter(is_active=True, owner=self.request.user)
        return ctx


class LavagemCreateView(LoginRequiredMixin, CreateView):
    model = Lavagem
    form_class = LavagemForm
    template_name = 'lavagens/form.html'
    success_url = reverse_lazy('lavagens:list')

    def post(self, request, *args, **kwargs):
        self.object = None
        form = LavagemForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        tipo = form.cleaned_data.get('tipo_lavagem')
        if not self.request.user.is_admin():
            if tipo:
                form.instance.valor_cobrado = tipo.preco
            else:
                form.instance.valor_cobrado = 0
        else:
            if not form.cleaned_data.get('valor_cobrado') and tipo:
                form.instance.valor_cobrado = tipo.preco
        form.instance.owner = self.request.user
        messages.success(self.request, f'Lavagem registada para {form.instance.matricula}.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Registar Nova Lavagem'
        ctx['btn_label'] = 'Registar Lavagem'
        ctx['tipos_info'] = {t.id: {'preco': str(t.preco), 'duracao': t.duracao_minutos}
                             for t in TipoLavagem.objects.filter(is_active=True, owner=self.request.user)}
        return ctx


class LavagemDeleteView(AdminRequiredMixin, DeleteView):
    model = Lavagem
    template_name = 'lavagens/confirm_delete.html'
    success_url = reverse_lazy('lavagens:list')

    def post(self, request, *args, **kwargs):
        lav = self.get_object()
        messages.success(request, f'Lavagem de {lav.matricula} eliminada.')
        return super().post(request, *args, **kwargs)


# ── Tipos de Lavagem ──────────────────────────────────────────────────────────

class TipoLavagemListView(LoginRequiredMixin, ListView):
    model = TipoLavagem
    template_name = 'lavagens/tipos_list.html'
    context_object_name = 'tipos'

    def get_queryset(self):
        return TipoLavagem.objects.filter(owner=self.request.user).annotate(total=Count('lavagem')).order_by('nome')


class TipoLavagemCreateView(LoginRequiredMixin, CreateView):
    model = TipoLavagem
    form_class = TipoLavagemForm
    template_name = 'lavagens/tipo_form.html'
    success_url = reverse_lazy('lavagens:tipos')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Tipo de lavagem criado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Tipo de Lavagem'
        ctx['btn_label'] = 'Criar'
        return ctx


class TipoLavagemUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoLavagem
    form_class = TipoLavagemForm
    template_name = 'lavagens/tipo_form.html'
    success_url = reverse_lazy('lavagens:tipos')

    def get_queryset(self):
        return TipoLavagem.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de lavagem atualizado.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nome}'
        ctx['btn_label'] = 'Guardar'
        return ctx
