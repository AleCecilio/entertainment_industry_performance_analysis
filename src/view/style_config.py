import pandas as pd

# =====================================================================
#   PALETA DE CORES SEMÂNTICAS (Por Categoria)
# =====================================================================
CORES = {
    'identificador': {'background-color': '#2B2D42', 'color': 'white'},  # Ardósia — títulos, IDs
    'criativo':      {'background-color': '#6D597A', 'color': 'white'},  # Roxo Muted — gêneros, coleções
    'entidade':      {'background-color': '#4A4E69', 'color': 'white'},  # Cinza Azulado — estúdios, autores
    'demografia':    {'background-color': '#3D5A80', 'color': 'white'},  # Azul Petróleo — países, idiomas
    'metrica':       {'background-color': '#D4A373', 'color': 'black'},  # Âmbar — scores, votos
    'financeiro':    {'background-color': '#588157', 'color': 'white'},  # Verde Musgo — budget, revenue
    'data':          {'background-color': '#9A8C98', 'color': 'white'},  # Cinza Rosado — datas, status
    'booleano':      {'background-color': '#C9ADA7', 'color': 'black'},  # Rosa Acinzentado — flags binárias
    'anomalia':      {'background-color': '#7B2D2D', 'color': 'white'},  # Vinho — nulos, outliers
    'neutro':        {'background-color': '#D8E2DC', 'color': 'black'},  # Verde Claro — sem categoria
    
    # 🎨 NOVAS CORES ANALÍTICAS E DE CONTEXTO
    'volume':        {'background-color': '#457B9D', 'color': 'white'},  # Azul Aço — Contagens absolutas
    'proporcao':     {'background-color': '#52796F', 'color': 'white'},  # Verde Sálvia — Porcentagens
    'descritivo':    {'font-style': 'italic'},                           # Apenas itálico para sinopses (sem fundo)
    'midia':         {'color': '#457B9D', 'text-decoration': 'underline'} # Estilo de Link para URLs
}

# Gradientes semânticos para .background_gradient()
GRADIENTES = {
    'metrica':    'viridis',
    'financeiro': 'Greens',
    'anomalia':   'Reds',
    'volume':     'Oranges',
    'score':      'YlOrRd',
    'neutro':     'Blues',
    'divergente': 'RdYlGn',  # útil para ROI (negativo → positivo)
    'correlacao': 'RdBu_r' 
}


# =====================================================================
#    MAPEAMENTO DE COLUNAS → CATEGORIA SEMÂNTICA
#    Cobre nomes crus e limpos dos três datasets do projeto.
# =====================================================================
MAPA_COLUNAS = {
    # — Identificadores e Títulos —
    'index': 'identificador', 'level_0': 'identificador',
    'id': 'identificador', 'Book Id': 'identificador', 'book_id': 'identificador',
    'anime_id': 'identificador', 'imdb_id': 'identificador',
    'isbn': 'identificador', 'isbn13': 'identificador',
    'title': 'identificador', 'Title': 'identificador',
    'original_title': 'identificador', 'title_english': 'identificador',
    'title_japanese': 'identificador', 'name': 'identificador',

    # — Textos Longos e Contexto (Recomendado deixar sem cor de fundo para legibilidade) —
    'overview': 'descritivo', 'tagline': 'descritivo',

    # — URLs, Imagens e Recursos Externos —
    'homepage': 'midia', 'poster_path': 'midia', 'image_url': 'midia',

    # — Categorias Criativas —
    'genres': 'criativo', 'genre': 'criativo',
    'belongs_to_collection': 'criativo', 'collection': 'criativo',
    'type': 'criativo', 'source': 'criativo', 'rating': 'criativo',

    # — Entidades, Criadores e Estúdios —
    'Author': 'entidade', 'author': 'entidade', 'publisher': 'entidade',
    'production_companies': 'entidade', 'studio': 'entidade',
    'producer': 'entidade', 'licensor': 'entidade', 'director': 'entidade',

    # — Demografia e Geografia —
    'language_code': 'demografia', 'original_language': 'demografia',
    'spoken_languages': 'demografia', 'production_countries': 'demografia',
    'country': 'demografia', 'language': 'demografia',

    # — Métricas de Recepção (scores, votos, popularidade) —
    'average_rating': 'metrica', 'vote_average': 'metrica', 'score': 'metrica',
    'ratings_count': 'metrica', 'vote_count': 'metrica', 'scored_by': 'metrica',
    'popularity': 'metrica', 'rank': 'metrica', 'favorites': 'metrica',
    'members': 'metrica', 'text_reviews_count': 'metrica',

    # — Métricas Físicas (tamanho, duração) —
    'num_pages': 'metrica', 'runtime': 'metrica',
    'duration': 'metrica', 'episodes': 'metrica',

    # — Financeiro —
    'budget': 'financeiro', 'revenue': 'financeiro', 'profit': 'financeiro',
    'box_office': 'financeiro',

    # — Datas e Status —
    'publication_date': 'data', 'release_date': 'data',
    'premiered': 'data', 'aired_string': 'data',
    'aired': 'data', 'status': 'data', 'year': 'data',

    # — Booleanos e Flags —
    'is_franchise': 'booleano', 'adult': 'booleano', 'is_sequel': 'booleano',
    'video': 'booleano', # Na API do TMDb, 'video' é True/False indicando se há asset de vídeo

    # --- Mapeamento de Volumes Temporários (Contagens) ---
    'Contagem': 'volume', 'contagem': 'volume', 'count': 'volume', 

    # --- Mapeamento de Proporções (Porcentagens) ---
    'porcentagem': 'proporcao', 'Porcentagem': 'proporcao', 'roi': 'proporcao',

    # --- Mapeamento de Correlações ---
    'correlacao': 'correlacao', 'Correlacao': 'correlacao',
}


# =====================================================================
#   ESTILO BASE DE TABELA (cabeçalho + alinhamento)
# =====================================================================
ESTILO_CABECALHO = [
    {'selector': 'th', 'props': [
        ('background-color', '#2B2D42'),
        ('color', 'white'),
        ('text-align', 'left'),
        ('font-weight', 'bold'),
        ('padding', '10px 15px'), # Ajustado para dar o mesmo respiro elegante do layout auto
    ]},
    {'selector': 'td', 'props': [
        ('text-align', 'left'),
        ('padding', '8px 15px'),  # Margem interna confortável
    ]},
    {'selector': 'caption', 'props': [
        ('font-weight', 'bold'),
        ('font-size', '14px'),
        ('text-align', 'left'),
        ('padding-bottom', '8px'),
    ]},
]

# =====================================================================
# FÁBRICA DE FORMATADORES DEFENSIVOS
# =====================================================================
def criar_formatador(padrao_string):
    """
    Recebe uma string de formatação (ex: 'US$ {:,.0f}') e retorna uma função
    segura que converte o valor para float antes de formatar. 
    Evita quebra de código (ValueError) se o dado for String ou NaN.
    """
    def formatar(valor):
        if pd.isna(valor) or valor == "":
            return "—"
        try:
            # Força a conversão para float para aplicar a regra matemática 'f'
            return padrao_string.format(float(valor))
        except (ValueError, TypeError):
            # Se for um texto que não vira número de jeito nenhum, exibe como texto
            return str(valor)
    return formatar


# =====================================================================
# DICIONÁRIO DE FORMATADORES APLICANDO A BLINDAGEM
# =====================================================================
FORMATADORES = {
    # --- Financeiro ---
    'budget':     criar_formatador('US$ {:,.0f}'),
    'revenue':    criar_formatador('US$ {:,.0f}'),
    'profit':     criar_formatador('US$ {:,.0f}'),
    'box_office': criar_formatador('US$ {:,.0f}'),
    
    # --- Proporções e Porcentagens ---
    'roi':                criar_formatador('{:.1f}%'),
    'Perda de Dados (%)': criar_formatador('{:.2f}%'),
    'porcentagem':        criar_formatador('{:.2f}%'),
    'Porcentagem':        criar_formatador('{:.2f}%'),
    
    # --- Volumes (Contagens inteiras com separador de milhares) ---
    'Contagem':      criar_formatador('{:,.0f}'),
    'contagem':      criar_formatador('{:,.0f}'),
    'count':         criar_formatador('{:,.0f}'),
    'vote_count':    criar_formatador('{:,.0f}'),
    'ratings_count': criar_formatador('{:,.0f}'),
    
    # --- Notas e Popularidade ---
    'vote_average':   criar_formatador('{:.1f}'),
    'average_rating': criar_formatador('{:.2f}'),
    'score':          criar_formatador('{:.2f}'),
    'popularity':     criar_formatador('{:.2f}'),
    
    # --- Grandezas Físicas ---
    'runtime':   criar_formatador('{:.0f} min'),
    'num_pages': criar_formatador('{:,.0f} págs'),

    # --- Correlação (Coeficiente puro, SEM porcentagem) ---
    'correlacao': criar_formatador('{:.2f}'),
    'Correlacao': criar_formatador('{:.2f}'),
}





