import time
import json
import pyautogui

# --- Configuração de Reprodução ---
INPUT_FILE = "mouse_events.json"
# Configuração de segurança do pyautogui (mover o mouse para (0, 0) para parar)
pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0.001 # Pausa mínima após cada chamada para evitar sobrecarga

# --- Funções de Reprodução ---

def load_events(filename):
    """Carrega os eventos do arquivo JSON."""
    try:
        with open(filename, 'r') as f:
            events = json.load(f)
        return events
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filename}' não encontrado.")
        print("Execute o 'RecordMouse.py' primeiro.")
        return None
    except json.JSONDecodeError:
        print(f"ERRO: Não foi possível ler o arquivo '{filename}'. Verifique se ele não está corrompido.")
        return None

def run_playback(events):
    """Executa a sequência de eventos."""
    for event in events:
        try:
            # 1. Espera o tempo registrado (delay)
            time.sleep(event['delay'])
            
            action = event['action']
            x = event['x']
            y = event['y']
            
            # 2. Executa a ação
            if action == 'move':
                # Move o mouse para a nova coordenada. 'duration' suaviza o movimento.
                pyautogui.moveTo(x, y, duration=0.01) 
            
            elif action == 'press':
                button = event.get('button', 'left')
                pyautogui.mouseDown(x=x, y=y, button=button)
            
            elif action == 'release':
                button = event.get('button', 'left')
                pyautogui.mouseUp(x=x, y=y, button=button)
                
        except pyautogui.FailSafeException:
            # Captura o movimento para o canto (0, 0)
            print("\n🚨 FAIL-SAFE ATIVADO! O mouse foi movido para o canto superior esquerdo.")
            print("Robô de reprodução parado.")
            return # Sai da função de reprodução atual

# --- Função Principal ---

def start_robot():
    """Carrega os eventos e executa em loop."""
    events = load_events(INPUT_FILE)
    if not events:
        return

    print(f"Eventos carregados: {len(events)}.")
    print("\n--- INICIANDO ROBÔ DE REPETIÇÃO ---")
    print("Você tem 5 segundos para focar na janela alvo.")
    print("🚨 Para PARAR, mova o cursor para o CANTO SUPERIOR ESQUERDO da tela (coordenada 0, 0).")
    
    time.sleep(5) # Delay inicial para preparação

    repetition_count = 0
    
    while True: # Loop infinito
        repetition_count += 1
        print(f"\n🤖 Repetição #{repetition_count} em execução...")
        
        run_playback(events)
        
        # Verifica se o Fail-Safe foi acionado e sai do loop principal
        if pyautogui.FailSafeException in sys.exc_info(): 
             # Isso garante que se a exceção foi capturada em 'run_playback', saímos do loop 'while True'
             break
        
        # Pausa entre as repetições
        time.sleep(2) 


# --- Execução do Programa ---

if __name__ == "__main__":
    import sys
    start_robot()