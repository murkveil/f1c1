"""Constantes do motor de negação contextual."""

NEGADORES: list[str] = [
    r"\bnão\b", r"\bnego\b", r"\bnega\b", r"\bsem\b",
    r"\bnunca\b", r"\bnenhum[a]?\b", r"\bausência\s+de\b",
]

RESTAURADORES: list[str] = [
    r"\bmas\b", r"\bporém\b", r"\bentretanto\b", r"\bcontudo\b",
    r"\btodavia\b", r"\bno\s+entanto\b", r"\bagora\s+sim\b",
    r"\brecentemente\b",
]

DUPLA_NEGACAO: list[str] = [
    r"\bnão\s+posso\s+negar\b",
    r"\bnão\s+nego\b",
    r"\bimpossível\s+negar\b",
]

JANELA_NEGACAO: int = 5

DELIMITADORES_ESCOPO: list[str] = [
    r"\be\b", r"\bou\b", r",", r"\.", r";", r":", r"\bque\s+(?!não)",
]
