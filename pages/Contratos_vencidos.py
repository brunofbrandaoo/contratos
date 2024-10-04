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

    url_base = st.secrets["general"]["url_base"]

    # Obter dados dos contratos
    contracts = get_contracts()

    if contracts:
        today = datetime.today().date()
        vencidos = []
        for contract in contracts:
            # Ajuste para converter a data de vigência final (vig_fim) corretamente
            if isinstance(contract[7], str):
                vig_fim_date = datetime.strptime(contract[7], '%Y-%m-%d').date()
            elif isinstance(contract[7], datetime):
                vig_fim_date = contract[7].date()
            else:
                vig_fim_date = contract[7]

            # Calcular dias a vencer (pode ser negativo se já estiver vencido)
            dias_a_vencer = (vig_fim_date - today).days

            # Determinar a situação do contrato
            situacao_calculada = calculate_situation(dias_a_vencer)

            # Definir `dias_a_vencer` como 0 se o valor for negativo, apenas para exibição
            dias_a_vencer_exibicao = max(0, dias_a_vencer)

            # Adicionar apenas os contratos na situação "Vencido"
            if situacao_calculada == 'Vencido':
                link_detalhes = f"{url_base}/Total_contratos?page=details&contract_id={contract[0]}"

                # Formatação das datas e valores
                vig_inicio_formatada = datetime.strptime(contract[6], '%Y-%m-%d').strftime('%d/%m/%Y') if isinstance(contract[6], str) else contract[6].strftime('%d/%m/%Y')
                vig_fim_formatada = vig_fim_date.strftime('%d/%m/%Y')
                valor_formatado = f"R$ {float(contract[5]):,.1f}"  # Formata com uma casa decimal e separador de milhar

                vencidos.append(
                    (
                        contract[2],  # Número do Contrato
                        contract[3],  # Fornecedor
                        contract[4],  # Objeto
                        valor_formatado,  # Valor do Contrato formatado
                        vig_inicio_formatada,  # Vigência Início formatada
                        vig_fim_formatada,  # Vigência Fim formatada
                        dias_a_vencer_exibicao,  # Exibir 0 para contratos vencidos
                        situacao_calculada,  # Situação
                        contract[19],  # Aditivo
                        contract[16],  # Movimentação
                        link_detalhes  # Link para detalhes
                    )
                )

        # Exibir os dados na tabela usando pandas DataFrame
        df = pd.DataFrame(
            vencidos, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 
                'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )

        # Aplicar cor preta para todas as células da coluna Situação onde a situação é "Vencido"
        def color_situation(val):
            color = 'background-color: black; color: white' if val == 'Vencido' else ''
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

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer):
    # Se o número de dias for menor que zero, o contrato está vencido
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

# Chama a função show_contratos_vencidos
show_contratos_vencidos()
