from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from accounts.mixins import AdminRequiredMixin
from .models import Product
from .forms import ProductForm
from .categories import CATEGORIAS


class CategoryListView(AdminRequiredMixin, TemplateView):
    template_name = 'products/category_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categorias'] = CATEGORIAS
        return ctx


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'produtos'
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.filter(owner=self.request.user)
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
        form.instance.owner = self.request.user
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

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nome}'
        ctx['btn_label'] = 'Guardar Alteracoes'
        return ctx


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:list')

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        produto = self.get_object()
        from stock.models import StockMovement
        if StockMovement.objects.filter(produto=produto).exists():
            messages.error(request, f'Nao e possivel eliminar "{produto.nome}" porque tem movimentacoes registadas.')
            return redirect('products:list')
        messages.success(request, f'Produto "{produto.nome}" eliminado.')
        return super().post(request, *args, **kwargs)
