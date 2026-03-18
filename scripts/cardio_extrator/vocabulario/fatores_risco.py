"""Expressões regulares pré-compiladas para fatores de risco cardiovascular."""

import re

EXPRESSOES_FATORES_RISCO: dict[str, list[re.Pattern[str]]] = {
    "tabagismo": [
        re.compile(r"(?:sou\s+)?fum(?:o|ante|ava|ei)"),
        re.compile(r"tabagis\w+"),
        re.compile(r"cigarr\w+"),
        re.compile(r"fumo\s+(?:\w+\s+){0,2}(?:maço|carteira)"),
    ],
    "diabetes": [
        re.compile(r"diabet\w+"),
        re.compile(r"açúcar\s+(?:no\s+sangue\s+)?alto"),
        re.compile(r"glicemia\s+(?:alta|elevada)"),
        re.compile(r"insulina"),
    ],
    "hipertensao": [
        re.compile(r"(?:pressão|pa)\s+(?:\w+\s+)?alta"),
        re.compile(r"hipertens\w+"),
        re.compile(r"pressão\s+(?:arterial\s+)?elevada"),
    ],
    "dislipidemia": [
        re.compile(r"colesterol\s+(?:\w+\s+)?(?:alto|elevado)"),
        re.compile(r"dislipidemia"),
        re.compile(r"triglicér\w+\s+(?:\w+\s+)?alt\w+"),
    ],
    "obesidade": [
        re.compile(r"obes\w+"),
        re.compile(r"sobrepeso"),
        re.compile(r"(?:muito\s+)?acima\s+do\s+peso"),
    ],
    "sedentarismo": [
        re.compile(r"sedentár\w+"),
        re.compile(r"não\s+(?:faço|pratico)\s+(?:\w+\s+)?exercício"),
        re.compile(r"não\s+(?:faço|pratico)\s+(?:\w+\s+)?atividade\s+física"),
        re.compile(r"vida\s+(?:\w+\s+)?sedentária"),
    ],
}
