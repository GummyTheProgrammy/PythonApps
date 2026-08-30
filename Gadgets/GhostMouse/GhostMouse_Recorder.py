import time
import json
import threading
from pynput import mouse

# --- Configuração de Gravação ---
OUTPUT_FILE = "mouse_events.json"
events = []
last_time = None
is_recording = False
stop_listener = threading.Event()

# --- Funções do Listener ---

def on_move(x, y):
    """Registra o movimento do mouse."""
    if is_recording:
        record_event("move", x, y)

def on_click(x, y, button, pressed):
    """Registra os cliques do mouse."""
    if is_recording:
        action = "press" if pressed else "release"
        record_event(action, x, y, button=str(button))
        
    # Usaremos uma condição no loop principal para parar

def record_event(action, x, y, button=None):
    """Calcula o delay e salva o evento na lista global."""
    global last_time
    
    current_time = time.time()
    
    # Calcula o tempo desde o último evento registrado
    delay = current_time - (last_time if last_time else current_time)
    
    event_data = {
        'action': action,
        'x': int(x),
        'y': int(y),
        'delay': delay,
    }
    if button:
        event_data['button'] = button.split('.')[-1] # Simplifica o nome do botão (ex: 'left', 'right')
        
    events.append(event_data)
    last_time = current_time

# --- Função Principal ---

def start_recording():
    """Inicia o listener do mouse em uma thread separada."""
    listener = mouse.Listener(on_click=on_click, on_move=on_move)
    listener.start()
    
    print("\n--- INICIANDO GRAVAÇÃO ---")
    print("Mova e clique livremente. Pressione ENTER para PARAR...")
    
    global is_recording
    is_recording = True
    
    # Aguarda o segundo comando (qualquer tecla + Enter)
    input() 
    
    # Parada
    is_recording = False
    listener.stop()
    listener.join()
    
    # Salva os eventos
    print(f"\nGravação parada. Salvando {len(events)} eventos em {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(events, f, indent=4)
    print("Salvo com sucesso! Você pode iniciar o robô agora.")


# --- Execução do Programa ---

if __name__ == "__main__":
    print(f"Robô de Gravação. O arquivo será salvo como: {OUTPUT_FILE}")
    
    # Primeiro comando de início
    user_input = input("Para começar a gravar, digite 'sim' ou 's': ").lower().strip()
    
    if user_input in ["sim", "s"]:
        start_recording()
    else:
        print("Gravação cancelada. Execute o programa novamente para começar.")