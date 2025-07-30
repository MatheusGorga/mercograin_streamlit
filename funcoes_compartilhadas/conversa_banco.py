# funcoes_compartilhadas/conversa_banco.py
# -*- coding: utf-8 -*-

"""
Camada de acesso genérica Google Sheets <-> Pandas.
Utiliza st.secrets para autenticação e st.cache_data para performance.
Versão revisada com CRUD otimizado.
"""

import pandas as pd
import gspread
import streamlit as st
import time
from functools import wraps
from gspread.exceptions import APIError
from .cria_id import cria_id

# ===================================================
# 🔐 CONFIGURAÇÃO E CONEXÃO
# ===================================================
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/10UJfdTMHZivl6J6Dd7TLu925gYX2hkPLXPTDzuXh62E/edit"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource(ttl=3600)
def _get_connection():
    creds = st.secrets["gdrive"]
    return gspread.service_account_from_dict(creds, scopes=SCOPES)

@st.cache_resource(ttl=3600)
def _get_spreadsheet():
    gc = _get_connection()
    return gc.open_by_url(URL_PLANILHA)

# ===================================================
# ❗ DECORADOR PARA TRATAMENTO DE ERROS DE API
# ===================================================
def retry_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tentativas = 5
        for i in range(tentativas):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                if "Quota exceeded" in str(e) and i < tentativas - 1:
                    time.sleep(5)
                else:
                    st.error(f"❌ Erro na API do Google: {e}")
                    raise e
        st.error("❌ Falha de comunicação com a API do Google após múltiplas tentativas.")
        return None
    return wrapper

# ===================================================
# 🔢 AJUSTE DE ESCALA NUMÉRICA (para dinheiro)
# ===================================================
def _scale(df: pd.DataFrame, tipos: dict, modo: str) -> pd.DataFrame:
    df = df.copy()
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        if tipo == "numero100":
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df[col] = df[col] / 100 if modo == "mostrar" else df[col] * 100
    return df

# ===================================================
# 🟩 SELECT (com cache de dados)
# ===================================================
@retry_api_error
@st.cache_data(ttl=600)
def select(tabela: str, tipos_colunas: dict) -> pd.DataFrame:
    sheet = _get_spreadsheet()
    ws = sheet.worksheet(tabela)
    records = ws.get_all_records(value_render_option="UNFORMATTED_VALUE")
    df = pd.DataFrame(records).rename(columns=str.strip)
    
    if df.empty:
        df = pd.DataFrame(columns=list(tipos_colunas.keys()))

    return _scale(df, tipos_colunas, "mostrar")

# ===================================================
# 🟦 INSERT (CORRIGIDO)
# ===================================================
@retry_api_error
def insert(tabela: str, dados):
    sheet = _get_spreadsheet()
    ws = sheet.worksheet(tabela)

    if isinstance(dados, dict):
        dados = [dados]
    
    # Adiciona ID automático para cada novo registro que não o tenha
    for item in dados:
        if "ID" not in item or pd.isna(item.get("ID")) or item.get("ID") == "":
            item["ID"] = cria_id()
    
    df_novos = pd.DataFrame(dados)
    
    header = ws.row_values(1)
    if not header:
        header = list(df_novos.columns)
        ws.append_row(header)

    # Garante que todas as colunas do header existam no DataFrame, preenchendo com "" se necessário
    for col in header:
        if col not in df_novos.columns:
            df_novos[col] = ""

    linhas_para_inserir = df_novos[header].astype(str).values.tolist()
    
    ws.append_rows(linhas_para_inserir)
    st.cache_data.clear()

# ===================================================
# 🟨 UPDATE (OTIMIZADO)
# ===================================================
@retry_api_error
def update(tabela: str, id_registro, novos_dados: dict) -> bool:
    sheet = _get_spreadsheet()
    ws = sheet.worksheet(tabela)
    
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    
    if df.empty or 'ID' not in df.columns:
        return False

    idx_list = df.index[df['ID'].astype(str) == str(id_registro)].tolist()
    if not idx_list:
        st.error(f"Registro com ID {id_registro} não encontrado para atualização.")
        return False
    
    row_to_update = idx_list[0] + 2
    header = ws.row_values(1)

    for campo, valor in novos_dados.items():
        if campo in header:
            col_to_update = header.index(campo) + 1
            ws.update_cell(row_to_update, col_to_update, str(valor))
    
    st.cache_data.clear()
    return True

# ===================================================
# 🟥 DELETE (OTIMIZADO)
# ===================================================
@retry_api_error
def delete(tabela: str, id_registro) -> bool:
    sheet = _get_spreadsheet()
    ws = sheet.worksheet(tabela)
    
    records = ws.get_all_records()
    df = pd.DataFrame(records)

    if df.empty or 'ID' not in df.columns:
        return False

    idx_list = df.index[df['ID'].astype(str) == str(id_registro)].tolist()
    if not idx_list:
        st.error(f"Registro com ID {id_registro} não encontrado para deleção.")
        return False

    row_to_delete = idx_list[0] + 2
    ws.delete_rows(row_to_delete)
    st.cache_data.clear()
    return True