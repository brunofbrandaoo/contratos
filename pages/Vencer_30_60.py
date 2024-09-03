import streamlit as st
import pandas as pd
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

def show_vencer_30_60():
    st.title('Contratos a vencer em até 60 dias')
    # Obter dados dos contratos
    contracts = get_contracts()

    # st.json(contracts[5])
    if contracts:
        today = datetime.today().date()
        renovar = []
        for contract in contracts:
            vig_fim_date = datetime.strptime(contract[8], '%Y-%m-%d').date()
            dias_a_vencer = (vig_fim_date - today).days
            passivel_renovacao = contract[25]  # Supondo que o campo `passivel_renovacao` esteja na posição 10

            # Calcula a situação considerando o campo passível de renovação
            situacao_calculada = calculate_situation(dias_a_vencer, passivel_renovacao)

            if situacao_calculada in ['Renovar', 'Novo Processo']:
                link_detalhes = f"http://localhost:8501/Total_contratos?page=details&contract_id={contract[0]}"
                renovar.append(
                    (
                        contract[2], contract[3], contract[4], 
                        contract[6], contract[7], contract[8], dias_a_vencer, situacao_calculada, 
                        contract[11], contract[24], link_detalhes
                    )
                )

        df = pd.DataFrame(
            renovar, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 
                'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )

        # Aplicar cor vermelha para todas as células da coluna Situação onde a situação é "Renovar" ou "Novo Processo"
        def color_situation(val):
            color = 'background-color: red; color: white' if val in ['Renovar', 'Novo Processo'] else ''
            return color

        styled_df = df.style.applymap(color_situation, subset=['Situação'])

        # Configurar a coluna de links
        st.dataframe(
            styled_df,
            column_config={
                "Detalhar": st.column_config.LinkColumn(
                    "Detalhar",
                    help="Clique para ver os detalhes do contrato",
                    display_text="Detalhar"
                ),
                "Valor do Contrato": st.column_config.NumberColumn(
                    "Valor do Contrato",
                    help="Valor do contrato em reais",
                    min_value=0,
                    max_value=100000000,
                ),
                "Movimentação": st.column_config.Column(
                    "Movimentação",
                    help="Movimentação do contrato",
                    width="large",
                )
            },
            hide_index=True,
        )
    else:
        st.write("Nenhum contrato encontrado.")

# Função para calcular a situação do contrato considerando o campo passível de renovação
def calculate_situation(dias_vencer, passivel_renovacao):
    if dias_vencer < 0:
        return 'Vencido'
    elif 1 < dias_vencer <= 60:
        return 'Renovar' if passivel_renovacao == 1 else 'Novo Processo'
    elif 60 <= dias_vencer <= 90:
        return 'Vencer 60 a 90 dias'
    elif 90 <= dias_vencer <= 120:
        return 'Vencer 90 a 120 dias'
    elif 120 <= dias_vencer <= 180:
        return 'Vencer 120 a 180 dias'
    else:
        return 'Vigente'

# Chama a função show_vencer_30_60
show_vencer_30_60()
