import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import src.utils.metrics as mt
from ._config import _set_config_graf
from ._formatters import _formatar_eixo_numerico


# =======================================================================
#       Gráficos Análise Univariada para Variáveis Numéricas 
# =======================================================================


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
        _formatar_eixo_numerico(
            ax=ax_hist, 
            s_plot=s_plot, 
            usar_log=usar_log, 
            tipo_dado=tipo_dado,
            valores_eixo=valores_eixo_x,
            eixo='x'
        )

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

# =======================================================================
#       Gráficos Análise Univariada para Variáveis Categóricas 
# =======================================================================

# ===== Barplot Horizontal de Métricas por Categoria (consome metrics.py) =====

def grafico_metricas_categorias(
        relatorio_metrica,
        coluna,
        titulo=None,
        x_label='',
        palette='Blues_r',
        tamanho_figura=None,
        polegadas=None,
        width=None
):
    """
    Consome DIRETAMENTE o dicionário gerado pelo metrics.py
    e plota as categorias em um gráfico de barras horizontais.
    """
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    if coluna not in relatorio_metrica:
        print(f"Erro: A coluna '{coluna}' não está no relatório fornecido.")
        return

    df_plot = relatorio_metrica[[coluna]]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax = sns.barplot(
        x=coluna,
        y=df_plot.index,
        data=df_plot,
        hue=df_plot.index,
        palette=palette,
        legend=False,
        width=width
    )

    titulo_real = titulo if titulo else f"Top Categorias: {coluna}"
    ax.set_title(titulo_real, fontsize=15, fontweight='bold', color='#2B2D42', pad=20)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel("")

    plt.tight_layout()
    plt.show()


# ===== Barplot Horizontal de Top N Categorias com Entropia =====

def grafico_top_categorias(
        df,
        nome_coluna,
        relatorio_df=None,
        top_n=10,
        titulo=None,
        palette='flare',
        tamanho_figura=None,
        polegadas=None,
        width=None
):
    """
    Plota as top N categorias com porcentagem e exibe a Entropia normalizada
    extraída do relatório gerado pelo metrics.py.
    """
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    resultados = mt._calc_categorical_freq(df, nome_coluna, top_n)

    if resultados[0] is None:
        print(f"Erro: A coluna '{nome_coluna}' está vazia ou é inválida.")
        return

    _, _, top_pct, _ = resultados

    df_plot = top_pct.reset_index()
    df_plot.columns = ['Categoria', 'Porcentagem']

    fig, ax = plt.subplots(figsize=tamanho_figura, dpi=polegadas)

    sns.barplot(
        x='Porcentagem',
        y='Categoria',
        data=df_plot,
        hue='Categoria',
        palette=palette,
        legend=False,
        width=width,
        ax=ax
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt='%.2f%%',
            padding=5,
            fontsize=10,
            fontweight='bold',
            color='#333333'
        )

    titulo_real = titulo if titulo else f"Top Categorias: {nome_coluna.capitalize()}"
    ax.set_title(titulo_real, fontsize=15, fontweight='bold', color='#2B2D42', pad=20)
    ax.set_xlabel("Participação no Dataset (%)", fontsize=12)
    ax.set_ylabel("")

    plt.xlim(0, df_plot['Porcentagem'].max() * 1.15)
    sns.despine(left=True, bottom=True)

    # ===== Anotação de Entropia Normalizada no Rodapé =====

    if relatorio_df is not None and nome_coluna in relatorio_df.index:
        entropia = relatorio_df.loc[nome_coluna, 'entropy_norm']
        ax.text(0.95, 0.05, f'Entropia (Caos): {entropia}',
                transform=ax.transAxes, ha='right', fontsize=10, color='gray')

    plt.tight_layout()
    plt.show()


# ===== Barplot Horizontal de Frequências Temporais (Ano, Mês, Década) =====

def grafico_top_tempo(
        df,
        coluna,
        top_n=10,
        titulo=None,
        palette='viridis',
        tamanho_figura=None,
        polegadas=None,
        width=None,
        extracao=None
):
    """
    Plota as frequências de variáveis de tempo (anos, meses, décadas).
    Se 'extracao' for 'month' ou 'year', extrai de uma coluna datetime.
    Caso contrário, usa o valor nativo da coluna.
    """
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    # ===== Extração e Tratamento da Variável Temporal =====

    if extracao == 'year':
        dados = pd.to_datetime(df[coluna], errors='coerce').dt.year.dropna()
        nome_eixo = 'Ano'
    elif extracao == 'month':
        dados = pd.to_datetime(df[coluna], errors='coerce').dt.month.dropna()
        nome_eixo = 'Mês'
    else:
        dados = df[coluna].dropna()
        nome_eixo = coluna.replace('_', ' ').title()

    top_release = (
        dados.value_counts()
        .head(top_n)
        .reset_index()
    )
    top_release.columns = [nome_eixo, 'Contagem']

    if pd.api.types.is_numeric_dtype(top_release[nome_eixo]):
        top_release[nome_eixo] = top_release[nome_eixo].astype(int).astype(str)
    else:
        top_release[nome_eixo] = top_release[nome_eixo].astype(str)

    fig, ax = plt.subplots(figsize=tamanho_figura, dpi=polegadas)

    sns.barplot(
        x='Contagem',
        y=nome_eixo,
        data=top_release,
        palette=palette,
        hue=nome_eixo,
        width=width,
        legend=False,
        ax=ax
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt='%d',
            padding=8,
            fontsize=10,
            fontweight='bold',
            color='#333333'
        )

    titulo_real = titulo if titulo else f"Top {top_n} Frequências por {nome_eixo}"

    ax.set_title(titulo_real, fontsize=16, fontweight='bold', color='#2B2D42', loc='left', pad=20)
    ax.set_xlabel("Quantidade de Registros", fontsize=12)
    ax.set_ylabel("")

    ax.grid(axis='x', alpha=0.2)
    ax.set_xlim(0, top_release['Contagem'].max() * 1.15)
    sns.despine()

    plt.tight_layout()
    plt.show()