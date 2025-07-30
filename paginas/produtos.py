# paginas/produtos.py
import streamlit as st
from funcoes_compartilhadas import conversa_banco, trata_tabelas, estilos

# --- Configurações da Tabela ---
TABELA = "produtos"
TIPOS_COLUNAS = {
    "ID": "id",
    "Nome": "texto",
    "Descricao": "texto",
    "Anac_Padrao": "texto",
}

def app():
    # --- Título e Estado ---
    estilos.set_page_title("Gerenciar Produtos")
    trata_tabelas.gerenciar_estado_grid("produtos")

    # --- Formulário de Criação ---
    with st.expander("➕ Adicionar Novo Produto"):
        with st.form("form_novo_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            descricao = st.text_input("Descrição")
            anac_padrao = st.text_area("Anac Padrão (Instruções/Especificações)")

            if st.form_submit_button("💾 Salvar Produto"):
                if not nome:
                    st.warning("⚠️ O 'Nome' do produto é obrigatório.")
                else:
                    novo_produto = {
                        "Nome": nome,
                        "Descricao": descricao,
                        "Anac_Padrao": anac_padrao,
                    }
                    conversa_banco.insert(TABELA, novo_produto)
                    st.success("✅ Produto salvo com sucesso!")

    # --- Leitura dos Dados ---
    df_produtos = conversa_banco.select(TABELA, TIPOS_COLUNAS)
    
    st.subheader("Produtos Cadastrados")

    # --- Definição das colunas visíveis e editáveis ---
    visiveis = {
        "Nome": "Nome do Produto",
        "Descricao": "Descrição",
        "Anac_Padrao": st.column_config.TextColumn("Anac Padrão", width="large")
    }
    colunas_editaveis = ["Nome", "Descricao", "Anac_Padrao"]

    # --- Renderização do Grid ---
    df_editado, ids_selecionados = trata_tabelas.grid(
        df=df_produtos,
        col_visiveis=visiveis,
        id_col="ID",
        key_sufixo="produtos"
    )

    # --- Lógica para Salvar e Deletar ---
    trata_tabelas.salvar_edicoes(
        editado=df_editado,
        original=df_produtos,
        editaveis=colunas_editaveis,
        tabela=TABELA,
        id_col="ID",
        tipos=TIPOS_COLUNAS,
        key_sufixo="produtos"
    )

    trata_tabelas.opcoes_especiais(
        tabela=TABELA,
        ids=ids_selecionados,
        id_col="ID",
        fn_insert=conversa_banco.insert
    )