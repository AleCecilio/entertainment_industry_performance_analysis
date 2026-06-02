import matplotlib.ticker as ticker

# ===== Formatador de Números Grandes (K, M, B) =====

def _formatar_numero(x, pos=None):
    """Formata números grandes de forma limpa (1K, 1M, 1B) sem cifrão."""
    if x >= 1e9:
        return f'{x*1e-9:.1f}B'
    elif x >= 1e6:
        return f'{x*1e-6:.0f}M'
    elif x >= 1e3:
        return f'{x*1e-3:.0f}K'
    return f'{x:.0f}'


# ===== Formatador de Valores Monetários (K, M, B com cifrão) =====

def _formatar_dinheiro(x, pos=None):
    if x >= 1e9:
        return f'${x*1e-9:.1f}B'
    elif x >= 1e6:
        return f'${x*1e-6:.0f}M'
    elif x >= 1e3:
        return f'${x*1e-3:.0f}K'
    return f'${x:.0f}'


# ===== Ticks Logarítmicos para Quantidade de Votos / Engajamento =====

def _get_vote_count_ticks():
    """
    Marcadores logarítmicos para o engajamento do público (quantidade de votos).
    Ideal para ver a diferença entre filmes amadores e blockbusters históricos.
    """
    return [
        1,
        10,
        100,
        1_000,
        10_000,
        50_000,
        100_000
    ]


# ===== Ticks e Rótulos Semânticos para Escalas de Nota =====

def _get_nota_ticks_and_labels(escala=10):
    """
    Gera marcadores dinâmicos para notas.
    Se escala=5 (Livros/Goodreads). Se escala=10 (Filmes/Animes).
    """
    match escala:
        case 5:
            dicionario_notas = {
                0.0: "0 (S/ Nota)", 1.0: "1 (Péssimo)", 2.0: "2 (Ruim)",
                3.0: "3 (Regular)", 4.0: "4 (Muito Bom)", 5.0: "5 (Obra-Prima)"
            }
        case 10:
            dicionario_notas = {
                0.0: "0 (S/ Nota)", 1.0: "1 (Desastre)", 2.0: "2 (Péssimo)",
                3.0: "3 (Ruim)", 4.0: "4 (Fraco)", 5.0: "5 (Regular)",
                6.0: "6 (Ok)", 7.0: "7 (Bom)", 8.0: "8 (Ótimo)",
                9.0: "9 (Excelente)", 10.0: "10 (Obra-Prima)"
            }
        case 100:
            dicionario_notas = {
                0.0: "0 (S/ Nota)", 10.0: "10 (Desastre)", 20.0: "20 (Péssimo)",
                30.0: "30 (Ruim)", 40.0: "40 (Fraco)", 50.0: "50 (Regular)",
                60.0: "60 (Ok)", 70.0: "70 (Bom)", 80.0: "80 (Ótimo)",
                90.0: "90 (Excelente)", 100.0: "100 (Obra-Prima)"
            }
        case _:
            raise ValueError("Escala inválida.")

    posicoes = list(dicionario_notas.keys())
    rotulos = list(dicionario_notas.values())
    return posicoes, rotulos


# ===== Ticks Financeiros para Escalas da Indústria do Entretenimento =====

def _get_entertainment_ticks():
    """
    Retorna os marcadores financeiros (ticks) estratégicos para cobrir as
    escalas de Literatura, Anime e Cinema em gráficos logarítmicos.
    """
    return [
        10_000,
        100_000,
        1_000_000,
        10_000_000,
        50_000_000,
        100_000_000,
        500_000_000,
        1_000_000_000,
        2_000_000_000
    ]

# ==============================================================================
# FUNÇÃO AUXILIAR: FORMATAÇÃO DO EIXO X (Distribuição Numérica)
# ==============================================================================

def _formatar_eixo_numerico(
        ax, 
        s_plot, 
        usar_log, 
        tipo_dado, 
        valores_eixo=None,
        eixo='x'
):
    """Aplica as regras de formatação (dinheiro, notas, votos) no eixo especificado (X ou Y)."""
    
    # 1. Define dinamicamente o objeto do eixo e a escala logarítmica
    axis_obj = ax.yaxis if eixo == 'y' else ax.xaxis
    
    if usar_log:
        ax.set_yscale('log') if eixo == 'y' else ax.set_xscale('log')
        axis_obj.set_minor_locator(ticker.NullLocator())

    # 2. Formatação manual via valores fornecidos
    if valores_eixo is not None:
        axis_obj.set_major_locator(ticker.FixedLocator(valores_eixo))
        labels = (
            [_formatar_dinheiro(x) for x in valores_eixo]
            if tipo_dado == 'moeda'
            else [str(x) for x in valores_eixo]
        )
        axis_obj.set_major_formatter(ticker.FixedFormatter(labels))
        ax.tick_params(axis=eixo, rotation=45)
        return

    # 3. Formatação automática baseada no tipo de dado
    match tipo_dado:
        case 'popularidade' if usar_log:
            ticks = [0.1, 1, 5, 10, 50, 100, 500, 1000]
            ticks = [t for t in ticks if t <= s_plot.max() * 1.5]
            axis_obj.set_major_locator(ticker.FixedLocator(ticks))
            axis_obj.set_major_formatter(ticker.FixedFormatter([str(t) for t in ticks]))
            ax.tick_params(axis=eixo, rotation=0)

        case 'popularidade':
            formatter = ticker.FuncFormatter(lambda x, pos: f"{x:,.1f}" if x < 10 else f"{int(x)}")
            axis_obj.set_major_formatter(formatter)
            ax.tick_params(axis=eixo, rotation=0)

        case 'nota_100':
            posicoes, rotulos = _get_nota_ticks_and_labels(escala=100)
            axis_obj.set_major_locator(ticker.FixedLocator(posicoes))
            axis_obj.set_major_formatter(ticker.FixedFormatter(rotulos))
            ax.tick_params(axis=eixo, rotation=45)

        case 'nota_10':
            posicoes, rotulos = _get_nota_ticks_and_labels(escala=10)
            axis_obj.set_major_locator(ticker.FixedLocator(posicoes))
            axis_obj.set_major_formatter(ticker.FixedFormatter(rotulos))
            ax.tick_params(axis=eixo, rotation=45)

        case 'nota_5':
            posicoes, rotulos = _get_nota_ticks_and_labels(escala=5)
            axis_obj.set_major_locator(ticker.FixedLocator(posicoes))
            axis_obj.set_major_formatter(ticker.FixedFormatter(rotulos))
            ax.tick_params(axis=eixo, rotation=45)

        case 'contagem' if usar_log:
            ticks = _get_vote_count_ticks()
            labels = [f"{t//1000}K" if t >= 1000 else str(t) for t in ticks]
            axis_obj.set_major_locator(ticker.FixedLocator(ticks))
            axis_obj.set_major_formatter(ticker.FixedFormatter(labels))
            ax.tick_params(axis=eixo, rotation=45)

        case 'contagem':
            from ._formatters import _formatar_numero
            axis_obj.set_major_formatter(ticker.FuncFormatter(_formatar_numero))
            ax.tick_params(axis=eixo, rotation=45)

        case 'moeda' if usar_log:
            ticks = _get_entertainment_ticks()
            labels = [_formatar_dinheiro(x) for x in ticks]
            axis_obj.set_major_locator(ticker.FixedLocator(ticks))
            axis_obj.set_major_formatter(ticker.FixedFormatter(labels))
            ax.tick_params(axis=eixo, rotation=45)

        case 'moeda':
            axis_obj.set_major_formatter(ticker.FuncFormatter(_formatar_dinheiro))
            ax.tick_params(axis=eixo, rotation=45)

        case _:
            pass