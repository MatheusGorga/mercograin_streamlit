# paginas/brokers.py
import streamlit as st
from funcoes_compartilhadas import conversa_banco, trata_tabelas, estilos

# --- Configurações da Tabela ---
TABELA = "brokers"
TIPOS_COLUNAS = {
    "ID": "id",
    "Nome": "texto",
    "Comissao_Pct": "numero100",
    "Contato": "texto",
}

def app():
    # --- Título e Estado ---
    estilos.set_page_title("Gerenciar Brokers (Corretores)")
    trata_tabelas.gerenciar_estado_grid("brokers")

    # --- Formulário de Criação ---
    with st.expander("➕ Adicionar Novo Broker"):
        with st.form("form_novo_broker", clear_on_submit=True):
            nome = st.text_input("Nome do Broker ou Empresa")
            comissao = st.number_input("Comissão Padrão (%)", min_value=0.0, step=0.1, format="%.2f")
            contato = st.text_input("Contato (Nome, E-mail ou Telefone)")

            if st.form_submit_button("💾 Salvar Broker"):
                if not nome:
                    st.warning("⚠️ O 'Nome' do broker é obrigatório.")
                else:
                    novo_broker = {
                        "Nome": nome,
                        "Comissao_Pct": comissao,
                        "Contato": contato,
                    }
                    conversa_banco.insert(TABELA, novo_broker)
                    st.success("✅ Broker salvo com sucesso!")

    # --- Leitura e Exibição dos Dados ---
    df_brokers = conversa_banco.select(TABELA, TIPOS_COLUNAS)
    
    st.subheader("Brokers Cadastrados")

    # --- Definição das colunas ---
    visiveis = {
        "Nome": "Nome",
        "Comissao_Pct": st.column_config.NumberColumn("Comissão (%)", format="%.2f %%"),
        "Contato": "Contato"
    }
    colunas_editaveis = ["Nome", "Comissao_Pct", "Contato"]

    # --- Renderização do Grid ---
    df_editado, ids_selecionados = trata_tabelas.grid(
        df=df_brokers,
        col_visiveis=visiveis,
        id_col="ID",
        key_sufixo="brokers"
    )

    # --- Lógica para Salvar e Deletar ---
    trata_tabelas.salvar_edicoes(
        editado=df_editado,
        original=df_brokers,
        editaveis=colunas_editaveis,
        tabela=TABELA,
        id_col="ID",
        tipos=TIPOS_COLUNAS,
        key_sufixo="brokers"
    )

    trata_tabelas.opcoes_especiais(
        tabela=TABELA,
        ids=ids_selecionados,
        id_col="ID",
        fn_insert=conversa_banco.insert
    )