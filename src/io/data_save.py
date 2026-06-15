from sqlalchemy import create_engine
from pathlib import Path
import pandas as pd
import numpy as np

def _acao_pkl(df,caminho_base):
    # Guarda em Pickle (O seu "Save State" do Python)
    df.to_pickle(caminho_base.with_suffix('.pkl'))

def _acao_csv(df,caminho_base, index):
    # Guardar em CSV (A sua vitrine para o mundo)
    # Usamos utf-8-sig para garantir que acentos funcionem no Excel
    df.to_csv(caminho_base.with_suffix('.csv'), index=index, encoding='utf-8-sig')

def _acao_parquet(df, caminho_base, index):
    df.to_parquet(caminho_base.with_suffix('.parquet'), index=index)

def _preparar_dataframe_para_sql(df):
    """
    Varre o DataFrame automaticamente, detecta colunas que contêm listas 
    ou arrays e as converte para texto puro (strings separadas por vírgula).
    """
    colunas_modificadas = []
    
    for coluna in df.columns:
        # Pega o primeiro valor que não seja nulo (NaN) para analisar a "cara" do dado
        amostra_valida = df[coluna].dropna()
        
        if not amostra_valida.empty:
            amostra = amostra_valida.iloc[0]
            
            # Se o banco detectar que a amostra é uma lista ou array do numpy...
            if isinstance(amostra, (list, np.ndarray)):
                
                # ...ele converte a coluna inteira. 
                # O map(str, x) garante que não quebre se houver números dentro da lista
                df[coluna] = df[coluna].apply(
                    lambda x: ', '.join(map(str, x)) if isinstance(x, (list, np.ndarray)) else x
                )
                colunas_modificadas.append(coluna)
        
    return df


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
            _acao_pkl(df,caminho_base)
            print(f"Sucesso! Ficheiro guardado em '{caminho_base}.pkl'")
        case 'csv':
            _acao_csv(df,caminho_base, index)
            print(f"Sucesso! Ficheiro guardado em '{caminho_base}.csv'")
        case 'parquet':
            _acao_parquet(df,caminho_base,index)
            print(f"Sucesso! Ficheiro guardado em '{caminho_base}.parquet'")
        case 'all':
            _acao_pkl(df,caminho_base)
            _acao_csv(df,caminho_base, index)
            _acao_parquet(df,caminho_base,index)
            print("Sucesso! Ficheiro guardado em")
            print(f"\n{caminho_base}.pkl")
            print(f"\n{caminho_base}.csv") 
            print(f"\n{caminho_base}.parquet")
        case _:
            print("Tipo de Arquivo Não Especificado!")
    
def save_db(df, caminho_db, nome_db):

    df =_preparar_dataframe_para_sql(df)
    
    # Configurando o motor do banco de dados (SQLite local)
    engine = create_engine(caminho_db)

    # Persistindo o Catálogo Unificado no banco
    df.to_sql(
        name=nome_db,
        con=engine,
        if_exists='replace',
        index=False
    )

    print(f"Banco de dados '{nome_db}' estruturado com sucesso")