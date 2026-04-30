import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.db.models import Sum

from accounts.mixins import AdminRequiredMixin
from products.models import Product
from stock.models import StockMovement


class ReportsIndexView(AdminRequiredMixin, TemplateView):
    template_name = 'reports/index.html'


class ProductReportView(AdminRequiredMixin, TemplateView):
    template_name = 'reports/product_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        data = []
        for p in Product.objects.all().order_by('nome'):
            entradas = StockMovement.objects.filter(produto=p, tipo='entrada').aggregate(t=Sum('quantidade'))['t'] or 0
            saidas = StockMovement.objects.filter(produto=p, tipo='saida').aggregate(t=Sum('quantidade'))['t'] or 0
            data.append({'produto': p, 'entradas': entradas, 'saidas': saidas, 'stock_atual': p.quantidade})
        ctx['data'] = data
        return ctx


class StockReportView(AdminRequiredMixin, TemplateView):
    template_name = 'reports/stock_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        qs = StockMovement.objects.select_related('produto').order_by('-data')
        if data_inicio:
            qs = qs.filter(data__date__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data__date__lte=data_fim)
        ctx['movimentos'] = qs
        ctx['data_inicio'] = data_inicio
        ctx['data_fim'] = data_fim
        ctx['total_entradas'] = qs.filter(tipo='entrada').aggregate(t=Sum('quantidade'))['t'] or 0
        ctx['total_saidas'] = qs.filter(tipo='saida').aggregate(t=Sum('quantidade'))['t'] or 0
        return ctx


# ─── PDF helper ─────────────────────────────────────────────────────────────

def _draw_page(canvas, doc, title):
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    w, h = doc.pagesize
    canvas.saveState()
    # Cabeçalho azul
    canvas.setFillColor(colors.HexColor('#1a56db'))
    canvas.rect(0, h - 2.5 * cm, w, 2.5 * cm, fill=True, stroke=False)
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 15)
    canvas.drawString(1.5 * cm, h - 1.45 * cm, 'CarWash Stock')
    canvas.setFont('Helvetica', 10)
    canvas.drawString(1.5 * cm, h - 2.05 * cm, title)
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(w - 1.5 * cm, h - 1.75 * cm, datetime.now().strftime('%d/%m/%Y %H:%M'))
    # Rodapé
    canvas.setFillColor(colors.HexColor('#94a3b8'))
    canvas.setFont('Helvetica', 8)
    canvas.drawString(1.5 * cm, 0.8 * cm, 'CarWash Stock — Sistema de Gestão de Inventário')
    canvas.drawRightString(w - 1.5 * cm, 0.8 * cm, f'Página {doc.page}')
    canvas.restoreState()


# ─── PDF Produtos ────────────────────────────────────────────────────────────

class ExportProductPDFView(AdminRequiredMixin, View):
    def get(self, request):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            topMargin=3.5*cm, bottomMargin=2*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)

        title_s = ParagraphStyle('t', fontSize=13, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#1e293b'), spaceAfter=4)
        sub_s = ParagraphStyle('s', fontSize=9, fontName='Helvetica',
                                textColor=colors.HexColor('#64748b'), spaceAfter=14)

        elements = [
            Paragraph('Relatório de Produtos', title_s),
            Paragraph(f'Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}', sub_s),
        ]

        headers = ['Produto', 'Unidade', 'Stock Atual', 'Entradas', 'Saídas', 'Estado']
        rows = [headers]
        for p in Product.objects.all().order_by('nome'):
            ent = StockMovement.objects.filter(produto=p, tipo='entrada').aggregate(t=Sum('quantidade'))['t'] or 0
            sai = StockMovement.objects.filter(produto=p, tipo='saida').aggregate(t=Sum('quantidade'))['t'] or 0
            rows.append([p.nome, p.unidade, str(p.quantidade), str(ent), str(sai),
                         'Alerta' if p.tem_alerta else 'Normal'])

        t = Table(rows, colWidths=[5.5*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm], repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a56db')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), 8.5),
            ('ALIGN', (2,1), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,1), (-1,-1), 6), ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        elements.append(t)

        doc.build(elements,
                  onFirstPage=lambda c, d: _draw_page(c, d, 'Relatório de Produtos'),
                  onLaterPages=lambda c, d: _draw_page(c, d, 'Relatório de Produtos'))
        buffer.seek(0)
        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="relatorio_produtos.pdf"'
        return resp


# ─── PDF Movimentações ───────────────────────────────────────────────────────

class ExportStockPDFView(AdminRequiredMixin, View):
    def get(self, request):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle

        data_inicio = request.GET.get('data_inicio', '')
        data_fim = request.GET.get('data_fim', '')
        qs = StockMovement.objects.select_related('produto').order_by('-data')
        if data_inicio:
            qs = qs.filter(data__date__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data__date__lte=data_fim)

        total_e = qs.filter(tipo='entrada').aggregate(t=Sum('quantidade'))['t'] or 0
        total_s = qs.filter(tipo='saida').aggregate(t=Sum('quantidade'))['t'] or 0

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            topMargin=3.5*cm, bottomMargin=2*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)

        title_s = ParagraphStyle('t', fontSize=13, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#1e293b'), spaceAfter=4)
        sub_s = ParagraphStyle('s', fontSize=9, fontName='Helvetica',
                                textColor=colors.HexColor('#64748b'), spaceAfter=10)

        periodo = f' | Período: {data_inicio or "—"} a {data_fim or "—"}' if (data_inicio or data_fim) else ''
        elements = [
            Paragraph('Relatório de Movimentações', title_s),
            Paragraph(f'Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}{periodo}', sub_s),
        ]

        # Resumo
        summary = Table(
            [['Total Entradas', 'Total Saídas'], [str(total_e), str(total_s)]],
            colWidths=[4*cm, 4*cm])
        summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TEXTCOLOR', (0,1), (0,1), colors.HexColor('#16a34a')),
            ('TEXTCOLOR', (1,1), (1,1), colors.HexColor('#dc2626')),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'), ('FONTSIZE', (0,1), (-1,1), 13),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ]))
        elements.append(summary)
        elements.append(Spacer(1, 0.4*cm))

        headers = ['Data', 'Produto', 'Tipo', 'Quantidade', 'Unidade']
        rows = [headers]
        for m in qs:
            rows.append([
                m.data.strftime('%d/%m/%Y %H:%M'),
                m.produto.nome,
                'Entrada' if m.tipo == 'entrada' else 'Saída',
                str(m.quantidade),
                m.produto.unidade,
            ])

        t = Table(rows, colWidths=[3.5*cm, 6*cm, 2.5*cm, 2.5*cm, 2*cm], repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a56db')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), 8.5),
            ('ALIGN', (2,1), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,1), (-1,-1), 6), ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        elements.append(t)

        doc.build(elements,
                  onFirstPage=lambda c, d: _draw_page(c, d, 'Relatório de Movimentações'),
                  onLaterPages=lambda c, d: _draw_page(c, d, 'Relatório de Movimentações'))
        buffer.seek(0)
        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="relatorio_movimentacoes.pdf"'
        return resp


# ─── CSV (mantido) ───────────────────────────────────────────────────────────

class ExportProductCSVView(AdminRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="relatorio_produtos.csv"'
        response.write('\ufeff')
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Produto', 'Unidade', 'Stock Atual', 'Total Entradas', 'Total Saídas'])
        for p in Product.objects.all().order_by('nome'):
            ent = StockMovement.objects.filter(produto=p, tipo='entrada').aggregate(t=Sum('quantidade'))['t'] or 0
            sai = StockMovement.objects.filter(produto=p, tipo='saida').aggregate(t=Sum('quantidade'))['t'] or 0
            writer.writerow([p.nome, p.unidade, p.quantidade, ent, sai])
        return response


class ExportStockCSVView(AdminRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="relatorio_movimentacoes.csv"'
        response.write('\ufeff')
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Data', 'Produto', 'Tipo', 'Quantidade', 'Unidade'])
        qs = StockMovement.objects.select_related('produto').order_by('-data')
        di = request.GET.get('data_inicio', '')
        df = request.GET.get('data_fim', '')
        if di:
            qs = qs.filter(data__date__gte=di)
        if df:
            qs = qs.filter(data__date__lte=df)
        for m in qs:
            writer.writerow([m.data.strftime('%d/%m/%Y %H:%M'), m.produto.nome,
                             m.get_tipo_display(), m.quantidade, m.produto.unidade])
        return response
