"""
Analisador de Diretórios - Backend

Aplicação de varredura recursiva e visualização hierárquica de tamanho de
diretórios. Construída com Eel (Python no backend, HTML/CSS/JS no frontend).

Regras arquiteturais adotadas neste módulo:
- Nenhuma biblioteca de GUI padrão (Tkinter, PySide6) ou framework web
  (Flask, Django etc.) é utilizada. A camada de interface é feita via Eel.
- A seleção de diretórios aciona o seletor nativo do Windows (via
  PowerShell em modo STA), trazendo a janela para o primeiro plano.
- O progresso da varredura é reportado ao frontend como valor numérico
  do tipo float (0.0 a 100.0).
- Erros são registrados em arquivo de log (app_error.log), além de
  retornados de forma estruturada para o frontend quando aplicável.
"""

import eel
import os
import sys
import logging
import threading
import subprocess
import traceback

# ---------------------------------------------------------------------------
# Log de erros
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "app_error.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("directory_analyzer")


def log_exception(context):
    logger.error("%s\n%s", context, traceback.format_exc())


# ---------------------------------------------------------------------------
# Estado global da varredura
# ---------------------------------------------------------------------------
scan_lock = threading.Lock()
scan_state = {
    "root": None,
    "tree": {},          # path -> node
    "total_dirs": 0,
    "processed_dirs": 0,
    "progress": 0.0,
    "scanning": False,
    "finished": False,
    "cancel": False,
    "error": None,
}


def _new_node(path, name, is_dir):
    return {
        "path": path,
        "name": name,
        "is_dir": is_dir,
        "size": 0.0,
        "children": [] if is_dir else None,
        "size_ready": not is_dir,   # arquivos já nascem com tamanho definitivo
        "_own_files_size": 0.0,
    }


def _count_total_dirs(root_path):
    """Contagem rápida (sem cálculo de tamanho) usada apenas como
    denominador para a barra de progresso."""
    total = 1
    try:
        for _, dirnames, _ in os.walk(root_path):
            total += len(dirnames)
    except OSError:
        log_exception("Falha ao contar diretórios para estimativa de progresso")
    return total


def _register_directory(path):
    """Registra o node do diretório e de seus filhos imediatos.
    Arquivos recebem tamanho exato de imediato; subpastas recebem
    tamanho provisório (0.0) até a fase de consolidação.
    Idempotente: pode ser chamada mais de uma vez para o mesmo path."""
    with scan_lock:
        if path not in scan_state["tree"]:
            name = os.path.basename(path) or path
            scan_state["tree"][path] = _new_node(path, name, True)

    try:
        entries = list(os.scandir(path))
    except (PermissionError, FileNotFoundError, OSError):
        log_exception(f"Sem acesso ao diretório: {path}")
        entries = []

    children_paths = []
    own_files_size = 0.0

    for entry in entries:
        try:
            if entry.is_dir(follow_symlinks=False):
                child_path = entry.path
                with scan_lock:
                    if child_path not in scan_state["tree"]:
                        scan_state["tree"][child_path] = _new_node(child_path, entry.name, True)
                children_paths.append(child_path)
            else:
                try:
                    size = float(entry.stat(follow_symlinks=False).st_size)
                except OSError:
                    size = 0.0
                file_path = entry.path
                node = _new_node(file_path, entry.name, False)
                node["size"] = size
                node["size_ready"] = True
                with scan_lock:
                    scan_state["tree"][file_path] = node
                children_paths.append(file_path)
                own_files_size += size
        except OSError:
            log_exception(f"Falha ao processar item dentro de: {path}")
            continue

    with scan_lock:
        node = scan_state["tree"][path]
        node["children"] = children_paths
        node["_own_files_size"] = own_files_size


def _consolidate_size(path):
    """Soma o tamanho de um diretório a partir de seus filhos já
    processados (arquivos com tamanho exato, subpastas já consolidadas)."""
    with scan_lock:
        node = scan_state["tree"].get(path)
        if node is None:
            return 0.0
        total = node.get("_own_files_size", 0.0)
        children = list(node.get("children") or [])

    for child_path in children:
        with scan_lock:
            child = scan_state["tree"].get(child_path)
        if child is not None:
            total += child["size"]

    with scan_lock:
        node = scan_state["tree"].get(path)
        if node is not None:
            node["size"] = total
            node["size_ready"] = True
    return total


def _safe_call(func_name, *args):
    """Chama uma função exposta no JS (via eel) sem derrubar a thread de
    varredura caso o frontend ainda não esteja pronto para recebê-la."""
    try:
        getattr(eel, func_name)(*args)
    except Exception:
        log_exception(f"Falha ao notificar o frontend ({func_name})")


def _scan_worker(root_path):
    try:
        scan_state["scanning"] = True
        scan_state["finished"] = False
        scan_state["processed_dirs"] = 0
        scan_state["progress"] = 0.0
        scan_state["error"] = None

        total_dirs = _count_total_dirs(root_path)
        scan_state["total_dirs"] = max(total_dirs, 1)

        # Fase 1: descoberta da estrutura (permite navegação imediata pelo
        # frontend, mesmo com a varredura ainda em andamento).
        all_dirs_topdown = []
        for current_dir, _dirnames, _filenames in os.walk(root_path, topdown=True):
            if scan_state["cancel"]:
                break
            _register_directory(current_dir)
            all_dirs_topdown.append(current_dir)

            scan_state["processed_dirs"] += 1
            progress = min(90.0, (scan_state["processed_dirs"] / scan_state["total_dirs"]) * 90.0)
            scan_state["progress"] = progress
            _safe_call("update_progress", progress)

        # Fase 2: consolidação dos tamanhos, das pastas mais profundas até a raiz.
        total_to_consolidate = max(len(all_dirs_topdown), 1)
        for i, dir_path in enumerate(reversed(all_dirs_topdown)):
            if scan_state["cancel"]:
                break
            size = _consolidate_size(dir_path)
            progress = 90.0 + min(10.0, ((i + 1) / total_to_consolidate) * 10.0)
            scan_state["progress"] = progress
            _safe_call("update_folder_size", dir_path, size)
            _safe_call("update_progress", progress)

        scan_state["progress"] = 100.0
        _safe_call("update_progress", 100.0)
        _safe_call("scan_complete")

    except Exception as exc:
        log_exception(f"Erro fatal durante a varredura de: {root_path}")
        scan_state["error"] = str(exc)
        _safe_call("scan_error", str(exc))
    finally:
        scan_state["scanning"] = False
        scan_state["finished"] = True


@eel.expose
def start_scan(root_path):
    """Inicia a varredura recursiva do diretório informado em thread separada.
    Registra a pasta raiz de forma síncrona antes de retornar, para que o
    frontend já consiga carregar seus dados imediatamente."""
    try:
        if not root_path or not os.path.isdir(root_path):
            return {"ok": False, "error": "Diretório inválido."}

        scan_state["root"] = root_path
        scan_state["tree"] = {}
        scan_state["cancel"] = False
        scan_state["error"] = None

        # Registro síncrono da raiz: elimina a corrida em que o frontend
        # pede os dados antes da thread de varredura ter começado a rodar.
        _register_directory(root_path)

        thread = threading.Thread(target=_scan_worker, args=(root_path,), daemon=True)
        thread.start()
        return {"ok": True}
    except Exception as exc:
        log_exception(f"Erro ao iniciar varredura de: {root_path}")
        return {"ok": False, "error": str(exc)}


@eel.expose
def get_progress():
    return {
        "progress": scan_state["progress"],
        "scanning": scan_state["scanning"],
        "finished": scan_state["finished"],
        "error": scan_state["error"],
    }


@eel.expose
def get_folder_data(path):
    """Retorna subpastas e arquivos de um diretório já indexado, mesmo que
    a varredura completa ainda não tenha terminado."""
    try:
        target = path or scan_state["root"]
        if not target:
            return {"ok": False, "error": "Nenhum diretório selecionado."}

        with scan_lock:
            node = scan_state["tree"].get(target)
            if node is None:
                return {"ok": False, "error": "Diretório ainda não indexado."}

            children = []
            for child_path in (node.get("children") or []):
                child = scan_state["tree"].get(child_path)
                if child is None:
                    continue
                children.append({
                    "name": child["name"],
                    "path": child["path"],
                    "is_dir": child["is_dir"],
                    "size": child["size"],
                    "size_ready": child["size_ready"],
                })

            is_root = target == scan_state["root"]
            parent_path = None
            if not is_root:
                parent_path = os.path.dirname(target)
                if not parent_path or parent_path == target:
                    parent_path = scan_state["root"]

            return {
                "ok": True,
                "path": target,
                "name": node["name"],
                "size": node["size"],
                "is_root": is_root,
                "parent": parent_path,
                "children": children,
            }
    except Exception as exc:
        log_exception(f"Erro ao obter dados do diretório: {path}")
        return {"ok": False, "error": str(exc)}


@eel.expose
def select_folder_dialog():
    """Abre o seletor nativo de pastas do Windows via PowerShell, em modo
    STA, forçando a janela para o primeiro plano."""
    if sys.platform != "win32":
        return {"ok": False, "error": "Seleção nativa disponível apenas no Windows."}

    ps_script = r"""
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::EnableVisualStyles()

$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "Selecione o diretorio raiz para analise"
$dialog.ShowNewFolderButton = $false

$owner = New-Object System.Windows.Forms.Form
$owner.TopMost = $true
$owner.ShowInTaskbar = $false
$owner.WindowState = 'Minimized'
$owner.StartPosition = 'Manual'
$owner.Location = New-Object System.Drawing.Point(-2000,-2000)
$owner.Show()
$owner.Activate()

$result = $dialog.ShowDialog($owner)
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $dialog.SelectedPath
}

$owner.Dispose()
"""
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-STA", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=300,
        )
        selected = completed.stdout.strip()
        if selected:
            return {"ok": True, "path": selected}
        if completed.stderr:
            log_exception(f"PowerShell reportou erro no seletor de pastas: {completed.stderr.strip()}")
        return {"ok": False, "error": "Nenhum diretório selecionado."}
    except Exception as exc:
        log_exception("Erro ao abrir o seletor nativo de pastas")
        return {"ok": False, "error": str(exc)}


@eel.expose
def log_frontend_error(message):
    """Permite que o frontend registre erros de JavaScript no mesmo
    arquivo de log do backend, facilitando o diagnóstico."""
    logger.error("Erro no frontend: %s", message)
    return {"ok": True}


def main():
    logger.info("Aplicação iniciada.")
    eel.init("web")
    try:
        eel.start("index.html", size=(1200, 780), port=0)
    except (SystemExit, MemoryError, KeyboardInterrupt):
        pass
    except Exception:
        log_exception("Erro fatal ao iniciar a janela da aplicação")


if __name__ == "__main__":
    main()