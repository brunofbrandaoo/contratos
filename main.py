import streamlit as st
from db import init_db, add_contract, update_contract, delete_contract, get_contracts, get_contract_by_id

# Inicializar banco de dados
init_db()

# Função para calcular a situação do contrato
def calculate_situation(dias_vencer):
    if dias_vencer < 0:
        return 'Vencido'
    elif dias_vencer <= 30:
        return 'Renovar'
    else:
        return 'Vigente'

st.title('Gerenciamento de Contratos')

# Botões em linha abaixo do título
col1, col2 = st.columns(2)
with col1:
    if st.button('Adicionar Contrato'):
        st.session_state['add_contract'] = True
with col2:
    st.write("")

# Formulário para adicionar novo contrato
if 'add_contract' in st.session_state:
    st.write("**Adicionar Novo Contrato**")
    numero = st.text_input("Número do Contrato")
    objeto = st.text_input("Objeto do Contrato")
    dias_vencer = st.number_input("Dias a Vencer", min_value=0, value=0)
    situacao = calculate_situation(dias_vencer)
    
    if st.button("Salvar Novo Contrato"):
        add_contract(numero, objeto, dias_vencer, situacao)
        st.success("Contrato adicionado com sucesso!")
        del st.session_state['add_contract']
        st.rerun()

# Exibir contratos
contracts = get_contracts()
for contract in contracts:
    id, numero, objeto, dias_vencer, situacao = contract
    situacao = calculate_situation(dias_vencer)
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col1:
        with st.expander(f"Número do Contrato: {numero}"):
            st.write(f"**Objeto do Contrato:** {objeto}")

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
            <div style='border: 1px solid #d7d7d8; border-radius: 10px; padding: 10px; margin-top: 5px;'>{situacao}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Editar Contrato {numero}", key=f"edit_{id}"):
            st.session_state['edit_contract'] = id
            st.rerun()
    with col2:
        if st.button(f"Remover Contrato {numero}", key=f"remove_{id}"):
            delete_contract(id)
            st.rerun()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mostrar o formulário de edição imediatamente abaixo do contrato em questão
    if 'edit_contract' in st.session_state and st.session_state['edit_contract'] == id:
        st.write(f"**Editando Contrato:** {numero}")
        novo_numero = st.text_input("Número do Contrato", value=numero, key=f"numero_{id}")
        novo_objeto = st.text_input("Objeto do Contrato", value=objeto, key=f"objeto_{id}")
        novos_dias_vencer = st.number_input("Dias a Vencer", value=dias_vencer, key=f"dias_vencer_{id}")
        
        if st.button("Salvar Alterações", key=f"salvar_{id}"):
            situacao = calculate_situation(novos_dias_vencer)
            update_contract(id, novo_numero, novo_objeto, novos_dias_vencer, situacao)
            st.success("Contrato atualizado com sucesso!")
            del st.session_state['edit_contract']
            st.rerun()
