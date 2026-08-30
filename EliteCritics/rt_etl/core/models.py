"""
core.models
===========

Definicao do esquema das tres entidades que compoem a base de dados
limpa exportada por este projeto. Mantido isolado da logica de
processamento (`core.etl`) para que o mapeamento de colunas possa ser
consultado ou reaproveitado por outras camadas (por exemplo, uma futura
interface EEL) sem depender do restante do pipeline.

Entidades
---------
CRITICO
    Um critico de cinema, identificado pelo nome. Atributo `top_critic`
    representa se o critico e classificado pela Rotten Tomatoes como
    "top critic".

FILME
    Um filme, identificado pelo slug/link da Rotten Tomatoes
    (`rotten_tomatoes_link`). Quando ha correspondencia no arquivo
    `rotten_tomatoes_movies.csv`, a entidade tambem carrega titulo,
    genero(s) (mantidos como string separada por virgula, pois um filme
    pode ter mais de um genero) e a decada de lancamento derivada de
    `original_release_date`. Filmes sem correspondencia mantem esses tres
    campos vazios.

REGISTRO_CRITICA
    Uma critica especializada individual, associando um CRITICO a um
    FILME, com o veiculo de publicacao, o veredito (Fresh/Rotten), a
    nota original, a data e o texto da critica.
"""

from __future__ import annotations

# Colunas esperadas no arquivo de origem de criticas (schema da amostra fornecida).
COLUNAS_ORIGEM = [
    "rotten_tomatoes_link",
    "critic_name",
    "top_critic",
    "publisher_name",
    "review_type",
    "review_score",
    "review_date",
    "review_content",
]

# Colunas minimas exigidas no arquivo de origem de filmes
# (rotten_tomatoes_movies.csv), usado para enriquecer a entidade FILME com
# genero e decada de lancamento.
COLUNAS_ORIGEM_FILMES = [
    "rotten_tomatoes_link",
    "movie_title",
    "genres",
    "original_release_date",
]

# Esquema de saida: entidade CRITICO
COLUNAS_CRITICO = [
    "critico_id",
    "nome_critico",
    "top_critic",
]

# Esquema de saida: entidade FILME
COLUNAS_FILME = [
    "filme_id",
    "rotten_tomatoes_link",
    "titulo_filme",
    "genero",
    "decada_lancamento",
]

# Esquema de saida: entidade REGISTRO_CRITICA
COLUNAS_REGISTRO_CRITICA = [
    "registro_id",
    "filme_id",
    "critico_id",
    "publisher_name",
    "review_type",
    "review_score",
    "review_score_normalizado",
    "review_date",
    "review_content",
]

NOME_ARQUIVO_CRITICO = "critico.csv"
NOME_ARQUIVO_FILME = "filme.csv"
NOME_ARQUIVO_REGISTRO_CRITICA = "registro_critica.csv"
