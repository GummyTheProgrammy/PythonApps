"""
core.utils
==========

Funcoes auxiliares de limpeza e normalizacao de valores, utilizadas pelo
modulo `core.etl`. Sao funcoes puras (sem efeitos colaterais de I/O),
adequadas para uso e teste independentes.
"""

from __future__ import annotations

import os
import re


class ArquivoNaoEncontradoError(Exception):
    """Levantada quando nenhum ou mais de um arquivo corresponde ao padrao buscado."""


def localizar_arquivo_por_padrao(pasta: str, padroes: list[str], descricao: str) -> str:
    """
    Localiza, dentro de `pasta`, um unico arquivo .csv cujo nome (em minusculas)
    contenha algum dos textos em `padroes`. Levanta erro descritivo quando
    nenhum ou mais de um arquivo correspondem, listando os candidatos.
    """
    candidatos = []
    for nome in sorted(os.listdir(pasta)):
        if not nome.lower().endswith(".csv"):
            continue
        nome_lower = nome.lower()
        if any(padrao in nome_lower for padrao in padroes):
            candidatos.append(os.path.join(pasta, nome))

    if len(candidatos) == 1:
        return candidatos[0]
    if len(candidatos) == 0:
        raise ArquivoNaoEncontradoError(
            f"Nenhum arquivo correspondente a '{descricao}' foi encontrado em {pasta}."
        )
    raise ArquivoNaoEncontradoError(
        f"Mais de um arquivo correspondente a '{descricao}' foi encontrado em {pasta}: "
        f"{candidatos}. Mantenha apenas um arquivo desse tipo na pasta."
    )


_PADRAO_FRACAO = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$")

_NOTAS_LETRA = {
    "A+": 4.3, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}
_NOTA_LETRA_MAXIMA = 4.3


def texto_valido(valor) -> bool:
    """Retorna True quando `valor` e uma string nao vazia apos remocao de espacos."""
    if valor is None:
        return False
    texto = str(valor).strip()
    return texto != "" and texto.lower() != "nan"


def normalizar_texto(valor) -> str | None:
    """Remove espacos nas extremidades; retorna None para valores vazios/ausentes."""
    if not texto_valido(valor):
        return None
    return str(valor).strip()


def normalizar_booleano(valor) -> bool:
    """Converte representacoes textuais/booleanas de 'top_critic' em bool."""
    if isinstance(valor, bool):
        return valor
    texto = str(valor).strip().lower()
    return texto in {"true", "1", "yes", "sim"}


def normalizar_score(valor) -> float | None:
    """
    Converte a nota original (formatos heterogeneos: 'x/y', percentuais no
    formato 'xx/100' e conceitos por letra 'A' a 'F', com sinais '+'/'-')
    em um valor numerico normalizado no intervalo [0, 1].

    Retorna None quando o formato nao e reconhecido ou o campo esta vazio,
    preservando o valor original (nao normalizado) em outra coluna.
    """
    if not texto_valido(valor):
        return None

    texto = str(valor).strip().upper()

    correspondencia = _PADRAO_FRACAO.match(texto)
    if correspondencia:
        numerador = float(correspondencia.group(1))
        denominador = float(correspondencia.group(2))
        if denominador > 0:
            resultado = numerador / denominador
            return round(min(max(resultado, 0.0), 1.0), 4)
        return None

    if texto in _NOTAS_LETRA:
        return round(_NOTAS_LETRA[texto] / _NOTA_LETRA_MAXIMA, 4)

    return None


def normalizar_data(valor) -> str | None:
    """
    Valida uma data no formato ISO (YYYY-MM-DD). Retorna a propria string
    quando valida, ou None quando ausente/malformada.
    """
    if not texto_valido(valor):
        return None

    texto = str(valor).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", texto):
        return texto
    return None


def normalizar_generos(valor) -> list[str]:
    """
    Converte o campo `genres` (string com generos separados por virgula,
    ex.: "Drama, Mystery & Suspense") em uma lista de generos distintos,
    sem espacos nas extremidades e sem entradas vazias.
    """
    if not texto_valido(valor):
        return []
    generos = [g.strip() for g in str(valor).split(",")]
    return [g for g in generos if g]


def normalizar_decada(data_lancamento) -> str | None:
    """
    Deriva a decada de lancamento (ex.: "1990s") a partir de uma data no
    formato ISO (YYYY-MM-DD). Retorna None quando a data e ausente ou
    malformada.
    """
    data_valida = normalizar_data(data_lancamento)
    if data_valida is None:
        return None
    ano = int(data_valida[:4])
    decada = (ano // 10) * 10
    return f"{decada}s"


_PALAVRAS_CHAVE_PUBLICO = {"audience", "publico", "público", "fan", "reader"}


def contem_indicio_de_publico(tipo_review) -> bool:
    """
    Verificacao defensiva de robustez: caso o campo de tipo/categoria da
    avaliacao (`review_type`) indique explicitamente tratar-se de uma
    avaliacao de publico (ex.: valor "Audience"), o registro e sinalizado
    para exclusao (regra de negocio 2).

    A verificacao e feita por igualdade de palavra inteira (nao por
    substring) e aplicada exclusivamente ao campo de tipo/categoria — NAO
    aos campos de identificacao do critico ou do veiculo de publicacao
    (`critic_name`, `publisher_name`), pois esses campos podem
    legitimamente conter as mesmas palavras em seus nomes proprios (ex.:
    um veiculo chamado "Audiences Everywhere"), o que geraria falsos
    positivos e excluiria criticos validos.

    O esquema da amostra fornecida contem apenas os valores "Fresh" e
    "Rotten" neste campo; esta funcao existe para tornar o pipeline
    robusto a variacoes do arquivo de origem completo.
    """
    if not texto_valido(tipo_review):
        return False
    palavras = re.findall(r"[a-zà-úA-ZÀ-Ú]+", str(tipo_review).lower())
    return any(palavra in _PALAVRAS_CHAVE_PUBLICO for palavra in palavras)
