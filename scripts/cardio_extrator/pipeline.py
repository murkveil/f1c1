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
from .inferencia import avaliar_red_flags, pontuar_doencas
from .modelos import ResultadoAnalise

logger = logging.getLogger("cardio_extrator")


def analisar_relato(relato: str, mapa: dict) -> ResultadoAnalise:
    """Executa o pipeline completo de análise para um relato.

    Args:
        relato: Texto do relato do paciente.
        mapa: Mapa de conhecimento carregado.

    Returns:
        ResultadoAnalise com todos os achados e diagnósticos.
    """
    logger.info("Iniciando análise do relato: '%s...'", relato[:50])

    achados = extrair_sintomas(relato)
    presentes = achados_presentes(achados)
    qualificadores = extrair_qualificadores(relato, presentes)
    contexto = extrair_contexto(relato)
    temporal = extrair_temporal(relato)
    vincular_temporal_achados(achados, temporal)
    fatores_risco = extrair_fatores_risco(relato)
    medicacoes = extrair_medicacoes(relato)

    diagnosticos = pontuar_doencas(
        achados, qualificadores, contexto, fatores_risco, mapa,
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
