import json
from db_manager import conectar_bd, buscar_filme_no_bd, inserir_filme
from scraper_core import trata_entrada, trata_entrada_critico, web_scraping_basico_filme, fetch_reviews_html
from HeadlessNavigator import fetch_full_reviews_html
from bs4 import BeautifulSoup
from db_manager import buscar_criticas_por_filme, buscar_critico_por_url, inserir_critico, inserir_critica

# Nota: O DB_NAME agora é tratado por `db_manager.py` (conectar_bd)

def main():
    """
    Função principal do Elite Critics.
    Usa `scraper_core` para gerar o slug e fazer o scraping quando necessário,
    e `db_manager` para cache/inserção no banco.
    """
    # --- Passo 1: Entrada do Usuário ---
    entrada_bruta = input("Digite o nome do filme (Ex: Twilight ou Zootopia 2): ")
    
    # Gera o slug para a URL usando `scraper_core.trata_entrada`
    slug_filme = trata_entrada(entrada_bruta)
    print(f"Slug gerado para Web Scraping: {slug_filme}")

    # Monta a URL canônica (usada como chave no DB)
    url_base = f"https://www.rottentomatoes.com/m/{slug_filme}"

    # --- Passo 2: Verifica cache via `db_manager` ---
    filme_data = buscar_filme_no_bd(url_base)
    if filme_data:
        print(f"Filme '{filme_data['nome']}' encontrado no cache do BD. Pulando Web Scraping.")
    else:
        # --- Passo 3: Web Scraping via `scraper_core` ---
        filme_data = web_scraping_basico_filme(slug_filme)
        if not filme_data:
            print("Análise abortada: Não foi possível obter os dados completos do filme.")
            return

        # --- Passo 4: Inserir/Atualizar no BD via `db_manager.inserir_filme` ---
        inserir_filme(filme_data)

    # Antes de apresentar os dados: salvar HTML das reviews (opcional)
    # 1) Salvamos a versão simples via requests (fallback)
    try:
        fetch_reviews_html(slug_filme)
    except Exception as e:
        print(f"Aviso: falha ao obter/salvar reviews (requests): {e}")

    # 2) Tentar carregar todas as reviews via Selenium (HeadlessNavigator)
    full_path, full_html = fetch_full_reviews_html(slug_filme)
    reviews_html_to_parse = None
    if full_html:
        reviews_html_to_parse = full_html
    else:
        # fallback: tentar abrir o arquivo salvo pelo fetch_requests
        try:
            nome_arquivo = f"{slug_filme}_reviews_raw_html.txt"
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                reviews_html_to_parse = f.read()
        except Exception:
            reviews_html_to_parse = None

    # Se houver HTML de reviews, extrair e inserir no DB
    if reviews_html_to_parse:
        try:
            # Extrai críticas e insere nas tabelas Critico e Critica
            soup = BeautifulSoup(reviews_html_to_parse, 'html.parser')

            # Tentativas de seletores para encontrar blocos de reviews
            candidate_selectors = [
                'div.review_table .review_table_row',
                'div.review_table .row',
                'div.review_table_row',
                'div.review_table__row',
                'div.review_table div.review'
            ]

            review_elements = []
            for sel in candidate_selectors:
                found = soup.select(sel)
                if found:
                    review_elements = found
                    break

            # Fallback: procurar por elementos com atributo data-qa contendo 'review' ou por article.review
            if not review_elements:
                review_elements = soup.select("[data-qa*='review']") or soup.select('article.review')

            for r in review_elements:
                # Extrair nome do crítico
                critic_name = None
                # vários caminhos possíveis
                c = r.select_one('.critic-name') or r.select_one('.reviewer a') or r.select_one('.critic__link') or r.select_one('.reviewer')
                if c:
                    critic_name = c.get_text(strip=True)
                else:
                    # tentar um link interno
                    a = r.find('a')
                    if a:
                        critic_name = a.get_text(strip=True)

                if not critic_name:
                    continue

                # Extrair aprovação usando <score-icon-critics sentiment="POSITIVE"> preferencialmente
                aprovado = None

                def extract_sentiment_from_tag(tag):
                    if not tag:
                        return None
                    if getattr(tag, 'attrs', None):
                        # prioriza atributo 'sentiment'
                        if 'sentiment' in tag.attrs:
                            return str(tag.attrs.get('sentiment')).strip().upper()
                        # outras variações
                        for attr in ('data-sentiment', 'data-qa-sentiment'):
                            if attr in tag.attrs:
                                return str(tag.attrs.get(attr)).strip().upper()
                    return None

                sentiment = None

                # 1) Prioridade: checar se HeadlessNavigator anotou o bloco com data-sentiment
                sentiment = None
                try:
                    ds = r.get('data-sentiment')
                    if ds:
                        sentiment = str(ds).strip().upper()
                except Exception:
                    sentiment = None

                # 2) procurar tag específica dentro do bloco da review (fallback)
                if not sentiment:
                    score_tag = r.find('score-icon-critics')
                    if score_tag:
                        sentiment = extract_sentiment_from_tag(score_tag)

                # 2) se não encontrada, procurar pelo próximo tag <score-icon-critics> no documento
                if not sentiment:
                    try:
                        nxt = r.find_next('score-icon-critics')
                        if nxt:
                            sentiment = extract_sentiment_from_tag(nxt)
                    except Exception:
                        sentiment = None

                # 3) fallback: procurar descendentes com atributo sentiment
                if not sentiment:
                    tag_with_sent = r.find(attrs=lambda a: a and 'sentiment' in a)
                    if tag_with_sent:
                        sentiment = extract_sentiment_from_tag(tag_with_sent)

                # Mapear sentiment para booleano
                if sentiment:
                    if 'POS' in sentiment or sentiment == 'TRUE':
                        aprovado = True
                    elif 'NEG' in sentiment or sentiment == 'FALSE':
                        aprovado = False
                    else:
                        aprovado = None

                # Fallback final: heurística por classes ou ícone
                if aprovado is None:
                    cls_text = ' '.join(r.get('class') or [])
                    if 'fresh' in cls_text:
                        aprovado = True
                    elif 'rotten' in cls_text:
                        aprovado = False
                    else:
                        if r.select_one('.icon.fresh') or r.find('span', string=lambda s: s and 'Fresh' in s):
                            aprovado = True
                        elif r.select_one('.icon.rotten') or r.find('span', string=lambda s: s and 'Rotten' in s):
                            aprovado = False

                # Extrair texto da crítica (opcional)
                texto = None
                t = r.select_one('.the_review') or r.select_one('.review-text') or r.select_one('.content')
                if t:
                    texto = t.get_text(strip=True)

                # Gerar url_critico via trata_entrada_critico
                url_critico_slug = trata_entrada_critico(critic_name)
                url_critico = f"https://www.rottentomatoes.com/critic/{url_critico_slug}"

                # Inserir crítico/critica no DB (usa chave 'aprovacao' por compatibilidade com DB)
                try:
                    inserir_critico({'url_critico': url_critico, 'nome': critic_name})
                    inserir_critica({'url_filme': url_base, 'url_critico': url_critico, 'aprovacao': aprovado, 'texto': texto})
                except Exception as e:
                    print(f"Aviso: falha ao inserir critica no DB para {critic_name}: {e}")
        except Exception as e:
            print(f"Aviso: falha ao extrair/inserir reviews: {e}")

    # --- Apresentação das Notas ---
    print("\n" + "="*50)
    print(f"🏆 Resultados de Elite Critics para: {filme_data['nome']}")
    print(f"Gêneros: {filme_data.get('generos', 'N/A')}")
    print("="*50)

    print(f"1. Tomatometer (Rotten Tomatoes Original): **{filme_data.get('nota_rt', 'N/A')}%**")
    print(f"2. Popcornmeter (Audience Score Original): **{filme_data.get('nota_popcornmeter', 'N/A')}%**")
    print("\n--- Cálculos Recalculados ---")
    print("3. Nota dos Críticos I - No Room for Noobies (NDCI): **Em Breve/Construção**")
    print("4. Nota dos Críticos II - Hierarchy (NDCII): **Em Breve/Construção**")

    # Mostrar as reviews em modo tabela (nome do critico, filme, aprovação)
    try:
        criticas = buscar_criticas_por_filme(url_base)
        if criticas:
            print('\n' + '-'*40)
            print('Reviews:')
            print(f"{'Critico':30} | {'Filme':20} | {'Aprovado'}")
            print('-'*40)
            for c in criticas:
                nome = c.get('nome')[:30]
                aprovado_str = 'True' if c.get('aprovacao') else 'False'
                print(f"{nome:30} | {entrada_bruta:20} | {aprovado_str}")
            print('-'*40)
        else:
            print('\nNenhuma crítica encontrada no banco para exibir.')
    except Exception as e:
        print(f"Aviso: falha ao buscar/exibir criticas: {e}")

if __name__ == '__main__':
    try:
        conectar_bd().close()
    except Exception:
        print("Erro: O arquivo 'elite_critics.db' pode não existir. Rode 'CreateTables.py' primeiro.")

    main()