import streamlit as st
import pandas as pd
from db import get_contracts
from datetime import datetime

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
    vencido = sum(1 for contract in contracts if contract[6] == 'Vencido')
    renovar = sum(1 for contract in contracts if contract[6] == 'Renovar')
    vencer_30_60 = sum(1 for contract in contracts if contract[6] == 'Vencer 30 a 60 dias')
    vencer_60_90 = sum(1 for contract in contracts if contract[6] == 'Vencer 60 a 90 dias')
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
        contracts = [(contract[0], contract[1], contract[2], contract[3], datetime.strptime(contract[4], '%Y-%m-%d').date(), (datetime.strptime(contract[4], '%Y-%m-%d').date() - today).days, calculate_situation((datetime.strptime(contract[4], '%Y-%m-%d').date() - today).days)) for contract in contracts]
        total, vencido, renovar, vencer_30_60, vencer_60_90, vigente, vencido_percent, renovar_percent, vencer_30_60_percent, vencer_60_90_percent, vigente_percent = calculate_dashboard_data(contracts)

        # Exibir cartões do dashboard
        st.markdown(f"""
        <style>
            .dashboard-container {{
                display: flex;
                justify-content: space-between;
                gap: 10px;
                flex-wrap: wrap;
            }}
            .dashboard-box {{
                flex: 1;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                color: white;
                min-width: 200px;
            }}
            .dashboard-box h3, .dashboard-box h1, .dashboard-box p {{
                color: white;
            }}
            .total-contratos {{ background-color: #28a745; }}
            .vencido {{ background-color: #dc3545; }}
            .renovar {{ background-color: #fd7e14; }}
            .vencer-30-60 {{ background-color: #ffc107; }}
            .vencer-60-90 {{ background-color: #ff7f50; }}
        </style>
        <div class="dashboard-container">
            <div class="dashboard-box total-contratos">
                <h3>TOTAL CONTRATOS</h3>
                <h1>{total}</h1>
                <p>100% Contratos ativos</p>
            </div>
            <div class="dashboard-box vencido">
                <h3>CONTRATOS VENCIDOS</h3>
                <h1>{vencido}</h1>
                <p>{vencido_percent:.2f}% contratos vencidos</p>
            </div>
            <div class="dashboard-box renovar">
                <h3>VENCEM EM (30 DIAS)</h3>
                <h1>{renovar}</h1>
                <p>{renovar_percent:.2f}% à vencer (30 Dias)</p>
            </div>
            <div class="dashboard-box vencer-30-60">
                <h3>VENCEM EM (30 A 60 DIAS)</h3>
                <h1>{vencer_30_60}</h1>
                <p>{vencer_30_60_percent:.2f}% à vencer (30 a 60 Dias)</p>
            </div>
            <div class="dashboard-box vencer-60-90">
                <h3>VENCEM EM (60 A 90 DIAS)</h1>
                <h1>{vencer_60_90}</h1>
                <p>{vencer_60_90_percent:.2f}% à vencer (60 a 90 Dias)</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write("Nenhum contrato encontrado.")
