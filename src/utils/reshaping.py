import pandas as pd

def gerar_contingencia(df, coluna_linha, coluna_coluna, top_n_linhas=20, top_n_colunas=20):
    """
    Gera uma tabela de contingência cruzando duas colunas que contêm listas.
    Aplica filtros de 'Top N' precocemente para evitar explosão de memória.
    """
    # Isola as colunas que importam
    df_base = df[[coluna_linha, coluna_coluna]].dropna().copy()

    # Explode e filtra a primeira coluna (que vai virar as Linhas da tabela)
    df_linhas = df_base.explode(coluna_linha)
    top_linhas = df_linhas[coluna_linha].value_counts().head(top_n_linhas).index
    df_linhas = df_linhas[df_linhas[coluna_linha].isin(top_linhas)]

    # Explode e filtra a segunda coluna (que vai virar as Colunas da tabela)
    df_crosstab = df_linhas.explode(coluna_coluna)
    top_colunas = df_crosstab[coluna_coluna].value_counts().head(top_n_colunas).index
    df_crosstab = df_crosstab[df_crosstab[coluna_coluna].isin(top_colunas)]

    # Gera a tabela final
    tabela_contingencia = pd.crosstab(
        df_crosstab[coluna_linha], 
        df_crosstab[coluna_coluna]
    )
    
    return tabela_contingencia