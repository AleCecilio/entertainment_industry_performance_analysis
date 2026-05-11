import pandas as pd
import numpy as np

# =====================================================================
# 1. PALETA SEMÂNTICA CENTRAL
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
# 2. MAPEAMENTO DE COLUNAS → CATEGORIA SEMÂNTICA
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
# 3. ESTILO BASE DE TABELA (cabeçalho + alinhamento)
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
# 4. FORMATADORES PADRÃO POR TIPO DE COLUNA
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


# =====================================================================
# 5. TEMPLATES DE VISUALIZAÇÃO
# =====================================================================

def estilizar_tabela(df, colunas_selecionadas=None, qtd_linhas=None, caption=None):
    """
    Template geral: aplica cores semânticas por coluna + cabeçalho padronizado.
    Nulos exibidos como '—' em cinza itálico.

    Parâmetros
    ----------
    df                  : DataFrame de entrada
    colunas_selecionadas: lista de colunas a exibir (None = todas)
    qtd_linhas          : número de linhas a exibir
    caption             : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    if colunas_selecionadas:
        colunas_validas = [c for c in colunas_selecionadas if c in df.columns]
        df_foco = df[colunas_validas].head(qtd_linhas)
    else:
        df_foco = df.head(qtd_linhas)

    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    for coluna in df_foco.columns:
        categoria = MAPA_COLUNAS.get(coluna)
        if categoria and categoria in CORES:
            estilo = estilo.set_properties(subset=[coluna], **CORES[categoria])

    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }

    estilo = estilo.map(
        lambda v: 'color: #888888; font-style: italic' if pd.isna(v) else ''
    ).format(formatter=formatadores_ativos, na_rep='—')

    return estilo


def estilizar_resumo_qualidade(df, col_quantidade=None, col_percentual='Perda de Dados (%)', qtd_linhas=None, caption=None):
    """
    Template para DataFrames de diagnóstico de qualidade (nulos, zeros, listas vazias).
    Aplica gradiente vermelho no percentual e laranja na quantidade.

    Parâmetros
    ----------
    df             : DataFrame com resumo de qualidade
    col_quantidade : nome da coluna de quantidade absoluta (autodetectada se None)
    col_percentual : nome da coluna de percentual
    qtd_linhas     : número de linhas a exibir (None = todas)
    caption        : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    if col_quantidade is None:
        candidatas = [c for c in df.columns if c != col_percentual]
        col_quantidade = candidatas[0] if candidatas else None

    df_foco = df.head(qtd_linhas) if qtd_linhas else df
    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    if col_percentual in df.columns:
        estilo = estilo.background_gradient(cmap=GRADIENTES['anomalia'], subset=[col_percentual])

    if col_quantidade and col_quantidade in df.columns:
        estilo = estilo.background_gradient(cmap=GRADIENTES['volume'], subset=[col_quantidade])

    formatadores = {}
    if col_percentual in df.columns:
        formatadores[col_percentual] = '{:.2f}%'
    if col_quantidade and col_quantidade in df.columns:
        formatadores[col_quantidade] = '{:,.0f}'

    return estilo.format(formatadores)


def estilizar_metricas(df, colunas_score=None, colunas_financeiras=None, qtd_linhas=None, caption=None):
    """
    Template para análises de performance: aplica gradientes em scores e colunas financeiras.

    Parâmetros
    ----------
    col
    if qtd_linhas is None:
        qtd_linhas = len(df)unas_score      : colunas de avaliação/popularidade (gradiente viridis)
    colunas_financeiras: colunas de budget/revenue (gradiente Greens)
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    df_foco = df.head(qtd_linhas)
    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    if colunas_score:
        cols_validas = [c for c in colunas_score if c in df_foco.columns]
        if cols_validas:
            estilo = estilo.background_gradient(cmap=GRADIENTES['metrica'], subset=cols_validas)

    if colunas_financeiras:
        cols_validas = [c for c in colunas_financeiras if c in df_foco.columns]
        if cols_validas:
            estilo = estilo.background_gradient(cmap=GRADIENTES['financeiro'], subset=cols_validas)

    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }

    return estilo.map(
        lambda v: 'color: #888888; font-style: italic' if pd.isna(v) else ''
    ).format(formatter=formatadores_ativos, na_rep='—')


def destacar_anomalias(df, mascara, colunas_destaque, colunas_contexto=None, qtd_linhas=None, caption=None):
    """
    Template para inspeção de anomalias: destaca colunas problemáticas em vinho escuro
    e exibe colunas de contexto em tom neutro.

    Parâmetros
    ----------
    mascara           : Series booleana para filtrar linhas anômalas
    colunas_destaque  : colunas que contêm a anomalia (fundo vinho)
    colunas_contexto  : colunas de suporte para leitura (fundo neutro)
    qtd_linhas        : número de linhas a exibir (None = todas)
    caption           : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    colunas_exibir = list(colunas_destaque)
    if colunas_contexto:
        colunas_exibir = list(colunas_contexto) + colunas_exibir

    df_foco = df.loc[mascara, [c for c in colunas_exibir if c in df.columns]]
    if qtd_linhas:
        df_foco = df_foco.head(qtd_linhas)

    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    for col in colunas_destaque:
        if col in df_foco.columns:
            estilo = estilo.set_properties(subset=[col], **CORES['anomalia'])

    return estilo.map(
        lambda v: 'color: #888888; font-style: italic' if pd.isna(v) else ''
    ).format(na_rep='—')


def estilizar_comparativo(df, col_grupo, colunas_metrica, qtd_linhas=None, caption=None):
    """
    Template para tabelas de comparação entre grupos (ex: franquia vs. independente).
    Aplica gradiente divergente nas métricas para facilitar a leitura de diferenças.

    Parâmetros
    ----------
    col_grupo      : coluna categórica de agrupamento (ex: 'is_franchise')
    colunas_metrica: colunas numéricas a comparar
    qtd_linhas     : número de linhas a exibir (None = todas)
    caption        : título opcional da tabela
    """
    if qtd_linhas is None:
        qtd_linhas = len(df)
    df_foco = df.head(qtd_linhas) if qtd_linhas else df
    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)

    if col_grupo in df_foco.columns:
        estilo = estilo.set_properties(subset=[col_grupo], **CORES['booleano'])

    cols_validas = [c for c in colunas_metrica if c in df_foco.columns]
    if cols_validas:
        estilo = estilo.background_gradient(cmap=GRADIENTES['divergente'], subset=cols_validas)

    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }

    return estilo.format(formatter=formatadores_ativos, na_rep='—')