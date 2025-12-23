from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.chrome.options import Options
import time


def fetch_full_reviews_html(slug_filme, wait=2.0, max_clicks=100):
    """
    Abre o Chrome em modo headless, navega até a página de reviews do filme,
    clica no botão 'Load More' até que ele desapareça (ou atinja max_clicks),
    salva o HTML final em `{slug_filme}_reviews_full_html.txt` e retorna o HTML.

    Retorna tuple (caminho_arquivo, html) ou (None, None) em caso de erro.
    """
    url_reviews = f"https://www.rottentomatoes.com/m/{slug_filme}/reviews"

    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    # Inicializa o driver; espera que chromedriver esteja no PATH
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        print(f"Erro ao iniciar o WebDriver: {e}")
        print("Verifique se o ChromeDriver está instalado e no PATH.")
        return None, None

    try:
        driver.get(url_reviews)
        time.sleep(wait)

        # Possíveis seletores do botão 'Load More' (variam ao longo do tempo)
        selectors = [
            'button.load-more',
            'button[data-qa="load-more-button"]',
            'button.js-load-more-btn',
            'button#reviews-load-more',
            '.load-more button',
            'button[data-load-more]',
            'rt-button[data-qa="load-more-btn"]',
            'div.load-more-container rt-button',
            'rt-button[data-LoadMoreManager]'
        ]

        clicks = 0
        while clicks < max_clicks:
            btn = None
            for sel in selectors:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, sel)
                    # Certifica-se que o botão esteja visível e clicável
                    if elem.is_displayed() and elem.is_enabled():
                        btn = elem
                        break
                except Exception:
                    continue

            if not btn:
                # Nenhum botão encontrado -> parar
                break

            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.2)
                # custom element click via JS to handle web components
                driver.execute_script("arguments[0].click();", btn)
            except ElementClickInterceptedException:
                # Talvez um overlay; tentar dar um pequeno scroll e tentar novamente
                driver.execute_script("window.scrollBy(0, -100);")
                time.sleep(0.5)
                try:
                    driver.execute_script("arguments[0].click();", btn)
                except Exception:
                    break
            except Exception:
                break

            clicks += 1
            time.sleep(wait)

            # verificar se o botão ainda existe/está visível (ou não possui a classe 'hide')
            still_there = False
            for sel in selectors:
                try:
                    elems = driver.find_elements(By.CSS_SELECTOR, sel)
                    for elem in elems:
                        cls_attr = (elem.get_attribute('class') or '')
                        # se o elemento não tem a classe 'hide' e está visível, ainda há mais para carregar
                        if 'hide' not in cls_attr and elem.is_displayed():
                            still_there = True
                            break
                    if still_there:
                        break
                except Exception:
                    continue

            if not still_there:
                break

        # Pegar o HTML final
        # Antes de pegar o HTML, anotar cada bloco de review com data-sentiment
        try:
            annotate_script = '''
            (function(){
                var reviewSelectors = [
                    'div.review_table .review_table_row',
                    'div.review_table .row',
                    'div.review_table_row',
                    'div.review_table__row',
                    'div.review_table div.review',
                    'article.review'
                ];
                var reviews = [];
                reviewSelectors.forEach(function(s){
                    document.querySelectorAll(s).forEach(function(el){ reviews.push(el); });
                });
                // remove duplicates
                reviews = reviews.filter(function(v,i,a){ return a.indexOf(v)===i; });

                reviews.forEach(function(r){
                    // procurar score-icon-critics dentro do bloco
                    var score = r.querySelector('score-icon-critics');
                    if(!score){
                        // procurar próximo score-icon-critics nos próximos irmãos
                        var node = r;
                        for(var i=0;i<10;i++){
                            if(!node) break;
                            node = node.nextElementSibling;
                            if(!node) break;
                            if(node.tagName && node.tagName.toLowerCase().indexOf('score-icon')===0){ score = node; break; }
                            var inner = node.querySelector ? node.querySelector('score-icon-critics') : null;
                            if(inner){ score = inner; break; }
                        }
                    }
                    if(score){
                        var s = score.getAttribute('sentiment') || score.getAttribute('data-sentiment') || '';
                        if(s){ r.setAttribute('data-sentiment', s); }
                    }
                });
            })();
            '''
            driver.execute_script(annotate_script)
        except Exception:
            # se anotação falhar, continuamos e retornamos o HTML bruto
            pass

        html = driver.page_source
        nome_arquivo = f"{slug_filme}_reviews_full_html.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML completo de reviews salvo em: {nome_arquivo}")
        return nome_arquivo, html

    except Exception as e:
        print(f"Erro no HeadlessNavigator ao coletar reviews: {e}")
        return None, None
    finally:
        try:
            driver.quit()
        except Exception:
            pass
