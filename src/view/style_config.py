import numpy as np
import pandas as pd

# =====================================================================
#   PALETA DE CORES SEMÂNTICAS (Por Categoria)
# =====================================================================
_CORES = {
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
    'volume':        {'background-color': '#457B9D', 'color': 'white'},  # Azul Aço — Contagens absolutas
    'proporcao':     {'background-color': '#52796F', 'color': 'white'},  # Verde Sálvia — Porcentagens
    'descritivo':    {'font-style': 'italic'},                           # Apenas itálico para sinopses (sem fundo)
    'midia':         {'color': '#457B9D', 'text-decoration': 'underline'} # Estilo de Link para URLs
}

# Gradientes semânticos para .background_gradient()
_GRADIENTES = {
    'metrica':    'viridis',
    'financeiro': 'Greens',
    'anomalia':   'Reds',
    'volume':     'Oranges',
    'score':      'YlOrRd',
    'neutro':     'Blues',
    'divergente': 'RdYlGn',  # útil para ROI (negativo → positivo)
    'correlacao': 'BrBG' 
}


# =====================================================================
#    MAPEAMENTO DE COLUNAS → CATEGORIA SEMÂNTICA
#    Cobre nomes crus, limpos e os gerados na Harmonização (Canônicos)
# =====================================================================
_MAPA_COLUNAS = {
    # — Identificadores e Títulos —
    'index': 'identificador', 'level_0': 'identificador',
    'id': 'identificador', 'Book Id': 'identificador', 'book id': 'identificador', 'book_id': 'identificador',
    'anime_id': 'identificador', 'imdb_id': 'identificador',
    'isbn': 'identificador', 'isbn13': 'identificador',
    'title': 'identificador', 'Title': 'identificador',
    'original_title': 'identificador', 'title_english': 'identificador',
    'title_japanese': 'identificador', 'name': 'identificador',

    # — Textos Longos e Contexto —
    'overview': 'descritivo', 'tagline': 'descritivo',

    # — URLs, Imagens e Recursos Externos —
    'homepage': 'midia', 'poster_path': 'midia', 'image_url': 'midia',

    # — Categorias Criativas & Classificações —
    'genres': 'criativo', 'genre': 'criativo',
    'belongs_to_collection': 'criativo', 'collection': 'criativo',
    'type': 'criativo', 'source': 'criativo', 'rating': 'criativo',
    'popularity_tier': 'criativo', # <--- Nova Feature Global

    # — Entidades, Criadores e Estúdios —
    'Author': 'entidade', 'author': 'entidade', 'publisher': 'entidade',
    'production_companies': 'entidade', 'studio': 'entidade',
    'producer': 'entidade', 'licensor': 'entidade', 'director': 'entidade',
    'producer_company': 'entidade', 

    # — Demografia e Geografia —
    'language_code': 'demografia', 'original_language': 'demografia',
    'spoken_languages': 'demografia', 'production_countries': 'demografia',
    'country': 'demografia', 'language': 'demografia',

    # — Métricas de Recepção (scores, votos, popularidade) —
    'average_rating': 'metrica', 'vote_average': 'metrica', 'score': 'metrica',
    'ratings_count': 'metrica', 'vote_count': 'metrica', 'scored_by': 'metrica',
    'popularity': 'metrica', 'rank': 'metrica', 'favorites': 'metrica',
    'members': 'metrica', 'text_reviews_count': 'metrica',
    'total_votes': 'metrica', 
    'global_score': 'metrica', 
    'votes_per_year': 'metrica', # <--- Nova Feature Global

    # — Métricas Físicas (tamanho, duração) —
    'num_pages': 'metrica', 'runtime': 'metrica',
    'duration': 'metrica', 'episodes': 'metrica',
    'content_length': 'metrica', 

    # — Financeiro —
    'budget': 'financeiro', 'revenue': 'financeiro', 'profit': 'financeiro',
    'box_office': 'financeiro',

    # — Datas e Status —
    'publication_date': 'data', 'release_date': 'data',
    'premiered': 'data', 'aired_string': 'data',
    'aired': 'data', 'status': 'data', 'year': 'data',
    'release_year': 'data', 'decade': 'data', 'age_years': 'data', # <--- Novas Features Globais

    # — Booleanos e Flags —
    'is_franchise': 'booleano', 'adult': 'booleano', 'is_sequel': 'booleano',
    'video': 'booleano',

    # --- Mapeamento de Volumes Temporários (Contagens) ---
    'Contagem': 'volume', 'contagem': 'volume', 'count': 'volume', 

    # --- Mapeamento de Proporções (Porcentagens) ---
    'porcentagem': 'proporcao', 'Porcentagem': 'proporcao', 'roi': 'proporcao',
    'perda de dados (%)': 'proporcao', 'Perda de Dados (%)': 'proporcao',

    # --- Mapeamento de Correlações ---
    'correlacao': 'correlacao', 'Correlacao': 'correlacao',
}


# =====================================================================
#   ESTILO BASE DE TABELA (cabeçalho + alinhamento)
# =====================================================================
_ESTILO_CABECALHO = [
    {'selector': 'th', 'props': [
        ('background-color', '#2B2D42'),
        ('color', 'white'),
        ('text-align', 'left'),
        ('font-weight', 'bold'),
        ('padding', '10px 15px'), 
    ]},
    {'selector': 'td', 'props': [
        ('text-align', 'left'),
        ('padding', '8px 15px'),  
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
def _criar_formatador(padrao_string):
    """
    Recebe uma string de formatação (ex: 'US$ {:,.0f}') e retorna uma função
    segura que converte o valor para float antes de formatar. 
    Evita quebra de código (ValueError) se o dado for String ou NaN.
    """
    def formatar(valor):
        if pd.isna(valor) or valor == "":
            return np.nan
        try:
            return padrao_string.format(float(valor))
        except (ValueError, TypeError):
            return str(valor)
    return formatar


# =====================================================================
# DICIONÁRIO DE FORMATADORES APLICANDO A BLINDAGEM
# =====================================================================
_FORMATADORES = {
    # --- Financeiro ---
    'budget':     _criar_formatador('US$ {:,.0f}'),
    'revenue':    _criar_formatador('US$ {:,.0f}'),
    'profit':     _criar_formatador('US$ {:,.0f}'),
    'box_office': _criar_formatador('US$ {:,.0f}'),
    
    # --- Proporções e Porcentagens ---
    'roi':                _criar_formatador('{:.1f}%'),
    'perda de dados (%)': _criar_formatador('{:.2f}%'),
    'Perda de Dados (%)': _criar_formatador('{:.2f}%'),
    'porcentagem':        _criar_formatador('{:.2f}%'),
    'Porcentagem':        _criar_formatador('{:.2f}%'),
    
    # --- Volumes (Contagens inteiras com separador de milhares) ---
    'Contagem':      _criar_formatador('{:,.0f}'),
    'contagem':      _criar_formatador('{:,.0f}'),
    'count':         _criar_formatador('{:,.0f}'),
    'vote_count':    _criar_formatador('{:,.0f}'),
    'ratings_count': _criar_formatador('{:,.0f}'),
    'total_votes':   _criar_formatador('{:,.0f}'),  
    'votes_per_year':_criar_formatador('{:,.0f}'), # <--- Nova Feature Global
    
    # --- Notas e Popularidade ---
    'vote_average':    _criar_formatador('{:.1f}'),
    'average_rating':  _criar_formatador('{:.2f}'),
    'score':           _criar_formatador('{:.2f}'),
    'popularity':      _criar_formatador('{:.2f}'),
    'global_score': _criar_formatador('{:.2f}'), 
    
    # --- Grandezas Físicas e Temporais ---
    'runtime':        _criar_formatador('{:.0f} min'),
    'num_pages':      _criar_formatador('{:,.0f} págs'),
    'content_length': _criar_formatador('{:,.0f}'),  
    'release_year':   _criar_formatador('{:.0f}'),      # <--- Sem vírgula para anos
    'age_years':      _criar_formatador('{:.0f} anos'), # <--- Sufixo descritivo

    # --- Correlação (Coeficiente puro, SEM porcentagem) ---
    'correlacao': _criar_formatador('{:.2f}'),
    'Correlacao': _criar_formatador('{:.2f}'),
}