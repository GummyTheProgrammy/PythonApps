import os
import sys
import subprocess
from moviepy import AudioFileClip  # Importamos o Clip de Áudio, não de Vídeo

# --- CONFIGURAÇÕES ---
OUTPUT_FOLDER = "audio_extracts"
SUPPORTED_EXTENSIONS = ('.mpeg', '.mpg', '.mp4', '.mkv', '.avi', '.mov', '.webm', '.ogg', '.opus', '.m4a')
BITRATE = "320k"

def get_files(folder_path):
    try:
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
        return files
    except FileNotFoundError:
        return None

def convert_with_moviepy(input_path, output_path):
    """Tenta converter usando MoviePy (AudioFileClip)."""
    clip = None
    try:
        # Tenta carregar APENAS o áudio, ignorando vídeo se não existir
        clip = AudioFileClip(input_path)
        clip.write_audiofile(output_path, bitrate=BITRATE, logger=None, codec='mp3')
        return True
    except Exception as e:
        return str(e)
    finally:
        if clip: clip.close()

def convert_force_ffmpeg(input_path, output_path):
    """
    Fallback: Chama o FFmpeg direto via linha de comando.
    Isso resolve arquivos do WhatsApp que o MoviePy não entende.
    """
    try:
        # Comando: ffmpeg -i input -b:a 320k -vn output.mp3
        # -y: sobrescrever / -vn: ignorar vídeo / -loglevel error: silêncio
        cmd = [
            "ffmpeg", 
            "-i", input_path, 
            "-b:a", BITRATE, 
            "-vn", 
            "-y", 
            "-loglevel", "error",
            output_path
        ]
        
        # Executa o comando sem mostrar janela (no Windows)
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        subprocess.run(cmd, check=True, startupinfo=startupinfo)
        return True
    except subprocess.CalledProcessError as e:
        return f"Erro FFmpeg nativo: {e}"
    except FileNotFoundError:
        return "FFmpeg não encontrado no PATH do sistema."

def main():
    print("\n" + "="*60)
    print(f"      WHATSAPP/VIDEO TO MP3 CONVERTER - {BITRATE} (v3.0)   ")
    print("="*60)

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    while True:
        target_folder = input("\nDigite o caminho da pasta: ").strip('"').strip("'")
        if not target_folder: continue
        files = get_files(target_folder)
        
        if files is None: print(f"Pasta não encontrada.")
        elif not files: print(f"Nenhum arquivo compatível encontrado.")
        else: break

    total = len(files)
    sucessos = 0
    erros = []

    print("-" * 60)
    
    for i, filename in enumerate(files):
        input_path = os.path.join(target_folder, filename)
        file_root = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_FOLDER, f"{file_root}.mp3")

        sys.stdout.write(f"\r[{i+1}/{total}] Processando: {filename[:25]}...")
        sys.stdout.flush()

        # TENTATIVA 1: MoviePy (Modo Áudio)
        result = convert_with_moviepy(input_path, output_path)

        # TENTATIVA 2: Se falhar, tenta FFmpeg Direto (Fallback)
        if result is not True:
            # sys.stdout.write(f" (Tentando modo forçado)...")
            result = convert_force_ffmpeg(input_path, output_path)

        if result is True:
            sucessos += 1
            sys.stdout.write(f"\r[{i+1}/{total}] {filename[:25]} -> OK!           \n")
        else:
            erros.append((filename, result))
            sys.stdout.write(f"\r[{i+1}/{total}] {filename[:25]} -> FALHA!        \n")

    print("-" * 60)
    print(f"Sucessos: {sucessos} | Falhas: {len(erros)}")
    
    if erros:
        print("\nErros:")
        for n, e in erros: print(f"- {n}: {e}")

    try: os.startfile(os.path.abspath(OUTPUT_FOLDER))
    except: pass

if __name__ == "__main__":
    main()
    input("\nENTER para sair...")