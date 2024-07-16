import streamlit as st
from db import get_contracts
from datetime import datetime
import plotly.express as px
import pandas as pd

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
    st.title('Dashboard de Contratos')

    # Obter dados dos contratos
    contracts = get_contracts()
    if contracts:
        today = datetime.today().date()
        contracts = [(contract[0], contract[1], contract[2], contract[3], contract[4], contract[5], contract[6], contract[7], contract[8], contract[9], (datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days, calculate_situation((datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days)) for contract in contracts]
        total, vencido, renovar, vencer_30_60, vencer_60_90, vigente, vencido_percent, renovar_percent, vencer_30_60_percent, vencer_60_90_percent, vigente_percent = calculate_dashboard_data(contracts)

        # Exibir cartões do dashboard
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            <style>
                .dashboard-container {{
                    display: flex;
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 25px;
                }}
                .dashboard-box {{
                    width: 480px;
                    height: 120px;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                }}
                .dashboard-box h3, .dashboard-box span, .dashboard-box p {{
                    color: white;
                    font-size: 20px;
                    text-align: center;
                }}
                .total-contratos {{ background-color: #d3d3d3; }}
                .vencido {{ background-color: #000000; }}
                .renovar {{ background-color: #dc3545; }}
                .vencer-30-60 {{ background-color: #ff7f50; }}
                .vencer-60-90 {{ background-color: #ffc107; }}
            </style>
            <div class="dashboard-container">
                <div class="dashboard-box total-contratos">
                    <p>TOTAL CONTRATOS</p>
                    <span>{total}</span>
                    <p>100% Contratos ativos</p>
                </div>
                <div class="dashboard-box vencido">
                    <p>CONTRATOS VENCIDOS</p>
                    <span>{vencido}</span>
                    <p>{vencido_percent:.2f}% contratos vencidos</p>
                </div>
                <div class="dashboard-box renovar">
                    <p>VENCEM EM (30 DIAS)</p>
                    <span>{renovar}</span>
                    <p>{renovar_percent:.2f}% à vencer (30 Dias)</p>
                </div>
                <div class="dashboard-box vencer-30-60">
                    <p>VENCEM EM (30 A 60 DIAS)</p>
                    <span>{vencer_30_60}</span>
                    <p>{vencer_30_60_percent:.2f}% à vencer (30 a 60 Dias)</p>
                </div>
                <div class="dashboard-box vencer-60-90">
                    <p>VENCEM EM (60 A 90 DIAS)</p>
                    <span>{vencer_60_90}</span>
                    <p>{vencer_60_90_percent:.2f}% à vencer (60 a 90 Dias)</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
