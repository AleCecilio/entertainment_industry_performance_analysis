import pandas as pd

# =====================================================================
# TRANSFORMAÇÕES ESTRUTURAIS DE DATASETS
# =====================================================================
def explodir_dataset(df, coluna):
    """
    Descompacta colunas que contêm listas (ex: gêneros, estúdios), 
    criando uma nova linha para cada item da lista e duplicando os demais dados.
    """

    # 2. Descompacta a lista (O motor real do Pandas)
    df_new = df.explode(coluna)

    # 3. Limpa espaços invisíveis (O .str.strip() lida bem com NaNs nativamente)
    # Apenas se certifica de aplicar como string
    df_new[coluna] = df_new[coluna].astype(str).str.strip()

    # 4. Reseta o índice para não termos vários índices repetidos (ex: 0, 0, 0, 1, 2)
    df_new.reset_index(drop=True, inplace=True)

    return df_new