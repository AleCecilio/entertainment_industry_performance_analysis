# src/data_loader.py
import pandas as pd
import sqlite3
import os

def load_data_csv(file_path):
    """
    Carrega o dataset bruto e garante que os tipos básicos estão corretos.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
    df = pd.read_csv(file_path, low_memory=False)
    print(f"Dados carregados com sucesso! Formato: {df.shape}")
    return df

def load_data_pkl(file_path):
    """
    Carrega o dataset bruto e garante que os tipos básico estão corretos 
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
    df = pd.read_pickle(file_path)
    print(f"Dados carregados com sucesso! Formato: {df.shape}")
    return df
