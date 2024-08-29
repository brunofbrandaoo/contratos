import streamlit as st
import pandas as pd
from db import get_contracts
from datetime import datetime

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

def show_vencer_120_180():
    st.title('Contratos a Vencer em 120 a 180 Dias')

    # Obter dados dos contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        vencer_60_90 = []
        for contract in contracts:
            vig_fim_date = datetime.strptime(contract[8], '%Y-%m-%d').date()
            dias_a_vencer = (vig_fim_date - today).days
            situacao_calculada = calculate_situation(dias_a_vencer)
            if situacao_calculada == 'Vencer 120 a 180 dias':
                link_detalhes = f"http://localhost:8501/Total_contratos?page=details&contract_id={contract[0]}"
                vencer_60_90.append(
                    (
                        contract[2], contract[3], contract[4], contract[6], 
                        contract[7], contract[8], contract[9], dias_a_vencer, situacao_calculada, 
                        contract[11], contract[24], link_detalhes
                    )
                )
        
        df = pd.DataFrame(
            vencer_60_90, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Prazo Limite', 
                'Dias a Vencer', 'Situação', 'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )
        def color_situation(val):
            return 'background-color: #054f77; color: white'

        styled_df = df.style.applymap(color_situation, subset=['Situação'])

        # Configurar a coluna de links
        st.dataframe(
            styled_df,
            column_config={
                "Detalhar": st.column_config.LinkColumn(
                    "Detalhar",
                    help="Clique para ver os detalhes do contrato",
                    display_text="Detalhar"
                )
            },
            hide_index=True,
        )
    else:
        st.write("Nenhum contrato encontrado.")

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

# Chama a função show_vencer_60_90
show_vencer_120_180()
