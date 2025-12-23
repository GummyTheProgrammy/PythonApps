import os
from moviepy import VideoFileClip

def video_sec_calc_recursivo():
    print("\n" + "="*50)
    print("PT-BR: Este script calcula o tempo total de duração de todos os vídeos em uma pasta e subpastas.")
    print("EN-US: This script calculates the total duration of all videos in a folder and subfolders.")
    print("Digite 'sair' para encerrar / Type 'exit' to quit.")
    print("="*50)

    caminho_inicial = input("\nInsira o caminho da pasta raiz / Enter the root folder path): ").strip()

    if caminho_inicial.lower() in ['sair', 'exit', 'quit']:
        return False

    if not os.path.exists(caminho_inicial):
        print(f"Erro: A pasta '{caminho_inicial}' não foi encontrada.")
        return True

    extensoes_video = ('.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v')
    total_segundos = 0.0
    contagem_arquivos = 0

    try:
        for raiz, _, arquivos in os.walk(caminho_inicial):
            for arquivo in arquivos:
                if arquivo.lower().endswith(extensoes_video):
                    caminho_completo = os.path.join(raiz, arquivo)
                    try:
                        clip = VideoFileClip(caminho_completo)
                        total_segundos += clip.duration
                        clip.close() 
                        contagem_arquivos += 1
                        print(f"[OK] {arquivo}")
                    except:
                        print(f"[ERRO] Falha ao ler: {arquivo}")

        # Cálculos de tempo
        seconds = int(total_segundos)
        minutes = int(total_segundos // 60)
        m_restantes, s_restantes = divmod(seconds, 60)
        h, m_finais = divmod(m_restantes, 60)

        print("\n" + "=" * 40)
        print(f"RESUMO / SUMMARY (Vídeos: {contagem_arquivos})")
        print("=" * 40)

        # Lógica de Output Condicional
        if h >= 1:
            # Se tiver uma hora ou mais
            print(f"Tempo Total: {h}h {m_finais}m {s_restantes}s")
            print(f"Tempo Total em minutos: {minutes}m")
            print(f"Tempo Total em segundos: {seconds}s")
        
        elif minutes >= 1:
            # Se tiver um minuto ou mais (mas menos de uma hora)
            print(f"Tempo Total em minutos: {minutes}m {s_restantes}s")
            print(f"Tempo Total em segundos: {seconds}s")
        
        else:
            # Se tiver menos de um minuto
            print(f"Tempo Total em segundos: {seconds}s")

        print("=" * 40)

    except Exception as e:
        print(f"Erro crítico: {e}")

    return True

if __name__ == "__main__":
    while True:
        if not video_sec_calc_recursivo():
            print("\nEncerrando programa... Até logo, Mestre.")
            break