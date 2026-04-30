from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from accounts.mixins import AdminRequiredMixin
from .models import Product
from .forms import ProductForm, CategoryFilterForm
from .categories import CATEGORIAS, CATEGORIAS_DICT


# ---------------------------------------------------------------------------
# Categorias (geridas como lista hardcoded — sem tabela própria)
# ---------------------------------------------------------------------------

class CategoryListView(AdminRequiredMixin, TemplateView):
    template_name = 'products/category_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Para cada categoria, conta quantos produtos existem
        # (campo 'unidade' não guarda categoria; mostramos apenas a lista)
        ctx['categorias'] = CATEGORIAS
        return ctx


# ---------------------------------------------------------------------------
# Produtos
# ---------------------------------------------------------------------------

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'produtos'
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(nome__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:list')

    def form_valid(self, form):
        messages.success(self.request, 'Produto criado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Produto'
        ctx['btn_label'] = 'Criar Produto'
        return ctx


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:list')

    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nome}'
        ctx['btn_label'] = 'Guardar Alterações'
        return ctx


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:list')

    def post(self, request, *args, **kwargs):
        produto = self.get_object()
        # Verificar se existem movimentações associadas
        from stock.models import StockMovement
        if StockMovement.objects.filter(produto=produto).exists():
            messages.error(
                request,
                f'Não é possível eliminar "{produto.nome}" porque tem movimentações de stock registadas.'
            )
            return redirect('products:list')
        messages.success(request, f'Produto "{produto.nome}" eliminado.')
        return super().post(request, *args, **kwargs)
