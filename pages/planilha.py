import streamlit as st
import pandas as pd
from db import get_contracts
from datetime import datetime

# tirar prazo limite
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

# Função para aplicar cores com base na situação
def color_situation(val):
    color = {
        'Vencido': '#000000',
        'Renovar': '#dc3545',
        'Vencer 30 a 60 dias': '#ff7f50',
        'Vencer 60 a 90 dias': '#ffc107',
        'Vigente': '#28a745'
    }.get(val, '')
    return f'background-color: {color}; color: white'

def show_planilha():
    st.title('Planilha de Contratos')

    # Exibir contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        transformed_contracts = []
        for contract in contracts:
            vig_fim_date = datetime.strptime(contract[8], '%Y-%m-%d').date()
            dias_a_vencer = (vig_fim_date - today).days
            situacao_calculada = calculate_situation(dias_a_vencer)
            transformed_contracts.append(
                (
                    contract[2], contract[3], contract[4], 
                    contract[6], contract[7], contract[8], dias_a_vencer, situacao_calculada, 
                    contract[11], contract[12]
                )
            )
        
        df = pd.DataFrame(
            transformed_contracts, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 
                'Aditivo', 'Movimentação'
            ]
        )
        
        # Aplicar cores à coluna Situação
        styled_df = df.style.applymap(color_situation, subset=['Situação'])
        
        st.write("## Dados dos Contratos")
        st.dataframe(styled_df)
    else:
        st.write("Nenhum contrato encontrado.")

# Chama a função show_planilha
show_planilha()
