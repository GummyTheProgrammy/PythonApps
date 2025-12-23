# PythonApps

PythonApps é uma coleção de aplicativos Python desenvolvidos para demonstrar programação prática, arquitetura modular e funcionalidade do mundo real. O principal objetivo deste repositório é servir como um portfólio técnico que aumente seu valor de mercado como desenvolvedor Python, apresentando habilidades em processamento de dados, automação, scraping, interfaces gráficas e manipulação de mídia.

---

**Objetivo**

- Demonstrar práticas de engenharia de software com projetos pequenos e independentes.
- Expor competências técnicas relevantes a empregadores e clientes (processamento de dados, análise, visualização, automação e GUI).
- Mantenha cada aplicação modular para facilitar a evolução, testes e reutilização de código.

---

**Aplicativos disponíveis**

- **EcomReport** (EcomReport/): ferramenta desktop que processa CSVs de vendas, valida dados, gera estatísticas (receita total, pedidos, AOV) e produz visualizações (barras, linhas, donuts) com exportação para PDF. UI em Tkinter, processamento com Pandas e gráficos com Matplotlib.
- **EliteCritics** (EliteCritics/): mecanismo de raspagem e análise para recalcular pontuações críticas (semelhante ao Tomatometer). Ele raspa páginas, armazena informações em SQLite e calcula métricas ponderadas pela experiência/gênero do crítico.
- **VideoTools** (VideoTools/): utilitários para processamento de vídeo em lote: cortar e concatenar (`SmartVideoCutter.py`), totalizar linhas de tempo (`TimelineTotalizer.py`), inspecionar resoluções (`MultiVideoInspector.py`) e extrair frames (`MultiVideoToFrames.py`) usando `moviepy` e `tqdm`.
- **GhostMouse** (GhostMouse/): gravador e reprodutor de eventos de mouse para automatizar tarefas repetitivas. Usa `pynput` para captura e `pyautogui` para reprodução com atrasos preservados e mecanismo à prova de falhas.
- **Contador** (Contador/): widget simples em Qt (PySide6) — contador minimalista, sempre no topo, com UI circular e arrastável e suporte para copiar valores para a área de transferência.
- **clean_csv** (clean_csv/): scripts utilitários para limpeza de CSVs, remoção de nulos e normalização de campos para preparar dados para análise.
- **TableScripts** (TableScripts/): scripts para criação e alteração de tabelas (ex.: `CreateTables.py`, `AlterTables.py`) usados ​​para gerenciar esquemas de banco de dados simples.
- **Junkcode**: pequenos experimentos e utilidades diversas (análises ad-hoc, transformações) utilizadas como laboratório de ideias.

Cada aplicação inclui um README local com instruções de uso, dependências e exemplos de execução. Exemplos de CSVs e ativos de teste estão presentes nas pastas correspondentes, quando aplicável.

---

**Tecnologias e Bibliotecas**

- **Python 3.8+**: linguagem principal utilizada em todos os projetos.
- **Pandas**: manipulação e limpeza de dados tabulares.
- **Matplotlib**: criação de gráficos e visualizações.
- **Travesseiro**: suporte para composição de imagens e geração de relatórios (PDF a partir de imagem).
- **Tkinter** / **PySide6 (Qt)**: interfaces gráficas (aplicativos de desktop simples e widgets).
- **moviepy, tqdm, numpy**: processamento e iteração de vídeo.
- **pynput, pyautogui**: captura e reproduz eventos de mouse para automação.
- **SQLite**: armazenamento local leve (usado por `EliteCritics`).
- **Requests / BeautifulSoup / Selenium** (quando necessário): raspagem e análise de HTML (dependendo do projeto).

Essas tecnologias foram escolhidas por sua robustez e ampla adoção pelo mercado, facilitando demonstrações práticas de ferramentas e fluxos de trabalho valorizados por equipes de engenharia e recrutadores.

---

### Contribuindo

Contribuições são bem-vindas! Você pode:
- Melhore os aplicativos existentes com novos recursos ou correções de bugs.
- Envie problemas ou receba solicitações via GitHub.

---

### Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter detalhes.