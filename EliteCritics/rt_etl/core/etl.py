"""
core.etl
========

Pipeline de transformacao da base de criticas da Rotten Tomatoes.

Fontes de origem
-----------------
1. Arquivo de criticas (`models.COLUNAS_ORIGEM`) — uma linha por critica
   especializada publicada.
2. Arquivo de filmes (`models.COLUNAS_ORIGEM_FILMES`) — uma linha por
   filme, usado apenas para enriquecer a entidade FILME com titulo,
   genero(s) e decada de lancamento. E opcional: na ausencia desse
   arquivo, a entidade FILME e gerada normalmente, apenas sem esses tres
   atributos.

Regras de negocio aplicadas
----------------------------
1. A saida contem exclusivamente tres entidades: CRITICO, FILME e
   REGISTRO_CRITICA (ver `core.models`).
2. Avaliacoes de publico sao excluidas. O esquema de origem das criticas
   nao contem avaliacoes de publico nem um campo diferenciador explicito;
   por isso, dois criterios sao aplicados de forma combinada e
   documentada:
     a. Registros sem `critic_name` preenchido nao correspondem a uma
        entidade CRITICO valida e sao excluidos.
     b. Verificacao defensiva de palavra-chave no campo de tipo/categoria
        da avaliacao (`review_type`, ver
        `core.utils.contem_indicio_de_publico`), para tornar o pipeline
        robusto a variacoes do arquivo de origem completo em relacao a
        amostra, sem incidir sobre nomes proprios de criticos ou
        veiculos de publicacao.
3. Registros orfaos sao impossiveis por construcao: as entidades FILME e
   CRITICO sao derivadas exclusivamente dos registros de critica que
   permanecem apos a limpeza (passo 2). Nao existe, portanto, filme sem
   critica ou critico sem registro na base final.

Observacao de arquitetura
--------------------------
Este modulo nao realiza nenhuma chamada a `print`, `input` ou qualquer
API de interface. Toda comunicacao com a camada de apresentacao ocorre
por meio de um `callback_progresso(fracao: float, mensagem: str)`
opcional. Essa separacao permite que o mesmo nucleo seja reutilizado por
uma interface de linha de comando (`main.py`) ou por uma futura interface
web empacotada com EEL, bastando substituir o callback.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

import pandas as pd

from . import models, utils

TAMANHO_LOTE_PADRAO = 50_000

# Fracao do progresso total reservada ao carregamento da dimensao de
# filmes (etapa rapida, pois esse arquivo e muito menor que o de
# criticas). O restante e distribuido proporcionalmente a leitura do
# arquivo de criticas.
FRACAO_PROGRESSO_DIMENSAO_FILME = 0.05


class EsquemaInvalidoError(Exception):
    """Levantada quando um arquivo de origem nao possui as colunas esperadas."""


@dataclass
class EstatisticasProcessamento:
    linhas_lidas: int = 0
    linhas_excluidas_sem_critico: int = 0
    linhas_excluidas_indicio_publico: int = 0
    registros_validos: int = 0
    total_criticos: int = 0
    total_filmes: int = 0
    filmes_sem_metadados: int = 0
    caminhos_saida: dict = field(default_factory=dict)


class RottenTomatoesETL:
    """Orquestra a leitura em lotes, limpeza, deduplicacao e exportacao."""

    def __init__(self, tamanho_lote: int = TAMANHO_LOTE_PADRAO):
        self.tamanho_lote = tamanho_lote

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------
    def processar(
        self,
        caminho_origem_criticas: str,
        diretorio_destino: str,
        caminho_origem_filmes: str | None = None,
        callback_progresso=None,
    ) -> EstatisticasProcessamento:
        """
        Executa o pipeline completo.

        Parametros
        ----------
        caminho_origem_criticas : str
            Caminho do CSV de criticas (esquema `models.COLUNAS_ORIGEM`).
        diretorio_destino : str
            Diretorio onde os tres arquivos de saida serao gravados.
        caminho_origem_filmes : str, opcional
            Caminho do CSV de filmes (esquema `models.COLUNAS_ORIGEM_FILMES`),
            usado para enriquecer a entidade FILME com titulo, genero(s) e
            decada de lancamento. Quando omitido, a entidade FILME e gerada
            sem esses tres atributos.
        callback_progresso : callable, opcional
            Funcao `(fracao: float, mensagem: str) -> None` chamada
            periodicamente durante o processamento.

        Retorna
        -------
        EstatisticasProcessamento
        """
        self._validar_arquivo_criticas(caminho_origem_criticas)
        if caminho_origem_filmes is not None:
            self._validar_arquivo_filmes(caminho_origem_filmes)
        os.makedirs(diretorio_destino, exist_ok=True)

        estatisticas = EstatisticasProcessamento()
        tamanho_arquivo = max(os.path.getsize(caminho_origem_criticas), 1)

        mapa_criticos: dict[str, dict] = {}
        mapa_filmes: dict[str, dict] = {}

        caminho_registro = os.path.join(diretorio_destino, models.NOME_ARQUIVO_REGISTRO_CRITICA)
        caminho_critico = os.path.join(diretorio_destino, models.NOME_ARQUIVO_CRITICO)
        caminho_filme = os.path.join(diretorio_destino, models.NOME_ARQUIVO_FILME)

        metadados_filmes: dict[str, dict] = {}
        if caminho_origem_filmes is not None:
            self._notificar(callback_progresso, 0.0, "Carregamento dos metadados de filmes iniciado.")
            metadados_filmes = self._carregar_metadados_filmes(caminho_origem_filmes)

        fracao_inicial = FRACAO_PROGRESSO_DIMENSAO_FILME if caminho_origem_filmes is not None else 0.0
        self._notificar(
            callback_progresso, fracao_inicial,
            "Leitura e processamento do arquivo de criticas iniciados."
        )

        with open(caminho_origem_criticas, "r", encoding="utf-8", newline="") as arquivo_entrada, \
                open(caminho_registro, "w", encoding="utf-8", newline="") as arquivo_registro:

            escritor_registro = csv.writer(arquivo_registro)
            escritor_registro.writerow(models.COLUNAS_REGISTRO_CRITICA)

            leitor = pd.read_csv(
                arquivo_entrada,
                chunksize=self.tamanho_lote,
                dtype=str,
                keep_default_na=True,
                na_filter=True,
            )

            for lote in leitor:
                self._processar_lote(
                    lote, mapa_criticos, mapa_filmes, metadados_filmes, escritor_registro, estatisticas
                )
                fracao_leitura = min(arquivo_entrada.tell() / tamanho_arquivo, 1.0)
                fracao_total = fracao_inicial + (1 - fracao_inicial) * fracao_leitura
                self._notificar(
                    callback_progresso, fracao_total,
                    f"Processamento em andamento ({estatisticas.linhas_lidas} linhas lidas)."
                )

        self._notificar(callback_progresso, 1.0, "Processamento das fontes de origem concluido.")

        self._exportar_criticos(caminho_critico, mapa_criticos)
        self._exportar_filmes(caminho_filme, mapa_filmes)

        estatisticas.total_criticos = len(mapa_criticos)
        estatisticas.total_filmes = len(mapa_filmes)
        estatisticas.caminhos_saida = {
            "critico": caminho_critico,
            "filme": caminho_filme,
            "registro_critica": caminho_registro,
        }
        return estatisticas

    # ------------------------------------------------------------------
    # Etapas internas
    # ------------------------------------------------------------------
    def _validar_arquivo_criticas(self, caminho: str) -> None:
        if not os.path.isfile(caminho):
            raise FileNotFoundError(f"Arquivo de criticas nao encontrado: {caminho}")

        cabecalho = pd.read_csv(caminho, nrows=0)
        colunas_faltantes = set(models.COLUNAS_ORIGEM) - set(cabecalho.columns)
        if colunas_faltantes:
            raise EsquemaInvalidoError(
                "O arquivo de criticas nao corresponde ao esquema esperado. "
                f"Colunas ausentes: {sorted(colunas_faltantes)}"
            )

    def _validar_arquivo_filmes(self, caminho: str) -> None:
        if not os.path.isfile(caminho):
            raise FileNotFoundError(f"Arquivo de filmes nao encontrado: {caminho}")

        cabecalho = pd.read_csv(caminho, nrows=0)
        colunas_faltantes = set(models.COLUNAS_ORIGEM_FILMES) - set(cabecalho.columns)
        if colunas_faltantes:
            raise EsquemaInvalidoError(
                "O arquivo de filmes nao corresponde ao esquema esperado. "
                f"Colunas ausentes: {sorted(colunas_faltantes)}"
            )

    def _carregar_metadados_filmes(self, caminho_origem_filmes: str) -> dict[str, dict]:
        """
        Carrega o arquivo de filmes por completo em memoria, indexado por
        `rotten_tomatoes_link`. Essa dimensao e tipicamente pequena (dezenas
        de milhares de filmes, no maximo) em comparacao com a tabela de
        fatos de criticas, o que torna essa abordagem adequada mesmo para
        volumes de origem grandes.
        """
        colunas_uso = list(models.COLUNAS_ORIGEM_FILMES)
        tabela = pd.read_csv(caminho_origem_filmes, dtype=str, usecols=colunas_uso)

        metadados: dict[str, dict] = {}
        for linha in tabela.itertuples(index=False):
            dados = linha._asdict()
            link = utils.normalizar_texto(dados.get("rotten_tomatoes_link"))
            if not link:
                continue
            metadados[link] = {
                "titulo_filme": utils.normalizar_texto(dados.get("movie_title")),
                "genero": ", ".join(utils.normalizar_generos(dados.get("genres"))) or None,
                "decada_lancamento": utils.normalizar_decada(dados.get("original_release_date")),
            }
        return metadados

    def _processar_lote(
        self,
        lote: pd.DataFrame,
        mapa_criticos: dict,
        mapa_filmes: dict,
        metadados_filmes: dict,
        escritor_registro,
        estatisticas: EstatisticasProcessamento,
    ) -> None:
        linhas_saida = []

        for linha in lote.itertuples(index=False):
            estatisticas.linhas_lidas += 1
            dados = linha._asdict()

            nome_critico = utils.normalizar_texto(dados.get("critic_name"))
            link_filme = utils.normalizar_texto(dados.get("rotten_tomatoes_link"))
            publisher = utils.normalizar_texto(dados.get("publisher_name"))
            tipo_review = utils.normalizar_texto(dados.get("review_type"))

            # Regra de negocio 2a: sem critico identificado, o registro nao
            # corresponde a uma critica especializada valida.
            if not nome_critico or not link_filme:
                estatisticas.linhas_excluidas_sem_critico += 1
                continue

            # Regra de negocio 2b: verificacao defensiva de indicios de
            # avaliacao de publico no campo de tipo/categoria.
            if utils.contem_indicio_de_publico(tipo_review):
                estatisticas.linhas_excluidas_indicio_publico += 1
                continue

            top_critic = utils.normalizar_booleano(dados.get("top_critic"))
            if nome_critico not in mapa_criticos:
                mapa_criticos[nome_critico] = {
                    "critico_id": len(mapa_criticos) + 1,
                    "nome_critico": nome_critico,
                    "top_critic": top_critic,
                }
            critico_id = mapa_criticos[nome_critico]["critico_id"]

            if link_filme not in mapa_filmes:
                info_filme = metadados_filmes.get(link_filme)
                if info_filme is None:
                    estatisticas.filmes_sem_metadados += 1
                    info_filme = {"titulo_filme": None, "genero": None, "decada_lancamento": None}
                mapa_filmes[link_filme] = {
                    "filme_id": len(mapa_filmes) + 1,
                    "rotten_tomatoes_link": link_filme,
                    **info_filme,
                }
            filme_id = mapa_filmes[link_filme]["filme_id"]

            nota_original = utils.normalizar_texto(dados.get("review_score"))
            nota_normalizada = utils.normalizar_score(nota_original)
            data_review = utils.normalizar_data(dados.get("review_date"))
            conteudo = utils.normalizar_texto(dados.get("review_content"))

            linhas_saida.append([
                estatisticas.registros_validos + len(linhas_saida) + 1,
                filme_id,
                critico_id,
                publisher,
                tipo_review,
                nota_original,
                nota_normalizada,
                data_review,
                conteudo,
            ])

        if linhas_saida:
            escritor_registro.writerows(linhas_saida)
            estatisticas.registros_validos += len(linhas_saida)

    def _exportar_criticos(self, caminho_critico: str, mapa_criticos: dict) -> None:
        with open(caminho_critico, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(models.COLUNAS_CRITICO)
            for critico in mapa_criticos.values():
                escritor.writerow([
                    critico["critico_id"],
                    critico["nome_critico"],
                    critico["top_critic"],
                ])

    def _exportar_filmes(self, caminho_filme: str, mapa_filmes: dict) -> None:
        with open(caminho_filme, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(models.COLUNAS_FILME)
            for filme in mapa_filmes.values():
                escritor.writerow([
                    filme["filme_id"],
                    filme["rotten_tomatoes_link"],
                    filme["titulo_filme"],
                    filme["genero"],
                    filme["decada_lancamento"],
                ])

    @staticmethod
    def _notificar(callback_progresso, fracao: float, mensagem: str) -> None:
        if callback_progresso is not None:
            callback_progresso(fracao, mensagem)
