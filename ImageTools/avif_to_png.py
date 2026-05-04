import os
import sys
import time
from PIL import Image
import pillow_avif  # Necessário para registrar o decodificador AVIF no PIL

# --- CONFIGURAÇÕES ---
OUTPUT_FOLDER = "render"
SUPPORTED_EXTENSIONS = ('.avif',)

def get_files_in_folder(folder_path):
    """Retorna lista de arquivos AVIF na pasta."""
    try:
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
        return files
    except FileNotFoundError:
        return None

def convert_image(file_path, output_path):
    """Converte uma única imagem para PNG."""
    try:
        with Image.open(file_path) as img:
            # Converte para RGBA ou RGB para garantir compatibilidade com PNG
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')
            img.save(output_path, "PNG", optimize=True)
        return True
    except Exception as e:
        return str(e)

def main():
    print("\n" + "="*60)
    print("           AVIF TO PNG CONVERTER - TOOL           ")
    print("="*60)

    # Cria a pasta render se não existir
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"[INFO] Pasta '{OUTPUT_FOLDER}' criada.")

    while True:
        target_folder = input("\nDigite o caminho da pasta com os arquivos AVIF: ").strip('"').strip("'")
        
        if not target_folder:
            print("Caminho vazio. Tente novamente.")
            continue
            
        files = get_files_in_folder(target_folder)

        if files is None:
            print(f"[ERRO] A pasta '{target_folder}' não foi encontrada.")
        elif not files:
            print(f"[AVISO] Nenhum arquivo .avif encontrado em '{target_folder}'.")
        else:
            print(f"\nEncontrados {len(files)} arquivos. Iniciando conversão...")
            break

    total = len(files)
    sucessos = 0
    erros = []

    # Loop de conversão com barra de progresso simples
    for i, filename in enumerate(files):
        input_path = os.path.join(target_folder, filename)
        
        # Define nome de saída (troca extensão para .png)
        file_root = os.path.splitext(filename)[0]
        output_filename = f"{file_root}.png"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        result = convert_image(input_path, output_path)

        if result is True:
            sucessos += 1
        else:
            erros.append((filename, result))

        # Feedback visual (estilo CLI)
        sys.stdout.write(f"\rProcessando: {i+1}/{total} - {filename[:20]}...")
        sys.stdout.flush()

    print(f"\n\n" + "="*60)
    print(f"CONVERSÃO FINALIZADA")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas:   {len(erros)}")
    
    if erros:
        print("\nArquivos com erro:")
        for nome, erro in erros:
            print(f"- {nome}: {erro}")

    print(f"\nAs imagens estão salvas na pasta: {os.path.abspath(OUTPUT_FOLDER)}")

if __name__ == "__main__":
    main()
    input("\nPressione ENTER para sair...")