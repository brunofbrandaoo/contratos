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
            valor_contrato REAL CHECK(valor_contrato >= 0),
            vig_inicio DATE,
            vig_fim DATE,
            prazo_limite INTEGER CHECK(prazo_limite BETWEEN 1 AND 5),
            dias_vencer INTEGER CHECK(dias_vencer >= 0),
            aditivo TEXT,
            prox_passo TEXT,
            modalidade TEXT,
            amparo_legal TEXT,
            categoria TEXT,
            data_assinatura DATE,
            data_publicacao DATE,
            itens TEXT,
            quantidade INTEGER CHECK(quantidade >= 0),
            gestor TEXT,
            contato TEXT,
            setor TEXT,
            observacao TEXT,
            acompanhamento TEXT,
            passivel_renovacao INTEGER CHECK(passivel_renovacao IN (0, 1))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aditivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            numero_aditivo INTEGER,
            nova_vig_fim DATE,
            novo_valor_contrato REAL,
            data_aditivo DATE,
            FOREIGN KEY (contract_id) REFERENCES contracts (id)
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

def add_contract(numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento, passivel_renovacao):
    execute_query('''
        INSERT INTO contracts (numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento, passivel_renovacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento, passivel_renovacao))

def update_contract(id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento, passivel_renovacao):
    execute_query('''
        UPDATE contracts
        SET numero_processo = ?, numero_contrato = ?, fornecedor = ?, objeto = ?, situacao = ?, valor_contrato = ?, vig_inicio = ?, vig_fim = ?, prazo_limite = ?, dias_vencer = ?, aditivo = ?, prox_passo = ?, modalidade = ?, amparo_legal = ?, categoria = ?, data_assinatura = ?, data_publicacao = ?, itens = ?, quantidade = ?, gestor = ?, contato = ?, setor = ?, observacao = ?, acompanhamento = ?, passivel_renovacao = ?
        WHERE id = ?
    ''', (numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento, passivel_renovacao, id))
    
def delete_contract(id):
    execute_query('''
        DELETE FROM contracts WHERE id = ?
    ''', (id,))

def get_contracts():
    return fetch_query('''
        SELECT id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento, passivel_renovacao FROM contracts
    ''')

def get_contract_by_id(id):
    result = fetch_query('''
        SELECT id, numero_processo, numero_contrato, fornecedor, objeto, situacao, valor_contrato, vig_inicio, vig_fim, prazo_limite, dias_vencer, aditivo, prox_passo, modalidade, amparo_legal, categoria, data_assinatura, data_publicacao, itens, quantidade, gestor, contato, setor, observacao, acompanhamento, passivel_renovacao 
        FROM contracts WHERE id = ?
    ''', (id,))
    return result[0] if result else None

def add_aditivo(contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, data_aditivo):
    execute_query('''
        INSERT INTO aditivos (contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, data_aditivo)
        VALUES (?, ?, ?, ?, ?)
    ''', (contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, data_aditivo))

def get_aditivos(contract_id):
    return fetch_query('''
        SELECT * FROM aditivos WHERE contract_id = ? ORDER BY numero_aditivo
    ''', (contract_id,))

if __name__ == "__main__":
    init_db()
    print("Banco de dados, tabela 'contracts' e tabela 'aditivos' criados com sucesso.")
