import math
from unittest import case
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
    
   

def _formatar_numero(x, pos=None):
    """Formata números grandes de forma limpa (1K, 1M, 1B) sem cifrão."""
    if x >= 1e9:
        return f'{x*1e-9:.1f}B'
    elif x >= 1e6:
        return f'{x*1e-6:.0f}M'
    elif x >= 1e3:
        return f'{x*1e-3:.0f}K'
    return f'{x:.0f}'

# Transforma 1.000.000 em "1M" e 1.000.000.000 em "1B"
def _formatar_dinheiro(x, pos=None):
    if x >= 1e9:
        return f'${x*1e-9:.1f}B'
    elif x >= 1e6:
        return f'${x*1e-6:.0f}M'
    elif x >= 1e3:
        return f'${x*1e-3:.0f}K'
    return f'${x:.0f}'

def _get_vote_count_ticks():
    """
    Marcadores logarítmicos para o engajamento do público (quantidade de votos).
    Ideal para ver a diferença entre filmes amadores e blockbusters históricos.
    """
    return [
        1,          # O filme que só o diretor avaliou
        10,         # Filmes indie locais / curtas de faculdade
        100,        # Filme cult ou antigo com público nichado
        1_000,      # Lançamento comercial padrão / Sucesso moderado
        10_000,     # Hit mundial do ano
        50_000,     # Mega Blockbuster histórico (Top 100 do TMDB)
        100_000     # Teto de segurança para visualização
    ]

def _get_nota_ticks_and_labels(escala=10):
    """
    Gera marcadores dinâmicos para notas. 
    Se escala=5 (Livros/Goodreads). Se escala=10 (Filmes/Animes).
    """
    match escala:
        case 5:
            dicionario_notas = {
                0.0: "0 (S/ Nota)", 1.0: "1 (Péssimo)", 2.0: "2 (Ruim)",
                3.0: "3 (Regular)", 4.0: "4 (Muito Bom)", 5.0: "5 (Obra-Prima)"
            } 
        case 10:
            dicionario_notas = {
                0.0: "0 (S/ Nota)", 1.0: "1 (Desastre)", 2.0: "2 (Péssimo)",
                3.0: "3 (Ruim)", 4.0: "4 (Fraco)", 5.0: "5 (Regular)",
                6.0: "6 (Ok)", 7.0: "7 (Bom)", 8.0: "8 (Ótimo)",
                9.0: "9 (Excelente)", 10.0: "10 (Obra-Prima)"
            }
        case 100:
            dicionario_notas = {
                0.0: "0 (S/ Nota)", 10.0: "10 (Desastre)", 20.0: "20 (Péssimo)",
                30.0: "30 (Ruim)", 40.0: "40 (Fraco)", 50.0: "50 (Regular)",
                60.0: "60 (Ok)", 70.0: "70 (Bom)", 80.0: "80 (Ótimo)",
                90.0: "90 (Excelente)", 100.0: "100 (Obra-Prima)"
            }
        case _:
            raise ValueError("Escala inválida.")
        
        
    posicoes = list(dicionario_notas.keys())
    rotulos = list(dicionario_notas.values())
    return posicoes, rotulos

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

def _desenhar_scatter_individual(ax, df_local, col_x, col_y):
    """Função sutil de auxílio para padronizar a renderização estática do scatter."""
    
    # Renderiza os pontos
    sns.scatterplot(
        data=df_local,
        x=col_x,
        y=col_y,
        alpha=0.5,      
        color='#2A6FDB',
        edgecolor='white',    
        ax=ax
    )
    
    # Linha de tendência analítica
    sns.regplot(
        data=df_local,
        x=col_x,
        y=col_y,
        scatter=False,
        color='#E63946',
        line_kws={'linewidth': 1.5, 'alpha': 0.8},
        ax=ax
    )
    
    # Padronização de labels e eixos
    ax.set_xlabel(col_x.replace('_', ' ').capitalize(), fontsize=10, fontweight='bold', color='#4A4E69')
    ax.grid(axis='both', linestyle=':', alpha=0.5)
    sns.despine(ax=ax)
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
    
    # Gráfico 1: Boxplot
    sns.boxplot(x=s_plot, ax=ax_box, color='#1E2780', fliersize=3, width=width)
    ax_box.set(xlabel='') 
    
    # Gráfico 2: Histograma + KDE
    sns.histplot(x=s_plot, ax=ax_hist, color='#1E2780', kde=True, bins=30, log_scale=usar_log)

    if usar_log:
        ax_hist.xaxis.set_minor_locator(ticker.NullLocator())
        ax_box.xaxis.set_minor_locator(ticker.NullLocator())

    # Configuração do eixo X 
    if valores_eixo_x is not None:

        ax_hist.xaxis.set_major_locator(ticker.FixedLocator(valores_eixo_x))
        labels = [
            _formatar_dinheiro(x) for x in valores_eixo_x
        ] if tipo_dado == 'moeda' else [
            str(x) for x in valores_eixo_x
        ]

        ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
        ax_hist.tick_params(axis='x', rotation=45)        
    else:
        match tipo_dado:
            case 'popularidade' if usar_log:
                ticks = [0.1, 1, 5, 10, 50, 100, 500, 1000]
                ticks = [t for t in ticks if t <= s_plot.max() * 1.5]
                labels = [str(t) for t in ticks]

                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(ticks))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
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
                formatter = ticker.FuncFormatter(_formatar_numero)

                ax_hist.xaxis.set_major_formatter(formatter)
                ax_hist.tick_params(axis='x', rotation=45)     

            case 'moeda' if usar_log:
                ticks = _get_entertainment_ticks()
                labels = [_formatar_dinheiro(x) for x in ticks]

                ax_hist.xaxis.set_major_locator(ticker.FixedLocator(ticks))
                ax_hist.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
                ax_hist.tick_params(axis='x', rotation=45) 

            case 'moeda':
                formatter = ticker.FuncFormatter(_formatar_dinheiro)

                ax_hist.xaxis.set_major_formatter(formatter)
                ax_hist.tick_params(axis='x', rotation=45)      

            case _:
                pass
    
    
    # Estilização
    titulo_real = titulo if titulo else f"Distribuição: {coluna.capitalize()}"
    ax_box.set_title(titulo_real, fontsize=14, pad=15)
    ax_hist.set_ylabel("Quantidade de Registros", fontsize=12)
    
    
    if usar_log:
        ax_hist.set_xlabel(f"{coluna.capitalize()} (Escala Logarítmica)", fontsize=12)
    else:
        ax_hist.set_xlabel(coluna.capitalize(), fontsize=12)

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
        bbox=dict(
            boxstyle='round,pad=0.5', 
            facecolor='white', 
            alpha=0.8, 
            edgecolor='gray'
        )
    )
        
    sns.despine(left=True, bottom=False)
    ax_box.spines['bottom'].set_visible(False)
    ax_box.tick_params(bottom=False)

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
    for container in ax.containers:
        ax.bar_label(
            container, 
            fmt='%.2f%%',      
            padding=5,          
            fontsize=10, 
            fontweight='bold', 
            color='#333333'
        )

    # Estilização
    titulo_real = titulo if titulo else f"Top Categorias: {nome_coluna.capitalize()}"
    ax.set_title(titulo_real, fontsize=15, fontweight='bold', color='#2B2D42', pad=20)
    ax.set_xlabel("Participação no Dataset (%)", fontsize=12)
    ax.set_ylabel("") 
    
    plt.xlim(0, df_plot['Porcentagem'].max() * 1.15)

    sns.despine(left=True, bottom=True) 
    
    # Busca a Entropia no relatório
    if relatorio_df is not None and nome_coluna in relatorio_df.index:
        entropia = relatorio_df.loc[nome_coluna, 'entropy_norm']
        ax.text(0.95, 0.05, f'Entropia (Caos): {entropia}', 
                transform=ax.transAxes, ha='right', fontsize=10, color='gray')
    
    plt.tight_layout()
    plt.show()

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
    Plota as frequências das variáveis relacionadas a tempo (anos, décadas, idade, meses).
    Se 'extracao' for 'month' ou 'year', tenta extrair a informação de uma coluna datetime.
    Caso contrário, assume que a coluna já está formatada (int, string) e conta os valores diretamente.
    """
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    # 1. Tratamento e Extração de Dados
    if extracao == 'year':
        dados = pd.to_datetime(df[coluna], errors='coerce').dt.year.dropna()
        nome_eixo = 'Ano'
    elif extracao == 'month':
        dados = pd.to_datetime(df[coluna], errors='coerce').dt.month.dropna()
        nome_eixo = 'Mês'
    else:
        # Pega a coluna no formato nativo (int, string, etc)
        dados = df[coluna].dropna()
        # Formata o nome do eixo para ficar bonito (ex: 'age_years' vira 'Age Years')
        nome_eixo = coluna.replace('_', ' ').title()

    # 2. Cálculo do Top N
    top_release = (
        dados.value_counts()
        .head(top_n)
        .reset_index()
    )
    top_release.columns = [nome_eixo, 'Contagem']

    # 3. Tipagem Defensiva para o Gráfico (Converte para string para garantir eixo categórico)
    if pd.api.types.is_numeric_dtype(top_release[nome_eixo]):
        top_release[nome_eixo] = top_release[nome_eixo].astype(int).astype(str)
    else:
        top_release[nome_eixo] = top_release[nome_eixo].astype(str)

    # 4. Configuração e Plotagem do Gráfico
    fig, ax = plt.subplots(figsize=tamanho_figura, dpi=polegadas)

    sns.barplot(
        x='Contagem',
        y=nome_eixo,
        data=top_release,
        palette=palette,
        hue=nome_eixo,
        width=width,
        legend=False, # Desativa legenda redundante do hue no seaborn moderno
        ax=ax
    )

    # 5. Adição dos Rótulos (Labels)
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt='%d',
            padding=8,
            fontsize=10,
            fontweight='bold',
            color='#333333'
        )

    # 6. Estilização do Título e Eixos
    titulo_real = titulo if titulo else f"Top {top_n} Frequências por {nome_eixo}"

    ax.set_title(
        titulo_real,
        fontsize=16,
        fontweight='bold',
        color='#2B2D42',
        loc='left',
        pad=20
    )

    ax.set_xlabel("Quantidade de Registros", fontsize=12)
    ax.set_ylabel("")

    ax.grid(axis='x', alpha=0.2)
    ax.set_xlim(0, top_release['Contagem'].max() * 1.15)
    sns.despine()

    plt.tight_layout()
    plt.show()


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
    Ajusta dinamicamente a arquitetura do layout baseando-se no quant_grafs 
    sem duplicar código de renderização.
    """

    lista_x = [coluna_x] if isinstance(coluna_x, str) else list(coluna_x)
    
   # Definição da Estrutura de Telas (Grid e Proporções)

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
    

    fig, axes = plt.subplots(
        n_rows, 
        n_cols, 
        figsize=tamanho_figura, 
        dpi=polegadas, 
        sharey=False
    )
    axes_flat = [axes] if quant_grafs == 1 else axes.flatten()


    # Laço Único de Renderização Eficiente
    for i in range(len(axes_flat)):
        ax = axes_flat[i]

        # Remove quadrantes órfãos do grid
        if i >= quant_grafs or i >= len(lista_x):
            fig.delaxes(ax)
            continue
            
        col_x = lista_x[i]
        df_local = df_plot[[col_x, coluna_y]].dropna()
        
        _desenhar_scatter_individual(ax, df_local, col_x, coluna_y)
        
        # Controle de visibilidade do eixo Y para não poluir grids múltiplos
        if quant_grafs == 1 or (i % n_cols == 0):
            ax.set_ylabel(coluna_y.replace('_', ' ').capitalize(), fontsize=10, fontweight='bold', color='#4A4E69')
        else:
            ax.set_ylabel('')

        # Filtro de Outliers por quadrante
        if limitar_eixos:
            ax.set_xlim(0, df_local[col_x].quantile(0.99))
            ax.set_ylim(0, df_local[coluna_y].quantile(0.99))
        else:
            ax.set_xlim(0, df_local[col_x].max() * 1.1)
            ax.set_ylim(0, df_local[coluna_y].max() * 1.1)


    #  Ajustes de Margens e Meta-dados
    titulo_real = titulo if titulo else f"Análise de Correlação com {coluna_y.replace('_', ' ').capitalize()}"
    fig.suptitle(titulo_real, fontsize=14, fontweight='bold', color='#2B2D42')

    # Ajuste milimétrico de margem dependendo da quantidade de linhas
    plt.subplots_adjust(top=0.88 if n_rows > 1 else 0.85, hspace=0.35, wspace=0.25)

    if limitar_eixos:
        texto_rodape = "* Observação: Os eixos estão limitados ao percentil 99 para mitigar distorções de outliers extremos."
        fig.text(0.02, -0.02 if n_rows > 1 else -0.05, texto_rodape, fontsize=9, style='italic', color='#4A4E69')

    plt.subplots_adjust(
        left=0.06,   # menor valor = mais para a esquerda
        right=0.98,
        top=0.88 if n_rows > 1 else 0.85,
        hspace=0.35,
        wspace=0.25
    )
    
    plt.show()

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
    Plota um Heatmap bivariado para avaliar a dependência entre duas variáveis categóricas.
    Calcula automaticamente o tamanho ideal do canvas com base no volume de dados.
    """

    _, polegadas, _ = _set_config_graf(polegadas)

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

    tabela_filtrada = tabela_absoluta.loc[
        top_languages,
        top_genres
    ]

    # Criação da Tabela Percentual (apenas dados filtrados)
    tabela_percentual = (
        tabela_filtrada.div(tabela_filtrada.sum(axis=1), axis=0)
    ) * 100

    # Motor de Dimensionamento Automático (Dynamic Layout)
    num_linhas = len(tabela_percentual.index)
    num_colunas = len(tabela_percentual.columns)
    
    largura_calculada = max(12, num_colunas * 1.1)
    altura_calculada = max(6, num_linhas * 0.75)
    
    fig, ax = plt.subplots(figsize=(largura_calculada, altura_calculada), dpi=polegadas)

    #  Renderização do Heatmap
    ax = sns.heatmap(
        tabela_percentual, 
        annot=False,          
        fmt=".1f",           
        cmap=palette,       
        linewidths=0,      
        cbar_kws={
            'label': 'Proporção dentro do grupo (%)',
            'shrink': 0.9
        },
        annot_kws={
            'size': 9
        },
        ax=ax
    )

    # 5Estilização de Títulos e Eixos (Sem negrito no título do eixo X)
    coluna_y = tabela_percentual.columns.name or "Categoria"
    coluna_x = tabela_percentual.index.name or "Grupo"

    titulo_real = (
        titulo
        if titulo
        else f"Análise Bivariada: {top_n} {coluna_y.capitalize()} por {top_n} {coluna_x.capitalize()}"
    )

    plt.title(titulo_real, fontsize=14, fontweight='bold', pad=20)
    plt.ylabel(coluna_x.capitalize(), fontsize=11)
    plt.xlabel(coluna_y.capitalize(), fontsize=11, labelpad=10)

    # Rotação inteligente para evitar que os textos longos se atropelem no eixo X
    if num_colunas > 3:
        plt.xticks(rotation=45, ha='right', rotation_mode='anchor')

    # Avaliação Estatística Inteligente no Rodapé (Match Case)
    p_texto = f"{p_valor:.4e}" if p_valor < 0.001 else f"{p_valor:.4f}"
    
    match p_valor:
        case p if p < 0.05:
            conclusao = "Existe associação estatística real (Variáveis Dependentes)"
        case _:
            conclusao = "As variáveis são independentes (Relação por acaso)"
    
    # Anotação ancorada ao eixo para não ser cortada ou colada nos rótulos
    p_texto = (
        f"{p_valor:.4e}"
        if p_valor < 0.001
        else f"{p_valor:.4f}"
    )

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

    fig.text(
        0.02,
        -0.06,
        texto_rodape,
        fontsize=10,
        style='italic',
        color='#4A4E69'
    )

    fig.subplots_adjust(bottom=0.18)
    plt.tight_layout()    

    # Abre o respiro inferior se as labels do eixo X estiverem rotacionadas em 45°
    if num_colunas > 3:
        plt.subplots_adjust(bottom=0.22)
        
    plt.show()