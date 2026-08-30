import eel
import subprocess
import threading
import mailbox
import csv
import os
import re
import shutil
import tempfile
import glob
import time
import logging
from email.header import decode_header
from email.utils import getaddresses, parsedate_to_datetime
from html.parser import HTMLParser
from tkinter import Tk, filedialog

eel.init('web')

CHUNK_BYTES = 1 * 1024 ** 3          # particiona o CSV a cada ~1 GiB de mbox processado
ATTACHMENT_RATIO_GUESS = 0.35        # estimativa: e-mail+texto costuma ser ~35% do PST original


# ----------------------------------------------------------------------
# Localiza o readpst.exe (instalado via MSYS2 - veja README.md)
# ----------------------------------------------------------------------
def _find_readpst():
    candidates = [
        r"C:\msys64\mingw64\bin\readpst.exe",
        shutil.which("readpst"),
        shutil.which("readpst.exe"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


READPST_PATH = _find_readpst()


def _setup_logger(pst_path):
    """Cria um logger dedicado por execucao, gravando em <pst>_log.txt"""
    log_path = pst_path + "_log.txt"
    logger = logging.getLogger(f"pst_{os.getpid()}_{int(time.time())}")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    return logger, log_path


def _format_eta(elapsed, pct):
    if pct <= 1.0:
        return "calculando tempo restante..."
    total_estimado = elapsed / (pct / 100.0)
    restante = max(0, total_estimado - elapsed)
    m, s = divmod(int(restante), 60)
    return f"~{m}min {s}s restantes"


def _check_disk_space(logger, tmp_dir, required_bytes):
    try:
        usage = shutil.disk_usage(tmp_dir)
        logger.info(
            f"Espaco livre em disco: {usage.free / 1e9:.2f} GB "
            f"(estimativa necessaria: {required_bytes / 1e9:.2f} GB)"
        )
        if usage.free < required_bytes:
            logger.warning("ATENCAO: espaco em disco pode ser insuficiente para esta conversao.")
            return False
    except Exception as e:
        logger.warning(f"Nao foi possivel checar espaco em disco: {e}")
    return True


@eel.expose
def select_file():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askopenfilename(
        title="Selecione o arquivo PST",
        filetypes=[("Arquivos PST", "*.pst"), ("Todos os arquivos", "*.*")],
    )
    root.destroy()
    return path or None


@eel.expose
def process_pst(pst_path):
    if not READPST_PATH:
        eel.update_progress({
            "phase": "error",
            "message": ("readpst.exe nao encontrado. Instale o MSYS2 e o pacote "
                        "mingw-w64-x86_64-libpst (veja README.md)."),
        })
        return
    thread = threading.Thread(target=_run, args=(pst_path,), daemon=True)
    thread.start()


# ----------------------------------------------------------------------
# Pipeline: PST -> (readpst, so e-mails, sem anexos) -> mbox -> CSV (particionado)
# ----------------------------------------------------------------------
def _run(pst_path):
    logger, log_path = _setup_logger(pst_path)
    tmp_dir = tempfile.mkdtemp(prefix="pst_extract_")
    logger.info(f"=== Iniciando processamento de: {pst_path} ===")
    try:
        pst_size = os.path.getsize(pst_path)
        logger.info(f"Tamanho do PST: {pst_size / 1e9:.2f} GB")
        _check_disk_space(logger, tempfile.gettempdir(), pst_size * 1.2)

        _convert(pst_path, tmp_dir, pst_size, logger)

        csv_base = pst_path + "_convertido"
        total, csv_paths = _extract_to_csv(tmp_dir, csv_base, logger)

        nomes = ", ".join(os.path.basename(p) for p in csv_paths)
        msg = f"Concluido: {total} e-mails exportados em {len(csv_paths)} arquivo(s): {nomes}"
        logger.info(msg)
        eel.update_progress({"phase": "done", "percent": 100.0, "message": msg})

    except Exception as e:
        logger.exception("Falha no processamento")
        eel.update_progress({
            "phase": "error",
            "message": f"Falha na execucao: {e}\nDetalhes em: {os.path.basename(log_path)}",
        })
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.info("=== Processamento finalizado ===")


def _convert(pst_path, out_dir, pst_size, logger):
    eel.update_progress({
        "phase": "converting", "percent": 0.0,
        "message": "Convertendo PST... calculando estimativa...",
    })

    readpst_debug_log = pst_path + "_readpst_debug.log"
    cmd = [
        READPST_PATH, "-q",
        "-t", "e",              # somente e-mails; descarta anexos (nao precisamos deles)
        "-L", "3", "-d", readpst_debug_log,
        "-o", out_dir, pst_path,
    ]
    # Nao usamos -r (recursivo): essa flag recria a estrutura de pastas do PST
    # como diretorios reais via chdir(), o que esbarra em restricoes de
    # nomenclatura do Windows (ex: "mk_recurse_dir: Cannot change to directory
    # Calendar: Invalid argument"). O modo padrao do readpst escreve arquivos
    # mbox soltos (sem recriar diretorios aninhados) e evita esse problema.
    logger.info("Comando readpst: " + " ".join(cmd))

    stop_event = threading.Event()
    start_time = time.time()

    def _monitor():
        while not stop_event.is_set():
            time.sleep(1.5)
            try:
                produzido = sum(
                    os.path.getsize(os.path.join(dp, f))
                    for dp, _, files in os.walk(out_dir) for f in files
                )
            except Exception:
                produzido = 0
            elapsed = time.time() - start_time
            # Estimativa: sem anexos, a saida costuma ser uma fracao do PST original.
            # Nunca deixamos passar de 95% antes do processo realmente terminar.
            pct = min(95.0, (produzido / (pst_size * ATTACHMENT_RATIO_GUESS)) * 100) if pst_size else 0.0
            eta = _format_eta(elapsed, pct)
            eel.update_progress({
                "phase": "converting",
                "percent": round(pct, 1),
                "message": f"Convertendo PST... {eta}",
            })

    monitor_thread = threading.Thread(target=_monitor, daemon=True)
    monitor_thread.start()

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    stdout, stderr = proc.communicate()
    stop_event.set()
    monitor_thread.join(timeout=2)

    logger.info(f"readpst finalizado com codigo de saida {proc.returncode}")
    if stdout:
        logger.debug("readpst stdout:\n" + stdout)
    if stderr:
        logger.debug("readpst stderr:\n" + stderr)
    logger.info(f"Log de debug interno do readpst salvo em: {readpst_debug_log}")

    if proc.returncode != 0:
        ja_convertido = [
            p for p in glob.glob(os.path.join(out_dir, "**", "*"), recursive=True)
            if os.path.isfile(p)
        ]
        if ja_convertido:
            logger.warning(
                f"readpst abortou (codigo {proc.returncode}), mas {len(ja_convertido)} "
                f"arquivo(s) ja foram convertidos antes do erro. Prosseguindo com esses dados "
                f"(o CSV ficara PARCIAL, faltando o que vinha depois da pasta que travou)."
            )
            eel.update_progress({
                "phase": "converting", "percent": 100.0,
                "message": "Conversao parcial (parou num erro, mas ha dados aproveitaveis).",
            })
            return
        raise RuntimeError(stderr.strip() or f"readpst retornou codigo {proc.returncode} (veja o log)")

    eel.update_progress({"phase": "converting", "percent": 100.0, "message": "Conversao concluida."})


def _extract_to_csv(mbox_dir, csv_base, logger):
    mbox_files = [
        p for p in glob.glob(os.path.join(mbox_dir, "**", "*"), recursive=True)
        if os.path.isfile(p)
    ]
    total_size = sum(os.path.getsize(p) for p in mbox_files) or 1
    logger.info(f"{len(mbox_files)} arquivo(s) mbox gerados pelo readpst, total {total_size / 1e9:.2f} GB")

    processed_bytes = 0
    processed = 0
    chunk_index = 1
    next_threshold = CHUNK_BYTES
    csv_paths = []
    start_time = time.time()

    def _open_new_csv(idx):
        path = f"{csv_base}_parte{idx:02d}.csv"
        fh = open(path, mode="w", newline="", encoding="utf-8-sig")
        w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        w.writerow(["Assunto", "Remetente", "Para", "Cópia", "Data", "Horário", "Corpo"])
        csv_paths.append(path)
        logger.info(f"Abrindo novo arquivo CSV (parte {idx}): {path}")
        return fh, w

    f, writer = _open_new_csv(chunk_index)

    eel.update_progress({"phase": "extracting", "percent": 0.0, "message": "Lendo mensagens e gerando CSV..."})

    try:
        for path in mbox_files:
            try:
                box = mailbox.mbox(path)
            except Exception as e:
                logger.warning(f"Nao foi possivel abrir {path}: {e}")
                processed_bytes += os.path.getsize(path)
                continue

            for msg in box:
                try:
                    data, hora = _split_date_hora(msg.get("Date", ""))
                    writer.writerow([
                        _decode_mime_words(msg.get("Subject", "")),
                        _names_only(msg.get("From", "")),
                        _names_only(msg.get("To", "")),
                        _names_only(msg.get("Cc", "")),
                        data,
                        hora,
                        _get_body_text(msg),
                    ])
                    processed += 1
                except Exception as e:
                    logger.debug(f"Erro ao gravar mensagem #{processed} de {path}: {e}")

                if processed % 50 == 0:
                    pct = round(min(99.99, 100 * processed_bytes / total_size), 2)
                    eta = _format_eta(time.time() - start_time, pct)
                    eel.update_progress({
                        "phase": "extracting", "percent": pct,
                        "message": f"Processando... {processed} e-mails lidos ({eta})",
                    })

            processed_bytes += os.path.getsize(path)
            box.close()

            if processed_bytes >= next_threshold:
                f.close()
                logger.info(f"Parte {chunk_index} fechada apos {processed_bytes / 1e9:.2f} GB processados")
                chunk_index += 1
                next_threshold += CHUNK_BYTES
                f, writer = _open_new_csv(chunk_index)
    finally:
        f.close()

    logger.info(f"Extracao concluida: {processed} mensagens em {len(csv_paths)} arquivo(s) CSV")
    return processed, csv_paths


def _decode_mime_words(value):
    """Decodifica cabecalhos MIME encoded-word (=?utf-8?B?...?=) para texto legivel."""
    if not value:
        return ""
    try:
        parts = decode_header(value)
    except Exception:
        return value
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            try:
                out.append(text.decode(enc or "utf-8", errors="ignore"))
            except (LookupError, Exception):
                out.append(text.decode("utf-8", errors="ignore"))
        else:
            out.append(text)
    # normaliza espacos que sobram entre pedacos decodificados (quebras de linha do encoded-word)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def _names_only(header_value):
    """Recebe um header To/Cc/From cru e devolve so os nomes de exibicao, separados por '; '.
    Quando um endereco nao tem nome de exibicao, cai para o proprio e-mail."""
    if not header_value:
        return ""
    pares = getaddresses([header_value])
    nomes = []
    for nome, email_addr in pares:
        nome = _decode_mime_words(nome).strip()
        if not nome:
            nome = email_addr
        if nome and nome not in nomes:
            nomes.append(nome)
    return "; ".join(nomes)


def _split_date_hora(date_header):
    """Separa o header Date em (data DD/MM/AAAA, hora HH:MM:SS). Se nao conseguir parsear,
    devolve o texto original na data e vazio na hora."""
    if not date_header:
        return "", ""
    try:
        dt = parsedate_to_datetime(date_header)
        if dt is None:
            return date_header, ""
        return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M:%S")
    except Exception:
        return date_header, ""


class _HTMLToText(HTMLParser):
    """Conversor minimo de HTML para texto legivel (so biblioteca padrao),
    preservando quebras de linha em tags de bloco e ignorando script/style."""

    BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._chunks = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag in self.BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip > 0:
            self._skip -= 1
        if tag in self.BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._chunks.append(data)

    def get_text(self):
        text = "".join(self._chunks)
        # colapsa espacos e linhas em branco excessivas
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()


def _html_to_text(html):
    parser = _HTMLToText()
    try:
        parser.feed(html)
        return parser.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html).strip()


# Linhas/frases que costumam marcar o inicio de assinatura ou rodape corporativo
_SIGNATURE_MARKERS = re.compile(
    r"^\s*(--\s*$"
    r"|atenciosamente\b"
    r"|att\.?\b"
    r"|abra[cç]os?\b"
    r"|cordialmente\b"
    r"|grato\b"
    r"|obrigad[oa]\b.{0,15}$"
    r"|this\s+e-?mail\s+and\s+any\s+files"
    r"|este\s+e-?mail\s+e\s+seus\s+anexos"
    r"|enviado\s+(do|pelo)\s+meu\s+"
    r"|sent\s+from\s+my\s+)",
    re.IGNORECASE,
)


def _strip_signature(body):
    """Corta o corpo no primeiro marcador de assinatura/rodape encontrado (heuristica -
    nao e 100% preciso, mas cobre os casos mais comuns em pt-BR/en)."""
    if not body:
        return body
    linhas = body.splitlines()
    for i, linha in enumerate(linhas):
        if _SIGNATURE_MARKERS.match(linha):
            corte = "\n".join(linhas[:i]).strip()
            # so aceita o corte se sobrar conteudo (evita zerar o corpo por falso positivo)
            if corte:
                return corte
    return body.strip()


def _get_body_text(msg):
    """Prioriza text/plain; se so houver text/html, converte para texto. Sempre remove assinatura."""
    plain, html_body = None, None

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_filename():
                continue
            ctype = part.get_content_type()
            charset = part.get_content_charset() or "utf-8"
            if ctype == "text/plain" and plain is None:
                payload = part.get_payload(decode=True) or b""
                plain = payload.decode(charset, errors="ignore")
            elif ctype == "text/html" and html_body is None:
                payload = part.get_payload(decode=True) or b""
                html_body = payload.decode(charset, errors="ignore")
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True) or b""
        raw = payload.decode(charset, errors="ignore")
        if msg.get_content_type() == "text/html":
            html_body = raw
        else:
            plain = raw

    corpo = plain if plain else (_html_to_text(html_body) if html_body else "")
    return _strip_signature(corpo)


if __name__ == "__main__":
    eel.start("index.html", size=(550, 450), mode="chrome")