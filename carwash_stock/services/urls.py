from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='list'),
    path('novo/', views.ServiceCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ServiceUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ServiceDeleteView.as_view(), name='delete'),
    path('<int:pk>/executar/', views.ServiceExecutionView.as_view(), name='execute'),
]
