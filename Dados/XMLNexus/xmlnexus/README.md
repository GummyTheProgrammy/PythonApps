# XMLNexus

Conversor de XML de NF-e para planilha Excel (.xlsx), com interface neumorphism.

## 1. Instalar dependências (rodar no Windows, no PowerShell/CMD, dentro da pasta do projeto)

```
pip install -r requirements.txt
```

Ou, se preferir instalar manualmente:

```
pip install eel openpyxl pyinstaller
```

> Obs.: o Eel abre a interface usando o Chrome ou Edge instalado no PC (modo "app").
> Se nenhum dos dois for encontrado, ele cai automaticamente para o navegador padrão.

## 2. Rodar em modo desenvolvimento (direto com Python)

```
python main.py
```

Isso abre a janela do XMLNexus. Clique em **"Selecionar pasta"**, escolha a pasta
com os XMLs das notas, depois clique em **"Gerar planilha"**.

- A planilha é salva **dentro da própria pasta selecionada**, com o nome
  `XMLNexus_Planilha_AAAAMMDD_HHMMSS.xlsx`.
- Se algum XML der erro (arquivo corrompido, não é NF-e, etc.), ele é **pulado**
  e reportado tanto na tela quanto em um arquivo de log
  `XMLNexus_log_erros_AAAAMMDD_HHMMSS.txt`, salvo na mesma pasta.
- Arquivos que não são `.xml` são ignorados automaticamente.

## 3. Empacotar como .exe (para rodar nativamente no Windows, sem precisar de Python instalado)

Dentro da pasta do projeto, rode:

```
pyinstaller --onefile --windowed --name XMLNexus --add-data "web;web" main.py
```

Parâmetros:
- `--onefile` → gera um único .exe
- `--windowed` → não abre o console preto do CMD junto (equivalente ao antigo `--noconsole`)
- `--add-data "web;web"` → inclui a pasta `web` (HTML/CSS/JS) dentro do executável.
  **Atenção**: no Windows o separador é `;` (ponto e vírgula). Se você compilar no Linux/Mac, use `:` no lugar.

Ao final, o executável estará em:

```
dist\XMLNexus.exe
```

Você pode copiar esse `.exe` para qualquer pasta ou pendrive e rodar sem precisar
instalar Python na máquina de destino (o Chrome/Edge continua sendo necessário
para exibir a interface).

### Se quiser um ícone personalizado
```
pyinstaller --onefile --windowed --name XMLNexus --add-data "web;web" --icon "caminho\para\icone.ico" main.py
```

### Se o Windows Defender/SmartScreen bloquear o .exe na primeira execução
Isso é normal para executáveis não assinados digitalmente gerados com PyInstaller.
Basta clicar em "Mais informações" → "Executar assim mesmo".

## Estrutura do projeto

```
xmlnexus/
├── main.py              -> backend Python (parsing do XML + geração do Excel + Eel)
├── requirements.txt
├── LEIA-ME.md
└── web/
    ├── index.html
    ├── style.css
    └── script.js
```

## Colunas geradas na planilha

| Coluna | Origem no XML |
|---|---|
| Arquivo | nome do arquivo .xml |
| Numero da NF | `ide/nNF` |
| Data de Emissao | `ide/dhEmi` (convertida para DD/MM/AAAA) |
| Codigo do Produto | `det/prod/cProd` |
| Descricao do Produto | `det/prod/xProd` |
| NCM | `det/prod/NCM` |
| Unidade | `det/prod/uCom` |
| Quantidade | `det/prod/qCom` |
| Valor Unitario | `det/prod/vUnCom` |
| Valor Total | `det/prod/vProd` |

Cada item de produto vira uma linha — se uma nota tiver 3 produtos, ela gera 3 linhas
na planilha, todas com o mesmo número de NF e data de emissão.
