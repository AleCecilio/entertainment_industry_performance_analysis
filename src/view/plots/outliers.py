import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import src.utils.metrics as mt
from ._config import _set_config_graf
from ._formatters import _formatar_eixo_numerico


# ==============================================================================
#   Gráfico de Análise de Outliers 
# ==============================================================================
def grafico_fronteira_outliers(
    df_plot,
    coluna,
    cerca_superior,
    cor_tema='#4A4E69',
    titulo=None,
    tamanho_figura=None,
    polegadas=None,
    width=None,
    usar_log=False,
    tipo_dado=None,
    valores_eixo_x=None
):
    """Gera um gráfico composto (Boxplot + Stripplot) evidenciando a cerca superior."""

    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    fig, ax = plt.subplots(figsize=tamanho_figura, dpi=polegadas)
    
    sns.boxplot(
        x=df_plot[coluna], 
        ax=ax, 
        color=cor_tema, 
        width=width, 
        fliersize=0, 
        boxprops=dict(alpha=0.3)
    )
    
    # Stripplot por cima para mostrar a densidade real
    sns.stripplot(
        x=df_plot[coluna], 
        ax=ax, 
        color=cor_tema, 
        size=3, 
        alpha=0.5, 
        jitter=0.25
    )
    
    # Linha vertical marcando a Cerca Superior
    ax.axvline(
        cerca_superior, 
        color='#E63946',
        linestyle='--', 
        linewidth=2.5, 
        label=f'Cerca Superior ({cerca_superior:,.0f})'
    )

    if usar_log:
        ax.xaxis.set_minor_locator(ticker.NullLocator())

    # ===== Configuração Dinâmica do Eixo X por Tipo de Dado =====
        _formatar_eixo_numerico(
            ax=ax, 
            s_plot=df_plot, 
            usar_log=usar_log, 
            tipo_dado=tipo_dado,
            valores_eixo=valores_eixo_x,
            eixo='x'
        )
    
    # Textos e formatação estética
    titulo_real = (
        titulo if titulo 
        else f"Distribuição de {coluna.replace('_', ' ').title()} e Fronteira de Outliers"
    )
    ax.set_title(
        titulo_real, 
        fontsize=14, 
        fontweight='bold', 
        pad=15, 
        color='#2b2d42'
    )
    ax.set_xlabel(
        coluna.replace('_', ' ').title(), 
        fontsize=11, 
        fontweight='bold', 
        color='#4A4E69'
    )

    if usar_log:
        ax.set_xlabel(f"{coluna.capitalize()} (Escala Logarítmica)", fontsize=12)
    else:
        ax.set_xlabel(coluna.capitalize(), fontsize=12)


    ax.legend(loc='lower right', frameon=True, shadow=True)
    
    sns.despine(left=True)
    ax.yaxis.set_visible(False)
    
    plt.show()

def grafico_distribuicao_financeira(
    df_plot,
    col_budget='budget',
    col_revenue='revenue',
    titulo_1=None,
    titulo_2=None,
    tamanho_figura=None,
    polegadas=None,
    width=None,
    usar_log=False,
    tipo_dado=None,
    valores_eixo_x=None
):
    """
    Plota a distribuição de Orçamento e Receita lado a lado na mesma figura,
    utilizando escala logarítmica para lidar com a grande amplitude dos valores.
    """
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura,polegadas,width)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=tamanho_figura,
        dpi=polegadas
    )

    # Gráfico 1: Orçamento (Budget)

    df_budget_valido = df_plot[df_plot[col_budget] > 0]

    sns.histplot(
        data=df_budget_valido,
        x=col_budget,
        kde=True,
        ax=axes[0],
        color='#2B2D42'
    )

    if usar_log:
        axes[0].xaxis.set_minor_locator(ticker.NullLocator())

    _formatar_eixo_numerico(
        ax=axes[0],
        s_plot=df_plot,
        usar_log=usar_log,
        tipo_dado=tipo_dado,
        valores_eixo=valores_eixo_x,
        eixo='x',
        menos_valores=True
    )

    titulo_real_1 = (
        titulo_1
        if titulo_1
        else f"Distribuição de {col_budget.replace('_', ' ').title()}"
    )

    axes[0].set_title(
        titulo_real_1,
        fontsize=14,
        fontweight='bold',
        pad=15,
        color='#2B2D42'
    )

    label_x_1 = (
        f"{col_budget.capitalize()} (Escala Logarítmica)"
        if usar_log
        else col_budget.replace('_', ' ').title()
    )

    axes[0].set_xlabel(
        label_x_1,
        fontsize=12,
        fontweight='bold',
        color='#4A4E69'
    )

    axes[0].set_ylabel('Frequência')

    # Gráfico 2: Receita (Revenue)

    df_revenue_valido = df_plot[df_plot[col_revenue] > 0]

    sns.histplot(
        data=df_revenue_valido,
        x=col_revenue,
        kde=True,
        ax=axes[1],
        color='#588157'
    )

    if usar_log:
        axes[1].xaxis.set_minor_locator(ticker.NullLocator())

    _formatar_eixo_numerico(
        ax=axes[1],
        s_plot=df_plot,
        usar_log=usar_log,
        tipo_dado=tipo_dado,
        valores_eixo=valores_eixo_x,
        eixo='x',
        menos_valores=True
    )

    titulo_real_2 = (
        titulo_2
        if titulo_2
        else f"Distribuição de {col_revenue.replace('_', ' ').title()}"
    )

    axes[1].set_title(
        titulo_real_2,
        fontsize=14,
        fontweight='bold',
        pad=15,
        color='#2B2D42'
    )

    label_x_2 = (
        f"{col_revenue.capitalize()} (Escala Logarítmica)"
        if usar_log
        else col_revenue.replace('_', ' ').title()
    )

    axes[1].set_xlabel(
        label_x_2,
        fontsize=12,
        fontweight='bold',
        color='#4A4E69'
    )

    axes[1].set_ylabel('Frequência')

    plt.suptitle(
        'Análise Combinada das Variáveis Financeiras (Antes da Limpeza)',
        fontsize=14,
        fontweight='bold',
        y=1.02
    )

    plt.tight_layout()
    plt.show()