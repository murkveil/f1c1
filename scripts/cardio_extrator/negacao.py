"""Motor de negação contextual para NLP clínico."""

from __future__ import annotations

import re
from bisect import bisect_left

from .vocabulario.negacao import (
    DELIMITADORES_ESCOPO,
    DUPLA_NEGACAO,
    JANELA_NEGACAO,
    NEGADORES,
    RESTAURADORES,
)

_RE_TOKEN = re.compile(r"\S+")


def _tokenizar(texto: str) -> tuple[list[tuple[str, int, int]], list[int]]:
    """Retorna tokens e vetor de posições para busca binária.

    Args:
        texto: Texto normalizado.

    Returns:
        Tupla (tokens, posições_início) onde posições é ordenado para bisect.
    """
    tokens = [(m.group(), m.start(), m.end()) for m in _RE_TOKEN.finditer(texto)]
    posicoes = [inicio for _, inicio, _ in tokens]
    return tokens, posicoes


def _idx_token(posicoes: list[int], pos: int) -> int | None:
    """Encontra o índice do token na posição dada via busca binária O(log n).

    Args:
        posicoes: Vetor ordenado de posições de início dos tokens.
        pos: Posição a buscar.

    Returns:
        Índice do token ou None se fora do range.
    """
    idx = bisect_left(posicoes, pos)
    return idx if idx < len(posicoes) else None


def _encontrar_negador(
    texto_norm: str,
    pos_inicio_match: int,
    posicoes: list[int],
) -> tuple[str | None, int]:
    """Verifica se há negador dentro da janela antes da posição do match.

    Args:
        texto_norm: Texto normalizado (minúsculo).
        pos_inicio_match: Posição de início do match do sintoma.
        posicoes: Vetor de posições para bisect.

    Returns:
        Tupla (negador_encontrado, posição_do_negador). None e -1 se não há.
    """
    idx_match = _idx_token(posicoes, pos_inicio_match)
    if idx_match is None:
        return None, -1

    janela_inicio = max(0, idx_match - JANELA_NEGACAO)
    janela_texto = texto_norm[:pos_inicio_match]

    for padrao in NEGADORES:
        for m in padrao.finditer(janela_texto):
            idx_negador = _idx_token(posicoes, m.start())
            if idx_negador is not None and idx_negador >= janela_inicio:
                return m.group(), m.start()

    return None, -1


def _verificar_restaurador(
    texto_norm: str,
    pos_negador: int,
    pos_match: int,
) -> bool:
    """Verifica se há restaurador entre o negador e o match do sintoma."""
    trecho = texto_norm[pos_negador:pos_match]
    for padrao in RESTAURADORES:
        if padrao.search(trecho):
            return True
    return False


def _verificar_delimitador_escopo(
    texto_norm: str,
    pos_negador: int,
    pos_match: int,
) -> bool:
    """Verifica se há delimitador de escopo entre o negador e o match."""
    trecho = texto_norm[pos_negador:pos_match]
    for padrao in DELIMITADORES_ESCOPO:
        if padrao.search(trecho):
            return True
    return False


def _verificar_dupla_negacao(texto_norm: str, pos_match: int) -> bool:
    """Verifica se o contexto antes do match contém dupla negação (= afirmação)."""
    janela = texto_norm[max(0, pos_match - 40):pos_match]
    for padrao in DUPLA_NEGACAO:
        if padrao.search(janela):
            return True
    return False


def detectar_negacao(
    texto_norm: str,
    pos_match: int,
    tokens: list[tuple[str, int, int]],
    posicoes: list[int] | None = None,
) -> tuple[bool, str | None]:
    """Determina se um achado na posição dada está negado.

    Args:
        texto_norm: Texto normalizado.
        pos_match: Posição de início do match.
        tokens: Tokens do texto com posições.
        posicoes: Vetor de posições para bisect (opcional, derivado de tokens se ausente).

    Returns:
        Tupla (negado, negador). negado=True se o achado está negado.
    """
    if posicoes is None:
        posicoes = [inicio for _, inicio, _ in tokens]

    if _verificar_dupla_negacao(texto_norm, pos_match):
        return False, None

    negador, pos_negador = _encontrar_negador(texto_norm, pos_inicio_match=pos_match, posicoes=posicoes)
    if negador is None:
        return False, None

    if _verificar_delimitador_escopo(texto_norm, pos_negador, pos_match):
        return False, None

    if _verificar_restaurador(texto_norm, pos_negador, pos_match):
        return False, None

    return True, negador
