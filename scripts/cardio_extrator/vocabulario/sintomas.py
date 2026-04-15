"""Expressões regulares pré-compiladas para detecção de sintomas cardiovasculares."""

import re

EXPRESSOES_SINTOMAS: dict[str, list[re.Pattern[str]]] = {
    "dor_toracica": [
        re.compile(r"dor\s+(?:\w+\s+){0,3}(?:peito|tórax|torax)"),
        re.compile(r"dor\s+torácica"),
        re.compile(r"dor\s+precordial"),
        re.compile(r"dor\s+retroesternal"),
        re.compile(r"aperto\s+(?:\w+\s+){0,4}(?:peito|tórax)"),
        re.compile(r"opressão\s+(?:\w+\s+){0,2}(?:peito|torácica|tórax)"),
        re.compile(r"pressão\s+(?:\w+\s+){0,2}peito"),
        re.compile(r"desconforto\s+(?:\w+\s+){0,2}(?:peito|torácico|precordial)"),
        re.compile(r"pontada\s+(?:\w+\s+){0,2}peito"),
    ],
    "dispneia": [
        re.compile(r"falta\s+de\s+ar"),
        re.compile(r"dificuldade\s+(?:para|de|em)\s+respirar"),
        re.compile(r"sufocamento"),
        re.compile(r"dispn[eé]ia"),
        re.compile(r"(?:não|sem)\s+consig\w+\s+respirar"),
    ],
    "ortopneia": [
        re.compile(r"falta\s+de\s+ar\s+(?:\w+\s+){0,2}(?:ao\s+)?deitar"),
        re.compile(r"(?:preciso|precisa|necessito|uso)\s+(?:\w+\s+){0,2}travesseiros?"),
        re.compile(r"ortopn[eé]ia"),
    ],
    "dispneia_paroxistica_noturna": [
        re.compile(r"(?:acordo|desperto|levanto)\s+(?:\w+\s+){0,5}(?:noite|madrugada)\s+(?:\w+\s+){0,4}(?:falta\s+de\s+ar|sufoc|sem\s+conseg\w+\s+respir)"),
        re.compile(r"(?:acordo|desperto)\s+(?:\w+\s+){0,4}(?:sufoc|falta\s+de\s+ar)"),
        re.compile(r"dispn[eé]ia\s+parox[ií]stica\s+noturna"),
    ],
    "edema_membros_inferiores": [
        re.compile(r"(?:pernas?|membros?\s+inferiores?|tornozelos?|pés)\s+(?:\w+\s+){0,3}(?:incha\w+|edema\w*)"),
        re.compile(r"(?:incha\w+|edema)\s+(?:\w+\s+){0,3}(?:pernas?|membros?\s+inferiores?|tornozelos?|pés)"),
        re.compile(r"edema\s+(?:de\s+)?(?:membros?\s+inferiores?|periférico|bilateral)"),
    ],
    "fadiga": [
        re.compile(r"cansaço\s+(?:constante|extremo|intenso|excessivo|(?:que\s+)?não\s+(?:passa|melhora|some))"),
        re.compile(r"fadiga"),
        re.compile(r"cansaço\s+desproporcional"),
        re.compile(r"exaust(?:ão|o)"),
        re.compile(r"fraqueza"),
        re.compile(r"astenia"),
    ],
    "palpitacao": [
        re.compile(r"palpita\w+"),
        re.compile(r"coração\s+(?:\w+\s+){0,2}(?:disparad|aceler|descompass)\w*"),
        re.compile(r"batimentos?\s+(?:irregulares?|acelerados?|descompassados?|rápidos?)"),
        re.compile(r"falhas?\s+(?:\w+\s+){0,2}batimentos?"),
        re.compile(r"taquicardia"),
    ],
    "sincope": [
        re.compile(r"(?:quase\s+)?desmai\w+"),
        re.compile(r"perda\s+(?:de\s+)?consci[eê]ncia"),
        re.compile(r"s[ií]ncope"),
        re.compile(r"apag(?:ão|ou|uei)"),
    ],
    "tontura": [
        re.compile(r"tontura"),
        re.compile(r"zonz(?:o|a|eira)"),
        re.compile(r"vertigem"),
        re.compile(r"cabeça\s+(?:leve|rodando)"),
        re.compile(r"escurecimento\s+(?:da\s+)?vis(?:ão|ta)"),
    ],
    "cefaleia": [
        re.compile(r"dor(?:es)?\s+de\s+cabeça"),
        re.compile(r"cefal[eé]ia"),
        re.compile(r"enxaqueca"),
    ],
    "febre": [
        re.compile(r"febre"),
        re.compile(r"febr(?:il|e)"),
        re.compile(r"temperatura\s+(?:elevada|alta)"),
    ],
    "tosse_seca_noturna": [
        re.compile(r"tosse\s+(?:seca\s+)?noturna"),
        re.compile(r"tosse\s+(?:à|a)\s+noite"),
        re.compile(r"tosse\s+seca"),
    ],
    "nocturia": [
        re.compile(r"urinando\s+(?:\w+\s+){0,2}(?:à|a)\s+noite"),
        re.compile(r"noct[úu]ria"),
        re.compile(r"levant\w+\s+(?:\w+\s+){0,3}(?:urinar|banheiro)\s+(?:\w+\s+){0,2}noite"),
    ],
    "nausea": [
        re.compile(r"n[áa]usea"),
        re.compile(r"enjô?o"),
        re.compile(r"vontade\s+de\s+vomitar"),
    ],
    "sudorese": [
        re.compile(r"suor\s+(?:frio|excessivo|abundante)"),
        re.compile(r"sudorese"),
        re.compile(r"transpiração\s+(?:fria|excessiva)"),
    ],
    "epistaxe": [
        re.compile(r"sangramento\s+nasal"),
        re.compile(r"sangue\s+(?:pelo|no)\s+nariz"),
        re.compile(r"epistaxe"),
    ],
    "visao_turva": [
        re.compile(r"vis(?:ão|ta)\s+(?:\w+\s+){0,2}(?:embara?çada|turva|borrada|emba[cç]ada)"),
        re.compile(r"enxerg\w+\s+(?:mal|emba[cç]ado)"),
    ],
    "zumbido": [
        re.compile(r"zumbido"),
        re.compile(r"zunido"),
        re.compile(r"chiado\s+(?:no|nos)\s+ouvido"),
    ],
    "mialgia": [
        re.compile(r"dor(?:es)?\s+muscular(?:es)?"),
        re.compile(r"mialgia"),
        re.compile(r"corpo\s+(?:todo\s+)?doendo"),
    ],
    "distensao_abdominal": [
        re.compile(r"barriga\s+(?:inchada|estufada|distendida)"),
        re.compile(r"disten(?:são|ção)\s+abdominal"),
        re.compile(r"saciedade\s+precoce"),
    ],
    "confusao_mental": [
        re.compile(r"confus(?:ão|o)\s+mental"),
        re.compile(r"desnorteado"),
        re.compile(r"sonolência\s+excessiva"),
    ],
}
