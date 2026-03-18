"""Extratores clínicos: sintomas, qualificadores, contexto, temporal, fatores de risco, medicações."""

from __future__ import annotations

import logging

from .modelos import AchadoClinico
from .negacao import detectar_negacao
from .vocabulario import (
    EXPRESSOES_CONTEXTO,
    EXPRESSOES_FATORES_RISCO,
    EXPRESSOES_MEDICACOES,
    EXPRESSOES_QUALIFICADORES,
    EXPRESSOES_SINTOMAS,
    PADROES_TEMPORAIS,
)

logger = logging.getLogger("cardio_extrator")


def extrair_sintomas(
    texto_norm: str,
    tokens: list[tuple[str, int, int]],
    posicoes: list[int],
) -> list[AchadoClinico]:
    """Identifica sintomas no texto, respeitando contexto de negação.

    Args:
        texto_norm: Texto já normalizado.
        tokens: Tokens pré-computados.
        posicoes: Vetor de posições para bisect.

    Returns:
        Lista de AchadoClinico com flag de presença/negação.
    """
    achados: list[AchadoClinico] = []
    sintomas_vistos: set[str] = set()

    for sintoma, padroes in EXPRESSOES_SINTOMAS.items():
        if sintoma in sintomas_vistos:
            continue
        for padrao in padroes:
            match = padrao.search(texto_norm)
            if match:
                negado, negador = detectar_negacao(
                    texto_norm, match.start(), tokens, posicoes,
                )
                achados.append(AchadoClinico(
                    sintoma=sintoma,
                    presente=not negado,
                    expressao_original=match.group(),
                    negador=negador,
                    posicao_texto=(match.start(), match.end()),
                ))
                sintomas_vistos.add(sintoma)
                logger.info(
                    "Sintoma '%s' detectado e %s (expressão: '%s')",
                    sintoma,
                    "confirmado" if not negado else f"NEGADO ({negador})",
                    match.group(),
                )
                break

    return achados


def achados_presentes(achados: list[AchadoClinico]) -> set[str]:
    """Retorna conjunto de sintomas confirmados (não negados).

    Args:
        achados: Lista de achados clínicos extraídos.

    Returns:
        Conjunto de nomes canônicos dos sintomas presentes.
    """
    return {a.sintoma for a in achados if a.presente}


def extrair_qualificadores(
    texto_norm: str,
    sintomas_presentes: set[str],
) -> dict[str, dict[str, bool]]:
    """Extrai qualificadores semiológicos dos sintomas presentes.

    Args:
        texto_norm: Texto já normalizado.
        sintomas_presentes: Conjunto de sintomas confirmados.

    Returns:
        Dicionário {sintoma: {qualificador: True}}.
    """
    qualificadores: dict[str, dict[str, bool]] = {}

    for sintoma in sintomas_presentes:
        if sintoma not in EXPRESSOES_QUALIFICADORES:
            continue

        quals_sintoma: dict[str, bool] = {}
        for nome_qual, padroes in EXPRESSOES_QUALIFICADORES[sintoma].items():
            for padrao in padroes:
                if padrao.search(texto_norm):
                    quals_sintoma[nome_qual] = True
                    break

        if quals_sintoma:
            qualificadores[sintoma] = quals_sintoma

    return qualificadores


def extrair_contexto(texto_norm: str) -> dict[str, bool]:
    """Extrai contextos clínicos relevantes do relato.

    Args:
        texto_norm: Texto já normalizado.

    Returns:
        Dicionário {nome_contexto: True}.
    """
    contexto: dict[str, bool] = {}

    for nome, padroes in EXPRESSOES_CONTEXTO.items():
        for padrao in padroes:
            if padrao.search(texto_norm):
                contexto[nome] = True
                break

    return contexto


def extrair_fatores_risco(texto_norm: str) -> dict[str, bool]:
    """Extrai fatores de risco cardiovascular mencionados no relato.

    Args:
        texto_norm: Texto já normalizado.

    Returns:
        Dicionário {fator_de_risco: True}.
    """
    fatores: dict[str, bool] = {}

    for fator, padroes in EXPRESSOES_FATORES_RISCO.items():
        for padrao in padroes:
            if padrao.search(texto_norm):
                fatores[fator] = True
                logger.debug("Fator de risco '%s' detectado no texto", fator)
                break

    return fatores


def extrair_medicacoes(texto_norm: str) -> dict[str, list[str]]:
    """Extrai medicações mencionadas no relato, agrupadas por classe.

    Args:
        texto_norm: Texto já normalizado.

    Returns:
        Dicionário {classe_medicacao: [medicamentos_encontrados]}.
    """
    medicacoes: dict[str, list[str]] = {}

    for classe, padroes in EXPRESSOES_MEDICACOES.items():
        encontrados: list[str] = []
        for padrao in padroes:
            match = padrao.search(texto_norm)
            if match:
                encontrados.append(match.group())
        if encontrados:
            medicacoes[classe] = encontrados
            logger.debug(
                "Medicação classe '%s' detectada: %s", classe, encontrados,
            )

    return medicacoes


def extrair_temporal(texto_norm: str) -> dict[str, str]:
    """Extrai atributos temporais do relato como um todo.

    Args:
        texto_norm: Texto já normalizado.

    Returns:
        Dicionário {atributo_temporal: valor_extraído}.
    """
    temporal: dict[str, str] = {}

    for atributo, padroes in PADROES_TEMPORAIS.items():
        for padrao in padroes:
            match = padrao.search(texto_norm)
            if match:
                temporal[atributo] = match.group(1) if match.lastindex else match.group()
                break

    return temporal


def vincular_temporal_achados(
    achados: list[AchadoClinico],
    temporal: dict[str, str],
) -> None:
    """Vincula informações temporais aos achados clínicos.

    Args:
        achados: Lista de achados clínicos (modificada in-place).
        temporal: Atributos temporais extraídos.
    """
    if not temporal:
        return

    for achado in achados:
        if achado.presente:
            achado.temporal = temporal
            break
