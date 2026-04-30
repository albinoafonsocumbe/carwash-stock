from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from products.models import Product
        from stock.models import StockMovement
        from lavagens.models import Lavagem
        from django.db.models import Sum, Count

        hoje = timezone.now().date()
        todos_produtos = list(Product.objects.all())

        # Produtos
        ctx['total_produtos'] = len(todos_produtos)
        ctx['produtos_alerta'] = [p for p in todos_produtos if p.tem_alerta]
        ctx['produtos_normais'] = len(todos_produtos) - len(ctx['produtos_alerta'])

        # Stock hoje
        ctx['total_entradas_hoje'] = StockMovement.objects.filter(tipo='entrada', data__date=hoje).count()
        ctx['total_saidas_hoje'] = StockMovement.objects.filter(tipo='saida', data__date=hoje).count()
        ctx['ultimas_movimentacoes'] = StockMovement.objects.select_related('produto').order_by('-data')[:8]

        # Lavagens
        ctx['total_lavagens'] = Lavagem.objects.count()
        ctx['lavagens_hoje'] = Lavagem.objects.filter(data__date=hoje).count()
        ctx['receita_hoje'] = Lavagem.objects.filter(data__date=hoje).aggregate(t=Sum('valor_cobrado'))['t'] or 0
        ctx['receita_total'] = Lavagem.objects.aggregate(t=Sum('valor_cobrado'))['t'] or 0
        ctx['ultimas_lavagens'] = Lavagem.objects.select_related('tipo_lavagem').order_by('-data')[:5]

        # Resumo de stock por produto (top 5 com mais movimento)
        ctx['top_produtos'] = todos_produtos[:5]

        return ctx
