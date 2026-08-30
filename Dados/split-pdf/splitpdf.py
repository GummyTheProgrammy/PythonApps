import os
from PyPDF2 import PdfReader, PdfWriter

def dividir_pdf_em_blocos(pdf_path, paginas_por_arquivo=7):
    if not os.path.isfile(pdf_path):
        print("Arquivo não encontrado.")
        return

    reader = PdfReader(pdf_path)
    total_paginas = len(reader.pages)

    nome_base = os.path.splitext(os.path.basename(pdf_path))[0]
    pasta_saida = os.path.dirname(pdf_path)

    for i in range(0, total_paginas, paginas_por_arquivo):
        writer = PdfWriter()

        for j in range(i, min(i + paginas_por_arquivo, total_paginas)):
            writer.add_page(reader.pages[j])

        numero_arquivo = (i // paginas_por_arquivo) + 1
        nome_saida = f"{nome_base}_parte_{numero_arquivo}.pdf"
        caminho_saida = os.path.join(pasta_saida, nome_saida)

        with open(caminho_saida, "wb") as f:
            writer.write(f)

        print(f"Criado: {caminho_saida}")

def main():
    pasta = input("Digite o caminho da pasta onde está o PDF: ").strip().strip('"')
    nome_arquivo = input("Digite o nome do arquivo PDF (ex: arquivo.pdf): ").strip()

    pdf_path = os.path.join(pasta, nome_arquivo)
    dividir_pdf_em_blocos(pdf_path, paginas_por_arquivo=7)

if __name__ == "__main__":
    main()