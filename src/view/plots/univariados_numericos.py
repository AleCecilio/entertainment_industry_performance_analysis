import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from ._config import _set_config_graf
from ._formatters import (
    _formatar_dinheiro,
    _get_nota_ticks_and_labels,
    _get_vote_count_ticks,
    _get_entertainment_ticks
)


# ===== Combo Boxplot + Histograma com KDE para Variáveis Numéricas =====

def grafico_distribuicao_numerica(
        df_plot,
        coluna,
        relatorio_df=None,
        titulo=None,
        tamanho_figura=None,
        polegadas=None,
        width=None,
        usar_log=False,
        tipo_dado=None,
        valores_eixo_x=None
):
    """
    Combina um Boxplot e um Histograma com KDE.
    Se um relatório for fornecido, estampa Skewness e % de Outliers no gráfico.
    """
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    fig, (ax_box, ax_hist) = plt.subplots(
        2, 1,
        figsize=tamanho_figura,
        dpi=polegadas,
        sharex=True,
        gridspec_kw={"height_ratios": (0.3, 0.7)}
    )

    s_plot = df_plot[coluna].replace(0, np.nan).dropna() if usar_log else df_plot[coluna].dropna()

    sns.boxplot(x=s_plot, ax=ax_box, color='#1E2780', fliersize=3, width=width)
    ax_box.set(xlabel='')

    sns.histplot(x=s_plot, ax=ax_hist, color='#1E2780', kde=True, bins=30, log_scale=usar_log)

    if usar_log:
        ax_hist.xaxis.set_minor_locator(ticker.NullLocator())
        ax_box.xaxis.set_minor_locator(ticker.NullLocator())

    # ===== Configuração Dinâmica do Eixo X por Tipo de Dado =====

    if valores_eixo_x is not None:
        ax_hist.xaxis.set_major_locator(ticker.FixedLocator(valores_eixo_x))
        labels = (
            [_formatar_dinheiro(x) for x in valores_eixo_x]
            if tipo_dado == 'moeda'
            else [str(x) for x in valores_eixo_x]
        )
        ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
        ax_hist.tick_params(axis='x', rotation=45)
    else:
        match tipo_dado:
            case 'popularidade' if usar_log:
                ticks = [0.1, 1, 5, 10, 50, 100, 500, 1000]
                ticks = [t for t in ticks if t <= s_plot.max() * 1.5]
                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(ticks))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter([str(t) for t in ticks]))
                ax_hist.tick_params(axis='x', rotation=0)

            case 'popularidade':
                formatter = ticker.FuncFormatter(lambda x, pos: f"{x:,.1f}" if x < 10 else f"{int(x)}")
                ax_hist.xaxis.set_major_formatter(formatter)
                ax_hist.tick_params(axis='x', rotation=0)

            case 'nota_100':
                posicoes, rotulos = _get_nota_ticks_and_labels(escala=100)
                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(posicoes))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(rotulos))
                ax_hist.tick_params(axis='x', rotation=45)

            case 'nota_10':
                posicoes, rotulos = _get_nota_ticks_and_labels(escala=10)
                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(posicoes))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(rotulos))
                ax_hist.tick_params(axis='x', rotation=45)

            case 'nota_5':
                posicoes, rotulos = _get_nota_ticks_and_labels(escala=5)
                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(posicoes))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(rotulos))
                ax_hist.tick_params(axis='x', rotation=45)

            case 'contagem' if usar_log:
                ticks = _get_vote_count_ticks()
                labels = [f"{t//1000}K" if t >= 1000 else str(t) for t in ticks]
                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(ticks))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
                ax_hist.tick_params(axis='x', rotation=45)

            case 'contagem':
                from ._formatters import _formatar_numero
                ax_hist.xaxis.set_major_formatter(ticker.FuncFormatter(_formatar_numero))
                ax_hist.tick_params(axis='x', rotation=45)

            case 'moeda' if usar_log:
                ticks = _get_entertainment_ticks()
                labels = [_formatar_dinheiro(x) for x in ticks]
                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(ticks))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
                ax_hist.tick_params(axis='x', rotation=45)

            case 'moeda':
                ax_hist.xaxis.set_major_formatter(ticker.FuncFormatter(_formatar_dinheiro))
                ax_hist.tick_params(axis='x', rotation=45)

            case _:
                pass

    # ===== Estilização de Títulos e Eixos =====

    titulo_real = titulo if titulo else f"Distribuição: {coluna.capitalize()}"
    ax_box.set_title(titulo_real, fontsize=14, pad=15)
    ax_hist.set_ylabel("Quantidade de Registros", fontsize=12)

    if usar_log:
        ax_hist.set_xlabel(f"{coluna.capitalize()} (Escala Logarítmica)", fontsize=12)
    else:
        ax_hist.set_xlabel(coluna.capitalize(), fontsize=12)

    # ===== Painel de Estatísticas (Skew, Kurtosis, Outliers) =====

    if relatorio_df is not None and coluna in relatorio_df.index:
        skew = round(relatorio_df.loc[coluna, 'skew'], 2)
        kurt = round(relatorio_df.loc[coluna, 'kurtosis'], 2)
        outliers_pct = round(relatorio_df.loc[coluna, 'outlier_%'], 2)

        texto_stats = f"Distorção (Skew): {skew}\nCurtose (Kurt): {kurt}\nOutliers: {outliers_pct}%"

        ax_hist.text(
            0.95, 0.85, texto_stats,
            transform=ax_hist.transAxes,
            ha='right', va='top',
            fontsize=10, color='#333333',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray')
        )

    sns.despine(left=True, bottom=False)
    ax_box.spines['bottom'].set_visible(False)
    ax_box.tick_params(bottom=False)

    plt.tight_layout()
    plt.show()