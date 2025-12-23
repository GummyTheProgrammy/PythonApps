# Video Processing Automation Suite

Este documento detalha o funcionamento dos scripts contidos na pasta `VideoTools`. Trata-se de um conjunto de ferramentas em Python desenvolvidas para automatizar a manipulação, análise e processamento de vídeos em lote, otimizando fluxos de trabalho de edição e gerenciamento de mídia.

Os scripts incluídos são:
* `SmartVideoCutter.py`
* `TimelineTotalizer.py`
* `MultiVideoInspector.py`
* `MultiVideoToFrames.py`

---

### Como Usar

Para executar qualquer um dos scripts, você precisa ter o **Python** instalado, juntamente com as bibliotecas **`moviepy`**, **`tqdm`**, **`keyboard`**, **`pillow`** e **`numpy`**. Instale todas via terminal com o comando:

```bash
pip install moviepy tqdm keyboard pillow numpy

```

#### 1. SmartVideoCutter.py

Uma ferramenta interativa para unir vídeos e cortá-los em segmentos menores automaticamente.

```bash
python SmartVideoCutter.py

```

* **Funcionalidade:** O script pedirá o caminho da pasta. Use as **setas do teclado (↑/↓)** para ajustar a duração do corte dinamicamente. Escolha a resolução (Horizontal, Vertical ou Customizada) e o padrão de nomeação.

#### 2. TimelineTotalizer.py

Calcula a duração total de todos os vídeos em uma estrutura de pastas (incluindo subpastas).

```bash
python TimelineTotalizer.py

```

* **Output:** Exibe o tempo total formatado (HH:MM:SS), além de totais em minutos e segundos, dependendo da duração acumulada.

#### 3. MultiVideoInspector.py

Analisa rapidamente uma pasta e lista a resolução (Largura x Altura) de cada arquivo de vídeo.

```bash
python MultiVideoInspector.py

```

* **Utilidade:** Perfeito para identificar arquivos fora do padrão (ex: misturar 1080p com 4K) antes de iniciar uma edição.

#### 4. MultiVideoToFrames.py

Extrai todos os quadros (frames) de todos os vídeos de uma pasta e os salva como imagens PNG.

```bash
python MultiVideoToFrames.py

```

* **Nota:** O script utiliza uma barra de progresso visual para acompanhar a extração, que pode ser intensiva.

---

### Como Funciona

Estes scripts demonstram o uso avançado da biblioteca **`moviepy`** combinada com manipulação de sistema de arquivos (`os`, `shutil`) e interação com o usuário.

1. **Interatividade e UX (`SmartVideoCutter.py`)**: Diferente de scripts de linha de comando estáticos, este arquivo utiliza a biblioteca **`keyboard`** para capturar eventos de tecla em tempo real, permitindo ajustes finos de parâmetros (como duração do corte) sem a necessidade de digitar números repetidamente. Ele também implementa lógica de validação de *input* para garantir que resoluções e caminhos sejam válidos.
2. **Processamento Recursivo (`TimelineTotalizer.py`)**: Utiliza `os.walk()` para navegar profundamente em árvores de diretórios. Isso demonstra a capacidade de lidar com estruturas de arquivos complexas, somando metadados de centenas de arquivos sem estourar a memória.
3. **Gerenciamento de Memória (`MultiVideoToFrames.py`)**: Ao lidar com a extração de milhares de imagens, o script não carrega o vídeo inteiro na RAM. Ele utiliza **iteradores** (`clip.iter_frames()`) para processar e salvar um quadro por vez, garantindo eficiência mesmo em vídeos longos.
4. **Concatenação Inteligente**: O `SmartVideoCutter` normaliza os vídeos para uma resolução alvo antes de concatenar, evitando erros comuns de compatibilidade de *codecs* ou dimensões variadas durante o processo de `concatenate_videoclips`.

---

### Benefícios

* **Produtividade**: Automatiza tarefas que levariam horas manualmente, como cortar dezenas de vídeos em partes iguais ou somar a duração de centenas de clipes.
* **Feedback Visual**: Todos os scripts (especialmente os de processamento longo) implementam barras de progresso (`tqdm` ou nativas do `moviepy`) e mensagens de status bilíngues (PT-BR / EN-US), melhorando a experiência do usuário.
* **Flexibilidade**: O código suporta diversos formatos de vídeo (`.mp4`, `.avi`, `.mkv`, etc.) e permite configurações personalizadas de resolução e nomenclatura.

---

### Contribuições

Contribuições para o repositório PythonApps são bem-vindas! Ideias para melhorias na pasta VideoTools:

* Adicionar suporte a aceleração por GPU (NVENC/CUDA) para renderização mais rápida.
* Criar uma interface gráfica (GUI) com `tkinter` ou `PyQt` para selecionar arquivos via "arrastar e soltar".
* Implementar filtros de imagem (ex: preto e branco, contraste) no extrator de frames.

Siga as diretrizes no repositório principal (`../README.md`) para contribuir.

---

### Licença

Este projeto está licenciado. Consulte o arquivo [LICENSE](https://www.google.com/search?q=../LICENSE) no repositório principal para obter detalhes.