import streamlit as st
from dashboard import show_dashboard
from planilha import show_planilha
from gerenciar_contratos import show_gerenciar_contratos

# Barra lateral para navegação
st.sidebar.title('Menu')
page = st.sidebar.radio('Selecione uma página:', ['Dashboard', 'Planilha', 'Gerenciar Contratos'])

if page == 'Dashboard':
    show_dashboard()
elif page == 'Planilha':
    show_planilha()
elif page == 'Gerenciar Contratos':
    show_gerenciar_contratos()
