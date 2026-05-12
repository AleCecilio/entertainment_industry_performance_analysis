import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =====================================================================
#   Plots 
# =====================================================================

FIGSIZE_DEFALT = (12, 8)
DPI_DEFALT = 120
WIDTH_DEFALT = 0.8

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