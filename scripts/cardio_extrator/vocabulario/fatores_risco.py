"""Expressões regulares para fatores de risco cardiovascular."""

EXPRESSOES_FATORES_RISCO: dict[str, list[str]] = {
    "tabagismo": [
        r"(?:sou\s+)?fum(?:o|ante|ava|ei)",
        r"tabagis\w+",
        r"cigarr\w+",
        r"fumo\s+(?:\w+\s+){0,2}(?:maço|carteira)",
    ],
    "diabetes": [
        r"diabet\w+",
        r"açúcar\s+(?:no\s+sangue\s+)?alto",
        r"glicemia\s+(?:alta|elevada)",
        r"insulina",
    ],
    "hipertensao": [
        r"(?:pressão|pa)\s+(?:\w+\s+)?alta",
        r"hipertens\w+",
        r"pressão\s+(?:arterial\s+)?elevada",
    ],
    "dislipidemia": [
        r"colesterol\s+(?:\w+\s+)?(?:alto|elevado)",
        r"dislipidemia",
        r"triglicér\w+\s+(?:\w+\s+)?alt\w+",
    ],
    "obesidade": [
        r"obes\w+",
        r"sobrepeso",
        r"(?:muito\s+)?acima\s+do\s+peso",
    ],
    "sedentarismo": [
        r"sedentár\w+",
        r"não\s+(?:faço|pratico)\s+(?:\w+\s+)?exercício",
        r"não\s+(?:faço|pratico)\s+(?:\w+\s+)?atividade\s+física",
        r"vida\s+(?:\w+\s+)?sedentária",
    ],
}
