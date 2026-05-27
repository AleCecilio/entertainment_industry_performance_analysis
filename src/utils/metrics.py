import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency

# =========================================================================
# HELPERS INTERNOS — DETECÇÃO AUTOMÁTICA DE TIPOS E CALCULO DE FREQUÊNCIA
# =========================================================================

def _calc_categorical_freq(df, col, top_n=10):
 
    s = df[col].dropna()
    if s.empty:
        return None, None, 0, False

    total_valid_rows = len(s)
    primeiro_valor = s.iloc[0]
    is_complex = False

    # Verificação de tipo
    try:
        hash(primeiro_valor)
        s_analise = s
    except TypeError:
        is_complex = True
        s_analise = s.explode().dropna()

    # Ignora JSONs sujos disfarçados de string
    if not is_complex and isinstance(primeiro_valor, str) and primeiro_valor.lstrip().startswith(("[", "{")):
        return None, None, 0, False

    # O Cálculo Puro
    freq = s_analise.value_counts()
    if freq.empty:
        return None, None, 0, False
        
    freq_top = freq.iloc[:top_n]
    pct_top = (freq_top / total_valid_rows * 100).round(1)

    return freq, freq_top, pct_top, total_valid_rows

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

        resultados = _calc_categorical_freq(df, col, top_n)
        
       
        if resultados[0] is None:
            continue
            
        freq, top_freq, top_pct, total_valid_rows = resultados

        # Entropia de Shannon normalizada 
        probs = freq / freq.sum()
        entropy_val = stats.entropy(probs, base=2)
        max_entropy = np.log2(len(freq)) if len(freq) > 1 else 1.0
        entropy_norm = round(entropy_val / max_entropy, 4) if max_entropy > 0 else 0.0

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
            "total_valid_rows": total_valid_rows,
            "unique_categories": len(freq),
            "entropy_norm":     entropy_norm,
            "top_values_count": top_values_count,
            "top_values_pct_%": top_values_pct,
        })

    if not relatorio:
        return pd.DataFrame()

    return (
        pd.DataFrame(relatorio)
        .set_index('column')
        .sort_values("entropy_norm", ascending=False)
    )


def datetime_summary(df, cols=None):
    """
    Resumo univariado para colunas de data/hora.
    Se 'cols' não for passado, detecta automaticamente todas as colunas datetime.
    """
    if cols is None:
        cols = df.select_dtypes(include='datetime').columns.tolist()
        
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
        # 1. Captura as datas completas dos extremos (sem a parte da hora)
        data_min = s.min().strftime('%Y-%m-%d')
        data_max = s.max().strftime('%Y-%m-%d')

        # 2. Calcula o range exato em anos inteiros
        # Usamos os timestamps brutos para o cálculo dos dias antes da formatação de string
        range_anos = int((s.max() - s.min()).days / 365.25)

        # 3. Extrai as séries de anos e meses para calcular as modas
        anos = s.dt.year
        meses = s.dt.month

        relatorio.append({
            'column': col,
            'min': data_min,                                      
            'max': data_max,                                   
            'range_years': range_anos,                            
            'unique_dates': s.nunique(),                 
            'most_frequent_year': int(anos.mode().iloc[0]) if not anos.mode().empty else None,
            'most_frequent_month': int(meses.mode().iloc[0]) if not meses.mode().empty else None
        })

    if not relatorio:
        return pd.DataFrame()

    return (
        pd.DataFrame(relatorio)
        .set_index('column')
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



def testar_dependencia_categorica(tabela_contingencia, alpha=0.05):
    """
    Executa o teste do Qui-Quadrado de Independência
    para duas colunas categóricas de qualquer dataset, exibindo o relatório final.
    """
    
    # Executar o Teste do Qui-Quadrado
    chi2, p, dof, expected = chi2_contingency(tabela_contingencia)

    # Formata o p-valor para notação científica se for muito pequeno
    p_formatado = f"{p:.4e}" if p < 0.001 else f"{p:.4f}"

    print("\nResultados do Teste Estatístico")
    print(f"Estatística Qui-Quadrado: {chi2:.4f}")
    print(f"Graus de Liberdade: {dof}")
    print(f"p-valor: {p_formatado}")

    print("\nConclusão do Teste")
    match p:
        case p if p < alpha:
            print(f"Como o p-valor ({p_formatado}) < {alpha}, REJEITAMOS a hipótese nula ($H_0$).")
            print("Conclusão: Existe uma associação estatisticamente significativa entre as duas variáveis!")
        case _:
            print(f"Como o p-valor ({p_formatado}) >= {alpha}, FALHAMOS em rejeitar a hipótese nula ($H_0$).")
            print("Conclusão: As variáveis são independentes (a relação observada é mero acaso).")
            
    return chi2, p, dof, expected