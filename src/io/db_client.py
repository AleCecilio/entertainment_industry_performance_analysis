from sqlalchemy import create_engine, text
from pathlib import Path
import pandas as pd
import numpy as np

def _preparar_dataframe_para_sql(df):
    """
    Varre o DataFrame automaticamente, detecta colunas que contêm listas 
    ou arrays e as converte para texto puro (strings separadas por vírgula).
    """
    df_copy = df.copy()
    colunas_modificadas = []

    for coluna in df_copy.columns:
        amostra_valida = df_copy[coluna].dropna()
        if not amostra_valida.empty:
            amostra = amostra_valida.iloc[0]
            if isinstance(amostra, (list, np.ndarray)):
                df_copy[coluna] = df_copy[coluna].apply(
                    lambda x: ', '.join(map(str, x)) if isinstance(x, (list, np.ndarray)) else x
                )
                colunas_modificadas.append(coluna)
                
    if colunas_modificadas:
        print(f"\nColunas achatadas para string: {colunas_modificadas}")

    return df_copy

def save_db(df, pasta, nome_banco, nome_tabela):
    """
    Formata o caminho, limpa estruturas complexas e persiste o DataFrame no banco SQL.
    Protegido por blocos try-except para máxima robustez.
    """
    engine = None
    try:
        # Garante que o caminho seja um objeto Path e monta o destino final .db
        caminho_completo = Path(pasta) / f"{nome_banco}.db"
        
        # Converte para o formato de string exigido pela URI do SQLAlchemy
        uri_banco = f"sqlite:///{caminho_completo.as_posix()}"
        engine = create_engine(uri_banco)
        
        # Limpa listas/arrays dinamicamente antes da inserção
        df_limpo = _preparar_dataframe_para_sql(df)
        
        # Grava no banco de dados
        df_limpo.to_sql(
            name=nome_tabela,
            con=engine,
            if_exists='replace',
            index=False
        )
        print(f"\nSucesso! Tabela '{nome_tabela}' criada no banco: '{caminho_completo.name}'")
        
    except Exception as e:
        print(f"\nErro crítico ao salvar no banco de dados SQL.\nDetalhes: {e}")
    
    finally:
        if engine is not None:
            engine.dispose()

    

def execute_query(caminho_db, alvo, eh_query=True):
    """
    Conecta ao banco e executa instruções SQL analíticas ou extrai tabelas inteiras.
    """
    engine = None

    try:
        caminho_completo = Path(caminho_db)
        uri_banco = f"sqlite:///{caminho_completo.as_posix()}"
        engine = create_engine(uri_banco)
        
        query = alvo if eh_query else f"SELECT * FROM {alvo}"
        
        with engine.connect() as conexao:
            df = pd.read_sql(query, con=conexao)
            
        print(f"\nDados carregados via SQL! Formato: {df.shape}")
        return df
        
    except Exception as e:
        print(f"\nErro crítico ao ler dados do banco SQL.\nDetalhes: {e}")
        return None
    
    finally:
        if engine is not None:
            engine.dispose()
    
def delete_table(caminho_db, nome_tabela):
    """
    Remove uma tabela específica do banco de dados SQLite.
    """
    engine = None

    try:
        caminho_completo = Path(caminho_db)
        uri_banco = f"sqlite:///{caminho_completo.as_posix()}"
        engine = create_engine(uri_banco)
        
        with engine.connect() as conexao:
            conexao.execute(
                text(f"DROP TABLE IF EXISTS {nome_tabela}")
            )
            conexao.commit()
        
        print(f"\nTabela '{nome_tabela}' removida com sucesso!")

    except Exception as e:
        print(f"\nErro ao remover a tabela.\nDetalhes: {e}")
    
    finally:
        if engine is not None:
            engine.dispose()

def delete_rows(caminho_db, nome_tabela, condicao):
    """
    Remove registros de uma tabela de acordo com uma condição SQL.
    """
    engine = None

    try:
        caminho_completo = Path(caminho_db)
        uri_banco = f"sqlite:///{caminho_completo.as_posix()}"
        engine = create_engine(uri_banco)
        
        query = f"""
            DELETE FROM {nome_tabela}
            WHERE {condicao}
        """

        with engine.connect() as conexao:
            resultado = conexao.execute(text(query))
            conexao.commit()
        
        print(
            f"\n{resultado.rowcount} registro(s) removido(s) da tabela '{nome_tabela}'."
        )

    except Exception as e:
        print(f"\nErro ao remover registros.\nDetalhes: {e}")
    
    finally:
        if engine is not None:
            engine.dispose()

def delete_database(caminho_db):
    """
    Exclui completamente um arquivo de banco SQLite.
    """
    try:
        caminho = Path(caminho_db)

        if caminho.exists():
            caminho.unlink()
            print(
                f"\nBanco '{caminho.name}' removido com sucesso!"
            )
        else:
            print(
                f"\nBanco '{caminho.name}' não encontrado."
            )

    except Exception as e:
        print(f"\nErro ao remover o banco.\nDetalhes: {e}")