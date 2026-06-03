import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from ._config import _set_config_graf
from ._formatters import _formatar_eixo_numerico

# ===== FUNÇÃO AUXILIAR DE PREPARAÇÃO (Separa Numéricos e Categóricos) =====

def _preparar_dados_bivariada(
        df, 
        cat_col, 
        num_col, 
        top_n_cats, 
        usar_log
):
    """
    Trata de forma isolada e específica as variáveis numéricas (Eixo Y) 
    e categóricas (Eixo X), explodindo listas caso necessário.
    """
    df_clean = df[[cat_col, num_col]].copy()

    # Tratamento numérico
    df_clean[num_col] = pd.to_numeric(df_clean[num_col], errors='coerce')
    if usar_log:
        df_clean = df_clean[df_clean[num_col] > 0]
    df_clean = df_clean.dropna(subset=[num_col])

    if df_clean.empty:
        return df_clean

    # Tratamento categórico
    amostra = df_clean[cat_col].dropna().iloc[0] if not df_clean[cat_col].dropna().empty else ""

    if isinstance(amostra, list):
        df_clean = df_clean.explode(cat_col)
    elif isinstance(amostra, str):
        if ';' in amostra:
            df_clean[cat_col] = df_clean[cat_col].str.split(';')
            df_clean = df_clean.explode(cat_col)
        elif ',' in amostra:
            df_clean[cat_col] = df_clean[cat_col].str.split(',')
            df_clean = df_clean.explode(cat_col)

    # Padroniza como texto limpo
    df_clean[cat_col] = df_clean[cat_col].astype(str).str.strip()
    df_clean = df_clean[df_clean[cat_col] != ''] 
    df_clean = df_clean.dropna(subset=[cat_col])

    # Filtra Top N Categorias
    if top_n_cats:
        top_cats = df_clean[cat_col].value_counts().nlargest(top_n_cats).index
        df_clean = df_clean[df_clean[cat_col].isin(top_cats)]

    return df_clean


# =====  FUNÇÃO ESPECÍFICA PARA BOXPLOT =====

def grafico_cat_vs_num_boxplot(
        df_plot, 
        cat_col, 
        num_col, 
        top_n_cats=None, 
        titulo=None,
        tamanho_figura=None, 
        polegadas=None, 
        width=None,
        usar_log=False, 
        tipo_dado=None, 
        valores_eixo_y=None
):
    """Gera um Boxplot com dados higienizados pela função de preparo."""
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)
    
    # Processamento isolado
    data_plot = _preparar_dados_bivariada(df_plot, cat_col, num_col, top_n_cats, usar_log)
    if data_plot.empty:
        print(f"Erro: Dados insuficientes após tratamento para {cat_col} e {num_col}.")
        return

    fig, ax = plt.subplots(figsize=tamanho_figura, dpi=polegadas)
    
    sns.boxplot(
        x=cat_col, 
        y=num_col, 
        hue=cat_col,       
        data=data_plot, 
        palette='viridis', 
        width=width, 
        legend=False,      
        ax=ax
    )

    _formatar_eixo_numerico(
        ax=ax,
        s_plot=data_plot[num_col], 
        usar_log=usar_log, 
        tipo_dado=tipo_dado, 
        valores_eixo=valores_eixo_y,
        eixo='y'
    )

    nome_x, nome_y = cat_col.replace('_', ' ').title(), num_col.replace('_', ' ').title()
    ax.set_title(titulo if titulo else f"Boxplot: {nome_y} por {nome_x}", fontsize=14, pad=15)
    ax.set_xlabel(nome_x, fontsize=12)
    if usar_log:
        ax.set_ylabel(f"{num_col.capitalize()} (Escala Logarítmica)", fontsize=12)
    else:
        ax.set_ylabel(f"{num_col.capitalize()}", fontsize=12)

    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.get_xticklabels(), ha="right", rotation_mode="anchor")

    sns.despine()
    plt.tight_layout()
    plt.show()


# ===== FUNÇÃO ESPECÍFICA PARA VIOLINPLOT =====

def grafico_cat_vs_num_violinplot(
        df_plot,
        cat_col, 
        num_col, 
        top_n_cats=None, 
        titulo=None,
        tamanho_figura=None, 
        polegadas=None,
        width=None,
        usar_log=False, 
        tipo_dado=None, 
        valores_eixo_y=None
):
    """Gera um Violinplot com dados higienizados pela função de preparo."""
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)
    
    # Processamento isolado
    data_plot = _preparar_dados_bivariada(df_plot, cat_col, num_col, top_n_cats, usar_log)
    if data_plot.empty:
        print(f"Erro: Dados insuficientes após tratamento para {cat_col} e {num_col}.")
        return

    fig, ax = plt.subplots(figsize=tamanho_figura, dpi=polegadas)

    sns.violinplot(
        x=cat_col, 
        y=num_col, 
        hue=cat_col,       
        data=data_plot, 
        palette='viridis', 
        inner='quartile', 
        width=width, 
        legend=False,      
        ax=ax
    )

    _formatar_eixo_numerico(
        ax=ax,
        s_plot=data_plot[num_col],
        usar_log=usar_log,
        tipo_dado=tipo_dado,
        valores_eixo=valores_eixo_y,
        eixo='y'
    )

    nome_x, nome_y = cat_col.replace('_', ' ').title(), num_col.replace('_', ' ').title()
    ax.set_title(titulo if titulo else f"Densidade: {nome_y} por {nome_x}", fontsize=14, pad=15)
    ax.set_xlabel(nome_x, fontsize=12)
    if usar_log:
        ax.set_ylabel(f"{num_col.capitalize()} (Escala Logarítmica)", fontsize=12)
    else:
        ax.set_ylabel(f"{num_col.capitalize()}", fontsize=12)

    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.get_xticklabels(), ha="right", rotation_mode="anchor")

    

    sns.despine(left=True, bottom=False)
    plt.tight_layout()
    plt.show()