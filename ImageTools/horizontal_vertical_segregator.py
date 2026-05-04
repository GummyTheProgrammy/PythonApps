import os
import shutil
import sys
import time
import traceback  # Essencial para ver o erro antes de fechar

def instalar_dependencias():
    print("⚠️  Faltam bibliotecas necessárias.")
    print("Por favor, abra o terminal e rode: pip install Pillow tqdm")

# Tentativa de importação segura
try:
    from PIL import Image
    from tqdm import tqdm
except ImportError as e:
    print(f"❌ Erro de Importação: {e}")
    instalar_dependencias()
    input("\nPressione ENTER para sair...")
    sys.exit()

def resolver_colisao_nome(pasta_destino, nome_arquivo):
    base, extensao = os.path.splitext(nome_arquivo)
    contador = 1
    novo_nome = nome_arquivo
    
    # Enquanto existir um arquivo com esse nome, incrementa o contador
    while os.path.exists(os.path.join(pasta_destino, novo_nome)):
        novo_nome = f"{base}_copy_{contador}{extensao}"
        contador += 1
        
    return novo_nome

def main():
    print("--- 📂 Organizador Vertical/Horizontal (Modo Seguro) ---")
    print("Dica: Você pode colar o caminho da pasta aqui.")
    
    diretorio_base = input("Mestre, insira o caminho da pasta: ").strip()
    
    # Remove aspas extras que o Windows às vezes coloca ao copiar caminho
    diretorio_base = diretorio_base.strip('"').strip("'")

    if not os.path.exists(diretorio_base):
        print(f"\n❌ ERRO: A pasta '{diretorio_base}' não foi encontrada.")
        return

    # Criar pastas
    dir_vert = os.path.join(diretorio_base, "vertical")
    dir_horiz = os.path.join(diretorio_base, "horizontal")
    
    os.makedirs(dir_vert, exist_ok=True)
    os.makedirs(dir_horiz, exist_ok=True)

    extensoes = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
    arquivos = [f for f in os.listdir(diretorio_base) if f.lower().endswith(extensoes)]
    
    if not arquivos:
        print("\n⚠️  Nenhuma imagem encontrada na raiz desta pasta.")
        return

    print(f"\nEncontradas {len(arquivos)} imagens. Iniciando...")
    time.sleep(1) # Pausa dramática para leitura

    movidos_h = 0
    movidos_v = 0
    erros = 0

    # Barra de progresso
    for arquivo in tqdm(arquivos, unit="img"):
        caminho_origem = os.path.join(diretorio_base, arquivo)
        
        try:
            with Image.open(caminho_origem) as img:
                largura, altura = img.size
                
                if largura > altura:
                    destino = dir_horiz
                    tipo = "H"
                else:
                    destino = dir_vert
                    tipo = "V"

            # Move o arquivo
            nome_final = resolver_colisao_nome(destino, arquivo)
            shutil.move(caminho_origem, os.path.join(destino, nome_final))
            
            if tipo == "H":
                movidos_h += 1
            else:
                movidos_v += 1

        except Exception as e:
            # Erro em um arquivo específico não para o loop
            erros += 1
            # Se quiser ver o erro específico de cada arquivo, descomente a linha abaixo:
            # print(f"Erro no arquivo {arquivo}: {e}")

    print("\n" + "="*40)
    print("✅  CONCLUSÃO DO RELATÓRIO:")
    print(f"↔️  Horizontais movidas: {movidos_h}")
    print(f"↕️  Verticais movidas:   {movidos_v}")
    print(f"⚠️  Falhas/Ignorados:    {erros}")
    print("="*40)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        # AQUI ESTÁ A PROTEÇÃO
        # Se o programa quebrar feio, ele mostra o erro e espera
        print("\n\n" + "!"*50)
        print("CRASH! Ocorreu um erro fatal no programa:")
        print("!"*50 + "\n")
        traceback.print_exc() # Imprime o erro técnico
    finally:
        # Isso garante que a janela NUNCA feche sozinha
        print("\n")
        input(">>> Pressione ENTER para fechar esta janela... <<<")