# 🎬 Elite Critics - Blueprint do Projeto

O Elite Critics é um sistema de classificação de filmes que recalcula a pontuação do Tomatometer (Críticos) do Rotten Tomatoes (RT), atribuindo pesos diferentes às críticas com base na experiência e ranqueamento do crítico em gêneros específicos.

## ⚙️ Entrada do Programa

* **Nome do Filme:** O nome (ou *slug*) do filme a ser analisado (Ex: `twilight` para o filme de 2008).

## 🗄️ Estrutura da Base de Dados (SQLite)

* **Convenção:** Nomes de tabelas em **singular** (`Filme`, `Critico`, `Critica`).
* **Tabela Filme:** Armazena dados do filme.
    * `url_filme (TEXT) (PK)`: Chave primária. Ex: `/m/twilight` ou `/m/1082855-twilight`.
    * `nome (TEXT)`: Nome completo do filme.
    * `nota_rt (INTEGER)`: Pontuação Tomatometer original do RT.
    * `nota_popcornmeter (INTEGER)`: Pontuação Popcornmeter original do RT.
    * `nota_ndci (REAL)`: Nota dos Críticos I - *No Room for Noobies* (Em Construção).
    * `nota_ndcii (REAL)`: Nota dos Críticos II - *Hierarchy* (Em Construção).
    * `generos (TEXT)`: Gêneros do filme, separados por vírgula (ex: 'Kids & Family, Musical, Fantasy').
* **Tabela Critico:** Armazena dados e experiência do crítico.
    * `url_critico (TEXT) (PK)`: Chave primária. Ex: `/critics/nome-do-critico/movies`.
    * `nome (TEXT)`: Nome completo do crítico.
    * `experiencia_genero (TEXT)`: JSON ou string serializada que armazena a experiência por gênero (ex: `{"Fantasy": 55, "Musical": 2, ...}`).
    * `rank_genero (TEXT)`: JSON ou string serializada que armazena o ranking por gênero (ex: `{"Fantasy": 3, "Musical": 0, ...}`).
* **Tabela Critica:** Armazena as avaliações de cada crítico.
    * `id (INTEGER) (PK)`: Chave primária incremental.
    * `url_critico (TEXT) (FK)`: Chave estrangeira para a tabela `Critico`.
    * `url_filme (TEXT) (FK)`: Chave estrangeira para a tabela `Filme`.
    * `aprovacao (BOOLEAN)`: `True` (Fresh/Positivo) ou `False` (Rotten/Negativo).

## 🗺️ Fluxo de Web Scraping e Processamento

1.  **Entrada:** Usuário insere o `nome_do_filme`.
2.  **Web Scraping I (Filme de Entrada):**
    * URL: `https://www.rottentomatoes.com/m/nome_do_filme` (usando `_`).
    * **Ação:**
        * Obter `nota_rt`, `generos` e URL real (*slug*) do filme (lidando com duplicação, ex: `twilight` vs `1082855-twilight`).
        * **Checar Cache/BD:** Usar a URL como chave para verificar se o filme já existe. Se não existir, salvar na tabela **Filme**.
3.  **Web Scraping II (Reviews):**
    * URL: `https://www.rottentomatoes.com/m/nome_do_filme/reviews`.
    * **Ação:**
        * Obter a lista de todos os críticos e sua `aprovacao (bool)` para o filme de entrada.
        * **Atenção:** Lidar com a paginação (*Load More*) para carregar todas as críticas.
4.  **Processamento e Web Scraping III (Experiência do Crítico):**
    * **Laço 1 (Por Crítico):** Para cada crítico encontrado:
        * **Checar Cache/BD:** Usar a URL do crítico para verificar se o crítico já existe e se a experiência por gênero foi calculada.
        * **Se Crítico NOVO:**
            * Web Scraping III: Acessar `https://www.rottentomatoes.com/critics/nome-do-critico/movies` (usando `-`).
            * **Atenção:** Lidar com a paginação (*Load More*) para obter a lista completa de filmes avaliados por este crítico.
            * **Laço 2 (Por Filme Avaliado):** Para cada filme avaliado:
                * Obter a URL do filme.
                * **Consulta BD Local:** Buscar o gênero do filme na tabela **Filme**.
                * **Se Gênero NÃO ENCONTRADO:** Fazer *Web Scraping* pontual da página do filme e salvar gênero na tabela **Filme**.
                * **Calcular EXP:** Se os gêneros do filme avaliado e o filme de entrada (`#1`) se cruzarem (mesmo que apenas um), incrementar a experiência do crítico naquele(s) gênero(s).
            * Calcular **Rank** do crítico com base na experiência por gênero e salvar na tabela **Critico**.
5.  **Cálculo da Pontuação (Output):**
    * **NDCI (Em Breve):** Recalcular a nota excluindo as críticas de críticos Rank 0 no gênero(s) relevante(s).
    * **NDCII (Em Breve):** Recalcular a nota aplicando pesos conforme o Rank do crítico no gênero(s) relevante(s).

## 🏆 Saída

* Tomatometer (RT)
* Popcornmeter (RT)
* Nota dos críticos I - no room for noobies (NDCI) **(Em Breve/Construção)**
* Nota dos críticos II - hierarchy (NDCII) **(Em Breve/Construção)**

---

### Contribuições

Contribuições para o EcomReport são bem-vindas! Você pode:
- Adicionar novos recursos (por exemplo, tipos de gráficos adicionais, filtros de dados).

- Melhorar o processamento de dados ou a interface do usuário/experiência do usuário.

- Enviar problemas ou solicitações de pull request via GitHub.

Siga as diretrizes no repositório principal do `PythonApps` (`../README.md`) para contribuir.

---

### Licença

Este projeto está licenciado. Consulte o arquivo [LICENSE](../LICENSE) no repositório principal para obter detalhes.