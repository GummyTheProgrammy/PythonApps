import os
from PIL import Image
from tqdm import tqdm

def process_images():
    # Solicita o diretório de origem
    diretorio = input("Digite o caminho do diretório com as imagens PNG: ").strip()

    # Verifica se o caminho inserido é válido
    if not os.path.isdir(diretorio):
        print("Diretório não encontrado. Verifique o caminho e tente novamente.")
        return

    # Define e cria a pasta 'render' dentro do diretório fornecido
    render_dir = os.path.join(diretorio, "render")
    if not os.path.exists(render_dir):
        os.makedirs(render_dir)

    # Mapeia todos os arquivos .png da pasta
    png_files = [f for f in os.listdir(diretorio) if f.lower().endswith('.png')]

    if not png_files:
        print("Nenhuma imagem PNG encontrada neste diretório.")
        return

    print(f"\nEncontradas {len(png_files)} imagens. Iniciando o processamento...")

    # tqdm cria a barra de progresso visual, calculando % e ETA automaticamente
    for filename in tqdm(png_files, desc="Processando", unit="img"):
        input_path = os.path.join(diretorio, filename)
        output_path = os.path.join(render_dir, filename)

        try:
            # Abre a imagem original garantindo que tenha o canal Alpha (transparência)
            with Image.open(input_path) as img:
                img = img.convert("RGBA")
                
                # Cria um fundo 100% preto com as mesmas dimensões da imagem original
                black_bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
                
                # Faz a composição (sobreposição) da imagem original sobre o fundo preto
                composite_img = Image.alpha_composite(black_bg, img)
                
                # Remove o canal alpha convertendo para RGB e salva na pasta render
                composite_img.convert("RGB").save(output_path, "PNG")
                
        except Exception as e:
            # Em caso de arquivo corrompido ou erro de leitura, avisa sem travar o loop
            print(f"\nErro ao processar a imagem '{filename}': {e}")

    print("\nProcessamento concluído com sucesso! Os arquivos estão na pasta 'render'.")

if __name__ == "__main__":
    process_images()