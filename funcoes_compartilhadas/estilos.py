# funcoes_compartilhadas/estilos.py
import streamlit as st

def aplicar_estilo_padrao():
    st.markdown(
        """
        <style>
            /* Remove o padding excessivo do topo */
            .block-container {
                padding-top: 2rem;
            }
            /* Estilo para o botão de logout */
            section[data-testid="stSidebar"] .stButton button {
                background-color: #e0e0e0;
                color: #333;
            }
            section[data-testid="stSidebar"] .stButton button:hover {
                background-color: #f44336;
                color: white;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_page_title(title: str):
    st.title(title)
    st.markdown("---")