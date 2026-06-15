from sqlalchemy import create_engine
from pathlib import Path
import pandas as pd


def _acao_pkl(file_path):
    return pd.read_pickle(file_path)


def _acao_csv(file_path):
    return pd.read_csv(file_path, low_memory=False)

def _acao_parquet(file_path):
    return pd.read_parquet(file_path)

def _acao_db_sql(caminho_db, alvo, eh_query = False):
    uri_banco = f"sqlite:///{caminho_db.as_posix()}"

    engine = create_engine(uri_banco)

    query = alvo if eh_query else f"SELECT * FROM {alvo}"

    with engine.connect() as conexao:
        df = pd.read_sql(query, con=conexao)
        
    return df


def load_data(file_path, tipo_arquivo, alvo=None, eh_query=False):
    
    file_path = Path(file_path)

    match tipo_arquivo:

        case 'pkl':
            try:
                df = _acao_pkl(file_path)
                print(f"Dados PKL carregados! Formato: {df.shape}")
                return df
            except Exception as e:
                print(f"Erro ao carregar PKL: {e}")
                return None

        case 'csv':
            try:
                df = _acao_csv(file_path)
                print(f"Dados CSV carregados! Formato: {df.shape}")
                return df
            except Exception as e:
                print(f"Erro ao carregar CSV: {e}")
                return None

        case 'parquet':
            try:
                df = _acao_parquet(file_path)
                print(f"Dados Parquet carregados! Formato: {df.shape}")
                return df
            except Exception as e:
                print(f"Erro ao carregar Parquet: {e}")
                return None

        case 'bd_sql':
            if not alvo:
                raise ValueError("Para carregar do banco SQL, o parâmetro 'alvo' é obrigatório.")
            try:
                df = _acao_db_sql(file_path, alvo, eh_query)
                print(f"Dados do banco SQL carregados! Formato: {df.shape}")
                return df
            except Exception as e:
                print(f"Erro ao carregar Banco de Dados SQL: {e}")
                return None

        case 'all':
            df_pkl, df_csv, df_parquet, df_sql = None, None, None, None
            
            try:
                df_pkl = _acao_pkl(file_path.with_suffix('.pkl'))
                print(f"PKL carregado! Formato: {df_pkl.shape}")
            except Exception as e:
                print(f"Aviso PKL: {e}")
                
            try:
                df_csv = _acao_csv(file_path.with_suffix('.csv'))
                print(f"CSV carregado! Formato: {df_csv.shape}")
            except Exception as e:
                print(f"Aviso CSV: {e}")
                
            try:
                df_parquet = _acao_parquet(file_path.with_suffix('.parquet'))
                print(f"PARQUET carregado! Formato: {df_parquet.shape}")
            except Exception as e:
                print(f"Aviso PARQUET: {e}")
                
            try:
                if alvo:
                    df_sql = _acao_db_sql(file_path.with_suffix('.db'), alvo, eh_query)
                    print(f"SQL carregado! Formato: {df_sql.shape}")
                else:
                    print("Aviso SQL: Parâmetro 'alvo' ausente. Banco ignorado no carregamento 'all'.")
            except Exception as e:
                print(f"Aviso SQL: {e}")

            return df_pkl, df_csv, df_parquet, df_sql 

        case _:
            raise ValueError(f"Tipo de arquivo '{tipo_arquivo}' não suportado!")