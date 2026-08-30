"""
core.models
===========

Constantes de nomes de arquivo e colunas esperadas na base limpa gerada
pelo projeto anterior (`rt_etl`), consumida por este pipeline.
"""

from __future__ import annotations

NOME_ARQUIVO_CRITICO = "critico.csv"
NOME_ARQUIVO_FILME = "filme.csv"
NOME_ARQUIVO_REGISTRO_CRITICA = "registro_critica.csv"

COLUNAS_CRITICO = ["critico_id", "nome_critico", "top_critic"]
COLUNAS_FILME = ["filme_id", "rotten_tomatoes_link", "titulo_filme", "genero", "decada_lancamento"]
COLUNAS_REGISTRO_CRITICA_USO = ["filme_id", "critico_id"]

NOME_ARQUIVO_SAIDA_HTML = "matriz_expertise.html"
NOME_ARQUIVO_SAIDA_CSV = "matriz_expertise.csv"
