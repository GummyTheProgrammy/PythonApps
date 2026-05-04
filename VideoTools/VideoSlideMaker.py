import os
import sys
import time
import keyboard  # pip install keyboard
import cv2       # pip install opencv-python
import numpy as np

def get_dynamic_speed(initial_value=5):
    val = initial_value
    print(f"\nPT-BR: Ajuste a velocidade da câmera (Setas ↑/↓). ENTER para confirmar.")
    print(f"EN-US: Adjust camera speed (Arrow keys ↑/↓). ENTER to confirm.")
    
    while True:
        bar = "|" + "=" * int(val) + "-" * (20 - int(val)) + "|"
        sys.stdout.write(f"\rVelocidade / Speed: {val} px/frame {bar}  ")
        sys.stdout.flush()
        
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'up':
                val = min(20, val + 1)
            elif event.name == 'down':
                val = max(1, val - 1)
            elif event.name == 'enter':
                print(f"\nConfirmado: {val} px/frame")
                return val
        time.sleep(0.05)

def main():
    print("\n" + "="*60)
    print("   PANORAMA VIDEO MAKER - V2 (FIXED MEMORY)   ")
    print("="*60)

    # 1. Inputs
    caminho_inicial = input("\nInsira o caminho da pasta de imagens: ").strip()
    if caminho_inicial.lower() in ['sair', 'exit']: return False
    if not os.path.exists(caminho_inicial):
        print("Erro: Pasta não encontrada.")
        return True

    speed = get_dynamic_speed(10)
    
    raw_name = input("\nDigite o nome do arquivo de saída (ex: 'meu_video'): ").strip()
    # Proteção contra colar caminho completo no nome
    nome_arquivo = os.path.basename(raw_name) 
    if not nome_arquivo: nome_arquivo = "video_panorama"
    # Garante extensão mp4
    if not nome_arquivo.lower().endswith(".mp4"): 
        nome_arquivo += ".mp4"

    # 2. Processamento
    EXTENSOES = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    arquivos = sorted([f for f in os.listdir(caminho_inicial) if f.lower().endswith(EXTENSOES)])
    
    if not arquivos:
        print("Nenhuma imagem encontrada.")
        return True

    print("\nProcessando imagens (Resize -> 1080p)...")
    processed_images = []
    target_height = 1080
    
    for f in arquivos:
        try:
            path = os.path.join(caminho_inicial, f)
            img = cv2.imread(path)
            if img is not None:
                h, w = img.shape[:2]
                scale = target_height / h
                new_w = int(w * scale)
                # Redimensiona
                resized = cv2.resize(img, (new_w, target_height), interpolation=cv2.INTER_LINEAR)
                processed_images.append(resized)
                sys.stdout.write(f"\rLendo: {f[:20]}... -> {new_w}x{target_height}")
                sys.stdout.flush()
        except Exception as e:
            print(f" - Erro ao ler {f}: {e}")

    if not processed_images: return True

    print("\n\nCriando Super Imagem (Merging)...")
    try:
        super_image = np.hstack(processed_images)
    except MemoryError:
        print("ERRO CRÍTICO: Falta de memória RAM para criar a super imagem.")
        return True

    super_h, super_w, _ = super_image.shape
    print(f"Dimensão Total: {super_w}x{super_h}")

    # 3. Renderização
    pasta_saida = os.path.join(caminho_inicial, "render")
    os.makedirs(pasta_saida, exist_ok=True)
    output_path = os.path.join(pasta_saida, nome_arquivo)
    
    video_w = 1920
    fps = 30
    
    # Padding se imagem for pequena
    if super_w < video_w:
        padding = video_w - super_w
        super_image = cv2.copyMakeBorder(super_image, 0, 0, 0, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        super_w = super_image.shape[1]

    # Tenta CODEC h.264 (avc1), se falhar, usa mp4v
    try:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (video_w, target_height))
    except:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (video_w, target_height))
    
    if not video_writer.isOpened():
        print(f"\nErro: Não foi possível criar o arquivo de vídeo em {output_path}")
        return True

    print(f"\nRenderizando vídeo em: {output_path}")
    print("Pressione CTRL+C para cancelar com segurança.")

    max_x = super_w - video_w
    current_x = 0
    
    try:
        while current_x < max_x:
            # CORREÇÃO CRÍTICA: .copy() garante memória contígua para o C++
            frame = super_image[:, current_x : current_x + video_w].copy()
            
            video_writer.write(frame)
            
            percent = (current_x / max_x) * 100
            sys.stdout.write(f"\rProgresso: {percent:.1f}% | X: {current_x}")
            sys.stdout.flush()
            
            current_x += speed

        # Frame final estático
        final_frame = super_image[:, super_w - video_w : super_w].copy()
        for _ in range(60): # 2 segundos
            video_writer.write(final_frame)
            
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuário. Salvando o que foi feito...")
    except Exception as e:
        print(f"\n\nERRO DURANTE A RENDERIZAÇÃO: {e}")
    finally:
        video_writer.release()
        print("\nVídeo finalizado e salvo.")

    return True

if __name__ == "__main__":
    while True:
        try:
            if not main(): break
        except Exception as e:
            print(f"Erro fatal: {e}")
            break