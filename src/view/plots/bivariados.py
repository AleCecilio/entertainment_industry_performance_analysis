import math
import seaborn as sns
import matplotlib.pyplot as plt

from ._config import _set_config_graf
from ._formatters import _formatar_eixo_numerico


# =======================================
#       Gráficos Análise Bivariada 
# =======================================


# ===== Helper Interno: Renderização Padronizada de Scatter Individual =====

def _desenhar_scatter_individual(ax, df_local, col_x, col_y):
    """Padroniza a renderização estática de um painel de scatter."""

    sns.scatterplot(
        data=df_local,
        x=col_x,
        y=col_y,
        alpha=0.5,
        color='#2A6FDB',
        edgecolor='white',
        ax=ax
    )

    sns.regplot(
        data=df_local,
        x=col_x,
        y=col_y,
        scatter=False,
        color='#E63946',
        line_kws={'linewidth': 1.5, 'alpha': 0.8},
        ax=ax
    )

    _formatar_eixo_numerico(ax, col_x, fontsize=10, fontweight='bold', color='#4A4E69')
    ax.grid(axis='both', linestyle=':', alpha=0.5)
    sns.despine(ax=ax)


# ===== Grid Dinâmico de Scatter com Linha de Tendência =====

def grafico_corr_scatter(
    df_plot,
    coluna_x,
    coluna_y,
    quant_grafs=1,
    titulo=None,
    tamanho_figura=None,
    polegadas=None,
    limitar_eixos=True
):
    """
    Plota gráficos de dispersão bivariados.
    Ajusta dinamicamente o layout baseando-se no quant_grafs.
    """
    lista_x = [coluna_x] if isinstance(coluna_x, str) else list(coluna_x)

    # ===== Definição Dinâmica do Grid de Painéis =====

    if quant_grafs == 1:
        n_rows, n_cols = 1, 1
    elif quant_grafs <= 3:
        n_rows, n_cols = 1, quant_grafs
        if tamanho_figura is None:
            tamanho_figura = (5.5 * n_cols, 4.5)
    else:
        n_cols = 2
        n_rows = math.ceil(quant_grafs / n_cols)
        if tamanho_figura is None:
            tamanho_figura = (6.5 * n_cols, 4.2 * n_rows)

    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=tamanho_figura, dpi=polegadas, sharey=False)
    axes_flat = [axes] if quant_grafs == 1 else axes.flatten()

    # ===== Laço de Renderização dos Painéis =====

    for i in range(len(axes_flat)):
        ax = axes_flat[i]

        if i >= quant_grafs or i >= len(lista_x):
            fig.delaxes(ax)
            continue

        col_x = lista_x[i]
        df_local = df_plot[[col_x, coluna_y]].dropna()

        _desenhar_scatter_individual(ax, df_local, col_x, coluna_y)

        if quant_grafs == 1 or (i % n_cols == 0):
            ax.set_ylabel(coluna_y.replace('_', ' ').capitalize(), fontsize=10, fontweight='bold', color='#4A4E69')
        else:
            ax.set_ylabel('')

        if limitar_eixos:
            ax.set_xlim(0, df_local[col_x].quantile(0.99))
            ax.set_ylim(0, df_local[coluna_y].quantile(0.99))
        else:
            ax.set_xlim(0, df_local[col_x].max() * 1.1)
            ax.set_ylim(0, df_local[coluna_y].max() * 1.1)

    # ===== Título Global e Rodapé de Observação =====

    titulo_real = titulo if titulo else f"Análise de Correlação com {coluna_y.replace('_', ' ').capitalize()}"
    fig.suptitle(titulo_real, fontsize=14, fontweight='bold', color='#2B2D42')

    if limitar_eixos:
        texto_rodape = "* Observação: Os eixos estão limitados ao percentil 99 para mitigar distorções de outliers extremos."
        fig.text(0.02, -0.02 if n_rows > 1 else -0.05, texto_rodape, fontsize=9, style='italic', color='#4A4E69')

    plt.subplots_adjust(
        left=0.06,
        right=0.98,
        top=0.88 if n_rows > 1 else 0.85,
        hspace=0.35,
        wspace=0.25
    )

    plt.show()


# ===== Heatmap Bivariado de Dependência entre Categorias =====

def grafico_dependencia_categorica(
    tabela_absoluta,
    chi2,
    p_valor,
    titulo=None,
    palette='YlGnBu',
    polegadas=None,
    top_n=10
):
    """
    Plota um Heatmap bivariado para avaliar dependência entre variáveis categóricas.
    Calcula automaticamente o tamanho do canvas com base no volume de dados.
    """
    _, polegadas, _ = _set_config_graf(polegadas=polegadas)

    # ===== Filtragem das Top N Categorias por Eixo =====

    top_genres = (
        tabela_absoluta.sum(axis=0)
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    top_languages = (
        tabela_absoluta.sum(axis=1)
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    tabela_filtrada = tabela_absoluta.loc[top_languages, top_genres]

    tabela_percentual = (
        tabela_filtrada.div(tabela_filtrada.sum(axis=1), axis=0)
    ) * 100

    # ===== Dimensionamento Automático do Canvas =====

    num_linhas = len(tabela_percentual.index)
    num_colunas = len(tabela_percentual.columns)

    largura_calculada = max(12, num_colunas * 1.1)
    altura_calculada = max(6, num_linhas * 0.75)

    fig, ax = plt.subplots(figsize=(largura_calculada, altura_calculada), dpi=polegadas)

    sns.heatmap(
        tabela_percentual,
        annot=False,
        fmt=".1f",
        cmap=palette,
        linewidths=0,
        cbar_kws={'label': 'Proporção dentro do grupo (%)', 'shrink': 0.9},
        annot_kws={'size': 9},
        ax=ax
    )

    # ===== Estilização de Títulos e Eixos =====

    coluna_y = tabela_percentual.columns.name or "Categoria"
    coluna_x = tabela_percentual.index.name or "Grupo"

    titulo_real = (
        titulo if titulo
        else f"Análise Bivariada: {top_n} {coluna_y.capitalize()} por {top_n} {coluna_x.capitalize()}"
    )

    plt.title(titulo_real, fontsize=14, fontweight='bold', pad=20)
    plt.ylabel(coluna_x.capitalize(), fontsize=11)
    plt.xlabel(coluna_y.capitalize(), fontsize=11, labelpad=10)

    if num_colunas > 3:
        plt.xticks(rotation=45, ha='right', rotation_mode='anchor')

    # ===== Rodapé com Resultado do Teste Qui-Quadrado =====

    p_texto = f"{p_valor:.4e}" if p_valor < 0.001 else f"{p_valor:.4f}"

    match p_valor:
        case p if p < 0.05:
            conclusao = "Existe associação estatística real"
        case _:
            conclusao = "As variáveis aparentam independência"

    texto_rodape = (
        f"Qui-Quadrado = {chi2:.2f}  |  "
        f"p-valor = {p_texto}  |  "
        f"{conclusao} (α = 5%)"
    )

    fig.text(0.02, -0.06, texto_rodape, fontsize=10, style='italic', color='#4A4E69')

    fig.subplots_adjust(bottom=0.18)
    plt.tight_layout()

    if num_colunas > 3:
        plt.subplots_adjust(bottom=0.22)

    plt.show()


# ===============================================================================
#       Gráficos Análise Bivariada para Variáveis Numéricas Vs Categóricas
# ===============================================================================


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
