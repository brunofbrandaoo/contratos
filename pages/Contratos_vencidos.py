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

def show_contratos_vencidos():
    st.title('Contratos Vencidos')

    # Obter dados dos contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        vencidos = []
        for contract in contracts:
            vig_fim_date = datetime.strptime(contract[8], '%Y-%m-%d').date()
            dias_a_vencer = max(0, (vig_fim_date - today).days)  # Garante que não decresça abaixo de 0
            situacao_calculada = calculate_situation(dias_a_vencer)
            if situacao_calculada == 'Vencido':
                link_detalhes = f"https://contratos-sudema.streamlit.app/Total_contratos?page=details&contract_id={contract[0]}"
                vencidos.append(
                    (
                        contract[2], contract[3], contract[4], 
                        contract[6], contract[7], contract[8], dias_a_vencer, situacao_calculada, 
                        contract[11], contract[24], link_detalhes
                    )
                )
        
        df = pd.DataFrame(
            vencidos, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 
                'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )

        # Aplicar cor preta para todas as células da coluna Situação
        def color_situation(val):
            return 'background-color: black; color: white'

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

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer):
    dias_vencer = max(0, dias_vencer)  # Garante que não decresça abaixo de 0
    if dias_vencer == 0:
        return 'Vencido'
    elif dias_vencer <= 30:
        return 'Renovar'
    elif dias_vencer <= 60:
        return 'Vencer 30 a 60 dias'
    elif dias_vencer <= 90:
        return 'Vencer 60 a 90 dias'
    else:
        return 'Vigente'

# Chama a função show_contratos_vencidos
show_contratos_vencidos()
