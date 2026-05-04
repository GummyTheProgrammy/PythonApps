import cv2
import numpy as np
import math
import os
import sys
import time
import keyboard 
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÕES FIXAS ---
V_WIDTH, V_HEIGHT = 1920, 1080
ASSETS_FOLDER = "assets"
BG_FILENAME = "FastReadVideoGenBG.png"
FPS = 30
FONT_SIZE = 180 

# Cores
COR_TEXTO = (255, 255, 255) 
COR_DESTAQUE = (230, 50, 50) 

def get_orp_index(word):
    clean = word.strip(".,!?\"()")
    length = len(clean)
    if length <= 1: return 0
    idx = int(math.ceil(length / 4.0)) 
    diff = len(word) - len(word.lstrip(".,!?\"()"))
    return min(idx + diff, len(word) - 1)

def get_dynamic_wpm(initial_value=300):
    val = initial_value
    print(f"\nPT-BR: Ajuste a velocidade (WPM) (Setas ↑/↓). ENTER para confirmar.")
    while True:
        sys.stdout.write(f"\rVelocidade: {val} WPM  ")
        sys.stdout.flush()
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'up': val += 10
            elif event.name == 'down': val = max(10, val - 10)
            elif event.name == 'enter':
                print(f"\nConfirmado: {val} WPM")
                return val
        time.sleep(0.05)

def criar_frame(word, font, bg_image, y_anchor_fixed):
    """
    Agora recebe y_anchor_fixed para garantir que o texto nunca pule verticalmente.
    """
    img_pil = bg_image.copy()
    draw = ImageDraw.Draw(img_pil)
    
    orp_idx = get_orp_index(word)
    part_left, part_orp, part_right = word[:orp_idx], word[orp_idx], word[orp_idx+1:]
    
    w_left = int(font.getlength(part_left))
    w_orp = int(font.getlength(part_orp))
    
    center_x = V_WIDTH // 2
    center_y = V_HEIGHT // 2 # Usado apenas para as guias
    
    x_orp = center_x - (w_orp // 2)
    x_left, x_right = x_orp - w_left, x_orp + w_orp
    
    # OBSERVAÇÃO DO MESTRE CORRIGIDA:
    # Usamos o y_anchor_fixed calculado no main(), ignorando a altura específica desta palavra.
    # Isso alinha todas as palavras pela base comum.
    
    # Guias Visuais
    guia_cor = (60, 60, 60)
    guia_len = 40
    # As guias continuam fixas no centro absoluto da tela
    draw.line([(center_x, center_y - 120), (center_x, center_y - 120 - guia_len)], fill=guia_cor, width=3)
    draw.line([(center_x, center_y + 120), (center_x, center_y + 120 + guia_len)], fill=guia_cor, width=3)

    draw.text((x_left, y_anchor_fixed), part_left, font=font, fill=COR_TEXTO)
    draw.text((x_orp, y_anchor_fixed), part_orp, font=font, fill=COR_DESTAQUE)
    draw.text((x_right, y_anchor_fixed), part_right, font=font, fill=COR_TEXTO)
    
    return np.array(img_pil)

def get_next_filename(folder):
    base = "render"
    ext = ".mp4"
    first_try = f"{base}{ext}"
    if not os.path.exists(os.path.join(folder, first_try)):
        return first_try
    counter = 0
    while True:
        candidate = f"{base} {counter}{ext}"
        if not os.path.exists(os.path.join(folder, candidate)):
            return candidate
        counter += 1

def main():
    print("\n" + "="*60)
    print("             FAST READ VIDEO GEN - V1.4 (STABLE)     ")
    print("="*60)

    bg_path = os.path.join(ASSETS_FOLDER, BG_FILENAME)
    if os.path.exists(bg_path):
        bg_pil = Image.open(bg_path).convert('RGB').resize((V_WIDTH, V_HEIGHT))
    else:
        bg_pil = Image.new('RGB', (V_WIDTH, V_HEIGHT), (0,0,0))

    font_paths = ["times.ttf", "georgia.ttf", "arial.ttf", "serif"]
    font = None
    for p in font_paths:
        try:
            font = ImageFont.truetype(p, FONT_SIZE)
            break
        except: continue
    if not font: font = ImageFont.load_default()

    # --- CORREÇÃO DE ALTURA ---
    # Calculamos a altura de uma letra de referência (Maiúscula)
    # Isso define a "Caixa" padrão para todo o vídeo.
    bbox_ref = font.getbbox("H") # H é uma boa referência de altura total
    ref_h = bbox_ref[3] - bbox_ref[1]
    
    # Calculamos o Y fixo para centralizar essa altura de referência
    # O -20 é o ajuste fino visual que já existia
    y_anchor_fixed = (V_HEIGHT // 2) - (ref_h // 2) - 20
    
    print("\nDigite ou cole o texto (ENTER duplo para processar):")
    lines = []
    while True:
        try:
            line = input()
            if line == "": break
            lines.append(line)
        except EOFError: break
    
    texto = " ".join(lines)
    if not texto.strip(): return True

    wpm = get_dynamic_wpm(350)
    
    os.makedirs("render", exist_ok=True)
    nome_final = get_next_filename("render")
    out_path = os.path.join("render", nome_final)
    abs_out_path = os.path.abspath(out_path)
    
    words = [w for w in texto.split() if w.strip()]
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(abs_out_path, fourcc, FPS, (V_WIDTH, V_HEIGHT))

    f_per_word = int(FPS * 60 / wpm)

    print(f"\nRenderizando '{nome_final}'...")

    for i, word in enumerate(words):
        # Passamos o y_anchor_fixed calculado UMA vez
        frame_np = criar_frame(word, font, bg_pil, y_anchor_fixed)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        
        duration = f_per_word
        if ',' in word: duration = int(duration * 1.5)
        elif any(p in word for p in '.!?'): duration *= 2
            
        for _ in range(duration):
            video_writer.write(frame_bgr)
        
        sys.stdout.write(f"\rProgresso: {i+1}/{len(words)}")
        sys.stdout.flush()

    video_writer.release()
    print(f"\n\nVídeo finalizado com sucesso!")
    print(f"Arquivo: {abs_out_path}")
    
    print("Abrindo vídeo...")
    try:
        os.startfile(abs_out_path)
    except Exception as e:
        print(f"Não foi possível abrir o player automaticamente: {e}")

    return True

if __name__ == "__main__":
    while True:
        if not main(): break
        time.sleep(1) 
        if input("\nGerar outro? (s/n): ").lower() != 's': break