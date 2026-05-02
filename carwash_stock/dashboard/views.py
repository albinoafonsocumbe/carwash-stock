from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.db.models import Sum

        hoje = timezone.now().date()

        # Defaults seguros
        ctx.update({
            'total_produtos': 0,
            'produtos_alerta': [],
            'produtos_normais': 0,
            'total_entradas_hoje': 0,
            'total_saidas_hoje': 0,
            'ultimas_movimentacoes': [],
            'total_lavagens': 0,
            'lavagens_hoje': 0,
            'receita_hoje': 0,
            'receita_total': 0,
            'ultimas_lavagens': [],
            'top_produtos': [],
        })

        try:
            from products.models import Product
            todos_produtos = list(Product.objects.filter(owner=self.request.user))
            ctx['total_produtos'] = len(todos_produtos)
            ctx['produtos_alerta'] = [p for p in todos_produtos if p.tem_alerta]
            ctx['produtos_normais'] = len(todos_produtos) - len(ctx['produtos_alerta'])
            ctx['top_produtos'] = todos_produtos[:5]
        except Exception:
            pass

        try:
            from stock.models import StockMovement
            ctx['total_entradas_hoje'] = StockMovement.objects.filter(owner=self.request.user, tipo='entrada', data__date=hoje).count()
            ctx['total_saidas_hoje'] = StockMovement.objects.filter(owner=self.request.user, tipo='saida', data__date=hoje).count()
            ctx['ultimas_movimentacoes'] = list(StockMovement.objects.filter(owner=self.request.user).select_related('produto').order_by('-data')[:8])
        except Exception:
            pass

        try:
            from lavagens.models import Lavagem
            ctx['total_lavagens'] = Lavagem.objects.filter(owner=self.request.user).count()
            ctx['lavagens_hoje'] = Lavagem.objects.filter(owner=self.request.user, data__date=hoje).count()
            ctx['receita_hoje'] = Lavagem.objects.filter(owner=self.request.user, data__date=hoje).aggregate(t=Sum('valor_cobrado'))['t'] or 0
            ctx['receita_total'] = Lavagem.objects.filter(owner=self.request.user).aggregate(t=Sum('valor_cobrado'))['t'] or 0
            ctx['ultimas_lavagens'] = list(Lavagem.objects.filter(owner=self.request.user).select_related('tipo_lavagem').order_by('-data')[:5])
        except Exception:
            pass

        return ctx
