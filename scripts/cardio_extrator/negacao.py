"""Motor de negação contextual para NLP clínico."""

from __future__ import annotations

import re

from .vocabulario.negacao import (
    DELIMITADORES_ESCOPO,
    DUPLA_NEGACAO,
    JANELA_NEGACAO,
    NEGADORES,
    RESTAURADORES,
)


def _tokenizar(texto: str) -> list[tuple[str, int, int]]:
    """Retorna lista de (token, posição_início, posição_fim)."""
    return [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", texto)]


def _encontrar_negador(
    texto_norm: str,
    pos_inicio_match: int,
    tokens: list[tuple[str, int, int]],
) -> tuple[str | None, int]:
    """Verifica se há negador dentro da janela antes da posição do match.

    Args:
        texto_norm: Texto normalizado (minúsculo).
        pos_inicio_match: Posição de início do match do sintoma.
        tokens: Lista de tokens do texto com posições.

    Returns:
        Tupla (negador_encontrado, posição_do_negador). None e -1 se não há.
    """
    idx_match = None
    for i, (_, inicio, _) in enumerate(tokens):
        if inicio >= pos_inicio_match:
            idx_match = i
            break
    if idx_match is None:
        return None, -1

    janela_inicio = max(0, idx_match - JANELA_NEGACAO)
    janela_texto = texto_norm[:pos_inicio_match]

    for padrao in NEGADORES:
        for m in re.finditer(padrao, janela_texto):
            idx_negador = None
            for i, (_, inicio, _) in enumerate(tokens):
                if inicio >= m.start():
                    idx_negador = i
                    break
            if idx_negador is not None and idx_negador >= janela_inicio:
                return m.group(), m.start()

    return None, -1


def _verificar_restaurador(
    texto_norm: str,
    pos_negador: int,
    pos_match: int,
) -> bool:
    """Verifica se há restaurador entre o negador e o match do sintoma.

    Args:
        texto_norm: Texto normalizado.
        pos_negador: Posição do negador no texto.
        pos_match: Posição do match do sintoma.

    Returns:
        True se há restaurador (negação é revertida).
    """
    trecho = texto_norm[pos_negador:pos_match]
    for padrao in RESTAURADORES:
        if re.search(padrao, trecho):
            return True
    return False


def _verificar_delimitador_escopo(
    texto_norm: str,
    pos_negador: int,
    pos_match: int,
) -> bool:
    """Verifica se há delimitador de escopo entre o negador e o match.

    Conjunções coordenativas (e, ou), vírgulas e pontos encerram o
    escopo de negação, impedindo que um negador numa oração afete
    sintomas de outra oração.

    Args:
        texto_norm: Texto normalizado.
        pos_negador: Posição do negador no texto.
        pos_match: Posição do match do sintoma.

    Returns:
        True se há delimitador (negação não se aplica ao match).
    """
    trecho = texto_norm[pos_negador:pos_match]
    for padrao in DELIMITADORES_ESCOPO:
        if re.search(padrao, trecho):
            return True
    return False


def _verificar_dupla_negacao(texto_norm: str, pos_match: int) -> bool:
    """Verifica se o contexto antes do match contém dupla negação (= afirmação).

    Args:
        texto_norm: Texto normalizado.
        pos_match: Posição do match do sintoma.

    Returns:
        True se há dupla negação (o sintoma é afirmado).
    """
    janela = texto_norm[max(0, pos_match - 40):pos_match]
    for padrao in DUPLA_NEGACAO:
        if re.search(padrao, janela):
            return True
    return False


def detectar_negacao(
    texto_norm: str,
    pos_match: int,
    tokens: list[tuple[str, int, int]],
) -> tuple[bool, str | None]:
    """Determina se um achado na posição dada está negado.

    Args:
        texto_norm: Texto normalizado.
        pos_match: Posição de início do match.
        tokens: Tokens do texto com posições.

    Returns:
        Tupla (negado, negador). negado=True se o achado está negado.
    """
    if _verificar_dupla_negacao(texto_norm, pos_match):
        return False, None

    negador, pos_negador = _encontrar_negador(texto_norm, pos_match, tokens)
    if negador is None:
        return False, None

    if _verificar_delimitador_escopo(texto_norm, pos_negador, pos_match):
        return False, None

    if _verificar_restaurador(texto_norm, pos_negador, pos_match):
        return False, None

    return True, negador
