"""
Categorias de produtos disponíveis no sistema.
Como a tabela 'produtos' não tem coluna de categoria, as categorias
são geridas como um campo de texto livre no modelo Product.
Esta lista serve de referência para filtros e sugestões na UI.
"""

CATEGORIAS = [
    ('detergentes', 'Detergentes'),
    ('ceras', 'Ceras e Polimentos'),
    ('microfibras', 'Microfibras e Panos'),
    ('desengordurantes', 'Desengordurantes'),
    ('aromatizantes', 'Aromatizantes'),
    ('outros', 'Outros'),
]

CATEGORIAS_DICT = dict(CATEGORIAS)


def get_categorias_choices():
    """Retorna lista de choices para uso em formulários."""
    return [('', '— Todas as categorias —')] + list(CATEGORIAS)
