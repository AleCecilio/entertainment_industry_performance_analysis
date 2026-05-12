# =====================================================================
#    PALETA SEMÂNTICA CENTRAL
#    Inspirada em "Color Wise" de Kate Strachnyi.
#    Princípio: a cor comunica o tipo de dado, não o dado em si.
# =====================================================================
CORES = {
    'identificador': {'background-color': '#2B2D42', 'color': 'white'},  # Ardósia — títulos, IDs
    'criativo':      {'background-color': '#6D597A', 'color': 'white'},  # Roxo Muted — gêneros, coleções
    'entidade':      {'background-color': '#4A4E69', 'color': 'white'},  # Cinza Azulado — estúdios, autores
    'demografia':    {'background-color': '#3D5A80', 'color': 'white'},  # Azul Petróleo — países, idiomas
    'metrica':       {'background-color': '#D4A373', 'color': 'black'},  # Âmbar — scores, votos, $
    'financeiro':    {'background-color': '#588157', 'color': 'white'},  # Verde Musgo — budget, revenue
    'data':          {'background-color': '#9A8C98', 'color': 'white'},  # Cinza Rosado — datas, status
    'booleano':      {'background-color': '#C9ADA7', 'color': 'black'},  # Rosa Acinzentado — flags binárias
    'anomalia':      {'background-color': '#7B2D2D', 'color': 'white'},  # Vinho — nulos, zeros, outliers
    'neutro':        {'background-color': '#D8E2DC', 'color': 'black'},  # Verde Claro — colunas sem categoria
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
}


# =====================================================================
#    MAPEAMENTO DE COLUNAS → CATEGORIA SEMÂNTICA
#    Cobre nomes crus e limpos dos três datasets do projeto.
# =====================================================================
MAPA_COLUNAS = {
    # — Identificadores e Títulos —
    'id': 'identificador', 'Book Id': 'identificador', 'book_id': 'identificador',
    'anime_id': 'identificador', 'imdb_id': 'identificador',
    'isbn': 'identificador', 'isbn13': 'identificador',
    'title': 'identificador', 'Title': 'identificador',
    'original_title': 'identificador', 'title_english': 'identificador',
    'title_japanese': 'identificador', 'name': 'identificador',

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
    'roi': 'financeiro', 'box_office': 'financeiro',

    # — Datas e Status —
    'publication_date': 'data', 'release_date': 'data',
    'premiered': 'data', 'aired_string': 'data',
    'aired': 'data', 'status': 'data', 'year': 'data',

    # — Booleanos e Flags —
    'is_franchise': 'booleano', 'adult': 'booleano', 'is_sequel': 'booleano',
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
        ('padding', '6px 10px'),
    ]},
    {'selector': 'td', 'props': [
        ('text-align', 'left'),
        ('padding', '4px 10px'),
    ]},
    {'selector': 'caption', 'props': [
        ('font-weight', 'bold'),
        ('font-size', '13px'),
        ('text-align', 'left'),
        ('padding-bottom', '6px'),
    ]},
]


# =====================================================================
#   FORMATADORES PADRÃO POR TIPO DE COLUNA
# =====================================================================
FORMATADORES = {
    'budget':         'US$ {:,.0f}',
    'revenue':        'US$ {:,.0f}',
    'profit':         'US$ {:,.0f}',
    'roi':            '{:.1f}%',
    'vote_average':   '{:.1f}',
    'average_rating': '{:.2f}',
    'score':          '{:.2f}',
    'popularity':     '{:.2f}',
    'runtime':        '{:.0f} min',
    'Perda de Dados (%)': '{:.2f}%',
}





