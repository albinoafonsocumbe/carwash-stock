from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsIndexView.as_view(), name='index'),
    path('produtos/', views.ProductReportView.as_view(), name='products'),
    path('stock/', views.StockReportView.as_view(), name='stock'),
    path('export/produtos/csv/', views.ExportProductCSVView.as_view(), name='export_products_csv'),
    path('export/produtos/pdf/', views.ExportProductPDFView.as_view(), name='export_products_pdf'),
    path('export/stock/csv/', views.ExportStockCSVView.as_view(), name='export_stock_csv'),
    path('export/stock/pdf/', views.ExportStockPDFView.as_view(), name='export_stock_pdf'),
]
