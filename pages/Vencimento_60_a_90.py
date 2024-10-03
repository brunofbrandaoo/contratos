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

# Função principal para exibir contratos a vencer em 60 a 90 dias
def show_vencer_60_90():
    st.title('Contratos a Vencer em 60 a 90 Dias')

    # Obter dados dos contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        vencer_60_90 = []

        for contract in contracts:
            # Verificar o tipo de `contract[7]` e converter para `datetime.date` se necessário
            if isinstance(contract[7], str):
                vig_fim_date = datetime.strptime(contract[7], '%Y-%m-%d').date()
            elif isinstance(contract[7], datetime):
                vig_fim_date = contract[7].date()
            else:
                vig_fim_date = contract[7]  # Caso já seja um `datetime.date`

            # Calcular o número de dias a vencer e definir como zero se for menor que 0
            dias_a_vencer = max(0, (vig_fim_date - today).days)

            # Calcular a situação com base nos dias a vencer
            situacao_calculada = calculate_situation(dias_a_vencer)
            
            # Adicionar apenas contratos que estão na situação "Vencer 60 a 90 dias"
            if situacao_calculada == 'Vencer 60 a 90 dias':
                link_detalhes = f"{url_base}/Total_contratos?page=details&contract_id={contract[0]}"

                # Formatação das datas e valores
                vig_inicio_formatada = datetime.strptime(contract[6], '%Y-%m-%d').strftime('%d/%m/%Y') if isinstance(contract[6], str) else contract[6].strftime('%d/%m/%Y')
                vig_fim_formatada = vig_fim_date.strftime('%d/%m/%Y')
                valor_formatado = f"R$ {float(contract[5]):,.1f}"  # Formata com uma casa decimal e separador de milhar

                vencer_60_90.append(
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
                        contract[19],  # Aditivo
                        contract[16],  # Movimentação
                        link_detalhes  # Link para detalhes
                    )
                )

        # Exibir os dados na tabela usando pandas DataFrame
        df = pd.DataFrame(
            vencer_60_90, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Prazo Limite', 
                'Dias a Vencer', 'Situação', 'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )

        # Aplicar cor laranja para células da coluna 'Situação' onde o valor é 'Vencer 60 a 90 dias'
        def color_situation(val):
            color = 'background-color: #fe843d; color: white' if val == 'Vencer 60 a 90 dias' else ''
            return color

        # Aplicar o estilo condicional
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

# Função para calcular a situação do contrato considerando o número de dias a vencer
def calculate_situation(dias_vencer):
    if dias_vencer <= 0:
        return 'Vencido'
    elif 1 <= dias_vencer < 60:
        return 'Renovar'
    elif 60 <= dias_vencer <= 90:
        return 'Vencer 60 a 90 dias'
    elif 90 < dias_vencer <= 120:
        return 'Vencer 90 a 120 dias'
    elif 120 < dias_vencer <= 180:
        return 'Vencer 120 a 180 dias'
    else:
        return 'Vigente'

# Chama a função show_vencer_60_90 para exibir os contratos
show_vencer_60_90()
