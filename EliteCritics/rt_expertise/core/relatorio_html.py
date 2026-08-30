"""
core.relatorio_html
====================

Geracao do relatorio HTML autocontido (sem dependencias externas de
build/framework) que serve como interface de apresentacao da Matriz de
Expertise. Contem apenas HTML/CSS/JS puro, embutido em um unico arquivo.

Este modulo e isolado da logica de agregacao (`core.matriz`): recebe
apenas dados ja calculados e devolve uma string HTML pronta para
gravacao em disco.
"""

from __future__ import annotations

import html as html_lib

_ORDEM_NIVEL = {"": 0, "Novato": 1, "Entusiasta": 2, "Especialista": 3}


def _ordinal_nivel(rotulo: str) -> int:
    """Mapeia um rotulo de nivel para um valor ordinal usado na ordenacao
    (rotulos de topo, como "Autoridade" ou "Historiador", recebem o maior
    valor, 4)."""
    return _ORDEM_NIVEL.get(rotulo, 4 if rotulo else 0)


def _classe_nivel(rotulo: str) -> str:
    mapa = {
        "": "nivel-vazio",
        "Novato": "nivel-1",
        "Entusiasta": "nivel-2",
        "Especialista": "nivel-3",
    }
    return mapa.get(rotulo, "nivel-4")


def gerar_relatorio(
    caminho_html: str,
    linhas: list,
    colunas_genero: list,
    colunas_decada: list,
    limiares_genero,
    limiares_decada,
) -> None:
    """Gera e grava em `caminho_html` o relatorio HTML da Matriz de Expertise."""

    colunas_fixas = [
        ("nome_critico", "Critico"),
        ("top_critic", "Top Critic"),
        ("total_filmes_analisados", "Total de filmes analisados"),
    ]
    colunas_dinamicas = [(c, c) for c in colunas_genero] + [(c, c) for c in colunas_decada]
    todas_colunas = colunas_fixas + colunas_dinamicas

    cabecalho_html = []
    for indice, (_, rotulo) in enumerate(todas_colunas):
        cabecalho_html.append(
            f'<th data-indice="{indice}" onclick="ordenarPor({indice})">{html_lib.escape(rotulo)}'
            f'<span class="seta-ordenacao"></span></th>'
        )

    linhas_html = []
    for linha in linhas:
        celulas = []
        celulas.append(
            f'<td class="coluna-critico" data-valor="{html_lib.escape(linha["nome_critico"].lower())}">'
            f'{html_lib.escape(linha["nome_critico"])}</td>'
        )
        celulas.append(
            f'<td data-valor="{1 if linha["top_critic"] else 0}">{"Sim" if linha["top_critic"] else "Nao"}</td>'
        )
        celulas.append(
            f'<td data-valor="{linha["total_filmes_analisados"]}">{linha["total_filmes_analisados"]}</td>'
        )
        for coluna, _ in [(c, c) for c in colunas_genero] + [(c, c) for c in colunas_decada]:
            rotulo_nivel = linha.get(coluna, "")
            ordinal = _ordinal_nivel(rotulo_nivel)
            classe = _classe_nivel(rotulo_nivel)
            texto = html_lib.escape(rotulo_nivel) if rotulo_nivel else "&mdash;"
            celulas.append(f'<td class="{classe}" data-valor="{ordinal}">{texto}</td>')

        linhas_html.append(
            f'<tr data-nome="{html_lib.escape(linha["nome_critico"].lower())}">' + "".join(celulas) + "</tr>"
        )

    total_criticos = len(linhas)
    total_generos = len(colunas_genero)
    total_decadas = len(colunas_decada)

    legenda_generos = (
        f'Ate {limiares_genero.limite_novato_max} filmes: Novato &middot; '
        f'{limiares_genero.limite_novato_max + 1} a {limiares_genero.limite_entusiasta_max}: Entusiasta &middot; '
        f'{limiares_genero.limite_entusiasta_max + 1} a {limiares_genero.limite_especialista_max}: Especialista &middot; '
        f'{limiares_genero.limite_especialista_max + 1}+: {html_lib.escape(limiares_genero.rotulo_topo)}'
    )
    legenda_decadas = (
        f'Ate {limiares_decada.limite_novato_max} filmes: Novato &middot; '
        f'{limiares_decada.limite_novato_max + 1} a {limiares_decada.limite_entusiasta_max}: Entusiasta &middot; '
        f'{limiares_decada.limite_entusiasta_max + 1} a {limiares_decada.limite_especialista_max}: Especialista &middot; '
        f'{limiares_decada.limite_especialista_max + 1}+: {html_lib.escape(limiares_decada.rotulo_topo)}'
    )

    documento = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Matriz de Expertise dos Criticos</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --cor-fundo: #f5f6f8;
    --cor-superficie: #ffffff;
    --cor-texto: #1c1e21;
    --cor-texto-secundario: #5b6270;
    --cor-borda: #e2e4e9;
    --cor-cabecalho: #eef0f4;
    --cor-linha-hover: #f0f4ff;
    --nivel-0: transparent;
    --nivel-1: #eaf7ec;
    --nivel-2: #bfe6c6;
    --nivel-3: #7dc98d;
    --nivel-4: #2f8f4e;
    --nivel-4-texto: #ffffff;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --cor-fundo: #14161a;
      --cor-superficie: #1c1f24;
      --cor-texto: #e7e9ee;
      --cor-texto-secundario: #9aa1ad;
      --cor-borda: #2b2f36;
      --cor-cabecalho: #21252b;
      --cor-linha-hover: #262b33;
      --nivel-1: #16311f;
      --nivel-2: #1f5a34;
      --nivel-3: #2c8a4d;
      --nivel-4: #3fbf6a;
      --nivel-4-texto: #0b1a10;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px;
    background: var(--cor-fundo);
    color: var(--cor-texto);
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  h1 {{ font-size: 1.4rem; margin: 0 0 4px; }}
  .subtitulo {{ color: var(--cor-texto-secundario); margin: 0 0 20px; font-size: 0.9rem; }}
  .painel {{
    background: var(--cor-superficie);
    border: 1px solid var(--cor-borda);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 16px;
  }}
  .resumo {{ display: flex; gap: 28px; flex-wrap: wrap; }}
  .resumo div strong {{ display: block; font-size: 1.3rem; }}
  .resumo div span {{ color: var(--cor-texto-secundario); font-size: 0.82rem; }}
  .legenda {{ font-size: 0.82rem; color: var(--cor-texto-secundario); margin-top: 10px; line-height: 1.6; }}
  .barra-controles {{ display: flex; gap: 10px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }}
  #filtro {{
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid var(--cor-borda);
    background: var(--cor-superficie);
    color: var(--cor-texto);
    min-width: 260px;
    font-size: 0.9rem;
  }}
  #contador-visivel {{ color: var(--cor-texto-secundario); font-size: 0.85rem; }}
  .tabela-wrapper {{
    background: var(--cor-superficie);
    border: 1px solid var(--cor-borda);
    border-radius: 10px;
    overflow: auto;
    max-height: 78vh;
  }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.83rem; white-space: nowrap; }}
  thead th {{
    position: sticky;
    top: 0;
    background: var(--cor-cabecalho);
    text-align: left;
    padding: 9px 10px;
    border-bottom: 1px solid var(--cor-borda);
    cursor: pointer;
    user-select: none;
    z-index: 1;
  }}
  thead th:hover {{ background: var(--cor-linha-hover); }}
  .seta-ordenacao {{ margin-left: 4px; opacity: 0.4; font-size: 0.75em; }}
  tbody td {{ padding: 7px 10px; border-bottom: 1px solid var(--cor-borda); text-align: center; }}
  tbody td.coluna-critico {{ text-align: left; font-weight: 500; }}
  tbody tr:hover {{ background: var(--cor-linha-hover); }}
  .nivel-vazio {{ color: var(--cor-texto-secundario); opacity: 0.5; }}
  .nivel-1 {{ background: var(--nivel-1); }}
  .nivel-2 {{ background: var(--nivel-2); }}
  .nivel-3 {{ background: var(--nivel-3); }}
  .nivel-4 {{ background: var(--nivel-4); color: var(--nivel-4-texto); font-weight: 600; }}
</style>
</head>
<body>

<h1>Matriz de Expertise dos Criticos</h1>
<p class="subtitulo">Classificacao de cada critico por volume de filmes distintos analisados, segmentado por genero e por decada de lancamento.</p>

<div class="painel">
  <div class="resumo">
    <div><strong>{total_criticos}</strong><span>Criticos</span></div>
    <div><strong>{total_generos}</strong><span>Generos</span></div>
    <div><strong>{total_decadas}</strong><span>Decadas</span></div>
  </div>
  <div class="legenda">
    <div><strong>Genero</strong> &mdash; {legenda_generos}</div>
    <div><strong>Decada</strong> &mdash; {legenda_decadas}</div>
  </div>
</div>

<div class="barra-controles">
  <input type="text" id="filtro" placeholder="Filtrar por nome do critico..." oninput="filtrarTabela()">
  <span id="contador-visivel"></span>
</div>

<div class="tabela-wrapper">
  <table id="tabela-matriz">
    <thead><tr>{''.join(cabecalho_html)}</tr></thead>
    <tbody>{''.join(linhas_html)}</tbody>
  </table>
</div>

<script>
  var direcaoOrdenacaoAtual = {{}};

  function filtrarTabela() {{
    var termo = document.getElementById('filtro').value.trim().toLowerCase();
    var linhas = document.querySelectorAll('#tabela-matriz tbody tr');
    var visiveis = 0;
    linhas.forEach(function (linha) {{
      var corresponde = linha.getAttribute('data-nome').indexOf(termo) !== -1;
      linha.style.display = corresponde ? '' : 'none';
      if (corresponde) visiveis++;
    }});
    document.getElementById('contador-visivel').textContent = visiveis + ' de ' + linhas.length + ' criticos';
  }}

  function ordenarPor(indiceColuna) {{
    var tbody = document.querySelector('#tabela-matriz tbody');
    var linhas = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
    var crescente = !direcaoOrdenacaoAtual[indiceColuna];
    direcaoOrdenacaoAtual = {{}};
    direcaoOrdenacaoAtual[indiceColuna] = crescente;

    linhas.sort(function (a, b) {{
      var celulaA = a.children[indiceColuna];
      var celulaB = b.children[indiceColuna];
      var valorA = celulaA.getAttribute('data-valor');
      var valorB = celulaB.getAttribute('data-valor');
      var numA = parseFloat(valorA);
      var numB = parseFloat(valorB);
      var comparacao;
      if (!isNaN(numA) && !isNaN(numB) && celulaA.getAttribute('data-valor') === String(numA)) {{
        comparacao = numA - numB;
      }} else {{
        comparacao = valorA.localeCompare(valorB);
      }}
      return crescente ? comparacao : -comparacao;
    }});

    linhas.forEach(function (linha) {{ tbody.appendChild(linha); }});

    document.querySelectorAll('thead th .seta-ordenacao').forEach(function (seta) {{ seta.textContent = ''; }});
    var setaAtual = document.querySelectorAll('thead th')[indiceColuna].querySelector('.seta-ordenacao');
    setaAtual.textContent = crescente ? '\\u25B2' : '\\u25BC';
  }}

  filtrarTabela();
</script>

</body>
</html>
"""

    with open(caminho_html, "w", encoding="utf-8") as arquivo:
        arquivo.write(documento)
