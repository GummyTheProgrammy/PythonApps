import os
import string
import sys
import time
import keyboard  # Necessário: pip install keyboard
from moviepy import VideoFileClip, concatenate_videoclips

def get_dynamic_duration(initial_value=19.5):
    """
    Permite ao usuário ajustar a duração usando as setas do teclado.
    """
    val = initial_value
    print(f"\nPT-BR: Ajuste a duração do corte (Setas ↑/↓). ENTER para confirmar.")
    print(f"EN-US: Adjust cut duration (Arrow keys ↑/↓). ENTER to confirm.")
    
    while True:
        sys.stdout.write(f"\rDuração / Duration: {val:.1f}s  ")
        sys.stdout.flush()
        
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'up':
                val += 0.1
            elif event.name == 'down':
                val = max(0.1, val - 0.1)
            elif event.name == 'enter':
                print(f"\nConfirmado: {val:.1f}s")
                return val
        time.sleep(0.05) # Evita saltos duplos rápidos demais

def get_valid_int(prompt):
    while True:
        try:
            val = int(input(prompt))
            if val > 0: return val
            print("Erro: Digite um número maior que zero.")
        except ValueError:
            print("Erro: Entrada inválida. Digite apenas números inteiros.")

def main():
    print("\n" + "="*60)
    print("PT-BR: Este script une vídeos de uma pasta e os corta em segmentos menores.")
    print("EN-US: This script joins videos from a folder and cuts them into smaller segments.")
    print("Digite 'sair' para encerrar / Type 'exit' to quit.")
    print("="*60)

    caminho_inicial = input("\nInsira o caminho da pasta raiz / Enter the root folder path: ").strip()
    
    if caminho_inicial.lower() in ['sair', 'exit', 'quit']:
        return False

    if not os.path.exists(caminho_inicial):
        print(f"Erro: Pasta não encontrada.")
        return True

    # 1. Configurações Dinâmicas
    duracao_corte = get_dynamic_duration(19.5)

    print("\nEscolha a Resolução / Choose Resolution:")
    print("[H] Horizontal (1280x720) | [V] Vertical (720x1280) | [C] Custom")
    res_choice = input("Opção / Option: ").strip().upper()
    
    if res_choice == 'H':
        res_alvo = (1280, 720)
    elif res_choice == 'V':
        res_alvo = (720, 1280)
    else:
        w = get_valid_int("Largura / Width: ")
        h = get_valid_int("Altura / Height: ")
        res_alvo = (w, h)

    nome_lote = input("\nDigite o nome do lote / Enter the batch name: ").strip() or "Video"

    print("\nEstrutura de Nomenclatura / Naming Structure:")
    print("[1] Alfa (A-Z + Rounds(overflow))")
    print("[2] Enum (01, 02, 03...)")
    tipo_nome = input("Opção / Option: ").strip()

    # 2. Processamento
    EXTENSOES = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.mpeg', '.mpg']
    arquivos = sorted([f for f in os.listdir(caminho_inicial) if os.path.isfile(os.path.join(caminho_inicial, f))])
    
    clips = []
    print("\nCarregando vídeos...")
    for arquivo in arquivos:
        if any(arquivo.lower().endswith(ext) for ext in EXTENSOES):
            try:
                clip = VideoFileClip(os.path.join(caminho_inicial, arquivo))
                clips.append(clip.resized(res_alvo))
            except Exception as e:
                print(f"Erro ao carregar {arquivo}: {e}")

    if not clips:
        print("Nenhum vídeo encontrado.")
        return True

    print("\nConcatenando vídeos... Aguarde.")
    timeline = concatenate_videoclips(clips, method="compose")
    duracao_total = timeline.duration
    pasta_saida_base = os.path.join(caminho_inicial, "render")
    
    if not os.path.exists(pasta_saida_base):
        os.makedirs(pasta_saida_base)

    tempo_atual = 0
    indice = 0
    round_num = 1
    alfabeto = string.ascii_uppercase

    print(f"\nDuração Total da Timeline: {duracao_total:.2f}s")
    print("Iniciando cortes...")

    while tempo_atual < duracao_total:
        fim_corte = min(tempo_atual + duracao_corte, duracao_total)
        
        if tipo_nome == '1':
            letra = alfabeto[indice % 26]
            if indice > 0 and indice % 26 == 0:
                round_num += 1
            
            pasta_destino = pasta_saida_base
            if round_num > 1:
                pasta_destino = os.path.join(pasta_saida_base, f"round {round_num}")
                os.makedirs(pasta_destino, exist_ok=True)
            
            nome_arquivo = f"{nome_lote} {letra}.mp4"
        else:
            pasta_destino = pasta_saida_base
            nome_arquivo = f"{nome_lote}_{indice + 1:03d}.mp4"

        # --- RESTAURAÇÃO DO PROGRESSO ---
        progresso_pct = (tempo_atual / duracao_total) * 100
        print(f"\nRenderizando: {nome_arquivo}")
        print(f"Progresso Geral: {progresso_pct:.1f}% concluído")
        # -------------------------------

        sub = timeline.subclipped(tempo_atual, fim_corte)
        sub.write_videofile(os.path.join(pasta_destino, nome_arquivo), codec="libx264", preset="ultrafast", fps=30, logger='bar')
        
        tempo_atual += duracao_corte
        indice += 1

    timeline.close()
    for c in clips: c.close()
    print("\nFinalizado com sucesso!")
    return True

if __name__ == "__main__":
    # Nota: 'keyboard' requer privilégios de administrador/root em alguns SOs
    while True:
        if not main():
            break