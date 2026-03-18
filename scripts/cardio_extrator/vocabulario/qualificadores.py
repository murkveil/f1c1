"""Expressões regulares pré-compiladas para qualificadores semiológicos."""

import re

EXPRESSOES_QUALIFICADORES: dict[str, dict[str, list[re.Pattern[str]]]] = {
    "dor_toracica": {
        "tipo_opressiva": [
            re.compile(r"aperto"), re.compile(r"opressão"),
            re.compile(r"pressão"), re.compile(r"peso"),
            re.compile(r"constri\w+"), re.compile(r"sufoc\w+"),
        ],
        "tipo_pleuritica": [
            re.compile(r"(?:dor\s+)?aguda"), re.compile(r"pontada"),
            re.compile(r"lancinante"),
            re.compile(r"piora\w*\s+(?:\w+\s+){0,3}respir"),
        ],
        "irradiacao_mse": [
            re.compile(r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}braço\s+esquerdo"),
            re.compile(r"(?:vai?\s+(?:para|pro)|irradi\w+\s+(?:para|pro)?)\s+(?:\w+\s+){0,3}(?:membro\s+superior\s+esquerdo|mse)"),
        ],
        "irradiacao_mandibula": [
            re.compile(r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}mandíbula"),
        ],
        "irradiacao_trapezio": [
            re.compile(r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}(?:trapézio|ombro)"),
        ],
        "piora_esforco": [
            re.compile(r"(?:piora|aparece|surge|durante)\s+(?:\w+\s+){0,3}(?:esforço|exercício|caminh|sub|corr|atividade)"),
            re.compile(r"(?:ao|quando)\s+(?:\w+\s+){0,2}(?:esforço|exercício|caminh|sub\w+\s+escada|corr)"),
        ],
        "piora_respiracao": [
            re.compile(r"piora\s+(?:\w+\s+){0,3}respir"),
            re.compile(r"piora\s+(?:\w+\s+){0,3}inspir"),
        ],
        "piora_decubito": [
            re.compile(r"piora\s+(?:\w+\s+){0,3}(?:deit|decúbito)"),
            re.compile(r"piora\s+(?:\w+\s+){0,3}(?:me\s+)?deit"),
        ],
        "alivio_repouso": [
            re.compile(r"(?:melhora|alívi\w*|some|passa)\s+(?:\w+\s+){0,3}(?:repos|descans|par)"),
        ],
        "alivio_inclinado": [
            re.compile(r"(?:melhora|alívi\w*)\s+(?:\w+\s+){0,4}(?:inclin|sent\w+\s+(?:e\s+)?inclin|sent\w+\s+para\s+frente)"),
            re.compile(r"(?:sento|inclino)\s+(?:\w+\s+){0,3}(?:para\s+)?frente"),
        ],
    },
    "palpitacao": {
        "irregular": [re.compile(r"irregular"), re.compile(r"descompass")],
        "inicio_subito": [
            re.compile(r"(?:começ|inici)\w+\s+(?:\w+\s+){0,3}(?:de\s+repente|súbit|do\s+nada)"),
            re.compile(r"(?:de\s+repente|súbit|do\s+nada)\s+(?:\w+\s+){0,3}(?:começ|inici)"),
        ],
        "precipitante_cafe": [re.compile(r"caf[eé]"), re.compile(r"cafeína")],
        "precipitante_estresse": [re.compile(r"estresse"), re.compile(r"ansiedade"), re.compile(r"nervos")],
    },
    "dispneia": {
        "aos_esforcos": [
            re.compile(r"(?:ao|durante|com)\s+(?:\w+\s+){0,3}(?:esforço|exercício|caminh|sub|escada)"),
        ],
        "ao_deitar": [
            re.compile(r"ao\s+deitar"),
            re.compile(r"deit\w+\s+(?:\w+\s+){0,2}dormir"),
        ],
    },
}
