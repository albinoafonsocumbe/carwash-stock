from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from accounts.mixins import AdminRequiredMixin
from products.models import Product
from .forms import StockEntryForm, StockExitForm
from .models import StockMovement


class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'stock/list.html'
    context_object_name = 'movimentos'
    paginate_by = 20

    def get_queryset(self):
        return StockMovement.objects.filter(owner=self.request.user).select_related('produto').order_by('-data')


# Alias para a URL existente 'stock:list'
StockListView = StockMovementListView


class StockEntryCreateView(AdminRequiredMixin, FormView):
    template_name = 'stock/entry_form.html'
    form_class = StockEntryForm
    success_url = reverse_lazy('stock:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        produto = form.cleaned_data['produto']
        quantidade = form.cleaned_data['quantidade']

        with transaction.atomic():
            p = Product.objects.select_for_update().get(pk=produto.pk)
            p.quantidade += quantidade
            p.save(update_fields=['quantidade'])
            StockMovement.objects.create(
                produto=p,
                tipo='entrada',
                quantidade=quantidade,
                owner=self.request.user,
            )

        messages.success(self.request, f'Entrada de {quantidade} {produto.unidade} de "{produto.nome}" registada com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Registar Entrada de Stock'
        return ctx


class StockExitCreateView(LoginRequiredMixin, FormView):
    template_name = 'stock/exit_form.html'
    form_class = StockExitForm
    success_url = reverse_lazy('stock:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        produto = form.cleaned_data['produto']
        quantidade = form.cleaned_data['quantidade']

        with transaction.atomic():
            p = Product.objects.select_for_update().get(pk=produto.pk)
            if quantidade > p.quantidade:
                messages.error(
                    self.request,
                    f'Stock insuficiente. Disponível: {p.quantidade} {p.unidade}.'
                )
                return self.form_invalid(form)
            p.quantidade -= quantidade
            p.save(update_fields=['quantidade'])
            StockMovement.objects.create(
                produto=p,
                tipo='saida',
                quantidade=quantidade,
                owner=self.request.user,
            )

        messages.success(
            self.request,
            f'Saída de {quantidade} {produto.unidade} de "{produto.nome}" registada com sucesso.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Registar Saída de Stock'
        return ctx
