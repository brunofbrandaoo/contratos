import psycopg2
from psycopg2 import sql
from datetime import datetime
from decimal import Decimal


# Função para criar a conexão com o banco de dados Supabase
def connect_db():
    return psycopg2.connect(
        host="aws-0-sa-east-1.pooler.supabase.com",
        database="postgres",
        user="postgres.bnuuqoacguqfvbtjuqmj",
        password="contratos-sudema"
    )

def execute_query(query, params=()):
    print("Executing query:", query)
    print("With parameters:", params)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()


def fetch_query(query, params=()):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def add_contract(numero_processo, numero_contrato, fornecedor, objeto, valor_contrato, vig_inicio, vig_fim, prazo_limite, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, gestor, contato, setor, observacao, passivel_renovacao):
    # Convertendo datas para string no formato YYYY-MM-DD
    vig_inicio_str = vig_inicio.strftime('%Y-%m-%d') if isinstance(vig_inicio, datetime) else vig_inicio
    vig_fim_str = vig_fim.strftime('%Y-%m-%d') if isinstance(vig_fim, datetime) else vig_fim
    data_assinatura_str = data_assinatura.strftime('%Y-%m-%d') if isinstance(data_assinatura, datetime) else data_assinatura
    data_publicacao_str = data_publicacao.strftime('%Y-%m-%d') if isinstance(data_publicacao, datetime) else data_publicacao

    # Garantir que valor_contrato seja Decimal para PostgreSQL
    valor_contrato_decimal = Decimal(valor_contrato)

    # Novo contrato inicia com aditivo = 0
    aditivo_inicial = 0

    params = (numero_processo, numero_contrato, fornecedor, objeto, valor_contrato_decimal, 
              vig_inicio_str, vig_fim_str, prazo_limite, modalidade, amparo_legal, 
              categoria, data_assinatura_str, data_publicacao_str, gestor, contato, 
              setor, observacao, passivel_renovacao, aditivo_inicial)

    print("Parâmetros:", params)  # Para verificar os valores antes de executar a consulta

    # Função para inserir no banco de dados
    execute_query('''
    INSERT INTO contracts (numero_processo, numero_contrato, fornecedor, objeto, valor_contrato, vig_inicio, vig_fim, prazo_limite, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, gestor, contato, setor, observacao, passivel_renovacao, aditivo)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', params)
# Função para atualizar um contrato
def update_contract(id, numero_processo, numero_contrato, fornecedor, objeto, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
                    modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, gestor, contato, setor, observacao, 
                    passivel_renovacao, aditivo):
    """
    Atualiza os detalhes de um contrato no banco de dados.

    Parameters:
    id (int): ID do contrato a ser atualizado.
    Todos os outros parâmetros correspondem às colunas da tabela `contracts`.
    """
    # Convertendo datas para string no formato YYYY-MM-DD, caso sejam objetos datetime
    vig_inicio_str = vig_inicio.strftime('%Y-%m-%d') if isinstance(vig_inicio, datetime) else vig_inicio
    vig_fim_str = vig_fim.strftime('%Y-%m-%d') if isinstance(vig_fim, datetime) else vig_fim
    data_assinatura_str = data_assinatura.strftime('%Y-%m-%d') if isinstance(data_assinatura, datetime) else data_assinatura
    data_publicacao_str = data_publicacao.strftime('%Y-%m-%d') if isinstance(data_publicacao, datetime) else data_publicacao

    # Garantir que valor_contrato seja Decimal para PostgreSQL
    valor_contrato_decimal = Decimal(valor_contrato)

    # Garantir que `aditivo` seja um valor inteiro
    aditivo_int = int(aditivo) if aditivo is not None else 0

    # Atualiza o contrato incluindo a coluna `aditivo`
    execute_query('''
        UPDATE contracts
        SET numero_processo = %s, numero_contrato = %s, fornecedor = %s, objeto = %s, valor_contrato = %s, vig_inicio = %s, 
            vig_fim = %s, prazo_limite = %s, modalidade = %s, amparo_legal = %s, categoria = %s, data_assinatura = %s, 
            data_publicacao = %s, gestor = %s, contato = %s, setor = %s, observacao = %s, passivel_renovacao = %s, aditivo = %s
        WHERE id = %s
    ''', (numero_processo, numero_contrato, fornecedor, objeto, valor_contrato_decimal, vig_inicio_str, vig_fim_str, prazo_limite, 
          modalidade, amparo_legal, categoria, data_assinatura_str, data_publicacao_str, gestor, contato, setor, observacao, 
          passivel_renovacao, aditivo_int, id))
# Função para excluir um contrato
def delete_contract(id):
    execute_query('''
        DELETE FROM contracts WHERE id = %s
    ''', (id,))

# Função para obter todos os contratos
def get_contracts():
    return fetch_query('''
        SELECT id, numero_processo, numero_contrato, fornecedor, objeto, valor_contrato, vig_inicio, vig_fim, prazo_limite, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, gestor, contato, setor, observacao, passivel_renovacao FROM contracts
    ''')

def get_contract_by_id(id):
    result = fetch_query('''
        SELECT id, numero_processo, numero_contrato, fornecedor, objeto, valor_contrato, vig_inicio, vig_fim, prazo_limite, 
               modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, gestor, contato, setor, observacao, 
               passivel_renovacao, aditivo
        FROM contracts WHERE id = %s
    ''', (id,))
    return result[0] if result else None

# Função para adicionar um aditivo
def add_aditivo(contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, codigo_aditivo, objeto_aditivo, data_assinatura_aditivo, data_publicacao_aditivo):
    execute_query('''
        INSERT INTO aditivos (contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, codigo_aditivo, objeto_aditivo, data_assinatura_aditivo, data_publicacao_aditivo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, codigo_aditivo, objeto_aditivo, data_assinatura_aditivo, data_publicacao_aditivo))

# Função para obter todos os aditivos de um contrato
def get_aditivos(contract_id):
    return fetch_query('''
        SELECT * FROM aditivos WHERE contract_id = %s ORDER BY numero_aditivo
    ''', (contract_id,))

if __name__ == "__main__":
    print("Banco de dados conectado com sucesso.")