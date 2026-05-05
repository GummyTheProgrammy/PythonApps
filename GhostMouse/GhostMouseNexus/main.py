import eel
import os
import threading
import json
import time
import pyautogui
from pynput import mouse, keyboard
from pathlib import Path

# Configurações de segurança
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001

eel.init('web')

# Variáveis de Estado
is_recording = False
is_playing = False
events = []
last_time = None
OUTPUT_FILE = "mouse_events.json"

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

# --- LÓGICA DE REPRODUÇÃO ---

def run_playback_loop():
    global is_playing
    try:
        with open(OUTPUT_FILE, 'r') as f:
            play_events = json.load(f)
        
        reps = 0
        while is_playing:
            reps += 1
            eel.update_status(f"Repetição #{reps}")()
            for event in play_events:
                if not is_playing: break
                
                time.sleep(event['delay'])
                action = event['action']
                x, y = event['x'], event['y']
                
                if action == 'move':
                    pyautogui.moveTo(x, y)
                elif action == 'press':
                    pyautogui.mouseDown(x, y, button=event['button'])
                elif action == 'release':
                    pyautogui.mouseUp(x, y, button=event['button'])
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

# --- ATALHOS GLOBAIS (O toque de mestre) ---
def on_f3():
    # O senhor pode usar esse atalho para disparar funções do front
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

eel.start('index.html', size=(800, 600))