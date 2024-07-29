import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_contracts
from datetime import datetime
from streamlit_shadcn_ui import link_button

# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer):
    if dias_vencer < 0:
        return 'Vencido'
    elif dias_vencer <= 30:
        return 'Renovar'
    elif dias_vencer <= 60:
        return 'Vencer 30 a 60 dias'
    elif dias_vencer <= 90:
        return 'Vencer 60 a 90 dias'
    else:
        return 'Vigente'

# Função para calcular os dados do dashboard
def calculate_dashboard_data(contracts):
    total = len(contracts)
    vencido = sum(1 for contract in contracts if contract[11] == 'Vencido')
    renovar = sum(1 for contract in contracts if contract[11] == 'Renovar')
    vencer_30_60 = sum(1 for contract in contracts if contract[11] == 'Vencer 30 a 60 dias')
    vencer_60_90 = sum(1 for contract in contracts if contract[11] == 'Vencer 60 a 90 dias')
    vigente = total - (vencido + renovar + vencer_30_60 + vencer_60_90)
    
    vencido_percent = (vencido / total) * 100 if total else 0
    renovar_percent = (renovar / total) * 100 if total else 0
    vencer_30_60_percent = (vencer_30_60 / total) * 100 if total else 0
    vencer_60_90_percent = (vencer_60_90 / total) * 100 if total else 0
    vigente_percent = (vigente / total) * 100 if total else 0
    
    return total, vencido, renovar, vencer_30_60, vencer_60_90, vigente, vencido_percent, renovar_percent, vencer_30_60_percent, vencer_60_90_percent, vigente_percent

def show_dashboard():
    st.markdown("<h1 style='text-align: center; margin-bottom: 48px;'>Dashboard de Contratos</h1>", unsafe_allow_html=True)

    # Obter dados dos contratos
    contracts = get_contracts()
    if contracts:
        today = datetime.today().date()
        contracts = [(contract[0], contract[1], contract[2], contract[3], contract[4], contract[5], contract[6], contract[7], contract[8], contract[9], (datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days, calculate_situation((datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days)) for contract in contracts]
        total, vencido, renovar, vencer_30_60, vencer_60_90, vigente, vencido_percent, renovar_percent, vencer_30_60_percent, vencer_60_90_percent, vigente_percent = calculate_dashboard_data(contracts)

        # Exibir link buttons do dashboard
        col1, col2 = st.columns([2, 1])
        with col1:
            link_button('Total Contratos', '/total_contracts', variant='default', class_name='bg-stone-300 text-white rounded-lg w-96 h-32 hover:bg-stone-100 shadow-md', key='total_contracts')
            link_button('Contratos Vencidos', '/contratos_vencidos', variant='default', class_name='bg-slate-950 hover:bg-slate-550 text-white rounded-lg w-96 h-32 shadow-md', key='contratos_vencidos')
            link_button('Vencer em 30 Dias', '/renovar', variant='default', class_name='bg-red-600 hover:bg-red-300 text-white rounded-lg w-96 h-32 shadow-md', key='vencer_30_dias')
            link_button('Vencer em 30 a 60 Dias', '/vencer_30_60', variant='default', class_name='bg-orange-400 hover:bg-orange-200 text-white rounded-lg w-96 h-32 shadow-md', key='vencer_30_60_dias')
            link_button('Vencer em 60 a 90 Dias', '/vencer_60_90', variant='default', class_name='bg-yellow-300 hover:bg-yellow-100 text-white rounded-lg w-96 h-32 shadow-md', key='vencer_60_90_dias')

        # Exibir gráfico de barras
        with col2:
            df = pd.DataFrame({
                'Situação': ['Vencido', 'Renovar', 'Vencer 30 a 60 dias', 'Vencer 60 a 90 dias', 'Vigente'],
                'Quantidade': [vencido, renovar, vencer_30_60, vencer_60_90, vigente],
                'Cor': ['#000000', '#dc3545', '#ff7f50', '#ffc107', '#28a745']
            })

            fig = px.bar(df, x='Situação', y='Quantidade', color='Situação', 
                         color_discrete_map={
                             'Vencido': '#000000',
                             'Renovar': '#dc3545',
                             'Vencer 30 a 60 dias': '#ff7f50',
                             'Vencer 60 a 90 dias': '#ffc107',
                             'Vigente': '#28a745'
                         },
                         title="Distribuição dos Contratos por Situação")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Nenhum contrato encontrado.")

# Chama a função show_dashboard
show_dashboard()
