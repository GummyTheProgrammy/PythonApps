import sqlite3
import json
import requests
from bs4 import BeautifulSoup
# Adicione outras bibliotecas de Web Scraping (como Selenium) aqui quando necessário

DB_NAME = 'elite_critics.db'

def conectar_bd():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def obter_info_basica_filme(slug_filme):
    """
    SIMULAÇÃO DE WEB SCRAPING: Obtém informações básicas do filme.
    Retorna um dicionário com os dados.
    """
    # A URL real usa underscore, como você observou
    url_base = f"https://www.rottentomatoes.com/m/{slug_filme}"
    print(f"\n--- Web Scraping I: {url_base} ---")
    
    # --- SIMULAÇÃO DE DADOS PARA TWILIGHT (2008) ---
    if slug_filme == 'twilight':
        return {
            'url_filme': '/m/twilight',
            'nome': 'Twilight (2008)',
            'nota_rt': 49,  # Pontuação real: 49%
            'generos': 'Fantasy, Romance, Drama, Adventure'
        }
    
    # Em um programa real, você faria a requisição aqui
    print("Implementação futura: Requisição HTTP para a URL do filme.")
    return None

def inserir_filme(filme_data):
    """Insere ou atualiza os dados do filme na tabela Filme."""
    conn = conectar_bd()
    print ("Conectado ao banco de dados!")
    cursor = conn.cursor()
    try:
        # Usamos REPLACE INTO para garantir que a chave única (url_filme) seja respeitada
        cursor.execute("""
            REPLACE INTO Filme (url_filme, nome, nota_rt, generos, nota_ndci, nota_ndcii)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            filme_data['url_filme'],
            filme_data['nome'],
            filme_data['nota_rt'],
            filme_data['generos'],
            None, # NDCI - Em Construção
            None  # NDCII - Em Construção
        ))
        conn.commit()
        print(f"Filme '{filme_data['nome']}' inserido/atualizado com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao inserir filme: {e}")
    finally:
        conn.close()

def main():
    """
    Função principal do Elite Critics.
    """
    # --- Passo 1: Entrada do Usuário (Simulada) ---
    filme_slug = 'twilight'
    print(f"🎬 Iniciando análise para o filme: {filme_slug}")

    # --- Passo 2: Web Scraping I e Inserção na BD ---
    filme_data = obter_info_basica_filme(filme_slug)
    
    if not filme_data:
        print("Erro: Não foi possível obter dados básicos do filme.")
        return

    inserir_filme(filme_data)
    
    # --- Passo 3: Apresentação das Notas ---
    print("\n" + "="*50)
    print(f"🏆 Resultados de Elite Critics para: {filme_data['nome']}")
    print("="*50)
    
    print(f"1. Tomatometer (Rotten Tomatoes Original): {filme_data['nota_rt']}%")
    
    # O Popcornmeter precisaria de outro Web Scraping
    print("2. Popcornmeter (Audience Score Original): 59% (SIMULAÇÃO)")
    
    print("\n--- Cálculos Recalculados ---")
    print("3. Nota dos Críticos I - No Room for Noobies (NDCI): Em Breve/Construção")
    print("4. Nota dos Críticos II - Hierarchy (NDCII): Em Breve/Construção")
    
    # --- Passos Futuros (Comentados para evitar erro de código) ---
    # print("\n--- Próximos Passos (Web Scraping II & Processamento) ---")
    # 1. Chamar Web Scraping II (Reviews): Obter lista de críticos e notas.
    # 2. Iniciar Laço 1 (Por Crítico): 
    #    - Se crítico novo, chamar Web Scraping III para lista de filmes.
    #    - Iniciar Laço 2 (Por Filme Avaliado) e consultar/scraping a tabela Filme para obter Gênero e calcular Experiência/Rank.
    # 3. Calcular NDCI e NDCII.

if __name__ == '__main__':
    # Garante que o banco de dados existe antes de tentar rodar o programa principal
    try:
        conectar_bd().close()
    except:
        print("Erro: O arquivo 'elite_critics.db' pode não existir. Rode 'CreateTables.py' primeiro.")

    main()