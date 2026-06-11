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
def plotar_fronteira_outliers(
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