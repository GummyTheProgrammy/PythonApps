"""
main.py
=======

Ponto de entrada da aplicacao de linha de comando (CMD) que gera a
Matriz de Expertise dos criticos a partir da base limpa produzida pelo
projeto `rt_etl` (arquivos `critico.csv`, `filme.csv` e
`registro_critica.csv`).

Este arquivo contem apenas a orquestracao da interface de linha de
comando e os parametros ajustaveis pelo usuario. Toda a logica de
negocio reside em `core.matriz`, e todo o acesso a APIs nativas do
Windows reside em `core.file_dialog` e `core.console_ui`. Essa separacao
de camadas e intencional: para uma futura empacotagem com EEL, basta
criar um novo arquivo de entrada que importe
`core.matriz.ConstrutorMatrizExpertise` e encaminhe o progresso e o
relatorio para a interface web, sem qualquer alteracao no nucleo de
processamento.
"""

from __future__ import annotations

import sys
import traceback

from core import console_ui
from core.matriz import ConstrutorMatrizExpertise, LimiaresNivel, BaseIncompletaError
from core.file_dialog import pick_folder, FileDialogUnavailableError

# ======================================================================
# PARAMETROS AJUSTAVEIS
# ======================================================================
# Faixas de quantidade de filmes distintos analisados que definem cada
# nivel de expertise. Ajuste estes valores conforme o volume da sua base
# (uma base muito maior ou muito menor que a original pode exigir faixas
# diferentes das sugeridas nas regras de negocio originais).
#
# Interpretacao: "ate LIMITE_NOVATO_MAX filmes" = Novato,
# "de LIMITE_NOVATO_MAX + 1 ate LIMITE_ENTUSIASTA_MAX" = Entusiasta,
# "de LIMITE_ENTUSIASTA_MAX + 1 ate LIMITE_ESPECIALISTA_MAX" = Especialista,
# "acima de LIMITE_ESPECIALISTA_MAX" = nivel maximo (rotulo especifico de
# cada dimensao, definido logo abaixo).
LIMITE_NOVATO_MAX = 20
LIMITE_ENTUSIASTA_MAX = 50
LIMITE_ESPECIALISTA_MAX = 99

# Rotulo do nivel maximo em cada dimensao de classificacao.
ROTULO_NIVEL_MAXIMO_GENERO = "Autoridade"
ROTULO_NIVEL_MAXIMO_DECADA = "Historiador"

# Quando True, um critico com ZERO filmes analisados em um determinado
# genero/decada recebe o rotulo "Novato" nessa coluna (leitura literal
# das regras de negocio, onde "ate 20 filmes" inclui o zero). Quando
# False (padrao), a coluna fica em branco para indicar "sem atuacao
# nesse genero/decada", o que torna a matriz mais informativa ao
# distinguir "nunca atuou" de "atuou pouco".
TRATAR_ZERO_COMO_NOVATO = False
# ======================================================================


def _limiares_genero() -> LimiaresNivel:
    return LimiaresNivel(
        limite_novato_max=LIMITE_NOVATO_MAX,
        limite_entusiasta_max=LIMITE_ENTUSIASTA_MAX,
        limite_especialista_max=LIMITE_ESPECIALISTA_MAX,
        rotulo_topo=ROTULO_NIVEL_MAXIMO_GENERO,
    )


def _limiares_decada() -> LimiaresNivel:
    return LimiaresNivel(
        limite_novato_max=LIMITE_NOVATO_MAX,
        limite_entusiasta_max=LIMITE_ENTUSIASTA_MAX,
        limite_especialista_max=LIMITE_ESPECIALISTA_MAX,
        rotulo_topo=ROTULO_NIVEL_MAXIMO_DECADA,
    )


def _requisitar_pasta_base() -> str | None:
    console_ui.print_status("onde esta a base de dados?")
    console_ui.print_status("Aguardando selecao da pasta na janela do Windows.")
    return pick_folder(title="Selecionar pasta com a base limpa (critico.csv, filme.csv, registro_critica.csv)")


def _requisitar_pasta_destino() -> str | None:
    console_ui.print_status("Aguardando selecao do diretorio de destino na janela do Windows.")
    return pick_folder(title="Selecionar diretorio de destino para a Matriz de Expertise")


def _callback_progresso(fracao: float, mensagem: str) -> None:
    console_ui.render_progress_bar(fracao, label="Processamento")


def _exibir_resumo(resultado) -> None:
    console_ui.print_section("Resumo do processamento")
    console_ui.print_status(f"Criticos processados: {resultado.total_criticos}")
    console_ui.print_status(f"Filmes considerados: {resultado.total_filmes}")
    console_ui.print_status(f"Pares critico/filme distintos analisados: {resultado.total_registros_lidos}")
    console_ui.print_status(f"Colunas de genero geradas: {len(resultado.colunas_genero)} ({', '.join(resultado.colunas_genero)})")
    console_ui.print_status(f"Colunas de decada geradas: {len(resultado.colunas_decada)} ({', '.join(resultado.colunas_decada)})")

    console_ui.print_section("Arquivos gerados")
    console_ui.print_status(f"csv: {resultado.caminho_saida_csv}")
    console_ui.print_status(f"html: {resultado.caminho_saida_html}")


def main() -> int:
    console_ui.enable_ansi_support()
    console_ui.print_section("Matriz de Expertise dos Criticos - Rotten Tomatoes")

    try:
        pasta_base = _requisitar_pasta_base()
    except FileDialogUnavailableError as erro:
        console_ui.print_status(f"Erro: {erro}")
        return 1

    if not pasta_base:
        console_ui.print_status("Operacao cancelada: nenhuma pasta de origem selecionada.")
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
        construtor = ConstrutorMatrizExpertise(
            limiares_genero=_limiares_genero(),
            limiares_decada=_limiares_decada(),
            tratar_zero_como_novato=TRATAR_ZERO_COMO_NOVATO,
        )
        resultado = construtor.construir(pasta_base, pasta_destino, callback_progresso=_callback_progresso)
    except BaseIncompletaError as erro:
        console_ui.print_status(f"Erro: {erro}")
        return 1
    except Exception:
        console_ui.print_status("Erro inesperado durante o processamento:")
        console_ui.print_status(traceback.format_exc())
        return 1
    finally:
        console_ui.show_cursor()

    _exibir_resumo(resultado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
