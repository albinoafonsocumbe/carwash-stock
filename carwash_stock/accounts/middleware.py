class PerfilElevadoMiddleware:
    """
    Aplica o perfil elevado da sessao ao utilizador em cada request.
    Ao fazer logout a sessao e destruida e o perfil volta ao original.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            elevado = request.session.get('perfil_elevado')
            if elevado:
                request.user._perfil_elevado = elevado
            else:
                # Garantir que nao ha elevacao residual
                if hasattr(request.user, '_perfil_elevado'):
                    del request.user._perfil_elevado
        return self.get_response(request)
