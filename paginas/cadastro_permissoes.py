# paginas/cadastro_permissoes.py
import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco, estilos

# --- Configurações das Tabelas ---
TABELA_PERMISSOES = "permissoes"
TIPOS_PERMISSOES = {
    "ID": "id",
    "ID_Usuario": "texto",
    "ID_Funcionalidade": "texto",
}

# --- Carregamento de Dados (cacheado) ---
@st.cache_data(ttl=300)
def carregar_dados_admin():
    """Carrega todas as tabelas necessárias para a tela de permissões."""
    dados = {
        "usuarios": conversa_banco.select("usuarios", {"ID": "id", "Nome": "texto", "Email": "texto"}),
        "menus": conversa_banco.select("menus", {"ID": "id", "Nome": "texto", "Ordem": "numero"}),
        "funcionalidades": conversa_banco.select("funcionalidades", {"ID": "id", "ID_Menu": "texto", "Nome": "texto"}),
        "permissoes": conversa_banco.select(TABELA_PERMISSOES, TIPOS_PERMISSOES),
    }
    return dados

def app():
    # --- Título e Carregamento de Dados ---
    estilos.set_page_title("🔑 Gerenciar Permissões de Usuário")
    dados_admin = carregar_dados_admin()

    # --- Seleção de Usuário ---
    st.subheader("1. Selecione um Usuário")
    
    # Filtra para não incluir o usuário ADMIN na lista de seleção
    df_usuarios = dados_admin["usuarios"][dados_admin["usuarios"]["ID"] != "ADMIN"]
    
    if df_usuarios.empty:
        st.info("Nenhum usuário cadastrado para definir permissões. Por favor, cadastre um usuário primeiro.")
        st.stop()

    # Cria um dicionário para o selectbox no formato {Nome (Email): ID}
    map_usuarios = {f'{row["Nome"]} ({row["Email"]})': row["ID"] for _, row in df_usuarios.iterrows()}
    
    usuario_selecionado_label = st.selectbox("Usuário:", list(map_usuarios.keys()))
    usuario_id_selecionado = map_usuarios[usuario_selecionado_label]

    st.markdown("---")

    # --- Interface de Definição de Permissões ---
    st.subheader("2. Defina as Funcionalidades Acessíveis")

    # Filtra as permissões atuais do usuário selecionado
    permissoes_atuais = dados_admin["permissoes"][dados_admin["permissoes"]["ID_Usuario"] == usuario_id_selecionado]
    ids_func_permitidas = permissoes_atuais["ID_Funcionalidade"].astype(str).tolist()

    # Dicionário para guardar o estado de todos os checkboxes
    novas_permissoes_selecao = {}

    # Itera sobre os menus ordenados para criar os grupos de checkboxes
    for _, menu in dados_admin["menus"].sort_values("Ordem").iterrows():
        with st.container(border=True):
            st.markdown(f"**Menu: {menu['Nome']}**")
            
            # Filtra as funcionalidades daquele menu
            funcs_do_menu = dados_admin["funcionalidades"][dados_admin["funcionalidades"]["ID_Menu"].astype(str) == str(menu["ID"])]
            
            if funcs_do_menu.empty:
                st.caption("Nenhuma funcionalidade cadastrada para este menu.")
                continue

            for _, func in funcs_do_menu.iterrows():
                # Define se o checkbox deve vir marcado (permissão atual)
                marcado = str(func["ID"]) in ids_func_permitidas
                
                # Cria o checkbox e armazena seu estado no dicionário
                novas_permissoes_selecao[str(func["ID"])] = st.checkbox(
                    label=f"{func['Nome']}",
                    value=marcado,
                    key=f"check_{usuario_id_selecionado}_{func['ID']}" # Chave única para evitar conflitos
                )

    # --- Botão para Salvar ---
    if st.button("💾 Salvar Permissões para este Usuário", type="primary", use_container_width=True):
        # 1. Deleta todas as permissões antigas do usuário
        for id_permissao_antiga in permissoes_atuais["ID"].tolist():
            conversa_banco.delete(TABELA_PERMISSOES, id_permissao_antiga)

        # 2. Insere as novas permissões baseadas nos checkboxes marcados
        permissoes_para_inserir = []
        for id_func, marcado in novas_permissoes_selecao.items():
            if marcado:
                permissoes_para_inserir.append({
                    "ID_Usuario": usuario_id_selecionado,
                    "ID_Funcionalidade": id_func,
                })
        
        if permissoes_para_inserir:
            conversa_banco.insert(TABELA_PERMISSOES, permissoes_para_inserir)
        
        st.success(f"✅ Permissões para o usuário **{usuario_selecionado_label}** foram atualizadas com sucesso!")
        # Limpa o cache para garantir que na próxima carga os dados estejam atualizados
        st.cache_data.clear()