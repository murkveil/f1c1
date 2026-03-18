"""Pré-processamento de texto para extração clínica."""

from __future__ import annotations

import re

CONTRACOES: list[tuple[str, str]] = [
    (r"\bpro\b", "para o"), (r"\bpra\b", "para a"),
    (r"\bpros\b", "para os"), (r"\bpras\b", "para as"),
    (r"\btô\b", "estou"), (r"\btá\b", "está"),
    (r"\bnum\b", "em um"), (r"\bnuma\b", "em uma"),
    (r"\bnuns\b", "em uns"), (r"\bnumas\b", "em umas"),
    (r"\bduma\b", "de uma"), (r"\bdum\b", "de um"),
    (r"\bpelo\b", "por o"), (r"\bpela\b", "por a"),
    (r"\bnele\b", "em ele"), (r"\bnela\b", "em ela"),
    (r"\bdele\b", "de ele"), (r"\bdela\b", "de ela"),
    (r"\bcê\b", "você"), (r"\bocê\b", "você"),
]

CORRECOES_ORTOGRAFICAS: dict[str, str] = {
    "dispineia": "dispneia", "dispinéia": "dispneia",
    "palpitassão": "palpitação", "palpitasão": "palpitação",
    "inchazo": "inchaço", "inchasço": "inchaço",
    "torax": "tórax", "toráx": "tórax",
    "exame": "exame",
    "cançaso": "cansaço", "cansaso": "cansaço",
    "cabeça": "cabeça",
    "nausea": "náusea",
    "colestero": "colesterol",
    "diabetis": "diabetes", "diabete": "diabetes",
    "pressao": "pressão",
    "coraçao": "coração", "coracao": "coração",
    "desmaiei": "desmaiei",
}


def normalizar(texto: str) -> str:
    """Normaliza texto: minúsculo, contrações expandidas, correções ortográficas.

    Aplica pré-processamento em 3 etapas:
    1. Conversão para minúsculo e simplificação de espaços
    2. Expansão de contrações coloquiais (pro->para o, tô->estou)
    3. Correção de erros ortográficos comuns em relatos de pacientes

    Args:
        texto: Texto original do relato.

    Returns:
        Texto normalizado pronto para extração por regex.
    """
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto).strip()

    for padrao, subst in CONTRACOES:
        texto = re.sub(padrao, subst, texto)

    for errado, correto in CORRECOES_ORTOGRAFICAS.items():
        texto = re.sub(r"\b" + re.escape(errado) + r"\b", correto, texto)

    return texto
