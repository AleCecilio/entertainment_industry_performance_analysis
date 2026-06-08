from .tables import (
    estilizar_tabela, 
    estilizar_resumo_qualidade, 
    estilizar_metricas,
    destacar_anomalias, 
    estilizar_comparativo,
    estilizar_matriz_correlacao,
    estilizar_relatorio_categorias
) 
from . import plots

__all__ = [
    # tables
    "estilizar_tabela", 
    "estilizar_resumo_qualidade", 
    "estilizar_metricas",
    "destacar_anomalias", 
    "estilizar_comparativo",
    "estilizar_matriz_correlacao",
    "estilizar_relatorio_categorias",

    # plots
    "plots"
]