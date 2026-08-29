### Comandos para rodar

pyinstaller --noconfirm --onedir --windowed ^
  --add-data "web;web" ^
  --add-data "ffmpeg_bin;ffmpeg_bin" ^
  --name "VideoCutter" ^
  main.py

# Video Cutter

App desktop simples para cortar vídeos numa timeline e exportar — incluindo
**batch cutting** (fatiar um intervalo marcado em pedaços de N segundos).
Feito com **Python (Eel) + HTML/CSS/JS**, usando **ffmpeg** para o corte de verdade.

Não é upload web: selecionar vídeo abre o explorador de arquivos nativo do
Windows, e exportar grava os cortes direto numa pasta do seu computador.

---

## Requisitos

- Python 3.9+ instalado no Windows
- **ffmpeg e ffprobe** — duas opções:
  1. Instalar no sistema e garantir que estão no PATH (`ffmpeg -version` funciona no CMD), **ou**
  2. Baixar os binários Windows (`ffmpeg.exe` e `ffprobe.exe`) e colocá-los dentro da pasta
     `ffmpeg_bin/` deste projeto. O programa procura primeiro em `ffmpeg_bin/`, e só
     depois no PATH do sistema. Isso é o recomendado se for empacotar como .exe,
     assim o programa roda sozinho em qualquer PC sem precisar instalar nada.
     Baixe em: https://www.gyan.dev/ffmpeg/builds/ (build "essentials", pasta `bin/`).
- Google Chrome ou Microsoft Edge instalado (o Eel abre a janela do app usando um
  deles em "modo app"; o Windows 10/11 já vem com Edge, então normalmente não
  precisa instalar nada extra).

## Instalação (modo desenvolvimento)

```bash
pip install -r requirements.txt
python main.py
```

Isso abre a janela do programa. Nenhuma configuração adicional é necessária.

## Como usar

1. **Selecionar vídeo** — abre o explorador de arquivos nativo do Windows.
2. O vídeo aparece no player, com uma timeline abaixo.
3. Marque o intervalo que quer cortar:
   - Toque em "Marcar início (I)" e "Marcar fim (O)" enquanto o vídeo toca
     (ou use as teclas `I`/`O` diretamente), **ou**
   - Arraste os dois "pinos" azuis na barra da timeline.
4. (Opcional) Marque **Batch cutting** e informe quantos segundos deve ter
   cada pedaço (padrão: 20s). Exemplo: se você marcou de 1:00 até 2:35
   (95 segundos) e colocar 10s, o programa vai gerar **9 vídeos de 10s + 1 de 5s**.
5. Clique em **"+ Adicionar corte à lista"**. Você pode adicionar quantos
   cortes quiser (batch ou não) antes de exportar.
6. (Opcional) Clique em **"Escolher pasta de destino..."** para escolher onde
   salvar. Se não escolher nada, os arquivos vão para a pasta `exports/`
   ao lado do programa.
7. Clique em **"Exportar tudo"**. Ao terminar, clique em **"Abrir pasta dos
   cortes"** para ver os arquivos no Explorer.

### Corte preciso (reencode) x corte rápido (stream copy)

- **Marcado (padrão)**: reprocessa o vídeo — o corte fica **exatamente** no
  tempo pedido, mas demora um pouco mais.
- **Desmarcado**: usa "stream copy" do ffmpeg — é bem mais rápido, porém o
  corte só pode acontecer em keyframes do vídeo original, então o início/fim
  real pode "escorregar" alguns segundos em relação ao que você marcou.
  Use quando velocidade importa mais que precisão exata (ex: vídeos muito
  longos e cortes grandes).

### Log

Todo upload (vídeo selecionado) e todo corte exportado é gravado em
`logs/cortes_log.txt`, com data/hora, nome do arquivo original, os tempos
de início/fim de cada corte e a pasta de saída. Use o botão **"Ver log"**
no topo para ver na hora, ou **"Abrir pasta do log"** para abrir a pasta
no Explorer.

---

## Empacotar como .exe (PyInstaller)

Para distribuir o programa sem precisar que quem for usar instale Python:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed ^
  --add-data "web;web" ^
  --add-data "ffmpeg_bin;ffmpeg_bin" ^
  --name "VideoCutter" ^
  main.py
```

(o `^` é o separador de linha do CMD do Windows; num único comando também funciona)

Isso gera uma pasta `dist/VideoCutter/` com o `VideoCutter.exe` e tudo que ele
precisa (incluindo a pasta `web/` e os binários do ffmpeg, se você os colocou
em `ffmpeg_bin/` antes de empacotar). Distribua essa pasta inteira.

Notas:
- Use `--onedir` (não `--onefile`) — fica mais rápido para abrir e mais fácil
  de depurar caso algo dê errado, já que o Eel precisa localizar a pasta `web/`.
- Se preferir `--onefile`, o código já trata isso (`sys._MEIPASS` via
  `sys.frozen`), mas o primeiro carregamento fica mais lento porque o
  Windows extrai tudo pra uma pasta temporária a cada execução.
- As pastas `exports/` e `logs/` são criadas automaticamente ao lado do
  `.exe` na primeira execução.

---

## Estrutura do projeto

```
video_cutter_eel/
├── main.py              # backend Python: diálogos nativos, corte via ffmpeg, log
├── requirements.txt
├── ffmpeg_bin/          # (opcional) coloque aqui ffmpeg.exe e ffprobe.exe para Windows
├── web/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js        # timeline, marcação de cortes, batch cutting, chamadas eel.*
├── exports/             # saída padrão dos cortes (se não escolher outra pasta)
└── logs/
    └── cortes_log.txt   # criado no primeiro uso
```
