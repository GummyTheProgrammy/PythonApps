# Analisador de Diretórios

Aplicação de varredura recursiva e visualização hierárquica de tamanho de
diretórios, construída com Eel (backend Python + frontend HTML/CSS/JS).

## Estrutura de pastas

```
directory_analyzer/
├── main.py                 # Backend Eel: varredura, progresso, seletor nativo
├── requirements.txt
├── README.md
└── web/
    ├── index.html
    ├── css/
    │   └── style.css       # Estilo Neumorfismo
    └── js/
        └── app.js          # Gráfico de rosca (Chart.js), drill-down, lista
```

## Requisitos

- Windows (o seletor nativo de pastas depende do PowerShell/Windows Forms).
- Python 3.9 ou superior.

## Instalação

```
pip install -r requirements.txt
```

## Execução

```
python main.py
```

## Funcionamento

1. O botão "Selecionar Pasta" aciona o seletor nativo do Windows, executado
   via PowerShell em modo STA e trazido ao primeiro plano.
2. Ao confirmar a seleção, o backend varre o diretório recursivamente em
   uma thread separada, permitindo que a interface continue respondendo e
   que o usuário navegue pelas pastas já indexadas enquanto o restante da
   varredura é concluído.
3. O progresso (valor `float` de 0.0 a 100.0) é reportado ao frontend e
   exibido em uma barra fixa no canto inferior da tela.
4. Os dados de cada diretório são exibidos em um gráfico de rosca
   (Chart.js) e em uma lista de apoio, ambos com suporte a navegação
   drill-down (clique para entrar em uma subpasta) e botão de retorno.
5. Os tamanhos são exibidos em Bytes/KB/MB/GB/TB, com a fonte da lista de
   apoio aumentando conforme a unidade (KB menor, MB médio, GB grande,
   TB muito grande). Nomes que não couberem na linha são exibidos com
   reticências no meio, preservando a extensão do arquivo.

## Empacotamento (PyInstaller)

Para gerar um executável standalone incluindo a pasta `web`:

```
pyinstaller --noconfirm --onefile --windowed --add-data "web;web" main.py
```

O executável resultante ficará em `dist/main.exe`. Caso o antivírus do
sistema sinalize falsos positivos (comum em builds do PyInstaller), utilize
`--onedir` no lugar de `--onefile` para reduzir a chance de bloqueio.

## Observações técnicas

- A varredura utiliza duas fases: (1) descoberta da estrutura e tamanho
  exato de arquivos, permitindo navegação imediata; (2) consolidação dos
  tamanhos de diretórios, das subpastas mais profundas até a raiz. Durante
  a fase 2, o rótulo "calculando..." é exibido para pastas cujo tamanho
  agregado ainda não foi consolidado.
- Diretórios sem permissão de leitura são ignorados silenciosamente
  durante a varredura.
