from supabase import create_client, Client
import pandas as pd
import streamlit as st
from db import add_contract, update_contract, delete_contract, get_contracts, get_contract_by_id, add_aditivo, get_aditivos
from datetime import datetime, timedelta
import os
import uuid
from decimal import Decimal
from datetime import datetime, date

url_supabase = st.secrets["supabase"]["url"]
key_supabase = st.secrets["supabase"]["key"]
# URL e chave de API do Supabase (substitua pelos seus valores)
SUPABASE_URL = url_supabase
SUPABASE_KEY = key_supabase

# Conectar ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bucket_name = 'contract-pdfs'

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

st.logo(image="sudema.png", link=None)

url_base = st.secrets["general"]["url_base"]

def upload_pdf_to_supabase(uploaded_file, contract_id, bucket_name='contract-pdfs'):
    """Faz o upload de um arquivo PDF para o bucket Supabase."""
    # Lê o conteúdo do arquivo usando `uploaded_file.read()`
    file_name = f"contract_{contract_id}/{uploaded_file.name}"
    
    # O `uploaded_file` é um `UploadedFile`, então devemos ler o conteúdo para bytes
    file_content = uploaded_file.read()
    
    # Realiza o upload para o Supabase utilizando o conteúdo em bytes
    response = supabase.storage.from_(bucket_name).upload(file_name, file_content)
    
    if response:
        return file_name
    else:
        st.error("Erro ao fazer upload do arquivo para o Supabase.")
        return None


def get_public_url(contract_id, file_name, bucket_name='contract-pdfs'):
    """Gera a URL pública correta incluindo o caminho completo."""
    try:
        # Construir o caminho completo do arquivo no bucket
        full_file_path = f"contract_{contract_id}/{file_name}"
        
        # Gerar a URL pública utilizando o caminho completo
        response = supabase.storage.from_(bucket_name).get_public_url(full_file_path)

        # Verificar se a resposta é um dicionário e possui a chave 'publicURL'
        if isinstance(response, dict) and 'publicURL' in response:
            return response['publicURL']
        else:
            st.error(f"Erro ao gerar URL pública: {response}")
            return None
    except Exception as e:
        st.error(f"Erro ao gerar URL pública para download: {e}")
        return None

def display_file_as_download_button(contract_id, file_name, bucket_name='contract-pdfs'):
    """Exibe um botão de download para o arquivo PDF usando o Streamlit."""
    try:
        # Lê o arquivo do Supabase e faz o download para exibição
        response = supabase.storage.from_(bucket_name).download(f"contract_{contract_id}/{file_name}")
        
        if response:
            # Exibir o botão de download usando o conteúdo do arquivo
            st.download_button(
                label=f"Baixar {file_name}",
                data=response,
                file_name=file_name,
                mime='application/pdf'
            )
        else:
            st.error(f"Não foi possível gerar o link para {file_name}.")
    except Exception as e:
        st.error(f"Erro ao fazer o download do arquivo: {e}")




def list_files_in_bucket(bucket_name, path=''):
    """Lista todos os arquivos no bucket."""
    try:
        response = supabase.storage.from_(bucket_name).list(path=path)
        return response
    except Exception as e:
        st.error(f"Erro ao listar arquivos no bucket: {e}")
        return []


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
    
def calculate_days_to_expiry(vig_fim):
    """
    Calcula a quantidade de dias até o vencimento do contrato.

    Parameters:
    vig_fim (datetime.date | str): Data de término da vigência do contrato como string no formato 'YYYY-MM-DD' ou como datetime.date.

    Returns:
    int: Número de dias restantes até o vencimento. Se já estiver vencido, retorna 0.
    """
    # Se `vig_fim` já for um objeto datetime.date, converte para string no formato necessário
    if isinstance(vig_fim, date):
        vig_fim = vig_fim.strftime('%Y-%m-%d')

    # Converter a data para um objeto datetime
    vig_fim_date = datetime.strptime(vig_fim, '%Y-%m-%d').date()
    
    # Obter a data atual
    hoje = datetime.now().date()
    
    # Calcular a diferença em dias
    dias_restantes = (vig_fim_date - hoje).days
    
    # Garante que não decresça abaixo de 0
    return max(0, dias_restantes)


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
    valor_contrato = st.number_input("Valor do Contrato", step=10.00, min_value=0.0)
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
            
            # Definir a vigência final do contrato como o valor de vig_fim no momento da criação
            vig_final_contrato_str = vig_fim.strftime('%Y-%m-%d')

            # Função que insere no banco
            add_contract(
                numero_processo, numero_contrato, fornecedor, objeto, valor_contrato_decimal, 
                vig_inicio_str, vig_fim_str, prazo_limite, modalidade, amparo_legal, categoria, 
                data_assinatura_str, data_publicacao_str, gestor, contato, setor, observacao, 
                passivel_renovacao, vig_final_contrato_str
            )

            st.session_state.show_add_contract_dialog = False
            st.rerun()


@st.experimental_dialog(title="Adicionar Aditivo")
def add_aditivo_dialog(contract_id, numero_contrato, vig_fim_atual, valor_contrato_atual):
    st.write(f"**Adicionar Aditivo ao Contrato:** {numero_contrato}")
    
    # Verificar se `vig_fim_atual` é uma string e convertê-la para `datetime.date` se necessário
    if isinstance(vig_fim_atual, str):
        vig_fim_atual = datetime.strptime(vig_fim_atual, '%Y-%m-%d').date()
    
    # Se `vig_fim_atual` já for um objeto datetime.date, ele será usado diretamente no date_input
    novo_vig_fim = st.date_input("Nova Data de Vigência Final", value=vig_fim_atual)
    novo_valor_contrato = st.number_input("Valor do Aditivo", value=float(valor_contrato_atual), format="%.2f")

    # Novos campos para o aditivo
    codigo_aditivo = st.text_input("Número do Aditivo")
    objeto_aditivo = st.text_input("Objeto do Aditivo")
    data_assinatura_aditivo = st.date_input("Data de Assinatura do Aditivo")
    data_publicacao_aditivo = st.date_input("Data de Publicação do Aditivo")
    
    if st.button("Salvar Aditivo"):
        contract = get_contract_by_id(contract_id)
        print(f"Contract fields: {contract}")
        print(f"Total fields in contract: {len(contract)}")

        # Imprimir cada campo e o índice correspondente
        for idx, field in enumerate(contract):
            print(f"Index {idx}: {field}")

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
                novo_valor_contrato,  # novo valor do contrato atualizado
                contract[6],  # vig_inicio (index correto é 6)
                novo_vig_fim,
                contract[8],  # prazo_limite (index correto é 8)
                contract[9],  # modalidade
                contract[10], # amparo_legal
                contract[11], # categoria
                contract[12], # data_assinatura
                contract[13], # data_publicacao
                contract[14], # gestor
                contract[15], # contato
                contract[16], # setor
                contract[17], # observacao
                contract[18], # passivel_renovacao (index correto é 18)
                novo_aditivo   # valor de aditivo atualizado
            )
            
            # Adiciona o aditivo com os novos campos
            add_aditivo(
                contract_id, 
                novo_aditivo, 
                novo_vig_fim, 
                novo_valor_contrato, 
                codigo_aditivo, 
                objeto_aditivo, 
                data_assinatura_aditivo, 
                data_publicacao_aditivo
            )
            
            st.success("Aditivo adicionado com sucesso!")
            st.session_state.show_add_aditivo_dialog = False
            st.rerun()


@st.experimental_dialog(title="Editar Contrato")
def edit_contract_dialog(contract):
    (id, numero_processo, numero_contrato, fornecedor, objeto, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
 modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, gestor, contato, setor, observacao, 
 passivel_renovacao, aditivo, vig_final_contrato) = contract


    st.write(f"**Editando Contrato:** {numero_contrato}")

    # Campos de edição no formulário
    novo_numero_processo = st.text_input("Número do Processo", value=numero_processo, key=f"numero_processo_{id}")
    novo_numero_contrato = st.text_input("Número do Contrato", value=numero_contrato, key=f"numero_contrato_{id}")
    novo_fornecedor = st.text_input("Fornecedor do Contrato", value=fornecedor, key=f"fornecedor_{id}")
    novo_objeto = st.text_input("Objeto", value=objeto, key=f"objeto_{id}")

    # Conversão de valor_contrato para float no `st.number_input` para evitar erro de tipo
    novo_valor_contrato = st.number_input(
        "Valor do Contrato", 
        value=float(valor_contrato),  # Converte para float
        step=10.00, 
        min_value=0.0, 
        key=f"valor_contrato_{id}"
    )

    novo_vig_inicio = st.date_input("Vigência Início", value=vig_inicio, key=f"vig_inicio_{id}")
    novo_vig_fim = st.date_input("Vigência Fim", value=vig_fim, key=f"vig_fim_{id}")
    novo_prazo_limite = st.radio("Prazo Limite (anos)", options=[1, 2, 3, 4, 5], index=prazo_limite - 1, key=f"prazo_limite_{id}")

    # Converter aditivo para inteiro
    novo_aditivo = int(aditivo) if aditivo else 0

    nova_modalidade = st.selectbox(
        "Modalidade", 
        ["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"], 
        index=["Dispensa", "Inegibilidade", "Pregão", "Concorrência", "Adesão a Ata"].index(modalidade), 
        key=f"modalidade_{id}"
    )

    novo_amparo_legal = st.selectbox(
        "Amparo Legal", 
        ["Lei 8.666/93", "Lei 14.133/21"], 
        index=["Lei 8.666/93", "Lei 14.133/21"].index(amparo_legal), 
        key=f"amparo_legal_{id}"
    )

    nova_categoria = st.selectbox(
        "Categoria", 
        ["Bens", "Serviços comuns", "Serviços de Engenharia"], 
        index=["Bens", "Serviços comuns", "Serviços de Engenharia"].index(categoria), 
        key=f"categoria_{id}"
    )

    nova_data_assinatura = st.date_input("Data de Assinatura", value=data_assinatura if data_assinatura else None, key=f"data_assinatura_{id}")
    nova_data_publicacao = st.date_input("Data de Publicação", value=data_publicacao if data_publicacao else None, key=f"data_publicacao_{id}")

    novo_observacao = st.text_input('Observação', value=observacao, key=f"observacao_{id}")

    novo_gestor = st.text_input("Gestor", value=gestor, key=f"gestor_{id}")
    novo_contato = st.text_input("Contato", value=contato, key=f"contato_{id}")
    novo_setor = st.text_input("Setor", value=setor, key=f"setor_{id}")
    novo_aditivo = aditivo

    # Calculando dias para vencimento
    novos_dias_vencer = max(0, (novo_vig_fim - datetime.today().date()).days)

    print(f"Quantidade de campos no contract: {len(contract)}")
    print(f"Campos retornados: {contract}")


    if st.button("Salvar Alterações", key=f"salvar_{id}"):
        # Calcular nova situação do contrato com base nos dias para vencer e se é passível de renovação
        situacao_calculada = calculate_situation(novos_dias_vencer, passivel_renovacao)

        # Chamar a função `update_contract` com os novos valores
        update_contract(
            id, 
            novo_numero_processo, 
            novo_numero_contrato, 
            novo_fornecedor, 
            novo_objeto, 
            novo_valor_contrato, 
            novo_vig_inicio, 
            novo_vig_fim, 
            novo_prazo_limite, 
            nova_modalidade, 
            novo_amparo_legal, 
            nova_categoria, 
            nova_data_assinatura, 
            nova_data_publicacao,
            novo_observacao,
            novo_gestor, 
            novo_contato, 
            novo_setor, 
            passivel_renovacao,
            novo_aditivo
        )
        st.success("Contrato atualizado com sucesso!")
        st.session_state.show_edit_contract_dialog = False
        st.rerun()

def format_date(date_value):
    """Converte uma data `datetime.date`, `datetime.datetime` ou string `YYYY-MM-DD` para `DD-MM-YYYY`."""
    if isinstance(date_value, datetime) or isinstance(date_value, date):
        return date_value.strftime('%d-%m-%Y')
    elif isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, '%Y-%m-%d').strftime('%d-%m-%Y')
        except ValueError:
            # Caso a string não esteja no formato esperado
            return date_value
    return date_value  # Retorna o valor original se não for datetime, date, nem string



def show_aditivo_details(contract_id):
    aditivos = get_aditivos(contract_id)
    if aditivos:
        # Espaçamento superior para separar a seção
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #f7f9fc; padding: 20px; border-radius: 12px; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #4a5568; text-align: center; margin-bottom: 20px; font-size: 24px;">Detalhes dos Aditivos</h3>
        """, unsafe_allow_html=True)

        for i, aditivo in enumerate(aditivos, 1):  # `i` começa em 1 e incrementa com cada iteração
            # Convertendo as datas para o formato `DD-MM-YYYY`
            vigencia_final = format_date(aditivo[3])
            assinatura = format_date(aditivo[7])
            publicacao = format_date(aditivo[8])

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
                    {i}  <!-- Aqui usamos `i` para numerar cada aditivo -->
                </div>
                <div style="flex: 1; min-width: 250px; margin-right: 20px;">
                    <p style="margin: 0; font-size: 18px;"><strong>Número do Aditivo:</strong> {aditivo[5]}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Data de Vigência Final do Aditivo:</strong> {vigencia_final}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Valor do aditivo:</strong> R$ {aditivo[4]:.2f}</p>
                </div>
                <div style="flex: 1; min-width: 250px; margin-left: 20px;">
                    <p style="margin: 0; font-size: 18px;"><strong>Objeto do Aditivo:</strong> {aditivo[6]}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Data de Assinatura do Aditivo:</strong> {assinatura}</p>
                    <p style="margin: 0; font-size: 18px;"><strong>Data de Publicação do Aditivo:</strong> {publicacao}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Fechamento do contêiner principal
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Este contrato ainda não possui aditivos.")

def calculate_time_remaining(vig_inicio, prazo_limite):
    if isinstance(vig_inicio, str):
        vig_inicio = datetime.strptime(vig_inicio, '%Y-%m-%d')
        
    end_date = vig_inicio + timedelta(days=prazo_limite * 365)  # Calcula a data final com base no prazo
    remaining_days = (end_date - datetime.now()).days  # Calcula os dias restantes

    return remaining_days


def contract_details_page(contract_id):
    contract = get_contract_by_id(contract_id)
    if contract:
        (
            id, numero_processo, numero_contrato, fornecedor, objeto, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
            modalidade, amparo_legal, categoria, data_assinatura, 
            data_publicacao, gestor, contato, setor, movimentacao, passivel_renovacao, aditivo, vig_final_contrato
        ) = contract

         # Formatar as datas no formato dia/mês/ano
        vig_inicio_formatada = vig_inicio.strftime('%d/%m/%Y') if isinstance(vig_inicio, date) else vig_inicio
        vig_fim_formatada = vig_fim.strftime('%d/%m/%Y') if isinstance(vig_fim, date) else vig_fim
        data_assinatura_formatada = data_assinatura.strftime('%d/%m/%Y') if isinstance(data_assinatura, date) else data_assinatura
        data_publicacao_formatada = data_publicacao.strftime('%d/%m/%Y') if isinstance(data_publicacao, date) else data_publicacao
        vig_final_contrato_formatada = vig_final_contrato.strftime('%d/%m/%Y') if isinstance(vig_fim, date) else vig_final_contrato

        dias_vencer = calculate_days_to_expiry(vig_fim)
        situacao = calculate_situation(dias_vencer, passivel_renovacao)
        passivel_renovacao_texto = "Sim" if passivel_renovacao == 1 else "Não"

        days_remaining = calculate_time_remaining(str(vig_inicio), prazo_limite)

        # Exibir contagem regressiva com `st.metric`
        # st.metric("Dias Restantes para o Prazo Limite", days_remaining, delta=-1, delta_color="inverse")

        # Exibir o progresso restante (opcional)
        progress_percentage = max(0, (days_remaining / (prazo_limite * 365)) * 100)
        # st.progress(int(progress_percentage))

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
                <strong>Valor do Contrato:</strong> {valor_contrato:.2f}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Vigência Início:</strong> {vig_inicio_formatada}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Vigência Fim:</strong> {vig_final_contrato_formatada}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Prazo Limite (anos):</strong> {prazo_limite}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Data de Assinatura:</strong> {data_assinatura_formatada}
            </div>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); font-size: 24px;">
                <strong>Data de Publicação:</strong> {data_publicacao_formatada}
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

        st.metric(label="Prazo limite do contrato", value=f'{days_remaining} dias', delta=-1, delta_color="normal")
        st.progress(int(progress_percentage))
        
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
        uploaded_file = None  # Inicializar a variável no início do escopo

        # Coluna 4 onde o arquivo pode ser enviado
        with col4:
            uploaded_file = st.file_uploader("Faça o upload de um arquivo PDF", type="pdf")

        # Verificar se há algum arquivo anexado
        if uploaded_file is not None:
            # Salvar no Supabase e obter o nome do arquivo salvo
            file_name = upload_pdf_to_supabase(uploaded_file, contract_id)
            if file_name:
                st.success(f"Arquivo PDF '{uploaded_file.name}' anexado com sucesso!")

                # Gerar URL pública para o download usando o caminho correto
                public_url = get_public_url(contract_id, uploaded_file.name)

                # Exibir botão de download com o link correto
                if public_url:
                    display_file_as_download_button(contract_id, uploaded_file.name)
                else:
                    st.error("Não foi possível gerar o link de download público.")

        # Listar arquivos anexados
        st.subheader("Arquivos Anexados")
        files = supabase.storage.from_(bucket_name).list(path=f"contract_{contract_id}/")

        # Exibir arquivos anexados ou informar que não há arquivos
        if files:
            for file in files:
                file_name = file['name']
                # Exibir botão de download para cada arquivo anexado
                display_file_as_download_button(contract_id, file_name.split('/')[-1])
        else:
            st.write("Nenhum arquivo anexado a este contrato.")

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
            # Garantir que estamos usando o índice correto para vig_fim
            if isinstance(contract[7], datetime):
                vig_fim_date = contract[7]
            else:
                try:
                    vig_fim_date = datetime.strptime(str(contract[7]), '%Y-%m-%d').date()
                except ValueError:
                    vig_fim_date = today  # Se a conversão falhar, use a data de hoje como fallback

            # Calcula o número de dias a vencer e garante que não seja menor que 0
            dias_a_vencer = max(0, (vig_fim_date - today).days)

            passivel_renovacao = contract[18]
            situacao_calculada = calculate_situation(dias_a_vencer, passivel_renovacao)
            link_detalhes = f"{url_base}/Total_contratos?page=details&contract_id={contract[0]}"


            vig_inicio_formatada = contract[6].strftime('%d-%m-%Y') if isinstance(contract[6], date) else contract[6]
            vig_fim_formatada = vig_fim_date.strftime('%d-%m-%Y')
            valor_formatado = f"R$ {float(contract[5]):,.1f}" 

            transformed_contracts.append(
                (
                    contract[2], contract[3], contract[4], 
                    valor_formatado, vig_inicio_formatada, vig_fim_formatada, dias_a_vencer, situacao_calculada, 
                    contract[19],  # Aditivo
                        contract[16],  # Movimentação
                        link_detalhes
                )
            )
        
        df = pd.DataFrame(
            transformed_contracts, 
            columns=[
                'Número do Contrato', 'Fornecedor', 'Objeto', 
                'Valor do Contrato', 'Vigência Início', 'Vigência Fim', 'Dias a Vencer', 'Situação', 'Aditivo', 'Movimentação', 'Detalhar'
            ]
        )
        
        st.dataframe(
            df.style.applymap(color_situation, subset=['Situação']),
            column_config={
                "Detalhar": st.column_config.LinkColumn(
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
