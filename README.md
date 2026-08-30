# PythonApps

# PT-BR

Este repositório reúne uma coleção de pequenos projetos Python e utilitários organizados como um "projeto de projetos". Cada pasta é tratada como um mini-projeto independente com propósito próprio — GUI, automação, processamento de dados, mídia ou experimentos.

A seguir há um resumo funcional (um parágrafo por pasta) para facilitar a navegação e a identificação do que cada projeto faz. Ao final há tags para pesquisa rápida e, na seção Dados, as extensões de arquivo relevantes (úteis para programas conversores e geradores, ex.: geração de PPTX, imagens ou executáveis).

---

AudioTools

Coleção de utilitários para processamento de áudio: conversão, extração de metadados e operações batch. Scripts em Python (.py) que manipulam arquivos de áudio comuns (.mp3, .wav, .flac) e produzem outputs dependentes do utilitário (logs .txt, gravações .wav).

Gadgets

Pasta com ferramentas de automação e interfaces pequenas: inclui o contador (`Counter`), o gravador/reprodutor de mouse (`GhostMouse`) e o monitor de progresso semanal (`weekly-progress`). Interfaces em Qt/Tkinter e scripts Python (.py). Alguns utilitários têm distribuições empacotadas (.exe) para uso local.

EliteCritics

Motor de scraping e análise para recalcular métricas críticas (tipo Tomatometer): coleta páginas, armazena em SQLite e gera relatórios e métricas ponderadas. Código Python (.py) e banco local (.sqlite / .db).

FileTools

Ferramentas de busca de arquivos e manipulação de caminhos; utilitários para localizar, filtrar e operar em conjuntos de ficheiros grandes. Scripts .py que produzem relatórios em .csv ou .txt.

FolderSizeNexus

Analisador de tamanhos de pastas e uso de disco — gera relatórios e visualizações rápidas do uso por diretório. Scripts .py que exportam somatórios em .csv ou .txt.

ImageTools

Utilitários de manipulação de imagens: redimensionamento, composição e conversão em lote. Trabalha com formatos como .jpg, .png e .bmp; scripts .py com saída de imagens e relatórios.

presentation-notes

Recursos e scripts para gerar conteúdo de apresentação (texto roteirizado). Contém ferramentas que podem exportar ou compor arquivos de apresentação (.pptx) a partir de templates e textos.

junkcode

Laboratório experimental — fragmentos, testes e provas de conceito. Código variado em .py e notas; não necessariamente pronto para produção.

VideoTools

Conjunto de utilitários para processamento de vídeo: inspeção, extração de frames, geração de timelines e cortes automáticos. Contém um subdiretório `VideoCutter` que oferece ferramentas de corte e concatenação. Trabalha com formatos .mp4, .mkv, .avi e gera frames .png/.jpg.

Dados

Pasta para projetos relacionados a dados e conversões:

- limpa_csv — scripts para limpeza e normalização de CSVs. Arquivos: .py. Entradas/saídas: .csv (ex.: example.csv, example_null_removed.csv).
- XMLNexus — processamento, validação e empacotamento de aplicações que trabalham com XML. Arquivos: .py, .spec, planilhas .xlsx e arquivos XML de exemplo (.xml). Distribuição compilada: .exe em `xmlnexus/dist/`.
- qr-code-gen — ferramentas para gerar QR codes e exportar imagens. Arquivos: .py; saídas típicas: .png, .svg, .pdf.

Observação: nesta pasta os tipos de arquivo são relevantes porque esses projetos frequentemente convertem/geram formatos de saída (por exemplo, geração de PPTX em "presentation-notes" ou EXE em XMLNexus).

---

Tags (PT-BR): automação, dados, csv, xml, vídeo, áudio, imagem, gui, pyinstaller, empacotamento, exe, qr, pptx, conversor

---

# ENGLISH

This repository collects small Python projects and utilities organized as a "project of projects". Each folder is a standalone mini-project focused on a specific domain: GUI, automation, data processing, media, or experimentation.

Below is a functional summary (one paragraph per folder) to help quickly understand what each project does. At the end there are tags to ease searching and, under the Data section, the file extensions used by converters and generators (e.g., PPTX output, images or executables).

---

AudioTools

A set of audio-processing utilities: format conversions, metadata extraction and batch operations. Python scripts (.py) operate on common audio files (.mp3, .wav, .flac) and produce outputs such as logs (.txt) or generated audio files (.wav).

Gadgets

Contains small automation and UI utilities: a counter (`Counter`), a mouse recorder/player (`GhostMouse`) and a weekly progress tracker (`weekly-progress`). Implemented with Qt/Tkinter and Python (.py). Some tools are distributed as standalone executables (.exe) for local use.

EliteCritics

A scraping and analysis engine that recalculates critic-based scores (Tomatometer-like). It scrapes web pages, stores data in SQLite, and computes weighted metrics and reports. Contains Python (.py) scripts and local database files (.sqlite/.db).

FileTools

File-search and file-management utilities: tools to locate, filter and operate on large file sets. Scripts (.py) that output reports in .csv or .txt formats.

FolderSizeNexus

Folder size analysis and disk-usage utilities that produce quick summaries and visual reports. Python scripts (.py) produce aggregated data in .csv or .txt.

ImageTools

Image manipulation and batch conversion utilities: resizing, compositing and format conversion for .jpg, .png, .bmp. Implemented as Python scripts (.py) with image outputs.

presentation-notes

Scripts and resources to generate presentation content (scripted text). Contains tools that can export or compose presentation files (.pptx) from templates and text inputs.

junkcode

Experimental playground: snippets, tests and proofs of concept. Mixed Python (.py) code and notes; not necessarily production-ready.

VideoTools

Video processing utilities: inspection, frame extraction, timeline generation and automated cutting. Includes the `VideoCutter` subfolder (previously "Video Cutter") for cutting and concatenation. Supports formats like .mp4, .mkv, .avi and outputs frames as .png/.jpg.

split-pdf

PDF splitting utilities: Python (.py) scripts that take .pdf files and export individual pages (.pdf) or collections as .zip.

Data

Folder for data-related projects and converters:

- limpa_csv — CSV cleaning and normalization scripts. Files: .py. Inputs/outputs: .csv.
- XMLNexus — XML processing, validation and packaged distributions. Files: .py, .spec, sample .xml and spreadsheets (.xlsx). Packaged executable: .exe in `xmlnexus/dist/`.
- qr-code-gen — QR code generation tools. Files: .py; outputs: .png, .svg, .pdf.

Note: file extensions are highlighted because these projects often convert or generate specific output formats (for example, PPTX generation in "presentation-notes" or EXE distribution in XMLNexus).

---

Tags (EN): automation, data, csv, xml, video, audio, image, gui, pyinstaller, packaging, exe, qr, pptx, converter

---

License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
