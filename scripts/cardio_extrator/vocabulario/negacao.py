"""Constantes pré-compiladas do motor de negação contextual."""

import re

NEGADORES: list[re.Pattern[str]] = [
    re.compile(r"\bnão\b"), re.compile(r"\bnego\b"),
    re.compile(r"\bnega\b"), re.compile(r"\bsem\b"),
    re.compile(r"\bnunca\b"), re.compile(r"\bnenhum[a]?\b"),
    re.compile(r"\bausência\s+de\b"),
]

RESTAURADORES: list[re.Pattern[str]] = [
    re.compile(r"\bmas\b"), re.compile(r"\bporém\b"),
    re.compile(r"\bentretanto\b"), re.compile(r"\bcontudo\b"),
    re.compile(r"\btodavia\b"), re.compile(r"\bno\s+entanto\b"),
    re.compile(r"\bagora\s+sim\b"), re.compile(r"\brecentemente\b"),
]

DUPLA_NEGACAO: list[re.Pattern[str]] = [
    re.compile(r"\bnão\s+posso\s+negar\b"),
    re.compile(r"\bnão\s+nego\b"),
    re.compile(r"\bimpossível\s+negar\b"),
]

JANELA_NEGACAO: int = 5

DELIMITADORES_ESCOPO: list[re.Pattern[str]] = [
    re.compile(r"\be\b"), re.compile(r"\bou\b"),
    re.compile(r","), re.compile(r"\."),
    re.compile(r";"), re.compile(r":"),
    re.compile(r"\bque\s+(?!não)"),
]
