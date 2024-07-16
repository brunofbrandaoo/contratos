import streamlit as st
from dashboard import show_dashboard
from planilha import show_planilha
from gerenciar_contratos import show_gerenciar_contratos
# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")

# Criar abas na interface principal
tab1, tab2, tab3 = st.tabs(['Dashboard', 'Planilha', 'Gerenciar Contratos'])

with tab1:
    show_dashboard()

with tab2:
    show_planilha()

with tab3:
    show_gerenciar_contratos()