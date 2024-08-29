import streamlit as st
import pandas as pd
import altair as alt
from db import get_contracts
from datetime import datetime
import streamlit_shadcn_ui as ui

# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")

st.sidebar.header("Navegação")
st.sidebar.page_link("Dashboard.py", label="Dashboard", icon="📊")
st.sidebar.page_link("pages/Total_contratos.py", label="Planilhas", icon="📈")
st.sidebar.page_link("pages/Vencer_30_60.py", label="Contratos com vencimento de 30 a 60 dias", icon="🟥")
st.sidebar.page_link("pages/Vencimento_60_a_90.py", label="Contratos com vencimento de 60 a 90 dias", icon="🟧")
st.sidebar.page_link("pages/vencer_90_120.py", label="Contratos com vencimento de 90 a 120 dias", icon="🟨")
st.sidebar.page_link("pages/vencer_120_180.py", label="Contratos com vencimento de 120 a 180 dias", icon="🟦")
st.sidebar.page_link("pages/Contratos_vencidos.py", label="Contratos vencidos", icon="⬛")

# st.logo(
#     LOGO_URL_LARGE,
#     link="logo_sudema.png",
#     icon_image=LOGO_URL_SMALL,
# )

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer):
    if dias_vencer < 0:
        return 'Vencido'
    elif 30 <= dias_vencer <= 60:
        return 'Renovar'
    elif 60 <= dias_vencer <= 90:
        return 'Vencer 60 a 90 dias'
    elif 90 <= dias_vencer <= 120:
        return 'Vencer 90 a 120 dias'
    elif 120 <= dias_vencer <= 180:
        return 'Vencer 120 a 180 dias'
    else:
        return 'Vigente'

# Função para calcular os dados do dashboard
def calculate_dashboard_data(contracts):
    total = len(contracts)
    vencido = sum(1 for contract in contracts if contract[11] == 'Vencido')
    vencer_30_60 = sum(1 for contract in contracts if contract[11] == 'Vencer 30 a 60 dias')
    vencer_60_90 = sum(1 for contract in contracts if contract[11] == 'Vencer 60 a 90 dias')
    vencer_90_120 = sum(1 for contract in contracts if contract[11] == 'Vencer 90 a 120 dias')
    vencer_120_180 = sum(1 for contract in contracts if contract[11] == 'Vencer 120 a 180 dias')
    vigente = total - (vencido + vencer_30_60 + vencer_60_90 + vencer_90_120 + vencer_120_180)
    
    vencido_percent = (vencido / total) * 100 if total else 0
    vencer_30_60_percent = (vencer_30_60 / total) * 100 if total else 0
    vencer_60_90_percent = (vencer_60_90 / total) * 100 if total else 0
    vencer_90_120_percent = (vencer_90_120 / total) * 100 if total else 0
    vencer_120_180_percent = (vencer_120_180 / total) * 100 if total else 0
    vigente_percent = (vigente / total) * 100 if total else 0
    
    return total, vencido, vencer_30_60, vencer_60_90, vencer_90_120, vencer_120_180, vigente, vencido_percent, vencer_30_60_percent, vencer_60_90_percent, vencer_90_120_percent, vencer_120_180_percent, vigente_percent

def show_dashboard():
    st.markdown("<h1 style='text-align: center; margin-bottom: 48px;'>Gestão de Vigência de Contratos</h1>", unsafe_allow_html=True)

    # Obter dados dos contratos
    contracts = get_contracts()
    if contracts:
        today = datetime.today().date()
        contracts = [(contract[0], contract[1], contract[2], contract[3], contract[4], contract[5], contract[6], contract[7], contract[8], contract[9], (datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days, calculate_situation((datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days)) for contract in contracts]
        total, vencido, vencer_30_60, vencer_60_90, vencer_90_120, vencer_120_180, vigente, vencido_percent, vencer_30_60_percent, vencer_60_90_percent, vencer_90_120_percent, vencer_120_180_percent, vigente_percent = calculate_dashboard_data(contracts)

        # Configuração de colunas
        col1, col2 = st.columns([1, 1])

        with col1:
            # Exibir link buttons do dashboard com contadores em HTML e CSS
            buttons_html = f"""
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <a href="/Total_contratos" style="text-decoration: none;">
                    <div style="background-color: #90ee90; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 24px;">Total Contratos</div>
                        <div style="font-size: 32px;">{total}</div>
                    </div>
                </a>
                <a href="/Vencer_30_60" style="text-decoration: none;">
                    <div style="background-color: #ff0000; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div>Vencem em 30 a 60 dias</div>
                        <div style="font-size: 24px;">{vencer_30_60}</div>
                    </div>
                </a>
                <a href="/Vencimento_60_a_90" style="text-decoration: none;">
                    <div style="background-color: #ff7f50; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div>Vencem em 60 a 90 Dias</div>
                        <div style="font-size: 24px;">{vencer_60_90}</div>
                    </div>
                </a>
                <a href="/vencer_90_120" style="text-decoration: none;">
                    <div style="background-color: #ffc107; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div>Vencem em 90 a 120 dias</div>
                        <div style="font-size: 24px;">{vencer_90_120}</div>
                    </div>
                </a>
                <a href="/vencer_120_180" style="text-decoration: none;">
                    <div style="background-color: #054f77; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div>Vencem em 120 a 180 Dias</div>
                        <div style="font-size: 24px;">{vencer_120_180}</div>
                    </div>
                </a>
                <a href="/Contratos_vencidos" style="text-decoration: none;">
                    <div style="background-color: #343a40; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div>Contratos Vencidos</div>
                        <div style="font-size: 24px;">{vencido}</div>
                    </div>
                </a>
            </div>
            """
            st.markdown(buttons_html, unsafe_allow_html=True)

        with col2:
            # Exibir gráfico de barras
            df = pd.DataFrame({
                'Situação': ['Vencido', 'Vencer 30 a 60 dias', 'Vencer 60 a 90 dias', 'Vencer 90 a 120 dias', 'Vencer 120 a 180 dias', 'Vigente'],
                'Quantidade': [vencido, vencer_30_60, vencer_60_90, vencer_90_120, vencer_120_180, vigente]
            })

            # Mapa de cores
            color_scale = alt.Scale(
                domain=['Vencido', 'Vencer 30 a 60 dias', 'Vencer 60 a 90 dias', 'Vencer 90 a 120 dias', 'Vencer 120 a 180 dias', 'Vigente'],
                range=['#343a40', '#ff0000', '#ff7f50', '#ffc107', '#add8e6', '#d3d3d3']
            )

            # Criar o gráfico de barras
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('Situação', sort=None),
                y=alt.Y('Quantidade', scale=alt.Scale(domain=[0, 50])),
                color=alt.Color('Situação', scale=color_scale)
            ).properties(
                title='Distribuição dos Contratos por Situação',
                width='container',  # Definir a largura do gráfico para se ajustar ao container
                height=300
            ).configure_axis(
                grid=False  # Remove as linhas de grade
            )

            # Exibir o gráfico no Streamlit
            st.altair_chart(chart, use_container_width=True)

            # Filtrar contratos para renovar e ordenar por dias a vencer

            # Ordenando os contratos com base no penúltimo elemento (dias a vencer)
            contracts_sorted_by_days = sorted(contracts, key=lambda x: x[-2])

            # Extraindo os valores dos terceiros elementos e penúltimos elementos
            numero_contrato_1 = contracts_sorted_by_days[0][2]
            dias_a_vencer_1 = contracts_sorted_by_days[0][-2]

            numero_contrato_2 = contracts_sorted_by_days[1][2]
            dias_a_vencer_2 = contracts_sorted_by_days[1][-2]

            numero_contrato_3 = contracts_sorted_by_days[2][2]
            dias_a_vencer_3 = contracts_sorted_by_days[2][-2]

            # numero_contrato_4 = contracts_sorted_by_days[3][2]
            # dias_a_vencer_4 = contracts_sorted_by_days[3][-2]


            # Exibir os valores em uma lista HTML e CSS estilizada
            list_html = f"""
            <div style="background-color: #ffe6e6; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #dc3545; margin-bottom: 20px;">Urgências para Renovação</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li style="margin-bottom: 10px; padding: 15px; background-color: white; border-radius: 4px; border-left: 5px solid #dc3545; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <strong>Contrato:</strong> {numero_contrato_1} - <strong style="color: #dc3545;">Dias a Vencer:</strong> {dias_a_vencer_1}
                    </li>
                    <li style="margin-bottom: 10px; padding: 15px; background-color: white; border-radius: 4px; border-left: 5px solid #dc3545; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <strong>Contrato:</strong> {numero_contrato_2} - <strong style="color: #dc3545;">Dias a Vencer:</strong> {dias_a_vencer_2}
                    </li>
                    <li style="margin-bottom: 10px; padding: 15px; background-color: white; border-radius: 4px; border-left: 5px solid #dc3545; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <strong>Contrato:</strong> {numero_contrato_3} - <strong style="color: #dc3545;">Dias a Vencer:</strong> {dias_a_vencer_3}
                    </li>
                </ul>
            </div>
            """

            st.markdown(list_html, unsafe_allow_html=True)

    else:
        st.write("Nenhum contrato encontrado.")

# Chama a função show_dashboard
show_dashboard()
