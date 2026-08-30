import tkinter as tk
from tkinter import ttk
import datetime
import keyboard
from screeninfo import get_monitors
import pystray
from PIL import Image, ImageDraw
import threading
import sys

# Configurações de expediente
HORA_INICIO = 8
HORA_FIM_SEG_QUI = 18
HORA_FIM_SEX = 17

# 4 dias de 10h + 1 dia de 9h
TOTAL_HORAS_SEMANA = (4 * 10) + (1 * 9)
TOTAL_SEGUNDOS_SEMANA = TOTAL_HORAS_SEMANA * 3600

def calcular_progresso():
    agora = datetime.datetime.now()
    dia_semana = agora.weekday()
    
    if dia_semana > 4 or (dia_semana == 4 and agora.hour >= HORA_FIM_SEX):
        return 100.0, True
    
    if dia_semana == 0 and agora.hour < HORA_INICIO:
        return 0.0, False

    segundos_trabalhados = 0
    for d in range(dia_semana):
        if d < 4:
            segundos_trabalhados += 10 * 3600
        else:
            segundos_trabalhados += 9 * 3600

    hora_fim_hoje = HORA_FIM_SEX if dia_semana == 4 else HORA_FIM_SEG_QUI
    segundos_atuais_hoje = agora.hour * 3600 + agora.minute * 60 + agora.second
    inicio_segundos = HORA_INICIO * 3600
    fim_segundos = hora_fim_hoje * 3600

    if segundos_atuais_hoje > fim_segundos:
        segundos_trabalhados += (fim_segundos - inicio_segundos)
    elif segundos_atuais_hoje > inicio_segundos:
        segundos_trabalhados += (segundos_atuais_hoje - inicio_segundos)

    porcentagem = (segundos_trabalhados / TOTAL_SEGUNDOS_SEMANA) * 100
    return porcentagem, False

def atualizar_interface():
    porcentagem, finalizou = calcular_progresso()
    
    if finalizou:
        lbl_texto_esq.config(text="tchau e benção")
        lbl_texto_dir.config(text="")
        barra['value'] = 100
    else:
        lbl_texto_esq.config(text="Barra de progresso semanal")
        lbl_texto_dir.config(text=f"{porcentagem:.2f}%")
        barra['value'] = porcentagem

    root.after(60000, atualizar_interface)

def alternar_visibilidade(event=None):
    if root.winfo_viewable():
        root.withdraw()
    else:
        root.deiconify()

def posicionar_janela(janela, largura, altura):
    monitores = get_monitors()
    monitor_alvo = monitores[1] if len(monitores) > 1 else monitores[0]
    x = monitor_alvo.x + monitor_alvo.width - largura - 20
    y = monitor_alvo.y + monitor_alvo.height - altura - 60
    janela.geometry(f'{largura}x{altura}+{x}+{y}')

# --- Lógica do System Tray (Ícone Oculto) ---
def criar_icone_imagem():
    # Gera um ícone simples verde na memória (64x64)
    imagem = Image.new('RGB', (64, 64), color=(20, 20, 20))
    desenho = ImageDraw.Draw(imagem)
    desenho.rectangle((16, 16, 48, 48), fill=(0, 200, 0))
    return imagem

def tray_mostrar(icon, item):
    root.after(0, root.deiconify)

def tray_ocultar(icon, item):
    root.after(0, root.withdraw)

def tray_sair(icon, item):
    icon.stop()
    root.after(0, root.destroy)

def iniciar_tray():
    menu = pystray.Menu(
        pystray.MenuItem('Mostrar (Alt+Z)', tray_mostrar),
        pystray.MenuItem('Ocultar (Alt+Z)', tray_ocultar),
        pystray.MenuItem('Sair', tray_sair)
    )
    icone = pystray.Icon("ProgressoSemanal", criar_icone_imagem(), "Progresso Semanal", menu)
    icone.run()

# --- Configuração da Interface (Tkinter) ---
root = tk.Tk()
root.title("Progresso Semanal")
root.overrideredirect(True)
root.attributes('-topmost', True)

LARGURA = 300
ALTURA = 45
posicionar_janela(root, LARGURA, ALTURA)

frame_principal = ttk.Frame(root, padding=5)
frame_principal.pack(fill=tk.BOTH, expand=True)

frame_texto = ttk.Frame(frame_principal)
frame_texto.pack(fill=tk.X, expand=False, pady=(0, 2))

lbl_texto_esq = ttk.Label(frame_texto, text="Barra de progresso semanal", font=("Segoe UI", 9))
lbl_texto_esq.pack(side=tk.LEFT)
lbl_texto_dir = ttk.Label(frame_texto, text="0.00%", font=("Segoe UI", 9, "bold"))
lbl_texto_dir.pack(side=tk.RIGHT)

barra = ttk.Progressbar(frame_principal, orient='horizontal', mode='determinate', length=LARGURA)
barra.pack(fill=tk.X, expand=False)

# Registra o atalho global
keyboard.add_hotkey('alt+z', lambda: root.event_generate('<<ToggleVisibility>>', when='tail'))
root.bind('<<ToggleVisibility>>', alternar_visibilidade)

# Inicia o System Tray em uma Thread separada para não travar a interface
threading.Thread(target=iniciar_tray, daemon=True).start()

atualizar_interface()
root.mainloop()