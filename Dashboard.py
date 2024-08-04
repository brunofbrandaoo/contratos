import streamlit as st
import pandas as pd
import altair as alt
from db import get_contracts
from datetime import datetime
import streamlit_shadcn_ui as ui

#colocar container azul 90 a 180
# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")

st.sidebar.header("Navegação")
st.sidebar.page_link("Dashboard.py", label="Dashboard", icon="📊")
st.sidebar.page_link("pages/Total_contratos.py", label="Planilhas", icon="📈")
st.sidebar.page_link("pages/Contratos_para_renovar.py", label="Contratos para renovar", icon="🟥")
st.sidebar.page_link("pages/Vencimento_30_a_60.py", label="Contratos com vencimento de 30 a 60 dias", icon="🟧")
st.sidebar.page_link("pages/vencer_60_90.py", label="Contratos com vencimento de 60 a 90 dias", icon="🟨")
st.sidebar.page_link("pages/Contratos_vencidos.py", label="Contratos vencidos", icon="⬛")

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
    st.markdown("<h1 style='text-align: center; margin-bottom: 48px;'>Gestão de Vigência de Contratos</h1>", unsafe_allow_html=True)

    # Obter dados dos contratos
    contracts = get_contracts()
    if contracts:
        today = datetime.today().date()
        contracts = [(contract[0], contract[1], contract[2], contract[3], contract[4], contract[5], contract[6], contract[7], contract[8], contract[9], (datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days, calculate_situation((datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days)) for contract in contracts]
        total, vencido, renovar, vencer_30_60, vencer_60_90, vigente, vencido_percent, renovar_percent, vencer_30_60_percent, vencer_60_90_percent, vigente_percent = calculate_dashboard_data(contracts)

        # Exibir link buttons do dashboard com contadores em HTML e CSS
        buttons_html = f"""
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            <a href="/Planilhas" style="text-decoration: none;">
                <div style="background-color: #28a745; color: white; border-radius: 8px; width: 360px; height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div>Total Contratos</div>
                    <div style="font-size: 24px;">{total}</div>
                </div>
            </a>
            <a href="/Contratos_para_renovar" style="text-decoration: none;">
                <div style="background-color: #dc3545; color: white; border-radius: 8px; width: 360px; height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div>Renovar - até 30 dias</div>
                    <div style="font-size: 24px;">{renovar}</div>
                </div>
            </a>
            <a href="/Vencimento_30_a_60" style="text-decoration: none;">
                <div style="background-color: #ff7f50; color: white; border-radius: 8px; width: 360px; height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div>Vencer em 30 a 60 Dias</div>
                    <div style="font-size: 24px;">{vencer_30_60}</div>
                </div>
            </a>
            <a href="/vencer_60_90" style="text-decoration: none;">
                <div style="background-color: #ffc107; color: white; border-radius: 8px; width: 360px; height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div>Vencer em 60 a 90 Dias</div>
                    <div style="font-size: 24px;">{vencer_60_90}</div>
                </div>
            </a>
            <a href="/Contratos_vencidos" style="text-decoration: none;">
                <div style="background-color: #343a40; color: white; border-radius: 8px; width: 360px; height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div>Contratos Vencidos</div>
                    <div style="font-size: 24px;">{vencido}</div>
                </div>
            </a>
        </div>
        """
        st.markdown(buttons_html, unsafe_allow_html=True)

        # Adicionar espaçamento vertical
        st.markdown("<div style='margin-top: 200px;'></div>", unsafe_allow_html=True)

        # Exibir gráfico de barras
        df = pd.DataFrame({
            'Situação': ['Vencido', 'Renovar', 'Vencer 30 a 60 dias', 'Vencer 60 a 90 dias', 'Vigente'],
            'Quantidade': [vencido, renovar, vencer_30_60, vencer_60_90, vigente]
        })

        # Mapa de cores
        color_scale = alt.Scale(
            domain=['Vencido', 'Renovar', 'Vencer 30 a 60 dias', 'Vencer 60 a 90 dias', 'Vigente'],
            range=['#000000', '#dc3545', '#ff7f50', '#ffc107', '#28a745']
        )

        # Criar o gráfico de barras
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Situação', sort=None),
            y=alt.Y('Quantidade', scale=alt.Scale(domain=[0, 50])),
            color=alt.Color('Situação', scale=color_scale)
        ).properties(
            title='Distribuição dos Contratos por Situação',
            width=300,  # Definir a largura do gráfico
            height=600
        ).configure_axis(
            grid=False  # Remove as linhas de grade
        )

        # Exibir o gráfico no Streamlit
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Nenhum contrato encontrado.")

# Chama a função show_dashboard
show_dashboard()
