import streamlit as st
import pandas as pd
from db import get_contracts
from datetime import datetime

# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")
url_base = st.secrets["general"]["url_base"]

# Barra lateral de navegação
st.sidebar.header("Navegação")
st.sidebar.page_link("Dashboard.py", label="Dashboard", icon="📊")
st.sidebar.page_link("pages/Total_contratos.py", label="Planilhas", icon="📈")
st.sidebar.page_link("pages/Vencer_30_60.py", label="Contratos com vencimento de 0 a 60 dias", icon="🟥")
st.sidebar.page_link("pages/Vencimento_60_a_90.py", label="Contratos com vencimento de 60 a 90 dias", icon="🟧")
st.sidebar.page_link("pages/vencer_90_120.py", label="Contratos com vencimento de 90 a 120 dias", icon="🟨")
st.sidebar.page_link("pages/vencer_120_180.py", label="Contratos com vencimento de 120 a 180 dias", icon="🟦")
st.sidebar.page_link("pages/Contratos_vencidos.py", label="Contratos vencidos", icon="⬛")

st.logo(image="sudema.png", link=None)

# Função principal para exibir os contratos a vencer em até 60 dias
def show_vencer_30_60():
    st.title('Contratos a vencer em até 60 dias')

    # Obter dados dos contratos usando a query ajustada
    contracts = get_contracts()
    if contracts:
        today = datetime.today().date()
        renovar = []

        for contract in contracts:
            # Verificar o tipo de `vig_fim` e converter para `datetime.date` se for string
            if isinstance(contract[7], str):
                vig_fim_date = datetime.strptime(contract[7], '%Y-%m-%d').date()
            elif isinstance(contract[7], datetime):
                vig_fim_date = contract[7].date()
            else:
                vig_fim_date = contract[7]  # Caso já seja um `datetime.date`

            # Calcula o número de dias a vencer
            dias_a_vencer = (vig_fim_date - today).days
            passivel_renovacao = contract[18]  # Ajustado conforme o campo `passivel_renovacao` na query SQL

            # Calcula a situação do contrato com base no prazo e se é passível de renovação
            situacao_calculada = calculate_situation(dias_a_vencer, passivel_renovacao)

            # Adiciona à lista somente contratos que precisam ser renovados ou iniciar novo processo
            if situacao_calculada in ['Renovar', 'Novo Processo']:
                link_detalhes = f"{url_base}/Total_contratos?page=details&contract_id={contract[0]}"
                
                # Formatações das datas e valores
                vig_inicio_formatada = datetime.strptime(contract[6], '%Y-%m-%d').strftime('%d/%m/%Y') if isinstance(contract[6], str) else contract[6].strftime('%d/%m/%Y')
                vig_fim_formatada = vig_fim_date.strftime('%d/%m/%Y')
                valor_formatado = f"R$ {float(contract[5]):,.1f}"  # Formata com uma casa decimal e separador de milhar

                renovar.append(
                    (
                        contract[2], contract[3], contract[4], 
                        valor_formatado, vig_inicio_formatada, vig_fim_formatada, dias_a_vencer, situacao_calculada, 
                        contract[19], contract[16], link_detalhes  # Ajustados os índices dos campos `aditivo` e `movimentacao`
                    )
                )

        # Exibir os dados na tabela usando pandas DataFrame
        df = pd.DataFrame(
            renovar, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 
                'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )

        # Aplicar cor vermelha para células da coluna 'Situação' onde o valor é 'Renovar' ou 'Novo Processo'
        def color_situation(val):
            color = 'background-color: red; color: white' if val in ['Renovar', 'Novo Processo'] else ''
            return color

        styled_df = df.style.applymap(color_situation, subset=['Situação'])

        # Configurar a coluna de links e exibir a tabela formatada no Streamlit
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

# Chama a função show_vencer_30_60 para exibir os contratos
show_vencer_30_60()
