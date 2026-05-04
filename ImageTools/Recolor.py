from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import os
import random

def quantizar_imagem(img, paleta_rgb):
    """Processa uma única imagem, quantizando suas cores com a paleta fornecida."""
    dados_imagem = np.array(img.convert("RGB"))
    dados_imagem_reshaped = dados_imagem.reshape(-1, 3)
    distancias = np.linalg.norm(dados_imagem_reshaped[:, np.newaxis, :] - paleta_rgb, axis=2)
    indices = np.argmin(distancias, axis=1)
    nova_imagem_array = paleta_rgb[indices].reshape(dados_imagem.shape)
    return Image.fromarray(nova_imagem_array.astype('uint8'))

def aplicar_flash_vertical(img):
    """Aplica o efeito de flash vertical."""
    largura, altura = img.size
    mascara_brilho = np.zeros((altura, largura, 3), dtype=np.uint8)
    for y in range(altura):
        fator = 1 - (y / altura)
        mascara_brilho[y, :, :] = int(255 * fator)
    
    img_np = np.array(img).astype(np.float32)
    img_flash = np.clip(img_np + mascara_brilho, 0, 255)
    return Image.fromarray(img_flash.astype('uint8'))

def ajustar_contraste(img, fator=1.5):
    """Ajusta o contraste da imagem."""
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(fator)

def aplicar_bloom(img, intensidade=5):
    """Aplica o efeito de 'bloom' (vazamento de luz) em áreas brilhantes."""
    img_np = np.array(img.convert('L'))
    brilho_alto = np.where(img_np > 200, 255, 0)
    brilho_alto = Image.fromarray(brilho_alto.astype('uint8'))
    brilho_borrado = brilho_alto.filter(ImageFilter.GaussianBlur(intensidade))
    img_bloom = Image.blend(img, brilho_borrado.convert('RGB'), alpha=0.3)
    return img_bloom

def adicionar_riscos_poeira_grao(img):
    """Adiciona efeitos de riscos, poeira e grão para um visual analógico."""
    largura, altura = img.size
    
    ruido = np.random.randint(-20, 20, (altura, largura, 3), dtype=np.int16)
    img_np = np.array(img).astype(np.int16)
    img_grao = np.clip(img_np + ruido, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_grao)

    mascara_poeira = Image.new('RGB', (largura, altura), color='black')
    pixels_poeira = mascara_poeira.load()
    for _ in range(int(largura * altura * 0.0001)):
        x = random.randint(0, largura - 1)
        y = random.randint(0, altura - 1)
        pixels_poeira[x, y] = (255, 255, 255)
    
    mascara_poeira = mascara_poeira.filter(ImageFilter.BoxBlur(1))
    img = Image.blend(img, mascara_poeira, alpha=0.1)

    return img

def obter_escolhas_usuario():
    """Pergunta ao usuário, uma única vez, quais efeitos aplicar e retorna as escolhas."""
    escolhas = {}
    print("\n--- Configuração de Efeitos para o Lote ---")
    
    escolhas['flash'] = input("Deseja aplicar o 'Flash Vertical' a todas as imagens? (sim/nao): ").lower() == 'sim'
    escolhas['contraste'] = input("Deseja aplicar 'Contraste Forte' a todas as imagens? (sim/nao): ").lower() == 'sim'
    escolhas['bloom'] = input("Deseja aplicar o 'Bloom' a todas as imagens? (sim/nao): ").lower() == 'sim'
    escolhas['analogico'] = input("Deseja aplicar os efeitos 'Riscos, Poeira e Grão' a todas as imagens? (sim/nao): ").lower() == 'sim'

    return escolhas

# Função principal (agora mais eficiente)
def processar_lote_imagens_com_efeitos(paleta_hex):
    pasta_entrada = "batch"
    pasta_saida = "processed"

    if not os.path.exists(pasta_entrada):
        os.makedirs(pasta_entrada)
        print(f"Pasta '{pasta_entrada}' criada. Coloque suas imagens aqui.")
        return
        
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    paleta_rgb = np.array([tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for c in paleta_hex])
    extensoes_validas = ('.png', '.jpg', '.jpeg')
    arquivos_encontrados = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(extensoes_validas)]
    
    if not arquivos_encontrados:
        print(f"Nenhuma imagem encontrada na pasta '{pasta_entrada}'.")
        return
    
    # 1. Obter as escolhas do usuário ANTES de processar o lote
    escolhas_usuario = obter_escolhas_usuario()
    
    print(f"\nIniciando o processamento de {len(arquivos_encontrados)} imagem(ns)...")
    
    # 2. Iterar sobre cada imagem e aplicar as escolhas
    for nome_arquivo in arquivos_encontrados:
        caminho_completo_entrada = os.path.join(pasta_entrada, nome_arquivo)
        caminho_completo_saida = os.path.join(pasta_saida, f"efeitos_{nome_arquivo}")
        
        print(f"Processando: {nome_arquivo}...")
        try:
            img = Image.open(caminho_completo_entrada)
            
            # Aplica a quantização de cor primeiro
            img_processada = quantizar_imagem(img, paleta_rgb)
            
            # Aplica os efeitos baseados nas escolhas do usuário
            if escolhas_usuario['flash']:
                img_processada = aplicar_flash_vertical(img_processada)
            if escolhas_usuario['contraste']:
                img_processada = ajustar_contraste(img_processada)
            if escolhas_usuario['bloom']:
                img_processada = aplicar_bloom(img_processada)
            if escolhas_usuario['analogico']:
                img_processada = adicionar_riscos_poeira_grao(img_processada)
            
            # Redimensiona para 1080x1350
            img_final = img_processada.resize((1080, 1350), Image.LANCZOS)
            
            img_final.save(caminho_completo_saida)
            print(f"Salvo em: {caminho_completo_saida}")
            
        except Exception as e:
            print(f"Erro ao processar a imagem {nome_arquivo}: {e}")

    print("\nProcessamento concluído.")

# Definir a paleta de cores
paleta = ["#FFE3B3", "#FF9A52", "#FF5252", "#C91E5A", "#3D2922"]

# Chamar a função principal
processar_lote_imagens_com_efeitos(paleta)