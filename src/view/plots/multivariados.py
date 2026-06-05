import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from ._formatters import _formatar_eixo_numerico

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
                        eixo='x'
                    )
                
                if y_var in col_log:
                    if col_log[y_var].get('usar_log', False):
                        ax_atual.set_ylim(bottom=df_numerico[y_var].min())
                        
                    _formatar_eixo_numerico(
                        ax=ax_atual, 
                        s_plot=df_numerico[y_var], 
                        usar_log=col_log[y_var].get('usar_log', False),
                        tipo_dado=col_log[y_var].get('tipo_dado'),
                        valores_eixo=col_log[y_var].get('valores_eixo'),
                        eixo='y'
                    )
    
    titulo_real = titulo if titulo else 'Matriz de Correlação Multivariada'
    g.figure.suptitle(titulo_real, y=0.98, fontsize=18, fontweight='bold', color='#2B2D42')
    
    plt.show()