import os
from moviepy import VideoFileClip

def verificar_resolucoes():
    print("\n" + "="*50)
    print("PT-BR: Este script lista a resolução (largura x altura) de todos os vídeos na pasta selecionada.")
    print("EN-US: This script lists the resolution (width x height) of all videos in the selected folder.")
    print("Digite 'sair' para encerrar / Type 'exit' to quit.")
    print("="*50)

    caminho_inicial = input("\nInsira o caminho da pasta raiz / Enter the root folder path): ").strip()

    if caminho_inicial.lower() in ['sair', 'exit', 'quit']:
        return False

    if not os.path.exists(caminho_inicial):
        print(f"Erro: A pasta '{caminho_inicial}' não foi encontrada.")
        return True

    extensoes_validas = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.mpeg', '.mpg', '.webm']
    
    print(f"\n{'ARQUIVO / FILE':<50} | RESOLUÇÃO / RESOLUTION")
    print("-" * 75)

    for arquivo in os.listdir(caminho_inicial):
        caminho_completo = os.path.join(caminho_inicial, arquivo)
        if os.path.isfile(caminho_completo):
            _, ext = os.path.splitext(arquivo)
            if ext.lower() in extensoes_validas:
                try:
                    clip = VideoFileClip(caminho_completo)
                    w, h = clip.size
                    nome_exibicao = (arquivo[:47] + '..') if len(arquivo) > 47 else arquivo
                    print(f"{nome_exibicao:<50} | {w}x{h}")
                    clip.close()
                except:
                    print(f"{arquivo[:47]:<50} | [ERRO]")
    
    print("-" * 75)
    return True

if __name__ == "__main__":
    while True:
        if not verificar_resolucoes():
            break