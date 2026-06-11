import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from pandas.plotting import parallel_coordinates

from ._config import _set_config_graf
from ._formatters import _formatar_eixo_numerico

# ===== Gráfico Pairplot para Variáveis Numéricas =====

def grafico_pairplot_numericos(       
        df_plot, 
        cols_focadas=None,
        col_log=None,
        coluna_hue=None,
        amostra=3000,
        titulo=None,
        paleta='colorblind',
        altura_painel=4.0,
        aspecto=1.2
):
    
    colunas_numericas = df_plot.select_dtypes(include=[np.number]).columns.tolist()
    
    colunas_finais = colunas_numericas.copy()
    if coluna_hue and coluna_hue in df_plot.columns:
        colunas_finais.append(coluna_hue)
        
    df_numerico = df_plot[colunas_finais].copy()

    if col_log:
        for col, regras in col_log.items():
            if col in df_numerico.columns and regras.get('usar_log', False):
                df_numerico[col] = df_numerico[col].mask(df_numerico[col] <= 0, np.nan)
                
    df_numerico = df_numerico.dropna()

    if len(colunas_numericas) < 2:
        print("Erro: São necessárias pelo menos 2 colunas numéricas para um Pairplot.")
        return

    if amostra and len(df_numerico) > amostra:
        df_numerico = df_numerico.sample(n=amostra, random_state=42)
        print(f"Nota: Exibindo amostra aleatória de {amostra} registros para performance.")

    if cols_focadas:
        cols_focadas = [col for col in cols_focadas if col in colunas_numericas]
        if not cols_focadas:
            print("Aviso:")
            print("Nenhuma das colunas focadas é numérica ou existe no DataFrame.") 
            print("Usando todas as numéricas.")
            cols_focadas = colunas_numericas
    else:
        cols_focadas = colunas_numericas

    g = sns.pairplot(
        data=df_numerico,
        hue=coluna_hue,
        vars=cols_focadas,  
        palette=paleta,
        corner=True,
        diag_kind='kde',             
        aspect=aspecto,
        height=altura_painel,
        plot_kws={
            'alpha': 0.7,        
            's': 25,             
            'edgecolor': 'none', 
        },diag_kws={
            'cut': 0  
        }
    )

    g.figure.subplots_adjust(wspace=0.05, hspace=0.05, top=1, right=0.88, bottom=0.08, left=0.08)

    for ax in g.diag_axes:
        ax.remove()

    if coluna_hue:
        sns.move_legend(
            g, 
            loc="upper right", 
            bbox_to_anchor=(0.98, 0.95), 
            fontsize=12, 
            title_fontsize=14,
            frameon=True,
            shadow=True
        )

    if col_log:
        for i, y_var in enumerate(g.y_vars):
            for j, x_var in enumerate(g.x_vars):
                
                ax_atual = g.axes[i, j]

                if ax_atual is None:
                    continue
                
                if x_var in col_log:
                    if col_log[x_var].get('usar_log', False):
                        ax_atual.set_xlim(left=df_numerico[x_var].min())
                        
                    _formatar_eixo_numerico(
                        ax=ax_atual, 
                        s_plot=df_numerico[x_var], 
                        usar_log=col_log[x_var].get('usar_log', False),
                        tipo_dado=col_log[x_var].get('tipo_dado'),
                        valores_eixo=col_log[x_var].get('valores_eixo'),
                        eixo='x',
                        menos_valores=True
                    )
                
                if y_var in col_log:
                    if i != j:
                        if col_log[y_var].get('usar_log', False):
                            ax_atual.set_ylim(bottom=df_numerico[y_var].min())
                            
                        _formatar_eixo_numerico(
                            ax=ax_atual, 
                            s_plot=df_numerico[y_var], 
                            usar_log=col_log[y_var].get('usar_log', False),
                            tipo_dado=col_log[y_var].get('tipo_dado'),
                            valores_eixo=col_log[y_var].get('valores_eixo'),
                            eixo='y',
                            menos_valores=True
                        )
    
    titulo_real = titulo if titulo else 'Matriz de Correlação Multivariada'
    g.figure.suptitle(titulo_real, y=0.98, fontsize=18, fontweight='bold', color='#2B2D42')
    
    plt.show()

# ===== Gráfico Bubble Charts para Análise Multivariada =====

def grafico_bubble_multivariado(
        df_plot, 
        x_col_dict,  # Ex: {'col': 'num_pages', 'tipo_dado': 'contagem', 'usar_log': False}
        y_col_dict,  # Ex: {'col': 'average_rating', 'tipo_dado': 'nota_5', 'usar_log': False}
        size_col=None, 
        hue_col=None, 
        titulo=None,
        tamanho_figura=None,
        polegadas=100,
        alpha=0.6,
        size_range=(20, 800),
        palette='Set1'
):
    """
    Gera um Gráfico de Bolhas (Bubble Chart) cruzando até 4 dimensões (X, Y, Tamanho e Cor).
    """
    
    # Configuração Inicial e Extração de Nomes
    tamanho_figura, polegadas, _ = _set_config_graf(tamanho_figura, polegadas)
    
    x_nome = x_col_dict.get('col')
    y_nome = y_col_dict.get('col')
    
    df_clean = df_plot.copy()

    # Blindagem Matemática (Tratamento de Zeros para Log)
    if x_col_dict.get('usar_log', False):
        df_clean[x_nome] = df_clean[x_nome].mask(df_clean[x_nome] <= 0, np.nan)
        
    if y_col_dict.get('usar_log', False):
        df_clean[y_nome] = df_clean[y_nome].mask(df_clean[y_nome] <= 0, np.nan)

    # Renderização do Gráfico
    fig, ax = plt.subplots(figsize=tamanho_figura, dpi=polegadas)
    
    sns.scatterplot(
        data=df_clean,
        x=x_nome,
        y=y_nome,
        size=size_col,     
        sizes=size_range,        
        hue=hue_col,  
        alpha=alpha,              
        palette=palette,
        edgecolor='w', 
        ax=ax
    )
    
    # Formatação Dinâmica dos Eixos (Não precisa de For Loop, é apenas um eixo!)
    if x_col_dict.get('usar_log', False):
        ax.set_xlim(left=df_clean[x_nome].min())
        
    _formatar_eixo_numerico(
        ax=ax, 
        s_plot=df_clean[x_nome], 
        usar_log=x_col_dict.get('usar_log', False),
        tipo_dado=x_col_dict.get('tipo_dado'),
        valores_eixo=x_col_dict.get('valores_eixo'),
        eixo='x'
    )

    if y_col_dict.get('usar_log', False):
        ax.set_ylim(bottom=df_clean[y_nome].min())
        
    _formatar_eixo_numerico(
        ax=ax, 
        s_plot=df_clean[y_nome], 
        usar_log=y_col_dict.get('usar_log', False),
        tipo_dado=y_col_dict.get('tipo_dado'),
        valores_eixo=y_col_dict.get('valores_eixo'),
        eixo='y'
    )
    
    # Estilização Final
    plt.title(titulo if titulo else f"Bubble Chart: {x_nome} vs {y_nome}", fontsize=16, fontweight='bold', pad=15)
    plt.xlabel(x_nome.replace('_', ' ').title(), fontsize=12)
    plt.ylabel(y_nome.replace('_', ' ').title(), fontsize=12)
    
    # Move a legenda complexa (que junta Cor e Tamanho) para fora do gráfico
    if hue_col or size_col:
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1.02, 1), title_fontsize=12, frameon=True)
    
    plt.tight_layout()
    plt.show()

# ===== Gráfico de Coordenadas Paralelas =====

def grafico_coordenadas_paralelas(
        df_plot, 
        colunas_jornada, 
        coluna_categoria, 
        titulo=None, 
        tamanho_figura=None,
        polegadas=100,
        amostra=600, 
        alpha=0.5,
        palette='Set2'
):
    """
    Gera um Gráfico de Coordenadas Paralelas aplicando Normalização MinMax 
    automaticamente para alinhar escalas diferentes.
    """
    tamanho_figura, polegadas, _ = _set_config_graf(tamanho_figura, polegadas)

    df_plot = df_plot[colunas_jornada + [coluna_categoria]].copy()

    # Amostragem para evitar o "Efeito Esparguete"
    if len(df_plot) > amostra:
        df_plot = df_plot.sample(n=amostra, random_state=42)
        
    # Normalização Inteligente (MinMaxScaler: converte tudo para 0 a 1)
    scaler = MinMaxScaler()
    df_scaled = df_plot.copy()
    df_scaled[colunas_jornada] = scaler.fit_transform(df_scaled[colunas_jornada])
    
    # Extração de Cores do Seaborn para o Pandas
    categorias_unicas = df_scaled[coluna_categoria].unique()
    paleta_cores = sns.color_palette(palette, n_colors=len(categorias_unicas)).as_hex()
    
    # Renderização do Gráfico
    plt.figure(figsize=tamanho_figura, dpi=polegadas)
    
    ax = parallel_coordinates(
        df_scaled,
        class_column=coluna_categoria,
        color=paleta_cores,
        alpha=alpha,
        linewidth=1.5
    )
    
    # Estilização
    plt.title(
        titulo if titulo 
        else f"Perfil Multivariado (Normalizado 0-1) por {coluna_categoria}", 
        fontsize=16, 
        fontweight='bold', 
        pad=15
    )
    plt.ylabel("Escala Relativa (0 = Mínimo | 1 = Máximo)", fontsize=12)
    
    # Limpar a grade do eixo Y pois os valores absolutos não importam mais, apenas a posição relativa
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    
    # Melhorar a leitura dos rótulos do eixo X
    plt.xticks(fontsize=11, fontweight='bold')
    
    # Ajustar Legenda
    plt.legend(title=coluna_categoria.replace('_', ' ').title(), bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
    
    plt.tight_layout()
    plt.show()


def grafico_coordenadas_paralelas_interativo(
        df_plot,
        colunas_jornada,
        coluna_categoria,
        titulo='Gráfico Coordenadas Paralelas',
        amostra=800
):
    """
    Gera um Gráfico de Coordenadas Paralelas Interativo usando Plotly.
    Permite arrastar eixos e filtrar dados selecionando intervalos com o rato.
    Inclui legenda dinâmica para qualquer variável categórica.
    """

    # Filtro e Amostragem (Evitar o "Efeito Esparguete")
    df_plot = df_plot[colunas_jornada + [coluna_categoria]].copy()

    if len(df_plot) > amostra:
        df_plot = df_plot.sample(n=amostra, random_state=42)

    # Normalização Inteligente (0 a 1)
    scaler = MinMaxScaler()
    df_scaled = df_plot.copy()
    df_scaled[colunas_jornada] = scaler.fit_transform(
        df_scaled[colunas_jornada]
    )

    # Categorias encontradas
    categorias = sorted(df_scaled[coluna_categoria].dropna().unique())

    # IDs numéricos para o Plotly
    mapa_ids = {cat: i for i, cat in enumerate(categorias)}
    df_scaled["Categoria_ID"] = (
        df_scaled[coluna_categoria].map(mapa_ids)
    )

    # Paleta reutilizável
    cores = [
        "#D65F5F",  # vermelho suave
        "#48A365",  # verde sálvia
        "#5E81AC",  # azul nórdico
        "#D79921",  # amarelo mostarda
        "#8E6C8A",  # roxo
        "#4C9F9F",  # turquesa
        "#C97B63",  # terracota
        "#6B7280",  # cinza
    ]

    # Escala contínua baseada no número de categorias
    if len(categorias) == 1:
        color_scale = [(0, cores[0]), (1, cores[0])]
    else:
        color_scale = [
            (
                i / (len(categorias) - 1),
                cores[i % len(cores)]
            )
            for i in range(len(categorias))
        ]

    # Criação do gráfico
    fig = px.parallel_coordinates(
        df_scaled,
        dimensions=colunas_jornada,
        color="Categoria_ID",
        color_continuous_scale=color_scale,
        title=f"<b>{titulo}</b>",
        labels={
            col: col.replace("_", " ").title()
            for col in colunas_jornada
        }
    )

    # Construção dinâmica da legenda
    legenda_html = "<b>Categorias</b><br>"

    for i, categoria in enumerate(categorias):
        cor = cores[i % len(cores)]
        legenda_html += (
            f'<span style="color:{cor};">■</span> '
            f'{categoria}<br>'
        )

    fig.add_annotation(
        text=legenda_html,
        x=1.22,          
        y=1,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="left",
        bordercolor="lightgray",
        borderwidth=1,
        bgcolor="white",
        font=dict(size=12)
    )

    # Layout
    fig.update_layout(
        coloraxis_showscale=False,
        font=dict(size=12),
        margin=dict(
            l=50,
            r=150,   
            b=50,
            t=80
        )
    )

    fig.show()