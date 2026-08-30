"""
core.console_ui
================

Componentes de apresentacao para o console (CMD). Restrito a saida de
texto/ANSI padrao: nenhuma biblioteca de interface grafica e utilizada.

Este modulo e propositalmente isolado do restante da aplicacao: ele nao
contem nenhuma regra de negocio, apenas rotinas de exibicao. Isso permite
que, em uma futura empacotagem com EEL, esta camada seja substituida por
uma camada de atualizacao de interface web sem alterar `core.etl`.
"""

from __future__ import annotations

import sys
import shutil

_ANSI_GREEN = "\033[92m"
_ANSI_DIM = "\033[2m"
_ANSI_RESET = "\033[0m"
_ANSI_BOLD = "\033[1m"

_CURSOR_HIDE = "\033[?25l"
_CURSOR_SHOW = "\033[?25h"

_ansi_enabled = False


def enable_ansi_support() -> None:
    """
    Habilita a interpretacao de sequencias ANSI no console do Windows
    (Windows 10+, ENABLE_VIRTUAL_TERMINAL_PROCESSING). Em outros sistemas
    operacionais, as sequencias ANSI ja sao interpretadas nativamente pelo
    terminal e nenhuma acao adicional e necessaria.
    """
    global _ansi_enabled
    if _ansi_enabled:
        return

    if sys.platform == "win32":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        STD_OUTPUT_HANDLE = -11
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)

    _ansi_enabled = True


def print_status(message: str) -> None:
    """Exibe uma mensagem de status neutra, sem qualificadores subjetivos."""
    print(message)


def print_section(title: str) -> None:
    """Exibe um cabecalho de secao neutro, para separar etapas do processamento."""
    print(f"\n{_ANSI_BOLD}{title}{_ANSI_RESET}")
    print("-" * len(title))


def render_progress_bar(progress: float, label: str = "", width: int | None = None) -> None:
    """
    Renderiza, na mesma linha do console (via retorno de carro), uma barra
    de progresso verde preenchida de acordo com `progress`.

    Parametros
    ----------
    progress : float
        Valor entre 0.0 e 1.0 representando a fracao concluida.
    label : str
        Rotulo curto exibido antes da barra (ex.: nome da etapa).
    width : int, opcional
        Largura da barra em caracteres. Quando omitido, e calculada a
        partir da largura atual do terminal.
    """
    progress = max(0.0, min(1.0, float(progress)))

    if width is None:
        terminal_columns = shutil.get_terminal_size(fallback=(100, 24)).columns
        reserved = len(label) + 12
        width = max(10, min(50, terminal_columns - reserved))

    filled_length = int(round(width * progress))
    bar = "#" * filled_length + "-" * (width - filled_length)
    percentage = progress * 100.0

    line = f"\r{label} {_ANSI_GREEN}[{bar}]{_ANSI_RESET} {percentage:6.2f}%"
    sys.stdout.write(line)
    sys.stdout.flush()

    if progress >= 1.0:
        sys.stdout.write("\n")
        sys.stdout.flush()


def hide_cursor() -> None:
    sys.stdout.write(_CURSOR_HIDE)
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write(_CURSOR_SHOW)
    sys.stdout.flush()
