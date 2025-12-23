import sqlite3

# Nome do arquivo do banco de dados (o mesmo usado em EliteCritics.py)
DB_NAME = 'elite_critics.db'

def conectar_bd():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def adicionar_coluna_popcornmeter():
    """
    Adiciona a coluna 'nota_popcornmeter' à tabela 'Filme'.
    A coluna é do tipo REAL (para armazenar a porcentagem, ex: 72).
    """
    conn = conectar_bd()
    cursor = conn.cursor()
    print(f"Conectado ao banco de dados '{DB_NAME}'.")
    
    coluna = 'nota_popcornmeter'

    try:
        # Comando SQL para adicionar a nova coluna
        cursor.execute(f"ALTER TABLE Filme ADD COLUMN {coluna} REAL;")
        conn.commit()
        print(f"✅ Coluna '{coluna}' adicionada à tabela 'Filme' com sucesso.")
        
    except sqlite3.OperationalError as e:
        # Este erro acontece se a coluna já existir
        if f"duplicate column name: {coluna}" in str(e):
            print(f"⚠️ Aviso: A coluna '{coluna}' já existe na tabela 'Filme'. Nenhuma alteração foi feita.")
        else:
            # Outro erro operacional inesperado
            print(f"❌ Erro operacional ao alterar a tabela: {e}")
            
    except sqlite3.Error as e:
        print(f"❌ Ocorreu um erro inesperado no SQLite: {e}")
        
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == '__main__':
    adicionar_coluna_popcornmeter()