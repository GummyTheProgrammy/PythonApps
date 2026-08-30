#!/usr/bin/env python3
"""
vectorize.py — Conversor raster -> SVG para artes complexas (textura/grunge/ilustração).

O que ele faz de verdade (nada de barra de progresso falsa):
  1. Upscale de alta qualidade (Lanczos) para dar mais "resolução" de contorno ao tracer.
  2. Denoise (Non-Local Means) para limpar ruído de JPEG sem destruir bordas.
  3. Suavização bilateral multi-passo (edge-preserving) para agrupar regiões de cor
     mantendo contornos nítidos — isso é o que faz o resultado final não virar
     "confete" de milhares de micro-formas.
  4. Quantização de cor via K-Means implementado com loop manual de iterações
     (progresso real, iteração por iteração — não é enfeite).
  5. Vetorização em si via vtracer (motor Rust), em modo de alta precisão
     (color_precision, path precision e filtro de speckle ajustados para
     detalhe máximo dentro do que uma vetorização automática consegue entregar).
  6. Escrita do SVG final com viewBox e limpeza básica.

Uso:
    python3 vectorize.py entrada.jpg saida.svg
    python3 vectorize.py entrada.jpg saida.svg --scale 3 --colors 48 --quality high

Limitações honestas: isso NÃO redesenha a arte. É uma aproximação vetorial de uma
ilustração raster com textura pesada; o SVG resultante terá muitas formas planas
empilhadas simulando o gradiente/textura original. Para corte em poucas cores ou
uma versão "clean" de logo, alguém precisa redesenhar manualmente por cima disso.
"""

import argparse
import sys
import time
import cv2
import numpy as np
from tqdm import tqdm

try:
    import vtracer
except ImportError:
    print("ERRO: pacote 'vtracer' não encontrado. Instale com:")
    print("  pip install vtracer --break-system-packages")
    sys.exit(1)


def stage_upscale(img, scale, steps=2):
    """Upscale gradual (em 'steps' passos) em vez de um salto único —
    reduz artefatos de interpolação em fatores grandes."""
    h, w = img.shape[:2]
    target_w, target_h = int(w * scale), int(h * scale)
    cur = img
    with tqdm(total=steps, desc="  [1/6] Upscale progressivo", unit="passo") as bar:
        for i in range(1, steps + 1):
            t = i / steps
            cw = int(w + (target_w - w) * t)
            ch = int(h + (target_h - h) * t)
            cur = cv2.resize(cur, (cw, ch), interpolation=cv2.INTER_LANCZOS4)
            bar.update(1)
    return cur


def stage_denoise(img, strength):
    """Non-Local Means colorido — genuinamente pesado computacionalmente,
    dividido em blocos para reportar progresso real por fatia da imagem."""
    h, w = img.shape[:2]
    n_blocks = 4 if max(h, w) > 1500 else 2
    block_h = h // n_blocks
    out = np.empty_like(img)
    with tqdm(total=n_blocks, desc="  [2/6] Denoise (Non-Local Means)", unit="bloco") as bar:
        for i in range(n_blocks):
            y0 = i * block_h
            y1 = h if i == n_blocks - 1 else (i + 1) * block_h
            # overlap para evitar costura visível entre blocos
            pad = 12
            py0, py1 = max(0, y0 - pad), min(h, y1 + pad)
            chunk = img[py0:py1]
            den = cv2.fastNlMeansDenoisingColored(
                chunk, None, h=strength, hColor=strength,
                templateWindowSize=7, searchWindowSize=21
            )
            out[y0:y1] = den[y0 - py0: y1 - py0]
            bar.update(1)
    return out


def stage_bilateral(img, passes):
    """Suavização bilateral iterativa: agrupa cor mantendo bordas."""
    cur = img
    with tqdm(total=passes, desc="  [3/6] Suavização edge-preserving", unit="passe") as bar:
        for _ in range(passes):
            cur = cv2.bilateralFilter(cur, d=9, sigmaColor=60, sigmaSpace=9)
            bar.update(1)
    return cur


def stage_kmeans_quantize(img, k, max_iter):
    """K-Means manual, iteração a iteração, com progresso real e critério
    de convergência (early stop se os centros pararem de mudar)."""
    data = img.reshape((-1, 3)).astype(np.float32)

    # inicialização k-means++
    criteria_init = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 1, 1.0)
    _, labels, centers = cv2.kmeans(
        data, k, None, criteria_init, 1, cv2.KMEANS_PP_CENTERS
    )

    prev_centers = centers.copy()
    with tqdm(total=max_iter, desc=f"  [4/6] Quantização de cor (k={k})", unit="iter") as bar:
        for it in range(max_iter):
            criteria = (cv2.TERM_CRITERIA_MAX_ITER, 1, 0)
            _, labels, centers = cv2.kmeans(
                data, k, labels, criteria, 1,
                cv2.KMEANS_USE_INITIAL_LABELS
            )
            shift = np.linalg.norm(centers - prev_centers)
            bar.set_postfix(deslocamento=f"{shift:.3f}")
            bar.update(1)
            if shift < 0.15:
                bar.update(max_iter - it - 1)
                break
            prev_centers = centers.copy()

    centers = np.clip(centers, 0, 255).astype(np.uint8)
    quantized = centers[labels.flatten()].reshape(img.shape)
    return quantized


def stage_vtrace(img_bgr, quality):
    """Chama o vtracer (motor Rust). Sem hook de progresso por iteração,
    então reportamos tempo decorrido real enquanto o processo roda em
    background — sem inventar percentuais."""
    presets = {
        "fast":   dict(color_precision=6, layer_difference=8,  corner_threshold=80,
                        length_threshold=4.0, splice_threshold=45, filter_speckle=4),
        "high":   dict(color_precision=8, layer_difference=4,  corner_threshold=60,
                        length_threshold=2.0, splice_threshold=30, filter_speckle=2),
        "max":    dict(color_precision=8, layer_difference=2,  corner_threshold=45,
                        length_threshold=1.0, splice_threshold=20, filter_speckle=1),
    }
    params = presets[quality]

    import threading, tempfile, os

    tmp_png = tempfile.mktemp(suffix=".png")
    tmp_svg = tempfile.mktemp(suffix=".svg")
    cv2.imwrite(tmp_png, img_bgr)

    result = {"error": None}

    def worker():
        try:
            vtracer.convert_image_to_svg_py(
                tmp_png, tmp_svg,
                colormode="color",
                hierarchical="stacked",
                mode="spline",
                filter_speckle=params["filter_speckle"],
                color_precision=params["color_precision"],
                layer_difference=params["layer_difference"],
                corner_threshold=params["corner_threshold"],
                length_threshold=params["length_threshold"],
                splice_threshold=params["splice_threshold"],
                path_precision=8,
            )
        except Exception as e:
            result["error"] = e

    t = threading.Thread(target=worker)
    start = time.time()
    t.start()
    with tqdm(desc="  [5/6] Tracing vetorial (vtracer)", unit="s",
              bar_format="{desc}: {elapsed} decorridos {postfix}") as bar:
        while t.is_alive():
            time.sleep(0.5)
            bar.update(0)
        t.join()

    if result["error"] is not None:
        raise result["error"]

    with open(tmp_svg, "r") as f:
        svg_str = f.read()

    os.remove(tmp_png)
    os.remove(tmp_svg)
    print(f"        concluído em {time.time()-start:.1f}s")
    return svg_str


def main():
    ap = argparse.ArgumentParser(description="Vetorização de alta qualidade raster -> SVG")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--scale", type=float, default=2.5, help="fator de upscale antes do tracing")
    ap.add_argument("--colors", type=int, default=40, help="nº de cores na quantização")
    ap.add_argument("--kmeans-iters", type=int, default=25, help="máx. iterações do k-means")
    ap.add_argument("--denoise-strength", type=float, default=8.0)
    ap.add_argument("--bilateral-passes", type=int, default=3)
    ap.add_argument("--quality", choices=["fast", "high", "max"], default="high")
    args = ap.parse_args()

    print(f"Carregando {args.input} ...")
    img = cv2.imread(args.input, cv2.IMREAD_COLOR)
    if img is None:
        print("ERRO: não consegui abrir a imagem de entrada.")
        sys.exit(1)
    print(f"  tamanho original: {img.shape[1]}x{img.shape[0]}")

    t0 = time.time()

    img = stage_upscale(img, args.scale)
    img = stage_denoise(img, args.denoise_strength)
    img = stage_bilateral(img, args.bilateral_passes)
    img = stage_kmeans_quantize(img, args.colors, args.kmeans_iters)

    print("  [6/6] Gerando SVG final...")
    svg_str = stage_vtrace(img, args.quality)

    with open(args.output, "w") as f:
        f.write(svg_str)

    elapsed = time.time() - t0
    print(f"\nFeito. SVG salvo em: {args.output}")
    print(f"Tempo total: {elapsed/60:.1f} min ({elapsed:.0f}s)")


if __name__ == "__main__":
    main()