"""
core.matriz
===========

Pipeline de construcao da "Matriz de Expertise": para cada critico da
base limpa gerada pelo projeto anterior (`rt_etl`), calcula quantos
filmes distintos ele analisou em cada genero e em cada decada de
lancamento, e classifica esse volume em um nivel de expertise.

Este modulo nao realiza nenhuma chamada a `print`, `input` ou qualquer
API de interface — toda comunicacao com a camada de apresentacao ocorre
por meio de um `callback_progresso(fracao: float, mensagem: str)`
opcional, no mesmo padrao adotado em `rt_etl.core.etl`. Isso permite
reutilizar este nucleo tanto na interface de linha de comando
(`main.py`) quanto em uma futura interface web empacotada com EEL.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

import pandas as pd

from . import models

FRACAO_APOS_CARGA_DIMENSOES = 0.05
FRACAO_APOS_LEITURA_REGISTROS = 0.85
FRACAO_APOS_AGREGACAO = 0.90

TAMANHO_LOTE_PADRAO = 100_000


class BaseIncompletaError(Exception):
    """Levantada quando a pasta selecionada nao contem os tres arquivos esperados."""


@dataclass(frozen=True)
class LimiaresNivel:
    """
    Faixas numericas de classificacao de nivel de expertise. Os tres
    primeiros campos definem os limites superiores de cada faixa (o
    limite superior da ultima faixa nomeada e implicito: qualquer
    quantidade acima de `limite_especialista_max` recebe `rotulo_topo`).
    """
    limite_novato_max: int
    limite_entusiasta_max: int
    limite_especialista_max: int
    rotulo_topo: str


def classificar_nivel(quantidade: int, limiares: LimiaresNivel, tratar_zero_como_novato: bool) -> str:
    """
    Classifica uma quantidade de filmes analisados em um rotulo de nivel,
    de acordo com `limiares`.

    Quando `quantidade` e zero e `tratar_zero_como_novato` e False (padrao),
    retorna string vazia em vez de "Novato": um critico que nunca analisou
    nenhum filme de um genero/decada especifico e tratado como "nao
    aplicavel" para essa coluna, em vez de receber uma classificacao. Esse
    comportamento e ajustavel pelo chamador.
    """
    if quantidade <= 0 and not tratar_zero_como_novato:
        return ""
    if quantidade <= limiares.limite_novato_max:
        return "Novato"
    if quantidade <= limiares.limite_entusiasta_max:
        return "Entusiasta"
    if quantidade <= limiares.limite_especialista_max:
        return "Especialista"
    return limiares.rotulo_topo


@dataclass
class ResultadoMatriz:
    colunas_genero: list = field(default_factory=list)
    colunas_decada: list = field(default_factory=list)
    total_criticos: int = 0
    total_filmes: int = 0
    total_registros_lidos: int = 0
    caminho_saida_csv: str = ""
    caminho_saida_html: str = ""


class ConstrutorMatrizExpertise:
    """Orquestra a leitura da base limpa, a agregacao e a exportacao da matriz."""

    def __init__(
        self,
        limiares_genero: LimiaresNivel,
        limiares_decada: LimiaresNivel,
        tratar_zero_como_novato: bool = False,
        tamanho_lote: int = TAMANHO_LOTE_PADRAO,
    ):
        self.limiares_genero = limiares_genero
        self.limiares_decada = limiares_decada
        self.tratar_zero_como_novato = tratar_zero_como_novato
        self.tamanho_lote = tamanho_lote

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------
    def construir(
        self,
        pasta_base: str,
        pasta_destino: str,
        callback_progresso=None,
    ) -> ResultadoMatriz:
        caminho_critico, caminho_filme, caminho_registro = self._validar_pasta_base(pasta_base)
        os.makedirs(pasta_destino, exist_ok=True)

        self._notificar(callback_progresso, 0.0, "Carregamento das entidades Critico e Filme iniciado.")
        criticos = self._carregar_criticos(caminho_critico)
        filmes = self._carregar_filmes(caminho_filme)
        self._notificar(
            callback_progresso, FRACAO_APOS_CARGA_DIMENSOES,
            "Entidades Critico e Filme carregadas. Leitura dos registros de critica iniciada."
        )

        filmes_por_critico = self._ler_registros(caminho_registro, callback_progresso)

        self._notificar(callback_progresso, FRACAO_APOS_LEITURA_REGISTROS, "Agregacao por genero e decada iniciada.")
        colunas_genero, colunas_decada = self._extrair_colunas(filmes)
        linhas = self._agregar(criticos, filmes, filmes_por_critico, colunas_genero, colunas_decada)

        self._notificar(callback_progresso, FRACAO_APOS_AGREGACAO, "Exportacao dos arquivos de saida iniciada.")

        caminho_csv = os.path.join(pasta_destino, models.NOME_ARQUIVO_SAIDA_CSV)
        caminho_html = os.path.join(pasta_destino, models.NOME_ARQUIVO_SAIDA_HTML)
        self._exportar_csv(caminho_csv, linhas, colunas_genero, colunas_decada)

        from . import relatorio_html
        relatorio_html.gerar_relatorio(
            caminho_html, linhas, colunas_genero, colunas_decada,
            self.limiares_genero, self.limiares_decada,
        )

        self._notificar(callback_progresso, 1.0, "Processamento concluido.")

        return ResultadoMatriz(
            colunas_genero=colunas_genero,
            colunas_decada=colunas_decada,
            total_criticos=len(criticos),
            total_filmes=len(filmes),
            total_registros_lidos=sum(len(v) for v in filmes_por_critico.values()),
            caminho_saida_csv=caminho_csv,
            caminho_saida_html=caminho_html,
        )

    # ------------------------------------------------------------------
    # Etapas internas
    # ------------------------------------------------------------------
    def _validar_pasta_base(self, pasta_base: str) -> tuple[str, str, str]:
        caminho_critico = os.path.join(pasta_base, models.NOME_ARQUIVO_CRITICO)
        caminho_filme = os.path.join(pasta_base, models.NOME_ARQUIVO_FILME)
        caminho_registro = os.path.join(pasta_base, models.NOME_ARQUIVO_REGISTRO_CRITICA)

        faltantes = [
            caminho for caminho in (caminho_critico, caminho_filme, caminho_registro)
            if not os.path.isfile(caminho)
        ]
        if faltantes:
            raise BaseIncompletaError(
                "A pasta selecionada nao contem a base limpa esperada. Arquivos ausentes: "
                f"{faltantes}"
            )
        return caminho_critico, caminho_filme, caminho_registro

    def _carregar_criticos(self, caminho_critico: str) -> dict[int, dict]:
        tabela = pd.read_csv(caminho_critico, dtype=str)
        criticos = {}
        for linha in tabela.itertuples(index=False):
            dados = linha._asdict()
            critico_id = int(dados["critico_id"])
            criticos[critico_id] = {
                "nome_critico": dados.get("nome_critico") or "",
                "top_critic": str(dados.get("top_critic")).strip().lower() == "true",
            }
        return criticos

    def _carregar_filmes(self, caminho_filme: str) -> dict[int, dict]:
        tabela = pd.read_csv(caminho_filme, dtype=str)
        filmes = {}
        for linha in tabela.itertuples(index=False):
            dados = linha._asdict()
            filme_id = int(dados["filme_id"])
            genero_bruto = dados.get("genero")
            generos = []
            if isinstance(genero_bruto, str) and genero_bruto.strip():
                generos = [g.strip() for g in genero_bruto.split(",") if g.strip()]
            decada = dados.get("decada_lancamento")
            decada = decada.strip() if isinstance(decada, str) and decada.strip() else None
            filmes[filme_id] = {"generos": generos, "decada": decada}
        return filmes

    def _ler_registros(self, caminho_registro: str, callback_progresso) -> dict[int, set]:
        """
        Le a tabela de fatos em lotes e retorna, para cada critico, o
        conjunto de filmes distintos que ele analisou (a deduplicacao via
        `set` garante que multiplas criticas do mesmo critico para o
        mesmo filme contem como um unico filme analisado).
        """
        filmes_por_critico: dict[int, set] = {}
        tamanho_arquivo = max(os.path.getsize(caminho_registro), 1)

        with open(caminho_registro, "r", encoding="utf-8", newline="") as arquivo:
            leitor = pd.read_csv(
                arquivo,
                chunksize=self.tamanho_lote,
                usecols=models.COLUNAS_REGISTRO_CRITICA_USO,
                dtype=str,
            )
            for lote in leitor:
                for critico_id, filme_id in zip(lote["critico_id"], lote["filme_id"]):
                    if pd.isna(critico_id) or pd.isna(filme_id):
                        continue
                    critico_id = int(critico_id)
                    filme_id = int(filme_id)
                    filmes_por_critico.setdefault(critico_id, set()).add(filme_id)

                fracao_leitura = min(arquivo.tell() / tamanho_arquivo, 1.0)
                fracao_total = (
                    FRACAO_APOS_CARGA_DIMENSOES
                    + (FRACAO_APOS_LEITURA_REGISTROS - FRACAO_APOS_CARGA_DIMENSOES) * fracao_leitura
                )
                total_lido = sum(len(v) for v in filmes_por_critico.values())
                self._notificar(
                    callback_progresso, fracao_total,
                    f"Leitura dos registros de critica em andamento ({total_lido} pares critico/filme unicos)."
                )

        return filmes_por_critico

    def _extrair_colunas(self, filmes: dict[int, dict]) -> tuple[list, list]:
        generos_existentes = set()
        decadas_existentes = set()
        for info in filmes.values():
            generos_existentes.update(info["generos"])
            if info["decada"]:
                decadas_existentes.add(info["decada"])

        colunas_genero = sorted(generos_existentes)
        colunas_decada = sorted(decadas_existentes, key=lambda d: int(d.rstrip("s")))
        return colunas_genero, colunas_decada

    def _agregar(
        self,
        criticos: dict[int, dict],
        filmes: dict[int, dict],
        filmes_por_critico: dict[int, set],
        colunas_genero: list,
        colunas_decada: list,
    ) -> list[dict]:
        linhas = []
        for critico_id, dados_critico in criticos.items():
            ids_filmes = filmes_por_critico.get(critico_id, set())

            contagem_genero = {genero: 0 for genero in colunas_genero}
            contagem_decada = {decada: 0 for decada in colunas_decada}

            for filme_id in ids_filmes:
                info_filme = filmes.get(filme_id)
                if info_filme is None:
                    continue
                for genero in info_filme["generos"]:
                    if genero in contagem_genero:
                        contagem_genero[genero] += 1
                if info_filme["decada"] and info_filme["decada"] in contagem_decada:
                    contagem_decada[info_filme["decada"]] += 1

            linha = {
                "critico_id": critico_id,
                "nome_critico": dados_critico["nome_critico"],
                "top_critic": dados_critico["top_critic"],
                "total_filmes_analisados": len(ids_filmes),
            }
            for genero in colunas_genero:
                linha[genero] = classificar_nivel(
                    contagem_genero[genero], self.limiares_genero, self.tratar_zero_como_novato
                )
            for decada in colunas_decada:
                linha[decada] = classificar_nivel(
                    contagem_decada[decada], self.limiares_decada, self.tratar_zero_como_novato
                )
            linhas.append(linha)

        linhas.sort(key=lambda l: l["nome_critico"].lower())
        return linhas

    def _exportar_csv(self, caminho_csv: str, linhas: list, colunas_genero: list, colunas_decada: list) -> None:
        cabecalho = ["critico_id", "nome_critico", "top_critic", "total_filmes_analisados"] + colunas_genero + colunas_decada
        with open(caminho_csv, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(cabecalho)
            for linha in linhas:
                escritor.writerow([linha[coluna] for coluna in cabecalho])

    @staticmethod
    def _notificar(callback_progresso, fracao: float, mensagem: str) -> None:
        if callback_progresso is not None:
            callback_progresso(fracao, mensagem)
