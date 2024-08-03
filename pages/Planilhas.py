import streamlit as st
import os

# Define as páginas disponíveis e seus caminhos
pages = {
    "Planilha Principal": "spreadsheets/Total_contratos.py",
    "Contratos a Renovar": "spreadsheets/Contratos_para_renovar.py",
    "Contratos Vencidos": "spreadsheets/Contratos_vencidos.py",
    "Vencimento 30 a 60 dias": "spreadsheets/Vencimento_30_a_60.py",
    "Vencer 60 a 90 dias": "spreadsheets/vencer_60_90.py",
}

# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")

# Menu lateral para navegação
st.sidebar.title("Menu")
selection = st.sidebar.radio("Selecione a página", list(pages.keys()))

# Função para importar e executar o script selecionado
def load_page(page_path):
    if os.path.exists(page_path):
        with open(page_path) as file:
            exec(file.read(), globals())
    else:
        st.error(f"A página {page_path} não foi encontrada.")

# Carrega a página selecionada
load_page(pages[selection])
