import pandas as pd
from datetime import datetime

# =====================================================================
# TRANSFORMAÇÕES ESTRUTURAIS DE DATASETS
# =====================================================================
def explodir_dataset(df, coluna):
    """
    Descompacta colunas que contêm listas (ex: gêneros, estúdios), 
    criando uma nova linha para cada item da lista e duplicando os demais dados.
    """

    # Descompacta a lista (O motor real do Pandas)
    df_new = df.explode(coluna)

    # Limpa espaços invisíveis (O .str.strip() lida bem com NaNs nativamente)
    # Apenas se certifica de aplicar como string
    df_new[coluna] = df_new[coluna].astype(str).str.strip()

    # Reseta o índice para não termos vários índices repetidos (ex: 0, 0, 0, 1, 2)
    df_new.reset_index(drop=True, inplace=True)

    return df_new



def criar_features_globais(df, coluna, nota_maxima):
    """
    Cria uma coluna com o score global baseado na nota máxima.
    Gera métricas globais de negócio válidas tanto para filmes quanto para livros,
    utilizando as colunas do Modelo Canónico.
    """

    df_feat = df.copy()

    if nota_maxima == 5:
        df_feat['global_score'] = (df_feat[coluna] / 5) * 100   
    elif nota_maxima == 10:
        df_feat['global_score'] = (df_feat[coluna] / 10) * 100
    
    # Garante que a release_date é do tipo datetime
    df_feat['release_date'] = pd.to_datetime(df_feat['release_date'], errors='coerce')
    
    # Criar Ano e Década
    df_feat['release_year'] = df_feat['release_date'].dt.year
    df_feat['decade'] = (df_feat['release_year'] // 10) * 10

    
    # Idade da Obra (Calculada com base no ano atual)
    ano_atual = datetime.now().year
    df_feat['age_years'] = ano_atual - df_feat['release_year']
    df_feat['age_years'] = df_feat['age_years'].replace(0, 1)
    
    # Taxa de Engajamento Anual (Votos por Ano)
    df_feat['votes_per_year'] = df_feat['total_votes'] / df_feat['age_years']
    
    # Quadrante de Popularidade (Exemplo simples usando a mediana)
    mediana_votos = df_feat['total_votes'].median()
    mediana_notas = df_feat['global_score'].median()
    
    def classificar_quadrante(row):
        if pd.isna(row['total_votes']) or pd.isna(row['global_score']):
            return 'Desconhecido'
            
        if row['total_votes'] >= mediana_votos and row['global_score'] >= mediana_notas:
            return 'Mainstream Hit' # (Aclamado e Popular)
        elif row['total_votes'] >= mediana_votos and row['global_score'] < mediana_notas:
            return 'Mass Appeal' # (Popular, mas Divisivo/Medíocre)
        elif row['total_votes'] < mediana_votos and row['global_score'] >= mediana_notas:
            return 'Hidden Gem / Cult' # (Pouco conhecido, mas muito Aclamado)
        else:
            return 'Nicho' # (Poucos votos e baixa/média avaliação)

    df_feat['popularity_tier'] = df_feat.apply(classificar_quadrante, axis=1)
    
    return df_feat



def harmonizar_esquema_dados(df, tipo_midia):
    """
    Padroniza os nomes das colunas (Schema Alignment) para um Modelo Canónico em inglês
    e garante que todas as colunas fiquem em letras minúsculas.
    """
    if tipo_midia == 'filme':
        dicionario_renomeacao = {
            'vote_average': 'average_rating',      
            'vote_count': 'total_votes',     
            'production_companies': 'producer_company',
        }
        
    elif tipo_midia == 'livro':
        dicionario_renomeacao = {
            'ratings_count': 'total_votes',
            'publication_date': 'release_date',    
            'publisher': 'producer_company',
            'language_code': 'original_language'
        }
        
    else:
        raise ValueError("Erro: O tipo_midia deve ser 'filme' ou 'livro'.")
        
    # 1. Aplica o mapeamento do modelo canônico
    df = df.rename(columns=dicionario_renomeacao)
    
    # 2. Força absolutamente todas as colunas do DataFrame a ficarem em minúsculo
    df.columns = df.columns.str.lower()
    
    return df