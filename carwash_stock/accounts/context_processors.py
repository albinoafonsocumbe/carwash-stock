def perfil_elevado(request):
    """
    Injeta 'perfil_elevado' no contexto.
    Se a sessao tiver 'perfil_elevado', o utilizador funciona como admin
    sem alterar o perfil real na base de dados.
    """
    if request.user.is_authenticated:
        elevado = request.session.get('perfil_elevado')
        if elevado:
            # Sobrepor temporariamente o perfil do utilizador
            request.user._perfil_elevado = elevado
    return {}
