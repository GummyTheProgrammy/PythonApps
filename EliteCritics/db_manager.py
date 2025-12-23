import sqlite3
import json

# Nome do arquivo do banco de dados (constante do projeto)
DB_NAME = 'elite_critics.db'

def conectar_bd():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def buscar_filme_no_bd(url_filme):
    """
    Busca um filme na tabela 'Filme' pelo seu URL.
    Retorna um dicionário com os dados ou None se não for encontrado.
    """
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        # Nota: Agora buscamos por 'nota_popcornmeter' também
        cursor.execute("SELECT url_filme, nome, nota_rt, generos, nota_popcornmeter FROM Filme WHERE url_filme = ?", (url_filme,))
        cached_data = cursor.fetchone()
        
        if cached_data:
            return {
                'url_filme': cached_data[0],
                'nome': cached_data[1],
                'nota_rt': cached_data[2],
                'generos': cached_data[3],
                'nota_popcornmeter': cached_data[4]
            }
        return None
    except sqlite3.Error as e:
        print(f"Erro no DB_MANAGER ao buscar filme: {e}")
        return None
    finally:
        conn.close()

def inserir_filme(filme_data):
    """
    Insere ou atualiza os dados do filme na tabela 'Filme'.
    Usa a URL como chave primária.
    """
    conn = conectar_bd()
    cursor = conn.cursor()
    print("Conectado ao banco de dados!")
    try:
        # Atualizamos o comando SQL para incluir a nova coluna 'nota_popcornmeter'
        cursor.execute("""
            REPLACE INTO Filme (url_filme, nome, nota_rt, nota_popcornmeter, generos, nota_ndci, nota_ndcii)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            filme_data['url_filme'],
            filme_data['nome'],
            filme_data['nota_rt'],
            filme_data.get('nota_popcornmeter'), # Usamos .get() com fallback caso não seja extraído
            filme_data['generos'],
            None, # NDCI
            None  # NDCII
        ))
        conn.commit()
        print(f"Filme '{filme_data['nome']}' inserido/atualizado com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro no DB_MANAGER ao inserir filme: {e}")
    finally:
        conn.close()


def buscar_critico_por_url(url_critico):
    """
    Busca um crítico na tabela 'Critico' pelo seu URL.
    Retorna um dicionário com os dados ou None se não for encontrado.
    """
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT url_critico, nome FROM Critico WHERE url_critico = ?", (url_critico,))
        row = cursor.fetchone()
        if row:
            return {'url_critico': row[0], 'nome': row[1]}
        return None
    except sqlite3.Error as e:
        print(f"Erro no DB_MANAGER ao buscar critico: {e}")
        return None
    finally:
        conn.close()


def inserir_critico(critico_data):
    """
    Insere ou atualiza um crítico na tabela 'Critico'.
    Espera um dicionário com 'url_critico' e 'nome'.
    """
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "REPLACE INTO Critico (url_critico, nome) VALUES (?, ?)",
            (critico_data['url_critico'], critico_data['nome'])
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro no DB_MANAGER ao inserir critico: {e}")
        return False
    finally:
        conn.close()


def inserir_critica(critica_data):
    """
    Insere uma crítica na tabela 'Critica'.
    Espera um dicionário com 'url_filme', 'url_critico', 'aprovacao' (0/1)
    """
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "REPLACE INTO Critica (url_filme, url_critico, aprovacao) VALUES (?, ?, ?)",
            (
                critica_data['url_filme'],
                critica_data['url_critico'],
                1 if critica_data.get('aprovacao') else 0,
            )
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro no DB_MANAGER ao inserir critica: {e}")
        return False
    finally:
        conn.close()


def buscar_criticas_por_filme(url_filme):
    """
    Retorna uma lista de críticas para um filme, com nome do crítico e aprovação.
    """
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT c.url_critico, c.nome, cr.aprovacao FROM Critica cr JOIN Critico c ON cr.url_critico = c.url_critico WHERE cr.url_filme = ?",
            (url_filme,)
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                'url_critico': r[0],
                'nome': r[1],
                'aprovacao': bool(r[2]),
            })
        return result
    except sqlite3.Error as e:
        print(f"Erro no DB_MANAGER ao buscar criticas: {e}")
        return []
    finally:
        conn.close()

# Você pode adicionar funções futuras aqui, como:
# def buscar_critico_no_bd(url_critico): ...
# def inserir_critico(critico_data): ...
# def inserir_critica(critica_data): ...