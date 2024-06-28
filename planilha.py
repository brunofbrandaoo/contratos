import streamlit as st
import pandas as pd
from db import get_contracts
from datetime import datetime

def show_planilha():
    st.title('Planilha de Contratos')

    # Exibir contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        contracts = [(contract[0], contract[1], contract[2], contract[3], datetime.strptime(contract[4], '%Y-%m-%d').date(), (datetime.strptime(contract[4], '%Y-%m-%d').date() - today).days, calculate_situation((datetime.strptime(contract[4], '%Y-%m-%d').date() - today).days)) for contract in contracts]
        df = pd.DataFrame(contracts, columns=['ID', 'Número', 'Fornecedor', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação'])
        st.write("## Dados dos Contratos")
        st.dataframe(df)
    else:
        st.write("Nenhum contrato encontrado.")

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer):
    if dias_vencer < 0:
        return 'Vencido'
    elif dias_vencer <= 30:
        return 'Renovar'
    else:
        return 'Vigente'


# # Função para calcular a situação do contrato
# def calculate_situation(dias_vencer):
#     if dias_vencer < 0:
#         return 'Vencido'
#     elif dias_vencer <= 30:
#         return 'Renovar'
#     else:
#         return 'Vigente'

# def show_planilha():
#     st.title('Planilha de Contratos')

#     # Exibir contratos
#     contracts = get_contracts()

#     if contracts:
#         today = datetime.today().date()
#         contracts = [(contract[0], contract[1], contract[2], contract[3], datetime.strptime(contract[4], '%Y-%m-%d').date(), (datetime.strptime(contract[4], '%Y-%m-%d').date() - today).days, calculate_situation((datetime.strptime(contract[4], '%Y-%m-%d').date() - today).days)) for contract in contracts]
#         df = pd.DataFrame(contracts, columns=['ID', 'Número', 'Fornecedor', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação'])
        
#         st.write("## Dados dos Contratos")

#         # Cabeçalhos das colunas
#         col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 2, 2, 2, 2, 2, 2])
#         with col1:
#             st.write("Selecione")
#         with col2:
#             st.write("ID")
#         with col3:
#             st.write("Número")
#         with col4:
#             st.write("Fornecedor")
#         with col5:
#             st.write("Vigência Início")
#         with col6:
#             st.write("Vigência Fim")
#         with col7:
#             st.write("Dias a Vencer")
#         with col8:
#             st.write("Situação")

#         # Dados das linhas
#         for index, row in df.iterrows():
#             col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 2, 2, 2, 2, 2, 2])
#             with col1:
#                 checkbox = st.checkbox("", key=f"checkbox_{index}")
#             with col2:
#                 st.write(row['ID'])
#             with col3:
#                 st.write(row['Número'])
#             with col4:
#                 st.write(row['Fornecedor'])
#             with col5:
#                 st.write(row['Vigência Início'])
#             with col6:
#                 st.write(row['Vigência Fim'])
#             with col7:
#                 st.write(row['Dias a Vencer'])
#             with col8:
#                 st.write(row['Situação'])

#             if checkbox:
#                 st.write("## Informações do Contrato")
#                 st.write(f"**Número do Contrato:** {row['Número']}")
#                 st.write(f"**Fornecedor do Contrato:** {row['Fornecedor']}")
#                 st.write(f"**Vigência Início:** {row['Vigência Início']}")
#                 st.write(f"**Vigência Fim:** {row['Vigência Fim']}")
#                 st.write(f"**Dias a Vencer:** {row['Dias a Vencer']}")
#                 st.write(f"**Situação:** {row['Situação']}")
#                 st.write("---")

#     else:
#         st.write("Nenhum contrato encontrado.")

# # Chamada da função para exibir a planilha (caso necessário)
# if __name__ == "__main__":
#     show_planilha()
