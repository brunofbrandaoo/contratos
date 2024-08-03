import streamlit as st
import pandas as pd
from db import get_contracts
from datetime import datetime

# Configura o layout para wide (largura total da página)
# st.set_page_config(layout="wide")

def show_vencer_30_60():
    st.title('Contratos a Vencer em 30 a 60 Dias')

    # Obter dados dos contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        vencer_30_60 = []
        for contract in contracts:
            vig_fim_date = datetime.strptime(contract[8], '%Y-%m-%d').date()
            dias_a_vencer = (vig_fim_date - today).days
            situacao_calculada = calculate_situation(dias_a_vencer)
            if situacao_calculada == 'Vencer 30 a 60 dias':
                vencer_30_60.append(
                    (
                        contract[0], contract[1], contract[2], contract[3], contract[4], contract[6], 
                        contract[7], contract[8], contract[9], dias_a_vencer, situacao_calculada, 
                        contract[11], contract[12]
                    )
                )
        
        df = pd.DataFrame(
            vencer_30_60, 
            columns=[
                'ID', 'Número do Processo', 'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Prazo Limite', 
                'Dias a Vencer', 'Situação', 'Aditivo', 'Próximo Passo'
            ]
        )
        st.write("## Contratos a Vencer em 30 a 60 Dias")
        st.dataframe(df)
    else:
        st.write("Nenhum contrato encontrado.")

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

# Chama a função show_vencer_30_60
show_vencer_30_60()
