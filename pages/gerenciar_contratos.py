import streamlit as st
from db import init_db, add_contract, update_contract, delete_contract, get_contracts, get_contract_by_id
from datetime import datetime, timedelta
import os

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
    modalidade = st.selectbox("Modalidade", ["dispensa", "inegibilidade", "pregao", "concorrencia"])
    amparo_legal = st.selectbox("Amparo Legal", ["Lei 8.666/93", "Lei 14.133/21"])
    categoria = st.selectbox("Categoria", ["compras", "serviços"])
    data_assinatura = st.date_input("Data de Assinatura")
    data_publicacao = st.date_input("Data de Publicação")
    itens = st.text_input("Itens")
    quantidade = st.number_input("Quantidade", step=1)
    valor_unitario = st.number_input("Valor Unitário", step=0.01)
    valor_total = st.number_input("Valor Total", step=0.01)
    gestor = st.text_input("Gestor")
    contato = st.text_input("Contato")
    setor = st.text_input("Setor")

    aditivo_checked = st.checkbox("Aditivo")
    if aditivo_checked:
        novo_vig_fim = st.date_input("Nova Data Final", value=vig_fim)
        aditivo = 1
    else:
        novo_vig_fim = vig_fim
        aditivo = 0

    if st.button("Salvar Novo Contrato"):
        dias_vencer = (novo_vig_fim - datetime.today().date()).days
        situacao_calculada = calculate_situation(dias_vencer)
        add_contract(numero_processo, numero_contrato, fornecedor, objeto, situacao_calculada, valor_contrato, vig_inicio, novo_vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor)
        st.session_state.show_add_contract_dialog = False
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
        id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor = contract
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
                st.write(f"**Valor Unitário:** {valor_unitario}")
                st.write(f"**Valor Total:** {valor_total}")
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

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Editar Contrato {numero_contrato}", key=f"edit_{id}"):
                st.session_state['edit_contract'] = id
                st.rerun()
        with col2:
            if st.button(f"Remover Contrato {numero_contrato}", key=f"remove_{id}"):
                delete_contract(id)
                st.rerun()
        with col3:
            uploaded_file = st.file_uploader(f"Anexos", type="pdf", key=f"upload_{id}")
            if uploaded_file is not None:
                file_path = save_uploaded_file(uploaded_file, id)
                st.success(f"Arquivo PDF anexado com sucesso: {file_path}")

        # Mostrar o formulário de edição imediatamente abaixo do contrato em questão
        if 'edit_contract' in st.session_state and st.session_state['edit_contract'] == id:
            st.write(f"**Editando Contrato:** {numero_contrato}")
            novo_numero_processo = st.text_input("Número do Processo", value=numero_processo, key=f"numero_processo_{id}")
            novo_numero_contrato = st.text_input("Número do Contrato", value=numero_contrato, key=f"numero_contrato_{id}")
            novo_fornecedor = st.text_input("Fornecedor do Contrato", value=fornecedor, key=f"fornecedor_{id}")
            novo_objeto = st.text_input("Objeto", value=objeto, key=f"objeto_{id}")
            novo_valor_contrato = st.number_input("Valor do Contrato", value=valor_contrato, step=0.01, key=f"valor_contrato_{id}")
            novo_vig_inicio = st.date_input("Vigência Início", value=vig_inicio, key=f"vig_inicio_{id}")
            novo_vig_fim = st.date_input("Vigência Fim", value=vig_fim, key=f"vig_fim_{id}")
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
            novo_valor_unitario = st.number_input("Valor Unitário", value=valor_unitario, step=0.01, key=f"valor_unitario_{id}")
            novo_valor_total = st.number_input("Valor Total", value=valor_total, step=0.01, key=f"valor_total_{id}")
            novo_gestor = st.text_input("Gestor", value=gestor, key=f"gestor_{id}")
            novo_contato = st.text_input("Contato", value=contato, key=f"contato_{id}")
            novo_setor = st.text_input("Setor", value=setor, key=f"setor_{id}")

            aditivo_checked = st.checkbox("Aditivo", key=f"aditivo_{id}")
            if aditivo_checked:
                novo_vig_fim = st.date_input("Nova Data Final", value=vig_fim, key=f"novo_vig_fim_{id}")
                novo_aditivo += 1

            novo_prox_passo = st.text_input("Próximo Passo", value=prox_passo, key=f"prox_passo_{id}")

            novos_dias_vencer = (novo_vig_fim - today).days
            
            if st.button("Salvar Alterações", key=f"salvar_{id}"):
                situacao_calculada = calculate_situation(novos_dias_vencer)
                update_contract(id, novo_numero_processo, novo_numero_contrato, novo_fornecedor, novo_objeto, situacao_calculada, novo_valor_contrato, novo_vig_inicio, novo_vig_fim, novo_prazo_limite, novos_dias_vencer, novo_aditivo, novo_prox_passo, nova_modalidade, novo_amparo_legal, nova_categoria, nova_data_assinatura, nova_data_publicacao, novos_itens, nova_quantidade, novo_valor_unitario, novo_valor_total, novo_gestor, novo_contato, novo_setor)
                st.success("Contrato atualizado com sucesso!")
                del st.session_state['edit_contract']
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# Chama a função show_gerenciar_contratos
show_gerenciar_contratos()
