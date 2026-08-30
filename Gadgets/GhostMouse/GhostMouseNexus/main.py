import eel
import os
import threading
import json
import time
import ctypes
from pynput import mouse, keyboard

# --- PULO DO GATO PARA MÚLTIPLAS TELAS ---
# Força o Windows a entregar a resolução real de todos os monitores, 
# impedindo que a escala de texto (DPI) distorça as coordenadas gravadas.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

eel.init('web')

# Variáveis de Estado
is_recording = False
is_playing = False
events = []
last_time = None
OUTPUT_FILE = "mouse_events.json"

# Controlador nativo do pynput (Substitui o pyautogui para reprodução perfeita)
mouse_ctrl = mouse.Controller()

# --- LÓGICA DE GRAVAÇÃO ---

def on_move(x, y):
    if is_recording:
        record_event("move", x, y)

def on_click(x, y, button, pressed):
    if is_recording:
        action = "press" if pressed else "release"
        record_event(action, x, y, button=str(button))

def record_event(action, x, y, button=None):
    global last_time
    current_time = time.time()
    delay = current_time - (last_time if last_time else current_time)
    
    event_data = {'action': action, 'x': int(x), 'y': int(y), 'delay': delay}
    if button:
        event_data['button'] = button.split('.')[-1]
        
    events.append(event_data)
    last_time = current_time

@eel.expose
def toggle_recording():
    global is_recording, events, last_time
    if not is_recording:
        events = []
        last_time = time.time()
        is_recording = True
        return "recording"
    else:
        is_recording = False
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(events, f, indent=4)
        return "idle"


# --- LÓGICA DE REPRODUÇÃO (REFEITA) ---

def sleep_with_check(duration):
    """
    Função de pausa responsiva. 
    Permite que o programa seja interrompido instantaneamente se o senhor apertar F4.
    """
    start = time.time()
    while time.time() - start < duration:
        if not is_playing: return False
        
        # FAIL-SAFE: Se jogar o mouse para a quina superior esquerda (0, 0), o robô desliga.
        if mouse_ctrl.position == (0, 0):
            print("Fail-safe ativado!")
            return False
            
        time.sleep(0.005)
    return True

def run_playback_loop():
    global is_playing
    try:
        with open(OUTPUT_FILE, 'r') as f:
            play_events = json.load(f)
        
        if not play_events:
            raise Exception("O arquivo de gravação está vazio.")

        reps = 0
        
        # CORREÇÃO DO PONTO DE INÍCIO: 
        # Teletransporta o mouse para o Ponto X exato antes do loop começar.
        first_event = play_events[0]
        mouse_ctrl.position = (first_event['x'], first_event['y'])
        time.sleep(0.5) # Dá meio segundo para a tela focar no ponto novo

        while is_playing:
            reps += 1
            eel.update_status(f"Repetição #{reps}")()
            
            for event in play_events:
                if not is_playing: break
                
                # Aguarda o delay com checagem de interrupção
                if not sleep_with_check(event['delay']):
                    is_playing = False
                    break
                
                action = event['action']
                x, y = event['x'], event['y']
                
                if action == 'move':
                    mouse_ctrl.position = (x, y)
                elif action == 'press':
                    mouse_ctrl.position = (x, y)
                    btn = getattr(mouse.Button, event['button'], mouse.Button.left)
                    mouse_ctrl.press(btn)
                elif action == 'release':
                    mouse_ctrl.position = (x, y)
                    btn = getattr(mouse.Button, event['button'], mouse.Button.left)
                    mouse_ctrl.release(btn)
                    
    except Exception as e:
        eel.finish_process("error", str(e))()
    finally:
        is_playing = False
        eel.finish_process("success", "Reprodução finalizada ou interrompida.")()

@eel.expose
def start_playback():
    global is_playing
    if not os.path.exists(OUTPUT_FILE):
        return "missing_file"
    
    is_playing = True
    threading.Thread(target=run_playback_loop, daemon=True).start()
    return "playing"

@eel.expose
def stop_playback():
    global is_playing
    is_playing = False
    return "idle"

# --- ATALHOS GLOBAIS ---
def on_f3():
    eel.trigger_shortcut("F3")()

def on_f4():
    eel.trigger_shortcut("F4")()

def start_hotkeys():
    with keyboard.GlobalHotKeys({'<f3>': on_f3, '<f4>': on_f4}) as h:
        h.join()

threading.Thread(target=start_hotkeys, daemon=True).start()

# Listener do mouse fixo
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
mouse_listener.start()

if __name__ == '__main__':
    eel.start('index.html', size=(800, 600))