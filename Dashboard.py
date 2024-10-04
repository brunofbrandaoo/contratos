import streamlit as st
import pandas as pd
import altair as alt
from db import get_contracts
from datetime import datetime

# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")

st.sidebar.header("Navegação")
st.sidebar.page_link("Dashboard.py", label="Dashboard", icon="📊")
st.sidebar.page_link("pages/Total_contratos.py", label="Planilhas", icon="📈")
st.sidebar.page_link("pages/Vencer_30_60.py", label="Contratos com vencimento de 0 a 60 dias", icon="🟥")
st.sidebar.page_link("pages/Vencimento_60_a_90.py", label="Contratos com vencimento de 60 a 90 dias", icon="🟧")
st.sidebar.page_link("pages/vencer_90_120.py", label="Contratos com vencimento de 90 a 120 dias", icon="🟨")
st.sidebar.page_link("pages/vencer_120_180.py", label="Contratos com vencimento de 120 a 180 dias", icon="🟦")
st.sidebar.page_link("pages/Contratos_vencidos.py", label="Contratos vencidos", icon="⬛")

st.logo(image="sudema.png", link=None)

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer, passivel_renovacao):
    dias_vencer = max(0, dias_vencer)  # Garante que dias_vencer não seja negativo
    if dias_vencer == 0:
        return 'Vencido'
    elif dias_vencer <= 60:
        return 'Renovar' if passivel_renovacao == 1 else 'Novo Processo'
    elif 60 < dias_vencer <= 90:
        return 'Vencer 60 a 90 dias'
    elif 90 < dias_vencer <= 120:
        return 'Vencer 90 a 120 dias'
    elif 120 < dias_vencer <= 180:
        return 'Vencer 120 a 180 dias'
    else:
        return 'Vigente'
    
def calculate_days_to_expiry(vig_fim, today):
    """Calcula o número de dias a vencer entre vig_fim e today."""
    if isinstance(vig_fim, datetime):
        vig_fim_date = vig_fim  # Usando o valor correto para a data de vigência final
    else:
        try:
            vig_fim_date = datetime.strptime(str(vig_fim), '%Y-%m-%d').date()
        except ValueError:
            print(f"Data inválida encontrada no contrato: {vig_fim}")
            vig_fim_date = today  # Se a conversão falhar, use a data de hoje como fallback
    return (vig_fim_date - today).days
    
def convert_to_date(value):
    """Converte o valor para uma data, se necessário."""
    if isinstance(value, datetime):
        return value.date()  # Se já for datetime, retorna a data
    elif isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()  # Tenta converter de string para datetime
        except ValueError:
            return datetime.today().date()  # Se falhar, usa a data de hoje como fallback
    else:
        return datetime.today().date()  # Se for outro tipo, usa a data de hoje como fallback


# Função para calcular os dados do dashboard
def calculate_dashboard_data(contracts):
    """Calcula a quantidade de contratos em cada situação."""
    total = len(contracts)
    vencido = sum(1 for contract in contracts if contract[-1] == 'Vencido')
    vencer_30_60 = sum(1 for contract in contracts if contract[-1] in ['Renovar', 'Novo Processo'])
    vencer_60_90 = sum(1 for contract in contracts if contract[-1] == 'Vencer 60 a 90 dias')
    vencer_90_120 = sum(1 for contract in contracts if contract[-1] == 'Vencer 90 a 120 dias')
    vencer_120_180 = sum(1 for contract in contracts if contract[-1] == 'Vencer 120 a 180 dias')
    vigente = total - (vencido + vencer_30_60 + vencer_60_90 + vencer_90_120 + vencer_120_180)
    
    return total, vencido, vencer_30_60, vencer_60_90, vencer_90_120, vencer_120_180, vigente


def show_dashboard():
    st.markdown("<h1 style='text-align: center; margin-bottom: 48px;'>Gestão de Vigência de Contratos</h1>", unsafe_allow_html=True)

    # Obter dados dos contratos
    contracts = get_contracts()
    if contracts:
        today = datetime.today().date()

        # Calcular os dias a vencer e a situação para cada contrato
        contracts = [
            (
                contract[0],  # ID do contrato
                contract[7],  # Vigência final
                # Ajuste para garantir que estamos usando o índice correto para vig_fim
                calculate_days_to_expiry(contract[7], today),  # Função ajustada para calcular dias a vencer
                calculate_situation(calculate_days_to_expiry(contract[7], today), contract[18])  # Situação calculada
            ) for contract in contracts
        ]

        # Print para depuração (opcional)
        print("Verificação dos Contratos:")
        for contract in contracts:
            print(f"ID: {contract[0]}, Vigência Final: {contract[1]}, Dias a Vencer: {contract[2]}, Situação: {contract[3]}")

        # Calcular as quantidades de contratos em cada situação
        total, vencido, vencer_30_60, vencer_60_90, vencer_90_120, vencer_120_180, vigente = calculate_dashboard_data(contracts)


        # Exibir os resultados no dashboard usando a lógica existente
        col1, col2 = st.columns([1, 1])

        with col1:
            # Exibir link buttons do dashboard com contadores em HTML e CSS
            buttons_html = f"""
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <a href="/Total_contratos" style="text-decoration: none;">
                    <div style="background-color: #38761d; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 24px;">Total Contratos</div>
                        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: white; color: #38761d; display: flex; align-items: center; justify-content: center; font-size: 40px; margin-top: 10px;">
                            {total}
                        </div>
                    </div>
                </a>
                <a href="/Vencer_30_60" style="text-decoration: none;">
                    <div style="background-color: #ff0000; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 24px;">Vencem em até 60 dias</div>
                        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: white; color: #ff0000; display: flex; align-items: center; justify-content: center; font-size: 40px; margin-top: 10px;">
                            {vencer_30_60}
                        </div>
                    </div>
                </a>
                <a href="/Vencimento_60_a_90" style="text-decoration: none;">
                    <div style="background-color: #fe843d; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 24px;">Vencem em 60 a 90 Dias</div>
                        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: white; color: #fe843d; display: flex; align-items: center; justify-content: center; font-size: 40px; margin-top: 10px;">
                            {vencer_60_90}
                        </div>
                    </div>
                </a>
                <a href="/vencer_90_120" style="text-decoration: none;">
                    <div style="background-color: #ffc107; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 24px;">Vencem em 90 a 120 dias</div>
                        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: white; color: #ffc107; display: flex; align-items: center; justify-content: center; font-size: 40px; margin-top: 10px;">
                            {vencer_90_120}
                        </div>
                    </div>
                </a>
                <a href="/vencer_120_180" style="text-decoration: none;">
                    <div style="background-color: #054f77; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 24px;">Vencem em 120 a 180 Dias</div>
                        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: white; color: #054f77; display: flex; align-items: center; justify-content: center; font-size: 40px; margin-top: 10px;">
                            {vencer_120_180}
                        </div>
                    </div>
                </a>
                <a href="/Contratos_vencidos" style="text-decoration: none;">
                    <div style="background-color: #343a40; color: white; border-radius: 8px; width: 440px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="font-size: 24px;">Contratos Vencidos</div>
                        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: white; color: #343a40; display: flex; align-items: center; justify-content: center; font-size: 40px; margin-top: 10px;">
                            {vencido}
                        </div>
                    </div>
                </a>
            </div>
            """

            st.markdown(buttons_html, unsafe_allow_html=True)

        with col2:
            # Exibir gráfico de barras
            df = pd.DataFrame({
                'Situação': ['Vencido', 'Vencer em até 60 dias', 'Vencer 60 a 90 dias', 'Vencer 90 a 120 dias', 'Vencer 120 a 180 dias', 'Vigente'],
                'Quantidade': [vencido, vencer_30_60, vencer_60_90, vencer_90_120, vencer_120_180, vigente]
            })

            # Mapa de cores
            color_scale = alt.Scale(
                domain=['Vencido', 'Vencer em até 60 dias', 'Vencer 60 a 90 dias', 'Vencer 90 a 120 dias', 'Vencer 120 a 180 dias', 'Vigente'],
                range=['#343a40', '#ff0000', '#fe843d', '#ffc107', '#054f77', '#38761d']
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

    else:
        st.write("Nenhum contrato encontrado.")

# Chama a função show_dashboard
show_dashboard()
