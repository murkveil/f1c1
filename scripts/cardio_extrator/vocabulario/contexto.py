"""Expressões regulares pré-compiladas para contextos clínicos."""

import re

EXPRESSOES_CONTEXTO: dict[str, list[re.Pattern[str]]] = {
    "prodomo_viral": [
        re.compile(r"(?:depois|após)\s+(?:\w+\s+){0,4}(?:gripe|resfriado|virose|infecção)"),
        re.compile(r"pr[oó]dromo\s+viral"),
    ],
    "historico_familiar_morte_subita": [
        re.compile(r"(?:pai|mãe|irmão|irmã|parente)\s+(?:\w+\s+){0,6}(?:falec|morr)\w+\s+(?:\w+\s+){0,4}(?:súbit|jovem|cedo)"),
        re.compile(r"(?:pai|mãe|irmão|irmã|parente)\s+(?:\w+\s+){0,4}(?:doença\s+(?:no\s+)?coração|cardiopatia)"),
        re.compile(r"(?:história|histórico)\s+familiar\s+(?:\w+\s+){0,3}(?:morte\s+súbita|cardíac)"),
    ],
    "esforco_fisico": [
        re.compile(r"(?:ao|durante|quando)\s+(?:\w+\s+){0,2}(?:esforço|exercício|caminh|sub\w+\s+escada|corr\w+|atividade\s+física)"),
    ],
}
