import os
import random
from PyPDF2 import PdfReader, PdfWriter

def extrair_paginas_aleatorias(pdf_path, quantidade=20):
    if not os.path.isfile(pdf_path):
        print("Arquivo não encontrado.")
        return

    reader = PdfReader(pdf_path)
    total_paginas = len(reader.pages)

    if total_paginas < quantidade:
        print(f"O PDF tem apenas {total_paginas} páginas. Não é possível sortear {quantidade}.")
        return

    paginas_sorteadas = sorted(random.sample(range(total_paginas), quantidade))

    writer = PdfWriter()
    for pagina in paginas_sorteadas:
        writer.add_page(reader.pages[pagina])

    nome_base = os.path.splitext(os.path.basename(pdf_path))[0]
    pasta_saida = os.path.dirname(pdf_path)
    caminho_saida = os.path.join(pasta_saida, f"{nome_base}_20_paginas_aleatorias.pdf")

    with open(caminho_saida, "wb") as f:
        writer.write(f)

    print("PDF criado com sucesso!")
    print(f"Arquivo salvo em: {caminho_saida}")
    print("Páginas sorteadas (contagem humana):", [p + 1 for p in paginas_sorteadas])

def main():
    pasta = input("Digite o caminho da pasta onde está o PDF: ").strip().strip('"')
    nome_arquivo = input("Digite o nome do arquivo PDF (ex: arquivo.pdf): ").strip()

    pdf_path = os.path.join(pasta, nome_arquivo)
    extrair_paginas_aleatorias(pdf_path, quantidade=20)

if __name__ == "__main__":
    main()