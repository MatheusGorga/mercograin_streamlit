# paginas/cadastro_usuarios.py
import streamlit as st
from funcoes_compartilhadas import conversa_banco, trata_tabelas, estilos, controle_acesso

# --- Configurações da Tabela ---
TABELA = "usuarios"
TIPOS_COLUNAS = {
    "ID": "id",
    "Nome": "texto",
    "Email": "texto",
    "Senha": "texto",
}

def app():
    # --- Título e Estado ---
    estilos.set_page_title("Gerenciar Usuários do Sistema")
    trata_tabelas.gerenciar_estado_grid("usuarios")

    # --- Formulário de Criação ---
    with st.expander("➕ Adicionar Novo Usuário"):
        with st.form("form_novo_usuario", clear_on_submit=True):
            st.subheader("Dados do Novo Usuário")
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail de Acesso")
            senha = st.text_input("Senha Inicial", type="password")
            senha_conf = st.text_input("Confirme a Senha", type="password")

            if st.form_submit_button("💾 Salvar Usuário"):
                if not nome or not email or not senha:
                    st.warning("⚠️ Todos os campos são obrigatórios.")
                elif senha != senha_conf:
                    st.error("❌ As senhas não conferem.")
                else:
                    # Criptografa a senha antes de salvar
                    senha_hash = controle_acesso._hash_senha(senha)
                    novo_usuario = {
                        "Nome": nome,
                        "Email": email.lower().strip(),
                        "Senha": senha_hash,
                    }
                    conversa_banco.insert(TABELA, novo_usuario)
                    st.success("✅ Usuário salvo com sucesso!")

    # --- Leitura e Exibição dos Dados ---
    df_usuarios = conversa_banco.select(TABELA, TIPOS_COLUNAS)
    
    # Filtra para não exibir o usuário ADMIN, que é do sistema
    df_display = df_usuarios[df_usuarios["ID"] != "ADMIN"]
    
    st.subheader("Usuários Cadastrados")

    # --- Definição das colunas visíveis e editáveis ---
    # A senha não é exibida por segurança
    visiveis = {
        "Nome": "Nome",
        "Email": "E-mail de Acesso",
    }
    colunas_editaveis = ["Nome", "Email"]

    # --- Renderização do Grid ---
    df_editado, ids_selecionados = trata_tabelas.grid(
        df=df_display,
        col_visiveis=visiveis,
        id_col="ID",
        key_sufixo="usuarios"
    )

    # --- Lógica para Salvar e Deletar ---
    trata_tabelas.salvar_edicoes(
        editado=df_editado,
        original=df_display,
        editaveis=colunas_editaveis,
        tabela=TABELA,
        id_col="ID",
        tipos=TIPOS_COLUNAS,
        key_sufixo="usuarios"
    )

    trata_tabelas.opcoes_especiais(
        tabela=TABELA,
        ids=ids_selecionados,
        id_col="ID",
        fn_insert=None # Clonar usuários não é uma boa prática de segurança
    )