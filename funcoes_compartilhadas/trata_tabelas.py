# funcoes_compartilhadas/trata_tabelas.py
# -*- coding: utf-8 -*-

"""
Módulo de UI genérico para exibir, filtrar, editar, deletar e clonar dados.
"""

import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco

def gerenciar_estado_grid(page_id: str):
    """Reseta o estado do grid ao mudar de página para evitar conflitos."""
    if st.session_state.get("_pagina_atual") != page_id:
        for key in list(st.session_state.keys()):
            if key.startswith("grid_"):
                del st.session_state[key]
        st.session_state["_pagina_atual"] = page_id

def grid(df: pd.DataFrame, col_visiveis: dict, id_col: str, key_sufixo: str):
    """Renderiza um grid editável com uma coluna de seleção."""
    if df.empty:
        st.info("Nenhum registro para exibir.")
        return df.copy(), []

    df_copy = df.copy()
    df_copy.insert(0, "Selecionar", False)
    
    col_config = {"Selecionar": st.column_config.CheckboxColumn(required=True)}
    for col, config in col_visiveis.items():
        if isinstance(config, str):
            col_config[col] = config
        else:
            col_config[col] = config

    # Usamos o 'on_change' para detectar edições e mostrar o botão de salvar
    if f"grid_editado_{key_sufixo}" not in st.session_state:
        st.session_state[f"grid_editado_{key_sufixo}"] = False

    def on_edit_change():
        st.session_state[f"grid_editado_{key_sufixo}"] = True

    editado = st.data_editor(
        df_copy,
        column_config=col_config,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key=f"grid_{key_sufixo}",
        on_change=on_edit_change
    )

    selecionados = editado[editado["Selecionar"]]
    ids_selecionados = selecionados[id_col].tolist() if not selecionados.empty else []
    
    return editado, ids_selecionados

def salvar_edicoes(editado, original, editaveis: list, tabela: str, id_col: str, tipos: dict, key_sufixo: str):
    """Compara o grid editado com o original e, se houver mudanças, mostra um botão para salvar."""
    if not st.session_state.get(f"grid_editado_{key_sufixo}", False):
        return

    try:
        # Encontra as linhas que foram modificadas
        mudancas = st.session_state[f'grid_{key_sufixo}']['edited_rows']
        ids_para_atualizar = []
        for idx, alteracao in mudancas.items():
            id_real = editado.loc[idx, id_col]
            # Filtra apenas as colunas que são editáveis
            valores_alterados = {k: v for k, v in alteracao.items() if k in editaveis}
            if valores_alterados: # Só adiciona se houve alteração em uma coluna editável
                ids_para_atualizar.append({'id': id_real, 'valores': valores_alterados})

        if not ids_para_atualizar:
            return

        if st.button("💾 Salvar Alterações", type="primary"):
            total_sucesso = 0
            for item in ids_para_atualizar:
                # A função de update será criada no conversa_banco.py
                sucesso = conversa_banco.update(
                    tabela=tabela,
                    id_registro=item['id'],
                    novos_dados=item['valores'],
                )
                if sucesso:
                    total_sucesso += 1
            
            st.success(f"✅ {total_sucesso} registro(s) atualizado(s).")
            st.session_state[f"grid_editado_{key_sufixo}"] = False
            st.cache_data.clear()
            st.rerun()

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar as edições: {e}")


def opcoes_especiais(tabela: str, ids: list, id_col: str, fn_insert):
    """Mostra um container com opções de deleção e clonagem para os itens selecionados."""
    if not ids:
        return

    with st.container(border=True):
        st.write(f"**{len(ids)} registro(s) selecionado(s)**")
        
        col1, col2 = st.columns(2)
        
        # --- Botão Deletar ---
        if col1.button("🗑️ Deletar Selecionados", use_container_width=True):
            sucesso = 0
            for id_registro in ids:
                # A função de delete será criada no conversa_banco.py
                if conversa_banco.delete(tabela, id_registro):
                    sucesso += 1
            st.success(f"🗑️ {sucesso} registro(s) deletado(s).")
            st.cache_data.clear()
            st.rerun()
            
        # --- Botão Clonar ---
        if fn_insert and col2.button("📄 Clonar Selecionados", use_container_width=True):
            df_original = conversa_banco.select(tabela, {}) # Tipos não são essenciais para clonar
            df_para_clonar = df_original[df_original[id_col].isin(ids)]
            
            # Remove o ID antigo para que um novo seja gerado
            df_para_clonar = df_para_clonar.drop(columns=[id_col])
            
            conversa_banco.insert(tabela, df_para_clonar)
            st.success(f"📄 {len(df_para_clonar)} registro(s) clonado(s).")
            st.cache_data.clear()
            st.rerun()