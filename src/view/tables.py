import warnings
import numpy as np
import pandas as pd
from .style_config import (
    CORES, 
    GRADIENTES, 
    MAPA_COLUNAS, 
    ESTILO_CABECALHO, 
    FORMATADORES
)


# =====================================================================
#   VARIAVEIS GLOBAIS 
# =====================================================================

MAX_LINHAS = 100
MAX_CELULAS = 10_000

# =====================================================================
#   FUNÇÕES DE CONFIGURAÇÃO 
# =====================================================================

# Controle de largura máxima e truncamento com '...' no CSS global
def controle_largura_max(df, estilo, quebra_linha=False):
    largura = 2000 // len(df.columns)
    largura = max(largura, 300)
    largura = min(largura, 600)

    white_space = ("normal" if quebra_linha else "nowrap")

    return estilo.set_table_styles([
        { "selector": "table", 
            "props": [
                ("table-layout", "auto"), # 'auto' deixa colunas pequenas serem pequenas
                ("width", "100%"),
                ("border-collapse", "collapse"),
                ("margin", "10px 0")
            ]
        },
        {"selector": "th", 
            "props": [
                ("text-align", "left"),
                ("font-weight", "bold"),
                ("padding", "10px 15px"),
                ("min-width", "100px"),
                ("max-width", f"{largura}px")
            ]
        },
        {"selector": "td",
            "props": [
                ("text-align", "left"),
                ("padding", "8px 15px"),
                ("max-width", f"{largura}px"),
                ("white-space", white_space),
                ("text-overflow", "ellipsis"),
                ("overflow", "hidden")
            ]
        }
    ], overwrite=False)

# Verificando o tamanho e ajusta o dataframe para exibição
def ajustar_tamanho_df (df_base, qtd_linhas):

    # Calculo do tamanho do dataframe
    celulas = qtd_linhas * len(df_base.columns)
    
    # Dicisão de visualização
    if celulas <= MAX_CELULAS and qtd_linhas <= MAX_LINHAS:
        return  df_base.head(qtd_linhas)

    else:
        warnings.warn(
            f"DataFrame muito grande "
            f"({celulas:,} células). "
            f"Mostrando apenas amostra."
        )

        return pd.concat([
            df_base.head(5),
            df_base.tail(5)
        ])

def config_celula_anomala(valor,valores_anomalos):
    # Modo Cirúrgico: Monta a string CSS baseada no dicionário de cores
    css_anomalia = (
        f"background-color: {
            CORES['anomalia']['background-color']
        }; color: {
            CORES['anomalia']['color']
        };"
    )

    #Checa se é nulo (caso 'NaN' ou None tenha sido passado na lista)
    if pd.isna(valor):
        return css_anomalia if (
            None in valores_anomalos 
            or "NaN" 
            in valores_anomalos
        ) else ""
    
    # Checa o valor exato ou a conversão dele em texto (ex: listas '[]')
    if valor in valores_anomalos or str(valor).strip() in valores_anomalos:
        return css_anomalia
        
    return ""

# =====================================================================
#   TEMPLATES DE VISUALIZAÇÃO
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

    # Definindo quantidade de linhas padrão
    if qtd_linhas is None:
        qtd_linhas = min(len(df), MAX_LINHAS)

    # Define dataframe base
    if colunas_selecionadas is not None:
        colunas_validas = [
            c for c in colunas_selecionadas
            if c in df.columns
        ]

        if not colunas_validas:
            raise ValueError(
                "Nenhuma coluna válida foi encontrada."
            )

        df_base = df[colunas_validas]

    else:
        df_base = df

    df_foco = ajustar_tamanho_df(df_base, qtd_linhas)

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

    return controle_largura_max(
        df_foco,
        estilo.map(
            lambda v: 'color: #888888;'
            'font-style: italic; '
            if pd.isna(v) else ''
        ).format(formatadores_ativos)
    )


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
    # Definindo quantidade de linhas padrão
    if qtd_linhas is None:
        qtd_linhas = min(len(df), MAX_LINHAS)

    if col_quantidade is None:
        candidatas = [c for c in df.columns if c != col_percentual]
        col_quantidade = candidatas[0] if candidatas else None

    df_foco = ajustar_tamanho_df(df, qtd_linhas)

    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)


    if caption:
        estilo = estilo.set_caption(caption)

    if col_percentual in df.columns:
        estilo = estilo.background_gradient(cmap=GRADIENTES['anomalia'], subset=[col_percentual])

    if col_quantidade and col_quantidade in df.columns:
        estilo = estilo.background_gradient(cmap=GRADIENTES['volume'], subset=[col_quantidade])

    formatadores_ativos = {}
    if col_percentual in df.columns:
        formatadores_ativos[col_percentual] = '{:.2f}%'
    if col_quantidade and col_quantidade in df.columns:
        formatadores_ativos[col_quantidade] = '{:,.0f}'

    return controle_largura_max(
        df_foco,
        estilo.map(
            lambda v: 'color: #888888;'
            'font-style: italic; '
            if pd.isna(v) else ''
        ).format(formatadores_ativos)
    )


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
    # Definindo quantidade de linhas padrão
    if qtd_linhas is None:
        qtd_linhas = min(len(df), MAX_LINHAS)

    df_foco = ajustar_tamanho_df(df, qtd_linhas)
    
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

    return controle_largura_max(
        df_foco,
        estilo.map(
            lambda v: 'color: #888888;'
            'font-style: italic; '
            if pd.isna(v) else ''
        ).format(formatadores_ativos)
    )


def destacar_anomalias(df, mascara, colunas_destaque, colunas_contexto=None,valores_anomalos=None, qtd_linhas=None, caption=None):
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
    # Definindo quantidade de linhas padrão
    if qtd_linhas is None:
        qtd_linhas = min(len(df), MAX_LINHAS)

    colunas_exibir = list(colunas_destaque)

    if colunas_contexto:
        colunas_exibir = list(colunas_contexto) + colunas_exibir

    df_foco = df.loc[mascara, [c for c in colunas_exibir if c in df.columns]]

    df_foco = ajustar_tamanho_df(df_foco, qtd_linhas)

    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)

    if caption:
        estilo = estilo.set_caption(caption)
    

    if valores_anomalos is None:
        for col in colunas_destaque:
            if col in df_foco.columns:
                estilo = estilo.set_properties(subset=[col], **CORES['anomalia'])
    else:
        cols_validas = [c for c in colunas_destaque if c in df_foco.columns]
        if cols_validas:
            estilo = estilo.map(
                config_celula_anomala, 
                valores_anomalos=valores_anomalos,
                subset=cols_validas
            )

    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }

    return controle_largura_max(
        df_foco,
        estilo.map(
            lambda v: 'color: #888888;'
            'font-style: italic; '
            if pd.isna(v) else ''
        ).format(formatadores_ativos)
    )



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
    # Definindo quantidade de linhas padrão
    if qtd_linhas is None:
        qtd_linhas = min(len(df), MAX_LINHAS)

    df_foco = ajustar_tamanho_df(df,qtd_linhas)

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

    return controle_largura_max(
        df_foco,
        estilo.map(
            lambda v: 'color: #888888;'
            'font-style: italic; '
            if pd.isna(v) else ''
        ).format(formatadores_ativos)
    )

def estilizar_matriz_correlacao(df_corr, caption="Mapa de Relacionamento (Matriz de Correlação)"):
    """
    Template exclusivo para Matrizes de Correlação geradas via df.corr().
    Aplica um mapa divergente estritamente travado entre -1.0 e +1.0, 
    garantindo que o valor 0.0 fique perfeitamente neutro no centro visual.
    """
    qtd_linhas = len(df_corr)

    df_foco = ajustar_tamanho_df(df_corr, qtd_linhas)

    # Aplica o cabeçalho base e bordas da tabela
    estilo = df_foco.style.set_table_styles(ESTILO_CABECALHO)
    
    if caption:
        estilo = estilo.set_caption(caption)
        
    # Travar vmin=-1 e vmax=1 é a regra de ouro para heatmaps de correlação perfeitos
    estilo = estilo.background_gradient(
        cmap=GRADIENTES['correlacao'], 
        vmin=-1.0, 
        vmax=1.0
    )
    
    formatadores_ativos = {
        col: fmt for col, fmt in FORMATADORES.items() if col in df_foco.columns
    }


    return controle_largura_max(
        df_foco,
        estilo.map(
            lambda v: 'color: #888888;'
            'font-style: italic; '
            if pd.isna(v) else ''
        ).format(formatadores_ativos)
    )