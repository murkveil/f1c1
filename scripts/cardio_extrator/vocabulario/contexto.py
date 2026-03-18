"""Expressões regulares para contextos clínicos."""

EXPRESSOES_CONTEXTO: dict[str, list[str]] = {
    "prodomo_viral": [
        r"(?:depois|após)\s+(?:\w+\s+){0,4}(?:gripe|resfriado|virose|infecção)",
        r"pr[oó]dromo\s+viral",
    ],
    "historico_familiar_morte_subita": [
        r"(?:pai|mãe|irmão|irmã|parente)\s+(?:\w+\s+){0,6}(?:falec|morr)\w+\s+(?:\w+\s+){0,4}(?:súbit|jovem|cedo)",
        r"(?:pai|mãe|irmão|irmã|parente)\s+(?:\w+\s+){0,4}(?:doença\s+(?:no\s+)?coração|cardiopatia)",
        r"(?:história|histórico)\s+familiar\s+(?:\w+\s+){0,3}(?:morte\s+súbita|cardíac)",
    ],
    "esforco_fisico": [
        r"(?:ao|durante|quando)\s+(?:\w+\s+){0,2}(?:esforço|exercício|caminh|sub\w+\s+escada|corr\w+|atividade\s+física)",
    ],
}
