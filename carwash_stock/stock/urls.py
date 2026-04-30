from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.StockMovementListView.as_view(), name='list'),
    path('entradas/nova/', views.StockEntryCreateView.as_view(), name='entry_create'),
    path('saidas/nova/', views.StockExitCreateView.as_view(), name='exit_create'),
]
