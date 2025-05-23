# database.py

import sqlite3 # Módulo para interagir com bancos de dados SQLite.
import os # Módulo para interagir com o sistema operacional, usado para caminhos de arquivo.
import sys # Para sys.exit em caso de erro crítico
import datetime # Adicionado para usar funcionalidades de data e hora

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
    print(f"DEBUG DB: Tentando criar tabelas em {DATABASE_NAME}...") # Added
    conn = None # Initialize conn
    try: # Added try-finally to ensure conn.close()
        conn = get_db_connection() # Obtém uma conexão com o banco.
        cursor = conn.cursor() # Cria um cursor para executar comandos SQL.
        print("DEBUG DB: Conexão e cursor obtidos.") # Added

        # Cria a tabela 'users' se ela não existir.
        print("DEBUG DB: Criando tabela 'users'...") # Added
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        print("DEBUG DB: Tabela 'users' criada/verificada.") # Added
        
        # Cria a tabela 'categories' se ela não existir.
        print("DEBUG DB: Criando tabela 'categories'...") # Added
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                color TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("DEBUG DB: Tabela 'categories' criada/verificada.") # Added

        # Cria a tabela 'transactions' se ela não existir.
        print("DEBUG DB: Criando tabela 'transactions'...") # Added
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                category_id TEXT NOT NULL,
                description TEXT NOT NULL,
                value REAL NOT NULL,
                due_date TEXT NOT NULL,
                payment_date TEXT, -- Pode ser NULL
               status TEXT,           -- 'Pago', 'Em Aberto'
                modality TEXT,         -- 'À vista', 'Parcelado'
                installments TEXT,     -- Formato "1/N", "2/N", etc. ou NULL/ "1/1" para à vista
                launch_date TEXT NOT NULL, -- Data de cadastro da transação
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        print("DEBUG DB: Tabela 'transactions' criada/verificada.") # Added
        # Adicionar outras tabelas aqui no futuro (ex: categories, transactions)

        conn.commit() # Salva as alterações no banco de dados.
        print("DEBUG DB: Commit realizado.") # Added
        print("Tabelas verificadas/criadas com sucesso.")
    except sqlite3.Error as e: # Added
        print(f"DEBUG DB: Erro SQLite durante create_tables: {e}") # Added
    except Exception as e: # Added
        print(f"DEBUG DB: Erro geral durante create_tables: {e}") # Added
    finally: # Added
        if conn:
            conn.close() # Fecha a conexão com o banco de dados.
            print("DEBUG DB: Conexão fechada.") # Added

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
            return True # Retorna True em caso de sucesso
        else:
            print(f"Usuário com ID '{user_id}' já existe ou não pôde ser adicionado.")
            return False # Retorna False se o usuário já existe ou não foi adicionado
    except sqlite3.Error as e:
        print(f"Erro ao adicionar usuário: {e}")
        return False # Retorna False em caso de erro
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

def get_user_name_by_id(user_id):
    """Busca e retorna o nome de um usuário pelo seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone() # Retorna uma única linha
    conn.close()
    return user["name"] if user else None

def add_category(category_id, user_id, name, category_type, color):
    """Adiciona uma nova categoria ao banco de dados se o ID não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO categories (id, user_id, name, type, color) VALUES (?, ?, ?, ?, ?)",
                       (category_id, user_id, name, category_type, color))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Categoria '{name}' (ID: {category_id}) adicionada com sucesso para o usuário ID: {user_id}.")
            return True
        else:
            print(f"Categoria com ID '{category_id}' já existe ou não pôde ser adicionada.")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao adicionar categoria: {e}")
        return False
    finally:
        conn.close()

def get_categories_by_user(user_id):
    """Busca e retorna todas as categorias cadastradas para um usuário específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, name, type, color FROM categories WHERE user_id = ? ORDER BY name ASC", (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return [{"id": cat["id"], "user_id": cat["user_id"], "name": cat["name"], "type": cat["type"], "color": cat["color"]} for cat in categories]
def update_category(category_id, name, category_type, color):
    """Atualiza uma categoria existente no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Atualiza o nome, tipo e cor da categoria com o ID especificado.
        cursor.execute("""
            UPDATE categories
            SET name = ?, type = ?, color = ?
            WHERE id = ?
        """, (name, category_type, color, category_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Categoria com ID '{category_id}' atualizada com sucesso.")
            return True
        else:
            print(f"Nenhuma categoria encontrada com ID '{category_id}' para atualizar.")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao atualizar categoria: {e}")
        return False
    finally:
        conn.close()

def add_transaction(transaction_id_base, user_id, category_id, original_description, total_value, initial_due_date, initial_payment_date=None, initial_status=None, modality=None, num_installments=None, launch_date=None):
    """Adiciona uma nova transação ao banco de dados.
    Se for parcelado, cria múltiplas entradas.
    initial_due_date e launch_date devem estar no formato YYYY-MM-DD.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if launch_date is None:
        launch_date = datetime.date.today().strftime("%Y-%m-%d")

    try:
        all_successful = True # Initialize all_successful here
        if modality == "Parcelado" and num_installments and num_installments > 1:
            value_per_installment = round(total_value / num_installments, 2)
            # Ajusta a última parcela para compensar arredondamentos
            remaining_value = total_value - (value_per_installment * (num_installments - 1))

            current_due_date_obj = datetime.datetime.strptime(initial_due_date, "%Y-%m-%d")

            for i in range(num_installments):
                parcel_number = i + 1
                transaction_id = f"{transaction_id_base}-{parcel_number}"
                description_with_installment = f"{original_description} ({parcel_number}/{num_installments})"
                installments_str = f"{parcel_number}/{num_installments}"
                current_value = value_per_installment if parcel_number < num_installments else remaining_value

                if parcel_number == 1:
                    status_for_installment = initial_status
                    payment_date_for_installment = initial_payment_date
                    due_date_for_installment_str = initial_due_date
                else:
                    status_for_installment = "Em Aberto" # Parcelas futuras são em aberto
                    payment_date_for_installment = None
                    # Calcula a data de vencimento para as parcelas subsequentes
                    # Adiciona um mês à data de vencimento da parcela anterior
                    due_date_for_installment_obj = current_due_date_obj.replace(day=1) + datetime.timedelta(days=31) # Vai para o próximo mês
                    # Tenta manter o mesmo dia do mês, ajustando se o mês for mais curto
                    try:
                        due_date_for_installment_obj = due_date_for_installment_obj.replace(day=current_due_date_obj.day)
                    except ValueError: # Dia inválido para o mês (ex: dia 31 em fevereiro)
                        # Vai para o último dia do mês anterior (que é o mês correto)
                        due_date_for_installment_obj = (due_date_for_installment_obj.replace(day=1) - datetime.timedelta(days=1))
                    
                    due_date_for_installment_str = due_date_for_installment_obj.strftime("%Y-%m-%d")
                    current_due_date_obj = due_date_for_installment_obj # Atualiza para a próxima iteração

                cursor.execute("""
                    INSERT OR IGNORE INTO transactions (id, user_id, category_id, description, value, due_date, payment_date, status, modality, installments, launch_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (transaction_id, user_id, category_id, description_with_installment, current_value, due_date_for_installment_str, payment_date_for_installment, status_for_installment, modality, installments_str, launch_date))
                
                if cursor.rowcount == 0:
                    all_successful = False
                    print(f"Parcela {parcel_number} da transação com ID base '{transaction_id_base}' já existe ou não pôde ser adicionada.")
        else: # À vista ou parcela única
            installments_display = "1/1" if modality == "À vista" else f"1/{num_installments or 1}"
            description_final = f"{original_description} (1/1)" if modality == "À vista" else original_description # Evita duplicar (1/1) se já tiver
            if modality == "Parcelado" and num_installments == 1: # Se for parcelado mas só 1 parcela
                 description_final = f"{original_description} (1/1)"

            cursor.execute("""
                INSERT OR IGNORE INTO transactions (id, user_id, category_id, description, value, due_date, payment_date, status, modality, installments, launch_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (transaction_id_base, user_id, category_id, description_final, total_value, initial_due_date, initial_payment_date, initial_status, modality, installments_display, launch_date))
            if cursor.rowcount == 0:
                all_successful = False
                print(f"Transação à vista com ID '{transaction_id_base}' já existe ou não pôde ser adicionada.")

        conn.commit()
        if all_successful:
            print(f"Transação(ões) baseada(s) em '{original_description}' (ID base: {transaction_id_base}) adicionada(s) com sucesso para o usuário ID: {user_id}.")
        return all_successful

    except sqlite3.Error as e:
        print(f"Erro ao adicionar transação: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado ao adicionar transação: {e}")
        return False
    finally:
        conn.close()

def delete_transaction(transaction_id):
    """Exclui uma transação do banco de dados pelo seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Transação com ID '{transaction_id}' excluída com sucesso.")
            return True
        else:
            print(f"Nenhuma transação encontrada com ID '{transaction_id}' para excluir.")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao excluir transação ID '{transaction_id}': {e}")
        return False
    finally:
        conn.close()
        
def delete_category(category_id):
    """Exclui uma categoria do banco de dados pelo seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Categoria com ID '{category_id}' excluída com sucesso.")
            return True
        else:
            print(f"Nenhuma categoria encontrada com ID '{category_id}' para excluir.")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao excluir categoria: {e}")
        return False
    finally:
        conn.close()

def delete_all_users():
    """Deleta todos os usuários da tabela users."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Delete all rows from the users table
        cursor.execute("DELETE FROM users")
        conn.commit()
        count = cursor.rowcount
        print(f"{count} usuários deletados com sucesso.")
        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar todos os usuários: {e}")
        # Pode ser necessário deletar categorias e transações primeiro se houver dependências
        print("Se houver categorias ou transações associadas a usuários, a exclusão pode falhar devido a chaves estrangeiras.")
        print("Considere deletar dados relacionados (categorias, transações) primeiro, se necessário.")
        return False
    finally:
        conn.close()
def delete_user_by_name(name):
    """Exclui um usuário do banco de dados pelo seu nome."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE name = ?", (name,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Usuário '{name}' excluído com sucesso.")
            return True
        else:
            print(f"Nenhum usuário encontrado com o nome '{name}' para excluir.")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao excluir usuário '{name}': {e}")
        return False
    finally:
        conn.close()

def get_monthly_expenses_by_category_for_year(user_id, year):
    """
    Busca a soma das despesas mensais por categoria para um usuário e ano específicos.
    Retorna um dicionário onde as chaves são nomes de categorias e os valores são listas
    de 12 totais mensais (Janeiro a Dezembro).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT
            c.name AS category_name,
            CAST(SUBSTR(t.due_date, 6, 2) AS INTEGER) AS month, -- Converte mês para INTEGER para ordenação
            SUM(t.value) AS monthly_total
        FROM
            transactions t
        JOIN
            categories c ON t.category_id = c.id
        WHERE
            t.user_id = ? AND
            SUBSTR(t.due_date, 1, 4) = ? AND
            c.type = 'Despesa'
        GROUP BY
            c.id, c.name, month
        ORDER BY
            c.name, month;
    """
    cursor.execute(query, (user_id, str(year)))
    results = cursor.fetchall()
    conn.close()
    return results

def get_category_summary_for_month(user_id, year, month_number):
    """
    Busca a soma das transações (despesas e proventos) por categoria para um usuário, ano e mês específicos.
    O mês é filtrado pela due_date.
    Retorna uma lista de dicionários: {'category_name': str, 'category_type': str, 'category_color': str, 'total_value': float}
    """
    conn = get_db_connection()
    print(f"DEBUG DB: get_category_summary_for_month (SUM) - user_id: {user_id}, year: {year}, month_number: {month_number}")
    cursor = conn.cursor()
    query = """
        SELECT
            c.name AS category_name,
            c.type AS category_type,
            c.color AS category_color,
            SUM(t.value) AS total_value
        FROM
            transactions t
        JOIN
            categories c ON t.category_id = c.id
        WHERE
            t.user_id = ? AND
            SUBSTR(t.due_date, 1, 4) = ? AND -- Ano
            CAST(SUBSTR(t.due_date, 6, 2) AS INTEGER) = ? -- Mês
        GROUP BY
            c.id, c.name, c.type, c.color
        ORDER BY
            c.name;
    """
    cursor.execute(query, (user_id, str(year), month_number))
    results = cursor.fetchall()
    print(f"DEBUG DB: get_category_summary_for_month (SUM) - Raw results: {results}")
    conn.close()
    return results

def get_category_totals_for_year(user_id, year, category_type):
    """
    Busca a soma total das transações por categoria para um usuário, ano e tipo de categoria específicos.
    Retorna uma lista de dicionários: {'category_name': str, 'total_value': float}
    ordenada pelo nome da categoria.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT
            c.name AS category_name,
            c.color AS category_color,
            SUM(t.value) AS total_value
        FROM
            transactions t
        JOIN
            categories c ON t.category_id = c.id
        WHERE
            t.user_id = ? AND
            SUBSTR(t.due_date, 1, 4) = ? AND -- Ano
            c.type = ? -- Tipo de Categoria (Despesa ou Provento)
        GROUP BY
            c.id, c.name, c.color
        HAVING
            SUM(t.value) IS NOT NULL -- Garante que apenas categorias com transações sejam retornadas
        ORDER BY
            c.name ASC;
    """
    cursor.execute(query, (user_id, str(year), category_type))
    results = cursor.fetchall()
    conn.close()
    return [{"category_name": row["category_name"], "category_color": row["category_color"], "total_value": row["total_value"]} for row in results]
def get_transactions_for_month(user_id, year, month_number):
    """
    Busca todas as transações para um usuário, ano e mês específicos.
    O mês é filtrado pela due_date.
    Retorna uma lista de dicionários.
    """
    conn = get_db_connection()
    print(f"DEBUG DB: get_transactions_for_month (DETAILS) - user_id: {user_id}, year: {year}, month_number: {month_number}")
    cursor = conn.cursor()
    query = """
        SELECT
            t.id,
            t.description,
            t.value,
            t.due_date,
            t.payment_date,
            t.status,
            t.modality,
            t.launch_date,
            t.installments,
            c.name AS category_name,
            c.type AS category_type,
            c.color AS category_color
        FROM
            transactions t
        JOIN
            categories c ON t.category_id = c.id
        WHERE
            t.user_id = ? AND
            SUBSTR(t.due_date, 1, 4) = ? AND -- Ano
            CAST(SUBSTR(t.due_date, 6, 2) AS INTEGER) = ? -- Mês
        ORDER BY
            t.due_date ASC, c.type DESC; -- Ordena por data, e proventos antes de despesas para mesma data
    """
    cursor.execute(query, (user_id, str(year), month_number))
    results = cursor.fetchall()
    print(f"DEBUG DB: get_transactions_for_month (DETAILS) - Raw results: {results}")
    conn.close()
    # Converte os objetos Row para dicionários, incluindo os novos campos
    return [
        {
            "id": row["id"], "description": row["description"], "value": row["value"],
            "due_date": row["due_date"], "payment_date": row["payment_date"],
            "status": row["status"], "category_name": row["category_name"],
            "category_type": row["category_type"], "category_color": row["category_color"], "launch_date": row["launch_date"],
            "modality": row["modality"], "installments": row["installments"]
        }
        for row in results
    ]

def get_transaction_by_id(transaction_id):
    """Busca uma transação específica pelo seu ID, incluindo o nome da categoria."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT
            t.id,
            t.user_id,
            t.category_id,
            t.description,
            t.value,
            t.due_date,
            t.payment_date,
            t.status,
            t.modality,
            t.installments,
            t.launch_date,
            c.name AS category_name,
            c.type AS category_type 
        FROM
            transactions t
        JOIN
            categories c ON t.category_id = c.id
        WHERE
            t.id = ?;
    """
    cursor.execute(query, (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    return dict(transaction) if transaction else None

def update_transaction(transaction_id, description, value, due_date, payment_date, status, category_id):
    """Atualiza uma transação existente no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE transactions
            SET description = ?, value = ?, due_date = ?, payment_date = ?, status = ?, category_id = ?
            WHERE id = ?
        """, (description, value, due_date, payment_date, status, category_id, transaction_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Transação ID '{transaction_id}' atualizada com sucesso.")
            return True
        else:
            print(f"Nenhuma transação encontrada com ID '{transaction_id}' para atualizar.")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao atualizar transação ID '{transaction_id}': {e}")
        return False
    finally:
        conn.close()


# Bloco para inicializar o banco de dados quando este script for executado diretamente (opcional, para teste).
if __name__ == "__main__":
    create_tables() # Garante que as tabelas existam
    
    # --- Para remover todos os usuários, descomente a linha abaixo e execute este arquivo (Database.py) ---
    # print("Deletando todos os usuários...")
    # delete_all_users()
    # print("Verificando usuários após exclusão:", get_all_users())
    # ------------------------------------------------------------------------------------------------------