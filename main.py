import pandas as pd
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

# Barra lateral para navegação
menu = st.sidebar.selectbox('Menu', options=['Planilha', 'Gerenciar Contratos'])

if menu == 'Planilha':
    # Exibir contratos
    contracts = get_contracts()
    
    if contracts:
        df = pd.DataFrame(contracts, columns=['ID', 'Número', 'Fornecedor', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação'])
        st.write("## Dados dos Contratos")
        st.dataframe(df)
else:
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
        fornecedor = st.text_input("Fornecedor do Contrato")
        vig_inicio = st.date_input("Vigência Início")
        vig_fim = st.date_input("Vigência Fim")
        dias_vencer = st.number_input("Dias a Vencer", min_value=0, value=0)
        situacao = calculate_situation(dias_vencer)
        
        if st.button("Salvar Novo Contrato"):
            add_contract(numero, fornecedor, vig_inicio, vig_fim, dias_vencer, situacao)
            st.success("Contrato adicionado com sucesso!")
            del st.session_state['add_contract']
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
        contracts = [contract for contract in contracts if contract[1] == st.session_state['pesquisa_numero']]

    for contract in contracts:
        id, numero, fornecedor, vig_inicio, vig_fim, dias_vencer, situacao = contract
        situacao = calculate_situation(dias_vencer)
        
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
        
        with col1:
            with st.expander(f"Número do Contrato: {numero}"):
                st.write(f"**Fornecedor do Contrato:** {fornecedor}")
                st.write(f"**Vigência Início:** {vig_inicio}")
                st.write(f"**Vigência Fim:** {vig_fim}")

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

        # Mostrar o formulário de edição imediatamente abaixo do contrato em questão
        if 'edit_contract' in st.session_state and st.session_state['edit_contract'] == id:
            st.write(f"**Editando Contrato:** {numero}")
            novo_numero = st.text_input("Número do Contrato", value=numero, key=f"numero_{id}")
            novo_fornecedor = st.text_input("Fornecedor do Contrato", value=fornecedor, key=f"fornecedor_{id}")
            novo_vig_inicio = st.date_input("Vigência Início", value=vig_inicio, key=f"vig_inicio_{id}")
            novo_vig_fim = st.date_input("Vigência Fim", value=vig_fim, key=f"vig_fim_{id}")
            novos_dias_vencer = st.number_input("Dias a Vencer", value=dias_vencer, key=f"dias_vencer_{id}")
            
            if st.button("Salvar Alterações", key=f"salvar_{id}"):
                situacao = calculate_situation(novos_dias_vencer)
                update_contract(id, novo_numero, novo_fornecedor, novo_vig_inicio, novo_vig_fim, novos_dias_vencer, situacao)
                st.success("Contrato atualizado com sucesso!")
                del st.session_state['edit_contract']
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
