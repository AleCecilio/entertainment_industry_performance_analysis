import numpy as np
import pandas as pd
from scipy import stats


# =====================================================================
# FUNÇÕES AUXILIARES — cada uma retorna uma Série com sufixo no índice
# =====================================================================

def data_missing_nan(df):
    n = df.isnull().sum()
    n.index = n.index + ' (Valores NaN)'
    return n

def data_missing_numeric(df):
    n = (df.select_dtypes(include='number') == 0).sum()
    n.index = n.index + ' (Zeros - Numérico)'
    return n

def data_missing_numeric_obj(df):
    n = (df == '0').sum()
    n.index = n.index + ' (Zeros - Texto)'
    return n

def data_missing_list(df):
    n = (df == '[]').sum()
    n.index = n.index + ' (Listas Vazias)'
    return n


# =====================================================================
# MAPA: tipo (string) → função correspondente
# =====================================================================
_TIPOS_MISSING = {
    'nan':         data_missing_nan,
    'numeric':     data_missing_numeric,
    'numeric_obj': data_missing_numeric_obj,
    'list':        data_missing_list,
}

_TIPOS_DEFAULT = ['nan', 'numeric', 'numeric_obj', 'list']


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
            Padrão: todos os quatro tipos.

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

    resumo_bruto = pd.concat(series_list)
    resumo_filtrado = resumo_bruto[resumo_bruto > 0]

    return (
        pd.DataFrame({
            'Quantidade':         resumo_filtrado,
            'Perda de Dados (%)': (resumo_filtrado / len(df)) * 100
        })
        .sort_values('Perda de Dados (%)', ascending=False)
    )


# =====================================================================
# ANÁLISE UNIVARIADA — COLUNAS NUMÉRICAS
# =====================================================================

def numeric_summary(df, round_decimals=2):
    """
    Resumo estatístico completo das colunas numéricas.

    Inclui estatísticas descritivas, forma da distribuição e detecção
    de outliers via método IQR (fence de 1.5 x IQR).
    """
    num_cols = df.select_dtypes(include='number').columns

    records = []
    for col in num_cols:
        s = df[col].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        fence_low  = q1 - 1.5 * iqr
        fence_high = q3 + 1.5 * iqr
        outlier_mask = (s < fence_low) | (s > fence_high)

        records.append({
            'mean':          s.mean(),
            'median':        s.median(),
            'std':           s.std(),
            'min':           s.min(),
            'max':           s.max(),
            'iqr':           iqr,
            'skew':          s.skew(),
            'kurtosis':      s.kurt(),
            'outlier_count': outlier_mask.sum(),
            'outlier_%':     outlier_mask.mean() * 100,
        })

    return (
        pd.DataFrame(records, index=num_cols)
        .round(round_decimals)
        .sort_values('missing_%', ascending=False)
    )


# =====================================================================
# ANÁLISE UNIVARIADA — COLUNAS CATEGÓRICAS
# =====================================================================

def categorical_summary(df, top_n=5, round_decimals=2):
    """
    Resumo das colunas categóricas com foco em distribuição e concentração.
    """
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns

    records = []
    for col in cat_cols:
        freq     = df[col].value_counts(dropna=True)
        freq_pct = freq / len(df) * 100

        # Entropia de Shannon normalizada
        probs   = freq / freq.sum()
        entropy = stats.entropy(probs, base=2)
        max_entropy = np.log2(len(freq)) if len(freq) > 1 else 1
        entropy_norm = round(entropy / max_entropy, round_decimals) if max_entropy > 0 else 0

        records.append({
            'column':            col,
            'unique':            df[col].nunique(),
            'top_category':      freq.index[0],
            'top_category_%':    round(freq_pct.iloc[0], round_decimals),
            'coverage_top_n_%':  round(freq_pct.iloc[:top_n].sum(), round_decimals),
            'entropy':           entropy_norm,
            'top_values':        {
                k: round(v, round_decimals)
                for k, v in freq_pct.iloc[:top_n].items()
            },
        })

    return (
        pd.DataFrame(records)
        .set_index('column')
        .sort_values('entropy', ascending=False)
    )


# =====================================================================
# ANÁLISE UNIVARIADA — COLUNAS DE LISTAS
# =====================================================================

def list_column_summary(df, cols=None, top_n=10, round_decimals=2):
    """
    Resumo univariado para colunas cujos valores são listas Python nativas.

    """
    if cols is None:
        cols = _detect_list_cols(df)

    if not cols:
        raise ValueError("Nenhuma coluna de lista encontrada. Passe cols= explicitamente.")

    result = {}
    for col in cols:
        s = df[col].dropna()

        sizes = s.apply(len)
        exploded = s.explode().dropna()
        freq = exploded.value_counts()

        top_freq = freq.iloc[:top_n]
        top_pct  = (top_freq / len(df) * 100).round(round_decimals)

        result[col] = {
            'list_size_stats': pd.DataFrame({
                'value': {
                    'min':    round(sizes.min(), round_decimals),
                    'max':    round(sizes.max(), round_decimals),
                    'mean':   round(sizes.mean(), round_decimals),
                    'median': round(sizes.median(), round_decimals),
                    'std':    round(sizes.std(), round_decimals),
                }
            }),
            'empty_%':       round((sizes == 0).mean() * 100, round_decimals),
            'single_item_%': round((sizes == 1).mean() * 100, round_decimals),
            'unique_values': freq.nunique(),
            'top_values':    pd.DataFrame({
                'count': top_freq.values,
                'pct_%': top_pct.values,
            }, index=top_freq.index),
        }

    return result


# =====================================================================
# ANÁLISE UNIVARIADA — COLUNAS DE DICIONÁRIOS
# =====================================================================

def dict_column_summary(df, cols=None, extract_key=None, top_n=10, round_decimals=2):
    """
    Resumo univariado para colunas cujos valores são dicionários Python nativos.
    """
    if cols is None:
        cols = _detect_dict_cols(df)

    if not cols:
        raise ValueError("Nenhuma coluna de dicionário encontrada. Passe cols= explicitamente.")

    result = {}
    for col in cols:
        s        = df[col]
        null_pct = round(s.isna().mean() * 100, round_decimals)
        s_valid  = s.dropna()

        if extract_key is not None:
            values = s_valid.apply(
                lambda d: d.get(extract_key) if isinstance(d, dict) else None
            ).dropna()

            freq    = values.value_counts()
            top_freq = freq.iloc[:top_n]
            top_pct  = (top_freq / len(df) * 100).round(round_decimals)

            result[col] = {
                'null_%':        null_pct,
                'unique_values': freq.nunique(),
                'top_values':    pd.DataFrame({
                    'count': top_freq.values,
                    'pct_%': top_pct.values,
                }, index=top_freq.index),
            }

        else:
            all_keys = set()
            for d in s_valid:
                if isinstance(d, dict):
                    all_keys.update(d.keys())

            key_records = []
            for key in sorted(all_keys):
                values   = s_valid.apply(lambda d: d.get(key) if isinstance(d, dict) else None)
                present  = values.notna()
                freq     = values[present].value_counts()
                top_vals = dict(zip(
                    freq.index[:top_n],
                    (freq.iloc[:top_n] / len(df) * 100).round(round_decimals)
                ))
                key_records.append({
                    'key':         key,
                    'presence_%':  round(present.mean() * 100, round_decimals),
                    'unique':      freq.nunique(),
                    'top_values':  top_vals,
                })

            result[col] = {
                'null_%':      null_pct,
                'keys_found':  sorted(all_keys),
                'key_summary': pd.DataFrame(key_records).set_index('key'),
            }

    return result


# =====================================================================
# HELPERS INTERNOS — DETECÇÃO AUTOMÁTICA DE TIPOS
# =====================================================================

def _detect_list_cols(df):
    """Detecta colunas cujo primeiro valor não-nulo é uma lista."""
    detected = []
    for col in df.columns:
        first_valid = df[col].dropna().iloc[0] if df[col].notna().any() else None
        if isinstance(first_valid, list):
            detected.append(col)
    return detected


def _detect_dict_cols(df):
    """Detecta colunas cujo primeiro valor não-nulo é um dicionário."""
    detected = []
    for col in df.columns:
        first_valid = df[col].dropna().iloc[0] if df[col].notna().any() else None
        if isinstance(first_valid, dict):
            detected.append(col)
    return detected