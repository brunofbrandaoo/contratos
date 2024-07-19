import streamlit as st
from db import get_contracts
from datetime import datetime
import pandas as pd

def show_filtered_contracts(situation):
    st.title(f'Contratos {situation}')
    contracts = get_contracts()
    if contracts:
        today = datetime.today().date()
        contracts = [(contract[0], contract[1], contract[2], contract[3], contract[4], contract[5], contract[6], contract[7], contract[8], contract[9], (datetime.strptime(contract[8], '%Y-%m-%d').date() - today).days, situation) for contract in contracts]
        filtered_contracts = [contract for contract in contracts if contract[11] == situation]
        df = pd.DataFrame(filtered_contracts, columns=["ID", "Nome", "Valor", "Data Início", "Data Fim", "Cliente", "Descrição", "Status", "Data Fim", "Dias Restantes", "Situação", "Status Calculado"])
        st.dataframe(df)
    else:
        st.write("Nenhum contrato encontrado.")

situation = "total"
show_filtered_contracts(situation)
