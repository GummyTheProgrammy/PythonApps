"""
Video Cutter - app desktop (Eel + ffmpeg)

Roda uma janela nativa (via Chrome/Edge em modo app) com um frontend
HTML/JS/CSS, mas toda a lógica de arquivos, corte de vídeo e log fica
aqui no Python. Não existe upload nem servidor "de verdade" para o
usuário: selecionar vídeo abre o explorador de arquivos nativo do
Windows, e exportar grava os cortes direto numa pasta escolhida por
ele (ou numa pasta padrão "exports" ao lado do programa).
"""

import os
import sys
import json
import uuid
import shutil
import subprocess
from datetime import datetime

import eel

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None


# ---------------------------------------------------------------------------
# Caminhos base (funciona tanto rodando com "python main.py" quanto
# empacotado como .exe via PyInstaller)
# ---------------------------------------------------------------------------

def get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
WEB_DIR = os.path.join(BASE_DIR, "web")
MEDIA_DIR = os.path.join(WEB_DIR, "media")          # servido pelo eel p/ preview no <video>
DEFAULT_EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "cortes_log.txt")
FFMPEG_BIN_DIR = os.path.join(BASE_DIR, "ffmpeg_bin")

for d in (MEDIA_DIR, DEFAULT_EXPORTS_DIR, LOG_DIR):
    os.makedirs(d, exist_ok=True)

ALLOWED_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


# ---------------------------------------------------------------------------
# Localização dos binários do ffmpeg/ffprobe
# (primeiro tenta a pasta ffmpeg_bin/ ao lado do programa - útil quando
# empacotado como .exe - senão cai para o PATH do sistema)
# ---------------------------------------------------------------------------

def resolve_binary(name: str) -> str:
    exe_name = name + (".exe" if os.name == "nt" else "")
    bundled = os.path.join(FFMPEG_BIN_DIR, exe_name)
    if os.path.isfile(bundled):
        return bundled
    found = shutil.which(name)
    if found:
        return found
    return name  # deixa estourar erro claro na hora de rodar, se não existir


FFMPEG = resolve_binary("ffmpeg")
FFPROBE = resolve_binary("ffprobe")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def log_line(text: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {text}\n")


def fmt_time(seconds: float) -> str:
    seconds = max(0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if h > 0:
        return f"{h:d}:{m:02d}:{s:05.2f}"
    return f"{m:d}:{s:05.2f}"


def safe_filename(name: str) -> str:
    keep = "-_.() "
    cleaned = "".join(c for c in name if c.isalnum() or c in keep).strip()
    return cleaned or "arquivo"


def ffprobe_duration(path: str) -> float:
    cmd = [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "json", path]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(out.stdout)
    return float(data["format"]["duration"])


def run_ffmpeg_cut(src: str, dst: str, start: float, duration: float, reencode: bool):
    if reencode:
        cmd = [
            FFMPEG, "-y",
            "-ss", f"{start:.3f}",
            "-i", src,
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k",
            dst,
        ]
    else:
        cmd = [
            FFMPEG, "-y",
            "-ss", f"{start:.3f}",
            "-i", src,
            "-t", f"{duration:.3f}",
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            dst,
        ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg falhou ao cortar {os.path.basename(dst)}:\n{result.stderr[-1500:]}")


def stage_video_for_preview(src_path: str) -> str:
    """
    Coloca uma cópia (ou hardlink, quando possível) do vídeo escolhido
    dentro de web/media/, para que o <video> do frontend consiga tocar
    o arquivo através do servidor local que o eel já sobe.
    Retorna o nome do arquivo dentro de media/.
    """
    ext = os.path.splitext(src_path)[1].lower()
    stored_name = f"{uuid.uuid4().hex[:10]}{ext}"
    dst_path = os.path.join(MEDIA_DIR, stored_name)
    try:
        os.link(src_path, dst_path)  # hardlink: instantâneo, sem duplicar espaço em disco (mesmo volume)
    except OSError:
        shutil.copy2(src_path, dst_path)  # fallback: copia de verdade (outro volume, etc.)
    return stored_name


def cleanup_media_dir(keep: str = None):
    """Remove vídeos antigos de web/media/ para não acumular lixo, mantendo (opcionalmente) o mais recente."""
    for fname in os.listdir(MEDIA_DIR):
        if fname == keep:
            continue
        try:
            os.remove(os.path.join(MEDIA_DIR, fname))
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Lógica principal (testável sem depender do diálogo nativo / eel)
# ---------------------------------------------------------------------------

def process_selected_video(path: str) -> dict:
    if not path or not os.path.isfile(path):
        return {"error": "Arquivo não encontrado."}

    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_EXT:
        return {"error": f"Extensão '{ext}' não suportada."}

    try:
        duration = ffprobe_duration(path)
    except Exception as e:
        return {"error": f"Não foi possível ler o vídeo (ffprobe): {e}"}

    cleanup_media_dir()
    stored_name = stage_video_for_preview(path)

    size_mb = os.path.getsize(path) / (1024 * 1024)
    log_line(
        f"UPLOAD | arquivo='{path}' | duracao={fmt_time(duration)} ({duration:.2f}s) | tamanho={size_mb:.2f}MB"
    )

    return {
        "stored_name": stored_name,
        "original_name": os.path.basename(path),
        "original_path": path,
        "duration": duration,
        "url": f"/media/{stored_name}",
    }


def do_export(payload: dict) -> dict:
    """
    payload esperado:
    {
      "stored_name": "abcd1234.mp4",
      "original_name": "meuvideo.mp4",
      "reencode": true,
      "output_folder": "" | "C:/Users/.../Cortes",
      "cuts": [
        {"start": 60, "end": 155, "batch": true,  "segment": 10},
        {"start": 300, "end": 330, "batch": false}
      ]
    }
    """
    stored_name = payload.get("stored_name")
    original_name = payload.get("original_name", stored_name or "video")
    reencode = bool(payload.get("reencode", True))
    cuts = payload.get("cuts") or []
    output_folder = (payload.get("output_folder") or "").strip()

    if not stored_name:
        return {"error": "Nenhum vídeo selecionado."}
    src_path = os.path.join(MEDIA_DIR, stored_name)
    if not os.path.isfile(src_path):
        return {"error": "Vídeo original não encontrado (selecione o vídeo novamente)."}
    if not cuts:
        return {"error": "Nenhum corte informado."}

    try:
        total_duration = ffprobe_duration(src_path)
    except Exception as e:
        return {"error": f"Erro ao ler duração do vídeo: {e}"}

    target_root = output_folder if output_folder and os.path.isdir(output_folder) else DEFAULT_EXPORTS_DIR
    base_name = os.path.splitext(safe_filename(original_name))[0]
    session_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir = os.path.join(target_root, session_name)
    os.makedirs(out_dir, exist_ok=True)

    exported_files = []
    errors = []

    for idx, cut in enumerate(cuts, start=1):
        try:
            start = float(cut["start"])
            end = float(cut["end"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"Corte #{idx}: início/fim inválidos.")
            continue

        start = max(0.0, min(start, total_duration))
        end = max(0.0, min(end, total_duration))
        if end <= start:
            errors.append(f"Corte #{idx}: intervalo inválido ({fmt_time(start)} -> {fmt_time(end)}).")
            continue

        is_batch = bool(cut.get("batch"))
        range_duration = end - start

        if is_batch:
            try:
                segment = float(cut.get("segment", 20))
                if segment <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                segment = 20.0

            n_full = int(range_duration // segment)
            remainder = round(range_duration - n_full * segment, 3)
            if remainder < 0.15:
                remainder = 0.0

            pieces = [segment] * n_full
            if remainder > 0:
                pieces.append(remainder)

            log_line(
                f"EXPORT-BATCH | arquivo='{original_name}' | intervalo={fmt_time(start)} -> {fmt_time(end)} "
                f"({range_duration:.2f}s) | segmento={segment:.2f}s | "
                f"gerados={len(pieces)} ({n_full} de {segment:.2f}s"
                + (f" + 1 de {remainder:.2f}s" if remainder > 0 else "") + ") | pasta='{}'".format(out_dir)
            )

            cursor = start
            for p_idx, piece_len in enumerate(pieces, start=1):
                out_name = f"corte{idx:02d}_batch{p_idx:03d}_{piece_len:.0f}s.mp4"
                out_path = os.path.join(out_dir, out_name)
                try:
                    run_ffmpeg_cut(src_path, out_path, cursor, piece_len, reencode)
                    exported_files.append(out_path)
                    log_line(f"  -> parte {p_idx}/{len(pieces)}: {out_name} [{fmt_time(cursor)} -> {fmt_time(cursor + piece_len)}]")
                except Exception as e:
                    errors.append(f"Corte #{idx} parte {p_idx}: {e}")
                cursor += piece_len
        else:
            out_name = safe_filename(
                f"corte{idx:02d}_{fmt_time(start).replace(':', 'm')}s-{fmt_time(end).replace(':', 'm')}s.mp4"
            )
            out_path = os.path.join(out_dir, out_name)
            try:
                run_ffmpeg_cut(src_path, out_path, start, range_duration, reencode)
                exported_files.append(out_path)
                log_line(
                    f"EXPORT-CORTE | arquivo='{original_name}' | {out_name} "
                    f"[{fmt_time(start)} -> {fmt_time(end)}] ({range_duration:.2f}s) | pasta='{out_dir}'"
                )
            except Exception as e:
                errors.append(f"Corte #{idx}: {e}")

    if not exported_files:
        try:
            os.rmdir(out_dir)
        except OSError:
            pass
        return {"error": "Nenhum arquivo foi exportado.", "details": errors}

    return {
        "output_folder": out_dir,
        "files": [os.path.basename(p) for p in exported_files],
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Diálogos nativos (tkinter) - só chamados de dentro das funções expostas
# ---------------------------------------------------------------------------

def _ask_open_video_dialog() -> str:
    if tk is None:
        raise RuntimeError("tkinter não está disponível neste ambiente.")
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Selecione um vídeo",
        filetypes=[
            ("Vídeos", "*.mp4 *.mov *.mkv *.avi *.webm *.m4v"),
            ("Todos os arquivos", "*.*"),
        ],
    )
    root.destroy()
    return path


def _ask_output_folder_dialog() -> str:
    if tk is None:
        raise RuntimeError("tkinter não está disponível neste ambiente.")
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Escolha a pasta de destino dos cortes")
    root.destroy()
    return folder


# ---------------------------------------------------------------------------
# Funções expostas ao JS (frontend)
# ---------------------------------------------------------------------------

@eel.expose
def pick_video():
    try:
        path = _ask_open_video_dialog()
    except Exception as e:
        return {"error": str(e)}
    if not path:
        return {"cancelled": True}
    return process_selected_video(path)


@eel.expose
def pick_output_folder():
    try:
        folder = _ask_output_folder_dialog()
    except Exception as e:
        return {"error": str(e)}
    return {"folder": folder or ""}


@eel.expose
def export_cuts(payload):
    return do_export(payload)


@eel.expose
def get_log_text():
    if not os.path.isfile(LOG_FILE):
        return "(log ainda vazio)"
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()


@eel.expose
def open_path(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@eel.expose
def get_default_exports_dir():
    return DEFAULT_EXPORTS_DIR


@eel.expose
def get_logs_dir():
    return LOG_DIR


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

def main():
    eel.init(WEB_DIR)
    start_kwargs = dict(size=(1320, 880), port=0)
    for mode in ("chrome", "edge", "default"):
        try:
            eel.start("index.html", mode=mode, **start_kwargs)
            return
        except EnvironmentError:
            continue
    print("Não foi possível abrir uma janela de navegador. Abra http://localhost manualmente.")


if __name__ == "__main__":
    main()
