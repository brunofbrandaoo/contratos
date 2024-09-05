import sqlite3

# Nome do arquivo do banco de dados
DATABASE_FILE = 'contracts.db'

def alter_aditivos_table():
    # Conectar ao banco de dados
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Passo 1: Renomear a tabela antiga
    cursor.execute("ALTER TABLE aditivos RENAME TO aditivos_old;")

    # Passo 2: Criar a nova tabela com a estrutura correta
    cursor.execute('''
        CREATE TABLE aditivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            numero_aditivo INTEGER,
            nova_vig_fim DATE,
            novo_valor_contrato REAL,
            codigo_aditivo INTEGER,            -- Alterado para INTEGER
            objeto_aditivo TEXT,
            data_assinatura_aditivo DATE,
            data_publicacao_aditivo DATE,
            FOREIGN KEY (contract_id) REFERENCES contracts (id)
        );
    ''')

    # Passo 3: Copiar os dados da tabela antiga para a nova
    cursor.execute('''
        INSERT INTO aditivos (id, contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, 
                              codigo_aditivo, objeto_aditivo, data_assinatura_aditivo, data_publicacao_aditivo)
        SELECT id, contract_id, numero_aditivo, nova_vig_fim, novo_valor_contrato, 
               codigo_aditivo, objeto_aditivo, data_assinatura_aditivo, data_publicacao_aditivo
        FROM aditivos_old;
    ''')

    # Passo 4: Remover a tabela antiga
    cursor.execute("DROP TABLE aditivos_old;")

    # Verificar a estrutura da tabela atualizada
    cursor.execute("PRAGMA table_info(aditivos);")
    columns = cursor.fetchall()

    print("\nEstrutura atualizada da tabela 'aditivos':")
    for column in columns:
        print(column)

    # Fechar a conexão com o banco de dados
    conn.commit()
    conn.close()

if __name__ == "__main__":
    alter_aditivos_table()
