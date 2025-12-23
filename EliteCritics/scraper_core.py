import requests
from bs4 import BeautifulSoup
import json

def trata_entrada(entrada_bruta):
    """
    Trata a entrada do usuário para gerar um slug de URL compatível com o Rotten Tomatoes.
    - Converte para minúsculas.
    - Troca espaços por underscores (_).
    """
    # Ex: "Twilight" -> "twilight", "Zootopia 2" -> "zootopia_2"
    return entrada_bruta.lower().replace(' ', '_')


def trata_entrada_critico(entrada_bruta):
    """
    Gera um slug para um crítico: minúsculas, espaços trocados por hífen '-'.
    Ex: "Roger Ebert" -> "roger-ebert"
    """
    return entrada_bruta.lower().replace(' ', '-')

def extrair_dados_basicos_filme(conteudo_html, url_base):
    """
    Extrai o nome, Tomatometer, Popcornmeter e Gêneros do HTML.
    Usa o bloco JSON-LD e o bloco de Scorecard para robustez.
    """
    soup = BeautifulSoup(conteudo_html, 'html.parser')
    filme_data = {'url_filme': url_base, 'nota_popcornmeter': None}
    
    # --- 1. Extração via JSON-LD (Fonte mais robusta para metadados) ---
    try:
        json_ld_script = soup.find('script', {'type': 'application/ld+json'})
        if json_ld_script:
            json_data = json.loads(json_ld_script.string)
            
            # Nome e Gêneros
            filme_data['nome'] = json_data.get('name')
            generos_list = json_data.get('genre', [])
            filme_data['generos'] = ', '.join(generos_list)
            
            # Nota RT (Tomatometer)
            agg_rating = json_data.get('aggregateRating')
            if agg_rating and 'ratingValue' in agg_rating:
                filme_data['nota_rt'] = int(agg_rating['ratingValue'])
            
    except Exception as e:
        print(f"Aviso: Falha na extração inicial via JSON-LD. Erro: {e}")

    # --- 2. Extração via JSON do Media Scorecard (Fonte robusta para notas) ---
    # Este bloco contém Popcornmeter e Tomatometer
    try:
        scorecard_script = soup.find('script', {'id': 'media-scorecard-json'})
        if scorecard_script:
            score_data = json.loads(scorecard_script.string)
            
            # Popcornmeter (Audience Score)
            audience_score = score_data.get('audienceScore', {}).get('score')
            if audience_score and audience_score.isdigit():
                filme_data['nota_popcornmeter'] = int(audience_score)
                
            # Tomatometer (Critico) - Confirmação/Sobrescrita
            critics_score = score_data.get('criticsScore', {}).get('score')
            if critics_score and critics_score.isdigit():
                filme_data['nota_rt'] = int(critics_score)
                
    except Exception as e:
        print(f"Aviso: Falha na extração de Popcornmeter/Tomatometer via Scorecard JSON. Erro: {e}")
        
    # Verifica se os dados mínimos foram extraídos
    if filme_data.get('nome') and filme_data.get('nota_rt') is not None and filme_data.get('generos'):
        return filme_data
    
    print("Erro: Dados críticos (Nome, Tomatometer ou Gênero) não foram encontrados.")
    return None

def web_scraping_basico_filme(slug_filme):
    """
    Executa a requisição HTTP e extrai os dados básicos do filme.
    """
    url_base = f"https://www.rottentomatoes.com/m/{slug_filme}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"\n--- Web Scraping I: {url_base} ---")
    
    try:
        response = requests.get(url_base, headers=headers, timeout=10)
        response.raise_for_status() 
        conteudo_html = response.text
        
        # Salva o HTML bruto para inspeção (opcional)
        nome_arquivo = f"{slug_filme}_raw_html.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_html)
        print(f"Conteúdo HTML baixado e salvo em: {nome_arquivo}")

        # Extrai os dados
        filme_data = extrair_dados_basicos_filme(conteudo_html, url_base)
        return filme_data

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para {url_base}: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o scraping: {e}")
        return None

def fetch_reviews_html(slug_filme):
    """
    Faz uma requisição à página de reviews do filme e salva o HTML bruto em
    um arquivo `{slug_filme}_reviews_raw_html.txt` para inspeção.
    Retorna o caminho do arquivo salvo em caso de sucesso, ou None em caso de erro.
    """
    url_reviews = f"https://www.rottentomatoes.com/m/{slug_filme}/reviews"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"\n--- Web Scraping Reviews: {url_reviews} ---")
    try:
        resp = requests.get(url_reviews, headers=headers, timeout=10)
        resp.raise_for_status()
        conteudo_html = resp.text

        nome_arquivo = f"{slug_filme}_reviews_raw_html.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_html)
        print(f"Conteúdo HTML de reviews salvo em: {nome_arquivo}")
        return nome_arquivo
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de reviews para {url_reviews}: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao salvar reviews: {e}")
        return None