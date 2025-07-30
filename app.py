# app.py
# -*- coding: utf-8 -*-

import streamlit as st
import importlib
import sys
from funcoes_compartilhadas import conversa_banco, estilos, controle_acesso

# --- Configuração Inicial da Página ---
st.set_page_config(
    page_title="Merco Contratos",
    page_icon="✍️",
    layout="wide"
)
estilos.aplicar_estilo_padrao()

# # --- Lógica de Login ---
# # Se o usuário não estiver logado, mostra a tela de login e para a execução.
# if not controle_acesso.usuario_logado():
#     controle_acesso.login()
#     st.stop()

# --- Lógica de Login (MODO DESENVOLVIMENTO - LOGIN DESATIVADO) ---
# O bloco de login original foi comentado para agilizar o desenvolvimento.
if not controle_acesso.usuario_logado():
      controle_acesso.login()
      st.stop()

# Força um usuário "ADMIN" logado para não precisar fazer login toda hora.
# Lembre-se de reativar o bloco de login acima para o ambiente de produção!
# if "usuario_logado" not in st.session_state:
#     st.session_state["usuario_logado"] = {
#        "ID": "ADMIN",
#         "Nome": "Desenvolvedor",
#          "Email": "dev@test.com"
#      }

# --- Construção do Menu Lateral Dinâmico ---
st.sidebar.image("imagens/logo.png", use_container_width=True) # Adicione sua logo em /imagens/logo.png
st.sidebar.markdown("---")

# Busca os menus e funcionalidades da planilha
try:
    menus = conversa_banco.select("menus", {"ID": "id", "Nome": "texto", "Ordem": "numero"})
    funcionalidades = conversa_banco.select("funcionalidades", {"ID": "id", "ID_Menu": "texto", "Nome": "texto", "Caminho": "texto"})
    
    # Aplica permissões (se houver)
    permissoes = controle_acesso.menus_liberados()
    if permissoes is not None: # Se não for Admin, filtra as funcionalidades permitidas
        ids_permitidos = [str(p["ID_Funcionalidade"]) for p in permissoes]
        funcionalidades = funcionalidades[funcionalidades["ID"].astype(str).isin(ids_permitidos)]

    # Monta o dicionário de menus disponíveis
    menus_disponiveis = {}
    for _, menu in menus.sort_values("Ordem").iterrows():
        itens = funcionalidades[funcionalidades["ID_Menu"].astype(str) == str(menu["ID"])]
        if not itens.empty:
            menus_disponiveis[menu["Nome"]] = {
                row["Caminho"]: row["Nome"]
                for _, row in itens.iterrows()
            }

    if not menus_disponiveis:
        st.warning("⚠️ Você não tem acesso a nenhuma funcionalidade.")
        controle_acesso.logout() # Mostra o botão de logout mesmo assim
        st.stop()

    # Renderiza os menus na sidebar
    area_selecionada = st.sidebar.selectbox("Área:", list(menus_disponiveis.keys()))
    
    funcionalidades_da_area = menus_disponiveis[area_selecionada]
    
    pagina_selecionada = st.sidebar.radio(
        "Funcionalidade:",
        list(funcionalidades_da_area.values())
    )

except Exception as e:
    st.error(f"Ocorreu um erro ao montar o menu. Verifique se as abas 'menus' e 'funcionalidades' estão corretas na sua planilha. Erro: {e}")
    st.stop()

# --- Carregamento da Página Selecionada ---
try:
    # Encontra o nome do arquivo .py correspondente à página selecionada
    arquivo_pagina = next(caminho for caminho, nome in funcionalidades_da_area.items() if nome == pagina_selecionada)
    
    # Importa e executa a função 'app' do módulo da página
    caminho_modulo = f"paginas.{arquivo_pagina}"
    if caminho_modulo in sys.modules:
        modulo_pagina = importlib.reload(sys.modules[caminho_modulo])
    else:
        modulo_pagina = importlib.import_module(caminho_modulo)
    
    modulo_pagina.app()

except StopIteration:
    st.info("Selecione uma funcionalidade no menu ao lado.")
except Exception as e:
    st.error(f"Erro ao carregar a página '{pagina_selecionada}': {e}")


# --- Botão de Logout no final da Sidebar ---
controle_acesso.logout()