import qrcode

def gerar_qr_code(dados, nome_arquivo):
    """
    Gera um arquivo de imagem com o QR Code estático baseado nos dados fornecidos.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(dados)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(nome_arquivo)
    print(f"Operacao concluida. QR Code salvo como: {nome_arquivo}")

if __name__ == "__main__":
    url = input("Insira a URL ou o texto para codificar: ")
    arquivo = input("Insira o nome do arquivo de saida (ex: codigo.png): ")
    gerar_qr_code(url, arquivo)