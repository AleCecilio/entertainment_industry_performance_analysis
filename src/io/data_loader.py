from pathlib import Path
import pandas as pd


def acao_pkl(file_path):
    return pd.read_pickle(file_path)


def acao_csv(file_path):
    return pd.read_csv(file_path, low_memory=False)

def acao_parquet(file_path):
    return pd.read_parquet(file_path)


def load_data(file_path, tipo_arquivo):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    match tipo_arquivo:

        case 'pkl':
            df = acao_pkl(file_path)

            print(f"Dados PKL carregados! Formato: {df.shape}")

            return df

        case 'csv':
            df = acao_csv(file_path)

            print(f"Dados CSV carregados! Formato: {df.shape}")

            return df
        case 'parquet':
            df = acao_parquet(file_path)

            print(f"Dados Parquet carregados! Formato: {df.shape}")

        case 'all':
            df_pkl = acao_pkl(file_path)
            df_csv = acao_csv(file_path)
            df_parquet = acao_parquet(file_path)

            print(f"PKL carregado! Formato: {df_pkl.shape}")
            print(f"CSV carregado! Formato: {df_csv.shape}")
            print(f"PARQUET carregado! Formato: {df_csv.shape}")

            return df_pkl, df_csv, df_parquet 
        case _:
            raise ValueError("Tipo de arquivo não suportado!")
