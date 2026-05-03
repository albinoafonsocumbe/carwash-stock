from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('registar/', views.RegisterView.as_view(), name='register'),
    path('utilizadores/', views.UserListView.as_view(), name='user_list'),
    path('utilizadores/novo/', views.UserCreateView.as_view(), name='user_create'),
    path('utilizadores/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_update'),
    path('utilizadores/<int:pk>/toggle/', views.UserToggleActiveView.as_view(), name='user_toggle'),
    path('elevar/', views.elevate_to_admin, name='elevate'),
    # Recuperacao de senha
    path('recuperar/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('recuperar/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
