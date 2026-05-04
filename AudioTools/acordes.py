import pygame
import numpy as np
import sys

# Inicializa o pygame e o mixer de áudio
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Dimensões iniciais da tela
WIDTH, HEIGHT = 800, 600
# pygame.RESIZABLE permite que a janela seja esticada/maximizada
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Sintetizador de Acordes - Mestre")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (50, 50, 50)
BLUE = (100, 150, 255)

# Variáveis Globais de Fonte
font_small = None
font_medium = None
font_large = None

def update_fonts(w, h):
    """Recalcula o tamanho das fontes com base na altura da tela."""
    global font_small, font_medium, font_large
    font_small = pygame.font.SysFont("Arial", max(16, int(h * 0.04)))
    font_medium = pygame.font.SysFont("Arial", max(20, int(h * 0.05)))
    font_large = pygame.font.SysFont("Arial", max(40, int(h * 0.15)), bold=True)

# Inicializa as fontes para o tamanho padrão
update_fonts(WIDTH, HEIGHT)

# Variáveis de Estado
is_major = True
interval_region = 4
history = []
current_key = None
current_sound = None

# Sistema de Volume
volume = 50  # Inteiro de 0 a 100
dragging_slider = False

def get_freq(note_index, octave):
    distance = (note_index - 9) + (octave - 4) * 12
    return 440.0 * (2.0 ** (distance / 12.0))

# Mapeamento do teclado atualizado (com sustenidos)
note_map = {
    pygame.K_a: (9, "A"),
    pygame.K_s: (10, "A#"),
    pygame.K_b: (11, "B"),
    pygame.K_c: (0, "C"),
    pygame.K_v: (1, "C#"),
    pygame.K_d: (2, "D"),
    pygame.K_r: (3, "D#"),  # Assumindo a tecla R para o D#
    pygame.K_e: (4, "E"),
    pygame.K_f: (5, "F"),
    pygame.K_t: (6, "F#"),
    pygame.K_g: (7, "G"),
    pygame.K_h: (8, "G#")
}

def generate_square_chord(freq1, freq2, duration=2.0, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave1 = np.sign(np.sin(2 * np.pi * freq1 * t))
    wave2 = np.sign(np.sin(2 * np.pi * freq2 * t))
    
    # Mistura base das ondas
    mixed = (wave1 + wave2) * 0.15
    audio = np.int16(mixed * 32767)
    
    stereo = np.empty((audio.size, 2), dtype=np.int16)
    stereo[:, 0] = audio
    stereo[:, 1] = audio
    
    return pygame.sndarray.make_sound(stereo)

# Loop principal
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    
    # Atualização dos elementos de interface do volume (baseado nas dimensões da tela)
    btn_minus = pygame.Rect(20, 20, 30, 30)
    slider_bg = pygame.Rect(60, 30, 150, 10)
    btn_plus = pygame.Rect(220, 20, 30, 30)
    # Posição do "botão" do slider calculada pela porcentagem
    knob_x = 60 + int((volume / 100) * 150) - 10
    knob_rect = pygame.Rect(knob_x, 20, 20, 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.VIDEORESIZE:
            # Reajusta as dimensões e atualiza as fontes dinamicamente
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            update_fonts(WIDTH, HEIGHT)
            
        # --- INTERAÇÃO COM MOUSE (VOLUME) ---
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo
                if btn_minus.collidepoint(event.pos):
                    volume = max(0, volume - 10)
                elif btn_plus.collidepoint(event.pos):
                    volume = min(100, volume + 10)
                elif knob_rect.collidepoint(event.pos) or slider_bg.collidepoint(event.pos):
                    dragging_slider = True
                    rel_x = event.pos[0] - slider_bg.x
                    volume = max(0, min(100, int((rel_x / slider_bg.w) * 100)))
                
                # Se o volume mudar enquanto o som toca, aplica imediatamente
                if current_sound:
                    current_sound.set_volume(volume / 100.0)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_slider = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:
                rel_x = event.pos[0] - slider_bg.x
                volume = max(0, min(100, int((rel_x / slider_bg.w) * 100)))
                if current_sound:
                    current_sound.set_volume(volume / 100.0)

        # --- INTERAÇÃO COM TECLADO ---
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_CAPSLOCK]:
                is_major = not is_major
            
            elif event.unicode == '+' or event.key == pygame.K_KP_PLUS:
                if interval_region < 9:
                    interval_region += 1
            elif event.unicode == '-' or event.key == pygame.K_KP_MINUS:
                if interval_region > 0:
                    interval_region -= 1
            
            elif event.key in note_map:
                if current_sound:
                    current_sound.stop()
                
                current_key = event.key
                base_idx, note_name = note_map[event.key]
                
                freq_root = get_freq(base_idx, interval_region)
                third_offset = 4 if is_major else 3
                freq_third = get_freq(base_idx + third_offset, interval_region)
                
                current_sound = generate_square_chord(freq_root, freq_third)
                # Aplica o volume atualizado do sistema (0.0 a 1.0)
                current_sound.set_volume(volume / 100.0)
                current_sound.play(loops=-1)
                
                # Nova regra: "M" some, e apenas "m" aparece para menores
                chord_name = f"{note_name}{'' if is_major else 'm'}"
                history.append(chord_name)
                if len(history) > 5:
                    history.pop(0)

        elif event.type == pygame.KEYUP:
            if event.key == current_key:
                if current_sound:
                    current_sound.stop()
                current_sound = None
                current_key = None

    # --- RENDERIZAÇÃO DA TELA ---
    
    # 1. Topo Esquerdo: Volume UI
    pygame.draw.rect(screen, GRAY, btn_minus)
    pygame.draw.rect(screen, GRAY, btn_plus)
    pygame.draw.rect(screen, DARK_GRAY, slider_bg)
    pygame.draw.rect(screen, WHITE, knob_rect)
    
    txt_minus = font_medium.render("-", True, BLACK)
    txt_plus = font_medium.render("+", True, BLACK)
    
    # Centraliza os textos de + e - nos botões
    screen.blit(txt_minus, (btn_minus.x + btn_minus.w//2 - txt_minus.get_width()//2, btn_minus.y + btn_minus.h//2 - txt_minus.get_height()//2))
    screen.blit(txt_plus, (btn_plus.x + btn_plus.w//2 - txt_plus.get_width()//2, btn_plus.y + btn_plus.h//2 - txt_plus.get_height()//2))
    
    # Texto de Volume (%)
    vol_text = font_small.render(f"Volume: {volume}%", True, WHITE)
    screen.blit(vol_text, (60, 60))

    # 2. Topo Centro: Intervalo
    text_interval = font_medium.render(f"Intervalo = {interval_region}", True, WHITE)
    screen.blit(text_interval, (WIDTH//2 - text_interval.get_width()//2, 30))
    
    # 3. Centro: Memória Horizontal Dinâmica
    if history:
        total_width = 0
        surfaces = []
        spacing = int(WIDTH * 0.05) # Espaçamento dinâmico (5% da largura da tela)
        
        for i, chord in enumerate(history):
            if i == len(history) - 1 and current_key is not None:
                surf = font_large.render(chord, True, BLUE) # Destaque em azul para melhor visibilidade
            else:
                surf = font_small.render(chord, True, GRAY)
            surfaces.append(surf)
            total_width += surf.get_width() + spacing
        
        total_width -= spacing
        start_x = WIDTH//2 - total_width//2
        curr_x = start_x
        
        for surf in surfaces:
            screen.blit(surf, (curr_x, HEIGHT//2 - surf.get_height()//2))
            curr_x += surf.get_width() + spacing
            
    # 4. Inferior: Modo Atual
    mode_text = "MODO: MAIOR" if is_major else "MODO: MENOR"
    text_mode = font_medium.render(mode_text, True, WHITE)
    screen.blit(text_mode, (WIDTH//2 - text_mode.get_width()//2, HEIGHT - int(HEIGHT * 0.15)))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()