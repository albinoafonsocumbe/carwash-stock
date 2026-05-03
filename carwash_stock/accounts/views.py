from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django import forms as django_forms
from django.utils import timezone
from datetime import timedelta

from accounts.mixins import AdminRequiredMixin
from .models import User


# ─── Backend de autenticacao por email ───────────────────────────────────────

class EmailBackend:
    """Autentica usando email em vez de username."""

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email__iexact=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# ─── Controlo de tentativas de login ─────────────────────────────────────────

_login_attempts = {}  # {ip: {'count': int, 'last': datetime}}
MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _is_locked(ip):
    data = _login_attempts.get(ip)
    if not data:
        return False, 0
    if data['count'] >= MAX_ATTEMPTS:
        elapsed = timezone.now() - data['last']
        remaining = LOCKOUT_MINUTES - int(elapsed.total_seconds() / 60)
        if remaining > 0:
            return True, remaining
        else:
            _login_attempts.pop(ip, None)
    return False, 0


def _record_attempt(ip, success):
    if success:
        _login_attempts.pop(ip, None)
        return
    data = _login_attempts.get(ip, {'count': 0, 'last': timezone.now()})
    data['count'] += 1
    data['last'] = timezone.now()
    _login_attempts[ip] = data


# ─── Views de autenticacao ────────────────────────────────────────────────────

class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        ip = _get_client_ip(request)

        # Verificar bloqueio
        locked, remaining = _is_locked(ip)
        if locked:
            messages.error(request, f'Conta temporariamente bloqueada. Tente novamente em {remaining} minuto(s).')
            return render(request, self.template_name, {'email': email, 'locked': True, 'remaining': remaining})

        # Tentar autenticar por email
        user = None
        try:
            u = User.objects.get(email__iexact=email)
            if u.check_password(password):
                user = u
        except User.DoesNotExist:
            pass

        if user is not None:
            if not user.is_active:
                messages.error(request, 'A sua conta esta desativada. Contacte o administrador.')
                _record_attempt(ip, False)
                return render(request, self.template_name, {'email': email})

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            _record_attempt(ip, True)

            # Redirecionar por perfil
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:index')
        else:
            _record_attempt(ip, False)
            data = _login_attempts.get(ip, {})
            remaining_attempts = MAX_ATTEMPTS - data.get('count', 0)
            if remaining_attempts <= 2:
                messages.error(request, f'Email ou palavra-passe incorretos. Restam {remaining_attempts} tentativa(s).')
            else:
                messages.error(request, 'Email ou palavra-passe incorretos.')
            return render(request, self.template_name, {'email': email})


class LogoutView(View):
    def post(self, request):
        # Limpar elevacao de perfil antes de fazer logout
        request.session.pop('perfil_elevado', None)
        logout(request)
        return redirect('accounts:login')

    def get(self, request):
        request.session.pop('perfil_elevado', None)
        logout(request)
        return redirect('accounts:login')


# ─── Formularios de utilizador ────────────────────────────────────────────────

class UserCreateForm(django_forms.ModelForm):
    password = django_forms.CharField(
        label='Palavra-passe',
        widget=django_forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text='Minimo 8 caracteres',
    )
    password_confirm = django_forms.CharField(
        label='Confirmar palavra-passe',
        widget=django_forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'perfil']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Apelido',
            'email': 'Email (usado para login)',
            'username': 'Nome de utilizador',
            'perfil': 'Perfil de acesso',
        }
        widgets = {
            'first_name': django_forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': django_forms.TextInput(attrs={'class': 'form-control'}),
            'email': django_forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@email.com'}),
            'username': django_forms.TextInput(attrs={'class': 'form-control'}),
            'perfil': django_forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise django_forms.ValidationError('Ja existe uma conta com este email.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'As palavras-passe nao coincidem.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserUpdateForm(django_forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'perfil', 'is_active']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Apelido',
            'email': 'Email',
            'username': 'Nome de utilizador',
            'perfil': 'Perfil de acesso',
            'is_active': 'Conta ativa',
        }
        widgets = {
            'first_name': django_forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': django_forms.TextInput(attrs={'class': 'form-control'}),
            'email': django_forms.EmailInput(attrs={'class': 'form-control'}),
            'username': django_forms.TextInput(attrs={'class': 'form-control'}),
            'perfil': django_forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise django_forms.ValidationError('Ja existe uma conta com este email.')
        return email


# ─── Views de utilizadores ────────────────────────────────────────────────────

class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'utilizadores'

    def get_queryset(self):
        return User.objects.all().order_by('email')


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, f'Utilizador criado com sucesso. Login: {form.cleaned_data["email"]}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Utilizador'
        ctx['btn_label'] = 'Criar Utilizador'
        return ctx


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Utilizador atualizado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.email}'
        ctx['btn_label'] = 'Guardar Alteracoes'
        return ctx


class UserToggleActiveView(AdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'Nao pode desativar a sua propria conta.')
        else:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            estado = 'ativado' if user.is_active else 'desativado'
            messages.success(request, f'Utilizador "{user.email}" {estado}.')
        return redirect('accounts:user_list')


# ─── Elevacao de perfil para admin ───────────────────────────────────────────

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def elevate_to_admin(request):
    """Verifica a password do proprio utilizador e eleva o perfil na sessao (temporario)."""
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Pedido invalido'}, status=400)

    if not request.user.check_password(password):
        return JsonResponse({'ok': False, 'error': 'Password incorreta'})

    # Guardar elevacao apenas na sessao — nao altera a base de dados
    request.session['perfil_elevado'] = 'admin'
    return JsonResponse({'ok': True, 'redirect': '/accounts/utilizadores/'})


# ─── Registo publico (sem campo de perfil) ────────────────────────────────────

class RegisterForm(django_forms.ModelForm):
    password = django_forms.CharField(
        label='Palavra-passe',
        widget=django_forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
    )
    password_confirm = django_forms.CharField(
        label='Confirmar palavra-passe',
        widget=django_forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise django_forms.ValidationError('Ja existe uma conta com este email.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'As palavras-passe nao coincidem.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.perfil = 'funcionario'  # sempre funcionario no registo publico
        if commit:
            user.save()
        return user


class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Conta criada com sucesso! Pode agora entrar com o email {user.email}.')
            return redirect('accounts:login')
        return render(request, self.template_name, {'form': form})


# ─── Recuperacao de senha ─────────────────────────────────────────────────────

import secrets
from django.core.mail import send_mail
from django.conf import settings as django_settings

# Armazenamento simples em memoria dos tokens (funciona para instancia unica)
# Para producao multi-instancia usar cache/DB
_reset_tokens = {}  # {token: {'user_id': int, 'expires': datetime}}


class PasswordResetRequestView(View):
    template_name = 'accounts/password_reset.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email__iexact=email)
            # Gerar token unico
            token = secrets.token_urlsafe(32)
            _reset_tokens[token] = {
                'user_id': user.pk,
                'expires': timezone.now() + timedelta(hours=1),
            }
            # Construir link
            domain = request.get_host()
            scheme = 'https' if request.is_secure() else 'http'
            link = f'{scheme}://{domain}/accounts/recuperar/{token}/'

            # Enviar email
            try:
                send_mail(
                    subject='Recuperacao de senha — CarWash Stock',
                    message=f'Clique no link para redefinir a sua senha:\n\n{link}\n\nO link expira em 1 hora.',
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, f'Email enviado para {email}. Verifique a sua caixa de entrada.')
            except Exception:
                # Se o email falhar, mostrar o link directamente (para desenvolvimento)
                messages.info(request, f'Link de recuperacao: {link}')
        except User.DoesNotExist:
            # Nao revelar se o email existe ou nao
            messages.success(request, f'Se o email {email} existir, receberá as instrucoes.')

        return redirect('accounts:login')


class PasswordResetConfirmView(View):
    template_name = 'accounts/password_reset_confirm.html'

    def _get_token_data(self, token):
        data = _reset_tokens.get(token)
        if not data:
            return None
        if timezone.now() > data['expires']:
            _reset_tokens.pop(token, None)
            return None
        return data

    def get(self, request, token):
        if not self._get_token_data(token):
            messages.error(request, 'Link invalido ou expirado. Solicite um novo.')
            return redirect('accounts:password_reset')
        return render(request, self.template_name, {'token': token})

    def post(self, request, token):
        data = self._get_token_data(token)
        if not data:
            messages.error(request, 'Link invalido ou expirado.')
            return redirect('accounts:password_reset')

        password = request.POST.get('password', '')
        confirm = request.POST.get('password_confirm', '')

        if len(password) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
            return render(request, self.template_name, {'token': token})

        if password != confirm:
            messages.error(request, 'As senhas nao coincidem.')
            return render(request, self.template_name, {'token': token})

        try:
            user = User.objects.get(pk=data['user_id'])
            user.set_password(password)
            user.save()
            _reset_tokens.pop(token, None)
            messages.success(request, 'Senha alterada com sucesso. Pode agora entrar.')
            return redirect('accounts:login')
        except User.DoesNotExist:
            messages.error(request, 'Utilizador nao encontrado.')
            return redirect('accounts:login')
