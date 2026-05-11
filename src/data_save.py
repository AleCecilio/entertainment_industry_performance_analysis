from pathlib import Path
import pandas as pd

def acao_pkl(df,caminho_base):
    # Guarda em Pickle (O seu "Save State" do Python)
    df.to_pickle(caminho_base.with_suffix('.pkl'))

def acao_csv(df,caminho_base, index):
    # Guardar em CSV (A sua vitrine para o mundo)
    # Usamos utf-8-sig para garantir que acentos funcionem no Excel
    df.to_csv(caminho_base.with_suffix('.csv'), index=index, encoding='utf-8-sig')


def save_dataset(df, nome_arquivo, pasta="../data/processed", tipo_arquivo='both', index=False):
    """
    Guarda o DataFrame em dois formatos: 
        .pkl (Binário): Preserva tipos nativos (listas/dicts) para uso no pipeline.
        .csv (Texto): Garante acessibilidade para visualização no GitHub/Excel.
    """
    
    # Transforma a string num Objeto de Caminho Inteligente (Pathlib)
    caminho_pasta = Path(pasta)

    # Cria a pasta se não existir (o parents=True e exist_ok=True substituem o os.makedirs)
    if not caminho_pasta.exists():
        caminho_pasta.mkdir(parents=True, exist_ok=True)
        print(f"Diretório criado: {caminho_pasta.as_posix()}")

    # Monta o caminho base sem a extensão
    caminho_base = caminho_pasta / nome_arquivo

    match tipo_arquivo:
        case 'pkl': 
            acao_pkl(df,caminho_base)
            print(f"Sucesso! Ficheiro guardado em '{caminho_base}.pkl'")
        case 'csv':
            acao_csv(df,caminho_base, index)
            print(f"Sucesso! Ficheiro guardado em '{caminho_base}.csv'")
        case 'both':
            acao_pkl(df,caminho_base)
            acao_csv(df,caminho_base, index)
            print(f"Sucesso! Ficheiro guardado em '{caminho_base}.pkl' e '{caminho_base}.csv' ")
        case _:
            print("Tipo de Arquivo Não Especificado!")
    

        