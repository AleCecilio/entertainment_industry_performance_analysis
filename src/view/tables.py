import numpy as np
import pandas as pd
from .style_config import (
    CORES, 
    GRADIENTES, 
    MAPA_COLUNAS, 
    ESTILO_CABECALHO, 
    FORMATADORES
)

# =====================================================================
#   TEMPLATES DE VISUALIZAÇÃO
# =====================================================================

def estilizar_tabela(df, colunas_selecionadas=None, qtd_linhas=None, caption=None):
    """
    Template geral: aplica cores semânticas por coluna + cabeçalho padronizado.
    Nulos exibidos como '—' em cinza itálico.

    Parâmetros
    ----------
    df                  : DataFrame de entrada
    colunas_selecionadas: lista de colunas a exibir (None = todas)
    qtd_linhas          : número de linhas a exibir
    caption             : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    if colunas_selecionadas:
        colunas_validas = [c for c in colunas_selecionadas if c in df.columns]
        df_foco = df[colunas_validas].head(qtd_linhas)
    else:
        df_foco = df.head(qtd_linhas)

    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    for coluna in df_foco.columns:
        categoria = MAPA_COLUNAS.get(coluna)
        if categoria and categoria in CORES:
            estilo = estilo.set_properties(subset=[coluna], **CORES[categoria])

    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }

    estilo = estilo.map(
        lambda v: 'color: #888888; font-style: italic' if pd.isna(v) else ''
    ).format(formatter=formatadores_ativos, na_rep='—')

    return estilo


def estilizar_resumo_qualidade(df, col_quantidade=None, col_percentual='Perda de Dados (%)', qtd_linhas=None, caption=None):
    """
    Template para DataFrames de diagnóstico de qualidade (nulos, zeros, listas vazias).
    Aplica gradiente vermelho no percentual e laranja na quantidade.

    Parâmetros
    ----------
    df             : DataFrame com resumo de qualidade
    col_quantidade : nome da coluna de quantidade absoluta (autodetectada se None)
    col_percentual : nome da coluna de percentual
    qtd_linhas     : número de linhas a exibir (None = todas)
    caption        : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    if col_quantidade is None:
        candidatas = [c for c in df.columns if c != col_percentual]
        col_quantidade = candidatas[0] if candidatas else None

    df_foco = df.head(qtd_linhas) if qtd_linhas else df
    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    if col_percentual in df.columns:
        estilo = estilo.background_gradient(cmap=GRADIENTES['anomalia'], subset=[col_percentual])

    if col_quantidade and col_quantidade in df.columns:
        estilo = estilo.background_gradient(cmap=GRADIENTES['volume'], subset=[col_quantidade])

    formatadores = {}
    if col_percentual in df.columns:
        formatadores[col_percentual] = '{:.2f}%'
    if col_quantidade and col_quantidade in df.columns:
        formatadores[col_quantidade] = '{:,.0f}'

    return estilo.format(formatadores)


def estilizar_metricas(df, colunas_score=None, colunas_financeiras=None, qtd_linhas=None, caption=None):
    """
    Template para análises de performance: aplica gradientes em scores e colunas financeiras.

    Parâmetros
    ----------
    col
    if qtd_linhas is None:
        qtd_linhas = len(df)unas_score      : colunas de avaliação/popularidade (gradiente viridis)
    colunas_financeiras: colunas de budget/revenue (gradiente Greens)
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    df_foco = df.head(qtd_linhas)
    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    if colunas_score:
        cols_validas = [c for c in colunas_score if c in df_foco.columns]
        if cols_validas:
            estilo = estilo.background_gradient(cmap=GRADIENTES['metrica'], subset=cols_validas)

    if colunas_financeiras:
        cols_validas = [c for c in colunas_financeiras if c in df_foco.columns]
        if cols_validas:
            estilo = estilo.background_gradient(cmap=GRADIENTES['financeiro'], subset=cols_validas)

    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }

    return estilo.map(
        lambda v: 'color: #888888; font-style: italic' if pd.isna(v) else ''
    ).format(formatter=formatadores_ativos, na_rep='—')


def destacar_anomalias(df, mascara, colunas_destaque, colunas_contexto=None, qtd_linhas=None, caption=None):
    """
    Template para inspeção de anomalias: destaca colunas problemáticas em vinho escuro
    e exibe colunas de contexto em tom neutro.

    Parâmetros
    ----------
    mascara           : Series booleana para filtrar linhas anômalas
    colunas_destaque  : colunas que contêm a anomalia (fundo vinho)
    colunas_contexto  : colunas de suporte para leitura (fundo neutro)
    qtd_linhas        : número de linhas a exibir (None = todas)
    caption           : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    colunas_exibir = list(colunas_destaque)
    if colunas_contexto:
        colunas_exibir = list(colunas_contexto) + colunas_exibir

    df_foco = df.loc[mascara, [c for c in colunas_exibir if c in df.columns]]
    if qtd_linhas:
        df_foco = df_foco.head(qtd_linhas)

    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    for col in colunas_destaque:
        if col in df_foco.columns:
            estilo = estilo.set_properties(subset=[col], **CORES['anomalia'])

    return estilo.map(
        lambda v: 'color: #888888; font-style: italic' if pd.isna(v) else ''
    ).format(na_rep='—')


def estilizar_comparativo(df, col_grupo, colunas_metrica, qtd_linhas=None, caption=None):
    """
    Template para tabelas de comparação entre grupos (ex: franquia vs. independente).
    Aplica gradiente divergente nas métricas para facilitar a leitura de diferenças.

    Parâmetros
    ----------
    col_grupo      : coluna categórica de agrupamento (ex: 'is_franchise')
    colunas_metrica: colunas numéricas a comparar
    qtd_linhas     : número de linhas a exibir (None = todas)
    caption        : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    df_foco = df.head(qtd_linhas) if qtd_linhas else df
    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    if col_grupo in df_foco.columns:
        estilo = estilo.set_properties(subset=[col_grupo], **CORES['booleano'])

    cols_validas = [c for c in colunas_metrica if c in df_foco.columns]
    if cols_validas:
        estilo = estilo.background_gradient(cmap=GRADIENTES['divergente'], subset=cols_validas)

    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }

    return estilo.format(formatter=formatadores_ativos, na_rep='—')

