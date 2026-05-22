import numpy as np
import pandas as pd
import seaborn as sns
import src.utils.metrics as mt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# =====================================================================
#   Variaveis Globais
# =====================================================================

_FIGSIZE_DEFALT = (12, 8)
_DPI_DEFALT = 120
_WIDTH_DEFALT = 0.8

# =====================================================================
#   Funções de Auxílio
# =====================================================================

# Configura gráficos 
def _set_config_graf(tamanho_figura=None, polegadas=None, width=None):
    if tamanho_figura is None:
        tamanho_figura = _FIGSIZE_DEFALT
    
    if polegadas is None:
        polegadas = _DPI_DEFALT

    if width is None:
        width = _WIDTH_DEFALT
    
    return tamanho_figura, polegadas, width


# Transforma 1.000.000 em "1M" e 1.000.000.000 em "1B"
def _formatar_dinheiro(x, pos):
    if x >= 1e9:
        return f'${x*1e-9:.1f}B'
    elif x >= 1e6:
        return f'${x*1e-6:.0f}M'
    elif x >= 1e3:
        return f'${x*1e-3:.0f}K'
    return f'${x:.0f}'

def _get_entertainment_ticks():
    """
    Retorna os marcadores financeiros (ticks) estratégicos para cobrir as 
    escalas de Literatura, Anime e Cinema em gráficos logarítmicos.
    """
    return [
        10_000,        # $10K: Avanço padrão de publicação de livros / Orçamento base de episódio de anime
        100_000,       # $100K: Livro best-seller de nicho / Custo de episódio de anime de alta qualidade
        1_000_000,     # $1M: Mega best-seller literário / Filme de cinema indie
        10_000_000,    # $10M: Orçamento de filmes em anime / Filme de cinema de médio porte
        50_000_000,    # $50M: Mega-hit de bilheteria de anime / Ponto de virada comercial em Hollywood
        100_000_000,   # $100M: O piso do Blockbuster de Hollywood moderno
        500_000_000,   # $500M: Sucesso mundial absoluto de cinema
        1_000_000_000, # $1B: O cobiçado "Clube do Bilhão" do cinema
        2_000_000_000  # $2B: O teto histórico da indústria
    ]

# =====================================================================
#   Plots 
# =====================================================================

def grafico_percentual_missing_data(df_plot, tamanho_figura=None, polegadas=None, width=None):
    """
    Gera um barplot horizontal focado em auditoria visual (QA).
    Mapeia a intensidade da cor pela gravidade da perda de dados.
    """

    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

        
    # Configuração de tela em alta definição
    plt.figure(figsize=tamanho_figura, dpi=polegadas)
    
    # Eixo em segundo plano: grade vertical discreta para guiar a leitura das barras
    plt.gca().set_axisbelow(True)
    plt.grid(axis='x', linestyle='--', alpha=0.4, color='#9A8C98')

    # Renderização da camada de dados
    ax = sns.barplot(
        x='Perda de Dados (%)',
        y=df_plot.index,
        data=df_plot,
        hue=df_plot.index,
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
    plt.xlim(0, df_plot['Perda de Dados (%)'].max() * 1.15)

    # Clean UI: remove as bordas do gráfico para maximizar a proporção de tinta-dados
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.show()

# =====================================================================
# GRÁFICOS NUMÉRICOS (O Combo do Skew e Kurtosis)
# =====================================================================

def grafico_distribuicao_numerica(
        df_plot, 
        coluna, 
        relatorio_df=None,
        titulo=None,  
        tamanho_figura=None, 
        polegadas=None,
        width=None,
        usar_log=False,
        formato_moeda=False,
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
    
    # Gráfico 1: Boxplot
    sns.boxplot(x=s_plot, ax=ax_box, color='#1E2780', fliersize=3, width=width)
    ax_box.set(xlabel='') 
    
    # Gráfico 2: Histograma + KDE
    sns.histplot(x=s_plot, ax=ax_hist, color='#1E2780', kde=True, bins=30, log_scale=usar_log)

    if valores_eixo_x is not None:
        ax_hist.set_xticks(valores_eixo_x)
    elif usar_log and formato_moeda:
        ax_hist.set_xticks(_get_entertainment_ticks())
    
    if formato_moeda:
        formatter = ticker.FuncFormatter(_formatar_dinheiro)
        ax_hist.xaxis.set_major_formatter(formatter)
    
    if formato_moeda:
        formatter = ticker.FuncFormatter(_formatar_dinheiro)
        ax_hist.xaxis.set_major_formatter(formatter)
    
    ax_hist.tick_params(axis='x', rotation=45)
    
    # Estilização
    titulo_real = titulo if titulo else f"Distribuição: {coluna.capitalize()}"
    ax_box.set_title(titulo_real, fontsize=14, fontweight='bold', pad=15)
    ax_hist.set_xlabel(coluna.capitalize(), fontsize=12)
    ax_hist.set_ylabel("Quantidade de Filmes", fontsize=12)
    

    if relatorio_df is not None and coluna in relatorio_df.index:
        skew = round(relatorio_df.loc[coluna, 'skew'], 2)
        kurt = round(relatorio_df.loc[coluna, 'kurtosis'], 2) # <-- Capturamos a Curtose
        outliers_pct = round(relatorio_df.loc[coluna, 'outlier_%'], 2)
        
        # Adicionamos a Curtose no texto do painel
        texto_stats = f"Distorção (Skew): {skew}\nCurtose (Kurt): {kurt}\nOutliers: {outliers_pct}%"
        
        # Coloca uma caixinha de texto no canto superior direito do Histograma
        ax_hist.text(0.95, 0.85, texto_stats, 
                     transform=ax_hist.transAxes, 
                     ha='right', va='top', 
                     fontsize=10, color='#333333',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    plt.tight_layout()
    plt.show()


# =====================================================================
# GRÁFICOS CATEGÓRICOS
# =====================================================================

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
    Consome DIRETAMENTE o dicionário gerado pelo seu arquivo metrics.py
    e plota as categorias em um gráfico de barras horizontais super legível.
    """

    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    # Extrai o DataFrame de top_values que o metrics.py gerou
    if coluna not in relatorio_metrica:
        print(f"Erro: A coluna '{coluna}' não está no relatório fornecido.")
        return
        
    df_plot = relatorio_metrica[[coluna]]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plota barras horizontais (mais fácil para ler textos longos como Gêneros)
    ax = sns.barplot(
        x=coluna,
        y=df_plot.index,
        data=df_plot,
        hue=df_plot.index,
        palette=palette,
        legend=False,
        width=width
    )

    # Estilização
    titulo_real = titulo if titulo else f"Top Categorias: {coluna}"
    ax.set_title(titulo_real, fontsize=15, fontweight='bold', color='#2B2D42', pad=20)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel("") # Remove o título do eixo Y para ficar mais limpo
    
    
    plt.tight_layout()
    plt.show()


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
    Plota barras horizontais recriando as porcentagens matemáticas limpas,
    mas extrai a Entropia diretamente do relatório já gerado.
    """

    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

   
    resultados = mt._calc_categorical_freq(df, nome_coluna, top_n)
    
    if resultados[0] is None:
        print(f"Erro: A coluna '{nome_coluna}' está vazia ou é inválida.")
        return
        
    _, _, top_pct, _ = resultados
    
    # Transforma em DataFrame para o Seaborn engolir com facilidade
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

    # Adiciona os números em cima de cada barra
    for p in ax.patches:
        width_bar = p.get_width()
        ax.annotate(f'{width_bar}%', 
                    (width_bar + 0.5, p.get_y() + p.get_height() / 2.), 
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#333333')

    # Estilização
    titulo_real = titulo if titulo else f"Top Categorias: {nome_coluna.capitalize()}"
    ax.set_title(titulo_real, fontsize=15, fontweight='bold', color='#2B2D42', pad=20)
    ax.set_xlabel("Participação no Dataset (%)", fontsize=12)
    ax.set_ylabel("") 
    
    sns.despine(left=True, bottom=True) # Deixa mais minimalista
    
    # Busca a Entropia no relatório
    if relatorio_df is not None and nome_coluna in relatorio_df.index:
        entropia = relatorio_df.loc[nome_coluna, 'entropy_norm']
        ax.text(0.95, 0.05, f'Entropia (Caos): {entropia}', 
                transform=ax.transAxes, ha='right', fontsize=10, color='gray')
    
    plt.tight_layout()
    plt.show()