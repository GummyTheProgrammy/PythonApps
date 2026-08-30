"""
main.py
=======

Ponto de entrada da aplicacao de linha de comando (CMD) para limpeza da
base de criticas especializadas da Rotten Tomatoes.

Este arquivo contem apenas a orquestracao da interface de linha de
comando. Toda a logica de negocio reside em `core.etl`, e todo o acesso
a APIs nativas do Windows reside em `core.file_dialog` e
`core.console_ui`. Essa separacao de camadas e intencional: para uma
futura empacotagem com EEL, basta criar um novo arquivo de entrada que
importe `core.etl.RottenTomatoesETL` e encaminhe o progresso para a
interface web, sem qualquer alteracao no nucleo de processamento.

Fontes de origem esperadas na pasta selecionada
-------------------------------------------------
- Um arquivo .csv cujo nome contenha "critic_review" (ou equivalente):
  esquema `models.COLUNAS_ORIGEM`.
- Um arquivo .csv cujo nome contenha "movie" (ou equivalente), opcional:
  esquema `models.COLUNAS_ORIGEM_FILMES`. Usado para enriquecer a
  entidade FILME com titulo, genero(s) e decada de lancamento.
"""

from __future__ import annotations

import sys
import traceback

from core import console_ui
from core.etl import RottenTomatoesETL, EsquemaInvalidoError
from core.file_dialog import pick_folder, FileDialogUnavailableError
from core.utils import localizar_arquivo_por_padrao, ArquivoNaoEncontradoError

PADROES_ARQUIVO_CRITICAS = ["critic_review", "criticas", "criticas_especializadas"]
PADROES_ARQUIVO_FILMES = ["movie", "filme"]


def _requisitar_pasta_origem() -> str | None:
    console_ui.print_status(
        "Aguardando selecao, na janela do Windows, da pasta que contem os arquivos de origem "
        "(criticas e, opcionalmente, filmes)."
    )
    return pick_folder(title="Selecionar pasta com os arquivos de origem")


def _requisitar_pasta_destino() -> str | None:
    console_ui.print_status("Aguardando selecao do diretorio de destino na janela do Windows.")
    return pick_folder(title="Selecionar diretorio de destino para a base limpa")


def _resolver_arquivos_origem(pasta_origem: str) -> tuple[str, str | None]:
    caminho_criticas = localizar_arquivo_por_padrao(
        pasta_origem, PADROES_ARQUIVO_CRITICAS, "arquivo de criticas"
    )

    try:
        caminho_filmes = localizar_arquivo_por_padrao(
            pasta_origem, PADROES_ARQUIVO_FILMES, "arquivo de filmes"
        )
    except ArquivoNaoEncontradoError:
        console_ui.print_status(
            "Arquivo de filmes nao localizado na pasta de origem. A entidade FILME sera "
            "gerada sem titulo, genero e decada de lancamento."
        )
        caminho_filmes = None

    return caminho_criticas, caminho_filmes


def _callback_progresso(fracao: float, mensagem: str) -> None:
    console_ui.render_progress_bar(fracao, label="Processamento")


def _exibir_resumo(estatisticas) -> None:
    console_ui.print_section("Resumo do processamento")
    console_ui.print_status(f"Linhas lidas no arquivo de criticas: {estatisticas.linhas_lidas}")
    console_ui.print_status(
        f"Linhas excluidas por ausencia de critico identificado: "
        f"{estatisticas.linhas_excluidas_sem_critico}"
    )
    console_ui.print_status(
        f"Linhas excluidas por indicio de avaliacao de publico: "
        f"{estatisticas.linhas_excluidas_indicio_publico}"
    )
    console_ui.print_status(f"Registros de critica validos exportados: {estatisticas.registros_validos}")
    console_ui.print_status(f"Total de criticos distintos: {estatisticas.total_criticos}")
    console_ui.print_status(f"Total de filmes distintos: {estatisticas.total_filmes}")
    console_ui.print_status(
        f"Filmes sem correspondencia no arquivo de filmes (sem titulo/genero/decada): "
        f"{estatisticas.filmes_sem_metadados}"
    )

    console_ui.print_section("Arquivos gerados")
    for entidade, caminho in estatisticas.caminhos_saida.items():
        console_ui.print_status(f"{entidade}: {caminho}")


def main() -> int:
    console_ui.enable_ansi_support()
    console_ui.print_section("Limpeza da base de criticas especializadas - Rotten Tomatoes")

    try:
        pasta_origem = _requisitar_pasta_origem()
    except FileDialogUnavailableError as erro:
        console_ui.print_status(f"Erro: {erro}")
        return 1

    if not pasta_origem:
        console_ui.print_status("Operacao cancelada: nenhuma pasta de origem selecionada.")
        return 1

    try:
        caminho_criticas, caminho_filmes = _resolver_arquivos_origem(pasta_origem)
    except ArquivoNaoEncontradoError as erro:
        console_ui.print_status(f"Erro: {erro}")
        return 1

    try:
        pasta_destino = _requisitar_pasta_destino()
    except FileDialogUnavailableError as erro:
        console_ui.print_status(f"Erro: {erro}")
        return 1

    if not pasta_destino:
        console_ui.print_status("Operacao cancelada: nenhum diretorio de destino selecionado.")
        return 1

    console_ui.print_section("Processamento")
    console_ui.hide_cursor()
    try:
        pipeline = RottenTomatoesETL()
        estatisticas = pipeline.processar(
            caminho_criticas,
            pasta_destino,
            caminho_origem_filmes=caminho_filmes,
            callback_progresso=_callback_progresso,
        )
    except (FileNotFoundError, EsquemaInvalidoError) as erro:
        console_ui.print_status(f"Erro no processamento: {erro}")
        return 1
    except Exception:
        console_ui.print_status("Erro inesperado durante o processamento:")
        console_ui.print_status(traceback.format_exc())
        return 1
    finally:
        console_ui.show_cursor()

    _exibir_resumo(estatisticas)
    return 0


if __name__ == "__main__":
    sys.exit(main())
