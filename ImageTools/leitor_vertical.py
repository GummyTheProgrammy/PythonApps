import os
import tkinter as tk
from tkinter import filedialog
import webbrowser
from flask import Flask, render_template_string, send_from_directory, jsonify
from threading import Timer

app = Flask(__name__)
BASE_DIR = ""
IMAGE_LIST = []

# Template HTML embutido para não precisar de múltiplos arquivos
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Leitor Vertical Mestre</title>
    <style>
        body, html {
            margin: 0; 
            padding: 0; 
            background-color: #0f0f0f;
            overflow-x: auto; /* Permite scroll horizontal se o zoom for muito grande */
        }
        
        /* Container que empilha as imagens */
        #image-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        
        /* Estilo das imagens para parecerem uma só */
        .comic-page {
            width: 100%; /* Largura inicial */
            max-width: none;
            display: block;
            margin: 0; 
            padding: 0;
            border: none;
        }

        /* Botões flutuantes no canto inferior direito */
        #controls {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: rgba(30, 30, 30, 0.8);
            padding: 15px;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }

        button {
            background: #444; 
            color: white; 
            border: none;
            padding: 12px 20px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: bold;
            border-radius: 6px;
            transition: background 0.2s;
        }

        button:hover { 
            background: #666; 
        }
        
        /* Customizando a barra de rolagem vertical */
        ::-webkit-scrollbar {
            width: 12px;
        }
        ::-webkit-scrollbar-track {
            background: #111; 
        }
        ::-webkit-scrollbar-thumb {
            background: #555; 
            border-radius: 6px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #777; 
        }
    </style>
</head>
<body>
    <div id="controls">
        <button onclick="zoom(10)">Zoom +</button>
        <button onclick="zoom(-10)">Zoom -</button>
        <button onclick="toggleFullScreen()">Fullscreen ⛶</button>
    </div>
    
    <div id="image-container"></div>

    <script>
        let currentZoom = 100; // Porcentagem inicial da largura da tela (100vw)

        function loadImages() {
            fetch('/get_images')
                .then(response => response.json())
                .then(images => {
                    const container = document.getElementById('image-container');
                    images.forEach(img => {
                        const imgEl = document.createElement('img');
                        imgEl.src = '/img/' + encodeURIComponent(img);
                        imgEl.className = 'comic-page';
                        imgEl.loading = "lazy"; // Carrega as imagens aos poucos para não travar
                        container.appendChild(imgEl);
                    });
                    updateZoom();
                });
        }

        function zoom(amount) {
            currentZoom += amount;
            if (currentZoom < 10) currentZoom = 10; // Limite mínimo de zoom
            updateZoom();
        }

        function updateZoom() {
            const images = document.querySelectorAll('.comic-page');
            images.forEach(img => {
                img.style.width = currentZoom + 'vw';
            });
        }

        function toggleFullScreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log(`Erro ao tentar fullscreen: ${err.message}`);
                });
            } else {
                document.exitFullscreen();
            }
        }

        // Inicia o carregamento assim que a página abrir
        window.onload = loadImages;
    </script>
</body>
</html>
"""

def scan_directory(base_path):
    """Vasculha os diretórios em ordem alfabética e retorna o vetor de imagens."""
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    images = []
    
    for root, dirs, files in os.walk(base_path):
        # Garante que as pastas e arquivos sejam processados em ordem alfabética
        dirs.sort()
        files.sort()
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                # Cria um caminho relativo para o Flask servir a imagem corretamente
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                # Troca barras do Windows por barras normais de web
                images.append(rel_path.replace('\\', '/'))
                
    return images

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_images')
def get_images():
    return jsonify(IMAGE_LIST)

@app.route('/img/<path:filename>')
def serve_image(filename):
    return send_from_directory(BASE_DIR, filename)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Oculta a janela principal do Tkinter
    root = tk.Tk()
    root.withdraw()
    
    # Pede o diretório ao usuário
    print("Selecione o diretório contendo as imagens...")
    selected_dir = filedialog.askdirectory(title="Selecione a pasta raiz das imagens")
    
    if selected_dir:
        BASE_DIR = selected_dir
        print(f"Lendo diretório: {BASE_DIR}")
        IMAGE_LIST = scan_directory(BASE_DIR)
        print(f"{len(IMAGE_LIST)} imagens encontradas.")
        
        if len(IMAGE_LIST) > 0:
            # Abre o navegador automaticamente após 1 segundo
            Timer(1.25, open_browser).start()
            # Inicia o servidor local
            app.run(port=5000)
        else:
            print("Nenhuma imagem encontrada no diretório selecionado.")
    else:
        print("Operação cancelada.")