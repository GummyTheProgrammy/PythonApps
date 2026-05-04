import os
import cv2
import shutil

def organizar_fotos_pb():
    # Pergunta a pasta para o usuário
    caminho_base = input("Mestre, forneça o caminho da pasta: ")

    if not os.path.exists(caminho_base):
        print("Esta pasta não existe!")
        return

    # Define e cria a pasta de destino se necessário
    pasta_destino = os.path.join(caminho_base, "preto e branco")
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    formatos_suportados = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    fotos_movidas = 0

    for arquivo in os.listdir(caminho_base):
        if arquivo.lower().endswith(formatos_suportados):
            caminho_completo = os.path.join(caminho_base, arquivo)
            
            # Carrega a imagem
            img = cv2.imread(caminho_completo)
            
            if img is None:
                continue

            # A mágica acontece aqui: 
            # Separamos os canais Azul, Verde e Vermelho
            b, g, r = cv2.split(img)
            
            # Comparamos se os canais são iguais. 
            # Se a diferença entre eles for zero, a imagem é P&B.
            diferenca_bg = cv2.absdiff(b, g)
            diferenca_gr = cv2.absdiff(g, r)

            if cv2.countNonZero(diferenca_bg) == 0 and cv2.countNonZero(diferenca_gr) == 0:
                # Se for P&B, executa o "Control X" (shutil.move)
                shutil.move(caminho_completo, os.path.join(pasta_destino, arquivo))
                fotos_movidas += 1
                print(f"Movido: {arquivo}")

    print(f"\nTarefa concluída, Mestre. {fotos_movidas} fotos foram movidas para '{pasta_destino}'.")

if __name__ == "__main__":
    organizar_fotos_pb()