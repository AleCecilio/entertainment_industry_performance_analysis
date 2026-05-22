import pandas as pd
import numpy as np
import ast

# =====================================================================
# FUNÇÃO BASE DE PARSING (O DESPERTADOR DE DADOS)
# =====================================================================
def _converter_para_objeto(valor):
    if pd.isna(valor) or valor in ['[]', '{}', '0', 0, '']:
        return None
        
    if isinstance(valor, (list, dict)):
        return valor
        
    try:
        return ast.literal_eval(str(valor))
    except (ValueError, SyntaxError):
        return None  # não é objeto, deixa pro chamador lidar


# =====================================================================
# EXTRATORES DE INFORMAÇÃO
# =====================================================================
def extrair_dicionario(valor, valor_padrao="Não Identificado", chave='name'):
    """
    Busca o valor de uma chave específica dentro de um dicionário.
    """
    # Acorda o dado internamente
    obj = _converter_para_objeto(valor)

    if isinstance(obj, dict):
        # O método .get() do Python já aceita um valor padrão (fallback) nativamente!
        return obj.get(chave, valor_padrao)
        
    # Se falhou em tudo, devolve o padrão
    return valor_padrao


def extrair_lista_dicts(valor, valor_padrao="Não Identificado", chave='name'):
    obj = _converter_para_objeto(valor)

    if isinstance(obj, list):
        # Lista de dicionários
        nomes = [item.get(chave) for item in obj if isinstance(item, dict) and chave in item]
        if nomes:
            return nomes

        # Lista de strings já parseada
        strings = [item for item in obj if isinstance(item, str)]
        if strings:
            return strings

    # String separada por ";"
    if isinstance(valor, str) and ';' in valor:
        return [p.strip() for p in valor.split(';') if p.strip()]

    return [valor_padrao] if isinstance(valor_padrao, str) else valor_padrao

