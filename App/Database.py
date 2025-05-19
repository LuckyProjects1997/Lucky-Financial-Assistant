# database.py

import sqlite3 # Módulo para interagir com bancos de dados SQLite.
import os # Módulo para interagir com o sistema operacional, usado para caminhos de arquivo.

# Obtém o diretório onde o script database.py está localizado.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define o caminho completo para o arquivo do banco de dados, garantindo que ele esteja no mesmo diretório que database.py.
DATABASE_NAME = os.path.join(BASE_DIR, "financial_assistant.db")

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    # print(f"DEBUG: Conectando ao banco de dados em: {DATABASE_NAME}") # Linha de depuração, pode ser removida depois.
    conn = sqlite3.connect(DATABASE_NAME) # Conecta ao arquivo do banco de dados.
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome.
    return conn # Retorna o objeto de conexão.

def create_tables():
    """Cria as tabelas necessárias no banco de dados se elas não existirem."""
    conn = get_db_connection() # Obtém uma conexão com o banco.
    cursor = conn.cursor() # Cria um cursor para executar comandos SQL.

    # Cria a tabela 'users' se ela não existir.
    # id: Identificador único do usuário (TEXTO, chave primária).
    # name: Nome do usuário (TEXTO, não pode ser nulo).
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    # Adicionar outras tabelas aqui no futuro (ex: categories, transactions)

    conn.commit() # Salva as alterações no banco de dados.
    conn.close() # Fecha a conexão com o banco de dados.
    print("Tabelas verificadas/criadas com sucesso.")

def add_user(user_id, name):
    """Adiciona um novo usuário ao banco de dados se o ID não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Tenta inserir o novo usuário.
        # A cláusula OR IGNORE faz com que, se o ID (PRIMARY KEY) já existir, o comando seja ignorado sem erro.
        cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Usuário '{name}' (ID: {user_id}) adicionado com sucesso.")
        else:
            print(f"Usuário com ID '{user_id}' já existe ou não pôde ser adicionado.")
    except sqlite3.Error as e:
        print(f"Erro ao adicionar usuário: {e}")
    finally:
        conn.close()

def get_all_users():
    """Busca e retorna todos os usuários cadastrados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users ORDER BY name ASC") # Busca todos os usuários, ordenados pelo nome.
    users = cursor.fetchall() # Retorna todas as linhas encontradas como uma lista de objetos Row.
    conn.close()
    # Converte os objetos Row para dicionários para facilitar o uso.
    return [{"id": user["id"], "name": user["name"]} for user in users]

# Bloco para inicializar o banco de dados quando este script for executado diretamente (opcional, para teste).
if __name__ == "__main__":
    create_tables() # Garante que as tabelas existam.
    # Adiciona o usuário Lucas como exemplo inicial.
    add_user("01", "Lucas")
    # add_user("02", "Maria") # Linha para adicionar Maria foi removida/comentada
    print("Usuários cadastrados:", get_all_users())