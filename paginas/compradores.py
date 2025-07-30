# paginas/compradores.py
import streamlit as st
from funcoes_compartilhadas import conversa_banco, trata_tabelas, estilos

# --- Configurações da Tabela ---
TABELA = "compradores"
TIPOS_COLUNAS = {
    "ID": "id",
    "Nome": "texto",
    "CNPJ": "texto",
    "Endereco": "texto",
    "Contato": "texto",
}

def app():
    # --- Título e Estado ---
    estilos.set_page_title("Gerenciar Compradores")
    trata_tabelas.gerenciar_estado_grid("compradores")

    # --- Formulário de Criação ---
    with st.expander("➕ Adicionar Novo Comprador"):
        with st.form("form_novo_comprador", clear_on_submit=True):
            nome = st.text_input("Nome do Comprador (Razão Social)")
            cnpj = st.text_input("CNPJ / CPF")
            endereco = st.text_input("Endereço Completo")
            contato = st.text_input("Contato (Nome, E-mail ou Telefone)")

            if st.form_submit_button("💾 Salvar Comprador"):
                if not nome or not cnpj:
                    st.warning("⚠️ 'Nome' e 'CNPJ' são campos obrigatórios.")
                else:
                    novo_comprador = {
                        "Nome": nome,
                        "CNPJ": cnpj,
                        "Endereco": endereco,
                        "Contato": contato,
                    }
                    conversa_banco.insert(TABELA, novo_comprador)
                    st.success("✅ Comprador salvo com sucesso!")

    # --- Leitura dos Dados ---
    df_compradores = conversa_banco.select(TABELA, TIPOS_COLUNAS)
    
    st.subheader("Compradores Cadastrados")

    # --- Definição das colunas visíveis e editáveis ---
    visiveis = {
        "Nome": "Nome",
        "CNPJ": "CNPJ / CPF",
        "Endereco": "Endereço",
        "Contato": "Contato"
    }
    colunas_editaveis = ["Nome", "CNPJ", "Endereco", "Contato"]

    # --- Renderização do Grid ---
    df_editado, ids_selecionados = trata_tabelas.grid(
        df=df_compradores,
        col_visiveis=visiveis,
        id_col="ID",
        key_sufixo="compradores"
    )

    # --- Lógica para Salvar e Deletar ---
    trata_tabelas.salvar_edicoes(
        editado=df_editado,
        original=df_compradores,
        editaveis=colunas_editaveis,
        tabela=TABELA,
        id_col="ID",
        tipos=TIPOS_COLUNAS,
        key_sufixo="compradores"
    )

    trata_tabelas.opcoes_especiais(
        tabela=TABELA,
        ids=ids_selecionados,
        id_col="ID",
        fn_insert=conversa_banco.insert
    )