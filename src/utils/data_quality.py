import numpy as np
import pandas as pd
from scipy import stats


# =====================================================================
# FUNÇÕES AUXILIARES — cada uma retorna uma Série com sufixo no índice
# =====================================================================

def _data_missing_nan(df):
    n = df.isnull().sum()
    n.index = n.index + ' (Valores NaN)'
    return n

def _data_missing_numeric(df):
    n = (df.select_dtypes(include='number') == 0).sum()
    n.index = n.index + ' (Zeros - Numérico)'
    return n

def _data_missing_numeric_obj(df):
    n = (df == '0').sum()
    n.index = n.index + ' (Zeros - Texto)'
    return n

def _data_missing_list(df):
    n = (df == '[]').sum()
    n.index = n.index + ' (Listas Vazias)'
    return n

def _data_missing_datetime(df):
    cols_data = [
        c for c in df.columns
        if 'date' in c.lower()
        or 'data' in c.lower()
        or 'time' in c.lower()
    ]
    series = []
    for col in cols_data:
        converted = pd.to_datetime(df[col], errors='coerce')
        nat_count = converted.isna().sum()
        series.append(
            pd.Series(
                nat_count,
                index=[f'{col} (Valores NaT)']
            )
        )
    if series:
        return pd.concat(series)
    return pd.Series(dtype='int64')


# =====================================================================
# MAPA: tipo (string) → função correspondente
# =====================================================================
_TIPOS_MISSING = {
    'nan':         _data_missing_nan,
    'numeric':     _data_missing_numeric,
    'numeric_obj': _data_missing_numeric_obj,
    'list':        _data_missing_list,
    'datetime':    _data_missing_datetime,
}

_TIPOS_DEFAULT = ['nan', 'numeric', 'numeric_obj', 'list', 'datetime']


# =====================================================================
# FUNÇÃO PRINCIPAL — DATA QUALITY
# =====================================================================

def resumo_qualidade(df, tipos=None):
    """
    Gera um DataFrame de diagnóstico de qualidade com contagem e percentual
    de dados faltantes, por tipo de "buraco".

    Parâmetros
    ----------
    df    : DataFrame a ser analisado
    tipos : lista de tipos a verificar. Opções:
            'nan'         → valores nulos (NaN/None)
            'numeric'     → zeros em colunas numéricas
            'numeric_obj' → strings '0' em colunas objeto
            'list'        → strings '[]' (listas vazias serializadas)
            'datetime'    → valores NaT em colunas de data/hora
            Padrão: todos os cinco tipos.

    Retorno
    -------
    DataFrame com colunas:
        'Quantidade'         → contagem absoluta de buracos
        'Perda de Dados (%)' → percentual sobre o total de linhas
    Ordenado do mais crítico para o menos crítico.
    """
    if tipos is None:
        tipos = _TIPOS_DEFAULT

    tipos_invalidos = [t for t in tipos if t not in _TIPOS_MISSING]
    if tipos_invalidos:
        raise ValueError(f"Tipos inválidos: {tipos_invalidos}. Use: {list(_TIPOS_MISSING.keys())}")

    series_list = [_TIPOS_MISSING[t](df) for t in tipos]
    series_list = [s for s in series_list if not s.empty]
    resumo_bruto = pd.concat(series_list)
    resumo_filtrado = resumo_bruto[resumo_bruto > 0]

    return (
        pd.DataFrame({
            'Quantidade':         resumo_filtrado,
            'Perda de Dados (%)': (resumo_filtrado / len(df)) * 100
        })
        .sort_values('Perda de Dados (%)', ascending=False)
    )