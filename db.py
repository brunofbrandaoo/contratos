import sqlite3

def init_db():
    conn = sqlite3.connect('contracts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            objeto TEXT,
            dias_vencer INTEGER,
            situacao TEXT
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

def add_contract(numero, objeto, dias_vencer, situacao):
    execute_query('''
        INSERT INTO contracts (numero, objeto, dias_vencer, situacao)
        VALUES (?, ?, ?, ?)
    ''', (numero, objeto, dias_vencer, situacao))

def update_contract(id, numero, objeto, dias_vencer, situacao):
    execute_query('''
        UPDATE contracts
        SET numero = ?, objeto = ?, dias_vencer = ?, situacao = ?
        WHERE id = ?
    ''', (numero, objeto, dias_vencer, situacao, id))

def delete_contract(id):
    execute_query('''
        DELETE FROM contracts WHERE id = ?
    ''', (id,))

def get_contracts():
    return fetch_query('''
        SELECT id, numero, objeto, dias_vencer, situacao FROM contracts
    ''')

def get_contract_by_id(id):
    return fetch_query('''
        SELECT id, numero, objeto, dias_vencer, situacao FROM contracts WHERE id = ?
    ''', (id,))
