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

_RE_ESPACOS = re.compile(r"\s+")

_PADRAO_CONTRACOES = re.compile(
    "|".join(f"({padrao})" for padrao, _ in CONTRACOES)
)
_SUBST_CONTRACOES = [subst for _, subst in CONTRACOES]


def _substituir_contracao(m: re.Match) -> str:
    for i, g in enumerate(m.groups()):
        if g is not None:
            return _SUBST_CONTRACOES[i]
    return m.group()


_PADRAO_CORRECOES = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in CORRECOES_ORTOGRAFICAS) + r")\b"
)


def normalizar(texto: str) -> str:
    """Normaliza texto: minúsculo, contrações expandidas, correções ortográficas.

    Executa 4 operações regex independente do tamanho dos dicionários:
    1. Simplificação de espaços
    2. Expansão de contrações coloquiais (1 passada)
    3. Correção de erros ortográficos (1 passada)

    Args:
        texto: Texto original do relato.

    Returns:
        Texto normalizado pronto para extração por regex.
    """
    texto = texto.lower()
    texto = _RE_ESPACOS.sub(" ", texto).strip()
    texto = _PADRAO_CONTRACOES.sub(_substituir_contracao, texto)
    texto = _PADRAO_CORRECOES.sub(
        lambda m: CORRECOES_ORTOGRAFICAS[m.group()], texto,
    )
    return texto
