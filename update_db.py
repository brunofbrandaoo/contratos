import sqlite3

def clear_table():
    conn = sqlite3.connect('contracts.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contracts')
    conn.commit()
    conn.close()
    print("Todos os dados da tabela 'contracts' foram apagados.")

if __name__ == "__main__":
    clear_table()
