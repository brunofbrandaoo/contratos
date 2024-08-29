# planilha.py

import pandas as pd
import streamlit as st
from db import init_db, add_contract, update_contract, delete_contract, get_contracts, get_contract_by_id, add_aditivo, get_aditivos
from datetime import datetime, timedelta
import os

# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")
st.sidebar.header("Navegação")
st.sidebar.page_link("Dashboard.py", label="Dashboard", icon="📊")
st.sidebar.page_link("pages/Total_contratos.py", label="Planilhas", icon="📈")
st.sidebar.page_link("pages/Vencer_30_60.py", label="Contratos com vencimento de 30 a 60 dias", icon="🟥")
st.sidebar.page_link("pages/Vencimento_60_a_90.py", label="Contratos com vencimento de 60 a 90 dias", icon="🟧")
st.sidebar.page_link("pages/vencer_90_120.py", label="Contratos com vencimento de 90 a 120 dias", icon="🟨")
st.sidebar.page_link("pages/vencer_120_180.py", label="Contratos com vencimento de 120 a 180 dias", icon="🟦")
st.sidebar.page_link("pages/Contratos_vencidos.py", label="Contratos vencidos", icon="⬛")

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer, passivel_renovacao):
    if dias_vencer <= 0:
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
        'Novo Processo': '#ff0000',  # Adiciona a mesma cor para "Novo Processo"
        'Vencer 60 a 90 dias': '#fe843d',
        'Vencer 90 a 120 dias': '#ffc107',
        'Vencer 120 a 180 dias': '#054f77',
        'Vigente': '#38761d'
    }.get(val, '')
    return f'background-color: {color}; color: white'

def save_uploaded_file(uploaded_file, contract_id):
    # Define o diretório para salvar os arquivos
    upload_directory = "uploads"
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)
    
    # Define o caminho do arquivo
    file_path = os.path.join(upload_directory, f"contract_{contract_id}.pdf")
    
    # Salva o arquivo
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

@st.experimental_dialog(title="Adicionar Novo Contrato")
def add_contract_dialog():
    st.write("**Adicionar Novo Contrato**")
    numero_processo = st.text_input("Número do Processo")
    numero_contrato = st.text_input("Número do Contrato")
    fornecedor = st.text_input("Fornecedor do Contrato")
    objeto = st.text_input("Objeto")
    valor_contrato = st.number_input("Valor do Contrato", step=1000.00, min_value=0.0)
    vig_inicio = st.date_input("Vigência Início")
    vig_fim = st.date_input("Vigência Fim")
    passivel_renovacao = st.selectbox("Passível de Renovação", [0, 1], format_func=lambda x: "Sim" if x == 1 else "Não, Novo Processo")
    prazo_limite = st.radio("Prazo Limite (anos)", options=[1, 2, 3, 4, 5])

    # Novos campos com selectbox
    modalidade = st.selectbox("Modalidade", ["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"])
    amparo_legal = st.selectbox("Amparo Legal", ["Lei 8.666/93", "Lei 14.133/21"])
    categoria = st.selectbox("Categoria", ["Bens", "Serviços comuns", "Serviços de Engenharia"])
    data_assinatura = st.date_input("Data de Assinatura")
    data_publicacao = st.date_input("Data de Publicação")
    itens = st.text_input("Itens") 
    quantidade = st.number_input("Quantidade de itens", min_value=0, step=1)
    # Novos campos de observacao e movimentacao
    observacao = st.text_area("Observação")
    movimentacao = st.text_area("Movimentação")
    gestor = st.text_input("Gestor")
    contato = st.text_input("Contato")
    setor = st.text_input("Setor")

    if st.button("Salvar Novo Contrato"):
        if valor_contrato < 0:
            st.error("O valor do contrato não pode ser negativo.")
        elif quantidade < 0:
            st.error("A quantidade de itens não pode ser negativa.")
        else:
            dias_vencer = (vig_fim - datetime.today().date()).days
            situacao_calculada = calculate_situation(dias_vencer, passivel_renovacao)
            add_contract(
                numero_processo, numero_contrato, fornecedor, objeto, situacao_calculada, valor_contrato, vig_inicio, vig_fim, 
                prazo_limite, dias_vencer, 0, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, 
                itens, quantidade, gestor, contato, setor, observacao, movimentacao, passivel_renovacao
            )
            st.session_state.show_add_contract_dialog = False
            st.rerun()

@st.experimental_dialog(title="Adicionar Aditivo")
def add_aditivo_dialog(contract_id, numero_contrato, vig_fim_atual, valor_contrato_atual):
    st.write(f"**Adicionar Aditivo ao Contrato:** {numero_contrato}")
    
    novo_vig_fim = st.date_input("Nova Data Final", value=datetime.strptime(vig_fim_atual, '%Y-%m-%d').date())
    novo_valor_contrato = st.number_input("Novo Valor do Contrato", value=float(valor_contrato_atual), format="%.2f")
    data_aditivo = st.date_input("Data do Aditivo", value=datetime.today())
    
    if st.button("Salvar Aditivo"):
        contract = get_contract_by_id(contract_id)
        if contract:
            try:
                aditivo = contract[11]  # Assumindo que o índice 11 corresponde ao campo 'aditivo'
                novo_aditivo = int(aditivo) + 1 if aditivo and aditivo.isdigit() else 1
            except (ValueError, AttributeError):
                novo_aditivo = 1
                st.warning(f"Valor inválido para aditivo: {aditivo}. Definindo como 1.")
            
            # Calcular novos dias a vencer
            hoje = datetime.today().date()
            novos_dias_vencer = (novo_vig_fim - hoje).days
            
            # Atualizar o contrato
            update_contract(
                contract_id,
                contract[1],  # numero_processo
                contract[2],  # numero_contrato
                contract[3],  # fornecedor
                contract[4],  # objeto
                calculate_situation(novos_dias_vencer),  # nova situação
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
            
            # Adicionar o novo aditivo
            add_aditivo(contract_id, novo_aditivo, novo_vig_fim, novo_valor_contrato, data_aditivo)
            
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

    # Novos campos no formulário de edição
    nova_modalidade = st.selectbox("Modalidade", ["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"], index=["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"].index(modalidade), key=f"modalidade_{id}")
    novo_amparo_legal = st.selectbox("Amparo Legal", ["Lei 8.666/93", "Lei 14.133/21"], index=["Lei 8.666/93", "Lei 14.133/21"].index(amparo_legal), key=f"amparo_legal_{id}")
    nova_categoria = st.selectbox("Categoria", ["Bens", "Serviços comuns", "Serviços de Engenharia"], index=["Bens", "Serviços comuns", "Serviços de Engenharia"].index(categoria), key=f"categoria_{id}")
    nova_data_assinatura = st.date_input("Data de Assinatura", value=datetime.strptime(data_assinatura, "%Y-%m-%d").date() if data_assinatura else None, key=f"data_assinatura_{id}")
    nova_data_publicacao = st.date_input("Data de Publicação", value=datetime.strptime(data_publicacao, "%Y-%m-%d").date() if data_publicacao else None, key=f"data_publicacao_{id}")
    novos_itens = st.text_input("Itens", value=itens, key=f"itens_{id}")
    nova_quantidade = st.number_input("Quantidade", value=quantidade, step=1, key=f"quantidade_{id}")
    # Novos campos de observacao e movimentacao
    nova_observacao = st.text_area("Observação", value=observacao, key=f"observacao_{id}")
    novo_movimentacao = st.text_area("movimentacao", value=movimentacao, key=f"movimentacao_{id}")
    novo_gestor = st.text_input("Gestor", value=gestor, key=f"gestor_{id}")
    novo_contato = st.text_input("Contato", value=contato, key=f"contato_{id}")
    novo_setor = st.text_input("Setor", value=setor, key=f"setor_{id}")

    novo_prox_passo = st.text_area("Próximo Passo", value=prox_passo, key=f"prox_passo_{id}")

    novos_dias_vencer = (novo_vig_fim - datetime.today().date()).days

    if st.button("Salvar Alterações", key=f"salvar_{id}"):
        situacao_calculada = calculate_situation(novos_dias_vencer, passivel_renovacao)
        update_contract(
            id, novo_numero_processo, novo_numero_contrato, novo_fornecedor, novo_objeto, situacao_calculada, novo_valor_contrato, novo_vig_inicio, novo_vig_fim, 
            novo_prazo_limite, novos_dias_vencer, novo_aditivo, novo_prox_passo, nova_modalidade, novo_amparo_legal, nova_categoria, nova_data_assinatura, 
            nova_data_publicacao, novos_itens, nova_quantidade, novo_gestor, novo_contato, novo_setor, nova_observacao, novo_movimentacao
        )
        st.success("Contrato atualizado com sucesso!")
        st.session_state.show_edit_contract_dialog = False
        st.rerun()

def show_aditivo_details(contract_id):
    aditivos = get_aditivos(contract_id)
    if aditivos:
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #e9ecef; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #495057; text-align: center; margin-bottom: 20px;">Detalhes dos Aditivos</h3>
        """, unsafe_allow_html=True)

        for aditivo in aditivos:
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); margin-bottom: 15px;">
                <strong>Número do Aditivo:</strong> {aditivo[2]}<br>
                <strong>Nova Data de Vigência:</strong> {aditivo[3]}<br>
                <strong>Novo Valor do Contrato:</strong> R$ {aditivo[4]:.2f}<br>
                <strong>Data do Aditivo:</strong> {aditivo[5]}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Este contrato ainda não possui aditivos.")

def contract_details_page(contract_id):
    contract = get_contract_by_id(contract_id)
    if contract:
        (
            id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
            dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, 
            data_publicacao, itens, quantidade, gestor, contato, setor, observacao, movimentacao, passivel_renovacao
        ) = contract

        passivel_renovacao_texto = "Sim" if passivel_renovacao == 1 else "Não"

        st.markdown(f"""
<div style="background-color: #f8f9fa; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <h2 style="color: #343a40; text-align: center; margin-bottom: 20px;">Detalhes do Contrato {numero_contrato}</h2>
    <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: space-between;">
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong style="font-size: 24px;">Número do Contrato:</strong> {numero_contrato}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Fornecedor:</strong> {fornecedor}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Objeto:</strong> {objeto}
        </div>
        <div style="{color_situation(situacao)}; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Situação:</strong> {situacao}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Vigência Início:</strong> {vig_inicio}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Valor do Contrato:</strong> {valor_contrato}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Vigência Fim:</strong> {vig_fim}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Prazo Limite (anos):</strong> {prazo_limite}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Aditivo:</strong> {aditivo}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Passível para renovação:</strong> {passivel_renovacao_texto}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Modalidade:</strong> {modalidade}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Amparo Legal:</strong> {amparo_legal}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Categoria:</strong> {categoria}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Data de Assinatura:</strong> {data_assinatura}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Data de Publicação:</strong> {data_publicacao}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Itens:</strong> {itens}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Quantidade:</strong> {quantidade}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Observação:</strong> {observacao}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>movimentacao:</strong> {movimentacao}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Gestor:</strong> {gestor}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Contato:</strong> {contato}
        </div>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); width: 48%;">
            <strong>Setor:</strong> {setor}
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
            uploaded_file = st.file_uploader(f"Anexos", type="pdf", key=f"upload_{id}")
            if uploaded_file is not None:
                file_path = save_uploaded_file(uploaded_file, id)
                st.success(f"Arquivo PDF anexado com sucesso: {file_path}")

        show_aditivo_details(contract_id)

def show_planilha():
    st.title('Planilha de Contratos')

    # Inicializar banco de dados
    init_db()

    # Botões em linha abaixo do título
    col1, col2 = st.columns([3, 1])  # Ajustar a proporção das colunas conforme necessário
    with col1:
        st.title('Gerenciamento de Contratos')
    with col2:
        if st.button('Adicionar Contrato'):
            st.session_state.show_add_contract_dialog = True
            add_contract_dialog()

    pesquisa_numero = st.text_input("Pesquisar Número do Contrato")

    # Botão de pesquisa
    if st.button("Pesquisar"):
        st.session_state['pesquisa_numero'] = pesquisa_numero

    # Exibir contratos
    contracts = get_contracts()
    if 'pesquisa_numero' in st.session_state:
        contracts = [contract for contract in contracts if contract[2] == st.session_state['pesquisa_numero']]

    if contracts:
        today = datetime.today().date()
        transformed_contracts = []
        for contract in contracts:
            vig_fim_date = datetime.strptime(contract[8], '%Y-%m-%d').date()
            dias_a_vencer = (vig_fim_date - today).days
            passivel_renovacao = contract[25]  # Considerando que 'passivel_renovacao' esteja na posição 25
            situacao_calculada = calculate_situation(dias_a_vencer, passivel_renovacao)
            link_detalhes = f"http://localhost:8501/Total_contratos?page=details&contract_id={contract[0]}"
            transformed_contracts.append(
                (
                    contract[2], contract[3], contract[4], 
                    contract[6], contract[7], contract[8], dias_a_vencer, situacao_calculada, 
                    contract[11], contract[24], link_detalhes
                )
            )
        
        df = pd.DataFrame(
            transformed_contracts, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 
                'Aditivo', 'Movimentação', 'Detalhes'
            ]
        )
        
        # Configurar a coluna de links
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
