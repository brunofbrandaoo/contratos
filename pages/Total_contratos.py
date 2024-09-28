import pandas as pd
import streamlit as st
from db import add_contract, update_contract, delete_contract, get_contracts, get_contract_by_id, add_aditivo, get_aditivos
from datetime import datetime, timedelta
import os
import uuid
from decimal import Decimal
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

url_base = st.secrets["general"]["url_base"]

def save_uploaded_file(uploaded_file):
    # Define o diretório temporário para salvar os arquivos
    save_directory = "uploads"  # Diretório onde os arquivos serão salvos
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)  # Cria o diretório se ele não existir

    # Gera um identificador único para o arquivo
    unique_id = str(uuid.uuid4())

    # Define o caminho completo do arquivo, incluindo o nome
    file_path = os.path.join(save_directory, f"{unique_id}_{uploaded_file.name}")

    # Salva o arquivo no diretório especificado
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Retorna o caminho do arquivo salvo
    return file_path

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer, passivel_renovacao):
    dias_vencer = max(0, dias_vencer)  # Garante que não decresça abaixo de 0
    if dias_vencer == 0:
        return 'Vencido'
    elif dias_vencer <= 60:
        return 'Renovar' if passivel_renovacao == 1 else 'Novo Processo'
    elif 60 < dias_vencer <= 90:
        return 'Vencer 60 a 90 dias'
    elif 90 < dias_vencer <= 120:
        return 'Vencer 90 a 120 dias'
    elif 120 < dias_vencer <= 180:
        return 'Vencer 120 a 180 dias'
    else:
        return 'Vigente'

# Função para aplicar cores com base na situação
def color_situation(val):
    color = {
        'Vencido': '#343a40',
        'Renovar': '#ff0000',
        'Novo Processo': '#ff0000',
        'Vencer 60 a 90 dias': '#fe843d',
        'Vencer 90 a 120 dias': '#ffc107',
        'Vencer 120 a 180 dias': '#054f77',
        'Vigente': '#38761d'
    }.get(val, '')
    return f'background-color: {color}; color: white'

def save_uploaded_file(uploaded_file, contract_id):
    upload_directory = "uploads"
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)
    
    file_path = os.path.join(upload_directory, f"contract_{contract_id}.pdf")
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

@st.experimental_dialog(title="Adicionar Novo Contrato")
def add_contract_dialog():
    st.write("**Adicionar Novo Contrato**")
    
    # Inputs de texto e número
    numero_processo = st.text_input("Número do Processo")
    numero_contrato = st.text_input("Número do Contrato")
    fornecedor = st.text_input("Fornecedor do Contrato")
    objeto = st.text_input("Objeto")
    valor_contrato = st.number_input("Valor do Contrato", step=1000.00, min_value=0.0)
    vig_inicio = st.date_input("Vigência Início")
    vig_fim = st.date_input("Vigência Fim")
    passivel_renovacao = st.selectbox("Passível de Renovação", [0, 1], format_func=lambda x: "Sim" if x == 1 else "Não, Novo Processo")
    prazo_limite = st.radio("Prazo Limite (anos)", options=[1, 2, 3, 4, 5])

    # Inputs de seleção e texto
    modalidade = st.selectbox("Modalidade", ["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"])
    amparo_legal = st.selectbox("Amparo Legal", ["Lei 8.666/93", "Lei 14.133/21"])
    categoria = st.selectbox("Categoria", ["Bens", "Serviços comuns", "Serviços de Engenharia"])
    data_assinatura = st.date_input("Data de Assinatura")
    data_publicacao = st.date_input("Data de Publicação")
    observacao = st.text_area("Observação")
    gestor = st.text_input("Gestor")
    contato = st.text_input("Contato")
    setor = st.text_input("Setor")

    if st.button("Salvar Novo Contrato"):
        # Validação simples de valores negativos
        if valor_contrato < 0:
            st.error("O valor do contrato não pode ser negativo.")
        else:
            # Calcula dias a vencer
            dias_vencer = max(0, (vig_fim - datetime.today().date()).days)
            situacao_calculada = calculate_situation(dias_vencer, passivel_renovacao)

            # Conversões necessárias para o banco de dados
            valor_contrato_decimal = Decimal(valor_contrato)  # Garantir que seja decimal
            vig_inicio_str = vig_inicio.strftime('%Y-%m-%d')  # Converter datas para string
            vig_fim_str = vig_fim.strftime('%Y-%m-%d')
            data_assinatura_str = data_assinatura.strftime('%Y-%m-%d')
            data_publicacao_str = data_publicacao.strftime('%Y-%m-%d')

            # Função que insere no banco
            add_contract(
                numero_processo, numero_contrato, fornecedor, objeto, valor_contrato_decimal, 
                vig_inicio_str, vig_fim_str, prazo_limite, modalidade, amparo_legal, categoria, 
                data_assinatura_str, data_publicacao_str, gestor, contato, setor, observacao, 
                passivel_renovacao
            )

            st.session_state.show_add_contract_dialog = False
            st.rerun()

@st.experimental_dialog(title="Adicionar Aditivo")
def add_aditivo_dialog(contract_id, numero_contrato, vig_fim_atual, valor_contrato_atual):
    st.write(f"**Adicionar Aditivo ao Contrato:** {numero_contrato}")
    
    novo_vig_fim = st.date_input("Nova Data de Vigência Final", value=datetime.strptime(vig_fim_atual, '%Y-%m-%d').date())
    novo_valor_contrato = st.number_input("Valor do Aditivo", value=float(valor_contrato_atual), format="%.2f")

    # Novos campos para o aditivo
    codigo_aditivo = st.text_input("Número do Aditivo")
    objeto_aditivo = st.text_input("Objeto do Aditivo")
    data_assinatura_aditivo = st.date_input("Data de Assinatura do Aditivo")
    data_publicacao_aditivo = st.date_input("Data de Publicação do Aditivo")
    
    if st.button("Salvar Aditivo"):
        contract = get_contract_by_id(contract_id)
        if contract:
            try:
                aditivo = contract[11]  # Assumindo que o índice 11 corresponde ao campo 'aditivo'
                novo_aditivo = int(aditivo) + 1 if aditivo and aditivo.isdigit() else 1
            except (ValueError, AttributeError):
                novo_aditivo = 1
                st.warning(f"Valor inválido para aditivo: {aditivo}. Definindo como 1.")
            
            hoje = datetime.today().date()
            novos_dias_vencer = max(0, (novo_vig_fim - hoje).days)
            
            update_contract(
                contract_id,
                contract[1],  # numero_processo
                contract[2],  # numero_contrato
                contract[3],  # fornecedor
                contract[4],  # objeto
                calculate_situation(novos_dias_vencer, contract[25]),  # nova situação
                novo_valor_contrato,
                contract[7],  # vig_inicio
                novo_vig_fim,
                contract[9],  # prazo_limite
                novos_dias_vencer,
                str(novo_aditivo),
                contract[12],  # prox_passo
                contract[13],  # modalidade
                contract[14],  # amparo_legal
                contract[15],  # categoria
                contract[16],  # data_assinatura
                contract[17],  # data_publicacao
                contract[18],  # itens
                contract[19],  # quantidade
                contract[20],  # gestor
                contract[21],  # contato
                contract[22],  # setor
                contract[23],  # observacao
                contract[24],  # movimentacao
                contract[25]   # passivel_renovacao
            )
            
            # Adiciona o aditivo sem o campo data_aditivo
            add_aditivo(contract_id, novo_aditivo, novo_vig_fim, novo_valor_contrato, codigo_aditivo, objeto_aditivo, data_assinatura_aditivo, data_publicacao_aditivo)
            
            st.success("Aditivo adicionado com sucesso!")
            st.session_state.show_add_aditivo_dialog = False
            st.rerun()


@st.experimental_dialog(title="Editar Contrato")
def edit_contract_dialog(contract):
    (
        id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
        dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, 
        quantidade, gestor, contato, setor, observacao, movimentacao, passivel_renovacao
    ) = contract
    st.write(f"**Editando Contrato:** {numero_contrato}")
    novo_numero_processo = st.text_input("Número do Processo", value=numero_processo, key=f"numero_processo_{id}")
    novo_numero_contrato = st.text_input("Número do Contrato", value=numero_contrato, key=f"numero_contrato_{id}")
    novo_fornecedor = st.text_input("Fornecedor do Contrato", value=fornecedor, key=f"fornecedor_{id}")
    novo_objeto = st.text_input("Objeto", value=objeto, key=f"objeto_{id}")
    novo_valor_contrato = st.number_input("Valor do Contrato", value=valor_contrato, step=1000.00, min_value=0.0, key=f"valor_contrato_{id}")
    novo_vig_inicio = st.date_input("Vigência Início", value=datetime.strptime(vig_inicio, "%Y-%m-%d").date(), key=f"vig_inicio_{id}")
    novo_vig_fim = st.date_input("Vigência Fim", value=datetime.strptime(vig_fim, "%Y-%m-%d").date(), key=f"vig_fim_{id}")
    novo_prazo_limite = st.radio("Prazo Limite (anos)", options=[1, 2, 3, 4, 5], index=prazo_limite - 1, key=f"prazo_limite_{id}")
    novo_aditivo = int(aditivo) if aditivo.isdigit() else 0

    nova_modalidade = st.selectbox("Modalidade", ["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"], index=["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"].index(modalidade), key=f"modalidade_{id}")
    novo_amparo_legal = st.selectbox("Amparo Legal", ["Lei 8.666/93", "Lei 14.133/21"], index=["Lei 8.666/93", "Lei 14.133/21"].index(amparo_legal), key=f"amparo_legal_{id}")
    nova_categoria = st.selectbox("Categoria", ["Bens", "Serviços comuns", "Serviços de Engenharia"], index=["Bens", "Serviços comuns", "Serviços de Engenharia"].index(categoria), key=f"categoria_{id}")
    nova_data_assinatura = st.date_input("Data de Assinatura", value=datetime.strptime(data_assinatura, "%Y-%m-%d").date() if data_assinatura else None, key=f"data_assinatura_{id}")
    nova_data_publicacao = st.date_input("Data de Publicação", value=datetime.strptime(data_publicacao, "%Y-%m-%d").date() if data_publicacao else None, key=f"data_publicacao_{id}")
    novo_movimentacao = st.text_area("Movimentação", value=movimentacao, key=f"movimentacao_{id}")
    novo_gestor = st.text_input("Gestor", value=gestor, key=f"gestor_{id}")
    novo_contato = st.text_input("Contato", value=contato, key=f"contato_{id}")
    novo_setor = st.text_input("Setor", value=setor, key=f"setor_{id}")

    novos_dias_vencer = max(0, (novo_vig_fim - datetime.today().date()).days)

    if st.button("Salvar Alterações", key=f"salvar_{id}"):
        situacao_calculada = calculate_situation(novos_dias_vencer, passivel_renovacao)
        update_contract(
            id, novo_numero_processo, novo_numero_contrato, novo_fornecedor, novo_objeto, situacao_calculada, novo_valor_contrato, novo_vig_inicio, novo_vig_fim, 
            novo_prazo_limite, novos_dias_vencer, novo_aditivo, "", nova_modalidade, novo_amparo_legal, nova_categoria, nova_data_assinatura, 
            nova_data_publicacao, "", 0, novo_gestor, novo_contato, novo_setor, "", novo_movimentacao, passivel_renovacao
        )
        st.success("Contrato atualizado com sucesso!")
        st.session_state.show_edit_contract_dialog = False
        st.rerun()


def show_aditivo_details(contract_id):
    aditivos = get_aditivos(contract_id)
    if aditivos:
        # Espaçamento superior para separar a seção
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #f7f9fc; padding: 20px; border-radius: 12px; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #4a5568; text-align: center; margin-bottom: 20px; font-size: 24px;">Detalhes dos Aditivos</h3>
        """, unsafe_allow_html=True)

        for i, aditivo in enumerate(aditivos, 1):
            st.markdown(f"""
            <div style="
                background-color: #ffffff; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); 
                margin-bottom: 20px; 
                display: flex; 
                flex-wrap: wrap; 
                justify-content: space-between; 
                align-items: flex-start;
                font-size: 16px;
                color: #2d3748;
                position: relative;
            ">
                <div style="
                    position: absolute;
                    top: -15px;
                    left: -15px;
                    width: 40px;
                    height: 40px;
                    background-color: #343a40;
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-weight: bold;
                    font-size: 18px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                ">
                    {aditivo[2]}
                </div>
                <div style="flex: 1; min-width: 250px; margin-right: 20px;">
                    <p style="margin: 0; font-size: 18px;"><strong>Número do Aditivo:</strong> {aditivo[5]}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Data de Vigência Final do Aditivo:</strong> {aditivo[3]}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Valor do aditivo:</strong> R$ {aditivo[4]:.2f}</p>
                </div>
                <div style="flex: 1; min-width: 250px; margin-left: 20px;">
                    <p style="margin: 0; font-size: 18px;"><strong>Objeto do Aditivo:</strong> {aditivo[6]}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Data de Assinatura do Aditivo:</strong> {aditivo[7]}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Data de Publicação do Aditivo:</strong> {aditivo[8]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Fechamento do contêiner principal
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Este contrato ainda não possui aditivos.")


def contract_details_page(contract_id):
    contract = get_contract_by_id(contract_id)
    if contract:
        (
            id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
            dias_vencer, aditivo, modalidade, amparo_legal, categoria, data_assinatura, 
            data_publicacao, gestor, contato, setor, movimentacao, passivel_renovacao
        ) = contract
        passivel_renovacao_texto = "Sim" if passivel_renovacao == 1 else "Não"
        situacao = calculate_situation(dias_vencer, passivel_renovacao)

        st.markdown(f"""
<div style="background-color: #f8f9fa; padding: 30px; border-radius: 12px; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);">
    <h2 style="color: #343a40; text-align: center; margin-bottom: 30px; font-size: 28px;">Detalhes do Contrato {numero_contrato}</h2>
    <div style="display: flex; gap: 40px; justify-content: space-between;">
        <!-- Coluna da esquerda -->
        <div style="flex: 1; display: flex; flex-direction: column; gap: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Número do Contrato:</strong> {numero_contrato}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Objeto:</strong> {objeto}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Fornecedor:</strong> {fornecedor}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Valor do Contrato:</strong> {valor_contrato}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Vigência Início:</strong> {vig_inicio}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Vigência Fim:</strong> {vig_fim}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Prazo Limite (anos):</strong> {prazo_limite}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Data de Assinatura:</strong> {data_assinatura}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Data de Publicação:</strong> {data_publicacao}
            </div>
            <div style="{color_situation(situacao)}; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Situação:</strong> {situacao}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Aditivo:</strong> {aditivo}
            </div>
        </div>
        <!-- Coluna da direita -->
        <div style="flex: 1; display: flex; flex-direction: column; gap: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Número processo:</strong> {numero_processo}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Modalidade:</strong> {modalidade}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Amparo Legal:</strong> {amparo_legal}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Categoria:</strong> {categoria}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Movimentação:</strong> {movimentacao}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Gestor:</strong> {gestor}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Contato:</strong> {contato}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Setor:</strong> {setor}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

        # Botões na página de detalhes
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button(f"Editar Contrato {numero_contrato}", key=f"edit_{id}"):
                st.session_state['edit_contract'] = id
                edit_contract_dialog(contract)
        with col2:
            if st.button(f"Remover Contrato {numero_contrato}", key=f"remove_{id}"):
                delete_contract(id)
                st.rerun()
        with col3:
            if st.button(f"Adicionar Aditivo {numero_contrato}", key=f"add_aditivo_{id}"):
                st.session_state['show_add_aditivo_dialog'] = id
                add_aditivo_dialog(id, numero_contrato, vig_fim, valor_contrato)
        with col4:
            uploaded_file = st.file_uploader("Anexos", type="pdf")
            if uploaded_file is not None:
                # Salva o arquivo usando um identificador único
                file_path = save_uploaded_file(uploaded_file, contract_id)
                st.success(f"Arquivo PDF anexado com sucesso: {file_path}")

                # Botão para download do arquivo salvo
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Baixar Arquivo",
                        data=f,
                        file_name=uploaded_file.name,
                        mime="application/pdf"
                    )

        show_aditivo_details(contract_id)

def show_planilha():
    st.title('Planilha de Contratos')

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title('Gerenciamento de Contratos')
    with col2:
        if st.button('Adicionar Contrato'):
            st.session_state.show_add_contract_dialog = True
            add_contract_dialog()

    pesquisa_numero = st.text_input("Pesquisar Número do Contrato")

    if st.button("Pesquisar"):
        st.session_state['pesquisa_numero'] = pesquisa_numero

    contracts = get_contracts()
    if 'pesquisa_numero' in st.session_state:
        contracts = [contract for contract in contracts if contract[2] == st.session_state['pesquisa_numero']]

    if contracts:
        today = datetime.today().date()
        transformed_contracts = []
        for contract in contracts:
            # Verifica se o valor de contract[8] é uma string e não None ou int
            if isinstance(contract[8], str):
                try:
                    vig_fim_date = datetime.strptime(contract[8], '%Y-%m-%d').date()
                except ValueError:
                    vig_fim_date = today  # Se a conversão falhar, use a data de hoje como fallback
            else:
                vig_fim_date = today  # Se não for string, usa a data de hoje

            dias_a_vencer = max(0, (vig_fim_date - today).days)
            passivel_renovacao = contract[18]  
            situacao_calculada = calculate_situation(dias_a_vencer, passivel_renovacao)
            link_detalhes = f"{url_base}/Total_contratos?page=details&contract_id={contract[0]}"
            transformed_contracts.append(
                (
                    contract[2], contract[3], contract[4], 
                    contract[5], contract[6], contract[7], dias_a_vencer, situacao_calculada, 
                    contract[17], link_detalhes
                )
            )
        
        df = pd.DataFrame(
            transformed_contracts, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 'Movimentação', 'Detalhes'
            ]
        )
        
        st.dataframe(
            df.style.applymap(color_situation, subset=['Situação']),
            column_config={
                "Detalhes": st.column_config.LinkColumn(
                    "Detalhes",
                    help="Clique para ver os detalhes do contrato",
                    display_text="Detalhar"
                )
            },
            hide_index=True,
        )

        st.json(contracts[0])
    else:
        st.write("Nenhum contrato encontrado.")

# Lógica para decidir qual página exibir
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["main"])[0]

if page == "details":
    contract_id = query_params.get("contract_id", [None])[0]
    if contract_id:
        contract_details_page(contract_id)
else:
    show_planilha()
