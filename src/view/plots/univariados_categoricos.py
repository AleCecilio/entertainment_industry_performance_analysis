import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import src.utils.metrics as mt
from ._config import _set_config_graf
from ._formatters import _formatar_numero


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