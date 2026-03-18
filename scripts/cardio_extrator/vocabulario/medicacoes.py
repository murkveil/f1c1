"""Expressões regulares para detecção de medicações cardiovasculares."""

EXPRESSOES_MEDICACOES: dict[str, list[str]] = {
    "anti_hipertensivo": [
        r"losartana", r"enalapril", r"amlodipina", r"atenolol",
        r"captopril", r"valsartana", r"nifedipina", r"metoprolol",
        r"propranolol", r"carvedilol", r"hidralazina",
        r"remédio\s+(?:\w+\s+){0,2}pressão",
    ],
    "anticoagulante": [
        r"varfarina", r"rivaroxabana", r"apixabana",
        r"dabigatrana", r"edoxabana", r"heparina",
        r"marevan", r"xarelto", r"eliquis",
    ],
    "antiplaquetario": [
        r"\baas\b", r"aspirina", r"clopidogrel",
        r"ticagrelor", r"prasugrel",
    ],
    "estatina": [
        r"sinvastatina", r"atorvastatina", r"rosuvastatina",
        r"pravastatina", r"fluvastatina",
        r"remédio\s+(?:\w+\s+){0,2}colesterol",
    ],
    "diuretico": [
        r"furosemida", r"hidroclorotiazida", r"espironolactona",
        r"indapamida", r"clortalidona",
        r"lasix",
    ],
    "antidiabetico": [
        r"metformina", r"glibenclamida", r"gliclazida",
        r"insulina", r"glargina", r"dapagliflozina",
        r"empagliflozina", r"sitagliptina",
        r"remédio\s+(?:\w+\s+){0,2}(?:diabetes|açúcar|glicemia)",
    ],
    "antiarritmico": [
        r"amiodarona", r"sotalol", r"propafenona",
        r"flecainida", r"digoxina",
    ],
}
