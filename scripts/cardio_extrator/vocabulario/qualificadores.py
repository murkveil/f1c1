"""Expressões regulares para qualificadores semiológicos."""

EXPRESSOES_QUALIFICADORES: dict[str, dict[str, list[str]]] = {
    "dor_toracica": {
        "tipo_opressiva": [
            r"aperto", r"opressão", r"pressão", r"peso",
            r"constri\w+", r"sufoc\w+",
        ],
        "tipo_pleuritica": [
            r"(?:dor\s+)?aguda", r"pontada", r"lancinante",
            r"piora\w*\s+(?:\w+\s+){0,3}respir",
        ],
        "irradiacao_mse": [
            r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}braço\s+esquerdo",
            r"(?:vai?\s+(?:para|pro)|irradi\w+\s+(?:para|pro)?)\s+(?:\w+\s+){0,3}(?:membro\s+superior\s+esquerdo|mse)",
        ],
        "irradiacao_mandibula": [
            r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}mandíbula",
        ],
        "irradiacao_trapezio": [
            r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}(?:trapézio|ombro)",
        ],
        "piora_esforco": [
            r"(?:piora|aparece|surge|durante)\s+(?:\w+\s+){0,3}(?:esforço|exercício|caminh|sub|corr|atividade)",
            r"(?:ao|quando)\s+(?:\w+\s+){0,2}(?:esforço|exercício|caminh|sub\w+\s+escada|corr)",
        ],
        "piora_respiracao": [
            r"piora\s+(?:\w+\s+){0,3}respir",
            r"piora\s+(?:\w+\s+){0,3}inspir",
        ],
        "piora_decubito": [
            r"piora\s+(?:\w+\s+){0,3}(?:deit|decúbito)",
            r"piora\s+(?:\w+\s+){0,3}(?:me\s+)?deit",
        ],
        "alivio_repouso": [
            r"(?:melhora|alívi\w*|some|passa)\s+(?:\w+\s+){0,3}(?:repos|descans|par)",
        ],
        "alivio_inclinado": [
            r"(?:melhora|alívi\w*)\s+(?:\w+\s+){0,4}(?:inclin|sent\w+\s+(?:e\s+)?inclin|sent\w+\s+para\s+frente)",
            r"(?:sento|inclino)\s+(?:\w+\s+){0,3}(?:para\s+)?frente",
        ],
    },
    "palpitacao": {
        "irregular": [r"irregular", r"descompass"],
        "inicio_subito": [
            r"(?:começ|inici)\w+\s+(?:\w+\s+){0,3}(?:de\s+repente|súbit|do\s+nada)",
            r"(?:de\s+repente|súbit|do\s+nada)\s+(?:\w+\s+){0,3}(?:começ|inici)",
        ],
        "precipitante_cafe": [r"caf[eé]", r"cafeína"],
        "precipitante_estresse": [r"estresse", r"ansiedade", r"nervos"],
    },
    "dispneia": {
        "aos_esforcos": [
            r"(?:ao|durante|com)\s+(?:\w+\s+){0,3}(?:esforço|exercício|caminh|sub|escada)",
        ],
        "ao_deitar": [
            r"ao\s+deitar",
            r"deit\w+\s+(?:\w+\s+){0,2}dormir",
        ],
    },
}
