import streamlit as st
from db import init_db, add_contract, update_contract, delete_contract, get_contracts, get_contract_by_id
from datetime import datetime, timedelta
from streamlit_modal import Modal
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

def show_gerenciar_contratos():
    # Inicializar banco de dados
    init_db()

    # Botões em linha abaixo do título
    modal = Modal(
        key="add_contract_modal", 
        title="Adicionar Novo Contrato",
        padding=8,    # default value
        max_width=1440  # default value
    )

    col1, col2 = st.columns([3, 1])  # Ajustar a proporção das colunas conforme necessário
    with col1:
        st.title('Gerenciamento de Contratos')
    with col2:
        if st.button('Adicionar Contrato'):
            modal.open()

    if modal.is_open():
        with modal.container():
            st.write("**Adicionar Novo Contrato**")
            numero_processo = st.text_input("Número do Processo")
            numero_contrato = st.text_input("Número do Contrato")
            fornecedor = st.text_input("Fornecedor do Contrato")
            objeto = st.text_input("Objeto")
            valor_contrato = st.number_input("Valor do Contrato", step=0.01)
            vig_inicio = st.date_input("Vigência Início")
            vig_fim = st.date_input("Vigência Fim")
            prazo_limite = vig_fim - timedelta(days=60)
            aditivo = 0
            prox_passo = st.text_input("Próximo Passo")
            aditivo_checked = st.checkbox("Aditivo")

            if aditivo_checked:
                novo_vig_fim = st.date_input("Nova Data Final", value=vig_fim)
                vig_fim = novo_vig_fim
                aditivo += 1

            if st.button("Salvar Novo Contrato"):
                dias_vencer = (vig_fim - datetime.today().date()).days
                situacao_calculada = calculate_situation(dias_vencer)
                add_contract(numero_processo, numero_contrato, fornecedor, objeto, situacao_calculada, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo)
                st.success("Contrato adicionado com sucesso!")
                modal.close()
                st.rerun()

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
        id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo = contract
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
            aditivo_checked = st.checkbox("Aditivo", key=f"aditivo_{id}")

            if aditivo_checked:
                novo_vig_fim = st.date_input("Nova Data Final", value=vig_fim, key=f"novo_vig_fim_{id}")
                novo_aditivo += 1

            novo_prox_passo = st.text_input("Próximo Passo", value=prox_passo, key=f"prox_passo_{id}")

            novos_dias_vencer = (novo_vig_fim - today).days
            
            if st.button("Salvar Alterações", key=f"salvar_{id}"):
                situacao_calculada = calculate_situation(novos_dias_vencer)
                update_contract(id, novo_numero_processo, novo_numero_contrato, novo_fornecedor, novo_objeto, situacao_calculada, novo_valor_contrato, novo_vig_inicio, novo_vig_fim, novo_prazo_limite, novos_dias_vencer, novo_aditivo, novo_prox_passo)
                st.success("Contrato atualizado com sucesso!")
                del st.session_state['edit_contract']
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
