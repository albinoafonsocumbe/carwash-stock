from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class AdminRequiredMixin(LoginRequiredMixin):
    """Garante que o utilizador está autenticado e tem perfil 'admin'."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin():
            messages.error(request, 'Nao tem permissao para aceder a esta pagina.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)
