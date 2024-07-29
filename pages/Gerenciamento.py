import streamlit as st
from db import init_db, add_contract, update_contract, delete_contract, get_contracts, get_contract_by_id
from datetime import datetime, timedelta
import os

# Configura o layout para wide (largura total da página)
st.set_page_config(layout="wide")

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer):
    if dias_vencer < 0:
        return 'Vencido'
    elif dias_vencer <= 30:
        return 'Renovar'
    else:
        return 'Vigente'

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
    valor_contrato = st.number_input("Valor do Contrato", step=0.01)
    vig_inicio = st.date_input("Vigência Início")
    vig_fim = st.date_input("Vigência Fim")
    prazo_limite = vig_fim - timedelta(days=60)
    prox_passo = st.text_input("Próximo Passo")

    # Novos campos com selectbox
    modalidade = st.selectbox("Modalidade", ["dispensa", "inegibilidade", "pregao", "concorrencia", "Adesão a Ata"])
    amparo_legal = st.selectbox("Amparo Legal", ["Lei 8.666/93", "Lei 14.133/21"])
    categoria = st.selectbox("Categoria", ["compras", "serviços", "Obras"])
    data_assinatura = st.date_input("Data de Assinatura")
    data_publicacao = st.date_input("Data de Publicação")
    itens = st.text_input("Itens") 
    quantidade = st.number_input("Quantidade de itens", step=1)
    # Novos campos de observacao e acompanhamento
    observacao = st.text_input("Observação")
    acompanhamento = st.text_input("Acompanhamento")
    gestor = st.text_input("Gestor")
    contato = st.text_input("Contato")
    setor = st.text_input("Setor")

    if st.button("Salvar Novo Contrato"):
        dias_vencer = (vig_fim - datetime.today().date()).days
        situacao_calculada = calculate_situation(dias_vencer)
        add_contract(numero_processo, numero_contrato, fornecedor, objeto, situacao_calculada, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, 0, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento)
        st.session_state.show_add_contract_dialog = False
        st.rerun()

@st.experimental_dialog(title="Adicionar Aditivo")
def add_aditivo_dialog(contract_id, numero_contrato, vig_fim_atual):
    st.write(f"**Adicionar Aditivo ao Contrato:** {numero_contrato}")
    novo_vig_fim = st.date_input("Nova Data Final", value=vig_fim_atual)
    
    if st.button("Salvar Aditivo"):
        today = datetime.today().date()
        dias_vencer = (novo_vig_fim - today).days
        situacao_calculada = calculate_situation(dias_vencer)
        contract = get_contract_by_id(contract_id)
        if contract:
            (
                id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, 
                prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, 
                data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento
            ) = contract
            
            novo_aditivo = int(aditivo) + 1 if aditivo.isdigit() else 1
            
            update_contract(
                id,
                numero_processo,
                numero_contrato,
                fornecedor,
                objeto,
                situacao_calculada,
                valor_contrato,
                vig_inicio,
                novo_vig_fim,
                prazo_limite,
                dias_vencer,
                novo_aditivo,
                prox_passo,
                modalidade,
                amparo_legal,
                categoria,
                data_assinatura,
                data_publicacao,
                itens,
                quantidade,
                gestor,
                contato,
                setor,
                observacao,
                acompanhamento
            )
            st.success("Aditivo adicionado com sucesso!")
            st.session_state.show_add_aditivo_dialog = False
            st.rerun()

@st.experimental_dialog(title="Editar Contrato")
def edit_contract_dialog(contract):
    (
        id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
        dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, 
        quantidade, gestor, contato, setor, observacao, acompanhamento
    ) = contract
    st.write(f"**Editando Contrato:** {numero_contrato}")
    novo_numero_processo = st.text_input("Número do Processo", value=numero_processo, key=f"numero_processo_{id}")
    novo_numero_contrato = st.text_input("Número do Contrato", value=numero_contrato, key=f"numero_contrato_{id}")
    novo_fornecedor = st.text_input("Fornecedor do Contrato", value=fornecedor, key=f"fornecedor_{id}")
    novo_objeto = st.text_input("Objeto", value=objeto, key=f"objeto_{id}")
    novo_valor_contrato = st.number_input("Valor do Contrato", value=valor_contrato, step=0.01, key=f"valor_contrato_{id}")
    novo_vig_inicio = st.date_input("Vigência Início", value=datetime.strptime(vig_inicio, "%Y-%m-%d").date(), key=f"vig_inicio_{id}")
    novo_vig_fim = st.date_input("Vigência Fim", value=datetime.strptime(vig_fim, "%Y-%m-%d").date(), key=f"vig_fim_{id}")
    novo_prazo_limite = novo_vig_fim - timedelta(days=60)
    novo_aditivo = int(aditivo) if aditivo.isdigit() else 0

    # Novos campos no formulário de edição
    nova_modalidade = st.selectbox("Modalidade", ["dispensa", "inegibilidade", "pregao", "concorrencia"], index=["dispensa", "inegibilidade", "pregao", "concorrencia"].index(modalidade), key=f"modalidade_{id}")
    novo_amparo_legal = st.selectbox("Amparo Legal", ["Lei 8.666/93", "Lei 14.133/21"], index=["Lei 8.666/93", "Lei 14.133/21"].index(amparo_legal), key=f"amparo_legal_{id}")
    nova_categoria = st.selectbox("Categoria", ["compras", "serviços"], index=["compras", "serviços"].index(categoria), key=f"categoria_{id}")
    nova_data_assinatura = st.date_input("Data de Assinatura", value=datetime.strptime(data_assinatura, "%Y-%m-%d").date() if data_assinatura else None, key=f"data_assinatura_{id}")
    nova_data_publicacao = st.date_input("Data de Publicação", value=datetime.strptime(data_publicacao, "%Y-%m-%d").date() if data_publicacao else None, key=f"data_publicacao_{id}")
    novos_itens = st.text_input("Itens", value=itens, key=f"itens_{id}")
    nova_quantidade = st.number_input("Quantidade", value=quantidade, step=1, key=f"quantidade_{id}")
    # Novos campos de observacao e acompanhamento
    nova_observacao = st.text_input("Observação", value=observacao, key=f"observacao_{id}")
    novo_acompanhamento = st.text_input("Acompanhamento", value=acompanhamento, key=f"acompanhamento_{id}")
    novo_gestor = st.text_input("Gestor", value=gestor, key=f"gestor_{id}")
    novo_contato = st.text_input("Contato", value=contato, key=f"contato_{id}")
    novo_setor = st.text_input("Setor", value=setor, key=f"setor_{id}")

    novo_prox_passo = st.text_input("Próximo Passo", value=prox_passo, key=f"prox_passo_{id}")

    novos_dias_vencer = (novo_vig_fim - datetime.today().date()).days

    if st.button("Salvar Alterações", key=f"salvar_{id}"):
        situacao_calculada = calculate_situation(novos_dias_vencer)
        update_contract(
            id, novo_numero_processo, novo_numero_contrato, novo_fornecedor, novo_objeto, situacao_calculada, novo_valor_contrato, novo_vig_inicio, novo_vig_fim, 
            novo_prazo_limite, novos_dias_vencer, novo_aditivo, novo_prox_passo, nova_modalidade, novo_amparo_legal, nova_categoria, nova_data_assinatura, 
            nova_data_publicacao, novos_itens, nova_quantidade, novo_gestor, novo_contato, novo_setor, nova_observacao, novo_acompanhamento
        )
        st.success("Contrato atualizado com sucesso!")
        st.session_state.show_edit_contract_dialog = False
        st.rerun()

def show_gerenciar_contratos():
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

    # Campo de pesquisa
    st.write("## Pesquisa de Contratos")
    pesquisa_numero = st.text_input("Pesquisar Número do Contrato")

    # Botão de pesquisa
    if st.button("Pesquisar"):
        st.session_state['pesquisa_numero'] = pesquisa_numero

    # Exibir contratos
    contracts = get_contracts()
    if 'pesquisa_numero' in st.session_state:
        contracts = [contract for contract in contracts if contract[2] == st.session_state['pesquisa_numero']]

    today = datetime.today().date()
    for contract in contracts:
        id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento = contract
        vig_inicio = datetime.strptime(vig_inicio, "%Y-%m-%d").date()
        vig_fim = datetime.strptime(vig_fim, "%Y-%m-%d").date()
        prazo_limite = vig_fim - timedelta(days=60)
        dias_vencer = (vig_fim - today).days
        situacao_calculada = calculate_situation(dias_vencer)
        
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
        
        with col1:
            with st.expander(f"Número do Contrato: {numero_contrato}"):
                st.write(f"**Fornecedor do Contrato:** {fornecedor}")
                st.write(f"**Objeto:** {objeto}")
                st.write(f"**Situação:** {situacao_calculada}")
                st.write(f"**Valor do Contrato:** {valor_contrato}")
                st.write(f"**Vigência Início:** {vig_inicio}")
                st.write(f"**Vigência Fim:** {vig_fim}")
                st.write(f"**Prazo Limite:** {prazo_limite}")
                st.write(f"**Aditivo:** {aditivo}")
                st.write(f"**Próximo Passo:** {prox_passo}")
                # Exibir novos campos
                st.write(f"**Modalidade:** {modalidade}")
                st.write(f"**Amparo Legal:** {amparo_legal}")
                st.write(f"**Categoria:** {categoria}")
                st.write(f"**Data de Assinatura:** {data_assinatura}")
                st.write(f"**Data de Publicação:** {data_publicacao}")
                st.write(f"**Itens:** {itens}")
                st.write(f"**Quantidade:** {quantidade}")
                st.write(f"**Observação:** {observacao}")
                st.write(f"**Acompanhamento:** {acompanhamento}")
                st.write(f"**Gestor:** {gestor}")
                st.write(f"**Contato:** {contato}")
                st.write(f"**Setor:** {setor}")

        with col2:
            st.markdown(f"""
            <div style='text-align: center; position: relative; bottom: 30px;'>
                <span style='font-size: 14px;'>Dias a Vencer</span>
                <div style='border: 1px solid #d7d7d8; border-radius: 10px; padding: 10px; margin-top: 5px;'>{dias_vencer}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='text-align: center; position: relative; bottom: 30px;'>
                <span style='font-size: 14px;'>Situação</span>
                <div style='border: 1px solid #d7d7d8; border-radius: 10px; padding: 10px; margin-top: 5px;'>{situacao_calculada}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.write("")

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
                add_aditivo_dialog(id, numero_contrato, vig_fim)

        with col4:
            uploaded_file = st.file_uploader(f"Anexos", type="pdf", key=f"upload_{id}")
            if uploaded_file is not None:
                file_path = save_uploaded_file(uploaded_file, id)
                st.success(f"Arquivo PDF anexado com sucesso: {file_path}")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# Chama a função show_gerenciar_contratos
show_gerenciar_contratos()
