import os

# Excluir o arquivo contracts.db se ele existir
if os.path.exists('contracts.db'):
    os.remove('contracts.db')
    print("Arquivo contracts.db excluído com sucesso.")
else:
    print("Arquivo contracts.db não encontrado.")
