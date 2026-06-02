import seaborn as sns
import matplotlib.pyplot as plt

from ._config import _set_config_graf


# ===== Barplot Horizontal de Auditoria de Dados Faltantes =====

def grafico_percentual_missing_data(df_plot, tamanho_figura=None, polegadas=None, width=None):
    """
    Gera um barplot horizontal focado em auditoria visual (QA).
    Mapeia a intensidade da cor pela gravidade da perda de dados.
    """
    tamanho_figura, polegadas, width = _set_config_graf(tamanho_figura, polegadas, width)

    plt.figure(figsize=tamanho_figura, dpi=polegadas)

    plt.gca().set_axisbelow(True)
    plt.grid(axis='x', linestyle='--', alpha=0.4, color='#9A8C98')

    ax = sns.barplot(
        x='Perda de Dados (%)',
        y=df_plot.index,
        data=df_plot,
        hue=df_plot.index,
        palette='Reds_r',
        legend=False,
        width=width
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            padding=5,
            fontsize=10,
            fontweight='semibold',
            color='#2B2D42',
            fmt='%.2f%%'
        )

    plt.title('Auditoria de Perda de Dados por Coluna', fontsize=15, fontweight='bold', color='#2B2D42', pad=20)
    plt.xlabel('Perda de Dados (%)', fontsize=11, fontweight='semibold', color='#4A4E69')
    plt.ylabel('Atributo', fontsize=11, fontweight='semibold', color='#4A4E69')
    plt.xlim(0, df_plot['Perda de Dados (%)'].max() * 1.15)

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.show()