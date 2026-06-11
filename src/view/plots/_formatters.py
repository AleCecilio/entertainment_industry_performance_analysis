import matplotlib.ticker as ticker


# ===== Formatadores de Números =====

def _formatar_numero(x, pos=None, *, prefixo=''):
    """Formata números grandes de forma limpa (1K, 1M, 1B), com prefixo opcional (ex: '$')."""
    if x >= 1e9:
        return f'{prefixo}{x * 1e-9:.1f}B'
    if x >= 1e6:
        return f'{prefixo}{x * 1e-6:.0f}M'
    if x >= 1e3:
        return f'{prefixo}{x * 1e-3:.0f}K'
    return f'{prefixo}{x:.0f}'


def _formatar_dinheiro(x, pos=None):
    """Formata valores monetários com cifrão (ex: $1.5B)."""
    return _formatar_numero(x, prefixo='$')

def _formatar_hora(x, pos=None):
    """Formata valores de tempo em horas e minutos (ex: 1:30h, 90min)."""
    if x >= 60:
        horas = int(x) // 60
        minutos = int(x) % 60
        return f'{horas}:{minutos:02d}h'
    return f'{x:.0f}min'


_TICKS_HORA = {
    5:  [30, 60, 90, 120, 180, 240, 300],       
    5j: [30, 60, 120, 180, 240, 300],             
    12: [60, 120, 180, 240, 360, 480, 600, 720],
    24: [60, 120, 240, 360, 480, 720, 1080, 1440],
}


# ===== Ticks Logarítmicos para Contagem / Engajamento =====

_ESCALAS_CONTAGEM = {
    'contagem_bilhao':         2_000_000_000,
    'contagem_centena_milhao':   200_000_000,
    'contagem_dezena_milhao':     20_000_000,
    'contagem_milhao':             2_000_000,
    'contagem_centena_milhar':       200_000,
    'contagem_dezena_milhar':         20_000,
    'contagem_milhar':                 2_000,
    'contagem_centena':                  200,
    'contagem_dezena':                    20,
}


def _get_count_ticks(escala=100_000):
    """
    Marcadores logarítmicos para engajamento do público (quantidade de votos/reviews).
    Filtra ticks acima da escala máxima esperada do dataset.
    """
    candidatos = [
        1, 10, 20, 100, 200,
        1_000, 2_000, 10_000, 20_000, 50_000,
        100_000, 200_000, 500_000,
        1_000_000, 2_000_000, 10_000_000, 20_000_000,
        100_000_000, 200_000_000, 500_000_000,
        1_000_000_000, 2_000_000_000,
    ]
    return [t for t in candidatos if t <= escala]


# ===== Ticks e Rótulos Semânticos para Escalas de Nota =====

_NOTAS = {
    5: {
        0.0: "0 (S/ Nota)", 1.0: "1 (Péssimo)",  2.0: "2 (Ruim)",
        3.0: "3 (Regular)", 4.0: "4 (Muito Bom)", 5.0: "5 (Obra-Prima)",
    },
    10: {
        0.0:  "0 (S/ Nota)",   1.0: "1 (Desastre)", 2.0: "2 (Péssimo)",
        3.0:  "3 (Ruim)",      4.0: "4 (Fraco)",    5.0: "5 (Regular)",
        6.0:  "6 (Ok)",        7.0: "7 (Bom)",      8.0: "8 (Ótimo)",
        9.0:  "9 (Excelente)", 10.0: "10 (Obra-Prima)",
    },
    100: {
        0.0:  "0 (S/ Nota)",    10.0: "10 (Desastre)", 20.0: "20 (Péssimo)",
        30.0: "30 (Ruim)",      40.0: "40 (Fraco)",    50.0: "50 (Regular)",
        60.0: "60 (Ok)",        70.0: "70 (Bom)",      80.0: "80 (Ótimo)",
        90.0: "90 (Excelente)", 100.0: "100 (Obra-Prima)",
    },
}


def _get_nota_ticks_and_labels(escala=10):
    """
    Gera marcadores e rótulos semânticos para escalas de nota.
    Escalas suportadas: 5 (Goodreads), 10 (Filmes/Animes), 100 (Metascore).
    """
    if escala not in _NOTAS:
        raise ValueError(f"Escala inválida: {escala}. Use 5, 10 ou 100.")
    dicionario = _NOTAS[escala]
    return list(dicionario.keys()), list(dicionario.values())


# ===== Ticks Financeiros para a Indústria do Entretenimento =====

def _get_entertainment_ticks(menos_valores=False, ):
    """
    Marcadores financeiros estratégicos para escalas logarítmicas
    cobrindo Literatura e Cinema.
    """
    if menos_valores == False:
        return [
            10_000, 100_000, 1_000_000, 10_000_000, 50_000_000,
            100_000_000, 500_000_000, 1_000_000_000, 2_000_000_000,
        ]
    else:
        return [
            10_000, 100_000, 1_000_000, 10_000_000,
            250_000_000, 2_000_000_000,
        ]


# ===== Helpers de Aplicação de Ticks =====

def _aplicar_ticks_fixos(ax, axis_obj, eixo, ticks, labels, rotation=45):
    """Aplica locator, formatter e rotação em um eixo de uma vez."""
    axis_obj.set_major_locator(ticker.FixedLocator(ticks))
    axis_obj.set_major_formatter(ticker.FixedFormatter(labels))
    ax.tick_params(axis=eixo, rotation=rotation)


def _aplicar_nota(ax, axis_obj, eixo, escala):
    """Aplica ticks semânticos de nota no eixo especificado."""
    posicoes, rotulos = _get_nota_ticks_and_labels(escala=escala)
    _aplicar_ticks_fixos(ax, axis_obj, eixo, posicoes, rotulos)


def _aplicar_contagem_log(ax, axis_obj, eixo, escala):
    """Aplica ticks logarítmicos de contagem (K/M/B) no eixo especificado."""
    ticks = _get_count_ticks(escala=escala)
    labels = [f"{t // 1_000}K" if t >= 1_000 else str(t) for t in ticks]
    _aplicar_ticks_fixos(ax, axis_obj, eixo, ticks, labels)


# ===== Formatação de Eixo Numérico =====

def _formatar_eixo_numerico(
        ax,
        s_plot, 
        usar_log, 
        tipo_dado, 
        valores_eixo=None, 
        eixo='x',
        menos_valores=False
):
    """Aplica as regras de formatação (dinheiro, notas, contagem) no eixo especificado (X ou Y)."""

    axis_obj = ax.yaxis if eixo == 'y' else ax.xaxis

    if usar_log:
        ax.set_yscale('log') if eixo == 'y' else ax.set_xscale('log')
        axis_obj.set_minor_locator(ticker.NullLocator())

    if valores_eixo is not None:
        labels = (
            [_formatar_dinheiro(x) for x in valores_eixo]
            if tipo_dado == 'moeda'
            else [str(x) for x in valores_eixo]
        )
        _aplicar_ticks_fixos(ax, axis_obj, eixo, valores_eixo, labels)
        return

    match tipo_dado:
        case 'popularidade' if usar_log:
            ticks = [
                t for t in [
                    0.1, 1, 5, 10, 50, 100, 500, 1000
                ] if t <= s_plot.max() * 1.5
            ]
            _aplicar_ticks_fixos(
                ax, axis_obj, 
                eixo, ticks, 
                [str(t) for t in ticks], 
                rotation=0
            )

        case 'popularidade':
            axis_obj.set_major_formatter(
                ticker.FuncFormatter(
                    lambda x, pos: f"{x:,.1f}" if x < 10 else f"{int(x)}"
                )
            )
            ax.tick_params(axis=eixo, rotation=0)
        
        case 'hora_5h' if usar_log:
            ticks = [30, 60, 90, 120, 180, 240, 300]
            _aplicar_ticks_fixos(
                ax, axis_obj, eixo, ticks,
                [_formatar_hora(t) for t in ticks],
                rotation=0       
            )

        case 'hora_5h':
            ticks = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
            _aplicar_ticks_fixos(
                ax, axis_obj, eixo, ticks,
                [_formatar_hora(t) for t in ticks],
                rotation=45
            )

        case 'hora_12h':
            ticks = [60, 120, 180, 240, 360, 480, 600, 720]
            _aplicar_ticks_fixos(
                ax, axis_obj, eixo, ticks,
                [_formatar_hora(t) for t in ticks],
            )

        case 'hora_24h':
            ticks = [60, 120, 240, 360, 480, 720, 1080, 1440]
            _aplicar_ticks_fixos(
                ax, axis_obj, eixo, ticks,
                [_formatar_hora(t) for t in ticks],
            )

        case 'nota_100': 
            _aplicar_nota(ax, axis_obj, eixo, 100)

        case 'nota_10':  
            _aplicar_nota(ax, axis_obj, eixo, 10)

        case 'nota_5':   
            _aplicar_nota(ax, axis_obj, eixo, 5)

        case tipo if tipo in _ESCALAS_CONTAGEM and usar_log:
            _aplicar_contagem_log(ax, axis_obj, eixo, _ESCALAS_CONTAGEM[tipo])

        case 'contagem':
            axis_obj.set_major_formatter(ticker.FuncFormatter(_formatar_numero))
            ax.tick_params(axis=eixo, rotation=45)

        case 'moeda' if usar_log:
            ticks = _get_entertainment_ticks(menos_valores)
            _aplicar_ticks_fixos(
                ax, 
                axis_obj, 
                eixo, 
                ticks, 
                [_formatar_dinheiro(x) for x in ticks]
            )
        case 'moeda':
            axis_obj.set_major_formatter(ticker.FuncFormatter(_formatar_dinheiro))
            ax.tick_params(axis=eixo, rotation=45)
          