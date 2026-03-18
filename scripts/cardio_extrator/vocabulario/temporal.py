"""Padrões regulares pré-compilados para extração de atributos temporais."""

import re

PADROES_TEMPORAIS: dict[str, list[re.Pattern[str]]] = {
    "inicio": [
        re.compile(r"há\s+((?:\w+\s+)?(?:dias?|semanas?|meses?|anos?|horas?))"),
        re.compile(r"há\s+(\d+\s+(?:dias?|semanas?|meses?|anos?|horas?))"),
        re.compile(r"desde\s+(ontem|anteontem|semana\s+passada|mês\s+passado)"),
        re.compile(r"(?:começou|iniciou|apareceu)\s+(?:há|faz)\s+((?:\w+\s+)?(?:dias?|semanas?|meses?|horas?))"),
        re.compile(r"(?:começou|iniciou|apareceu)\s+(?:\w+\s+){0,3}(ontem|anteontem|hoje|semana\s+passada)"),
    ],
    "duracao": [
        re.compile(r"(?:dura|duram)\s+(?:\w+\s+){0,2}(\d+\s+(?:minutos?|horas?|segundos?))"),
        re.compile(r"(?:dura|duram)\s+(\w+\s+(?:minutos?|horas?))"),
        re.compile(r"(persistente|contínu[oa]|o\s+dia\s+todo|o\s+tempo\s+todo)"),
        re.compile(r"(?:por|durante)\s+(\d+\s+(?:minutos?|horas?|dias?))"),
    ],
    "frequencia": [
        re.compile(r"(toda\s+(?:noite|manhã|dia|semana))"),
        re.compile(r"(\d+\s*(?:x|vezes?)\s+(?:por|ao|na|no)\s+(?:dia|semana|mês))"),
        re.compile(r"((?:esporádic|ocasional|frequent|diári|intermitente)\w*)"),
    ],
    "progressao": [
        re.compile(r"((?:vem\s+)?(?:piorando|agravando|intensificando))"),
        re.compile(r"((?:vem\s+)?(?:melhorando|aliviando|diminuindo))"),
        re.compile(r"(estável|estacion\w+|sem\s+(?:mudança|alteração))"),
        re.compile(r"((?:cada\s+vez\s+)?(?:pior|mais\s+(?:forte|intenso|frequent)))"),
    ],
}
