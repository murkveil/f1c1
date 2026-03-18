"""Motor de inferência: avaliação de condições, scoring e red flags."""

from __future__ import annotations

import logging

from .extratores import achados_presentes
from .modelos import AchadoClinico, AlertaRedFlag, ScoreDiagnostico

logger = logging.getLogger("cardio_extrator")

CHAVES_META = {"intersecoes", "ambiguidades_clinicas", "red_flags"}


def avaliar_condicao(
    condicao: dict,
    sintomas_presentes: set[str],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
) -> bool:
    """Avalia uma condição declarativa contra o estado clínico atual.

    Suporta os seguintes tipos de condição:
    - {"sintoma": "nome"} -- sintoma presente
    - {"qualificador": "sintoma.qualificador"} -- qualificador presente
    - {"contexto": "nome"} -- contexto clínico presente
    - {"fator_risco": "nome"} -- fator de risco presente
    - {"operador": "AND", "criterios": [...]} -- todos verdadeiros
    - {"operador": "OR", "criterios": [...]} -- ao menos um verdadeiro
    - {"operador": "COUNT_GE", "criterios": [...], "limiar": N} -- ao menos N verdadeiros

    Args:
        condicao: Dicionário descrevendo a condição.
        sintomas_presentes: Sintomas confirmados.
        qualificadores: Qualificadores extraídos.
        contexto: Contextos clínicos extraídos.
        fatores_risco: Fatores de risco extraídos.

    Returns:
        True se a condição é satisfeita.
    """
    if "sintoma" in condicao:
        return condicao["sintoma"] in sintomas_presentes

    if "qualificador" in condicao:
        partes = condicao["qualificador"].split(".", 1)
        if len(partes) != 2:
            return False
        sintoma, qual = partes
        return qualificadores.get(sintoma, {}).get(qual, False)

    if "contexto" in condicao:
        return contexto.get(condicao["contexto"], False)

    if "fator_risco" in condicao:
        return fatores_risco.get(condicao["fator_risco"], False)

    operador = condicao.get("operador")
    criterios = condicao.get("criterios", [])

    if operador == "AND":
        return all(
            avaliar_condicao(c, sintomas_presentes, qualificadores, contexto, fatores_risco)
            for c in criterios
        )

    if operador == "OR":
        return any(
            avaliar_condicao(c, sintomas_presentes, qualificadores, contexto, fatores_risco)
            for c in criterios
        )

    if operador == "COUNT_GE":
        limiar = condicao.get("limiar", 1)
        contagem = sum(
            1 for c in criterios
            if avaliar_condicao(c, sintomas_presentes, qualificadores, contexto, fatores_risco)
        )
        return contagem >= limiar

    return False


def _calcular_score_maximo(scoring: dict) -> float:
    """Calcula o score máximo possível de uma doença (para normalização).

    Args:
        scoring: Seção 'scoring' do mapa de conhecimento da doença.

    Returns:
        Soma de todos os pesos base + todos os bônus possíveis.
    """
    max_sintomas = sum(
        cfg["peso_base"] for cfg in scoring["sintomas"].values()
    )
    max_bonus = sum(
        r["bonus"] for r in scoring.get("regras_bonificacao", [])
    )
    max_fatores = sum(scoring.get("fatores_risco", {}).values())
    return max_sintomas + max_bonus + max_fatores


def pontuar_doenca(
    doenca_config: dict,
    sintomas_presentes: set[str],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
) -> tuple[float, list[str]]:
    """Avalia UMA doença contra os achados clínicos. Sem if/elif por doença.

    Args:
        doenca_config: Configuração completa da doença no mapa.
        sintomas_presentes: Sintomas confirmados do relato.
        qualificadores: Qualificadores semiológicos extraídos.
        contexto: Contextos clínicos extraídos.
        fatores_risco: Fatores de risco extraídos.

    Returns:
        Tupla (score_bruto, justificativas).
    """
    scoring = doenca_config.get("scoring", {})
    score = 0.0
    justificativas: list[str] = []

    for sintoma, cfg in scoring.get("sintomas", {}).items():
        if sintoma in sintomas_presentes:
            peso = cfg["peso_base"]
            score += peso
            justificativas.append(f"sintoma: {sintoma} (peso {peso:.1f})")

    for regra in scoring.get("regras_bonificacao", []):
        if avaliar_condicao(
            regra["condicao"],
            sintomas_presentes, qualificadores, contexto, fatores_risco,
        ):
            score += regra["bonus"]
            justificativas.append(
                f"bônus +{regra['bonus']:.1f}: {regra['justificativa']}"
            )

    for regra in scoring.get("regras_exclusao", []):
        if avaliar_condicao(
            regra["condicao"],
            sintomas_presentes, qualificadores, contexto, fatores_risco,
        ):
            score += regra["penalidade"]
            justificativas.append(
                f"penalidade {regra['penalidade']:.1f}: {regra['justificativa']}"
            )

    for fator, peso in scoring.get("fatores_risco", {}).items():
        if fatores_risco.get(fator, False):
            score += peso
            justificativas.append(f"fator de risco: {fator} (+{peso:.1f})")

    return score, justificativas


def pontuar_doencas(
    achados: list[AchadoClinico],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
    mapa: dict,
) -> list[ScoreDiagnostico]:
    """Calcula pontuação normalizada para todas as doenças do mapa.

    Args:
        achados: Achados clínicos extraídos.
        qualificadores: Qualificadores semiológicos.
        contexto: Contextos clínicos.
        fatores_risco: Fatores de risco.
        mapa: Mapa de conhecimento completo.

    Returns:
        Lista de ScoreDiagnostico ordenada por score normalizado (desc).
    """
    presentes = achados_presentes(achados)
    resultados: list[ScoreDiagnostico] = []

    for chave, config in mapa.items():
        if chave in CHAVES_META:
            continue

        score_bruto, justificativas = pontuar_doenca(
            config, presentes, qualificadores, contexto, fatores_risco,
        )

        if score_bruto <= 0:
            continue

        score_max = _calcular_score_maximo(config.get("scoring", {}))
        score_norm = score_bruto / score_max if score_max > 0 else 0.0
        score_norm = min(score_norm, 1.0)

        if score_norm < 0.3:
            confianca = "baixa"
        elif score_norm < 0.6:
            confianca = "moderada"
        else:
            confianca = "alta"

        resultados.append(ScoreDiagnostico(
            doenca=chave,
            nome_exibicao=config.get("nome_exibicao", chave),
            score_bruto=score_bruto,
            score_normalizado=score_norm,
            confianca=confianca,
            justificativas=justificativas,
        ))

    resultados.sort(key=lambda x: x.score_normalizado, reverse=True)

    if len(resultados) >= 2:
        diff = resultados[0].score_normalizado - resultados[1].score_normalizado
        if diff < 0.10:
            logger.warning(
                "Ambiguidade: scores de %s (%.2f) e %s (%.2f) diferem em < 0.10",
                resultados[0].nome_exibicao, resultados[0].score_normalizado,
                resultados[1].nome_exibicao, resultados[1].score_normalizado,
            )

    return resultados


def avaliar_red_flags(
    mapa: dict,
    sintomas_presentes: set[str],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
) -> list[AlertaRedFlag]:
    """Avalia combinações de achados que indicam emergência cardiovascular.

    Args:
        mapa: Mapa de conhecimento completo (contém seção red_flags).
        sintomas_presentes: Sintomas confirmados.
        qualificadores: Qualificadores semiológicos.
        contexto: Contextos clínicos.
        fatores_risco: Fatores de risco.

    Returns:
        Lista de AlertaRedFlag para as condições satisfeitas.
    """
    alertas: list[AlertaRedFlag] = []

    for red_flag in mapa.get("red_flags", []):
        if avaliar_condicao(
            red_flag["condicao"],
            sintomas_presentes, qualificadores, contexto, fatores_risco,
        ):
            alertas.append(AlertaRedFlag(
                nome=red_flag["nome"],
                mensagem=red_flag["mensagem"],
                prioridade=red_flag["prioridade"],
            ))

    return alertas
