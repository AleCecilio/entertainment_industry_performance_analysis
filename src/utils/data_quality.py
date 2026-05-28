import numpy as np
import pandas as pd
from scipy import stats

# =====================================================================
# DETECTOR UNIVERSAL DE COLUNAS DE DATA (Heurística Dinâmica)
# =====================================================================

def _identificar_colunas_data(df):
    """Identifica dinamicamente quais colunas são de data/hora no dataframe."""
    cols_data = []
    for c in df.columns:
        if not ('date' in c.lower() or 'data' in c.lower() or 'time' in c.lower()):
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            continue
        amostra = df[c].dropna().head(5).astype(str)
        if not amostra.empty and amostra.str.isnumeric().all():
            continue
        cols_data.append(c)
    return cols_data

# =====================================================================
# FUNÇÕES AUXILIARES — cada uma retorna uma Série com sufixo no índice
# =====================================================================

def _data_missing_nan(df):
    cols_data = _identificar_colunas_data(df)
    cols_para_checar = [c for c in df.columns if c not in cols_data]
    if not cols_para_checar:
        return pd.Series(dtype='int64')
    n = df[cols_para_checar].isnull().sum()
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
    cols_data = _identificar_colunas_data(df)
    
    series = []
    for col in cols_data:
        converted = pd.to_datetime(df[col], errors='coerce')
        total_nat = converted.isna().sum()
        series.append(
            pd.Series(
                total_nat,
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