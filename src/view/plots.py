import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# =====================================================================
#   Variaveis Globais
# =====================================================================

FIGSIZE_DEFALT = (12, 8)
DPI_DEFALT = 120
WIDTH_DEFALT = 0.8

# =====================================================================
#   Funções de Auxílio
# =====================================================================

# Transforma 1.000.000 em "1M" e 1.000.000.000 em "1B"
def formatar_dinheiro(x, pos):
    if x >= 1e9:
        return f'${x*1e-9:.1f}B'
    elif x >= 1e6:
        return f'${x*1e-6:.0f}M'
    elif x >= 1e3:
        return f'${x*1e-3:.0f}K'
    return f'${x:.0f}'
# =====================================================================
#   Plots 
# =====================================================================

def grafico_percentual_missing_data(df, tamanho_figura=None, polegadas=None, width=None):
    """
    Gera um barplot horizontal focado em auditoria visual (QA).
    Mapeia a intensidade da cor pela gravidade da perda de dados.
    """

    if tamanho_figura is None:
        tamanho_figura = FIGSIZE_DEFALT
    
    if polegadas is None:
        polegadas = DPI_DEFALT

    if width is None:
        width = WIDTH_DEFALT

        
    # Configuração de tela em alta definição
    plt.figure(figsize=tamanho_figura, dpi=polegadas)
    
    # Eixo em segundo plano: grade vertical discreta para guiar a leitura das barras
    plt.gca().set_axisbelow(True)
    plt.grid(axis='x', linestyle='--', alpha=0.4, color='#9A8C98')

    # Renderização da camada de dados
    ax = sns.barplot(
        x='Perda de Dados (%)',
        y=df.index,
        data=df,
        hue=df.index,
        palette='Reds_r',
        legend=False,
        width=width
    )

    # Rótulos no topo das barras com tipografia reforçada
    for container in ax.containers:
        ax.bar_label(
            container, 
            padding=5, 
            fontsize=10, 
            fontweight='semibold', 
            color='#2B2D42', 
            fmt='%.2f%%'
        )

    # Estilização de títulos e eixos alinhada à paleta do projeto
    plt.title('Auditoria de Perda de Dados por Coluna', fontsize=15, fontweight='bold', color='#2B2D42', pad=20)
    plt.xlabel('Perda de Dados (%)', fontsize=11, fontweight='semibold', color='#4A4E69')
    plt.ylabel('Atributo', fontsize=11, fontweight='semibold', color='#4A4E69')

    # Ajuste dinâmico do eixo X para garantir que os rótulos de texto não sejam cortados
    plt.xlim(0, df['Perda de Dados (%)'].max() * 1.15)

    # Clean UI: remove as bordas do gráfico para maximizar a proporção de tinta-dados
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.show()

# =====================================================================
# GRÁFICOS NUMÉRICOS (O Combo do Skew e Kurtosis)
# =====================================================================

def grafico_distribuicao_numerica(
        df, 
        coluna, 
        titulo=None,  
        tamanho_figura=None, 
        polegadas=None,
        width=None,
        usar_log=False,
        formato_moeda=False
    ):
    """
    Combina um Boxplot (para mostrar os outliers detectados pelo IQR) 
    e um Histograma com curva KDE (para mostrar o skew e kurtosis).
    """

    if tamanho_figura is None:
        tamanho_figura = FIGSIZE_DEFALT
    
    if polegadas is None:
        polegadas = DPI_DEFALT

    if width is None:
        width = WIDTH_DEFALT

    fig, (ax_box, ax_hist) = plt.subplots(
        2, 1, 
        figsize=tamanho_figura,
        dpi=polegadas,
        sharex=True,
        gridspec_kw={"height_ratios": (0.3, 0.7)}
    )

    x_dados = df[coluna].replace(0, np.nan).dropna() if usar_log else df[coluna].dropna()
    
    # Gráfico 1: Boxplot (Cima) - Foco em Outliers
    sns.boxplot(
        x=x_dados, 
        ax=ax_box, 
        color='#1E2780', 
        fliersize=3, 
        width=width
    )
    ax_box.set(xlabel='') 
    
    # Gráfico 2: Histograma + Curva de Densidade (Baixo) - Foco na Distribuição
    sns.histplot(
        x=x_dados, 
        ax=ax_hist, 
        color='#1E2780', 
        kde=True, 
        bins=30, 
        log_scale=usar_log
)
    
    if formato_moeda:
        formatter = ticker.FuncFormatter(formatar_dinheiro)
        ax_hist.xaxis.set_major_formatter(formatter)
    
    # Estilização
    titulo_real = titulo if titulo else f"Distribuição: {coluna.capitalize()}"
    ax_box.set_title(titulo_real, fontsize=14, fontweight='bold', pad=15)
    ax_hist.set_xlabel(coluna.capitalize(), fontsize=12)
    ax_hist.set_ylabel("Quantidade de Filmes", fontsize=12)
    
    # Limpeza visual
    sns.despine(left=True, bottom=False)
    ax_box.spines['bottom'].set_visible(False)
    ax_box.tick_params(bottom=False)
    
    plt.tight_layout()
    plt.show()


# =====================================================================
# GRÁFICOS CATEGÓRICOS (O Combo da Entropia e Market Share)
# =====================================================================

def grafico_top_categorias(relatorio_metrica, coluna_nome, titulo=None, cor_barra="#d9534f"):
    """
    Consome DIRETAMENTE o dicionário gerado pelo seu arquivo metrics.py
    e plota as categorias em um gráfico de barras horizontais super legível.
    """
    # Extrai o DataFrame de top_values que o metrics.py gerou
    if coluna_nome not in relatorio_metrica:
        print(f"Erro: A coluna '{coluna_nome}' não está no relatório fornecido.")
        return
        
    df_plot = relatorio_metrica[coluna_nome]['top_values']
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plota barras horizontais (mais fácil para ler textos longos como Gêneros)
    sns.barplot(
        x='pct_%', 
        y=df_plot.index, 
        data=df_plot, 
        color=cor_barra, 
        ax=ax
    )
    
    # Adiciona os números em cima de cada barra para não precisarmos olhar o eixo X
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'{width}%', 
                    (width + 0.5, p.get_y() + p.get_height() / 2.), 
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#333333')

    # Estilização
    titulo_real = titulo if titulo else f"Top Categorias: {coluna_nome}"
    ax.set_title(titulo_real, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Participação no Dataset (%)", fontsize=12)
    ax.set_ylabel("") # Remove o título do eixo Y para ficar mais limpo
    
    # Pega o valor da entropia só para colocar uma legenda inteligente
    entropia = relatorio_metrica[coluna_nome]['entropy_norm']
    ax.text(0.95, 0.05, f'Entropia (Caos): {entropia}', 
            transform=ax.transAxes, ha='right', fontsize=10, color='gray')
    
    plt.tight_layout()
    plt.show()

# =====================================================================
# GRÁFICOS PARA LISTAS (Foco no Tamanho/Volume)
# =====================================================================

def grafico_tamanho_listas(df, coluna, titulo=None, cor="#f0ad4e"):
    """
    Mostra a distribuição do tamanho das listas em uma coluna.
    Ex: Quantos filmes têm 1 gênero? Quantos têm 2? Quantos não têm nenhum (0)?
    """
    # Calcula o tamanho de cada lista (se for nulo, conta como 0)
    tamanhos = df[coluna].dropna().apply(len)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Usamos countplot porque o tamanho das listas costuma ser números inteiros pequenos (0, 1, 2, 3...)
    sns.countplot(x=tamanhos, color=cor, ax=ax)
    
    # Adiciona o número exato em cima de cada barra
    for p in ax.patches:
        height = p.get_height()
        if height > 0: # Só anota se tiver algo
            ax.annotate(f'{int(height)}', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#555555')

    titulo_real = titulo if titulo else f"Quantidade de Itens por Linha: {coluna}"
    ax.set_title(titulo_real, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel(f"Número de itens na lista de {coluna}", fontsize=12)
    ax.set_ylabel("Quantidade de Filmes", fontsize=12)
    
    plt.tight_layout()
    plt.show()


# =====================================================================
# GRÁFICOS PARA DICIONÁRIOS (Foco na Presença de Chaves)
# =====================================================================

def grafico_presenca_chaves_dict(relatorio_metrica, coluna_nome, titulo=None, cor="#5cb85c"):
    """
    Consome o relatório do dict_column_summary e plota um gráfico de barras 
    mostrando a porcentagem de presença de cada chave dentro do dicionário.
    """
    if coluna_nome not in relatorio_metrica or 'key_summary' not in relatorio_metrica[coluna_nome]:
        print(f"Erro: Relatório inválido para a coluna de dicionário '{coluna_nome}'.")
        return
        
    df_plot = relatorio_metrica[coluna_nome]['key_summary'].reset_index()
    
    # Ordena para a chave que mais aparece ficar no topo
    df_plot = df_plot.sort_values(by='presence_%', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.barplot(x='presence_%', y='key', data=df_plot, color=cor, ax=ax)
    
    # Anota a porcentagem
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'{width}%', 
                    (width + 0.5, p.get_y() + p.get_height() / 2.), 
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#333333')

    titulo_real = titulo if titulo else f"Presença de Atributos (Dict): {coluna_nome}"
    ax.set_title(titulo_real, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Frequência de Aparição (%)", fontsize=12)
    ax.set_ylabel("Chaves do Dicionário", fontsize=12)
    
    # Mostra a % geral de dados nulos na coluna inteira
    nulos = relatorio_metrica[coluna_nome]['null_%']
    ax.text(0.95, 0.05, f'Dados totalmente nulos (Vazios): {nulos}%', 
            transform=ax.transAxes, ha='right', fontsize=10, color='red')
    
    plt.tight_layout()
    plt.show()