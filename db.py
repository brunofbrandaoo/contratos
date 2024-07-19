import sqlite3

def init_db():
    conn = sqlite3.connect('contracts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_processo TEXT,
            numero_contrato TEXT,
            objeto TEXT,
            fornecedor TEXT,
            situacao TEXT,
            valor_contrato REAL,
            vig_inicio DATE,
            vig_fim DATE,
            prazo_limite DATE,
            dias_vencer INTEGER,
            aditivo TEXT,
            prox_passo TEXT,
            modalidade TEXT,
            amparo_legal TEXT,
            categoria TEXT,
            data_assinatura DATE,
            data_publicacao DATE,
            itens TEXT,
            quantidade INTEGER,
            valor_unitario REAL,
            valor_total REAL,
            gestor TEXT,
            contato TEXT,
            setor TEXT
        )
    ''')
    conn.commit()
    conn.close()

def execute_query(query, params=()):
    conn = sqlite3.connect('contracts.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=()):
    conn = sqlite3.connect('contracts.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

def add_contract(numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor):
    execute_query('''
        INSERT INTO contracts (numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor))

def update_contract(id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor):
    execute_query('''
        UPDATE contracts
        SET numero_processo = ?, numero_contrato = ?, fornecedor = ?, objeto = ?, situacao = ?, valor_contrato = ?, vig_inicio = ?, vig_fim = ?, prazo_limite = ?, dias_vencer = ?, aditivo = ?, prox_passo = ?, modalidade = ?, amparo_legal = ?, categoria = ?, data_assinatura = ?, data_publicacao = ?, itens = ?, quantidade = ?, valor_unitario = ?, valor_total = ?, gestor = ?, contato = ?, setor = ?
        WHERE id = ?
    ''', (numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor, id))

def delete_contract(id):
    execute_query('''
        DELETE FROM contracts WHERE id = ?
    ''', (id,))

def get_contracts():
    return fetch_query('''
        SELECT id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor FROM contracts
    ''')

def get_contract_by_id(id):
    return fetch_query('''
        SELECT id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, valor_unitario, valor_total, gestor, contato, setor FROM contracts WHERE id = ?
    ''', (id,))

if __name__ == "__main__":
    init_db()
    print("Banco de dados e tabela 'contracts' criados com sucesso.")
