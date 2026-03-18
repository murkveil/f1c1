"""Pipeline de análise: orquestra extratores, inferência e red flags."""

from __future__ import annotations

import logging

from .extratores import (
    achados_presentes,
    extrair_contexto,
    extrair_fatores_risco,
    extrair_medicacoes,
    extrair_qualificadores,
    extrair_sintomas,
    extrair_temporal,
    vincular_temporal_achados,
)
from .inferencia import avaliar_red_flags, pontuar_doencas, pre_calcular_scores_maximos
from .modelos import ResultadoAnalise
from .negacao import _tokenizar
from .preprocessamento import normalizar

logger = logging.getLogger("cardio_extrator")


def analisar_relato(
    relato: str,
    mapa: dict,
    scores_maximos: dict[str, float] | None = None,
) -> ResultadoAnalise:
    """Executa o pipeline completo de análise para um relato.

    Args:
        relato: Texto do relato do paciente.
        mapa: Mapa de conhecimento carregado.
        scores_maximos: Cache de scores máximos (opcional).

    Returns:
        ResultadoAnalise com todos os achados e diagnósticos.
    """
    logger.info("Iniciando análise do relato: '%s...'", relato[:50])

    texto_norm = normalizar(relato)
    tokens, posicoes = _tokenizar(texto_norm)

    achados = extrair_sintomas(texto_norm, tokens, posicoes)
    presentes = achados_presentes(achados)
    qualificadores = extrair_qualificadores(texto_norm, presentes)
    contexto = extrair_contexto(texto_norm)
    temporal = extrair_temporal(texto_norm)
    vincular_temporal_achados(achados, temporal)
    fatores_risco = extrair_fatores_risco(texto_norm)
    medicacoes = extrair_medicacoes(texto_norm)

    diagnosticos = pontuar_doencas(
        presentes, qualificadores, contexto, fatores_risco, mapa, scores_maximos,
    )

    alertas = avaliar_red_flags(
        mapa, presentes, qualificadores, contexto, fatores_risco,
    )

    logger.info(
        "Análise concluída: %d sintomas, %d diagnósticos, %d alertas",
        len(presentes), len(diagnosticos), len(alertas),
    )

    return ResultadoAnalise(
        relato_original=relato,
        sintomas=achados,
        qualificadores=qualificadores,
        contexto=contexto,
        temporal=temporal,
        fatores_risco=fatores_risco,
        medicacoes=medicacoes,
        diagnosticos=diagnosticos,
        alertas=alertas,
    )
