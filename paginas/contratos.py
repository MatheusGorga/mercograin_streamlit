# paginas/contratos.py
import os
import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco, trata_tabelas, estilos, gerador_pdf
from datetime import datetime

# --- Configurações da Tabela Principal ---
TABELA_CONTRATOS = "contratos"
TIPOS_CONTRATOS = {
    "ID": "id", "ID_Comprador": "texto", "ID_Vendedor": "texto", "ID_Produto": "texto",
    "ID_Broker": "texto", "ID_TipoContrato": "texto", "ID_Status": "texto",
    "Quantidade": "numero", "ID_Unidade": "texto", "Preco": "numero100",
    "Data_Contrato": "data", "Safra": "texto", "Periodo_Entrega": "texto",
    "ID_Incoterm": "texto", "Local_Embarque": "texto", "Observacoes": "texto",
    "Caminho_PDF": "texto", "Anac_Contrato": "texto"
}
@st.cache_data(ttl=600)
def carregar_dados_apoio():
    """Carrega dados de tabelas de apoio para os seletores."""
    dados = {
        "compradores": conversa_banco.select("compradores", {"ID": "id", "Nome": "texto", "CNPJ": "texto", "Endereco": "texto"}),
        "vendedores": conversa_banco.select("vendedores", {"ID": "id", "Nome": "texto", "CNPJ": "texto", "Endereco": "texto"}),
        "produtos": conversa_banco.select("produtos", {"ID": "id", "Nome": "texto", "Anac_Padrao": "texto"}),
        "brokers": conversa_banco.select("brokers", {"ID": "id", "Nome": "texto"}),
        "unidades": conversa_banco.select("unidades", {"ID": "id", "Nome": "texto"}),
        "incoterms": conversa_banco.select("incoterms", {"ID": "id", "Nome": "texto"}),
        "tipos_contrato": conversa_banco.select("tipos_contrato", {"ID": "id", "Nome": "texto"}),
        "status_contrato": conversa_banco.select("status_contrato", {"ID": "id", "Nome": "texto"}),
    }
    return dados

def app():
    """Função principal da página de contratos."""
    estilos.set_page_title("Painel de Contratos")
    dados_apoio = carregar_dados_apoio()
    
    # Mapeamentos para os seletores
    map_compradores = pd.Series(dados_apoio["compradores"].ID.values, index=dados_apoio["compradores"].Nome).to_dict()
    map_vendedores = pd.Series(dados_apoio["vendedores"].ID.values, index=dados_apoio["vendedores"].Nome).to_dict()
    map_produtos = pd.Series(dados_apoio["produtos"].ID.values, index=dados_apoio["produtos"].Nome).to_dict()
    map_brokers = pd.Series(dados_apoio["brokers"].ID.values, index=dados_apoio["brokers"].Nome).to_dict()
    map_unidades = pd.Series(dados_apoio["unidades"].ID.values, index=dados_apoio["unidades"].Nome).to_dict()
    map_incoterms = pd.Series(dados_apoio["incoterms"].ID.values, index=dados_apoio["incoterms"].Nome).to_dict()
    map_tipos_contrato = pd.Series(dados_apoio["tipos_contrato"].ID.values, index=dados_apoio["tipos_contrato"].Nome).to_dict()
    map_status = pd.Series(dados_apoio["status_contrato"].ID.values, index=dados_apoio["status_contrato"].Nome).to_dict()

    # Formulário para adicionar novo contrato
    with st.expander("➕ Adicionar Novo Contrato"):
        with st.form("form_novo_contrato", clear_on_submit=True):
            st.subheader("Detalhes da Negociação")
            col1, col2, col3 = st.columns(3)
            with col1:
                data_contrato = st.date_input("Data do Contrato", datetime.now(), key="new_data")
                comprador_nome = st.selectbox("Comprador", list(map_compradores.keys()), key="new_comprador")
                vendedor_nome = st.selectbox("Vendedor", list(map_vendedores.keys()), key="new_vendedor")
                produto_nome = st.selectbox("Produto", ["Selecione..."] + list(map_produtos.keys()), key="new_produto")
            with col2:
                quantidade = st.number_input("Quantidade", min_value=0.0, step=1.0, format="%.2f", key="new_qtd")
                unidade_nome = st.selectbox("Unidade", list(map_unidades.keys()), key="new_unidade")
                preco = st.number_input("Preço", min_value=0.0, step=0.01, format="%.2f", key="new_preco")
                safra = st.text_input("Safra (Ex: 24/25)", key="new_safra")
            with col3:
                periodo_entrega = st.text_input("Período de Entrega", key="new_entrega")
                incoterm_nome = st.selectbox("Incoterm", list(map_incoterms.keys()), key="new_incoterm")
                local_embarque = st.text_input("Local de Embarque", key="new_local")
                broker_nome = st.selectbox("Broker (Opcional)", ["Nenhum"] + list(map_brokers.keys()), key="new_broker")
            
            st.markdown("---")
            st.subheader("Anac e Observações")
            anac_default = ""
            if produto_nome != "Selecione...":
                anac_default = dados_apoio["produtos"][dados_apoio["produtos"]["Nome"] == produto_nome]["Anac_Padrao"].iloc[0]
            anac_contrato = st.text_area("Anac do Contrato", value=anac_default, height=150, key="new_anac")
            observacoes = st.text_area("Observações Gerais", key="new_obs")
            
            if st.form_submit_button("💾 Salvar Contrato"):
                if produto_nome == "Selecione...": 
                    st.warning("⚠️ Selecione um produto para continuar.")
                else:
                    novo_contrato = { "ID_Comprador": map_compradores[comprador_nome], "ID_Vendedor": map_vendedores[vendedor_nome], "ID_Produto": map_produtos[produto_nome], "ID_Broker": map_brokers.get(broker_nome) if broker_nome != "Nenhum" else None, "ID_TipoContrato": map_tipos_contrato.get("Venda"), "ID_Status": map_status.get("Em negociação"), "Quantidade": quantidade, "ID_Unidade": map_unidades[unidade_nome], "Preco": preco, "Data_Contrato": data_contrato.strftime("%Y-%m-%d"), "Safra": safra, "Periodo_Entrega": periodo_entrega, "ID_Incoterm": map_incoterms[incoterm_nome], "Local_Embarque": local_embarque, "Observacoes": observacoes, "Anac_Contrato": anac_contrato }
                    conversa_banco.insert(TABELA_CONTRATOS, novo_contrato)
                    st.success("✅ Contrato salvo com sucesso!")
                    st.rerun()

    # Exibição e gerenciamento dos contratos existentes
    st.subheader("Contratos Lançados")
    df_contratos = conversa_banco.select(TABELA_CONTRATOS, TIPOS_CONTRATOS)

    if not df_contratos.empty:
        df_display = df_contratos.copy()
        for col, map_data in [("Comprador", dados_apoio["compradores"]), ("Vendedor", dados_apoio["vendedores"]), ("Produto", dados_apoio["produtos"]), ("Status", dados_apoio["status_contrato"])]:
            map_series = pd.Series(map_data.Nome.values, index=map_data.ID.astype(str))
            df_display[col] = df_display[f"ID_{col}"].astype(str).map(map_series)
        
        colunas_para_mostrar = { "Data_Contrato": "Data", "Comprador": "Comprador", "Vendedor": "Vendedor", "Produto": "Produto", "Quantidade": "Qtd", "Preco": "Preço", "Status": "Status", "ID": "ID"}
        df_display_final = df_display[list(colunas_para_mostrar.keys())].rename(columns=colunas_para_mostrar)
        df_display_final.insert(0, "Selecionar", False)
        
        df_editado = st.data_editor(
            df_display_final, 
            column_config={"ID": None, "Selecionar": st.column_config.CheckboxColumn(required=True)}, 
            disabled=df_display_final.columns.drop("Selecionar"), 
            hide_index=True, 
            use_container_width=True, 
            key="grid_contratos"
        )
        ids_selecionados = df_editado[df_editado["Selecionar"]]["ID"].tolist()

        if ids_selecionados:
            with st.container(border=True):
                st.write(f"**{len(ids_selecionados)} contrato(s) selecionado(s)**")
                col_edit, col_delete, col_pdf = st.columns([2, 2, 3])

                if col_delete.button("🗑️ Deletar Contratos Selecionados", use_container_width=True):
                    sucesso = 0
                    for id_contrato in ids_selecionados:
                        if conversa_banco.delete(TABELA_CONTRATOS, id_contrato): 
                            sucesso += 1
                    st.success(f"🗑️ {sucesso} contrato(s) deletado(s).")
                    st.rerun()

                if len(ids_selecionados) == 1:
                    id_para_acao = ids_selecionados[0]
                    contrato_selecionado = df_contratos[df_contratos["ID"] == id_para_acao].iloc[0]

                    if col_edit.button("📝 Editar Contrato Selecionado", use_container_width=True):
                        st.session_state['editando_contrato_id'] = id_para_acao
                    
                    try:
                        # Prepara os dados para o template
                        dados_para_template = {
                            'NOME_COMPRADOR': df_display.loc[df_display['ID'] == id_para_acao, 'Comprador'].iloc[0],
                            'CNPJ_COMPRADOR': dados_apoio['compradores'].loc[dados_apoio['compradores']['ID'] == contrato_selecionado['ID_Comprador'], 'CNPJ'].iloc[0],
                            'ENDERECO_COMPRADOR': dados_apoio['compradores'].loc[dados_apoio['compradores']['ID'] == contrato_selecionado['ID_Comprador'], 'Endereco'].iloc[0],
                            'NOME_VENDEDOR': df_display.loc[df_display['ID'] == id_para_acao, 'Vendedor'].iloc[0],
                            'CNPJ_VENDEDOR': dados_apoio['vendedores'].loc[dados_apoio['vendedores']['ID'] == contrato_selecionado['ID_Vendedor'], 'CNPJ'].iloc[0],
                            'ENDERECO_VENDEDOR': dados_apoio['vendedores'].loc[dados_apoio['vendedores']['ID'] == contrato_selecionado['ID_Vendedor'], 'Endereco'].iloc[0],
                            'PRODUTO': df_display.loc[df_display['ID'] == id_para_acao, 'Produto'].iloc[0],
                            'QUANTIDADE': f"{contrato_selecionado['Quantidade']:.2f}",
                            'UNIDADE': dados_apoio['unidades'].loc[dados_apoio['unidades']['ID'] == contrato_selecionado['ID_Unidade'], 'Nome'].iloc[0],
                            'PRECO': f"{contrato_selecionado['Preco']:.2f}",
                            'SAFRA': contrato_selecionado['Safra'],
                            'ANAC': contrato_selecionado['Anac_Contrato'],
                            'PERIODO_ENTREGA': contrato_selecionado['Periodo_Entrega'],
                            'DATA_CONTRATO': contrato_selecionado['Data_Contrato'],
                            'CONTRATO_NUMERO': f"MG{contrato_selecionado['ID']}",
                            'IE_VENDEDOR': 'Teste', # Substitua se tiver esse dado no banco
                            'IE_COMPRADOR': '091/0370567', # Substitua se tiver esse dado no banco
                            'DATA_PAGAMENTO': '30.05.2025' # Substitua por um campo dinâmico se necessário
                        }

                        # Constrói o caminho absoluto para o template, independente de onde o script é executado.
                        caminho_script_atual = os.path.abspath(__file__)
                        project_root = os.path.dirname(os.path.dirname(caminho_script_atual))
                        TEMPLATE_DOCX_PATH = os.path.join(project_root, "templates", "contrato.docx")
                        
                        pdf_bytes = gerador_pdf.criar_contrato_pdf(
                        dados_contrato=dados_para_template
                        )
                        # Cria o botão de download
                        col_pdf.download_button(
                            label="📄 Gerar Contrato em PDF",
                            data=pdf_bytes,
                            file_name=f"Contrato_{id_para_acao}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        col_pdf.error(f"Erro ao gerar PDF: {e}")

                # Formulário de edição
                if 'editando_contrato_id' in st.session_state and st.session_state['editando_contrato_id'] == ids_selecionados[0]:
                    st.subheader(f"Editando Contrato ID: {st.session_state['editando_contrato_id']}")
                    contrato_original = df_contratos[df_contratos["ID"] == st.session_state['editando_contrato_id']].iloc[0]
                    
                    with st.form("form_edita_contrato"):
                        obs_edit = st.text_area("Observações Gerais (Edição)", value=contrato_original["Observacoes"])
                        status_edit_nome = st.selectbox("Status do Contrato", list(map_status.keys()), index=list(map_status.values()).index(contrato_original["ID_Status"]))
                        
                        if st.form_submit_button("💾 Salvar Alterações"):
                            dados_atualizados = {"Observacoes": obs_edit, "ID_Status": map_status[status_edit_nome]}
                            if conversa_banco.update(TABELA_CONTRATOS, st.session_state['editando_contrato_id'], dados_atualizados):
                                st.success("✅ Contrato atualizado com sucesso!")
                                del st.session_state['editando_contrato_id']
                                st.rerun()
                            else: 
                                st.error("❌ Falha ao atualizar o contrato.")
    else:
        st.info("Nenhum contrato cadastrado ainda.")
