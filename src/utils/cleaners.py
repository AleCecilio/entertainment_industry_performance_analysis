import pandas as pd
import numpy as np
import ast

# =====================================================================
# 1. FUNÇÃO BASE DE PARSING (O DESPERTADOR DE DADOS)
# =====================================================================
def converter_para_objeto(valor):
    """
    Transforma strings em listas ou dicionários reais.
    Se for lixo, nulo ou vazio, devolve None para que o extrator lide com isso.
    """
    if pd.isna(valor) or valor in ['[]', '{}', '0', 0, '']:
        return None
        
    if isinstance(valor, (list, dict)):
        return valor
        
    try:
        return ast.literal_eval(str(valor))
    except (ValueError, SyntaxError):
        return None


# =====================================================================
# 2. EXTRATORES DE INFORMAÇÃO
# =====================================================================
def extrair_dicionario(valor, valor_padrao="Não Identificado", chave='name'):
    """
    Busca o valor de uma chave específica dentro de um dicionário.
    """
    # Acorda o dado internamente
    obj = converter_para_objeto(valor)

    if isinstance(obj, dict):
        # O método .get() do Python já aceita um valor padrão (fallback) nativamente!
        return obj.get(chave, valor_padrao)
        
    # Se falhou em tudo, devolve o padrão
    return valor_padrao


def extrair_lista_dicts(valor, valor_padrao="Não Identificado", chave='name'):
    """
    Busca os valores dentro de uma lista de dicionários.
    Garante que o retorno padrão também seja uma lista para não quebrar a coluna.
    """
    obj = converter_para_objeto(valor)

    if isinstance(obj, list):
        nomes = [item.get(chave) for item in obj if isinstance(item, dict) and chave in item]
        
        if nomes:
            return nomes

    return [valor_padrao] if isinstance(valor_padrao, str) else valor_padrao