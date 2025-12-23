import sqlite3
import os

# Nome do arquivo do banco de dados
DB_NAME = 'elite_critics.db'

def criar_tabelas():
    """
    Cria a base de dados SQLite e as tabelas Critico, Filme e Critica.
    """
    try:
        # Conecta ao banco de dados (cria o arquivo se não existir)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        print(f"Banco de dados '{DB_NAME}' conectado com sucesso.")

        # --- 1. Tabela Critico ---
        # experiencia_genero e rank_genero serão TEXT e armazenarão dados JSON/string serializada
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Critico (
                url_critico TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                experiencia_genero TEXT,
                rank_genero TEXT
            );
        """)
        print("Tabela 'Critico' criada/verificada.")

        # --- 2. Tabela Filme ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Filme (
                url_filme TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                nota_rt INTEGER,
                nota_ndci REAL,
                nota_ndcii REAL,
                generos TEXT
            );
        """)
        print("Tabela 'Filme' criada/verificada.")

        # --- 3. Tabela Critica ---
        # Armazena o relacionamento (muitos para muitos) e a aprovação
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Critica (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_critico TEXT NOT NULL,
                url_filme TEXT NOT NULL,
                aprovacao BOOLEAN NOT NULL,
                FOREIGN KEY (url_critico) REFERENCES Critico(url_critico),
                FOREIGN KEY (url_filme) REFERENCES Filme(url_filme)
            );
        """)
        print("Tabela 'Critica' criada/verificada.")

        # Salva as alterações
        conn.commit()

    except sqlite3.Error as e:
        print(f"Ocorreu um erro no SQLite: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == '__main__':
    criar_tabelas()