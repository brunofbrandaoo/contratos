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

def show_vencer_120_180():
    st.title('Contratos a Vencer em 120 a 180 Dias')

    # Obter dados dos contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        vencer_120_180 = []
        for contract in contracts:
            # Ajuste para converter a data de vigência final (vig_fim) corretamente
            if isinstance(contract[7], str):
                vig_fim_date = datetime.strptime(contract[7], '%Y-%m-%d').date()
            elif isinstance(contract[7], datetime):
                vig_fim_date = contract[7].date()
            else:
                vig_fim_date = contract[7]

            # Calcular dias a vencer
            dias_a_vencer = (vig_fim_date - today).days

            # Calcular a situação com base nos dias a vencer
            situacao_calculada = calculate_situation(dias_a_vencer)
            
            # Adicionar contratos que estão na situação "Vencer 120 a 180 dias"
            if situacao_calculada == 'Vencer 120 a 180 dias':
                link_detalhes = f"{url_base}/Total_contratos?page=details&contract_id={contract[0]}"

                # Formatação das datas e valores
                vig_inicio_formatada = datetime.strptime(contract[6], '%Y-%m-%d').strftime('%d/%m/%Y') if isinstance(contract[6], str) else contract[6].strftime('%d/%m/%Y')
                vig_fim_formatada = vig_fim_date.strftime('%d/%m/%Y')
                valor_formatado = f"R$ {float(contract[5]):,.1f}"  # Formata com uma casa decimal e separador de milhar

                vencer_120_180.append(
                    (
                        contract[2],  # Número do Contrato
                        contract[3],  # Fornecedor
                        contract[4],  # Objeto
                        valor_formatado,  # Valor do Contrato formatado
                        vig_inicio_formatada,  # Vigência Início formatada
                        vig_fim_formatada,  # Vigência Fim formatada
                        contract[8],  # Prazo Limite
                        dias_a_vencer,  # Dias a Vencer
                        situacao_calculada,  # Situação
                        contract[18],  # Aditivo
                        contract[16],  # Movimentação
                        link_detalhes  # Link para detalhes
                    )
                )

        # Exibir os dados na tabela usando pandas DataFrame
        df = pd.DataFrame(
            vencer_120_180, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Prazo Limite', 
                'Dias a Vencer', 'Situação', 'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )

        # Aplicar cor personalizada para a coluna 'Situação'
        def color_situation(val):
            color = 'background-color: #054f77; color: white' if val == 'Vencer 120 a 180 dias' else ''
            return color

        # Aplicar o estilo condicional para a coluna de situação
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

# Função para calcular a situação do contrato com base no número de dias a vencer
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

# Chama a função show_vencer_120_180 para exibir os contratos
show_vencer_120_180()
