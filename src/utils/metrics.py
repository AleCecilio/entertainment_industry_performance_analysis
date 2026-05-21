import numpy as np
import pandas as pd
from scipy import stats

# =====================================================================
# ANÁLISE UNIVARIADA — COLUNAS NUMÉRICAS
# =====================================================================

def numeric_summary(df, cols=None):
    """
    Resumo estatístico completo das colunas numéricas.
    Se 'cols' não for passado, detecta automaticamente todas as colunas numéricas.
    """
    if cols is None:
        cols = df.select_dtypes(include='number').columns.tolist()
        
    if isinstance(cols, str):
        cols = [cols]

    if not cols:
        return pd.DataFrame()

    relatorio = []
    for col in cols:
        if col not in df.columns:
            continue

        s = df[col].dropna()
        if s.empty:
            continue
            
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        fence_low  = q1 - 1.5 * iqr
        fence_high = q3 + 1.5 * iqr
        outlier_mask = (s < fence_low) | (s> fence_high)

        relatorio.append({
            'column':        col,
            'mean':          s.mean(),
            'median':        s.median(),
            'std':           s.std(),
            'min':           s.min(),
            'max':           s.max(),
            'iqr':           iqr,
            'skew':          s.skew(),
            'kurtosis':      s.kurt(),
            'outlier_count': outlier_mask.sum(),
            'outlier_%':     (outlier_mask.mean() * 100),
        })

    if not relatorio:
        return pd.DataFrame()

    return (
        pd.DataFrame(relatorio)
        .set_index('column')
        .sort_values('mean', ascending=False)
    )


def categorical_summary(df, cols = None, top_n = 10):
    """
    Resumo univariado unificado para colunas categóricas simples ou em formato
    de lista/array (incluindo np.ndarray gerados pela leitura de .parquet).
    """
    if cols is None:
        cols = df.select_dtypes(include=["object", "category", "string", "boolean"]).columns.tolist()

    if isinstance(cols, str):
        cols = [cols]

    if not cols:
        return pd.DataFrame()

    relatorio = []

    for col in cols:
        if col not in df.columns:
            continue

        s = df[col].dropna()
        if s.empty:
            continue

        # --- Triagem: detecta se a coluna guarda estruturas unhashable ---
        primeiro_valor = s.iloc[0]
        try:
            hash(primeiro_valor)
            is_complex = False
        except TypeError:
            is_complex = True

        # --- Ignora strings sujas de JSON ---
        if not is_complex and isinstance(primeiro_valor, str) and primeiro_valor.lstrip().startswith(("[", "{")):
            continue

        # --- Frequência ---
        if is_complex:
            freq = s.explode().dropna().value_counts()
        else:
            freq = s.value_counts()

        if freq.empty:
            continue

        # --- Entropia de Shannon normalizada ---
        probs = freq / freq.sum()
        entropy_val = stats.entropy(probs, base=2)
        max_entropy = np.log2(len(freq)) if len(freq) > 1 else 1.0
        entropy_norm = round(entropy_val / max_entropy, 4) if max_entropy > 0 else 0.0

        # --- Top N formatado com bullet points verticais ---
        top_freq = freq.iloc[:top_n]
        top_pct = (top_freq / len(s) * 100).round(1)

        top_values_count = "\n".join(
            f"• {idx} ({count})"
            for idx, count in zip(top_freq.index, top_freq.values)
        )
        top_values_pct = "\n".join(
            f"• {idx} ({pct}%)"
            for idx, pct in zip(top_pct.index, top_pct.values)
        )

        relatorio.append({
            "column":           col,
            "total_valid_rows": len(s),
            "unique_categories": len(freq),
            "entropy_norm":     entropy_norm,
            "top_values_count": top_values_count,
            "top_values_pct_%": top_values_pct,
        })

    if not relatorio:
        return pd.DataFrame()

    return (
        pd.DataFrame(relatorio)
        .set_index("column")
        .sort_values("entropy_norm", ascending=False)
    )

# =====================================================================
# ANÁLISE UNIVARIADA — MÚLTIPLOS ARQUIVOS EXPLODIDOS
# =====================================================================

def exploded_files_summary(dataframes_dict, top_n=10):
    """
    Gera resumos para colunas categóricas que estão salvas em arquivos 
    e DataFrames separados (um arquivo .parquet para cada recurso explodido).
    """
    relatorio_geral = {}
    
    for col_name, df in dataframes_dict.items():
        if col_name in df.columns:
            # Reutiliza o motor categórico já automatizado
            relatorio_geral.update(categorical_summary(df, cols=col_name, top_n=top_n))
        else:
            cols_cand = df.select_dtypes(include=['object', 'string', 'category', 'bool']).columns.tolist()
            if cols_cand:
                # Usa a primeira coluna detectada com o nome da chave fornecida
                resumo_temp = categorical_summary(df, cols=cols_cand[0], top_n=top_n)
                relatorio_geral[col_name] = resumo_temp.get(cols_cand[0])
                
    return relatorio_geral


# =====================================================================
# ANÁLISE UNIVARIADA — COLUNAS DE DICIONÁRIOS (CAMADA INTERIM)
# =====================================================================

def dict_column_summary(df, cols=None, extract_key=None, top_n=10):
    """
    Resumo univariado para colunas cujos valores são dicionários Python nativos.
    Se 'cols' não for passado, detecta automaticamente os dicionários.
    """
    if cols is None:
        cols = _detect_dict_cols(df)
        
    if isinstance(cols, str):
        cols = [cols]

    if not cols:
        return {"erro": "Nenhuma coluna de dicionário encontrada."}

    result = {}
    for col in cols:
        if col not in df.columns:
            continue
            
        s        = df[col]
        null_pct = round(s.isna().mean() * 100)
        s_valid  = s.dropna()
        if s_valid.empty:
            continue

        if extract_key is not None:
            values = s_valid.apply(
                lambda d: d.get(extract_key) if isinstance(d, dict) else None
            ).dropna()

            freq    = values.value_counts()
            top_freq = freq.iloc[:top_n]
            top_pct  = (top_freq / len(df) * 100).round(2)

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
                    (freq.iloc[:top_n] / len(df) * 100).round(2)
                ))
                key_records.append({
                    'key':         key,
                    'presence_%':  round(present.mean() * 100),
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