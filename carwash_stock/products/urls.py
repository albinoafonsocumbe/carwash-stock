from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Produtos
    path('', views.ProductListView.as_view(), name='list'),
    path('novo/', views.ProductCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ProductUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ProductDeleteView.as_view(), name='delete'),
    # Categorias
    path('categorias/', views.CategoryListView.as_view(), name='categories'),
]
