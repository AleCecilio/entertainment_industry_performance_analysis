# ===== Configurações Globais e Setup de Figura =====

_FIGSIZE_DEFALT = (12, 8)
_DPI_DEFALT = 120
_WIDTH_DEFALT = 0.8


# ===== Aplicador de Defaults de Figura =====

def _set_config_graf(tamanho_figura=None, polegadas=None, width=None):
    if tamanho_figura is None:
        tamanho_figura = _FIGSIZE_DEFALT
    if polegadas is None:
        polegadas = _DPI_DEFALT
    if width is None:
        width = _WIDTH_DEFALT
    return tamanho_figura, polegadas, width