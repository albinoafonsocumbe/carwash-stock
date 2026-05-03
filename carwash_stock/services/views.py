from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from accounts.mixins import AdminRequiredMixin
from .models import Service, ServiceProduct
from .forms import ServiceForm, ServiceProductFormSet, ServiceExecutionForm
from stock.models import StockMovement
from products.models import Product


class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'servicos'

    def get_queryset(self):
        return Service.objects.prefetch_related('produtos__produto').order_by('nome')


class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('services:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = ServiceProductFormSet(self.request.POST, instance=self.object)
        else:
            ctx['formset'] = ServiceProductFormSet(instance=self.object)
        ctx['titulo'] = 'Novo Serviço'
        ctx['btn_label'] = 'Criar Serviço'
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = None
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
            formset = ServiceProductFormSet(self.request.POST, instance=self.object)
            if formset.is_valid():
                formset.save()
        messages.success(self.request, f'Serviço "{self.object.nome}" criado com sucesso.')
        return redirect(self.success_url)


class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('services:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = ServiceProductFormSet(self.request.POST, instance=self.object)
        else:
            ctx['formset'] = ServiceProductFormSet(instance=self.object)
        ctx['titulo'] = f'Editar: {self.object.nome}'
        ctx['btn_label'] = 'Guardar Alterações'
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ServiceForm(request.POST, request.FILES, instance=self.object)
        if form.is_valid():
            return self.form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
            formset = ServiceProductFormSet(self.request.POST, instance=self.object)
            if formset.is_valid():
                formset.save()
        messages.success(self.request, f'Serviço "{self.object.nome}" atualizado com sucesso.')
        return redirect(self.success_url)


class ServiceDeleteView(AdminRequiredMixin, DeleteView):
    model = Service
    template_name = 'services/service_confirm_delete.html'
    success_url = reverse_lazy('services:list')

    def post(self, request, *args, **kwargs):
        servico = self.get_object()
        messages.success(request, f'Serviço "{servico.nome}" eliminado.')
        return super().post(request, *args, **kwargs)


class ServiceExecutionView(LoginRequiredMixin, FormView):
    template_name = 'services/execution_form.html'
    form_class = ServiceExecutionForm
    success_url = reverse_lazy('services:list')

    def get_servico(self):
        return get_object_or_404(Service, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        servico = self.get_servico()
        ctx['servico'] = servico
        ctx['produtos_servico'] = servico.produtos.select_related('produto').all()
        return ctx

    def form_valid(self, form):
        servico = self.get_servico()
        n = form.cleaned_data['quantidade_execucoes']
        produtos_servico = list(servico.produtos.select_related('produto').all())

        insuficientes = []
        for sp in produtos_servico:
            necessario = sp.quantidade_usada * n
            if sp.produto.quantidade < necessario:
                insuficientes.append({
                    'nome': sp.produto.nome,
                    'disponivel': sp.produto.quantidade,
                    'necessario': necessario,
                    'unidade': sp.produto.unidade,
                })

        if insuficientes:
            ctx = self.get_context_data(form=form)
            ctx['insuficientes'] = insuficientes
            return self.render_to_response(ctx)

        with transaction.atomic():
            for sp in produtos_servico:
                necessario = sp.quantidade_usada * n
                p = Product.objects.select_for_update().get(pk=sp.produto.pk)
                p.quantidade -= necessario
                p.save(update_fields=['quantidade'])
                StockMovement.objects.create(
                    produto=p,
                    tipo='saida',
                    quantidade=necessario,
                )

        messages.success(
            self.request,
            f'Serviço "{servico.nome}" executado {n}x com sucesso. Stock atualizado.'
        )
        return redirect(self.success_url)
