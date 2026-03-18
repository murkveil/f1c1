"""Expressões regulares para detecção de sintomas cardiovasculares."""

EXPRESSOES_SINTOMAS: dict[str, list[str]] = {
    "dor_toracica": [
        r"dor\s+(?:\w+\s+){0,3}(?:peito|tórax|torax)",
        r"dor\s+torácica",
        r"dor\s+precordial",
        r"dor\s+retroesternal",
        r"aperto\s+(?:\w+\s+){0,4}(?:peito|tórax)",
        r"opressão\s+(?:\w+\s+){0,2}(?:peito|torácica|tórax)",
        r"pressão\s+(?:\w+\s+){0,2}peito",
        r"desconforto\s+(?:\w+\s+){0,2}(?:peito|torácico|precordial)",
        r"pontada\s+(?:\w+\s+){0,2}peito",
    ],
    "dispneia": [
        r"falta\s+de\s+ar",
        r"dificuldade\s+(?:para|de|em)\s+respirar",
        r"sufocamento",
        r"dispn[eé]ia",
        r"(?:não|sem)\s+consig\w+\s+respirar",
    ],
    "ortopneia": [
        r"falta\s+de\s+ar\s+(?:\w+\s+){0,2}(?:ao\s+)?deitar",
        r"(?:preciso|precisa|necessito|uso)\s+(?:\w+\s+){0,2}travesseiros?",
        r"ortopn[eé]ia",
    ],
    "dispneia_paroxistica_noturna": [
        r"(?:acordo|desperto|levanto)\s+(?:\w+\s+){0,5}(?:noite|madrugada)\s+(?:\w+\s+){0,4}(?:falta\s+de\s+ar|sufoc|sem\s+conseg\w+\s+respir)",
        r"(?:acordo|desperto)\s+(?:\w+\s+){0,4}(?:sufoc|falta\s+de\s+ar)",
        r"dispn[eé]ia\s+parox[ií]stica\s+noturna",
    ],
    "edema_membros_inferiores": [
        r"(?:pernas?|membros?\s+inferiores?|tornozelos?|pés)\s+(?:\w+\s+){0,3}(?:incha\w+|edema\w*)",
        r"(?:incha\w+|edema)\s+(?:\w+\s+){0,3}(?:pernas?|membros?\s+inferiores?|tornozelos?|pés)",
        r"edema\s+(?:de\s+)?(?:membros?\s+inferiores?|periférico|bilateral)",
    ],
    "fadiga": [
        r"cansaço\s+(?:constante|extremo|intenso|excessivo|(?:que\s+)?não\s+(?:passa|melhora|some))",
        r"fadiga",
        r"cansaço\s+desproporcional",
        r"exaust(?:ão|o)",
        r"fraqueza",
        r"astenia",
    ],
    "palpitacao": [
        r"palpita\w+",
        r"coração\s+(?:\w+\s+){0,2}(?:disparad|aceler|descompass)\w*",
        r"batimentos?\s+(?:irregulares?|acelerados?|descompassados?|rápidos?)",
        r"falhas?\s+(?:\w+\s+){0,2}batimentos?",
        r"taquicardia",
    ],
    "sincope": [
        r"(?:quase\s+)?desmai\w+",
        r"perda\s+(?:de\s+)?consci[eê]ncia",
        r"s[ií]ncope",
        r"apag(?:ão|ou|uei)",
    ],
    "tontura": [
        r"tontura",
        r"zonz(?:o|a|eira)",
        r"vertigem",
        r"cabeça\s+(?:leve|rodando)",
        r"escurecimento\s+(?:da\s+)?vis(?:ão|ta)",
    ],
    "cefaleia": [
        r"dor(?:es)?\s+de\s+cabeça",
        r"cefal[eé]ia",
        r"enxaqueca",
    ],
    "febre": [
        r"febre",
        r"febr(?:il|e)",
        r"temperatura\s+(?:elevada|alta)",
    ],
    "tosse_seca_noturna": [
        r"tosse\s+(?:seca\s+)?noturna",
        r"tosse\s+(?:à|a)\s+noite",
        r"tosse\s+seca",
    ],
    "nocturia": [
        r"urinando\s+(?:\w+\s+){0,2}(?:à|a)\s+noite",
        r"noct[úu]ria",
        r"levant\w+\s+(?:\w+\s+){0,3}(?:urinar|banheiro)\s+(?:\w+\s+){0,2}noite",
    ],
    "nausea": [
        r"n[áa]usea",
        r"enjô?o",
        r"vontade\s+de\s+vomitar",
    ],
    "sudorese": [
        r"suor\s+(?:frio|excessivo|abundante)",
        r"sudorese",
        r"transpiração\s+(?:fria|excessiva)",
    ],
    "epistaxe": [
        r"sangramento\s+nasal",
        r"sangue\s+(?:pelo|no)\s+nariz",
        r"epistaxe",
    ],
    "visao_turva": [
        r"vis(?:ão|ta)\s+(?:\w+\s+){0,2}(?:embara?çada|turva|borrada|emba[cç]ada)",
        r"enxerg\w+\s+(?:mal|emba[cç]ado)",
    ],
    "zumbido": [
        r"zumbido",
        r"zunido",
        r"chiado\s+(?:no|nos)\s+ouvido",
    ],
    "mialgia": [
        r"dor(?:es)?\s+muscular(?:es)?",
        r"mialgia",
        r"corpo\s+(?:todo\s+)?doendo",
    ],
    "distensao_abdominal": [
        r"barriga\s+(?:inchada|estufada|distendida)",
        r"disten(?:são|ção)\s+abdominal",
        r"saciedade\s+precoce",
    ],
    "confusao_mental": [
        r"confus(?:ão|o)\s+mental",
        r"desnorteado",
        r"sonolência\s+excessiva",
    ],
}
