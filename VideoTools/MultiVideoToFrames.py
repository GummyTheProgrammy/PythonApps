import os
import numpy as np
from PIL import Image
from moviepy import VideoFileClip
from tqdm import tqdm

def extrair_frames():
    print("\n" + "="*50)
    print("PT-BR: Este script extrai todos os frames de vídeos em uma pasta e os salva como imagens PNG.")
    print("EN-US: This script extracts all frames from videos in a folder and saves them as PNG images.")
    print("Digite 'sair' para encerrar / Type 'exit' to quit.")
    print("="*50)

    caminho_inicial = input("\nInsira o caminho da pasta raiz / Enter the root folder path): ").strip()
    
    if caminho_inicial.lower() in ['sair', 'exit', 'quit']:
        return False

    if not os.path.exists(caminho_inicial):
        print(f"Erro: A pasta '{caminho_inicial}' não foi encontrada.")
        return True

    PASTA_SAIDA = os.path.join(caminho_inicial, "render")
    EXTENSOES_VALIDAS = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.mpeg', '.mpg', '.webm']
    
    if not os.path.exists(PASTA_SAIDA):
        os.makedirs(PASTA_SAIDA)

    arquivos = sorted([f for f in os.listdir(caminho_inicial) if os.path.isfile(os.path.join(caminho_inicial, f))])
    videos_para_processar = []
    total_frames_global = 0

    print("\n--- Analisando arquivos / Analyzing files ---")
    for arquivo in arquivos:
        _, ext = os.path.splitext(arquivo)
        if ext.lower() in EXTENSOES_VALIDAS:
            caminho_completo = os.path.join(caminho_inicial, arquivo)
            try:
                clip_temp = VideoFileClip(caminho_completo)
                frames_estimados = int(clip_temp.fps * clip_temp.duration)
                total_frames_global += frames_estimados
                videos_para_processar.append(caminho_completo)
                clip_temp.close()
            except:
                continue

    if not videos_para_processar:
        print("Nenhum vídeo válido encontrado nesta pasta.")
        return True

    contador_global_img = 1
    with tqdm(total=total_frames_global, unit='fr', desc="Progresso Total") as barra_progresso:
        for caminho_video in videos_para_processar:
            try:
                clip = VideoFileClip(caminho_video)
                for frame_array in clip.iter_frames(fps=clip.fps, dtype="uint8"):
                    imagem_pil = Image.fromarray(frame_array)
                    nome_imagem = f"{contador_global_img:08d}.png"
                    imagem_pil.save(os.path.join(PASTA_SAIDA, nome_imagem), format="PNG")
                    contador_global_img += 1
                    barra_progresso.update(1)
                clip.close()
            except Exception as e:
                print(f"\nErro em {os.path.basename(caminho_video)}: {e}")

    print(f"\nSucesso! Imagens salvas em: {PASTA_SAIDA}")
    return True

if __name__ == "__main__":
    while True:
        if not extrair_frames():
            break