# funcoes_compartilhadas/controle_acesso.py
import streamlit as st
import hashlib
from . import conversa_banco

# --- Constantes ---
TABELA_USUARIOS = "usuarios"
TIPOS_USUARIOS = {"ID": "id", "Nome": "texto", "Email": "texto", "Senha": "texto"}

# --- Funções de Sessão ---
def usuario_logado():
    return st.session_state.get("usuario_logado")

def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

# --- Interface de Login ---
def login():
    st.header("✍️ Merco Contratos")
    st.markdown("---")
    
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", use_container_width=True):
        if not email or not senha:
            st.error("Preencha todos os campos.")
            return

        df_usuarios = conversa_banco.select(TABELA_USUARIOS, TIPOS_USUARIOS)
        usuario = df_usuarios[df_usuarios["Email"].str.lower() == email.lower()]

        if not usuario.empty:
            senha_hash_armazenada = usuario.iloc[0]["Senha"]
            senha_hash_digitada = _hash_senha(senha)

            if senha_hash_armazenada == senha_hash_digitada:
                st.session_state["usuario_logado"] = usuario.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Senha incorreta.")
        else:
            st.error("Usuário não encontrado.")

# --- Interface de Logout ---
def logout():
    st.sidebar.markdown("---")
    usuario_info = st.session_state.get("usuario_logado")
    if usuario_info:
        st.sidebar.write(f"Usuário: **{usuario_info['Nome']}**")
    
    if st.sidebar.button("Sair do Sistema"):
        st.session_state.pop("usuario_logado", None)
        st.rerun()

# --- Lógica de Permissões ---
def menus_liberados():
    if not usuario_logado():
        return []

    usuario_id = str(st.session_state["usuario_logado"]["ID"])
    if usuario_id == "ADMIN": # Super usuário
        return None

    df_permissoes = conversa_banco.select("permissoes", {"ID": "id", "ID_Usuario": "texto", "ID_Funcionalidade": "texto"})
    
    if df_permissoes.empty:
        return []

    permissoes_usuario = df_permissoes[df_permissoes["ID_Usuario"] == usuario_id]
    return permissoes_usuario.to_dict(orient="records")