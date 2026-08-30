# Limpeza da base de críticas especializadas — Rotten Tomatoes

Ferramenta de linha de comando (CMD) para transformar os arquivos brutos
da Rotten Tomatoes em uma base relacional limpa, composta por três
entidades: **Crítico**, **Filme** e **Registro de Crítica**.

Requer Windows (o seletor de pastas usa a API COM nativa do sistema).

## Instalação

```
pip install -r requirements.txt
```

## Execução

```
python main.py
```

O programa abre o seletor de pastas moderno do Windows para escolha da
**pasta de origem** — que deve conter o arquivo de críticas e,
opcionalmente, o arquivo de filmes (ver abaixo) —, em seguida o seletor
de pastas para o **diretório de destino**, e processa os dados exibindo
uma barra de progresso no próprio console.

## Arquivos de origem esperados na pasta selecionada

| Arquivo (identificado pelo nome)      | Obrigatório | Esquema mínimo esperado |
|----------------------------------------|:-----------:|--------------------------|
| contém `critic_review` no nome         | Sim         | `rotten_tomatoes_link, critic_name, top_critic, publisher_name, review_type, review_score, review_date, review_content` |
| contém `movie` no nome                 | Não         | `rotten_tomatoes_link, movie_title, genres, original_release_date` |

O arquivo de filmes corresponde ao `rotten_tomatoes_movies.csv` do
dataset ["Rotten Tomatoes movies and critic reviews dataset"](https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset)
do Kaggle. Quando presente, é usado apenas para enriquecer a entidade
Filme com título, gênero(s) e década de lançamento — o join é feito por
`rotten_tomatoes_link`. Na ausência desse arquivo, a entidade Filme é
gerada normalmente, apenas sem esses três atributos.

**Nota sobre amostras reduzidas:** se as amostras de críticas e de
filmes forem sorteadas independentemente uma da outra (como pode ocorrer
ao gerar amostras menores para teste), a interseção de filmes entre
elas será parcial — parte dos filmes ficará sem título/gênero/década.
Isso é uma limitação da amostragem, não do pipeline: no dataset completo,
por virem da mesma base, a cobertura é praticamente total. O resumo
final exibido no console informa quantos filmes ficaram sem
correspondência (`filmes_sem_metadados`).

## Esquema de saída

| Arquivo                | Conteúdo                                                        |
|-------------------------|-------------------------------------------------------------------|
| `critico.csv`           | `critico_id`, `nome_critico`, `top_critic`                        |
| `filme.csv`             | `filme_id`, `rotten_tomatoes_link`, `titulo_filme`, `genero`, `decada_lancamento` |
| `registro_critica.csv`  | `registro_id`, `filme_id`, `critico_id`, `publisher_name`, `review_type`, `review_score`, `review_score_normalizado`, `review_date`, `review_content` |

`genero` mantém os gêneros originais separados por vírgula (um filme
pode ter mais de um gênero — ex.: `"Action & Adventure, Drama"`).
`decada_lancamento` é derivada de `original_release_date` no formato
`"1990s"`, `"2000s"` etc.

## Regras de negócio aplicadas

1. **Apenas três entidades na saída.** Não há colunas ou arquivos além
   dos listados acima — os atributos de gênero/década/título vivem
   dentro da própria entidade Filme, não criam uma quarta entidade.
2. **Exclusão de avaliações de público.** O arquivo de críticas não
   contém avaliações de público nem um campo diferenciador explícito
   para identificá-las — é uma base exclusivamente de críticas
   especializadas. Ainda assim, o pipeline aplica dois critérios para
   tratar o caso de forma robusta caso o arquivo completo apresente
   variações:
   - registros sem `critic_name` preenchido não constituem uma entidade
     Crítico válida e são descartados;
   - uma verificação defensiva por palavra inteira
     (`core.utils.contem_indicio_de_publico`) descarta registros cujo
     campo `review_type` indique explicitamente avaliação de público
     (ex.: "Audience"). Essa checagem incide apenas sobre o campo de
     tipo/categoria — nunca sobre `critic_name` ou `publisher_name` —
     para não excluir por engano críticos ou veículos cujo nome próprio
     contenha essas palavras (ex.: o veículo "Audiences Everywhere").
3. **Ausência de registros órfãos.** As entidades Filme e Crítico são
   construídas exclusivamente a partir dos registros de crítica que
   sobrevivem à limpeza (regra 2). Por construção, não é possível existir
   filme sem crítica associada ou crítico sem registro de crítica.

## Arquitetura

```
rt_etl/
├── main.py               # Orquestração de linha de comando (CMD)
├── requirements.txt
└── core/
    ├── etl.py             # Regras de negócio e pipeline de dados (sem I/O de UI)
    ├── models.py          # Esquema das entidades de saída
    ├── utils.py            # Funções puras de normalização/parsing/localização de arquivos
    ├── file_dialog.py      # Seletor nativo do Windows (ctypes / IFileOpenDialog)
    └── console_ui.py       # Barra de progresso e mensagens de console (ANSI)
```

A camada `core` não realiza nenhuma chamada a `print`, `input` ou a
qualquer API de interface: `RottenTomatoesETL.processar(...)` recebe um
`callback_progresso(fracao, mensagem)` opcional, chamado periodicamente
durante o processamento. `main.py` é a única camada que conhece o CMD.

### Reaproveitamento com EEL

Essa separação permite empacotar a mesma lógica com [EEL](https://github.com/python-eel/Eel)
sem alterar `core/`: um novo ponto de entrada (por exemplo, `web_main.py`)
importaria `core.etl.RottenTomatoesETL`, exporia uma função com
`@eel.expose` para disparar `processar(...)`, e o `callback_progresso`
chamaria `eel.atualizar_progresso(fracao, mensagem)` para atualizar a
página web em vez de `core.console_ui`. `core.file_dialog` também pode
ser mantido (uma aplicação EEL ainda roda em um processo Python nativo)
ou substituído por um input HTML de pasta, conforme a necessidade.

### Desempenho

O arquivo de críticas é lido em lotes (`chunksize`, padrão de 50.000
linhas) via `pandas.read_csv`, evitando carregar o arquivo completo em
memória. O progresso é calculado a partir da posição do cursor de leitura
(`file.tell()`) em relação ao tamanho do arquivo em bytes, sem exigir uma
pré-contagem de linhas. As tabelas de dimensão (Crítico, Filme e os
metadados carregados do arquivo de filmes) são mantidas em memória
durante o processamento — sua cardinalidade é tipicamente ordens de
grandeza menor que a tabela de fatos (Registro de Crítica); para volumes
extremos de críticos/filmes distintos, essa premissa deve ser
reavaliada.
