"""Padrões regulares para extração de atributos temporais."""

PADROES_TEMPORAIS: dict[str, list[str]] = {
    "inicio": [
        r"há\s+((?:\w+\s+)?(?:dias?|semanas?|meses?|anos?|horas?))",
        r"há\s+(\d+\s+(?:dias?|semanas?|meses?|anos?|horas?))",
        r"desde\s+(ontem|anteontem|semana\s+passada|mês\s+passado)",
        r"(?:começou|iniciou|apareceu)\s+(?:há|faz)\s+((?:\w+\s+)?(?:dias?|semanas?|meses?|horas?))",
        r"(?:começou|iniciou|apareceu)\s+(?:\w+\s+){0,3}(ontem|anteontem|hoje|semana\s+passada)",
    ],
    "duracao": [
        r"(?:dura|duram)\s+(?:\w+\s+){0,2}(\d+\s+(?:minutos?|horas?|segundos?))",
        r"(?:dura|duram)\s+(\w+\s+(?:minutos?|horas?))",
        r"(persistente|contínu[oa]|o\s+dia\s+todo|o\s+tempo\s+todo)",
        r"(?:por|durante)\s+(\d+\s+(?:minutos?|horas?|dias?))",
    ],
    "frequencia": [
        r"(toda\s+(?:noite|manhã|dia|semana))",
        r"(\d+\s*(?:x|vezes?)\s+(?:por|ao|na|no)\s+(?:dia|semana|mês))",
        r"((?:esporádic|ocasional|frequent|diári|intermitente)\w*)",
    ],
    "progressao": [
        r"((?:vem\s+)?(?:piorando|agravando|intensificando))",
        r"((?:vem\s+)?(?:melhorando|aliviando|diminuindo))",
        r"(estável|estacion\w+|sem\s+(?:mudança|alteração))",
        r"((?:cada\s+vez\s+)?(?:pior|mais\s+(?:forte|intenso|frequent)))",
    ],
}
