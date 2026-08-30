# Matriz de Expertise dos Críticos — Rotten Tomatoes

Ferramenta de linha de comando (CMD) que lê a base limpa gerada pelo
projeto `rt_etl` e produz a **Matriz de Expertise**: para cada crítico,
classifica seu volume de atuação em cada gênero e em cada década de
lançamento, em um nível de expertise.

Requer Windows (o seletor de pastas usa a API COM nativa do sistema) e a
base já processada por `rt_etl` (arquivos `critico.csv`, `filme.csv` e
`registro_critica.csv` em uma mesma pasta).

## Instalação

```
pip install -r requirements.txt
```

## Execução

```
python main.py
```

O programa pergunta no console onde está a base de dados, abre o
seletor de pastas nativo do Windows para escolha da pasta com a base
limpa, em seguida o seletor de pastas para o diretório de destino, e
processa os dados exibindo uma barra de progresso verde no console.
Ao final, gera dois arquivos: `matriz_expertise.csv` (dados brutos) e
`matriz_expertise.html` (relatório interativo — busca por nome e
ordenação por coluna).

## Parâmetros ajustáveis

No topo de `main.py`:

| Variável | Padrão | Significado |
|---|---|---|
| `LIMITE_NOVATO_MAX` | 20 | Até quantos filmes = Novato |
| `LIMITE_ENTUSIASTA_MAX` | 50 | Até quantos filmes = Entusiasta |
| `LIMITE_ESPECIALISTA_MAX` | 99 | Até quantos filmes = Especialista |
| `ROTULO_NIVEL_MAXIMO_GENERO` | "Autoridade" | Rótulo acima de `LIMITE_ESPECIALISTA_MAX` filmes, por gênero |
| `ROTULO_NIVEL_MAXIMO_DECADA` | "Historiador" | Rótulo acima de `LIMITE_ESPECIALISTA_MAX` filmes, por década |
| `TRATAR_ZERO_COMO_NOVATO` | `False` | Ver seção abaixo |

## Regras de negócio aplicadas

- **Uma coluna por gênero e uma coluna por década existentes na base** —
  os conjuntos de colunas não são fixos: são extraídos dinamicamente a
  partir dos gêneros e décadas presentes em `filme.csv`, o que faz o
  script se adaptar automaticamente a bases de volumes/composições
  diferentes.
- **"Filmes analisados"** é contado por **filme distinto**, não por
  crítica: se um crítico escreveu duas críticas para o mesmo filme, isso
  conta como 1 filme analisado, não 2. A deduplicação é feita via
  conjunto (`set`) de `filme_id` por crítico.
- **Classificação por faixa** (idêntica para gênero e década, mudando
  apenas o rótulo do nível máximo): até 20 filmes = Novato; 21–50 =
  Entusiasta; 51–99 = Especialista; 100+ = Autoridade (gênero) ou
  Historiador (década).
- **Zero filmes analisados em uma coluna**: por padrão
  (`TRATAR_ZERO_COMO_NOVATO = False`), a célula fica em branco (`—`) em
  vez de "Novato", para distinguir "o crítico nunca atuou nesse
  gênero/década" de "atuou muito pouco". A leitura literal das regras de
  negócio ("até 20 filmes = Novato") tecnicamente inclui o zero; se
  preferir essa leitura literal, basta ajustar a variável para `True`.

## Esquema de saída

`matriz_expertise.csv` / `matriz_expertise.html`:

```
critico_id, nome_critico, top_critic, total_filmes_analisados,
<uma coluna por genero existente>, <uma coluna por decada existente>
```

## Arquitetura

```
rt_expertise/
├── main.py                 # Orquestração de linha de comando (CMD) + parâmetros ajustáveis
├── requirements.txt
└── core/
    ├── matriz.py             # Regras de negócio e pipeline de agregação (sem I/O de UI)
    ├── relatorio_html.py      # Geração do relatório HTML autocontido (HTML/CSS/JS puro)
    ├── models.py              # Nomes de arquivo/colunas da base limpa consumida
    ├── file_dialog.py         # Seletor nativo do Windows (ctypes / IFileOpenDialog) — reaproveitado do rt_etl
    └── console_ui.py          # Barra de progresso e mensagens de console (ANSI) — reaproveitado do rt_etl
```

`core.matriz` não realiza nenhuma chamada a `print`, `input` ou a
qualquer API de interface: `ConstrutorMatrizExpertise.construir(...)`
recebe um `callback_progresso(fracao, mensagem)` opcional. `main.py` é
a única camada que conhece o CMD; `core.relatorio_html` conhece apenas
HTML/CSS/JS, não a lógica de agregação.

### Reaproveitamento com EEL

Um novo ponto de entrada (`web_main.py`) importaria
`core.matriz.ConstrutorMatrizExpertise`, exporia uma função com
`@eel.expose` para disparar `construir(...)`, e o `callback_progresso`
chamaria `eel.atualizar_progresso(fracao, mensagem)` em vez de
`core.console_ui`. O próprio `matriz_expertise.html` gerado já pode ser
servido diretamente como a tela de resultado do app EEL — não precisa
ser reescrito.

### Desempenho

`registro_critica.csv` é lido em lotes (`chunksize`, padrão de 100.000
linhas) via `pandas.read_csv`. O progresso é calculado a partir da
posição do cursor de leitura (`file.tell()`) em relação ao tamanho do
arquivo. As entidades Crítico e Filme, além do mapeamento
crítico→conjunto de filmes distintos, são mantidos em memória — sua
cardinalidade combinada é da mesma ordem de grandeza da tabela de fatos
já processada por `rt_etl`.
