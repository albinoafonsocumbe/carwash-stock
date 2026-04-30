from django.urls import path
from . import views

app_name = 'lavagens'

urlpatterns = [
    path('', views.LavagemDashboardView.as_view(), name='dashboard'),
    path('historico/', views.LavagemListView.as_view(), name='list'),
    path('nova/', views.LavagemCreateView.as_view(), name='create'),
    path('<int:pk>/eliminar/', views.LavagemDeleteView.as_view(), name='delete'),
    path('tipos/', views.TipoLavagemListView.as_view(), name='tipos'),
    path('tipos/novo/', views.TipoLavagemCreateView.as_view(), name='tipo_create'),
    path('tipos/<int:pk>/editar/', views.TipoLavagemUpdateView.as_view(), name='tipo_update'),
]
